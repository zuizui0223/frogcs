"""Tests of cross-ontogeny vegetation model hypotheses and actual source replay."""
import unittest
import numpy as np
import pandas as pd

from model_native_2x2x2_prior import (
    DESIGN,model_names,cube_design,matching_prior_draws
)
from model_native_vegetation_abc import legal_plant_inventory,cross_plant_design
from run_vegetation_cross_ontogeny_80y import (
    original_subsource,matching_actual_parent_draws,replay_frozen_context,
    CONTEXTS,FAMILIES,BASE_ROLE
)


class CrossOntogenyPlantABCTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.models=model_names(pd.read_csv(DESIGN))

    def test_all_six_original_structural_contexts_available(self):
        seen=set()
        for context in CONTEXTS:
            for family in FAMILIES:
                actual=original_subsource(self.models,context,family)
                self.assertEqual(len(actual),2)
                self.assertEqual(set(actual.risk),{False,True})
                seen.add((context,family))
        self.assertEqual(len(seen),6)

    def test_64_subsample_preserves_original_256_draw_identity(self):
        a=matching_actual_parent_draws()
        parent=matching_prior_draws(256)
        pd.testing.assert_frame_equal(a.reset_index(drop=True),
                                      parent.iloc[::4].reset_index(drop=True))
        np.testing.assert_array_equal(a.draw,np.arange(0,256,4))
        self.assertEqual(len(a),64)
        self.assertTrue(a.draw.is_unique)

    def test_exact_original_seasonal_and_annual_model_across_all_stage_contexts(self):
        for context in CONTEXTS:
            for family in FAMILIES:
                anchor=replay_frozen_context(
                    self.models,context,family,years=3,window=1,dt=.5)
                self.assertLess(anchor["clone_F_B"],1e-8)
                self.assertLess(anchor["clone_F_fraction"],1e-8)
                self.assertLess(anchor["clone_F_B_sd"],1e-7)

    def test_complete_144_structure_prior_factorial_without_selective_deletion(self):
        roles=legal_plant_inventory()
        sub=original_subsource(self.models,"original","baseline")
        prior=matching_actual_parent_draws()
        original=cube_design(sub,prior)
        plants=cross_plant_design(original,roles)
        self.assertEqual(len(plants),12*2*64*2*8)
        self.assertEqual(plants.structure_id.nunique(),24)
        self.assertTrue(plants.groupby(["structure_id","draw"]).reverse_on.nunique().eq(2).all())
        self.assertTrue(plants.groupby(["structure_id","draw","reverse_on"]).vertex.nunique().eq(8).all())
        self.assertEqual(plants.draw.nunique(),64)
        self.assertEqual(roles[roles.plant_model==BASE_ROLE].shape[0],1)


if __name__=="__main__":
    unittest.main()
