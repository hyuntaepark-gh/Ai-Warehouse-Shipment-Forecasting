"""Explore paired descriptive strategy scores from two pinned research runs."""

from deployment.analytics_access import data_path, selected, download_view, table_view

import json

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from chart_access import data_section, source_detail
from data_loading import DataIssue
from model_strategies_data import PROTOCOL_METHODS, R16, SOURCES, V3, load_strategy_study
from product_layout import PLOT_CONFIG, boundary, panel, research_unavailable
from research_overview import STUDY
from research_overview_data import DATASETS, HORIZONS, SOURCE_REGISTRY


PROTOCOL_LABELS = {V3: "V3 benchmark", R16: "R16 meta-models"}
PREFERRED_PAIRS = {V3: ("HorizonRegime", "HorizonOnly"), R16: ("MetaLossBlend", "DevConvexBlend")}
STRATEGIES = {
    "HorizonOnly": ("Horizon only", "Selection rule", "Chooses a candidate separately for each horizon using development-origin WAPE."),
    "HorizonRegime": ("Horizon + regime", "Selection rule", "Chooses a candidate by horizon and demand regime measured from data available at the origin. Sparse groups fall back to the horizon rule."),
    "EqualWeight": ("Equal weight", "Fixed blend", "Averages Seasonal Naive, the four-week moving average, Direct Ridge and Recursive Ridge with equal weights."),
    "SeasonalBlend": ("Seasonal blend", "Fixed blend", "Averages Seasonal Naive and the four-week moving average with equal weights."),
    "DevConvexBlend": ("Convex blend", "Development-tuned blend", "Searches nonnegative weights in 0.25 increments for Seasonal Blend, Equal Weight and Direct Pooled HGB. Development selects the weights for each horizon."),
    "DirectPooledHGB": ("Direct pooled HGB", "Direct model", "Fits one histogram gradient-boosted model with forecast lead as an input. Training labels end before the origin."),
    "DirectRidge": ("Direct Ridge", "Direct model", "Fits a separate Ridge model for each lead using features available at the forecast origin."),
    "RecursiveRidge": ("Recursive Ridge", "Recursive model", "Repeats a one-step Ridge forecast and feeds earlier predictions back into subsequent steps."),
    "MetaHardClassifier": ("Meta classifier", "Meta-learned selection", "A random forest classifier learns the lowest-loss candidate in each development window and predicts a candidate for each outer window."),
    "MetaLossBlend": ("Meta loss blend", "Meta-learned blend", "A multi-output random forest predicts the WAPE of the original candidates. A softmax converts the predicted losses into weights."),
}
CSS = """<style>
.st-key-strategies_page .strategy-scope {margin:0;color:var(--wiq-muted);font-size:13px;line-height:1.45;}
.st-key-strategy_controls [data-testid="stWidgetLabel"] p {font-size:12px!important;font-weight:650;}
.st-key-strategy_finding {padding:8px 13px;background:#eaf6f4;border-left:3px solid var(--wiq-teal);border-radius:0 8px 8px 0;}
.st-key-strategy_finding p {margin:0;color:#164d55;font-size:15px;line-height:1.45;}
.st-key-strategy_panels [data-testid="stHorizontalBlock"] {display:grid!important;grid-template-columns:minmax(0,1.65fr) minmax(300px,1fr);}
.st-key-strategy_panels [data-testid="stColumn"] {width:100%!important;min-width:0!important;}
.st-key-strategy_panels [data-testid="stCaptionContainer"] {opacity:1;}
.st-key-strategy_panels [data-testid="stCaptionContainer"] p {font-size:12px!important;}
@media(max-width:1040px){
    .st-key-strategy_panels [data-testid="stHorizontalBlock"] {grid-template-columns:minmax(0,1fr);}
}
@media(max-width:600px){
    .st-key-strategies_page .wiq-boundary {font-size:13px!important;line-height:1.4;}
    .st-key-strategy_finding p {font-size:14px;}
}
</style>"""

CHART_CONFIG = {**PLOT_CONFIG, "displayModeBar": False}


def _name(method):
    return STRATEGIES[method][0]


