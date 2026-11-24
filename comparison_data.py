"""CSV-backed comparison cohorts. Never rank rows from different evaluation tasks."""
from dataclasses import dataclass

import pandas as pd

from data_loading import DataIssue, read_csv

GROUPS = ["2016 full-year aggregate holdout", "2014–2015 retrospective backtesting",
          "Warehouse-level forecasting", "Historical recursive validation"]
METRICS = ["WAPE (%)", "MAE", "RMSE"]
MODEL_TYPES = {
    "TimesFM 3.0": "Pretrained foundation model · zero-shot",
    "ETS": "Exponential smoothing", "SARIMAX": "Seasonal ARIMA with exogenous inputs",
    "Refined SARIMA": "Seasonal ARIMA", "Seasonal Naive": "Seasonal benchmark",
    "Prophet": "Additive statistical model", "N-BEATS": "Neural time-series model",
    "N-HiTS": "Neural time-series model", "Random Forest": "Tree ensemble",
    "XGBoost": "Gradient-boosted trees", "Naive": "Naive benchmark",
    "Recursive XGBoost": "Recursive gradient-boosted trees",
}
FILES = {
    "holdout": "tables/full_year_model_comparison.csv",
    "yearly": "tables/timesfm_historical_yearly_results.csv",
    "pooled": "tables/timesfm_historical_pooled_summary.csv",
    "weekly": "tables/timesfm_historical_weekly_predictions.csv",
    "warehouse": "tables/dashboard_performance_summary.csv",
    "recursive_summary": "tables/recursive_12_week_backtest_summary.csv",
    "recursive_warehouse": "tables/recursive_12_week_warehouse_results.csv",
    "recursive_predictions": "tables/recursive_12_week_backtest_predictions.csv",
    "reconciliation": "tables/hierarchical_warehouse_forecasts.csv",
}
COHORT_FIELDS = ["Evaluation_Group", "Evaluation_Period", "Horizon", "Target", "Methodology", "Sample"]


@dataclass
class Comparison:
    scores: pd.DataFrame
    predictions: pd.DataFrame
    metadata: dict
    limitation: str


def table(directory, name, columns):
    frame = read_csv(directory, FILES[name])
    if frame.empty or not set(columns).issubset(frame.columns):
        raise DataIssue(f"{FILES[name]}: empty table or missing columns {sorted(set(columns) - set(frame))}")
    return frame


def validate_predictions(frame):
    """Long model rows; require equal dated actual/predicted samples per entity."""
    frame = frame.copy()
    frame["Date"] = pd.to_datetime(frame.Date, errors="coerce", format="ISO8601")
    if frame.Date.isna().any() or frame[["Model", "Entity"]].isna().any().any():
        raise DataIssue("Invalid dated prediction identifiers.")
    for column in ["Actual", "Prediction"]:
        frame[column] = pd.to_numeric(frame[column], errors="coerce")
        if not frame[column].map(lambda v: pd.notna(v) and float('-inf') < v < float('inf')).all():
            raise DataIssue(f"Non-finite {column} in prediction export.")
    if frame.duplicated(["Entity", "Date", "Model"]).any():
        raise DataIssue("Duplicate entity/model/date predictions.")
    if frame.groupby(["Entity", "Date"]).Actual.nunique().gt(1).any():
        raise DataIssue("Conflicting actual observations across model predictions.")
    for _, entity in frame.groupby("Entity"):
        dates = [set(group.Date) for _, group in entity.groupby("Model")]
        if dates and any(d != dates[0] for d in dates):
            raise DataIssue("Prediction dates are not aligned across models.")
    return frame.sort_values(["Entity", "Model", "Date"]).reset_index(drop=True)


def aggregate_predictions(directory, years):
    frame = table(directory, "weekly", ["Date", "Year", "Evaluation", "Actual", "Prediction", "Model"])
    frame = frame.loc[frame.Year.isin(years)].copy()
    if frame.empty:
        raise DataIssue("No predictions for the selected evaluation years.")
    dates = pd.to_datetime(frame.Date, errors="coerce", format="ISO8601")
    expected = frame.Year.map({2014: "Retrospective validation", 2015: "Retrospective validation",
                              2016: "2016 final holdout (reference)"})
    if not dates.dt.year.eq(frame.Year).all() or not frame.Evaluation.eq(expected).all():
        raise DataIssue("Prediction dates or evaluation labels disagree with the selected cohort.")
    if not frame.groupby(["Year", "Model"]).size().eq(52).all():
        raise DataIssue("Incomplete year-ahead prediction export; expected 52 model-weeks per year.")
    frame["Entity"] = "Aggregate demand"
    return validate_predictions(frame[["Date", "Entity", "Model", "Actual", "Prediction"]])


