# Phase 1 validation — October 16, 2026

## Operational Insights product redesign

All **99 tests pass**, including seven new workspace tests. Numerical source checks,
filters, downloads, missing-data behavior and prior pages remain covered. All 87 source
hashes are unchanged; the other six renderers and existing shared theme also match their
pre-edit hash snapshot. Browser captures verify 1440px desktop and 390px mobile layouts,
with no horizontal page overflow and correctly stacked mobile analytical panels. See
OPERATIONAL_PRODUCT_DESIGN.md and OPERATIONAL_PRODUCT_QA.md for design and evidence.

## Phase 3 addition: Executive Overview design pilot

All **92 tests pass**, including eight new redesign/data-integrity checks. The pilot
retains filters, full-precision downloads and cohort boundaries. It adds source-derived
headlines, ties-aware error highlighting, monthly-axis checks, deep-link navigation,
Overview-only CSS isolation, accessible text/series colors and safe empty/archive states.
All **87** source hashes remain unchanged. Startup and HTTP 200 / ok health checks pass.
Browser content-width checks at 1109/810/511px confirm four/two/one KPI columns with
equal heights and no horizontal page overflow. See OVERVIEW_REDESIGN_QA.md for exact
metrics, browser limits, before/after screenshots and remaining recommendations.

## Phase 2 addition: Operational Insights

The complete suite passes **84 tests**: all 70 previous checks plus 14 operational
additions. New tests validate 48 exported demand/P90 ratios, 72 operational-summary
values, four recent observed means and dates, original risk labels/text, FVA baselines,
source-defined scenarios, warehouse/horizon/metric/scenario controls, empty selections,
missing/corrupt data isolation and full-precision display/download separation.
Maximum operational-summary discrepancy is 4.656612873077393e-10; maximum ratio
discrepancy is 1.1102230246251565e-16. All 87 original source hashes match the baseline.
See OPERATIONAL_INSIGHTS.md for the source and methodology inventory.

Streamlit restarted successfully and its health endpoint returned HTTP 200 / ok.
Browser checks exercised all three operational views and the 4-week planning filter;
the displayed forecast total changed from 223.72M (12 weeks) to 69.25M (4 weeks).
Historical monitoring displayed 3 warning weeks and 2 persistent warning weeks.
Scenario charts and policy tables loaded without source errors. The available preview
viewport is narrow; wider desktop visual review remains part of final QA.

## Phase 2 addition: Future Forecasting

The full suite now has **70 passing tests**: all 57 previous checks plus 13 archived-forecast
tests. They verify the Dec 25, 2016 origin, 48 aligned records, horizons 1–12 for four
warehouses, coverage before aggregation, cumulative sums, selected-denominator shares,
combined weekly peaks, exported summary consistency, invalid/duplicate/missing rows,
precision and UI filters. Valid forecasts remain visible if historical reliability
evidence is missing, while incomplete forecasts withhold totals. No interval bands,
future actuals or projected-period accuracy values are fabricated.

All 36 exported total/mean/peak comparisons pass at 0.00001 units absolute tolerance;
maximum difference is 4.656612873077393e-10 units. All 87 original source hashes match
their saved baseline. See FUTURE_FORECASTING.md for sources and exact aggregate totals.
Streamlit startup and HTTP 200 / ok health checks passed. Browser review confirmed the
weekly/cumulative projected views and 4/8/12-week summaries. The final full suite passed
all 70 tests after the test-fixture dtype warning was removed.

## Phase 2 addition: Model Validation

All **57 tests passed**: the previous 46 checks plus 11 validation additions. New tests
load all 24 validation contracts and recompute yearly/monthly/quarterly and pooled
metrics from weekly predictions. They check year/evaluation separation, filters, empty
and malformed sources, stability ranges, scenario deltas, seed summaries, calibration
percentages/counts, bias arithmetic, significance metadata gaps and monitoring nulls.
UI checks exercise every evidence area and nested diagnostic. The source-hash check
still confirms all 87 originals are unchanged. The significance inventory entry now
marks exact dates/target as unverified rather than borrowing another table's dates.

Streamlit restarted successfully at http://127.0.0.1:8501; health returned HTTP 200 / ok.
Browser review confirmed the backtesting view and the corrected empirical calibration
plot. The available preview is narrow; desktop viewport review remains useful before
public deployment. See MODEL_VALIDATION.md for the complete source/metadata inventory.

## Phase 2 addition: Warehouse Analytics

