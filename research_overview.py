"""Research landing page for the final M5 and Favorita study."""

from deployment.analytics_access import data_path, selected, table_view

from html import escape
import json

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from chart_access import data_section, source_detail
from data_loading import DataIssue
from navigation import FORECAST_HORIZONS, MODEL_STRATEGIES, NUMERICAL_STABILITY, RESEARCH_VALIDATION, navigate
from product_layout import PLOT_CONFIG, boundary, header, panel, research_unavailable, scope
from research_overview_data import DATASETS, METHODS, OVERVIEW_SOURCES, SOURCE_REGISTRY, ResearchOverviewData, load_research_overview


METHOD_LABELS = {"DirectRidge": "Direct Ridge", "RecursiveRidge": "Recursive Ridge"}
COMPONENT_LABELS = {
    "FullControl": "All safeguards",
    "NoLog": "Without log transform",
    "NoStoreScale": "Without store scaling",
    "NoStandardization": "Without standardization",
    "NoUpperCap": "Without upper cap",
}
STUDY = {
    "Favorita": ("Corporación Favorita", "Reported family sales · units can vary by product family"),
    "M5": ("M5", "Recorded unit sales"),
}
CHART_CONFIG = {**PLOT_CONFIG, "displayModeBar": False}
RESEARCH_CSS = """
<style>
.st-key-retail_overview h3 {line-height:1.4!important;}
.st-key-retail_overview .retail-scope {margin:0;color:var(--wiq-muted);font-size:13px;line-height:1.5;}
.st-key-retail_overview .retail-findings {margin:8px 0 10px;color:var(--wiq-muted);font-size:12px;line-height:1.55;}
.st-key-retail_overview .retail-table {font-size:12px;width:100%;margin:0 0 8px;font-variant-numeric:tabular-nums;}
.st-key-retail_overview .retail-table caption {color:var(--wiq-muted);font-size:12px;text-align:left;margin:0 0 5px;}
.st-key-retail_overview .retail-table th,.st-key-retail_overview .retail-table td {padding:6px 7px;border-bottom:1px solid var(--wiq-line);}
.st-key-retail_overview .retail-table thead {background:#f5f7fa;color:var(--wiq-muted);}
.st-key-retail_overview .retail-table tbody th {font-weight:550;text-align:left;}
.st-key-retail_overview .retail-table td {text-align:right;white-space:nowrap;}
.st-key-retail_overview .retail-table .retail-log {background:#eaf6f4;color:#164d55;}
.st-key-retail_overview .retail-table .retail-control th {font-weight:700;}
.st-key-retail_overview .retail-finding {margin:0;color:#164d55;background:#eaf6f4;border-left:3px solid #087f8c;border-radius:0 8px 8px 0;padding:8px 11px;font-size:14px!important;}
@media (max-width:920px) {
    .st-key-retail_panels [data-testid="stHorizontalBlock"] {flex-direction:column;}
    .st-key-retail_panels [data-testid="stColumn"] {width:100%!important;min-width:0!important;}
}
</style>
"""


def _wape(value):
    if value >= 1e8:
        mantissa, exponent = f"{value:.2e}".split("e")
        exponent = str(int(exponent)).translate(str.maketrans("0123456789-", "⁰¹²³⁴⁵⁶⁷⁸⁹⁻"))
        return f"{mantissa} × 10{exponent}%"
    return f"{value:,.2f}%"


