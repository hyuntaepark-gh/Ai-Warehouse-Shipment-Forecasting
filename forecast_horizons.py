"""Forecast horizon explorer for the final retailer study."""

from deployment.analytics_access import data_path, selected, download_view, table_view

import json

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from chart_access import data_section, source_detail
from data_loading import DataIssue
from forecast_horizons_data import METRICS, ORIGINS, load_forecast_horizons
from product_layout import PLOT_CONFIG, boundary, panel, research_unavailable
from research_overview import METHOD_LABELS, STUDY
from research_overview_data import DATASETS, HORIZONS, METHODS, SOURCE_REGISTRY


BOTH = "Both strategies"
CHART_CONFIG = {**PLOT_CONFIG, "displayModeBar": False}
MARKS = {
    "DirectRidge": ("#087f8c", "circle", "solid"),
    "RecursiveRidge": ("#4a5aa8", "diamond", "dash"),
}
CSS = """<style>
.st-key-horizon_explorer .horizon-scope {margin:0;color:var(--wiq-muted);font-size:13px;line-height:1.45;}
.st-key-horizon_finding {padding:8px 13px;background:#eaf6f4;border-left:3px solid var(--wiq-teal);border-radius:0 8px 8px 0;}
.st-key-horizon_finding p {margin:0;color:#164d55;font-size:15px;line-height:1.45;}
.st-key-horizon_explorer .horizon-focus {font-size:13px;color:var(--wiq-muted);line-height:1.45;margin:0;}
.st-key-horizon_explorer .horizon-focus p {margin:0;}
.st-key-horizon_explorer .wiq-boundary {max-width:none;}
.st-key-horizon_controls [data-testid="stWidgetLabel"] p {font-size:12px!important;font-weight:650;}
.st-key-horizon_panels [data-testid="stHorizontalBlock"] {display:grid!important;grid-template-columns:minmax(0,2.35fr) minmax(255px,1fr);}
.st-key-horizon_panels [data-testid="stColumn"] {width:100%!important;min-width:0!important;}
@media(max-width:1050px){
    .st-key-horizon_panels [data-testid="stHorizontalBlock"] {grid-template-columns:minmax(0,1fr);}
}
@media(max-width:600px){
    .st-key-horizon_finding p {font-size:14px;}
    .st-key-horizon_explorer .horizon-focus {font-size:12px;}
    .st-key-horizon_explorer .wiq-boundary {font-size:13px!important;line-height:1.4;}
}
</style>"""


def horizon_finding(data, metric, focus, methods):
    label = STUDY[data.dataset][0]
    label_text = METRICS[metric]
    metric_label = label_text[0].lower() + label_text[1:]
    scores = data.metric(metric).loc[focus, list(methods)].dropna()
    period = f"{label} · {focus} week{'s' if focus != 1 else ''}"
    if len(scores) < len(methods):
        if scores.empty:
            return f"**{period}.** The selected {metric_label} is unavailable."
        available = scores.index[0]
        return (f"**{period}.** {METHOD_LABELS[available]} scored {scores.iloc[0]:.2f}%. "
                f"The paired {metric_label} comparison is unavailable.")
    if len(methods) == 1:
        return f"**{period}.** {METHOD_LABELS[methods[0]]} scored **{scores.iloc[0]:.2f}%** {metric_label}."
    low, high = scores.sort_values().index
    gap = scores[high] - scores[low]
    if gap == 0:
        return f"**{period}.** Both strategies scored **{scores[low]:.2f}%** {metric_label}."
    if f"{gap:.2f}" == "0.00":
        return f"**{period}.** The strategies differ by **less than 0.01 percentage points** in {metric_label}."
    return (f"**{period}.** {METHOD_LABELS[low]} had **{gap:.2f} percentage points lower** "
            f"{metric_label} ({scores[low]:.2f}% vs. {scores[high]:.2f}%).")


