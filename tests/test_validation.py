from navigation import ROUTES, LABELS
"""Actual CSV evidence, cohort separation, scale checks and validation-page behavior."""
import json
import unittest
from unittest.mock import patch

import pandas as pd
from streamlit.testing.v1 import AppTest

from data_loading import DataIssue, ROOT, read_csv, source_directory
from source_catalog import evaluation_context
from validation_data import (CONTRACTS, METRICS, MODELS, SECTIONS, calibration_percentages,
                             evidence, temporal_evidence, yearly_evidence)


class ValidationDataTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.directory = source_directory()
        cls.weekly = read_csv(cls.directory, "tables/timesfm_historical_weekly_predictions.csv")
        cls.weekly.Date = pd.to_datetime(cls.weekly.Date)

    def test_all_24_validation_contracts_read_actual_exports(self):
        self.assertEqual(len(CONTRACTS), 24)
        for name, columns in CONTRACTS.items():
            with self.subTest(source=name):
                frame = evidence(self.directory, name)
                self.assertTrue(set(columns).issubset(frame))
                self.assertFalse(frame.empty)

    def test_yearly_periods_do_not_mix_and_metrics_match_predictions(self):
        for cohort, years in [("Retrospective 2014–2015", [2014, 2015]), ("2016 holdout reference", [2016])]:
            frame = yearly_evidence(self.directory, cohort, years, MODELS)
            self.assertEqual(set(frame.Year), set(years))
            self.assertEqual(frame.Evaluation.nunique(), 1)
            for row in frame.to_dict("records"):
                weekly = self.weekly.loc[self.weekly.Year.eq(row["Year"]) & self.weekly.Model.eq(row["Model"])]
                self.assert_metrics(row, weekly)
        with self.assertRaises(DataIssue):
            yearly_evidence(self.directory, "Retrospective 2014–2015", [2016], MODELS)
        self.assertTrue(yearly_evidence(self.directory, "2016 holdout reference", [], MODELS).empty)

    def assert_metrics(self, row, weekly):
        errors = weekly.Actual - weekly.Prediction
        self.assertAlmostEqual(row["MAE"], errors.abs().mean(), places=5)
        self.assertAlmostEqual(row["RMSE"], errors.pow(2).mean() ** .5, places=5)
        self.assertAlmostEqual(row["WAPE (%)"], errors.abs().sum() / weekly.Actual.abs().sum() * 100, places=7)

    def test_monthly_quarterly_and_pooled_metrics_match_weekly_subsets(self):
        for grain in ["Quarterly", "Monthly"]:
            for cohort, years in [("Retrospective 2014–2015", [2014, 2015]), ("Pooled 2014–2015", []), ("2016 holdout reference", [2016])]:
                _, frame = temporal_evidence(self.directory, grain, cohort, years, MODELS)
                for row in frame.to_dict("records"):
                    weekly = self.weekly.loc[self.weekly.Model.eq(row["Model"]) & self.weekly.Year.isin([2014, 2015] if cohort.startswith("Pooled") else [row["Year"]])]
                    period = weekly.Date.dt.quarter if grain == "Quarterly" else weekly.Date.dt.month
                    weekly = weekly.loc[period.eq(row["Period_Number"])]
                    self.assertEqual(len(weekly), row["Weeks"])
                    self.assert_metrics(row, weekly)
            with self.assertRaises(DataIssue):
                temporal_evidence(self.directory, grain, "Pooled 2014–2015", [2016], MODELS)

    def test_temporal_filters_and_stability_ranges(self):
        name, frame = temporal_evidence(self.directory, "Monthly", "2016 holdout reference", [2016], ["ETS"], ["Jan", "Feb"])
        self.assertEqual(len(frame), 2)
        self.assertEqual(set(frame.Model), {"ETS"})
        self.assertEqual(set(frame.Year), {2016})
        self.assertEqual(set(frame.Period), {"Jan", "Feb"})
        for stem in ["monthly", "quarterly"]:
            pooled = evidence(self.directory, f"timesfm_historical_{stem}_pooled")
            summary = evidence(self.directory, f"timesfm_{stem}_stability_summary")
            for row in summary.to_dict("records"):
                values = pooled.loc[pooled.Model.eq(row["Model"]), "WAPE (%)"]
                column = f"Pooled_{stem.title()}_WAPE_Range_pp"
                self.assertAlmostEqual(row[column], values.max() - values.min(), places=8)

    def test_stress_baseline_deltas_and_seed_summaries(self):
        for name in ["data_quality_impact", "data_disruption_robustness"]:
            frame = evidence(self.directory, name)
            expected = frame["WAPE (%)"] - frame["WAPE (%)"].iloc[0]
            self.assertTrue((expected - frame.WAPE_Change_pp).abs().lt(1e-8).all())
            self.assertNotIn("Year", frame)
        seeds = evidence(self.directory, "random_seed_stability")
        summary = evidence(self.directory, "random_seed_stability_summary")
        for row in summary.to_dict("records"):
            values = seeds.loc[seeds.Model.eq(row["Model"])]
            self.assertAlmostEqual(row["Mean_WAPE"], values["WAPE (%)"].mean(), places=8)
            self.assertAlmostEqual(row["Std_WAPE"], values["WAPE (%)"].std(ddof=1), places=8)
            self.assertAlmostEqual(row["Min_WAPE"], values["WAPE (%)"].min(), places=8)
            self.assertAlmostEqual(row["Max_WAPE"], values["WAPE (%)"].max(), places=8)

    def test_calibration_counts_and_coverage_scales_not_multiplied_twice(self):
        raw = evidence(self.directory, "forecast_calibration")
        normalized = calibration_percentages(raw)
        self.assertTrue((normalized.Observed_Coverage_Pct - raw.Covered / raw.Observations * 100).abs().lt(1e-8).all())
        self.assertTrue(normalized.Observed_Coverage_Pct.between(0, 100).all())
        self.assertTrue(normalized.Observed_Coverage_Pct.eq(raw.Observed_Coverage).all())
        self.assertTrue((raw.Total_Width / raw.Observations - raw.Average_Width).abs().lt(1e-6).all())
        quantile = evidence(self.directory, "quantile_warehouse_results")
        self.assertTrue((quantile.Coverage * 100 - quantile["Coverage (%)"]).abs().lt(1e-8).all())
        altered = raw.copy()
        altered.Observed_Coverage /= 100
        with self.assertRaises(DataIssue):
            calibration_percentages(altered)

    def test_bias_summary_arithmetic_and_no_inferred_model(self):
        frame = evidence(self.directory, "forecast_bias_summary")
        self.assertTrue((frame.Total_Signed_Error / frame.Observations - frame.Mean_Signed_Error).abs().lt(1e-6).all())
        self.assertTrue((frame.Total_Signed_Error / frame.Total_Demand * 100 - frame.Bias_Pct).abs().lt(1e-8).all())
        self.assertTrue((frame.Underforecast_Rate * 100 - frame.Underforecast_Rate_Pct).abs().lt(1e-8).all())
        self.assertNotIn("Model", frame)

    def test_statistical_and_leakage_exports_do_not_supply_missing_methods(self):
        stats = evidence(self.directory, "forecast_significance_test")
        self.assertTrue(stats.HAC_p_value.between(0, 1).all())
        self.assertTrue(stats.CI_95_Lower.lt(0).all() and stats.CI_95_Upper.gt(0).all())
        self.assertNotIn("Test_Statistic", stats)
        self.assertNotIn("Week", stats)
        context = evaluation_context("forecast_significance_test.csv")
        self.assertIn("unverified", context["family"])
        self.assertNotIn("2016-01-10", context["period"])
        audit = evidence(self.directory, "data_leakage_audit")
        self.assertTrue(audit.Details.isna().all())
        self.assertEqual(len(audit), 8)

    def test_monitoring_retains_nulls_flags_and_exported_errors(self):
        raw = read_csv(self.directory, "tables/model_monitoring_2016.csv")
        frame = evidence(self.directory, "model_monitoring_2016")
        self.assertEqual(frame.Rolling_WAPE_Pct.isna().sum(), raw.Rolling_WAPE_Pct.isna().sum())
        self.assertGreater(frame.Rolling_WAPE_Pct.isna().sum(), 0)
        self.assertTrue(((frame.Demand - frame.Forecast).abs() - frame.Absolute_Error).abs().lt(1e-8).all())
        self.assertEqual(frame.Warning.sum(), raw.Warning.sum())
        self.assertEqual(set(frame.Week.dt.year), {2016})

    def test_missing_columns_bad_numeric_and_evaluation_labels_rejected(self):
        raw = read_csv(self.directory, "tables/timesfm_historical_yearly_results.csv")
        for altered in [raw.drop(columns="MAE"), raw.assign(MAE=float("nan")), raw.assign(Evaluation="Independent validation")]:
            with patch("validation_data.read_csv", return_value=altered), self.assertRaises(DataIssue):
                evidence(self.directory, "timesfm_historical_yearly_results")


