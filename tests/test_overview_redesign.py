from navigation import ROUTES, LABELS
"""Overview pilot: source-derived storytelling, scoped styling and retained interaction."""
import json
import unittest
from unittest.mock import patch

import pandas as pd
from streamlit.testing.v1 import AppTest

from data_loading import ROOT, read_csv, source_directory
from display_formatting import compact_units
from future_data import WEEKLY_SOURCE
from overview_data import holdout_kpis, load_overview
from overview_design import CSS, INK, MODEL_COLORS, MUTED, TEAL, WAREHOUSE_COLORS, error_comparison, style_figure


class OverviewDesignDataTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = load_overview(source_directory())

    def test_comparison_values_order_minima_and_units_match_exports(self):
        for metric in ["WAPE (%)", "MAE", "RMSE"]:
            original = self.data["holdout"].copy(deep=True)
            figure, ranked = error_comparison(original, metric)
            pd.testing.assert_frame_equal(original, self.data["holdout"])
            self.assertEqual(list(figure.data[0].y), ranked.Model.tolist())
            self.assertEqual(list(figure.data[0].x), ranked[metric].tolist())
            self.assertTrue(ranked[metric].is_monotonic_increasing)
            self.assertEqual(len(ranked), len(original))
            colors = list(figure.data[0].marker.color)
            self.assertEqual(colors.count(TEAL), int(ranked[metric].eq(ranked[metric].min()).sum()))
            self.assertTrue(all(c in [TEAL, MUTED] for c in colors))
            styled = style_figure(figure)
            self.assertFalse(styled.layout.xaxis.rangeslider.visible)
            self.assertEqual(styled.layout.font.size, 14)

    def test_equal_minima_are_retained_without_arbitrary_winner(self):
        frame = self.data["holdout"].copy()
        frame.loc[frame.index[:2], "WAPE (%)"] = frame["WAPE (%)"].min()
        figure, ranked = error_comparison(frame, "WAPE (%)")
        self.assertEqual(list(figure.data[0].marker.color).count(TEAL), 2)
        self.assertEqual(len(ranked), len(frame))

    def test_text_contrast_and_responsive_style_are_scoped(self):
        def luminance(color):
            channels = [int(color[i:i+2], 16) / 255 for i in [1, 3, 5]]
            linear = [x / 12.92 if x <= .04045 else ((x + .055) / 1.055) ** 2.4 for x in channels]
            return sum(x * weight for x, weight in zip(linear, [.2126, .7152, .0722]))
        for foreground, background in [(INK, "#ffffff"), ("#526278", "#ffffff"),
            ("#526278", "#f5f7fb"), (INK, "#eaf5f5"), (TEAL, "#ffffff")]:
            ratio = (max(luminance(foreground), luminance(background)) + .05) / (min(luminance(foreground), luminance(background)) + .05)
            self.assertGreaterEqual(ratio, 4.5)
        self.assertIn("@media(max-width:1200px)", CSS)
        for color in set(MODEL_COLORS.values()) | set(WAREHOUSE_COLORS.values()) | {MUTED}:
            self.assertGreaterEqual(1.05 / (luminance(color) + .05), 3)
        self.assertIn("@media(max-width:700px)", CSS)
        self.assertIn("grid-template-columns:1fr", CSS)
        self.assertIn("focus-visible", CSS)
        self.assertIn(".st-key-executive_pilot", CSS)


