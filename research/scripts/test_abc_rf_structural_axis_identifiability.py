"""Synthetic tests for actual 80-year ABC-RF grouped identifiability audit."""
import unittest

import numpy as np
import pandas as pd

from abc_rf_structural_axis_identifiability import (
    EXPECTED_CLASSES,EXPECTED_HELD,posterior_uncertainty,
    summarize_classifier_errors,AXES
)


def fixture():
    model=[f"{context}__{family}__risk{risk}"
           for context in ("original","D_first_S_overtakes","S_first_D_overtakes")
           for family in ("baseline","shared_both")
           for risk in (0,1)]
    data=[]
    post=[]
    for scale in ("log","raw","marginal_scale"):
        for i,actual in enumerate(model):
            for j,predicted in enumerate(model):
                n=26 if j in (i,(i+1)%12) else 0
                data.append(dict(scale=scale,true_structure=actual,
                                 predicted_structure=predicted,n=n,
                                 source_count=52,fraction=n/52))
            post.append(dict(scale=scale,structure_id=actual,
                             conditional_abc_model_share=.5 if i<2 else 0.,
                             n_accepted=1 if i<2 else 0))
    return pd.DataFrame(data),pd.DataFrame(post)


class ActualRFAttributeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.matrix,cls.abc=fixture()

    def test_full_confusion_rows_preserve_all_independent_holdout_source_units(self):
        a,b=summarize_classifier_errors(self.matrix)
        self.assertEqual(len(a),3*4)
        self.assertEqual(len(b),3*(3**2+2**2+2**2))
        self.assertTrue(a.n_heldout.eq(EXPECTED_HELD).all())
        self.assertTrue(a.heldout_accuracy.between(0,1).all())
        self.assertTrue(a.groupby("scale").axis.nunique().eq(4).all())
        self.assertTrue(a[a.axis=="full_12_classes"].heldout_accuracy.eq(.5).all())
        self.assertTrue(set(AXES).issubset(set(a.axis)))

    def test_hypothetical_model_posterior_concentration_is_conditional(self):
        a=posterior_uncertainty(self.abc)
        self.assertEqual(len(a),3)
        self.assertTrue(a.n_distinct_structures_with_positive_support.eq(2).all())
        np.testing.assert_allclose(a.conditional_effective_number_of_models,[2.]*3,atol=1e-10)
        np.testing.assert_allclose(a.top_two_class_share,[1.]*3,atol=1e-10)

    def test_drop_holdout_records_fails_closed(self):
        a=self.matrix.copy()
        a.loc[0,"n"]=25
        with self.assertRaises(ValueError):
            summarize_classifier_errors(a)
        x=self.matrix[self.matrix.scale!="log"]
        with self.assertRaises(ValueError):
            summarize_classifier_errors(x.iloc[:-1])

    def test_broken_abc_normalization_never_reported_as_confident(self):
        a=self.abc.copy()
        a.loc[0,"conditional_abc_model_share"]=.99
        with self.assertRaises(AssertionError):
            posterior_uncertainty(a)
        a=self.abc.iloc[:-1]
        with self.assertRaises(AssertionError):
            posterior_uncertainty(a)


if __name__=="__main__":
    unittest.main()
