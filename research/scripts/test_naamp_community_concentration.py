import unittest
import numpy as np
from scipy.special import expit
from naamp_community_concentration import ProfiledPairs, endpoint, require_disjoint_routes

class ConcentrationTests(unittest.TestCase):
    def test_pair_total_and_shift(self):
        offsets=[np.array([-2.,0,1,3]),np.array([-1.,2,3])]
        ys=[np.array([0,1,0,1]),np.array([0,1,0])]
        model=ProfiledPairs(offsets,[np.zeros(4),np.zeros(3)],ys)
        q=model.probabilities(0)
        self.assertAlmostEqual(q[:4].sum(),2,places=9)
        self.assertAlmostEqual(q[4:].sum(),1,places=9)
        for offset,target,got in [(offsets[0],2,q[:4]),(offsets[1],1,q[4:])]:
            lo,hi=-50.,50.
            for _ in range(80):
                mid=(lo+hi)/2
                if expit(offset+mid).sum()<target:lo=mid
                else:hi=mid
            np.testing.assert_allclose(got,expit(offset+(lo+hi)/2),atol=1e-10)

    def test_boundary_counts(self):
        model=ProfiledPairs([np.zeros(2),np.zeros(3)],[np.ones(2),np.ones(3)],[[0,0],[1,1,1]])
        np.testing.assert_allclose(model.probabilities(3),[0,0,1,1,1],atol=1e-12)
        self.assertTrue(np.isfinite(model.logscores(3)).all())

    def test_endpoints(self):
        w=np.array([[1,1,1,1],[0,1,0,0],[1,1,1,1]],bool)
        d=np.array([[0,0,0,0],[0,0,0,0],[1,0,0,0]],bool)
        np.testing.assert_equal(endpoint(w,d),[2,3,3])

    def test_zero_predictor_and_fold_leak(self):
        m=ProfiledPairs([np.zeros(3)],[np.zeros(3)],[[1,0,0]])
        np.testing.assert_allclose(m.logscores(2),m.logscores(0))
        require_disjoint_routes(['a'],['b'])
        with self.assertRaises(ValueError):require_disjoint_routes(['a'],['a'])

if __name__=='__main__':unittest.main()
