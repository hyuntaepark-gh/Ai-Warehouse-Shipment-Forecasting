"""Shared, presentation-only BI design primitives.

No forecasting, numerical transformations or source-file writes occur here.
Material caveats remain in their original page views.
"""
from html import escape
from navigation import LABELS

import streamlit as st

INK = "#172b4d"
TEAL = "#087f8c"
MUTED = "#526278"
GRID = "#e8edf3"
WAREHOUSE_COLORS = {"Whse_A": "#087f8c", "Whse_C": "#916128", "Whse_J": "#5168ac", "Whse_S": "#9c6389"}
MODEL_PALETTE = ["#087f8c", "#916128", "#5168ac", "#9c6389", "#7855a3", "#63748b", "#357e72", "#b07348"]

STORIES = {
    "Historical Demand": (
        "DEMAND EXPLORER · OBSERVED RECORDS",
        "Historical Demand Analysis",
        "How did recorded demand evolve over time?",
        "Explore observed weekly order demand, compare recorded years and see variation across warehouse samples. This page does not score forecasts.",
        "2014–2016 aggregate sample", "Warehouse view: 51 weeks in 2016",
    ),
    "Model Comparison": (
        "FORECAST LAB · COMPARABLE EVALUATIONS",
        "Model Comparison",
        "Which forecasting approach performed best in each test?",
        "Explore error rankings within the same evaluation group, then examine aligned predictions. Results from different horizons are deliberately kept separate.",
        "WAPE · MAE · RMSE", "No cross-cohort rankings",
    ),
    "Warehouse Analytics": (
        "NETWORK EXPLORER · LOCATION DETAIL",
        "Warehouse Analytics",
        "What changes from warehouse to warehouse?",
        "Compare recorded demand, within-warehouse forecast scores and a separate reconciliation diagnostic. A 51-week observation sample is not a full calendar year.",
        "Four warehouses", "Observed sample: 51 weeks",
    ),
    "Model Validation": (
        "MODEL ASSURANCE · RESEARCH EVIDENCE",
        "Model Validation",
        "How much confidence can we place in the results?",
        "Investigate backtests, time stability, external evidence and diagnostics. Validation limitations are part of the research findings, not fine print.",
        "Historical experiments", "Exploratory ≠ independent",
    ),
    "Future Forecasting": (
        "PLANNING OUTLOOK · ARCHIVED PROJECTIONS",
        "Future Forecasting",
        "What did the model project at the end of 2016?",
        "Inspect the saved 4-, 8- and 12-week forecast outlook by warehouse. These are historical projections, not current or live demand forecasts.",
        "Origin: 25 Dec 2016", "No complete 2017 evaluation outcomes",
    ),
    "Operational Insights": (
        "DECISION SUPPORT · ILLUSTRATIVE INDICATORS",
        "Operational Insights",
        "Where might a planner want to investigate further?",
        "Explore source-reported demand risk, historical monitoring and illustrative scenarios. None of these indicators establishes actual constraints or financial savings.",
        "Archived evidence", "Not a live alert system",
    ),
}

