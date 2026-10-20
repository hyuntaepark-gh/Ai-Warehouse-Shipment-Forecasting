# Model Validation — Phase 2, Task 5

Implemented Model Validation only. All four existing analysis pages and the seven-page
navigation are preserved. Future Forecasting and Operational Insights remain placeholders.
The page focuses on evidence and interpretation limits, without adding performance rankings.

## Evidence areas and CSV sources

All paths below are under `capstone_final_outputs/tables/`. The page reads 24 validation
exports, plus one weekly prediction export used to corroborate dated backtest coverage.

| Evidence area | Source files | Treatment |
|---|---|---|
| Historical backtesting | timesfm_historical_yearly_results.csv; timesfm_historical_weekly_predictions.csv | 2014–2015 retrospective folds shown separately from the 2016 holdout reference; TimesFM, ETS and Seasonal Naive; year/model/metric filters |
| Quarterly stability | timesfm_historical_quarterly_results.csv; timesfm_historical_quarterly_pooled.csv; timesfm_quarterly_stability_summary.csv | Separate yearly and pooled retrospective views; heatmap, trend, period and model filters |
| Monthly stability | timesfm_historical_monthly_results.csv; timesfm_historical_monthly_pooled.csv; timesfm_monthly_stability_summary.csv | Existing weekly observations grouped by recorded month; weekly WAPE and summed-month APE have different meanings |
| External M5 | m5_external_validation.csv | Reported XGBoost and Seasonal Naive metrics; no cross-dataset rankings or inferred dates/horizon |
| Quality and disruption stress tests | data_quality_impact.csv; data_disruption_robustness.csv | Simulated scenarios, exported baseline changes, no claim of observed real-world disruption |
| Seed sensitivity | random_seed_stability.csv; random_seed_stability_summary.csv | Categorical seed scatter and exported summaries; seed choice is not a time axis |
| Calibration and uncertainty | forecast_calibration.csv; week7_uncertainty.csv; quantile_comparison.csv; quantile_warehouse_results.csv | Coverage versus target, interval-width evidence and quantile summaries; no prediction bands reconstructed |
| Bias | forecast_bias_summary.csv; forecast_bias_quarterly.csv | Warehouse selection, quarterly signed-error/underforecast-rate diagnostics and reported counts |
| Statistical evidence | forecast_significance_test.csv | Exported mean loss difference, HAC-labeled p-value and 95% interval only; exact dates and test method remain unverified |
| Leakage assertions | data_leakage_audit.csv | Original Check/Status/Details and reported-status filter; details are blank, not replaced with invented audit evidence |
| Monitoring | model_monitoring_2016.csv | Historical rolling WAPE with exported warning flags and quarter filter; missing initial values remain missing |
| Recursive validation | recursive_12_week_backtest_summary.csv; recursive_12_week_warehouse_results.csv; recursive_12_week_backtest_predictions.csv | 12-week pooled scores and warehouse-specific differences; no fabricated individual 4/8-week scores |

## Periods and selection limitations

The aggregate year-ahead observations span Jan 5–Dec 28, 2014; Jan 4–Dec 27, 2015; and
Jan 3–Dec 25, 2016, with 52 weekly observations per model/year. Retrospective and holdout
filters cannot combine those evaluation classes. ETS structure was selected on the same
2014–2015 folds used for retrospective reporting. The later reuse of 2016 for exploratory
model comparison/framework selection prevents independent post-selection interpretation.

Pooled quarterly/monthly WAPE rows use total weekly absolute error divided by total actual
demand across 2014–2015, not arithmetic averages of year/period percentage errors. The page
reads those pooled rows, rather than reconstructing pooled errors from summary percentages.
Pooled RMSE is likewise not a simple mean of annual RMSE. Stability-summary ranges are
percentage-point differences across the full exported retrospective calendar periods.
They remain explicitly separate from chart period/year filters, including when the chart
shows 2016. Descriptive winner counts in the source are not significance tests.

Calendar-month/quarter diagnostics assign the entire weekly value to its recorded timestamp.
No monthly model was independently fitted and these are not exact daily calendar-month
transaction totals. Summed-month APE allows weekly errors to cancel, unlike weekly WAPE.
Small month-level samples do not establish independent generalization.

