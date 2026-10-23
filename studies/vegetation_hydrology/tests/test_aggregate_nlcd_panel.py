import csv
import io
import json
import tempfile
import unittest
import zipfile
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from aggregate_nlcd_c1v2_panel import aggregate, ingest

class TestAnnualPanelAggregation(unittest.TestCase):
    def make_archive(self, root, year, site="123", extra=None):
        fields=("RouteNumber","SiteID","year","radius_m","n_buffer_pixels",
                "n_valid_pixels","coverage_fraction","qc_status","frac_forest",
                "frac_woody_wetland","frac_emergent_wetland","frac_open_water",
                "frac_developed","frac_shrub","frac_grass_herb","frac_agriculture")
        f=io.StringIO();wr=csv.DictWriter(f,fieldnames=fields);wr.writeheader()
        rows=[]
        for rad in (100,500):
            r={"RouteNumber":"1001","SiteID":site,"year":str(year),
               "radius_m":str(rad),"n_buffer_pixels":"100",
               "n_valid_pixels":"100","coverage_fraction":"1",
               "qc_status":"ok",
               "frac_forest":"0.5","frac_woody_wetland":"0.5",
               "frac_emergent_wetland":"0","frac_open_water":"0",
               "frac_developed":"0","frac_shrub":"0",
               "frac_grass_herb":"0","frac_agriculture":"0"}
            if extra:r.update(extra)
            rows.append(r)
        wr.writerows(rows)
        receipt={"version":"USGS Annual NLCD Collection 1.2","year":year,
                 "counts_csv_downloaded":False,"frog_outcomes_read":False,
                 "ecological_effects_estimated":False,
                 "buffers":{"rows":2,"site_years_extracted":1}}
        path=Path(root)/f"{year}.zip"
        with zipfile.ZipFile(path,"w") as z:
            z.writestr(f"nlcd_c1v2_{year}_site_year_buffers.csv",f.getvalue())
            z.writestr(f"nlcd_c1v2_{year}_receipt.json",json.dumps(receipt))
        return path
    def test_two_year_panel_and_site_change(self):
        with tempfile.TemporaryDirectory() as t:
            p=[self.make_archive(t,2001),self.make_archive(t,2007)]
            rows,report=aggregate(p,[2001,2007],expected_site_years=2)
            self.assertEqual(len(rows),4)
            self.assertEqual(report["n_site_years"],2)
            self.assertEqual(report["n_buffer_rows"],4)
            self.assertEqual(report["earliest_latest_within_site_change"][500]["n_sites_span_ge_5y"],1)
            self.assertFalse(report["ecological_effect_estimated"])
    def test_missing_year_fail_closed(self):
        with tempfile.TemporaryDirectory() as t:
            p=[self.make_archive(t,2001)]
            with self.assertRaisesRegex(ValueError,"missing years"):
                aggregate(p,[2001,2002],expected_site_years=2)
    def test_bad_fraction_rejected(self):
        with tempfile.TemporaryDirectory() as t:
            p=self.make_archive(t,2001,extra={"frac_forest":"0.9"})
            with self.assertRaisesRegex(ValueError,"invalid categorical"):
                ingest(p)
    def test_bad_version_rejected(self):
        with tempfile.TemporaryDirectory() as t:
            p=self.make_archive(t,2001)
            with zipfile.ZipFile(p) as z:records={k:z.read(k) for k in z.namelist()}
            rec=json.loads(records["nlcd_c1v2_2001_receipt.json"])
            rec["version"]="USGS Annual NLCD Collection 1.1"
            with zipfile.ZipFile(p,"w") as z:
                for name,data in records.items():
                    z.writestr(name,json.dumps(rec) if name.endswith("_receipt.json") else data)
            with self.assertRaisesRegex(ValueError,"unverified source"):
                ingest(p)

if __name__=="__main__":unittest.main()
