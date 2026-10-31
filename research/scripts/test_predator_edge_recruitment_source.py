"""Directed edge-ablation source identity, active edge, and FE-null checks.

Original frog F arrives day 20 and has 45d aquatic duration: finishes at t=65.
D starts day 0 and its aquatic duration in the rate-factorial is 40/60d,
so emergence stage ends at 45/65. F has no completed cohort before D
emergence ends. Thus the original F→emerging-D edge (edge_FE) is zero
EXACTLY, including when reverse_on=1. This null is biological-source
timing, not support for an ecological absence of adult predation.
"""
import unittest

import numpy as np

from rate_axis_synthetic_growth_rescue_80y import (
    original_rate_factorial,swap_fixed_rate_axis
)
from finite_n_source_cohort_bridge import (
    make_source_group,simulate_finite_group,seasonal_kernel
)

ACTIVE_EDGES={
    "SF":"F_killed_by_S",
    "DF":"F_killed_by_D",
    "DS":"S_killed_by_D",
    "SD":"D_killed_by_S",
}
EDGE_FE="FE"


def exposed_source():
    full=original_rate_factorial(12)
    group=full[
        full.context.isin(("original","D_first_S_overtakes"))&
        full.plant_model.eq("SF0_DF0_DS1_L0")&
        full.reverse_on.eq(1)
    ].copy().reset_index(drop=True)
    if len(group)!=16:
        raise AssertionError("F/S/D source cohorts or reversal ON missing")
    return group


class OriginalTrophicEdgeSourceTests(unittest.TestCase):

    def test_true_original_F_and_D_stage_windows_never_overlap(self):
        g=exposed_source()
        params,season,*_=make_source_group(g)
        durations=season["stage_durations"]
        f_finish=np.asarray([p["f_arrival"] for p in params])+durations[:,0]
        d_emergence_finish=(np.asarray([p["d_arrival"] for p in params])
                            +durations[:,2]+5)
        self.assertTrue(np.all(f_finish>=d_emergence_finish))
        self.assertTrue(np.all(f_finish==65))
        self.assertEqual(set(d_emergence_finish),{45.,65.})

    def test_FE_edge_is_exactly_zero_in_main_rate_factorial(self):
        for rate in (original_rate_factorial(12),swap_fixed_rate_axis(12,"rho")):
            params,opts,*_=make_source_group(rate)
            outcomes=seasonal_kernel(
                params,initial_cohorts=np.ones((len(params),3)),
                dt=.25,diagnostics=True,**opts)
            self.assertEqual(float(outcomes["D_killed_by_F"].abs().max()),0.)
            self.assertEqual(float(outcomes["audit_H_FE"].abs().max()),0.)
            self.assertEqual(float(outcomes["D_dead"].isna().sum()),0.)

    def test_each_other_directed_edge_actually_works_and_ablation_zeroes_its_hazard(self):
        group=exposed_source()
        params,opts,*_=make_source_group(group)
        baseline=seasonal_kernel(
            params,initial_cohorts=np.ones((len(params),3)),
            dt=.25,**opts)
        for edge,death_key in ACTIVE_EDGES.items():
            self.assertGreater(float(baseline[death_key].sum()),0.,
                               "Source edge was never active: "+edge)
            selected=dict(opts)
            selected["pathway_controls"]={
                **opts["pathway_controls"],
                "edge_"+edge:np.zeros(len(params))
            }
            removed=seasonal_kernel(
                params,initial_cohorts=np.ones((len(params),3)),
                dt=.25,**selected)
            self.assertEqual(float(removed[death_key].abs().max()),0.,
                             "Ablation failed to eliminate only "+edge)

    def test_finite_source_default_and_structurally_null_FE_are_pathwise_identical(self):
        group=exposed_source()
        normal=simulate_finite_group(
            group,scale=3,seed=101,mode="both",immigration=False,
            years=4,dt=.25)
        null=simulate_finite_group(
            group,scale=3,seed=101,mode="both",immigration=False,
            years=4,dt=.25,edge_off=None)
        fe=simulate_finite_group(
            group,scale=3,seed=101,mode="both",immigration=False,
            years=4,dt=.25,edge_off="FE")
        for key in normal:
            np.testing.assert_array_equal(normal[key],null[key])
            np.testing.assert_array_equal(normal[key],fe[key],
                err_msg="FE source was claimed structurally null but changed "+key)

    def test_invalid_multi_edge_ablation_fails_closed(self):
        g=exposed_source()
        with self.assertRaises(ValueError):
            simulate_finite_group(
                g,scale=3,seed=101,mode="off",immigration=False,
                years=4,edge_off="SF,DF")


if __name__=="__main__":
    unittest.main()
