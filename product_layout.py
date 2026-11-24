"""Theme and the publication hold message for public navigation."""
import streamlit as st
from release_policy import PUBLIC_HOLD

CSS = """<style>
[data-testid="stElementContainer"]:has([data-testid="stMarkdownContainer"]>style:only-child){display:none;}
:root{--wiq-navy:#182e4c;--wiq-teal:#087f8c;--wiq-muted:#526278;--wiq-line:#e2e8f0;}
[data-testid="stMainBlockContainer"]{max-width:1480px!important;padding:3.65rem 2rem 3rem!important;}
[data-testid="stMainBlockContainer"] [data-testid="stVerticalBlock"]{gap:11px;}
[data-testid="stAppHeader"]{background:transparent;}
h1{font-size:32px!important;line-height:1.18!important;letter-spacing:-.045em!important;padding:0!important;}
h3{font-size:17px!important;line-height:1.35!important;margin:0!important;padding:0!important;}
.st-key-workspace_header{gap:3px!important;}
.st-key-workspace_header [data-testid="stMarkdownContainer"]:has(>.wiq-eyebrow){margin-bottom:0!important;}
.st-key-workspace_title [data-testid="stHeading"]{min-width:0;}
.st-key-workspace_title .st-key-wiq_data_access{flex-shrink:0;}
.wiq-hero{margin:0 0 5px;}
.bi-finding{padding:10px 14px!important;margin:5px 0!important;}.bi-finding strong{font-size:15px!important;}.bi-finding p{font-size:12px!important;}
.wiq-eyebrow{display:block;min-height:24px;padding-bottom:6px;font-size:11px!important;font-weight:750;line-height:15px!important;letter-spacing:.1em;color:#087f8c;text-transform:uppercase;margin:0;}
.wiq-lead{font-size:16px;line-height:1.45;color:#34465f;max-width:900px;margin:0;}
.wiq-chips{display:flex;gap:6px;flex-wrap:wrap;margin:5px 0 2px;}
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
.wiq-mini-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(145px,1fr));gap:10px;}
.wiq-mini{min-width:0;padding:10px 13px;background:#fff;border:1px solid #e2e8f0;border-radius:10px;}
.wiq-mini small{font-size:11px;color:#526278;display:block;}
.wiq-mini b{font-size:23px;letter-spacing:-.035em;color:#182e4c;display:block;margin:3px 0;}
.wiq-mini span{font-size:11px;color:#526278;}
.wiq-boundary{font-size:13px!important;line-height:1.45;padding:8px 12px;background:#fff8ea;border:1px solid #eee1c7;border-radius:7px;color:#68532c;margin:0;}
.wiq-scope{font-size:13px!important;color:var(--wiq-muted);line-height:1.45;margin:0;}
[data-testid="stMetric"]{min-height:91px!important;padding:13px 16px!important;border-radius:11px!important;}
[data-testid="stMetricValue"]{font-size:27px!important;}
[data-testid="stMetricLabel"] p{font-size:11px!important;}
[data-testid="stCaptionContainer"]{opacity:1!important;}
[data-testid="stCaptionContainer"] p{font-size:12px!important;line-height:1.4!important;}
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
@media(max-width:920px){[data-testid="stMainBlockContainer"]{padding:3.65rem 1.15rem 2rem!important;}.wiq-insight-grid{grid-template-columns:1fr;}.wiq-mini-grid{grid-template-columns:repeat(2,minmax(0,1fr));}.st-key-wiq_hero_row [data-testid="stHorizontalBlock"]{flex-direction:column;}.st-key-wiq_hero_row [data-testid="stColumn"]{width:100%!important;}}
@media(max-width:600px){h1{font-size:25px!important;}.wiq-lead{font-size:14px;}[class*="st-key-wiq_panel_"]{padding:12px;}.wiq-mini b{font-size:20px;}.wiq-mini{padding:8px 10px;}.st-key-workspace_title button p{font-size:12px!important;}.st-key-workspace_title button{min-height:34px!important;padding:4px 7px!important;}.st-key-workspace_title [data-testid="stIconMaterial"]{font-size:16px!important;}}
@media(prefers-reduced-motion:reduce){[data-testid="stPlotlyChart"] .modebar{transition:none;}}
</style>"""

def apply_product_theme():
    st.markdown(CSS, unsafe_allow_html=True)

def publication_hold(title, study):
    """Show a result-free availability state before importing any study loaders."""
    st.title(title)
    st.caption(study)
    st.info(PUBLIC_HOLD, icon=":material/lock:")
    st.markdown("This public preview shows the study navigation. "
                "Charts, tables and downloads are withheld pending approval for their release.")
