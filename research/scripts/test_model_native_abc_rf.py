"""ABC-RF 4-sign model-choice invariants with equal structural priors.

Synthetic-only check; the actual 3x4 structural-reference validation occurs
in the GitHub Actions job against genuinely rerun 80-year source artifacts.
"""
import unittest
import numpy as np
import pandas as pd
from tempfile import TemporaryDirectory
from pathlib import Path

from model_native_abc_rf import (
    SCALES,RF_N_CLASSES,PRIOR_PARAMS,features,wilson_ci,
    reject_four_sign_abc,rf_model_choice,sign_fingerprint_equivalence,
    load_actual_refs
)
from model_native_2x2x2_prior import METRICS,TARGET


def fake_abc(n=20):
    rng=np.random.default_rng(330)
    original=[]
    prior=[]
    contexts=("original","D_first_S_overtakes","S_first_D_overtakes")
    for draw in range(n):
        prior.append(dict(draw=draw,attack_scale=.25+.01*draw,
            s_growth_multiplier=.8,d_growth_multiplier=1.1,
            rho=.7,conversion=4.,f_juvenile_survival=.8,
            f_adult_survival=.4,f_delay=2+draw%2))
    for context in contexts:
        for family in ("baseline","shared_both"):
            for risk in (False,True):
                cls=f"{context}__{family}__risk{int(risk)}"
                cidx=len(original)//(n*2)
                for draw in range(n):
                    for reverse in (0,1):
                        signs=np.asarray(TARGET).copy()
                        # Ensure all 12 structural classes are preserved and
                        # some generate target; others have deterministic mismatch.
                        if cidx>=3:
                            signs[cidx%4]*=-1
                        if draw%11==0:
                            signs[(cidx+2)%4]=0
                        raw=signs.copy()
                        if draw%3==0:raw[1]*=-1
                        rec=dict(context=context,family=family,risk=risk,
                                 structure_id=cls,draw=draw,reverse_on=reverse,
                                 original_case=cidx,case_id=cidx,
                                 matches_log=bool(np.array_equal(signs,TARGET)),
                                 matches_raw=bool(np.array_equal(raw,TARGET)))
                        for mode,s in (("log",signs),("raw",raw)):
                            for i,k in enumerate(METRICS):
                                rec[f"sign_{mode}_{k}"]=int(s[i])
                        original.append(rec)
    return pd.DataFrame(original),pd.DataFrame(prior)


class ModelNativeABCRFTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.reference,cls.prior=fake_abc()

    def test_exact_sign_abc_preserves_equal_class_priors_and_rates(self):
        a,p,_=reject_four_sign_abc(self.reference,self.prior,"log")
        self.assertEqual(len(a),12)
        self.assertTrue(a.n_actual_simulations.eq(40).all())
        self.assertEqual(len(p),12*len(PRIOR_PARAMS))
        self.assertTrue(a.acceptance_rate.between(0,1).all())
        self.assertAlmostEqual(a.conditional_abc_model_share.sum(),1.,places=12)
        self.assertEqual(int(a.n_accepted.sum()),
                         int(self.reference.matches_log.sum()))
        self.assertTrue(p.n_enough_for_interpretation.isin([True,False]).all())

    def test_empirical_posterior_is_sensitive_to_response_scale(self):
        x,_,_=reject_four_sign_abc(self.reference,self.prior,"log")
        y,_,_=reject_four_sign_abc(self.reference,self.prior,"raw")
        self.assertGreater(abs(x.acceptance_rate.to_numpy()-
                               y.acceptance_rate.to_numpy()).sum(),0)
        z,_,_=reject_four_sign_abc(self.reference,self.prior,"marginal_scale")
        self.assertEqual(len(z),12)

    def test_balanced_nuisance_reversal_and_scale(self):
        a=features(self.reference,"log")
        b=features(self.reference,"raw")
        c=features(self.reference,"marginal_scale")
        self.assertEqual(a.shape,(12*20*2,4))
        self.assertEqual(c.shape,a.shape)
        self.assertTrue(np.isin(c,[-1,0,1]).all())
        np.testing.assert_array_equal(c,features(self.reference,"marginal_scale"))
        self.assertFalse(np.array_equal(a,b))
        s=self.reference
        self.assertTrue(s.groupby(["structure_id","draw"]).reverse_on.nunique().eq(2).all())

    def test_wilson_interval_and_invalid_counts(self):
        self.assertAlmostEqual(wilson_ci(0,100)[0],0.)
        self.assertAlmostEqual(wilson_ci(100,100)[1],1.)
        lo,hi=wilson_ci(50,100)
        self.assertLess(lo,.5)
        self.assertGreater(hi,.5)
        with self.assertRaises(ValueError):wilson_ci(3,2)

    def test_correct_two_stage_oob_error_and_draw_block_holdout(self):
        d,conf,imp=rf_model_choice(self.reference,"log")
        self.assertEqual(len(conf),12*12)
        self.assertEqual(len(imp),4)
        self.assertTrue(0<=d["prior_oob_error"]<=1)
        self.assertTrue(0<=d["holdout_model_accuracy"]<=1)
        self.assertTrue(0<=d["conditional_rf_selected_class_support"]<=1)
        self.assertEqual(d["n_reference_train"]+d["n_reference_holdout"],len(self.reference))
        self.assertEqual(int(conf.n.sum()),d["n_reference_holdout"])
        self.assertEqual(d["n_process_draws_train"]+d["n_process_draws_holdout"],20)
        self.assertTrue(conf.groupby("true_structure").fraction.sum().between(.99999,1.00001).all())

    def test_empirically_identical_sign_vectors_can_be_grouped(self):
        eq=sign_fingerprint_equivalence(self.reference)
        self.assertEqual(eq.groupby("scale").n_structures.sum().to_dict(),
                         {"log":12,"raw":12})
        self.assertTrue(eq.n_structures.ge(1).all())

    def test_missing_real_source_refuse_to_report_abc(self):
        with TemporaryDirectory() as td:
            with self.assertRaises(FileNotFoundError):
                load_actual_refs(Path(td))


if __name__=="__main__":
    unittest.main()
