"""Final Research workspace for matched stability and component experiments."""

import json
from math import log10

import plotly.graph_objects as go
import streamlit as st

from chart_access import data_section, source_detail
from data_loading import DataIssue
from numerical_stability_data import CORRECTION, MODE, SOURCES, load_numerical_stability
from product_layout import PLOT_CONFIG, boundary, mini_cards, panel, research_unavailable
from research_overview import METHOD_LABELS, STUDY
from research_overview_data import DATASETS, HORIZONS, METHODS, SOURCE_REGISTRY


OTHER_COMPONENTS = ("NoStoreScale", "NoStandardization", "NoUpperCap")
LABELS = {
    "NoLog": "Without log transform",
    "NoStoreScale": "Without store scaling",
    "NoStandardization": "Without standardization",
    "NoUpperCap": "Without upper cap",
    CORRECTION: CORRECTION,
}
CHART_CONFIG = {**PLOT_CONFIG, "displayModeBar": False}
CSS = """<style>
.st-key-stability_page .stability-scope {margin:0;color:var(--wiq-muted);font-size:13px;line-height:1.45;}
.st-key-stability_controls [data-testid="stWidgetLabel"] p {font-size:12px!important;font-weight:650;}
.st-key-stability_finding {padding:8px 13px;background:#eaf6f4;border-left:3px solid var(--wiq-teal);border-radius:0 8px 8px 0;}
.st-key-stability_finding p {margin:0;color:#164d55;font-size:15px;line-height:1.45;}
.st-key-stability_page .wiq-mini {min-width:0;}
.st-key-stability_page .wiq-mini b {font-variant-numeric:tabular-nums;overflow-wrap:anywhere;}
.st-key-stability_page .wiq-mini:first-child {border-top:3px solid #087f8c;}
.st-key-stability_page .wiq-mini:nth-child(2) {border-top:3px solid #4a5aa8;}
.st-key-stability_panels [data-testid="stHorizontalBlock"] {display:grid!important;grid-template-columns:minmax(0,1.65fr) minmax(320px,1fr);}
.st-key-stability_panels [data-testid="stColumn"] {width:100%!important;min-width:0!important;}
@media(max-width:1040px){
    .st-key-stability_panels [data-testid="stHorizontalBlock"] {grid-template-columns:minmax(0,1fr);}
}
@media(max-width:600px){
    .st-key-stability_page .wiq-boundary {font-size:13px!important;line-height:1.4;}
    .st-key-stability_page .wiq-mini {padding:7px 10px;}
    .st-key-stability_page .wiq-mini-grid {gap:8px;}
    .st-key-stability_page .wiq-mini b {font-size:19px!important;margin:1px 0;}
    .st-key-stability_finding p {font-size:14px;}
}
</style>"""


def _number(value):
    if abs(value) < 100_000:
        return f"{value:,.2f}"
    mantissa, exponent = f"{value:.2e}".split("e")
    superscript = str(int(exponent)).translate(str.maketrans("0123456789-", "⁰¹²³⁴⁵⁶⁷⁸⁹⁻"))
    return f"{mantissa} × 10{superscript}"


def _wape(value):
    return "Unavailable" if value is None else _number(value) + "%"


def _pp(value):
    if value is None:
        return "Unavailable"
    if value == 0:
        return "0.00 pp"
    sign = "+" if value > 0 else "−"
    if abs(value) < 0.005:
        return f"{sign}{abs(value):.2g} pp"
    return sign + _number(abs(value)) + " pp"


def _effect(delta):
    if delta == 0:
        return "left WAPE unchanged"
    amount = "less than 0.01" if abs(delta) < 0.005 else _number(abs(delta))
    direction = "raised" if delta > 0 else "lowered"
    return f"{direction} WAPE by {amount} pp"


def finding(data, condition):
    result = data.comparisons[condition]
    scope = f"{STUDY[data.dataset][0]} · {data.horizon} wk · {METHOD_LABELS[data.method]}"
    if result.delta_pp is None:
        return f"**{scope}.** A verified matched comparison is unavailable for this selection."
    if condition == CORRECTION:
        subject = "The V1 → V2 correction"
    elif condition == "NoLog":
        subject = "Log removal"
    else:
        subject = LABELS[condition].replace("Without ", "Removing the ", 1)
    return f"**{scope}.** {subject} {_effect(result.delta_pp)}."


def _log_axis(result, condition):
    pair = [result.baseline, result.selected]
    return condition == CORRECTION and all(v is not None and v > 0 for v in pair) and max(pair) / min(pair) >= 100


