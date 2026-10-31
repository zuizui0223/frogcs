"""Synthetic tests for an assumed (not calibrated) nonnegative observation link."""
import unittest
import numpy as np

from test_select_macro_trophic_scenarios import test_sites, source_fixture
from select_macro_trophic_scenarios import (
    fit_predict, load_cohort, scenario_surfaces, assign_folds, fixed_nested_comparison
)
from diagnose_monotone_observation_link import compute_fixed_choice_constrained


class MonotoneLinkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        sites,visits=test_sites()
        cls.d=load_cohort(sites,visits,expected=90)
        cls.surfaces,_=scenario_surfaces([source_fixture()])
        cls.folds=assign_folds(cls.d,5)
        _,_,cls.choices=fixed_nested_comparison(
            cls.d,cls.surfaces,cls.folds,restrict_candidates=list(sorted(cls.surfaces))[:3])

    def test_negative_free_slope_reduces_to_additive_null(self):
        rng=np.random.default_rng(32)
        n=90
        cov=rng.normal(0,1,n)
        feature=np.linspace(-2,2,n)
        x=np.column_stack([cov,feature])
        response=np.rint(10/(1+np.exp(2*feature))).astype(float)
        trials=np.full(n,10.)
        free,slope=fit_predict(x,response,trials,x,return_mechanism_slope=True)
        limited,beta=fit_predict(x,response,trials,x,return_mechanism_slope=True,
                                 nonnegative_mechanism=True)
        null=fit_predict(x[:,:1],response,trials,x[:,:1])
        self.assertLess(slope,0)
        self.assertGreaterEqual(beta,0)
        self.assertLessEqual(beta,2e-6)
        np.testing.assert_allclose(limited,null,rtol=0,atol=3e-5)
        self.assertGreater(np.mean(np.abs(free-null)),.05)

    def test_positive_free_slope_retained_by_bound(self):
        x=np.column_stack([np.sin(np.arange(75)*1.2),np.linspace(-2,2,75)])
        y=np.rint(10/(1+np.exp(-2*x[:,1]))).astype(float)
        n=np.full(75,10.)
        u,b=fit_predict(x,y,n,x,return_mechanism_slope=True)
        c,bc=fit_predict(x,y,n,x,return_mechanism_slope=True,nonnegative_mechanism=True)
        self.assertGreater(b,0)
        self.assertGreater(bc,0)
        np.testing.assert_allclose(u,c,rtol=0,atol=2e-5)

    def test_all_folds_replayed_without_new_winner_search(self):
        data,slopes,summary=compute_fixed_choice_constrained(
            self.d,self.surfaces,self.choices,reps=49)
        self.assertEqual(len(data),180)
        self.assertEqual(len(slopes),10)
        self.assertEqual(len(summary),30)
        self.assertTrue(slopes.nonnegative_standardized_slope.ge(-1e-9).all())
        self.assertTrue(data.p_nonnegative.between(0,1,inclusive="neither").all())
        self.assertTrue(summary.n_visits.gt(0).all())

    def test_holdout_labels_do_not_affect_constrained_fold_predictions(self):
        original,slopes,_=compute_fixed_choice_constrained(
            self.d,self.surfaces,self.choices,reps=39)
        changed=self.d.copy();mask=self.folds==0
        changed.loc[mask,"k"]=changed.loc[mask,"n"]-changed.loc[mask,"k"]
        modified,slopes2,_=compute_fixed_choice_constrained(
            changed,self.surfaces,self.choices,reps=39)
        for bg in ("uniform","target_group"):
            a=original[(original.background==bg)&(original.outer_fold==0)].sort_values("site")
            b=modified[(modified.background==bg)&(modified.outer_fold==0)].sort_values("site")
            np.testing.assert_array_equal(a.p_nonnegative.to_numpy(),b.p_nonnegative.to_numpy())
            np.testing.assert_array_equal(
                slopes[(slopes.background==bg)&(slopes.outer_fold==0)].nonnegative_standardized_slope,
                slopes2[(slopes2.background==bg)&(slopes2.outer_fold==0)].nonnegative_standardized_slope)


if __name__=="__main__":
    unittest.main()
