"""G11 response-blind structural holdout selection and original-model pairing tests."""
import unittest

from run_g11_disjoint_structure_27rate import (
    frozen_selection, make_grid, RATE_GRID, N_SCENARIOS, N_VERTICES,
)
from confirmatory_2x2_vegetation_predator_switch import original_draws


class TestDisjointStructuralHoldout(unittest.TestCase):
    def test_orig_3600_catalog_720_legal_and_256_disjoint(self):
        models,nu,selection,digest=frozen_selection()
        old=set(original_draws()[2].original_base_model_id.astype(int))
        new=set(nu.baseline_model_id.astype(int))
        self.assertEqual(len(models),3600)
        self.assertEqual(len(old),256)
        self.assertEqual(len(new),256)
        self.assertTrue(old.isdisjoint(new))
        self.assertEqual(selection["eligible_legal_base_structures"],720)
        self.assertEqual(selection["remaining_preselection_structures"],464)
        self.assertEqual(len(selection["new_base_ids_by_source"]),256)
        self.assertEqual(len(digest),64)
        self.assertEqual(N_SCENARIOS,82944)
        self.assertEqual(N_VERTICES,663552)

    def test_holdout_seed_identity_is_frozen(self):
        _,n1,id1,s1=frozen_selection()
        _,n2,id2,s2=frozen_selection()
        self.assertEqual(s1,s2)
        self.assertEqual(id1,id2)
        self.assertEqual(n1.to_dict("records"),n2.to_dict("records"))

    def test_every_rate_has_four_legal_original_model_ids(self):
        _,x,_,_=make_grid((0,1),(0,13,26),(0,2))
        self.assertEqual(len(x),2*3*2*4)
        self.assertTrue(x.draw_id.is_unique)
        self.assertTrue(x.groupby(["source_id","rate_id","context_id"])
                        .arm.nunique().eq(4).all())
        self.assertTrue(x.groupby("source_id")
                        [["strength","refuge_order","gate_code"]]
                        .nunique().max().max()==1)
        self.assertTrue(x.groupby(["source_id","context_id","rate_id"])
                        .model_id.nunique().eq(4).all())
        self.assertEqual(len(RATE_GRID),27)
        self.assertEqual(RATE_GRID[0],(.5,.25,2.))
        self.assertEqual(RATE_GRID[-1],(3.,.75,8.))

    def test_duplicate_or_unknown_sources_and_rates_stop(self):
        for kwargs in [
            dict(source_ids=(0,0),rate_ids=(0,)),
            dict(source_ids=(256,),rate_ids=(0,)),
            dict(source_ids=(0,),rate_ids=(0,0)),
            dict(source_ids=(0,),rate_ids=(27,)),
            dict(source_ids=(0,),rate_ids=(0,),contexts=(0,0)),
        ]:
            with self.assertRaises(AssertionError):
                make_grid(**kwargs)


if __name__=="__main__":
    unittest.main()
