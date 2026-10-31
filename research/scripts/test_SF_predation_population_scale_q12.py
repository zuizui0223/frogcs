"""q12 source identity, finite-N conservation and true inactive FE timing tests."""
import unittest
import numpy as np
from run_predator_edge_recruitment_80y import source_by_recruitment_regime
from finite_n_source_cohort_bridge import (
    simulate_finite_group,summarize_finite_group,make_source_group,seasonal_kernel
)
from run_SF_predation_population_scale_q12_80y import NETWORKS,NETWORK_ACTIVE

def group():
    src=source_by_recruitment_regime("rate12_rho0")
    s=src[(src.context=="original")&
          src.plant_model.eq("SF0_DF0_DS1_L0")&
          src.reverse_on.eq(1)].reset_index(drop=True)
    assert len(s)==8
    return s

class LargerPopulationSourceTests(unittest.TestCase):

    def test_explicit_all_four_is_pathwise_same_as_default_q12(self):
        g=group()
        for mode in ("off","both"):
            kwargs=dict(scale=12,seed=101,mode=mode,
                        immigration=False,years=4,dt=.25,transfer=.15)
            original=simulate_finite_group(g,**kwargs)
            explicit=simulate_finite_group(g,active_edges=("SF","DF","DS","SD"),**kwargs)
            for key in original:
                np.testing.assert_array_equal(original[key],explicit[key],
                     err_msg="Original biological source q12 default mismatch: "+key)

    def test_explicit_no_SF_is_pathwise_same_as_previous_single_edge(self):
        g=group()
        for mode in ("off","both"):
            kw=dict(scale=12,seed=101,mode=mode,
                    immigration=False,years=4,dt=.25,transfer=.15)
            old=simulate_finite_group(g,edge_off="SF",**kw)
            new=simulate_finite_group(g,active_edges=("DF","DS","SD"),**kw)
            for name in old:
                np.testing.assert_array_equal(old[name],new[name])

    def test_no_trophic_predation_has_exact_zero_direct_mortality(self):
        g=group();p,opts,*_=make_source_group(g)
        opts["pathway_controls"]={
            **opts["pathway_controls"],
            **{"edge_"+e:np.zeros(len(p)) for e in ("SF","DF","DS","SD","FE")}
        }
        out=seasonal_kernel(
            p,initial_cohorts=np.ones((len(p),3)),
            dt=.25,**opts)
        for field in ("F_killed_by_S","F_killed_by_D","S_killed_by_D",
                      "D_killed_by_S","D_killed_by_F"):
            self.assertEqual(float(out[field].abs().max()),0.)

    def test_q12_all_networks_source_events_and_mass_accounted(self):
        g=group()
        for arm in NETWORKS:
            for mode in ("off","both"):
                r=simulate_finite_group(
                    g,scale=12,seed=101,mode=mode,
                    immigration=False,years=4,dt=.25,transfer=.15,
                    active_edges=NETWORK_ACTIVE[arm])
                f,e=summarize_finite_group(
                    g,r,scale=12,seed=101,mode=mode,
                    immigration=False,years=4)
                self.assertEqual(len(f),8*3)
                self.assertEqual(int(f.n_local_returns.sum()),len(e))
                self.assertFalse(r["external"].any())
                self.assertTrue(np.issubdtype(r["hist"].dtype,np.integer))
                np.testing.assert_array_equal(
                    r["arrivals"].sum(axis=2),r["departures"].sum(axis=2))
                self.assertTrue((r["hist"]>=0).all())
                if mode=="off":
                    self.assertFalse(r["arrivals"].any())

    def test_switching_q3_to_q12_is_true_count_scale_change(self):
        g=group()
        k=dict(seed=101,mode="both",immigration=False,
               years=4,dt=.25,transfer=.15,active_edges=("SF",))
        old=simulate_finite_group(g,scale=3,**k)
        high=simulate_finite_group(g,scale=12,**k)
        self.assertFalse(np.array_equal(old["hist"][0],high["hist"][0]))
        self.assertEqual(int(high["hist"][0,0,0,0]),4*int(old["hist"][0,0,0,0]))

if __name__=="__main__":
    unittest.main()
