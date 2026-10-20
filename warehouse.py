"""Warehouse Analytics: actual-demand characteristics, scoped scores and deep dive."""
from ui_controls import choice
from product_layout import insights, mini_cards, panel
import calendar

import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from chart_access import chart_header, chart_options, chart_view, data_section, filters, download_frame, source_detail

from comparison_data import METRICS, reconciliation_predictions
from data_loading import DataIssue, source_directory
from display_formatting import compact_units, readable_table
from historical_data import aggregate_history, seasonal_profile, trend_with_gaps
from model_comparison import comparison_chart, prediction_panel
from design_system import finding, WAREHOUSE_COLORS
from overview import COLORS, data_download
from warehouse_data import (ACTUAL_SOURCE, SCORE_SOURCE, aligned_actuals, load_warehouse_actuals,
                            warehouse_rankings, warehouse_statistics)

PALETTE = WAREHOUSE_COLORS


def render_warehouse():
    directory = source_directory()
    try:
        history = load_warehouse_actuals(directory)
    except (DataIssue, OSError, ValueError) as exc:
        st.warning(f"Warehouse analytics data unavailable: {exc}")
        return
    st.info("Observed demand covers 10 Jan–25 Dec 2016: 51 exported weeks per warehouse. Totals summarize this sample only; they are not extrapolated into full-year totals. Rolling model scores use separate 52-week samples for A/C/S and 51 weeks for J.")
    with filters('Filters', 'warehouse_warehouse_filters'):
        selected = st.multiselect("Warehouses to compare", sorted(history.Series.unique()),
                                  default=sorted(history.Series.unique()), key="warehouse_selected", persist_state="session")
        aggregation = st.selectbox("Warehouse trend aggregation", ["Weekly", "Monthly", "Quarterly"], key="warehouse_aggregation", persist_state="session")
    if not selected:
        st.info("Select at least one warehouse to view demand, performance and deep-dive results.")
        return
    actual = aligned_actuals(history, selected)
    if actual.empty:
        st.warning("No shared observation dates are available for the selected warehouses.")
        return
    stats = warehouse_statistics(actual)
    weekly_selected = actual.groupby("Date").Demand.sum()
    mini_cards([(row.Warehouse, compact_units(row.Observed_Sum), f"{int(row.Observed_Weeks)} weeks · {row.Selected_Demand_Share_Pct:.1f}% of selected sample") for row in stats.itertuples()])
    with st.container(key="wiq_hero_row"):
        hero_left, hero_right = st.columns([1.5, 1], gap="medium")
    insight_slot = st.container()
    demand_tab, performance_tab, deep_tab = st.tabs(["Demand profile", "Forecast comparison", "Warehouse detail"])
    with demand_tab, data_section("Selected sample KPIs & sources", 'Methodology'):
        a, b, c, d = st.columns(4)
        a.metric("Selected observed demand", compact_units(actual.Demand.sum()))
        a.caption("Order-demand units · 51-week sample")
        b.metric("Mean selected total per week", compact_units(weekly_selected.mean()))
        b.caption("Combined selected warehouses · units/week")
        c.metric("Observed warehouse-weeks", f"{len(actual):,}")
        c.caption(f"{len(selected)} warehouse(s) · {actual.Date.nunique()} aligned dates")
        d.metric("Observed date coverage", f"{actual.Date.nunique()} weeks")
        d.caption(f"{actual.Date.min():%d %b %Y} – {actual.Date.max():%d %b %Y}")
        st.caption(f"Source for observed-demand KPIs: {ACTUAL_SOURCE} · Demand column only; forecast values are excluded.")


    with demand_tab:
        with hero_left, panel("warehouse_trends", "Demand across the network", "Aligned observed weeks · 10 Jan–25 Dec 2016"):
            grouped = aggregate_history(actual, aggregation)
            figure = px.line(trend_with_gaps(grouped, aggregation), x="Period", y="Demand", color="Series", markers=True,
                             color_discrete_map=PALETTE, custom_data=["Observations"],
                             labels={"Series": "Warehouse", "Demand": "Actual order demand (units)" if aggregation == "Weekly" else "Sum of observed weekly actuals (units)",
                                     "Period": "Recorded weekly date" if aggregation == "Weekly" else f"{aggregation} bucket of weekly timestamps"})
            figure.update_traces(connectgaps=False, hovertemplate="%{x|%Y-%m-%d}<br>%{y:,.0f} units<br>%{customdata[0]} observed weeks<extra>%{fullData.name}</extra>")
            figure.update_layout(hovermode="x unified")
            comparison_chart(figure, "warehouse_actual_trends", height=310)
            st.caption("Actual demand only. Monthly/quarterly sums assign entire weeks to their recorded timestamp; they are not exact daily calendar-period transaction totals. January and Q1 have reduced coverage. No missing observations are filled.")
            data_download(grouped, "warehouse_actual_trends")

        variation_panel, monthly_panel = st.columns(2)
        st.markdown("#### Demand scale & variability")
        with hero_right, panel("warehouse_scale", "Demand scale", "Selected 51-week sample · not full-year totals"):
            figure = px.bar(stats, x="Warehouse", y="Observed_Sum", color="Warehouse", color_discrete_map=PALETTE,
                            labels={"Observed_Sum": "Observed sample demand (units)"})
            figure.update_layout(showlegend=False)
            comparison_chart(figure, "warehouse_observed_sums", height=310)
        with variation_panel, panel("warehouse_variability", "Relative weekly variation", "CV describes demand variability, not forecast error"):
            cv_plot = stats.assign(CV_Percent=stats.CV * 100)
            figure = px.bar(cv_plot, x="Warehouse", y="CV_Percent", color="Warehouse", color_discrete_map=PALETTE,
                            labels={"CV_Percent": "Weekly coefficient of variation (%)"})
            figure.update_layout(showlegend=False)
            comparison_chart(figure, "warehouse_cv", height=350)
        with data_section("Demand statistics & selected-sample shares", 'Full Data Tables'):
            stats_columns = ["Warehouse", "Observed_Sum", "Mean_Weekly_Demand", "Weekly_Std_Dev", "CV", "Observed_Weeks", "Selected_Demand_Share_Pct"]
            st.dataframe(readable_table(stats[stats_columns]), width="stretch", hide_index=True,
                         column_config={"Observed_Sum": st.column_config.NumberColumn("Observed demand"),
                                        "Mean_Weekly_Demand": st.column_config.NumberColumn("Weekly mean"),
                                        "Weekly_Std_Dev": st.column_config.NumberColumn("Weekly std. dev."),
                                        "Observed_Weeks": st.column_config.NumberColumn("Observed weeks"),
                                        "Selected_Demand_Share_Pct": st.column_config.NumberColumn("Selected sample share (%)", format="%.2f")})
        st.caption("Weekly mean and sample standard deviation (n−1) are calculated from observed demand. CV = standard deviation / mean; displayed as a percentage and undefined for nonpositive means. Shares refer only to selected warehouses in this 51-week sample. These are demand characteristics, not forecasting accuracy scores.")
        largest = stats.loc[stats.Observed_Sum.idxmax()]
        finding(f"{largest.Warehouse} has the largest share of selected observed demand",
                f"{largest.Selected_Demand_Share_Pct:.1f}% of the selected 51-week warehouse sample. Demand scale varies; use WAPE alongside absolute forecast errors, and do not interpret this share as physical capacity.")
        if stats.CV.notna().any():
            variable = stats.loc[stats.CV.idxmax()]
            st.caption(f"Highest selected relative weekly variability: {variable.Warehouse} (CV {variable.CV:.1%}). This is observed variation, not a cause of demand changes.")
        data_download(stats, "warehouse_demand_statistics")

        with monthly_panel, panel("warehouse_months", "Monthly demand pattern", "Mean observed demand per week; partial January coverage"):
            monthly = seasonal_profile(actual)
            values = monthly.pivot(index="Series", columns="Month", values="Mean_Weekly_Demand").reindex(columns=range(1, 13))
            counts = monthly.pivot(index="Series", columns="Month", values="Observed_Weeks").reindex(index=values.index, columns=range(1, 13))
            figure = go.Figure(go.Heatmap(x=list(calendar.month_abbr)[1:], y=values.index, z=values.to_numpy(),
                                         customdata=counts.to_numpy(), colorscale="Teal", colorbar=dict(title="Mean units/week"), hoverongaps=False,
                                         hovertemplate="%{y} · %{x}<br>Mean weekly actual: %{z:,.0f} units<br>%{customdata} observed weeks<extra></extra>"))
            comparison_chart(figure, "warehouse_monthly_patterns", height=350)
            st.caption("Mean weekly actual demand by recorded month. Hover for observation counts. One partial historical year supports descriptive patterns, not a claim of stable recurring seasonality or a validated capacity/staffing requirement.")
            source_detail("Source for all demand panels: " + ACTUAL_SOURCE)
            data_download(monthly, "warehouse_monthly_patterns")

    with performance_tab:
        st.subheader("Which model had the lowest error at each warehouse?")
        metric = choice("Warehouse performance metric", METRICS, horizontal=True, key="warehouse_metric", persist_state="session")
        try:
            ranked = warehouse_rankings(directory, selected, metric)
            winners = ranked.loc[ranked.Rank_Within_Warehouse.eq(1)]
            st.caption("One-step rolling evaluation · A/C/S: 03 Jan–25 Dec 2016 (52 weeks); J: 10 Jan–25 Dec 2016 (51 weeks). Target is each warehouse's weekly order demand. Exact rolling fit/update details are not exported.")
            st.warning("The chart places separate warehouse cohorts side by side. There is no cross-warehouse leaderboard or pooled winner. These scores are not comparable to aggregate year-ahead or fixed-origin recursive scores. MAE/RMSE also depend on warehouse demand scale.")
            figure = px.bar(ranked, x="Warehouse", y=metric, color="Model", barmode="group", color_discrete_map=COLORS,
                            custom_data=["Test_Weeks", "Evaluation_Period"])
            figure.update_traces(hovertemplate="%{x}<br>%{y:,.4f}<br>%{customdata[0]} test weeks<br>%{customdata[1]}<extra>%{fullData.name}</extra>")
            comparison_chart(figure, "warehouse_performance", height=400)
            st.markdown("#### Lowest exported error in each warehouse cohort")
            st.dataframe(readable_table(winners[["Warehouse", "Model", metric, "Test_Weeks", "Evaluation_Period", "Horizon"]]),
                         width="stretch", hide_index=True)
            st.caption("Best is defined by the selected metric among Naive, Random Forest and XGBoost for that warehouse only. Ties are retained. This descriptive result does not establish statistical superiority or deployment readiness.")
            for warehouse in selected:
                winning = winners.loc[winners.Warehouse.eq(warehouse)]
                value = winning[metric].iloc[0]
                formatted = f"{value:.2f}%" if metric == "WAPE (%)" else compact_units(value)
                st.write(f"**{warehouse}**: {', '.join(winning.Model)} has the lowest exported {metric} (**{formatted}**) within its rolling sample.")
            columns = ["Warehouse", "Rank_Within_Warehouse", "Model", "Model_Type"] + METRICS + ["Test_Weeks", "Evaluation_Period", "Horizon", "Methodology", "Source"]
            with data_section("All rolling model scores & evaluation metadata", 'Methodology'):
                st.dataframe(readable_table(ranked[columns]), width="stretch", hide_index=True)
            source_detail("Source: " + SCORE_SOURCE + " · all metric values are exported scores, not recalculated from the shorter demand sample.")
            data_download(ranked, "warehouse_rolling_performance")
        except (DataIssue, OSError, ValueError, KeyError) as exc:
            st.warning(f"Warehouse performance data unavailable: {exc}")

    with deep_tab:
        st.subheader("Explore one warehouse in detail")
        warehouse = st.selectbox("Deep-dive warehouse", selected, key="warehouse_deep_dive", persist_state="session")
        row = stats.loc[stats.Warehouse.eq(warehouse)].iloc[0]
        a, b, c, d = st.columns(4)
        a.metric("Observed sample demand", compact_units(row.Observed_Sum))
        b.metric("Mean weekly actual", compact_units(row.Mean_Weekly_Demand))
        c.metric("Weekly standard deviation", compact_units(row.Weekly_Std_Dev))
        d.metric("Weekly CV", f"{row.CV:.1%}" if row.CV == row.CV else "Undefined")
        st.caption(f"{warehouse} · {int(row.Observed_Weeks)} weeks · {row.First_Observation:%d %b %Y} – {row.Last_Observation:%d %b %Y} · source: {ACTUAL_SOURCE}")
        st.write(f"The largest observed week in this sample is **{row.Peak_Observed_Week:%d %b %Y}**, with **{compact_units(row.Max_Weekly_Demand)}** demand units. The export does not establish a cause or an operational capacity limit.")
        try:
            performance = warehouse_rankings(directory, [warehouse], metric)
            st.markdown("#### Warehouse-specific rolling scores")
            st.caption(f"Ranking metric: {metric} (selected on Forecast performance). These scores use the rolling evaluation period below, not necessarily the 51-week observed-demand sample above.")
            st.dataframe(readable_table(performance[["Model", "Rank_Within_Warehouse"] + METRICS + ["Test_Weeks", "Evaluation_Period"]]), width="stretch", hide_index=True)
            source_detail("Source: " + SCORE_SOURCE)
            data_download(performance, "warehouse_deep_dive_scores")
        except (DataIssue, OSError, ValueError, KeyError) as exc:
            st.warning(f"Warehouse rolling detail unavailable: {exc}")
        st.markdown("#### Actual vs predicted · separate reconciliation diagnostic")
        st.info("Complete aligned CSV trajectories for the rolling Naive/Random Forest/XGBoost comparison are unavailable. The chart below uses the separate 51-week reconciliation export; it does not illustrate or recompute the rolling scores above.")
        try:
            predictions = reconciliation_predictions(directory, warehouse)
            st.caption(f"{warehouse} · {predictions.Date.min():%d %b %Y} – {predictions.Date.max():%d %b %Y} · {predictions.Date.nunique()} aligned weeks · source: {ACTUAL_SOURCE}")
            prediction_panel(predictions, list(predictions.Model.unique()), "warehouse_deep_dive_predictions",
                             "Solid: actual demand. Dashed: original nonnegative warehouse forecast and reconciled forecast. No per-warehouse reconciliation scores are manufactured.")
            st.caption("Model types: XGBoost-based original warehouse forecast; hierarchical reconciliation of those predictions. This historical diagnostic is not a new forecast or proof of a better operational plan.")
        except (DataIssue, OSError, ValueError, KeyError) as exc:
            st.warning(f"Aligned warehouse predictions unavailable: {exc}")

    with insight_slot:
        largest = stats.loc[stats.Observed_Sum.idxmax()]
        insights([
            ("Key finding", f"{largest.Warehouse} leads the selected demand sample", f"{largest.Selected_Demand_Share_Pct:.1f}% of selected observed units; no cross-warehouse accuracy rank."),
            ("Important caveat", "51 observed weeks", "January and Q1 have reduced coverage. Rolling scores use their own 51/52-week samples."),
            ("Explore next", "Profile → forecast → detail", "Compare variation, then inspect each warehouse within its own evaluation cohort."),
        ])
    with data_section("Coverage, sources & interpretation limits", 'Data Sources'):
        st.dataframe(stats[["Warehouse", "Observed_Weeks", "First_Observation", "Last_Observation", "Gaps_Over_7_Days"]], hide_index=True, width="stretch")
        st.markdown(f"""- **Actual-demand source:** `{ACTUAL_SOURCE}` — only `Demand` is used for demand KPIs and patterns; model predictions are not counted as actuals.
- **Rolling-score source:** `{SCORE_SOURCE}` — Naive, Random Forest and XGBoost; rank separately within each warehouse and metric.
- **Aligned prediction diagnostic:** `{ACTUAL_SOURCE}` — `Original_Nonnegative` and `Reconciled_Forecast` against `Demand` on the same timestamps.
- Warehouse training characteristics and early-2016 recursive backtests describe other samples and are not merged with this observed-demand sample or rolling evaluation.
- The exports do not provide daily transactions, a full multi-year warehouse history, staffing, inventory, verified shipping volume, physical capacity or operating costs. No such quantities or causal explanations are inferred.
- Weekly timestamp-based calendar groupings are descriptive sums/means of recorded weeks, not exact daily transaction aggregates. Original capstone files remain unchanged; no forecasting models are retrained.""")
    st.caption("WAREHOUSE ANALYTICS · Actual-demand characteristics and forecasting accuracy remain separate · CSV downloads retain full numerical precision")
