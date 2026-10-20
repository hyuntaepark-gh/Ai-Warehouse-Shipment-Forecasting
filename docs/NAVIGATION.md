# Proposed navigation

Executive Overview (Phase 1), Historical Demand, Model Comparison, Warehouse Analytics
Model Validation, Future Forecasting and Operational Insights (Phase 2) are implemented.
The overview includes four separate analysis tabs:
2016 full-year holdout, 2014–2015 retrospective, warehouse diagnostics, and archived future outlook.

| Page | Proposed purpose and contents | Period safeguards |
|---|---|---|
| Executive Overview | Verified headline KPIs, historical demand trend, saved forecast context, source readiness and provenance | Separate historical 2016 results from future forecasts originating in December 2016; no cross-period ranking |
| Historical Demand | Implemented: actual weekly trends, period comparisons, monthly weekly-mean patterns, distributions, variability, coverage and downloads | 2014–2016 aggregate actuals; separate 51-week 2016 warehouse sample. Product/category history is unavailable. Weekly timestamp groups are not daily calendar-period totals. |
| Model Comparison | Implemented: four evaluation groups, WAPE/MAE/RMSE rankings, aligned actual/predicted charts, model/fold/warehouse/horizon filters, model types and downloads | Rank only within one reviewed target, period, sample, horizon and protocol; unverified supplementary exports are unranked; reconciliation predictions remain a separate diagnostic |
| Warehouse Analytics | Implemented: multi-warehouse actual demand KPIs/trends, variability and monthly patterns; within-warehouse model ranks; selected-warehouse deep dive and downloads | 51-week observed sample stays separate from 51/52-week rolling scores and the separately labeled reconciliation prediction diagnostic; no full-year extrapolation or global model leaderboard |
| Model Validation | Implemented: backtesting, temporal stability, external M5 evidence, robustness/seed sensitivity, uncertainty/bias, statistical/leakage/monitoring diagnostics and recursive validation | Retrospective and holdout views stay separate; unknown dates/protocols are labeled; no cross-cohort rankings or fabricated intervals; audit assertions do not imply independent validation |
| Future Forecasting | Implemented: verified archive coverage, warehouse/horizon filters, weekly/cumulative projections, selected aggregates, contributions, 4/8/12-week summaries, numeric reconciliation and downloads | Origin Dec 25, 2016; Jan 1–Mar 19, 2017 projections; no missing forecasts filled, no observed 2017 accuracy or invented intervals; historical backtest shown separately |
| Operational Insights | Implemented: archived demand/P90 indicators and source risk labels, recent actual reference, bias/monitoring, illustrative scenarios, loss/capacity policies and FVA context with filters/downloads | Dec 25, 2016 origin; no invented risk rules or capacity assumptions; observed references, projections, historical diagnostics and undated supplementary experiments stay separate; conditional considerations are not validated decisions |

## Source inspection status

All 74 CSVs have been read and documented in SOURCE_INVENTORY.md, together with the
source README and existing HTML dashboard review. The bundle contains 87 files in total.
Exact dates absent from supplementary exports remain explicitly unverified. The
overview ranks models only within reviewed compatible cohorts.
