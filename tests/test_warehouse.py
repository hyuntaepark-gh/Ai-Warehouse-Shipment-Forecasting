from navigation import ROUTES, LABELS
"""Warehouse actuals, scoped model cohorts and page regressions use original CSVs."""
import json
import unittest
from unittest.mock import patch

import pandas as pd
from streamlit.testing.v1 import AppTest

from comparison_data import METRICS, reconciliation_predictions
from data_loading import DataIssue, ROOT, read_csv, source_directory
from warehouse_data import (ACTUAL_SOURCE, SCORE_SOURCE, WAREHOUSES, aligned_actuals,
                            load_warehouse_actuals, warehouse_rankings, warehouse_statistics)


class WarehouseDataTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.directory = source_directory()
        cls.history = load_warehouse_actuals(cls.directory)

    def test_actual_coverage_and_all_warehouse_statistics(self):
        raw = read_csv(self.directory, ACTUAL_SOURCE)
        stats = warehouse_statistics(self.history).set_index("Warehouse")
        self.assertEqual(set(stats.index), set(WAREHOUSES))
        self.assertEqual(len(self.history), 204)
        self.assertTrue(stats.Observed_Weeks.eq(51).all())
        self.assertTrue(stats.First_Observation.eq(pd.Timestamp("2016-01-10")).all())
        self.assertTrue(stats.Last_Observation.eq(pd.Timestamp("2016-12-25")).all())
        self.assertTrue(stats.Gaps_Over_7_Days.eq(0).all())
        for warehouse in WAREHOUSES:
            observations = raw.loc[raw.Warehouse.eq(warehouse)]
            self.assertAlmostEqual(stats.loc[warehouse, "Observed_Sum"], observations.Demand.sum())
            self.assertAlmostEqual(stats.loc[warehouse, "Mean_Weekly_Demand"], observations.Demand.mean())
            self.assertAlmostEqual(stats.loc[warehouse, "Weekly_Std_Dev"], observations.Demand.std(ddof=1))
            self.assertAlmostEqual(stats.loc[warehouse, "CV"], observations.Demand.std(ddof=1) / observations.Demand.mean())
            self.assertEqual(stats.loc[warehouse, "Peak_Observed_Week"], pd.Timestamp(observations.loc[observations.Demand.idxmax(), "Week"]))
        self.assertAlmostEqual(stats.Selected_Demand_Share_Pct.sum(), 100)

    def test_selection_and_shares_use_only_observed_selected_data(self):
        selected = aligned_actuals(self.history, ["Whse_A", "Whse_S"])
        self.assertEqual(set(selected.Series), {"Whse_A", "Whse_S"})
        self.assertEqual(len(selected), 102)
        stats = warehouse_statistics(selected)
        self.assertEqual(stats.Observed_Sum.sum(), selected.Demand.sum())
        self.assertAlmostEqual(stats.Selected_Demand_Share_Pct.sum(), 100)
        one = warehouse_statistics(aligned_actuals(self.history, ["Whse_A"]))
        self.assertEqual(one.Selected_Demand_Share_Pct.iloc[0], 100)
        self.assertTrue(aligned_actuals(self.history, []).empty)

    def test_alignment_does_not_invent_or_zero_fill_missing_dates(self):
        altered = self.history.drop(self.history.index[0])
        paired = aligned_actuals(altered, ["Whse_A", "Whse_C"])
        self.assertEqual(len(paired), 100)
        self.assertFalse(paired.Demand.isna().any())
        self.assertEqual(paired.groupby("Series").Date.apply(set).iloc[0], paired.groupby("Series").Date.apply(set).iloc[1])
        with patch("warehouse_data.load_history", return_value=altered), self.assertRaises(DataIssue):
            load_warehouse_actuals(self.directory)

    def test_unknown_warehouse_or_duplicate_actuals_are_rejected(self):
        with self.assertRaises(DataIssue):
            aligned_actuals(self.history, ["Unknown"])
        with self.assertRaises(DataIssue):
            aligned_actuals(pd.concat([self.history, self.history.iloc[[0]]]), ["Whse_A"])
        with self.assertRaises(DataIssue):
            warehouse_rankings(self.directory, ["Unknown"], "MAE")

    def test_all_metrics_rank_only_within_each_warehouse_and_match_exports(self):
        raw = read_csv(self.directory, SCORE_SOURCE)
        for metric in METRICS:
            ranks = warehouse_rankings(self.directory, WAREHOUSES, metric)
            self.assertEqual(len(ranks), 12)
            for warehouse in WAREHOUSES:
                rows = ranks.loc[ranks.Warehouse.eq(warehouse)]
                exported = raw.loc[raw.Warehouse.eq(warehouse)]
                self.assertEqual(rows.Rank_Within_Warehouse.min(), 1)
                self.assertEqual(rows.Rank_Within_Warehouse.max(), 3)
                self.assertEqual(rows[metric].min(), exported[metric].min())
                self.assertEqual(set(rows.Model), {"Naive", "Random Forest", "XGBoost"})
                self.assertEqual(rows.Test_Weeks.unique().tolist(), [51 if warehouse == "Whse_J" else 52])
                self.assertEqual(rows.Evaluation_Period.nunique(), 1)
                self.assertEqual(rows.Target.nunique(), 1)
                for model in rows.Model:
                    self.assertEqual(rows.loc[rows.Model.eq(model), metric].iloc[0], exported.loc[exported.Model.eq(model), metric].iloc[0])
        self.assertNotIn("Rank", ranks)  # No global cross-warehouse leaderboard.

    def test_partial_history_not_used_as_rolling_sample_or_score_denominator(self):
        ranks = warehouse_rankings(self.directory, ["Whse_A"], "WAPE (%)")
        self.assertEqual(ranks.Test_Weeks.iloc[0], 52)
        self.assertEqual(self.history.loc[self.history.Series.eq("Whse_A")].Date.nunique(), 51)
        self.assertEqual(ranks.Evaluation_Period.iloc[0], "2016-01-03 to 2016-12-25")

    def test_deep_dive_actuals_and_diagnostic_dates_match_the_same_export(self):
        for warehouse in WAREHOUSES:
            predictions = reconciliation_predictions(self.directory, warehouse)
            actuals = predictions[["Date", "Actual"]].drop_duplicates().sort_values("Date")
            history = self.history.loc[self.history.Series.eq(warehouse)].sort_values("Date")
            self.assertEqual(actuals.Actual.to_list(), history.Demand.to_list())
            self.assertEqual(actuals.Date.to_list(), history.Date.to_list())
            self.assertEqual(len(predictions), 102)
            self.assertNotIn("Random Forest", set(predictions.Model))
            self.assertNotIn("Naive", set(predictions.Model))


