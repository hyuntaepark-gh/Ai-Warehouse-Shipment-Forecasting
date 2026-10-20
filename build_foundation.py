"""Offline, reproducible summaries. Never import or run this from Streamlit.

python build_foundation.py --raw-dir /private/data --notebook /private/research.ipynb
"""
from pathlib import Path
import argparse
import hashlib
import json
import zipfile
import numpy as np
import pandas as pd

PRIMARY = 'Historical Product Demand.csv'
FILES = [PRIMARY, 'sales_train_evaluation.csv', 'calendar.csv', 'sell_prices.csv']
SCHEMA = ['Product_Code', 'Warehouse', 'Product_Category', 'Date', 'Order_Demand']
CELLS = [7, 26, 40, 48, 54, 55, 66, 110, 878, 880, 882, 884, 885, 886, 888, 889]


def sha(path):
    with Path(path).open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def prepare_primary(frame):
    """Notebook cells 7/26/55: retain signs, repeated rows and zeros."""
    if list(frame.columns) != SCHEMA:
        raise ValueError('Unexpected primary schema')
    f = frame.copy()
    f['Date'] = pd.to_datetime(f['Date'], errors='coerce')
    values = f['Order_Demand'].astype(str).str.strip().str.replace(r'^\((.*)\)$', r'-\1', regex=True)
    f['Demand'] = pd.to_numeric(values, errors='raise')
    return f


def weekly_sample(frame):
    """Notebook cells 66/110; Sunday-ending sum, no interpolation/deduplication."""
    sample = frame.loc[frame.Date.between('2012-01-02', '2016-12-25')].copy()
    weekly = sample.set_index('Date').Demand.resample('W-SUN').sum().rename('Order_Demand').reset_index()
    return sample, weekly


def complete_m5_weeks(calendar, days):
    dates = calendar.loc[calendar.d.isin(days), ['d', 'date']].copy()
    if dates.d.duplicated().any() or len(dates) != len(days):
        raise ValueError('M5 sales day/calendar mapping is not one-to-one')
    dates['date'] = pd.to_datetime(dates.date, errors='raise')
    dates['Week'] = dates.date.dt.to_period('W-SUN').dt.end_time.dt.normalize()
    counts = dates.groupby('Week').size()
    return dates, counts[counts.eq(7)].index


def compose(frame, column):
    return frame.groupby(column, dropna=False).agg(Records=('Demand', 'size'),
        Order_Demand=('Demand', 'sum'), Products=('Product_Code', 'nunique')).reset_index()


def primary_summaries(raw):
    f = prepare_primary(raw)
    dated = f.loc[f.Date.notna()].copy()
    sample, weekly = weekly_sample(f)
    model = f.loc[f.Date.between('2012-01-01', '2016-12-31')]
    day_index = pd.date_range(dated.Date.min(), dated.Date.max(), freq='D')
    daily = dated.groupby('Date').size().reindex(day_index, fill_value=0).rename('Records').rename_axis('Date').reset_index()
    daily['Year'] = daily.Date.dt.year
    daily['Month'] = daily.Date.dt.month
    annual = daily.groupby('Year').agg(Records=('Records', 'sum'), Calendar_Days=('Date', 'size'),
        Observed_Days=('Records', lambda x: int(x.gt(0).sum()))).reset_index()
    # Full calendar-year denominator exposes partial boundaries, not just min/max span.
    annual['Calendar_Days'] = pd.to_datetime(annual.Year.astype(str)+'-12-31').dt.dayofyear
    annual['No_Record_Days'] = annual.Calendar_Days-annual.Observed_Days
    annual['Window'] = annual.Year.map(lambda y: 'Sparse boundary year' if y in [2011,2017] else 'Modeling year; completeness unverified')
    months = pd.period_range(dated.Date.min(), dated.Date.max(), freq='M')
    monthly = dated.groupby(dated.Date.dt.to_period('M')).size().reindex(months,fill_value=0).rename('Records').rename_axis('Period').reset_index()
    monthly['Year'] = monthly.Period.dt.year
    monthly['Month'] = monthly.Period.dt.month
    monthly['Observed_Days'] = dated.groupby(dated.Date.dt.to_period('M')).Date.nunique().reindex(months,fill_value=0).to_numpy()
    monthly['Calendar_Days'] = monthly.Period.dt.days_in_month
    monthly['Period'] = monthly.Period.astype(str)
    missing = pd.DataFrame({'Column': raw.columns, 'Missing': raw.isna().sum().values})
    missing['Percent'] = missing.Missing/len(raw)*100
    later=f.loc[f.Date.dt.year.eq(2017)].copy()
    later_daily=later.groupby(['Date','Warehouse']).agg(Records=('Demand','size'),Order_Demand=('Demand','sum')).reset_index()
    overview=dict(records=len(raw),dated_records=len(dated),missing_dates=int(raw.Date.isna().sum()),
        invalid_dates=int((f.Date.isna() & raw.Date.notna()).sum()),warehouses=int(raw.Warehouse.nunique()),
        products=int(raw.Product_Code.nunique()),categories=int(raw.Product_Category.nunique()),
        date_start=str(dated.Date.min().date()),date_end=str(dated.Date.max().date()),
        observed_days=int(dated.Date.nunique()),span_days=len(day_index),no_record_days=int(daily.Records.eq(0).sum()),
        repeated_rows=int(raw.duplicated().sum()),negative_records=int(f.Demand.lt(0).sum()),zero_records=int(f.Demand.eq(0).sum()),
        modeling_records=len(model),weekly_source_records=len(sample),weekly_observations=len(weekly),
        weekly_start=str(weekly.Date.min().date()),weekly_end=str(weekly.Date.max().date()),
        weekly_total=float(weekly.Order_Demand.sum()),excluded_edge_records=len(model)-len(sample),
        records_2017=len(later),dates_2017=int(later.Date.nunique()),warehouses_2017=sorted(later.Warehouse.unique()),
        products_2017=int(later.Product_Code.nunique()),excel_row_limit_match=len(raw)+1==1048576,
        last_record=raw.iloc[-1].to_dict())
    tables={'annual':annual,'monthly':monthly,'daily':daily,'missingness':missing,'weekly':weekly,
        'warehouses':compose(f,'Warehouse'),'categories':compose(f,'Product_Category'),
        'products':f.groupby(['Product_Code','Product_Category']).agg(Records=('Demand','size'),Order_Demand=('Demand','sum')).reset_index(),
        'warehouse_categories':f.groupby(['Warehouse','Product_Category']).agg(Records=('Demand','size'),Order_Demand=('Demand','sum')).reset_index(),
        'observations_2017':later_daily}
    return overview,tables