def _wape(value):
    return "Not available" if pd.isna(value) else f"{value:.2f}%"


def finding(study, horizon, strategy, reference):
    scope = f"**{STUDY[study.dataset][0]} · {study.protocol} · {horizon} wk.**"
    if strategy == reference:
        return scope + " Choose two different strategies to compare them."
    delta = study.difference(horizon, strategy, reference)
    if delta is None:
        missing = [_name(m) for m in (strategy, reference) if pd.isna(study.wape.at[m, horizon])]
        return f"{scope} Not available for {' and '.join(missing)}."
    if delta == 0:
        return f"{scope} {_name(strategy)} and {_name(reference)} both scored **{_wape(study.wape.at[strategy, horizon])}** WAPE."
    direction = "lower" if delta < 0 else "higher"
    magnitude = f"{abs(delta):.2f} pp" if abs(delta) >= 0.005 else "less than 0.01 pp"
    return f"{scope} {_name(strategy)} had **{magnitude} {direction} WAPE** than {_name(reference)}."


def strategy_matrix(study, horizon):
    matrix = study.wape
    colors = matrix.copy()
    for column in matrix.columns:
        values = matrix[column].dropna()
        span = values.max() - values.min()
        colors.loc[values.index, column] = (values - values.min()) / span if len(values) == len(matrix) and span else 0.5
    xs, ys = list(range(len(HORIZONS))), list(range(len(matrix)))
    scores = [[None if pd.isna(value) else float(value) for value in row] for row in matrix.to_numpy()]
    text = [["" if value is None else f"{value:.2f}" for value in row] for row in scores]
    hover = [
        [f"{method} · {h} wk<br>{_wape(value)} pooled WAPE" for h, value in zip(HORIZONS, row)]
        for method, row in zip(matrix.index, scores)
    ]
    figure = go.Figure(go.Heatmap(
        x=xs, y=ys, z=colors.astype(object).where(colors.notna(), None).to_numpy().tolist(),
        customdata=scores, text=text, texttemplate="%{text}", hovertext=hover,
        hovertemplate="%{hovertext}<extra></extra>", hoverongaps=False,
        textfont={"size": 12, "color": "#182e4c"},
        zmin=0, zmax=1, colorscale=[[0, "#addbd4"], [0.5, "#e4edf2"], [1, "#f3e3d5"]],
        xgap=3, ygap=3, showscale=False, meta={"dataset": study.dataset, "protocol": study.protocol},
    ))
    unavailable = [(x, y) for y, row in enumerate(scores) for x, value in enumerate(row) if value is None]
    if unavailable:
        figure.add_scatter(
            x=[x for x, _ in unavailable], y=[y for _, y in unavailable], mode="text", text="N/A",
            textfont={"size": 11, "color": "#54647b"}, showlegend=False,
            hovertemplate="Not available<extra></extra>",
        )
    focus = HORIZONS.index(horizon)
    figure.add_vrect(x0=focus - 0.5, x1=focus + 0.5, line={"color": "#3a6980", "width": 2})
    figure.update_layout(
        template="plotly_white", height=320, plot_bgcolor="#f5f7fa", margin={"l": 3, "r": 8, "t": 24, "b": 4},
        font={"size": 11, "color": "#40536d"}, hoverlabel={"font_size": 11},
        xaxis={"tickvals": xs, "ticktext": [f"{h} wk" for h in HORIZONS], "side": "top", "range": [-.52, 4.52],
               "fixedrange": True, "showgrid": False, "zeroline": False, "automargin": True},
        yaxis={"tickvals": ys, "ticktext": [_name(m) for m in matrix.index], "range": [len(ys) - .48, -.52],
               "fixedrange": True, "showgrid": False, "zeroline": False, "automargin": True},
    )
    return figure


