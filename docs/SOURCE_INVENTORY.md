# Source inventory

Source directory: `capstone_final_outputs/` (relative to the repository root)

Observed date spans describe file contents, not verified model evaluation windows.

## figures/full_year_wape_comparison.png

Type: .png; size: 75337 bytes.

## figures/future_12_week_warehouse_forecast.png

Type: .png; size: 135762 bytes.

## figures/m5_external_validation_wape.png

Type: .png; size: 33410 bytes.

## figures/multi_year_backtest_wape.png

Type: .png; size: 45492 bytes.

## figures/quarterly_forecast_performance.png

Type: .png; size: 80631 bytes.

## figures/timesfm_2016_monthly_demand_totals.png

Type: .png; size: 288363 bytes.

## figures/timesfm_cross_year_quarterly_wape.png

Type: .png; size: 110864 bytes.

## figures/timesfm_historical_backtesting_wape.png

Type: .png; size: 84590 bytes.

## figures/timesfm_historical_monthly_wape_heatmap.png

Type: .png; size: 241605 bytes.

## figures/timesfm_historical_pooled_quarterly_wape.png

Type: .png; size: 85007 bytes.

## figures/warehouse_scenario_alerts.png

Type: .png; size: 55447 bytes.

## README_summary.md

Type: .md; size: 15798 bytes.

## tables/artifact_manifest.csv

Type: .csv; size: 3836 bytes.

Rows: 86. Family: **Cross-experiment summary / documentation**.

Period: Mixed or not applicable; see individual metric/statement

Evidence: Table contents; summary labels may identify subsets but do not supply row-level predictions.

Caution: Do not treat summary rows as one evaluation cohort. Exported leakage PASS checks are not independent verification.

| Column | Inferred dtype | Nulls |
|---|---|---|
| File | object | 0 |
| Size_KB | float64 | 0 |

Observed date spans: `{}`

Exported context values: `{}`

## tables/automated_model_test.csv

Type: .csv; size: 96 bytes.

Rows: 1. Family: **Supplementary experiment — exact evaluation window unverified**.

Period: No exact dates in this export; not admitted to overview rankings

Evidence: CSV schema and contents inspected; source notebook / explicit split metadata not included in bundle.

Caution: May describe validation, stress tests, uncertainty, timing or illustrative scenarios. Do not infer test dates or compatibility from similar scores.

| Column | Inferred dtype | Nulls |
|---|---|---|
| Selected_Model | object | 0 |
| MAE | float64 | 0 |
| RMSE | float64 | 0 |
| WAPE (%) | float64 | 0 |

Observed date spans: `{}`

Exported context values: `{}`

## tables/automated_model_validation.csv

Type: .csv; size: 223 bytes.

Rows: 3. Family: **Supplementary experiment — exact evaluation window unverified**.

Period: No exact dates in this export; not admitted to overview rankings

Evidence: CSV schema and contents inspected; source notebook / explicit split metadata not included in bundle.

Caution: May describe validation, stress tests, uncertainty, timing or illustrative scenarios. Do not infer test dates or compatibility from similar scores.

| Column | Inferred dtype | Nulls |
|---|---|---|
| Model | object | 0 |
| MAE | float64 | 0 |
| RMSE | float64 | 0 |
| WAPE (%) | float64 | 0 |

Observed date spans: `{}`

Exported context values: `{"Model": ["XGBoost", "Random Forest", "Naive"]}`

## tables/capacity_optimization.csv

Type: .csv; size: 158 bytes.

Rows: 2. Family: **Supplementary experiment — exact evaluation window unverified**.

Period: No exact dates in this export; not admitted to overview rankings

Evidence: CSV schema and contents inspected; source notebook / explicit split metadata not included in bundle.

Caution: May describe validation, stress tests, uncertainty, timing or illustrative scenarios. Do not infer test dates or compatibility from similar scores.

| Column | Inferred dtype | Nulls |
|---|---|---|
| Policy | object | 0 |
| Total_Expected_Loss | float64 | 0 |
| Average_Planned_Capacity | float64 | 0 |

Observed date spans: `{}`

Exported context values: `{}`

## tables/category_model_comparison.csv

Type: .csv; size: 165 bytes.

Rows: 2. Family: **Supplementary experiment — exact evaluation window unverified**.

Period: No exact dates in this export; not admitted to overview rankings

Evidence: CSV schema and contents inspected; source notebook / explicit split metadata not included in bundle.

Caution: May describe validation, stress tests, uncertainty, timing or illustrative scenarios. Do not infer test dates or compatibility from similar scores.

| Column | Inferred dtype | Nulls |
|---|---|---|
| Model | object | 0 |
| MAE | float64 | 0 |
| RMSE | float64 | 0 |
| WAPE (%) | float64 | 0 |

Observed date spans: `{}`

Exported context values: `{"Model": ["Seasonal Naive", "XGBoost"]}`

## tables/cold_start_comparison.csv

Type: .csv; size: 767 bytes.

Rows: 8. Family: **Supplementary experiment — exact evaluation window unverified**.

Period: No exact dates in this export; not admitted to overview rankings

Evidence: CSV schema and contents inspected; source notebook / explicit split metadata not included in bundle.

Caution: May describe validation, stress tests, uncertainty, timing or illustrative scenarios. Do not infer test dates or compatibility from similar scores.

| Column | Inferred dtype | Nulls |
|---|---|---|
| Held_Out_Warehouse | object | 0 |
| Model | object | 0 |
| Observations | int64 | 0 |
| MAE | float64 | 0 |
| RMSE | float64 | 0 |
| WAPE (%) | float64 | 0 |

Observed date spans: `{}`

Exported context values: `{"Model": ["Calendar XGBoost", "Cross-Warehouse Seasonal Mean"], "Observations": [52]}`

## tables/common_model_comparison.csv

Type: .csv; size: 762 bytes.

Rows: 9. Family: **2016 common-period / reconciliation subset**.

Period: 2016-01-10 to 2016-12-25; 51 weeks (dated exports and research_conclusions.csv)

Evidence: hierarchical_warehouse_forecasts.csv, model_monitoring_2016.csv; research_conclusions.csv 51-week common-period statement.

Caution: Never combine with 52-week full-year errors; ensemble is separately evaluated.

| Column | Inferred dtype | Nulls |
|---|---|---|
| Model | object | 0 |
| MAE | float64 | 0 |
| RMSE | float64 | 0 |
| WAPE (%) | float64 | 0 |

Observed date spans: `{}`

Exported context values: `{"Model": ["Warehouse XGBoost - Aggregated", "Warehouse RF - Aggregated", "Overall SARIMA Refined - Rolling", "Overall Random Forest", "Overall XGBoost", "Overall ARIMA - Rolling", "Overall SARIMA Initial - Rolling", "Overall Seasonal Naive", "Overall Naive"]}`

## tables/dashboard_performance_summary.csv

Type: .csv; size: 1008 bytes.

Rows: 12. Family: **2016 warehouse rolling forecasts**.

Period: 2016; 52 test weeks for A/C/S; 51 for J in dashboard_performance_summary

Evidence: Original HTML dashboard trace timestamps and Test_Weeks; README_summary.md distinguishes warehouse rolling evaluation.

Caution: Within-warehouse comparisons only; different grain and information set from aggregate year-ahead forecasts.

| Column | Inferred dtype | Nulls |
|---|---|---|
| Warehouse | object | 0 |
| Model | object | 0 |
| Test_Weeks | int64 | 0 |
| Forecast_High_Demand_Alerts | int64 | 0 |
| MAE | float64 | 0 |
| RMSE | float64 | 0 |
| WAPE (%) | float64 | 0 |

Observed date spans: `{}`

Exported context values: `{"Warehouse": ["Whse_A", "Whse_C", "Whse_J", "Whse_S"], "Model": ["Naive", "Random Forest", "XGBoost"], "Test_Weeks": [52, 51]}`

## tables/data_disruption_robustness.csv

Type: .csv; size: 397 bytes.

Rows: 4. Family: **Supplementary experiment — exact evaluation window unverified**.

Period: No exact dates in this export; not admitted to overview rankings

Evidence: CSV schema and contents inspected; source notebook / explicit split metadata not included in bundle.

Caution: May describe validation, stress tests, uncertainty, timing or illustrative scenarios. Do not infer test dates or compatibility from similar scores.

