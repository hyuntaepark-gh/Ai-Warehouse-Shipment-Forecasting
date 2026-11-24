"""Present coverage, archived inference, and reproducibility for Final Research."""

import json

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from chart_access import data_section, source_detail
from data_loading import DataIssue
from forecast_horizons import coverage_figure
from model_strategies import STRATEGIES
from product_layout import PLOT_CONFIG, boundary, mini_cards, panel, research_unavailable
from research_overview import STUDY
from research_overview_data import DATASETS, HORIZONS, SOURCE_REGISTRY
from research_validation_data import (
    BLOCKS, COVERAGE_PINS, ELIGIBILITY_PINS, FAMILY_PINS, HAS_INTERVAL, UNESTIMABLE, load_validation_study,
)


PREFERRED_PAIRS = {"V3": ("HorizonRegime", "DirectPooledHGB"), "R19": ("MetaLossBlend", "DevConvexBlend")}
ABLATIONS = {
    "FullControl": "all safeguards", "NoLog": "no log", "NoStoreScale": "no store scaling",
    "NoStandardization": "no standardization", "NoUpperCap": "no upper cap",
}
CHART_CONFIG = {**PLOT_CONFIG, "displayModeBar": False}
CSS = """<style>
.st-key-validation_research_page .validation-scope {margin:0;color:var(--wiq-muted);font-size:13px;line-height:1.45;}
.st-key-validation_research_controls [data-testid="stWidgetLabel"] p {font-size:12px!important;font-weight:650;}
.st-key-validation_research_finding {padding:8px 13px;background:#eaf6f4;border-left:3px solid var(--wiq-teal);border-radius:0 8px 8px 0;}
.st-key-validation_research_finding p {margin:0;color:#164d55;font-size:15px;line-height:1.45;}
.st-key-validation_research_panels [data-testid="stHorizontalBlock"] {display:grid!important;grid-template-columns:minmax(0,1.2fr) minmax(0,1fr);}
.st-key-validation_research_panels [data-testid="stColumn"] {width:100%!important;min-width:0!important;}
.st-key-validation_research_panels [data-testid="stCaptionContainer"] {opacity:1;}
.st-key-validation_research_panels [data-testid="stCaptionContainer"] p {font-size:12px!important;}
.st-key-validation_research_evidence .wiq-mini-grid {display:grid;grid-template-columns:repeat(3,minmax(0,1fr));}
@media(max-width:920px){
    .st-key-validation_research_panels [data-testid="stHorizontalBlock"] {grid-template-columns:minmax(0,1fr);}
}
@media(max-width:600px){
    .st-key-validation_research_page .wiq-boundary {font-size:13px!important;line-height:1.4;}
    .st-key-validation_research_finding p {font-size:14px;}
    .st-key-validation_research_evidence .wiq-mini-grid {grid-template-columns:minmax(0,1fr);}
}
</style>"""


def _method_name(method):
    family, _, safeguard = method.partition("_")
    if safeguard in ABLATIONS:
        return f"{family} Ridge · {ABLATIONS[safeguard]}"
    return STRATEGIES[method][0] if method in STRATEGIES else method


def _pair_name(pair):
    return " vs. ".join(map(_method_name, pair))


def _effect(value):
    return "Not available" if pd.isna(value) else f"{value:+.2f} pp".replace("-", "−")


def _p_value(value):
    return "Not available" if pd.isna(value) else f"{value:.4f}"


def _replication_note(row, block):
    if row.status == UNESTIMABLE:
        return "Not available · At least one forecast in this pair is unavailable."
    if row.status != HAS_INTERVAL:
        return f"**{_effect(row.difference_pp)}** · Too few disjoint origins for a 95% interval or p-value."
    interval = f"[{row.ci_low:.2f}, {row.ci_high:.2f}] pp".replace("-", "−")
    probability = (f"Holm-adjusted p = **{_p_value(row.adjusted_p)}**" if block == 2
                   else "Holm adjustment applies to the primary view")
    return f"**{_effect(row.difference_pp)}** · 95% interval {interval} · {probability}."