def ridge_figure(data, metric, focus, methods):
    figure = go.Figure()
    values = data.metric(metric)
    for method in methods:
        color, symbol, dash = MARKS[method]
        figure.add_scatter(
            x=list(HORIZONS), y=[None if pd.isna(v) else float(v) for v in values[method]],
            name=METHOD_LABELS[method], meta=data.dataset, mode="lines+markers", connectgaps=False,
            line={"color": color, "width": 3, "dash": dash},
            marker={"size": [12 if horizon == focus else 8 for horizon in HORIZONS], "symbol": symbol,
                    "line": {"color": "white", "width": 1}},
            customdata=data.coverage[list(ORIGINS)].to_numpy().tolist(),
            hovertemplate=("%{y:.2f}%<br>Scored origins %{customdata[0]}"
                           "<br>Disjoint origins %{customdata[1]}" + f"<extra>{METHOD_LABELS[method]}</extra>"),
        )
    figure.update_layout(
        template="plotly_white", height=340, hovermode="x unified",
        margin={"l": 4, "r": 10, "t": 8, "b": 4},
        font={"color": "#40536d", "size": 12},
        legend={"orientation": "h", "x": 0, "y": 1.02, "yanchor": "bottom"},
        xaxis={"title": "Forecast horizon (weeks)", "type": "category", "categoryorder": "array",
               "categoryarray": list(HORIZONS), "tickvals": list(HORIZONS),
               "ticktext": [str(h) for h in HORIZONS], "showgrid": False,
               "fixedrange": True, "automargin": True},
        yaxis={"title": f"{METRICS[metric]} (%)", "ticksuffix": "%", "gridcolor": "#e2e8f0",
               "rangemode": "tozero", "fixedrange": True, "automargin": True},
    )
    return figure


def coverage_figure(data, focus):
    figure = go.Figure()
    labels = [f"{h} wk" for h in HORIZONS]
    total = data.coverage.overlapping_origins.to_list()
    disjoint = data.coverage.nonoverlapping_origins.to_list()
    figure.add_bar(
        x=total, y=labels, orientation="h", name="All scored", width=0.62, marker_color="#dce7f0",
        hovertemplate="%{x} scored origins<extra></extra>",
    )
    figure.add_bar(
        x=disjoint, y=labels, orientation="h", name="Disjoint subset", width=0.40, marker_color="#087f8c",
        hovertemplate="%{x} disjoint origins<extra></extra>",
    )
    figure.add_scatter(
        x=[n + 0.7 for n in total], y=labels, mode="text", textposition="middle right", showlegend=False,
        hoverinfo="skip", text=[f"{subset} / {count}" for subset, count in zip(disjoint, total)],
        textfont={"size": 12, "color": "#182e4c"},
    )
    figure.update_layout(
        template="plotly_white", height=270, barmode="overlay",
        margin={"l": 3, "r": 12, "t": 6, "b": 4}, font={"size": 11, "color": "#40536d"},
        legend={"orientation": "h", "x": 0, "y": 1.04, "yanchor": "bottom"},
        xaxis={"title": "Forecast origins", "range": [0, max(total) + 10], "fixedrange": True,
               "gridcolor": "#e2e8f0", "dtick": 10, "automargin": True},
        yaxis={"categoryorder": "array", "categoryarray": labels, "autorange": "reversed",
               "tickvals": labels, "ticktext": [f"<b>{label}</b>" if h == focus else label
                                             for h, label in zip(HORIZONS, labels)],
               "fixedrange": True, "automargin": True},
    )
    return figure


def _details(data, *, include_downloads, registry):
    for key in ("scores", "origins"):
        pin = registry[key]
        source_detail(f'{pin["path"]} · {pin["source_file"]} · {pin["run_id"]} · {pin["section"]}')
    table = data.table().assign(run_id=registry["scores"]["run_id"])
    display_table = table.rename(columns={
        "overlapping_origins": "All scored origins", "nonoverlapping_origins": "Disjoint origins",
        "origins": "Origins for strategy", "wape": "Pooled WAPE (%)",
        "mean_origin_wape": "Mean origin WAPE (%)", "store_weeks": "Scored store-week cases",
    })
    with data_section("Ridge results · " + STUDY[data.dataset][0], "Full Data Tables"):
        if include_downloads:
            table_view(display_table, hide_index=True, width="stretch")
        else:
            # The interactive dataframe toolbar provides a client-side CSV export.
            st.table(display_table, hide_index=True)
    if include_downloads:
        with data_section("Selected retailer · all five horizons", "CSV Downloads"):
            download_view("Download horizon results", table.to_csv(index=False), mime="text/csv",
                               file_name=f"forecast_horizons_{data.dataset.lower()}.csv",
                               key="horizon_download", on_click="ignore")
            st.caption("Full source precision. Blank scores indicate unavailable results. Local research use.")
    with data_section("Retrospective rolling-origin evaluation"):
        st.write(
            "Direct Ridge fits a forecast for each lead. Recursive Ridge feeds previous predictions into later leads. "
            "The V2 complete cohort scores matched store-week cases for both strategies within each retailer and horizon. "
            "Pooled WAPE is 100 × total absolute error ÷ total absolute observed sales. Mean origin WAPE is the "
            "arithmetic mean of the WAPE values calculated separately for each scored origin. Lower is better for both."
        )
    with data_section("Coverage and interpretation", "Research Limitations"):
        st.write(
            "A forecast origin is a starting point for a forecast window. The score uses all eligible origins, "
            "so scored store-week cases can recur in overlapping windows. The disjoint count describes a subset "
            "of those origins. Target weeks and cases differ across horizons. V2 followed inspection of V1. "
            "These error differences are descriptive. The results measure recorded retail sales and belong to "
            "a separate study from the warehouse order-demand dashboards."
        )