| Column | Inferred dtype | Nulls |
|---|---|---|
| Scenario | object | 0 |
| MAE | float64 | 0 |
| RMSE | float64 | 0 |
| WAPE (%) | float64 | 0 |
| WAPE_Change_pp | float64 | 0 |

Observed date spans: `{}`

Exported context values: `{}`

## tables/data_leakage_audit.csv

Type: .csv; size: 314 bytes.

Rows: 8. Family: **Cross-experiment summary / documentation**.

Period: Mixed or not applicable; see individual metric/statement

Evidence: Table contents; summary labels may identify subsets but do not supply row-level predictions.

Caution: Do not treat summary rows as one evaluation cohort. Exported leakage PASS checks are not independent verification.

| Column | Inferred dtype | Nulls |
|---|---|---|
| Check | object | 0 |
| Status | object | 0 |
| Details | float64 | 8 |

Observed date spans: `{}`

Exported context values: `{}`

## tables/data_quality_impact.csv

Type: .csv; size: 528 bytes.

Rows: 5. Family: **Supplementary experiment — exact evaluation window unverified**.

Period: No exact dates in this export; not admitted to overview rankings

Evidence: CSV schema and contents inspected; source notebook / explicit split metadata not included in bundle.

Caution: May describe validation, stress tests, uncertainty, timing or illustrative scenarios. Do not infer test dates or compatibility from similar scores.

| Column | Inferred dtype | Nulls |
|---|---|---|
| Scenario | object | 0 |
| MAE | float64 | 0 |
| RMSE | float64 | 0 |
| WAPE (%) | float64 | 0 |
| WAPE_Change_pp | float64 | 0 |

Observed date spans: `{}`

Exported context values: `{}`

## tables/demand_level_performance.csv

Type: .csv; size: 718 bytes.

Rows: 9. Family: **Supplementary experiment — exact evaluation window unverified**.

Period: No exact dates in this export; not admitted to overview rankings

Evidence: CSV schema and contents inspected; source notebook / explicit split metadata not included in bundle.

Caution: May describe validation, stress tests, uncertainty, timing or illustrative scenarios. Do not infer test dates or compatibility from similar scores.

| Column | Inferred dtype | Nulls |
|---|---|---|
| Demand_Level | object | 0 |
| Model | object | 0 |
| Observations | int64 | 0 |
| MAE | float64 | 0 |
| RMSE | float64 | 0 |
| WAPE (%) | float64 | 0 |

Observed date spans: `{}`

Exported context values: `{"Model": ["Naive", "Random Forest", "XGBoost"], "Observations": [74, 82, 51]}`

## tables/ensemble_aggregate_comparison.csv

Type: .csv; size: 236 bytes.

Rows: 3. Family: **2016 common-period / reconciliation subset**.

Period: 2016-01-10 to 2016-12-25; 51 weeks (dated exports and research_conclusions.csv)

Evidence: hierarchical_warehouse_forecasts.csv, model_monitoring_2016.csv; research_conclusions.csv 51-week common-period statement.

Caution: Never combine with 52-week full-year errors; ensemble is separately evaluated.

| Column | Inferred dtype | Nulls |
|---|---|---|
| Model | object | 0 |
| MAE | float64 | 0 |
| RMSE | float64 | 0 |
| WAPE (%) | float64 | 0 |

Observed date spans: `{}`

Exported context values: `{"Model": ["Random Forest", "XGBoost", "Weighted Ensemble"]}`

## tables/ensemble_comparison.csv

Type: .csv; size: 230 bytes.

Rows: 3. Family: **Supplementary experiment — exact evaluation window unverified**.

Period: No exact dates in this export; not admitted to overview rankings

Evidence: CSV schema and contents inspected; source notebook / explicit split metadata not included in bundle.

Caution: May describe validation, stress tests, uncertainty, timing or illustrative scenarios. Do not infer test dates or compatibility from similar scores.

| Column | Inferred dtype | Nulls |
|---|---|---|
| Model | object | 0 |
| MAE | float64 | 0 |
| RMSE | float64 | 0 |
| WAPE (%) | float64 | 0 |

Observed date spans: `{}`

Exported context values: `{"Model": ["Random Forest", "XGBoost", "Weighted Ensemble"]}`

## tables/ensemble_validation_weights.csv

Type: .csv; size: 452 bytes.

Rows: 11. Family: **Supplementary experiment — exact evaluation window unverified**.

Period: No exact dates in this export; not admitted to overview rankings

Evidence: CSV schema and contents inspected; source notebook / explicit split metadata not included in bundle.

Caution: May describe validation, stress tests, uncertainty, timing or illustrative scenarios. Do not infer test dates or compatibility from similar scores.

| Column | Inferred dtype | Nulls |
|---|---|---|
| XGB_Weight | float64 | 0 |
| RF_Weight | float64 | 0 |
| Validation_WAPE_Pct | float64 | 0 |

Observed date spans: `{}`

Exported context values: `{}`

## tables/ets_sarima_comparison.csv

Type: .csv; size: 166 bytes.

Rows: 2. Family: **2016 aggregate full-year holdout**.

Period: 2016-01-03 to 2016-12-25; 52 weekly timestamps

Evidence: README_summary.md: Additional Full-Year Forecasting Results; weekly predictions corroborate dates for ETS, TimesFM and Seasonal Naive.

Caution: Aggregate year-ahead forecasts; later comparisons are exploratory, not independent post-selection validation.

| Column | Inferred dtype | Nulls |
|---|---|---|
| Model | object | 0 |
| MAE | float64 | 0 |
| RMSE | float64 | 0 |
| WAPE (%) | float64 | 0 |

Observed date spans: `{}`

Exported context values: `{"Model": ["Refined SARIMA", "ETS(A,N,A)"]}`

## tables/ets_validation_results.csv

Type: .csv; size: 482 bytes.

Rows: 6. Family: **2014–2015 retrospective year-ahead diagnostics**.

Period: 2014-01-05 to 2014-12-28 and 2015-01-04 to 2015-12-27; 104 pooled weeks

Evidence: README_summary.md: TimesFM Historical Year-Ahead Backtesting; ETS validation table Year values.

Caution: ETS configuration selected on the same folds. ets_validation_summary reports fold means, not pooled error metrics.

| Column | Inferred dtype | Nulls |
|---|---|---|
| Model | object | 0 |
| Year | int64 | 0 |
| MAE | float64 | 0 |
| RMSE | float64 | 0 |
| WAPE (%) | float64 | 0 |

Observed date spans: `{}`

Exported context values: `{"Model": ["ETS(A,N,A)", "ETS(A,A,A)", "ETS(A,Ad,A)"], "Year": [2014, 2015]}`

## tables/ets_validation_summary.csv

Type: .csv; size: 257 bytes.

Rows: 3. Family: **2014–2015 retrospective year-ahead diagnostics**.

Period: 2014-01-05 to 2014-12-28 and 2015-01-04 to 2015-12-27; 104 pooled weeks

Evidence: README_summary.md: TimesFM Historical Year-Ahead Backtesting; ETS validation table Year values.

Caution: ETS configuration selected on the same folds. ets_validation_summary reports fold means, not pooled error metrics.

| Column | Inferred dtype | Nulls |
|---|---|---|
| Model | object | 0 |
| Folds | int64 | 0 |
| Mean_MAE | float64 | 0 |
| Mean_RMSE | float64 | 0 |
| Mean_WAPE | float64 | 0 |

Observed date spans: `{}`

Exported context values: `{"Model": ["ETS(A,N,A)", "ETS(A,A,A)", "ETS(A,Ad,A)"]}`

## tables/final_metrics_summary.csv

Type: .csv; size: 753 bytes.

Rows: 16. Family: **Cross-experiment summary / documentation**.

Period: Mixed or not applicable; see individual metric/statement

Evidence: Table contents; summary labels may identify subsets but do not supply row-level predictions.

Caution: Do not treat summary rows as one evaluation cohort. Exported leakage PASS checks are not independent verification.

| Column | Inferred dtype | Nulls |
|---|---|---|
| Metric | object | 0 |
| Value | float64 | 0 |

Observed date spans: `{}`

Exported context values: `{}`

## tables/final_presentation_outline.csv

Type: .csv; size: 435 bytes.