GLOBAL_CSS = """
<style>
:root {--bi-ink:#172b4d;--bi-teal:#087f8c;--bi-muted:#526278;--bi-line:#dfe5ef;--bi-canvas:#f5f7fb;}
[class*="st-key-bi_page_intro"]{background:#fff;border:1px solid #e2e8f0;border-radius:16px;padding:25px 30px 22px;margin-bottom:22px;}
[class*="st-key-bi_page_intro"] h1{font-size:clamp(1.85rem,2.6vw,2.6rem);line-height:1.13;margin:0;letter-spacing:-.045em;}
.bi-eyebrow{font-weight:750;font-size:11px;letter-spacing:.11em;text-transform:uppercase;color:#087f8c;margin:0 0 8px;}
.bi-question{font-size:18px;font-weight:650;color:#172b4d;line-height:1.4;}
.bi-intro-desc{font-size:15px;color:#526278;max-width:850px;line-height:1.62;margin:0;}
html, body, [data-testid="stApp"] {font-family:system-ui,-apple-system,"Segoe UI",Arial,sans-serif;color:var(--bi-ink);}
[data-testid="stAppViewContainer"]{background:#f5f7fb;}
[data-testid="stMainBlockContainer"],.block-container{max-width:1370px!important;padding-top:2.2rem!important;padding-bottom:4rem!important;}
[data-testid="stSidebar"] {background:#fff;border-right:1px solid var(--bi-line);}
[data-testid="stSidebar"] [data-testid="stSidebarContent"] {padding-top:1.5rem;}
h1,h2,h3,[data-testid="stHeading"] {color:#172b4d;letter-spacing:-.03em;}
h2 {font-size:1.5rem!important;line-height:1.3!important;margin-top:1rem!important;}
h3 {font-size:1.22rem!important;}
p {line-height:1.55;}
[data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] p{font-size:13px!important;color:#526278!important;line-height:1.5!important;}
.bi-hero {background:#fff;border:1px solid #e2e8f0;border-radius:16px;padding:27px 32px 25px;margin:0 0 22px;}
.bi-hero .bi-eyebrow{font-weight:750;font-size:11px;letter-spacing:.11em;text-transform:uppercase;color:#087f8c;margin-bottom:10px;}
.bi-hero h1{font-size:clamp(1.85rem,2.6vw,2.6rem);letter-spacing:-.045em;margin:0 0 10px;line-height:1.13;}
.bi-hero .bi-question{font-size:18px;font-weight:650;line-height:1.4;color:#172b4d;margin:2px 0 8px;}
.bi-hero p{font-size:15px;color:#526278;line-height:1.62;margin:0;max-width:850px;}
.bi-pills{display:flex;flex-wrap:wrap;gap:9px;margin-top:18px;}
.bi-pills span{border:1px solid #d6e5e5;border-radius:999px;background:#f1f8f7;padding:6px 11px;font-size:12px;font-weight:650;color:#16606b;}
.bi-finding {margin:15px 0 18px;padding:17px 20px;background:#eaf5f5;border-left:4px solid #087f8c;border-radius:0 12px 12px 0;}
.bi-finding strong{display:block;color:#172b4d;font-size:16px;margin-bottom:5px;line-height:1.4;}
.bi-finding p{margin:0;color:#43596f;font-size:14px;line-height:1.6;}
.bi-divider{height:1px;background:#e1e7f0;margin:21px 0;}
[data-testid="stMetric"] {background:#fff;border:1px solid #e1e8f0;border-radius:12px;padding:19px 18px;min-height:115px;}
[data-testid="stMetricLabel"] p{font-size:13px!important;color:#526278!important;white-space:normal;}
[data-testid="stMetricValue"]{font-size:clamp(1.45rem,2vw,2rem)!important;color:#172b4d!important;letter-spacing:-.035em;}
[data-testid="stPlotlyChart"] {background:#fff;border-radius:12px;border:1px solid #e5eaf1;overflow:hidden;padding:4px;}
[data-testid="stDataFrame"] {border-radius:10px;overflow:hidden;}
[data-testid="stExpander"] {border:1px solid #e0e7ef;border-radius:10px;background:#fff;}
[data-testid="stExpander"] summary {font-weight:650;font-size:14px;color:#172b4d;}
[data-testid="stAlert"]{border-radius:10px;}
[data-testid="stTabs"] [role="tab"] {font-weight:650;font-size:14px;}
.stButton>button,.stDownloadButton>button {border-radius:9px;min-height:38px;font-weight:600;}
button:focus-visible,[role="radio"]:focus-visible {outline:3px solid #087f8c!important;outline-offset:2px!important;}
[data-testid="stWidgetLabel"] p {font-size:13px;font-weight:650;}
@media(max-width:960px){.block-container{padding-left:1.25rem!important;padding-right:1.25rem!important;}.bi-hero{padding:24px 22px;}}
@media(max-width:640px){.block-container{padding:1rem .8rem 3rem!important;}.bi-hero{padding:20px 16px;border-radius:12px;}[class*="st-key-bi_page_intro"]{padding:20px 16px;border-radius:12px;}.bi-hero .bi-question{font-size:16px;}.bi-hero p{font-size:14px;}[data-testid="stMetric"] {min-height:0;padding:14px;}[data-testid="stHorizontalBlock"] {gap:10px;}}
</style>
"""


def apply_global_theme():
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)


def page_intro(page):
    """Native Streamlit heading retained for keyboard semantics and existing UI tests."""
    from product_layout import header
    eyebrow, title, question, description, first, second = STORIES[page]
    leads = {
        "Historical Demand": "Explore the recorded demand pattern before interpreting a forecast.",
        "Model Comparison": "Compare forecast errors within one compatible evaluation group.",
        "Warehouse Analytics": "Demand scale and variability differ across the four warehouse samples.",
        "Model Validation": "Historical evidence is useful; reused evaluations limit confidence in generalization.",
        "Future Forecasting": "Explore the saved outlook from December 2016, with no complete 2017 evaluation outcomes.",
    }
    header(LABELS[page], leads[page], "Archived study", first, second)



def finding(title, description):
    st.markdown(f'<aside class="bi-finding"><strong>{escape(str(title))}</strong>'
                f'<p>{escape(str(description))}</p></aside>', unsafe_allow_html=True)


def style_plot(figure, height=390):
    """Apply consistent styling without changing any traces, values or axes meanings."""
    figure.update_layout(
        template="plotly_white", height=height,
        margin=dict(l=20, r=48, t=18, b=75),
        font=dict(family='Arial, sans-serif', size=14, color=INK),
        paper_bgcolor='#ffffff', plot_bgcolor='#ffffff',
        legend=dict(orientation='h', y=-.30, x=0, title_text='', font=dict(size=13)),
        hoverlabel=dict(font_size=14),
        hovermode=figure.layout.hovermode or 'closest',
    )
    figure.update_xaxes(rangeslider_visible=False, automargin=True,
                        tickfont=dict(size=13, color=MUTED),
                        title_font=dict(size=13, color=INK), zeroline=False)
    figure.update_yaxes(automargin=True, gridcolor=GRID,
                        tickfont=dict(size=13, color=MUTED),
                        title_font=dict(size=13, color=INK), zeroline=False)
    return figure