def paired_effect_figure(study, block, pair, focus):
    data = study.pair(block, pair)
    supported = data.loc[data.status.eq(HAS_INTERVAL)]
    point_only = data.loc[data.difference_pp.notna() & ~data.status.eq(HAS_INTERVAL)]
    missing = data.index[data.difference_pp.isna()].to_list()
    figure = go.Figure()
    if not supported.empty:
        intervals_x = [value for row in supported.itertuples() for value in (row.ci_low, row.ci_high, None)]
        intervals_y = [value for h in supported.index for value in (HORIZONS.index(h), HORIZONS.index(h), None)]
        figure.add_scatter(x=intervals_x, y=intervals_y, mode="lines", line={"color": "#087f8c", "width": 3},
                           showlegend=False, hoverinfo="skip", name="Pointwise 95% interval")
    for rows, name, symbol in ((supported, "95% interval", "circle"), (point_only, "Point only", "circle-open")):
        if rows.empty:
            continue
        hover = []
        for row in rows.itertuples():
            label = f"{row.Index} wk · {_effect(row.difference_pp)}<br>{row.nonoverlap_origins} disjoint origins"
            if row.status == HAS_INTERVAL:
                label += (f"<br>95% interval [{row.ci_low:.4g}, {row.ci_high:.4g}] pp"
                          f"<br>Holm-adjusted p: {_p_value(row.adjusted_p)}")
            else:
                label += "<br>Insufficient temporal replication"
            hover.append(label)
        figure.add_scatter(
            x=rows.difference_pp.to_list(), y=[HORIZONS.index(h) for h in rows.index], name=name,
            mode="markers", customdata=rows.index.to_list(), hovertext=hover, hovertemplate="%{hovertext}<extra></extra>",
            marker={"color": "#087f8c" if symbol == "circle" else "#6277a8", "symbol": symbol,
                    "size": [12 if h == focus else 8 for h in rows.index], "line": {"width": 1.5}},
        )
    for h in missing:
        figure.add_annotation(xref="paper", x=0.98, y=HORIZONS.index(h), xanchor="right", text="Not available",
                              showarrow=False, font={"size": 11, "color": "#526278"})

    bounds = [0, *data.difference_pp.dropna(), *supported.ci_low, *supported.ci_high]
    low, high = min(bounds), max(bounds)
    padding = max((high - low) * .13, .03)
    figure.add_vline(x=0, line={"color": "#687b8d", "dash": "dot", "width": 1.5}, layer="below")
    figure.update_layout(
        template="plotly_white", height=226, showlegend=False, margin={"l": 4, "r": 9, "t": 4, "b": 4},
        font={"size": 11, "color": "#40536d"}, meta={"family": study.family, "dataset": study.dataset, "block": block},
        xaxis={"title": "Paired WAPE difference (pp)", "range": [low - padding, high + padding],
               "fixedrange": True, "gridcolor": "#e2e8f0", "zeroline": False, "automargin": True},
        yaxis={"tickvals": list(range(len(HORIZONS))), "range": [4.5, -.5],
               "ticktext": [f"<b>{h} wk</b>" if h == focus else f"{h} wk" for h in HORIZONS],
               "fixedrange": True, "showgrid": False, "zeroline": False, "automargin": True},
    )
    return figure


