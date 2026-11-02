"""Fast guards for the genuine finite-N same-256 R4 extension."""
import unittest
import numpy as np
import pandas as pd

from integrated_finite_main3600 import (
    run_finite_batch, source_replay_gate, sample_ring_transfer,
)
from run_newseed_2x2_original_finite_N_R4 import (
    make_all_arms, EXPECTED_ARMS_PER_BASE, SEEDS, N_SHARDS,
)


class Same256NewseedR4Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.models,cls.prior,cls.arms=make_all_arms()

    def test_original_PR161_structure_and_identical_nuisance(self):
        self.assertEqual(len(self.prior),3072)
        self.assertEqual(self.prior.source_id.nunique(),256)
        self.assertEqual(len(self.arms),24576)
        self.assertEqual(EXPECTED_ARMS_PER_BASE,96)
        self.assertEqual(N_SHARDS,16)
        self.assertEqual(set(self.arms.seed),set(SEEDS))
        self.assertTrue(self.arms.groupby("source_id").size().eq(96).all())
        self.assertEqual(set(self.arms.arm),{"00","10","01","11"})
        self.assertEqual(set(self.arms.context_id),{0,1,2})
        self.assertEqual(set(self.arms.move_on),{0,1})
        self.assertEqual(set(self.arms.q),{3,12})
        self.assertTrue(self.arms.edge_SF_on.eq(1).all())
        self.assertTrue(self.arms.groupby(["source_id","context_id","arm"]).size().eq(8).all())

    def test_original_main_annual_model_replays_without_new_cohort_calibration(self):
        r=self.arms[(self.arms.edge_SF_on==1)&(self.arms.move_on==0)].iloc[:1].copy()
        self.assertLessEqual(source_replay_gate(r),1e-11)

    def test_unmodified_original_model_genuine_short_finite_population(self):
        r=self.arms[self.arms.source_id.eq(0)&
                    self.arms.context_id.eq(0)&
                    self.arms.q.eq(3)].copy()
        for (_,_,_),g in r.groupby(["behavior","litter","gate_code"]):
            z=run_finite_batch(g,years=20,dt=1.0)
            self.assertEqual(len(z),len(g))
            self.assertTrue(z.occupied_year80.between(0,8).all())
            self.assertTrue(z.occupied_mean_year61_80.between(0,8).all())
            self.assertTrue(z.recolonization_events_80y.ge(0).all())
            self.assertTrue(z.local_extinction_events_80y.ge(0).all())
            self.assertTrue(z.movement_assisted_returns_80y.le(z.recolonization_events_80y).all())
            self.assertTrue(z[z.move_on==0].movement_assisted_returns_80y.eq(0).all())

    def test_integer_ring_transfer_conserves_mass(self):
        a=np.arange(24,dtype=np.int64).reshape(1,8,3)
        new,incoming,outgoing=sample_ring_transfer(a,.15,np.random.default_rng(50))
        np.testing.assert_array_equal(new.sum(axis=1),a.sum(axis=1))
        np.testing.assert_array_equal(new,a+incoming-outgoing)


if __name__=="__main__":
    unittest.main()
