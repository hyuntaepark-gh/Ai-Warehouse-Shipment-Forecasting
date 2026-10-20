"""Dataset structure and research provenance, separate from model evaluation."""
from html import escape
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from chart_access import chart_header, download_frame, source_detail, data_section
from design_system import style_plot
from foundation_data import load_foundation, CLARIFICATION
from navigation import navigate
from product_layout import header, mini_cards, boundary, panel, PLOT_CONFIG

TEAL='#087f8c'
NAVY='#182e4c'
GOLD='#b08a48'


def open_external_validation():
    st.session_state['validation_section']='External M5 validation'
    st.session_state['validation_tabs']='External validation'
    navigate('Model Validation')


def chart(key,title,figure,frame,source):
    with panel(key,title):
        chart_header('foundation_'+key,title)
        style_plot(figure,height=350)
        st.plotly_chart(figure,key='foundation_'+key,width='stretch',config=PLOT_CONFIG)
        source_detail('Source: '+source+' · precomputed, read-only summary')
        download_frame(frame,'foundation_'+key,key='foundation_download_'+key,
                       label='Download summary CSV')


def pipeline(p):
    steps=[('01 · Raw source',f"{p['records']:,} records",'Signed order demand; repeated rows retained.'),
        ('02 · Usable dates',f"{p['dated_records']:,} records",'Parse dates; exclude 11,239 missing dates. No interpolation.'),
        ('03 · Modeling years',f"{p['modeling_records']:,} records",'2012–2016 only; retain negatives, zeros and high demand.'),
        ('04 · Weekly source',f"{p['weekly_source_records']:,} records",'02 Jan 2012–25 Dec 2016; exclude 1,664 boundary records.'),
        ('05 · Weekly series',f"{p['weekly_observations']:,} observations",'Sum signed demand into Sunday-ending weeks.')]
    st.markdown('''<style>.foundation-flow{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:10px}.foundation-step{border:1px solid #dce5ef;border-top:3px solid #087f8c;border-radius:9px;padding:14px;background:white}.foundation-step small{font-size:10px;color:#087f8c;font-weight:700}.foundation-step b{display:block;font-size:18px;color:#182e4c;margin:8px 0}.foundation-step p{font-size:12px;line-height:1.5;color:#526278;margin:0}@media(max-width:850px){.foundation-flow{grid-template-columns:1fr 1fr}}@media(max-width:500px){.foundation-flow{grid-template-columns:1fr}}</style>''',unsafe_allow_html=True)
    st.markdown('<div class="foundation-flow">'+''.join('<article class="foundation-step"><small>'+escape(a)+'</small><b>'+escape(b)+'</b><p>'+escape(c)+'</p></article>' for a,b,c in steps)+'</div>',unsafe_allow_html=True)


