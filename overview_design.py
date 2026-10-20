"""Overview-only design pilot; specialist-page styling remains unchanged."""
from html import escape

import plotly.express as px
import streamlit as st
from chart_access import chart_header, chart_options, chart_view, data_section, filters, download_frame, source_detail
from product_layout import PLOT_CONFIG

INK = "#172b4d"
TEAL = "#087f8c"
MUTED = "#66758c"
FONT = "Arial, sans-serif"
MODEL_COLORS = {"Actual": INK, "TimesFM 3.0": TEAL, "ETS": "#916128", "Seasonal Naive": "#7855a3",
                "XGBoost": TEAL, "Random Forest": "#916128", "Naive": "#7855a3", "Recursive XGBoost": TEAL}
WAREHOUSE_COLORS = {"Whse_A": TEAL, "Whse_C": "#916128", "Whse_J": "#5168ac", "Whse_S": "#9c6389"}

CSS = """
<style>
.block-container:has(.st-key-executive_pilot) {max-width:1320px; padding-top:2.5rem; padding-bottom:3rem;}
.st-key-executive_pilot {font-family:Arial,sans-serif; color:#172b4d; container-type:inline-size; container-name:executive;}
.st-key-executive_pilot h1 {font-size:2.25rem; line-height:1.2; margin:0; letter-spacing:-.035em;}
.st-key-executive_pilot h3 {font-size:1.4rem; line-height:1.35; letter-spacing:-.02em; padding-top:0;}
.st-key-executive_pilot p {line-height:1.6;}
.st-key-executive_pilot [data-testid="stCaptionContainer"] {font-size:14px; color:#526278;}
.st-key-executive_pilot [data-testid="stCaptionContainer"] p {font-size:14px; color:#526278;}
.exec-eyebrow {font-size:12px; font-weight:700; letter-spacing:.1em; color:#526278; margin:0 0 8px;}
.exec-summary {background:#eaf5f5; border-left:3px solid #087f8c; border-radius:0 10px 10px 0; padding:18px 24px; margin:8px 0;}
.exec-summary strong {display:block; font-size:21px; line-height:1.4; margin-bottom:6px;}
.exec-summary p {margin:0; font-size:15px;}
.exec-note {color:#526278; font-size:14px; line-height:1.6; margin:0;}
.st-key-executive_pilot [data-testid="stHorizontalBlock"]:has(.exec-kpi-marker) {display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:16px;}
.st-key-executive_pilot [data-testid="stHorizontalBlock"]:has(.exec-kpi-marker) > [data-testid="stColumn"] {min-width:0; width:auto!important;}
.st-key-executive_pilot [data-testid="stColumn"]:has(.exec-kpi-marker) > [data-testid="stVerticalBlock"],
.st-key-executive_pilot [data-testid="stLayoutWrapper"]:has([class*="st-key-exec_kpi_"]) {height:100%;}
.st-key-executive_pilot [data-testid="stElementContainer"]:has(.exec-kpi-marker) {display:none;}
.st-key-executive_pilot [class*="st-key-exec_kpi_"] {background:#fff; border:1px solid #dfe5ef; border-radius:12px; padding:20px; height:100%;}
.st-key-executive_pilot [data-testid="stMetric"] {border:0; background:transparent; padding:0; border-radius:0;}
.st-key-executive_pilot [data-testid="stMetricLabel"] p {font-size:14px; white-space:normal; color:#526278;}
.st-key-executive_pilot [data-testid="stMetricValue"] {font-size:32px; letter-spacing:-.04em; color:#172b4d;}
.st-key-executive_pilot [data-testid="stPlotlyChart"] {background:#fff; border-radius:12px; overflow:hidden;}
.exec-insight {padding:16px 0; border-top:2px solid #087f8c;}
.exec-insight strong {font-size:17px; display:block; margin-bottom:6px;}
.exec-insight p {font-size:15px; margin:0;}
.exec-warehouse-grid {display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:16px; margin:8px 0 16px;}
.exec-warehouse-grid article {background:#fff; border-radius:10px; padding:16px; border-top:2px solid #087f8c;}
.exec-warehouse-grid span,.exec-warehouse-grid small {color:#526278; font-size:14px;}
.exec-warehouse-grid strong {display:block; font-size:26px; margin:6px 0;}
.exec-warehouse-grid p {font-size:14px; margin:0 0 6px;}
.st-key-executive_pilot [data-testid="stButton"] button {border-color:#c5d3df; border-radius:8px; min-height:44px; color:#172b4d; font-size:14px;}
.st-key-executive_pilot button:focus-visible {outline:3px solid #087f8c; outline-offset:3px;}
@media(max-width:1200px) {
 .st-key-executive_pilot [data-testid="stHorizontalBlock"]:has(.exec-kpi-marker) {grid-template-columns:repeat(2,minmax(0,1fr));}
 .exec-warehouse-grid {grid-template-columns:repeat(2,minmax(0,1fr));}
}
@container executive (max-width:1000px) {
 .st-key-executive_pilot [data-testid="stHorizontalBlock"]:has(.exec-kpi-marker) {grid-template-columns:repeat(2,minmax(0,1fr));}
 .exec-warehouse-grid {grid-template-columns:repeat(2,minmax(0,1fr));}
}
@container executive (max-width:520px) {
 .st-key-executive_pilot [data-testid="stHorizontalBlock"]:has(.exec-kpi-marker) {grid-template-columns:1fr;}
 .exec-warehouse-grid {grid-template-columns:1fr;}
 .st-key-executive_pilot [data-testid="stHorizontalBlock"] {flex-direction:column;}
 .st-key-executive_pilot [data-testid="stColumn"] {min-width:0; width:100%!important;}
}
@media(max-width:700px) {
 .block-container:has(.st-key-executive_pilot) {padding:2rem 1rem;}
 .st-key-executive_pilot h1 {font-size:1.9rem;}
 .st-key-executive_pilot [data-testid="stHorizontalBlock"] {flex-direction:column;}
 .st-key-executive_pilot [data-testid="stColumn"] {min-width:0; width:100%!important;}
 .st-key-executive_pilot [data-testid="stHorizontalBlock"]:has(.exec-kpi-marker) {grid-template-columns:1fr;}
 .exec-summary {padding:16px;}
 .exec-warehouse-grid {grid-template-columns:1fr;}
}
</style>
"""


