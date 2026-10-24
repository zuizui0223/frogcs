import importlib.util
import unittest
from pathlib import Path
P=Path(__file__).resolve().parents[1]/"scripts"/"audit_route_habitat_contrast.py"
spec=importlib.util.spec_from_file_location("contrast",P)
x=importlib.util.module_from_spec(spec)
spec.loader.exec_module(x)
class TestContrasts(unittest.TestCase):
    def test_route_means_once_per_physical_site_and_no_frog_data(self):
        rows=[]
        for y in [2001,2002]:
            for n in range(8):
                wet=.3 if n==7 else 0
                rows.append({"RouteNumber":"R","SiteID":str(n),"year":str(y),
                    "radius_m":"500","qc_status":"ok",
                    "frac_woody_wetland":str(wet),"frac_emergent_wetland":"0",
                    "frac_open_water":"0","frac_forest":"0",
                    "frac_developed":"0","frac_agriculture":"0"})
        r=x.audit(rows,strict=False)
        self.assertEqual(r["site_years_500m"],16)
        self.assertEqual(r["physical_sites"],8)
        self.assertEqual(r["route_balanced_once_per_route"]["n_groups"],1)
        self.assertEqual(r["route_year_descriptive_not_independent"]["n_groups"],2)
        self.assertEqual(r["route_balanced_once_per_route"]["wetland"]["ge_25pp_count"],1)
        self.assertEqual(r["site_level_veg_wetland_ge10pct_and_open_water_lt1pct"]["sites"],1)
        self.assertTrue(r["no_frog_outcomes_accessed"])
    def test_duplicate_siteyear_rejected(self):
        row={"RouteNumber":"R","SiteID":"s1","year":2001,"radius_m":500,
             "qc_status":"ok","frac_woody_wetland":0,"frac_emergent_wetland":0,
             "frac_open_water":0,"frac_forest":0,"frac_developed":0,"frac_agriculture":0}
        with self.assertRaisesRegex(ValueError,"duplicate"):
            x.audit([row,row],min_stations=1)
if __name__=="__main__":unittest.main()
