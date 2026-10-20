"""Illustrative decision support with explicit boundaries between evidence types."""
import plotly.express as px
import streamlit as st
from chart_access import chart_header, chart_options, chart_view, data_section, filters, download_frame, source_detail
from product_layout import apply_product_theme, chips

from data_loading import DataIssue, source_directory
from display_formatting import compact_units, readable_table
from future_data import HORIZONS, WAREHOUSES, WEEKLY_SOURCE
from model_comparison import comparison_chart
from html import escape
from bi_components import apply_workspace, workspace_header, kpis, panel, chart as product_chart, insight_cards
from operational_charts import comparison_markup, detail_figure, warehouse_name, weekly_heatmap
from operational_data import (PLANNING_SOURCE, load_planning, recent_observed_context,
                              selected_planning, supplementary)
from overview import COLORS, data_download
from validation_data import evidence
from warehouse import PALETTE

VIEWS = ["Archived planning indicators", "Historical bias & monitoring", "Illustrative scenarios & capacity"]
ERRORS = (DataIssue, OSError, ValueError, KeyError)


def table(frame, name, *sources):
    download_frame(frame,name,key="download_operations_"+name,
                   filename="operations_"+name+".csv",sources=sources)



def planning_panel(directory):
    archive = load_planning(directory)
    summary_slot = st.container()
    with st.container(key="ops_filters"):
        left, right = st.columns([2, 1], vertical_alignment="center")
        with left:
            warehouses = st.pills("Planning warehouses", WAREHOUSES, selection_mode="multi", default=WAREHOUSES,
                                  format_func=lambda name: "Warehouse " + name[-1], key="ops_warehouses", persist_state="session")
        with right:
            horizon = st.segmented_control("Planning horizon (weeks)", HORIZONS, default=12,
                                           format_func=lambda h: f"{h} weeks", key="ops_horizon", persist_state="session")
    if not warehouses:
        st.info("Select at least one warehouse for archived planning indicators.")
        return
    if horizon is None:
        st.info("Select a forecast horizon to view the archived planning evidence.")
        return
    weekly, summary = selected_planning(archive, warehouses, horizon)
    above = int(summary.Weeks_Above_Historical_P90.sum())
    watch = summary.loc[summary.Illustrative_Risk_Level.eq("Watch"), "Warehouse"].tolist()
    lead = f"{above} of {len(weekly)} projected warehouse-weeks exceed their historical P90 references."
    if above == 0:
        lead = f"All {len(weekly)} projected warehouse-weeks remain below their historical P90 references."
    labels = " Source ‘Watch’ labels: " + ", ".join(warehouse_name(w) for w in watch) + "." if watch else " No selected warehouse has a source ‘Watch’ horizon label."
    with summary_slot:
        st.markdown(f'<p class="ops-lead"><strong>{escape(lead)}</strong>{escape(labels)}</p>', unsafe_allow_html=True)
        kpis([
            ("Forecast demand", compact_units(weekly.Predicted_Demand.sum()), "Projected units · selected warehouses"),
            ("Weeks above historical P90", str(above), f"Of {len(weekly)} projected warehouse-weeks · not incidents"),
            ("Warehouse coverage", f"{len(warehouses)} / {archive['weekly'].Warehouse.nunique()}", "Selected / verified archive warehouses"),
            ("Forecast horizon", f"{horizon} weeks", f"{weekly.Week.min():%d %b} – {weekly.Week.max():%d %b %Y}"),
        ])
    with st.container(key="ops_primary_row"):
        left, right = st.columns([1, 1.6], gap="medium")
        with left, panel("compare", "Which warehouses are closest to P90?", "Peak projected demand as a share of each warehouse’s historical reference"):
            st.markdown(comparison_markup(summary), unsafe_allow_html=True)
        with right, panel("heatmap", "When is projected demand closest to P90?", "Warehouse × projected week · darker blue = higher demand / P90, not greater risk severity"):
            figure, _ = weekly_heatmap(weekly)
            product_chart(figure, "ops_weekly_heatmap", height=270)
    st.markdown('<p class="ops-boundary">P90 is a historical demand reference, not physical capacity or a forecast interval. Normal / Watch labels are source-reported and illustrative; their rules are undocumented. A Watch label does not mean P90 was exceeded.</p>', unsafe_allow_html=True)
    detail_left, implication_right = st.columns([1.8, 1], gap="medium")
    with detail_left, panel("detail", "Investigate one warehouse", "Compare the saved weekly projection with its historical P90 reference"):
        selected = st.selectbox("Warehouse detail", warehouses, format_func=warehouse_name, key="ops_detail", persist_state="session")
        records = weekly.loc[weekly.Warehouse.eq(selected)]
        row = summary.loc[summary.Warehouse.eq(selected)].iloc[0]
        a, b = st.columns([2.4, 1], gap="large")
        with a:
            product_chart(detail_figure(records), "ops_warehouse_detail", height=300)
        with b:
            st.markdown(f'<div class="ops-fact-grid" style="grid-template-columns:1fr"><div><small>Projected weekly average</small><b>{compact_units(row.Average_Weekly_Demand)} units</b></div><div><small>Historical P90 reference</small><b>{compact_units(records.Historical_P90.iloc[0])} units</b></div><div><small>Source horizon label</small><b>{escape(row.Illustrative_Risk_Level)}</b></div></div>', unsafe_allow_html=True)
    observed = None
    try:
        observed = recent_observed_context(directory, archive["planning"])
        observed = observed.loc[observed.Warehouse.isin(warehouses)]
    except ERRORS as exc:
        st.warning(f"Recent actual reference verification unavailable: {exc}. Recent means remain source summaries, not reconstructed observations.")
    if observed is not None:
        observed_row = observed.loc[observed.Warehouse.eq(selected)].iloc[0]
        observed_title = f"{compact_units(observed_row.Recent_4Week_Mean_Observed)} units per week"
        observed_body = f"{warehouse_name(selected)} averaged this demand across four observed weeks, {observed_row.First_Observed_Week:%d %b}–{observed_row.Last_Observed_Week:%d %b %Y}. This is not a full-year total."
    else:
        observed_title = "Recent reference is unverified"
        observed_body = "The original summary is available, but its recent actual observations could not be checked. No history is filled in."
    with implication_right:
        insight_cards([
            ("Observed fact", observed_title, observed_body),
            ("Archived projection", f"{row.Change_vs_Recent_4Week_Pct:+.1f}% vs recent demand", f"The {horizon}-week projected weekly mean is compared with the exported four-week observed mean. This is a level comparison, not an accuracy score."),
            ("Illustrative implication", "Validate before changing the plan", "If reviewing a similar pattern, check current demand and measured operational constraints first. These exports cannot establish capacity, staffing or financial decisions."),
        ])
    with data_section("Sources, full-precision data & downloads", 'Full Data Tables'):
        st.caption("Forecast: " + WEEKLY_SOURCE + " · planning: " + PLANNING_SOURCE + " · cross-check: tables/future_4_8_12_week_summary.csv")
        table(summary, "selected_planning", PLANNING_SOURCE)
        data_download(weekly, "operations_selected_weekly_risk")
        table(summary[["Warehouse", "Recent_4Week_Mean_Observed", "Average_Weekly_Demand", "Change_vs_Recent_4Week_Pct"]], "observed_reference_comparison", PLANNING_SOURCE)
        if observed is not None:
            table(observed, "recent_actual_reference", "tables/hierarchical_warehouse_forecasts.csv")
        data_download(records, "operations_warehouse_detail")
    with data_section("Methodology, source planning considerations & validation", 'Methodology'):
        st.write("Ratio = archived projected demand / exported Historical_P90. The comparison uses each warehouse’s maximum ratio within the selected horizon. The heatmap shows the individual weekly ratios on a fixed 0–100% color scale. This is not a new risk score, capacity utilization or model performance measure.")
        st.write("The P90 estimation window, quantile method and Normal/Watch classification rules are not provided. No category rule is inferred. Forecasts originate on December 25, 2016; complete 2017 warehouse-week outcomes and future forecast bounds are unavailable (53 sparse raw January records exist).")
        st.write("Change = (projected horizon weekly mean / exported recent four-week observed mean − 1) × 100. No cause is inferred. The actual-demand export has 51 observed weeks per warehouse, Jan 10–Dec 25, 2016; it is not annualized.")
        for record in summary.itertuples():
            st.write(f"**{record.Warehouse} · {record.Illustrative_Risk_Level}** — source illustrative consideration: {record.Planning_Consideration}")
        st.caption(f"Checked 48 weekly ratios, {len(archive['checks'])} operational-summary values and 36 separate forecast-summary values. Categories remain original source labels.")
        data_download(archive["checks"], "operations_summary_checks")


