import unittest
import numpy as np
from exact_k_model import masks_for_k,group_features,log_probability,fit,route_fold

class ExactKUnit(unittest.TestCase):
    def test_combinatorial_denominators(self):
        from math import comb
        for k in (2,3,5,9):
            a=masks_for_k(k)
            self.assertEqual(a.shape,(comb(10,k),10))
            self.assertTrue(np.all(a.sum(axis=1)==k))
    def test_uniform_probability(self):
        x=np.arange(10,dtype=float)[:,None]
        y=np.array([1,1,1,0,0,0,0,0,0,0])
        _,possible,selected=group_features(x,y)
        self.assertAlmostEqual(log_probability(np.zeros(1),possible,selected),-np.log(120))
    def test_known_site_affinity(self):
        x=np.linspace(-1,1,10)[:,None]
        y=np.array([0,0,0,0,0,0,0,0,1,1])
        _,possible,selected=group_features(x,y)
        b=fit([(possible,selected)]*20,1)
        self.assertGreater(b[0],0)
        self.assertGreater(log_probability(b,possible,selected),log_probability(np.zeros(1),possible,selected))
    def test_route_fold_deterministic(self):
        self.assertEqual(route_fold("VA","880011"),route_fold("VA","880011"))
    def test_zero_or_all_ten_rejected(self):
        with self.assertRaises(ValueError):
            group_features(np.ones((10,2)),np.zeros(10))
    def test_invariance_to_route_mean(self):
        x=np.column_stack([np.arange(10),np.arange(10)*.1])
        y=np.array([1,1,0,0,0,0,0,0,0,0])
        _,a,b=group_features(x,y)
        _,c,d=group_features(x+100,y)
        self.assertTrue(np.allclose(a,c))
        self.assertTrue(np.allclose(b,d))

if __name__=="__main__":unittest.main()
