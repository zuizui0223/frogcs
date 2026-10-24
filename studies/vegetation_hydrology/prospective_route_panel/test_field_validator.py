import csv
import pathlib
import unittest
from collections import Counter
from field_validator import paired_water_rank

HERE=pathlib.Path(__file__).resolve().parent
class TestProspectiveSourceOnlyPanel(unittest.TestCase):
    def test_30_routes_and_habitat_groups(self):
        with (HERE/"ROUTE_SHORTLIST_V0_1.csv").open(newline="") as f:
            rows=list(csv.DictReader(f))
        self.assertEqual(len(rows),30)
        self.assertEqual(Counter(r["group"] for r in rows),{"A":10,"B":10,"C":10})
        self.assertEqual(len({r["RouteNumber"] for r in rows}),30)
        for r in rows:
            self.assertLessEqual(float(r["max_pairwise_km"]),25)
        for group in "ABC":
            statecounts=Counter(r["State"] for r in rows if r["group"]==group)
            self.assertEqual(len(statecounts),6)
            self.assertLessEqual(max(statecounts.values()),2)
    def test_route_wide_water_change_cancels(self):
        a={str(i):float(i) for i in range(10)}
        b={k:v+10 for k,v in a.items()}
        got=paired_water_rank(a,b)
        self.assertAlmostEqual(got["site_relative_change_range_cm"],0)
        self.assertAlmostEqual(got["site_relative_change_rms_cm"],0)
        self.assertAlmostEqual(got["route_common_change_cm"],10)
    def test_site_specific_water_change_survives(self):
        a={str(i):0. for i in range(10)}
        b=a.copy();b["1"]=4
        got=paired_water_rank(a,b)
        self.assertAlmostEqual(got["site_relative_change_range_cm"],4)
        self.assertTrue(got["nonuniform_site_change"])
    def test_missing_water_not_imputed_zero(self):
        a={str(i):0. for i in range(10)}
        b=a.copy();b["0"]=float("nan")
        with self.assertRaisesRegex(ValueError,"missing water"):
            paired_water_rank(a,b)
    def test_unmatched_site_rejected(self):
        with self.assertRaises(ValueError):
            paired_water_rank({"1":1,"2":2},{"1":2,"3":3})

if __name__=="__main__":
    unittest.main()