def _details(study):
    pins = json.loads(SOURCE_REGISTRY.read_bytes())["artifacts"]
    inference_key = FAMILY_PINS[study.family]
    for key in (inference_key, *COVERAGE_PINS, *ELIGIBILITY_PINS):
        pin = pins[key]
        source_detail(f'{pin["path"]} · {pin["source_file"]} · {pin["experiment"]} · {pin["run_id"]} · {pin["section"]}')
        source_detail(f'{pin["path"]} · SHA-256 {pin["sha256"]}')
    evidence = pins["validation_evidence"]
    source_detail(f'{evidence["path"]} · {evidence["source_file"]} · {evidence["section"]}')
    for parent in evidence["parents"]:
        source_detail(f'{parent["source_path"]} · SHA-256 {parent["sha256"]}')

    data = study.inference.assign(family=study.family, run_id=pins[inference_key]["run_id"])
    coverage = study.coverage.reset_index().assign(dataset=study.dataset, scope="V2 complete Ridge cohort")
    with data_section("Saved exploratory comparisons", "Full Data Tables"):
        st.dataframe(data.drop(columns=["dataset", "family", "run_id"]), hide_index=True, width="stretch")
    with data_section("Ridge origin coverage", "Full Data Tables"):
        st.dataframe(coverage, hide_index=True, width="stretch")
    with data_section("Selected retailer and inference family", "CSV Downloads"):
        st.download_button("Download inference rows", data.to_csv(index=False),
                           file_name=f"{study.dataset.lower()}_{study.family.lower()}_inference.csv",
                           mime="text/csv", key="validation_research_download", on_click="ignore")
        st.download_button("Download Ridge origin coverage", coverage.to_csv(index=False),
                           file_name=f"{study.dataset.lower()}_ridge_origins.csv",
                           mime="text/csv", key="validation_research_coverage_download", on_click="ignore")
        st.caption("Full source precision. Blank intervals, probabilities, and effects represent unavailable values.")
    with data_section("Retrospective design and disjoint origins"):
        st.write(
            "Store eligibility uses the first 108 weeks. Development labels end by week 172 and outer origins begin "
            "at that cut. Later rolling origins may use earlier outcomes available to them. Multiple rolling origins "
            "can share target weeks. Disjoint origins are chosen in chronological order with at least one horizon "
            "between starts. The primary chart is scoped to the V2 complete Ridge cohort. The inference rows use "
            "their own saved disjoint-origin counts, verified on matched target cases."
        )
    with data_section("Paired intervals and multiple comparisons"):
        st.write(
            "The effect is the named method's pooled WAPE minus its comparator's pooled WAPE on common complete "
            "store-week cases in disjoint windows. Pooled WAPE is 100 × total absolute error ÷ total absolute "
            "observed sales. The saved block bootstrap uses 5,000 draws, at least 12 disjoint origins and at "
            "least six blocks. The 95% intervals are pointwise effect intervals. They do not describe future "
            "forecast uncertainty."
        )
        st.write(
            "Holm adjustment is applied separately within the full estimable block-2 family for V3 and R19. "
            "Dataset, horizon and pair filters preserve the saved adjusted values. Block 4 is a sensitivity "
            "view with saved unadjusted probabilities available in the table. R19 uses R16 forecasts and "
            "has its own inference family. The R16 Model Strategies view reports all-origin descriptive scores."
        )
    with data_section("Interpretation and reproducibility", "Research Limitations"):
        st.write(
            "Prior inspection and repeated use of the outer data limit confirmatory interpretation. Overlapping "
            "rolling origins share target weeks, and annual disjoint coverage is small. The observed sales "
            "targets do not measure latent demand or causal retailer differences. The earlier R19 2/4 match "
            "record was superseded by the corrected 4/4 local replay. The exact cause of that earlier "
            "discrepancy and the original R16 engine fingerprint remain unresolved. Independent reproduction "
            "and peer review remain outstanding."
        )


def _controls():
    with st.container(key="validation_research_controls", horizontal=True, vertical_alignment="bottom", gap="xsmall"):
        dataset = st.segmented_control("Retail dataset", DATASETS, default="M5", required=True,
                                      key="validation_research_dataset", persist_state="session")
        family = st.segmented_control("Inference run", tuple(FAMILY_PINS), default="V3", required=True,
                                     key="validation_research_family", persist_state="session")
        options = st.popover("Evidence", icon=":material/tune:", key="validation_research_options")
    return dataset, family, options


def _comparison(study, options):
    with options:
        horizon = st.selectbox("Focus horizon", HORIZONS, format_func=lambda h: f"{h} wk", index=1,
                               key="validation_research_horizon", persist_state="session")
        block = st.selectbox("Bootstrap blocks", BLOCKS, format_func=lambda b: f"{b} origins · " +
                             ("primary Holm" if b == 2 else "sensitivity"),
                             key="validation_research_block", persist_state="session")
        pairs = study.pairs()
        pair = st.selectbox("Strategy pair", pairs, format_func=_pair_name,
                            index=pairs.index(PREFERRED_PAIRS[study.family]),
                            key=f"validation_research_pair_{study.family}", persist_state="session")
    return horizon, block, pair


