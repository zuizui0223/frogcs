"""Guard original G13 four-sign, entropy and exact-stratum null algebra."""
import unittest
import numpy as np
import pandas as pd

from g13_abc_pom_conditional_structure_null import (
    diversity,expectation_by_strata,features,AXES,B,SEED,
)

class TestG13ModelNativeStructureNull(unittest.TestCase):
    def test_entropy_and_unique_ids(self):
        ids=np.array([0,1,1,2,3,4,4,4],dtype=int)
        mask=np.array([False,True,True,True,False,False,True,True])
        n,h,top10,top50=diversity(ids,mask)
        self.assertEqual(n,3)
        self.assertGreater(h,2)
        self.assertLessEqual(h,3)
        self.assertEqual(top10,1.)
        self.assertEqual(top50,1.)

    def test_conditional_hypergeometric_expectation_variance(self):
        f=np.array([[1,0],[1,0],[0,1],[0,1]],dtype=bool)
        mean,var=expectation_by_strata(f,[np.arange(4)],[2])
        np.testing.assert_allclose(mean,[1.,1.])
        np.testing.assert_allclose(var,[1/3,1/3])

    def test_all_fixed_structural_axes_and_levels_encoded(self):
        self.assertEqual(B,4999)
        self.assertEqual(SEED,20261107)
        x=pd.DataFrame({k:[0,1,0] for k in AXES})
        col,flags=features(x)
        self.assertEqual(len(col),len(AXES)*2)
        self.assertEqual(flags.shape,(3,len(AXES)*2))
        self.assertTrue(flags.sum(axis=1).tolist()==[len(AXES)]*3)

    def test_invalid_empty_accepted_ids_must_stop(self):
        with self.assertRaises(AssertionError):
            diversity(np.array([1,2,3]),np.zeros(3,bool))

if __name__=="__main__":
    unittest.main()
