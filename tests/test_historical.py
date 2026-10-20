from navigation import ROUTES, LABELS
"""Actual-export tests and defensive tests for historical-only aggregations."""
import unittest
from unittest.mock import patch

import pandas as pd
from streamlit.testing.v1 import AppTest

from data_loading import DataIssue, ROOT, read_csv, source_directory
from historical_data import (LEVELS, SOURCES, aggregate_history, coverage, load_history,
                             seasonal_profile, trend_with_gaps, variability)


class HistoricalDataTests(unittest.TestCase):
    def setUp(self):
        self.directory = source_directory()

    def test_aggregate_actuals_are_counted_once_and_predictions_excluded(self):
        raw = read_csv(self.directory, SOURCES["Aggregate demand"])
        actual = load_history(self.directory, "Aggregate demand")
        self.assertEqual(len(actual), 156)
        self.assertEqual(actual.groupby("Year").size().to_dict(), {2014: 52, 2015: 52, 2016: 52})
        self.assertAlmostEqual(actual.Demand.sum(), raw.Actual.sum() / raw.Model.nunique())
        self.assertFalse(set(actual) & {"Prediction", "Error", "Model"})
        self.assertEqual(set(actual.Evaluation), {"Retrospective validation", "2016 final holdout (reference)"})

    def test_all_aggregations_preserve_observed_totals_and_counts(self):
        for scope in SOURCES:
            actual = load_history(self.directory, scope)
            for level in LEVELS:
                with self.subTest(scope=scope, level=level):
                    grouped = aggregate_history(actual, level)
                    self.assertAlmostEqual(grouped.Demand.sum(), actual.Demand.sum())
                    self.assertEqual(grouped.Observations.sum(), len(actual))
                    self.assertEqual(set(grouped.Type), {"Actual demand" if level == "Weekly" else "Aggregated actual demand"})

    def test_monthly_actual_totals_agree_with_existing_export(self):
        actual = load_history(self.directory, "Aggregate demand")
        monthly = aggregate_history(actual, "Monthly")
        exported = read_csv(self.directory, "tables/timesfm_historical_monthly_results.csv")
        for row in monthly.itertuples():
            target = exported.loc[exported.Year.eq(row.Year) & exported.Month.eq(row.Period.month)]
            self.assertTrue(target.Actual_Month_Total.eq(row.Demand).all())
            self.assertTrue(target.Weeks.eq(row.Observations).all())

    def test_warehouse_export_has_only_available_partial_year(self):
        actual = load_history(self.directory, "Warehouse sample")
        self.assertEqual(len(actual), 204)
        self.assertEqual(set(actual.Year), {2016})
        self.assertEqual(actual.Series.nunique(), 4)
        self.assertTrue(actual.groupby("Series").size().eq(51).all())
        self.assertEqual(actual.Date.min(), pd.Timestamp("2016-01-10"))
        self.assertEqual(actual.Date.max(), pd.Timestamp("2016-12-25"))
        self.assertFalse(set(actual) & {"XGBoost", "Reconciled_Forecast"})
        quarterly = aggregate_history(actual, "Quarterly")
        self.assertTrue(quarterly.loc[quarterly.Period.dt.quarter.eq(1)].Observations.eq(12).all())

    def test_variability_and_seasonal_means_use_weekly_actuals(self):
        actual = load_history(self.directory, "Aggregate demand")
        frame = actual.loc[actual.Year.eq(2014)]
        summary = variability(frame).iloc[0]
        self.assertAlmostEqual(summary.Weekly_Std_Dev, frame.Demand.std(ddof=1))
        self.assertAlmostEqual(summary.CV, frame.Demand.std(ddof=1) / frame.Demand.mean())
        season = seasonal_profile(frame)
        self.assertEqual(season.Observed_Weeks.sum(), len(frame))
        for row in season.itertuples():
            self.assertAlmostEqual(row.Mean_Weekly_Demand, frame.loc[frame.Date.dt.month.eq(row.Month)].Demand.mean())

    def test_gaps_not_filled_or_connected_and_missing_month_not_zero(self):
        frame = load_history(self.directory, "Aggregate demand")
        frame = frame.loc[frame.Year.eq(2014)].drop(index=1)
        grouped = aggregate_history(frame, "Weekly")
        self.assertEqual(len(grouped), 51)
        plotted = trend_with_gaps(grouped, "Weekly")
        self.assertEqual(plotted.Demand.isna().sum(), 1)
        self.assertEqual(plotted.Demand.sum(), grouped.Demand.sum())
        self.assertEqual(coverage(frame).Gaps_Over_7_Days.iloc[0], 1)
        march_removed = frame.loc[frame.Date.dt.month.ne(3)]
        self.assertNotIn(3, seasonal_profile(march_removed).Month.to_list())

    def test_conflicting_actuals_and_duplicate_warehouse_rows_rejected(self):
        raw = read_csv(self.directory, SOURCES["Aggregate demand"])
        raw.loc[0, "Actual"] += 1
        with patch("historical_data.read_csv", return_value=raw), self.assertRaises(DataIssue):
            load_history(self.directory, "Aggregate demand")
        raw = read_csv(self.directory, SOURCES["Warehouse sample"])
        raw = pd.concat([raw, raw.iloc[[0]]])
        with patch("historical_data.read_csv", return_value=raw), self.assertRaises(DataIssue):
            load_history(self.directory, "Warehouse sample")

    def test_invalid_actual_and_date_rejected_and_cv_undefined(self):
        raw = read_csv(self.directory, SOURCES["Aggregate demand"])
        for column, invalid in [("Actual", float("inf")), ("Date", "invalid")]:
            altered = raw.copy()
            altered.loc[0, column] = invalid
            with patch("historical_data.read_csv", return_value=altered), self.assertRaises(DataIssue):
                load_history(self.directory, "Aggregate demand")
        single = load_history(self.directory, "Aggregate demand").iloc[[0]].copy()
        self.assertTrue(pd.isna(variability(single).CV.iloc[0]))
        single.Demand = 0
        self.assertTrue(pd.isna(variability(single).CV.iloc[0]))