def comparison_figure(result, condition):
    labels = ("Original (V1)", "Stabilized (V2)") if condition == CORRECTION else ("FullControl", LABELS[condition])
    values = [result.baseline, result.selected]
    log_axis = _log_axis(result, condition)
    scores = [value for value in values if value is not None]
    limits = [log10(min(scores)) - 0.22, log10(max(scores)) + 0.32] if log_axis else [0, (max(scores, default=0) or 1) * 1.18]
    figure = go.Figure()
    for index, (value, label, color) in enumerate(zip(values, labels, ("#087f8c", "#4a5aa8"))):
        if value is not None:
            figure.add_scatter(
                x=[value], y=[index], name=label, mode="markers+text",
                text=[_wape(value)], textposition="top center", cliponaxis=False,
                marker={"size": 13, "color": color, "symbol": ("circle", "diamond")[index]},
                hovertemplate=f"{label}<br>Pooled WAPE {_wape(value)}<extra></extra>",
            )
    if result.baseline is not None:
        figure.add_vline(x=result.baseline, line={"color": "#087f8c", "dash": "dot", "width": 1.5}, layer="below")
    figure.update_layout(
        template="plotly_white", showlegend=False, height=224,
        margin={"l": 4, "r": 24, "t": 16, "b": 6}, font={"size": 12, "color": "#40536d"},
        xaxis={"title": "Pooled WAPE (log scale)" if log_axis else "Pooled WAPE (%)",
               "type": "log" if log_axis else "linear", "range": limits, "ticksuffix": "%",
               "fixedrange": True, "automargin": True, "gridcolor": "#e2e8f0"},
        yaxis={"tickvals": [0, 1], "ticktext": list(labels), "range": [1.62, -0.58],
               "showgrid": False, "zeroline": False, "fixedrange": True, "automargin": True},
    )
    return figure


def safeguards_figure(data):
    effects = [data.comparisons[c].delta_pp for c in OTHER_COMPONENTS]
    present = [delta for delta in effects if delta is not None]
    left, right = min([0, *present]), max([0, *present])
    padding = max(right - left, 0.05) * 0.3
    labels = ("Store scaling", "Standardization", "Upper cap")
    colors = ["#a74832" if value is not None and value > 0 else "#087f8c" for value in effects]

    figure = go.Figure()
    for i, (label, delta, color) in enumerate(zip(labels, effects, colors)):
        if delta is None:
            continue
        figure.add_shape(type="line", x0=0, x1=delta, y0=i, y1=i, line={"color": color, "width": 4})
        figure.add_scatter(
            x=[delta], y=[i], mode="markers+text", text=[_pp(delta)], textposition="top center", cliponaxis=False,
            marker={"size": 8, "color": color}, name=label,
            hovertemplate=f"Without {label.lower()}<br>{_pp(delta)} vs. FullControl<extra></extra>",
        )
    figure.add_vline(x=0, line={"color": "#5c6e83", "width": 1.5}, layer="below")
    figure.update_layout(
        template="plotly_white", showlegend=False, height=224,
        margin={"l": 4, "r": 17, "t": 16, "b": 6}, font={"size": 12, "color": "#40536d"},
        xaxis={"title": "WAPE change (pp)", "range": [left - padding, right + padding],
               "fixedrange": True, "automargin": True, "gridcolor": "#e2e8f0"},
        yaxis={"tickvals": [0, 1, 2], "ticktext": list(labels), "range": [2.42, -0.62],
               "showgrid": False, "fixedrange": True, "automargin": True},
    )
    return figure


def _controls():
    with st.container(key="stability_controls", horizontal=True, vertical_alignment="bottom", gap="xsmall"):
        dataset = st.segmented_control(
            "Retail dataset", DATASETS, default="Favorita", required=True,
            key="stability_dataset", persist_state="session",
        )
        method = st.segmented_control(
            "Ridge strategy", METHODS, format_func=MODE.__getitem__, default=METHODS[0], required=True,
            key="stability_strategy", persist_state="session",
        )
        with st.popover("Experiment", icon=":material/tune:", key="stability_options"):
            horizon = st.selectbox(
                "Forecast horizon", HORIZONS, format_func=lambda h: f"{h} wk", index=4,
                key="stability_horizon", persist_state="session",
            )
            condition = st.selectbox(
                "Comparison", ("NoLog", *OTHER_COMPONENTS, CORRECTION), format_func=LABELS.__getitem__,
                key="stability_condition", persist_state="session",
            )
    return dataset, method, horizon, condition


def _results(data, condition):
    result = data.comparisons[condition]
    correction = condition == CORRECTION
    mini_cards([
        ("Original V1 WAPE" if correction else "FullControl WAPE", _wape(result.baseline), "Original run" if correction else "All four safeguards"),
        ("Stabilized V2 WAPE" if correction else "Ablation WAPE", _wape(result.selected), "After the correction" if correction else LABELS[condition]),
        ("Change in WAPE", _pp(result.delta_pp), "V2 − V1" if correction else "Ablation − FullControl"),
        ("Matched cases" if result.delta_pp is not None else "Reference cases",
         f"{data.cases:,}" if data.cases is not None else "Unavailable",
         f"{data.origins} origins · {data.disjoint} disjoint"),
    ])