Rows: 14. Family: **Cross-experiment summary / documentation**.

Period: Mixed or not applicable; see individual metric/statement

Evidence: Table contents; summary labels may identify subsets but do not supply row-level predictions.

Caution: Do not treat summary rows as one evaluation cohort. Exported leakage PASS checks are not independent verification.

| Column | Inferred dtype | Nulls |
|---|---|---|
| Slide | int64 | 0 |
| Topic | object | 0 |

Observed date spans: `{}`

Exported context values: `{}`

## tables/final_report_outline.csv

Type: .csv; size: 546 bytes.

Rows: 19. Family: **Cross-experiment summary / documentation**.

Period: Mixed or not applicable; see individual metric/statement

Evidence: Table contents; summary labels may identify subsets but do not supply row-level predictions.

Caution: Do not treat summary rows as one evaluation cohort. Exported leakage PASS checks are not independent verification.

| Column | Inferred dtype | Nulls |
|---|---|---|
| Section | object | 0 |

Observed date spans: `{}`

Exported context values: `{}`

## tables/forecast_bias_quarterly.csv

Type: .csv; size: 893 bytes.

Rows: 16. Family: **2016 warehouse rolling forecasts**.

Period: 2016; 52 test weeks for A/C/S; 51 for J in dashboard_performance_summary

Evidence: Original HTML dashboard trace timestamps and Test_Weeks; README_summary.md distinguishes warehouse rolling evaluation.

Caution: Within-warehouse comparisons only; different grain and information set from aggregate year-ahead forecasts.

| Column | Inferred dtype | Nulls |
|---|---|---|
| Warehouse | object | 0 |
| Quarter | object | 0 |
| Mean_Signed_Error | float64 | 0 |
| Underforecast_Rate_Pct | float64 | 0 |

Observed date spans: `{}`

Exported context values: `{"Warehouse": ["Whse_A", "Whse_C", "Whse_J", "Whse_S"]}`

## tables/forecast_bias_summary.csv

Type: .csv; size: 687 bytes.

Rows: 4. Family: **2016 warehouse rolling forecasts**.

Period: 2016; 52 test weeks for A/C/S; 51 for J in dashboard_performance_summary

Evidence: Original HTML dashboard trace timestamps and Test_Weeks; README_summary.md distinguishes warehouse rolling evaluation.

Caution: Within-warehouse comparisons only; different grain and information set from aggregate year-ahead forecasts.

| Column | Inferred dtype | Nulls |
|---|---|---|
| Warehouse | object | 0 |
| Observations | int64 | 0 |
| Total_Demand | float64 | 0 |
| Total_Signed_Error | float64 | 0 |
| Mean_Signed_Error | float64 | 0 |
| MAE | float64 | 0 |
| Underforecast_Rate | float64 | 0 |
| Bias_Pct | float64 | 0 |
| Underforecast_Rate_Pct | float64 | 0 |
| Longest_Underforecast_Streak | int64 | 0 |

Observed date spans: `{}`

Exported context values: `{"Warehouse": ["Whse_A", "Whse_C", "Whse_J", "Whse_S"], "Observations": [52, 51]}`

## tables/forecast_calibration.csv

Type: .csv; size: 336 bytes.

Rows: 4. Family: **Supplementary experiment — exact evaluation window unverified**.

Period: No exact dates in this export; not admitted to overview rankings

Evidence: CSV schema and contents inspected; source notebook / explicit split metadata not included in bundle.

Caution: May describe validation, stress tests, uncertainty, timing or illustrative scenarios. Do not infer test dates or compatibility from similar scores.

| Column | Inferred dtype | Nulls |
|---|---|---|
| Target_Coverage | float64 | 0 |
| Observations | int64 | 0 |
| Covered | int64 | 0 |
| Total_Width | float64 | 0 |
| Observed_Coverage | float64 | 0 |
| Average_Width | float64 | 0 |

Observed date spans: `{}`

Exported context values: `{"Observations": [207]}`

## tables/forecast_error_summary.csv

Type: .csv; size: 339 bytes.

Rows: 4. Family: **2016 warehouse rolling forecasts**.

Period: 2016; 52 test weeks for A/C/S; 51 for J in dashboard_performance_summary

Evidence: Original HTML dashboard trace timestamps and Test_Weeks; README_summary.md distinguishes warehouse rolling evaluation.

Caution: Within-warehouse comparisons only; different grain and information set from aggregate year-ahead forecasts.

| Column | Inferred dtype | Nulls |
|---|---|---|
| Warehouse | object | 0 |
| Observations | int64 | 0 |
| Mean_Signed_Error | float64 | 0 |
| MAE | float64 | 0 |
| Underforecast_Rate_Pct | float64 | 0 |

Observed date spans: `{}`

Exported context values: `{"Warehouse": ["Whse_A", "Whse_C", "Whse_J", "Whse_S"], "Observations": [52, 51]}`

## tables/forecast_significance_test.csv

Type: .csv; size: 169 bytes.

Rows: 1. Family: **Statistical comparison — exact evaluation dates unverified**.

Period: 51 observations; exact dates and target level not encoded in this export

Evidence: Comparison, Weeks, Mean_Loss_Difference, HAC_p_value and 95% interval columns only.

Caution: Do not borrow dates from another 51-week table. Named test, statistic, loss definition and HAC settings are not exported; non-significance is not proof of equality.

| Column | Inferred dtype | Nulls |
|---|---|---|
| Comparison | object | 0 |
| Weeks | int64 | 0 |
| Mean_Loss_Difference | float64 | 0 |
| HAC_p_value | float64 | 0 |
| CI_95_Lower | float64 | 0 |
| CI_95_Upper | float64 | 0 |

Observed date spans: `{}`

Exported context values: `{"Weeks": [51]}`

## tables/forecast_value_added.csv

Type: .csv; size: 543 bytes.

Rows: 6. Family: **Supplementary experiment — exact evaluation window unverified**.

Period: No exact dates in this export; not admitted to overview rankings

Evidence: CSV schema and contents inspected; source notebook / explicit split metadata not included in bundle.

Caution: May describe validation, stress tests, uncertainty, timing or illustrative scenarios. Do not infer test dates or compatibility from similar scores.

| Column | Inferred dtype | Nulls |
|---|---|---|
| Evaluation_Level | object | 0 |
| Model | object | 0 |
| WAPE (%) | float64 | 0 |
| Baseline_WAPE (%) | float64 | 0 |
| FVA_Improvement (%) | float64 | 0 |

Observed date spans: `{}`

Exported context values: `{"Model": ["Naive", "Random Forest", "XGBoost"]}`

## tables/full_year_model_comparison.csv

Type: .csv; size: 556 bytes.

Rows: 8. Family: **2016 aggregate full-year holdout**.

Period: 2016-01-03 to 2016-12-25; 52 weekly timestamps

Evidence: README_summary.md: Additional Full-Year Forecasting Results; weekly predictions corroborate dates for ETS, TimesFM and Seasonal Naive.

Caution: Aggregate year-ahead forecasts; later comparisons are exploratory, not independent post-selection validation.

| Column | Inferred dtype | Nulls |
|---|---|---|
| Model | object | 0 |
| MAE | float64 | 0 |
| RMSE | float64 | 0 |
| WAPE (%) | float64 | 0 |

Observed date spans: `{}`

Exported context values: `{"Model": ["TimesFM 3.0", "ETS", "SARIMAX", "Refined SARIMA", "Seasonal Naive", "Prophet", "N-BEATS", "N-HiTS"]}`

## tables/future_4_8_12_week_summary.csv

Type: .csv; size: 658 bytes.

Rows: 12. Family: **Archived future forecasts**.

Period: Origin 2016-12-25; forecasts 2017-01-01 to 2017-03-19

Evidence: Forecast_Origin and Week in future_warehouse_weekly_forecasts.csv; 4/8/12-week summaries.

Caution: No observed 2017 outcomes. Risk categories and planning considerations are illustrative; P90 is not physical capacity.

| Column | Inferred dtype | Nulls |
|---|---|---|
| Warehouse | object | 0 |
| Projected_Total_Demand | float64 | 0 |
| Average_Weekly_Demand | float64 | 0 |
| Peak_Weekly_Demand | float64 | 0 |
| Horizon_Weeks | int64 | 0 |

