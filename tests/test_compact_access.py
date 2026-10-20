"""Compact access regressions: no accordion bars, stable state and CSV parity."""
import unittest
from streamlit.testing.v1 import AppTest
from data_loading import ROOT
from navigation import ROUTES
from chart_access import CATEGORIES

class CompactAccessTests(unittest.TestCase):
    def app(self):
        return AppTest.from_file(str(ROOT/'app.py')).run(timeout=30)

    def test_all_pages_have_one_data_center_and_no_expanders(self):
        app=self.app()
        for route in ROUTES:
            with self.subTest(route=route):
                app.sidebar.button(key='nav_'+route).click().run(timeout=30)
                self.assertFalse(app.exception)
                self.assertFalse(app.error)
                self.assertEqual(len(app.get('expander')),0)
                labels=[t.label for t in app.tabs]
                for category in CATEGORIES:self.assertEqual(labels.count(category),1)
                keys=[getattr(e,'key',None) for e in app.main]
                self.assertEqual(keys.count('wiq_data_access'),1)
                self.assertTrue(any(str(k).startswith('chart_toolbar_') for k in keys))

    def test_contextual_csv_matches_consolidated_download(self):
        app=self.app()
        for route in ROUTES:
            with self.subTest(route=route):
                app.sidebar.button(key='nav_'+route).click().run(timeout=30)
                buttons={e.key:e for e in app.get('download_button')}
                chart_keys=[k for k in buttons if k and k.endswith('_chart')]
                self.assertTrue(chart_keys)
                for key in chart_keys:
                    self.assertIn(key[:-6],buttons)
                    self.assertEqual(buttons[key].proto.url,buttons[key[:-6]].proto.url)
                    self.assertTrue(buttons[key].proto.url)

    def test_methods_action_preserves_chart_filter_and_opens_page_center(self):
        app=self.app()
        app.multiselect(key='holdout_models').set_value(['ETS']).run(timeout=30)
        app.button(key='chart_methods_holdout_demand').click().run(timeout=30)
        self.assertTrue(app.session_state['wiq_data_center'])
        self.assertEqual(app.multiselect(key='holdout_models').value,['ETS'])
        self.assertFalse(app.exception)
        app.sidebar.button(key='nav_Historical Demand').click().run(timeout=30)
        app.sidebar.button(key='nav_Executive Overview').click().run(timeout=30)
        self.assertEqual(app.multiselect(key='holdout_models').value,['ETS'])

    def test_overview_shortcuts_are_inside_one_small_popover(self):
        app=self.app()
        self.assertFalse(any(h.value=='Start exploring' for h in app.subheader))
        keys={getattr(e,'key',None) for e in app.main}
        self.assertIn('wiq_explore',keys)
        for route in ROUTES:
            if route!='Executive Overview':
                self.assertTrue(app.button(key='exec_nav_'+route))
        self.assertFalse(app.exception)

if __name__=='__main__':unittest.main()
