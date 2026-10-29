import unittest
import numpy as np
from scipy.stats import rankdata
from common_scale_comparison import transform, weighted_core, effects


class CommonScaleTests(unittest.TestCase):
    def test_weighted_ties_equal_expanded_ranks(self):
        x=np.array([1.,1.,4.,9.]);w=np.array([3,2,1,4]);expanded=np.repeat(x,w)
        ranks=rankdata(expanded);ranks=(ranks-ranks.mean())/ranks.std()
        np.testing.assert_allclose(np.repeat(transform(x,w,'rank'),w),ranks,atol=1e-12)

    def test_weighted_estimator_equals_explicit_replication(self):
        import itertools
        a=np.array(list(itertools.product([0.,1.],[.25,1.,2.],[.25,1.,2.])))
        v,s,o=a.T;y=3-.1*o-.3*s+.4*v+.02*o*s-.03*v*s*o
        w=np.arange(len(v))%4+1
        for xt in ['raw','rank']:
            for yt in ['raw','rank']:
                b=weighted_core(o,s,v,y,w,xt,yt)
                c=weighted_core(*[np.repeat(z,w) for z in [o,s,v,y]],np.ones(w.sum()),xt,yt)
                for term in ['OS','OV','SV','OSV','OS_low','OS_high','OS_high_minus_low','R2']:
                    self.assertAlmostEqual(b[term],c[term],places=10)

    def test_conditional_contrast_uses_actual_standardized_V(self):
        b=np.array([.2,-.1,.3,-.4,.2,.1,.05])
        e=effects(b,-.3,3.)
        self.assertAlmostEqual(e['OS_low'],-.415)
        self.assertAlmostEqual(e['OS_high'],-.25)
        self.assertAlmostEqual(e['OS_high_minus_low'],.165)

    def test_strictly_increasing_response_conversion_keeps_ranks(self):
        x=np.array([.3,.7,.7,1.,2.,4.]);w=np.array([1,3,2,4,1,2])
        np.testing.assert_allclose(transform(x,w,'rank'),transform(np.log(x),w,'rank'),atol=1e-12)


if __name__=='__main__':unittest.main()
