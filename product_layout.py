"""Shared presentation components for the seven Warehouse IQ workspaces.

These components display supplied values only. Data contracts and calculations
remain in the existing *_data modules.
"""
from contextlib import contextmanager
from html import escape
import streamlit as st

PLOT_CONFIG = {"displaylogo": False, "responsive": True, "scrollZoom": False,
               "modeBarButtonsToRemove": ["lasso2d", "select2d", "autoScale2d"]}

CSS = """<style>
[data-testid="stElementContainer"]:has([data-testid="stMarkdownContainer"]>style:only-child){display:none;}
:root{--wiq-navy:#182e4c;--wiq-teal:#087f8c;--wiq-muted:#526278;--wiq-line:#e2e8f0;}
[data-testid="stMainBlockContainer"]{max-width:1480px!important;padding:4.2rem 2rem 3rem!important;}
[data-testid="stVerticalBlock"]{gap:14px;}
[data-testid="stAppHeader"]{background:transparent;}
body:has(.st-key-ops_product) [data-testid="stMainBlockContainer"]{padding-top:4.2rem!important;}
h1{font-size:32px!important;line-height:1.18!important;letter-spacing:-.045em!important;padding:0!important;}
h3{font-size:17px!important;line-height:1.35!important;margin:0!important;padding:0!important;}
.wiq-hero{margin:0 0 5px;}
.bi-finding{padding:10px 14px!important;margin:5px 0!important;}.bi-finding strong{font-size:15px!important;}.bi-finding p{font-size:12px!important;}
.wiq-eyebrow{font-size:10px;font-weight:750;letter-spacing:.14em;color:#087f8c;text-transform:uppercase;margin:0 0 7px;}
.wiq-lead{font-size:17px;line-height:1.5;color:#34465f;max-width:1000px;margin:0;}
.wiq-chips{display:flex;gap:7px;flex-wrap:wrap;margin:10px 0 6px;}
.wiq-chip{font-size:10px;font-weight:650;color:#40536d;background:#eaf0f6;border:1px solid #dce5ef;border-radius:5px;padding:4px 8px;white-space:nowrap;}
.wiq-chip:first-child{color:#16606b;background:#e7f3f2;border-color:#cde5e2;}
[class*="st-key-wiq_panel_"]{background:#fff;border:1px solid #e2e8f0;border-radius:13px;padding:18px 20px;}
[class*="st-key-wiq_panel_"] [data-testid="stPlotlyChart"]{border:0;padding:0;border-radius:0;}
.wiq-panel-title{font-size:16px;font-weight:720;color:#182e4c;margin:0;letter-spacing:-.02em;}
.wiq-panel-sub{font-size:11px;color:#526278;margin:3px 0 8px;}
[class*="st-key-wiq_toolbar"]{background:#edf2f8;border:1px solid #e0e7ef;border-radius:10px;padding:10px 14px;}
[class*="st-key-wiq_toolbar"] [data-testid="stWidgetLabel"] p{font-size:11px!important;}
.wiq-insight-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px;margin:2px 0 8px;}
.wiq-insight{background:#fff;border:1px solid #e2e8f0;border-top:3px solid #087f8c;border-radius:10px;padding:13px 16px;}
.wiq-insight:nth-child(2){border-top-color:#b08a48;}
.wiq-insight:nth-child(3){border-top-color:#5168ac;}
.wiq-insight small{font-size:9px;font-weight:750;text-transform:uppercase;letter-spacing:.09em;color:#526278;}
.wiq-insight strong{display:block;font-size:14px;line-height:1.4;color:#182e4c;margin:5px 0;}
.wiq-insight p{font-size:12px;line-height:1.5;color:#526278;margin:0;}
.wiq-mini-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px;}
.wiq-mini{padding:13px 16px;background:#fff;border:1px solid #e2e8f0;border-radius:10px;}
.wiq-mini small{font-size:11px;color:#526278;display:block;}
.wiq-mini b{font-size:23px;letter-spacing:-.035em;color:#182e4c;display:block;margin:3px 0;}
.wiq-mini span{font-size:11px;color:#526278;}
.wiq-boundary{font-size:12px;line-height:1.5;padding:8px 12px;background:#fff8ea;border:1px solid #eee1c7;border-radius:7px;color:#68532c;margin:0;}
[data-testid="stMetric"]{min-height:91px!important;padding:13px 16px!important;border-radius:11px!important;}
[data-testid="stMetricValue"]{font-size:27px!important;}
[data-testid="stMetricLabel"] p{font-size:11px!important;}
[data-testid="stCaptionContainer"] p{font-size:11px!important;line-height:1.4!important;}
[data-testid="stTabs"] [role="tablist"]{gap:8px;border-bottom:1px solid #dfe6ef;padding-bottom:5px;}
[data-testid="stTabs"] [role="tab"]{font-size:12px;background:#eaf0f6;border-radius:6px;padding:7px 13px;height:36px;}
[data-testid="stTabs"] [aria-selected="true"]{background:#182e4c;color:#fff;}
[data-testid="stTabs"] [data-baseweb="tab-highlight"]{display:none;}
[data-testid="stExpander"] summary{font-size:12px!important;}
[data-testid="stAlert"]{padding:9px 12px!important;}
[data-testid="stAlert"] p{font-size:12px!important;line-height:1.5!important;}
[data-testid="stPlotlyChart"] .modebar{opacity:0;transition:opacity .15s;}
[data-testid="stPlotlyChart"]:hover .modebar,[data-testid="stPlotlyChart"]:focus-within .modebar{opacity:1;}
.st-key-wiq_hero_row [data-testid="stColumn"]{min-width:0!important;}
@media(min-width:1000px){.st-key-executive_pilot [data-testid="stHorizontalBlock"]:has(.exec-kpi-marker){grid-template-columns:repeat(4,minmax(0,1fr))!important;}.exec-warehouse-grid{grid-template-columns:repeat(4,minmax(0,1fr))!important;}}
.st-key-executive_pilot [class*="st-key-exec_kpi_"]{gap:5px!important;}
.st-key-executive_pilot [class*="st-key-exec_kpi_"] [data-testid="stVerticalBlock"]{gap:5px!important;}
.exec-warehouse-grid p,.exec-warehouse-grid span,.exec-warehouse-grid small{font-size:11px!important;}
.exec-warehouse-grid strong{margin:2px 0!important;}

.st-key-wiq_explore [data-testid="stButton"] button{justify-content:flex-start;padding:15px 17px;min-height:66px;border:1px solid #dce5ef;background:#fff;}
@media(min-width:1000px){.st-key-wiq_hero_row>[data-testid="stVerticalBlock"]>[data-testid="stHorizontalBlock"]{flex-direction:row!important;}}
@media(max-width:900px){[data-testid="stMainBlockContainer"]{padding:1.2rem!important;}.wiq-insight-grid{grid-template-columns:1fr;}.wiq-mini-grid{grid-template-columns:repeat(2,minmax(0,1fr));}.st-key-wiq_hero_row [data-testid="stHorizontalBlock"]{flex-direction:column;}.st-key-wiq_hero_row [data-testid="stColumn"]{width:100%!important;}}
@media(max-width:600px){h1{font-size:27px!important;}.wiq-lead{font-size:15px;}[class*="st-key-wiq_panel_"]{padding:14px 12px;}.wiq-mini b{font-size:20px;}}
@media(prefers-reduced-motion:reduce){[data-testid="stPlotlyChart"] .modebar{transition:none;}}
</style>"""


