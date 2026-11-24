"""Verify page policy without creating or activating any real publication secret."""
from hashlib import sha256
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from deployment import analytics_access
from deployment.analytics_routes import PAGES
from navigation import LABELS, ROUTES


class AnalyticsGateTests(unittest.TestCase):
    def test_all_original_routes_have_independent_file_contracts(self):
        contract = json.loads(analytics_access._MANIFEST.read_bytes())
        self.assertEqual(set(PAGES), set(ROUTES))
        self.assertEqual(set(contract), set(LABELS.values()))
        self.assertEqual(len({v["profile"] for v in contract.values()}), 13)
        self.assertNotIn("foundation_summaries/m5_weekly.csv", contract["Data Foundation"]["files"])

    def test_evidence_scopes_bind_to_a_single_page_and_file_subset(self):
        full = json.loads(analytics_access._MANIFEST.read_bytes())
        profiles = {spec["profile"] for spec in full.values()}
        for page, parent in full.items():
            for key, spec in analytics_access.evidence_scopes(page).items():
                self.assertTrue(key.startswith(page + " / "))
                self.assertNotIn(spec["profile"], profiles)
                profiles.add(spec["profile"])
                self.assertTrue(spec["files"].keys() <= parent["files"].keys())
                self.assertTrue(spec["display_scope"].startswith(key + "/"))
        for dataset in ("M5", "Favorita"):
            self.assertIn(f"Forecast Horizons / {dataset}", analytics_access.evidence_scopes("Forecast Horizons"))

    def test_selected_scope_cannot_bleed_between_requests(self):
        self.assertEqual(analytics_access.retail_datasets(("M5", "Favorita")), ("M5", "Favorita"))
        with analytics_access.render_inputs({}, selection={"dataset": "M5"}):
            self.assertEqual(analytics_access.retail_datasets(("M5", "Favorita")), ("M5",))
        self.assertIsNone(analytics_access.selected("dataset"))

    def test_wrong_service_commit_page_bytes_and_preview_fail_closed(self):
        data = b"test fixture bytes"
        payload_file = "tables/test.csv"
        pin = {"sha256": sha256(data).hexdigest(), "bytes": len(data)}
        entry = {"profile":"test-page","files":{payload_file:pin},
                 "attribution_revision":"test-revision","display_scope":"Test/v1/chart"}
        scoped_entry = dict(entry, page="Test")
        raw = json.dumps({"Test / Chart": scoped_entry}).encode()
        commit = "a" * 40
        env = {"WIQ_RELEASE_MODE":"public","RENDER":"true","RENDER_SERVICE_ID":"test-service",
               "IS_PULL_REQUEST":"false","RENDER_GIT_COMMIT":commit}
        decision = {
            "status":"authorized","profile":entry["profile"],"target":"host_storage",
            "package_spec_sha256":sha256(raw).hexdigest(), "page":"Test",
            "display":{"scope":entry["display_scope"],"evidence_reference":"test fixture"},
            "approved_by":"test fixture","approved_on":"2000-01-01","authority_basis":"test fixture",
            "decision_reference":"test fixture","attribution_revision":entry["attribution_revision"],
            "render_service_id":"test-service","deployed_commit":commit,"final_release_reference":"test fixture",
            "files":{payload_file:{"sha256":pin["sha256"],"channels":["host_storage","public_display"],
                                   "evidence_reference":"test fixture"}}}
        with tempfile.TemporaryDirectory() as scratch:
            root = Path(scratch)
            manifest, scopes, approvals = root/"manifest.json", root/"scopes.json", root/"test-only.json"
            manifest.write_text("{}", encoding="utf-8")
            scopes.write_bytes(raw)
            file = root/"private-mount"/entry["profile"]/payload_file
            file.parent.mkdir(parents=True)
            with patch.object(analytics_access, "_MANIFEST", manifest), patch.object(analytics_access, "_SCOPES", scopes):
                def load(page="Test / Chart", render=env):
                    return analytics_access.approved_payload(page,render,approvals=approvals,private_mount=root/"private-mount")
                self.assertIsNone(load())
                approvals.write_text(json.dumps({"Test / Chart":decision}),encoding="utf-8")
                self.assertIsNone(load())
                file.write_bytes(data)
                self.assertEqual(load(),{payload_file:data})
                for key, value in (("RENDER_SERVICE_ID","other"),("RENDER_GIT_COMMIT","b"*40),("IS_PULL_REQUEST","true")):
                    self.assertIsNone(load(render=env | {key:value}))
                self.assertIsNone(load("Another page"))
                self.assertIsNone(load("Test"))
                self.assertIsNone(load("Test / Other chart"))
                for key, value in (("page", "Another page"),
                                   ("display", {"scope": "Other/v1/chart", "evidence_reference": "fixture"})):
                    approvals.write_text(json.dumps({"Test / Chart":decision | {key:value}}), encoding="utf-8")
                    self.assertIsNone(load())
                approvals.write_text(json.dumps({"Test / Chart":decision}), encoding="utf-8")
                file.write_bytes(data+b"changed")
                self.assertIsNone(load())
                file.write_bytes(data)
                (file.parent/"unreviewed.csv").write_bytes(data)
                self.assertIsNone(load())

    def test_render_inputs_does_not_expose_another_route(self):
        origin=Path("local-only.json")
        with analytics_access.render_inputs({"scope/a.csv":b"fixture"}):
            active=analytics_access.data_path("scope/a.csv",origin)
            self.assertEqual(active.read_bytes(),b"fixture")
            self.assertFalse(analytics_access.data_path("scope/not-reviewed.csv",origin).exists())
        self.assertEqual(analytics_access.data_path("scope/a.csv",origin),origin)
        self.assertFalse(active.exists())
