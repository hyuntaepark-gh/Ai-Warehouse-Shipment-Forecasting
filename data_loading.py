"""Read-only capstone access. No model training, forecasting, or source writes."""
from pathlib import Path
import json
import os

import pandas as pd
from source_catalog import evaluation_context

ROOT = Path(__file__).resolve().parent


class DataIssue(ValueError):
    """An actionable source/configuration problem suitable for display."""


def source_directory():
    return Path(os.environ.get("CAPSTONE_DATA_DIR", ROOT / "capstone_final_outputs")).resolve()


def source_path(directory, relative):
    root = Path(directory).resolve()
    path = (root / relative).resolve()
    if not path.is_relative_to(root):
        raise DataIssue("Source paths must stay inside the capstone directory.")
    if not path.is_file():
        raise DataIssue(f"Missing source file: {relative}")
    return path


def read_csv(directory, relative):
    path = source_path(directory, relative)
    try:
        return pd.read_csv(path, encoding="utf-8-sig")
    except (UnicodeError, pd.errors.ParserError, pd.errors.EmptyDataError, OSError) as exc:
        raise DataIssue(f"Cannot read {relative}: {exc}") from exc


def inventory(directory):
    """Inspect every file and CSV schema; date spans are NOT evaluation periods."""
    root = Path(directory)
    if not root.is_dir():
        return []
    records = []
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        record = {"file": path.relative_to(root).as_posix(), "bytes": path.stat().st_size,
                  "type": path.suffix.lower(), "evaluation_period": "Unverified"}
        if path.suffix.lower() == ".csv":
            record["evaluation_context"] = evaluation_context(record["file"])
            if not record["evaluation_context"]["family"].startswith("Supplementary"):
                record["evaluation_period"] = record["evaluation_context"]["period"]
            try:
                frame = read_csv(root, record["file"])
                record.update(rows=len(frame), columns={c: str(t) for c, t in frame.dtypes.items()},
                              null_counts={c: int(n) for c, n in frame.isna().sum().items()})
                spans = {}
                for column in frame.columns:
                    if any(token in column.lower() for token in ("date", "month", "period", "week", "origin")):
                        # Require explicit calendar strings; never interpret numeric indexes as dates.
                        values = frame[column].dropna().astype(str)
                        if not values.empty and values.str.match(r"^\d{4}-\d{2}(-\d{2})?($|[ T])").all():
                            dates = pd.to_datetime(values, errors="coerce")
                            if dates.notna().all():
                                spans[column] = {"start": str(dates.min().date()), "end": str(dates.max().date())}
                record["observed_date_spans"] = spans
                context_columns = [c for c in frame if c in (
                    "Year", "Evaluation", "Validation_Years", "Historical_Validation_Years", "Forecast_Origin",
                    "Forecast_Weeks", "Test_Weeks", "Horizon_Weeks", "Observations", "Weeks", "Warehouse", "Model")]
                record["exported_context"] = {c: frame[c].dropna().unique().tolist() for c in context_columns}
            except DataIssue as exc:
                record["error"] = str(exc)
        records.append(record)
    return records


def load_manifest(path=None):
    path = Path(path or ROOT / "dashboard_sources.json")
    if not path.exists():
        return {"metrics": [], "charts": []}
    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(manifest, dict) or any(not isinstance(manifest.get(k, []), list) for k in ("metrics", "charts")):
            raise ValueError("Expected an object with metrics and charts lists")
        return manifest
    except (ValueError, OSError) as exc:
        raise DataIssue(f"Invalid dashboard_sources.json: {exc}") from exc


def bound_frame(directory, binding):
    """Require human-reviewed period evidence before displaying any result."""
    required = ("file", "label", "kind", "period_start", "period_end", "period_evidence", "value_column")
    missing = [key for key in required if not binding.get(key)]
    if missing:
        raise DataIssue(f"Source binding missing: {', '.join(missing)}")
    if binding["kind"] not in ("historical", "future"):
        raise DataIssue("Result kind must be historical or future.")
    start, end = pd.Timestamp(binding["period_start"]), pd.Timestamp(binding["period_end"])
    if pd.isna(start) or pd.isna(end) or start > end:
        raise DataIssue("Invalid result period.")
    if binding["kind"] == "historical" and (start.year != 2016 or end.year != 2016):
        raise DataIssue("V1 overview historical bindings must describe 2016 results.")
    if binding["kind"] == "future":
        origin = pd.Timestamp(binding.get("forecast_origin"))
        if pd.isna(origin) or origin.year != 2016 or origin.month != 12 or start <= origin:
            raise DataIssue("Future results require a December 2016 forecast origin preceding the horizon.")
    frame = read_csv(directory, binding["file"])
    for column, value in binding.get("filters", {}).items():
        if column not in frame:
            raise DataIssue(f"Missing filter column: {column}")
        frame = frame.loc[frame[column].astype(str) == str(value)]
    column = binding["value_column"]
    if column not in frame:
        raise DataIssue(f"Missing value column: {column}")
    if binding.get("date_column"):
        date_column = binding["date_column"]
        if date_column not in frame:
            raise DataIssue(f"Missing date column: {date_column}")
        dates = pd.to_datetime(frame[date_column], errors="coerce")
        if dates.isna().any():
            raise DataIssue(f"Invalid or missing dates in {date_column}")
        frame = frame.assign(**{date_column: dates})
        frame = frame.loc[dates.between(start, end)]
    values = pd.to_numeric(frame[column], errors="coerce")
    if frame.empty or values.isna().any() or not values.map(lambda v: float('-inf') < v < float('inf')).all():
        raise DataIssue(f"No complete finite numeric results for {binding['label']}")
    return frame.assign(**{column: values})


def metric_value(directory, binding):
    frame = bound_frame(directory, binding)
    values = frame[binding["value_column"]]
    aggregation = binding.get("aggregation", "single")
    if aggregation == "single":
        if len(values) != 1:
            raise DataIssue("Single metrics require exactly one row; add explicit filters.")
        return float(values.iloc[0])
    if aggregation == "sum":
        return float(values.sum())
    if aggregation == "mean":
        return float(values.mean())
    raise DataIssue("Supported aggregations: single, sum, mean.")
