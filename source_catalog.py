"""Reviewed evaluation families; table names never imply comparable scores."""

GROUPS = {
    "2016 aggregate full-year holdout": {
        "files": "full_year_model_comparison ets_sarima_comparison timesfm_zero_shot_results prophet_comparison nbeats_nhits_comparison quarterly_forecast_performance",
        "period": "2016-01-03 to 2016-12-25; 52 weekly timestamps",
        "evidence": "README_summary.md: Additional Full-Year Forecasting Results; weekly predictions corroborate dates for ETS, TimesFM and Seasonal Naive.",
        "caution": "Aggregate year-ahead forecasts; later comparisons are exploratory, not independent post-selection validation.",
    },
    "2014–2015 retrospective year-ahead diagnostics": {
        "files": "timesfm_historical_pooled_summary timesfm_historical_quarterly_pooled timesfm_historical_monthly_pooled timesfm_quarterly_stability_summary timesfm_monthly_stability_summary ets_validation_results ets_validation_summary",
        "period": "2014-01-05 to 2014-12-28 and 2015-01-04 to 2015-12-27; 104 pooled weeks",
        "evidence": "README_summary.md: TimesFM Historical Year-Ahead Backtesting; ETS validation table Year values.",
        "caution": "ETS configuration selected on the same folds. ets_validation_summary reports fold means, not pooled error metrics.",
    },
    "Mixed retrospective / holdout; split by Year and Evaluation": {
        "files": "timesfm_historical_yearly_results timesfm_historical_weekly_predictions timesfm_historical_quarterly_results timesfm_historical_monthly_results timesfm_quarterly_lowest_wape_models timesfm_monthly_lowest_wape_models",
        "period": "2014, 2015 retrospective; 2016 final holdout reference",
        "evidence": "Explicit Year/Evaluation columns and README_summary.md historical analyses.",
        "caution": "Do not pool 2016 with 2014–2015; monthly groups use recorded weekly dates, not daily calendar-month totals.",
    },
    "2016 warehouse rolling forecasts": {
        "files": "dashboard_performance_summary warehouse_model_comparison warehouse_characteristics forecast_bias_summary forecast_bias_quarterly forecast_error_summary global_local_comparison",
        "period": "2016; 52 test weeks for A/C/S; 51 for J in dashboard_performance_summary",
        "evidence": "Original HTML dashboard trace timestamps and Test_Weeks; README_summary.md distinguishes warehouse rolling evaluation.",
        "caution": "Within-warehouse comparisons only; different grain and information set from aggregate year-ahead forecasts.",
    },
    "2016 common-period / reconciliation subset": {
        "files": "common_model_comparison hierarchical_reconciliation hierarchical_warehouse_comparison hierarchical_warehouse_forecasts model_monitoring_2016 ensemble_aggregate_comparison",
        "period": "2016-01-10 to 2016-12-25; 51 weeks (dated exports and research_conclusions.csv)",
        "evidence": "hierarchical_warehouse_forecasts.csv, model_monitoring_2016.csv; research_conclusions.csv 51-week common-period statement.",
        "caution": "Never combine with 52-week full-year errors; ensemble is separately evaluated.",
    },
    "Statistical comparison — exact evaluation dates unverified": {
        "files": "forecast_significance_test",
        "period": "51 observations; exact dates and target level not encoded in this export",
        "evidence": "Comparison, Weeks, Mean_Loss_Difference, HAC_p_value and 95% interval columns only.",
        "caution": "Do not borrow dates from another 51-week table. Named test, statistic, loss definition and HAC settings are not exported; non-significance is not proof of equality.",
    },
    "Early-2016 recursive backtest": {
        "files": "recursive_12_week_backtest_predictions recursive_12_week_backtest_summary recursive_12_week_warehouse_results",
        "period": "2016-01-03 to 2016-03-20; cumulative 4/8/12-week windows",
        "evidence": "Dated prediction rows and README_summary.md: Historical Recursive Forecast Validation; origin at end of 2015.",
        "caution": "Three eligible warehouses; J excluded. Retrospective recursive diagnostic, not the annual holdout task.",
    },
    "Archived future forecasts": {
        "files": "future_warehouse_weekly_forecasts future_4_8_12_week_summary future_operational_decision_summary",
        "period": "Origin 2016-12-25; forecasts 2017-01-01 to 2017-03-19",
        "evidence": "Forecast_Origin and Week in future_warehouse_weekly_forecasts.csv; 4/8/12-week summaries.",
        "caution": "No complete 2017 evaluation outcomes. Risk categories and planning considerations are illustrative; P90 is not physical capacity.",
    },
    "2016 matched multi-horizon samples": {
        "files": "multi_horizon_predictions multi_horizon_comparison",
        "period": "2016-03-27 to 2016-12-25; 40 test weeks per horizon",
        "evidence": "Week and Horizon_Weeks in prediction export; Test_Weeks in comparison.",
        "caution": "Compare models within one horizon only; not equivalent to full-year or recursive evaluation.",
    },
    "External M5 validation": {
        "files": "m5_external_validation",
        "period": "Exact test dates not exported",
        "evidence": "README_summary.md: External Validation; separate M5 retail dataset.",
        "caution": "Different dataset and demand scale. Excluded from primary-data model rankings.",
    },
    "Cross-experiment summary / documentation": {
        "files": "final_metrics_summary research_conclusions research_limitations artifact_manifest final_presentation_outline final_report_outline week10_robustness week9_interpretation data_leakage_audit",
        "period": "Mixed or not applicable; see individual metric/statement",
        "evidence": "Table contents; summary labels may identify subsets but do not supply row-level predictions.",
        "caution": "Do not treat summary rows as one evaluation cohort. Exported leakage PASS checks are not independent verification.",
    },
}


def evaluation_context(filename):
    stem = filename.rsplit("/", 1)[-1].removesuffix(".csv")
    for family, group in GROUPS.items():
        if stem in group["files"].split():
            return {"family": family, **{k: v for k, v in group.items() if k != "files"}}
    return {
        "family": "Supplementary experiment — exact evaluation window unverified",
        "period": "No exact dates in this export; not admitted to overview rankings",
        "evidence": "CSV schema and contents inspected; source notebook / explicit split metadata not included in bundle.",
        "caution": "May describe validation, stress tests, uncertainty, timing or illustrative scenarios. Do not infer test dates or compatibility from similar scores.",
    }
