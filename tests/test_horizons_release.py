"""Verify the isolated pilot build and the publication boundary."""

from base64 import b64encode
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from streamlit.testing.v1 import AppTest

from deployment.prepare_horizons_release import PILOT_RELEASE, PILOT_RUNTIME, prepare_candidate
from deployment.public_horizons_gate import ATTRIBUTION_REVISION, load_approved_pilot, prepare_host_envelope
from deployment.validate_public_data_package import ROOT, SPEC, digest, inventory, json_bytes
from release_policy import PUBLIC_HOLD
from run_dashboard import launch_settings

ENTRY = ROOT / "deployment" / "public_horizons_app.py"
SERVICE = {"RENDER": "true", "IS_PULL_REQUEST": "false", "RENDER_SERVICE_ID": "test-service",
           "WIQ_RELEASE_MODE": "horizons_display"}


class HorizonsReleaseTests(unittest.TestCase):
    def test_stage_is_code_only_and_finds_all_chart_imports_from_stage(self):
        with tempfile.TemporaryDirectory(prefix="wiq pilot build ") as tmp:
            parent = Path(tmp)
            stage = parent / "candidate"
            prepare_candidate(stage)
            paths = {p.relative_to(stage).as_posix() for p in stage.rglob("*") if p.is_file()}
            self.assertEqual(paths, PILOT_RUNTIME | PILOT_RELEASE | {"render.yaml"})
            self.assertFalse(any(name.endswith((".csv", ".html", ".ipynb")) for name in paths))
            self.assertFalse((stage / "research_overview_sources.json").exists())
            blueprint = (stage / "render.yaml").read_text(encoding="utf-8")
            for line in ("python run_dashboard.py horizons-release", "value: 3.12.10",
                         "healthCheckPath: /_stcore/health", 'autoDeployTrigger: "off"',
                         "-c deployment/linux-constraints.txt"):
                self.assertIn(line, blueprint)
            command = "import forecast_horizons, deployment.public_horizons_app"
            subprocess.run([sys.executable, "-B", "-c", command], cwd=stage,
                           capture_output=True, check=True, timeout=30)
            self.assertEqual(launch_settings("horizons-release", {"PORT": "18721"}), ("0.0.0.0", 18721))
            with self.assertRaises(ValueError):
                launch_settings("horizons-release", {})

    def test_gate_checks_destination_channels_attribution_and_exact_bytes(self):
        # Isolated metadata fixture only. It points at no actual research results.
        payload = {"test-only.txt": b"Unit test sentinel"}
        spec = json_bytes({"profiles": {"horizons": {"files": inventory(payload), "download_scopes": {}}}})
        record = {
            "status": "authorized", "profile": "horizons", "target": "host_storage",
            "package_spec_sha256": digest(spec), "decision_reference": "Unit test only",
            "approved_by": "Unit test", "authority_basis": "Unit test only", "approved_on": "2026-01-01",
            "render_service_id": "test-service", "attribution_revision": ATTRIBUTION_REVISION,
            "files": {"test-only.txt": {
                "sha256": digest(payload["test-only.txt"]), "channels": ["host_storage", "public_display"],
                "evidence_reference": "Unit test only",
            }},
            "downloads": {},
        }
        files = {name: b64encode(data).decode("ascii") for name, data in payload.items()}
        with tempfile.TemporaryDirectory(prefix="wiq pilot authorization ") as tmp:
            spec_path, secret = (Path(tmp) / file for file in ("review.json", "secret.json"))
            spec_path.write_bytes(spec)

            def read(env=SERVICE, authorization=record, objects=files):
                secret.write_bytes(json_bytes({"authorization": authorization, "files": objects}))
                return load_approved_pilot(env, secret, spec_path)

            self.assertIsNone(load_approved_pilot(SERVICE, secret, spec_path))
            self.assertEqual(read(), payload)
            for change in ({"IS_PULL_REQUEST": "true"}, {"RENDER_SERVICE_ID": "wrong-service"},
                           {"WIQ_RELEASE_MODE": "local"}, {"RENDER": "false"}, {"IS_PULL_REQUEST": ""}):
                with self.subTest(env=change):
                    self.assertIsNone(read(env={**SERVICE, **change}))
            for change in ({"status": "pending_human"}, {"target": "public_git"},
                           {"attribution_revision": "different"}, {"package_spec_sha256": "different"},
                           {"files": {"test-only.txt": {**record["files"]["test-only.txt"],
                                                        "channels": ["host_storage"]}}}):
                with self.subTest(grant=change):
                    self.assertIsNone(read(authorization={**record, **change}))
            for invalid in ({"test-only.txt": "!!!!"}, {}, {**files, "unexpected": "AA=="},
                            {"test-only.txt": b64encode(b"Study data changed").decode("ascii")}):
                self.assertIsNone(read(objects=invalid))
            secret.write_bytes(b"{")
            self.assertIsNone(load_approved_pilot(SERVICE, secret, spec_path))

    def test_pending_human_decision_never_builds_host_file(self):
        with tempfile.TemporaryDirectory(prefix="wiq pilot blocked ") as tmp:
            approval, output = (Path(tmp) / file for file in ("pending.json", "host.json"))
            approval.write_text('{"status": "pending_human"}', encoding="utf-8")
            with patch("deployment.public_horizons_gate.review_payload") as review:
                with self.assertRaisesRegex(ValueError, "human decision"):
                    prepare_host_envelope(approval, output)
            review.assert_not_called()
            self.assertFalse(output.exists())
        self.assertEqual(json.loads(SPEC.read_bytes())["approved_data_files"], [])

    def test_real_local_files_do_not_populate_the_unapproved_public_entry(self):
        with patch.dict("os.environ", SERVICE):
            app = AppTest.from_file(str(ENTRY)).run(timeout=30)
        self.assertFalse(app.exception)
        self.assertEqual([info.value for info in app.info], [PUBLIC_HOLD])
        for kind in ("plotly_chart", "button_group", "table", "download_button"):
            self.assertFalse(app.get(kind), kind)
