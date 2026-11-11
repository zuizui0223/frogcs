"""Fixed original AU sample: avoid effect hunting via alternative stage-tagging."""
import importlib.util
import json
import sys
import unittest
from copy import deepcopy
from pathlib import Path
MOD=Path(__file__).resolve().parents[1]/"macro"/"analyze_au_phase_annotation_era_sensitivity.py"
spec=importlib.util.spec_from_file_location("au_phase_era_robustness",MOD)
mod=importlib.util.module_from_spec(spec)
sys.modules[spec.name]=mod
spec.loader.exec_module(mod)

class SourceSelectionRobustness(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.src=json.loads(mod.INPUT.read_text())
        cls.result=mod.analyse(cls.src)

    def test_original_eligibility_fixed(self):
        self.assertEqual(self.result["n_original_band_years"],36)
        self.assertEqual(self.result["n_fixed_original_eligible"],34)
        self.assertEqual(mod.validate(self.result),True)

    def test_stage_filter_changes_nine_original_panel_phase_signs(self):
        x=self.result
        self.assertEqual(x["n_sign_reversal_when_swapping_adult_stage_vs_all"],9)
        self.assertEqual(x["n_positive_explicit_adult"],17)
        self.assertEqual(x["n_positive_all_odonata"],22)

    def test_national_surplus_stage_sensitivity(self):
        x=self.result
        self.assertAlmostEqual(x["primary_mean_adult_surplus"],.0037140896096421886,places=11)
        self.assertAlmostEqual(x["sensitivity_mean_all_odonata_surplus"],.020152120954087884,places=11)

    def test_extremes_preserve_sign_with_stage_ontology_choice(self):
        by={x["lat_band"]:x for x in self.result["band_summary"]}
        mid=by["-32_-26"];far=by["-14_-10"]
        self.assertGreater(mid["mean_explicit_adult_surplus"],0)
        self.assertGreater(mid["mean_all_odonata_surplus"],0)
        self.assertLess(far["mean_explicit_adult_surplus"],0)
        self.assertLess(far["mean_all_odonata_surplus"],0)

    def test_two_reporting_eras_not_independent_geographic_holdout(self):
        by={x["lat_band"]:x for x in self.result["band_summary"]}
        self.assertEqual(by["-32_-26"]["period_2018_2020"]["n"],3)
        self.assertEqual(by["-32_-26"]["period_2021_2023"]["n"],3)
        self.assertGreater(by["-32_-26"]["period_2018_2020"]["adult"],0)
        self.assertGreater(by["-32_-26"]["period_2021_2023"]["adult"],0)
        self.assertEqual(by["-14_-10"]["period_2018_2020"]["n"],1)
        self.assertEqual(by["-14_-10"]["period_2021_2023"]["n"],3)

    def test_northern_limited_stage_tag_coverage_not_imputed(self):
        band={x["lat_band"]:x for x in self.result["band_summary"]}
        self.assertEqual(band["-14_-10"]["n_eligible"],4)
        self.assertEqual(sum(not x["eligible"] for x in self.result["original_panels"]),2)

    def test_simultaneous_month_rotation_is_invariant(self):
        f=[.5,.2,.1,.1,.1]+[0]*7
        a=[.1,.3,.3,.2,.1]+[0]*7
        x=mod.rotation_surplus(f,a)
        y=mod.rotation_surplus([f[(i-3)%12] for i in range(12)],
                               [a[(i-3)%12] for i in range(12)])
        self.assertAlmostEqual(x,y,places=12)

    def test_bad_month_denominator_raises(self):
        bad=deepcopy(self.src)
        bad["source_monthly_rows"][0]["monthly_counts"][0]+=1
        with self.assertRaisesRegex(ValueError,"month denominators"):
            mod.analyse(bad)
if __name__=="__main__":unittest.main()
