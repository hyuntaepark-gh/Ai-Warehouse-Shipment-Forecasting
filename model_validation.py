"""Validation evidence and its limits; no leaderboards, fitting or inferred intervals."""
from ui_controls import choice
from product_layout import mini_cards, insights, panel, boundary
import calendar

import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from chart_access import chart_header, chart_options, chart_view, data_section, filters, download_frame, source_detail

from comparison_data import aggregate_predictions
from data_loading import DataIssue, source_directory
from display_formatting import readable_table
from model_comparison import comparison_chart
from design_system import finding
from overview import COLORS, data_download
from validation_data import (METRICS, MODELS, SECTIONS, calibration_percentages, evidence,
                             temporal_evidence, yearly_evidence)

RETRO = "Retrospective 2014–2015"
HOLDOUT = "2016 holdout reference"
POOLED = "Pooled 2014–2015"


def source(name):
    source_detail(f"Source: tables/{name}.csv")


def show_table(name, frame):
    download_frame(frame,name,key="validation_download_"+name,label="Download evidence CSV",
                   sources=(f"tables/{name}.csv",))



def models_filter(options=MODELS, key="validation_models"):
    return st.multiselect("Evidence models", list(options), default=list(options), key=key, persist_state="session")


def historical_panel(directory):
    hero_slot = st.container()
    with chart_options('validation_backtest'):
        # Put the two primary decisions first; hide secondary filters until needed.
        primary, measure = st.columns([1.7, 1.0], gap="medium")
        with primary:
            cohort = choice("Backtesting evaluation", [RETRO, HOLDOUT], horizontal=True, persist_state="session", key="bi_model_validation_backtesting_evaluation")
        with measure:
            metric = choice("Backtest metric", METRICS, horizontal=True, persist_state="session", key="bi_model_validation_backtest_metric")
        allowed = [2014, 2015] if cohort == RETRO else [2016]
        with st.container():
            year_area, model_area = st.columns(2, gap="medium")
            with year_area:
                years = st.multiselect("Backtest years", allowed, default=allowed, persist_state="session", key=f"validation_backtest_years_{cohort}")
            with model_area:
                models = models_filter()
    frame = yearly_evidence(directory, cohort, years, models)
    if frame.empty:
        st.info("Select at least one available year and model.")
        return
    dated = aggregate_predictions(directory, years)
    date_rows = dated.assign(Year=dated.Date.dt.year).groupby("Year", as_index=False).agg(
        First_Observation=("Date", "min"), Last_Observation=("Date", "max"), Observed_Weeks=("Date", "nunique"))
    st.caption("Aggregate weekly order demand · 52-week year-ahead forecasts at separate origins. Training history and forecast-week counts are reported in the table.")
    if cohort == RETRO:
        st.warning("2014 and 2015 are retrospective diagnostics and ETS model-selection folds. ETS configuration was selected on these same years; this is not independent validation.")
    else:
        st.warning("2016 is a separate final holdout reference. It was subsequently revisited for exploratory comparisons and framework selection; these results are not independent post-selection validation.")
    plot = frame.assign(Year_Label=frame.Year.astype(int).astype(str))
    figure = px.scatter(plot, x="Year_Label", y=metric, color="Model", symbol="Model", color_discrete_map=COLORS,
                        hover_data=["Evaluation", "Train_Weeks", "Forecast_Weeks"], labels={"Year_Label": "Evaluation year"})
    figure.update_traces(marker_size=12)
    with hero_slot:
        st.caption(f"{cohort} · {metric} · separate annual forecast origins")
        comparison_chart(figure, "validation_backtest", height=320)
    st.caption("Reported errors by year, not a ranking. A different information set was available at each origin. MAE/RMSE are demand units; WAPE is an error percentage.")
    show_table("timesfm_historical_yearly_results", frame)
    with data_section("Observed calendar coverage", 'Full Data Tables'):
        st.dataframe(date_rows, hide_index=True, width="stretch")
    source("timesfm_historical_weekly_predictions")


