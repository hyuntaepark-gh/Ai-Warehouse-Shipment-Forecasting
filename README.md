# Supply Chain Analytics Dashboard — Version 1

A Python, Streamlit, Pandas and Plotly portfolio application presenting existing results
from a 15-week academic capstone. It is a read-only historical analytics dashboard:
no models are trained, no new forecasts are produced, and no original outputs are edited.

## Operational Insights — new product design reference

Operational Insights now uses a wider planning workspace, four headline KPIs, compact
filters, a warehouse threshold comparison, weekly heatmap and selected-warehouse detail
panel. Observed facts, archived projections and illustrative implications are distinct.
Full tables, methodology and source inventories are available on demand. All previous
evidence views, filters, limitations and full-precision CSV downloads remain available.
Only this page and its new scoped components were redesigned; other page renderers and
the existing theme retain their pre-edit hashes.

See the [product design system](docs/OPERATIONAL_PRODUCT_DESIGN.md) and
[QA report with 1440px before/after and 390px mobile screenshots](docs/OPERATIONAL_PRODUCT_QA.md).
The full suite passes **99 tests**; all **87 original source hashes remain unchanged**.

## Phase 3 — Executive Overview design pilot

The seven-page [UI/UX audit](docs/UI_UX_AUDIT.md) was recorded before redesign.
The [design system](docs/DESIGN_SYSTEM.md) defines typography, spacing, cards,
accessible colors, chart conventions and responsive layouts. Only Executive Overview
adopts the pilot: a concise research summary, four integrated KPI cards, an actual-first
historical trend, full-width model comparison, warehouse highlights, question-led
sections and six navigation actions. Prior filters/downloads are retained; detailed
retrospective and archived-future analysis is available on demand. Material evaluation
caveats remain visible. The other six pages retain their existing design pending review.

See [pilot QA and before/after screenshots](docs/OVERVIEW_REDESIGN_QA.md).

## Run locally

