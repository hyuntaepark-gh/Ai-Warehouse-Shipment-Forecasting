"""Exact-byte package and authorization validation."""
from datetime import date
from hashlib import sha256
import json
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]

def digest(data):
    return sha256(data).hexdigest()

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
    channels = {target, "public_display"} if target == "host_storage" else {target}
    for path, pin in plan["files"].items():
        grant = grants[path]
        if (not isinstance(grant, dict) or grant.get("sha256") != pin["sha256"]
                or not isinstance(grant.get("channels"), list)
                or not channels.issubset(grant["channels"])
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
    payload = {}
    for name, pin in plan["files"].items():
        with safe_path(root, name).open("rb") as stream:
            data = stream.read(pin["bytes"] + 1)
        if len(data) != pin["bytes"] or digest(data) != pin["sha256"]:
            raise ValueError(f"Package file differs from the reviewed bytes: {name}")
        payload[name] = data
    return payload
