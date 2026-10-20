"""Insight-led Overview pilot; all figures remain scoped to their source cohorts."""
from ui_controls import choice
from product_layout import chips, insights, mini_cards, panel, apply_product_theme
from html import escape
from navigation import navigate, LABELS
import json

import plotly.express as px
import streamlit as st
from chart_access import chart_header, chart_options, chart_view, data_section, filters, download_frame, source_detail

from data_loading import DataIssue, inventory, source_directory
from display_formatting import compact_units, readable_table
from future_data import forecast_views, load_archive, select_records
from overview import data_download, demand_plot, source_note
from overview_data import actual_demand, holdout_kpis, load_overview
from overview_design import (MODEL_COLORS, WAREHOUSE_COLORS, apply_design, error_comparison,
                             insight, kpi_cards, show_chart)


open_page = navigate


def observed_trend(data, compact=False):
    if not compact:
        st.subheader("How did demand change through 2016?")
    observed = actual_demand(data["weekly"], 2016)
    if not compact:
        st.caption(f"Observed aggregate order demand · {observed.Date.min():%d %b} – {observed.Date.max():%d %b %Y}")
    with chart_options('holdout_demand'):
        left, right = st.columns([2, 1])
        with left:
            models = st.multiselect("Forecast overlays", sorted(data["weekly"].Model.unique()),
                                     default=[], key="holdout_models", persist_state="session")
        with chart_view("holdout_demand"):
            grain = choice("Demand view", ["Weekly", "Monthly grouped weeks"], horizontal=True, persist_state="session", key="bi_executive_overview_demand_view")
    figure, plotted = demand_plot(data["weekly"], 2016, models, grain != "Weekly")
    for trace in figure.data:
        trace.line.color = MODEL_COLORS.get(trace.name, "#66758c")
        trace.line.width = 3 if trace.name == "Actual" else 2
        trace.line.dash = "solid" if trace.name == "Actual" else "dash"
        if trace.name != "Actual":
            trace.name = "Saved prediction · " + trace.name
    figure.update_layout(hovermode="x unified", showlegend=bool(models))
    figure.update_xaxes(title_text="Month assigned from weekly timestamp" if grain != "Weekly" else "Recorded weekly date")
    quantity = "Sum of weekly demand (units)" if grain != "Weekly" else "Observed / predicted demand (units)" if models else "Observed order demand (units)"
    figure.update_yaxes(title_text=quantity, tickformat=".3s")
    show_chart(figure, "holdout_demand", 245 if compact else 400)
    with data_section("Demand insight, data & sources", 'Full Data Tables'):
        peak = observed.loc[observed.Actual.idxmax()]
        st.write(f"Peak observed weekly demand was **{compact_units(peak.Actual)} units** on **{peak.Date:%d %b %Y}**. The series describes demand variation; the exports do not establish its causes.")
        if grain != "Weekly":
            st.caption("Monthly values sum weekly observations by recorded timestamp. They are not exact calendar-month transaction totals or separately trained monthly forecasts.")
        if models:
            st.caption("Solid line: observed demand. Dashed lines: saved fixed-origin 2016 predictions. Forecasts are not observations or new model runs.")
        source_note("weekly")
        data_download(plotted, "2016_demand_view")


def holdout_comparison(data, kpi, compact=False):
    if not compact:
        st.subheader("Which models had the lowest 2016 forecast error?")
    if not compact:
        st.caption("Same aggregate target · 52-week year-ahead holdout · 03 Jan – 25 Dec 2016")
    with chart_view("holdout_comparison"):
        metric = st.selectbox("Comparison metric", ["WAPE (%)", "MAE", "RMSE"],
            help="WAPE is total absolute error divided by total absolute demand. MAE and RMSE are demand-unit error measures; lower is better.", persist_state="session", key="bi_executive_overview_comparison_metric")
    figure, ranked = error_comparison(data["holdout"], metric)
    show_chart(figure, "holdout_comparison", 275 if compact else 420)
    with data_section("Ranking details, quarterly results & download", 'Methodology'):
        winners = ranked.loc[ranked[metric].eq(ranked[metric].min()), "Model"].tolist()
        st.write(f"**{' / '.join(winners)}** recorded the lowest exported **{metric}** in this cohort. Teal marks the minimum; this descriptive comparison does not establish statistical superiority.")
        st.caption("WAPE is an error percentage, not an accuracy score. MAE and RMSE use demand units. These fixed-origin scores must not be ranked against rolling warehouse or recursive results.")
        source_note("holdout")
        data_download(ranked.drop(columns="Display_Error"), "2016_full_year_comparison")
        with data_section("Quarterly variation within the 2016 holdout", 'Methodology'):
            quarterly = data["quarterly"]
            pivot = quarterly.pivot(index="Model", columns="Quarter", values="WAPE (%)")
            figure = px.imshow(pivot, text_auto=".2f", aspect="auto", color_continuous_scale="Teal", labels={"color": "WAPE (%)"})
            show_chart(figure, "holdout_quarters", 340)
            st.caption("Subsets of the same annual predictions; not independent forecast experiments. A low annual error does not imply the lowest error every quarter.")
            source_note("quarterly")
            data_download(quarterly, "2016_quarterly_results")