def temporal_panel(directory):
    scope_area, time_area, metric_area = st.columns([1.5, 1.1, 1.1], gap="medium")
    with scope_area:
        cohort = st.selectbox("Temporal evaluation", [RETRO, POOLED, HOLDOUT], persist_state="session", key="bi_model_validation_temporal_evaluation")
    with time_area:
        grain = choice("Temporal resolution", ["Quarterly", "Monthly"], horizontal=True, persist_state="session", key="bi_model_validation_temporal_resolution")
    with metric_area:
        metric = choice("Temporal error metric", METRICS, horizontal=True, persist_state="session", key="bi_model_validation_temporal_error_metric")
    periods = ["Q1", "Q2", "Q3", "Q4"] if grain == "Quarterly" else list(calendar.month_abbr)[1:]
    with filters('Options', 'model_validation_temporal_secondary'):
        years = [] if cohort == POOLED else st.multiselect("Temporal years", [2016] if cohort == HOLDOUT else [2014, 2015],
                                                          default=[2016] if cohort == HOLDOUT else [2014, 2015], persist_state="session", key=f"validation_temporal_years_{cohort}")
        models = models_filter(key="validation_temporal_models")
        selected_periods = st.multiselect("Calendar periods", periods, default=periods, key=f"validation_periods_{grain}", persist_state="session")
    name, frame = temporal_evidence(directory, grain, cohort, years, models, selected_periods)
    if frame.empty:
        st.info("Select at least one available year, model and period.")
        return
    st.warning("2014–2015 are retrospective and post-selection for ETS. The 2016 reference stays separate. Calendar subsets are descriptive diagnostics, not independent validation samples.")
    st.caption("Pooled WAPE is total weekly absolute error / total actual demand across the selected historical folds, not a simple average of percentage errors. Each displayed pooled period comes directly from its exported pooled row; filtering periods does not recompute or average those rows.")
    frame = frame.assign(Display_Sample=frame.Model + " · " + frame.Sample)
    pivot = frame.pivot(index="Display_Sample", columns="Period", values=metric).reindex(columns=[p for p in periods if p in selected_periods])
    counts = frame.pivot(index="Display_Sample", columns="Period", values="Weeks").reindex(index=pivot.index, columns=pivot.columns)
    figure = go.Figure(go.Heatmap(x=pivot.columns, y=pivot.index, z=pivot.to_numpy(), customdata=counts.to_numpy(),
                                 colorscale="Teal", hoverongaps=False, colorbar=dict(title=metric),
                                 hovertemplate="%{y} · %{x}<br>Error: %{z:,.4f}<br>%{customdata} observed weeks<extra></extra>"))
    comparison_chart(figure, "validation_temporal_heatmap", height=max(350, len(pivot) * 55))
    figure = px.line(frame, x="Period", y=metric, color="Model", line_dash="Sample", markers=True,
                     color_discrete_map=COLORS, category_orders={"Period": periods}, hover_data=["Weeks"])
    comparison_chart(figure, "validation_temporal_trend")
    st.caption("Month-level analyses group the existing weekly timestamps; no monthly model was separately trained. Entire weekly values are assigned to their timestamp's month. These are not exact daily calendar-month transaction totals. Weekly WAPE differs from Month_Total_APE (%), where opposing weekly errors can cancel when totals are summed.")
    show_table(name, frame.drop(columns=["Display_Sample"]))
    with data_section("Full retrospective stability summary · independent of period filters", 'Methodology'):
        summary_name = f"timesfm_{'quarterly' if grain == 'Quarterly' else 'monthly'}_stability_summary"
        summary = evidence(directory, summary_name)
        summary = summary.loc[summary.Model.isin(models)]
        st.caption("Exported min/max/range describe all pooled 2014–2015 calendar periods, even if the chart shows 2016 or a filtered subset. WAPE ranges are percentage points. Winner counts are descriptive counts, not significance tests.")
        show_table(summary_name, summary)


def external_panel(directory):
    frame = evidence(directory, "m5_external_validation")
    models = models_filter(frame.Model.unique(), "validation_external_models")
    frame = frame.loc[frame.Model.isin(models)]
    metric = choice("M5 reported metric", METRICS, horizontal=True, persist_state="session", key="bi_model_validation_m5_reported_metric")
    st.warning("External dataset · exact evaluation dates, forecast horizon and subset specification are not exported. The two reported model results are displayed as one source experiment, without asserting fully verified cohort metadata or adding ranks.")
    st.write("M5 is a separate retail-sales dataset; the primary Historical Product Demand data records warehouse order demand. The capstone references M5 sales, calendar and sell-price files. Different targets, scales and settings prevent direct comparison of their error magnitudes with primary-dataset scores.")
    if frame.empty:
        st.info("Select at least one M5 model.")
        return
    figure = px.bar(frame, x="Model", y=metric, color="Model", color_discrete_map=COLORS)
    figure.update_layout(showlegend=False)
    comparison_chart(figure, "validation_external")
    show_table("m5_external_validation", frame)
    st.caption("One external experiment provides limited transfer evidence, not broad proof of generalizability. No M5 predictions or further datasets are reconstructed.")