def horizon_figure(data: ResearchOverviewData, dataset: str) -> go.Figure:
    figure = go.Figure()
    origins = data.origins[["overlapping_origins", "nonoverlapping_origins"]].to_numpy()
    for method, color, symbol in zip(METHODS, ("#087f8c", "#4a5aa8"), ("circle", "diamond")):
        figure.add_scatter(
            x=data.horizon_wape.index.to_list(), y=data.horizon_wape[method].to_list(),
            name=METHOD_LABELS[method], mode="lines+markers", customdata=origins,
            line={"color": color, "width": 3}, marker={"size": 8, "symbol": symbol},
            hovertemplate="WAPE %{y:.2f}%<br>All origins %{customdata[0]}<br>Disjoint %{customdata[1]}",
            meta=dataset,
        )
    figure.update_layout(
        template="plotly_white", height=300, hovermode="x unified",
        margin={"l": 8, "r": 14, "t": 8, "b": 14},
        font={"color": "#40536d", "size": 12},
        legend={"orientation": "h", "x": 0, "y": 1, "yanchor": "bottom"},
        xaxis={
            "title": "Forecast horizon (weeks)", "tickvals": data.horizon_wape.index.to_list(),
            "ticktext": [str(h) for h in data.horizon_wape.index], "showgrid": False,
            "hoverformat": "d", "fixedrange": True, "automargin": True,
        },
        yaxis={"title": "Pooled WAPE (%)", "gridcolor": "#e2e8f0", "rangemode": "tozero",
               "fixedrange": True, "automargin": True, "ticksuffix": "%"},
    )
    return figure


def _ablation_table(data: ResearchOverviewData):
    rows = []
    for key, row in data.ablations.loc[["FullControl", "NoLog"]].iterrows():
        css = ' class="retail-log"' if key == "NoLog" else ' class="retail-control"' if key == "FullControl" else ""
        rows.append(
            f'<tr{css}><th scope="row">{escape(COMPONENT_LABELS[key])}</th>'
            f'<td>{_wape(row.Direct)}</td><td>{_wape(row.Recursive)}</td></tr>'
        )
    return (
        '<table class="retail-table"><caption>52-week V3 ablations · pooled WAPE</caption>'
        '<thead><tr><th scope="col">Model setup</th><th scope="col">Direct</th>'
        '<th scope="col">Recursive</th></tr></thead><tbody>' + "".join(rows) + "</tbody></table>"
    )


def _stability(data: ResearchOverviewData):
    st.subheader("Numerical stability")
    scope("V3 single-safeguard removal · same cases and other safeguards")
    st.markdown(_ablation_table(data), unsafe_allow_html=True)
    st.button("Explore stability", on_click=navigate, args=(NUMERICAL_STABILITY,),
              key="retail_link_stability", icon=":material/arrow_forward:", type="tertiary")


def _log_finding(data):
    log = data.ablations.loc["NoLog"]
    control = data.ablations.loc["FullControl"]
    if (log > control).all():
        return "At 52 weeks, log removal increased V3 error for both models."
    if (log < control).all():
        return "At 52 weeks, log removal lowered V3 error for both models."
    return "At 52 weeks, the effect of log removal differed by model."


def _research_details(data: ResearchOverviewData):
    registry = json.loads(data_path("research_overview_sources.json", SOURCE_REGISTRY).read_text(encoding="utf-8"))
    for key in OVERVIEW_SOURCES:
        pin = registry["artifacts"][key]
        source_detail(f'{pin["source_file"]} · {pin["experiment"]} · {pin["run_id"]} · {pin["section"]}')
    with data_section("Evaluation", "Methodology"):
        st.write(
            "The study uses retrospective store-week forecasts at 1, 4, 12, 26 and 52 weeks. "
            "Selection uses chronological development data. The horizon chart uses the V2 complete cohort, "
            "with WAPE calculated as total absolute error divided by total absolute observed sales. "
            "Direct Ridge fits forecasts for each lead. Recursive Ridge feeds earlier predictions into later leads."
        )
    with data_section("Horizon results", "Full Data Tables"):
        table_view(data.horizon_wape.rename(columns=METHOD_LABELS).join(data.origins), width="stretch")
    with data_section("Matched V1 → V2 correction and V3 component ablations", "Full Data Tables"):
        table_view(data.matched[["V1_WAPE", "V2_WAPE"]].rename(index=METHOD_LABELS), width="stretch")
        table_view(data.ablations.rename(index=COMPONENT_LABELS), width="stretch")
    with data_section("Annual meta-model eligibility", "Full Data Tables"):
        table_view(data.meta_annual[["pooled_WAPE", "status"]], width="stretch")
    with data_section("Local research exports", "CSV Downloads"):
        st.caption("These local research tables are pending public redistribution clearance.")
    with data_section("Interpreting the research", "Research Limitations"):
        st.write(
            "Forecast cases can overlap across origins. The evaluation was retrospective and V2 was corrected "
            "after inspecting V1. V3 component effects depend on the other safeguards. "
            "R16 and R19 are exploratory. The recorded replay establishes local artifact agreement. "
            "Independent reproduction and the original R16 engine fingerprint are unresolved."
        )