def warehouse_summary(data):
    cards = []
    for warehouse, scores in data["warehouse"].groupby("Warehouse", sort=True):
        winners = scores.loc[scores["WAPE (%)"].eq(scores["WAPE (%)"].min())]
        names = " / ".join(winners.Model)
        cards.append(f'<article><span>{escape(warehouse)}</span><strong>{winners["WAPE (%)"].iloc[0]:.2f}%</strong><p>{escape(names)} · lowest rolling WAPE</p><small>{int(scores.Test_Weeks.iloc[0])} test weeks</small></article>')
    st.markdown('<div class="exec-warehouse-grid">' + "".join(cards) + '</div>', unsafe_allow_html=True)
    source_note("warehouse")


def warehouse_highlights(data):
    st.subheader("Does the same approach work for every warehouse?")
    st.write("Local evaluation matters. Compare models within each warehouse; these rolling results answer a different question from the aggregate year-ahead holdout.")
    warehouse = st.selectbox("Warehouse", sorted(data["warehouse"].Warehouse.unique()), persist_state="session", key="bi_executive_overview_warehouse")
    rolling = data["warehouse"].loc[data["warehouse"].Warehouse.eq(warehouse)]
    figure, ranked = error_comparison(rolling, "WAPE (%)")
    show_chart(figure, "warehouse_rolling", 340)
    st.caption("One-step rolling evaluation · A/C/S: 03 Jan–25 Dec 2016 (52 weeks); J: 10 Jan–25 Dec 2016 (51 weeks). No cross-warehouse leaderboard. Exact rolling fitting/update details are not exported.")
    data_download(ranked.drop(columns="Display_Error"), "warehouse_rolling_results")
    with data_section("Separate reliability evidence · historical recursive backtest", 'Methodology'):
        predictions = data["recursive_predictions"]
        st.caption(f"Origin: end of 2015 (exact date unexported) · {predictions.Week.min():%d %b} – {predictions.Week.max():%d %b %Y} · 12 weeks · three eligible warehouses")
        recursive = data["recursive"]
        figure = px.bar(recursive, x="Warehouse", y="WAPE (%)", color="Model", barmode="group", text_auto=".2f", color_discrete_map=MODEL_COLORS)
        show_chart(figure, "warehouse_recursive", 360)
        summary = data["recursive_summary"].loc[data["recursive_summary"].Horizon_Weeks.eq(12)]
        for row in summary.to_dict("records"):
            st.write(f"{row['Model']}: **{row['WAPE (%)']:.2f}% pooled WAPE** on the eligible sample.")
        st.warning("Warehouse outcomes vary substantially. Whse_J was excluded because 52 consecutive pre-origin weeks were unavailable. This is a retrospective diagnostic, not independent post-selection validation or an accuracy score for the archived 2017 forecasts.")
        source_note("recursive", "recursive_predictions", "recursive_summary")
        data_download(recursive, "recursive_warehouse_results")


