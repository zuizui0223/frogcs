import unittest
import numpy as np
from verify_structural_alias import (
    probabilities,aliased_parameterizations,site_specific_change_rank,self_test
)
class TestStructuralEquivalence(unittest.TestCase):
    def test_exact_k_probability_is_normalized(self):
        from math import comb
        for k in (2,3,5):
            p=probabilities(np.arange(10,dtype=float)/10,k)
            self.assertEqual(len(p),comb(10,k))
            self.assertAlmostEqual(p.sum(),1.,places=12)
    def test_habitat_alternate_persistent_site_process_is_identical(self):
        rng=np.random.default_rng(6)
        a,b=aliased_parameterizations(
            rng.random(10),rng.random(10),rng.normal(size=10))
        self.assertLess(np.max(np.abs(probabilities(a,3)-probabilities(b,3))),1e-12)
    def test_uniform_water_or_route_weather_is_not_site_change(self):
        a=np.arange(10)/20
        r=site_specific_change_rank(a,a+.1)
        self.assertAlmostEqual(r["site_specific_change_range"],0.,places=12)
        self.assertTrue(abs(r["mean_route_common_change"])>.05)
        self.assertFalse(r["rank_support_ge5pp"])
    def test_site_relative_water_change_has_rank(self):
        a=np.ones(10)*.1;b=a.copy();b[0]+=.2
        self.assertTrue(site_specific_change_rank(a,b)["rank_support_ge5pp"])
    def test_missing_original_water_fails(self):
        with self.assertRaisesRegex(ValueError,"six matched"):
            site_specific_change_rank(np.array([np.nan]*10),np.zeros(10))
    def test_numeric_333_route_algebra(self):
        a=self_test()
        self.assertLess(a["max_site_effect_parameter_alias_difference"],1e-12)
        self.assertLess(a["max_routewide_weather_offset_difference"],1e-12)
if __name__=="__main__":unittest.main()
