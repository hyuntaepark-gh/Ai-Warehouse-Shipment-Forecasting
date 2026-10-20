"""Archived December 2016 projections; never current forecasts or future accuracy."""
from ui_controls import choice
from product_layout import insights, mini_cards, panel
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from chart_access import chart_header, chart_options, chart_view, data_section, filters, download_frame, source_detail

from data_loading import DataIssue, source_directory
from display_formatting import compact_units, readable_table
from future_data import (HORIZONS, SUMMARY_SOURCE, TOLERANCE_UNITS, WAREHOUSES, WEEKLY_SOURCE,
                         combined_summaries, forecast_views, load_archive, warehouse_summaries)
from model_comparison import comparison_chart
from design_system import finding
from overview import data_download
from validation_data import evidence
from warehouse import PALETTE


def reliability_context(directory):
    with data_section("Methodology & separate historical reliability evidence", 'Methodology'):
        st.write("The capstone describes a recursive process: refit using available historical observations, predict the next week, then use predicted values in later forecasting steps. This page reads the saved output; it does not refit or execute a model. The future CSV does not encode model identity or hyperparameters.")
        st.warning("Future origin: 25 December 2016. Historical backtest origin: end of 2015, with the exact origin date not exported. These are different forecast exercises. Backtest error is not an accuracy score for the archived 2017 projections.")
        try:
            summary = evidence(directory, "recursive_12_week_backtest_summary")
            summary = summary.loc[summary.Horizon_Weeks.eq(12)]
            predictions = evidence(directory, "recursive_12_week_backtest_predictions")
            warehouses = evidence(directory, "recursive_12_week_warehouse_results")
            st.caption(f"Observed backtest window: {predictions.Week.min():%d %b %Y} – {predictions.Week.max():%d %b %Y} · {len(predictions)} warehouse-weeks · A/C/S only")
            st.dataframe(readable_table(summary), width="stretch", hide_index=True)
            source_detail("Source: tables/recursive_12_week_backtest_summary.csv · dates/counts: tables/recursive_12_week_backtest_predictions.csv")
            for model in summary.Model:
                score = summary.loc[summary.Model.eq(model), "WAPE (%)"].iloc[0]
                st.write(f"Historical 12-week {model}: **{score:.2f}% WAPE** on the pooled eligible backtest sample.")
            st.caption("Warehouse-specific accuracy varies substantially. Whse_J was excluded because 52 consecutive pre-origin observations were unavailable; this does not remove its saved forecasts from the four-warehouse future archive.")
            data_download(warehouses, "future_context_historical_warehouse_backtest")
            data_download(summary, "future_context_historical_backtest")
        except (DataIssue, OSError, ValueError, KeyError) as exc:
            st.warning(f"Historical reliability evidence unavailable: {exc}. Archived forecast totals above do not supply missing accuracy information.")
        st.caption("Recursive errors can propagate or persist over multiple steps. A favorable pooled historical score does not establish reliable forecasts for every warehouse or origin. The historical backtest is retrospective, not independent post-selection validation. See Model Validation for the full evidence; complete 2017 warehouse-week outcomes are unavailable (53 sparse raw January records exist).")