def pair_figure(study, horizon, strategy, reference):
    if strategy == reference or study.difference(horizon, strategy, reference) is None:
        return None
    methods = (strategy, reference)
    values = [float(study.wape.at[method, horizon]) for method in methods]
    figure = go.Figure(go.Bar(
        x=values, y=[0, 1], orientation="h", width=0.32,
        marker_color=["#087f8c", "#6277a8"], text=[_wape(v) for v in values], textposition="outside",
        textfont={"size": 12}, cliponaxis=False,
        customdata=list(methods), hovertemplate="%{customdata}<br>WAPE %{x:.4f}%<extra></extra>",
    ))
    figure.update_layout(
        template="plotly_white", height=180, margin={"l": 3, "r": 19, "t": 6, "b": 0},
        font={"size": 11, "color": "#40536d"},
        xaxis={"title": "Pooled WAPE (%)", "ticksuffix": "%", "range": [0, (max(values) or 1) * 1.30],
               "gridcolor": "#e2e8f0", "fixedrange": True, "automargin": True},
        yaxis={"tickvals": [0, 1], "ticktext": [_name(m) for m in methods], "range": [1.45, -.45],
               "showgrid": False, "zeroline": False, "fixedrange": True, "automargin": True},
    )
    return figure


def _controls():
    with st.container(key="strategy_controls", horizontal=True, vertical_alignment="bottom", gap="xsmall"):
        dataset = selected("dataset") or st.segmented_control("Retail dataset", DATASETS, default="M5", required=True,
                                      key="strategy_dataset", persist_state="session")
        protocol = st.segmented_control("Evaluation protocol", tuple(PROTOCOL_METHODS), default=V3, required=True,
                                       key="strategy_protocol", persist_state="session")
        with st.popover("Comparison", icon=":material/tune:", key="strategy_options"):
            horizon = st.selectbox("Forecast horizon", HORIZONS, format_func=lambda h: f"{h} wk", index=1,
                                   key="strategy_horizon", persist_state="session")
            methods = PROTOCOL_METHODS[protocol]
            strategy, reference = PREFERRED_PAIRS[protocol]
            strategy = st.selectbox("Strategy", methods, index=methods.index(strategy), format_func=_name,
                                     key=f"strategy_challenger_{protocol}", persist_state="session")
            reference = st.selectbox("Reference strategy", methods, index=methods.index(reference), format_func=_name,
                                      key=f"strategy_reference_{protocol}", persist_state="session")
    return dataset, protocol, horizon, strategy, reference


def _details(study):
    registry = json.loads(data_path("research_overview_sources.json", SOURCE_REGISTRY).read_text(encoding="utf-8"))["artifacts"]
    for key in SOURCES[study.protocol]:
        pin = registry[key]
        source_detail(f'{pin["path"]} · {pin["source_file"]} · {pin["experiment"]} · {pin["run_id"]} · {pin["section"]}')
    primary = registry["strategies" if study.protocol == V3 else "meta_scores"]
    table = study.table().assign(run_id=primary["run_id"])
    with data_section("Pooled WAPE by strategy and horizon", "Full Data Tables"):
        table_view(table.drop(columns=["run_id", "dataset", "protocol"]), hide_index=True, width="stretch")
    if study.eligibility is not None:
        with data_section("R16 development and outer-window eligibility", "Full Data Tables"):
            table_view(study.eligibility.reset_index(), hide_index=True, width="stretch")
    with data_section("Selected dataset and protocol", "CSV Downloads"):
        download_view("Download strategy scores and coverage", table.to_csv(index=False),
                           file_name=f"strategy_scores_{study.dataset.lower()}_{study.protocol.lower()}.csv",
                           mime="text/csv", on_click="ignore", key="strategy_download")
        st.caption("Full source precision. Blank WAPE cells are unavailable. Local research use.")
    with data_section("Strategies in this protocol"):
        descriptions = [
            {"Method": method, "Type": STRATEGIES[method][1], "Definition": STRATEGIES[method][2]}
            for method in study.wape.index
        ]
        table_view(pd.DataFrame(descriptions), hide_index=True, width="stretch")
    with data_section("Chronological evaluation and metric"):
        st.write(
            "The retail target is observed store-week sales. M5 reports unit sales. Favorita’s reported family "
            "sales units can vary. Store eligibility uses the first 108 weeks and the development cut is week 172. "
            "Development targets end before the outer targets begin. Strategies share complete store-week cases "
            "within each retailer, horizon and protocol. Pooled WAPE is 100 × total absolute error ÷ total absolute observed sales."
        )
        if study.protocol == R16:
            st.write(
                "R16 adapts two feature-based strategies using seven original candidates. Inputs are CV, seasonal correlation, "
                "zero share and trend measured at the origin. Each horizon needs at least ten complete, positive-demand "
                "development store-origin windows. The loss blend uses softmax temperature 10 WAPE percentage points. "
                "The later convex blend is scored as a reference alongside the adapted models."
            )
        else:
            st.write(
                "Selection uses the arithmetic mean of origin-level development WAPE. The displayed results pool complete "
                "outer case errors. The V3 Ridge controls reproduce the stabilized V2 predictions on the same rows."
            )
    with data_section("Study limits", "Research Limitations"):
        st.write(
            "Outer results are retrospective. Both studies use inspected data and R16 reuses the V3 outer cases. "
            "A forecast origin starts a forecast window, and rolling windows can overlap. "
            "V3 and R16 stay separate from R19 inference and the original Warehouse Operations study."
        )


