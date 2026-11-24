"""Build private per-route payloads from frozen inputs. This does not authorize or publish them."""
import argparse
import csv
import io
from hashlib import sha256
import json
from pathlib import Path, PurePosixPath

HERE = Path(__file__).resolve().parents[1]
SPEC = HERE / "docs" / "analytical_runtime_pins.json"
SCOPES = HERE / "docs" / "evidence_scope_pins.json"


def canonical(value):
    return (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode()


def relative(root, name):
    portable = PurePosixPath(name)
    if portable.is_absolute() or not portable.parts or ".." in portable.parts or portable.as_posix() != name or "\\" in name:
        raise ValueError("Invalid overlay path.")
    result = root / portable
    if result.resolve() != result:
        raise ValueError("Linked overlay source.")
    return result


def source_bytes(root, name, scope_files, selection=None):
    selection = selection or {}
    dataset = selection.get("dataset")
    if dataset and name.startswith("final_research_exports/tables/") and name.endswith(".csv"):
        with relative(root, name).open(encoding="utf-8-sig", newline="") as original:
            reader = csv.DictReader(original)
            rows = [row for row in reader if row["dataset"] == dataset]
            if not rows:
                raise ValueError(f"No rows for the selected retailer: {name}")
            result = io.StringIO(newline="")
            writer = csv.DictWriter(result, fieldnames=reader.fieldnames, lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)
            return result.getvalue().encode("utf-8")
    if name == "research_overview_sources.json":
        source = json.loads(relative(root, name).read_bytes())
        selected = {}
        permitted = ("path", "sha256", "rows", "columns", "keys", "source_file", "run_id", "prior_run_id",
                     "experiment", "section", "protocol")
        for alias, item in source["artifacts"].items():
            if f"final_research_exports/{item['path']}" in scope_files:
                pin = {key: item[key] for key in permitted if key in item}
                if dataset and item["path"].endswith(".csv"):
                    projected = source_bytes(root, f"final_research_exports/{item['path']}", scope_files, selection)
                    pin["sha256"] = sha256(projected).hexdigest()
                    pin["rows"] = sum(1 for _ in csv.DictReader(io.StringIO(projected.decode("utf-8"))))
                if "parents" in item:
                    pin["parents"] = [{"source_path": f"Reviewed evidence input {i}", "sha256": parent["sha256"]}
                                      for i, parent in enumerate(item["parents"], start=1)]
                selected[alias] = pin
        return canonical({"revision_status": source["revision_status"], "artifacts": selected})
    if name == "foundation_summaries/manifest.json":
        source = json.loads(relative(root, name).read_bytes())
        primary = {key: value for key, value in source["primary"].items() if key != "last_record"}
        manifest = {"schema_version": source["schema_version"]}
        if selection.get("foundation") != "retail":
            manifest["primary"] = primary
        if selection.get("foundation") != "warehouse":
            manifest["m5"] = source["m5"]
        manifest["summary_files"] = {key: {"sha256": value["sha256"]} for key, value in source["summary_files"].items()
                                     if f"foundation_summaries/{key}" in scope_files}
        return canonical(manifest)
    return relative(root, name).read_bytes()


def prepare(root, destination, name):
    spec = json.loads(SPEC.read_bytes()).get(name)
    if spec is None:
        spec = json.loads(SCOPES.read_bytes())[name]
    root = root.resolve(strict=True)
    output = destination.resolve()
    if output.is_relative_to(HERE) or output.is_relative_to(root):
        raise ValueError("Use an isolated private destination outside both source trees.")
    verified = {}
    for path, pin in spec["files"].items():
        data = source_bytes(root, path, spec["files"], spec.get("selection"))
        if len(data) != pin["bytes"] or sha256(data).hexdigest() != pin["sha256"]:
            raise ValueError(f"Pinned source mismatch: {path}")
        verified[path] = data
    output.mkdir(parents=True, exist_ok=False)
    for path, data in verified.items():
        target = relative(output, path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("page")
    parser.add_argument("--private-source", type=Path, required=True)
    parser.add_argument("--destination", type=Path, required=True)
    args = parser.parse_args()
    prepare(args.private_source, args.destination, args.page)