def m5_summaries(raw_dir):
    sales_path=raw_dir/FILES[1]
    header=pd.read_csv(sales_path,nrows=0).columns.tolist()
    days=[x for x in header if x.startswith('d_')]
    calendar=pd.read_csv(raw_dir/'calendar.csv')
    dates,complete=complete_m5_weeks(calendar,days)
    ids=['id','item_id','dept_id','cat_id','store_id','state_id']
    meta=[]; store_totals=None; sales_missing=0; negative=0; zero=0
    for chunk in pd.read_csv(sales_path,chunksize=1500):
        meta.append(chunk[ids])
        sales_missing+=int(chunk.isna().sum().sum())
        negative+=int(chunk[days].lt(0).sum().sum())
        zero+=int(chunk[days].eq(0).sum().sum())
        totals=chunk.groupby('store_id')[days].sum()
        store_totals=totals if store_totals is None else store_totals.add(totals,fill_value=0)
    meta=pd.concat(meta,ignore_index=True)
    store_daily=store_totals.rename_axis('Store').reset_index().melt(id_vars='Store',var_name='d',value_name='Sales_Units').merge(dates,on='d',validate='many_to_one')
    weekly=store_daily.loc[store_daily.Week.isin(complete)].groupby(['Store','Week'],as_index=False).Sales_Units.sum()
    # Notebook feature warm-up needs lag_52. Each series is dense after seven-day filtering.
    usable=sorted(complete)[52:]
    test=usable[-52:]
    prices_count=0; price_missing=0; price_min=None; price_max=None; price_nonpositive=0
    price_keys=[]; price_stores=set(); price_items=set()
    store_codes={x:i for i,x in enumerate(sorted(meta.store_id.unique()))}
    item_codes={x:i for i,x in enumerate(sorted(meta.item_id.unique()))}
    for chunk in pd.read_csv(raw_dir/'sell_prices.csv',chunksize=150000):
        prices_count+=len(chunk);price_missing+=int(chunk.isna().sum().sum())
        price_nonpositive+=int(chunk.sell_price.le(0).sum())
        price_min=float(chunk.sell_price.min()) if price_min is None else min(price_min,float(chunk.sell_price.min()))
        price_max=float(chunk.sell_price.max()) if price_max is None else max(price_max,float(chunk.sell_price.max()))
        price_stores.update(chunk.store_id.unique());price_items.update(chunk.item_id.unique())
        # Collision-free packed keys, bounded by the verified identifier domains.
        stores=chunk.store_id.map(store_codes);items=chunk.item_id.map(item_codes)
        if stores.isna().any() or items.isna().any() or not chunk.wm_yr_wk.between(0,99999).all():
            raise ValueError('Unrecognized M5 price key domain')
        price_keys.append(((stores.astype('int64')*len(item_codes)+items.astype('int64'))*100000+chunk.wm_yr_wk).to_numpy())
    price_duplicates=prices_count-len(np.unique(np.concatenate(price_keys)))
    info=dict(series=len(meta),items=int(meta.item_id.nunique()),stores=int(meta.store_id.nunique()),
        categories=int(meta.cat_id.nunique()),departments=int(meta.dept_id.nunique()),states=int(meta.state_id.nunique()),
        sales_days=len(days),sales_start=str(dates.date.min().date()),sales_end=str(dates.date.max().date()),
        sales_missing_cells=sales_missing,sales_negative_cells=negative,sales_zero_cells=zero,
        repeated_series_keys=int(meta.duplicated(['store_id','item_id']).sum()),calendar_records=len(calendar),
        calendar_start=str(calendar.date.min()),calendar_end=str(calendar.date.max()),
        calendar_missing=calendar.isna().sum().astype(int).to_dict(),calendar_duplicate_days=int(calendar.d.duplicated().sum()),
        complete_weeks=len(complete),weekly_store_observations=len(weekly),
        first_week=str(min(complete).date()),last_week=str(max(complete).date()),
        reconstructed_test_start=str(min(test).date()),reconstructed_test_end=str(max(test).date()),
        reconstructed_train_weeks=len(usable)-len(test),reconstructed_test_weeks=len(test),feature_warmup_weeks=52,
        price_records=prices_count,price_missing_cells=price_missing,price_nonpositive=price_nonpositive,
        price_min=price_min,price_max=price_max,price_repeated_keys=price_duplicates,
        price_stores=len(price_stores),price_items=len(price_items),
        price_used_in_notebook_features=False)
    composition=meta.groupby(['state_id','store_id','cat_id'],as_index=False).agg(Series=('id','size'))
    return info,{'m5_composition':composition,'m5_weekly':weekly}


