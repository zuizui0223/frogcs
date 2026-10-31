"""Predeclared fixed-source controls for individual biological-rate replacements."""
import unittest
import numpy as np

from rate_axis_synthetic_growth_rescue_80y import (
    AXES, DIMENSIONS, PHYSICS, paired_rate_endpoints,
    swap_fixed_rate_axis, verify_complete_swap_positive_control,
)
from spatial_cohort_80y_bridge import replay_gate
from finite_n_source_cohort_bridge import simulate_finite_group,summarize_finite_group

class OriginalLHSRateAxisChecks(unittest.TestCase):
    def test_only_original_eight_prior_axes_and_complete_swap(self):
        self.assertEqual(len(AXES),8)
        self.assertEqual(len(set(AXES)),8)
        self.assertEqual(len(set(DIMENSIONS.values())),8)
        self.assertTrue(verify_complete_swap_positive_control())

    def test_all_sixteen_counterfactuals_change_exact_one_axis(self):
        low,high=paired_rate_endpoints()
        self.assertEqual(len(low),128)
        self.assertEqual(len(high),128)
        for base_id in (0,12):
            base,other=(low,high) if base_id==0 else (high,low)
            for axis in AXES:
                c=swap_fixed_rate_axis(base_id,axis)
                self.assertEqual(len(c),128)
                self.assertEqual(set(c.draw),{base_id})
                for key in PHYSICS:
                    expected=(other if key==DIMENSIONS[axis] else base)
                    np.testing.assert_allclose(
                        c[key].to_numpy(float),expected[key].to_numpy(float),
                        rtol=0,atol=1e-12)
                np.testing.assert_array_equal(c.sa,20)
                np.testing.assert_array_equal(c.da,0)
                self.assertEqual(
                    set(c.context),
                    {"original","S_growth_fast_only",
                     "D_aquatic_long_only","D_first_S_overtakes"})

    def test_replay_and_finite_integer_source_with_changed_rate(self):
        c=swap_fixed_rate_axis(0,"rho")
        error=replay_gate(c,years=4,window=2,dt=.25)
        for val in error.values():
            self.assertLessEqual(val,1e-8)
        g=c[(c.context=="original") &
             (c.plant_model=="SF0_DF0_DS1_L0") &
             (c.reverse_on==0)].reset_index(drop=True)
        self.assertEqual(len(g),8)
        outcomes=simulate_finite_group(
            g,scale=3,seed=101,mode="both",
            immigration=False,years=4,dt=.25,transfer=.15)
        frame,events=summarize_finite_group(
            g,outcomes,scale=3,seed=101,mode="both",
            immigration=False,years=4)
        self.assertEqual(len(frame),8*3)
        self.assertEqual(len(events),int(frame.n_local_returns.sum()))
        self.assertTrue((outcomes["hist"]>=0).all())
        self.assertTrue((frame.n_external_immigrants==0).all())


if __name__=="__main__":
    unittest.main()