def robustness_panel(directory):
    mode = st.selectbox("Robustness experiment", ["Training data quality", "Input and target perturbations", "Random-seed stability"], persist_state="session", key="bi_model_validation_robustness_experiment")
    metric = choice("Robustness reported metric", METRICS, horizontal=True, persist_state="session", key="bi_model_validation_robustness_reported_metric")
    st.warning("Supplementary exploratory experiments · exact evaluation dates, horizon and full protocol are unverified in these exports. Simulated perturbations are not observed operational disruptions. Do not compare these scores directly with annual or recursive cohorts.")
    if mode == "Random-seed stability":
        name = "random_seed_stability"
        raw = evidence(directory, name)
        models = models_filter(raw.Model.unique(), "validation_seed_models")
        frame = raw.loc[raw.Model.isin(models)].copy()
        if frame.empty:
            st.info("Select at least one seed-stability model.")
            return
        plot = frame.assign(Seed_Label=frame.Random_Seed.astype(int).astype(str))
        figure = px.scatter(plot, x="Seed_Label", y=metric, color="Model", color_discrete_map=COLORS,
                            labels={"Seed_Label": "Random seed (categorical experiment label)"})
        figure.update_traces(marker_size=11)
        comparison_chart(figure, "validation_seeds")
        st.caption("These points describe sensitivity to exported seed choices. Seed labels are not a time axis; stability across these runs does not establish temporal robustness or generalization.")
        show_table(name, frame)
        summary_name = "random_seed_stability_summary"
        summary = evidence(directory, summary_name)
        show_table(summary_name, summary.loc[summary.Model.isin(models)])
    else:
        name = "data_quality_impact" if mode == "Training data quality" else "data_disruption_robustness"
        raw = evidence(directory, name)
        scenarios = st.multiselect("Experimental scenarios", list(raw.Scenario), default=list(raw.Scenario), key=f"validation_scenarios_{name}", persist_state="session")
        frame = raw.loc[raw.Scenario.isin(scenarios)]
        if frame.empty:
            st.info("Select at least one experimental scenario.")
            return
        figure = px.bar(frame, x=metric, y="Scenario", orientation="h", color_discrete_sequence=["#087f8c"])
        figure.update_yaxes(autorange="reversed")
        comparison_chart(figure, "validation_perturbations", height=430)
        st.caption("Scenarios retain source order, not a performance ranking. Exported WAPE_Change_pp is the difference from that experiment's clean baseline, in percentage points. Model identity is not a column in these scenario exports; no identity is inferred from matching scores.")
        show_table(name, frame)


