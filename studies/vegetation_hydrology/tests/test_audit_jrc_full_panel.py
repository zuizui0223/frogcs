import importlib.util
import unittest
from pathlib import Path
S=Path(__file__).resolve().parents[1]/"scripts"/"audit_jrc_full_panel.py"
spec=importlib.util.spec_from_file_location("full_jrc",S)
full=importlib.util.module_from_spec(spec);spec.loader.exec_module(full)
class TestFullPanelSourceOnly(unittest.TestCase):
    def test_expected_full_frame(self):
        self.assertEqual(full.EXPECTED_TOTAL_VISITS,185221)
        self.assertEqual(full.EXPECTED_TOTAL_SITE_MONTHS,172153)
        self.assertEqual(full.YEARS,set(range(2001,2016)))
    def test_zero_is_not_dry(self):
        self.assertIn("n_no_observation",full.COLUMNS)
        self.assertIn("n_valid_pixels",full.COLUMNS)
        self.assertIn("n_water_pixels",full.COLUMNS)
        self.assertTrue(full.truth("True"))
        self.assertFalse(full.truth("False"))
    def test_frog_fields_prohibited(self):
        self.assertTrue({"Species","CallingIndex"}.issubset(full.FORBIDDEN))
        self.assertTrue(full.FORBIDDEN.isdisjoint(full.COLUMNS))
if __name__=="__main__":unittest.main()