def historical_panel(directory):
    st.info("Historical diagnostics are separate from December 2016-origin projected risk. Exact model identity and evaluation metadata are not encoded in the bias export; no cohort is assigned from matching counts alone.")
    try:
        bias = evidence(directory, "forecast_bias_summary")
        selected = st.multiselect("Bias warehouses", sorted(bias.Warehouse.unique()), default=sorted(bias.Warehouse.unique()), key="ops_bias_warehouses", persist_state="session")
        bias = bias.loc[bias.Warehouse.isin(selected)]
        if bias.empty:
            st.info("Select a warehouse to display historical bias diagnostics.")
        else:
            metric = st.selectbox("Bias diagnostic", ["Bias_Pct", "Underforecast_Rate_Pct", "Longest_Underforecast_Streak"], key="ops_bias_metric", persist_state="session")
            labels = {"Bias_Pct": "Exported signed bias (%)", "Underforecast_Rate_Pct": "Exported underforecast rate (%)", "Longest_Underforecast_Streak": "Exported longest underforecast streak (observations)"}
            figure = px.bar(bias, x="Warehouse", y=metric, color="Warehouse", color_discrete_map=PALETTE, labels=labels)
            figure.update_layout(showlegend=False)
            comparison_chart(figure, "ops_bias_chart", height=340)
            table(bias, "historical_bias", "tables/forecast_bias_summary.csv")
            st.caption("Bias measures signed error; MAE measures absolute error; risk labels describe a separate illustrative planning exercise. The signed-error convention is not defined in this export, so positive/negative bias is not assigned an over/underforecast interpretation. Underforecast rates and streaks are reported as named by the source. No model-specific recommendation follows from unidentified diagnostics.")
            st.write("If underforecasting were an operational concern, review the source-reported rates and streaks alongside actual service and inventory evidence before changing policy. No service failures or inventory shortages are measured here.")
    except ERRORS as exc:
        st.warning(f"Bias evidence unavailable: {exc}")
    st.subheader("Archived 2016 monitoring flags")
    try:
        monitoring = evidence(directory, "model_monitoring_2016")
        st.caption(f"Observed monitoring window: {monitoring.Week.min():%d %b %Y} – {monitoring.Week.max():%d %b %Y} · {len(monitoring)} weekly records · aggregate scope, no warehouse selector")
        a, b = st.columns(2)
        a.metric("Exported warning weeks", str(int(monitoring.Warning.sum())))
        b.metric("Exported persistent warning weeks", str(int(monitoring.Persistent_Warning.sum())))
        figure = px.line(monitoring, x="Week", y="Rolling_WAPE_Pct", markers=True,
                          labels={"Week": "Historical weekly timestamp", "Rolling_WAPE_Pct": "Exported rolling WAPE (%)"},
                          custom_data=["Warning", "Persistent_Warning"])
        figure.update_traces(line_color="#087f8c", connectgaps=False,
            hovertemplate="%{x|%d %b %Y}<br>Rolling WAPE: %{y:.2f}%<br>Warning: %{customdata[0]}<br>Persistent warning: %{customdata[1]}<extra></extra>")
        comparison_chart(figure, "ops_monitoring_chart", height=330)
        flag_only = st.checkbox("Show flagged monitoring rows only", key="ops_flagged", persist_state="session")
        table(monitoring.loc[monitoring.Warning | monitoring.Persistent_Warning] if flag_only else monitoring,
              "historical_monitoring", "tables/model_monitoring_2016.csv")
        st.caption("Flags are archived diagnostics, not live alerts or observed disruptions. The model, rolling-window length, warning threshold and persistence rule are not supplied; none is inferred. Initial missing rolling WAPE values remain missing. Flags and bias summaries are not joined into an evaluation cohort.")
        st.write("If reviewing a flagged historical week, inspect the aligned errors and data quality before attributing a cause. The export does not establish why performance changed.")
    except ERRORS as exc:
        st.warning(f"Monitoring evidence unavailable: {exc}")


