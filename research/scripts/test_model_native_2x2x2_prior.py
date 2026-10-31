"""Exact model-native factorial 80-year ABC/POM implementation tests.

All fixtures synthetic; baseline old 80-y result is separately verified in the
real-data workflow (including F_B and F_fraction) before interpretation.
"""
from __future__ import annotations
import unittest

import numpy as np
import pandas as pd

from run_macro_process_prior_predictive import DESIGN
from model_native_2x2x2_prior import (
    METRICS,TARGET,VERTICES,EPS, model_names,matching_prior_draws,
    cube_design,annual_recurrence_batch,four_contrasts,categorized_sign,
    summarize_cube_output
)
from extension_annual_summary_20261029 import summarize_years


class ModelNativePriorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.structures=model_names(pd.read_csv(DESIGN))
        cls.draws=matching_prior_draws(4,seed=20261031)

    def test_twelve_classes_and_two_edge_aliases_are_distinct_in_source(self):
        self.assertEqual(len(self.structures),12)
        self.assertEqual(self.structures.structure_id.nunique(),12)
        self.assertTrue((self.structures.case_on!=self.structures.case_off).all())
        self.assertEqual(self.structures.risk.value_counts().to_dict(),{False:6,True:6})
        self.assertEqual(self.structures.context.nunique(),3)
        self.assertEqual(self.structures.family.nunique(),2)

    def test_priors_are_reproducible_balanced_and_same_across_structures(self):
        other=matching_prior_draws(4,seed=20261031)
        pd.testing.assert_frame_equal(self.draws,other)
        self.assertEqual(self.draws.reverse_on.value_counts().to_dict(),{0:2,1:2})
        self.assertEqual(self.draws.f_delay.value_counts().to_dict(),{2:2,3:2})
        grid=cube_design(self.structures[self.structures.context=="original"],self.draws)
        self.assertEqual(len(grid),4*4*8)
        self.assertTrue(grid.groupby(["structure_id","draw"]).vertex.nunique().eq(8).all())
        self.assertEqual(set(grid.vegetation),{0,1})
        self.assertEqual(set(grid.S_source),{.25,2.})
        self.assertEqual(set(grid.D_source),{.25,2.})

    def test_factorial_difference_in_differences_and_log_signs(self):
        y=np.empty((2,2,2))
        for v,s,d in VERTICES:
            y[v,s,d]=5-3*s*d-2*v*d+2*v*s+1*v*s*d
        got=four_contrasts(y)
        np.testing.assert_allclose(got,[-2.5,-1.5,2.5,1.],rtol=0,atol=1e-12)
        np.testing.assert_array_equal(categorized_sign(got),TARGET)
        with self.assertRaises(ValueError):four_contrasts(np.ones((2,2,3)))
        np.testing.assert_array_equal(categorized_sign([0,1e-10,-1e-11,1e-8],
                                                       epsilon=1e-9),[0,0,0,1])

    def test_true_model_annual_batch_matches_unmodified_original_annual_model(self):
        # One dynamically sampled source under each juvenile F maturation delay
        # and the two reversed-predation choices, each with 8 factorial corners.
        structures=self.structures[(self.structures.context=="original")&
                                   (~self.structures.risk)&
                                   (self.structures.family=="baseline")]
        d=self.draws
        frame=cube_design(structures,d)
        out=annual_recurrence_batch(frame,years=5,window=2,dt=.5)
        for draw in d.itertuples(index=False):
            g=frame[frame.draw==draw.draw].sort_values("vertex")
            n=len(g)
            scenarios=[dict(community="FSD",roles=15,refuge_order="D",
                            vegetation=float(x.vegetation),
                            f_arrival=20.,s_arrival=x.sa,d_arrival=x.da,
                            attack_scale=x.attack_scale,cue=0.,
                            reverse=bool(x.reverse_on),rho=x.rho)
                       for x in g.itertuples(index=False)]
            opts=dict(stage_durations=np.column_stack([
                         np.full(n,45.),np.full(n,80.),g.dduration.to_numpy(float)]),
                      functional_response="litter",
                      behavioral_refuge=False,
                      handling_s=g.hs.to_numpy(float),
                      handling_d=g.hd.to_numpy(float),
                      s_growth=g.sg.to_numpy(float),
                      d_growth=g.dg.to_numpy(float),
                      sd_size_mode="dynamic",
                      pathway_controls=dict(
                          cover_SF=1.,cover_DF=0.,cover_DS=0.,cover_SD=0.,
                          support_DF=0.,support_DS=0.,emerge_survival=0.,
                          emerge_exposure=0.,cue_SD=0.,
                          edge_SD=np.ones(n),edge_DS=np.ones(n)))
            source=np.column_stack([np.ones(n),g.S_source.to_numpy(float),
                                    g.D_source.to_numpy(float)])
            raw=summarize_years(scenarios,years=5,window=2,dt=.5,
                                source_cohorts=source,seasonal_options=opts,
                                conversion=(draw.conversion,)*3,
                                survival=(draw.f_adult_survival,.5,0.),
                                juvenile=(draw.f_juvenile_survival,.8,.8),
                                delays=(int(draw.f_delay),2,1))
            computed=out[out.draw==draw.draw].sort_values("vertex")
            np.testing.assert_allclose(computed.F_B,raw.F_B,atol=1e-10,rtol=0)
            np.testing.assert_allclose(computed.F_fraction,raw.F_fraction,
                                       atol=1e-10,rtol=0)

    def test_factorial_output_sign_controls_hold_a_single_cube_per_draw(self):
        frame=cube_design(self.structures.head(1),self.draws)
        rows=frame.copy()
        rows["F_B"]=np.exp(np.asarray(
            [4-3*(r.vertex//2%2)*(r.vertex%2)
             -2*(r.vertex//4)*(r.vertex%2)
             +2*(r.vertex//4)*(r.vertex//2%2)
             +(r.vertex//4)*(r.vertex//2%2)*(r.vertex%2)
             for r in rows.itertuples(index=False)]))
        x=summarize_cube_output(rows)
        self.assertEqual(len(x),4)
        self.assertTrue(x.matches_log.all())
        self.assertTrue(x[[f"sign_log_{p}" for p in METRICS]].eq([-1,-1,1,1]).all().all())
        with self.assertRaises(AssertionError):
            summarize_cube_output(rows.iloc[:-1])


if __name__=="__main__":
    unittest.main()