def apply_design():
    st.markdown(CSS, unsafe_allow_html=True)


def insight(title, text):
    st.markdown(f'<div class="exec-insight"><strong>{escape(title)}</strong><p>{escape(text)}</p></div>', unsafe_allow_html=True)


def kpi_cards(items):
    for index, (column, (label, value, context)) in enumerate(zip(st.columns(4), items)):
        with column, st.container(key=f"exec_kpi_{index}"):
            st.markdown('<span class="exec-kpi-marker"></span>', unsafe_allow_html=True)
            st.metric(label, value)
            st.caption(context)


def style_figure(figure, height=380):
    figure.update_layout(template="plotly_white", height=height,
        font=dict(family=FONT, size=14, color=INK), paper_bgcolor="white", plot_bgcolor="white",
        margin=dict(l=24, r=36, t=20, b=60),
        legend=dict(orientation="h", y=-.30, x=0, title_text="", font_size=13),
        hoverlabel=dict(font_size=14), hovermode="closest")
    figure.update_xaxes(rangeslider_visible=False, automargin=True, showgrid=False,
                        title_font_size=14, tickfont_size=13, zeroline=False)
    figure.update_yaxes(automargin=True, title_font_size=14, tickfont_size=13,
                        gridcolor="#edf0f5", zeroline=False)
    return figure


def show_chart(figure, key, height=380):
    chart_header(key)
    st.plotly_chart(style_figure(figure, height), width="stretch", key=key,
                   config=PLOT_CONFIG)


def error_comparison(frame, metric):
    """Only the caller's compatible cohort; exact minima are all highlighted."""
    ranked = frame.sort_values(metric, kind="stable").copy()
    ranked["Display_Error"] = ranked[metric].map(lambda v: f"{v:.2f}%" if metric == "WAPE (%)" else f"{v:,.0f}")
    figure = px.bar(ranked, y="Model", x=metric, orientation="h", text="Display_Error")
    figure.update_traces(marker_color=[TEAL if x == ranked[metric].min() else MUTED for x in ranked[metric]],
                         textposition="outside", cliponaxis=False,
                         hovertemplate="%{y}<br>%{x:,.4f}" + ("%" if metric == "WAPE (%)" else " demand units") + "<extra></extra>")
    if metric != "WAPE (%)":
        from display_formatting import compact_units
        figure.update_traces(text=ranked[metric].map(compact_units).tolist())
    figure.update_yaxes(autorange="reversed", title_text="")
    figure.update_xaxes(title_text="Forecast error · WAPE (%)" if metric == "WAPE (%)" else f"{metric} · demand units",
                        range=[0, ranked[metric].max() * 1.22], tickformat=".3s" if metric != "WAPE (%)" else None)
    figure.update_layout(showlegend=False)
    return figure, ranked
