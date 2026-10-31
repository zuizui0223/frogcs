"""Synthetic invariants for baseline-vs-amplification *paired* R² audit."""
import unittest
import numpy as np
import pandas as pd

from r2_calibrated_directional_pom import FAMILIES,NOISE_TYPES,MODES,BACKGROUNDS
from audit_r2_facilitation_pairs import paired_facilitation,eight_condition_stability


class NoiseMatchedPairedAuditTests(unittest.TestCase):
    def test_pairing_is_case_preserving_and_outcome_blind(self):
        out=[]
        for noise in NOISE_TYPES:
            for bg in BACKGROUNDS:
                for mode in MODES:
                    for i in range(24):
                        for stage in ("neutral","moderate","strong"):
                            delta={"neutral":0.,"moderate":.02,"strong":-.01}[stage]
                            out.append(dict(family="facilitation72",noise_type=noise,
                                            background=bg,mode=mode,case=f"case_{i:03d}",
                                            hypothesis=stage,
                                            soft_joint_agreement=.2+delta,
                                            modal_complete_frequency=.10+delta,
                                            q_lowS_near_zero=.6+delta,
                                            r2_evaluation_mean=.05,
                                            calibration_status="MATCHED_R2"))
        x,s,stable=paired_facilitation(pd.DataFrame(out))
        self.assertEqual(len(x),384)
        self.assertEqual(len(s),16)
        self.assertEqual(len(stable),48)
        self.assertEqual(int(stable[stable.hypothesis=="moderate"].all_eight_strictly_positive.sum()),24)
        self.assertEqual(int(stable[stable.hypothesis=="strong"].all_eight_nonnegative.sum()),0)
        self.assertTrue(s[s.hypothesis=="moderate"].positive_gain_cases.eq(24).all())
        self.assertTrue(s[s.hypothesis=="strong"].negative_gain_cases.eq(24).all())

    def test_all_group_consensus_is_checked_across_exactly_eight_conditions(self):
        x=[]
        counts={"frozen132":104,"realrate192":128,"facilitation72":48}
        for family,n in counts.items():
            for i in range(n):
                for noise in NOISE_TYPES:
                    for bg in BACKGROUNDS:
                        for mode in MODES:
                            x.append(dict(family=family,source_group=f"{family}_{i:03d}",
                                noise_type=noise,background=bg,mode=mode,
                                calibration_status="MATCHED_R2",
                                modal_complete_count=14 if i%2 else 0,
                                modal_complete_frequency=.109375 if i%2 else 0.,
                                soft_joint_agreement=.25,
                                q_lowS_near_zero=.9))
        scores,totals=eight_condition_stability(pd.DataFrame(x))
        self.assertEqual(len(scores),sum(counts.values()))
        self.assertEqual(len(totals),3)
        for row in totals.itertuples():
            expected=counts[row.family]//2
            self.assertEqual(row.n_all_8_with_any_complete,expected)
            self.assertEqual(row.n_all_8_at_least_10pct,expected)
        # Losing an entire condition should be a fatal source completeness error.
        with self.assertRaises(AssertionError):
            eight_condition_stability(pd.DataFrame(x).iloc[:-1])


if __name__=="__main__":
    unittest.main()
