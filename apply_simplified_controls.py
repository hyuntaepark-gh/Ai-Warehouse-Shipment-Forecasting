"""Non-destructive installer for compact page filters in Warehouse IQ.

Run from the latest local project root:
    python apply_simplified_controls.py

This patch does not replace app.py or navigation.py and does not modify CSVs.
"""
from __future__ import annotations

import ast
import hashlib
from pathlib import Path
from datetime import datetime
import shutil
import sys

ROOT = Path(__file__).resolve().parent
PAGES = [
    'executive_overview.py',
    'historical.py',
    'model_comparison.py',
    'warehouse.py',
    'model_validation.py',
    'future_forecasting.py',
    'operational_insights.py',
]

HELPER = '''"""Compact, accessible dropdowns for the historical analytics dashboard.

Use a single stable selection instead of radio buttons. No calculations changed.
"""
import streamlit as st


def choice(label, options, *, index=0, horizontal=False, **kwargs):
    """Drop-in replacement for st.radio without radio-circle clutter.

    A named dropdown uses less space than a row of radio circles and cannot be
    cleared accidentally. Existing keys, labels, and default choices remain.
    """
    values = list(options)
    if not values:
        raise ValueError(f"{label}: no selection options")
    if not (0 <= index < len(values)):
        raise ValueError(f"{label}: index {index} outside available options")
    return st.selectbox(label, values, index=index, **kwargs)
'''

# Group the filters shown in the user's Model Validation screenshot. Keep all
# widget labels stable so we do not change the meaning of selections.
ORIGINAL_BACKTEST = '''    cohort = choice("Backtesting evaluation", [RETRO, HOLDOUT], horizontal=True)
    allowed = [2014, 2015] if cohort == RETRO else [2016]
    years = st.multiselect("Backtest years", allowed, default=allowed)
    models = models_filter()
    metric = choice("Backtest metric", METRICS, horizontal=True)
'''
NEW_BACKTEST = '''    # Put the two primary decisions first; hide secondary filters until needed.
    primary, measure = st.columns([1.7, 1.0], gap="medium")
    with primary:
        cohort = choice("Backtesting evaluation", [RETRO, HOLDOUT], horizontal=True)
    with measure:
        metric = choice("Backtest metric", METRICS, horizontal=True)
    allowed = [2014, 2015] if cohort == RETRO else [2016]
    with st.expander("Refine results · years and models", expanded=False):
        year_area, model_area = st.columns(2, gap="medium")
        with year_area:
            years = st.multiselect("Backtest years", allowed, default=allowed)
        with model_area:
            models = models_filter()
'''

ORIGINAL_TEMPORAL = '''    cohort = st.selectbox("Temporal evaluation", [RETRO, POOLED, HOLDOUT])
    grain = choice("Temporal resolution", ["Quarterly", "Monthly"], horizontal=True)
    years = [] if cohort == POOLED else st.multiselect("Temporal years", [2016] if cohort == HOLDOUT else [2014, 2015],
                                                      default=[2016] if cohort == HOLDOUT else [2014, 2015])
    models = models_filter(key="validation_temporal_models")
    metric = choice("Temporal error metric", METRICS, horizontal=True)
    periods = ["Q1", "Q2", "Q3", "Q4"] if grain == "Quarterly" else list(calendar.month_abbr)[1:]
    selected_periods = st.multiselect("Calendar periods", periods, default=periods, key=f"validation_periods_{grain}")
'''
NEW_TEMPORAL = '''    scope_area, time_area, metric_area = st.columns([1.5, 1.1, 1.1], gap="medium")
    with scope_area:
        cohort = st.selectbox("Temporal evaluation", [RETRO, POOLED, HOLDOUT])
    with time_area:
        grain = choice("Temporal resolution", ["Quarterly", "Monthly"], horizontal=True)
    with metric_area:
        metric = choice("Temporal error metric", METRICS, horizontal=True)
    periods = ["Q1", "Q2", "Q3", "Q4"] if grain == "Quarterly" else list(calendar.month_abbr)[1:]
    with st.expander("Refine results · years, models and months/quarters", expanded=False):
        years = [] if cohort == POOLED else st.multiselect("Temporal years", [2016] if cohort == HOLDOUT else [2014, 2015],
                                                          default=[2016] if cohort == HOLDOUT else [2014, 2015])
        models = models_filter(key="validation_temporal_models")
        selected_periods = st.multiselect("Calendar periods", periods, default=periods, key=f"validation_periods_{grain}")
'''

# Hide optional multi-select details in a short expandable filter row.
# Patterns are intentionally exact; a diverged latest Codex file is left intact.
OTHER_LAYOUTS = {
    'model_comparison.py': [(
        '''        selected = st.multiselect("Models in comparison", model_options, default=model_options, key=f"comparison_models_{group}")''',
        '''        with st.expander("Choose models to compare", expanded=False):
            selected = st.multiselect("Models in comparison", model_options, default=model_options, key=f"comparison_models_{group}")''')],
    'warehouse.py': [(
        '''    selected = st.multiselect("Warehouses to compare", sorted(history.Series.unique()),
                              default=sorted(history.Series.unique()), key="warehouse_selected")''',
        '''    with st.expander("Choose warehouses", expanded=False):
        selected = st.multiselect("Warehouses to compare", sorted(history.Series.unique()),
                                  default=sorted(history.Series.unique()), key="warehouse_selected")''')],
    'future_forecasting.py': [(
        '''    selected = st.multiselect("Forecast warehouses", WAREHOUSES, default=WAREHOUSES, key="future_selected")
    horizon = choice("Forecast horizon (weeks)", HORIZONS, index=2, horizontal=True, key="future_horizon")''',
        '''    time_area, location_area = st.columns([1, 1], gap="medium")
    with time_area:
        horizon = choice("Forecast horizon (weeks)", HORIZONS, index=2, horizontal=True, key="future_horizon")
    with location_area:
        with st.expander("Choose warehouses", expanded=False):
            selected = st.multiselect("Forecast warehouses", WAREHOUSES, default=WAREHOUSES, key="future_selected")''')],
    'operational_insights.py': [(
        '''    warehouses = st.multiselect("Planning warehouses", WAREHOUSES, default=WAREHOUSES, key="ops_warehouses")
    horizon = choice("Planning horizon (weeks)", HORIZONS, index=2, horizontal=True, key="ops_horizon")''',
        '''    time_area, location_area = st.columns([1, 1], gap="medium")
    with time_area:
        horizon = choice("Planning horizon (weeks)", HORIZONS, index=2, horizontal=True, key="ops_horizon")
    with location_area:
        with st.expander("Choose warehouses", expanded=False):
            warehouses = st.multiselect("Planning warehouses", WAREHOUSES, default=WAREHOUSES, key="ops_warehouses")''')],
}

