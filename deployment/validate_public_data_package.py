"""Validate a future authorized data-only release. This command never builds a package."""
import argparse
import csv
from datetime import date
from hashlib import sha256
from io import StringIO
import json
from pathlib import Path, PurePosixPath
import sys

ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "docs" / "public_data_package.json"
REGISTRY = "research_overview_sources.json"
DATA_DIR = "final_research_exports"
RIDGE = {"DirectRidge", "RecursiveRidge"}
DATASETS = {"M5", "Favorita"}
HORIZONS = {1, 4, 12, 26, 52}
PARENT_LABELS = (
    "Notebook revision verification",
    "Frozen metric reconciliation",
    "V2 execution status",
    "V3 execution status",
    "R19 execution status",
)


def digest(data):
    return sha256(data).hexdigest()


def load_json(path):
    return json.loads(path.read_bytes())


def json_bytes(value):
    return (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode("utf-8")


def safe_path(root, name):
    relative = PurePosixPath(name)
    if (relative.is_absolute() or ".." in relative.parts or not relative.parts
            or relative.as_posix() != name or "\\" in name or ":" in name):
        raise ValueError("A package path must be canonical and relative.")
    target = root / relative
    if target.resolve() != target:
        raise ValueError(f"Linked path is outside the package contract: {name}")
    return target


def filter_ridge(data, complete_scope):
    reader = csv.DictReader(StringIO(data.decode("utf-8-sig"), newline=""))
    selected = [row for row in reader
                if row["dataset"] in DATASETS and row["method"] in RIDGE
                and (not complete_scope or row["scope"] == "complete_all_origins")]
    expected = {(dataset, horizon, method)
                for dataset in DATASETS for horizon in HORIZONS for method in RIDGE}
    actual = {(row["dataset"], int(row["horizon"]), row["method"]) for row in selected}
    if actual != expected or len(selected) != len(expected):
        raise ValueError("The source does not contain one selected Ridge row per cohort and horizon.")
    output = StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=reader.fieldnames, lineterminator="\n")
    writer.writeheader()
    writer.writerows(selected)
    return output.getvalue().encode("utf-8"), len(selected)


def review_payload(profile, root=ROOT):
    """Derive candidate digests in memory from the pinned sources. No files are written."""
    root = root.resolve()
    source_registry = load_json(root / REGISTRY)
    artifacts = source_registry["artifacts"]
    aliases = ("scores", "origins") if profile == "horizons" else tuple(artifacts)
    reviewed = {}
    payload = {}
    for alias in aliases:
        original = artifacts[alias]
        name = f"{DATA_DIR}/{original['path']}"
        data = safe_path(root, name).read_bytes()
        if digest(data) != original["sha256"]:
            raise ValueError(f"Frozen input hash mismatch: {name}")
        pin = {key: value for key, value in original.items()
               if key not in {"source_path", "parents"}}
        if alias in {"scores", "matched"}:
            data, pin["rows"] = filter_ridge(data, complete_scope=(alias == "scores"))
            pin["sha256"] = digest(data)
            pin["parent_sha256"] = original["sha256"]
            pin["release_selection"] = ("Direct and Recursive Ridge, complete_all_origins across both retailers and all five horizons."
                                        if alias == "scores" else
                                        "Direct and Recursive Ridge matched corrections across both retailers and all five horizons.")
        if alias == "validation_evidence":
            pin["parents"] = [
                {"source_path": label, "sha256": parent["sha256"]}
                for label, parent in zip(PARENT_LABELS, original["parents"], strict=True)
            ]
        reviewed[alias] = pin
        payload[name] = data
    payload[REGISTRY] = json_bytes({
        "revision_status": source_registry["revision_status"],
        "distribution": "Use only within the separately authorized publication scope.",
        "artifacts": reviewed,
    })
    return payload


def inventory(payload):
    return {path: {"sha256": digest(data), "bytes": len(data)} for path, data in payload.items()}