From this project directory in PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m streamlit run app.py --server.address 127.0.0.1 --server.port 8501 --browser.gatherUsageStats false
```

Open [localhost:8501](http://127.0.0.1:8501). The default source is
`capstone_final_outputs` beside `app.py`. To use another read-only copy:

```powershell
$env:CAPSTONE_DATA_DIR = 'D:\path\to\capstone_final_outputs'
```

Use Refresh source files after replacing inputs. Restart the server after adding new
Python modules. The app reports missing files, schema changes, malformed dates and
non-finite values instead of substituting sample results.

## Implemented Executive Overview

The seven-page sidebar is preserved. Executive Overview, Historical Demand, Model
Comparison, Warehouse Analytics, Model Validation, Future Forecasting and Operational
Insights are implemented for the available exports.

- Four CSV-derived KPI cards: lowest 2016 holdout WAPE and model, relative WAPE reduction
  versus Seasonal Naive in the same cohort, observed demand, and dated weekly coverage.
- **2016 full-year holdout:** interactive actual demand with selectable forecast overlays;
  weekly/monthly grouped views; an eight-model comparison with WAPE/MAE/RMSE selection;
  and quarterly error heatmap. TimesFM, ETS and Seasonal Naive have exported weekly
  predictions; the other five models have summary scores only.
- **2014–2015 retrospective:** separate annual comparisons, exported pooled metrics and
  selectable historical demand years. Pooled WAPE is never a mean of annual percentages.
- **Warehouse diagnostics:** warehouse-filtered rolling model scores plus a separately
  labeled early-2016 recursive comparison. Whse_J has 51 rolling test weeks; the other
  warehouses have 52. The recursive backtest includes A/C/S only.
- **Archived future outlook:** December 25, 2016 origin, warehouse selection and 4/8/12-week
  planning horizons. Forecast curves and operational labels come directly from exports.
- Consistent Plotly styling, zoom/pan/hover, data downloads, per-panel sources, limitations,
  original capstone conclusions, and an inventory/schema browser for all 74 CSVs.

Actual demand is deduplicated across model rows before aggregation. Monthly views
assign an entire weekly observation to the month of its recorded timestamp. They are
not exact daily calendar-month totals. Demand units are order quantities, not shipments.

## Historical Demand Analysis

The Historical Demand page adds actual-demand trends, annual/quarterly/monthly
comparisons, monthly mean-weekly seasonality heatmaps, distribution plots, variability
statistics, year and aggregation filters, coverage evidence and downloads. Warehouse
filters appear only for the separate four-warehouse 51-week 2016 sample. All charts use
actual observations, never prediction columns; missing observations are not filled.

See [Historical Demand sources, methods and limitations](docs/HISTORICAL_DEMAND.md).
The aggregate sample has 156 distinct weekly actuals across 2014–2016. The warehouse
sample has 204 warehouse-weeks from Jan 10–Dec 25, 2016. Daily transaction history and
a complete multi-year warehouse series are unavailable. Monthly bucket totals are
explicitly labeled as sums grouped by weekly timestamp, not exact calendar-month totals.

## Model Comparison

Four separate evaluation groups expose comparable WAPE/MAE/RMSE rankings, model types,
evaluation metadata, actual-vs-predicted charts where available, filters, readable tables
and full-precision CSV downloads. Model Comparison uses no Plotly range sliders. Annual,
retrospective, rolling warehouse and recursive scores are never merged into one ranking.
Unverified supplementary exports are browsable but unranked. Per-warehouse recursive
4/8-week scores are not fabricated when only prediction rows are available.

See [Model Comparison methods, sources and limitations](docs/MODEL_COMPARISON.md).
The Model Comparison iteration passed 38 tests. Shared display formatting uses K/M/B
demand/error units and percentage CV while leaving numeric download data intact.

## Warehouse Analytics

The new warehouse page compares observed demand, weekly mean, variability, counts and
selected-sample shares for the four warehouses. Multi-warehouse trends and monthly
patterns use the aligned Jan 10–Dec 25, 2016 actual sample. Rolling model rankings are
separate for each warehouse and metric; 51-week actuals are never annualized or used
to recompute the 52-week exported scores. The deep dive labels the aligned reconciliation
prediction diagnostic separately from missing complete rolling CSV prediction traces.

See [Warehouse Analytics sources, features and limitations](docs/WAREHOUSE_ANALYTICS.md).
The warehouse iteration passed 46 tests, including eight new warehouse checks; see the
Model Validation section for the current suite total. All 87 original capstone files remain unchanged.

## Model Validation

Seven evidence areas cover historical backtesting, monthly/quarterly stability, external
M5 results, simulated quality/disruption tests and seed sensitivity, empirical uncertainty
and bias, statistical/leakage/monitoring diagnostics, and 12-week recursive validation.
Results retain their own evaluation scope; retrospective, selection-fold and holdout
limitations are explicit. No new rankings or prediction intervals are added.

The page reads 24 validation CSVs plus the weekly prediction export for dated backtest
coverage. It reports unknown dates/protocols rather than borrowing them from similarly
sized samples. Calibration percentages are checked against covered/observation counts.
Leakage audit PASS entries remain exported assertions, not independently rerun checks.

See [Model Validation sources and research limitations](docs/MODEL_VALIDATION.md).
The Model Validation iteration passed 57 tests. All 87 original files remain unchanged.

## Future Forecasting

The archived forecast page verifies the December 25, 2016 origin and complete four-warehouse
12-week coverage before showing quantities. Weekly/cumulative charts, warehouse contributions,
selected combined totals and 4/8/12-week summaries come from validated exported records.
All 36 total/mean/peak cross-checks agree with the original summaries. Forecasts are labeled
historical projections, with no observed 2017 accuracy, invented bounds or risk recommendations.

See [Future Forecasting sources, calculations and limitations](docs/FUTURE_FORECASTING.md).
The complete test suite now has **70 passing tests**. All 87 originals remain unchanged.

## Verified evaluation boundaries

| Cohort | Available period | Interpretation |
|---|---|---|
| Aggregate full-year holdout | Jan 3–Dec 25, 2016; 52 weeks | Year-ahead task; eight-model exported summary |
| Retrospective year-ahead | Jan 5–Dec 28, 2014; Jan 4–Dec 27, 2015 | Two 52-week folds; 104 pooled weeks per model |
| Warehouse rolling | 2016; 52 weeks A/C/S, 51 J | Different information set and grain from aggregate year-ahead |
| Common-period aggregate subset | Jan 10–Dec 25, 2016; 51 weeks | Available in supplementary exports; not merged with 52-week scores |
| Recursive warehouse backtest | Jan 3–Mar 20, 2016 | Origin at end of 2015; cumulative 4/8/12-week windows |
| Multi-horizon experiment | Mar 27–Dec 25, 2016; 40 weeks | Separate matched sample; not merged with annual scores |
| Archived future forecasts | Jan 1–Mar 19, 2017 | Origin Dec 25, 2016; no observed outcomes |

The original README explicitly documents the full-year cohort. Weekly predictions
corroborate the exact dates and scores for the three models with dated exports. Existing
HTML traces corroborate the warehouse rolling dates. The app uses CSVs for all displayed
metrics and charts; it does not scrape result values from HTML or screenshots.

ETS configuration was selected on the same 2014–2015 folds used for retrospective
reporting. The 2016 holdout was also reused for exploratory model comparisons. Neither
comparison establishes independent post-selection generalization. WAPE is weighted
absolute percentage error, not an accuracy percentage; lower is better. Relative WAPE
reduction is `(baseline WAPE - model WAPE) / baseline WAPE * 100`.

All 74 CSVs were inspected. Twenty-three supplementary tables lack enough exported
metadata to verify exact evaluation windows; they are documented as unverified and
excluded from overview rankings. The source notebook and raw input datasets are not
in this output bundle. External M5 results use another dataset. Staffing, capacity and
cost scenarios are illustrative because physical capacity and cost data are unavailable.

## Documentation and reproducibility

- [Full inventory](docs/SOURCE_INVENTORY.md): every source file, CSV columns, inferred
  types, null counts, observed date spans, exported context values and evaluation families.
- [Evaluation periods and findings](docs/EVALUATION_PERIODS.md): evidence and boundaries.
- [Navigation and Phase 2](docs/NAVIGATION.md): seven-page plan.
- [Validation](docs/VALIDATION.md): tests, server check and preservation evidence.
- `docs/source_inventory.json`: machine-readable inventory.
- `docs/source_hashes_before.json`: SHA-256 baseline of all 87 original files before work.

```powershell
python audit_sources.py
python -m unittest discover -s tests -v
```

The audit writes only under `docs/`. Actual-data tests recompute exported error metrics
and forecast totals, check UI controls, and compare original file hashes with the
preimplementation snapshot. Additional temporary-fixture tests cover defensive loaders.
Run the original-hash test against this exact bundled copy, not a different source folder.

## Code structure

- `app.py`: page configuration, theme and seven-page navigation.
- `overview.py`: retained shared chart/download helpers and the Overview pilot entry point.
- `executive_overview.py`: insight-led Executive Overview pilot and retained research controls.
- `overview_design.py`: Overview-scoped styling, cards and Plotly theme; no specialist-page restyling.
- `overview_data.py`: table contracts, validation and presentation aggregations.
- `historical.py`: Historical Demand Analysis UI, filters, charts and interpretation.
- `historical_data.py`: actual-only history, observed-period aggregation and variability.
- `model_comparison.py`: scoped comparison UI, rankings and aligned prediction charts.
- `comparison_data.py`: explicit comparison cohorts, prediction validation and ranking guards.
- `display_formatting.py`: shared display-only K/M/B and CV-percentage formatting.
- `warehouse.py`: Warehouse Analytics views, filters, charts, insights and downloads.
- `warehouse_data.py`: reviewed actual sample, aligned comparisons, warehouse statistics and scoped rolling ranks.
- `model_validation.py`: evidence-focused validation UI and research interpretations.
- `validation_data.py`: validation source contracts, period filters, coverage-scale checks and missing-data handling.
- `future_forecasting.py`: archived forecast page, interactive views and scoped reliability context.
- `future_data.py`: strict archive coverage/origin checks, summary reconciliation and cumulative quantities.
- `operational_insights.py`: archived planning indicators, historical monitoring and illustrative scenarios.
- `operational_data.py`: risk arithmetic, planning reconciliation, recent actual references and supplementary contracts.
- `data_loading.py`: read-only CSV access, path validation and schema inventory.
- `source_catalog.py`: reviewed evaluation families, evidence and limitations.
- `dashboard_sources.json`: explicit table-role bindings; no metric values.
- `audit_sources.py`: reproducible documentation generator.
- `tests/`: actual-data regressions and missing-data/source safety checks.

## Phase 2

All seven pages are implemented for the available exports. Operational Insights adds
warehouse/horizon filters, original risk labels, demand/P90 ratios, verified recent
actual references, bias and archived monitoring, source-defined scenarios, illustrative
capacity/loss tables and separate FVA context. Its downloads retain full precision;
undocumented rules and assumptions remain explicit. See
[Operational Insights sources, checks and limitations](docs/OPERATIONAL_INSIGHTS.md).
The complete suite passes **105 tests**, including the Overview, Operational Insights and navigation checks;
all **87 original source hashes are unchanged**.
Richer historical
product/category or transaction analysis requires additional raw data. Resolve missing evaluation metadata from the
original notebook before using undated supplementary experiments in comparisons.
No retraining or live forecasting is required by this roadmap. Add deployment packaging
and large-bundle caching only when the intended hosting environment is selected.


## Phase 3 · Portfolio UI refinement (seven-page edition)

The shared navigation now uses **Warehouse IQ · Demand Intelligence** branding,
four business-oriented groups and seven icon-based native Streamlit buttons.
A 252px sidebar replaces the radio list and Planning Insights popover. New page
titles match the menu, while existing route identities, filters, calculations and
downloads remain intact. The historical study and archived status stay visible.
See the [navigation design system](docs/NAVIGATION_REDESIGN.md) and
[QA results with desktop/mobile screenshots](docs/NAVIGATION_QA.md).

The application now shares a unified business-intelligence theme across the seven
views. Each specialist page opens with a question-led summary and short context
labels; major result panels use consistent card, typography and Plotly styling.
Research limitations remain visible, with full-precision exports and technical
metadata available in expandable details. The original data directory remains
read-only. The 2016 holdout, 2014–2015 retrospective diagnostics and 2016-origin
archived future projections are **not** interchangeable.

On Windows, open a terminal in the project root and run:

```powershell
python -m pip install -r requirements.txt
python -m streamlit run app.py
python -m unittest discover -s tests -v
```

Visit http://localhost:8501. Before publicly deploying, run the browser and
mobile-width QA checklist in `docs/PHASE3_DELIVERY.md` and confirm datasets to
be shared comply with source licenses and repository size limits.