def uncertainty_panel(directory):
    mode = st.selectbox("Reliability diagnostic", ["Empirical calibration", "Quantile diagnostics", "Warehouse bias"], persist_state="session", key="bi_model_validation_reliability_diagnostic")
    st.info("Point forecast accuracy measures error magnitude. Uncertainty reliability asks whether intervals cover outcomes at their intended rate; interval width describes sharpness. Good point accuracy alone does not establish reliable uncertainty, and wide intervals can raise coverage.")
    if mode == "Empirical calibration":
        name = "forecast_calibration"
        frame = calibration_percentages(evidence(directory, name))
        st.warning("Empirical interval summaries · model identity, exact evaluation dates and horizon are not specified in this calibration export. No row-level interval bounds are available, so no prediction bands are reconstructed.")
        figure = go.Figure()
        figure.add_trace(go.Scatter(x=frame.Target_Coverage, y=frame.Observed_Coverage_Pct, mode="lines+markers", name="Reported empirical coverage", line_color="#087f8c"))
        figure.add_trace(go.Scatter(x=[0, 100], y=[0, 100], mode="lines", name="Ideal calibration reference", line=dict(color="#8290a5", dash="dash")))
        figure.update_layout(xaxis_title="Target coverage (%)", yaxis_title="Observed coverage (%)")
        comparison_chart(figure, "validation_calibration")
        figure = px.scatter(frame, x="Target_Coverage", y="Average_Width", size="Observations",
                            labels={"Target_Coverage": "Target coverage (%)", "Average_Width": "Average interval width (demand units)"}, color_discrete_sequence=["#087f8c"])
        comparison_chart(figure, "validation_width")
        st.caption("Observed_Coverage is already a percentage and is checked against Covered / Observations × 100. Observed_Coverage_Pct retains that scale without another multiplication. Counts and average widths remain as exported.")
        show_table(name, frame)
        with data_section("Additional exported uncertainty summary", 'Methodology'):
            show_table("week7_uncertainty", evidence(directory, "week7_uncertainty"))
            st.caption("Exact dates and model metadata are not encoded in this summary; no missing interval endpoints are inferred.")
    elif mode == "Quantile diagnostics":
        st.warning("Exact dates, horizon and the quantile method's intended target coverage are not exported. These summaries do not establish interval calibration on an independent sample.")
        frame = evidence(directory, "quantile_comparison")
        figure = px.scatter(frame, x="Average_Width", y="Coverage (%)", color="Method", symbol="Method",
                            labels={"Average_Width": "Reported average width (demand units)"})
        figure.update_traces(marker_size=13)
        comparison_chart(figure, "validation_quantile_methods")
        show_table("quantile_comparison", frame)
        warehouses = evidence(directory, "quantile_warehouse_results")
        chosen = st.multiselect("Quantile warehouses", list(warehouses.Warehouse), default=list(warehouses.Warehouse), persist_state="session", key="bi_model_validation_quantile_warehouses")
        show_table("quantile_warehouse_results", warehouses.loc[warehouses.Warehouse.isin(chosen)])
        st.caption("Coverage (%) and width are reported separately; no missing target rate or interval bounds are synthesized.")
    else:
        summary = evidence(directory, "forecast_bias_summary")
        warehouse = st.selectbox("Bias warehouse", sorted(summary.Warehouse.unique()), persist_state="session", key="bi_model_validation_bias_warehouse")
        frame = summary.loc[summary.Warehouse.eq(warehouse)]
        st.caption("2016 warehouse diagnostic · A/C/S: 52 observations; J: 51. Bias export has no explicit model-identity column. Signed-error convention is not defined in the CSV; signed values are shown without assigning their sign an under/overforecast direction.")
        show_table("forecast_bias_summary", frame)
        quarterly = evidence(directory, "forecast_bias_quarterly")
        quarterly = quarterly.loc[quarterly.Warehouse.eq(warehouse)]
        metric = choice("Bias diagnostic measure", ["Mean_Signed_Error", "Underforecast_Rate_Pct"], horizontal=True, persist_state="session", key="bi_model_validation_bias_diagnostic_measure")
        figure = px.line(quarterly, x="Quarter", y=metric, markers=True, color_discrete_sequence=["#087f8c"])
        comparison_chart(figure, "validation_bias")
        show_table("forecast_bias_quarterly", quarterly)
        st.caption("The exported underforecast rate and longest streak describe a historical sample. Bias can cancel across observations; small mean signed error is not proof of small absolute errors. These are not warehouse capacity or staffing estimates.")


