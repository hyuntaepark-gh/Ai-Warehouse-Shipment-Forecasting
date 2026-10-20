"""Reusable product UI primitives, activated only inside the operational workspace."""
from html import escape
from contextlib import contextmanager

import streamlit as st
from chart_access import chart_header, chart_options, chart_view, data_section, filters, download_frame, source_detail

BLUE = "#2866c9"
INK = "#192b44"
CSS = """<style>
body:has(.st-key-ops_product) [data-testid="stMainBlockContainer"] {max-width:1440px!important;padding:1.1rem 2rem 3rem!important;}
body:has(.st-key-ops_product) [data-testid="stAppHeader"] {background:transparent;}
.st-key-ops_product {font-family:Inter,system-ui,-apple-system,"Segoe UI",sans-serif;color:#192b44;container-type:inline-size;}
.st-key-ops_product p {line-height:1.5;}
.st-key-ops_product [data-testid="stVerticalBlock"] {gap:14px;}
.ops-brand {display:flex;gap:10px;align-items:center;font-size:13px;font-weight:750;letter-spacing:.015em;color:#192b44;}
.ops-brand b {background:#192b44;color:#fff;padding:5px 9px;border-radius:7px;font-size:19px;}
.ops-brand span {color:#68768a;font-size:12px;font-weight:500;margin-left:12px;}
.ops-heading {display:flex;justify-content:space-between;align-items:center;gap:12px;margin:0;}
.ops-heading h1 {font-size:30px!important;font-weight:720;letter-spacing:-.04em;line-height:1.2;margin:0;padding:0;}
.ops-archive {font-size:12px;font-weight:650;white-space:nowrap;border:1px solid #d5dfed;border-radius:20px;padding:6px 12px;background:#fff;color:#526278;}
.ops-lead {font-size:16px;color:#34465f;margin:0;line-height:1.55;}
.ops-lead strong {color:#192b44;font-weight:700;}
.ops-boundary {font-size:12px;color:#526278;line-height:1.55;margin:0;}
.st-key-ops_filters {background:#eaf0f8;border-radius:10px;padding:8px 14px;}
.st-key-ops_product [data-testid="stWidgetLabel"] p {font-size:12px!important;color:#526278;font-weight:600;}
.st-key-ops_product [data-testid="stButtonGroup"] button {font-size:13px!important;border-radius:7px!important;min-height:34px;}
.st-key-ops_product [data-testid="stButtonGroup"] button[aria-pressed="true"] {background:#192b44!important;color:#fff!important;border-color:#192b44!important;}
.st-key-ops_product [data-testid="stButtonGroup"] button[aria-checked="true"] {background:#192b44!important;color:#fff!important;border-color:#192b44!important;}
.st-key-ops_topbar [data-testid="stHorizontalBlock"] {flex-wrap:nowrap;align-items:center;}
.st-key-ops_topbar [data-testid="stColumn"] {min-width:0!important;}
.st-key-ops_product [class*="st-key-ops_kpi_"] {background:#fff;padding:17px 20px;border-radius:12px;border:1px solid #e3e9f2;height:100%;}
.st-key-ops_product .st-key-ops_kpi_0 {background:#192b44;border-color:#192b44;}
.st-key-ops_product [data-testid="stMetric"] {padding:0!important;min-height:0!important;background:none!important;border:none!important;}
.st-key-ops_product [data-testid="stMetricLabel"] p {font-size:13px!important;white-space:normal;color:#526278!important;}
.st-key-ops_product [data-testid="stMetricValue"] {font-size:32px!important;line-height:1.3;font-weight:650;letter-spacing:-.04em;color:#192b44!important;}
.st-key-ops_product [data-testid="stCaptionContainer"] p {font-size:12px!important;color:#526278!important;}
.st-key-ops_product .st-key-ops_kpi_0 [data-testid="stMetricLabel"] p,
.st-key-ops_product .st-key-ops_kpi_0 [data-testid="stCaptionContainer"] p {color:#d2deed!important;}
.st-key-ops_product .st-key-ops_kpi_0 [data-testid="stMetricValue"] {color:#fff!important;}
.st-key-ops_product [data-testid="stHorizontalBlock"]:has(.ops-kpi-marker) {display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:16px;}
.st-key-ops_product [data-testid="stHorizontalBlock"]:has(.ops-kpi-marker)>[data-testid="stColumn"] {width:auto!important;min-width:0;}
.st-key-ops_product [data-testid="stColumn"]:has(.ops-kpi-marker)>[data-testid="stVerticalBlock"],
.st-key-ops_product [data-testid="stLayoutWrapper"]:has([class*="st-key-ops_kpi_"]) {height:100%;}
.st-key-ops_product [data-testid="stElementContainer"]:has(.ops-kpi-marker) {display:none;}
.st-key-ops_product [class*="st-key-ops_panel_"] {background:#fff;border:1px solid #e3e9f2;border-radius:12px;padding:20px 22px;}
.ops-panel-title {font-size:17px;font-weight:700;letter-spacing:-.02em;margin:0;color:#192b44;}
.ops-panel-sub {font-size:12px;color:#526278;margin:3px 0 12px;line-height:1.4;}
.st-key-ops_product [data-testid="stPlotlyChart"] {background:transparent;border:0;padding:0;border-radius:0;}
.ops-compare-head,.ops-compare-row {display:grid;grid-template-columns:88px 1fr 58px 58px;gap:12px;align-items:center;}
.ops-compare-head {font-size:10px;letter-spacing:.06em;text-transform:uppercase;color:#526278;padding:0 0 10px;}
.ops-compare-row {padding:13px 0;border-top:1px solid #eef1f5;}
.ops-wh {font-size:14px;font-weight:650;}
.ops-track {height:10px;background:#eaf0f8;border-radius:5px;overflow:hidden;}
.ops-track span {display:block;height:100%;background:#2866c9;border-radius:5px;}
.ops-ratio {font-size:15px;font-weight:700;text-align:right;font-variant-numeric:tabular-nums;}
.ops-label {font-size:11px;border:1px solid #d5dfeb;background:#f7f9fc;color:#40516a;padding:3px 5px;border-radius:5px;text-align:center;}
.ops-scale {font-size:11px;color:#526278;margin:10px 0 0;}
.ops-insight-grid {display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px;margin:2px 0 8px;}
.ops-insight {background:#fff;border:1px solid #e3e9f2;border-radius:12px;padding:18px 20px;}
.ops-insight small {font-size:10px;font-weight:750;letter-spacing:.08em;text-transform:uppercase;color:#526278;}
.ops-insight strong {display:block;font-size:17px;line-height:1.4;margin:7px 0;color:#192b44;}
.ops-insight p {font-size:13px;line-height:1.6;color:#526278;margin:0;}
.ops-fact-grid {display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px;padding:10px 0 0;}
.ops-fact-grid small {font-size:12px;color:#526278;display:block;}
.ops-fact-grid b {font-size:19px;font-weight:650;display:block;margin-top:4px;}
.st-key-ops_product [data-testid="stExpander"] {border:1px solid #e3e9f2;border-radius:10px;}
.st-key-ops_product button:focus-visible {outline:3px solid #2866c9!important;outline-offset:3px;}
@media(max-width:900px) {
 .st-key-ops_product [data-testid="stHorizontalBlock"]:has(.ops-kpi-marker) {grid-template-columns:repeat(2,minmax(0,1fr));}
 .st-key-ops_primary_row [data-testid="stHorizontalBlock"],.st-key-ops_panel_detail [data-testid="stHorizontalBlock"] {flex-direction:column!important;}
 .st-key-ops_primary_row [data-testid="stColumn"],.st-key-ops_panel_detail [data-testid="stColumn"] {width:100%!important;min-width:0;flex:1 1 100%!important;}
 .ops-insight-grid {grid-template-columns:1fr;}
}
@media(max-width:600px) {
 body:has(.st-key-ops_product) [data-testid="stMainBlockContainer"] {padding:1rem .9rem 2rem!important;}
 .ops-heading {align-items:flex-start;flex-direction:column;gap:7px;}
 .ops-heading h1 {font-size:26px!important;}
 .ops-brand span {display:none;}
 .ops-brand {font-size:11px;gap:7px;}
 .st-key-ops_topbar [data-testid="stColumn"] {width:auto!important;flex:1 1 auto!important;}
 .st-key-ops_topbar [data-testid="stColumn"]:last-child {flex:0 0 93px!important;}
 .ops-lead {font-size:14px;}
 .st-key-ops_product [class*="st-key-ops_kpi_"] {padding:13px;}
 .st-key-ops_product [data-testid="stMetricValue"] {font-size:27px!important;}
 .st-key-ops_product [class*="st-key-ops_panel_"] {padding:16px 12px;}
 .st-key-ops_filters [data-testid="stHorizontalBlock"] {flex-direction:column;}
 .st-key-ops_filters [data-testid="stColumn"] {width:100%!important;min-width:0;}
 .st-key-ops_warehouses [role="toolbar"] {display:grid!important;grid-template-columns:repeat(2,minmax(0,1fr));gap:6px;overflow:visible!important;}
 .st-key-ops_warehouses [data-testid="stButtonGroup"] {overflow:visible!important;}
 .ops-compare-head,.ops-compare-row {grid-template-columns:78px 1fr 46px 50px;gap:7px;}
 .ops-ratio {font-size:13px;}
 .ops-wh {font-size:13px;}
 .st-key-ops_panel_heatmap .annotation {display:none;}
 .ops-fact-grid {gap:10px;}
 .ops-fact-grid b {font-size:17px;}
}
</style>"""


