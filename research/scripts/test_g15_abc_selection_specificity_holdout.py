"""G15 fixed null selection and source-mapping algebra tests."""
import unittest
import numpy as np
from g14_abc_ensemble_geographic_acoustic_holdout import original_four_interaction_coefficients
from abc_pom_main3600 import corner_contrasts
from g15_abc_selection_specificity_holdout import REP,SEED,SHARDS,MODELS,require

class TestG15Specificity(unittest.TestCase):
    def test_frozen_null_count_and_controls(self):
        self.assertEqual(REP,199)
        self.assertEqual(SEED,20261108)
        self.assertEqual(SHARDS,4)
        self.assertEqual(MODELS,("ABC_794","SIGN_ONLY"))
        self.assertEqual(set(range(0,REP,4)) |
                         set(range(1,REP,4)) |
                         set(range(2,REP,4)) |
                         set(range(3,REP,4)),set(range(REP)))
    def test_unit_signed_factorial_is_fixed(self):
        original=np.array([[-1.,-1.,1.,1.]])
        beta=original_four_interaction_coefficients(original)[0]
        np.testing.assert_allclose(beta,[-1.5,-1.5,.5,1.],atol=0,rtol=0)
        z=np.zeros((1,2,2,2))
        for v in range(2):
            for s in range(2):
                for o in range(2):
                    z[0,v,s,o]=beta[0]*s*o+beta[1]*v*o+beta[2]*v*s+beta[3]*v*s*o
        np.testing.assert_allclose(corner_contrasts(z),original,atol=1e-14,rtol=0)
    def test_bad_source_selectivity_request_stops(self):
        with self.assertRaises(AssertionError):
            require(False,"Invalid source")

if __name__=="__main__":
    unittest.main()