def render_future():
    directory = source_directory()
    st.warning("These are historical forward-looking projections originating on December 25, 2016—not current forecasts. Complete 2017 warehouse-week outcomes are unavailable (the raw source has only 53 sparse January records), so no forecast accuracy is calculated for the projected period.")
    try:
        archive = load_archive(directory)
    except (DataIssue, OSError, ValueError, KeyError) as exc:
        st.warning(f"Future forecasting data unavailable: {exc}")
        st.caption("Forecast totals are withheld until origin, dates, complete warehouse coverage and exported summaries pass validation. No missing projections are filled.")
        return
    weekly, checks = archive["weekly"], archive["checks"]
    time_area, location_area, view_area = st.columns([1, 1.5, 1], gap="medium")
    with time_area:
        horizon = choice("Forecast horizon (weeks)", HORIZONS, index=2, horizontal=True, key="future_horizon", persist_state="session")
    with location_area:
        with filters('Options', 'future_forecasting_outlook_warehouses'):
            selected = st.multiselect("Forecast warehouses", WAREHOUSES, default=WAREHOUSES, key="future_selected", persist_state="session")
    with view_area:
        view = choice("Projection view", ["Weekly", "Cumulative"], horizontal=True, key="future_view", persist_state="session")
    if not selected:
        st.info("Select at least one warehouse to view archived projections.")
        return
    detail, combined = forecast_views(weekly, selected, horizon)
    summaries = warehouse_summaries(weekly, selected)
    totals = combined_summaries(weekly, selected)
    current = summaries.loc[summaries.Horizon_Weeks.eq(horizon)]
    selected_total = totals.loc[totals.Horizon_Weeks.eq(horizon)].iloc[0]
    a, b, c, d = st.columns(4)
    for column, window in zip([a, b, c], HORIZONS):
        total = totals.loc[totals.Horizon_Weeks.eq(window)].iloc[0]
        column.metric(f"Projected total · {window} weeks", compact_units(total.Projected_Total_Demand))
        column.caption("Selected warehouses · cumulative window")
    d.metric("Selected forecast coverage", f"{len(detail)} records")
    d.caption(f"{len(selected)} warehouse(s) × {horizon} weeks · {combined.Week.min():%d %b} – {combined.Week.max():%d %b %Y}")
    st.caption("Forecast quantities are summed from validated Predicted_Demand records; they are not observed order demand.")

    with st.container(key="wiq_hero_row"):
        projection_panel, contribution_panel = st.columns([1.7, 1], gap="medium")
    with projection_panel, panel("outlook_projection", "Archived demand outlook", "Weekly or cumulative saved projections · selected warehouses"):
        with chart_options("future_projection_chart"):
            show_combined = st.checkbox("Show selected warehouses combined", value=True, key="future_combined", persist_state="session")
        value = "Predicted_Demand" if view == "Weekly" else "Cumulative_Projected_Demand"
        figure = px.line(detail, x="Week", y=value, color="Warehouse", markers=True, color_discrete_map=PALETTE,
                         labels={value: "Projected weekly demand (units)" if view == "Weekly" else "Projected cumulative demand (units)", "Week": "Archived projected weekly date"})
        if show_combined:
            figure.add_trace(go.Scatter(x=combined.Week, y=combined[value], mode="lines+markers",
                                       name="Selected total", line=dict(color="#172b4d", width=3, dash="dot")))
        figure.update_layout(hovermode="x unified")
        figure.update_traces(hovertemplate="%{y:,.2f} projected units<extra>%{fullData.name}</extra>")
        comparison_chart(figure, "future_projection_chart", height=330)
        st.caption("All lines are archived predictions. Cumulative values sum projected weeks 1 through each displayed horizon week; no observation or missing forecast is added. The combined line is calculated only after aligned coverage is verified.")
        source_detail("Source: " + WEEKLY_SOURCE)
        data_download(detail, "future_selected_weekly_and_cumulative")
        data_download(combined, "future_selected_combined_projection")

    with contribution_panel, panel("outlook_contribution", "Warehouse contributions", "Share of selected projected volume · same horizon"):
        figure = px.bar(current, x="Warehouse", y="Projected_Total_Demand", color="Warehouse", color_discrete_map=PALETTE,
                        custom_data=["Contribution_Pct"], labels={"Projected_Total_Demand": f"Projected volume over {horizon} weeks (units)"})
        figure.update_traces(hovertemplate="%{x}<br>%{y:,.2f} projected units<br>%{customdata[0]:.2f}% of selected volume<extra></extra>")
        figure.update_layout(showlegend=False)
        comparison_chart(figure, "future_warehouse_contributions", height=250)
        with data_section("Contribution table & download", 'Full Data Tables'):
            st.dataframe(readable_table(current), width="stretch", hide_index=True,
                         column_config={"Contribution_Pct": st.column_config.NumberColumn("Selected volume contribution (%)", format="%.2f")})
        st.caption("Contributions use the selected warehouses and the same horizon as the denominator. They are forecast magnitudes, not actual demand shares, warehouse capacity utilization or risk classifications. Shares are undefined if total projected volume is zero.")
        if current.Projected_Total_Demand.sum() > 0:
            largest = current.loc[current.Projected_Total_Demand.idxmax()]
            st.write(f"**{largest.Warehouse}** contributes **{largest.Contribution_Pct:.1f}%** of selected projected volume over {horizon} weeks. The weekly chart shows how those archived projections vary across the horizon; it does not establish a cause or an operating requirement.")
        data_download(current, "future_selected_warehouse_comparison")

    insights([
        ("Selected outlook", f"{compact_units(selected_total.Projected_Total_Demand)} over {horizon} weeks", f"Projected weekly mean: {compact_units(selected_total.Average_Weekly_Demand)} units."),
        ("Combined peak", f"{compact_units(selected_total.Peak_Weekly_Demand)} projected units", "Maximum of aligned weekly sums; individual warehouse peaks are not added."),
        ("Important caveat", "Archived projection, not live forecast", "Origin 25 Dec 2016. No complete 2017 evaluation outcomes, forecast accuracy or valid future bounds."),
    ])
    windows_tab, reliability_tab = st.tabs(["Planning windows & downloads", "Reliability & archive checks"])
    with windows_tab:
        st.subheader("How does the total change across planning windows?")
        st.caption("These tables always show all three windows for the selected warehouses, independently of the chart's horizon filter. A 12-week total already includes weeks 1–4 and 1–8; do not add the three window totals together.")
        with data_section("Compare detailed 4-, 8- and 12-week totals", 'Methodology'):
            st.dataframe(readable_table(totals), width="stretch", hide_index=True)
        st.caption("Combined peak weekly demand is calculated from the sum of projections on each shared date, then maximized. Exported warehouse-level peaks are not added together.")
        data_download(summaries, "future_all_windows_warehouse_summaries")
        data_download(totals, "future_all_windows_combined_summaries")
        source_detail("Records: " + WEEKLY_SOURCE + " · summary cross-check: " + SUMMARY_SOURCE)

    with reliability_tab:
        st.info("Forecast uncertainty: no valid lower/upper forecast bounds are exported for these future weeks. Historical_P90 is a historical demand reference, not a confidence interval or physical capacity. No forecast bands or uncertainty estimates are invented.")
        reliability_context(directory)
        with data_section("Archive integrity, sources & missing metadata", 'Data Sources'):
            st.info(f"Verified origin: {weekly.Forecast_Origin.iloc[0]:%d %B %Y} · projected weeks: {weekly.Week.min():%d %b %Y} – {weekly.Week.max():%d %b %Y} · {len(weekly)} records · {weekly.Warehouse.nunique()} warehouses × 12 aligned forecast weeks. Coverage is complete for the exported four-warehouse archive.")
            st.caption(f"All four warehouses have exactly one record at each of horizons 1–12 and dates match origin + 7 × horizon days. All 12 exported warehouse/window rows were reconciled across total, mean and peak: {len(checks)} numeric checks, absolute tolerance {TOLERANCE_UNITS:g} demand units.")
            st.write(f"Maximum absolute summary discrepancy: **{checks.Absolute_Difference.max():.12g} units**.")
            data_download(checks, "future_forecast_summary_reconciliation")
            st.markdown("""- Primary sources: `future_warehouse_weekly_forecasts.csv` and `future_4_8_12_week_summary.csv`.
    - `future_operational_decision_summary.csv` was inspected; operational risk and planning recommendations are left for Operational Insights. Its recent-history summaries are not displayed as reconstructed historical observations.
    - No complete 2017 warehouse-week actuals or valid forecast bounds are supplied; the raw source contains only 53 sparse January records. There is no actual-demand overlay and no projected-period WAPE/MAE/RMSE.
    - Forecast model identity, model configuration and fitting details are not encoded in the future CSV; the source README describes a recursive historical exercise.
    - Forecast quantities are projected order demand, not confirmed shipments, staffing, physical capacity or verified financial outcomes.
    - Original files are read only. No model is retrained, no new projections are generated and no incomplete coverage is extrapolated.""")
        st.caption("ARCHIVED FUTURE FORECASTING · 25 DEC 2016 ORIGIN · PREDICTIONS, OBSERVATIONS AND BACKTEST RESULTS REMAIN DISTINCT")