def recursive_predictions(directory, horizon, warehouse=None):
    frame = table(directory, "recursive_predictions", ["Week", "Warehouse", "Horizon_Week", "Demand", "Recursive_XGBoost", "Seasonal_Naive"])
    frame = frame.loc[frame.Horizon_Week.le(horizon)]
    if warehouse is not None:
        frame = frame.loc[frame.Warehouse.eq(warehouse)]
    if frame.empty or not frame.groupby("Warehouse").Horizon_Week.apply(lambda s: sorted(s) == list(range(1, horizon + 1))).all():
        raise DataIssue("Incomplete recursive horizon observations.")
    frame = frame.rename(columns={"Week": "Date", "Warehouse": "Entity", "Demand": "Actual"})
    frame = frame.melt(id_vars=["Date", "Entity", "Actual"], value_vars=["Recursive_XGBoost", "Seasonal_Naive"],
                       var_name="Model", value_name="Prediction")
    frame.Model = frame.Model.map({"Recursive_XGBoost": "Recursive XGBoost", "Seasonal_Naive": "Seasonal Naive"})
    return validate_predictions(frame)


def reconciliation_predictions(directory, warehouse):
    frame = table(directory, "reconciliation", ["Week", "Warehouse", "Demand", "Original_Nonnegative", "Reconciled_Forecast"])
    frame = frame.loc[frame.Warehouse.eq(warehouse)].rename(columns={"Week": "Date", "Warehouse": "Entity", "Demand": "Actual"})
    if frame.empty:
        raise DataIssue("No reconciliation predictions for the selected warehouse.")
    frame = frame.melt(id_vars=["Date", "Entity", "Actual"], value_vars=["Original_Nonnegative", "Reconciled_Forecast"],
                       var_name="Model", value_name="Prediction")
    frame.Model = frame.Model.map({"Original_Nonnegative": "Original nonnegative warehouse forecast",
                                  "Reconciled_Forecast": "Reconciled warehouse forecast"})
    return validate_predictions(frame)


