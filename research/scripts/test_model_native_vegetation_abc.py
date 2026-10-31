"""Scientific gates for canonical-main vegetation function comparison."""
import unittest
import numpy as np
import pandas as pd

from model_native_2x2x2_prior import model_names,cube_design,matching_prior_draws,DESIGN,annual_recurrence_batch
from model_native_vegetation_abc import (
    legal_plant_inventory,cross_plant_design,annual_recurrence_plant,
    confirm_baseline_against_original,main_catalog_audit
)


class LegalVegetationABCTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        allmodels=model_names(pd.read_csv(DESIGN))
        cls.models=allmodels[(allmodels.context=="original")&
                             (allmodels.family=="baseline")]
        cls.plants=legal_plant_inventory()

    def test_main_canonical_12_plant_roles_all_possible(self):
        p=self.plants
        self.assertEqual(len(p),12)
        self.assertTrue((~(p.cover_DF.eq(1)&p.litter.eq(1))).all())
        self.assertTrue(p.groupby(["cover_SF","litter"]).size().sort_values().to_list()==[2,2,4,4])
        axes,roles=main_catalog_audit(p)
        self.assertGreaterEqual(len(axes),20)
        self.assertEqual(int(roles.matching_main_3600_models.sum()),3600)
        self.assertTrue(roles.matching_main_3600_models.gt(0).all())

    def test_role_cube_has_same_shared_demographic_draws_and_both_edges(self):
        p=matching_prior_draws(4)
        grid=cube_design(self.models,p)
        full=cross_plant_design(grid,self.plants)
        self.assertEqual(len(full),12*2*4*2*8)
        self.assertTrue(full.groupby(["plant_model","risk","draw"]).reverse_on.nunique().eq(2).all())
        self.assertTrue(full.groupby(["structure_id","draw","reverse_on"]).vertex.nunique().eq(8).all())
        self.assertTrue(full.groupby("draw").attack_scale.nunique().eq(1).all())

    def test_clone_replays_unmodified_original_seasonal_annual_kernel(self):
        short=confirm_baseline_against_original(self.models,years=4,window=2,dt=.5)
        self.assertLess(short["F_B"],1e-9)
        self.assertLess(short["F_fraction"],1e-9)
        self.assertLess(short["F_B_sd"],1e-7)

    def test_vegetation_mechanisms_reach_the_same_original_population_indices(self):
        p=matching_prior_draws(2)
        original=cube_design(self.models,p)
        plant=self.plants[(self.plants.cover_SF==1)&
                          (self.plants.litter==1)&
                          (self.plants.cover_DF==0)&
                          (self.plants.cover_DS==0)]
        g=cross_plant_design(original,plant)
        new=annual_recurrence_plant(g,years=3,window=1,dt=.5)
        old=annual_recurrence_batch(original,years=3,window=1,dt=.5)
        cols=["draw","original_case","reverse_on","vertex"]
        a=new.sort_values(cols).reset_index(drop=True)
        b=old.sort_values(cols).reset_index(drop=True)
        np.testing.assert_array_equal(a[cols],b[cols])
        for key in ("F_B","F_fraction","F_B_sd"):
            np.testing.assert_allclose(a[key],b[key],atol=1e-9,rtol=0)

    def test_distinct_plant_function_roles_actually_change_stage_transitions(self):
        p=matching_prior_draws(2)
        original=cube_design(self.models,p)
        choice=self.plants[(self.plants.cover_SF==1)&
                           (self.plants.cover_DF==0)&
                           (self.plants.cover_DS==0)]
        g=cross_plant_design(original,choice)
        z=annual_recurrence_plant(g,years=4,window=2,dt=.5)
        r=z.groupby("plant_model").F_B.mean()
        self.assertEqual(len(r),2)
        self.assertGreater(abs(float(r.iloc[0]-r.iloc[1])),1e-10)


if __name__=="__main__":
    unittest.main()
