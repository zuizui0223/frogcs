"""Numerical invariants of post-result rank-R² noise calibration.

Fixture tests are purely synthetic. They never establish that the NAAMP
observation noise or the aquatic F_B-to-chorus link has been calibrated.
"""
import unittest

import numpy as np
import pandas as pd

from test_select_macro_trophic_scenarios import test_sites,source_fixture
from select_macro_trophic_scenarios import load_cohort,scenario_surfaces
from pattern_oriented_abc_pilot import get_design,stats_from_y,rankz
from directional_context_modulation_pom import contrast_point
from r2_calibrated_directional_pom import (
    MODES,rankrows,orthogonal_regression,site_rank_r2,common_noise,
    signal_at_sites,calibrate_r2,noisy_rank_r2,
    five_pattern_matrix,categories,category_agreement
)


class AcousticR2MatchedPOMTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        s,v=test_sites(block_count=15,sites_per_block=6)
        cls.d=load_cohort(s,v,expected=90)
        cls.design=get_design(cls.d,"uniform")
        cls.q,cls.pinv=orthogonal_regression(cls.design)
        cls.surfaces,_=scenario_surfaces([source_fixture()])
        cls.rng=np.random.default_rng(42)

    def test_exact_rank_regression_r2_matches_manual_ols(self):
        r=rankrows(self.d.strong_rate.to_numpy()[None,:])[0]
        actual=site_rank_r2(r[None,:],self.q)[0]
        x=self.design["x"]
        fit=x@np.linalg.lstsq(x,r,rcond=1e-12)[0]
        manual=1-((r-fit)**2).sum()/((r-r.mean())**2).sum()
        self.assertAlmostEqual(actual,manual,places=12)
        self.assertGreater(actual,0)
        self.assertLess(actual,1)

    def test_all_five_patterns_equal_individual_site_regressions(self):
        y=self.rng.normal(size=(7,len(self.d)))
        ranked=rankrows(y)
        bulk=five_pattern_matrix(ranked,self.design,self.pinv)
        for i in range(len(y)):
            single=stats_from_y(ranked[i],self.design)
            contrast=contrast_point(ranked[i],self.design)
            np.testing.assert_allclose(bulk[i,:4],contrast,rtol=0,atol=1e-11)
            self.assertAlmostEqual(bulk[i,4],single[4],places=11)

    def test_calibration_only_r2_and_independent_eval_noise(self):
        x=self.design["x"]
        signal=rankz(x[:,1]+x[:,2]*.3)
        cal=common_noise(self.d,20,100,"iid")
        eval_noise=common_noise(self.d,32,200,"iid")
        c=calibrate_r2(signal,.22,cal,self.q)
        self.assertIn(c["calibration_status"],
                      ("MATCHED_R2","MATCHED_WITHOUT_NOISE"))
        self.assertLessEqual(c["r2_abs_error"],.002)
        self.assertGreater(c["sigma"],0)
        held=noisy_rank_r2(signal,c["relative_sigma"],eval_noise,self.q)
        self.assertLess(abs(held.mean()-.22),.1)
        self.assertFalse(np.array_equal(cal[:5],eval_noise[:5]))

    def test_r2_unreachable_with_adding_noise_is_not_false_match(self):
        signal=self.rng.normal(size=len(self.d))
        r0=site_rank_r2(rankrows(signal[None,:]),self.q)[0]
        cal=common_noise(self.d,8,110,"iid")
        c=calibrate_r2(signal,min(.99,r0+.2),cal,self.q)
        self.assertEqual(c["calibration_status"],"NOISE_ONLY_R2_UNREACHABLE")
        self.assertEqual(c["relative_sigma"],0.)
        self.assertGreater(c["r2_abs_error"],.002)

    def test_rank_before_noise_cannot_recover_absolute_effect_magnitude(self):
        grid=self.surfaces["case_000"]
        original=signal_at_sites(self.d,"uniform",grid,"rank_signal")
        amplified=signal_at_sites(self.d,"uniform",grid**4,"rank_signal")
        np.testing.assert_array_equal(original,amplified)
        # With scenario-wise SNR matching, even raw-log signal's global
        # positive rescaling is confounded with fitted Gaussian noise SD.
        raw1=signal_at_sites(self.d,"uniform",grid,"log_signal")
        raw2=signal_at_sites(self.d,"uniform",grid**4,"log_signal")
        noise=common_noise(self.d,10,41,"iid")
        ranks1=rankrows(raw1[None,:]+1.2*raw1.std()*noise)
        ranks2=rankrows(raw2[None,:]+1.2*raw2.std()*noise)
        np.testing.assert_allclose(ranks1,ranks2,rtol=0,atol=1e-11)

    def test_common_spatial_noise_has_valid_scale(self):
        for type_ in ("iid","spatial_block_025"):
            x=common_noise(self.d,8,23,type_)
            self.assertEqual(x.shape,(8,len(self.d)))
            np.testing.assert_allclose(x.mean(axis=1),0,atol=1e-14)
            np.testing.assert_allclose(x.std(axis=1),1,atol=1e-14)

    def test_joint_five_categorical_soft_not_independent_posterior(self):
        observed=np.array([[-1,-1,-1,-1,0],
                           [-1,-1,-1,-1,0]],dtype=int)
        modeled=np.array([[-1,-1,-1,-1,0],
                          [-1,1,-1,1,-1]],dtype=int)
        score,exact=category_agreement(observed,modeled,range(5))
        self.assertAlmostEqual(score,(1+.25**3)/2,places=12)
        self.assertAlmostEqual(exact,.5,places=12)
        arr=np.array([[-1,-1,-1,-1,-.01],[-1,-1,-1,-1,.20]])
        result=categories(arr,.15)
        self.assertEqual(result[:,4].tolist(),[0,1])

    def test_unexpected_conditions_fail_closed(self):
        with self.assertRaises(ValueError):
            common_noise(self.d,5,7,"unsupported")
        with self.assertRaises(ValueError):
            signal_at_sites(self.d,"uniform",self.surfaces["case_000"],"bad")
        with self.assertRaises(ValueError):
            categories(np.ones((4,4)),.1)
        with self.assertRaises(ValueError):
            calibrate_r2(np.ones(len(self.d)),.3,
                         common_noise(self.d,6,18,"iid"),self.q)


if __name__=="__main__":
    unittest.main()
