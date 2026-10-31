"""Synthetic-only checks of directional constraint-lattice diagnostics."""
import unittest
import numpy as np
import pandas as pd

from diagnose_signed_context_tradeoff import (
    METRICS,normalize_sources,observed_sign_targets,satisfies,
    enumerate_all_subsets,minimal_conflicts,threshold_sensitivity
)


def small_fixture():
    cases={
        "uniform":[(-1,-1,1,-1),(-1,1,-1,-1),(1,-1,1,-1),(1,1,1,1)],
        "target_group":[(-1,-1,1,-1),(-1,1,-1,-1),(1,-1,-1,-1),(1,1,1,1)]
    }
    frozen=[]
    rate=[]
    observation=[]
    for bg, patterns in cases.items():
        for case,pattern in enumerate(patterns):
            frozen.append(dict(background=bg,case=f"case_{case:03d}",
                               source_group=f"case_{case:03d}",
                               **{"model_sign_"+n:int(v) for n,v in zip(METRICS,pattern)}))
            rate.append(dict(background=bg,case=f"case_{case:03d}",
                             rate_draw=0,structural_group=f"group_{case}",
                             **dict(zip(METRICS,pattern))))
        for metric in METRICS:
            confidence=.99 if bg=="uniform" or metric=="OV" else .92
            observation.append(dict(background=bg,metric=metric,
                                    observed_direction=-1,
                                    frequency_negative=confidence,
                                    frequency_positive=1-confidence))
    return pd.DataFrame(frozen),pd.DataFrame(rate),pd.DataFrame(observation)


class MinimalSignedConflictTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.frozen,cls.rate,cls.observation=small_fixture()

    def test_joint_direction_lattice_has_the_expected_30_rows(self):
        target=observed_sign_targets(self.observation,.90)
        a=enumerate_all_subsets(self.frozen,self.rate,target)
        self.assertEqual(len(a),30)
        self.assertEqual(int(a.n_constraints.max()),4)
        self.assertEqual(int(a[a.background=="uniform"].n_frozen_cases.max()),3)
        target95=observed_sign_targets(self.observation,.95)
        self.assertEqual(len(target95["uniform"]),4)
        self.assertEqual(list(target95["target_group"]),["OV"])

    def test_minimal_failure_is_pair_in_uniform_but_triple_in_target(self):
        a=enumerate_all_subsets(self.frozen,self.rate,
                                observed_sign_targets(self.observation,.90))
        b=minimal_conflicts(a,"n_frozen_source_groups")
        subset={(r.background,r.subset) for r in b.itertuples()}
        self.assertIn(("uniform","OV;delta_S_high_minus_low"),subset)
        self.assertIn(("target_group","OS;OV;delta_S_high_minus_low"),subset)
        self.assertNotIn(("uniform","OS;OV;delta_S_high_minus_low"),subset)

    def test_threshold_sensitivity_keeps_full_catalog_and_cross_no_win(self):
        a=threshold_sensitivity(self.frozen,self.rate,self.observation)
        self.assertEqual(len(a),4)
        self.assertTrue(a[a.threshold==.90].n_robust_directions.eq(4).all())
        self.assertEqual(a[(a.threshold==.95)&(a.background=="target_group")].
                         n_robust_directions.iloc[0],1)
        self.assertTrue(a.n_cross_background_case_labels.eq(0).all())

    def test_mismatched_process_rate_row_rejected_without_source_matching(self):
        # Full input shape lets the same source-validation code protect 384
        # genuine-rate rows from accidental joins to an unrelated cohort.
        fixed=[]
        rate=[]
        source=[]
        for bg in ("uniform","target_group"):
            for case in range(132):
                fixed.append(dict(background=bg,case=f"case_{case:03d}",
                                  source_group=f"source_{case%104:03d}",
                                  **{"model_sign_"+m:-1 for m in METRICS}))
            for draw in range(8):
                for case in range(24):
                    tag=f"case_{case:03d}"
                    rate.append(dict(background=bg,rate_draw=draw,case=tag,
                                     structural_group=f"group_{case%12}",
                                     model_delta_S=-.3,model_delta_V=-.2))
                    source.append(dict(background=bg,draw=draw,case=tag,
                                       OS=-.2,OV=-.1,
                                       O_with_S_low=.1,O_with_S_high=-.2,
                                       heldout_O_with_V_zero=.0,
                                       heldout_O_with_V_positive=-.2))
        a,b,receipt=normalize_sources(pd.DataFrame(fixed),pd.DataFrame(rate),
                                       pd.DataFrame(source))
        self.assertEqual(len(a),264)
        self.assertEqual(len(b),384)
        self.assertAlmostEqual(receipt["max_recomputed_delta_S_discrepancy"],0)
        broken=pd.DataFrame(source)
        broken.loc[0,"O_with_S_low"]=.2
        with self.assertRaises(AssertionError):
            normalize_sources(pd.DataFrame(fixed),pd.DataFrame(rate),broken)


if __name__=="__main__":
    unittest.main()
