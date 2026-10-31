"""Source identity checks for three new frozen biological rate vectors."""
import unittest

import numpy as np

from run_growth_duration_rate_stress_80y import biological_factorial
from spatial_cohort_80y_bridge import replay_gate


class BiologicalRateStressSourceTests(unittest.TestCase):
    def test_original_LHS_rate_ids_are_untouched(self):
        for id in (4,8,12):
            data=biological_factorial(id)
            self.assertEqual(len(data),128)
            self.assertEqual(set(data.draw),{id})
            self.assertEqual(data.structure_id.nunique(),8)
            self.assertEqual(set(data.context),{
                "original","S_growth_fast_only",
                "D_aquatic_long_only","D_first_S_overtakes"})
            self.assertTrue(np.allclose(data.sa,20))
            self.assertTrue(np.allclose(data.da,0))

    def test_all_biological_rate_sources_replay_original_kernel(self):
        for id in (4,8,12):
            errors=replay_gate(biological_factorial(id),years=4,window=2,dt=.25)
            for val in errors.values():
                self.assertLessEqual(val,1e-8)

    def test_growth_duration_grid_is_exactly_factorial(self):
        data=biological_factorial(8)
        for (plant,reverse,vertex),q in data.groupby(["plant_model","reverse_on","vertex"]):
            self.assertEqual(len(q),4)
            a=q.set_index("context")
            for c in ("original","S_growth_fast_only",
                      "D_aquatic_long_only","D_first_S_overtakes"):
                self.assertIn(c,a.index)
            self.assertAlmostEqual(
                a.at["S_growth_fast_only","sg"],
                a.at["D_first_S_overtakes","sg"],places=12)
            self.assertAlmostEqual(
                a.at["D_aquatic_long_only","dduration"],
                a.at["D_first_S_overtakes","dduration"],places=12)
            self.assertAlmostEqual(
                a.at["S_growth_fast_only","dduration"],
                a.at["original","dduration"],places=12)
            self.assertAlmostEqual(
                a.at["D_aquatic_long_only","sg"],
                a.at["original","sg"],places=12)


if __name__=="__main__":
    unittest.main()
