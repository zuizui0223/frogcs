"""Synthetic algebra tests for fixed-rate adult/larval S dispersal comparison."""
import unittest
import numpy as np
import pandas as pd

from tracked_spatial_pedigree import SEEDS,GUILDS
from run_equal_rate_S_stage_dispersal import NEW_MODES
from summarize_equal_rate_S_stage_dispersal import (
    ENDPOINTS,paired_effects,summarize_four_seed
)


def source_fixture():
    rows=[]
    for mode in NEW_MODES:
        stage,rate=mode.rsplit("_",1)
        adult=stage=="S_adult"
        high=rate=="022"
        for reverse in (False,True):
            for seed in SEEDS:
                for guild in GUILDS:
                    # Exact known stage×rate 2×2 contrast among S:
                    # larva low=2, adult low=3, larva high=4, adult high=6.
                    occupied=((2+int(adult)) if not high else
                              (6 if adult else 4))
                    if guild!="S":occupied=8
                    rec=dict(mobility=mode,S_move_stage=stage,rate_code=rate,
                             reverse=reverse,seed=seed,guild=guild,
                             n_occupied_year_end=occupied,
                             n_local_extinction_events=2,
                             n_recolonizations=2,
                             n_two_year_followup_eligible=1,
                             n_two_year_retained=1,
                             n_two_census_persistence_plus_local_births=1,
                             n_seen_survivor_movements=3,
                             n_with_external_natal_parent_births=1,
                             n_multisite_founder_lineages=2,
                             n_living_elsewhere_than_founder_patch=3)
                    rows.append(rec)
    return pd.DataFrame(rows)


class EqualDiffusionRateABCOutputTests(unittest.TestCase):
    def test_exact_stage_difference_at_fixed_rate(self):
        q=source_fixture()
        stage,rate,interaction=paired_effects(q)
        self.assertEqual(len(stage),16)
        self.assertEqual(len(rate),16)
        self.assertEqual(len(interaction),8)
        self.assertTrue(stage[stage.rate_code=="005"].delta_n_occupied_year_end.eq(1).all())
        self.assertTrue(stage[stage.rate_code=="022"].delta_n_occupied_year_end.eq(2).all())
        self.assertTrue(interaction.interaction_n_occupied_year_end.eq(1).all())
        self.assertTrue(rate[rate.S_move_stage=="S_larva"].delta_n_occupied_year_end.eq(2).all())
        self.assertTrue(rate[rate.S_move_stage=="S_adult"].delta_n_occupied_year_end.eq(3).all())

    def test_four_stochastic_seeds_are_grouped_not_patch_replications(self):
        s,r,i=paired_effects(source_fixture())
        out=summarize_four_seed(s,r,i)
        self.assertEqual(len(out),10)
        self.assertTrue(out.n_stochastic_seed_pairs.eq(4).all())
        for key in ENDPOINTS:
            self.assertTrue(np.isfinite(out["mean_"+key]).all())
        low=out[(out.comparison=="stage")&(out.rate_code=="005")]
        self.assertTrue(low.mean_n_occupied_year_end.eq(1).all())
        high=out[(out.comparison=="stage")&(out.rate_code=="022")]
        self.assertTrue(high.mean_n_occupied_year_end.eq(2).all())

    def test_missing_one_prior_seed_or_stochastic_arm_fails_closed(self):
        x=source_fixture()
        incomplete=x[~((x.mobility=="S_adult_022")&
                       (x.guild=="S")&(x.seed==SEEDS[-1])&(x.reverse==True))]
        with self.assertRaises(AssertionError):
            paired_effects(incomplete)
        s,r,i=paired_effects(x)
        with self.assertRaises(AssertionError):
            summarize_four_seed(s.iloc[:-1],r,i)
        duplicate=x[x.guild=="S"].iloc[[0]]
        with self.assertRaises(AssertionError):
            paired_effects(pd.concat([x,duplicate],ignore_index=True))


if __name__=="__main__":
    unittest.main()