def load_comparison(directory, group, *, fold="Pooled 2014–2015", warehouse="Whse_A", horizon=12, recursive_scope="Pooled eligible warehouses"):
    if group not in GROUPS:
        raise DataIssue("Unknown evaluation group.")
    predictions = pd.DataFrame(columns=["Date", "Entity", "Model", "Actual", "Prediction"])
    metadata = {"Evaluation_Group": group, "Target": "Aggregate weekly order demand", "Methodology": "Fixed-origin year-ahead evaluation"}
    limitation = "The 2016 holdout was revisited for exploratory model comparison. It is not independent post-selection validation. Weekly predictions are exported for only three of the eight summary models."
    if group == GROUPS[0]:
        scores = table(directory, "holdout", ["Model"])
        predictions = aggregate_predictions(directory, [2016])
        metadata.update(Evaluation_Period="2016-01-03 to 2016-12-25", Horizon="52 weeks ahead", Sample="52 aggregate weeks", Source=FILES["holdout"], Prediction_Source=FILES["weekly"])
    elif group == GROUPS[1]:
        if fold not in ["Pooled 2014–2015", "2014", "2015"]:
            raise DataIssue("Select a retrospective fold or the exported pooled cohort.")
        years = [2014, 2015] if fold == "Pooled 2014–2015" else [int(fold)]
        predictions = aggregate_predictions(directory, years)
        if len(years) == 2:
            scores = table(directory, "pooled", ["Model", "Validation_Years", "Weeks"])
            if not scores.Validation_Years.eq("2014-2015").all() or not scores.Weeks.eq(104).all():
                raise DataIssue("Pooled summary does not match the 2014–2015 cohort.")
            source = FILES["pooled"]
            period = "2014-01-05 to 2014-12-28; 2015-01-04 to 2015-12-27"
        else:
            scores = table(directory, "yearly", ["Model", "Year", "Evaluation", "Forecast_Weeks"])
            scores = scores.loc[scores.Year.eq(years[0])].copy()
            if scores.empty or not scores.Evaluation.eq("Retrospective validation").all() or not scores.Forecast_Weeks.eq(52).all():
                raise DataIssue("Retrospective summary does not match the selected fold.")
            source = FILES["yearly"]
            period = f"{predictions.Date.min():%Y-%m-%d} to {predictions.Date.max():%Y-%m-%d}"
        metadata.update(Evaluation_Period=period, Horizon="52 weeks per forecast origin", Sample=f"{52 * len(years)} aggregate weeks", Source=source, Prediction_Source=FILES["weekly"])
        limitation = "2014–2015 are retrospective diagnostics. ETS configuration was selected on these same folds. Pooled metrics use all 104 weekly errors, not an average of annual WAPE or RMSE. The pooled sample is two separate year-ahead forecasts, not one 104-week forecast."
    elif group == GROUPS[2]:
        scores = table(directory, "warehouse", ["Warehouse", "Model", "Test_Weeks"])
        scores = scores.loc[scores.Warehouse.eq(warehouse)].copy()
        if scores.empty or scores.Test_Weeks.nunique() != 1:
            raise DataIssue("No comparable rolling scores for the selected warehouse.")
        expected_weeks = 51 if warehouse == "Whse_J" else 52
        if not scores.Test_Weeks.eq(expected_weeks).all():
            raise DataIssue("Warehouse rolling sample differs from reviewed coverage.")
        metadata.update(Target=f"Weekly order demand · {warehouse}", Methodology="Warehouse rolling one-step evaluation",
                        Evaluation_Period=f"2016-01-{'10' if warehouse == 'Whse_J' else '03'} to 2016-12-25",
                        Horizon="One step ahead at rolling origins", Sample=f"{expected_weeks} warehouse-weeks · {warehouse}",
                        Source=FILES["warehouse"], Prediction_Source="Complete matching rolling prediction CSV unavailable")
        limitation = "Compare models within this warehouse only. A/C/S have 52 weeks; J has 51. Rolling forecasts use a different information set from aggregate year-ahead and fixed-origin recursive forecasts. Exact rolling fit/update details are not exported. Dates are corroborated by the original HTML trace timestamps; scores come from CSV."
    else:
        if horizon not in [4, 8, 12]:
            raise DataIssue("Available recursive evaluation horizons are 4, 8 and 12 weeks.")
        pooled = recursive_scope == "Pooled eligible warehouses"
        if not pooled and recursive_scope not in ["Whse_A", "Whse_C", "Whse_S"]:
            raise DataIssue("Whse_J is not eligible for the recursive backtest.")
        predictions = recursive_predictions(directory, horizon, None if pooled else recursive_scope)
        if pooled:
            scores = table(directory, "recursive_summary", ["Model", "Horizon_Weeks", "Observations"])
            scores = scores.loc[scores.Horizon_Weeks.eq(horizon)].copy()
            source = FILES["recursive_summary"]
        elif horizon == 12:
            scores = table(directory, "recursive_warehouse", ["Model", "Warehouse", "Observations"])
            scores = scores.loc[scores.Warehouse.eq(recursive_scope)].copy()
            source = FILES["recursive_warehouse"]
        else:
            # Per-warehouse 4/8-week summary metrics are not exported. Never invent them.
            scores = pd.DataFrame(columns=["Model"])
            source = "Per-warehouse 4/8-week summary scores not exported"
        metadata.update(Target=f"Warehouse weekly order demand · {recursive_scope}", Methodology="Fixed-origin recursive validation; seasonal benchmark on identical rows",
                        Evaluation_Period=f"{predictions.Date.min():%Y-%m-%d} to {predictions.Date.max():%Y-%m-%d}",
                        Horizon=f"Cumulative first {horizon} forecast weeks", Sample=f"{predictions[['Entity', 'Date']].drop_duplicates().shape[0]} warehouse-weeks",
                        Source=source, Prediction_Source=FILES["recursive_predictions"], Forecast_Origin="End of 2015; exact origin date not exported")
        limitation = "Retrospective recursive diagnostic, not the 2016 aggregate annual holdout. Whse_J was excluded because 52 consecutive historical weeks were unavailable before the origin. Warehouse outcomes vary substantially. Observed 2017 outcomes are unavailable, so this does not directly validate future forecasts."
    scores = scores.copy()
    scores["Model_Type"] = scores.Model.map(MODEL_TYPES).fillna("Type unverified in reviewed metadata")
    for key, value in metadata.items():
        scores[key] = value
    return Comparison(scores, predictions, metadata, limitation)


def available_metrics(scores):
    return [metric for metric in METRICS if metric in scores and not scores.empty]


def rank_models(scores, metric, selected=None):
    if metric not in METRICS or metric not in scores:
        raise DataIssue("Selected metric is not exported for this cohort.")
    if not set(COHORT_FIELDS).issubset(scores):
        raise DataIssue("Comparison metadata is incomplete; ranking is not allowed.")
    # Check the original cohort BEFORE model filters, so filtering cannot hide mixed tasks.
    if any(scores[column].isna().any() or scores[column].nunique() != 1 for column in COHORT_FIELDS):
        raise DataIssue("Mixed evaluation periods, horizons, targets or methodologies cannot be ranked together.")
    frame = scores.loc[scores.Model.isin(selected)].copy() if selected is not None else scores.copy()
    if frame.empty:
        return frame
    if frame.Model.isna().any() or frame.Model.duplicated().any():
        raise DataIssue("Ambiguous model rows; select one evaluation cohort first.")
    values = pd.to_numeric(frame[metric], errors="coerce")
    if not values.map(lambda v: pd.notna(v) and 0 <= v < float('inf')).all():
        raise DataIssue("Missing or invalid exported metric; rankings are unavailable.")
    frame[metric] = values
    frame["Rank"] = values.rank(method="min").astype(int)
    return frame.sort_values([metric, "Model"]).reset_index(drop=True)
