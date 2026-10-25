"""Original-source phase atlas reproduction and non-overclaim regression suite."""
import importlib.util
import json
import math
import sys
import unittest
from copy import deepcopy
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]/"macro"
SCRIPT=ROOT/"analyze_australian_phase_atlas.py"
spec=importlib.util.spec_from_file_location("australia_phase_macro",SCRIPT)
mod=importlib.util.module_from_spec(spec)
sys.modules[spec.name]=mod
spec.loader.exec_module(mod)


class MacroSourceIntegrity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.src=mod.read_source()
        cls.out=mod.analyze(cls.src)

    def test_freeze_grid_exact(self):
        self.assertEqual(len(self.src["source_monthly_rows"]),108)
        self.assertEqual(self.out["n_panels_total"],36)
        self.assertEqual(self.out["n_eligible"],34)

    def test_global_macro_readback_original_pinned_counts(self):
        self.assertTrue(mod.validate(self.out,mod.RESULT))
        self.assertEqual(self.src["totals"]["frogid_call_positive_species_rows"]["sum"],1026737)
        self.assertEqual(self.src["totals"]["odonata_stage_adult_rows"]["sum"],16148)
        self.assertEqual(self.src["totals"]["odonata_any_stage_rows"]["sum"],114179)

    def test_month_unknown_excluded_not_zero(self):
        missing=self.src["date_missing_validation"]
        self.assertEqual(missing["explicit_nonmonthly_records_in_original_odonata_all"],263)
        self.assertEqual(missing["affected_panels"],4)

    def test_no_assumed_odonata_adults(self):
        self.assertTrue(all(row["count"]>=0 for row in self.src["source_monthly_rows"]))
        a=sum(r["count"] for r in self.src["source_monthly_rows"] if r["stream"]=="odonata_stage_adult_rows")
        b=sum(r["count"] for r in self.src["source_monthly_rows"] if r["stream"]=="odonata_any_stage_rows")
        self.assertLess(a,b)

    def test_source_filter_fails_when_adult_filter_missing(self):
        corrupted=deepcopy(self.src)
        x=next(z for z in corrupted["source_monthly_rows"] if z["stream"]=="odonata_stage_adult_rows")
        x["url"]=x["url"].replace("lifeStage=Adult","")
        from tempfile import TemporaryDirectory
        with TemporaryDirectory() as d:
            p=Path(d)/"bad.json"
            p.write_text(json.dumps(corrupted))
            with self.assertRaisesRegex(ValueError,"Adult label filter"):
                mod.read_source(p)

    def test_month_vector_with_missing_data_fails(self):
        corrupted=deepcopy(self.src)
        corrupted["source_monthly_rows"][0]["monthly_counts"][0]+=1
        from tempfile import TemporaryDirectory
        with TemporaryDirectory() as d:
            p=Path(d)/"bad.json"
            p.write_text(json.dumps(corrupted))
            with self.assertRaisesRegex(ValueError,"month sums"):
                mod.read_source(p)

    def test_panel_unit_is_latitude_by_year_not_month_as_independent(self):
        keys={(p["band"],p["year"]) for p in self.out["group_panels"]}
        self.assertEqual(len(keys),36)

    def test_universal_acoustic_alignment_not_supported(self):
        self.assertEqual(self.out["main"]["panels_excess_positive"],17)
        self.assertEqual(self.out["main"]["panels_excess_nonpositive"],17)
        self.assertLess(abs(self.out["main"]["mean_excess_vs_12month_rotation"]),.005)

    def test_circular_month_wrap(self):
        self.assertEqual(mod.circular([1]+[0]*11)["peak_month"],1)
        self.assertAlmostEqual(mod.overlap([.25,.75],[.5,.5]),.75)

    def test_low_n_north_dropped_without_tuning(self):
        unfit=[x for x in self.out["group_panels"] if not x["eligible"]]
        self.assertEqual({(x["band"],x["year"]) for x in unfit},{("-14_-10",2018),("-14_-10",2020)})
    
    def test_source_ceiling_not_causal(self):
        self.assertIn("not",self.out["claim_ceiling"].lower())


if __name__=="__main__":
    unittest.main()
