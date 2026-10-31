"""Tests for stable same-geometry spatial mixing versus local dynamic environment."""
import unittest
import numpy as np
from test_observed_neighbour_lag_dispersal_identifiability import fixture
from observed_neighbour_lag_dispersal_identifiability import annual_panel,fixed_effect_association
from recover_dispersal_vs_spatiotemporal_environment import (
    stable_synthetic_panel,MIXING,auc_score
)

class SpatialNullStress(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        a,b=fixture()
        cls.annual,cls.panel,cls.geom=annual_panel(
            a,b,expect_sites=120,expect_visits=1200)

    def test_all_prespecified_synthetic_models_finite(self):
        for kind in ("SHARED_ROUTE_ENV","LOCAL_ENV_PERSISTENCE"):
            y=stable_synthetic_panel(self.annual,self.geom,seed=16,
                                      kind=kind,mixing=0.)
            self.assertEqual(len(y),len(self.annual))
            self.assertTrue(((y>=0)&(y<=1)).all())
            score=fixed_effect_association(self.panel,values=y)
            self.assertTrue(np.isfinite(score["nearest_minus_farthest"]))
        for mix in MIXING[1:]:
            y=stable_synthetic_panel(self.annual,self.geom,seed=16,
                                     kind="STABLE_NEIGHBOUR_MIXING",mixing=mix)
            self.assertTrue(((y>=0)&(y<=1)).all())

    def test_source_seed_reproducibility(self):
        for kind,m in (("SHARED_ROUTE_ENV",0.),
                       ("LOCAL_ENV_PERSISTENCE",0.),
                       ("STABLE_NEIGHBOUR_MIXING",.25)):
            a=stable_synthetic_panel(self.annual,self.geom,seed=12,kind=kind,mixing=m)
            b=stable_synthetic_panel(self.annual,self.geom,seed=12,kind=kind,mixing=m)
            np.testing.assert_array_equal(a,b)

    def test_environment_has_NO_animal_neighbour_parameter(self):
        with self.assertRaises(ValueError):
            stable_synthetic_panel(self.annual,self.geom,seed=3,
                                   kind="LOCAL_ENV_PERSISTENCE",mixing=.25)
        with self.assertRaises(ValueError):
            stable_synthetic_panel(self.annual,self.geom,seed=3,
                                   kind="SHARED_ROUTE_ENV",mixing=.65)
        with self.assertRaises(ValueError):
            stable_synthetic_panel(self.annual,self.geom,seed=3,
                                   kind="STABLE_NEIGHBOUR_MIXING",mixing=.37)

    def test_auc_not_interpreted_as_field_causality(self):
        self.assertEqual(auc_score([0,0],[1,1]),1.)
        self.assertEqual(auc_score([2,2],[1,1]),0.)
        self.assertEqual(auc_score([1,1],[1,1]),.5)

if __name__=="__main__":
    unittest.main()
