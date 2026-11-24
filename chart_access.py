"""Native chart toolbars and one page-level data center; presentation only."""
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass, field
from html import escape
import streamlit as st

TITLES = {
    'holdout_demand':'Observed demand', 'holdout_comparison':'2016 model ranking',
    'holdout_quarters':'Quarterly forecast error', 'warehouse_rolling':'Warehouse model scores',
    'warehouse_recursive':'Recursive backtest', 'retrospective_years':'Earlier forecast origins',
    'retrospective_pooled':'Pooled retrospective errors', 'retrospective_demand':'Earlier demand & predictions',
    'archived_future':'Archived demand outlook', 'history_trend':'Recorded demand',
    'history_comparisons':'Period comparison', 'history_seasonality':'Monthly weekly means',
    'history_variability':'Weekly demand distribution', 'warehouse_actual_trends':'Network demand',
    'warehouse_observed_sums':'Warehouse demand scale', 'warehouse_cv':'Relative demand variability',
    'warehouse_monthly_patterns':'Monthly demand profile', 'warehouse_performance':'Warehouse forecast comparison',
    'warehouse_deep_dive_predictions':'Reconciliation diagnostic', 'comparison_ranked':'Model ranking',
    'comparison_actual_predicted':'Aligned actuals & predictions', 'comparison_reconciliation_plot':'Reconciliation diagnostic',
    'future_projection_chart':'Archived demand outlook', 'future_warehouse_contributions':'Warehouse contributions',
    'ops_weekly_heatmap':'Demand / historical P90 by week', 'ops_warehouse_detail':'Warehouse outlook',
    'ops_bias_chart':'Historical bias', 'ops_monitoring_chart':'Archived monitoring',
    'ops_scenarios_chart':'Illustrative scenarios', 'ops_loss_chart':'Illustrative planning loss',
    'validation_backtest':'Historical backtesting', 'validation_temporal_heatmap':'Error across calendar periods',
    'validation_temporal_trend':'Temporal error pattern', 'validation_external':'External M5 evidence',
    'validation_seeds':'Random-seed stability', 'validation_perturbations':'Exploratory perturbations',
    'validation_calibration':'Empirical interval coverage', 'validation_width':'Interval width',
    'validation_quantile_methods':'Quantile diagnostics', 'validation_bias':'Warehouse bias',
    'validation_monitoring':'Historical monitoring', 'validation_recursive':'Recursive validation',
}
CATEGORIES=['Data Sources','Full Data Tables','CSV Downloads','Methodology','Research Limitations']

@dataclass
class PageAccess:
    sections: dict
    headers: dict = field(default_factory=dict)
    frames: set = field(default_factory=set)
    sources: set = field(default_factory=set)

_access = ContextVar('warehouse_iq_page_access', default=None)

CSS='''<style>
.st-key-wiq_data_access{margin:0;}
[class*="st-key-chart_toolbar_"]{padding:0!important;background:transparent!important;border:0!important;}
[class*="st-key-chart_toolbar_"] [data-testid="stHorizontalBlock"]{display:flex!important;align-items:center!important;gap:8px!important;flex-wrap:wrap;}
[class*="st-key-chart_toolbar_"] [data-testid="stColumn"]{min-width:0!important;width:100%!important;}
[class*="st-key-chart_toolbar_"] [data-testid="stPopover"] button{padding:4px 7px!important;min-height:34px!important;border-color:#dfe6ef!important;box-shadow:none!important;}
[class*="st-key-chart_toolbar_"] [data-testid="stWidgetLabel"]{display:none;}
[class*="st-key-chart_toolbar_"] [data-baseweb="select"]{font-size:12px;}
.wiq-chart-title{font-size:16px!important;font-weight:700;color:#182e4c;line-height:1.4;margin:0;}
.wiq-chart-scope{font-size:12px!important;line-height:1.4;color:#526278;margin:2px 0 0;}
.st-key-wiq_explore [data-testid="stButton"] button{min-height:34px!important;padding:5px 10px!important;}
.st-key-wiq_toolbar_comparison{background:transparent!important;border:0!important;padding:0!important;max-width:430px;}
[data-testid="stPopoverBody"]{max-width:min(850px,94vw)!important;max-height:78vh!important;overflow-y:auto!important;}
[data-testid="stPopoverBody"] [data-testid="stTabs"] [role="tablist"]{flex-wrap:wrap;gap:3px;}
[data-testid="stPopoverBody"] [data-testid="stMetric"]{min-height:0!important;}
.wiq-insight-grid{display:block!important;}
.wiq-compact-finding{font-size:13px;line-height:1.5;color:#40536d;border-left:3px solid #087f8c;padding:6px 12px;margin:4px 0 10px;}
.wiq-compact-finding strong{color:#182e4c;}
@media(max-width:600px){[class*="st-key-chart_toolbar_"] [data-testid="stColumn"]{width:auto!important;flex:1 1 auto!important;}.wiq-chart-title{font-size:15px!important;}}
</style>'''


