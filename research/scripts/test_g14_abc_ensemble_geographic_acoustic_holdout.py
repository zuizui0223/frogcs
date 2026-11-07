"""G14 test: exact eight-corner interaction algebra, source population labels."""
import unittest
import numpy as np

from abc_pom_main3600 import corner_contrasts
from g14_abc_ensemble_geographic_acoustic_holdout import (
    original_four_interaction_coefficients,TEMPLATES,BASELINES,
)

class TestG14LogFactorialMapping(unittest.TestCase):
    def test_exact_2x2x2_interaction_basis_mapping(self):
        q=np.array([[.7,-1.1,.6,-.3],[-.8,.2,-.1,.4]])
        for v in q:
            z=np.empty((1,2,2,2))
            for V in (0,1):
                for S in (0,1):
                    for D in (0,1):
                        z[0,V,S,D]=(2.+.2*V-.7*S+.3*D
                                    +v[0]*S*D+v[1]*V*D
                                    +v[2]*V*S+v[3]*V*S*D)
            a=corner_contrasts(z)
            reconstructed=original_four_interaction_coefficients(a)
            np.testing.assert_allclose(reconstructed[0],v,atol=1e-14,rtol=0)

    def test_fixed_full_family_and_no_field_outcome_selection(self):
        self.assertEqual(TEMPLATES,(
            "ABC_accepted","ABC_accepted_viable","all_20000_prior","R2_rejected"))
        self.assertEqual(BASELINES,("flex_add","flex_all"))

    def test_missing_or_nonfinite_original_four_contrasts_rejected(self):
        with self.assertRaises(AssertionError):
            original_four_interaction_coefficients(np.array([[np.nan,0,0,0]]))
        with self.assertRaises(AssertionError):
            original_four_interaction_coefficients(np.zeros((4,3)))

if __name__=="__main__":
    unittest.main()
