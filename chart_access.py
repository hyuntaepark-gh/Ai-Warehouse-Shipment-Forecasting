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
    current_chart: str | None = None
    in_details: bool = False

_access = ContextVar('warehouse_iq_page_access', default=None)

CSS='''<style>
.st-key-wiq_data_access{display:flex;justify-content:flex-end;margin:0;}
[class*="st-key-chart_toolbar_"]{padding:0!important;background:transparent!important;border:0!important;}
[class*="st-key-chart_toolbar_"] [data-testid="stHorizontalBlock"]{display:grid!important;grid-template-columns:minmax(85px,1fr) 128px 32px 32px!important;align-items:center!important;gap:6px!important;}
[class*="st-key-chart_toolbar_"] [data-testid="stColumn"]{min-width:0!important;width:100%!important;}
[class*="st-key-chart_toolbar_"] [data-testid="stPopover"] button{padding:4px!important;width:32px!important;min-height:33px!important;border-color:#dfe6ef!important;box-shadow:none!important;}
[class*="st-key-chart_toolbar_"] [data-testid="stWidgetLabel"]{display:none;}
[class*="st-key-chart_toolbar_"] [data-baseweb="select"]{font-size:12px;}
[class*="st-key-chart_toolbar_"] [data-testid="stPopoverButton"] [data-testid="stIconMaterial"]{display:none!important;}
.wiq-chart-title{font-size:15px;font-weight:700;color:#182e4c;line-height:1.4;margin:0;}
.wiq-chart-scope{font-size:11px;line-height:1.4;color:#526278;margin:2px 0 0;}
.st-key-wiq_explore [data-testid="stButton"] button{min-height:34px!important;padding:5px 10px!important;}
.st-key-wiq_toolbar_comparison{background:transparent!important;border:0!important;padding:0!important;max-width:430px;}
[data-testid="stPopoverBody"]{max-width:min(850px,94vw)!important;max-height:78vh!important;overflow-y:auto!important;}
[data-testid="stPopoverBody"][aria-label="⋯"]{width:min(320px,94vw)!important;max-width:min(320px,94vw)!important;}
[data-testid="stPopoverBody"] [data-testid="stTabs"] [role="tablist"]{flex-wrap:wrap;gap:3px;}
[data-testid="stPopoverBody"] [data-testid="stMetric"]{min-height:0!important;}
.wiq-insight-grid{display:block!important;}
.wiq-compact-finding{font-size:13px;line-height:1.5;color:#40536d;border-left:3px solid #087f8c;padding:6px 12px;margin:4px 0 10px;}
.wiq-compact-finding strong{color:#182e4c;}
@media(max-width:600px){[class*="st-key-chart_toolbar_"] [data-testid="stColumn"]{width:auto!important;flex:1 1 auto!important;}[class*="st-key-chart_toolbar_"] [data-testid="stColumn"]:last-child{flex:0 0 40px!important;}.wiq-chart-title{font-size:14px;}[data-testid="stMainBlockContainer"]{padding-top:4rem!important;}}
</style>'''


def start_data_center(page):
    st.markdown(CSS,unsafe_allow_html=True)
    with st.container(key='wiq_data_access'):
        _, action=st.columns([5,1.5])
        with action:
            with st.popover('Data & Methods',icon=':material/database:',key='wiq_data_center',on_change='rerun',width='content'):
                st.markdown('**'+page+' · Data & Methods**')
                tabs=st.tabs(CATEGORIES)
                sections=dict(zip(CATEGORIES,tabs))
    _access.set(PageAccess(sections))


def _open_data():
    st.session_state['wiq_data_center']=True


def chart_header(key,title=None,scope=''):
    access=_access.get()
    if access is None:
        return None
    if key not in access.headers:
        title=title or TITLES.get(key,key.replace('_',' ').title())
        has_view=key in {'holdout_demand','holdout_comparison'}
        has_settings=key in {'holdout_demand','comparison_ranked','validation_backtest','future_projection_chart'}
        columns=f"minmax(85px,1fr) {128 if has_view else 0}px {32 if has_settings else 0}px 32px"
        st.markdown(f'<style>.st-key-chart_toolbar_{key} [data-testid="stHorizontalBlock"]{{grid-template-columns:{columns}!important;}}</style>',unsafe_allow_html=True)
        with st.container(key='chart_toolbar_'+key):
            heading,view,settings,actions=st.columns([6,2,0.8,0.8],vertical_alignment='center')
            with heading:
                st.markdown(f'<p class="wiq-chart-title">{escape(title)}</p>',unsafe_allow_html=True)
                if scope:
                    st.markdown(f'<p class="wiq-chart-scope">{escape(scope)}</p>',unsafe_allow_html=True)
            with actions:
                more=st.popover('⋯',help='Chart actions: '+title,key='chart_more_'+key,width='content')
            with more:
                st.caption(title+' · displayed selection')
                st.button('Data & Methods',key='chart_methods_'+key,on_click=_open_data,icon=':material/info:')
                st.caption('Sources, full tables, CSV exports and interpretation limits are available in the page data center. Material evaluation boundaries remain visible beside the analysis.')
        access.headers[key]=dict(view=view,settings=settings,more=more,options=None)
    access.current_chart=key
    return access.headers[key]


def chart_options(key,title=None):
    header=chart_header(key,title)
    if header is None:
        return st.popover('Chart settings',icon=':material/tune:',width='content')
    if header['options'] is None:
        with header['settings']:
            header['options']=st.popover('⚙',help='Customize '+(title or TITLES.get(key,'chart')),key='chart_options_'+key,width='content')
    return header['options']


def chart_view(key):
    header=chart_header(key)
    return header['view'] if header else st.container()


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
    previous, chart=access.in_details,access.current_chart
    access.in_details=True
    try:
        with access.sections[category]:
            st.markdown('#### '+title)
            yield
    finally:
        access.in_details,access.current_chart=previous,chart


def source_detail(text):
    access=_access.get()
    if access:
        if text not in access.sources:
            access.sources.add(text)
            with access.sections['Data Sources']:
                st.caption(text)
        if access.current_chart:
            with access.headers[access.current_chart]['more']:
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
            with access.sections['Data Sources']:
                st.caption(source)
        if access.current_chart:
            with access.headers[access.current_chart]['more']:
                st.download_button('Download displayed CSV',data,file_name=filename,mime='text/csv',key=key+'_chart',on_click='ignore')
    else:
        st.dataframe(readable_table(frame),hide_index=True,width='stretch')
        st.download_button(label,data,file_name=filename,mime='text/csv',key=key,on_click='ignore')
