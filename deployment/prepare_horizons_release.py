"""Prepare the code-only pilot or build its separately approved Render secret file."""

import argparse
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from deployment.public_horizons_gate import prepare_host_envelope
from verify_public_stage import redacted_findings, stage_files

PILOT_RUNTIME = {
    ".streamlit/config.toml", "chart_access.py", "data_loading.py", "design_system.py",
    "forecast_horizons.py", "forecast_horizons_data.py", "navigation.py", "product_layout.py",
    "release_policy.py", "requirements.txt", "research_overview.py",
    "research_overview_data.py", "run_dashboard.py", "source_catalog.py",
}
PILOT_RELEASE = {
    "deployment/linux-constraints.txt", "deployment/public_horizons_app.py",
    "deployment/public_horizons_gate.py", "deployment/validate_public_data_package.py",
    "docs/public_data_package.json",
}


def prepare_candidate(destination, root=ROOT):
    root = root.resolve()
    legacy = {file.relative_to(root).as_posix() for file in stage_files(root=root)}
    if not PILOT_RUNTIME <= legacy:
        raise ValueError("Required pilot modules are missing from the reviewed runtime.")
    files = {name: name for name in PILOT_RUNTIME | PILOT_RELEASE}
    files["render.yaml"] = "deployment/render.horizons.yaml"
    for name in files.values():
        source = root / name
        if source.resolve() != source or redacted_findings(source.read_text(encoding="utf-8")):
            raise ValueError(f"Release scan failed for {name}.")

    stage = destination.resolve()
    stage.mkdir(parents=True, exist_ok=False)
    for name, original in files.items():
        target = stage / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(root / original, target)
    return len(files)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    subcommands = parser.add_subparsers(dest="command", required=True)
    stage = subcommands.add_parser("stage")
    stage.add_argument("directory", type=Path)
    secret = subcommands.add_parser("host-envelope")
    secret.add_argument("authorization", type=Path)
    secret.add_argument("destination", type=Path)
    args = parser.parse_args()
    try:
        if args.command == "stage":
            count = prepare_candidate(args.directory)
            print(f"Staged {count} code and configuration files. No research data or authorization was packaged.")
        else:
            prepare_host_envelope(args.authorization, args.destination)
            print("Prepared a separate Render secret file for the recorded hosting grant.")
    except (OSError, ValueError, KeyError, TypeError) as exc:
        parser.exit(1, f"Release preparation failed: {exc}\n")


if __name__ == "__main__":
    main()
