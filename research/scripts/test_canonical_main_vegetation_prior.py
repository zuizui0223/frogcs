"""Synthetic test of main-original vegetation/cue canonical class priors."""
import unittest
import numpy as np
import pandas as pd

from test_summarize_vegetation_cross_ontogeny_abc import fake_all_stage_sources
from canonical_main_vegetation_prior import (
    confirm_main_equivalence,main_role_multiplicities,
    equal_class_and_role_priors,reweight_main_canonical,N_CANONICAL
)


class MainCanonicalPlantPriorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        x=fake_all_stage_sources()
        x["min_F_B"]=1.
        x["max_F_B"]=2.
        # The synthetic source fixture exposes beta values; the actual
        # genuine 80y source also contains each exact sign column.
        for scale in ("log","raw"):
            for term in ("OS","OV","SV","OSV"):
                x[f"sign_{scale}_{term}"]=np.sign(
                    x[f"beta_{scale}_{term}"]).astype(int)
        cls.x=x

    def test_main_3600_canonical_redundant_risk_structure_removed(self):
        a,receipt=confirm_main_equivalence(self.x)
        self.assertEqual(receipt["n_exactly_equal_risk_pairs"],4608)
        self.assertEqual(receipt["canonical_distinct_model_cases"],108*64*2)
        self.assertEqual(a.structure_id.nunique(),N_CANONICAL)
        self.assertFalse(((a.cover_SF==0)&a.risk).any())
        self.assertTrue(a[a.cover_SF==1].risk.nunique()==2)

    def test_invented_behavioral_refuge_difference_detected_before_selection(self):
        broken=self.x.copy()
        i=(broken.cover_SF.eq(0)&broken.risk.eq(True))
        broken.loc[i,"beta_log_OV"]=.12345
        with self.assertRaises(AssertionError):
            confirm_main_equivalence(broken)

    def test_three_prior_scheme_probabilities_all_positive_and_normalized(self):
        a,_=confirm_main_equivalence(self.x)
        meta=a.drop_duplicates("structure_id").set_index("structure_id")
        counts=main_role_multiplicities(a)
        self.assertEqual(len(counts),12)
        self.assertEqual(int(counts.sum()),3600)
        w=equal_class_and_role_priors(meta,counts)
        self.assertEqual(len(w),3)
        for value in w.values():
            self.assertEqual(len(value),N_CANONICAL)
            self.assertAlmostEqual(float(value.sum()),1.,places=12)
            self.assertGreater(float(value.min()),0)
        # Equal-plant prior mass is 1/12, even though the SF=0 roles have
        # 6 canonical classes while SF=1 roles have 12.
        for role in counts.index:
            mask=meta.plant_model.eq(role).to_numpy()
            self.assertAlmostEqual(w["equal_12_plant_roles"][mask].sum(),1/12,places=12)
            self.assertAlmostEqual(w["main3600_role_multiplicity"][mask].sum(),counts[role]/3600,places=12)

    def test_canonical_abc_no_lost_rate_draws_or_correlated_labels(self):
        out,receipt=reweight_main_canonical(self.x,n_boot=99)
        a=out["canonical_model_prior_class_shares"]
        b=out["canonical_model_prior_marginals"]
        t=out["canonical_prior_comparison"]
        self.assertEqual(len(a),2*3*108)
        self.assertEqual(len(t),6)
        self.assertTrue(a.groupby(["scale","structural_prior"]).
                        conditional_model_share.sum().between(.999999,1.000001).all())
        self.assertTrue(b.groupby(["scale","structural_prior","dimension"]).
                        conditional_share.sum().between(.999999,1.000001).all())
        self.assertEqual(receipt["n_exactly_equal_risk_pairs"],4608)
        self.assertEqual(set(t.scale),{"log","raw"})


if __name__=="__main__":
    unittest.main()
