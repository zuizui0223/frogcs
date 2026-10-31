"""Pair-resampling sanity checks: two reverse edges at one draw are dependent."""
import unittest
import numpy as np
import pandas as pd
from audit_paired_genuine_abc import (
    paired_bootstrap,draw_rate_matrix,paired_signature_equivalence,
    tolerance_sensitivity
)
from model_native_abc_rf import reject_four_sign_abc
from test_model_native_abc_rf import fake_abc


class GenuineABCPairedPriorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ref,cls.prior=fake_abc(n=24)

    def test_paired_priors_do_not_count_identical_edges_as_independent(self):
        x=self.ref[["structure_id","context","family","risk","draw","reverse_on"]].copy()
        x["accepted"]=self.ref.matches_log.to_numpy(bool)
        classes,actual,ident=draw_rate_matrix(x)
        self.assertEqual(actual.shape,(24,12))
        self.assertTrue((actual==0).any())
        self.assertTrue(np.all(actual<=2))
        self.assertTrue(np.all(ident==1.))
        table,groups=paired_bootstrap(x,n_boot=99,seed=99)
        self.assertEqual(len(table),12)
        self.assertEqual(len(groups),3+2+2)
        self.assertTrue(table.n_effective_paired_rate_draws.eq(24).all())
        self.assertTrue(table.paired_draw_abc_share_ci_low.le(
            table.paired_draw_abc_share_ci_high).all())
        self.assertAlmostEqual(table.conditional_abc_share.sum(),1.)

    def test_same_original_rate_draws_shared_across_all_structures(self):
        x=self.ref[["structure_id","context","family","risk","draw","reverse_on"]].copy()
        x["accepted"]=self.ref.matches_log.to_numpy(bool)
        table,_=paired_bootstrap(x,n_boot=50)
        p=table.set_index("structure_id")
        orig=p.loc["original__baseline__risk0"]
        self.assertEqual(int(orig.n_accepted),
                         int(self.ref[(self.ref.structure_id==orig.name)].matches_log.sum()))
        self.assertGreater(orig.conditional_abc_share,0)

    def test_reversal_sign_check_requires_matching_draws(self):
        eq=paired_signature_equivalence(self.ref)
        self.assertEqual(len(eq),12*2)
        self.assertTrue(eq.n_draws.eq(24).all())
        self.assertTrue(eq.n_identical_ABC_acceptance.eq(24).all())
        corrupt=self.ref.copy()
        corrupt.loc[corrupt.index[0],"draw"]=10000
        with self.assertRaises(AssertionError):
            paired_signature_equivalence(corrupt)

    def test_tolerance_equivalence_with_synthetic_sign_source(self):
        x=self.ref.copy()
        for name in ("log","raw"):
            for tol in ("strict11","loose7"):
                x[f"matches_{name}_{tol}"]=x[f"matches_{name}"]
        table=tolerance_sensitivity(x)
        self.assertEqual(len(table),12*2*3)
        self.assertTrue(table.conditional_abc_share.between(0,1).all())


if __name__=="__main__":
    unittest.main()