Observed date spans: `{}`

Exported context values: `{"Warehouse": ["Whse_A", "Whse_C", "Whse_J", "Whse_S"], "Horizon_Weeks": [4, 8, 12]}`

## tables/future_operational_decision_summary.csv

Type: .csv; size: 2262 bytes.

Rows: 12. Family: **Archived future forecasts**.

Period: Origin 2016-12-25; forecasts 2017-01-01 to 2017-03-19

Evidence: Forecast_Origin and Week in future_warehouse_weekly_forecasts.csv; 4/8/12-week summaries.

Caution: No observed 2017 outcomes. Risk categories and planning considerations are illustrative; P90 is not physical capacity.

| Column | Inferred dtype | Nulls |
|---|---|---|
| Warehouse | object | 0 |
| Horizon_Weeks | int64 | 0 |
| Projected_Total_Demand | float64 | 0 |
| Average_Weekly_Demand | float64 | 0 |
| Peak_Weekly_Demand | float64 | 0 |
| Recent_4Week_Mean_Observed | float64 | 0 |
| Change_vs_Recent_4Week_Pct | float64 | 0 |
| Weeks_Above_Historical_P90 | int64 | 0 |
| Max_Demand_to_P90_Ratio | float64 | 0 |
| Illustrative_Risk_Level | object | 0 |
| Planning_Consideration | object | 0 |

Observed date spans: `{}`

Exported context values: `{"Warehouse": ["Whse_A", "Whse_C", "Whse_J", "Whse_S"], "Horizon_Weeks": [4, 8, 12]}`

## tables/future_warehouse_weekly_forecasts.csv

Type: .csv; size: 4216 bytes.

Rows: 48. Family: **Archived future forecasts**.

Period: Origin 2016-12-25; forecasts 2017-01-01 to 2017-03-19

Evidence: Forecast_Origin and Week in future_warehouse_weekly_forecasts.csv; 4/8/12-week summaries.

Caution: No observed 2017 outcomes. Risk categories and planning considerations are illustrative; P90 is not physical capacity.

| Column | Inferred dtype | Nulls |
|---|---|---|
| Warehouse | object | 0 |
| Forecast_Origin | object | 0 |
| Week | object | 0 |
| Horizon_Week | int64 | 0 |
| Predicted_Demand | float64 | 0 |
| Historical_P90 | float64 | 0 |
| Demand_to_P90_Ratio | float64 | 0 |
| Illustrative_Risk_Level | object | 0 |

Observed date spans: `{"Forecast_Origin": {"start": "2016-12-25", "end": "2016-12-25"}, "Week": {"start": "2017-01-01", "end": "2017-03-19"}}`

Exported context values: `{"Warehouse": ["Whse_A", "Whse_C", "Whse_J", "Whse_S"], "Forecast_Origin": ["2016-12-25"]}`

## tables/global_local_comparison.csv

Type: .csv; size: 651 bytes.

Rows: 8. Family: **2016 warehouse rolling forecasts**.

Period: 2016; 52 test weeks for A/C/S; 51 for J in dashboard_performance_summary

Evidence: Original HTML dashboard trace timestamps and Test_Weeks; README_summary.md distinguishes warehouse rolling evaluation.

Caution: Within-warehouse comparisons only; different grain and information set from aggregate year-ahead forecasts.

| Column | Inferred dtype | Nulls |
|---|---|---|
| Warehouse | object | 0 |
| Model | object | 0 |
| MAE | float64 | 0 |
| RMSE | float64 | 0 |
| WAPE (%) | float64 | 0 |

Observed date spans: `{}`

Exported context values: `{"Warehouse": ["Whse_A", "Whse_C", "Whse_J", "Whse_S"], "Model": ["Global XGBoost", "Local XGBoost"]}`

## tables/hierarchical_reconciliation.csv

Type: .csv; size: 263 bytes.

Rows: 3. Family: **2016 common-period / reconciliation subset**.

Period: 2016-01-10 to 2016-12-25; 51 weeks (dated exports and research_conclusions.csv)

Evidence: hierarchical_warehouse_forecasts.csv, model_monitoring_2016.csv; research_conclusions.csv 51-week common-period statement.

Caution: Never combine with 52-week full-year errors; ensemble is separately evaluated.

| Column | Inferred dtype | Nulls |
|---|---|---|
| Forecast | object | 0 |
| MAE | float64 | 0 |
| RMSE | float64 | 0 |
| WAPE (%) | float64 | 0 |

Observed date spans: `{}`

Exported context values: `{}`

## tables/hierarchical_warehouse_comparison.csv

Type: .csv; size: 180 bytes.

Rows: 2. Family: **2016 common-period / reconciliation subset**.

Period: 2016-01-10 to 2016-12-25; 51 weeks (dated exports and research_conclusions.csv)

Evidence: hierarchical_warehouse_forecasts.csv, model_monitoring_2016.csv; research_conclusions.csv 51-week common-period statement.

Caution: Never combine with 52-week full-year errors; ensemble is separately evaluated.

| Column | Inferred dtype | Nulls |
|---|---|---|
| Forecast | object | 0 |
| MAE | float64 | 0 |
| RMSE | float64 | 0 |
| WAPE (%) | float64 | 0 |

Observed date spans: `{}`

Exported context values: `{}`

## tables/hierarchical_warehouse_forecasts.csv

Type: .csv; size: 18392 bytes.

Rows: 204. Family: **2016 common-period / reconciliation subset**.

Period: 2016-01-10 to 2016-12-25; 51 weeks (dated exports and research_conclusions.csv)

Evidence: hierarchical_warehouse_forecasts.csv, model_monitoring_2016.csv; research_conclusions.csv 51-week common-period statement.

Caution: Never combine with 52-week full-year errors; ensemble is separately evaluated.

| Column | Inferred dtype | Nulls |
|---|---|---|
| Week | object | 0 |
| Warehouse | object | 0 |
| Demand | float64 | 0 |
| XGBoost | float64 | 0 |
| Original_Nonnegative | float64 | 0 |
| Scale | float64 | 0 |
| Reconciled_Forecast | float64 | 0 |

Observed date spans: `{"Week": {"start": "2016-01-10", "end": "2016-12-25"}}`

Exported context values: `{"Warehouse": ["Whse_A", "Whse_C", "Whse_J", "Whse_S"]}`

## tables/illustrative_cost_simulation.csv

Type: .csv; size: 969 bytes.

Rows: 9. Family: **Supplementary experiment — exact evaluation window unverified**.

Period: No exact dates in this export; not admitted to overview rankings

Evidence: CSV schema and contents inspected; source notebook / explicit split metadata not included in bundle.

Caution: May describe validation, stress tests, uncertainty, timing or illustrative scenarios. Do not infer test dates or compatibility from similar scores.

| Column | Inferred dtype | Nulls |
|---|---|---|
| Scenario | object | 0 |
| Model | object | 0 |
| Warehouse_Weeks | int64 | 0 |
| Underforecast_Units | float64 | 0 |
| Overforecast_Units | float64 | 0 |
| Total_Planning_Loss_Units | float64 | 0 |
| Loss_per_1000_Demand_Units | float64 | 0 |

Observed date spans: `{}`

Exported context values: `{"Model": ["Naive", "Random Forest", "XGBoost"]}`

## tables/lightgbm_comparison.csv

Type: .csv; size: 263 bytes.

Rows: 2. Family: **Supplementary experiment — exact evaluation window unverified**.

Period: No exact dates in this export; not admitted to overview rankings

Evidence: CSV schema and contents inspected; source notebook / explicit split metadata not included in bundle.

Caution: May describe validation, stress tests, uncertainty, timing or illustrative scenarios. Do not infer test dates or compatibility from similar scores.

| Column | Inferred dtype | Nulls |
|---|---|---|
| Model | object | 0 |
| MAE | float64 | 0 |
| RMSE | float64 | 0 |
| WAPE (%) | float64 | 0 |
| Training_Time_ms | float64 | 0 |
| Prediction_Time_ms | float64 | 0 |

Observed date spans: `{}`

Exported context values: `{"Model": ["XGBoost", "LightGBM"]}`

## tables/lstm_gru_comparison.csv

Type: .csv; size: 218 bytes.

Rows: 3. Family: **Supplementary experiment — exact evaluation window unverified**.

