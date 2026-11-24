"""Native navigation interactions, stable route identity, and source integrity."""
import hashlib
import json
import unittest

from streamlit.testing.v1 import AppTest
from app_test_support import calculation_digest, warehouse_app

from data_loading import ROOT
from navigation import CSS, DESTINATIONS, LABELS, ROUTES, WAREHOUSE_ROUTES, navigate


class NavigationTests(unittest.TestCase):
    def app(self):
        return warehouse_app()

    def test_group_order_and_unique_route_identity(self):
        self.assertEqual(len(set(ROUTES)), 13)
        self.assertEqual(len(WAREHOUSE_ROUTES), 8)
        self.assertEqual(list(LABELS.values()), ["Research Overview", "Forecast Horizons", "Numerical Stability", "Model Strategies", "Research Validation", "Overview", "Demand Trends", "Warehouse Explorer",
            "Model Performance", "Demand Outlook", "Planning Insights", "Forecast Reliability", "Data Foundation"])
        self.assertEqual(list(dict.fromkeys(d.group for d in DESTINATIONS)),
            ["FINAL RESEARCH", "WORKSPACE", "ANALYTICS", "FORECAST & PLANNING", "RESEARCH"])
        self.assertEqual(len({d.icon for d in DESTINATIONS}), 13)

    def test_all_native_destinations_and_single_selected_state(self):
        app = self.app()
        for route in WAREHOUSE_ROUTES:
            app.sidebar.button(key="nav_" + route).click().run(timeout=30)
            self.assertFalse(app.exception, route)
            self.assertFalse(app.error, route)
            self.assertEqual(app.session_state["navigation"], route)
            self.assertEqual([b.label for b in app.sidebar.button], ["Final Research", *(LABELS[r] for r in WAREHOUSE_ROUTES)])
            self.assertFalse(app.sidebar.radio)
            self.assertEqual(len([b for b in app.sidebar if getattr(b, "key", None) == "wiq_active"]), 1)
            self.assertTrue(any("Current page: " + LABELS[route] in m.value for m in app.sidebar.markdown))
            self.assertEqual(app.title[0].value, LABELS[route])
            self.assertTrue(app.get("download_button"), route)

    def test_sidebar_is_compact_archived_and_free_of_source_controls(self):
        app = self.app()
        text = " ".join(m.value for m in app.sidebar.markdown)
        self.assertIn("Warehouse IQ", text)
        self.assertIn("Demand Intelligence", text)
        self.assertIn("Historical Study · 2014–2016", text)
        self.assertIn("No live monitoring", text)
        self.assertNotIn("RESEARCH CONTEXT", text)
        self.assertFalse(any(b.label == "Refresh source files" for b in app.sidebar.button))
        self.assertIn("width:252px", CSS)
        self.assertIn(":focus-visible", CSS)
        self.assertIn("button:hover", CSS)
        self.assertNotIn("nth-child", CSS)
        self.assertNotIn("radiogroup", CSS)

    def test_current_page_reselection_preserves_filter_and_downloads(self):
        app = self.app()
        app.sidebar.button(key="nav_Historical Demand").click().run(timeout=30)
        years = next(m for m in app.multiselect if m.label == "Available years")
        years.set_value([2016]).run(timeout=30)
        before = {d.key for d in app.get("download_button")}
        app.sidebar.button(key="nav_Historical Demand").click().run(timeout=30)
        self.assertEqual(next(m for m in app.multiselect if m.label == "Available years").value, [2016])
        self.assertEqual(before, {d.key for d in app.get("download_button")})
        self.assertFalse(app.exception)

    def test_invalid_route_rejected_and_stale_state_recovers(self):
        with self.assertRaises(ValueError):
            navigate("Unknown page")
        app = AppTest.from_file(str(ROOT / "app.py"))
        app.session_state["navigation"] = "Removed page"
        app.run(timeout=30)
        self.assertFalse(app.exception)
        self.assertEqual(app.session_state["navigation"], "Research Overview")

    def test_all_calculation_modules_and_87_original_files_unchanged(self):
        baseline = json.loads((ROOT / "docs/navigation_calculation_baseline.json").read_text())
        self.assertGreaterEqual(len(baseline), 7)
        for name, digest in baseline.items():
            self.assertEqual(calculation_digest(ROOT / name), digest, name)
        original = json.loads((ROOT / "docs/source_hashes_before.json").read_text())
        self.assertEqual(len(original), 87)
        for name, digest in original.items():
            self.assertEqual(hashlib.sha256((ROOT / name).read_bytes()).hexdigest(), digest, name)


if __name__ == "__main__":
    unittest.main()
