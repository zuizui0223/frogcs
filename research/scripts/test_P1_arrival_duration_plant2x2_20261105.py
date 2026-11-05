"""Fail closed tests of independently crossed salamander arrival/duration."""
from __future__ import annotations
import unittest
import numpy as np

from confirmatory_2x2_vegetation_predator_switch import (
    original_draws,simulate_original_80y
)
from run_P1_arrival_duration_plant2x2_true80_20261105 import (
    N_BASE,N_SCENARIOS,N_VERTICES,TIMING,ARMS,create_factorial,
    seasonal_original
)


class PureSalamanderArrivalDurationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.models,cls.proposals=create_factorial()

    def test_source_256_canonical_fourarms_and_four_stages(self):
        p=self.proposals
        self.assertEqual(len(p),4096)
        self.assertEqual(N_SCENARIOS,4096)
        self.assertEqual(N_VERTICES,32768)
        self.assertEqual(p.source_id.nunique(),256)
        self.assertTrue(p.groupby(["source_id","timing"]).arm.nunique().eq(4).all())
        self.assertTrue(p.groupby(["source_id","arm"]).timing.nunique().eq(4).all())
        self.assertEqual(set(p.timing),{"LS","LL","ES","EL"})
        self.assertEqual(set(p.S_arrival),{0,40})
        self.assertEqual(set(p.S_duration),{40,60})
        self.assertTrue(p.D_duration.eq(60).all())
        self.assertTrue(p.F_arrival.eq(20).all())
        self.assertTrue(p.attack.eq(.5).all())
        self.assertTrue(p.rho.eq(.75).all())
        self.assertTrue(p.groupby("source_id")["model_id"].nunique().eq(4).all())

    def test_exact_original_stage1_and_stage2_precommitted(self):
        orig_models,original,_=original_draws()
        old=original[original.context_id.isin([1,2])].copy()
        p=self.proposals[self.proposals.timing.isin(["LS","EL"])].copy()
        old_id=old.set_index("draw_id")
        for row in p.itertuples(index=False):
            src=old_id.loc[row.original_draw_id]
            self.assertEqual(int(src.model_id),int(row.model_id))
            self.assertEqual(int(src.source_id),int(row.source_id))
            self.assertEqual(str(src.arm),str(row.arm))
            self.assertEqual(float(src.attack),float(row.attack))
            self.assertEqual(float(src.rho),float(row.rho))
            self.assertEqual(float(src.conversion),float(row.conversion))
            self.assertEqual(float(src.strength),float(row.strength))
            self.assertEqual(str(src.refuge_order),str(row.refuge_order))
            self.assertEqual(int(src.gate_code),int(row.gate_code))

    def test_true_original_fouryear_source_replay_and_vegetation_negative_control(self):
        p=self.proposals[self.proposals.source_id.eq(0)].copy()
        now,vertices=seasonal_original(p,self.models,years=4,window=2)
        self.assertEqual(len(now),16)
        self.assertEqual(len(vertices),128)
        old_models,old_p,_=original_draws()
        old=old_p[old_p.source_id.eq(0)&old_p.context_id.isin([1,2])]
        effects,_=simulate_original_80y(old,old_models,years=4,window=2)
        for t,context in (("LS",1),("EL",2)):
            actual=now[now.timing.eq(t)].set_index("arm").sort_index()
            prior=effects[effects.context_id.eq(context)].set_index("arm").sort_index()
            for metric in ("log_OS","log_OV","log_SV","log_OSV",
                           "mean_F_B","mean_log_F_B","min_F","min_S",
                           "H_SF_V1_S2_D2","H_DF_V1_S2_D2"):
                np.testing.assert_allclose(actual[metric],prior[metric],
                                           rtol=0,atol=1e-9,err_msg=metric)
        neg=vertices[vertices.vegetation.eq(0)]
        for metric in ("F_B","S_B","D_B","audit_H_SF","audit_H_DF",
                       "audit_H_SD","audit_H_DS"):
            grouped=neg.groupby(["source_id","timing","vertex"])[metric]
            self.assertLessEqual(float((grouped.max()-grouped.min()).abs().max()),
                                 1e-9,metric)


if __name__=="__main__":
    unittest.main()