def research_context(data, directory):
    with data_section("Additional research · retrospective results & archived forecasts", 'Methodology'):
        retro, future = st.tabs(["2014–2015 retrospective", "Archived future outlook"])
        with retro:
            st.subheader("How did performance differ at earlier origins?")
            st.caption("Aggregate year-ahead diagnostics · 2014: 05 Jan–28 Dec · 2015: 04 Jan–27 Dec")
            st.warning("ETS was selected using these same 2014–2015 folds. These post-selection diagnostics are not independent validation; 2016 remains a separate holdout reference.")
            yearly = data["yearly"].loc[data["yearly"].Year.isin([2014, 2015])].copy()
            yearly["Year"] = yearly.Year.astype(str)
            figure = px.bar(yearly, x="Year", y="WAPE (%)", color="Model", barmode="group", text_auto=".2f", color_discrete_map=MODEL_COLORS)
            show_chart(figure, "retrospective_years", 360)
            source_note("yearly")
            pooled = data["pooled"]
            figure, ranked = error_comparison(pooled, "WAPE (%)")
            show_chart(figure, "retrospective_pooled", 340)
            st.caption(f"Pooled retrospective WAPE uses total weekly absolute error / total absolute actual demand over {int(pooled.Weeks.iloc[0])} weeks per model, not a mean of annual percentages.")
            source_note("pooled")
            year = st.selectbox("Retrospective demand year", [2014, 2015], persist_state="session", key="bi_executive_overview_retrospective_demand_year")
            figure, plotted = demand_plot(data["weekly"], year, sorted(data["weekly"].Model.unique()))
            for trace in figure.data:
                trace.line.color = MODEL_COLORS.get(trace.name, "#66758c")
                trace.line.dash = "solid" if trace.name == "Actual" else "dash"
            show_chart(figure, "retrospective_demand", 380)
            st.caption("Actual observations and saved predictions at the selected historical year-ahead origin.")
            source_note("weekly")
            data_download(yearly, "retrospective_yearly_results")
            data_download(ranked.drop(columns="Display_Error"), "retrospective_pooled_results")
            data_download(plotted, "retrospective_demand_view")
        with future:
            st.subheader("What did the archived planning exercise project?")
            st.warning("Archived origin: December 25, 2016. These are not current forecasts. Complete 2017 warehouse-week outcomes and valid forecast intervals are unavailable (53 sparse raw January records exist), so projected-period accuracy cannot be assessed.")
            try:
                archive = load_archive(directory)
                weekly = archive["weekly"]
                st.caption(f"Archived projections · {weekly.Week.min():%d %b} – {weekly.Week.max():%d %b %Y} · complete four-warehouse archive")
                horizon = st.select_slider("Planning horizon (weeks)", options=[4, 8, 12], value=12, persist_state="session", key="bi_executive_overview_planning_horizon_weeks")
                warehouses = st.multiselect("Forecast warehouses", sorted(weekly.Warehouse.unique()), default=sorted(weekly.Warehouse.unique()), persist_state="session", key="bi_executive_overview_forecast_warehouses")
                if warehouses:
                    _, combined = forecast_views(weekly, warehouses, horizon)
                    displayed = select_records(weekly, warehouses, horizon)
                    st.metric("Projected demand · selected warehouses", compact_units(combined.Predicted_Demand.sum()) + " units")
                    figure = px.line(displayed, x="Week", y="Predicted_Demand", color="Warehouse", markers=True,
                        color_discrete_map=WAREHOUSE_COLORS,
                        labels={"Predicted_Demand": "Archived projected demand (units)", "Week": "Projected weekly date"})
                    show_chart(figure, "archived_future", 380)
                else:
                    displayed = weekly.iloc[:0].copy()
                    st.metric("Projected demand · selected warehouses", "—")
                    st.info("Select at least one warehouse to view saved forecasts.")
                planning = data["planning"].loc[data["planning"].Horizon_Weeks.eq(horizon) & data["planning"].Warehouse.isin(warehouses)]
                source_note("future", "planning")
                st.caption("Planning labels are illustrative and their classification rules are undocumented. Historical P90 is a demand reference, not physical capacity or an uncertainty bound. No operating requirement or financial savings is inferred.")
                with data_section("Illustrative planning labels & source considerations", 'Full Data Tables'):
                    st.dataframe(readable_table(planning), hide_index=True, width="stretch")
                data_download(displayed, "archived_future_forecasts")
                data_download(planning, "archived_planning_summary")
            except (DataIssue, OSError, ValueError, KeyError) as exc:
                st.warning(f"Archived outlook unavailable: {exc}. Forecast quantities are withheld until complete coverage is verified.")


def evidence_details(data, directory):
    with data_section("Sources, methods & research limitations", 'Research Limitations'):
        st.write("Demand is recorded order quantity, not confirmed shipments. Physical capacity, headcount, inventory and verified operating costs are unavailable. WAPE is sum of absolute forecast errors / sum of absolute actual demand × 100; lower error does not establish operational benefit.")
        st.write("The 2016 holdout was revisited for exploratory comparisons and framework selection. Retrospective, rolling, recursive and archived future results stay separate. No chart implies independent post-selection validation or future accuracy.")
        st.dataframe(data["conclusions"], hide_index=True, width="stretch")
        st.dataframe(data["limitations"], hide_index=True, width="stretch")
        source_note("conclusions", "limitations")
        with data_section("Source inventory, schemas & evaluation families", 'Data Sources'):
            records = inventory(directory)
            csv_records = [r for r in records if r["type"] == ".csv"]
            st.caption(f"{len(csv_records)} CSV tables · {len(records)} original source files · {sum('error' in r for r in csv_records)} CSV read errors. Undated supplementary evaluations remain unverified.")
            st.dataframe([{"File": r["file"], "Rows": r.get("rows"), "Evaluation family": r["evaluation_context"]["family"], "Period": r["evaluation_context"]["period"], "Read error": r.get("error", "")} for r in csv_records], hide_index=True, width="stretch")
            selected = st.selectbox("Inspect CSV schema", [r["file"] for r in csv_records], persist_state="session", key="bi_executive_overview_inspect_csv_schema")
            if selected:
                st.json(next(r for r in csv_records if r["file"] == selected))
            st.download_button("Download full source inventory", json.dumps(records, indent=2), file_name="source_inventory.json", mime="application/json")


