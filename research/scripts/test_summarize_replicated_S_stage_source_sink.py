"""Synthetic inference checks for 12 new/reused matched real-ABM seed groups."""
import unittest

import numpy as np
import pandas as pd

from summarize_replicated_S_stage_source_sink import (
    ALL_SEEDS,METRICS,matched_stage_rate_trophic_pom
)
from run_equal_rate_S_stage_dispersal import NEW_MODES,DIFFUSION_VALUES


def synthetic_full_seed_source():
    data=[]
    for mode in NEW_MODES:
        stage,code=mode.rsplit("_",1)
        diffusion=DIFFUSION_VALUES[code]
        for reverse in (False,True):
            for seed in ALL_SEEDS:
                for guild in ("F","S","D"):
                    # S adult-high movement loses occupancy under reversal OFF,
                    # and can regain occupancy under reversal ON.
                    base=4.
                    if guild=="S":
                        base=2.
                        if stage=="S_adult":base+=1.
                        if code=="022" and stage=="S_larva":base+=2.
                        if code=="022" and stage=="S_adult":
                            base+=(-1. if not reverse else 3.)
                    data.append(dict(
                        mobility=mode,reverse=reverse,seed=seed,guild=guild,
                        stage_mobility=stage,per_capita_diffusion=diffusion,
                        occupied_year20=base,
                        alive_year20=base+10,
                        total_births=100+base*2,
                        total_deaths=90,
                        cumulative_net_recruitment=10+base*2,
                        n_surviving_moves=30 if code=="022" else 6,
                        n_local_extinctions=9-base,
                        n_recolonizations=4 if stage=="S_adult" else 1,
                        n_return_followups_eligible=2,
                        n_return_persistent_two_censuses=1,
                        n_return_persistent_and_born_locally=1,
                        n_return_censored=2,
                        max_abs_local_source_sink_residual=0))
    return pd.DataFrame(data)


class TwelveSeedStochasticReplicateTests(unittest.TestCase):
    def test_all_96_complete_simulation_paths_and_guilds(self):
        a=synthetic_full_seed_source()
        self.assertEqual(len(a),96*3)
        full,paired,summary,conditions=matched_stage_rate_trophic_pom(a,n_boot=199)
        self.assertEqual(len(full),96)
        self.assertEqual(len(paired),12*2*len(METRICS))
        self.assertEqual(len(summary),2*len(METRICS)*5)
        self.assertEqual(len(conditions),8)
        self.assertTrue(conditions.n_seeds.eq(12).all())

    def test_matched_stage_rate_and_trophic_interactions_are_not_conflated(self):
        _,paired,summary,_=matched_stage_rate_trophic_pom(
            synthetic_full_seed_source(),n_boot=199)
        occ=summary[(summary.metric=="occupied_year20") &
                    (summary.comparison=="adult_minus_larva_022")]
        self.assertEqual(len(occ),2)
        self.assertLess(float(occ[occ.reverse.eq(False)].mean_difference.iloc[0]),0)
        self.assertGreater(float(occ[occ.reverse.eq(True)].mean_difference.iloc[0]),0)
        self.assertEqual(
            int(occ[occ.reverse.eq(False)].n_negative.iloc[0]),12)
        self.assertEqual(
            int(occ[occ.reverse.eq(True)].n_positive.iloc[0]),12)
        self.assertEqual(set(paired.seed),set(ALL_SEEDS))
        self.assertTrue(summary.n_seed_replicates.eq(12).all())

    def test_missing_seed_or_source_sink_failure_rejected(self):
        a=synthetic_full_seed_source()
        b=a[~((a.seed==112)&(a.mobility=="S_adult_022")&
              (a.reverse==True)&(a.guild=="S"))].copy()
        with self.assertRaises(ValueError):
            matched_stage_rate_trophic_pom(b,n_boot=99)
        b=a.copy()
        b.loc[0,"max_abs_local_source_sink_residual"]=1
        with self.assertRaises(ValueError):
            matched_stage_rate_trophic_pom(b,n_boot=99)
        b=a.copy()
        b.loc[0,"seed"]=999
        with self.assertRaises(ValueError):
            matched_stage_rate_trophic_pom(b,n_boot=99)


if __name__=="__main__":
    unittest.main()