def _pair_panel(study, horizon, strategy, reference):
    st.subheader("Selected strategies")
    counts = study.coverage.loc[horizon]
    st.markdown(
        f'<p class="strategy-scope">{horizon} wk · {counts.evaluated_origins} evaluated origins · '
        f'{counts.disjoint_origins} disjoint · {counts.complete_store_weeks:,} store-week cases</p>',
        unsafe_allow_html=True,
    )
    figure = pair_figure(study, horizon, strategy, reference)
    if figure is not None:
        st.plotly_chart(figure, width="stretch", theme=None, config=CHART_CONFIG, key="strategy_pair_chart")
        st.caption("Same scored cases · lower WAPE is better")
    elif strategy != reference:
        st.markdown(
            f"**{_name(strategy)}** · {_wape(study.wape.at[strategy, horizon])}  \n"
            f"**{_name(reference)}** · {_wape(study.wape.at[reference, horizon])}"
        )
        st.caption("A paired difference requires both scores.")
    name, kind, definition = STRATEGIES[strategy]
    st.markdown(f"**{name}** · {kind}")
    st.caption(definition)


def render_model_strategies():
    st.markdown(CSS, unsafe_allow_html=True)
    with st.container(key="strategies_page"):
        dataset, protocol, horizon, strategy, reference = _controls()
        try:
            study = load_strategy_study(dataset, protocol)
        except (DataIssue, OSError, ValueError) as error:
            research_unavailable(error)
            return

        with st.container(key="strategy_finding"):
            st.markdown(finding(study, horizon, strategy, reference))
        annual = study.annual_disjoint
        annual_text = (f"M5 has {annual['M5']} disjoint origins and Favorita has {annual['Favorita']}"
                       if len(annual) == len(DATASETS) else f"{dataset} has {annual[dataset]} disjoint origins")
        boundary(f"These are retrospective comparisons on previously inspected data. At 52 weeks, {annual_text}.")
        with st.container(key="strategy_panels"):
            matrix, comparison = st.columns([1.65, 1])
            with matrix, panel("strategy_matrix", "Strategy performance"):
                st.subheader("Strategy performance")
                st.markdown(f'<p class="strategy-scope">{PROTOCOL_LABELS[protocol]} · Pooled WAPE (%) · Teal marks '
                            'lower error within complete columns</p>', unsafe_allow_html=True)
                st.plotly_chart(strategy_matrix(study, horizon), width="stretch", theme=None,
                                config=CHART_CONFIG, key="strategy_matrix_chart")
                if study.wape.isna().any().any():
                    annual_meta = study.eligibility.loc[52] if study.eligibility is not None else None
                    if annual_meta is not None and annual_meta.status != "ESTIMABLE":
                        st.caption(f"N/A · Not available. At 52 weeks, {annual_meta.development_windows_eligible} of "
                                   f"{annual_meta.development_windows_total} development windows qualified.")
                    else:
                        st.caption("N/A · Not available")
            with comparison, panel("strategy_pair", "Selected strategies"):
                _pair_panel(study, horizon, strategy, reference)
        _details(study)
