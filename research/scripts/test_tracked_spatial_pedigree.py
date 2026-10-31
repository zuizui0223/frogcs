"""Actual original-ABM pathwise equivalence and durable genealogy invariants."""
import unittest
from dataclasses import replace
import numpy as np
import pandas as pd

from multigeneration_reversal import (
    Rates,FT,FA,SL,DN,DE,DA,PREDATION,
    initial_grid,simulate_abm,initial_agents
)
from tracked_spatial_pedigree import (
    PedigreeAudit,GUILDS,patch_occupancy_transitions,simulate_traced_abm,
    per_guild_patch_counts
)


def inert():
    return Rates(natural=(0.,)*7,maturation=(0.,)*7,
                 fecundity=(0.,)*7,diffusion=(0.,)*7,
                 a_sf=0.,a_df=0.,a_ds=0.,a_sd=0.,a_fe=0.,
                 density_response=False,seasonal_births=False)


class TrueSpatiotemporalPedigreeTests(unittest.TestCase):
    def test_exact_same_original_abm_kernel_year_stage_and_predation_ledger(self):
        x,v=initial_grid(4)
        p=Rates()
        traced=simulate_traced_abm(x,v,p,years=3,dt=.05,reverse=True,seed=77)
        reference,final=simulate_abm(x,v,p,years=3,dt=.05,reverse=True,seed=77)
        a=traced["annual"].sort_values("year")
        b=reference[reference.year>0].sort_values("year")
        for term in ("F_tadpole","F_adult","S_larva","D_nymph","D_emerging","D_adult"):
            if term in a.columns:
                np.testing.assert_array_equal(a[term].to_numpy(float),b[term].to_numpy(float))
        np.testing.assert_array_equal(a.n_alive.to_numpy(float),b.n_total.to_numpy(float))
        for name in PREDATION:
            col="deaths_"+name
            np.testing.assert_array_equal(a[col].to_numpy(float),b[col].to_numpy(float))
        one=traced["final_agents"]
        for key in ("uid","parent","generation","cell","stage","age"):
            np.testing.assert_array_equal(getattr(one,key),getattr(final,key))
        self.assertEqual(len(traced["registry"]),one.next_uid)

    def test_periodic_neighbor_moves_and_disabled_dispersal_are_exact(self):
        x,v=initial_grid(5)
        no=replace(Rates(),diffusion=(0.,)*7)
        z=simulate_traced_abm(x,v,no,years=2,dt=.05,seed=22)
        self.assertTrue(z["movements"].empty)
        self.assertFalse(z["patch"].known_surviving_immigrant_arrivals.any())
        self.assertFalse(z["registry"].lifetime_surviving_moves.any())
        self.assertEqual(int(z["annual"].n_observed_survivor_movements.sum()),0)
        moved=simulate_traced_abm(x,v,Rates(),years=2,dt=.05,seed=22)
        self.assertGreater(len(moved["movements"]),0)
        for row in moved["movements"].itertuples(index=False):
            self.assertIn(row.destination_patch,
                          ((row.source_patch-1)%5,(row.source_patch+1)%5))
        self.assertEqual(int(moved["annual"].n_observed_survivor_movements.sum()),
                         len(moved["movements"]))

    def test_true_ancestral_chain_survives_parent_death_and_reaches_grandchildren(self):
        x=np.zeros((7,3),int);x[FA]=[7,5,8]
        p=replace(inert(),maturation=(20.,0.,0.,0.,0.,0.,0.),
                  fecundity=(0.,7.,0.,0.,0.,0.,0.),
                  natural=(.25,.60,0.,0.,0.,0.,0.),
                  capacity=80.)
        z=simulate_traced_abm(x,np.zeros(3),p,years=3,dt=.05,seed=19)
        a=z["registry"].set_index("uid")
        self.assertGreater(int((a.generation>=2).sum()),0)
        all_children=a[a.generation>0]
        self.assertTrue((all_children.parent_uid>=0).all())
        for uid,row in all_children.iterrows():
            parent=a.loc[int(row.parent_uid)]
            self.assertEqual(int(parent.generation)+1,int(row.generation))
            self.assertEqual(int(parent.founder_uid),int(row.founder_uid))
            self.assertEqual(str(parent.guild),str(row.guild))
            self.assertLess(int(row.parent_uid),int(uid))
        self.assertTrue(a.uid.is_unique if "uid" in a else a.index.is_unique)
        self.assertGreaterEqual(int(a.loc[~a.alive,"generation"].max()),0)
        self.assertEqual(int(z["lineages"].loc[z["lineages"].guild=="F",
                          "max_generation_ever"].iloc[0]),int(a.generation.max()))

    def test_annual_extinction_and_recolonization_are_true_transitions(self):
        before=np.asarray([[1,0,0,2],[0,5,1,0],[0,0,0,0]])
        after=np.asarray([[0,2,0,1],[3,0,1,0],[0,0,4,0]])
        lost,colonized=patch_occupancy_transitions(before,after)
        self.assertEqual(np.flatnonzero(lost[0]).tolist(),[0])
        self.assertEqual(np.flatnonzero(colonized[0]).tolist(),[1])
        self.assertEqual(np.flatnonzero(lost[1]).tolist(),[1])
        self.assertEqual(np.flatnonzero(colonized[1]).tolist(),[0])
        self.assertEqual(np.flatnonzero(colonized[2]).tolist(),[2])
        self.assertFalse(np.any(lost&colonized))
        with self.assertRaises(ValueError):
            patch_occupancy_transitions(before,after[:,1:])

    def test_no_process_conserves_all_uids_and_never_generates_phantom_births(self):
        x=np.zeros((7,4),int);x[FA]=[3,0,4,0];x[DN]=[1,2,0,0]
        z=simulate_traced_abm(x,[0.,.8,0.,.9],inert(),years=3,
                              dt=.05,seed=43)
        self.assertTrue(z["annual"].n_births.eq(0).all())
        self.assertTrue(z["annual"].n_deaths.eq(0).all())
        self.assertTrue(z["annual"].n_alive.eq(x.sum()).all())
        self.assertFalse(z["patch"].locally_extinct.any())
        self.assertFalse(z["patch"].recolonized.any())
        self.assertTrue(z["registry"].parent_uid.eq(-1).all())
        self.assertTrue(z["registry"].alive.all())

    def test_fixed_seed_replays_all_offspring_and_immigrant_events(self):
        x,v=initial_grid(4)
        a=simulate_traced_abm(x,v,Rates(),years=2,dt=.05,seed=41)
        b=simulate_traced_abm(x,v,Rates(),years=2,dt=.05,seed=41)
        for key in ("annual","patch","registry","movements","lineages"):
            pd.testing.assert_frame_equal(a[key],b[key])
        for year,g in a["patch"].groupby("year"):
            self.assertEqual(len(g),4*3)
        self.assertEqual(int(a["annual"].n_births.sum()),
                         int((a["registry"].generation>0).sum()))
        self.assertEqual(len(a["registry"]),
                         x.sum()+int(a["annual"].n_births.sum()))


if __name__=="__main__":
    unittest.main()