# Update AppTest references to the native widgets used in the revised UI.
# Keep existing navigation tests untouched: the latest Codex sidebar may use
# links or buttons rather than radio controls.
TEST_REPLACEMENTS = (
    ('next(r for r in app.radio if', 'next(r for r in app.selectbox if'),
    ('app.selectbox[0].set_value(level)', 'next(s for s in app.selectbox if s.label == "Trend aggregation").set_value(level)'),
    ('app.selectbox[0].set_value(metric)', 'next(s for s in app.selectbox if s.label == "Bias diagnostic").set_value(metric)'),
)


def digest_tree(directory: Path):
    return {str(p.relative_to(directory)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(directory.rglob('*')) if p.is_file()}


def main():
    missing = [f for f in PAGES if not (ROOT / f).is_file()]
    if missing:
        print('This script must be placed in the Warehouse Demand Platform root.')
        print('Missing page modules:', ', '.join(missing))
        return 2

    data_dir = ROOT / 'capstone_final_outputs'
    old_hashes = digest_tree(data_dir) if data_dir.exists() else None
    proposed = {}
    for name in PAGES:
        path = ROOT / name
        contents = path.read_text(encoding='utf-8')
        updated = contents.replace('st.radio(', 'choice(')
        if 'choice(' in updated and 'from ui_controls import choice' not in updated:
            # Absolute project-root import; no app/router files changed.
            updated = 'from ui_controls import choice\n' + updated if not updated.startswith(('"""', "'''")) else updated
            if updated == contents.replace('st.radio(', 'choice('):
                # Insert after module docstring and future imports, if present.
                tree = ast.parse(updated)
                lines = updated.splitlines(keepends=True)
                at = 0
                for node in tree.body:
                    if (isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant) and
                            isinstance(node.value.value, str)) or isinstance(node, ast.ImportFrom) and node.module == '__future__':
                        at = node.end_lineno
                    else:
                        break
                lines.insert(at, 'from ui_controls import choice\n')
                updated = ''.join(lines)
        for before, after in OTHER_LAYOUTS.get(name, []):
            if after in updated:
                continue
            if before in updated:
                updated = updated.replace(before, after)
                print('  Simplified optional filters in', name)
            else:
                print('  NOTE: Optional filter grouping skipped in changed', name)
        if name == 'model_validation.py':
            if ORIGINAL_BACKTEST in updated:
                updated = updated.replace(ORIGINAL_BACKTEST, NEW_BACKTEST)
                print('  Grouped backtesting controls')
            else:
                print('  NOTE: Current backtesting layout differs; automatic regroup skipped')
            if ORIGINAL_TEMPORAL in updated:
                updated = updated.replace(ORIGINAL_TEMPORAL, NEW_TEMPORAL)
                print('  Grouped temporal controls')
            else:
                print('  NOTE: Current temporal layout differs; automatic regroup skipped')
        try:
            ast.parse(updated, filename=name)
        except SyntaxError as exc:
            print(f'Aborted: edited {name} would be invalid Python: {exc}')
            return 1
        if updated != contents:
            proposed[path] = updated

    # Adjust tests that explicitly expect a radio widget, without changing the
    # assertions about values, math, navigation, or original exports.
    test_dir = ROOT / 'tests'
    if test_dir.is_dir():
        for path in test_dir.glob('test_*.py'):
            contents = path.read_text(encoding='utf-8')
            updated = contents
            for before, after in TEST_REPLACEMENTS:
                updated = updated.replace(before, after)
            if updated != contents:
                ast.parse(updated, filename=str(path))
                proposed[path] = updated

    helper_path = ROOT / 'ui_controls.py'
    if not helper_path.exists():
        proposed[helper_path] = HELPER
    else:
        old = helper_path.read_text(encoding='utf-8')
        if old != HELPER:
            print('Existing ui_controls.py differs; preserve it and review manually.')
            return 1

    if not proposed:
        print('Already applied. No files changed.')
        return 0
    backup_root = ROOT / '.ui_backup' / datetime.now().strftime('%Y%m%d-%H%M%S')
    for path, updated in proposed.items():
        if path.exists():
            backup_path = backup_root / path.relative_to(ROOT)
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, backup_path)
        path.write_text(updated, encoding='utf-8')
        print('Updated:', path.name)
    if old_hashes is not None and digest_tree(data_dir) != old_hashes:
        raise AssertionError('Unexpected source-data change')
    print('Original Capstone data unchanged.')
    print('Latest app.py/navigation.py remain untouched.')
    print('UI-specific tests migrated where recognizable; rerun the complete suite.')
    print('Backups:', backup_root)
    return 0


if __name__ == '__main__':
    sys.exit(main())
