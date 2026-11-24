"""Build and validate a Phase 7B data-free preview from an explicit allowlist."""
import argparse
import ast
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path, PurePosixPath
import re
import shutil

ROOT = Path(__file__).resolve().parent
MANIFEST = ROOT / "docs" / "public_release_manifest.json"
CREDENTIAL_PATTERNS = {
    "private key": r"-----BEGIN (?:[A-Z0-9]+ )*PRIVATE KEY-----",
    "access token": r"\b(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{35,}|"
                    r"AKIA[A-Z0-9]{16}|ASIA[A-Z0-9]{16}|AIza[A-Za-z0-9_-]{35}|"
                    r"xox[baprs]-[A-Za-z0-9-]{16,}|sk-(?:proj-)?[A-Za-z0-9_-]{20,})\b",
    "credential assignment": r"""(?im)^\s*(?:[\w-]*?(?:password|passwd|api[_-]?key|secret[_-]?key|access[_-]?token))["']?\s*[:=]\s*["']\S{8,}["']""",
    "credential in URL": r"https?://[^/\s:@]+:[^/\s@]+@",
}
LOCAL_PATH = r"(?i)(?<![\w])[a-z]:[\\/]|/(?:Users|home)/[^/\s<]+"
PII = r"(?i)\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b"


def redacted_findings(content):
    """Return types and line numbers. Matched values are never logged."""
    patterns = {**CREDENTIAL_PATTERNS, "workstation path": LOCAL_PATH, "email": PII}
    return [(label, content.count("\n", 0, match.start()) + 1)
            for label, pattern in patterns.items() for match in re.finditer(pattern, content)]


def checked_relative(name):
    path = PurePosixPath(name)
    if (not path.parts or path.is_absolute() or ".." in path.parts
            or "\\" in name or ":" in name or path.as_posix() != name):
        raise ValueError(f"Invalid release path: {name!r}")
    return path


def stage_files(root=ROOT, manifest_path=MANIFEST):
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    data = manifest["data_candidates"]
    if manifest["approved_public_data"] or any(row["public_status"] != "pending" for row in data):
        raise ValueError("Phase 7B preview expects an empty public data approval list.")
    names = manifest["stage_files"]
    if len({name.casefold() for name in names}) != len(names):
        raise ValueError("Duplicate staged filenames.")
    required = {"app.py", "run_dashboard.py", "release_policy.py", "render.yaml",
                "requirements.txt", ".streamlit/config.toml", "dashboard_sources.json"}
    if not required.issubset(names):
        raise ValueError("Missing a required runtime file.")
    root = root.resolve()
    inputs = []
    for name in names:
        rel = checked_relative(name)
        is_source = len(rel.parts) == 1 and rel.suffix == ".py"
        if not is_source and name not in required:
            raise ValueError(f"Non-runtime item in the data-free stage: {name}")
        file = root / rel
        if file.resolve() != file or not file.is_file():
            raise ValueError(f"Missing or linked staged file: {name}")
        violations = redacted_findings(file.read_text(encoding="utf-8"))
        if violations:
            raise ValueError(f"Release scan flagged {name}: {violations}")
        inputs.append(file)
    modules = {file.stem for file in root.glob("*.py")}
    staged_modules = {file.stem for file in inputs if file.suffix == ".py"}
    for file in inputs:
        if file.suffix != ".py":
            continue
        tree = ast.parse(file.read_text(encoding="utf-8"), filename=file.name)
        for node in ast.walk(tree):
            imports = [item.name for item in node.names] if isinstance(node, ast.Import) else (
                [node.module] if isinstance(node, ast.ImportFrom) and node.module else [])
            missing = {name.split(".")[0] for name in imports} & (modules - staged_modules)
            if missing:
                raise ValueError(f"Staged {file.name} requires excluded modules: {sorted(missing)}")
    return inputs


def prepare_stage(destination, root=ROOT, manifest_path=MANIFEST):
    sources = stage_files(root, manifest_path)
    destination = destination.resolve()
    destination.mkdir(parents=True, exist_ok=False)
    for source in sources:
        target = destination / source.relative_to(root.resolve())
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
    return len(sources)


def verify_pins(root=ROOT, manifest_path=MANIFEST):
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    counts = Counter()
    for record in manifest["data_candidates"] + manifest["local_hash_checks"]:
        file = root / checked_relative(record["path"])
        if not file.is_file() or sha256(file.read_bytes()).hexdigest() != record["sha256"]:
            raise ValueError(f"Missing or changed pinned file: {record['path']}")
        counts[record["group"]] += 1
    return counts


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", type=Path, help="New directory for the data-free preview")
    parser.add_argument("--verify-pins", action="store_true", help="Verify local study inputs")
    args = parser.parse_args()
    print(f"Validated {len(stage_files())} data-free preview files.")
    if args.stage:
        print(f"Copied {prepare_stage(args.stage)} files to isolated staging.")
    if args.verify_pins:
        for group, count in sorted(verify_pins().items()):
            print(f"{group}: {count} SHA-256 matches")


if __name__ == "__main__":
    main()