## Unresolved metadata and interpretation

- M5 is a separate retail-sales experiment; primary data describes warehouse order demand.
  Exact M5 dates, forecast horizon, detailed subset and full protocol are not exported.
  One external dataset cannot establish broad generalizability, and its errors must not
  be pooled with the primary dataset.
- Exact test dates/horizons/protocols are absent from stress and seed experiments. Scenario
  exports do not include model identities; these are not inferred from matching scores.
  Perturbations are simulated experiments, not evidence of actual business disruptions.
- Calibration `Observed_Coverage` is already in percentage units, verified against
  `Covered / Observations * 100`. It is not multiplied by 100 again. Warehouse quantile
  `Coverage` is a fraction while `Coverage (%)` is a percentage; source fields are retained.
- Empirical coverage and average width describe uncertainty reliability/sharpness, not
  point-error accuracy. Exact calibration/quantile dates, model identities, horizon and
  quantile target rate are not supplied in those files. Row-level bounds are unavailable;
  no interval endpoints, bands or additional uncertainty metrics are fabricated.
- Bias summaries report 2016 warehouse samples: 52 observations A/C/S, 51 J. Their model
  identity and signed-error convention are not explicitly encoded. Signed values are
  reported without assigning a sign an under/overforecast direction. Exported underforecast
  rates retain their source labels. Cancellation of signed errors does not imply low MAE.
- The significance export reports 51 observations but no exact dates or target level.
  Inventory metadata was corrected to avoid borrowing dates from another 51-week table.
  The export supplies a HAC-labeled p-value and 95% interval, but no named test, test
  statistic, loss definition, null specification or HAC settings. The interval includes
  zero; non-significance is not proof of equal performance. No new test is run.
- Leakage PASS statuses are exported assertions; all Details cells are blank. This dashboard
  does not rerun the original checks or independently certify absence of leakage. Named
  checks do not resolve retrospective model-selection bias or holdout reuse.
- Monitoring has dated rows Jan 10–Dec 25, 2016, but no model identity, window-length or
  flag-threshold specification. Initial rolling-WAPE nulls and exported flags are preserved.
  No threshold/window is reverse-engineered, and these are not live operational alerts.
- Recursive validation spans Jan 3–Mar 20, 2016, from an end-of-2015 origin whose exact
  date is not exported. It covers A/C/S only (36 warehouse-weeks at 12 weeks). Whse_J lacked
  the required 52 consecutive pre-origin weeks. The warehouse filter does not recompute
  the three-warehouse pooled scores. Individual 4/8-week summary scores are not invented.
  These recursive results are separate from rolling and annual tasks and cannot directly
  validate archived 2017 forecasts because observed 2017 outcomes are unavailable.

Resolving these metadata gaps requires the original notebook, split definitions and model
protocols. Demand remains recorded order demand, not shipment volume or verified operational
capacity. No causal claims, model retraining or new forecasts are introduced.

## Interface and reproducibility

Seven evidence areas load independently through one selector. Supported year, model,
period, metric, scenario, warehouse and monitoring-quarter filters are available within
the relevant area. Empty selections and missing/invalid sources produce explicit messages.
Charts use the established theme and have no range sliders. Tables use readable demand
units, and CSV downloads preserve unrounded numeric data and original source fields.
Derived display columns are explicitly labeled; no source file is written.

Run `python -m unittest discover -s tests -v`: **57 tests passed**, including the previous
46 checks and 11 new validation tests. Tests cover all 24 source contracts, yearly/period
cohort separation, WAPE/MAE/RMSE recomputation against weekly predictions, pooled rows,
stability ranges, stress deltas, seed summaries, coverage scales/counts, bias arithmetic,
monitoring nulls/flags, missing/invalid data, and every evidence area/nested filter.
The existing SHA-256 check confirms all **87 original source files** match their baseline.

Streamlit startup and HTTP 200 / `ok` health check passed after a fresh server restart.
Browser review confirmed the backtesting interface and empirical calibration charts on
the correct percentage scale. The available browser preview is narrow; a full desktop
viewport visual review remains useful before public deployment.
