"""Synthetic and replay invariants only. No field-mechanism assertions."""
import unittest
import numpy as np
import pandas as pd
from test_select_macro_trophic_scenarios import test_sites, source_fixture
from select_macro_trophic_scenarios import (
    load_cohort, scenario_surfaces, assign_folds, fixed_nested_comparison,
    fit_predict, predictor_design, candidate_scores_at_sites,
)
from diagnose_macro_scenario_information import (
    candidate_information, reversals_independent, replay_selected,
    stratum_score, fraction_independent,
)


class MechanismInformationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        sites,visits=test_sites()
        cls.d=load_cohort(sites,visits,expected=90)
        cls.surfaces,cls.metadata=scenario_surfaces([source_fixture()])
        cls.folds=assign_folds(cls.d,5)
        cls.pred,cls.inner,cls.choices=fixed_nested_comparison(
            cls.d,cls.surfaces,cls.folds,restrict_candidates=list(sorted(cls.surfaces))[:3])

    def test_partial_information_bounds(self):
        info=candidate_information(self.d,self.surfaces)
        self.assertEqual(len(info),48)
        self.assertTrue(info.log_f_sd.gt(0).all())
        self.assertTrue(info.frac_not_explained_by_interactions.between(0,1).all())
        self.assertTrue(info.frac_not_explained_by_additive.between(0,1).all())
        self.assertTrue((info.frac_not_explained_by_interactions <=
                         info.frac_not_explained_by_additive+1e-8).all())
        x=np.arange(15.)[:,None]
        self.assertAlmostEqual(fraction_independent(np.arange(15.),x),0.,places=10)

    def test_exact_reversal_pairs_without_collapsing_cases(self):
        result=reversals_independent(self.surfaces,self.metadata)
        self.assertEqual(len(result),12)
        self.assertTrue(result.n_changed_cells_gt_1e_10.gt(0).all())
        self.assertTrue(result.grid_cells.eq(162).all())

    def test_unchanged_cv_predictions_and_mechanism_coefficients(self):
        info=candidate_scores_at_sites(self.d,"uniform",self.surfaces)
        design=predictor_design(self.d,"uniform",info)
        x=design["case_000"]
        train=self.folds!=0;test=~train
        p=fit_predict(x[train],self.d.k[train].to_numpy(),self.d.n[train].to_numpy(),x[test])
        q,slope=fit_predict(x[train],self.d.k[train].to_numpy(),self.d.n[train].to_numpy(),x[test],
                            return_mechanism_slope=True)
        np.testing.assert_array_equal(p,q)
        self.assertTrue(np.isfinite(slope))

    def test_replay_selection_and_vegetation_strata(self):
        replay,slopes=replay_selected(self.d,self.surfaces,self.choices)
        self.assertEqual(len(replay),180)
        self.assertEqual(len(slopes),10)
        self.assertTrue(np.isfinite(slopes.normalized_log_F_B_coefficient).all())
        scores,support=stratum_score(replay,reps=99)
        self.assertEqual(len(scores),18)
        self.assertEqual(len(support),6)
        self.assertEqual(set(scores.vegetation_support),{"all","V_positive","V_zero"})
        for bg in ("uniform","target_group"):
            sub=scores[scores.background==bg]
            total=sub[sub.vegetation_support=="all"].n_visits.iloc[0]
            npos=sub[sub.vegetation_support=="V_positive"].n_visits.iloc[0]
            nzero=sub[sub.vegetation_support=="V_zero"].n_visits.iloc[0]
            self.assertEqual(total,npos+nzero)

    def test_heldout_outcome_change_does_not_retrain_that_fold(self):
        first,coeff=replay_selected(self.d,self.surfaces,self.choices)
        changed=self.d.copy()
        mask=self.folds==0
        changed.loc[mask,"k"]=changed.loc[mask,"n"]-changed.loc[mask,"k"]
        second,coeff2=replay_selected(changed,self.surfaces,self.choices)
        for bg in ("uniform","target_group"):
            a=first[(first.background==bg)&(first.outer_fold==0)].sort_values("site")
            b=second[(second.background==bg)&(second.outer_fold==0)].sort_values("site")
            for col in ("p_scenario","p_selected_environment","p_env_additive","p_env_interactions"):
                np.testing.assert_array_equal(a[col].to_numpy(),b[col].to_numpy())
            ab=coeff[(coeff.background==bg)&(coeff.outer_fold==0)]
            bb=coeff2[(coeff2.background==bg)&(coeff2.outer_fold==0)]
            np.testing.assert_array_equal(ab.normalized_log_F_B_coefficient,
                                          bb.normalized_log_F_B_coefficient)


if __name__=="__main__":
    unittest.main()
