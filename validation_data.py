"""Read-only validation evidence contracts; unknown experiment metadata stays unknown."""
import pandas as pd

from data_loading import DataIssue, read_csv

MODELS = ["TimesFM 3.0", "ETS", "Seasonal Naive"]
METRICS = ["WAPE (%)", "MAE", "RMSE"]
SECTIONS = ["Historical backtesting", "Temporal stability", "External M5 validation",
            "Data quality & robustness", "Uncertainty & bias", "Statistical, leakage & monitoring", "Recursive validation"]
CONTRACTS = {
    "timesfm_historical_yearly_results": ["Year", "Evaluation", "Model", "Train_Weeks", "Forecast_Weeks"] + METRICS,
    "timesfm_historical_quarterly_results": ["Year", "Evaluation", "Quarter", "Model", "Weeks"] + METRICS,
    "timesfm_historical_quarterly_pooled": ["Quarter", "Model", "Validation_Years", "Weeks"] + METRICS,
    "timesfm_quarterly_stability_summary": ["Model", "Historical_Validation_Years", "Pooled_Quarterly_WAPE_Min", "Pooled_Quarterly_WAPE_Max", "Pooled_Quarterly_WAPE_Range_pp"],
    "timesfm_historical_monthly_results": ["Year", "Evaluation", "Month", "Month_Name", "Model", "Weeks", "Actual_Month_Total", "Predicted_Month_Total", "Month_Total_APE (%)"] + METRICS,
    "timesfm_historical_monthly_pooled": ["Month", "Month_Name", "Model", "Validation_Years", "Weeks"] + METRICS,
    "timesfm_monthly_stability_summary": ["Model", "Validation_Years", "Pooled_Monthly_WAPE_Min", "Pooled_Monthly_WAPE_Max", "Pooled_Monthly_WAPE_Range_pp"],
    "m5_external_validation": ["Model"] + METRICS,
    "data_quality_impact": ["Scenario", "WAPE_Change_pp"] + METRICS,
    "data_disruption_robustness": ["Scenario", "WAPE_Change_pp"] + METRICS,
    "random_seed_stability": ["Model", "Random_Seed"] + METRICS,
    "random_seed_stability_summary": ["Model", "Mean_MAE", "Mean_RMSE", "Mean_WAPE", "Std_WAPE", "Min_WAPE", "Max_WAPE"],
    "forecast_calibration": ["Target_Coverage", "Observations", "Covered", "Total_Width", "Observed_Coverage", "Average_Width"],
    "week7_uncertainty": ["Target Coverage (%)", "Observed Coverage (%)", "Average Interval Width", "Point Forecast MAE", "Actual Above Upper Bound"],
    "quantile_comparison": ["Method", "Coverage (%)", "Average_Width"],
    "quantile_warehouse_results": ["Warehouse", "Coverage", "Coverage (%)", "Average_Width"],
    "forecast_bias_summary": ["Warehouse", "Observations", "Total_Demand", "Total_Signed_Error", "Mean_Signed_Error", "MAE", "Underforecast_Rate", "Bias_Pct", "Underforecast_Rate_Pct", "Longest_Underforecast_Streak"],
    "forecast_bias_quarterly": ["Warehouse", "Quarter", "Mean_Signed_Error", "Underforecast_Rate_Pct"],
    "forecast_significance_test": ["Comparison", "Weeks", "Mean_Loss_Difference", "HAC_p_value", "CI_95_Lower", "CI_95_Upper"],
    "data_leakage_audit": ["Check", "Status", "Details"],
    "model_monitoring_2016": ["Week", "Demand", "Forecast", "Absolute_Error", "Rolling_WAPE_Pct", "Warning", "Persistent_Warning"],
    "recursive_12_week_backtest_summary": ["Horizon_Weeks", "Model", "Observations"] + METRICS,
    "recursive_12_week_warehouse_results": ["Warehouse", "Model", "Observations"] + METRICS,
    "recursive_12_week_backtest_predictions": ["Warehouse", "Week", "Horizon_Week", "Recursive_XGBoost", "Seasonal_Naive", "Demand"],
}
TEXT = {"Model", "Evaluation", "Quarter", "Month_Name", "Validation_Years", "Historical_Validation_Years",
        "Scenario", "Method", "Warehouse", "Comparison", "Check", "Status", "Details", "Week", "Warning", "Persistent_Warning"}


