"""Validate complete archived forecasts before any selected or aggregate calculation."""
import math

import pandas as pd

from data_loading import DataIssue, read_csv

WAREHOUSES = ["Whse_A", "Whse_C", "Whse_J", "Whse_S"]
HORIZONS = [4, 8, 12]
ORIGIN = pd.Timestamp("2016-12-25")
WEEKLY_SOURCE = "tables/future_warehouse_weekly_forecasts.csv"
SUMMARY_SOURCE = "tables/future_4_8_12_week_summary.csv"
SUMMARY_METRICS = ["Projected_Total_Demand", "Average_Weekly_Demand", "Peak_Weekly_Demand"]
TOLERANCE_UNITS = 0.00001


def validate_weekly(frame):
    required = {"Warehouse", "Forecast_Origin", "Week", "Horizon_Week", "Predicted_Demand"}
    if frame.empty or not required.issubset(frame):
        raise DataIssue(f"Weekly forecast export is empty or missing columns: {sorted(required - set(frame))}")
    frame = frame.copy()
    for column in ["Forecast_Origin", "Week"]:
        frame[column] = pd.to_datetime(frame[column], errors="coerce", format="ISO8601")
        if frame[column].isna().any():
            raise DataIssue(f"Invalid archived forecast date in {column}.")
    if not frame.Forecast_Origin.eq(ORIGIN).all():
        raise DataIssue("Forecast origin must be December 25, 2016 for every record.")
    if frame.Warehouse.isna().any() or set(frame.Warehouse) != set(WAREHOUSES):
        raise DataIssue("Incomplete or unknown warehouse coverage: all four archived warehouses are required before aggregation.")
    for column in ["Horizon_Week", "Predicted_Demand"]:
        values = pd.to_numeric(frame[column], errors="coerce")
        if not values.map(lambda value: pd.notna(value) and 0 <= value < float('inf')).all():
            raise DataIssue(f"Non-finite, missing or negative forecast value in {column}.")
        frame[column] = values
    if not frame.Horizon_Week.between(1, 12).all() or not frame.Horizon_Week.mod(1).eq(0).all():
        raise DataIssue("Forecast horizon identifiers must be integers 1 through 12.")
    frame.Horizon_Week = frame.Horizon_Week.astype(int)
    if frame.duplicated(["Warehouse", "Horizon_Week"]).any() or frame.duplicated(["Warehouse", "Week"]).any():
        raise DataIssue("Duplicate warehouse/horizon or warehouse/date forecast rows.")
    for warehouse, group in frame.groupby("Warehouse"):
        if sorted(group.Horizon_Week) != list(range(1, 13)):
            raise DataIssue(f"Incomplete 12-week forecast coverage for {warehouse}; no missing projections will be filled.")
    expected = frame.Forecast_Origin + pd.to_timedelta(frame.Horizon_Week * 7, unit="D")
    if not frame.Week.eq(expected).all():
        raise DataIssue("Weekly timestamps are not aligned with forecast origin and horizon identifiers.")
    return frame.sort_values(["Warehouse", "Horizon_Week"]).reset_index(drop=True)


def select_records(weekly, warehouses, horizon):
    weekly = validate_weekly(weekly)
    if horizon not in HORIZONS:
        raise DataIssue("Supported archived horizon filters are 4, 8 and 12 weeks.")
    if not warehouses or len(warehouses) != len(set(warehouses)) or not set(warehouses).issubset(WAREHOUSES):
        raise DataIssue("Select one or more distinct archived warehouses.")
    return weekly.loc[weekly.Warehouse.isin(warehouses) & weekly.Horizon_Week.le(horizon)].copy()


def forecast_views(weekly, warehouses, horizon):
    selected = select_records(weekly, warehouses, horizon)
    # Keep only projection fields; operational risk categories/P90 are not forecast intervals.
    detail = selected[["Warehouse", "Forecast_Origin", "Week", "Horizon_Week", "Predicted_Demand"]].copy()
    detail["Cumulative_Projected_Demand"] = detail.groupby("Warehouse").Predicted_Demand.cumsum()
    detail["Type"] = "Archived projected demand"
    combined = detail.groupby(["Forecast_Origin", "Week", "Horizon_Week"], as_index=False).agg(
        Predicted_Demand=("Predicted_Demand", "sum"), Warehouse_Count=("Warehouse", "nunique"))
    if not combined.Warehouse_Count.eq(len(warehouses)).all():
        raise DataIssue("Selected weekly warehouse coverage is incomplete; combined totals are unavailable.")
    combined = combined.sort_values("Horizon_Week")
    combined["Cumulative_Projected_Demand"] = combined.Predicted_Demand.cumsum()
    combined["Type"] = "Archived projected demand · selected warehouses combined"
    return detail, combined