def _details(data):
    registry = json.loads(SOURCE_REGISTRY.read_text(encoding="utf-8"))["artifacts"]
    for key in SOURCES:
        pin = registry[key]
        source_detail(f'{pin["path"]} · {pin["source_file"]} · {pin["run_id"]} · {pin["section"]}')
    source_detail(f"Matched correction prior run · {registry['matched']['prior_run_id']} · "
                  "V1_COMPARISON_STATUS.csv in the Phase 1.5 evidence manifest.")
    coverage = {"scored_origins": data.origins, "disjoint_origins": data.disjoint}
    ablations = data.ablations.assign(run_id=registry["ablations"]["run_id"], **coverage)
    correction = data.correction_row.assign(
        run_id=registry["matched"]["run_id"],
        comparison_available=data.comparisons[CORRECTION].delta_pp is not None,
        **coverage,
    )
    with data_section("Component ablations · V3", "Full Data Tables"):
        st.dataframe(ablations[["component", "complete_rows", "failed_rows", "full_cohort_WAPE",
                               "full_cohort_delta_pp", "status", "comparison_available"]],
                     hide_index=True, width="stretch")
    with data_section("Matched original and stabilized scores · V1 and V2", "Full Data Tables"):
        st.dataframe(correction, hide_index=True, width="stretch")
    with data_section("Selected retailer, horizon and strategy", "CSV Downloads"):
        for label, frame, key in (
            ("Component ablations", ablations, "ablations"), ("Matched correction", correction, "correction")
        ):
            st.download_button(
                f"Download {label.lower()}", frame.to_csv(index=False),
                file_name=f"{data.dataset.lower()}_{data.horizon}wk_{data.method}_{key}.csv",
                mime="text/csv", key=f"stability_download_{key}", on_click="ignore",
            )
        st.caption("Full source precision. Blank scores indicate unavailable results. Local research use.")
    with data_section("Matched cohorts and metric"):
        st.write(
            "Pooled WAPE is 100 × total absolute error ÷ total absolute observed sales. "
            "The V3 full-cohort comparison holds retailer, strategy, horizon and scored store-week cases fixed. "
            "FullControl reproduces the V2 reference. The V1 → V2 table comes from the saved match on input "
            "fingerprints, target keys, actuals and completeness masks."
        )
        st.write(
            "The chart uses the saved V3 change from FullControl. For the correction, the display reverses "
            "the source column V1_minus_V2_pp to show selected minus baseline consistently."
        )
    with data_section("Interpreting the effects", "Research Limitations"):
        st.write(
            "Each ablation measures removal of one safeguard while the others are in place. These effects are "
            "conditional on this setup. V2 followed review of V1 and changed several safeguards together. "
            "Store-week cases can repeat across overlapping forecast windows. Disjoint windows describe coverage. "
            "The comparisons are retrospective and descriptive."
        )


def render_numerical_stability():
    st.markdown(CSS, unsafe_allow_html=True)
    with st.container(key="stability_page"):
        dataset, method, horizon, condition = _controls()
        try:
            studies = load_numerical_stability(horizon, method)
        except (DataIssue, OSError, ValueError) as error:
            research_unavailable(error)
            return
        data = studies[dataset]
        result = data.comparisons[condition]
        with st.container(key="stability_finding"):
            st.markdown(finding(data, condition))
        _results(data, condition)
        caveat = ("V2 changed several safeguards after review of V1. The matched change is retrospective."
                  if condition == CORRECTION else
                  "Each ablation removes one safeguard with the others in place. Effects are descriptive.")
        boundary(caveat + (" The annual cohort has limited disjoint origins." if horizon == 52 else ""))

        with st.container(key="stability_panels"):
            primary, supporting = st.columns([1.65, 1])
            with primary, panel("stability_pair", "Matched forecast error"):
                st.subheader("Matched forecast error")
                scope = ("V1 and V2 correction" if condition == CORRECTION else "V3 single-safeguard removal")
                axis = " · Logarithmic axis, with original WAPE values" if _log_axis(result, condition) else ""
                st.markdown(f'<p class="stability-scope">{scope} · Lower WAPE is better{axis}</p>',
                            unsafe_allow_html=True)
                st.plotly_chart(comparison_figure(result, condition), width="stretch", theme=None,
                                config=CHART_CONFIG, key="stability_pair_chart")
            with supporting, panel("stability_safeguards", "Scaling, standardization and cap"):
                st.subheader("Scaling, standardization and cap")
                st.markdown('<p class="stability-scope">V3 · Change from FullControl (pp)</p>', unsafe_allow_html=True)
                st.plotly_chart(safeguards_figure(data), width="stretch", theme=None,
                                config=CHART_CONFIG, key="stability_safeguards_chart")
                if any(data.comparisons[c].delta_pp is None for c in OTHER_COMPONENTS):
                    st.caption("A blank row indicates an unavailable matched result.")

        contrast = [
            f"{STUDY[name][0]} {_pp(study.comparisons['NoLog'].delta_pp)}"
            for name, study in studies.items() if study.comparisons["NoLog"].delta_pp is not None
        ]
        if len(contrast) == len(DATASETS):
            st.markdown(f"**WAPE change after log removal** · {' · '.join(contrast)}. Each change uses its retailer’s FullControl.")
        _details(data)