def scenarios_panel(directory):
    st.warning("SUPPLEMENTARY ILLUSTRATIVE EXPORTS · Evaluation dates, threshold definitions and full scenario/capacity protocols are unverified. Panels remain separate; they are not evidence of observed disruptions, actual constraints or financial savings.")
    st.subheader("Exported demand scenarios")
    try:
        scenarios = supplementary(directory, "scenario_summary")
        selected = st.multiselect("Exported scenarios", list(scenarios.Scenario), default=list(scenarios.Scenario), key="ops_scenarios", persist_state="session")
        selected_rows = scenarios.loc[scenarios.Scenario.isin(selected)]
        if selected_rows.empty:
            st.info("Select at least one exported scenario.")
        else:
            metric = st.selectbox("Scenario indicator", ["Average_Risk_Ratio", "Maximum_Risk_Ratio", "Threshold_Exceedances"], key="ops_scenario_metric", persist_state="session")
            figure = px.bar(selected_rows, x="Scenario", y=metric, labels={metric: metric.replace("_", " ")})
            figure.update_traces(marker_color="#087f8c")
            comparison_chart(figure, "ops_scenarios_chart", height=330)
            table(selected_rows, "scenarios", "tables/scenario_summary.csv")
        st.caption("Baseline, Demand +10% and Demand +20% are source-defined hypothetical scenarios. Ratios and exceedance counts are displayed as exported; their denominator, threshold, dates and population are unspecified. They cannot be compared to the 48 future archive rows or interpreted as P90 exceedances without further documentation.")
    except ERRORS as exc:
        st.warning(f"Scenario evidence unavailable: {exc}")
    st.subheader("Illustrative planning loss")
    try:
        costs = supplementary(directory, "illustrative_cost_simulation")
        scenario = st.selectbox("Planning-loss scenario", list(costs.Scenario.unique()), key="ops_cost_scenario", persist_state="session")
        costs = costs.loc[costs.Scenario.eq(scenario)]
        figure = px.bar(costs, x="Model", y="Loss_per_1000_Demand_Units", color="Model", color_discrete_map=COLORS,
                        labels={"Loss_per_1000_Demand_Units": "Exported planning-loss units per 1,000 demand units"})
        figure.update_layout(showlegend=False)
        comparison_chart(figure, "ops_loss_chart", height=330)
        table(costs, "illustrative_loss", "tables/illustrative_cost_simulation.csv")
        st.caption("Each scenario reports 207 warehouse-weeks per model. Exact dates, perturbation procedure and loss weights are absent. Values are illustrative planning-loss units, not currency or verified costs. No cross-scenario financial savings or model ranking is calculated.")
    except ERRORS as exc:
        st.warning(f"Planning-loss evidence unavailable: {exc}")
    st.subheader("Illustrative capacity policies")
    try:
        capacity = supplementary(directory, "capacity_optimization")
        table(capacity, "capacity_policies", "tables/capacity_optimization.csv")
        st.caption("Baseline Planning and Optimized Planning are exported illustrative policy names. Average_Planned_Capacity is a modeled planning quantity, not measured physical capacity; Total_Expected_Loss has no documented monetary unit. Dates, objective weights and constraints are not exported. Neither policy is a validated recommendation.")
    except ERRORS as exc:
        st.warning(f"Capacity evidence unavailable: {exc}")
    with data_section("Forecast Value Added · separate supplementary accuracy evidence", 'Methodology'):
        try:
            fva = supplementary(directory, "forecast_value_added")
            level = st.selectbox("FVA evaluation level", list(fva.Evaluation_Level.unique()), key="ops_fva_level", persist_state="session")
            table(fva.loc[fva.Evaluation_Level.eq(level)], "fva", "tables/forecast_value_added.csv")
            st.caption("Reported FVA = (baseline WAPE − model WAPE) / baseline WAPE × 100, checked against each exported Naive baseline. It is relative error reduction, not operational benefit or financial savings. Evaluation dates, horizon and protocol are unverified; warehouse-level and aggregate results remain separate and no leaderboard is created.")
        except ERRORS as exc:
            st.warning(f"FVA evidence unavailable: {exc}")
    st.write("If considering a comparable scenario, use the exported differences as questions to investigate, then validate assumptions against measured warehouse constraints and actual costs before choosing a policy. These simulations alone cannot specify staffing, inventory or service levels.")


