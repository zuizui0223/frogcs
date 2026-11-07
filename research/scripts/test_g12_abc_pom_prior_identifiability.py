"""G12 pure synthetic prior/acceptance algebra tests with known truth."""
import unittest
import numpy as np
import pandas as pd
from g12_abc_pom_prior_identifiability import accept,weights,ess,diversity,PRIORS,EPS

class TestG12PriorDiagnostic(unittest.TestCase):
    def test_original_prior_is_unit_weight(self):
        x=pd.DataFrame({"attack":[.5,1.5,3.],
                        "rho":[.25,.5,.75],
                        "conversion":[2.,4.,8.]})
        w=weights(x,"uniform_original")
        np.testing.assert_allclose(w,np.ones(3),rtol=0,atol=0)
        self.assertEqual(ess(w),3)

    def test_all_nine_prior_scenarios_positive_and_frozen(self):
        self.assertEqual(len(PRIORS),9)
        x=pd.DataFrame({"attack":[.5,1.5,3.],
                        "rho":[.25,.5,.75],
                        "conversion":[2.,4.,8.]})
        for k in PRIORS:
            w=weights(x,k)
            self.assertTrue(np.isfinite(w).all())
            self.assertTrue((w>0).all())
            self.assertLessEqual(ess(w),3+1e-10)
        self.assertEqual(tuple(EPS),(0.,1e-6,1e-4,1e-3,1e-2,5e-2,1e-1))

    def test_strict_four_sign_epsilon(self):
        z=np.array([[-2.,-3.,2.,3.],[-.001,-.002,.003,.004],
                    [2.,-3.,2.,3.]],dtype=float)
        np.testing.assert_array_equal(accept(z,0),[True,True,False])
        np.testing.assert_array_equal(accept(z,.01),[True,False,False])

    def test_model_diversity_and_ess(self):
        d=diversity(np.array([1,2,3]),np.ones(3))
        self.assertEqual(d["distinct_accepted_models"],3)
        self.assertAlmostEqual(d["shannon_effective_models"],3)
        self.assertAlmostEqual(d["simpson_effective_models"],3)
        self.assertAlmostEqual(d["top10_accepted_mass"],1)
        self.assertEqual(ess(np.array([1.,0.,0.])),1)

if __name__=="__main__":
    unittest.main()