class WarehouseAppTests(unittest.TestCase):
    def test_page_and_filters_keep_demand_and_performance_samples_separate(self):
        app = AppTest.from_file(str(ROOT / "app.py")).run(timeout=30)
        app.sidebar.button(key="nav_" + "Warehouse Analytics").click().run(timeout=30)
        self.assertFalse(app.exception)
        self.assertFalse(app.error)
        self.assertEqual(app.title[0].value, "Warehouse Explorer")
        self.assertEqual(len(app.sidebar.button), 8)
        self.assertEqual(len(app.get("plotly_chart")), 6)
        self.assertTrue(any(m.label == "Observed warehouse-weeks" and m.value == "204" for m in app.metric))
        for level in ["Monthly", "Quarterly"]:
            next(s for s in app.selectbox if s.label == "Warehouse trend aggregation").set_value(level).run(timeout=30)
            self.assertFalse(app.exception)
        for metric in METRICS:
            next(r for r in app.selectbox if r.label == "Warehouse performance metric").set_value(metric).run(timeout=30)
            self.assertFalse(app.exception)
        next(s for s in app.selectbox if s.label == "Deep-dive warehouse").set_value("Whse_J").run(timeout=30)
        self.assertFalse(app.exception)
        next(m for m in app.multiselect if m.label == "Warehouses to compare").set_value(["Whse_J"]).run(timeout=30)
        self.assertFalse(app.exception)
        self.assertFalse(app.error)
        self.assertTrue(any(m.label == "Observed warehouse-weeks" and m.value == "51" for m in app.metric))
        for element in app.get("plotly_chart"):
            spec = json.loads(element.proto.spec)
            self.assertFalse(spec.get("layout", {}).get("xaxis", {}).get("rangeslider", {}).get("visible", False))
        next(m for m in app.multiselect if m.label == "Warehouses to compare").set_value([]).run(timeout=30)
        self.assertFalse(app.exception)
        self.assertTrue(any("Select at least one warehouse" in i.value for i in app.info))


if __name__ == "__main__":
    unittest.main()
