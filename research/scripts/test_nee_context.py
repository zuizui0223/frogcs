import unittest
import numpy as np
from nee_context_robustness import prepare, block_fit, bootstrap_fit, bh

class ContextFitTests(unittest.TestCase):
    def setUp(self):
        self.rng=np.random.default_rng(29)
        self.g=np.repeat(np.arange(12),5)
        self.x=self.rng.normal(size=(60,7))
        self.c=self.rng.normal(size=(60,3))
        self.y=self.x@np.arange(1,8)+self.c@np.array([2.,-1.,.5])+self.rng.normal(size=60)

    def test_within_equals_explicit_route_fixed_effects(self):
        z,y,g,info=prepare(self.x,self.c,self.y,self.g,'within')
        got=block_fit(z,y,g)[0]
        full=np.column_stack([self.x,self.c,np.eye(12)[self.g]])
        expected=np.linalg.lstsq(full,self.y,rcond=None)[0][:7]
        np.testing.assert_allclose(got,expected,atol=1e-10)

    def test_weighted_blocks_equal_literal_resampled_routes(self):
        z,y,g,info=prepare(self.x,self.c,self.y,self.g,'pooled')
        chosen=np.array([0,0,2,3,3,4,5,7,8,9,10,11])
        weights=np.bincount(chosen,minlength=12)[None,:]
        got=bootstrap_fit(z,y,g,weights)[0]
        idx=np.concatenate([np.flatnonzero(g==k) for k in chosen])
        expected=np.linalg.lstsq(z[idx],y[idx],rcond=None)[0][:7]
        np.testing.assert_allclose(got,expected,atol=1e-10)

    def test_nonidentifiable_focal_is_rejected(self):
        with self.assertRaisesRegex(ValueError,'focal'):
            prepare(self.x,self.x[:,[0]],self.y,self.g,'pooled')

    def test_bh_excludes_unsupported_tests_and_retains_order(self):
        np.testing.assert_allclose(bh([.02,np.nan,.9,.01]),[.03,np.nan,.9,.03])

    def test_between_uses_mean_of_products_not_product_of_means(self):
        z,y,g,info=prepare(self.x,self.c,self.y,self.g,'between')
        np.testing.assert_allclose(z[:,:7],self.x.reshape(12,5,7).mean(axis=1))
        np.testing.assert_allclose(y,self.y.reshape(12,5).mean(axis=1))

if __name__=='__main__':unittest.main()
