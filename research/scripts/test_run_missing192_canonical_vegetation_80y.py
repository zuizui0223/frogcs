"""Minimal scientific integrity tests for remaining 192 genuine 80-year simulations."""
import unittest
import numpy as np
import pandas as pd

from model_native_2x2x2_prior import DESIGN,model_names,cube_design
from model_native_vegetation_abc import legal_plant_inventory
from run_missing192_canonical_vegetation_80y import (
    new_draws_only,canonical_cube,N_TO_RUN,
    N_BIOLOGICAL_RUNS_PER_SHARD,CONTEXTS,FAMILIES
)
from run_vegetation_cross_ontogeny_80y import (
    original_subsource,replay_frozen_context
)


class RemainingCanonicalModelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.models=model_names(pd.read_csv(DESIGN))

    def test_parent_rate_draws_are_a_disjoint_full256_partition(self):
        other=new_draws_only()
        self.assertEqual(len(other),N_TO_RUN)
        self.assertEqual(other.draw.nunique(),192)
        self.assertTrue(other.draw.mod(4).ne(0).all())
        self.assertEqual(len(set(other.draw)|set(np.arange(0,256,4))),256)
        self.assertFalse(set(other.draw)&set(np.arange(0,256,4)))

    def test_all18_plant_risk_hypotheses_and_both_reversal_states(self):
        other=new_draws_only().head(4)
        ctx=original_subsource(self.models,"D_first_S_overtakes","shared_both")
        base=cube_design(ctx,other)
        cells=canonical_cube(base,legal_plant_inventory())
        self.assertEqual(len(cells),18*4*2*8)
        self.assertEqual(cells.structure_id.nunique(),18)
        self.assertEqual(cells.draw.nunique(),4)
        self.assertEqual(cells.reverse_on.nunique(),2)
        self.assertFalse((cells.cover_SF.eq(0)&cells.risk.eq(True)).any())
        self.assertTrue(cells.groupby(["structure_id","draw","reverse_on"]).
                        vertex.nunique().eq(8).all())

    def test_exact_unchanged_kernel_replay_in_one_nonoriginal_context(self):
        anchor=replay_frozen_context(
            self.models,"S_first_D_overtakes","shared_both",
            years=4,window=2,dt=.5)
        self.assertLess(anchor["clone_F_B"],1e-9)
        self.assertLess(anchor["clone_F_fraction"],1e-9)

    def test_unauthorized_shared_parent_duplicate_rejected(self):
        other=new_draws_only().head(2)
        ctx=original_subsource(self.models,"original","shared_both")
        a=cube_design(ctx,other)
        duplicate=pd.concat([a,a.iloc[[0]]],ignore_index=True)
        with self.assertRaises(AssertionError):
            canonical_cube(duplicate,legal_plant_inventory())


if __name__=="__main__":
    unittest.main()
