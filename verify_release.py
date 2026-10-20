"""Offline release preflight; requires pandas and Plotly but not Streamlit.

Run from the project root: python verify_release.py
Does not write to or recalculate the original Capstone CSV exports.
"""
import ast
from hashlib import sha256
import json
from pathlib import Path

import pandas as pd

from data_loading import ROOT, source_directory
from future_data import (WAREHOUSES, HORIZONS, WEEKLY_SOURCE, SUMMARY_SOURCE,
                         validate_weekly, reconcile_summary, combined_summaries)
from overview_data import load_overview, holdout_kpis


def run():
    root = ROOT
    sources = source_directory()
    if not sources.exists():
        raise AssertionError(f"Missing source folder: {sources}")

    for file in root.glob("*.py"):
        ast.parse(file.read_text(encoding="utf-8"), filename=file.name)
    print("PASS: Python syntax parsed for all project source modules")

    recorded = json.loads((root / "docs/source_hashes_before.json").read_text(encoding="utf-8"))
    assert len(recorded) == 87, f"Expected 87 archival source hashes, got {len(recorded)}"
    for relative, original_digest in recorded.items():
        local = root / relative
        assert local.is_file(), f"Missing original file: {relative}"
        assert sha256(local.read_bytes()).hexdigest() == original_digest, f"Changed original file: {relative}"
    print(f"PASS: {len(recorded)} unchanged original Capstone files (SHA-256)")

    holdout = load_overview(sources)
    metrics = holdout_kpis(holdout)
    assert metrics["weeks"] == 52
    assert metrics["best_model"] == "TimesFM 3.0"
    assert 12.34 < metrics["best_wape"] < 12.36
    assert len(holdout["holdout"]) == 8
    print(f"PASS: 2016 aggregate holdout · {metrics['weeks']} weeks · {metrics['best_model']} {metrics['best_wape']:.4f}% WAPE")

    actuals = (holdout["weekly"][["Year", "Date", "Actual"]].drop_duplicates())
    assert actuals.groupby("Year").size().to_dict() == {2014: 52, 2015: 52, 2016: 52}
    print("PASS: 2014–2016 recorded aggregate weeks count distinct actuals once")

    weekly = validate_weekly(pd.read_csv(sources / WEEKLY_SOURCE))
    summary = pd.read_csv(sources / SUMMARY_SOURCE)
    checks = reconcile_summary(weekly, summary)
    assert len(weekly) == 48
    assert set(weekly.Warehouse) == set(WAREHOUSES)
    assert set(weekly.Horizon_Week) == set(range(1, 13))
    assert len(checks) == 36
    assert checks.Absolute_Difference.max() < .00001
    totals = combined_summaries(weekly, WAREHOUSES)
    expected = {4: 69.25, 8: 145.4, 12: 223.72}
    for horizon in HORIZONS:
        millions = float(totals.loc[totals.Horizon_Weeks.eq(horizon), "Projected_Total_Demand"].iloc[0]) / 1e6
        assert abs(millions - expected[horizon]) < .01, (horizon, millions)
    print("PASS: 48 archived warehouse/week projections · 36 summary reconciliations · historical origin")
    print("OFFLINE PRECHECK PASSED. Execute full Streamlit/AppTest suite on your Windows workstation.")


if __name__ == "__main__":
    run()
