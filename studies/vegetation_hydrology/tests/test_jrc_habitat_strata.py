import importlib.util
import sys
import unittest
from pathlib import Path
S=Path(__file__).resolve().parents[1]/"scripts"
sys.path.insert(0,str(S))
P=S/"pilot_jrc_habitat_strata.py"
sp=importlib.util.spec_from_file_location("jrc_stratified",P)
m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
MANIFEST=Path(__file__).resolve().parents[1]/"feasibility"/"JRC_PRIOR_MONTH_ENVIRONMENT_STRATIFIED_N9_2026-10-24.csv"

class TestOutcomeBlindJRCStrata(unittest.TestCase):
    def test_predeclared_sha256_and_complete_3_by_3(self):
        s=m.read_manifest(MANIFEST)
        self.assertEqual(len(s),9)
        self.assertEqual(len({(e["year"],e["stratum"]) for e in s}),9)
        self.assertEqual(len({e["state"] for e in s}),9)
    def test_dates_and_no_response_columns(self):
        s=m.read_manifest(MANIFEST)
        self.assertTrue(all(2000<=m.preceding_month(e["date"])[0]<=2015 for e in s))
        self.assertTrue(all("CallingIndex" not in e and "Species" not in e for e in s))

if __name__=="__main__":unittest.main()
