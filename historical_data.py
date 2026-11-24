"""Actual-demand observations only; no interpolation, forecast values or model fits."""
import pandas as pd

from data_loading import DataIssue, read_csv

SOURCES = {
    "Aggregate demand": "tables/timesfm_historical_weekly_predictions.csv",
    "Warehouse sample": "tables/hierarchical_warehouse_forecasts.csv",
}
LEVELS = {"Weekly": None, "Monthly": "M", "Quarterly": "Q", "Annual": "Y"}


def load_history(directory, scope):
    if scope not in SOURCES:
        raise DataIssue("Unknown historical demand scope.")
    frame = read_csv(directory, SOURCES[scope])
    columns = (["Date", "Actual", "Year", "Evaluation", "Model"] if scope == "Aggregate demand"
               else ["Week", "Warehouse", "Demand"])
    missing = set(columns) - set(frame)
    if missing or frame.empty:
        raise DataIssue(f"{SOURCES[scope]}: empty history or missing columns {sorted(missing)}")
    dates = pd.to_datetime(frame[columns[0]], errors="coerce", format="ISO8601")
    values = pd.to_numeric(frame["Actual" if scope == "Aggregate demand" else "Demand"], errors="coerce")
    if dates.isna().any() or not values.map(lambda x: pd.notna(x) and float('-inf') < x < float('inf')).all():
        raise DataIssue("Historical observations contain invalid dates or non-finite demand.")
    frame = frame.assign(Date=dates, Demand=values)
    if scope == "Aggregate demand":
        if frame[["Year", "Evaluation", "Model"]].isna().any().any():
            raise DataIssue("Aggregate history is missing source evaluation labels.")
        if not pd.to_numeric(frame.Year, errors="coerce").eq(frame.Date.dt.year).all():
            raise DataIssue("Source Year disagrees with the recorded date.")
        if frame.groupby("Date").Demand.nunique().gt(1).any():
            raise DataIssue("Conflicting actual demand repeated across forecast models.")
        if frame.groupby("Date").Evaluation.nunique().gt(1).any():
            raise DataIssue("Conflicting evaluation labels for an actual-demand timestamp.")
        # Actual values repeat per forecast model. Count each recorded date exactly once.
        frame = frame[["Date", "Demand", "Evaluation"]].drop_duplicates()
        frame["Series"] = "Aggregate actual demand"
    else:
        if frame.Warehouse.isna().any():
            raise DataIssue("Historical warehouse observations contain a missing warehouse.")
        frame["Series"] = frame.Warehouse.astype(str)
        frame["Evaluation"] = "2016 common-period warehouse sample"
        frame = frame[["Date", "Demand", "Series", "Evaluation"]]
        if frame.duplicated(["Date", "Series"]).any():
            raise DataIssue("Duplicate warehouse-week observations; cannot safely aggregate.")
    frame["Year"] = frame.Date.dt.year
    return frame.sort_values(["Series", "Date"]).reset_index(drop=True)


def aggregate_history(frame, level):
    """Group only observed rows. Missing periods remain absent, never zero-filled."""
    if level not in LEVELS:
        raise DataIssue("Unknown aggregation level.")
    frame = frame.copy()
    frame["Period"] = (frame.Date if level == "Weekly" else
                       frame.Date.dt.to_period(LEVELS[level]).dt.to_timestamp())
    result = frame.groupby(["Series", "Year", "Period"], as_index=False).agg(
        Demand=("Demand", "sum"), Observations=("Demand", "size"),
        First_Observation=("Date", "min"), Last_Observation=("Date", "max"))
    result["Type"] = "Actual demand" if level == "Weekly" else "Aggregated actual demand"
    return result.sort_values(["Series", "Period"]).reset_index(drop=True)


def coverage(frame):
    rows = []
    for (series, year), group in frame.groupby(["Series", "Year"]):
        dates = group.Date.sort_values()
        # This records observed gaps only between first and last export timestamps.
        gaps = int(dates.diff().gt(pd.Timedelta(7, unit="D")).sum())
        rows.append({"Series": series, "Year": int(year), "Observed_Weeks": len(group),
                     "First_Observation": dates.min(), "Last_Observation": dates.max(),
                     "Gaps_Over_7_Days": gaps, "Evaluation": "; ".join(sorted(group.Evaluation.unique()))})
    return pd.DataFrame(rows)


def variability(frame):
    result = frame.groupby(["Series", "Year"], as_index=False).agg(
        Observed_Weeks=("Demand", "size"), Observed_Sum=("Demand", "sum"),
        Mean_Weekly_Demand=("Demand", "mean"), Weekly_Std_Dev=("Demand", "std"),
        Min_Weekly_Demand=("Demand", "min"), Max_Weekly_Demand=("Demand", "max"))
    result["CV"] = result.Weekly_Std_Dev.div(result.Mean_Weekly_Demand.where(result.Mean_Weekly_Demand.gt(0)))
    return result


def seasonal_profile(frame):
    frame = frame.assign(Month=frame.Date.dt.month)
    return frame.groupby(["Series", "Year", "Month"], as_index=False).agg(
        Mean_Weekly_Demand=("Demand", "mean"), Observed_Weeks=("Demand", "size"))


def trend_with_gaps(aggregated, level):
    """Insert null separators solely for plotting gaps; never create demand values."""
    segments = []
    for _, group in aggregated.groupby("Series"):
        group = group.sort_values("Period")
        previous = None
        for row in group.to_dict("records"):
            if previous is not None:
                expected = (previous + pd.Timedelta(7, unit="D") if level == "Weekly" else
                            (previous.to_period(LEVELS[level]) + 1).start_time)
                if row["Period"] > expected:
                    segments.append({"Series": row["Series"], "Period": expected, "Demand": None})
            segments.append(row)
            previous = row["Period"]
    return pd.DataFrame(segments)