def diagnostics_panel(directory):
    mode = st.selectbox("Audit diagnostic", ["Statistical evidence", "Leakage audit", "Historical monitoring"], persist_state="session", key="bi_model_validation_audit_diagnostic")
    if mode == "Statistical evidence":
        frame = evidence(directory, "forecast_significance_test")
        st.caption("RF − XGBoost · exported 51-week comparison. Exact test dates and target level are not encoded in this significance export; no dates are inferred from another 51-week table. No additional hypothesis test is run.")
        show_table("forecast_significance_test", frame)
        st.warning("The export labels a HAC_p_value, mean loss difference and 95% confidence interval. It does not provide a test-statistic value, named test, loss definition, null specification or HAC bandwidth/lag setting. Those details remain unverified; this page does not invent them.")
        st.write("The reported 95% confidence interval includes zero. This does not establish a clear performance difference on that sample. A non-significant result is not proof that model performance is equal, and it does not validate future generalization.")
    elif mode == "Leakage audit":
        frame = evidence(directory, "data_leakage_audit")
        statuses = st.multiselect("Reported audit statuses", sorted(frame.Status.unique()), default=sorted(frame.Status.unique()), persist_state="session", key="bi_model_validation_reported_audit_statuses")
        selected = frame.loc[frame.Status.isin(statuses)]
        st.metric("Reported PASS checks", int(selected.Status.eq("PASS").sum()))
        show_table("data_leakage_audit", selected)
        st.warning("These are exported audit assertions, not checks re-executed by this dashboard. Details are blank in the export, so pass criteria, underlying code and supporting evidence cannot be independently verified here.")
        st.caption("The named checks concern train/test separation, historical lag alignment, past-only rolling means and feature/category eligibility. They do not eliminate the documented post-selection or repeated-holdout limitations.")
    else:
        frame = evidence(directory, "model_monitoring_2016")
        quarter = st.selectbox("Monitoring quarter", ["All available 2016"] + sorted(frame.Week.dt.to_period("Q").astype(str).unique()), persist_state="session", key="bi_model_validation_monitoring_quarter")
        selected = frame if quarter == "All available 2016" else frame.loc[frame.Week.dt.to_period("Q").astype(str).eq(quarter)]
        st.caption(f"Historical aggregate monitoring · {frame.Week.min():%d %b %Y} – {frame.Week.max():%d %b %Y} · {len(frame)} weekly rows · model identity, rolling-window length and flag thresholds are not encoded in this file.")
        figure = go.Figure(go.Scatter(x=selected.Week, y=selected.Rolling_WAPE_Pct, mode="lines", name="Exported rolling WAPE", connectgaps=False, line_color="#087f8c"))
        for column, label, color in [("Warning", "Exported warning", "#d89129"), ("Persistent_Warning", "Exported persistent warning", "#a85272")]:
            flagged = selected.loc[selected[column]]
            figure.add_trace(go.Scatter(x=flagged.Week, y=flagged.Rolling_WAPE_Pct, mode="markers", name=label, marker=dict(color=color, size=10)))
        figure.update_layout(xaxis_title="Recorded weekly date", yaxis_title="Rolling WAPE (%)")
        comparison_chart(figure, "validation_monitoring")
        st.caption("Initial missing rolling-WAPE values remain missing, not zero. Flags are historical exported diagnostics, not live alerts or verified operational disruptions. No warning threshold or rolling-window length is reverse-engineered.")
        show_table("model_monitoring_2016", selected)


def recursive_panel(directory):
    summary = evidence(directory, "recursive_12_week_backtest_summary")
    summary = summary.loc[summary.Horizon_Weeks.eq(12)]
    warehouses = evidence(directory, "recursive_12_week_warehouse_results")
    pred = evidence(directory, "recursive_12_week_backtest_predictions")
    models = models_filter(summary.Model.unique(), "validation_recursive_models")
    chosen = st.multiselect("Recursive validation warehouses", sorted(warehouses.Warehouse.unique()), default=sorted(warehouses.Warehouse.unique()), persist_state="session", key="bi_model_validation_recursive_validation_warehouses")
    metric = choice("Recursive validation metric", METRICS, horizontal=True, persist_state="session", key="bi_model_validation_recursive_validation_metric")
    st.caption(f"Fixed-origin recursive diagnostic · origin at end of 2015 (exact date not exported) · {pred.Week.min():%d %b %Y} – {pred.Week.max():%d %b %Y} · 12 weeks · {len(pred)} observed warehouse-weeks")
    st.warning("Whse_J was excluded because the required 52 consecutive historical observations were unavailable before the origin. This retrospective recursive procedure is separate from rolling and aggregate year-ahead evaluations. It does not directly validate archived 2017 forecasts; complete observed warehouse-week outcomes are unavailable (53 sparse January records exist in the raw source).")
    pooled = summary.loc[summary.Model.isin(models)]
    filtered = warehouses.loc[warehouses.Model.isin(models) & warehouses.Warehouse.isin(chosen)]
    if not models:
        st.info("Select at least one recursive model.")
        return
    st.markdown("#### Pooled eligible sample · unchanged by warehouse filter")
    show_table("recursive_12_week_backtest_summary", pooled)
    st.caption("The pooled 12-week scores retain all three eligible warehouses. The filter below displays individual-warehouse evidence and does not manufacture new pooled scores.")
    if filtered.empty:
        st.info("Select at least one eligible warehouse to view warehouse differences.")
    else:
        figure = px.bar(filtered, x="Warehouse", y=metric, color="Model", barmode="group", color_discrete_map=COLORS)
        comparison_chart(figure, "validation_recursive")
        show_table("recursive_12_week_warehouse_results", filtered)
    st.caption("Warehouse-specific performance varies; aggregate improvement does not imply an improvement for every warehouse. Individual-warehouse 4/8-week summary scores are not exported, so they are not fabricated. No ranking is combined across evaluation designs.")
    with data_section("Underlying 12-week observed/predicted rows", 'Full Data Tables'):
        show_table("recursive_12_week_backtest_predictions", pred.loc[pred.Warehouse.isin(chosen)])