class OverviewDesignAppTests(unittest.TestCase):
    def app(self):
        return AppTest.from_file(str(ROOT / "app.py")).run(timeout=30)

    def test_headlines_and_four_primary_kpis_are_source_derived(self):
        app = self.app()
        kpi = holdout_kpis(load_overview(source_directory()))
        self.assertFalse(app.exception)
        self.assertFalse(app.error)
        expected = {"Lowest holdout WAPE": f"{kpi['best_wape']:.2f}%",
                    "Error reduction vs baseline": f"{kpi['relative_reduction']:.1f}%",
                    "Observed 2016 demand": compact_units(kpi["demand"]), "Holdout coverage": f"{kpi['weeks']} weeks"}
        self.assertEqual({m.label: m.value for m in app.metric if m.label in expected}, expected)
        summary = next(m.value for m in app.markdown if '<div class="exec-summary">' in m.value)
        self.assertIn(kpi["best_model"], summary)
        self.assertIn(f"{kpi['best_wape']:.2f}%", summary)
        self.assertTrue(any("not independent post-selection" in m.value for m in app.markdown))
        self.assertFalse(any("PHASE 1" in c.value for c in app.caption))

    def test_observations_default_and_saved_prediction_filters_remain(self):
        app = self.app()
        self.assertEqual(app.multiselect(key="holdout_models").value, [])
        spec = json.loads(next(e for e in app.get("plotly_chart") if e.proto.id.endswith("-holdout_demand")).proto.spec)
        self.assertEqual([s["name"] for s in spec["data"]], ["Actual"])
        app.multiselect(key="holdout_models").set_value(["ETS"]).run(timeout=30)
        spec = json.loads(next(e for e in app.get("plotly_chart") if e.proto.id.endswith("-holdout_demand")).proto.spec)
        self.assertEqual([s["name"] for s in spec["data"]], ["Actual", "Saved prediction · ETS"])
        self.assertEqual(spec["data"][1]["line"]["dash"], "dash")
        next(r for r in app.selectbox if r.label == "Demand view").set_value("Monthly grouped weeks").run(timeout=30)
        self.assertFalse(app.exception)
        self.assertTrue(any("not exact calendar-month" in c.value for c in app.caption))
        monthly = json.loads(next(e for e in app.get("plotly_chart") if e.proto.id.endswith("-holdout_demand")).proto.spec)
        self.assertEqual(monthly["layout"]["xaxis"]["title"]["text"], "Month assigned from weekly timestamp")
        self.assertEqual(monthly["layout"]["yaxis"]["title"]["text"], "Sum of weekly demand (units)")
        for chart in app.get("plotly_chart"):
            spec = json.loads(chart.proto.spec)
            self.assertFalse(spec.get("layout", {}).get("xaxis", {}).get("rangeslider", {}).get("visible", False))

    def test_downloads_remain_and_future_empty_selection_is_not_zero(self):
        app = self.app()
        keys = {item.key for item in app.get("download_button")}
        self.assertTrue({"download_2016_demand_view", "download_2016_full_year_comparison", "download_warehouse_rolling_results",
            "download_recursive_warehouse_results", "download_retrospective_yearly_results", "download_retrospective_pooled_results",
            "download_archived_future_forecasts"}.issubset(keys))
        self.assertTrue(any({"Forecast_Origin", "Historical_P90", "Demand_to_P90_Ratio", "Illustrative_Risk_Level"}.issubset(frame.value.columns) for frame in app.dataframe))
        next(m for m in app.multiselect if m.label == "Forecast warehouses").set_value([]).run(timeout=30)
        self.assertFalse(app.exception)
        self.assertTrue(any(m.label == "Projected demand · selected warehouses" and m.value == "—" for m in app.metric))
        self.assertTrue(any("Select at least one warehouse" in i.value for i in app.info))

    def test_every_deep_link_reaches_correct_page_and_overview_css_is_removed(self):
        app = self.app()
        for destination in [r for r in ROUTES if r != "Executive Overview"]:
            next(b for b in app.button if b.key == "exec_nav_" + destination).click().run(timeout=30)
            self.assertFalse(app.exception)
            self.assertEqual(app.session_state["navigation"], destination)
            self.assertFalse(any("exec-summary" in m.value for m in app.markdown))
            app.sidebar.button(key="nav_" + "Executive Overview").click().run(timeout=30)
            self.assertFalse(app.exception)

    def test_partial_archived_forecast_withheld_without_disabling_historical_overview(self):
        original = read_csv
        def reader(directory, source):
            frame = original(directory, source)
            return frame.iloc[1:].copy() if source == WEEKLY_SOURCE else frame
        with patch("future_data.read_csv", side_effect=reader):
            app = self.app()
        self.assertFalse(app.exception)
        self.assertFalse(app.error)
        self.assertTrue(any("Archived outlook unavailable" in w.value for w in app.warning))
        self.assertEqual(len(app.metric), 4)
        self.assertEqual(len(app.get("plotly_chart")), 8)


if __name__ == "__main__":
    unittest.main()