class ValidationAppTests(unittest.TestCase):
    def test_all_evidence_areas_and_nested_filters_render(self):
        app = AppTest.from_file(str(ROOT / "app.py")).run(timeout=30)
        app.sidebar.button(key="nav_" + "Model Validation").click().run(timeout=30)
        self.assertFalse(app.exception)
        self.assertEqual(app.title[0].value, "Forecast Reliability")
        next(r for r in app.selectbox if r.label == "Backtesting evaluation").set_value("2016 holdout reference").run(timeout=30)
        self.assertTrue(any("2016 is a separate final holdout" in w.value for w in app.warning))
        for section in SECTIONS:
            app.selectbox[0].set_value(section).run(timeout=30)
            self.assertFalse(app.exception)
            self.assertFalse(any("Model validation data unavailable:" in w.value for w in app.warning))
        app.selectbox[0].set_value("Temporal stability").run(timeout=30)
        next(r for r in app.selectbox if r.label == "Temporal resolution").set_value("Monthly").run(timeout=30)
        next(s for s in app.selectbox if s.label == "Temporal evaluation").set_value("Pooled 2014–2015").run(timeout=30)
        self.assertFalse(app.exception)
        next(m for m in app.multiselect if m.label == "Calendar periods").set_value([]).run(timeout=30)
        self.assertTrue(any("Select at least one" in i.value for i in app.info))
        app.selectbox[0].set_value("Data quality & robustness").run(timeout=30)
        for mode in ["Input and target perturbations", "Random-seed stability"]:
            next(s for s in app.selectbox if s.label == "Robustness experiment").set_value(mode).run(timeout=30)
            self.assertFalse(app.exception)
        app.selectbox[0].set_value("Uncertainty & bias").run(timeout=30)
        self.assertEqual(len(app.get("plotly_chart")), 2)
        for mode in ["Quantile diagnostics", "Warehouse bias"]:
            next(s for s in app.selectbox if s.label == "Reliability diagnostic").set_value(mode).run(timeout=30)
            self.assertFalse(app.exception)
        next(s for s in app.selectbox if s.label == "Bias warehouse").set_value("Whse_J").run(timeout=30)
        app.selectbox[0].set_value("Statistical, leakage & monitoring").run(timeout=30)
        for mode in ["Leakage audit", "Historical monitoring"]:
            next(s for s in app.selectbox if s.label == "Audit diagnostic").set_value(mode).run(timeout=30)
            self.assertFalse(app.exception)
        next(s for s in app.selectbox if s.label == "Monitoring quarter").set_value("2016Q1").run(timeout=30)
        self.assertFalse(app.exception)
        for chart in app.get("plotly_chart"):
            spec = json.loads(chart.proto.spec)
            self.assertFalse(spec.get("layout", {}).get("xaxis", {}).get("rangeslider", {}).get("visible", False))
        app.selectbox[0].set_value("Recursive validation").run(timeout=30)
        chosen = next(m for m in app.multiselect if m.label == "Recursive validation warehouses")
        self.assertNotIn("Whse_J", chosen.options)
        chosen.set_value(["Whse_A"]).run(timeout=30)
        self.assertFalse(app.exception)
        self.assertFalse(app.error)
        self.assertTrue(any("unchanged by warehouse filter" in heading.value for heading in app.markdown))


if __name__ == "__main__":
    unittest.main()