def _controls():
    with st.container(key="horizon_controls", horizontal=True, vertical_alignment="bottom"):
        dataset = selected("dataset") or st.segmented_control(
            "Retail dataset", DATASETS, default="M5", required=True, key="horizon_dataset", persist_state="session",
        )
        focus = st.selectbox(
            "Focus horizon", HORIZONS, format_func=lambda h: f"{h} week{'s' if h != 1 else ''}", index=4,
            width=144, key="horizon_focus", persist_state="session",
        )
        with st.popover("Chart options", icon=":material/tune:", key="horizon_options"):
            metric = st.selectbox(
                "Error metric", tuple(METRICS), format_func=METRICS.__getitem__,
                key="horizon_metric", persist_state="session",
            )
            strategy = st.selectbox(
                "Ridge strategy", (BOTH, *METHODS), format_func=lambda value: METHOD_LABELS.get(value, value),
                key="horizon_strategy", persist_state="session",
            )
    return dataset, focus, metric, METHODS if strategy == BOTH else (strategy,)


def render_forecast_horizons(*, include_downloads=True, load_data=None, registry=None):
    if load_data is None:
        load_data = load_forecast_horizons
    st.markdown(CSS, unsafe_allow_html=True)
    with st.container(key="horizon_explorer"):
        dataset, focus, metric, methods = _controls()
        try:
            data = load_data(dataset)
        except (DataIssue, OSError, ValueError) as error:
            research_unavailable(error)
            return

        with st.container(key="horizon_finding"):
            st.markdown(horizon_finding(data, metric, focus, methods))
        annual = data.annual_disjoint
        annual_text = (f"{annual['M5']} disjoint 52-week origins for M5 and {annual['Favorita']} for Favorita"
                       if len(annual) == len(DATASETS) else f"{annual[dataset]} disjoint 52-week origins for {dataset}")
        boundary(f"Annual evidence is limited to {annual_text}. V2 followed review of the original evaluation. "
                 "Error differences are descriptive, and target windows vary by horizon.")

        with st.container(key="horizon_panels"):
            hero, coverage = st.columns([2.35, 1])
            with hero, panel("horizon_ridge", "Ridge error by forecast horizon"):
                st.subheader("Ridge error by forecast horizon")
                st.markdown(f'<p class="horizon-scope">{STUDY[dataset][1]} · V2 complete cohort · Lower WAPE is better</p>',
                            unsafe_allow_html=True)
                counts = data.coverage.loc[focus]
                st.markdown(
                    f'<p class="horizon-focus"><strong>{focus} wk</strong> · {counts.overlapping_origins} scored origins · '
                    f'{counts.nonoverlapping_origins} disjoint</p>', unsafe_allow_html=True,
                )
                st.plotly_chart(ridge_figure(data, metric, focus, methods), width="stretch", theme=None,
                                config=CHART_CONFIG, key="horizon_ridge_chart")
            with coverage, panel("horizon_origin_counts", "Evaluation coverage"):
                st.subheader("Evaluation coverage")
                st.markdown('<p class="horizon-scope">Disjoint origins are a subset of all scored origins.</p>',
                            unsafe_allow_html=True)
                st.plotly_chart(coverage_figure(data, focus), width="stretch", theme=None,
                                config=CHART_CONFIG, key="horizon_coverage_chart")
                st.caption("Labels show disjoint / all scored origins. The score uses the full set.")
        if registry is None:
            registry = json.loads(data_path("research_overview_sources.json", SOURCE_REGISTRY).read_text(encoding="utf-8"))["artifacts"]
        _details(data, include_downloads=include_downloads, registry=registry)