Period: No exact dates in this export; not admitted to overview rankings

Evidence: CSV schema and contents inspected; source notebook / explicit split metadata not included in bundle.

Caution: May describe validation, stress tests, uncertainty, timing or illustrative scenarios. Do not infer test dates or compatibility from similar scores.

| Column | Inferred dtype | Nulls |
|---|---|---|
| Model | object | 0 |
| MAE | float64 | 0 |
| RMSE | float64 | 0 |
| WAPE (%) | float64 | 0 |

Observed date spans: `{}`

Exported context values: `{"Model": ["Refined SARIMA", "LSTM", "GRU"]}`

## tables/lstm_gru_training_summary.csv

Type: .csv; size: 99 bytes.

Rows: 2. Family: **Supplementary experiment — exact evaluation window unverified**.

Period: No exact dates in this export; not admitted to overview rankings

Evidence: CSV schema and contents inspected; source notebook / explicit split metadata not included in bundle.

Caution: May describe validation, stress tests, uncertainty, timing or illustrative scenarios. Do not infer test dates or compatibility from similar scores.

| Column | Inferred dtype | Nulls |
|---|---|---|
| Model | object | 0 |
| Selected_Epochs | int64 | 0 |
| Best_Validation_Loss | float64 | 0 |

Observed date spans: `{}`

Exported context values: `{"Model": ["LSTM", "GRU"]}`

## tables/m5_external_validation.csv

Type: .csv; size: 164 bytes.

Rows: 2. Family: **External M5 validation**.

Period: Exact test dates not exported

Evidence: README_summary.md: External Validation; separate M5 retail dataset.

Caution: Different dataset and demand scale. Excluded from primary-data model rankings.

| Column | Inferred dtype | Nulls |
|---|---|---|
| Model | object | 0 |
| MAE | float64 | 0 |
| RMSE | float64 | 0 |
| WAPE (%) | float64 | 0 |

Observed date spans: `{}`

Exported context values: `{"Model": ["Seasonal Naive", "XGBoost"]}`

## tables/model_complexity_comparison.csv

Type: .csv; size: 436 bytes.

Rows: 3. Family: **Supplementary experiment — exact evaluation window unverified**.

Period: No exact dates in this export; not admitted to overview rankings

Evidence: CSV schema and contents inspected; source notebook / explicit split metadata not included in bundle.

Caution: May describe validation, stress tests, uncertainty, timing or illustrative scenarios. Do not infer test dates or compatibility from similar scores.

| Column | Inferred dtype | Nulls |
|---|---|---|
| Model | object | 0 |
| MAE | float64 | 0 |
| RMSE | float64 | 0 |
| WAPE (%) | float64 | 0 |
| Training_Time_s | float64 | 0 |
| Prediction_Time_ms | float64 | 0 |
| Serialized_Size_KB | float64 | 0 |

Observed date spans: `{}`

Exported context values: `{"Model": ["Random Forest", "XGBoost", "LightGBM"]}`

## tables/model_monitoring_2016.csv

Type: .csv; size: 3885 bytes.

Rows: 51. Family: **2016 common-period / reconciliation subset**.

Period: 2016-01-10 to 2016-12-25; 51 weeks (dated exports and research_conclusions.csv)

Evidence: hierarchical_warehouse_forecasts.csv, model_monitoring_2016.csv; research_conclusions.csv 51-week common-period statement.

Caution: Never combine with 52-week full-year errors; ensemble is separately evaluated.

| Column | Inferred dtype | Nulls |
|---|---|---|
| Week | object | 0 |
| Demand | float64 | 0 |
| Forecast | float64 | 0 |
| Absolute_Error | float64 | 0 |
| Rolling_WAPE_Pct | float64 | 7 |
| Warning | bool | 0 |
| Persistent_Warning | bool | 0 |

Observed date spans: `{"Week": {"start": "2016-01-10", "end": "2016-12-25"}}`

Exported context values: `{}`

## tables/multi_horizon_comparison.csv

Type: .csv; size: 665 bytes.

Rows: 8. Family: **2016 matched multi-horizon samples**.

Period: 2016-03-27 to 2016-12-25; 40 test weeks per horizon

Evidence: Week and Horizon_Weeks in prediction export; Test_Weeks in comparison.

Caution: Compare models within one horizon only; not equivalent to full-year or recursive evaluation.

| Column | Inferred dtype | Nulls |
|---|---|---|
| Horizon_Weeks | int64 | 0 |
| Model | object | 0 |
| Test_Observations | int64 | 0 |
| Test_Weeks | int64 | 0 |
| MAE | float64 | 0 |
| RMSE | float64 | 0 |
| WAPE (%) | float64 | 0 |

Observed date spans: `{}`

Exported context values: `{"Horizon_Weeks": [1, 4, 8, 12], "Model": ["XGBoost", "Seasonal Naive"], "Test_Weeks": [40]}`

## tables/multi_horizon_predictions.csv

Type: .csv; size: 34522 bytes.

Rows: 640. Family: **2016 matched multi-horizon samples**.

Period: 2016-03-27 to 2016-12-25; 40 test weeks per horizon

Evidence: Week and Horizon_Weeks in prediction export; Test_Weeks in comparison.

Caution: Compare models within one horizon only; not equivalent to full-year or recursive evaluation.

| Column | Inferred dtype | Nulls |
|---|---|---|
| Week | object | 0 |
| Warehouse | object | 0 |
| Demand | float64 | 0 |
| Horizon_Weeks | int64 | 0 |
| XGBoost | float64 | 0 |
| Seasonal_Naive | float64 | 0 |

Observed date spans: `{"Week": {"start": "2016-03-27", "end": "2016-12-25"}}`

Exported context values: `{"Warehouse": ["Whse_A", "Whse_C", "Whse_J", "Whse_S"], "Horizon_Weeks": [1, 4, 8, 12]}`

## tables/nbeats_nhits_comparison.csv

Type: .csv; size: 224 bytes.

Rows: 3. Family: **2016 aggregate full-year holdout**.

Period: 2016-01-03 to 2016-12-25; 52 weekly timestamps

Evidence: README_summary.md: Additional Full-Year Forecasting Results; weekly predictions corroborate dates for ETS, TimesFM and Seasonal Naive.

Caution: Aggregate year-ahead forecasts; later comparisons are exploratory, not independent post-selection validation.

| Column | Inferred dtype | Nulls |
|---|---|---|
| Model | object | 0 |
| MAE | float64 | 0 |
| RMSE | float64 | 0 |
| WAPE (%) | float64 | 0 |

Observed date spans: `{}`

Exported context values: `{"Model": ["N-BEATS", "N-HiTS", "Refined SARIMA"]}`

## tables/prophet_comparison.csv

Type: .csv; size: 161 bytes.

Rows: 2. Family: **2016 aggregate full-year holdout**.

Period: 2016-01-03 to 2016-12-25; 52 weekly timestamps

Evidence: README_summary.md: Additional Full-Year Forecasting Results; weekly predictions corroborate dates for ETS, TimesFM and Seasonal Naive.

Caution: Aggregate year-ahead forecasts; later comparisons are exploratory, not independent post-selection validation.

| Column | Inferred dtype | Nulls |
|---|---|---|
| Model | object | 0 |
| MAE | float64 | 0 |
| RMSE | float64 | 0 |
| WAPE (%) | float64 | 0 |

Observed date spans: `{}`

Exported context values: `{"Model": ["Refined SARIMA", "Prophet"]}`

## tables/quantile_comparison.csv

Type: .csv; size: 169 bytes.

Rows: 2. Family: **Supplementary experiment — exact evaluation window unverified**.

Period: No exact dates in this export; not admitted to overview rankings

Evidence: CSV schema and contents inspected; source notebook / explicit split metadata not included in bundle.

Caution: May describe validation, stress tests, uncertainty, timing or illustrative scenarios. Do not infer test dates or compatibility from similar scores.

| Column | Inferred dtype | Nulls |
|---|---|---|
| Method | object | 0 |
| Coverage (%) | float64 | 0 |
| Average_Width | float64 | 0 |

Observed date spans: `{}`

Exported context values: `{}`

## tables/quantile_warehouse_results.csv

Type: .csv; size: 301 bytes.

Rows: 4. Family: **Supplementary experiment — exact evaluation window unverified**.