def apply_workspace():
    st.markdown(CSS, unsafe_allow_html=True)


def workspace_header():
    st.markdown('<div class="ops-brand">FORECAST &amp; PLANNING <span>Archived research / Decision support</span></div>', unsafe_allow_html=True)
    st.markdown('<header class="ops-heading"><h1>Planning Insights</h1><span class="ops-archive">ARCHIVED · 25 DEC 2016 ORIGIN</span></header>', unsafe_allow_html=True)


def kpis(items):
    for index, (column, item) in enumerate(zip(st.columns(4), items)):
        with column, st.container(key=f"ops_kpi_{index}"):
            st.markdown('<i class="ops-kpi-marker"></i>', unsafe_allow_html=True)
            st.metric(item[0], item[1])
            st.caption(item[2])


@contextmanager
def panel(key, title, subtitle=""):
    with st.container(key="ops_panel_" + key):
        if key not in {"heatmap", "detail"}:
            st.markdown(f'<div class="ops-panel-title">{escape(title)}</div><div class="ops-panel-sub">{escape(subtitle)}</div>', unsafe_allow_html=True)
        yield


def chart(figure, key, height=300):
    chart_header(key)
    figure.update_layout(template="plotly_white", height=height, font=dict(family="Arial, sans-serif",size=14,color=INK),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=12,r=18,t=12,b=32), hoverlabel=dict(font_size=14),
        legend=dict(orientation="h",y=-.23,x=0,title_text="",font_size=12))
    figure.update_xaxes(rangeslider_visible=False, automargin=True, showgrid=False, tickfont_size=13)
    figure.update_yaxes(automargin=True, gridcolor="#edf1f7", zeroline=False, tickfont_size=13)
    st.plotly_chart(figure, key=key, width="stretch", config={"displaylogo":False,"responsive":True})


def insight_cards(items):
    cards = []
    for kind, title, body in items:
        cards.append(f'<article class="ops-insight"><small>{escape(kind)}</small><strong>{escape(title)}</strong><p>{escape(body)}</p></article>')
    st.markdown('<div class="ops-insight-grid">' + "".join(cards) + '</div>', unsafe_allow_html=True)
