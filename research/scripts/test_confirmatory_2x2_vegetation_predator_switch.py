"""Fail-closed tests of the independent-seed 2x2 source contract and source replay."""
from __future__ import annotations
import unittest
import numpy as np

from abc_pom_main3600 import accepted_signs, corner_contrasts
from confirmatory_2x2_vegetation_predator_switch import (
    ARMS, N_BASE, RANDOM_SEED, SOURCE_MAIN_SHA, original_draws,
    simulate_original_80y, check_source_replay,
)


class NewSeedOriginalSourcePairedTwoByTwoTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.models,cls.p,cls.nuisance=original_draws()

    def test_unique_independent_canonical_backgrounds(self):
        p=self.p
        self.assertEqual(N_BASE,256)
        self.assertEqual(RANDOM_SEED,20261123)
        self.assertEqual(len(p),3072)
        self.assertEqual(p.draw_id.nunique(),3072)
        self.assertEqual(p.source_id.nunique(),256)
        self.assertEqual(set(p.arm),{arm for arm,_,_ in ARMS})
        self.assertTrue(p.groupby(["source_id","context_id"]).arm.nunique().eq(4).all())
        self.assertTrue(p.groupby("source_id").model_id.nunique().eq(4).all())
        self.assertTrue(p.attack.eq(.5).all())
        self.assertTrue(p.rho.eq(.75).all())

    def test_identical_source_background_rate_and_context(self):
        m=self.models
        p=self.p
        features=[x for x in m if x not in
                 ("model_id","assumptions","extrapolation_flags","cover_SF","support_DF")]
        q=p.merge(m,on="model_id",validate="many_to_one",suffixes=("","_source"))
        for col in features:
            self.assertTrue(q.groupby("source_id")[col].nunique().eq(1).all(),col)
        for col in ("attack","rho","conversion","strength","refuge_order","gate_code"):
            self.assertTrue(p.groupby("source_id")[col].nunique().eq(1).all(),col)
        self.assertEqual(SOURCE_MAIN_SHA,
                         "5e2f0a87c639df373fa2700b29403d2ab417a1cc")

    def test_small_genuine_source_4year_replay_and_no_vegetation_null(self):
        sub=self.p[self.p.source_id.lt(2)].copy()
        effects,v=simulate_original_80y(sub,self.models,years=4,window=2)
        self.assertEqual(len(effects),24)
        self.assertEqual(len(v),192)
        self.assertTrue(check_source_replay(self.models,sub,effects,years=4))
        # V=0 must be exactly unaffected by both plant feature interventions.
        v=v[v.vegetation.eq(0)]
        for col in ("F_B","audit_H_SF","audit_H_DF"):
            g=v.groupby(["source_id","context_id","vertex"])[col]
            self.assertLessEqual(float((g.max()-g.min()).abs().max()),1e-9,col)

    def test_original_abc_four_sign_is_not_field_measurement(self):
        examples=np.array([
            [[[-1., 0.],[.1,-.2]], [[-1.,-1.],[.1,-.3]]],
        ])
        c=corner_contrasts(examples)
        self.assertEqual(c.shape,(1,4))
        x=accepted_signs(c,eps=1e-6)
        self.assertEqual(x.shape,(1,))


if __name__=="__main__":
    unittest.main()
