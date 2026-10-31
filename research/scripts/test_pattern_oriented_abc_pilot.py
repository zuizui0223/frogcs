"""Tests of descriptive POM and *conditional* ABC; NO empirical model claims."""
import unittest
import numpy as np
import pandas as pd

from test_select_macro_trophic_scenarios import test_sites, source_fixture
from select_macro_trophic_scenarios import load_cohort, scenario_surfaces
from pattern_oriented_abc_pilot import (
    PATTERNS, HOLDOUT, rankz, get_design, stats_from_y,
    bootstrap_observed, group_exact_surfaces, pattern_assessment,
    site_response, prior_reference, conditional_abc, recovery_matrix,
    multivariate_distance
)


class PatternABCFixtureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        sites,visits=test_sites(block_count=15,sites_per_block=6)
        cls.d=load_cohort(sites,visits,expected=90)
        cls.surfaces,_=scenario_surfaces([source_fixture()])
        cls.design=get_design(cls.d,"uniform")
        cls.obs=cls.d.strong_rate.to_numpy()

    def test_multivariate_and_holdout_patterns_have_identical_site_grain(self):
        p,h=stats_from_y(self.obs,self.design,holdout=True)
        self.assertEqual(len(p),len(PATTERNS))
        self.assertEqual(len(h),len(HOLDOUT))
        np.testing.assert_allclose(p[:4],np.linalg.lstsq(
            self.design["x"],rankz(self.obs),rcond=1e-12)[0][4:8],rtol=0,atol=1e-10)
        self.assertTrue(np.isfinite(h).all())

    def test_any_strict_monotone_transform_keeps_same_rank_patterns(self):
        y=site_response(self.d,"uniform",self.surfaces["case_000"])
        a,h=stats_from_y(y,self.design,holdout=True)
        b,k=stats_from_y(np.exp(y*.25),self.design,holdout=True)
        np.testing.assert_allclose(a,b,rtol=0,atol=1e-10)
        np.testing.assert_allclose(h,k,rtol=0,atol=1e-10)

    def test_spatial_bootstrap_covariance_not_deterministically_singular(self):
        draws,cov,inv,meta=bootstrap_observed(
            self.obs,self.design,self.d.spatial_block,n_boot=99)
        self.assertEqual(draws.shape[1],len(PATTERNS))
        self.assertGreater(len(draws),90)
        self.assertEqual(cov.shape,(6,6))
        np.testing.assert_allclose(cov@inv,np.eye(6),atol=1e-6)
        self.assertTrue(np.all(np.linalg.eigvalsh(cov)>0))
        self.assertGreaterEqual(meta["n_spatial_blocks"],15)

    def test_exact_duplicate_source_grids_are_grouped(self):
        duplicate={k:v.copy() for k,v in self.surfaces.items()}
        duplicate["case_999"]=duplicate["case_000"].copy()
        labels,groups=group_exact_surfaces(duplicate)
        self.assertEqual(labels["case_000"],labels["case_999"])
        self.assertEqual(sum(map(len,groups.values())),25)

    def test_abc_reference_recoverability_is_conditional_only(self):
        eq,_=group_exact_surfaces(self.surfaces)
        ref=prior_reference(self.d,"uniform",self.design,self.surfaces,eq,
                            seed=240,per_case=5)
        self.assertEqual(len(ref),120)
        o=stats_from_y(self.obs,self.design)
        draws,cov,inv,_=bootstrap_observed(
            self.obs,self.design,self.d.spatial_block,n_boot=99)
        pm,accepted,threshold,minimum=conditional_abc(ref,o,inv,accept_fraction=.1)
        self.assertAlmostEqual(float(pm.sum()),1.,places=10)
        self.assertEqual(len(accepted),12)
        self.assertGreaterEqual(threshold,minimum)
        self.assertTrue(np.isfinite(pm).all())
        sample=recovery_matrix(self.d,"uniform",self.design,self.surfaces,eq,ref,inv,
                               seed=5,n=2)
        self.assertEqual(len(sample),48)
        self.assertTrue(sample.recovered.isin([True,False]).all())
        self.assertTrue(np.isfinite(sample.min_distance_sq).all())

    def test_fixed_real_site_projection_changes_with_site_source_mapping(self):
        x=next(iter(self.surfaces.values()))
        a=site_response(self.d,"uniform",x,warps=(1.,1.))
        b=site_response(self.d,"uniform",x,warps=(.65,1.35))
        self.assertGreater(np.count_nonzero(a!=b),0)
        self.assertTrue((a>0).all())
        with self.assertRaises(ValueError):
            site_response(self.d,"uniform",x[:1])


if __name__=="__main__":
    unittest.main()
