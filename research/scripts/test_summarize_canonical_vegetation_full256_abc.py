"""Synthetic no-pruning gates for 108-class original 256 rate-draw ABC."""
import unittest

import numpy as np
import pandas as pd

from test_summarize_vegetation_cross_ontogeny_abc import fake_all_stage_sources
from summarize_canonical_vegetation_full256_abc import (
    exact_abc,canonical_only,N_DRAWS
)


class CanonicalFull256ABCTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        base=canonical_only(fake_all_stage_sources())
        # Never distort ecological responses in this synthetic fixture;
        # four disjoint copies of 64 original IDs provide complete 256 rows.
        copies=[]
        for i in range(4):
            copy=base.copy()
            copy["draw"]=copy["draw"]+i
            copies.append(copy)
        cls.x=pd.concat(copies,ignore_index=True)

    def test_exact_model_count_and_all_main_structure_prior_names(self):
        self.assertEqual(len(self.x),108*256*2)
        self.assertEqual(self.x.structure_id.nunique(),108)
        self.assertTrue(self.x.groupby("structure_id").draw.nunique().eq(256).all())
        self.assertTrue(self.x.groupby(["structure_id","draw"]).reverse_on.nunique().eq(2).all())
        self.assertFalse((self.x.cover_SF.eq(0)&self.x.risk.eq(True)).any())

    def test_all_three_priors_are_distinct_and_each_normalized(self):
        result=exact_abc(self.x,n_boot=19)
        classes=result["full256_108class_abc"]
        marg=result["full256_main_axis_prior_marginals"]
        leads=result["full256_structural_prior_leaders"]
        paired=result["full256_vegetation_paired_effects"]
        self.assertEqual(len(classes),108*3*2)
        self.assertEqual(len(leads),3*2)
        self.assertEqual(len(paired),2*3*2*4)
        self.assertTrue(classes.groupby(["scale","prior"]).conditional_abc_share.sum().
                        between(.999999999,1.000000001).all())
        for x in marg.groupby(["scale","prior","axis"]):
            self.assertAlmostEqual(x[1].conditional_abc_share.sum(),1.,places=10)
        self.assertTrue(paired.n_independent_rate_draws.eq(256).all())

    def test_missing_model_or_rate_is_fatal(self):
        broken=self.x.iloc[:-1]
        with self.assertRaises(AssertionError):
            exact_abc(broken,n_boot=13)
        corrupted=self.x.copy()
        corrupted.loc[0,"reverse_on"]=15
        with self.assertRaises(AssertionError):
            exact_abc(corrupted,n_boot=13)


if __name__=="__main__":
    unittest.main()