EVIDENCE_GROUPS = ["Backtesting", "Stability", "External validation", "Uncertainty & bias", "Diagnostics"]
EVIDENCE_CATEGORY = dict(zip(SECTIONS, ["Backtesting", "Stability", "External validation", "Stability", "Uncertainty & bias", "Diagnostics", "Backtesting"]))
DEFAULT_SECTION = {name: next(section for section in SECTIONS if EVIDENCE_CATEGORY[section] == name) for name in EVIDENCE_GROUPS}


def _sync_evidence_tab():
    st.session_state["validation_tabs"] = EVIDENCE_CATEGORY[st.session_state["validation_section"]]


def _sync_evidence_section():
    group = st.session_state["validation_tabs"]
    if EVIDENCE_CATEGORY.get(st.session_state.get("validation_section")) != group:
        st.session_state["validation_section"] = DEFAULT_SECTION[group]


def render_validation():
    directory = source_directory()
    try:
        annual = evidence(directory, "timesfm_historical_yearly_results")
        external = evidence(directory, "m5_external_validation")
        mini_cards([
            ("Annual model-year results", len(annual), "Reported results, not independent experiments"),
            ("Historical annual origins", annual.Year.nunique(), "2014 / 2015 / 2016 · kept separate"),
            ("Validation areas", len(SECTIONS), "Historical, external & supplementary evidence"),
            ("External dataset", "M5", f"{external.Model.nunique()} model summaries · dates unverified"),
        ])
    except (DataIssue, OSError, ValueError, KeyError):
        pass  # The selected panel reports its specific missing-data condition.
    boundary("Exploratory evidence: ETS reused its selection folds, the 2016 holdout was revisited, and supplementary protocols are incomplete. No independent post-selection validation is claimed.")
    current = st.session_state.get("validation_section", SECTIONS[0])
    tabs = st.tabs(EVIDENCE_GROUPS, default=EVIDENCE_CATEGORY[current], key="validation_tabs", on_change=_sync_evidence_section)
    panels = [historical_panel, temporal_panel, external_panel, robustness_panel, uncertainty_panel, diagnostics_panel, recursive_panel]
    for group, tab in zip(EVIDENCE_GROUPS, tabs):
        if tab.open:
            with tab:
                with filters('Options', 'model_validation_evidence_area'):
                    section = st.selectbox("Validation evidence area", SECTIONS, key="validation_section", on_change=_sync_evidence_tab, persist_state="session")
                st.subheader(section)
                try:
                    with panel("reliability_evidence", "Evidence for the selected question", "Only the selected evidence area is rendered; no combined rankings"):
                        panels[SECTIONS.index(section)](directory)
                except (DataIssue, OSError, ValueError, KeyError) as exc:
                    st.warning(f"Model validation data unavailable: {exc}")
    insights([
        ("Key finding", "Evidence has several boundaries", "Annual origins, warehouse tests and recursive forecasts use different information sets."),
        ("Important caveat", "No single confidence score", "Point accuracy does not establish calibrated uncertainty or operational readiness."),
        ("Explore next", "Review stability and external evidence", "Keep missing dates and methods explicit when interpreting supplementary exports."),
    ])
    with data_section("Research limitations & methodology", 'Research Limitations'):
        st.caption("Research outputs only · no models trained, new forecasts generated, intervals fabricated or original capstone files modified. Source CSV downloads retain numeric precision. Missing metadata requires the original notebook and evaluation protocol.")
