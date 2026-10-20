from navigation import ROUTES, LABELS
"""Verify real-export cohort boundaries, numeric accuracy, filters and display precision."""
import unittest

import pandas as pd
from streamlit.testing.v1 import AppTest

from comparison_data import (COHORT_FIELDS, FILES, GROUPS, METRICS, available_metrics,
                             load_comparison, rank_models, reconciliation_predictions,
                             validate_predictions)
from data_loading import DataIssue, ROOT, read_csv, source_directory
from display_formatting import compact_units, readable_table
from source_catalog import evaluation_context


def assert_export_metrics(test, scores, predictions):
    for row in scores.to_dict("records"):
        frame = predictions.loc[predictions.Model.eq(row["Model"])]
        errors = frame.Actual - frame.Prediction
        calculated = {"MAE": errors.abs().mean(), "RMSE": errors.pow(2).mean() ** .5,
                      "WAPE (%)": errors.abs().sum() / frame.Actual.abs().sum() * 100}
        for metric in METRICS:
            test.assertAlmostEqual(row[metric], calculated[metric], places=5)


class ComparisonDataTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.directory = source_directory()

    def test_holdout_scores_and_available_prediction_models(self):
        result = load_comparison(self.directory, GROUPS[0])
        self.assertEqual(len(result.scores), 8)
        self.assertEqual(result.predictions.Model.nunique(), 3)
        self.assertEqual(len(result.predictions), 156)
        scores = result.scores.loc[result.scores.Model.isin(result.predictions.Model)]
        assert_export_metrics(self, scores, result.predictions)
        for metric in METRICS:
            ranked = rank_models(result.scores, metric)
            self.assertEqual(ranked.iloc[0][metric], result.scores[metric].min())
            self.assertEqual(ranked.Rank.min(), 1)
            self.assertEqual(ranked.Source.nunique(), 1)

    def test_retrospective_metrics_never_include_2016(self):
        for fold in ["Pooled 2014–2015", "2014", "2015"]:
            result = load_comparison(self.directory, GROUPS[1], fold=fold)
            self.assertTrue(set(result.predictions.Date.dt.year).issubset({2014, 2015}))
            self.assertEqual(len(result.scores), 3)
            self.assertEqual(result.predictions.Date.nunique(), 104 if fold.startswith("Pooled") else 52)
            assert_export_metrics(self, result.scores, result.predictions)
            for metric in METRICS:
                self.assertEqual(len(rank_models(result.scores, metric)), 3)
        with self.assertRaises(DataIssue):
            load_comparison(self.directory, GROUPS[1], fold="2016")

    def test_warehouse_scores_are_filtered_to_one_exported_sample(self):
        raw = read_csv(self.directory, FILES["warehouse"])
        for warehouse in raw.Warehouse.unique():
            result = load_comparison(self.directory, GROUPS[2], warehouse=warehouse)
            self.assertEqual(set(result.scores.Warehouse), {warehouse})
            self.assertEqual(result.scores.Test_Weeks.nunique(), 1)
            self.assertTrue(result.predictions.empty)
            self.assertIn(str(result.scores.Test_Weeks.iloc[0]), result.metadata["Sample"])
            for metric in METRICS:
                self.assertEqual(rank_models(result.scores, metric).iloc[0][metric], raw.loc[raw.Warehouse.eq(warehouse), metric].min())

    def test_recursive_pool_and_individual_12week_scores(self):
        for horizon in [4, 8, 12]:
            result = load_comparison(self.directory, GROUPS[3], horizon=horizon)
            self.assertEqual(result.predictions.Date.nunique(), horizon)
            self.assertEqual(result.predictions.Entity.nunique(), 3)
            assert_export_metrics(self, result.scores, result.predictions)
        for warehouse in ["Whse_A", "Whse_C", "Whse_S"]:
            result = load_comparison(self.directory, GROUPS[3], horizon=12, recursive_scope=warehouse)
            self.assertEqual(set(result.predictions.Entity), {warehouse})
            assert_export_metrics(self, result.scores, result.predictions)

    def test_unexported_recursive_metrics_not_manufactured(self):
        for horizon in [4, 8]:
            result = load_comparison(self.directory, GROUPS[3], horizon=horizon, recursive_scope="Whse_A")
            self.assertTrue(result.scores.empty)
            self.assertEqual(available_metrics(result.scores), [])
            self.assertEqual(result.predictions.Date.nunique(), horizon)
        with self.assertRaises(DataIssue):
            load_comparison(self.directory, GROUPS[3], recursive_scope="Whse_J")

    def test_mixed_cohorts_and_missing_metadata_cannot_be_ranked(self):
        result = load_comparison(self.directory, GROUPS[0])
        for field in COHORT_FIELDS:
            altered = result.scores.copy()
            altered.loc[0, field] = "Different evaluation metadata"
            # The model filter must not hide mixed metadata present in the source cohort.
            with self.subTest(field=field), self.assertRaises(DataIssue):
                rank_models(altered, "MAE", [altered.Model.iloc[1]])
        mixed = pd.concat([result.scores, load_comparison(self.directory, GROUPS[2]).scores])
        with self.assertRaises(DataIssue):
            rank_models(mixed, "MAE")
        with self.assertRaises(DataIssue):
            rank_models(result.scores.drop(columns="Horizon"), "MAE")

    def test_missing_metrics_ties_and_selected_model_rankings(self):
        scores = load_comparison(self.directory, GROUPS[0]).scores
        selected = list(scores.Model.iloc[:2])
        ranked = rank_models(scores, "MAE", selected)
        self.assertEqual(set(ranked.Model), set(selected))
        tied = scores.iloc[:2].copy()
        tied.MAE = tied.MAE.iloc[0]
        self.assertEqual(rank_models(tied, "MAE").Rank.tolist(), [1, 1])
        with self.assertRaises(DataIssue):
            rank_models(scores.drop(columns="RMSE"), "RMSE")
        invalid = scores.copy()
        invalid.loc[0, "MAE"] = float("nan")
        with self.assertRaises(DataIssue):
            rank_models(invalid, "MAE")

    def test_aligned_predictions_reject_mismatch_duplicates_and_conflicting_actuals(self):
        predictions = load_comparison(self.directory, GROUPS[0]).predictions
        for altered in [predictions.iloc[1:], pd.concat([predictions, predictions.iloc[[0]]])]:
            with self.assertRaises(DataIssue):
                validate_predictions(altered)
        altered = predictions.copy()
        altered.loc[0, "Actual"] += 1
        with self.assertRaises(DataIssue):
            validate_predictions(altered)

    def test_reconciliation_is_separate_and_has_actual_predicted_pairs(self):
        result = reconciliation_predictions(self.directory, "Whse_J")
        self.assertEqual(len(result), 102)
        self.assertEqual(result.Date.nunique(), 51)
        self.assertEqual(result.Date.min(), pd.Timestamp("2016-01-10"))
        self.assertNotIn("Rank", result)
        self.assertEqual(result.Model.nunique(), 2)
        self.assertIn("unverified", evaluation_context("lstm_gru_comparison.csv")["family"])

    def test_display_units_and_cv_preserve_download_precision(self):
        self.assertEqual(compact_units(1234), "1.23K")
        self.assertEqual(compact_units(1234567), "1.23M")
        self.assertEqual(compact_units(1234567890), "1.23B")
        frame = pd.DataFrame({"Mean_Weekly_Demand": [1234567.891234567], "CV": [.123456789]})
        original = frame.to_csv(index=False)
        styled = readable_table(frame)
        html = styled.to_html()
        self.assertIn("12.3%", html)
        self.assertIn("1.23M", html)
        self.assertEqual(frame.to_csv(index=False), original)
        pd.testing.assert_frame_equal(frame, styled.data)


