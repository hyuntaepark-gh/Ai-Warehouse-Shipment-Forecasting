"""Release checks exercise the data-free package as well as the full local app."""
import json
from pathlib import Path
import tempfile
import tomllib
import unittest
from unittest.mock import Mock, patch

import streamlit as st
import run_dashboard
from streamlit.testing.v1 import AppTest

from data_loading import DataIssue, source_path
from navigation import LABELS, ROUTES
from release_policy import PUBLIC_HOLD, public_data_blocked
from run_dashboard import launch_settings
from verify_public_stage import (
    MANIFEST, ROOT, checked_relative, prepare_stage, redacted_findings, stage_files,
)


class PublicReleaseTests(unittest.TestCase):
    def test_manifest_covers_routes_and_contains_no_approved_data(self):
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        candidates = {item["path"]: item for item in manifest["data_candidates"]}
        self.assertEqual(set(manifest["route_dependencies"]), set(LABELS.values()))
        self.assertFalse(manifest["approved_public_data"])
        self.assertEqual(set(candidates), {r for paths in manifest["route_dependencies"].values() for r in paths})
        for page, paths in manifest["route_dependencies"].items():
            self.assertTrue(paths)
            self.assertTrue(all(page in candidates[path]["pages"] and candidates[path]["public_status"] == "pending"
                                for path in paths))
        self.assertGreater(len(stage_files()), 30)

    def test_guard_covers_render_and_bad_modes(self):
        for env, blocked in [
            ({}, False), ({"WIQ_RELEASE_MODE": "local"}, False), ({"WIQ_RELEASE_MODE": "public"}, True),
            ({"WIQ_RELEASE_MODE": "unrecognised"}, True), ({"RENDER": "true", "WIQ_RELEASE_MODE": "local"}, True),
        ]:
            with self.subTest(env=env), patch.dict("os.environ", env, clear=True):
                self.assertEqual(public_data_blocked("127.0.0.1"), blocked)
        with patch.dict("os.environ", {}, clear=True):
            for unsafe_address in (None, "0.0.0.0", "::"):
                self.assertTrue(public_data_blocked(unsafe_address))

    def test_public_routes_cannot_read_local_data_or_register_downloads(self):
        flags = {"WIQ_RELEASE_MODE": "public", "CAPSTONE_DATA_DIR": str(ROOT / "capstone_final_outputs")}
        app = AppTest.from_file(str(ROOT / "app.py"))
        with patch.dict("os.environ", flags), patch("pandas.read_csv", side_effect=AssertionError("data read")) as read, \
             patch.object(st, "download_button", side_effect=AssertionError("download registered")) as download:
            for route in ROUTES:
                with self.subTest(route=route):
                    app.session_state["navigation"] = route
                    app.run(timeout=20)
                    self.assertFalse(app.exception)
                    self.assertEqual(app.title[0].value, LABELS[route])
                    self.assertEqual(app.info[0].value, PUBLIC_HOLD)
                    for element in ("download_button", "plotly_chart", "dataframe", "metric"):
                        self.assertFalse(app.get(element))
            read.assert_not_called()
            download.assert_not_called()

    def test_staging_copies_only_the_allowlist_and_runs_with_no_datasets(self):
        with tempfile.TemporaryDirectory(prefix="warehouse iq release ") as scratch:
            destination = Path(scratch) / "stage"
            count = prepare_stage(destination)
            self.assertEqual(count, len(stage_files()))
            self.assertEqual({p.relative_to(destination).as_posix() for p in destination.rglob("*") if p.is_file()},
                             {p.relative_to(ROOT).as_posix() for p in stage_files()})
            config = {"WIQ_RELEASE_MODE": "public", "CAPSTONE_DATA_DIR": str(destination / "missing")}
            with patch.dict("os.environ", config):
                app = AppTest.from_file(str(destination / "app.py")).run(timeout=20)
            self.assertFalse(app.exception)
            self.assertEqual(app.title[0].value, "Research Overview")
            self.assertEqual(app.info[0].value, PUBLIC_HOLD)

    def test_port_selection_and_portable_source_paths(self):
        self.assertEqual(launch_settings("local", {"PORT": "10000"}), ("127.0.0.1", 8507))
        self.assertEqual(launch_settings("render", {"PORT": "10000"}), ("0.0.0.0", 10000))
        self.assertEqual(launch_settings("preview", {"PORT": "18015"}), ("127.0.0.1", 18015))
        for value in ("", "decoy", "0", "65536", "９９"):
            with self.subTest(port=value), self.assertRaises(ValueError):
                launch_settings("render", {"PORT": value})
        for value in ("../record.csv", "./app.py", "/absolute", "Q:/private/file.csv", "data\\private.csv"):
            with self.subTest(path=value), self.assertRaises(ValueError):
                checked_relative(value)
        with tempfile.TemporaryDirectory(prefix="warehouse data ") as folder:
            root = Path(folder)
            (root / "tables").mkdir()
            (root / "tables" / "result.csv").write_text("value\n1\n", encoding="utf-8")
            self.assertEqual(source_path(root, "tables/result.csv"), root / "tables" / "result.csv")
            for path in ("tables/missing.csv", "../private.csv"):
                with self.subTest(path=path), self.assertRaises(DataIssue) as failure:
                    source_path(root, path)
                self.assertNotIn(str(root), str(failure.exception))

    def test_launcher_execs_streamlit_in_render_and_keeps_local_loopback(self):
        config = tomllib.loads((ROOT / ".streamlit" / "config.toml").read_text(encoding="utf-8"))
        self.assertEqual(config["server"]["address"], "127.0.0.1")
        self.assertEqual(config["server"]["port"], 8507)
        self.assertFalse(config["server"]["enableStaticServing"])

        linux = Mock(name="linux_os")
        linux.name = "posix"
        linux.environ = {"PORT": "10000"}
        linux.execve.side_effect = SystemExit
        with patch.object(run_dashboard, "os", linux), patch("sys.argv", ["run_dashboard.py", "render"]), \
             self.assertRaises(SystemExit):
            run_dashboard.main()
        linux.chdir.assert_called_once_with(ROOT)
        _, args, environment = linux.execve.call_args.args
        self.assertEqual(args[args.index("--server.address") + 1], "0.0.0.0")
        self.assertEqual(args[args.index("--server.port") + 1], "10000")
        self.assertEqual(environment["WIQ_RELEASE_MODE"], "public")
        self.assertEqual(environment["STREAMLIT_CLIENT_SHOW_ERROR_DETAILS"], "none")

        windows = Mock(name="windows_os")
        windows.name = "nt"
        windows.environ = {}
        with patch.object(run_dashboard, "os", windows), patch("sys.argv", ["run_dashboard.py"]), \
             patch.object(run_dashboard.subprocess, "call", return_value=0) as start:
            self.assertEqual(run_dashboard.main(), 0)
        args = start.call_args.args[0]
        self.assertEqual(args[args.index("--server.address") + 1], "127.0.0.1")
        self.assertEqual(args[args.index("--server.port") + 1], "8507")
        self.assertNotIn("WIQ_RELEASE_MODE", start.call_args.kwargs["env"])

    def test_scan_returns_categories_not_matched_values(self):
        test_text = "\n".join(("password = " + "'a-test-credential'", "ghp_" + "Z" * 36,
                               "Z:/a-private-directory", "person" + "@example.test"))
        self.assertEqual(set(redacted_findings(test_text)), {
            ("credential assignment", 1), ("access token", 2), ("workstation path", 3), ("email", 4),
        })
