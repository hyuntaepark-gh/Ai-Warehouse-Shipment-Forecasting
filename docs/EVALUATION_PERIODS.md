# Evaluation periods and source findings

Inspected October 16, 2026: all **74 CSVs**, 11 PNG figures, the source README and
existing HTML dashboard; **87 original files** in total. All CSVs parse successfully.
Detailed schemas and exported context values appear in SOURCE_INVENTORY.md.

## Admitted comparisons

| Scope | Source tables | Dates / grain | Evidence and treatment |
|---|---|---|---|
| 2016 full-year holdout | full_year_model_comparison; quarterly_forecast_performance | 52 aggregate weeks, Jan 3–Dec 25 | README full-year section; weekly prediction and yearly tables corroborate three shared models |
| 2014 retrospective | timesfm_historical_yearly_results; timesfm_historical_weekly_predictions | Jan 5–Dec 28; 52 weeks per model | Explicit Year and Evaluation; 104 training weeks reported |
| 2015 retrospective | same as above | Jan 4–Dec 27; 52 weeks per model | Explicit labels; 156 training weeks reported |
| Pooled 2014–2015 | timesfm_historical_pooled_summary | 104 weeks per model | Recomputed WAPE agrees with weekly rows; never includes 2016 |
| 2016 warehouse rolling | dashboard_performance_summary | 52 weeks A/C/S, 51 J | Test_Weeks and original HTML trace dates; no annual aggregate ranking |
| Early-2016 recursive | recursive_12_week_* | Jan 3–Mar 20; 36 warehouse-weeks at 12 weeks | Prediction dates; README origin at end of 2015; J excluded |
| Archived future | future_warehouse_weekly_forecasts; future_operational_decision_summary | Origin Dec 25, 2016; Jan 1–Mar 19, 2017 | Explicit origin/horizon; no actual 2017 demand |

Other dated exports include the Jan 10–Dec 25, 2016 common-period subset (51 weeks)
and the Mar 27–Dec 25, 2016 matched multi-horizon experiment (40 weeks). They are
cataloged separately and not merged into Executive Overview annual rankings.

## Key findings displayed

- TimesFM 3.0: 12.35% WAPE in the exported 2016 full-year cohort; ETS: 12.87%.
- ETS: 12.79% pooled retrospective WAPE across 2014–2015, versus TimesFM 13.43%.
  ETS configuration selection used those same folds, so this is exploratory.
- Observed 2016 aggregate order demand: 984,736,814 units across 52 timestamps.
  The weekly table repeats actuals once per model; the app counts them once per date.
- Warehouse model performance varies. Whse_A rolling Random Forest WAPE is 30.71%,
  versus XGBoost 45.09%. These scores are not the recursive backtest scores.
- Early-2016 recursive XGBoost WAPE is 59.39% pooled versus Seasonal Naive 70.62%.
  Whse_A is worse under recursive XGBoost (103.20% versus 32.11%).

These numbers describe exported historical results; the application reads them from
CSVs and derives only display aggregations. No results are hardcoded in the UI.

## Metadata gaps and limitations

Twenty-three supplementary CSVs have no verifiable exact evaluation dates in the bundle.
Each is listed with its full columns and an explicit unverified-window designation in
the inventory. They include supplementary neural benchmarks, stress experiments,
calibration, automated selection and illustrative operations tables. The LSTM/GRU
comparison, for example, reports a different SARIMA reference score from the full-year
table, so it is deliberately excluded from the eight-model annual comparison.

The separate M5 validation also lacks exported exact dates and uses a different dataset.
Summary/report-outline files are documentation or mixed-scope summaries, not new cohorts.
Pooled WAPE differs from the arithmetic fold means in ets_validation_summary.csv.

The original notebook and raw demand files are not supplied. Exact splits for undated
exports should be resolved there in Phase 2. The README documents repeated exploratory
use of 2016 results and post-selection limitations. No independent model superiority,
validated physical capacity requirements or measured financial savings are claimed.
