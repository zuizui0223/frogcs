"""Synthetic integrity tests of predeclared local-environment nuisance sweep."""
import unittest
import numpy as np
from test_observed_neighbour_lag_dispersal_identifiability import fixture
from observed_neighbour_lag_dispersal_identifiability import annual_panel
from recover_dispersal_vs_spatiotemporal_environment import stable_synthetic_panel
from spatial_environment_nuisance_mixing_recovery import ENV_LEVELS,MOVING

class SpatialNuisanceGrid(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        s,v=fixture()
        cls.a,cls.panel,cls.g=annual_panel(s,v,expect_sites=120,expect_visits=1200)

    def test_predeclared_environment_and_movement_models_are_finite(self):
        self.assertEqual(ENV_LEVELS,(0.,.12,.25,.38,.5))
        self.assertEqual(MOVING,(.12,.25,.40,.65))
        series=[]
        for e in ENV_LEVELS:
            y=stable_synthetic_panel(
                self.a,self.g,seed=153,kind="LOCAL_ENV_PERSISTENCE",
                mixing=0.,environment_near=e)
            self.assertEqual(len(y),len(self.a))
            self.assertTrue(((y>=0)&(y<=1)).all())
            series.append(y)
        self.assertFalse(np.array_equal(series[0],series[-1]))
        for m in MOVING:
            y=stable_synthetic_panel(
                self.a,self.g,seed=153,kind="STABLE_NEIGHBOUR_MIXING",
                mixing=m)
            self.assertTrue(((y>=0)&(y<=1)).all())

    def test_no_migration_is_compulsory_in_environmental_cases(self):
        for env in ENV_LEVELS:
            with self.assertRaises(ValueError):
                stable_synthetic_panel(
                    self.a,self.g,seed=7,kind="LOCAL_ENV_PERSISTENCE",
                    mixing=.25,environment_near=env)

    def test_bad_environment_prior_rejected(self):
        with self.assertRaises(ValueError):
            stable_synthetic_panel(
                self.a,self.g,seed=7,kind="LOCAL_ENV_PERSISTENCE",
                mixing=0.,environment_near=.999)

if __name__=="__main__":
    unittest.main()
