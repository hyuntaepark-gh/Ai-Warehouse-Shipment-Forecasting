# Phase 3 delivery — Seven-page BI presentation refresh

## What changed

This iteration refines the existing historical-research app in place. It does **not** add forecasting or change any Capstone exports.

| View | Visible presentation change | Evidence boundary maintained |
|---|---|---|
| Executive Overview | Existing source-derived redesign retained; navigation and shell now use common branding and color system | 2016 aggregate 52-week holdout, separate retrospective and warehouse cohorts |
| Historical Demand | Answer-first, source-scoped page introduction; 2014–2016 or 51-week warehouse context; dynamically derived highest observed period; more useful section questions; detailed variability table collapsible | Counts actual demand once; weekly timestamp-based buckets remain descriptive, never exact daily/monthly transaction totals |
| Model Comparison | Evaluation question up front; compact visible cohort identity; source and method details expandable; winner highlighted narratively; full ranking table expandable | No cross-cohort ranking and no statistical-superiority claim |
| Warehouse Analytics | Scannable page introduction and question-led headings; highest selected observed demand share highlighted; shared chart style and color palette | 51-week observed sample separate from rolling 51/52-week scores and reconciliation diagnostic |
| Model Validation | Reliability-first headline and key research boundary; consistent chart surfaces across evidence panels | Post-selection, revisited 2016 holdout and unverified protocols remain labeled |
| Future Forecasting | Source-scoped archived-origin identity; live horizon-dependent projection insight; clearer time-window and contribution questions; detailed window table collapsible | Dec 25, 2016 origin; no 2017 observations, new accuracy numbers or invented intervals |
| Operational Insights | Plain-language decision-support introduction and warning; prominent reminder that planning indicators are illustrative | No physical capacity, headcount, inventory, causal disruptions or verified cost benefits inferred |

## Shared design system

- `design_system.py` holds the palette, compact narrative cards, seven page stories, sitewide responsive styles and the shared Plotly chart presentation function.
- `app.py` provides the persistent brand/navigation and the common specialist-page introduction. The original **radio labels and widget keys remain unchanged** for existing automated UI tests.
- `overview.py` and `model_comparison.py` route specialist charts through the same axis, hover, legend, font and grid style; chart traces/data are unchanged.
- KPI cards, controls and visual tables share consistent surface, spacing and contrast rules. Dense raw tables are increasingly available on demand rather than preceding interpretation.
- All CSV downloads preserve the source numeric precision; no formatting is written back into data frames/exports.

## QA performed in this delivery environment

1. All modified Python files parsed and compiled successfully.
2. SHA-256 digest of **every one of the 87 original `capstone_final_outputs/` files** matched the source ZIP and existing hash manifest.
3. Independent offline data-contract checks passed (run `python verify_release.py`): 8 models in 2016 52-week holdout; 156 distinct 2014–2016 aggregate actual weeks; 48 archived warehouse/horizon projection rows; 36 numeric summary comparisons; 4/8/12-week cumulative totals align with source.
4. The modified package was assembled without `__pycache__`, local virtual environments, secrets or `.git` directories.

**Not verified in this environment:** The supplied repo reports a prior 92-test passing result. Those tests **have not been rerun on these changes** because Streamlit is not installed in the available environment and package-network access is unavailable. Browser layout, visual screenshots, live interactions, responsive and cross-browser checks therefore still require running locally. Do not treat offline source checks as equivalent to passing the full Streamlit tests.

## Required local acceptance testing

From the project root (PowerShell):

```powershell
python -m pip install -r requirements.txt
python verify_release.py
python -m unittest discover -s tests -v
python -m streamlit run app.py
```

Open `http://localhost:8501` and check the following **at desktop, tablet and phone widths**:

- All seven sidebar destinations open without errors; page introductions and KPI cards fit without horizontal clipping.
- On Historical Demand: switch aggregate/warehouse scope; change year, aggregation, and warehouse filters; empty selections show honest missing-data states.
- On Model Comparison: change cohorts and WAPE/MAE/RMSE; verify only same-cohort rankings and retained CSV downloads; check aligned predictions where available.
- On Warehouse Analytics: compare demand, within-warehouse rankings and the separate reconciliation diagnostic; the 51-week caveat is readable.
- On Model Validation: traverse all seven evidence areas and change nested filters; check no unsupported independent-validation claims.
- On Future Forecasting: switch 4/8/12 weeks, warehouses and weekly/cumulative modes; 2016 archive date stays visible; no invented confidence interval.
- On Operational Insights: review the original exported Normal/Watch classifications and the separate, illustrative scenarios without implicit severity or savings claims.
- Export a CSV in each page and check the underlying numeric values are not rounded or reformatted; compare against the original source where applicable.
- Check browser zoom at 100% and 125%, keyboard Tab focus, Chrome and Edge at minimum; review long model/warehouse labels and hover annotations.

## Deferred work / source limitations

- Missing verified dates and research protocols for certain supplementary exports remain unresolved. The original notebook is the appropriate source for clarifying definitions, not UI inference.
- No complete rolling prediction traces, raw daily/product series, current warehouse data, observed 2017 results or validated forecast bounds were added.
- This is a **historical research analytics dashboard (Version 1)**. User uploads, real-time feeds and model execution are reserved for Version 2.
- Before public deployment, verify the rights to redistribute data/figures and decide whether to host full CSV exports or publish a reduced safe subset.
