"""Fast cross-layer contract and true main kernel audit for integrated 2/3/4."""
import tempfile
import unittest
from pathlib import Path
import numpy as np
import pandas as pd

from abc_pom_main3600 import draw_prior
from integrated_finite_main3600 import (
    arms_for_selected, sample_ring_transfer, source_replay_gate, run_finite_batch,
)
from integrated_paired_stage_vegetation import build_matched_variants


def tiny_selected(n=2):
    p=draw_prior(n,seed=20261101)
    p["sample_weight"] = 1./n
    return p


class Integrated234Tests(unittest.TestCase):
    def test_source_arm_selection_independent_of_predicted_outcomes(self):
        s=tiny_selected()
        a=arms_for_selected(s)
        self.assertEqual(len(a), 2*16)
        self.assertTrue((a.groupby("draw_id").size()==16).all())
        self.assertEqual(set(a.edge_SF_on),{0,1})
        self.assertEqual(set(a.move_on),{0,1})
        self.assertEqual(set(a.q),{3,12})
        self.assertEqual(set(a.seed),{101,102})

    def test_mass_conserving_ring_movement(self):
        rng=np.random.default_rng(5)
        x=np.arange(24,dtype=np.int64).reshape(1,8,3)
        y, incoming,outgoing=sample_ring_transfer(x,.15,rng)
        self.assertTrue(np.array_equal(x.sum(axis=1),y.sum(axis=1)))
        self.assertTrue(np.array_equal(y, x+incoming-outgoing))

    def test_main_deterministic_source_replay(self):
        arms=arms_for_selected(tiny_selected(n=1))
        baseline=arms[(arms.edge_SF_on==1)&(arms.move_on==0)].iloc[:1]
        error=source_replay_gate(baseline)
        self.assertLessEqual(error,1e-11)

    def test_paired_stage_intervention_preserves_original_ids(self):
        selected=tiny_selected()
        p,m,k=build_matched_variants(selected)
        self.assertEqual(len(p),2*3*2*2)
        self.assertEqual(len(m),len(p))
        self.assertEqual(len(k),len(p))
        self.assertEqual(int(k.was_source.sum()), 2*len(selected))
        self.assertTrue(k.draw_id.is_unique)

    def test_stochastic_20year_main_kernel_short_cohort(self):
        # A real 20-year finite-N simulation, not a fabricated output table.
        arms=arms_for_selected(tiny_selected(n=1))
        group=arms.iloc[:4]
        result=run_finite_batch(group,years=20,dt=1.0)
        self.assertEqual(len(result),4)
        self.assertTrue(result.occupied_year80.between(0,8).all())
        self.assertTrue((result.recolonization_events_80y>=0).all())
        self.assertTrue((result.movement_assisted_returns_80y>=0).all())


if __name__=="__main__":
    unittest.main()
