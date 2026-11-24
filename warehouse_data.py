"""Warehouse actuals and rolling scores remain distinct evaluation samples."""
import pandas as pd

from comparison_data import GROUPS, METRICS, load_comparison, rank_models
from data_loading import DataIssue
from historical_data import coverage, load_history, variability

WAREHOUSES = ["Whse_A", "Whse_C", "Whse_J", "Whse_S"]
ACTUAL_SOURCE = "tables/hierarchical_warehouse_forecasts.csv"
SCORE_SOURCE = "tables/dashboard_performance_summary.csv"


def load_warehouse_actuals(directory):
    frame = load_history(directory, "Warehouse sample")
    if set(frame.Series) != set(WAREHOUSES):
        raise DataIssue("Warehouse history does not contain the four reviewed warehouses.")
    expected_dates = set(pd.date_range("2016-01-10", "2016-12-25", freq="W-SUN"))
    for warehouse, rows in frame.groupby("Series"):
        if set(rows.Date) != expected_dates:
            raise DataIssue(f"{warehouse}: coverage differs from the reviewed Jan 10–Dec 25, 2016 sample.")
    return frame


def warehouse_statistics(frame):
    if frame.empty:
        raise DataIssue("Select at least one warehouse for statistics.")
    result = variability(frame).merge(coverage(frame), on=["Series", "Year", "Observed_Weeks"], validate="one_to_one")
    peaks = frame.loc[frame.groupby("Series").Demand.idxmax(), ["Series", "Date"]].rename(columns={"Date": "Peak_Observed_Week"})
    result = result.merge(peaks, on="Series", validate="one_to_one")
    total = result.Observed_Sum.sum()
    result["Selected_Demand_Share_Pct"] = result.Observed_Sum / total * 100 if total > 0 else float("nan")
    return result.rename(columns={"Series": "Warehouse"})


def aligned_actuals(frame, warehouses):
    """Only dates observed for every selected warehouse; never fill gaps."""
    selected = frame.loc[frame.Series.isin(warehouses)].copy()
    if not warehouses:
        return selected
    if set(selected.Series) != set(warehouses):
        raise DataIssue("Requested warehouse observations are unavailable.")
    if selected.duplicated(["Series", "Date"]).any():
        raise DataIssue("Duplicate warehouse/date observations.")
    counts = selected.groupby("Date").Series.nunique()
    return selected.loc[selected.Date.isin(counts.loc[counts.eq(len(set(warehouses)))].index)].copy()


def warehouse_rankings(directory, warehouses, metric):
    if metric not in METRICS:
        raise DataIssue("Unsupported warehouse performance metric.")
    if not warehouses or not set(warehouses).issubset(WAREHOUSES):
        raise DataIssue("Select one or more reviewed warehouses.")
    results = []
    for warehouse in warehouses:
        comparison = load_comparison(directory, GROUPS[2], warehouse=warehouse)
        if set(comparison.scores.Model) != {"Naive", "Random Forest", "XGBoost"}:
            raise DataIssue(f"{warehouse}: expected the reviewed Naive, Random Forest and XGBoost cohort.")
        # Rank each target/sample independently. Never pass multiple warehouses to rank_models.
        ranked = rank_models(comparison.scores, metric).rename(columns={"Rank": "Rank_Within_Warehouse"})
        results.append(ranked)
    return pd.concat(results, ignore_index=True)
