# Model Comparison — Phase 2

Only Model Comparison was implemented in this iteration. Executive Overview and
Historical Demand retain their analyses, filters and downloads. Their demand-number
formatting now uses the same display-only K/M/B formatter and CV is displayed as a
percentage. The original numerical frames and CSV download precision are preserved.
The seven-page navigation is unchanged; four destinations remain placeholders.

## Evaluation groups and sources

| Group | Metric source CSV | Prediction source CSV | Ranking boundary |
|---|---|---|---|
| 2016 full-year aggregate holdout | full_year_model_comparison.csv | timesfm_historical_weekly_predictions.csv | Eight-model annual summary; aggregate weekly demand; Jan 3–Dec 25, 2016; 52-week year-ahead task |
| Retrospective 2014 or 2015 | timesfm_historical_yearly_results.csv | timesfm_historical_weekly_predictions.csv | One selected 52-week fold; 2016 rows excluded |
| Pooled 2014–2015 | timesfm_historical_pooled_summary.csv | timesfm_historical_weekly_predictions.csv | Two separate year-ahead origins; 104 pooled weekly errors, not one 104-week forecast |
| Warehouse rolling | dashboard_performance_summary.csv | Complete matching CSV prediction export unavailable | One warehouse at a time; same models/sample within that warehouse; 52 weeks A/C/S, 51 weeks J |
| Recursive pooled validation | recursive_12_week_backtest_summary.csv | recursive_12_week_backtest_predictions.csv | Same three eligible warehouses, one cumulative 4/8/12-week horizon at a time |
| Recursive per-warehouse validation | recursive_12_week_warehouse_results.csv | recursive_12_week_backtest_predictions.csv | One eligible warehouse; scores exported only for the 12-week horizon |
| Separate unranked reconciliation diagnostic | No per-warehouse scores displayed | hierarchical_warehouse_forecasts.csv | Original nonnegative and reconciled forecasts; Jan 10–Dec 25, 2016; distinct 51-week sample |

All CSV paths are relative to `capstone_final_outputs/tables/`. The original README
establishes annual cohort membership and research limitations. Original HTML trace
timestamps corroborate warehouse rolling periods: Jan 3–Dec 25 for A/C/S and Jan 10–Dec
25 for J. Those dates are documented metadata; displayed scores come from CSV.
Recursive observations begin Jan 3, 2016. The source README describes the origin as
the end of 2015; the exact origin date is not exported and is not inferred.

## Interaction and interpretation

- Evaluation group selector with cohort-specific fold, warehouse, recursive sample and
  horizon controls. Model filtering never changes evaluation cohort membership.
- WAPE, MAE and RMSE selection where the selected summary exports them.
- Horizontal performance bars, dynamic chart heights, readable labels, model-type
  descriptions, rank table and full-precision comparison CSV downloads.
- Rankings reject mixed period, horizon, target, methodology or sample metadata before
  model filtering. Missing/invalid metric values are rejected. Exact ties share a rank.
  Rankings are descriptive within selected models, not statistical superiority claims.
- Actual vs predicted charts use aligned saved weekly observations, with solid actual
  and dashed predicted lines. No range sliders are added. Actuals appear once per date.
- Pooled retrospective rankings remain pooled while the chart displays one explicit
  fold at a time. Pooled recursive rankings remain pooled while the line chart displays
  one explicit warehouse at a time. Chart subsets do not silently recompute rankings.
- A separate checkbox exposes the reconciliation prediction diagnostic in warehouse
  mode. Its predictions are never labeled as the full rolling comparison, and never
  used to recompute those scores. Its original/reconciled series are independent of
  the rolling model filter.
- Unverified supplementary tables are exposed in an explicitly unranked viewer, with
  metadata warnings and CSV downloads. Exact dates or compatible tasks are not inferred
  from similar numeric scores. External M5 data stays outside primary-data rankings.

K/M/B formats and CV percentages are display-only; tables/downloads retain the original
numeric data. Demand analysis and forecasting accuracy are kept separate. The page
does not attribute demand spikes or drops to causes, train models, generate forecasts,
or convert weekly timestamp groups into daily transaction totals.

## Remaining limitations

- Five of the eight annual summary models lack weekly prediction rows. Their scores
  remain visible but no trajectories or independently recomputed metrics are invented.
- Warehouse rolling summaries lack complete matching CSV prediction rows. Incomplete
  CSV subsets are not substituted for the original rolling task.
- Individual-warehouse 4/8-week recursive scores are absent. Predictions are available,
  but no scores/rankings are manufactured. Select the pooled sample or 12-week horizon
  to see exported scores. Whse_J was excluded from the recursive backtest.
- Exact rolling model fit/update details are not exported; the established rolling
  cohort is reported with that limitation, not an inferred refit schedule.
- Retrospective ETS selection used the same 2014–2015 folds. Repeated exploratory use
  of 2016 results does not establish independent post-selection generalization.
- Exact evaluation dates remain unverified for 23 supplementary exports. The separate
  M5 dataset also lacks exported exact dates. Resolving those gaps requires the original
  notebook and split metadata.
- Observed 2017 outcomes are unavailable. Recursive historical validation does not
  directly validate the archived forecasts originating in December 2016.

## Validation

All **38 tests passed**, including the 27 existing checks and 11 new comparison and
formatting tests. New tests cover all four groups, metric filtering, same-cohort ranking,
ties, mixed/unknown metadata rejection, actual/predicted alignment, recursive scopes,
unexported metrics, reconciliation isolation, missing prediction coverage, model/fold/
warehouse/horizon filters, absent range sliders, and unchanged numeric download data.
Where predictions exist, tests recompute WAPE, MAE and RMSE from the actual exports.
The existing SHA-256 test confirms all **87 original files** match their saved baseline.

The server started successfully at http://127.0.0.1:8501 and its health endpoint returned
HTTP 200 / `ok`. Browser review confirmed the new page and preserved navigation. It
caught a repeated bar-label issue; each bar now uses its own model's value, with a
regression assertion checking every label against the source score. The browser preview
available here is narrow, so a full desktop viewport review remains useful before public
deployment.

Run `python -m unittest discover -s tests -v` from the project directory. Start with
`python -m streamlit run app.py --server.address 127.0.0.1 --server.port 8501`.
