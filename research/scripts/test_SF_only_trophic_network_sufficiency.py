"""Two-way predator-pathway source necessity / sufficiency execution tests."""
import unittest

import numpy as np

from rate_axis_synthetic_growth_rescue_80y import original_rate_factorial
from finite_n_source_cohort_bridge import (
    make_source_group,simulate_finite_group,seasonal_kernel
)

KILL={
    "SF":"F_killed_by_S",
    "DF":"F_killed_by_D",
    "DS":"S_killed_by_D",
    "SD":"D_killed_by_S",
    "FE":"D_killed_by_F",
}

def case():
    s=original_rate_factorial(12)
    a=s[(s.context=="original")&
        (s.plant_model=="SF0_DF0_DS1_L0")&
        (s.reverse_on==1)].reset_index(drop=True)
    if len(a)!=8:raise AssertionError("Source eight cells missing")
    return a

class SoleActivePredatorSourceTests(unittest.TestCase):

    def test_SF_only_seasonal_hazards_are_the_only_live_direct_predation(self):
        g=case();p,opts,*_=make_source_group(g)
        opts["pathway_controls"]={
            **opts["pathway_controls"],
            **{"edge_"+name:np.ones(len(p)) if name=="SF" else np.zeros(len(p))
               for name in ("SF","DF","DS","SD","FE")}
        }
        o=seasonal_kernel(
            p,initial_cohorts=np.ones((len(p),3)),
            dt=.25,**opts)
        self.assertGreater(float(o[KILL["SF"]].sum()),0)
        for edge in ("DF","DS","SD","FE"):
            self.assertEqual(float(o[KILL[edge]].abs().max()),0.)

    def test_no_direct_edges_mean_no_direct_trophic_death(self):
        g=case();p,opts,*_=make_source_group(g)
        opts["pathway_controls"]={
            **opts["pathway_controls"],
            **{"edge_"+name:np.zeros(len(p))
               for name in ("SF","DF","DS","SD","FE")}
        }
        o=seasonal_kernel(
            p,initial_cohorts=np.ones((len(p),3)),
            dt=.25,**opts)
        for edge in KILL:
            self.assertEqual(float(o[KILL[edge]].abs().max()),0.)

    def test_original_default_mode_pathwise_replays_sole_active_all_case(self):
        g=case()
        x=simulate_finite_group(
            g,scale=3,seed=101,mode="both",
            immigration=False,years=4)
        y=simulate_finite_group(
            g,scale=3,seed=101,mode="both",
            immigration=False,years=4,active_edges=("SF","DF","DS","SD"))
        for key in x:
            np.testing.assert_array_equal(
                x[key],y[key],
                err_msg="Retaining all four active source edges must preserve original "+key)

    def test_sole_SF_and_no_direct_predation_differ_but_keep_integer_mass(self):
        g=case()
        for active in (("SF",),()):
            a=simulate_finite_group(
                g,scale=3,seed=101,mode="both",
                immigration=False,years=4,
                active_edges=active)
            self.assertEqual(a["hist"].dtype,np.int32)
            self.assertFalse(a["external"].any())
            np.testing.assert_array_equal(
                a["arrivals"].sum(axis=2),a["departures"].sum(axis=2))
        with self.assertRaises(ValueError):
            simulate_finite_group(g,scale=3,seed=101,mode="both",
                 immigration=False,years=4,active_edges=("SF",),edge_off="DS")
        with self.assertRaises(ValueError):
            simulate_finite_group(g,scale=3,seed=101,mode="both",
                 immigration=False,years=4,active_edges=("SF","SF"))

if __name__=="__main__":
    unittest.main()