def research_boundaries():
    with data_section("Research boundaries & documentation gaps", 'Research Limitations'):
        st.markdown("""- Source documentation: `capstone_final_outputs/README_summary.md`, sections Operational Decision Support and Key Research Limitations. The original notebook is not included; undocumented rules cannot be recovered here.
- Order demand is not confirmed shipment volume. Projected high demand does not automatically establish capacity requirements or operational incidents.
- P90 values are exported historical demand references; the estimation population and risk-category cutoffs are unknown. Source risk labels are not recalculated or assigned traffic-light colors.
- Bias, accuracy, monitoring flags and illustrative risk describe different evidence. Unknown evaluation dates are never borrowed from another CSV; retrospective and post-selection results do not establish prospective reliability.
- No actual 2017 forecast accuracy, new uncertainty bounds, causal explanations, physical constraints or financial savings are inferred.
- `warehouse_characteristics.csv` was inspected but its training-period demand summaries are not displayed as 2016 observations. Historical Demand and Warehouse Analytics provide the observed sample context; Future Forecasting and Model Validation retain detailed projection and reliability analysis.
- Downloads retain full numerical precision. All original exports are read only; no model is retrained.""")


def render_operational():
    apply_workspace()
    apply_product_theme()
    st.markdown('<style>.ops-insight-grid{grid-template-columns:1fr!important;gap:10px!important;}.ops-insight{padding:13px 16px!important;}.ops-insight strong{font-size:15px!important;}.ops-insight p{font-size:12px!important;}.st-key-ops_product [class*="st-key-ops_panel_"]{padding:17px 18px!important;}.st-key-ops_product [class*="st-key-ops_kpi_"]{padding:13px 17px!important;}.st-key-ops_product [data-testid="stMetric"]{padding:0!important;}</style>', unsafe_allow_html=True)
    with st.container(key="ops_product"):
        workspace_header()
        chips("Archived study", "25 Dec 2016 origin", "Illustrative planning")
        st.markdown('<p class="ops-boundary">Historical projections, not live operations. Origin: December 25, 2016. No complete 2017 evaluation outcomes; planning implications are illustrative.</p>', unsafe_allow_html=True)
        view = st.segmented_control("Operational evidence", VIEWS, default=VIEWS[0],
            format_func=lambda v: {VIEWS[0]: "Planning outlook", VIEWS[1]: "Historical", VIEWS[2]: "Scenarios"}[v],
            key="ops_view", label_visibility="collapsed", persist_state="session")
        if view is None:
            st.info("Select an evidence view to continue.")
        else:
            try:
                {VIEWS[0]: planning_panel, VIEWS[1]: historical_panel, VIEWS[2]: scenarios_panel}[view](source_directory())
            except ERRORS as exc:
                st.warning(f"Operational insights data unavailable: {exc}")
                st.caption("Affected indicators are withheld; no missing records, thresholds or categories are substituted. Other evidence views remain accessible.")
        research_boundaries()