class ComparisonAppTests(unittest.TestCase):
    def test_all_groups_metrics_filters_and_prediction_views(self):
        app = AppTest.from_file(str(ROOT / "app.py")).run(timeout=30)
        app.sidebar.button(key="nav_" + "Model Comparison").click().run(timeout=30)
        self.assertFalse(app.exception)
        self.assertEqual(len(app.get("plotly_chart")), 2)
        import json
        plotted = json.loads(app.get("plotly_chart")[0].proto.spec)
        scores = load_comparison(source_directory(), GROUPS[0]).scores.set_index("Model")
        for trace in plotted["data"]:
            self.assertEqual(trace["text"], [f"{scores.loc[trace['name'], 'WAPE (%)']:.2f}%"])
        for metric in METRICS:
            next(r for r in app.selectbox if r.label == "Ranking metric").set_value(metric).run(timeout=30)
            self.assertFalse(app.exception)
        next(m for m in app.multiselect if m.label == "Models in comparison").set_value(["Prophet"]).run(timeout=30)
        self.assertTrue(any("No aligned prediction" in i.value for i in app.info))
        self.assertEqual(len(app.get("plotly_chart")), 1)
        next(m for m in app.multiselect if m.label == "Models in comparison").set_value([]).run(timeout=30)
        self.assertTrue(any("Select at least one model" in i.value for i in app.info))
        app.selectbox(key="comparison_group").set_value(GROUPS[1]).run(timeout=30)
        next(s for s in app.selectbox if s.label == "Retrospective cohort").set_value("2015").run(timeout=30)
        self.assertFalse(app.exception)
        self.assertEqual(len(app.get("plotly_chart")), 2)
        app.selectbox(key="comparison_group").set_value(GROUPS[2]).run(timeout=30)
        next(s for s in app.selectbox if s.label == "Comparison warehouse").set_value("Whse_J").run(timeout=30)
        app.checkbox[0].set_value(True).run(timeout=30)
        self.assertFalse(app.exception)
        self.assertEqual(len(app.get("plotly_chart")), 2)
        app.selectbox(key="comparison_group").set_value(GROUPS[3]).run(timeout=30)
        next(s for s in app.selectbox if s.label == "Recursive horizon (weeks)").set_value(4)
        next(s for s in app.selectbox if s.label == "Recursive evaluation sample").set_value("Whse_A").run(timeout=30)
        self.assertFalse(app.exception)
        self.assertEqual(len(app.get("plotly_chart")), 1)
        self.assertTrue(any("summary scores are not exported" in i.value for i in app.info))
        # Check that range sliders are absent from every new comparison chart.
        for element in app.get("plotly_chart"):
            spec = json.loads(element.proto.spec)
            self.assertFalse(spec.get("layout", {}).get("xaxis", {}).get("rangeslider", {}).get("visible", False))


if __name__ == "__main__":
    unittest.main()
