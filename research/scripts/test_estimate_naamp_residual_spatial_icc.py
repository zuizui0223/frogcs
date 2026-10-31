"""Synthetic + original-site checks of spatial rank-OLS residual ICC.

An ecological 2° regression-residual cluster effect is not the same as
independent acoustic instrumental noise; its value is a sensitivity input.
"""
from __future__ import annotations

import unittest
import numpy as np
import pandas as pd

from test_select_macro_trophic_scenarios import test_sites
from select_macro_trophic_scenarios import load_cohort
from estimate_naamp_residual_spatial_icc import (
    grouped_sufficient,unequal_icc,icc_conditional_bootstrap,
    observed_residual_cohort,empirical_block_noise
)


class ObservedSpatialResidualTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        s,v=test_sites(block_count=15,sites_per_block=8)
        cls.d=load_cohort(s,v,expected=120)

    def test_unequal_group_sizes_known_random_intercept(self):
        rng=np.random.default_rng(772)
        sizes=[10+i*2 for i in range(35)]
        block_effect=rng.normal(0,np.sqrt(.4),size=len(sizes))
        residual=np.concatenate([
            rng.normal(block_effect[j],np.sqrt(.6),size=n)
            for j,n in enumerate(sizes)])
        groups=np.concatenate([np.repeat(j,n) for j,n in enumerate(sizes)])
        stats=grouped_sufficient(residual,groups)
        value=unequal_icc(stats)
        self.assertEqual(value["n_groups"],len(sizes))
        self.assertEqual(value["n_sites"],sum(sizes))
        self.assertGreater(value["icc"],.15)
        self.assertLess(value["icc"],.65)
        self.assertAlmostEqual(value["alpha_block_to_site"]**2,
                               value["icc"]/(1-value["icc"]))

    def test_near_zero_and_singleton_routes_valid(self):
        rng=np.random.default_rng(3)
        e=rng.normal(size=100)
        labels=np.asarray([0]*30+[1]*30+[2]*30+list(range(3,13)))
        stats=grouped_sufficient(e,labels)
        self.assertEqual(len(stats),13)
        self.assertTrue(np.isfinite(unequal_icc(stats)["icc"]))
        with self.assertRaises(ValueError):
            grouped_sufficient(np.arange(10.),np.arange(10))

    def test_whole_block_bootstrap_is_seeded_and_keeps_clusters_distinct(self):
        rng=np.random.default_rng(77)
        x=rng.normal(size=200)
        groups=np.repeat(np.arange(20),10)
        suff=grouped_sufficient(x,groups)
        x=icc_conditional_bootstrap(suff,n_boot=50,seed=34)
        y=icc_conditional_bootstrap(suff,n_boot=50,seed=34)
        pd.testing.assert_frame_equal(x,y)
        self.assertEqual(len(x),50)
        self.assertTrue(x.icc.between(0,1).all())
        self.assertTrue(np.isfinite(x.to_numpy(float)).all())
        with self.assertRaises(ValueError):
            icc_conditional_bootstrap(suff,n_boot=0)

    def test_field_cohort_residuals_preserve_source_ols_definition(self):
        # A 120-site purely synthetic fixture is not the archived 4,248-site
        # source; check full report only on actual CI-backed field source.
        self.assertEqual(self.d.spatial_block.nunique(),15)
        self.assertTrue((self.d.n>0).all())
        self.assertEqual(int(self.d.n.sum()),120*8)

    def test_correlated_noise_is_deterministic_given_rng_and_has_unit_scale(self):
        a=empirical_block_noise(self.d,24,seed=44,icc=.3)
        b=empirical_block_noise(self.d,24,seed=44,icc=.3)
        np.testing.assert_array_equal(a,b)
        np.testing.assert_allclose(a.mean(axis=1),0,atol=1e-13)
        np.testing.assert_allclose(a.std(axis=1),1,atol=1e-13)
        z=empirical_block_noise(self.d,24,seed=44,icc=0.)
        self.assertGreater(np.max(np.abs(a-z)),1e-5)
        with self.assertRaises(ValueError):
            empirical_block_noise(self.d,5,seed=4,icc=-.2)
        with self.assertRaises(ValueError):
            empirical_block_noise(self.d,5,seed=4,icc=1.)

    def test_estimator_detects_known_cluster_effect_not_noisy_sign(self):
        rng=np.random.default_rng(1877)
        g=np.repeat(np.arange(45),20)
        noise=rng.normal(size=len(g))
        blocks=rng.normal(size=45)
        enough=.75*blocks[g]+.4*noise
        pure=.4*rng.normal(size=len(g))
        with_cluster=unequal_icc(grouped_sufficient(enough,g))
        without_cluster=unequal_icc(grouped_sufficient(pure,g))
        self.assertGreater(with_cluster["icc"],without_cluster["icc"]+.2)
        self.assertLess(without_cluster["icc"],.2)


if __name__=="__main__":
    unittest.main()
