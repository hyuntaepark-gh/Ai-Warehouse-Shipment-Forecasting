# Operational Insights — Phase 2, Task 7

Implemented October 16, 2026. This page reads archived evidence only. It does not
generate forecasts, classify new risk, retrain models or recommend measured resources.
All six earlier pages and the seven-page navigation remain available.

## Views and provenance

| View / source CSV under capstone_final_outputs/tables | Records | Use and boundaries |
|---|---:|---|
| future_warehouse_weekly_forecasts.csv | 48 | Four warehouses × 12 aligned projected weeks; demand/P90 ratios and original weekly Normal/Watch labels. Origin Dec 25, 2016; Jan 1–Mar 19, 2017 projected dates. No actual 2017 outcomes. |
| future_operational_decision_summary.csv | 12 | Warehouse × 4/8/12-week planning windows; projected quantities, recent observed reference, change, P90 exceedances, maximum ratio, original horizon labels and illustrative planning considerations. |
| future_4_8_12_week_summary.csv | 12 | Independent export cross-check of projected total, weekly mean and peak. |
| hierarchical_warehouse_forecasts.csv | 204 | Demand column only: 51 observed weeks per warehouse, Jan 10–Dec 25, 2016. Last four weeks verify recent means. Prediction columns are not used for these observed references. |
| forecast_bias_summary.csv | 4 | Warehouse-filtered signed bias, named underforecast rates and streaks; absolute error stays conceptually separate. Exact model identity, dates and signed-error convention are unspecified. |
| model_monitoring_2016.csv | 51 | Jan 10–Dec 25, 2016 aggregate rolling WAPE and archived warning flags. Warehouse-level filters do not apply to this aggregate export. |
| scenario_summary.csv | 3 | Baseline, Demand +10%, Demand +20% exported scenarios. Hypothetical ratios/counts; threshold/population/dates/protocol unverified. |
| illustrative_cost_simulation.csv | 9 | Three models × three scenarios; 207 warehouse-weeks per row. Source planning-loss quantities, no monetary conversion or savings calculation. |
| capacity_optimization.csv | 2 | Original illustrative policy names, expected loss and average planned quantity; physical capacity and objective weights are absent. |
| forecast_value_added.csv | 6 | Two separate evaluation levels; three models each. Relative WAPE reduction against the exported Naive baseline, not financial value. Dates, horizon and protocol unverified. |

Also inspected `warehouse_characteristics.csv` and the complete source
`README_summary.md`. Training demand summaries are not represented as 2016 actuals.
The original notebook is not supplied, so missing definitions remain unresolved.
No figures or HTML arrays are used to invent additional operational observations.

## Interaction and interpretation

The archived planning view supports one/multiple warehouses and 4/8/12 weeks. Plotly
shows projected demand relative to the saved historical P90 and changes versus recent
observed mean. Tables retain source labels and planning considerations. Warehouse
identity colors are consistent with Warehouse Analytics; there are no invented
traffic-light severity colors. Ratio 1 marks equality with P90, not a Normal/Watch
boundary. Risk rules, horizon-label aggregation, percentile history and quantile
method are not documented.

The historical view offers warehouse and diagnostic controls for bias, plus an
independent aggregate monitoring chart and a flagged-row filter. Missing initial
rolling errors remain null. Monitoring model, rolling-window length, warning
threshold and persistence rule are unknown. No causal explanation or live alert
is inferred. Different source counts do not establish identical cohorts.

The scenario view offers a multi-scenario comparison, indicator selector,
planning-loss scenario selector and separate FVA evaluation-level selector. These
are descriptive supplementary exports with unverified evaluation metadata, not a
model leaderboard. Scenario counts of 202/204 must not be treated as exceedances
among the 48 future records. No loss formula is reverse engineered.

Conditional interpretations link to the displayed source metrics. The source
planning text is explicitly illustrative. Demand is order quantity, not shipment
volume, required capacity or staffing. No service, inventory, actual cost, physical
constraint or realized benefit is measured by these exports. Detailed reliability
and forecast-volume analyses remain on Model Validation and Future Forecasting.

## Numerical verification

- All 48 saved ratios match Predicted_Demand / Historical_P90; maximum absolute
  discrepancy **1.1102230246251565e-16** (tolerance 1e-10).
- All 12 planning rows reconcile total, weekly mean, peak, change from recent
  mean, strict P90 exceedance count and maximum ratio: **72 checks**. Maximum
  absolute discrepancy **4.656612873077393e-10**. Quantity tolerance 0.00001 units;
  change/count/ratio tolerance 1e-8.
- Another **36 checks** reconcile total/mean/peak against the separate future summary.
- Recent four observed timestamps are **Dec 4, 11, 18 and 25, 2016**. Their means
  match exactly: A 512,895.25; C 3,273,727.5; J 15,233,746.75; S 2,249,123.5 units.
- All **48 projected warehouse-weeks are below P90**. At 12 weeks, exported horizon
  labels are Watch for A/J and Normal for C/S. These labels do not mean P90 exceedance.
- At 12 weeks, projected mean changes from the recent observed reference are
  A +32.999881%, C −19.538772%, J −16.768094%, S +17.726307%. No cause is asserted.
- Six FVA percentages reconcile to their own evaluation-level Naive baselines.
  Scenario ratio scaling agrees with the exported +10%/+20% scenario labels;
  this check does not verify undocumented threshold or cost methodology.
- Display uses readable units/percentages; downloadable CSVs retain numeric precision.

## Validation and remaining work

The complete suite passes **84 tests**, including 14 new operational tests. Coverage
includes ratios, original labels/text, summary arithmetic, actual reference dates,
warehouse/horizon/scenario controls, FVA baselines, corrupt/missing sources,
optional-panel failure isolation, empty selections, downloads and chart configuration.
Existing tests still exercise all earlier pages and verify the unchanged hashes of
all **87** original files.

Streamlit startup and HTTP 200 / ok health checks passed. Browser review confirmed
all three views, projected totals changing with the horizon, historical warning counts
and scenario/policy content. The browser preview was narrow; desktop viewport review
remains part of final QA.

Missing definitions cannot be resolved without the original notebook or supporting
documentation. Final QA may include wider viewport review and deployment planning;
neither deployment nor a large UI redesign is part of this iteration.
