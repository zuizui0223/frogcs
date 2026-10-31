"""Exact factorial OS/OV/SV/OSV orientations and frozen POM integrity."""
import unittest
import numpy as np
import pandas as pd
from abc_intrinsic_factorial import (
    one_factorial,sign_code,eight_corners,subset_corners,
    catalogue_structure,summarize_factorial,TARGET,METRICS
)


class IntrinsicFactorialTests(unittest.TestCase):
    def test_contrasts_obey_true_binary_interaction_orientation(self):
        corners=eight_corners()
        v=corners[:,0];s=(corners[:,1]>1).astype(float)
        o=(corners[:,2]>1).astype(float)
        for name,vector,axis in [
            ("OS",2*o*s,0),("OV",-3*o*v,1),
            ("SV",4*s*v,2),("OSV",5*o*s*v,3)]:
            contrasts=one_factorial(vector.reshape(1,8))[0]
            self.assertAlmostEqual(contrasts[axis],[2.,-3.,4.,5.][axis],places=12)
            for k in range(4):
                if k!=axis:
                    self.assertAlmostEqual(contrasts[k],0.,places=12)

    def test_full_target_four_signs_and_zero_as_nonmatch(self):
        corners=eight_corners()
        v=corners[:,0];s=(corners[:,1]>1).astype(float)
        o=(corners[:,2]>1).astype(float)
        values=np.exp(.2-1*o*s-1*o*v+1*s*v+2*o*s*v)
        signed=sign_code(one_factorial(np.log(values).reshape(1,8)))[0]
        np.testing.assert_array_equal(signed,TARGET)
        null=sign_code(one_factorial(np.ones((1,8))))[0]
        self.assertTrue((null==0).all())
        self.assertFalse(np.array_equal(null,TARGET))

    def test_main_12_structures_pair_reversal_and_eight_cells(self):
        cases,grid=catalogue_structure()
        self.assertEqual(cases.structural_class.nunique(),12)
        self.assertEqual(len(cases),24)
        self.assertEqual(len(grid),24*162)
        self.assertTrue(cases.groupby("structural_class").edge.nunique().eq(2).all())
        reduced=subset_corners(grid)
        self.assertEqual(len(reduced),24*8)

    def test_empty_or_duplicate_corners_fail_closed(self):
        corners=eight_corners()
        rows=[dict(case=1,vegetation=v,S_source=s,D_source=d,F_B=1.+v+s+d)
              for v,s,d in corners]
        f=pd.DataFrame(rows)
        self.assertEqual(len(summarize_factorial(f)),2)
        for x in (f.iloc[:-1],pd.concat([f,f.iloc[[0]]]),f.assign(F_B=0.)):
            with self.assertRaises(ValueError):
                summarize_factorial(x)

    def test_response_transform_may_reverse_interaction_sign(self):
        # Multiplicative and additive scales are BOTH retained. A raw
        # interaction may differ from a log interaction for positive outputs.
        rng=np.random.default_rng(7)
        found=False
        for _ in range(150):
            y=np.exp(rng.normal(0,1,8))
            log=sign_code(one_factorial(np.log(y)[None,:]))[0]
            raw=sign_code(one_factorial(y[None,:]))[0]
            if np.any(log!=raw):found=True;break
        self.assertTrue(found)


if __name__=="__main__":
    unittest.main()