def _evidence_status(study):
    e = study.evidence
    with st.container(key="validation_research_evidence"):
        st.subheader("Reproducibility evidence")
        replay = (e["v3_local_replay_status"] == "MATCHING_LOCAL_REPLAY"
                  and e["r19_local_replay_status"] == "MATCHING_LOCAL_ARTIFACT_REPLAY")
        mini_cards([
            ("Authoritative notebook revisions", f"{e['verified_authoritative_notebooks']} verified", "SHA-256 checks for notebooks and pinned inputs"),
            ("Frozen predictions and scores", f"{e['matched_cases_per_version']:,} cases", "Keys, actuals and completeness matched per revision"),
            ("Local replay", "Matches recorded" if replay else "Review required",
             f"V2 · {e['v2_matched_local_replays']} matches · V3 replay matched · R19 · {e['r19_matching_artifacts']} R16 artifacts"),
        ])
        if not e["independent_reproduction_verified"] and not e["original_r16_engine_fingerprint_recorded"]:
            st.markdown("**Independent reproduction remains unverified.** The original R16 engine fingerprint is unavailable.")
        meta = study.annual_meta
        if study.unavailable_meta_scores:
            st.markdown(f"**Favorita · 52 weeks.** {study.unavailable_meta_scores} R16 meta-model scores are unavailable. "
                        f"{meta.development_windows_eligible} of {meta.development_windows_total} development windows qualified.")


def render_research_validation():
    st.markdown(CSS, unsafe_allow_html=True)
    with st.container(key="validation_research_page"):
        dataset, family, options = _controls()
        try:
            study = load_validation_study(dataset, family)
        except (DataIssue, OSError, ValueError) as error:
            research_unavailable(error)
            return
        horizon, block, pair = _comparison(study, options)
        annual = study.coverage.loc[52]
        with st.container(key="validation_research_finding"):
            st.markdown(f"**{STUDY[dataset][0]} · Annual Ridge.** {annual.overlapping_origins} origins were scored. "
                        f"The disjoint subset contains **{annual.nonoverlapping_origins}**.")
        boundary("The outer data were inspected during earlier experiments. Rolling evaluation windows can overlap, "
                 "and the V3 and R19 results are exploratory.")

        with st.container(key="validation_research_panels"):
            coverage, effects = st.columns([1.2, 1])
            with coverage, panel("validation_research_origins", "Ridge evaluation coverage"):
                st.subheader("Ridge evaluation coverage")
                st.markdown('<p class="validation-scope">V2 complete cohort · Labels show disjoint / all scored origins</p>',
                            unsafe_allow_html=True)
                figure = coverage_figure(study, horizon)
                figure.update_layout(height=258)
                st.plotly_chart(figure, width="stretch", theme=None, config=CHART_CONFIG, key="validation_research_coverage_chart")
                st.caption("Disjoint windows share no target weeks. Rolling origins can cover the same weeks.")

            with effects, panel("validation_research_effect", "Statistical evidence"):
                st.subheader("Statistical evidence")
                scope = "primary Holm" if block == 2 else "sensitivity"
                st.markdown(f'<p class="validation-scope">{family} · {block}-origin blocks · {scope}</p>', unsafe_allow_html=True)
                row = study.pair(block, pair).loc[horizon]
                st.markdown(f"**{_pair_name(pair)}**", help="The named method's WAPE minus its comparator's WAPE.")
                st.plotly_chart(paired_effect_figure(study, block, pair, horizon), width="stretch", theme=None,
                                config=CHART_CONFIG, key="validation_research_effect_chart")
                st.markdown(f"**{horizon} wk · {row.nonoverlap_origins} disjoint.** {_replication_note(row, block)}")
                st.caption("Negative favors the named method. Filled dots have 95% effect intervals. Open dots show point effects only.")

        _evidence_status(study)
        _details(study)
