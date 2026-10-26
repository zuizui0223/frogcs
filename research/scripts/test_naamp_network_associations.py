import unittest
import numpy as np
import pandas as pd
from naamp_odonata_caudata_associations import tertiles
from naamp_vegetation_network_associations import fit


class NetworkAssociationTests(unittest.TestCase):
    def test_tertiles_do_not_split_ties(self):
        v=np.repeat(np.arange(6),8)
        bins,cuts=tertiles(v)
        self.assertEqual(set(bins),{0,1,2})
        for value in set(v): self.assertEqual(len(set(bins[v==value])),1)

    def test_within_route_coefficients_match_explicit_fixed_effects(self):
        rng=np.random.default_rng(128)
        x=rng.normal(size=120);s=rng.normal(size=120)
        v=rng.integers(0,2,size=120);g=np.repeat(np.arange(6),20)
        y=.4*x-.3*s+.5*x*s*v+g+rng.normal(size=120)*.1
        def zrank(a):
            b=pd.Series(a).rank().to_numpy()
            return (b-b.mean())/b.std()
        xr,sr,yr=zrank(x),zrank(s),zrank(y)
        terms=np.column_stack([xr,sr,v,xr*sr,xr*v,sr*v,xr*sr*v])
        full=np.column_stack([pd.get_dummies(g).to_numpy(),terms])
        expected=np.linalg.lstsq(full,yr,rcond=None)[0][-7:]
        np.testing.assert_allclose(fit(x,s,v,y,g,True),expected,atol=1e-12)

    def test_missing_vegetation_contrast_is_not_zero_effect(self):
        rng=np.random.default_rng(129)
        x=rng.normal(size=120);s=rng.normal(size=120);y=x+s
        result=fit(x,s,np.zeros(120),y,np.repeat(np.arange(6),20),False)
        self.assertTrue(np.isnan(result).all())


if __name__=='__main__':unittest.main()
