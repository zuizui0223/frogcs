"""Synthetic controls for five-stage-model POM: seed pairing and censoring."""
import unittest
import numpy as np
import pandas as pd

from summarize_stage_dispersal_pom import (
    MODES,SEEDS,GUILDS,complete_source_table,paired_dispersal_effects,
    model_native_motifs
)


def matched_five_modes():
    rows=[]
    for mode in MODES:
        for reverse in (False,True):
            for seed in SEEDS:
                for guild in GUILDS:
                    if guild=="S":
                        occupied={"off":2,"original":4,"adult_only":5,
                                  "aquatic_only":3,"S_only":6}[mode]
                        returns={"off":0,"original":3,"adult_only":2,
                                 "aquatic_only":1,"S_only":4}[mode]
                    else:
                        occupied=0 if guild=="D" and reverse else 8
                        returns=0
                    followed=1 if returns else 0
                    rows.append(dict(mobility=mode,reverse=reverse,seed=seed,
                        guild=guild,occupied_year20=occupied,
                        n_extinctions=returns,
                        n_recolonizations=returns,
                        n_observed_survivor_movements=0 if mode=="off" else returns*3,
                        n_living_elsewhere_than_founder_patch=0 if mode=="off" else returns*5,
                        n_living_grandchild_or_later=20 if guild=="F" else 3,
                        n_multisite_founder_lineages=0 if mode=="off" else int(returns>0),
                        n_two_followups_eligible=followed,
                        n_two_followups_retained=followed,
                        n_two_followups_and_local_birth=followed,
                        n_two_followups_censored=returns-followed,
                        n_postreturn_outside_parent_birth_events=followed))
    return pd.DataFrame(rows)


class FiveStageMigrationPOMTests(unittest.TestCase):
    def test_no_missing_source_model_and_100pct_seed_coverage(self):
        a=matched_five_modes()
        x=complete_source_table(a[a.mobility.isin(("off","original"))],
                                a[~a.mobility.isin(("off","original"))])
        self.assertEqual(len(x),120)
        self.assertTrue(x.groupby(["mobility","reverse","guild"]).seed.nunique().eq(4).all())
        self.assertTrue(x[x.mobility=="off"].n_observed_survivor_movements.eq(0).all())

    def test_contrasts_include_7_legal_comparisons_per_seed_group(self):
        a=matched_five_modes()
        source=complete_source_table(a[a.mobility.isin(("off","original"))],
                                     a[~a.mobility.isin(("off","original"))])
        contrasts=paired_dispersal_effects(source)
        self.assertEqual(len(contrasts),168)
        tested=contrasts[(contrasts.mobility=="adult_only")&
                         (contrasts.baseline=="no_dispersal")&
                         (contrasts.guild=="S")]
        self.assertTrue(tested.delta_occupied_year20.eq(3).all())
        self.assertTrue(tested.delta_n_recolonizations.eq(2).all())
        testfull=contrasts[(contrasts.mobility=="adult_only")&
                           (contrasts.baseline=="original_all_stages")&
                           (contrasts.guild=="S")]
        self.assertTrue(testfull.delta_occupied_year20.eq(1).all())
        self.assertEqual(contrasts.groupby(
            ["mobility","baseline","reverse","guild"]).seed.nunique().min(),4)

    def test_pom_motif_sufficiency_does_not_fake_field_posterior(self):
        x=matched_five_modes()
        source=complete_source_table(x[x.mobility.isin(("off","original"))],
                                     x[~x.mobility.isin(("off","original"))])
        motif=model_native_motifs(source,paired_dispersal_effects(source))
        self.assertEqual(len(motif),30)
        self.assertTrue(motif.n_stochastic_seeds.eq(4).all())
        self.assertTrue(motif.outcome_scope.eq(
            "MODEL_NATIVE_UNCALIBRATED_SPATIAL_POM_NOT_FIELD_ABC").all())
        on=motif[(motif.mobility=="adult_only")&
                 (motif.guild=="S")&(motif.reverse==False)].iloc[0]
        self.assertEqual(on.n_seed_replicates_with_recolonization,4)
        self.assertEqual(on.n_seed_replicates_with_birth_plus_2year_persistence,4)
        self.assertEqual(on.n_seed_replicates_exceeding_same_seed_no_mobility_occupancy,4)

    def test_broken_annual_censoring_and_double_seeds_fail(self):
        a=matched_five_modes()
        prior=a[a.mobility.isin(("off","original"))]
        fresh=a[~a.mobility.isin(("off","original"))]
        bad=fresh.copy()
        bad.loc[bad.index[0],"n_two_followups_censored"]=999
        with self.assertRaises(AssertionError):
            complete_source_table(prior,bad)
        with self.assertRaises(AssertionError):
            complete_source_table(prior,pd.concat([fresh,fresh.iloc[[0]]]))
        with self.assertRaises(AssertionError):
            complete_source_table(prior,fresh.iloc[:-1])


if __name__=="__main__":
    unittest.main()
