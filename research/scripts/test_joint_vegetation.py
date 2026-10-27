import itertools
import unittest
import pandas as pd
import numpy as np
from check_joint_vegetation import assess


class JointVegetation(unittest.TestCase):
    def test_known_joint_interactions(self):
        d=pd.DataFrame([dict(context='test',vegetation=v,S_source=s,D_source=x,
                            F_B=20-v*x+v*s-.1*s*x,F_C=20-v*x+v*s-.1*s*x)
                        for v,s,x in itertools.product([0.,1.],[.25,1.,2.],[.25,1.,2.])])
        q=assess(d,['context'])
        np.testing.assert_allclose(q.DV,-1);np.testing.assert_allclose(q.SV,1)
        self.assertTrue(q.all_three_with_negative_D.all())
        pd.testing.assert_frame_equal(q,assess(d.sample(frac=1,random_state=1),['context']))

    def test_missing_cell_fails(self):
        with self.assertRaises(KeyError):
            assess(pd.DataFrame([dict(context='x',vegetation=0,S_source=1,D_source=1,F_B=1,F_C=1)]),['context'])


if __name__=='__main__':unittest.main()