def _data_center_popover(page, categories):
    with st.popover('Data & Methods',icon=':material/database:',key='wiq_data_center',width='content'):
        st.markdown('**'+page+' · Data & Methods**')
        return dict(zip(categories, st.tabs(categories)))


def start_data_center(page, *, include_downloads=True):
    categories = CATEGORIES if include_downloads else [name for name in CATEGORIES if name != 'CSV Downloads']
    st.markdown(CSS,unsafe_allow_html=True)
    with st.container(key='wiq_data_access', width='content'):
        sections = _data_center_popover(page, categories)
    _access.set(PageAccess(sections))


def chart_header(key,title=None,scope=''):
    access=_access.get()
    if access is None:
        return None
    if key not in access.headers:
        title=title or TITLES.get(key,key.replace('_',' ').title())
        has_view=key in {'holdout_demand','holdout_comparison'}
        has_settings=key in {'holdout_demand','comparison_ranked','validation_backtest','future_projection_chart'}
        with st.container(key='chart_toolbar_'+key):
            widths = [3] + ([1.5] if has_view else []) + ([1.25] if has_settings else [])
            heading, *slots = st.columns(widths,vertical_alignment='center') if len(widths) > 1 else [st.container()]
            view = slots.pop(0) if has_view else None
            settings = slots.pop(0) if has_settings else None
            with heading:
                st.markdown(f'<div class="wiq-chart-title" role="heading" aria-level="3">{escape(title)}</div>',unsafe_allow_html=True)
                if scope:
                    st.markdown(f'<p class="wiq-chart-scope">{escape(scope)}</p>',unsafe_allow_html=True)
        access.headers[key]=dict(view=view,settings=settings,options=None)
    return access.headers[key]


def chart_options(key,title=None):
    header=chart_header(key,title)
    if header is None or header['settings'] is None:
        return st.popover('Options',icon=':material/tune:',width='content')
    if header['options'] is None:
        with header['settings']:
            header['options']=st.popover('Options',help='Customize '+(title or TITLES.get(key,'chart')),key='chart_options_'+key,width='content')
    return header['options']


def chart_view(key):
    header=chart_header(key)
    return (header and header['view']) or st.container()


def filters(label,key):
    return st.popover(label,icon=':material/tune:',key=key,width='content')


@contextmanager
def data_section(title,category='Methodology'):
    access=_access.get()
    if access is None:
        with st.container():
            st.markdown('**'+title+'**')
            yield
        return
    with access.sections[category]:
        st.markdown('#### '+title)
        yield


def source_detail(text):
    access=_access.get()
    if access:
        if text not in access.sources:
            access.sources.add(text)
            with access.sections['Data Sources']:
                st.caption(text)
    else:
        st.caption(text)


def download_frame(frame,name,*,key=None,label='Download CSV',filename=None,sources=()):
    from display_formatting import readable_table
    access=_access.get()
    key=key or 'download_'+name
    filename=filename or name+'.csv'
    data=frame.to_csv(index=False)
    if access and key in access.frames:
        return
    if access:
        access.frames.add(key)
        with access.sections['Full Data Tables']:
            st.markdown('#### '+name.replace('_',' ').title())
            st.dataframe(readable_table(frame),hide_index=True,width='stretch')
        with access.sections['CSV Downloads']:
            st.download_button(label+' · '+name.replace('_',' '),data,file_name=filename,mime='text/csv',key=key,on_click='ignore')
        for source in sources:
            source_detail(source)
    else:
        st.dataframe(readable_table(frame),hide_index=True,width='stretch')
        st.download_button(label,data,file_name=filename,mime='text/csv',key=key,on_click='ignore')
