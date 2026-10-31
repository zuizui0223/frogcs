"""Synthetic unit tests: invariants and explicit contrasts, not field validation."""
import unittest
from dataclasses import replace
import numpy as np
import pandas as pd

from multigeneration_reversal import (
    FT, FA, SL, SA, DN, DE, DA, Agents, Rates, PREDATION,
    abm_step, initial_agents, initial_grid, pde_step,
    simulate_abm, simulate_pde, _schedule,
)


def inert():
    return Rates(natural=(0.,)*7, maturation=(0.,)*7,
                 fecundity=(0.,)*7, diffusion=(0.,)*7,
                 a_sf=0., a_df=0., a_ds=0., a_sd=0., a_fe=0.,
                 density_response=False, seasonal_births=False)


class SpatialReversalTests(unittest.TestCase):
    def test_zero_process_conserves_all_individuals_and_density(self):
        x=np.zeros((7,3),int); x[FA]=[4,2,6];x[DN]=[2,1,0]
        v=np.array([0.,.8,.5]);p=inert()
        new,dead=pde_step(x,v,p,.05,.2)
        np.testing.assert_allclose(new,x,rtol=0,atol=1e-12)
        np.testing.assert_array_equal(dead,np.zeros((5,3)))
        agents=initial_agents(x)
        old_uid=agents.uid.copy()
        loss=abm_step(agents,v,p,.05,.2,np.random.default_rng(10))
        np.testing.assert_array_equal(agents.counts(3),x)
        np.testing.assert_array_equal(agents.uid,old_uid)
        self.assertEqual(loss.sum(),0)

    def test_reverse_is_only_adult_frog_to_emerging_dragonfly(self):
        x=np.zeros((7,2),int);x[FT]=20;x[FA]=100;x[DN]=40;x[DE]=200
        v=np.zeros(2)
        p=replace(inert(),a_df=.004,a_fe=.025)
        on,h_on=pde_step(x,v,p,.1,.1,reverse=True)
        off,h_off=pde_step(x,v,p,.1,.1,reverse=False)
        self.assertLess(on[DE].sum(),off[DE].sum())
        self.assertAlmostEqual(on[FT].sum(),off[FT].sum(),places=10)
        self.assertGreater(h_on[4].sum(),0)
        self.assertEqual(h_off[4].sum(),0)
        aa=initial_agents(x);bb=initial_agents(x)
        ra=np.random.default_rng(22);rb=np.random.default_rng(22)
        dead_on=abm_step(aa,v,p,.1,.1,ra,reverse=True)
        dead_off=abm_step(bb,v,p,.1,.1,rb,reverse=False)
        self.assertGreater(dead_on[4].sum(),0)
        self.assertEqual(dead_off[4].sum(),0)
        self.assertLess(aa.counts(2)[DE].sum(),bb.counts(2)[DE].sum())

    def test_overlap_absence_has_no_fake_reversal(self):
        x=np.zeros((7,3));x[FT]=4;x[DE]=10
        v=np.array([0.,.5,1.])
        p=replace(inert(),a_fe=.5)
        a,h=pde_step(x,v,p,.025,.3,reverse=True)
        b,_=pde_step(x,v,p,.025,.3,reverse=False)
        np.testing.assert_allclose(a,b,rtol=0,atol=0)
        self.assertEqual(h[4].sum(),0)

    def test_second_generation_is_real_individual_ancestry(self):
        x=np.zeros((7,2),int);x[FA]=4
        p=replace(inert(),maturation=(20.,0.,0.,0.,0.,0.,0.),
                  fecundity=(0.,20.,0.,0.,0.,0.,0.),capacity=1e6)
        traj,agents=simulate_abm(x,[0.,0.],p,years=2,dt=.05,seed=7)
        self.assertGreater(agents.generation.max(),1)
        self.assertTrue((agents.parent[agents.generation>0] >= 0).all())
        self.assertTrue((agents.parent[agents.generation>0] < agents.next_uid).all())
        self.assertEqual(len(agents.uid),len(np.unique(agents.uid)))
        self.assertTrue((agents.age >= 0).all())
        self.assertGreater(traj.iloc[-1].F_adult,traj.iloc[0].F_adult)
        pde,_=simulate_pde(x,[0.,0.],p,years=2,dt=.05)
        self.assertGreater(pde.iloc[-1].F_adult,pde.iloc[0].F_adult)

    def test_diffusion_mass_conservation_and_neighbour_moves(self):
        x=np.zeros((7,5),int);x[DA,2]=4000
        p=replace(inert(),diffusion=(0.,0.,0.,0.,0.,0.,.6))
        v=np.zeros(5)
        new,_=pde_step(x,v,p,.1,.2)
        self.assertAlmostEqual(new.sum(),x.sum(),places=10)
        self.assertGreater(new[DA,1],0)
        self.assertGreater(new[DA,3],0)
        pop=initial_agents(x)
        abm_step(pop,v,p,.1,.2,np.random.default_rng(4))
        self.assertEqual(len(pop.stage),4000)
        self.assertGreater(pop.counts(5)[DA,1],0)
        self.assertGreater(pop.counts(5)[DA,3],0)
        self.assertAlmostEqual(pop.counts(5)[DA,1],new[DA,1],delta=50)

    def test_reversal_changes_later_dragonfly_recruitment(self):
        x=np.zeros((7,3));x[FA]=50;x[DE]=20
        p=replace(inert(),maturation=(0.,0.,0.,0.,0.,16.,0.),
                  fecundity=(0.,0.,0.,0.,0.,0.,3.),capacity=1e6,a_fe=.12)
        on,_=simulate_pde(x,np.zeros(3),p,years=3,dt=.025,reverse=True)
        off,_=simulate_pde(x,np.zeros(3),p,years=3,dt=.025,reverse=False)
        self.assertLess(on.iloc[1].D_adult,off.iloc[1].D_adult)
        self.assertLess(on.iloc[2].D_nymph,off.iloc[2].D_nymph)
        self.assertGreater(on.iloc[1].deaths_F_adult_to_D_emerging,0)
        self.assertEqual(off.iloc[1].deaths_F_adult_to_D_emerging,0)

    def test_numerical_refinement_and_reproducibility(self):
        init,v=initial_grid(4)
        p=Rates()
        coarse,_=pde_step(init,v,p,.05,.20,reverse=True)
        fine,_=pde_step(init,v,p,.025,.20,reverse=True)
        fine,_=pde_step(fine,v,p,.025,.225,reverse=True)
        self.assertLess(float(abs(coarse-fine).max()),1.0)
        a,agents=simulate_abm(init,v,p,years=2,dt=.05,seed=222)
        b,agents2=simulate_abm(init,v,p,years=2,dt=.05,seed=222)
        pd.testing.assert_frame_equal(a,b)
        np.testing.assert_array_equal(agents.uid,agents2.uid)
        self.assertEqual(_schedule(20,.025),40)
        self.assertTrue((a[['n_total','D_adult','F_adult']].to_numpy()>=0).all())

    def test_fail_closed_on_invalid_rates_and_grids(self):
        init,v=initial_grid(3)
        with self.assertRaises(ValueError):
            pde_step(init,v,Rates(),dt=1.,time=0)
        with self.assertRaises(ValueError):
            initial_agents(np.ones((7,3))*.4)
        with self.assertRaises(ValueError):
            pde_step(init,v[:1],Rates(),.025,.0)
        with self.assertRaises(ValueError):
            _schedule(2,.03)


if __name__=="__main__":
    unittest.main()