def render_overview():
    apply_design()
    apply_product_theme()
    st.markdown('<style>.exec-summary{padding:0!important;background:none!important;border:0!important;margin:0!important;}.exec-summary strong{font-size:18px!important;}.exec-summary p{font-size:13px!important;margin:3px 0 0!important;}.st-key-executive_pilot [class*="st-key-exec_kpi_"]{padding:13px 16px!important;min-height:0!important;}.st-key-executive_pilot [data-testid="stMetric"]{padding:0!important;min-height:0!important;}.exec-warehouse-grid{margin:0!important;}.exec-warehouse-grid article{padding:12px 15px!important;}.exec-warehouse-grid strong{font-size:23px!important;}.exec-note{margin:0!important;font-size:11px!important;}</style>', unsafe_allow_html=True)
    with st.container(key="executive_pilot"):
        st.markdown('<p class="wiq-eyebrow">Workspace / Research overview</p>', unsafe_allow_html=True)
        st.title("Overview")
        directory = source_directory()
        if not directory.is_dir() or not any(directory.iterdir()):
            st.warning("Capstone data unavailable. The capstone_final_outputs directory is missing or empty.")
            st.caption("Restore the original source folder or set CAPSTONE_DATA_DIR, then refresh.")
            return
        try:
            data = load_overview(directory)
            kpi = holdout_kpis(data)
        except (DataIssue, OSError, ValueError, KeyError) as exc:
            st.error(f"Cannot load Executive Overview: {exc}")
            return
        st.markdown(f'<div class="exec-summary"><strong>{escape(kpi["best_model"])} led the 2016 aggregate comparison with {kpi["best_wape"]:.2f}% WAPE.</strong><p>Warehouse results varied; validate locally before interpreting aggregate gains.</p></div>', unsafe_allow_html=True)
        chips("Archived study", "2016 aggregate holdout", "52 observed weeks", "Order demand · not shipments")
        st.markdown('<p class="exec-note"><strong>Research boundary:</strong> the holdout was revisited; results are exploratory, not independent post-selection validation.</p>', unsafe_allow_html=True)
        kpi_cards([
            ("Lowest holdout WAPE", f"{kpi['best_wape']:.2f}%", f"{kpi['best_model']} · 2016 error"),
            ("Error reduction vs baseline", f"{kpi['relative_reduction']:.1f}%", f"Vs Seasonal Naive · {kpi['baseline_wape']:.2f}% WAPE"),
            ("Observed 2016 demand", compact_units(kpi['demand']), "Observed units · counted once"),
            ("Holdout coverage", f"{kpi['weeks']} weeks", "03 Jan–25 Dec 2016"),
        ])
        with st.container(key="wiq_hero_row"):
            left, right = st.columns([1.2, 1], gap="medium")
            with left, panel("overview_trend", "The demand story", "Observed weekly order demand · 2016"):
                observed_trend(data, compact=True)
            with right, panel("overview_ranking", "The model result", "Same aggregate target · same 52-week holdout"):
                holdout_comparison(data, kpi, compact=True)
        warehouse_summary(data)
        ets = data["holdout"].loc[data["holdout"].Model.eq("ETS"), "WAPE (%)"].iloc[0]
        insights([
            ("Key finding", f"{kpi['relative_reduction']:.1f}% lower WAPE vs baseline", "Relative error reduction against Seasonal Naive in this holdout only."),
            ("Important caveat", f"{abs(ets-kpi['best_wape']):.2f} pp separates TimesFM and ETS", "This descriptive gap alone does not establish statistical superiority."),
            ("Explore next", "Local evidence stays local", "Warehouse rolling scores and archived projections answer different questions."),
        ])
        with st.popover("Explore pages",icon=":material/explore:",key="overview_explore",width="content"), st.container(key="wiq_explore"):
            for routes in [["Historical Demand", "Model Comparison", "Warehouse Analytics"],
                           ["Model Validation", "Future Forecasting", "Operational Insights", "Data Foundation"]]:
                for destination in routes:
                    with st.container():
                        st.button(LABELS[destination] + " →", on_click=open_page, args=(destination,), width="stretch", key="exec_nav_" + destination)
        local, research = st.tabs(["Warehouse evidence", "Earlier origins & archived outlook"])
        with local:
            warehouse_highlights(data)
        with research:
            research_context(data, directory)
        evidence_details(data, directory)
        st.caption("ARCHIVED CAPSTONE · Historical order demand · Full-precision CSV downloads · No models retrained")