Period: No exact dates in this export; not admitted to overview rankings

Evidence: CSV schema and contents inspected; source notebook / explicit split metadata not included in bundle.

Caution: May describe validation, stress tests, uncertainty, timing or illustrative scenarios. Do not infer test dates or compatibility from similar scores.

| Column | Inferred dtype | Nulls |
|---|---|---|
| Warehouse | object | 0 |
| Coverage | float64 | 0 |
| Average_Width | float64 | 0 |
| Coverage (%) | float64 | 0 |

Observed date spans: `{}`

Exported context values: `{"Warehouse": ["Whse_A", "Whse_C", "Whse_J", "Whse_S"]}`

## tables/quarterly_forecast_performance.csv

Type: .csv; size: 918 bytes.

Rows: 12. Family: **2016 aggregate full-year holdout**.

Period: 2016-01-03 to 2016-12-25; 52 weekly timestamps

Evidence: README_summary.md: Additional Full-Year Forecasting Results; weekly predictions corroborate dates for ETS, TimesFM and Seasonal Naive.

Caution: Aggregate year-ahead forecasts; later comparisons are exploratory, not independent post-selection validation.

| Column | Inferred dtype | Nulls |
|---|---|---|
| Quarter | object | 0 |
| Model | object | 0 |
| Weeks | int64 | 0 |
| MAE | float64 | 0 |
| RMSE | float64 | 0 |
| WAPE (%) | float64 | 0 |

Observed date spans: `{}`

Exported context values: `{"Model": ["Refined SARIMA", "ETS", "TimesFM 3.0"], "Weeks": [13]}`

## tables/random_seed_stability.csv

Type: .csv; size: 731 bytes.

Rows: 10. Family: **Supplementary experiment — exact evaluation window unverified**.

Period: No exact dates in this export; not admitted to overview rankings

Evidence: CSV schema and contents inspected; source notebook / explicit split metadata not included in bundle.

Caution: May describe validation, stress tests, uncertainty, timing or illustrative scenarios. Do not infer test dates or compatibility from similar scores.

| Column | Inferred dtype | Nulls |
|---|---|---|
| Model | object | 0 |
| Random_Seed | int64 | 0 |
| MAE | float64 | 0 |
| RMSE | float64 | 0 |
| WAPE (%) | float64 | 0 |

Observed date spans: `{}`

Exported context values: `{"Model": ["Random Forest", "XGBoost"]}`

## tables/random_seed_stability_summary.csv

Type: .csv; size: 310 bytes.

Rows: 2. Family: **Supplementary experiment — exact evaluation window unverified**.

Period: No exact dates in this export; not admitted to overview rankings

Evidence: CSV schema and contents inspected; source notebook / explicit split metadata not included in bundle.

Caution: May describe validation, stress tests, uncertainty, timing or illustrative scenarios. Do not infer test dates or compatibility from similar scores.

| Column | Inferred dtype | Nulls |
|---|---|---|
| Model | object | 0 |
| Mean_MAE | float64 | 0 |
| Mean_RMSE | float64 | 0 |
| Mean_WAPE | float64 | 0 |
| Std_WAPE | float64 | 0 |
| Min_WAPE | float64 | 0 |
| Max_WAPE | float64 | 0 |

Observed date spans: `{}`

Exported context values: `{"Model": ["Random Forest", "XGBoost"]}`

## tables/recursive_12_week_backtest_predictions.csv

Type: .csv; size: 1916 bytes.

Rows: 36. Family: **Early-2016 recursive backtest**.

Period: 2016-01-03 to 2016-03-20; cumulative 4/8/12-week windows

Evidence: Dated prediction rows and README_summary.md: Historical Recursive Forecast Validation; origin at end of 2015.

Caution: Three eligible warehouses; J excluded. Retrospective recursive diagnostic, not the annual holdout task.

| Column | Inferred dtype | Nulls |
|---|---|---|
| Warehouse | object | 0 |
| Week | object | 0 |
| Horizon_Week | int64 | 0 |
| Recursive_XGBoost | float64 | 0 |
| Seasonal_Naive | float64 | 0 |
| Demand | float64 | 0 |

Observed date spans: `{"Week": {"start": "2016-01-03", "end": "2016-03-20"}}`

Exported context values: `{"Warehouse": ["Whse_A", "Whse_C", "Whse_S"]}`

## tables/recursive_12_week_backtest_summary.csv

Type: .csv; size: 514 bytes.

Rows: 6. Family: **Early-2016 recursive backtest**.

Period: 2016-01-03 to 2016-03-20; cumulative 4/8/12-week windows

Evidence: Dated prediction rows and README_summary.md: Historical Recursive Forecast Validation; origin at end of 2015.

Caution: Three eligible warehouses; J excluded. Retrospective recursive diagnostic, not the annual holdout task.

| Column | Inferred dtype | Nulls |
|---|---|---|
| Horizon_Weeks | int64 | 0 |
| Model | object | 0 |
| Observations | int64 | 0 |
| MAE | float64 | 0 |
| RMSE | float64 | 0 |
| WAPE (%) | float64 | 0 |

Observed date spans: `{}`

Exported context values: `{"Horizon_Weeks": [4, 8, 12], "Model": ["Recursive XGBoost", "Seasonal Naive"], "Observations": [12, 24, 36]}`

## tables/recursive_12_week_warehouse_results.csv

Type: .csv; size: 524 bytes.

Rows: 6. Family: **Early-2016 recursive backtest**.

Period: 2016-01-03 to 2016-03-20; cumulative 4/8/12-week windows

Evidence: Dated prediction rows and README_summary.md: Historical Recursive Forecast Validation; origin at end of 2015.

Caution: Three eligible warehouses; J excluded. Retrospective recursive diagnostic, not the annual holdout task.

| Column | Inferred dtype | Nulls |
|---|---|---|
| Warehouse | object | 0 |
| Model | object | 0 |
| Observations | int64 | 0 |
| MAE | float64 | 0 |
| RMSE | float64 | 0 |
| WAPE (%) | float64 | 0 |

Observed date spans: `{}`

Exported context values: `{"Warehouse": ["Whse_A", "Whse_C", "Whse_S"], "Model": ["Recursive XGBoost", "Seasonal Naive"], "Observations": [12]}`

## tables/research_conclusions.csv

Type: .csv; size: 1702 bytes.

Rows: 11. Family: **Cross-experiment summary / documentation**.

Period: Mixed or not applicable; see individual metric/statement

Evidence: Table contents; summary labels may identify subsets but do not supply row-level predictions.

Caution: Do not treat summary rows as one evaluation cohort. Exported leakage PASS checks are not independent verification.

| Column | Inferred dtype | Nulls |
|---|---|---|
| Conclusion | object | 0 |

Observed date spans: `{}`

Exported context values: `{}`

## tables/research_limitations.csv

Type: .csv; size: 2483 bytes.

Rows: 15. Family: **Cross-experiment summary / documentation**.

Period: Mixed or not applicable; see individual metric/statement

Evidence: Table contents; summary labels may identify subsets but do not supply row-level predictions.

Caution: Do not treat summary rows as one evaluation cohort. Exported leakage PASS checks are not independent verification.

| Column | Inferred dtype | Nulls |
|---|---|---|
| Limitation | object | 0 |
| Impact | object | 0 |

Observed date spans: `{}`

Exported context values: `{}`

## tables/scenario_summary.csv

Type: .csv; size: 231 bytes.

Rows: 3. Family: **Supplementary experiment — exact evaluation window unverified**.

Period: No exact dates in this export; not admitted to overview rankings

Evidence: CSV schema and contents inspected; source notebook / explicit split metadata not included in bundle.

Caution: May describe validation, stress tests, uncertainty, timing or illustrative scenarios. Do not infer test dates or compatibility from similar scores.

| Column | Inferred dtype | Nulls |
|---|---|---|
| Scenario | object | 0 |
| Average_Risk_Ratio | float64 | 0 |
| Maximum_Risk_Ratio | float64 | 0 |
| Threshold_Exceedances | int64 | 0 |

Observed date spans: `{}`

Exported context values: `{}`

## tables/timesfm_historical_monthly_pooled.csv

Type: .csv; size: 3553 bytes.

Rows: 36. Family: **2014–2015 retrospective year-ahead diagnostics**.

