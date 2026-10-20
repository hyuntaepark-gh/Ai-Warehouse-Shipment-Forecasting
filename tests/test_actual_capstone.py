from navigation import ROUTES, LABELS
"""Integration checks read real capstone outputs; no source file is changed."""
import hashlib
import json
import unittest

import pandas as pd
from streamlit.testing.v1 import AppTest

from data_loading import ROOT, inventory, source_directory
from overview import demand_plot
from overview_data import actual_demand, holdout_kpis, load_overview, wape


class ActualCapstoneTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.directory = source_directory()
        cls.data = load_overview(cls.directory)

    def test_every_csv_is_readable_and_documented(self):
        records = [r for r in inventory(self.directory) if r["type"] == ".csv"]
        self.assertEqual(len(records), 74)
        for record in records:
            with self.subTest(file=record["file"]):
                self.assertNotIn("error", record)
                self.assertTrue(record["columns"])
                self.assertIn("evidence", record["evaluation_context"])

    def test_yearly_metrics_match_weekly_predictions(self):
        for row in self.data["yearly"].to_dict("records"):
            frame = self.data["weekly"].loc[lambda d: d.Year.eq(row["Year"]) & d.Model.eq(row["Model"])]
            errors = frame.Actual - frame.Prediction
            with self.subTest(year=row["Year"], model=row["Model"]):
                self.assertEqual(len(frame), row["Forecast_Weeks"])
                self.assertAlmostEqual(wape(frame.Actual, frame.Prediction), row["WAPE (%)"], places=7)
                self.assertAlmostEqual(errors.abs().mean(), row["MAE"], places=5)
                self.assertAlmostEqual((errors.pow(2).mean()) ** .5, row["RMSE"], places=5)

    def test_pooled_retrospective_wape_excludes_holdout(self):
        for row in self.data["pooled"].to_dict("records"):
            frame = self.data["weekly"].loc[lambda d: d.Year.isin([2014, 2015]) & d.Model.eq(row["Model"])]
            self.assertEqual(len(frame), row["Weeks"])
            self.assertAlmostEqual(wape(frame.Actual, frame.Prediction), row["WAPE (%)"], places=7)

    def test_holdout_table_agrees_with_dated_predictions_where_available(self):
        for model in self.data["weekly"].Model.unique():
            annual = self.data["yearly"].loc[lambda d: d.Year.eq(2016) & d.Model.eq(model)].iloc[0]
            full = self.data["holdout"].loc[lambda d: d.Model.eq(model)].iloc[0]
            for metric in ["MAE", "RMSE", "WAPE (%)"]:
                self.assertAlmostEqual(annual[metric], full[metric], places=5)

    def test_kpis_and_monthly_actuals_do_not_triple_count_models(self):
        kpi = holdout_kpis(self.data)
        actual = actual_demand(self.data["weekly"], 2016)
        self.assertEqual(kpi["weeks"], 52)
        self.assertEqual(kpi["demand"], actual.Actual.sum())
        self.assertAlmostEqual(self.data["weekly"].loc[lambda d: d.Year.eq(2016)].Actual.sum(), kpi["demand"] * 3)
        _, monthly = demand_plot(self.data["weekly"], 2016, [], monthly=True)
        self.assertEqual(len(monthly), 12)
        self.assertEqual(monthly.Demand.sum(), kpi["demand"])

    def test_recursive_scores_match_separate_early_2016_sample(self):
        predictions = self.data["recursive_predictions"]
        mapping = {"Recursive XGBoost": "Recursive_XGBoost", "Seasonal Naive": "Seasonal_Naive"}
        for row in self.data["recursive_summary"].to_dict("records"):
            frame = predictions.loc[predictions.Horizon_Week.le(row["Horizon_Weeks"])]
            self.assertEqual(len(frame), row["Observations"])
            self.assertAlmostEqual(wape(frame.Demand, frame[mapping[row["Model"]]]), row["WAPE (%)"], places=5)
        for row in self.data["recursive"].to_dict("records"):
            frame = predictions.loc[predictions.Warehouse.eq(row["Warehouse"])]
            self.assertAlmostEqual(wape(frame.Demand, frame[mapping[row["Model"]]]), row["WAPE (%)"], places=5)

    def test_future_origin_and_planning_sums(self):
        future = self.data["future"]
        self.assertEqual(future.Forecast_Origin.nunique(), 1)
        self.assertEqual(future.Forecast_Origin.iloc[0], pd.Timestamp("2016-12-25"))
        self.assertEqual(len(future), 48)
        for row in self.data["planning"].to_dict("records"):
            frame = future.loc[future.Warehouse.eq(row["Warehouse"]) & future.Horizon_Week.le(row["Horizon_Weeks"])]
            self.assertEqual(len(frame), row["Horizon_Weeks"])
            self.assertAlmostEqual(frame.Predicted_Demand.sum(), row["Projected_Total_Demand"], places=5)

    def test_live_app_renders_actual_results_and_all_filters(self):
        app = AppTest.from_file(str(ROOT / "app.py")).run(timeout=30)
        self.assertFalse(app.exception)
        self.assertFalse(app.error)
        self.assertEqual(len(app.get("plotly_chart")), 9)
        self.assertEqual(len(app.sidebar.button), 8)
        self.assertTrue(any(m.value == f"{holdout_kpis(self.data)['best_wape']:.2f}%" for m in app.metric))
        for box in list(app.selectbox):
            if box.label == "Comparison metric":
                box.set_value("RMSE")
            elif box.label == "Warehouse":
                box.set_value("Whse_J")
            elif box.label == "Retrospective demand year":
                box.set_value(2015)
        next(r for r in app.selectbox if r.label == "Demand view").set_value("Monthly grouped weeks")
        app.select_slider[0].set_value(4)
        app.run(timeout=30)
        self.assertFalse(app.exception)
        self.assertFalse(app.error)
        app.multiselect[0].set_value([])
        app.multiselect[1].set_value([])
        app.run(timeout=30)
        self.assertFalse(app.exception)
        self.assertFalse(app.error)
        self.assertTrue(any("Select at least one warehouse" in i.value for i in app.info))

    def test_original_files_match_preimplementation_hashes(self):
        expected = json.loads((ROOT / "docs/source_hashes_before.json").read_text())
        current = {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                   for p in self.directory.rglob("*") if p.is_file()}
        self.assertEqual(current, expected)


if __name__ == "__main__":
    unittest.main()
