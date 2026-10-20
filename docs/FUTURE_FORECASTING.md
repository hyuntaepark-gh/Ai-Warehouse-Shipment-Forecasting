# Future Forecasting — Phase 2, Task 6

Implemented Future Forecasting only. The previous five pages and seven-page navigation
retain their functionality. Operational Insights remains the sole placeholder.

## Archive identity and coverage

The verified forecast origin is **December 25, 2016**. The archive contains **48 weekly
projection records**, four warehouses (Whse_A/C/J/S) with horizons 1–12 each. Forecast
timestamps span **January 1–March 19, 2017**. These are historical forward-looking
projections, not live/current forecasts or observed demand.

Before displaying any aggregate, the page validates the original complete archive:
all four warehouses, a single reviewed origin, unique warehouse/horizon and date keys,
finite nonnegative projected quantities, integer horizons 1–12, and timestamps equal to
origin plus 7 × horizon days. Missing rows, unknown warehouses, duplicates or inconsistent
dates prevent totals from being shown. No coverage is filled or extrapolated, even if
the UI selection would exclude the damaged part of the archive.

## Sources

| CSV | Use |
|---|---|
| tables/future_warehouse_weekly_forecasts.csv | Primary projected quantities, dates, origin and horizon identifiers; coverage checks and all computed views |
| tables/future_4_8_12_week_summary.csv | Cross-check all 12 warehouse/window rows against weekly totals, means and peaks |
| tables/recursive_12_week_backtest_summary.csv | Separately labeled pooled 12-week historical reliability evidence |
| tables/recursive_12_week_backtest_predictions.csv | Corroborate the historical backtest observation dates and 36 warehouse-week count |
| tables/recursive_12_week_warehouse_results.csv | Optional warehouse-specific historical evidence download, distinct from the projected quantities |

Paths are relative to `capstone_final_outputs`. `future_operational_decision_summary.csv`
was inspected and its quantity fields are also checked in tests against the weekly
records. Its risk classifications and planning recommendations are not displayed here;
they are reserved for Operational Insights. Its recent-history summary is not treated
as timestamped observed history. No original files are written.

## Implemented features

- Verified origin, projected coverage dates, complete record count and selected-scope KPIs.
- Single/multiple warehouse selection and 4/8/12-week horizon filters.
- Weekly and cumulative projected-demand lines, with an optional combined selected-total
  line. All series are labeled projected; no actual-demand overlay or interval bands.
- Warehouse projected-volume comparisons, means, peaks and percentage contribution to
  selected volume over the same horizon.
- Combined 4/8/12-week summaries plus per-warehouse summaries and full-precision downloads.
  All three window summaries remain available regardless of the chart's selected horizon.
- Source references, maximum numeric reconciliation discrepancy, and downloadable checks.
- Compact methodology/reliability context instead of a duplicate validation dashboard.
- Explicit missing-data states and independent handling of absent historical evidence.

## Calculation and numerical validation

The page derives quantities directly from validated `Predicted_Demand` records. Each
warehouse's cumulative series sums its own weeks 1 through the displayed horizon week.
Combined weekly values sum warehouses on a shared timestamp, then cumulative values
sum those combined weekly values. Combined peak demand is the maximum of those shared
weekly sums, **not** the sum of warehouse-specific peaks. Contribution denominators use
only selected warehouses and the same horizon; zero-total contributions are undefined.

All four warehouses combined:

| Window | Projected cumulative demand | Projected mean per week | Projected peak combined week |
|---|---:|---:|---:|
| 4 weeks | 69,250,338.375 | 17,312,584.59375 | 19,554,062.5625 |
| 8 weeks | 145,403,102.625 | 18,175,387.828125 | 20,626,869.3125 |
| 12 weeks | 223,720,550.875 | 18,643,379.239583332 | 21,327,790.5625 |

The 12-week total already includes the first 4 and 8 weeks. These nested window totals
must not be added together. All 36 checks (12 warehouse/window combinations × total,
mean and peak) agree with the exported summary within an absolute tolerance of **0.00001
demand units**. Maximum observed difference: **4.656612873077393e-10 units**, attributable
to floating-point representation. Main statistics use readable K/M/B display units;
downloaded values retain numeric precision. The figures above are documentation only;
the application does not hardcode these result values.

## Methodology, uncertainty and limitations

The source README describes refitting with available history and recursively generating
later weeks from prior predictions. This dashboard reads the saved output and executes
no model. Future CSVs do not encode model identity, hyperparameters or detailed fit
protocols. No identity is inferred solely from a similarly named historical procedure.

The separate historical recursive exercise has an **end-of-2015 origin** (exact date not
exported) and observations from **January 3–March 20, 2016**. At 12 weeks it includes A/C/S
only, 36 warehouse-weeks. Whse_J lacked 52 consecutive pre-origin historical weeks; that
historical exclusion does not remove its saved projections from the future archive.
Historical pooled WAPE is 59.39% for Recursive XGBoost and 70.62% for Seasonal Naive,
with substantial warehouse variation. This is retrospective diagnostic evidence, not
independent post-selection validation or accuracy for the December 2016 forecast origin.

Observed 2017 outcomes are not supplied, so no projected-period MAE/RMSE/WAPE is computed.
Valid future lower/upper bounds are absent; no confidence intervals or uncertainty bands
are generated. `Historical_P90` is a historical demand reference, not a forecast bound
or physical capacity. Historical calibration/error statistics are not converted into
future intervals. Recursive errors can propagate/persist over horizons and differ by
warehouse. No operational requirements, cause of forecast patterns, staffing levels,
capacity or financial effects are inferred. The quantities describe projected order
demand, not confirmed shipments.

## Tests and runtime verification

All **70 tests passed**: 57 previous regressions plus 13 new archive/page checks. New
tests cover origin/date/horizon integrity, complete warehouse coverage, duplicate and
non-finite rejection, cumulative sums, selected-denominator contributions, correctly
combined peaks, all summary reconciliations, full-precision display data, filters,
missing-source handling, withheld aggregates for incomplete archives, and independence
from unavailable historical evidence. The existing SHA-256 test confirms that all
**87 original source files** match their saved baseline.

Run `python -m unittest discover -s tests -v`. Start the app with
`python -m streamlit run app.py --server.address 127.0.0.1 --server.port 8501`.

Fresh Streamlit startup and HTTP 200 / `ok` health checks passed. Browser review confirmed
the archive-origin/coverage banner, warehouse/horizon controls, weekly and cumulative
projection views, and the three combined summary totals. All 70 tests passed again after
removing a test-only dtype warning. The available browser preview is narrow; desktop
viewport review remains useful before public deployment.