Period: 2014-01-05 to 2014-12-28 and 2015-01-04 to 2015-12-27; 104 pooled weeks

Evidence: README_summary.md: TimesFM Historical Year-Ahead Backtesting; ETS validation table Year values.

Caution: ETS configuration selected on the same folds. ets_validation_summary reports fold means, not pooled error metrics.

| Column | Inferred dtype | Nulls |
|---|---|---|
| Month | int64 | 0 |
| Month_Name | object | 0 |
| Model | object | 0 |
| Validation_Years | object | 0 |
| Weeks | int64 | 0 |
| MAE | float64 | 0 |
| RMSE | float64 | 0 |
| WAPE (%) | float64 | 0 |

Observed date spans: `{}`

Exported context values: `{"Model": ["Seasonal Naive", "ETS", "TimesFM 3.0"], "Validation_Years": ["2014-2015 (retrospective)"], "Weeks": [8, 10, 9]}`

## tables/timesfm_historical_monthly_results.csv

Type: .csv; size: 17206 bytes.

Rows: 108. Family: **Mixed retrospective / holdout; split by Year and Evaluation**.

Period: 2014, 2015 retrospective; 2016 final holdout reference

Evidence: Explicit Year/Evaluation columns and README_summary.md historical analyses.

Caution: Do not pool 2016 with 2014–2015; monthly groups use recorded weekly dates, not daily calendar-month totals.

| Column | Inferred dtype | Nulls |
|---|---|---|
| Year | int64 | 0 |
| Month | int64 | 0 |
| Month_Name | object | 0 |
| Evaluation | object | 0 |
| Model | object | 0 |
| Weeks | int64 | 0 |
| MAE | float64 | 0 |
| RMSE | float64 | 0 |
| WAPE (%) | float64 | 0 |
| Actual_Month_Total | float64 | 0 |
| Predicted_Month_Total | float64 | 0 |
| Month_Total_Error | float64 | 0 |
| Month_Total_APE (%) | float64 | 0 |

Observed date spans: `{}`

Exported context values: `{"Year": [2014, 2015, 2016], "Evaluation": ["Retrospective validation", "2016 final holdout (reference)"], "Model": ["Seasonal Naive", "ETS", "TimesFM 3.0"], "Weeks": [4, 5]}`

## tables/timesfm_historical_pooled_summary.csv

Type: .csv; size: 289 bytes.

Rows: 3. Family: **2014–2015 retrospective year-ahead diagnostics**.

Period: 2014-01-05 to 2014-12-28 and 2015-01-04 to 2015-12-27; 104 pooled weeks

Evidence: README_summary.md: TimesFM Historical Year-Ahead Backtesting; ETS validation table Year values.

Caution: ETS configuration selected on the same folds. ets_validation_summary reports fold means, not pooled error metrics.

| Column | Inferred dtype | Nulls |
|---|---|---|
| Model | object | 0 |
| Validation_Years | object | 0 |
| Weeks | int64 | 0 |
| MAE | float64 | 0 |
| RMSE | float64 | 0 |
| WAPE (%) | float64 | 0 |

Observed date spans: `{}`

Exported context values: `{"Model": ["ETS", "TimesFM 3.0", "Seasonal Naive"], "Validation_Years": ["2014-2015"], "Weeks": [104]}`

## tables/timesfm_historical_quarterly_pooled.csv

Type: .csv; size: 1051 bytes.

Rows: 12. Family: **2014–2015 retrospective year-ahead diagnostics**.

Period: 2014-01-05 to 2014-12-28 and 2015-01-04 to 2015-12-27; 104 pooled weeks

Evidence: README_summary.md: TimesFM Historical Year-Ahead Backtesting; ETS validation table Year values.

Caution: ETS configuration selected on the same folds. ets_validation_summary reports fold means, not pooled error metrics.

| Column | Inferred dtype | Nulls |
|---|---|---|
| Quarter | object | 0 |
| Model | object | 0 |
| Validation_Years | object | 0 |
| Weeks | int64 | 0 |
| MAE | float64 | 0 |
| RMSE | float64 | 0 |
| WAPE (%) | float64 | 0 |

Observed date spans: `{}`

Exported context values: `{"Model": ["Seasonal Naive", "ETS", "TimesFM 3.0"], "Validation_Years": ["2014-2015"], "Weeks": [26]}`

## tables/timesfm_historical_quarterly_results.csv

Type: .csv; size: 3817 bytes.

Rows: 36. Family: **Mixed retrospective / holdout; split by Year and Evaluation**.

Period: 2014, 2015 retrospective; 2016 final holdout reference

Evidence: Explicit Year/Evaluation columns and README_summary.md historical analyses.

Caution: Do not pool 2016 with 2014–2015; monthly groups use recorded weekly dates, not daily calendar-month totals.

| Column | Inferred dtype | Nulls |
|---|---|---|
| Year | int64 | 0 |
| Quarter | object | 0 |
| Evaluation | object | 0 |
| Model | object | 0 |
| Weeks | int64 | 0 |
| MAE | float64 | 0 |
| RMSE | float64 | 0 |
| WAPE (%) | float64 | 0 |

Observed date spans: `{}`

Exported context values: `{"Year": [2014, 2015, 2016], "Evaluation": ["Retrospective validation", "2016 final holdout (reference)"], "Model": ["TimesFM 3.0", "Seasonal Naive", "ETS"], "Weeks": [13]}`

## tables/timesfm_historical_weekly_predictions.csv

Type: .csv; size: 43081 bytes.

Rows: 468. Family: **Mixed retrospective / holdout; split by Year and Evaluation**.

Period: 2014, 2015 retrospective; 2016 final holdout reference

Evidence: Explicit Year/Evaluation columns and README_summary.md historical analyses.

Caution: Do not pool 2016 with 2014–2015; monthly groups use recorded weekly dates, not daily calendar-month totals.

| Column | Inferred dtype | Nulls |
|---|---|---|
| Year | int64 | 0 |
| Evaluation | object | 0 |
| Date | object | 0 |
| Model | object | 0 |
| Actual | float64 | 0 |
| Prediction | float64 | 0 |
| Error | float64 | 0 |

Observed date spans: `{"Date": {"start": "2014-01-05", "end": "2016-12-25"}}`

Exported context values: `{"Year": [2014, 2015, 2016], "Evaluation": ["Retrospective validation", "2016 final holdout (reference)"], "Model": ["TimesFM 3.0", "ETS", "Seasonal Naive"]}`

## tables/timesfm_historical_yearly_results.csv

Type: .csv; size: 1025 bytes.

Rows: 9. Family: **Mixed retrospective / holdout; split by Year and Evaluation**.

Period: 2014, 2015 retrospective; 2016 final holdout reference

Evidence: Explicit Year/Evaluation columns and README_summary.md historical analyses.

Caution: Do not pool 2016 with 2014–2015; monthly groups use recorded weekly dates, not daily calendar-month totals.

| Column | Inferred dtype | Nulls |
|---|---|---|
| Year | int64 | 0 |
| Evaluation | object | 0 |
| Model | object | 0 |
| Train_Weeks | int64 | 0 |
| Forecast_Weeks | int64 | 0 |
| MAE | float64 | 0 |
| RMSE | float64 | 0 |
| WAPE (%) | float64 | 0 |

Observed date spans: `{}`

Exported context values: `{"Year": [2014, 2015, 2016], "Evaluation": ["Retrospective validation", "2016 final holdout (reference)"], "Model": ["TimesFM 3.0", "ETS", "Seasonal Naive"], "Forecast_Weeks": [52]}`

## tables/timesfm_monthly_lowest_wape_models.csv

Type: .csv; size: 2548 bytes.

Rows: 36. Family: **Mixed retrospective / holdout; split by Year and Evaluation**.

Period: 2014, 2015 retrospective; 2016 final holdout reference

Evidence: Explicit Year/Evaluation columns and README_summary.md historical analyses.

Caution: Do not pool 2016 with 2014–2015; monthly groups use recorded weekly dates, not daily calendar-month totals.

| Column | Inferred dtype | Nulls |
|---|---|---|
| Year | int64 | 0 |
| Month | int64 | 0 |
| Month_Name | object | 0 |
| Evaluation | object | 0 |
| Lowest_WAPE_Model | object | 0 |
| Weeks | int64 | 0 |
| WAPE (%) | float64 | 0 |