class HistoricalAppTests(unittest.TestCase):
    def test_actual_page_filters_scopes_and_all_aggregation_levels(self):
        app = AppTest.from_file(str(ROOT / "app.py")).run(timeout=30)
        app.sidebar.button(key="nav_" + "Historical Demand").click().run(timeout=30)
        self.assertFalse(app.exception)
        self.assertFalse(app.error)
        self.assertEqual(app.title[0].value, "Demand Trends")
        self.assertEqual(len(app.get("plotly_chart")), 4)
        self.assertFalse(any(m.label == "Historical warehouses" for m in app.multiselect))
        app.multiselect[0].set_value([2014, 2016])
        for level in LEVELS:
            next(s for s in app.selectbox if s.label == "Trend aggregation").set_value(level).run(timeout=30)
            self.assertFalse(app.exception)
            self.assertFalse(app.error)
        next(r for r in app.selectbox if r.label == "Comparison period").set_value("Monthly").run(timeout=30)
        next(r for r in app.selectbox if r.label == "Comparison period").set_value("Quarterly").run(timeout=30)
        self.assertFalse(app.exception)
        app.multiselect[0].set_value([]).run(timeout=30)
        self.assertTrue(any("Select at least one" in i.value for i in app.info))
        next(r for r in app.selectbox if r.label == "Historical data scope").set_value("Warehouse sample").run(timeout=30)
        self.assertFalse(app.exception)
        self.assertEqual(app.multiselect[0].options, ["2016"])
        app.multiselect[1].set_value(["Whse_J"]).run(timeout=30)
        self.assertFalse(app.exception)
        self.assertFalse(app.error)
        self.assertTrue(any("51-week common-period sample" in w.value for w in app.warning))
        app.multiselect[1].set_value([]).run(timeout=30)
        self.assertFalse(app.exception)
        self.assertTrue(any("Select at least one" in i.value for i in app.info))


if __name__ == "__main__":
    unittest.main()