def evidence(directory, name):
    if name not in CONTRACTS:
        raise DataIssue("Unknown validation source.")
    frame = read_csv(directory, f"tables/{name}.csv")
    missing = set(CONTRACTS[name]) - set(frame)
    if frame.empty or missing:
        raise DataIssue(f"{name}.csv: empty table or missing columns {sorted(missing)}")
    for column in CONTRACTS[name]:
        if column not in TEXT:
            values = pd.to_numeric(frame[column], errors="coerce")
            allowed_null = frame[column].isna() if column == "Rolling_WAPE_Pct" else pd.Series(False, index=frame.index)
            finite = values.map(lambda v: pd.notna(v) and float('-inf') < v < float('inf'))
            if not (finite | allowed_null).all():
                raise DataIssue(f"{name}.csv: invalid or missing numeric evidence in {column}")
            frame[column] = values
            if column in METRICS and frame[column].lt(0).any():
                raise DataIssue(f"{name}.csv: negative error metric in {column}")
        elif column not in {"Details", "Week", "Warning", "Persistent_Warning"} and frame[column].isna().any():
            raise DataIssue(f"{name}.csv: missing {column} labels")
    if "Week" in frame:
        frame["Week"] = pd.to_datetime(frame.Week, errors="coerce", format="ISO8601")
        if frame.Week.isna().any():
            raise DataIssue(f"{name}.csv: invalid recorded dates")
    for column in ["Warning", "Persistent_Warning"]:
        if column in frame:
            labels = frame[column].astype(str).str.lower()
            if not labels.isin(["true", "false"]).all():
                raise DataIssue(f"{name}.csv: invalid {column} flags")
            frame[column] = labels.eq("true")
    if name == "model_monitoring_2016" and (not frame.Week.dt.year.eq(2016).all() or frame.Week.duplicated().any()):
        raise DataIssue("Monitoring rows must contain unique 2016 weekly dates.")
    if "Evaluation" in frame:
        expected = frame.Year.map({2014: "Retrospective validation", 2015: "Retrospective validation",
                                   2016: "2016 final holdout (reference)"})
        if not frame.Evaluation.eq(expected).all():
            raise DataIssue("Year and retrospective/holdout labels disagree.")
    if "Validation_Years" in frame:
        if not frame.Validation_Years.astype(str).isin(["2014-2015", "2014-2015 (retrospective)"]).all():
            raise DataIssue("Pooled/stability source must exclude the 2016 holdout.")
    if "Historical_Validation_Years" in frame and not frame.Historical_Validation_Years.eq("2014-2015").all():
        raise DataIssue("Quarterly stability source must contain retrospective years only.")
    return frame


def yearly_evidence(directory, cohort, years, models):
    allowed = [2014, 2015] if cohort == "Retrospective 2014–2015" else [2016] if cohort == "2016 holdout reference" else []
    if not allowed or not set(years).issubset(allowed):
        raise DataIssue("Retrospective and holdout years cannot be combined.")
    frame = evidence(directory, "timesfm_historical_yearly_results")
    return frame.loc[frame.Year.isin(years) & frame.Model.isin(models)].copy()


def temporal_evidence(directory, grain, cohort, years, models, periods=None):
    if grain not in ["Quarterly", "Monthly"]:
        raise DataIssue("Temporal evidence must be quarterly or monthly.")
    stem = "quarterly" if grain == "Quarterly" else "monthly"
    pooled = cohort == "Pooled 2014–2015"
    if pooled and not set(years).issubset({2014, 2015}):
        raise DataIssue("Pooled retrospective evidence cannot contain holdout years.")
    name = f"timesfm_historical_{stem}_{'pooled' if pooled else 'results'}"
    frame = evidence(directory, name)
    if not pooled:
        allowed = [2014, 2015] if cohort == "Retrospective 2014–2015" else [2016] if cohort == "2016 holdout reference" else []
        if not allowed or not set(years).issubset(allowed):
            raise DataIssue("Temporal filters cannot merge retrospective and holdout results.")
        frame = frame.loc[frame.Year.isin(years)].copy()
        frame["Sample"] = frame.Year.astype(int).astype(str)
    else:
        frame["Sample"] = "Pooled 2014–2015"
    frame = frame.loc[frame.Model.isin(models)].copy()
    frame["Period"] = frame.Quarter if grain == "Quarterly" else frame.Month_Name
    frame["Period_Number"] = frame.Quarter.str.removeprefix("Q").astype(int) if grain == "Quarterly" else frame.Month
    if periods is not None:
        frame = frame.loc[frame.Period.isin(periods)]
    return name, frame.sort_values(["Sample", "Model", "Period_Number"])


def calibration_percentages(frame):
    frame = frame.copy()
    if not frame.Observed_Coverage.between(0, 100).all() or not frame.Target_Coverage.between(0, 100).all():
        raise DataIssue("Calibration percentage scales are invalid.")
    if not frame.Observations.gt(0).all() or not frame.Covered.between(0, frame.Observations).all():
        raise DataIssue("Invalid empirical coverage counts.")
    expected = frame.Covered / frame.Observations * 100
    if (frame.Observed_Coverage - expected).abs().gt(1e-8).any():
        raise DataIssue("Reported calibration percentages disagree with covered/observation counts.")
    frame["Observed_Coverage_Pct"] = frame.Observed_Coverage
    return frame
