"""Compact access regressions: no accordion bars, stable state and CSV parity."""
import unittest
from app_test_support import warehouse_app
from data_loading import ROOT
from navigation import WAREHOUSE_ROUTES
from chart_access import CATEGORIES

class CompactAccessTests(unittest.TestCase):
    def app(self):
        return warehouse_app()

    def test_all_pages_have_one_data_center_and_no_expanders(self):
        app=self.app()
        for route in WAREHOUSE_ROUTES:
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

    def test_each_csv_has_one_download_control(self):
        app=self.app()
        for route in WAREHOUSE_ROUTES:
            with self.subTest(route=route):
                app.sidebar.button(key='nav_'+route).click().run(timeout=30)
                buttons={e.key:e for e in app.get('download_button')}
                self.assertTrue(buttons)
                self.assertFalse(any(k and k.endswith('_chart') for k in buttons))
                self.assertTrue(all(button.proto.url for button in buttons.values()))

    def test_shared_methods_center_coexists_with_chart_filter_and_persists(self):
        app=self.app()
        app.multiselect(key='holdout_models').set_value(['ETS']).run(timeout=30)
        self.assertEqual(sum(getattr(item, "key", None) == "wiq_data_access" for item in app.main), 1)
        self.assertFalse(any(item.key and item.key.startswith("chart_methods_") for item in app.button))
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
        for route in WAREHOUSE_ROUTES:
            if route!='Executive Overview':
                self.assertTrue(app.button(key='exec_nav_'+route))
        self.assertFalse(app.exception)

if __name__=='__main__':unittest.main()
