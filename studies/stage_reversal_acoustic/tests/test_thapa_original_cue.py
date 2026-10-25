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

    def test_published_original_receipt_group_arithmetic(self):
        import json
        path=Path(__file__).resolve().parents[1]/"macro"/"results"/"THAPA_ORIGINAL_588_PAIL_REANALYSIS_20261025.json"
        source=json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(source["sha256"],mod.SOURCE_SHA256)
        self.assertEqual(sum(r["n_source_rows"] for r in source["systems"].values()),588)
        for specimen in source["systems"].values():
            m=specimen["pail_level_mean_change"]
            # Sham effects cancel from cross-vs-within: independent group arithmetic.
            d_larval=m["larval"]["adult"]-m["larval"]["larval"]
            d_adult=m["adult"]["larval"]-m["adult"]["adult"]
            residual=(d_larval+d_adult)/2
            reported=specimen["contrasts"]["cross_minus_within_stage"]["estimate"]
            self.assertAlmostEqual(residual,reported,places=5)
            self.assertAlmostEqual(reported,specimen["complete_pair_only_sensitivity"]["cross_minus_within_stage"],places=5)

    def test_source_missing_sham_cue_cannot_define_extra_negative(self):
        import json
        path=Path(__file__).resolve().parents[1]/"macro"/"results"/"THAPA_ORIGINAL_588_PAIL_REANALYSIS_20261025.json"
        src=json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(src["systems"]["salamander"]["missing_pail_test_cue_cells"],{"sham|adult":1})
        self.assertEqual(src["systems"]["salamander"]["available_pail_count_by_group"]["sham"]["adult"],5)
        self.assertEqual(src["systems"]["beetle"]["n_pail_cue_pairs_complete"],18)

    def test_source_sha_and_provenance_frozen(self):
        self.assertEqual(len(mod.SOURCE_SHA256),64)
        self.assertIn("pmc-oa-opendata",mod.SRC)
        self.assertEqual(sum(mod.ACTUAL_ROWS.values()),588)
        self.assertEqual(sum(mod.DOCUMENTED_2024_TESTED.values()),717)


if __name__=="__main__":
    unittest.main()