Observed date spans: `{}`

Exported context values: `{"Year": [2014, 2015, 2016], "Evaluation": ["Retrospective validation", "2016 final holdout (reference)"], "Weeks": [4, 5]}`

## tables/timesfm_monthly_stability_summary.csv

Type: .csv; size: 421 bytes.

Rows: 3. Family: **2014–2015 retrospective year-ahead diagnostics**.

Period: 2014-01-05 to 2014-12-28 and 2015-01-04 to 2015-12-27; 104 pooled weeks

Evidence: README_summary.md: TimesFM Historical Year-Ahead Backtesting; ETS validation table Year values.

Caution: ETS configuration selected on the same folds. ets_validation_summary reports fold means, not pooled error metrics.

| Column | Inferred dtype | Nulls |
|---|---|---|
| Model | object | 0 |
| Validation_Years | object | 0 |
| Pooled_Monthly_WAPE_Min | float64 | 0 |
| Pooled_Monthly_WAPE_Max | float64 | 0 |
| Pooled_Monthly_WAPE_Range_pp | float64 | 0 |
| Lowest_WAPE_Year_Month_Count_of_24 | int64 | 0 |

Observed date spans: `{}`

Exported context values: `{"Model": ["ETS", "Seasonal Naive", "TimesFM 3.0"], "Validation_Years": ["2014-2015 (retrospective)"]}`

## tables/timesfm_quarterly_lowest_wape_models.csv

Type: .csv; size: 843 bytes.

Rows: 12. Family: **Mixed retrospective / holdout; split by Year and Evaluation**.

Period: 2014, 2015 retrospective; 2016 final holdout reference

Evidence: Explicit Year/Evaluation columns and README_summary.md historical analyses.

Caution: Do not pool 2016 with 2014–2015; monthly groups use recorded weekly dates, not daily calendar-month totals.

| Column | Inferred dtype | Nulls |
|---|---|---|
| Year | int64 | 0 |
| Quarter | object | 0 |
| Evaluation | object | 0 |
| Lowest_WAPE_Model | object | 0 |
| Weeks | int64 | 0 |
| WAPE (%) | float64 | 0 |

Observed date spans: `{}`

Exported context values: `{"Year": [2014, 2015, 2016], "Evaluation": ["Retrospective validation", "2016 final holdout (reference)"], "Weeks": [13]}`

## tables/timesfm_quarterly_stability_summary.csv

Type: .csv; size: 384 bytes.

Rows: 3. Family: **2014–2015 retrospective year-ahead diagnostics**.

Period: 2014-01-05 to 2014-12-28 and 2015-01-04 to 2015-12-27; 104 pooled weeks

Evidence: README_summary.md: TimesFM Historical Year-Ahead Backtesting; ETS validation table Year values.

Caution: ETS configuration selected on the same folds. ets_validation_summary reports fold means, not pooled error metrics.

| Column | Inferred dtype | Nulls |
|---|---|---|
| Model | object | 0 |
| Historical_Validation_Years | object | 0 |
| Pooled_Quarterly_WAPE_Min | float64 | 0 |
| Pooled_Quarterly_WAPE_Max | float64 | 0 |
| Pooled_Quarterly_WAPE_Range_pp | float64 | 0 |
| Best_Year_Quarter_Count_of_8 | int64 | 0 |

Observed date spans: `{}`

Exported context values: `{"Model": ["Seasonal Naive", "ETS", "TimesFM 3.0"], "Historical_Validation_Years": ["2014-2015"]}`

## tables/timesfm_zero_shot_results.csv

Type: .csv; size: 104 bytes.

Rows: 1. Family: **2016 aggregate full-year holdout**.

Period: 2016-01-03 to 2016-12-25; 52 weekly timestamps

Evidence: README_summary.md: Additional Full-Year Forecasting Results; weekly predictions corroborate dates for ETS, TimesFM and Seasonal Naive.

Caution: Aggregate year-ahead forecasts; later comparisons are exploratory, not independent post-selection validation.

| Column | Inferred dtype | Nulls |
|---|---|---|
| Model | object | 0 |
| MAE | float64 | 0 |
| RMSE | float64 | 0 |
| WAPE (%) | float64 | 0 |

Observed date spans: `{}`

Exported context values: `{"Model": ["TimesFM 3.0 Zero-Shot"]}`

## tables/warehouse_characteristics.csv

Type: .csv; size: 712 bytes.

Rows: 4. Family: **2016 warehouse rolling forecasts**.

Period: 2016; 52 test weeks for A/C/S; 51 for J in dashboard_performance_summary

Evidence: Original HTML dashboard trace timestamps and Test_Weeks; README_summary.md distinguishes warehouse rolling evaluation.

Caution: Within-warehouse comparisons only; different grain and information set from aggregate year-ahead forecasts.

| Column | Inferred dtype | Nulls |
|---|---|---|
| Warehouse | object | 0 |
| Mean_Demand | float64 | 0 |
| Demand_Std | float64 | 0 |
| Training_Weeks | int64 | 0 |
| CV | float64 | 0 |
| MAE | float64 | 0 |
| RMSE | float64 | 0 |
| WAPE (%) | float64 | 0 |
| Demand_Scale | object | 0 |
| Volatility_Level | object | 0 |

Observed date spans: `{}`

Exported context values: `{"Warehouse": ["Whse_A", "Whse_C", "Whse_J", "Whse_S"]}`

## tables/warehouse_model_comparison.csv

Type: .csv; size: 223 bytes.

Rows: 3. Family: **2016 warehouse rolling forecasts**.

Period: 2016; 52 test weeks for A/C/S; 51 for J in dashboard_performance_summary

Evidence: Original HTML dashboard trace timestamps and Test_Weeks; README_summary.md distinguishes warehouse rolling evaluation.

Caution: Within-warehouse comparisons only; different grain and information set from aggregate year-ahead forecasts.

| Column | Inferred dtype | Nulls |
|---|---|---|
| Model | object | 0 |
| MAE | float64 | 0 |
| RMSE | float64 | 0 |
| WAPE (%) | float64 | 0 |

Observed date spans: `{}`

Exported context values: `{"Model": ["Naive", "Random Forest", "XGBoost"]}`

## tables/week10_robustness.csv

Type: .csv; size: 248 bytes.

Rows: 7. Family: **Cross-experiment summary / documentation**.

Period: Mixed or not applicable; see individual metric/statement

Evidence: Table contents; summary labels may identify subsets but do not supply row-level predictions.

Caution: Do not treat summary rows as one evaluation cohort. Exported leakage PASS checks are not independent verification.

| Column | Inferred dtype | Nulls |
|---|---|---|
| Metric | object | 0 |
| Value | object | 0 |

Observed date spans: `{}`

Exported context values: `{}`

## tables/week7_uncertainty.csv

Type: .csv; size: 174 bytes.

Rows: 1. Family: **Supplementary experiment — exact evaluation window unverified**.

Period: No exact dates in this export; not admitted to overview rankings

Evidence: CSV schema and contents inspected; source notebook / explicit split metadata not included in bundle.

Caution: May describe validation, stress tests, uncertainty, timing or illustrative scenarios. Do not infer test dates or compatibility from similar scores.

| Column | Inferred dtype | Nulls |
|---|---|---|
| Target Coverage (%) | float64 | 0 |
| Observed Coverage (%) | float64 | 0 |
| Average Interval Width | float64 | 0 |
| Point Forecast MAE | float64 | 0 |
| Actual Above Upper Bound | int64 | 0 |

Observed date spans: `{}`

Exported context values: `{}`

## tables/week9_interpretation.csv

Type: .csv; size: 217 bytes.

Rows: 6. Family: **Cross-experiment summary / documentation**.

Period: Mixed or not applicable; see individual metric/statement

Evidence: Table contents; summary labels may identify subsets but do not supply row-level predictions.

Caution: Do not treat summary rows as one evaluation cohort. Exported leakage PASS checks are not independent verification.

| Column | Inferred dtype | Nulls |
|---|---|---|
| Metric | object | 0 |
| Value | object | 0 |

Observed date spans: `{}`

Exported context values: `{}`

## warehouse_forecasting_dashboard.html

Type: .html; size: 4873997 bytes.
