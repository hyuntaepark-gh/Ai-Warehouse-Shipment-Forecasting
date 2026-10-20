"""Read-only operational evidence. Exported categories are never reverse engineered."""
import math

import pandas as pd

from data_loading import DataIssue, read_csv
from future_data import (HORIZONS, SUMMARY_METRICS, TOLERANCE_UNITS, WAREHOUSES,
                         load_archive, reconcile_summary, select_records)
from warehouse_data import load_warehouse_actuals

PLANNING_SOURCE = "tables/future_operational_decision_summary.csv"
SUPPLEMENTARY = {
    "scenario_summary": (["Scenario"], ["Average_Risk_Ratio", "Maximum_Risk_Ratio", "Threshold_Exceedances"]),
    "capacity_optimization": (["Policy"], ["Total_Expected_Loss", "Average_Planned_Capacity"]),
    "illustrative_cost_simulation": (["Scenario", "Model"], ["Warehouse_Weeks", "Underforecast_Units", "Overforecast_Units", "Total_Planning_Loss_Units", "Loss_per_1000_Demand_Units"]),
    "forecast_value_added": (["Evaluation_Level", "Model"], ["WAPE (%)", "Baseline_WAPE (%)", "FVA_Improvement (%)"]),
}


def checked_table(frame, labels, numbers, source):
    frame = frame.copy()
    required = set(labels + numbers)
    if frame.empty or not required.issubset(frame):
        raise DataIssue(f"{source}: empty table or missing columns {sorted(required - set(frame))}")
    for column in labels:
        if frame[column].isna().any() or frame[column].astype(str).str.strip().eq("").any():
            raise DataIssue(f"{source}: missing {column} labels")
    for column in numbers:
        frame[column] = pd.to_numeric(frame[column], errors="coerce")
        if not frame[column].map(lambda x: pd.notna(x) and math.isfinite(x)).all():
            raise DataIssue(f"{source}: invalid numeric field {column}")
    return frame


def load_planning(directory):
    archive = load_archive(directory)
    weekly = checked_table(archive["weekly"], ["Illustrative_Risk_Level"],
                           ["Historical_P90", "Demand_to_P90_Ratio"], "weekly risk export")
    if not weekly.Historical_P90.gt(0).all() or weekly.Demand_to_P90_Ratio.lt(0).any():
        raise DataIssue("Historical P90 references must be positive and demand ratios nonnegative.")
    if not weekly.groupby("Warehouse").Historical_P90.nunique().eq(1).all():
        raise DataIssue("Historical P90 reference changes within an archived warehouse.")
    expected = weekly.Predicted_Demand / weekly.Historical_P90
    if (expected - weekly.Demand_to_P90_Ratio).abs().gt(1e-10).any():
        raise DataIssue("Exported demand/P90 ratios disagree with predictions and historical references.")
    planning = checked_table(read_csv(directory, PLANNING_SOURCE),
        ["Warehouse", "Illustrative_Risk_Level", "Planning_Consideration"],
        ["Horizon_Weeks", *SUMMARY_METRICS, "Recent_4Week_Mean_Observed", "Change_vs_Recent_4Week_Pct",
         "Weeks_Above_Historical_P90", "Max_Demand_to_P90_Ratio"], PLANNING_SOURCE)
    checks = reconcile_summary(weekly, planning)
    if not planning.Recent_4Week_Mean_Observed.gt(0).all():
        raise DataIssue("Recent observed demand references must be positive for percentage changes.")
    if not planning.groupby("Warehouse").Recent_4Week_Mean_Observed.nunique().eq(1).all():
        raise DataIssue("Recent observed references differ across horizons for the same warehouse.")
    for row in planning.itertuples():
        records = select_records(weekly, [row.Warehouse], row.Horizon_Weeks)
        expected_fields = {
            "Change_vs_Recent_4Week_Pct": (records.Predicted_Demand.mean() / row.Recent_4Week_Mean_Observed - 1) * 100,
            "Weeks_Above_Historical_P90": int(records.Predicted_Demand.gt(records.Historical_P90).sum()),
            "Max_Demand_to_P90_Ratio": records.Demand_to_P90_Ratio.max(),
        }
        for metric, calculated in expected_fields.items():
            reported = getattr(row, metric)
            difference = abs(reported - calculated)
            if difference > 1e-8:
                raise DataIssue(f"Operational summary mismatch: {row.Warehouse}/{row.Horizon_Weeks}/{metric}")
            checks.loc[len(checks)] = [row.Warehouse, row.Horizon_Weeks, metric, calculated, reported, difference]
    return {"weekly": weekly, "planning": planning, "checks": checks}


def selected_planning(archive, warehouses, horizon):
    weekly = select_records(archive["weekly"], warehouses, horizon)
    summary = archive["planning"]
    return weekly, summary.loc[summary.Warehouse.isin(warehouses) & summary.Horizon_Weeks.eq(horizon)].copy()


def recent_observed_context(directory, planning):
    history = load_warehouse_actuals(directory)
    recent = history.sort_values("Date").groupby("Series").tail(4)
    result = recent.groupby("Series", as_index=False).agg(
        Recent_4Week_Mean_Observed=("Demand", "mean"), Observed_Weeks=("Date", "nunique"),
        First_Observed_Week=("Date", "min"), Last_Observed_Week=("Date", "max")).rename(columns={"Series": "Warehouse"})
    reference = planning[["Warehouse", "Recent_4Week_Mean_Observed"]].drop_duplicates()
    paired = result.merge(reference, on="Warehouse", suffixes=("", "_Exported"), validate="one_to_one")
    if len(paired) != len(WAREHOUSES) or not paired.Observed_Weeks.eq(4).all() or (
        paired.Recent_4Week_Mean_Observed - paired.Recent_4Week_Mean_Observed_Exported).abs().gt(TOLERANCE_UNITS).any():
        raise DataIssue("Recent observed demand does not reconcile with the planning references.")
    return result


def supplementary(directory, name):
    if name not in SUPPLEMENTARY:
        raise DataIssue("Unknown operational supplementary source.")
    labels, numbers = SUPPLEMENTARY[name]
    frame = checked_table(read_csv(directory, f"tables/{name}.csv"), labels, numbers, name)
    if frame.duplicated(labels).any():
        raise DataIssue(f"{name}: duplicate evidence keys")
    for column in numbers:
        if column != "FVA_Improvement (%)" and frame[column].lt(0).any():
            raise DataIssue(f"{name}: negative {column}")
    for column in ["Warehouse_Weeks", "Threshold_Exceedances"]:
        if column in frame and not frame[column].mod(1).eq(0).all():
            raise DataIssue(f"{name}: counts must be integers")
    if name == "forecast_value_added":
        if not frame["Baseline_WAPE (%)"].gt(0).all():
            raise DataIssue("FVA baseline must be positive.")
        expected = (1 - frame["WAPE (%)"] / frame["Baseline_WAPE (%)"]) * 100
        if (frame["FVA_Improvement (%)"] - expected).abs().gt(1e-8).any():
            raise DataIssue("FVA percentages do not reconcile with exported WAPE baselines.")
        for _, group in frame.groupby("Evaluation_Level"):
            baseline = group.loc[group.Model.eq("Naive"), "WAPE (%)"]
            if len(baseline) != 1 or not (group["Baseline_WAPE (%)"] - baseline.iloc[0]).abs().le(1e-8).all():
                raise DataIssue("FVA evaluation level has inconsistent Naive baselines.")
    return frame
