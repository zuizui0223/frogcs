"""Reproducible source and finite population accounting gates (no field inference)."""
import unittest
import numpy as np

from finite_n_source_cohort_bridge import (
    annual_conditional_means, finite_annual_update, sample_ring_transfer,
    simulate_finite_group, summarize_finite_group, source_cube, GUILDS
)
from spatial_cohort_80y_bridge import replay_gate


class FiniteNSourceBridgeTests(unittest.TestCase):

    def test_ring_flow_is_exact_integer_and_closed(self):
        rng=np.random.default_rng(20261031)
        x=rng.integers(0,12,size=(3,8,3))
        for p in (0, .15, .22, 1.):
            y,arr,dep=sample_ring_transfer(x,p,np.random.default_rng(13))
            np.testing.assert_array_equal(y, x+arr-dep)
            np.testing.assert_array_equal(arr.sum(axis=1),dep.sum(axis=1))
            np.testing.assert_array_equal(y.sum(axis=1),x.sum(axis=1))
            self.assertTrue((y>=0).all())
            if p==0:
                np.testing.assert_array_equal(y,x)
        with self.assertRaises(ValueError):
            sample_ring_transfer(x,-.2,rng)

    def test_conditional_source_annual_equation(self):
        B=np.array([[[.2,1.0,.3],[0.,.4,1.2]]],float)
        due=np.array([[[.0,.5,.8],[.4,.0,.0]]],float)
        survive=np.array([[[.4,.5,0.],[.4,.5,0.]]])
        rho=np.full((1,2,1),.75)
        conv=np.full((1,2,3),4.)
        juvenile=np.full((1,2,3),.8)
        delays=np.array([[[3,2,1],[3,2,1]]])
        source=np.array([[[1.,2.,.25],[1.,2.,.25]]])
        carry,loc,external=annual_conditional_means(
            B,due,survive,rho,conv,juvenile,delays,source
        )
        manual_loc = rho*conv*juvenile**(delays-1)*due/(1+due/1.)
        np.testing.assert_allclose(loc,manual_loc,rtol=0,atol=1e-12)
        np.testing.assert_allclose(carry,survive*B,rtol=0,atol=1e-12)
        np.testing.assert_allclose(external,(1-rho)*(1-survive)*source,atol=1e-12)
        _,_,zero=annual_conditional_means(
            B,due,survive,rho,conv,juvenile,delays,source,immigrants=False
        )
        self.assertFalse(zero.any())

    def test_one_year_finite_mass_conservation(self):
        rng=np.random.default_rng(12)
        N=np.arange(1,1+2*8*3).reshape(2,8,3).astype(int)
        due=np.ones_like(N)*2
        survival=np.broadcast_to(np.array([.4,.5,0.]),N.shape)
        rho=np.ones((2,8,1))*.75
        conv=np.ones(N.shape)*4
        juvenile=np.ones(N.shape)*.8
        delays=np.broadcast_to(np.array([2,2,1]),N.shape)
        source=np.ones(N.shape)
        for mode in ("off","recruits","carryover","both"):
            y,l=finite_annual_update(
                N,due,survival,rho,conv,juvenile,delays,source,
                rng,scale=6,movement=mode,immigration=False)
            np.testing.assert_array_equal(
                y,l["survivors"]+l["local_recruits"]+l["external"]+
                  l["arrivals"]-l["departures"])
            np.testing.assert_array_equal(
                l["arrivals"].sum(axis=1),l["departures"].sum(axis=1))
            self.assertFalse(l["external"].any())
            if mode=="off":
                self.assertFalse(l["arrivals"].any())

    def test_source_annual_replay_against_pr146(self):
        errors=replay_gate(source_cube(1),years=4,window=2,dt=.25)
        for value in errors.values():
            self.assertLessEqual(value,1e-8)

    def test_real_season_source_stochastic_seed_and_zero(self):
        cube=source_cube(1)
        g=cube[cube.plant_model.eq("SF0_DF0_DS1_L0") &
               cube.context.eq("original") &
               cube.reverse_on.eq(0)].reset_index(drop=True)
        a=simulate_finite_group(g,scale=3,seed=101,mode="off",
                                immigration=False,years=4,dt=.25)
        b=simulate_finite_group(g,scale=3,seed=101,mode="off",
                                immigration=False,years=4,dt=.25)
        for k in a:
            np.testing.assert_array_equal(a[k],b[k])
        summary,events=summarize_finite_group(
            g,a,scale=3,seed=101,mode="off",immigration=False,years=4
        )
        self.assertEqual(len(summary),8*len(GUILDS))
        self.assertFalse(a["external"].any())
        self.assertFalse(a["arrivals"].any())
        self.assertEqual(summary.n_local_returns.sum(),len(events))
        self.assertTrue(np.issubdtype(a["hist"].dtype,np.integer))

    def test_exact_event_censor_and_delayed_source_not_migrant(self):
        cube=source_cube(1)
        g=cube.iloc[:1].copy()
        years=4
        H=np.zeros((years+1,1,8,3),dtype=np.int32)
        # Two zero->positive returns, at year1 and last census year4.
        H[1,0,0,0]=2
        H[2,0,0,0]=1
        H[3,0,0,0]=1
        H[4,0,0,0]=1
        H[4,0,1,0]=1
        loc=np.zeros((years,1,8,3),dtype=np.int32)
        loc[0,0,0,0]=2
        loc[1,0,0,0]=1
        loc[3,0,1,0]=1
        zeros=np.zeros_like(loc)
        deaths=np.zeros_like(loc)
        deaths[1,0,0,0]=2
        # No model execution in this bookkeeping-only fixture.
        states=dict(hist=H,local_recruits=loc,
                    external=zeros,arrivals=zeros,departures=zeros,
                    deaths=deaths)
        summary,events=summarize_finite_group(
            g,states,scale=3,seed=101,mode="off",
            immigration=False,years=years)
        f=summary[summary.guild=="F"].iloc[0]
        self.assertEqual(int(f.n_local_returns),2)
        self.assertEqual(int(f.n_2y_observable_returns),1)
        self.assertEqual(int(f.n_2y_persistent_returns),1)
        self.assertEqual(int(f.n_2y_persistent_with_recruitment),1)
        self.assertEqual(int(f.n_3y_observable_returns),1)
        self.assertEqual(int(f.n_3y_persistent_returns),1)
        self.assertEqual(int(f.n_3y_persistent_with_recruitment),1)
        f_events=events[events.guild=="F"]
        self.assertEqual(set(f_events.cause_label),{"delayed_local_recruitment"})
        self.assertEqual(int(f_events.followup_2y_observable.sum()),1)


if __name__=="__main__":
    unittest.main()