def render_research_overview():
    st.markdown(RESEARCH_CSS, unsafe_allow_html=True)
    with st.container(key="retail_overview"):
        header(
            "How do numerical safeguards and model choice affect retail sales forecasts at different horizons?",
        )
        dataset = selected("dataset") or st.segmented_control(
            "Dataset", DATASETS, format_func=lambda value: STUDY[value][0],
            default="Favorita", required=True, key="retail_overview_dataset", persist_state="session",
        )
        if dataset is None:
            st.info("Select a retail dataset to view its research results.")
            return
        try:
            data = load_research_overview(dataset)
        except (DataIssue, OSError, ValueError, pd.errors.ParserError) as error:
            research_unavailable(error)
            return

        annual = data.horizon_wape.loc[52]
        short = data.horizon_wape.loc[1]
        origin = data.origins.loc[52]
        st.markdown(
            f'<p class="retail-finding"><strong>V2 pooled WAPE, 1 → 52 weeks.</strong> '
            f'Direct Ridge {_wape(short.DirectRidge)} → {_wape(annual.DirectRidge)} · '
            f'Recursive Ridge {_wape(short.RecursiveRidge)} → {_wape(annual.RecursiveRidge)}. {_log_finding(data)}</p>',
            unsafe_allow_html=True,
        )
        boundary(f"Retrospective retail sales · Annual scored / disjoint origins: "
                 f"{origin.overlapping_origins} / {origin.nonoverlapping_origins}. "
                 "The stability correction followed inspection of the original evaluation.")

        with st.container(key="retail_panels"):
            horizon, stability = st.columns([3, 2])
            with horizon, panel("retail_horizons", "Forecast horizons"):
                st.subheader("Forecast horizons")
                scope(f"{STUDY[dataset][1]} · V2 complete cohort")
                st.plotly_chart(horizon_figure(data, dataset), width="stretch",
                                config=CHART_CONFIG, key="retail_horizon_chart")
                st.caption("Lower WAPE indicates less error. Origin and target coverage changes by horizon.")
                st.button("Explore horizons", on_click=navigate, args=(FORECAST_HORIZONS,),
                          key="retail_link_horizons", icon=":material/arrow_forward:", type="tertiary")
            with stability, panel("retail_stability", "Numerical stability"):
                _stability(data)

        if data.meta_annual.pooled_WAPE.isna().all():
            available = data.meta_development
            st.caption(
                f"At 52 weeks, the development-tuned V3 combination scored {_wape(data.convex_annual_wape)} WAPE. "
                "Favorita’s annual meta-model scores are unavailable. "
                f"{available.development_windows_eligible} of {available.development_windows_total} "
                "development windows met the eligibility rules."
            )
        else:
            loss_blend = data.meta_annual.loc["MetaLossBlend", "pooled_WAPE"]
            st.caption(f"At 52 weeks, the adapted R16 loss-weighted meta-model scored {_wape(loss_blend)} WAPE.")
        with st.container(horizontal=True, gap="xsmall"):
            st.button("Compare strategies", on_click=navigate, args=(MODEL_STRATEGIES,),
                      key="retail_link_strategies", icon=":material/arrow_forward:", type="tertiary")
            st.button("Review validation", on_click=navigate, args=(RESEARCH_VALIDATION,),
                      key="retail_link_validation", icon=":material/arrow_forward:", type="tertiary")
        _research_details(data)
