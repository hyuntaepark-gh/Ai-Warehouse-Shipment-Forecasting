from navigation import ROUTES, LABELS
"""Product workspace interactions and exact correspondence to archived source records."""
import hashlib
import json
import unittest

import pandas as pd
from streamlit.testing.v1 import AppTest

from bi_components import CSS
from data_loading import ROOT, source_directory
from operational_data import load_planning, selected_planning
from operational_charts import HEAT_COLORS, comparison_markup, detail_figure, heatmap_text_color, weekly_heatmap


def group(app, key):
    return next(e for e in app.get("button_group") if e.key == key)


class OperationalProductTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.archive = load_planning(source_directory())

    def app(self):
        app = AppTest.from_file(str(ROOT / "app.py")).run(timeout=30)
        return app.sidebar.button(key="nav_" + "Operational Insights").click().run(timeout=30)

    def test_heatmap_cells_and_hover_data_match_every_source_record(self):
        for horizon in [4, 8, 12]:
            weekly, summary = selected_planning(self.archive, ["Whse_A", "Whse_C", "Whse_J", "Whse_S"], horizon)
            before = weekly.copy(deep=True)
            figure, pivot = weekly_heatmap(weekly)
            self.assertEqual(pivot.shape, (4, horizon))
            self.assertEqual(len(figure.data), 1)
            for i, warehouse in enumerate(pivot.index):
                for j, date in enumerate(pivot.columns):
                    row = weekly.loc[weekly.Warehouse.eq(warehouse) & weekly.Week.eq(date)].iloc[0]
                    self.assertAlmostEqual(figure.data[0].z[i][j], row.Demand_to_P90_Ratio * 100, places=10)
                    hover = figure.data[0].customdata[i][j]
                    self.assertEqual(hover[0], row.Predicted_Demand)
                    self.assertEqual(hover[1], row.Historical_P90)
                    self.assertEqual(hover[2], row.Illustrative_Risk_Level)
            pd.testing.assert_frame_equal(weekly, before)
            self.assertEqual(figure.data[0].zmin, 0)
            self.assertEqual(figure.data[0].zmax, 100)

    def test_comparison_uses_exported_peaks_and_labels_without_new_risk_scores(self):
        _, summary = selected_planning(self.archive, ["Whse_A", "Whse_C", "Whse_J", "Whse_S"], 12)
        markup = comparison_markup(summary)
        for row in summary.itertuples():
            self.assertIn(f"{row.Max_Demand_to_P90_Ratio * 100:.1f}%", markup)
            self.assertIn(row.Illustrative_Risk_Level, markup)
        self.assertLess(markup.index('Whse_A:'), markup.index('Whse_J:'))
        self.assertIn("not derived from the bar", markup)
        self.assertNotIn("#ff", markup)

    def test_detail_contains_only_selected_projection_and_source_reference(self):
        for warehouse in ["Whse_A", "Whse_C", "Whse_J", "Whse_S"]:
            records = self.archive["weekly"].loc[lambda d: d.Warehouse.eq(warehouse)]
            figure = detail_figure(records)
            self.assertEqual(len(figure.data), 2)
            self.assertEqual(list(figure.data[0].y), records.Predicted_Demand.tolist())
            self.assertEqual(list(figure.data[1].y), records.Historical_P90.tolist())
            self.assertEqual(list(figure.data[0].x), records.Week.tolist())
            self.assertEqual(figure.data[1].name, "Historical P90 reference")

    def test_heatmap_annotation_contrast_and_mobile_stacking_rules(self):
        for percent in range(101):
            scale=percent/50
            index=min(int(scale),1)
            fraction=scale-index
            channels=[(a+(b-a)*fraction)/255 for a,b in zip(HEAT_COLORS[index],HEAT_COLORS[index+1])]
            luminance=sum((v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4)*w for v,w in zip(channels,[.2126,.7152,.0722]))
            contrast=1.05/(luminance+.05) if heatmap_text_color(percent)=="#ffffff" else (luminance+.05)/.05
            self.assertGreaterEqual(contrast,4.5)
        self.assertIn('.st-key-ops_primary_row [data-testid="stHorizontalBlock"]',CSS)
        self.assertIn('grid-template-columns:repeat(2,minmax(0,1fr))',CSS)

    def test_four_kpis_and_warehouse_horizon_detail_interactions(self):
        app = self.app()
        self.assertFalse(app.exception)
        self.assertEqual({e.label:e.value for e in app.metric}, {"Forecast demand":"223.72M", "Weeks above historical P90":"0", "Warehouse coverage":"4 / 4", "Forecast horizon":"12 weeks"})
        for horizon in [4, 8, 12]:
            group(app, "ops_horizon").set_value(horizon).run(timeout=30)
            self.assertFalse(app.exception)
            self.assertTrue(any(e.label=="Forecast horizon" and e.value==f"{horizon} weeks" for e in app.metric))
        group(app, "ops_warehouses").set_value(["Whse_A", "Whse_J"]).run(timeout=30)
        next(e for e in app.selectbox if e.label=="Warehouse detail").set_value("Whse_J").run(timeout=30)
        self.assertFalse(app.exception)
        self.assertTrue(any(e.label=="Warehouse coverage" and e.value=="2 / 4" for e in app.metric))
        group(app, "ops_warehouses").set_value(["Whse_C"]).run(timeout=30)
        self.assertFalse(app.exception)
        self.assertEqual(next(e for e in app.selectbox if e.label=="Warehouse detail").value, "Whse_C")
        group(app, "ops_horizon").set_value(None).run(timeout=30)
        self.assertFalse(app.exception)
        self.assertEqual(len(app.metric), 0)
        self.assertTrue(any("Select a forecast horizon" in e.value for e in app.info))

    def test_downloads_and_evidence_boundaries_remain_accessible(self):
        app = self.app()
        keys = {e.key for e in app.get("download_button")}
        self.assertTrue({"download_operations_selected_planning", "download_operations_selected_weekly_risk",
            "download_operations_observed_reference_comparison", "download_operations_recent_actual_reference",
            "download_operations_summary_checks", "download_operations_warehouse_detail"}.issubset(keys))
        self.assertTrue(any("December 25, 2016" in e.value and "No complete 2017 evaluation" in e.value for e in app.markdown))
        self.assertTrue(any("not physical capacity" in e.value for e in app.markdown))
        cards = next(e.value for e in app.markdown if '<div class="ops-insight-grid">' in e.value)
        for text in ["Observed fact", "Archived projection", "Illustrative implication"]:
            self.assertIn(text, cards)
        original = self.archive["weekly"].to_csv(index=False)
        pd.testing.assert_frame_equal(self.archive["weekly"], load_planning(source_directory())["weekly"])
        self.assertEqual(original, self.archive["weekly"].to_csv(index=False))

    def test_navigation_and_scoped_css_do_not_refactor_other_pages(self):
        app = self.app()
        self.assertEqual([e.label for e in app.sidebar.button], list(LABELS.values()))
        for page in [r for r in ROUTES if r != "Operational Insights"]:
            app.sidebar.button(key="nav_" + page).click().run(timeout=30)
            self.assertFalse(app.exception)
            self.assertEqual(app.session_state["navigation"],page)
            self.assertFalse(any("ops-heading" in e.value for e in app.markdown))
            app.sidebar.button(key="nav_" + "Operational Insights").click().run(timeout=30)
        expected = json.loads((ROOT/'docs/navigation_calculation_baseline.json').read_text())
        for name, digest in expected.items():
            self.assertEqual(hashlib.sha256((ROOT/name).read_bytes()).hexdigest(),digest,name)
        self.assertIn('max-width:1440px', CSS)
        self.assertIn('@media(max-width:600px)',CSS)


if __name__ == "__main__":
    unittest.main()
