"""Test original stage diffusion ablations without touching ABM/PDE kernels."""
import unittest
import numpy as np
import pandas as pd

from multigeneration_reversal import (
    Rates,STAGES,FT,FA,SL,SA,DN,DE,DA,initial_grid
)
from tracked_spatial_pedigree import simulate_traced_abm,SEEDS
from run_stage_specific_dispersal_ablation import (
    stage_mobility_rates,MOBILITY_STAGES,NEW_MODES,
    actual_mode_summary
)


class StageDiffusionHypothesisTests(unittest.TestCase):
    def test_original_and_off_are_exact_controls_and_stage_modes_disjoint(self):
        p=Rates()
        self.assertEqual(stage_mobility_rates("original",p),p)
        self.assertEqual(stage_mobility_rates("off",p).diffusion,(0.,)*7)
        self.assertEqual(set(MOBILITY_STAGES["adult_only"]),{FA,SA,DA})
        self.assertEqual(set(MOBILITY_STAGES["aquatic_only"]),{FT,SL,DN})
        self.assertEqual(set(MOBILITY_STAGES["S_only"]),{SL,SA})
        for mode in NEW_MODES:
            q=stage_mobility_rates(mode,p)
            for k in range(7):
                self.assertEqual(q.diffusion[k],
                    p.diffusion[k] if k in MOBILITY_STAGES[mode] else 0.)
        with self.assertRaises(ValueError):
            stage_mobility_rates("unknown",p)

    def test_only_mobile_stage_types_appear_in_per_uid_move_ledger(self):
        x,v=initial_grid(4)
        for mode in NEW_MODES:
            p=stage_mobility_rates(mode)
            z=simulate_traced_abm(x,v,p,years=1,dt=.05,seed=11,reverse=False)
            permitted={STAGES[i] for i in MOBILITY_STAGES[mode]}
            observed=set(z["movements"].stage) if len(z["movements"]) else set()
            self.assertTrue(observed.issubset(permitted))
            self.assertTrue(z["registry"].uid.is_unique)
            self.assertEqual(len(z["patch"]),2*4*3)
            self.assertEqual(len(z["lineages"]),3)

    def test_stage_specific_model_outputs_differ_in_comparable_synthetic_system(self):
        x,v=initial_grid(4)
        a=simulate_traced_abm(x,v,stage_mobility_rates("adult_only"),
                              years=2,dt=.05,seed=13,reverse=False)
        b=simulate_traced_abm(x,v,stage_mobility_rates("aquatic_only"),
                              years=2,dt=.05,seed=13,reverse=False)
        self.assertGreater(len(a["movements"]),0)
        self.assertGreater(len(b["movements"]),0)
        self.assertNotEqual(a["movements"].stage.value_counts().to_dict(),
                            b["movements"].stage.value_counts().to_dict())

    def test_mode_summary_maintains_no-recolonization_negative_fixture(self):
        patch=[]
        for reverse in (False,True):
            for seed in SEEDS:
                for guild in ("F","S","D"):
                    for year in range(21):
                        for place in range(3):
                            patch.append(dict(mobility="adult_only",
                                reverse=reverse,seed=seed,guild=guild,
                                patch=place,year=year,occupied=True,
                                locally_extinct=False,recolonized=False,
                                known_surviving_immigrant_arrivals=0))
        p=pd.DataFrame(patch)
        m=actual_mode_summary(p,pd.DataFrame(),year=20)
        self.assertEqual(len(m),24)
        self.assertTrue(m.n_occupied_year_end.eq(3).all())
        self.assertTrue(m.n_recolonizations.eq(0).all())
        self.assertTrue(m.n_two_census_persistence_plus_local_births.eq(0).all())
        self.assertTrue(m.n_return_events_right_censored_at_2years.eq(0).all())


if __name__=="__main__":
    unittest.main()