def require_authorization(record, profile, target, plan, spec_hash):
    if (not isinstance(record, dict) or record.get("status") != "authorized" or record.get("profile") != profile
            or record.get("target") != target or record.get("package_spec_sha256") != spec_hash):
        raise ValueError("An explicit human decision for the exact profile, target, and specification is required.")
    for key in ("decision_reference", "approved_by", "authority_basis"):
        if not isinstance(record.get(key), str) or not record[key].strip():
            raise ValueError(f"The human authorization record must supply {key}.")
    date.fromisoformat(record.get("approved_on", ""))
    grants = record.get("files")
    if not isinstance(grants, dict) or grants.keys() != plan["files"].keys():
        raise ValueError("Authorization must cover exactly the files in the selected profile.")
    for path, pin in plan["files"].items():
        grant = grants[path]
        if (not isinstance(grant, dict) or grant.get("sha256") != pin["sha256"]
                or not isinstance(grant.get("channels"), list)
                or not {target, "public_display"}.issubset(grant["channels"])
                or not isinstance(grant.get("evidence_reference"), str)
                or not grant["evidence_reference"].strip()):
            raise ValueError(f"File digest, display permission, destination permission or evidence missing: {path}")
    downloads = record.get("downloads", {})
    if not isinstance(downloads, dict):
        raise ValueError("Browser CSV authorization must be keyed by reviewed output scope.")
    allowed = plan["download_scopes"]
    for key, grant in downloads.items():
        if (key not in allowed or not isinstance(grant, dict) or grant.get("scope_sha256") != allowed[key]
                or grant.get("channel") != "browser_csv"
                or not isinstance(grant.get("evidence_reference"), str)
                or not grant["evidence_reference"].strip()):
            raise ValueError(f"Separate browser CSV permission is missing or out of scope: {key}")
    return sorted(downloads)


def validate_package(package, plan):
    """Validate only the data overlay, without reading from other directories."""
    root = package.resolve(strict=True)
    if package.is_symlink() or package.is_junction() or not root.is_dir():
        raise ValueError("The package must be a directory.")
    present = set()
    for path in root.rglob("*"):
        name = path.relative_to(root).as_posix()
        safe_path(root, name)
        if path.is_file():
            present.add(name)
        elif not path.is_dir() or not any(file.startswith(name + "/") for file in plan["files"]):
            raise ValueError(f"Unexpected package entry: {name}")
    expected = set(plan["files"])
    if present != expected:
        raise ValueError(f"Package membership differs. Missing {sorted(expected - present)}. Unexpected {sorted(present - expected)}.")
    for name, pin in plan["files"].items():
        data = safe_path(root, name).read_bytes()
        if digest(data) != pin["sha256"] or len(data) != pin["bytes"]:
            raise ValueError(f"Package file differs from the reviewed bytes: {name}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", required=True, choices=("horizons", "final_research"))
    parser.add_argument("--package", type=Path)
    parser.add_argument("--authorization", type=Path)
    parser.add_argument("--target", choices=("host_storage", "public_git"))
    args = parser.parse_args()
    spec_data = SPEC.read_bytes()
    plan = json.loads(spec_data)["profiles"][args.profile]
    if not any((args.package, args.authorization, args.target)):
        if inventory(review_payload(args.profile)) != plan["files"]:
            raise ValueError("In-memory candidate digests differ from the reviewed specification.")
        print(f"Verified {len(plan['files'])} proposed file digests in memory. No package was written.")
        return
    if not all((args.package, args.authorization, args.target)):
        parser.error("Validating an assembled package requires --package, --authorization and --target together.")
    downloads = require_authorization(load_json(args.authorization), args.profile, args.target, plan, digest(spec_data))
    validate_package(args.package, plan)
    print(f"Reviewed data overlay matched. Recorded browser CSV scopes: {len(downloads)}.")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, KeyError, TypeError) as exc:
        sys.exit(f"Release package validation failed: {exc}")
