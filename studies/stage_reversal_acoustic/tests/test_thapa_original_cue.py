"""Deterministic synthetic functional checks; original raw source stays in PMC."""
import importlib.util
import sys
import unittest
from pathlib import Path

FILE=Path(__file__).resolve().parents[1]/"macro"/"analyze_thapa_original_pail.py"
spec=importlib.util.spec_from_file_location("thapa_pail",FILE)
mod=importlib.util.module_from_spec(spec)
sys.modules[spec.name]=mod
spec.loader.exec_module(mod)


class OriginalStageCueMath(unittest.TestCase):
    def setUp(self):
        # Artificial 6 conditioning pails per train; two test cues per pail.
        self.mock={
          "sham":[{"larval":0.0,"adult":0.0} for _ in range(6)],
          "larval":[{"larval":-2.0,"adult":-1.0} for _ in range(6)],
          "adult":[{"larval":-3.0,"adult":-4.0} for _ in range(6)]
        }

    def test_stage_ontology(self):
        self.assertEqual(mod.stage("Adult Beetle Odor"),"adult")
        self.assertEqual(mod.stage("Larval Salamander Odor"),"larval")
        self.assertEqual(mod.stage("water "),"sham")
        with self.assertRaisesRegex(ValueError,"unrecognized"):
            mod.stage("unknown")

    def test_directional_transfers_exact(self):
        x,_=mod.effects(self.mock)
        self.assertAlmostEqual(x["cross_stage_mean"],-2.)
        self.assertAlmostEqual(x["within_stage_mean"],-3.)
        self.assertAlmostEqual(x["cross_minus_within_stage"],1.)

    def test_clustering_effects_constant_across_pails(self):
        b=mod.bootstrap(self.mock)
        self.assertEqual(b["cross_stage_mean"]["estimate"],-2.)
        self.assertEqual(b["cross_stage_mean"]["bootstrap95"],(-2.,-2.))

    def test_bootstrap_seed_and_repeatability(self):
        a=mod.bootstrap(self.mock)
        b=mod.bootstrap(self.mock)
        self.assertEqual(a,b)

    def test_leave_pail_out_no_false_sign_change(self):
        x=mod.influence(self.mock)
        self.assertEqual(x["cross_stage_mean"]["sign_flips"],0)
        self.assertEqual(x["cross_minus_within_stage"]["n_leave_one_pail_analyses"],18)

    def test_source_sha_and_provenance_frozen(self):
        self.assertEqual(len(mod.SOURCE_SHA256),64)
        self.assertIn("pmc-oa-opendata",mod.SRC)
        self.assertEqual(sum(mod.ACTUAL_ROWS.values()),588)
        self.assertEqual(sum(mod.DOCUMENTED_2024_TESTED.values()),717)


if __name__=="__main__":
    unittest.main()
