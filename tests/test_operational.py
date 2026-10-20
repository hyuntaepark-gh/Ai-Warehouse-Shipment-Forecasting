from navigation import ROUTES, LABELS
"""Actual exported planning evidence, reconciliation, isolation and interactive controls."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import pandas as pd
from streamlit.testing.v1 import AppTest

from data_loading import DataIssue, ROOT, read_csv, source_directory
from future_data import HORIZONS, WAREHOUSES, WEEKLY_SOURCE
from operational_data import (PLANNING_SOURCE, SUPPLEMENTARY, load_planning,
                              recent_observed_context, selected_planning, supplementary)


class OperationalDataTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.directory = source_directory()
        cls.archive = load_planning(cls.directory)

    def test_risk_ratios_and_source_thresholds_reconcile(self):
        weekly = self.archive["weekly"]
        self.assertEqual(len(weekly), 48)
        self.assertLess((weekly.Predicted_Demand / weekly.Historical_P90 - weekly.Demand_to_P90_Ratio).abs().max(), 1e-10)
        self.assertEqual(set(weekly.Illustrative_Risk_Level), {"Normal", "Watch"})
        self.assertTrue(weekly.Demand_to_P90_Ratio.lt(1).all())
        self.assertTrue(weekly.loc[weekly.Illustrative_Risk_Level.eq("Watch"), "Demand_to_P90_Ratio"].lt(1).all())
        self.assertEqual(len(self.archive["checks"]), 72)
        self.assertLess(self.archive["checks"].Absolute_Difference.max(), 1e-8)

    def test_source_categories_and_planning_text_are_preserved(self):
        exported = read_csv(self.directory, PLANNING_SOURCE)
        pd.testing.assert_frame_equal(self.archive["planning"], exported)
        raw = read_csv(self.directory, WEEKLY_SOURCE).sort_values(["Warehouse", "Horizon_Week"])
        self.assertEqual(self.archive["weekly"].Illustrative_Risk_Level.tolist(), raw.Illustrative_Risk_Level.tolist())
        last = exported.loc[exported.Horizon_Weeks.eq(12)].set_index("Warehouse")
        self.assertEqual(last.Illustrative_Risk_Level.to_dict(), {"Whse_A": "Watch", "Whse_C": "Normal", "Whse_J": "Watch", "Whse_S": "Normal"})
        self.assertEqual(last.Weeks_Above_Historical_P90.sum(), 0)

    def test_horizon_and_warehouse_filters(self):
        for horizon in HORIZONS:
            weekly, summary = selected_planning(self.archive, ["Whse_A", "Whse_J"], horizon)
            self.assertEqual(len(weekly), 2 * horizon)
            self.assertEqual(len(summary), 2)
            self.assertTrue(summary.Horizon_Weeks.eq(horizon).all())
            self.assertEqual(set(summary.Warehouse), {"Whse_A", "Whse_J"})
            for row in summary.itertuples():
                records = weekly.loc[weekly.Warehouse.eq(row.Warehouse)]
                self.assertAlmostEqual(records.Predicted_Demand.sum(), row.Projected_Total_Demand, places=6)
                self.assertEqual(records.Predicted_Demand.gt(records.Historical_P90).sum(), row.Weeks_Above_Historical_P90)
        for warehouses, horizon in [([], 12), (["Unknown"], 12), (WAREHOUSES, 6)]:
            with self.assertRaises(DataIssue):
                selected_planning(self.archive, warehouses, horizon)

    def test_recent_actual_means_have_verified_four_week_coverage(self):
        recent = recent_observed_context(self.directory, self.archive["planning"])
        self.assertEqual(len(recent), 4)
        self.assertTrue(recent.Observed_Weeks.eq(4).all())
        self.assertTrue(recent.First_Observed_Week.eq(pd.Timestamp("2016-12-04")).all())
        self.assertTrue(recent.Last_Observed_Week.eq(pd.Timestamp("2016-12-25")).all())
        self.assertEqual(recent.set_index("Warehouse").Recent_4Week_Mean_Observed.to_dict(), {
            "Whse_A": 512895.25, "Whse_C": 3273727.5, "Whse_J": 15233746.75, "Whse_S": 2249123.5})
        bad = self.archive["planning"].copy()
        bad.loc[bad.Warehouse.eq("Whse_A"), "Recent_4Week_Mean_Observed"] += 1
        with self.assertRaises(DataIssue):
            recent_observed_context(self.directory, bad)

    def test_missing_invalid_risk_fields_and_inconsistent_planning_rejected(self):
        original_reader = read_csv
        for source, field, value in [(WEEKLY_SOURCE, "Historical_P90", 0),
            (WEEKLY_SOURCE, "Demand_to_P90_Ratio", 2), (WEEKLY_SOURCE, "Illustrative_Risk_Level", None),
            (PLANNING_SOURCE, "Weeks_Above_Historical_P90", 1),
            (PLANNING_SOURCE, "Change_vs_Recent_4Week_Pct", float("nan")),
            (PLANNING_SOURCE, "Max_Demand_to_P90_Ratio", 2),
            (PLANNING_SOURCE, "Recent_4Week_Mean_Observed", 0)]:
            bad = read_csv(self.directory, source)
            bad.loc[0, field] = value
            def reader(directory, name):
                return bad.copy() if name == source else original_reader(directory, name)
            with self.subTest(field=field), patch("operational_data.read_csv", side_effect=reader):
                # future_data has its own reader; supply changed weekly records there as well.
                with patch("future_data.read_csv", side_effect=reader), self.assertRaises(DataIssue):
                    load_planning(self.directory)

    def test_all_supplementary_contracts_and_precision(self):
        expected = {"scenario_summary": 3, "capacity_optimization": 2, "illustrative_cost_simulation": 9, "forecast_value_added": 6}
        from display_formatting import readable_table
        for name in SUPPLEMENTARY:
            frame = supplementary(self.directory, name)
            self.assertEqual(len(frame), expected[name])
            pd.testing.assert_frame_equal(frame, read_csv(self.directory, f"tables/{name}.csv"))
            csv = frame.to_csv(index=False)
            pd.testing.assert_frame_equal(readable_table(frame).data, frame)
            self.assertEqual(csv, frame.to_csv(index=False))

    def test_only_exported_scenarios_and_separate_populations(self):
        scenarios = supplementary(self.directory, "scenario_summary")
        self.assertEqual(scenarios.Scenario.tolist(), ["Baseline", "Demand +10%", "Demand +20%"])
        self.assertEqual(scenarios.Threshold_Exceedances.tolist(), [202, 204, 204])
        costs = supplementary(self.directory, "illustrative_cost_simulation")
        self.assertTrue(costs.Warehouse_Weeks.eq(207).all())
        self.assertFalse(set(costs) & {"Week", "Forecast_Origin", "Capacity", "Savings"})
        baseline = scenarios.iloc[0]
        for factor, index in [(1.1, 1), (1.2, 2)]:
            self.assertAlmostEqual(scenarios.iloc[index].Average_Risk_Ratio, baseline.Average_Risk_Ratio * factor, places=8)
            self.assertAlmostEqual(scenarios.iloc[index].Maximum_Risk_Ratio, baseline.Maximum_Risk_Ratio * factor, places=8)

    def test_fva_uses_own_evaluation_level_baselines(self):
        frame = supplementary(self.directory, "forecast_value_added")
        self.assertEqual(set(frame.Evaluation_Level), {"Warehouse-Level", "Aggregated Weekly"})
        for _, group in frame.groupby("Evaluation_Level"):
            naive = group.loc[group.Model.eq("Naive"), "WAPE (%)"].iloc[0]
            expected = (1 - group["WAPE (%)"] / naive) * 100
            self.assertLess((group["FVA_Improvement (%)"] - expected).abs().max(), 1e-8)

    def test_missing_duplicate_and_nonfinite_supplementary_sources_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(DataIssue):
                supplementary(Path(directory), "scenario_summary")
        for name in SUPPLEMENTARY:
            frame = supplementary(self.directory, name)
            for bad in [frame.iloc[:0], pd.concat([frame, frame.iloc[[0]]]), frame.drop(columns=[frame.columns[-1]])]:
                with patch("operational_data.read_csv", return_value=bad), self.assertRaises(DataIssue):
                    supplementary(self.directory, name)
        bad = supplementary(self.directory, "forecast_value_added")
        bad.loc[0, "FVA_Improvement (%)"] = 1
        with patch("operational_data.read_csv", return_value=bad), self.assertRaises(DataIssue):
            supplementary(self.directory, "forecast_value_added")


class OperationalAppTests(unittest.TestCase):
    def app(self):
        app = AppTest.from_file(str(ROOT / "app.py")).run(timeout=30)
        return app.sidebar.button(key="nav_" + "Operational Insights").click().run(timeout=30)

    def test_planning_horizons_warehouses_empty_selection_and_charts(self):
        app = self.app()
        self.assertFalse(app.exception)
        self.assertFalse(app.error)
        self.assertEqual(len(app.sidebar.button), 8)
        self.assertEqual(len(app.get("plotly_chart")), 2)
        self.assertFalse(any("unavailable:" in w.value for w in app.warning))
        self.assertEqual(len(app.metric), 4)
        self.assertTrue(any("ops-label" in m.value and "Watch" in m.value for m in app.markdown))
        for horizon in HORIZONS:
            next(r for r in app.get("button_group") if r.key == "ops_horizon").set_value(horizon).run(timeout=30)
            self.assertFalse(app.exception)
            self.assertTrue(any(m.label == "Weeks above historical P90" and m.value == "0" for m in app.metric))
        next(r for r in app.get("button_group") if r.key == "ops_warehouses").set_value(["Whse_A"]).run(timeout=30)
        for chart in app.get("plotly_chart"):
            spec = json.loads(chart.proto.spec)
            self.assertFalse(spec.get("layout", {}).get("xaxis", {}).get("rangeslider", {}).get("visible", False))
            self.assertIn(len(spec["data"]), [1, 2])
        next(r for r in app.get("button_group") if r.key == "ops_warehouses").set_value([]).run(timeout=30)
        self.assertFalse(app.exception)
        self.assertEqual(len(app.metric), 0)
        self.assertTrue(any("Select at least one warehouse" in i.value for i in app.info))

    def test_historical_bias_filters_and_archived_monitoring(self):
        app = self.app()
        next(r for r in app.get("button_group") if r.key == "ops_view").set_value("Historical bias & monitoring").run(timeout=30)
        self.assertFalse(app.exception)
        self.assertTrue(any(m.label == "Exported warning weeks" and m.value == "3" for m in app.metric))
        self.assertTrue(any(m.label == "Exported persistent warning weeks" and m.value == "2" for m in app.metric))
        for metric in ["Underforecast_Rate_Pct", "Longest_Underforecast_Streak"]:
            next(s for s in app.selectbox if s.label == "Bias diagnostic").set_value(metric).run(timeout=30)
            self.assertFalse(app.exception)
        app.checkbox[0].set_value(True).run(timeout=30)
        self.assertEqual(len(app.dataframe[-1].value), 3)
        app.multiselect[0].set_value([]).run(timeout=30)
        self.assertFalse(app.exception)
        self.assertTrue(any("Select a warehouse" in i.value for i in app.info))
        self.assertEqual(len(app.get("plotly_chart")), 1)

    def test_scenario_loss_and_fva_filters_and_empty_selection(self):
        app = self.app()
        next(r for r in app.get("button_group") if r.key == "ops_view").set_value("Illustrative scenarios & capacity").run(timeout=30)
        self.assertFalse(app.exception)
        self.assertFalse(app.error)
        self.assertFalse(any("unavailable:" in w.value for w in app.warning))
        self.assertEqual(len(app.get("plotly_chart")), 2)
        next(s for s in app.selectbox if s.label == "Scenario indicator").set_value("Threshold_Exceedances")
        next(s for s in app.selectbox if s.label == "Planning-loss scenario").set_value("Demand +20%")
        next(s for s in app.selectbox if s.label == "FVA evaluation level").set_value("Aggregated Weekly")
        app.multiselect[0].set_value(["Baseline", "Demand +20%"]).run(timeout=30)
        self.assertFalse(app.exception)
        self.assertEqual(set(app.dataframe[0].value.Scenario), {"Baseline", "Demand +20%"})
        app.multiselect[0].set_value([]).run(timeout=30)
        self.assertFalse(app.exception)
        self.assertTrue(any("Select at least one exported scenario" in i.value for i in app.info))

    def test_inconsistent_planning_withholds_indicators(self):
        with patch("operational_insights.load_planning", side_effect=DataIssue("inconsistent archive")):
            app = self.app()
        self.assertFalse(app.exception)
        self.assertEqual(len(app.metric), 0)
        self.assertEqual(len(app.get("plotly_chart")), 0)
        self.assertTrue(any("Operational insights data unavailable" in w.value for w in app.warning))

    def test_optional_evidence_failure_isolated_from_other_panels(self):
        app = self.app()
        with patch("operational_insights.recent_observed_context", side_effect=DataIssue("missing actual reference")):
            app.run(timeout=30)
        self.assertFalse(app.exception)
        self.assertEqual(len(app.get("plotly_chart")), 2)
        self.assertTrue(any("Recent actual reference verification unavailable" in w.value for w in app.warning))
        original = supplementary
        def reader(directory, name):
            if name == "scenario_summary":
                raise DataIssue("missing scenarios")
            return original(directory, name)
        with patch("operational_insights.supplementary", side_effect=reader):
            next(r for r in app.get("button_group") if r.key == "ops_view").set_value("Illustrative scenarios & capacity").run(timeout=30)
        self.assertFalse(app.exception)
        self.assertTrue(any("Scenario evidence unavailable" in w.value for w in app.warning))
        self.assertEqual(len(app.get("plotly_chart")), 1)


if __name__ == "__main__":
    unittest.main()
