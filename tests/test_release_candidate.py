"""Publication boundary checks for the clean CFS source tree."""

from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

from streamlit.testing.v1 import AppTest

from deployment.cfs_area_gate import load_approved_cfs
from deployment.page_publication import CFS_RELEASE_CHECKS, cfs_area_plan
from deployment.validate_public_data_package import validate_package
from navigation import LABELS, RESEARCH_ROUTES, ROUTES, WAREHOUSE_ROUTES
from release_policy import PUBLIC_HOLD
from verify_public_stage import ROOT, SOURCE_FILES, verify_source


class ReleaseCandidateTests(unittest.TestCase):
    def test_all_routes_remain_held_without_authorization(self):
        app = AppTest.from_file(str(ROOT / "app.py"))
        self.assertEqual(len(ROUTES), 13)
        self.assertEqual(len(set(ROUTES)), 13)
        flags = {"WIQ_RELEASE_MODE": "public", "RENDER": "true", "IS_PULL_REQUEST": "false",
                 "RENDER_SERVICE_ID": "test-service-no-grant"}
        with tempfile.TemporaryDirectory() as folder, patch.dict("os.environ", flags), \
             patch("deployment.cfs_area_gate.SECRET_FILE", Path(folder) / "missing-secret") as secret, \
             patch("deployment.cfs_area_gate.load_approved_cfs", wraps=load_approved_cfs) as gate:
            self.assertFalse(secret.exists())
            app.run(timeout=20)
            for route in RESEARCH_ROUTES:
                with self.subTest(route=route):
                    app.sidebar.button(key="nav_" + route).click().run(timeout=20)
                    self.assert_held(app, route)
            app.sidebar.button(key="nav_warehouse_track").click().run(timeout=20)
            for route in WAREHOUSE_ROUTES:
                with self.subTest(route=route):
                    app.sidebar.button(key="nav_" + route).click().run(timeout=20)
                    self.assert_held(app, route)
            self.assertEqual(gate.call_count, 1)

    def assert_held(self, app, route):
        self.assertFalse(app.exception)
        self.assertEqual(app.title[0].value, LABELS[route])
        self.assertTrue(app.subheader)
        self.assertEqual(app.info[0].value, PUBLIC_HOLD)
        for kind in ("plotly_chart", "download_button", "dataframe", "table", "metric"):
            self.assertFalse(app.get(kind))

    def test_only_data_foundation_dispatches_the_cfs_renderer(self):
        app = AppTest.from_file(str(ROOT / "app.py"))
        app.session_state["navigation"] = "Data Foundation"
        fixture = {"test-only": b"fixture"}
        with patch("deployment.cfs_area_gate.load_approved_cfs", return_value=fixture) as gate, \
             patch("cfs_area_coverage.parse_coverage", return_value=({}, ())) as parse, \
             patch("cfs_area_coverage.render_coverage") as render:
            app.run(timeout=20)
            self.assertFalse(app.exception)
            parse.assert_called_once_with(fixture)
            render.assert_called_once_with({}, ())
            self.assertFalse(app.info)
            self.assertIn("own publication clearance", app.caption[-1].value)
            app.sidebar.button(key="nav_Historical Demand").click().run(timeout=20)
            self.assert_held(app, "Historical Demand")
            gate.assert_called_once()
            render.assert_called_once()

    def test_conditional_decision_cannot_activate_the_plan(self):
        plan = cfs_area_plan()
        with self.assertRaises(ValueError):
            plan.validate({"status": "blocked", "release_checks": CFS_RELEASE_CHECKS}, service_id="test-service")
        with self.assertRaisesRegex(ValueError, "distribution of the CFS pilot files is denied"):
            plan.validate_git({}, repository="owner/repository")
        self.assertEqual(plan.download_scopes, {})

    def test_unreviewed_files_fail_source_build(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            for name in SOURCE_FILES:
                target = root / name
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / name, target)
            self.assertEqual(verify_source(root), SOURCE_FILES)
            (root / "runtime").mkdir()
            (root / "runtime" / "unreviewed.csv").write_bytes(b"example")
            with self.assertRaisesRegex(ValueError, "Unexpected source entry"):
                verify_source(root)

    def test_package_rejects_altered_file_bytes(self):
        plan = cfs_area_plan()
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            for name, pin in plan.files.items():
                (root / name).write_bytes(b"!" * pin["bytes"])
            with self.assertRaisesRegex(ValueError, "reviewed bytes"):
                validate_package(root, {"files": plan.files})


if __name__ == "__main__":
    unittest.main()
