"""Offline data contracts, notebook-rule fixtures and eight-page integration."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import pandas as pd
from streamlit.testing.v1 import AppTest
from build_foundation import SCHEMA, prepare_primary, weekly_sample, primary_summaries, complete_m5_weeks
from foundation_data import load_foundation, SUMMARY_DIR
from data_loading import ROOT, source_directory


class FoundationCalculationTests(unittest.TestCase):
    def test_signed_values_and_notebook_week_boundaries_keep_repeated_rows(self):
        raw=pd.DataFrame([
            ['P','A','C',None,'5 '],['P','A','C','2012/1/1','100'],
            ['P','A','C','2012/1/2','10'],['P','A','C','2012/1/2','10'],
            ['P','A','C','2012/1/8','(3)'],['P','A','C','2012/1/9','0'],
            ['P','A','C','2016/12/25','2'],['P','A','C','2016/12/26','9'],
            ['P','A','C','2017/1/2','7']],columns=SCHEMA)
        prepared=prepare_primary(raw)
        self.assertEqual(prepared.Demand.tolist(),[5,100,10,10,-3,0,2,9,7])
        sample,weekly=weekly_sample(prepared)
        self.assertEqual(len(sample),5)
        series=weekly.set_index('Date').Order_Demand
        self.assertEqual(series.loc['2012-01-08'],17)
        self.assertEqual(series.loc['2012-01-15'],0)
        self.assertEqual(series.loc['2016-12-25'],2)
        self.assertEqual(series.sum(),19)
        info,tables=primary_summaries(raw)
        self.assertEqual(info['missing_dates'],1)
        self.assertEqual(info['repeated_rows'],1)
        self.assertEqual(tables['annual'].Records.sum()+info['missing_dates'],len(raw))

    def test_m5_calendar_filters_partial_weeks_and_stays_separate(self):
        calendar=pd.DataFrame({'d':['d_'+str(i) for i in range(1,11)],'date':pd.date_range('2011-01-29',periods=10)})
        dates,weeks=complete_m5_weeks(calendar,['d_'+str(i) for i in range(1,10)])
        self.assertEqual(weeks.tolist(),[pd.Timestamp('2011-02-06')])
        self.assertEqual(len(dates),9)
        with self.assertRaises(ValueError):complete_m5_weeks(calendar,['d_999'])
        with self.assertRaises(ValueError):complete_m5_weeks(pd.concat([calendar,calendar.iloc[:1]]),['d_1'])

    def test_verified_raw_counts_missingness_and_calendar_coverage(self):
        info,t=load_foundation();p=info['primary']
        self.assertEqual((p['records'],p['missing_dates'],p['dated_records']),(1048575,11239,1037336))
        self.assertEqual((p['warehouses'],p['products'],p['categories']),(4,2160,33))
        self.assertEqual((p['date_start'],p['date_end']),('2011-01-08','2017-01-09'))
        self.assertEqual((p['observed_days'],p['span_days'],p['no_record_days']),(1729,2194,465))
        self.assertEqual(t['annual'].set_index('Year').Records.to_dict(),{2011:640,2012:203635,2013:218298,2014:216404,2015:209661,2016:188645,2017:53})
        self.assertEqual(t['monthly'].Records.sum(),p['dated_records'])
        self.assertEqual(t['daily'].Records.gt(0).sum(),p['observed_days'])
        self.assertEqual(t['missingness'].Missing.sum(),11239)
        self.assertEqual((p['repeated_rows'],p['negative_records'],p['zero_records']),(122423,10469,28681))
        self.assertTrue(p['excel_row_limit_match'])
        self.assertEqual(p['last_record']['Date'],'2016/6/27')

    def test_composition_reconciles_to_raw_not_cleaned_sample(self):
        info,t=load_foundation();p=info['primary']
        for name in ['warehouses','categories','products','warehouse_categories']:
            self.assertEqual(t[name].Records.sum(),p['records'],name)
        self.assertEqual(len(t['products'].Product_Code.unique()),2160)
        self.assertEqual(t['observations_2017'].Records.sum(),53)
        self.assertEqual(t['observations_2017'].Date.nunique(),6)
        self.assertNotIn('Whse_A',t['observations_2017'].Warehouse.tolist())

    def test_weekly_reconciliation_against_all_archived_actuals(self):
        info,t=load_foundation();p=info['primary']
        self.assertEqual((p['modeling_records'],p['weekly_source_records'],p['excluded_edge_records']),(1036643,1034979,1664))
        self.assertEqual(len(t['weekly']),260)
        raw=t['weekly'].set_index('Date').Order_Demand
        archive=pd.read_csv(source_directory()/'tables/timesfm_historical_weekly_predictions.csv')
        actual=archive.groupby('Date').Actual.agg(['min','max'])
        self.assertEqual(len(actual),156)
        pd.testing.assert_series_equal(actual['min'],raw.reindex(actual.index),check_names=False,check_dtype=False)
        self.assertTrue(actual['min'].eq(actual['max']).all())
        self.assertEqual(info['archived_actual_reconciliation']['max_absolute_difference'],0)

    def test_m5_structure_is_not_primary_coverage_or_error_metrics(self):
        info,t=load_foundation();m=info['m5']
        self.assertEqual((m['series'],m['items'],m['stores'],m['sales_days']),(30490,3049,10,1941))
        self.assertEqual((m['calendar_records'],m['price_records']),(1969,6841121))
        self.assertEqual((m['sales_missing_cells'],m['repeated_series_keys'],m['price_repeated_keys']),(0,0,0))
        self.assertEqual((m['complete_weeks'],len(t['m5_weekly'])),(277,2770))
        self.assertEqual(t['m5_composition'].Series.sum(),30490)
        self.assertEqual(m['reconstructed_test_start'],'2015-05-31')
        self.assertFalse(m['price_used_in_notebook_features'])
        self.assertNotIn('Whse_A',t['m5_weekly'].Store.unique())
        self.assertNotIn('WAPE',t['m5_weekly'].columns)

    def test_only_small_summary_files_are_loaded_and_tampering_fails_closed(self):
        self.assertLess(sum(p.stat().st_size for p in SUMMARY_DIR.iterdir()),300000)
        load_foundation.clear()
        original=pd.read_csv;paths=[]
        def read(path,*args,**kwargs):
            paths.append(Path(path))
            return original(path,*args,**kwargs)
        with patch('foundation_data.pd.read_csv',side_effect=read):load_foundation()
        self.assertTrue(paths)
        self.assertTrue(all(p.parent==SUMMARY_DIR for p in paths))
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            info={'schema_version':1,'summary_files':{'bad.csv':{'sha256':'wrong'}}}
            (root/'manifest.json').write_text(json.dumps(info))
            (root/'bad.csv').write_text('a\n1\n')
            with self.assertRaises(ValueError):load_foundation(tmp)


class FoundationPageTests(unittest.TestCase):
    def app(self):
        app=AppTest.from_file(str(ROOT/'app.py')).run(timeout=30)
        return app.sidebar.button(key='nav_Data Foundation').click().run(timeout=30)

    def test_page_coverage_charts_data_center_and_research_disclosures(self):
        app=self.app()
        self.assertFalse(app.exception)
        self.assertEqual(len(app.sidebar.button),8)
        self.assertEqual(len(app.get('expander')),0)
        self.assertGreaterEqual(len(app.get('plotly_chart')),10)
        text='\n'.join(e.value for e in app.markdown)
        self.assertIn('1,048,575',text)
        self.assertIn('truncation warning, not proof',text)
        self.assertIn('blanket statement is incorrect',text)
        self.assertTrue(any('53 records' in x.value for x in app.info))
        self.assertTrue(app.get('download_button'))

    def test_product_selection_persists_across_external_metrics_navigation(self):
        app=self.app()
        app.selectbox(key='foundation_category').select('Category_019').run(timeout=30)
        app.button(key='foundation_reliability').click().run(timeout=30)
        self.assertEqual(app.session_state['navigation'],'Model Validation')
        self.assertEqual(app.session_state['validation_section'],'External M5 validation')
        self.assertTrue(any(s.label=='M5 reported metric' for s in app.selectbox))
        self.assertFalse(app.exception)
        app.sidebar.button(key='nav_Data Foundation').click().run(timeout=30)
        self.assertEqual(app.selectbox(key='foundation_category').value,'Category_019')
        self.assertFalse(app.exception)


if __name__=='__main__':unittest.main()
