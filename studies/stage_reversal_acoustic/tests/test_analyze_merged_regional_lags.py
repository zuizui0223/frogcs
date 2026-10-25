"""Prespecified lag arithmetic checks; no synthetic or observational p-values."""
import importlib.util
import json
import sys
import unittest
from pathlib import Path

DIR=Path(__file__).resolve().parents[1]
SCRIPT=DIR/"src"/"analyze_merged_regional_lags.py"
spec=importlib.util.spec_from_file_location("regional_lags",SCRIPT)
mod=importlib.util.module_from_spec(spec)
sys.modules[spec.name]=mod
spec.loader.exec_module(mod)


class LagReanalysisTests(unittest.TestCase):
    def test_observed_original_aggregate_reproduces_lags(self):
        src=json.loads((DIR/"results"/"FROGID_ANAX_COARSE_WEEKLY_REAL_2018_2019_V1.json").read_text())
        out=mod.run(src)
        self.assertTrue(mod.validate(out,src))
        self.assertEqual(out["n_focal_call_positive_events"],6)
        self.assertEqual(out["n_frogid_recording_events"],982)
        self.assertEqual(len(out["same_anchor_directional_diagnostics"]),4)

    def test_survey_missing_is_not_anax_zero(self):
        sample=[{"week_start":"2018-09-03","unique_recording_events":1,
                 "focal_positive_recording_events":0,"anax_emergers":None,
                 "anax_valid_wetland_visits":None}]
        v=mod.classify(sample)
        self.assertIsNone(next(iter(v.values()))[1])

    def test_survey_effort_with_unobserved_count_fails(self):
        sample=[{"week_start":"2018-09-03","unique_recording_events":1,
                 "focal_positive_recording_events":0,"anax_emergers":None,
                 "anax_valid_wetland_visits":11}]
        with self.assertRaisesRegex(ValueError,"BOTH missing"):
            mod.classify(sample)

    def test_focal_fraction_cannot_exceed_eligible_submissions(self):
        sample=[{"week_start":"2018-09-03","unique_recording_events":1,
                 "focal_positive_recording_events":2,"anax_emergers":0,
                 "anax_valid_wetland_visits":11}]
        with self.assertRaisesRegex(ValueError,"invalid audio"):
            mod.classify(sample)

    def test_no_false_correlation_with_constant_signal(self):
        self.assertIsNone(mod.pearson([(0,1),(0,3),(0,7),(0,9)]))


if __name__=="__main__":
    unittest.main()