def warehouse_summaries(weekly, warehouses):
    rows = []
    for horizon in HORIZONS:
        selected = select_records(weekly, warehouses, horizon)
        for warehouse, group in selected.groupby("Warehouse"):
            rows.append({"Warehouse": warehouse, "Horizon_Weeks": horizon,
                         "Projected_Total_Demand": float(group.Predicted_Demand.sum()),
                         "Average_Weekly_Demand": float(group.Predicted_Demand.mean()),
                         "Peak_Weekly_Demand": float(group.Predicted_Demand.max()),
                         "Forecast_Records": len(group)})
    result = pd.DataFrame(rows)
    denominator = result.groupby("Horizon_Weeks").Projected_Total_Demand.transform("sum")
    result["Contribution_Pct"] = result.Projected_Total_Demand.div(denominator.where(denominator.gt(0))) * 100
    return result


def combined_summaries(weekly, warehouses):
    rows = []
    for horizon in HORIZONS:
        _, combined = forecast_views(weekly, warehouses, horizon)
        rows.append({"Horizon_Weeks": horizon, "Selected_Warehouses": len(warehouses),
                     "Projected_Total_Demand": float(combined.Predicted_Demand.sum()),
                     "Average_Weekly_Demand": float(combined.Predicted_Demand.mean()),
                     "Peak_Weekly_Demand": float(combined.Predicted_Demand.max()),
                     "First_Projected_Week": combined.Week.min(), "Last_Projected_Week": combined.Week.max()})
    return pd.DataFrame(rows)


def reconcile_summary(weekly, exported):
    required = {"Warehouse", "Horizon_Weeks", *SUMMARY_METRICS}
    if exported.empty or not required.issubset(exported):
        raise DataIssue("The exported 4/8/12-week summary is empty or missing required columns.")
    exported = exported.copy()
    for column in ["Horizon_Weeks"] + SUMMARY_METRICS:
        exported[column] = pd.to_numeric(exported[column], errors="coerce")
        if not exported[column].map(lambda value: pd.notna(value) and 0 <= value < float('inf')).all():
            raise DataIssue(f"Invalid exported forecast summary value in {column}.")
    keys = ["Warehouse", "Horizon_Weeks"]
    if exported.duplicated(keys).any() or set(zip(exported.Warehouse, exported.Horizon_Weeks)) != {(w, h) for w in WAREHOUSES for h in HORIZONS}:
        raise DataIssue("Exported summary must contain exactly one row per warehouse and 4/8/12-week horizon.")
    calculated = warehouse_summaries(weekly, WAREHOUSES)
    paired = calculated.merge(exported, on=keys, suffixes=("_Calculated", "_Exported"), validate="one_to_one")
    checks = []
    for row in paired.to_dict("records"):
        for metric in SUMMARY_METRICS:
            computed, reported = row[metric + "_Calculated"], row[metric + "_Exported"]
            difference = abs(computed - reported)
            if not math.isclose(computed, reported, abs_tol=TOLERANCE_UNITS, rel_tol=0):
                raise DataIssue(f"Forecast summary mismatch for {row['Warehouse']} / {row['Horizon_Weeks']} weeks / {metric}.")
            checks.append({"Warehouse": row["Warehouse"], "Horizon_Weeks": row["Horizon_Weeks"], "Metric": metric,
                           "Calculated": computed, "Exported": reported, "Absolute_Difference": difference})
    return pd.DataFrame(checks)


def load_archive(directory):
    weekly = validate_weekly(read_csv(directory, WEEKLY_SOURCE))
    summary = read_csv(directory, SUMMARY_SOURCE)
    checks = reconcile_summary(weekly, summary)
    return {"weekly": weekly, "summary": summary, "checks": checks}