The complete suite now has **46 passing tests**, including all 38 previous checks and
eight warehouse additions. They verify actual sample counts/date coverage, statistics
and peaks against CSVs, shares for selected warehouses, alignment without zero filling,
all three metric rankings within each warehouse, separate 51/52-week samples, deep-dive
prediction alignment, and filters/empty selections. All 87 source hashes still match
the original baseline. The app restarted successfully and returned HTTP 200 / ok from
its health endpoint. See WAREHOUSE_ANALYTICS.md for sources and interpretation limits.

## Phase 2 addition: Model Comparison

The full suite now has **38 passing tests**: the 27 previous tests plus 11 new tests.
All earlier Executive Overview/Historical Demand regressions and source-preservation
checks were run. New numerical tests cover aligned metrics for the annual shared
models, retrospective folds/pooled cohort, and recursive horizons/warehouses. Ranking
guards reject mixed periods/horizons/targets/methodologies/samples and invalid scores.
UI tests exercise all four groups, metric/model/fold/warehouse/horizon controls, missing
predictions, unexported recursive metrics and the separate reconciliation diagnostic.
Display tests verify K/M/B formatting, CV percentages and unchanged full-precision data.
All 87 originals still match their saved SHA-256 baseline. See MODEL_COMPARISON.md.
Fresh Streamlit startup and HTTP 200 / ok health check passed. Browser review found
and resolved repeated bar labels; tests now verify each plotted label against its model's
exported metric. The complete 38-test suite passed again after that correction.

## Phase 2 addition: Historical Demand

The full suite now contains **27 passing tests**, including nine new historical
analysis checks. All existing tests were run. Numerical checks verify actual-only
deduplication, total/count preservation at every aggregation level, agreement with the
exported monthly actual totals, warehouse partial coverage, seasonal means, sample CV,
gap handling and malformed inputs. AppTest exercised all aggregation levels and filters,
including empty selections. The original 87-file SHA-256 preservation check still passes.
See HISTORICAL_DEMAND.md for methods and source limitations.
The app was restarted with the new modules; its health endpoint returned HTTP 200 / ok,
and the Historical Demand page was verified in the browser.

## Automated checks

`python -m unittest discover -s tests -v`: **18 tests passed**.

- All 74 actual CSV files parse and have documented schemas/evaluation contexts.
- Recomputed all nine yearly MAE/RMSE/WAPE rows from 468 weekly prediction records.
- Recomputed pooled 2014–2015 WAPE from 104 weeks per model, excluding 2016.
- Verified agreement between full-year and yearly holdout metrics for shared models.
- Verified demand deduplication and monthly sums; no triple-counting across model rows.
- Recomputed pooled recursive scores at 4/8/12 weeks and warehouse-level 12-week WAPE.
- Verified December 25, 2016 forecast origin and all warehouse/horizon planning totals.
- Rendered the actual-data app with Streamlit AppTest: nine Plotly figures, no errors.
- Exercised metric switching, monthly aggregation, retrospective year, warehouse,
  horizon and empty forecast/model selections. All seven navigation destinations exist.
- Tested missing-data behavior, unsafe paths, missing columns/period evidence and
  ambiguous single-row metrics using temporary fixtures only.
- All **87 source files** match the SHA-256 hashes recorded before implementation.

Only the benign Streamlit bare-test ScriptRunContext warning remains in test output.
No actual-data test failures or app exceptions remain.

## Running server and browser review

The app runs at http://127.0.0.1:8501. The health endpoint returned **HTTP 200 / ok**.
Browser review confirmed the KPI cards, 2016 chart/model summary, and separate
retrospective results. A stale-server module import error was resolved by restarting
the server after adding new Python modules. Narrow-screen header spacing was adjusted.
The browser preview available in this session was narrow; a full desktop visual review
across multiple screen sizes remains useful before public deployment.

## Verification limits

Five models in the eight-row annual comparison have summary scores but no exported
weekly predictions in this bundle; their numeric scores cannot be independently
recomputed here. The README establishes their annual cohort. Warehouse rolling summary
metrics likewise lack a complete CSV prediction export, so the app presents the original
scores and labels sample sizes rather than recomputing them from a different subset.
Exact windows for 23 undated supplementary exports remain unverified and excluded from
rankings. No model is retrained to fill those gaps. 2017 outcomes are unavailable.

Tested runtime: Python 3.12, Streamlit 1.66.0, Pandas 2.3.3, Plotly 6.9.0.
