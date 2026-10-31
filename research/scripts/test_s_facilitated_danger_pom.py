"""Synthetic tests for separate speculative salamander-facilitated D→F kernel."""
import unittest
import numpy as np

from stage_network_extension_20261029 import simulate as original
from stage_network_s_facilitated_danger_20261031 import simulate as alternative


class DangerAmplificationTests(unittest.TestCase):
    def setUp(self):
        self.scenarios=[
            dict(community="FSD",roles=15,refuge_order="D",
                 vegetation=0.,f_arrival=20.,s_arrival=0.,d_arrival=0.,
                 attack_scale=.5,cue=0.,reverse=False),
            dict(community="FSD",roles=15,refuge_order="D",
                 vegetation=1.,f_arrival=20.,s_arrival=0.,d_arrival=0.,
                 attack_scale=.5,cue=0.,reverse=False)]
        self.densities=np.array([[1.,.25,1.],[1.,2.,1.]])
        self.kw=dict(dt=.25,initial_cohorts=self.densities,
                     functional_response="litter")

    def test_zero_strength_replays_every_existing_output(self):
        x=original(self.scenarios,**self.kw)
        y=alternative(self.scenarios,**self.kw,
                      s_facilitated_danger_strength=0.,
                      background_danger_fraction=1.)
        for name in x.columns:
            if name not in y:raise AssertionError("Lost existing stage result")
            if np.issubdtype(x[name].dtype,np.number):
                np.testing.assert_allclose(x[name],y[name],rtol=0,atol=1e-12)

    def test_s_facilitation_is_a_distinct_nonnegative_hypothesis(self):
        baseline=alternative(self.scenarios,**self.kw,
                             s_facilitated_danger_strength=0.,
                             background_danger_fraction=1.)
        strong=alternative(self.scenarios,**self.kw,
                           s_facilitated_danger_strength=2.5,
                           background_danger_fraction=.15)
        self.assertTrue(np.isfinite(strong.F_completed).all())
        self.assertTrue((strong.F_completed>=0).all())
        self.assertGreater(float(np.max(np.abs(
            strong.F_completed-baseline.F_completed))),1e-12)
        self.assertTrue(strong.F_killed_by_D.ge(0).all())

    def test_fails_closed_on_undefined_negative_attack_hypothesis(self):
        with self.assertRaises(ValueError):
            alternative(self.scenarios,**self.kw,
                        s_facilitated_danger_strength=-1.)
        with self.assertRaises(ValueError):
            alternative(self.scenarios,**self.kw,
                        s_facilitated_danger_strength=1.,
                        background_danger_fraction=-.1)


if __name__=="__main__":
    unittest.main()