def build(raw_dir,notebook,out,capstone=None):
    out.mkdir(parents=True,exist_ok=True)
    initial={n:dict(bytes=(raw_dir/n).stat().st_size,sha256=sha(raw_dir/n)) for n in FILES}
    nb=json.loads(notebook.read_text(encoding='utf-8'))
    evidence=[dict(cell_index=i,source=''.join(nb['cells'][i]['source'])) for i in CELLS]
    # Fail closed when supplied notebook differs from the inspected preprocessing contract.
    contracts={7:'return -float(x[1:-1])',55:'negative_policy = "keep"',66:'.resample("W-SUN")',
        40:'not automatically removed',888:'-52:',889:'rolling one-week-ahead'}
    for index,needle in contracts.items():
        if needle not in ''.join(nb['cells'][index]['source']):raise ValueError(f'Notebook rule changed at cell {index}')
    primary,tables=primary_summaries(pd.read_csv(raw_dir/PRIMARY))
    m5,m5_tables=m5_summaries(raw_dir);tables.update(m5_tables)
    reconciliation={}
    if capstone:
        exported=pd.read_csv(capstone/'tables/timesfm_historical_weekly_predictions.csv')
        exported['Date']=pd.to_datetime(exported.Date)
        actual=exported.groupby('Date').Actual.agg(['min','max'])
        if not actual['min'].eq(actual['max']).all():raise ValueError('Conflicting export actuals')
        weekly=tables['weekly'].set_index('Date').Order_Demand
        delta=(actual['min']-weekly.reindex(actual.index)).abs()
        if delta.isna().any() or delta.max()>1e-6:raise ValueError('Raw weekly sums differ from archived actuals')
        reconciliation=dict(weeks=len(actual),max_absolute_difference=float(delta.max()),status='matched')
    zip_info=None
    if (raw_dir/'calendar.zip').exists():
        with zipfile.ZipFile(raw_dir/'calendar.zip') as z:
            members=[]
            for name in FILES:
                with z.open(name) as f: digest=hashlib.file_digest(f,'sha256').hexdigest()
                if digest!=initial[name]['sha256']:raise ValueError('ZIP/extracted CSV mismatch: '+name)
                members.append(dict(name=name,bytes=z.getinfo(name).file_size,sha256=digest))
        zip_info=dict(sha256=sha(raw_dir/'calendar.zip'),members=members)
    for name in FILES:
        if sha(raw_dir/name)!=initial[name]['sha256']:raise ValueError('Source mutated during summary build')
    summary=dict(schema_version=1,primary=primary,m5=m5,source_files=initial,
        notebook=dict(name=notebook.name,sha256=sha(notebook),cells=len(nb['cells']),index_base=0,evidence=evidence),
        archive=zip_info,archived_actual_reconciliation=reconciliation)
    for name,table in tables.items():table.to_csv(out/(name+'.csv'),index=False)
    summary['summary_files']={p.name:dict(bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(out.glob('*.csv'))}
    (out/'manifest.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    print(json.dumps(dict(primary=primary,m5=m5,reconciliation=reconciliation,summary_bytes=sum(p.stat().st_size for p in out.iterdir())),indent=2))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--raw-dir',type=Path,required=True)
    parser.add_argument('--notebook',type=Path,required=True)
    parser.add_argument('--output',type=Path,default=Path(__file__).parent/'foundation_summaries')
    parser.add_argument('--capstone',type=Path)
    args=parser.parse_args()
    build(args.raw_dir,args.notebook,args.output,args.capstone)
