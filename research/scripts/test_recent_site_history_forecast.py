import importlib.util
from pathlib import Path
import unittest
import numpy as np

PATH=Path(__file__).with_name('recent_site_history_forecast.py')

class ForecastTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.module=None
        if PATH.exists():
            spec=importlib.util.spec_from_file_location('recent_forecast',PATH)
            cls.module=importlib.util.module_from_spec(spec);spec.loader.exec_module(cls.module)

    def test_implementation_exists(self):
        self.assertIsNotNone(self.module, 'Forecast implementation has not yet been written')

    def test_exact_mask_count(self):
        if self.module is None:self.skipTest('red implementation gate')
        from math import comb
        for k in range(11):
            m=self.module.masks(k)
            self.assertEqual(m.shape,(comb(10,k),10))
            np.testing.assert_array_equal(m.sum(1),np.full(len(m),k))

    def test_probability_normalization_and_offset_invariance(self):
        if self.module is None:self.skipTest('red implementation gate')
        eta=np.arange(10)*.13
        m=self.module.masks(3)
        from scipy.special import logsumexp
        lp=m@eta-logsumexp(m@eta)
        self.assertAlmostEqual(float(np.exp(lp).sum()),1.,places=12)
        np.testing.assert_allclose(lp,m@(eta+5)-logsumexp(m@(eta+5)),atol=1e-12)

    def test_features_exclude_recent_and_current_from_background(self):
        if self.module is None:self.skipTest('red implementation gate')
        hist={y:np.zeros(10) for y in range(2001,2007)}
        hist[2004]=np.ones(10); hist[2005][0]=1;hist[2006]=np.ones(10)
        z,r,o,n=self.module.features(hist,2006)
        self.assertEqual(n,3)
        np.testing.assert_allclose(z,np.log(.125/.875))
        np.testing.assert_array_equal(r,hist[2005]);np.testing.assert_array_equal(o,hist[2004])
        hist[2006]=np.zeros(10);hist[2015]=np.ones(10)
        z2,r2,o2,n2=self.module.features(hist,2006)
        np.testing.assert_array_equal(z,z2);np.testing.assert_array_equal(r,r2)
        self.assertEqual(n,n2)

    def test_missing_exact_lag_rejected(self):
        if self.module is None:self.skipTest('red implementation gate')
        hist={y:np.zeros(10) for y in (2001,2002,2003,2004,2006)}
        with self.assertRaises(ValueError):self.module.features(hist,2006)

    def test_conditional_gradient_matches_finite_difference(self):
        if self.module is None:self.skipTest('red implementation gate')
        f={'z':np.linspace(-1,1,10),'recent':np.array([1,0]*5),
           'older':np.array([0,1]*5),'y':np.array([1,0,0,1,0,0,0,0,0,0])}
        d=self.module.design([f],'recent');b=np.array([.4,.7])
        loss,grad=self.module.objective(b,d)
        for j in range(2):
            delta=np.zeros(2);delta[j]=1e-5
            num=(self.module.objective(b+delta,d)[0]-self.module.objective(b-delta,d)[0])/2e-5
            self.assertAlmostEqual(num,grad[j],places=7)

    def test_recency_and_older_identical_information_gives_equal_score(self):
        if self.module is None:self.skipTest('red implementation gate')
        f={'z':np.linspace(-1,1,10),'recent':np.array([1,0]*5),
           'older':np.array([1,0]*5),'y':np.array([1,0,0,1,0,0,0,0,0,0])}
        b=np.array([.4,.7])
        np.testing.assert_allclose(self.module.scores(b,self.module.design([f],'recent')),
                                   self.module.scores(b,self.module.design([f],'older')))

    def test_site_permutation_preserves_score(self):
        if self.module is None:self.skipTest('red implementation gate')
        f={'z':np.linspace(-1,1,10),'recent':np.array([1,0]*5),
           'older':np.array([1,0]*5),'y':np.array([1,0,0,1,0,0,0,0,0,0])}
        perm=np.array([3,2,8,0,4,1,6,5,9,7]);g={k:v[perm] for k,v in f.items()}
        b=np.array([.4,.7])
        np.testing.assert_allclose(self.module.scores(b,self.module.design([f],'recent')),
                                   self.module.scores(b,self.module.design([g],'recent')),atol=1e-12)

if __name__=='__main__':unittest.main()
