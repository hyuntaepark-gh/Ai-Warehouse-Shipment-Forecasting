from navigation import ROUTES, LABELS
"""Real archived projections, cumulative arithmetic, coverage and missing-data guards."""
import json
import unittest
from unittest.mock import patch

import pandas as pd
from streamlit.testing.v1 import AppTest

from data_loading import DataIssue, ROOT, read_csv, source_directory
from future_data import (HORIZONS, ORIGIN, SUMMARY_SOURCE, TOLERANCE_UNITS, WAREHOUSES, WEEKLY_SOURCE,
                         combined_summaries, forecast_views, load_archive, reconcile_summary,
                         select_records, validate_weekly, warehouse_summaries)


class FutureDataTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.directory = source_directory()
        cls.archive = load_archive(cls.directory)
        cls.weekly = cls.archive["weekly"]

    def test_origin_horizon_dates_and_complete_four_warehouse_coverage(self):
        self.assertEqual(len(self.weekly), 48)
        self.assertTrue(self.weekly.Forecast_Origin.eq(ORIGIN).all())
        self.assertEqual(set(self.weekly.Warehouse), set(WAREHOUSES))
        self.assertEqual(self.weekly.Week.min(), pd.Timestamp("2017-01-01"))
        self.assertEqual(self.weekly.Week.max(), pd.Timestamp("2017-03-19"))
        for _, frame in self.weekly.groupby("Warehouse"):
            self.assertEqual(frame.Horizon_Week.tolist(), list(range(1, 13)))

    def test_horizon_filters_and_cumulative_projection_arithmetic(self):
        for horizon in HORIZONS:
            detail, combined = forecast_views(self.weekly, ["Whse_A", "Whse_J"], horizon)
            self.assertEqual(len(detail), horizon * 2)
            self.assertEqual(len(combined), horizon)
            self.assertTrue(combined.Warehouse_Count.eq(2).all())
            for _, group in detail.groupby("Warehouse"):
                self.assertAlmostEqual(group.Cumulative_Projected_Demand.iloc[-1], group.Predicted_Demand.sum(), places=6)
                self.assertTrue(group.Cumulative_Projected_Demand.diff().dropna().ge(0).all())
            self.assertAlmostEqual(combined.Cumulative_Projected_Demand.iloc[-1], detail.Predicted_Demand.sum(), places=6)

    def test_combined_peak_is_peak_of_weekly_sums(self):
        summaries = combined_summaries(self.weekly, WAREHOUSES)
        for row in summaries.itertuples():
            frame = select_records(self.weekly, WAREHOUSES, row.Horizon_Weeks)
            by_week = frame.groupby("Week").Predicted_Demand.sum()
            self.assertEqual(row.Peak_Weekly_Demand, by_week.max())
            self.assertEqual(row.Average_Weekly_Demand, by_week.mean())
            self.assertEqual(row.Projected_Total_Demand, by_week.sum())
        separate_peaks = self.weekly.groupby("Warehouse").Predicted_Demand.max().sum()
        self.assertNotEqual(summaries.iloc[-1].Peak_Weekly_Demand, separate_peaks)

    def test_contributions_use_selected_warehouse_horizon_denominators(self):
        for selected in [WAREHOUSES, ["Whse_A", "Whse_C"], ["Whse_J"]]:
            summary = warehouse_summaries(self.weekly, selected)
            self.assertEqual(len(summary), len(selected) * 3)
            for _, group in summary.groupby("Horizon_Weeks"):
                self.assertAlmostEqual(group.Contribution_Pct.sum(), 100, places=10)
                expected = group.Projected_Total_Demand / group.Projected_Total_Demand.sum() * 100
                self.assertTrue(expected.eq(group.Contribution_Pct).all())

    def test_all_36_summary_checks_and_operational_quantity_context_agree(self):
        checks = self.archive["checks"]
        self.assertEqual(len(checks), 36)
        self.assertTrue(checks.Absolute_Difference.le(TOLERANCE_UNITS).all())
        operational = read_csv(self.directory, "tables/future_operational_decision_summary.csv")
        calculated = warehouse_summaries(self.weekly, WAREHOUSES)
        paired = calculated.merge(operational, on=["Warehouse", "Horizon_Weeks"], suffixes=("_Computed", "_Exported"))
        for metric in ["Projected_Total_Demand", "Average_Weekly_Demand", "Peak_Weekly_Demand"]:
            self.assertTrue((paired[metric + "_Computed"] - paired[metric + "_Exported"]).abs().le(TOLERANCE_UNITS).all())

    def test_missing_warehouse_or_week_rejected_before_aggregation(self):
        for frame in [self.weekly.iloc[1:], self.weekly.loc[self.weekly.Warehouse.ne("Whse_J")]]:
            with self.assertRaises(DataIssue):
                validate_weekly(frame)
            with self.assertRaises(DataIssue):
                forecast_views(frame, ["Whse_A"], 4)

    def test_invalid_origin_date_and_horizon_rejected(self):
        for column, value in [("Forecast_Origin", pd.Timestamp("2016-12-18")), ("Week", pd.Timestamp("2017-01-02")), ("Horizon_Week", 1.5)]:
            frame = self.weekly.copy()
            if column == "Horizon_Week":
                frame[column] = frame[column].astype(float)
            frame.loc[0, column] = value
            with self.subTest(column=column), self.assertRaises(DataIssue):
                validate_weekly(frame)
        with self.assertRaises(DataIssue):
            select_records(self.weekly, WAREHOUSES, 6)

    def test_duplicate_nonfinite_negative_and_unknown_rows_rejected(self):
        with self.assertRaises(DataIssue):
            validate_weekly(pd.concat([self.weekly, self.weekly.iloc[[0]]]))
        for value in [float("nan"), float("inf"), -1]:
            frame = self.weekly.copy()
            frame.loc[0, "Predicted_Demand"] = value
            with self.assertRaises(DataIssue):
                validate_weekly(frame)
        with self.assertRaises(DataIssue):
            select_records(self.weekly, ["Unknown"], 12)
        with self.assertRaises(DataIssue):
            select_records(self.weekly, [], 12)

    def test_summary_missing_rows_duplicates_or_mismatch_are_rejected(self):
        summary = self.archive["summary"]
        bad = summary.copy()
        bad.loc[0, "Projected_Total_Demand"] += 1
        for frame in [bad, summary.iloc[1:], pd.concat([summary, summary.iloc[[0]]])]:
            with self.assertRaises(DataIssue):
                reconcile_summary(self.weekly, frame)

    def test_projection_outputs_do_not_invent_actuals_bounds_or_risk(self):
        detail, combined = forecast_views(self.weekly, WAREHOUSES, 12)
        for frame in [detail, combined]:
            self.assertFalse(set(frame) & {"Actual", "Demand", "Lower", "Upper", "Historical_P90", "Illustrative_Risk_Level"})
            self.assertTrue(frame.Type.str.contains("projected demand").all())
        original = detail.to_csv(index=False)
        from display_formatting import readable_table
        pd.testing.assert_frame_equal(readable_table(detail).data, detail)
        self.assertEqual(detail.to_csv(index=False), original)


