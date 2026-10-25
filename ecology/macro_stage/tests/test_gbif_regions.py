import unittest
from ecology.macro_stage.scripts.run_gbif_region import REGIONS,STAGES,parse_month

class TestMacroSource(unittest.TestCase):
    def test_predeclared_regions_and_stage_labels(self):
        self.assertEqual(len(REGIONS),15)
        self.assertEqual(len(STAGES),12)
        self.assertIn(("salamander_egg",953,"Egg"),STAGES)
        self.assertIn(("odonate_nymph",789,"Nymph"),STAGES)
    def test_monthly_facets_are_12_months_and_not_zeros_from_missing_stage(self):
        x={"count":7,"facets":[{"field":"MONTH","counts":[{"name":"1","count":2},{"name":"8","count":5}]}]}
        v,_=parse_month(x)
        self.assertEqual((len(v),sum(v),v[0],v[7]),(12,7,2,5))
    def test_out_of_calendar_month_rejected(self):
        with self.assertRaises(ValueError):
            parse_month({"count":1,"facets":[{"field":"MONTH","counts":[{"name":"13","count":1}]}]})
if __name__=="__main__":unittest.main()
