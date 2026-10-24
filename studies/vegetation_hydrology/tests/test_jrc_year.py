import importlib.util
import sys
import unittest
from pathlib import Path
P=Path(__file__).resolve().parents[1]/"scripts"
sys.path.insert(0,str(P))
f=P/"run_jrc_prior_month_year.py"
spec=importlib.util.spec_from_file_location("jrc_year",f)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class TestJRCYear(unittest.TestCase):
    def test_source_checksums_pinned(self):
        self.assertEqual(len(m.PIN_COORD),64)
        self.assertEqual(len(m.PIN_CAL),64)
    def test_year_source_budget_bounded(self):
        self.assertTrue(m.MAX_YEAR_TRANSFER<=2_500_000_000)
        self.assertIn("PreviousMonth",m.OUTPUT_COLUMNS)
    def test_no_response_endpoint_output(self):
        self.assertNotIn("CallingIndex",m.OUTPUT_COLUMNS)
        self.assertNotIn("Species",m.OUTPUT_COLUMNS)
if __name__=="__main__":unittest.main()
