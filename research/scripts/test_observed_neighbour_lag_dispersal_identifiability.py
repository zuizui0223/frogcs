"""Non-field synthetic fixtures for NAAMP lagged-neighbour identifiability code."""
import unittest
import numpy as np
import pandas as pd
from observed_neighbour_lag_dispersal_identifiability import (
    neighbour_geometry, annual_panel, demean_matrix,
    fixed_effect_association,simulate_source_panel,auc_score,
)

def fixture():
    rng=np.random.default_rng(119)
    sites=[];visits=[]
    for route in range(30):
        for j in range(4):
            sid=f"r{route}_s{j}"
            sites.append(dict(site=sid,route=f"route{route}",
                lat=34.+route*.06+j*.001,
                lon=-90.+j*.008+route*.02))
            for year in range(2016,2021):
                for visit in range(2):
                    visits.append(dict(site=sid,year=year,
                        run=f"{route}_{j}_{year}_{visit}",
                        timeout=0,strong=int(rng.random()<.45),
                        air=float(rng.normal(19,3)),
                        noise=float(rng.normal(2,1)),
                        doy=float(rng.normal(150,22))))
    return pd.DataFrame(sites),pd.DataFrame(visits)


class NeighbourLagSourcePattern(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sites,cls.visits=fixture()
        cls.annual,cls.panel,cls.geom=annual_panel(
            cls.sites,cls.visits,
            expect_sites=120,expect_visits=1200)

    def test_observed_geometry_and_temporal_eligibility(self):
        self.assertEqual(len(self.geom),120)
        self.assertEqual(len(self.panel),120*4)
        self.assertEqual(self.panel.route.nunique(),30)
        self.assertFalse(self.geom.nearest_site.eq(self.geom.site).any())
        self.assertFalse(self.geom.farthest_site.eq(self.geom.site).any())
        self.assertTrue((self.geom.nearest_km<=self.geom.farthest_km).all())
        i=self.panel.set_index(["site","year"])
        for row in self.panel.itertuples(index=False):
            self.assertIn((row.site,row.year-1),self.annual.set_index(["site","year"]).index)
        self.assertTrue(set(self.panel.year).isdisjoint({2016}))

    def test_fixed_effect_decomposition_retains_near_lag_contrast(self):
        p=self.panel.copy()
        rng=np.random.default_rng(88)
        site_offset={s:float(rng.normal(0,1)) for s in p.site.unique()}
        routeyear_offset={s:float(rng.normal(0,1)) for s in p.route_year.unique()}
        p["rate"]=(.72*p.near_prev+.13*p.own_prev-.07*p.far_prev
           +.2*p.site.map(site_offset)+.1*p.route_year.map(routeyear_offset)
           +rng.normal(0,.025,size=len(p)))
        est=fixed_effect_association(p,n_boot=99)
        self.assertAlmostEqual(est["beta_nearest_prior"],.72,delta=.12)
        self.assertAlmostEqual(est["beta_farthest_prior"],-.07,delta=.12)
        self.assertEqual(est["n_conditional_route_bootstraps"],99)
        self.assertGreater(est["nearest_minus_farthest"],.5)

    def test_synthetic_null_and_neighbour_model_under_same_original_mask(self):
        z=simulate_source_panel(self.annual,self.geom,seed=20261031,
                                neighbour_coupling=0.)
        v=simulate_source_panel(self.annual,self.geom,seed=20261031,
                                neighbour_coupling=.65)
        self.assertEqual(len(z),len(self.annual))
        self.assertTrue(((z>=0)&(z<=1)).all())
        self.assertTrue(((v>=0)&(v<=1)).all())
        self.assertFalse(np.array_equal(z,v))
        a=fixed_effect_association(self.panel,values=z)
        b=fixed_effect_association(self.panel,values=v)
        self.assertTrue(np.isfinite([
            a["nearest_minus_farthest"],b["nearest_minus_farthest"]]).all())

    def test_weighted_two_way_projection_and_auc(self):
        rng=np.random.default_rng(10)
        n=180
        x=rng.normal(size=(n,3))
        w=rng.uniform(.2,2.,n)
        g1=np.repeat(np.arange(30),6)
        g2=np.tile(np.arange(6),30)
        z=demean_matrix(x,[g1,g2],w)
        for g in (g1,g2):
            for j in range(3):
                self.assertLess(np.abs(np.bincount(g,weights=z[:,j]*w)).max(),1e-6)
        self.assertAlmostEqual(auc_score([0.,0.],[1.,2.]),1.)
        self.assertAlmostEqual(auc_score([1.,1.],[1.,1.]),.5)

    def test_invalid_cohort_and_geometry_fail_closed(self):
        with self.assertRaises(AssertionError):
            annual_panel(self.sites,self.visits,
                         expect_sites=121,expect_visits=1200)
        with self.assertRaises(ValueError):
            neighbour_geometry(self.sites.iloc[[0,0]])
        with self.assertRaises(ValueError):
            simulate_source_panel(self.annual,self.geom,seed=1,
                                  neighbour_coupling=.9)


if __name__=="__main__":
    unittest.main()