def render_foundation():
    try: info,t=load_foundation()
    except (OSError,ValueError,KeyError) as error:
        header('Data Foundation','Verified dataset summaries are currently unavailable.','Source integrity')
        st.warning('Data Foundation summaries unavailable: '+str(error))
        return
    p,m=info['primary'],info['m5']
    header('Data Foundation','A million demand records become 260 weekly observations. Coverage limits matter before model scores.',
           'Primary source · 2011–2017','Modeling window · 2012–2016','Order demand · not shipments')
    mini_cards([('Raw records',f"{p['records']:,}",'Includes undated records'),
                ('Warehouses',str(p['warehouses']),'Recorded source locations'),
                ('Products',f"{p['products']:,}",'Unique product codes'),
                ('Product categories',str(p['categories']),'Recorded category codes')])
    st.caption(f"Dated source: {p['date_start']} to {p['date_end']} · {p['dated_records']:,} usable-date records · {p['missing_dates']/p['records']:.2%} missing dates.")
    boundary('Source completeness is unverified: 1,048,575 data rows plus a header exactly match Excel’s 1,048,576-row worksheet limit. This is a truncation warning, not proof of truncation. The final row is dated June 2016; the file is not chronologically ordered.')
    tabs=st.tabs(['Coverage','Warehouse & products','Data quality','Research pipeline','M5 external data'])
    with tabs[0]:
        st.subheader('Dense modeling years, sparse edges')
        st.caption('Record counts use actual raw rows with usable dates. No-record dates mean no supplied records; they do not prove zero demand or lost transactions.')
        left,right=st.columns([1,1.5])
        with left:
            annual=t['annual']
            fig=px.bar(annual,x='Year',y='Records',color='Window',color_discrete_sequence=[GOLD,TEAL],hover_data=['Observed_Days','No_Record_Days'])
            fig.update_layout(showlegend=False)
            fig.update_xaxes(dtick=1,title=None)
            chart('annual','Raw records by year',fig,annual,'Historical Product Demand.csv')
        with right:
            monthly=t['monthly']
            grid=monthly.pivot(index='Year',columns='Month',values='Records').reindex(columns=range(1,13))
            fig=px.imshow(grid,aspect='auto',color_continuous_scale=['#f3f6fa','#8bc8c8',TEAL],labels=dict(x='Calendar month',y='Year',color='Raw records'))
            fig.update_xaxes(tickmode='array',tickvals=list(range(1,13)),ticktext=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'])
            chart('monthly','Monthly record coverage',fig,monthly,'Historical Product Demand.csv')
        st.caption('Zero cells are months inside the supplied date span with no records. Blank cells after January 2017 are outside that span. Full calendar-year day counts expose partial years; days without records can include weekends and holidays.')
        scope=st.selectbox('Coverage detail year',t['annual'].Year.astype(int).tolist(),index=5,key='foundation_year',persist_state='session')
        daily=t['daily'].loc[t['daily'].Year.eq(scope)]
        fig=px.bar(daily,x='Date',y='Records',color_discrete_sequence=[TEAL])
        chart('daily','Recorded dates within the source span',fig,daily,'Historical Product Demand.csv')
        st.caption(f"{p['observed_days']:,} distinct recorded dates across {p['span_days']:,} calendar dates in the min/max span; {p['no_record_days']:,} dates have no supplied records. This source calendar differs from the 260 Sunday-ending forecasting observations.")
    with tabs[1]:
        st.subheader('Composition of the supplied source')
        st.caption('All raw records, including rows with missing dates. Bars count records, not shipments, customers or unique transactions.')
        left,right=st.columns(2)
        with left:
            f=t['warehouses'].sort_values('Records')
            fig=px.bar(f,x='Records',y='Warehouse',orientation='h',color_discrete_sequence=[TEAL],hover_data=['Products','Order_Demand'])
            chart('warehouses','Warehouse record composition',fig,f,'Historical Product Demand.csv')
        with right:
            f=t['categories'].nlargest(12,'Records').sort_values('Records')
            fig=px.bar(f,x='Records',y='Product_Category',orientation='h',color_discrete_sequence=[NAVY])
            chart('categories','12 largest categories by records',fig,t['categories'],'Historical Product Demand.csv')
        category=st.selectbox('Product category',['All categories']+sorted(t['categories'].Product_Category),key='foundation_category',persist_state='session')
        products=t['products']
        if category!='All categories':products=products.loc[products.Product_Category.eq(category)]
        left,right=st.columns(2)
        with left:
            top=products.nlargest(15,'Records').sort_values('Records')
            fig=px.bar(top,x='Records',y='Product_Code',orientation='h',color_discrete_sequence=[TEAL],hover_data=['Product_Category','Order_Demand'])
            chart('products','Most recorded products · top 15',fig,products,'Historical Product Demand.csv')
        with right:
            fig=px.histogram(products,x='Records',nbins=35,color_discrete_sequence=[NAVY])
            fig.update_yaxes(title='Product/category combinations')
            chart('distribution','Record-frequency distribution',fig,products,'Historical Product Demand.csv')
        grid=t['warehouse_categories'].pivot(index='Product_Category',columns='Warehouse',values='Records').fillna(0)
        fig=px.imshow(grid,aspect='auto',color_continuous_scale=['#f3f6fa',TEAL],labels={'color':'Records'})
        fig.update_layout(height=520)
        chart('mix','Category × warehouse composition',fig,t['warehouse_categories'],'Historical Product Demand.csv')
    with tabs[2]:
        st.subheader('Quality findings, with explicit treatment')
        mini_cards([('Missing dates',f"{p['missing_dates']:,}",'Excluded from time-series samples'),
            ('Identical extra rows',f"{p['repeated_rows']:,}",'Retained; no transaction identifier'),
            ('Negative demand',f"{p['negative_records']:,}",'Signed values retained'),
            ('Zero demand',f"{p['zero_records']:,}",'Retained as recorded')])
        left,right=st.columns(2)
        with left:
            fig=px.bar(t['missingness'],x='Missing',y='Column',orientation='h',color_discrete_sequence=[GOLD],hover_data=['Percent'])
            chart('missingness','Missing values in the five source fields',fig,t['missingness'],'Historical Product Demand.csv')
        with right:
            f=t['annual'].copy();f['Recorded-day share (%)']=f.Observed_Days/f.Calendar_Days*100
            fig=px.bar(f,x='Year',y='Recorded-day share (%)',color_discrete_sequence=[TEAL],hover_data=['Observed_Days','Calendar_Days'])
            fig.update_yaxes(range=[0,100]);fig.update_xaxes(dtick=1)
            chart('day_coverage','Dates represented within each calendar year',fig,f,'Historical Product Demand.csv')
        st.caption('Duplicate indicator: pandas duplicated() on the original five CSV columns counts extra exact repetitions, not all members of repeated groups. Identical-looking rows cannot be confirmed as errors without transaction IDs. No malformed nonmissing dates were found. Negative demand meaning is undocumented; no return/shipment interpretation is inferred.')
        st.subheader('2017 source audit · a documented clarification')
        st.info(CLARIFICATION)
        later=t['observations_2017']
        fig=px.bar(later,x='Date',y='Records',color='Warehouse',color_discrete_sequence=[TEAL,NAVY,GOLD])
        chart('2017','Sparse January 2017 observations',fig,later,'Historical Product Demand.csv')
        st.write('Earlier dashboard documentation said observed 2017 outcomes were unavailable. That blanket statement is incorrect for the raw CSV. The research deliberately excluded the partial 2017 year. These 53 rows cover 45 products, omit Whse_A, and end on 9 January; the archived forecast spans 1 January–19 March 2017. Matching dates alone does not establish complete warehouse-week actuals. No future WAPE, MAE or RMSE has been added, and existing forecasts and model conclusions are unchanged.')
    with tabs[3]:
        st.subheader('From source records to forecasting evidence')
        pipeline(p)
        st.caption('Confirmed against MITA_Capstone_Week_15.ipynb cells 7, 26, 40, 54–55, 66 and 110 (zero-based). “Modeling years” is a calendar filter, not a claim that every transaction was supplied. Negative values, repeated rows, zeros and high-demand observations are retained.')
        stages=pd.DataFrame([
            ['Training','Primary weekly observations before the forecast origin','Historical inputs; past-only lags/rolling features for ML. Training windows depend on the experiment.'],
            ['Retrospective validation','2014 and 2015 · 52 weekly timestamps each','Separate annual origins; ETS selection reused these folds.'],
            ['Holdout reference','2016 · 52 aggregate weekly timestamps','One year-ahead aggregate holdout, later revisited; warehouse rolling evaluation is a different experiment.'],
            ['Archived outlook','Origin 25 Dec 2016 · 1 Jan–19 Mar 2017','12 recursively projected weeks; predictions without complete observed validation targets.']],
            columns=['Stage','Time window','Interpretation'])
        for _,row in stages.iterrows():
            st.markdown('**'+row.Stage+' · '+row['Time window']+'**')
            st.caption(row.Interpretation)
        st.success('Reconciliation: all 156 distinct archived aggregate actuals for 2014–2016 exactly match the notebook-rule raw weekly sums. Maximum absolute difference: 0. No model was refitted.')
        chart('weekly','The cleaned weekly aggregate · signed order demand',px.line(t['weekly'],x='Date',y='Order_Demand',color_discrete_sequence=[TEAL]),t['weekly'],'Historical Product Demand.csv; notebook cells 66/110')
        with data_section('Forecast preparation and evidence windows','Methodology'):
            st.dataframe(stages,hide_index=True,width='stretch')
            st.write('W-SUN uses Sunday labels and right-closed weekly bins. Filtering ends on 25 December 2016. An absent raw date is not imputed as an observed zero; weekly resampling sums the available records. “Complete-week bounds” describes chosen calendar boundaries, not independently verified source completeness.')
    with tabs[4]:
        st.subheader('M5 is a separate retail panel')
        st.write('External validation tests transfer of the weekly forecasting framework to another dataset. Primary warehouse order demand and M5 item/store daily sales are different populations and are never combined into one score or source total here.')
        mini_cards([('Item/store series',f"{m['series']:,}",'One row per item × store'),('M5 items',f"{m['items']:,}",'3 categories · 7 departments'),('Stores',str(m['stores']),'3 states'),('Observed sales days',f"{m['sales_days']:,}",'Wide columns d_1 … d_1941')])
        st.caption(f"Sales: {m['sales_start']}–{m['sales_end']}. Calendar: {m['calendar_records']:,} days through {m['calendar_end']}; calendar rows beyond the last sales column are not extra observed sales.")
        st.markdown('**Sales + calendar → daily store totals → seven-day weeks → past-only features**')
        st.write(f"The notebook aggregates items within each store, joins d to calendar dates, retains {m['complete_weeks']} seven-day weeks, and creates lags through 52 weeks. The final 52 usable weeks form a rolling one-week-ahead test, rather than one 52-week-ahead forecast. A source-rule reconstruction gives {m['reconstructed_test_start']}–{m['reconstructed_test_end']}; these reconstructed dates do not rewrite dates missing from the original metric exports.")
        st.caption(f"sell_prices.csv contains {m['price_records']:,} store/item/week prices (join keys: store_id, item_id, wm_yr_wk). It is supplied and checked for existence, but is not read into the displayed notebook’s M5 feature construction. Calendar event and SNAP columns are also not used by that feature pipeline. No pricing effect is inferred.")
        f=t['m5_composition']
        fig=px.bar(f,x='store_id',y='Series',color='cat_id',color_discrete_sequence=[TEAL,NAVY,GOLD],labels={'store_id':'M5 store','Series':'Item/store series','cat_id':'M5 category'})
        chart('m5_structure','M5 panel composition · not primary warehouse demand',fig,f,'sales_train_evaluation.csv')
        st.caption('Sales: no missing cells, negative quantities or repeated item/store keys. Prices: no missing cells or repeated join keys; values range 0.01–107.32 (currency unverified from these files). Empty calendar event fields usually denote no recorded named event; they are not interpreted as corrupted dates.')
        st.button('View external validation in Forecast Reliability →',key='foundation_reliability',on_click=open_external_validation,icon=':material/verified_user:')
    with data_section('Source inventory and verification','Data Sources'):
        rows=[dict(Dataset='Primary' if n.startswith('Historical') else 'M5',File=n,Bytes=v['bytes'],SHA256=v['sha256']) for n,v in info['source_files'].items()]
        st.dataframe(pd.DataFrame(rows),hide_index=True,width='stretch')
        st.caption('All four extracted CSVs match calendar.zip members byte for byte. Raw files and ZIP are not required by this deployed dashboard.')
        st.caption('Notebook: '+info['notebook']['name']+' · SHA-256 '+info['notebook']['sha256'])
    with data_section('Notebook-confirmed rules','Methodology'):
        for item in info['notebook']['evidence']:
            st.markdown('**Notebook cell '+str(item['cell_index'])+' (zero-based)**')
            st.code(item['source'],language='python')
    with data_section('Coverage, completeness and research clarification','Research Limitations'):
        st.write(CLARIFICATION)
        st.write('Excel row-limit coincidence suggests possible export truncation; no larger authoritative original or export log was supplied, so completeness and truncation remain unverified. Dates with no records may be normal non-ordering days. Duplicate-looking rows are retained. Demand is not confirmed shipment volume.')
        st.markdown('[Excel worksheet row limit · Microsoft](https://support.microsoft.com/en-us/office/excel-specifications-and-limits-1672b34d-7043-467e-8e27-269d656771c3)')
        st.caption('The original Capstone README and 87 archival files remain immutable. This explicit raw-source clarification supersedes their blanket 2017-unavailability wording without altering numerical research results.')
    st.caption('DATA FOUNDATION · Verified raw-source summaries · Primary and M5 kept separate · Original research results preserved')
