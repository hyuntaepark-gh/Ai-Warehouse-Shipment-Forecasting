# Warehouse Analytics — Phase 2, Task 4

Implemented Warehouse Analytics only. Executive Overview, Historical Demand, Model
Comparison and the seven-page sidebar retain their existing functionality. Model
Validation, Future Forecasting and Operational Insights remain placeholders.

## Sources and cohort boundaries

| Purpose | CSV source | Coverage / treatment |
|---|---|---|
| Demand KPIs, aligned trends, monthly patterns | tables/hierarchical_warehouse_forecasts.csv | Demand column only; Whse_A/C/J/S, 51 weeks each, Jan 10–Dec 25, 2016; 204 warehouse-week observations |
| Rolling forecasting scores | tables/dashboard_performance_summary.csv | Naive, Random Forest, XGBoost; 52 weeks A/C/S (Jan 3–Dec 25), 51 weeks J (Jan 10–Dec 25) |
| Deep-dive prediction diagnostic | tables/hierarchical_warehouse_forecasts.csv | Original_Nonnegative and Reconciled_Forecast compared with Demand on identical 51-week timestamps; no per-warehouse reconciliation scores invented |

All source paths are relative to `capstone_final_outputs`. Rolling dates were previously
corroborated against the original HTML dashboard trace timestamps; all displayed scores
and demand values come from CSVs. No original file is modified.

The warehouse characteristics export describes training data, so its means and CVs
are not substituted for the 2016 observed sample. Early-2016 recursive validation uses
another methodology/sample and is not combined with rolling scores on this page.

## Features

- Multi-warehouse selection controls all three views. Empty selections are handled
  explicitly. Actual-demand comparisons use only dates shared by selected warehouses.
- Top KPIs show observed demand sum, combined selected mean per observed week, observed
  warehouse-week count, and actual date coverage. No 51-to-52-week annualization occurs.
- Demand characteristics: aligned actual-demand trends with weekly/monthly/quarterly
  options, sample demand totals, CV bars, readable per-warehouse statistics, and a
  heatmap of mean weekly demand by recorded calendar month with observation counts.
- Statistics include observed sum, weekly mean, sample standard deviation, CV, min/max,
  available counts, observed peak date, coverage and share of the selected sample.
- Forecast performance: WAPE/MAE/RMSE selection, grouped model bars, each warehouse's
  lowest-error model(s), all model scores/metadata and downloads. Rankings are computed
  separately within each warehouse; the side-by-side chart is not a global leaderboard.
- Deep dive: selected-warehouse KPIs and descriptive peak information, warehouse-specific
  rolling scores, and aligned actual vs predicted reconciliation trajectories with
  solid actual/dashed prediction lines. Missing complete rolling prediction CSVs are
  explicitly noted, not replaced by the reconciliation diagnostic.
- Source references, research limitations and full-precision CSV downloads for trends,
  statistics, monthly patterns, rolling scores, and aligned diagnostic predictions.

## Interpretation limits

Demand is recorded order demand, not verified shipment volume. Shares describe only
the selected warehouses and observed sample. Standard deviation uses n−1; CV is sample
standard deviation / mean weekly demand, displayed as a percentage and undefined for
nonpositive means. CV describes demand variability, not forecasting accuracy.

Calendar groups assign the entire weekly observation to its recorded timestamp's month
or quarter. They are not exact daily calendar-period transaction totals. January and Q1
have reduced coverage in the 51-week sample. No observations are filled or extrapolated;
the page rejects source coverage differing from the reviewed export rather than
silently retaining a misleading 51-week label.

Forecast rankings compare the same model cohort, target, period and one-step rolling
methodology within each warehouse. Ties are retained. They do not compare 51-week demand
statistics as if they were the denominator for 52-week score exports, establish
statistical superiority, or claim independent post-selection validation. A/C/S and J
have different score sample lengths. MAE/RMSE also depend on demand scale. Exact rolling
fit/update details are not exported.

The deep-dive reconciliation chart describes a separate historical transformation of
warehouse forecasts. It does not provide the missing Naive/Random Forest rolling
trajectories or establish that reconciliation improves a particular warehouse's accuracy.
No error metrics are manufactured for that diagnostic.

Raw daily transactions, full multi-year warehouse histories, physical capacity, staffing,
inventory and costs are unavailable. No operational requirements or causes of demand
spikes/drops are inferred. One partial historical year supports descriptive monthly
patterns, not proof of stable seasonality.

## Validation

The complete suite has **46 passing tests**: all 38 previous checks plus eight new
warehouse tests. New tests cover actual sample coverage, statistics and peak dates,
selected-denominator shares, aligned dates without filling, rejection of unknown or
duplicate observations, all three metric rankings per warehouse, 51/52-week separation,
diagnostic actual/predicted alignment and UI filters/empty selections/range-slider absence.
The original SHA-256 check confirms all **87 source files** remain unchanged.

The Streamlit server was restarted at http://127.0.0.1:8501. Its health endpoint returned
HTTP 200 / `ok`. Browser review confirmed the demand view, within-warehouse model
comparisons and the separately labeled deep-dive predictions render successfully.
The available browser preview is narrow; desktop viewport review remains useful before
public deployment. All 46 tests passed again after the final table-layout refinements.
