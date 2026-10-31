"""Synthetic and source-table invariants for the post-hoc empirical-ICC POM.

Never interpret spatial residual correlation as acoustic detection error or
as a biologically validated stage-to-adult recruitment/calling conversion.
"""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
import numpy as np
import pandas as pd

from test_select_macro_trophic_scenarios import test_sites,source_fixture
from select_macro_trophic_scenarios import load_cohort,scenario_surfaces
from pattern_oriented_abc_pilot import get_design
from r2_calibrated_directional_pom import (
    orthogonal_regression,signal_at_sites,calibrate_r2,
    rankrows,site_rank_r2,five_pattern_matrix,categories,category_agreement
)
from estimate_naamp_residual_spatial_icc import empirical_block_noise
from evaluate_naamp_empirical_block_pom import read_icc


class EmpiricalICCNoiseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        s,v=test_sites(block_count=15,sites_per_block=8)
        cls.data=load_cohort(s,v,expected=120)
        cls.design=get_design(cls.data,"uniform")
        cls.q,cls.pinv=orthogonal_regression(cls.design)
        cls.surfaces,_=scenario_surfaces([source_fixture()])

    def test_read_actual_source_summary_and_residual_calibration(self):
        s=read_icc()
        self.assertEqual(set(s.index),{"uniform","target_group"})
        self.assertEqual(s.n_spatial_blocks.to_list(),[56,56] if s.index[0]=="uniform" else [56,56])
        for bg in s.index:
            self.assertGreaterEqual(s.loc[bg,"icc"],0)
            self.assertLess(s.loc[bg,"icc"],1)
            self.assertGreater(s.loc[bg,"alpha_block_to_site"],.25)

    def test_injected_cluster_effect_changes_noise_but_not_source_response(self):
        noise=empirical_block_noise(self.data,32,711,.13)
        other=empirical_block_noise(self.data,32,711,0.)
        self.assertEqual(noise.shape,(32,120))
        self.assertGreater(np.max(abs(noise-other)),.1)
        grid=self.surfaces["case_000"]
        f=signal_at_sites(self.data,"uniform",grid,"rank_signal")
        s=signal_at_sites(self.data,"uniform",grid,"log_signal")
        self.assertFalse(np.allclose(f,s))
        self.assertTrue(np.isfinite(f).all() and np.isfinite(s).all())

    def test_shared_regression_r2_calibration_and_five_direction_patterns(self):
        noise=empirical_block_noise(self.data,24,10,.13)
        second=empirical_block_noise(self.data,32,20,.13)
        signal=self.design["o"]+.25*self.design["s"]
        config=calibrate_r2(signal,.10,noise,self.q)
        self.assertIn(config["calibration_status"],(
            "MATCHED_R2","MATCHED_WITHOUT_NOISE",
            "NOISE_R2_NOT_BRACKETED","APPROXIMATE_R2_UNMATCHED"))
        predictions=rankrows(signal[None,:]+config["sigma"]*second)
        r2=site_rank_r2(predictions,self.q)
        p=five_pattern_matrix(predictions,self.design,self.pinv)
        self.assertEqual(p.shape,(32,5))
        cat=categories(p,.15)
        self.assertEqual(cat.shape,(32,5))
        self.assertTrue(np.isfinite(r2).all())
        soft,exact=category_agreement(cat,cat,tuple(range(5)))
        self.assertTrue(0<=soft<=1)
        self.assertTrue(0<=exact<=1)

    def test_duplicate_outputs_have_exactly_the_same_model_noise_response(self):
        grid=self.surfaces["case_000"]
        duplicate=grid.copy()
        noise=empirical_block_noise(self.data,16,41,.133)
        r1=rankrows(signal_at_sites(self.data,"uniform",grid,"rank_signal")[None,:]+
                    3.2*noise)
        r2=rankrows(signal_at_sites(self.data,"uniform",duplicate,"rank_signal")[None,:]+
                    3.2*noise)
        np.testing.assert_array_equal(r1,r2)

    def test_corrupt_icc_summary_is_rejected_before_ecological_score(self):
        valid=read_icc().reset_index()
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp)/"icc.csv"
            valid.loc[0,"icc"]=-.1
            valid.to_csv(p,index=False)
            with self.assertRaises((AssertionError,ValueError)):
                read_icc(p)
            x=valid.copy()
            x.loc[0,"icc"]=1
            x.to_csv(p,index=False)
            with self.assertRaises((AssertionError,ValueError)):
                read_icc(p)


if __name__=="__main__":
    unittest.main()
