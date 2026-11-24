"""Verify and stage this exact public-source checkout."""
import argparse
from pathlib import Path, PurePosixPath
import re
import shutil

ROOT = Path(__file__).resolve().parent

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

RUNTIME_FILES = frozenset({
    "reporting_intro.py",
    "docs/evidence_scope_pins.json",
    "bi_components.py",
    "chart_access.py",
    "comparison_data.py",
    "dashboard_sources.json",
    "data_foundation.py",
    "data_loading.py",
    "deployment/analytics_access.py",
    "deployment/analytics_routes.py",
    "display_formatting.py",
    "docs/analytical_runtime_pins.json",
    "executive_overview.py",
    "forecast_horizons.py",
    "forecast_horizons_data.py",
    "foundation_data.py",
    "future_data.py",
    "future_forecasting.py",
    "historical.py",
    "historical_data.py",
    "model_comparison.py",
    "model_strategies.py",
    "model_strategies_data.py",
    "model_validation.py",
    "numerical_stability.py",
    "numerical_stability_data.py",
    "operational_charts.py",
    "operational_data.py",
    "operational_insights.py",
    "overview.py",
    "overview_data.py",
    "overview_design.py",
    "presentation_data.py",
    "research_overview.py",
    "research_overview_data.py",
    "research_validation.py",
    "research_validation_data.py",
    "source_catalog.py",
    "ui_controls.py",
    "validation_data.py",
    "warehouse.py",
    "warehouse_data.py",
    ".streamlit/config.toml",
    "app.py",
    "cfs_area_coverage.py",
    "deployment/cfs_area_gate.py",
    "deployment/page_publication.py",
    "deployment/render_payload.py",
    "deployment/validate_public_data_package.py",
    "design_system.py",
    "docs/cfs_area_coverage_package.json",
    "navigation.py",
    "product_layout.py",
    "release_policy.py",
    "render.yaml",
    "requirements.txt",
    "run_dashboard.py",
})
SOURCE_FILES = RUNTIME_FILES | {
    "deployment/prepare_analytical_overlay.py",
    "tests/test_analytical_access.py",
    "deployment/Dockerfile",
    "deployment/prepare_linux_context.py",
    "docs/NAVIGATION_QA.md",
    "docs/NAVIGATION_REDESIGN.md",
    "README_FIRST.md",
    "deployment/linux_smoke.py",
    "display_formatting.py",
    "docs/CFS_AREA_COVERAGE_RELEASE.md",
    "docs/DESIGN_SYSTEM.md",
    "docs/NAVIGATION.md",
    "docs/PROJECT_BUILD_HISTORY.md",
    "ui_controls.py",
    ".gitattributes", ".gitignore", "deployment/linux-constraints.txt",
                                "README.md", "tests/test_release_candidate.py", "verify_public_stage.py"}


def verify_source(root=ROOT):
    """Refuse a checkout containing files outside this reviewed public source tree."""
    root = root.resolve()
    directories = {PurePosixPath(name).parent.as_posix() for name in SOURCE_FILES} - {"."}
    present = set()

    def visit(directory):
        for path in directory.iterdir():
            name = path.relative_to(root).as_posix()
            if name == ".git":
                continue
            if path.is_symlink() or path.is_junction():
                raise ValueError(f"Linked source entry: {name}")
            if name in directories and path.is_dir():
                visit(path)
            elif name in SOURCE_FILES and path.is_file():
                errors = redacted_findings(path.read_text(encoding="utf-8"))
                if errors:
                    raise ValueError(f"Release scan flagged {name}: {errors}")
                present.add(name)
            else:
                raise ValueError(f"Unexpected source entry: {name}")

    visit(root)
    if present != SOURCE_FILES:
        raise ValueError(f"Missing public source entries: {sorted(SOURCE_FILES - present)}")
    return frozenset(present)


def stage_files(root=ROOT):
    verify_source(root)
    return [root / name for name in sorted(RUNTIME_FILES)]


def prepare_stage(destination, root=ROOT):
    sources = stage_files(root)
    destination.mkdir(parents=True, exist_ok=False)
    for source in sources:
        target = destination / source.relative_to(root)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
    return len(sources)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", type=Path, help="New guarded runtime directory")
    args = parser.parse_args()
    if args.stage:
        print(f"Staged {prepare_stage(args.stage)} guarded runtime files.")
    else:
        print(f"Verified {len(verify_source())} public source files.")


if __name__ == "__main__":
    main()
