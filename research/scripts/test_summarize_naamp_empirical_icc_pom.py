"""Synthetic integrity tests for full three-noise ICC comparison and matched risk."""
import unittest
import pandas as pd

from summarize_naamp_empirical_icc_pom import (
    robust_three_noise,matched_forthcoming_facilitation,CONTEXTS
)


class EmpiricalICCCombinedAuditTests(unittest.TestCase):
    def test_12_observation_noise_conditions_represented_for_each_source(self):
        rows=[]
        groups={"frozen132":104,"realrate192":128,"facilitation72":48}
        for family,count in groups.items():
            for i in range(count):
                for noise in ("iid","spatial_block_025","naamp_residual_icc_2degree"):
                    for background in ("uniform","target_group"):
                        for mode in ("rank_signal","log_signal"):
                            rows.append(dict(family=family,
                                source_group=f"{family}_source_{i:03d}",
                                noise_type=noise,background=background,mode=mode,
                                calibration_status="MATCHED_R2",
                                modal_complete_count=12 if i%2 else 0,
                                modal_complete_frequency=.09375 if i%2 else 0.,
                                soft_joint_agreement=.2,
                                q_lowS_near_zero=.7))
        x=pd.DataFrame(rows)
        s,t=robust_three_noise(x)
        self.assertEqual(len(s),sum(groups.values()))
        self.assertEqual(len(t),3)
        self.assertTrue(s.n_conditions.eq(CONTEXTS).all())
        self.assertEqual(s.all_12_ge_10pct.sum(),0)
        self.assertEqual(t.n_all_12_any_exact.sum(),140)
        with self.assertRaises(ValueError):
            robust_three_noise(x.iloc[:-1])

    def test_same_original_case_pair_compares_stronger_vs_neutral(self):
        x=[]
        for bg in ("uniform","target_group"):
            for mode in ("rank_signal","log_signal"):
                for case in range(24):
                    for stage in ("neutral","moderate","strong"):
                        delta={"neutral":0.,"moderate":.02,"strong":-.03}[stage]
                        x.append(dict(family="facilitation72",background=bg,mode=mode,
                                      case=f"case_{case:03d}",hypothesis=stage,
                                      calibration_status="MATCHED_R2",
                                      source_group=f"{stage}_case_{case:03d}",
                                      soft_joint_agreement=.18+delta,
                                      modal_complete_frequency=.08+delta,
                                      q_lowS_near_zero=.6+delta))
        paired,summary=matched_forthcoming_facilitation(pd.DataFrame(x))
        self.assertEqual(len(paired),192)
        self.assertEqual(len(summary),8)
        self.assertTrue(summary[summary.treatment=="moderate"].mean_gain.gt(0).all())
        self.assertTrue(summary[summary.treatment=="strong"].mean_gain.lt(0).all())
        self.assertTrue(summary.n_cases.eq(24).all())

    def test_broken_pair_fails_without_fabricating_performance(self):
        x=[]
        for case in range(24):
            for bg in ("uniform","target_group"):
                for mode in ("rank_signal","log_signal"):
                    for stage in ("neutral","moderate","strong"):
                        x.append(dict(family="facilitation72",background=bg,mode=mode,
                                      case=f"case_{case:03d}",hypothesis=stage,
                                      calibration_status="MATCHED_R2",
                                      source_group="sim",
                                      soft_joint_agreement=.2,
                                      modal_complete_frequency=.1,
                                      q_lowS_near_zero=.6))
        with self.assertRaises((ValueError,AssertionError)):
            matched_forthcoming_facilitation(pd.DataFrame(x).iloc[:-1])


if __name__=="__main__":
    unittest.main()
