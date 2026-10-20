from navigation import ROUTES, LABELS
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from data_loading import DataIssue, ROOT, bound_frame, inventory, metric_value, source_path


class SourceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.directory = Path(self.temp.name)
        (self.directory / "fixture.csv").write_text(
            "date,warehouse,value\n2016-01-01,A,2\n2016-02-01,A,3\n2016-03-01,B,7\n", encoding="utf-8")
        self.binding = dict(file="fixture.csv", label="Synthetic test only", kind="historical",
                            period_start="2016-01-01", period_end="2016-02-01",
                            period_evidence="Synthetic test fixture", value_column="value",
                            date_column="date", filters={"warehouse": "A"}, aggregation="sum")

    def tearDown(self):
        self.temp.cleanup()

    def test_inventory_records_schema_without_claiming_evaluation_period(self):
        item = inventory(self.directory)[0]
        self.assertEqual(item["rows"], 3)
        self.assertIn("warehouse", item["columns"])
        self.assertEqual(item["evaluation_period"], "Unverified")
        self.assertEqual(item["observed_date_spans"]["date"]["end"], "2016-03-01")

    def test_filtered_metric_and_no_source_modification(self):
        before = (self.directory / "fixture.csv").read_bytes()
        self.assertEqual(metric_value(self.directory, self.binding), 5)
        self.assertEqual((self.directory / "fixture.csv").read_bytes(), before)

    def test_period_evidence_required(self):
        del self.binding["period_evidence"]
        with self.assertRaises(DataIssue):
            bound_frame(self.directory, self.binding)

    def test_single_rejects_multiple_rows(self):
        self.binding["aggregation"] = "single"
        with self.assertRaises(DataIssue):
            metric_value(self.directory, self.binding)

    def test_path_traversal_rejected(self):
        with self.assertRaises(DataIssue):
            source_path(self.directory, "../outside.csv")

    def test_future_origin_required(self):
        self.binding.update(kind="future", period_start="2017-01-01", period_end="2017-02-01")
        with self.assertRaises(DataIssue):
            bound_frame(self.directory, self.binding)

    def test_non_2016_historical_rejected(self):
        self.binding["period_start"] = "2015-01-01"
        with self.assertRaises(DataIssue):
            bound_frame(self.directory, self.binding)

    def test_missing_column_reported(self):
        self.binding["value_column"] = "absent"
        with self.assertRaises(DataIssue):
            bound_frame(self.directory, self.binding)


class AppTests(unittest.TestCase):
    def test_missing_sources_and_all_navigation_destinations(self):
        from streamlit.testing.v1 import AppTest
        with tempfile.TemporaryDirectory() as temp:
            with patch.dict(os.environ, {"CAPSTONE_DATA_DIR": str(Path(temp) / "missing")}):
                app = AppTest.from_file(str(ROOT / "app.py")).run(timeout=30)
                self.assertEqual(len(app.exception), 0)
                self.assertTrue(any("Capstone data unavailable" in item.value for item in app.warning))
                self.assertEqual(len(app.sidebar.button), 8)
                for page in [r for r in ROUTES if r != "Executive Overview"]:
                    app.sidebar.button(key="nav_" + page).click().run()
                    self.assertEqual(len(app.exception), 0)
                    if page == "Historical Demand":
                        self.assertTrue(any("Historical demand data unavailable" in item.value for item in app.warning))
                    elif page == "Model Comparison":
                        self.assertTrue(any("Model comparison data unavailable" in item.value for item in app.warning))
                    elif page == "Warehouse Analytics":
                        self.assertTrue(any("Warehouse analytics data unavailable" in item.value for item in app.warning))
                    elif page == "Model Validation":
                        self.assertTrue(any("Model validation data unavailable" in item.value for item in app.warning))
                    elif page == "Future Forecasting":
                        self.assertTrue(any("Future forecasting data unavailable" in item.value for item in app.warning))
                    elif page == "Data Foundation":
                        self.assertTrue(any("Data Foundation" in h.value for h in app.title))
                    else:
                        self.assertTrue(any("Operational insights data unavailable" in item.value for item in app.warning))


if __name__ == "__main__":
    unittest.main()
