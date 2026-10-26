import unittest
import numpy as np
from naamp_prior_community_allocation import conditional_loglik, other_history, Likelihood, subsets
from scipy.special import logsumexp


class ConditionalTests(unittest.TestCase):
    def test_uniform_one_and_two(self):
        self.assertAlmostEqual(conditional_loglik(np.zeros(3), np.zeros(3), [1,0,0], 0), -np.log(3))
        self.assertAlmostEqual(conditional_loglik(np.zeros(3), np.zeros(3), [1,1,0], 0), -np.log(3))

    def test_weighted_and_constant_invariance(self):
        eta=np.log([1.,2.,3.])
        self.assertAlmostEqual(conditional_loglik(eta, np.zeros(3), [0,1,1], 0), np.log(6/11))
        self.assertAlmostEqual(conditional_loglik(eta, np.ones(3), [0,1,1], 4), np.log(6/11))

    def test_target_exclusion_and_missing(self):
        y=np.array([[2,0],[1,3]],float)
        exposure=np.array([2,4],float)
        np.testing.assert_allclose(other_history(y, exposure, 0), [.5,.75])
        with self.assertRaises(ValueError): other_history(y, [0,4], 0)

    def test_avoidance_sign(self):
        self.assertGreater(conditional_loglik(np.zeros(3), [0,1,2], [1,0,0], -1), conditional_loglik(np.zeros(3), [0,1,2], [1,0,0], 1))

    def test_batched_fitting_path_matches_enumeration(self):
        rng=np.random.default_rng(20261026)
        rows=[]; cases=[]
        for k in range(1,10):
            offset=rng.normal(size=10); x=rng.normal(size=10)
            y=np.arange(10)<k; comb=subsets(10,k)
            b=offset[comb].sum(axis=1); b-=logsumexp(b)
            rows.append(dict(b=b,x=x[comb].sum(axis=1),observed_x=x[y].sum(),
                             base_ll=conditional_loglik(offset,x,y,0)))
            cases.append((offset,x,y))
        for beta in [-5,-1,0,1,5]:
            expected=[conditional_loglik(o,x,y,beta)-conditional_loglik(o,x,y,0) for o,x,y in cases]
            np.testing.assert_allclose(Likelihood(rows).gain(beta),expected,atol=1e-12)


if __name__ == '__main__': unittest.main()
