"""Verified overview table contracts and presentation-only aggregations."""
import pandas as pd

from data_loading import DataIssue, load_manifest, read_csv

CONTRACTS = {
    "holdout": ["Model", "MAE", "RMSE", "WAPE (%)"],
    "weekly": ["Year", "Evaluation", "Date", "Model", "Actual", "Prediction"],
    "yearly": ["Year", "Evaluation", "Model", "Forecast_Weeks", "WAPE (%)"],
    "pooled": ["Model", "Validation_Years", "Weeks", "MAE", "RMSE", "WAPE (%)"],
    "quarterly": ["Quarter", "Model", "Weeks", "WAPE (%)"],
    "warehouse": ["Warehouse", "Model", "Test_Weeks", "Forecast_High_Demand_Alerts", "MAE", "RMSE", "WAPE (%)"],
    "recursive": ["Warehouse", "Model", "Observations", "WAPE (%)"],
    "recursive_summary": ["Horizon_Weeks", "Model", "Observations", "WAPE (%)"],
    "recursive_predictions": ["Warehouse", "Week", "Horizon_Week", "Demand", "Recursive_XGBoost", "Seasonal_Naive"],
    "future": ["Warehouse", "Forecast_Origin", "Week", "Horizon_Week", "Predicted_Demand", "Historical_P90"],
    "planning": ["Warehouse", "Horizon_Weeks", "Projected_Total_Demand", "Change_vs_Recent_4Week_Pct",
                 "Illustrative_Risk_Level", "Planning_Consideration"],
    "limitations": ["Limitation", "Impact"],
    "conclusions": ["Conclusion"],
}


def load_overview(directory):
    tables = load_manifest().get("tables", {})
    result = {}
    for name, columns in CONTRACTS.items():
        if name not in tables:
            raise DataIssue(f"Missing table binding: {name}")
        frame = read_csv(directory, tables[name])
        missing = set(columns) - set(frame)
        if missing or frame.empty:
            raise DataIssue(f"{tables[name]}: empty table or missing columns {sorted(missing)}")
        for column in columns:
            if column in ("MAE", "RMSE", "WAPE (%)", "Actual", "Prediction", "Demand", "Predicted_Demand",
                          "Projected_Total_Demand", "Historical_P90", "Change_vs_Recent_4Week_Pct",
                          "Test_Weeks", "Forecast_High_Demand_Alerts", "Observations", "Weeks",
                          "Year", "Forecast_Weeks", "Horizon_Week", "Horizon_Weeks", "Recursive_XGBoost", "Seasonal_Naive"):
                values = pd.to_numeric(frame[column], errors="coerce")
                if not values.map(lambda v: pd.notna(v) and float('-inf') < v < float('inf')).all():
                    raise DataIssue(f"{tables[name]}: non-finite numeric value in {column}")
                frame[column] = values
        for column in ("Date", "Week", "Forecast_Origin"):
            if column in frame:
                frame[column] = pd.to_datetime(frame[column], errors="coerce")
                if frame[column].isna().any():
                    raise DataIssue(f"{tables[name]}: invalid {column}")
        result[name] = frame
    weekly = result["weekly"]
    if not weekly.Date.dt.year.eq(weekly.Year).all() or not set(weekly.Year) == {2014, 2015, 2016}:
        raise DataIssue("Weekly prediction years do not match the reviewed evaluation cohorts.")
    if weekly.duplicated(["Year", "Model", "Date"]).any():
        raise DataIssue("Duplicate model-week prediction rows.")
    if weekly.groupby("Date").Actual.nunique().gt(1).any():
        raise DataIssue("Conflicting actual demand across model rows.")
    if not weekly.groupby(["Year", "Model"]).size().eq(52).all():
        raise DataIssue("Expected 52 weekly results per year and model.")
    expected_evaluation = weekly.Year.map({2014: "Retrospective validation", 2015: "Retrospective validation",
                                          2016: "2016 final holdout (reference)"})
    if not weekly.Evaluation.eq(expected_evaluation).all():
        raise DataIssue("Unexpected retrospective/holdout evaluation labels.")
    if not result["pooled"].Validation_Years.eq("2014-2015").all():
        raise DataIssue("Pooled table contains a different evaluation period.")
    if not result["pooled"].Weeks.eq(104).all():
        raise DataIssue("Expected 104 retrospective weeks per model.")
    future = result["future"]
    if not future.Forecast_Origin.eq(pd.Timestamp("2016-12-25")).all() or not future.Week.gt(future.Forecast_Origin).all():
        raise DataIssue("Archived forecast origin or horizon differs from the reviewed December 2016 exercise.")
    return result


def actual_demand(weekly, year):
    """One actual per timestamp, regardless of the number of forecast models."""
    return (weekly.loc[weekly.Year.eq(year), ["Date", "Actual"]]
            .drop_duplicates().sort_values("Date").reset_index(drop=True))


def holdout_kpis(data):
    comparison = data["holdout"].sort_values("WAPE (%)")
    best = comparison.iloc[0]
    baseline = comparison.loc[comparison.Model.eq("Seasonal Naive"), "WAPE (%)"]
    if len(baseline) != 1 or baseline.iloc[0] <= 0:
        raise DataIssue("Expected one positive Seasonal Naive holdout baseline.")
    actual = actual_demand(data["weekly"], 2016)
    return {"best_model": best.Model, "best_wape": float(best["WAPE (%)"]),
            "baseline_wape": float(baseline.iloc[0]),
            "relative_reduction": float((1 - best["WAPE (%)"] / baseline.iloc[0]) * 100),
            "demand": float(actual.Actual.sum()), "weeks": len(actual),
            "start": actual.Date.min(), "end": actual.Date.max()}


def wape(actual, prediction):
    denominator = actual.abs().sum()
    if denominator == 0:
        raise DataIssue("WAPE is undefined for zero total absolute actual demand.")
    return float((actual - prediction).abs().sum() / denominator * 100)