def apply_product_theme():
    st.markdown(CSS, unsafe_allow_html=True)


def chips(*items):
    st.markdown('<div class="wiq-chips">' + ''.join(
        f'<span class="wiq-chip">{escape(str(item))}</span>' for item in items) + '</div>', unsafe_allow_html=True)


def header(title, takeaway, *context):
    st.markdown('<div class="wiq-eyebrow">Warehouse IQ / Demand intelligence</div>', unsafe_allow_html=True)
    st.title(title)
    st.markdown(f'<p class="wiq-lead">{escape(takeaway)}</p>', unsafe_allow_html=True)
    chips(*context)


def insights(items):
    # Keep distinct numerical findings; omit repeated navigation/caveat cards.
    item = None
    if items and "lower WAPE vs baseline" in str(items[0][1]):
        item = items[1]  # The TimesFM/ETS gap adds evidence beyond the KPI row.
    elif items and items[0][0] == "Selected outlook":
        item = ("Selected outlook", items[1][1], items[0][2])
    if item:
        _, title, body = item
        st.markdown('<div class="wiq-insight-grid"><p class="wiq-compact-finding"><strong>' + escape(str(title)) + '</strong> · ' + escape(str(body)) + '</p></div>',unsafe_allow_html=True)
    else:
        st.markdown('<div class="wiq-insight-grid"></div>',unsafe_allow_html=True)



def mini_cards(items):
    st.markdown('<div class="wiq-mini-grid">' + ''.join(
        f'<article class="wiq-mini"><small>{escape(str(label))}</small><b>{escape(str(value))}</b><span>{escape(str(context))}</span></article>'
        for label, value, context in items) + '</div>', unsafe_allow_html=True)


@contextmanager
def panel(key, title, subtitle=''):
    with st.container(key='wiq_panel_' + key):
        pass  # The chart toolbar owns its title; the panel provides its surface only.
        yield


def boundary(text):
    st.markdown(f'<p class="wiq-boundary">{escape(text)}</p>', unsafe_allow_html=True)
