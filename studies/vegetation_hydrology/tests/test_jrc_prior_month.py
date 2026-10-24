import importlib.util
from pathlib import Path
import unittest
import sys
P=Path(__file__).resolve().parents[1]/"scripts"/"pilot_jrc_prior_month.py"
sys.path.insert(0,str(P.parent))
S=importlib.util.spec_from_file_location("jrc_month_probe",P)
m=importlib.util.module_from_spec(S)
S.loader.exec_module(m)

class TestJRCMonthGrid(unittest.TestCase):
    def test_prior_month_uses_only_completed_month(self):
        self.assertEqual(m.preceding_month("2001-01-01"),(2000,12))
        self.assertEqual(m.preceding_month("2008-07-30"),(2008,6))
        self.assertEqual(m.preceding_month("2015-12-01"),(2015,11))
    def test_verified_world_grid_north_west_offsets(self):
        self.assertEqual(m.jrc_tile(39.4,-79.3),"0000160000-0000400000")
        self.assertEqual(m.jrc_tile(43.1,-89.1),"0000120000-0000360000")
    def test_url_is_official_monthly_prefix(self):
        self.assertTrue(m.source_url(2001,6,39.4,-79.3).endswith(
            "/2001/2001_06/2001_06-0000160000-0000400000.tif"))
    def test_unreasonable_coordinates_rejected(self):
        with self.assertRaises(ValueError):m.jrc_tile(12.0,-80.0)
        with self.assertRaises(ValueError):m.source_url(2030,1,39,-80)

if __name__=="__main__":unittest.main()
