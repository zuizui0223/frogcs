"""Source identity and factorial ablation specification checks."""
import unittest

import numpy as np

from isolate_S_growth_D_duration_finite80y import (
    NEW_CONTEXTS,source_factorial,run,pair_difference
)
from spatial_cohort_80y_bridge import replay_gate
from finite_n_source_cohort_bridge import simulate_finite_group,summarize_finite_group


class SourceGrowthDurationFactorial(unittest.TestCase):

    def test_original_and_old_alternative_same_arrival_order(self):
        hybrids,o,d=source_factorial()
        self.assertEqual(len(hybrids),64)
        for source in (o,d):
            np.testing.assert_allclose(source.sa,20)
            np.testing.assert_allclose(source.da,0)
            self.assertEqual(len(source),32)
        np.testing.assert_allclose(o.dduration,40)
        np.testing.assert_allclose(d.dduration,60)
        np.testing.assert_allclose(d.sg/o.sg,.030/.014)

    def test_independently_change_growth_and_aquatic_duration(self):
        hybrids,o,d=source_factorial()
        a=hybrids[hybrids.context.eq("S_growth_fast_only")].sort_values(
            ["plant_model","reverse_on","vertex","draw"]
        ).reset_index(drop=True)
        b=hybrids[hybrids.context.eq("D_aquatic_long_only")].sort_values(
            ["plant_model","reverse_on","vertex","draw"]
        ).reset_index(drop=True)
        self.assertEqual(len(a),32)
        self.assertEqual(len(b),32)
        np.testing.assert_allclose(a.sg,d.sg)
        np.testing.assert_allclose(a.dduration,o.dduration)
        np.testing.assert_allclose(b.sg,o.sg)
        np.testing.assert_allclose(b.dduration,d.dduration)
        np.testing.assert_allclose(a.sa,b.sa)
        np.testing.assert_allclose(a.da,b.da)
        self.assertFalse((a.original_case>=0).any())
        self.assertEqual(set(hybrids.context),set(NEW_CONTEXTS))

    def test_full_source_replay_after_single_factor_change(self):
        hybrids,*_=source_factorial()
        errs=replay_gate(hybrids,years=4,window=2,dt=.25)
        for field,val in errs.items():
            self.assertLessEqual(val,1e-8)

    def test_actual_source_run_events_and_pairing(self):
        hybrids,*_=source_factorial()
        g=hybrids[
            hybrids.context.eq("S_growth_fast_only")&
            hybrids.plant_model.eq("SF0_DF0_DS1_L0")&
            hybrids.reverse_on.eq(0)
        ].reset_index(drop=True)
        self.assertEqual(len(g),8)
        records=[]
        for mode in ("off","both"):
            o=simulate_finite_group(
                g,scale=3,seed=101,mode=mode,
                immigration=False,years=4,dt=.25
            )
            a,e=summarize_finite_group(
                g,o,scale=3,seed=101,mode=mode,
                immigration=False,years=4
            )
            self.assertEqual(int(a.n_local_returns.sum()),len(e))
            self.assertFalse(a.n_external_immigrants.any())
            records.append(a)
        import pandas as pd
        p=pair_difference(pd.concat(records,ignore_index=True))
        self.assertEqual(len(p),8*3)
        self.assertTrue(np.isfinite(p.delta_final_occupied_patches).all())


if __name__=="__main__":
    unittest.main()
