"""Synthetic checks for direction-only, low-S ternary and duplicate-safe POM."""
import unittest

import numpy as np

from test_select_macro_trophic_scenarios import test_sites, source_fixture
from select_macro_trophic_scenarios import load_cohort, scenario_surfaces
from pattern_oriented_abc_pilot import (
    get_design, stats_from_y, bootstrap_observed, group_exact_surfaces
)
from directional_pom_132 import (
    PATTERNS, LOW_S, observational_categories,
    selected_directional_constraints, agreement, probability_rows,
    rank_direction_groups, nuisance_draws, simulate_response_states, site_response
)


class DirectionalPOMTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        a,b=test_sites(block_count=15,sites_per_block=6)
        cls.d=load_cohort(a,b,expected=90)
        all_surfaces,_=scenario_surfaces([source_fixture()])
        unique=sorted(all_surfaces)
        cls.surfaces={name:all_surfaces[name] for name in unique[:3]}
        cls.surfaces["duplicate_000"]=cls.surfaces[unique[0]].copy()
        cls.bg="uniform";cls.design=get_design(cls.d,cls.bg)

    def test_uncertain_symbols_not_assumed_directions(self):
        r=np.random.default_rng(4)
        b=r.normal(size=(999,6))
        b[:,0]=-3.
        b[:,1]=-2.
        b[:,2]=r.normal(size=999)
        b[:,3]=r.normal(size=999)
        b[:,4]=r.normal(loc=.02,scale=.001,size=999)
        b[:,5]=-1.
        obs,delta=observational_categories(b)
        self.assertGreaterEqual(delta,.05)
        self.assertEqual(selected_directional_constraints(obs),(0,1,5,4))
        self.assertTrue((obs[:,LOW_S]==0).all())
        self.assertTrue((obs[:,0]==-1).all())

    def test_joint_matching_keeps_correlations_and_ternary(self):
        obs=np.array([[-1,-1,1,1,0,-1],
                      [-1,-1,1,1,0,-1]],dtype=np.int8)
        sim=np.array([[-1,-1,1,1,0,-1],
                      [-1,1,1,1,1,-1]],dtype=np.int8)
        soft,exact,composite=agreement(obs,sim,(0,1,5,4))
        self.assertAlmostEqual(exact,.5)
        self.assertAlmostEqual(soft,.53125)
        self.assertAlmostEqual(composite,.25)
        self.assertEqual(probability_rows(obs,[4]).shape,(1,3))

    def test_exact_source_duplicates_share_stochastic_outcomes(self):
        eq,groups=group_exact_surfaces(self.surfaces)
        self.assertEqual(eq[next(iter(self.surfaces))],eq["duplicate_000"])
        rng=nuisance_draws(self.d,5,seed=1009)
        delta=.10
        a=simulate_response_states(self.d,self.bg,self.design,
                                   self.surfaces[next(iter(self.surfaces))],
                                   delta,rng)
        b=simulate_response_states(self.d,self.bg,self.design,
                                   self.surfaces["duplicate_000"],delta,rng)
        np.testing.assert_array_equal(a,b)

    def test_rank_and_recovery_do_not_duplicate_exact_source_probability(self):
        target=stats_from_y(self.d.strong_rate,self.design)
        boot,_,_,_=bootstrap_observed(self.d.strong_rate,self.design,
                                      self.d.spatial_block,n_boot=99)
        _,h=group_exact_surfaces(self.surfaces)
        eq={min(members):sorted(members) for members in h.values()}
        scores,signatures,obs,rec,receipt,probs,_=rank_direction_groups(
            self.d,self.bg,self.surfaces,eq,target,boot,nreps=5,nrecovery=2)
        self.assertEqual(len(scores),4)
        self.assertEqual(receipt["n_exact_source_groups"],3)
        self.assertEqual(len(rec),3*2)
        self.assertEqual(int(signatures.n_case_labels.sum()),4)
        self.assertEqual(len(obs),len(PATTERNS))
        self.assertTrue(scores.joint_direction_soft_score.between(0,1).all())
        self.assertTrue(rec.directional_group_recovered.isin([True,False]).all())
        p=scores.set_index("case")
        np.testing.assert_allclose(
            p.loc["duplicate_000",["joint_direction_soft_score",
                                    "strict_joint_matching_probability"]].to_numpy(float),
            p.loc[next(iter(self.surfaces)),["joint_direction_soft_score",
                                              "strict_joint_matching_probability"]].to_numpy(float),
            atol=0,rtol=0)

    def test_bad_categorical_coverage_rejected(self):
        with self.assertRaises(ValueError):
            observational_categories(np.ones((3,4)))
        with self.assertRaises(ValueError):
            agreement(np.ones((4,6)),np.ones((3,6)),())
        with self.assertRaises(ValueError):
            observational_categories(np.ones((4,6)),threshold=-1)


if __name__=="__main__":
    unittest.main()
