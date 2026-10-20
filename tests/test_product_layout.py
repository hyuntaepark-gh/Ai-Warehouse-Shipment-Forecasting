"""Product-layout regressions; existing numerical and source tests stay unchanged."""
import json
import unittest
from streamlit.testing.v1 import AppTest
from data_loading import ROOT
from navigation import ROUTES, LABELS
from future_data import combined_summaries, load_archive
from display_formatting import compact_units
from data_loading import source_directory


class ProductLayoutTests(unittest.TestCase):
    def app(self):
        return AppTest.from_file(str(ROOT / 'app.py')).run(timeout=30)

    def test_all_seven_pages_have_context_insights_and_existing_downloads(self):
        app = self.app()
        for route in ROUTES:
            with self.subTest(route=route):
                app.sidebar.button(key='nav_' + route).click().run(timeout=30)
                self.assertFalse(app.exception)
                self.assertFalse(app.error)
                content = '\n'.join(x.value for x in app.markdown)
                if route == 'Operational Insights':
                    self.assertIn('ops-insight-grid', content)
                    self.assertIn('December 25, 2016', content)
                elif route == 'Data Foundation':
                    self.assertIn('wiq-mini-grid', content)
                    self.assertIn('wiq-chips', content)
                else:
                    self.assertIn('wiq-insight-grid', content)
                    self.assertIn('wiq-chips', content)
                self.assertTrue(app.get('download_button'))
                self.assertEqual([x.label for x in app.sidebar.button], list(LABELS.values()))
                self.assertFalse(app.sidebar.radio)

    def test_demand_exploration_tabs_and_filter_survive_page_navigation(self):
        app = self.app()
        app.sidebar.button(key='nav_Historical Demand').click().run(timeout=30)
        self.assertEqual([t.label for t in app.tabs if t.label not in ["Data Sources","Full Data Tables","CSV Downloads","Methodology","Research Limitations"]], ['Trend', 'Period comparison', 'Seasonality', 'Variability'])
        next(m for m in app.multiselect if m.label == 'Available years').set_value([2016]).run(timeout=30)
        before = {e.key for e in app.get('download_button')}
        app.sidebar.button(key='nav_Model Comparison').click().run(timeout=30)
        app.sidebar.button(key='nav_Historical Demand').click().run(timeout=30)
        self.assertEqual(next(m for m in app.multiselect if m.label == 'Available years').value, [2016])
        self.assertEqual(before, {e.key for e in app.get('download_button')})
        self.assertEqual(len(app.get('plotly_chart')), 4)
        self.assertFalse(app.exception)

    def test_outlook_windows_match_validated_totals_and_selection_persists(self):
        app = self.app()
        app.sidebar.button(key='nav_Future Forecasting').click().run(timeout=30)
        next(m for m in app.multiselect if m.label == 'Forecast warehouses').set_value(['Whse_A','Whse_J']).run(timeout=30)
        next(s for s in app.selectbox if s.label == 'Forecast horizon (weeks)').set_value(4).run(timeout=30)
        totals = combined_summaries(load_archive(source_directory())['weekly'], ['Whse_A','Whse_J'])
        for row in totals.itertuples():
            metric = next(m for m in app.metric if m.label == f'Projected total · {row.Horizon_Weeks} weeks')
            self.assertEqual(metric.value, compact_units(row.Projected_Total_Demand))
        app.sidebar.button(key='nav_Executive Overview').click().run(timeout=30)
        app.sidebar.button(key='nav_Future Forecasting').click().run(timeout=30)
        self.assertEqual(next(s for s in app.selectbox if s.label == 'Forecast horizon (weeks)').value, 4)
        self.assertEqual(next(m for m in app.multiselect if m.label == 'Forecast warehouses').value, ['Whse_A','Whse_J'])
        self.assertFalse(app.exception)

    def test_reliability_renders_only_selected_evidence_and_updates_year_options(self):
        app = self.app()
        app.sidebar.button(key='nav_Model Validation').click().run(timeout=30)
        self.assertEqual([t.label for t in app.tabs if t.label not in ["Data Sources","Full Data Tables","CSV Downloads","Methodology","Research Limitations"]], ['Backtesting','Stability','External validation','Uncertainty & bias','Diagnostics'])
        self.assertEqual(len(app.get('plotly_chart')), 1)
        next(s for s in app.selectbox if s.label == 'Backtesting evaluation').set_value('2016 holdout reference').run(timeout=30)
        self.assertEqual(next(m for m in app.multiselect if m.label == 'Backtest years').value, [2016])
        self.assertTrue(any('2016 is a separate final holdout' in w.value for w in app.warning))
        app.selectbox(key='validation_section').set_value('External M5 validation').run(timeout=30)
        self.assertEqual(len(app.get('plotly_chart')), 1)
        self.assertTrue(any(s.label == 'M5 reported metric' for s in app.selectbox))
        self.assertFalse(any(s.label == 'Backtesting evaluation' for s in app.selectbox))
        self.assertFalse(app.exception)

    def test_primary_chart_panels_exist_without_duplicating_analytical_traces(self):
        app = self.app()
        expected = {
            'Executive Overview': ('wiq_panel_overview_trend','wiq_panel_overview_ranking',9),
            'Warehouse Analytics': ('wiq_panel_warehouse_trends','wiq_panel_warehouse_scale',6),
            'Future Forecasting': ('wiq_panel_outlook_projection','wiq_panel_outlook_contribution',2),
        }
        for route, (left, right, chart_count) in expected.items():
            with self.subTest(route=route):
                app.sidebar.button(key='nav_'+route).click().run(timeout=30)
                keys = {getattr(e,'key',None) for e in app.main}
                self.assertIn(left, keys)
                self.assertIn(right, keys)
                self.assertEqual(len(app.get('plotly_chart')),chart_count)
                self.assertFalse(app.exception)


if __name__ == '__main__':
    unittest.main()
