"""Synthetic-only checks of signed context modulation, shared-block bootstrap.

Not a biological or independent observation validation.
"""
import unittest

import numpy as np

from test_select_macro_trophic_scenarios import test_sites,source_fixture
from select_macro_trophic_scenarios import load_cohort,scenario_surfaces
from pattern_oriented_abc_pilot import (
    get_design, stats_from_y, group_exact_surfaces, site_response
)
from directional_pom_132 import nuisance_draws
from directional_context_modulation_pom import (
    METRICS, contrast_point, joint_observed_bootstrap, selected_observed_signs,
    joint_direction_score, simulated_contrasts, rank_fixed_132
)


class SignedContextAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        sites,visits=test_sites(block_count=15,sites_per_block=6)
        cls.d=load_cohort(sites,visits,expected=90)
        cls.design=get_design(cls.d,"uniform")
        full,_=scenario_surfaces([source_fixture()])
        cls.surfaces=dict(list(sorted(full.items()))[:4])
        cls.surfaces["identical_case"]=cls.surfaces["case_000"].copy()
        _,groups=group_exact_surfaces(cls.surfaces)
        cls.groups={min(v):sorted(v) for v in groups.values()}

    def test_direct_signed_context_difference_is_same_as_original_parts(self):
        y=self.d.strong_rate.to_numpy()
        got=contrast_point(y,self.design)
        a,b=stats_from_y(y,self.design,holdout=True)
        self.assertEqual(len(got),len(METRICS))
        np.testing.assert_allclose(got,[a[0],a[1],a[5]-a[4],b[1]-b[0]],
                                   rtol=0,atol=1e-12)

    def test_high_s_and_vegetation_modulation_can_be_directly_negative(self):
        o=self.design["o"]
        s=self.design["s"]
        high=s>np.median(s)
        response=o*np.where(high,-1.,1.)
        res=contrast_point(response,self.design)
        self.assertLess(res[2],-.5)
        response_v=o*np.where(self.d.V.to_numpy()>0,-1.,1.)
        self.assertLess(contrast_point(response_v,self.design)[3],-.5)

    def test_common_bootstrap_is_replayable_and_finite(self):
        a=joint_observed_bootstrap(self.d.strong_rate,self.d,self.design,
                                   n_boot=99,seed=37)
        b=joint_observed_bootstrap(self.d.strong_rate,self.d,self.design,
                                   n_boot=99,seed=37)
        self.assertEqual(a.shape,(99,4))
        np.testing.assert_array_equal(a,b)
        obs=contrast_point(self.d.strong_rate,self.design)
        selection,sign,table=selected_observed_signs(obs,a,confidence=.60)
        self.assertGreaterEqual(len(selection),1)
        self.assertEqual(len(table),4)
        self.assertTrue(table.frequency_negative.between(0,1).all())
        self.assertTrue(np.isfinite(table.observed).all())

    def test_no_unsupported_direction_selected(self):
        raw=np.array([[-1,-1,-1,1],[-1,1,-1,-1],
                      [-1,-1,-1,1],[-1,1,-1,-1]],float)
        selection,point,table=selected_observed_signs(
            [-1,-.3,-.8,.1],raw,confidence=.9)
        self.assertEqual(selection,(0,2))
        with self.assertRaises(ValueError):
            selected_observed_signs([-1,-.3,-.8,.1],raw,confidence=.5)

    def test_joint_scoring_is_not_a_product_of_marginal_probabilities(self):
        obs=np.array([[-1,-1,-1,-1],[-1,-1,-1,-1]],float)
        sim=np.array([[-1,-1,-1,-1],[-1,1,-1,1]],float)
        score,exact=joint_direction_score(obs,sim,(0,1,2,3))
        self.assertAlmostEqual(score,.53125)
        self.assertAlmostEqual(exact,.5)

    def test_identical_frozen_sources_have_identical_predictions(self):
        grid=self.surfaces["case_000"]
        draws=nuisance_draws(self.d,5,seed=2207)
        p=simulated_contrasts(self.d,"uniform",self.design,grid,draws)
        q=simulated_contrasts(self.d,"uniform",self.design,
                              self.surfaces["identical_case"],draws)
        np.testing.assert_array_equal(p,q)

    def test_full_grouping_and_pseudo_recovery_under_shared_noise(self):
        y=self.d.strong_rate
        point=contrast_point(y,self.design)
        boot=joint_observed_bootstrap(y,self.d,self.design,n_boot=99)
        selected,sign,_=selected_observed_signs(point,boot,confidence=.6)
        scores,groups,rec,conf=rank_fixed_132(self.d,"uniform",self.design,
                            boot,selected,sign,self.surfaces,self.groups,
                            n_model=5,n_recovery=2)
        self.assertEqual(len(scores),len(self.surfaces))
        self.assertEqual(int(groups.n_cases.sum()),len(self.surfaces))
        self.assertEqual(len(rec),len(self.groups)*2)
        self.assertEqual(int(conf.n.sum()),len(rec))
        self.assertTrue(conf.groupby(["background","true_signature"]).fraction
                        .sum().between(.999999,1.000001).all())
        self.assertTrue(scores.joint_soft.between(0,1).all())
        rep=scores.set_index("case")
        self.assertEqual(rep.loc["case_000","joint_soft"],
                         rep.loc["identical_case","joint_soft"])
        self.assertEqual(rep.loc["case_000","source_group"],
                         rep.loc["identical_case","source_group"])


if __name__ == "__main__":
    unittest.main()