class FutureAppTests(unittest.TestCase):
    def test_horizon_warehouse_cumulative_and_empty_selection_filters(self):
        app = AppTest.from_file(str(ROOT / "app.py")).run(timeout=30)
        app.sidebar.button(key="nav_" + "Future Forecasting").click().run(timeout=30)
        self.assertFalse(app.exception)
        self.assertFalse(app.error)
        self.assertEqual(len(app.sidebar.button), 8)
        self.assertEqual(len(app.get("plotly_chart")), 2)
        self.assertFalse(any("unavailable:" in w.value for w in app.warning))
        self.assertTrue(any("not current forecasts" in w.value for w in app.warning))
        self.assertTrue(any(m.label == "Selected forecast coverage" and m.value == "48 records" for m in app.metric))
        for horizon in HORIZONS:
            next(r for r in app.selectbox if r.label == "Forecast horizon (weeks)").set_value(horizon).run(timeout=30)
            self.assertFalse(app.exception)
            self.assertTrue(any(m.label == "Selected forecast coverage" and m.value == f"{4 * horizon} records" for m in app.metric))
        next(r for r in app.selectbox if r.label == "Projection view").set_value("Cumulative").run(timeout=30)
        app.multiselect[0].set_value(["Whse_A", "Whse_J"]).run(timeout=30)
        app.checkbox[0].set_value(False).run(timeout=30)
        self.assertFalse(app.exception)
        self.assertFalse(app.error)
        for element in app.get("plotly_chart"):
            spec = json.loads(element.proto.spec)
            self.assertFalse(spec.get("layout", {}).get("xaxis", {}).get("rangeslider", {}).get("visible", False))
            self.assertTrue(all(trace.get("fill") in [None, "none"] for trace in spec["data"]))
        app.multiselect[0].set_value([]).run(timeout=30)
        self.assertTrue(any("Select at least one warehouse" in i.value for i in app.info))

    def test_partial_forecast_source_withholds_totals(self):
        weekly = read_csv(source_directory(), WEEKLY_SOURCE).iloc[1:]
        original_reader = read_csv
        def reader(directory, name):
            return weekly.copy() if name == WEEKLY_SOURCE else original_reader(directory, name)
        app = AppTest.from_file(str(ROOT / "app.py")).run(timeout=30)
        with patch("future_data.read_csv", side_effect=reader):
            app.sidebar.button(key="nav_" + "Future Forecasting").click().run(timeout=30)
        self.assertFalse(app.exception)
        self.assertTrue(any("Future forecasting data unavailable" in w.value for w in app.warning))
        self.assertEqual(len(app.metric), 0)
        self.assertEqual(len(app.get("plotly_chart")), 0)

    def test_missing_backtest_evidence_does_not_disable_valid_forecast_archive(self):
        app = AppTest.from_file(str(ROOT / "app.py")).run(timeout=30)
        with patch("future_forecasting.evidence", side_effect=DataIssue("Missing backtest source")):
            app.sidebar.button(key="nav_" + "Future Forecasting").click().run(timeout=30)
        self.assertFalse(app.exception)
        self.assertEqual(len(app.get("plotly_chart")), 2)
        self.assertTrue(any("Historical reliability evidence unavailable" in w.value for w in app.warning))
        self.assertTrue(any(m.label == "Selected forecast coverage" and m.value == "48 records" for m in app.metric))


if __name__ == "__main__":
    unittest.main()
