"""Generate source documentation outside the original capstone folder."""
import json
from pathlib import Path
from data_loading import ROOT, inventory, source_directory


def main():
    directory = source_directory()
    records = inventory(directory)
    output = ROOT / "docs"
    output.mkdir(exist_ok=True)
    (output / "source_inventory.json").write_text(json.dumps(records, indent=2), encoding="utf-8")
    lines = ["# Source inventory", "", f"Source directory: `{directory}`", "",
             "Observed date spans describe file contents, not verified model evaluation windows.", ""]
    if not records:
        lines += ["**Blocked: source directory is missing or empty.** No CSV columns, results, figures, README, HTML dashboard, or evaluation periods were available to inspect.", ""]
    for record in records:
        lines += [f"## {record['file']}", "", f"Type: {record['type']}; size: {record['bytes']} bytes.", ""]
        if "error" in record:
            lines += [f"Read error: {record['error']}", ""]
        if "columns" in record:
            context = record["evaluation_context"]
            lines += [f"Rows: {record['rows']}. Family: **{context['family']}**.", "",
                      f"Period: {context['period']}", "", f"Evidence: {context['evidence']}", "",
                      f"Caution: {context['caution']}", "", "| Column | Inferred dtype | Nulls |", "|---|---|---|"]
            lines += [f"| {c.replace('|', '/')} | {t} | {record['null_counts'][c]} |" for c, t in record["columns"].items()]
            lines += ["", f"Observed date spans: `{json.dumps(record['observed_date_spans'])}`", ""]
            lines += [f"Exported context values: `{json.dumps(record['exported_context'])}`", ""]
    (output / "SOURCE_INVENTORY.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"Inspected {len(records)} files. Report: {output / 'SOURCE_INVENTORY.md'}")


if __name__ == "__main__":
    main()
