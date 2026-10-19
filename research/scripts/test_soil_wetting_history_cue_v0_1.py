#!/usr/bin/env python3
"""No-outcome tests for precommitted 24h/7d soil-water-trajectory comparison."""
from __future__ import annotations
import sys
import unittest
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
import numpy as np
import pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parent))
import soil_wetting_history_cue_v0_1 as new

def fake_pairs():
    return pd.DataFrame([
        dict(wet_RunID="101",dry_RunID="103",route_cluster="OH:21",
             soil1_w=.23,soil2_w=.20,soil1_d=.13,soil2_d=.12),
        dict(wet_RunID="102",dry_RunID="104",route_cluster="OH:21",
             soil1_w=.33,soil2_w=.28,soil1_d=.17,soil2_d=.14)])

def fake_history():
    return pd.DataFrame([
        dict(RunID="101",soil1_t=.23,soil2_t=.20,soil1_24h=.21,soil2_24h=.18,
             soil1_168h=.14,soil2_168h=.13),
        dict(RunID="102",soil1_t=.33,soil2_t=.28,soil1_24h=.30,soil2_24h=.25,
             soil1_168h=.32,soil2_168h=.27),
        dict(RunID="103",soil1_t=.13,soil2_t=.12,soil1_24h=.11,soil2_24h=.10,
             soil1_168h=.12,soil2_168h=.11),
        dict(RunID="104",soil1_t=.17,soil2_t=.14,soil1_24h=.15,soil2_24h=.12,
             soil1_168h=.11,soil2_168h=.09)])

class WettingTrajectoryTests(unittest.TestCase):
    def test_lagged_hours_are_before_floored_utc_survey(self):
        t=datetime(2014,6,30,21,45,tzinfo=ZoneInfo("America/New_York"))
        times=new.source_times(t)
        self.assertEqual(times["now"],np.datetime64("2014-07-01T01:00:00.000000000"))
        self.assertEqual(times["minus24"],np.datetime64("2014-06-30T01:00:00.000000000"))
        self.assertEqual(times["minus168"],np.datetime64("2014-06-24T01:00:00.000000000"))
        self.assertTrue(times["minus168"]<times["minus24"]<times["now"])
    def test_pair_7day_change_and_current_values(self):
        d=new.attach(fake_pairs(),fake_history())
        self.assertEqual(len(d),2)
        # wet 101 common rise (0.215-0.135)=0.080;
        # dry 103 common rise (0.125-0.115)=0.010
        self.assertAlmostEqual(d.h7_delta.iloc[0],.070,places=12)
        self.assertAlmostEqual(d.h24_delta.iloc[0],0,places=12)
        self.assertAlmostEqual(d.current_soil_common_delta.iloc[0],.09,places=12)
        self.assertAlmostEqual(d.soil2_mid.iloc[0],(.20+.12)/2,places=12)
    def test_missing_lag_fails_closed(self):
        x=fake_history().drop(columns=["soil2_168h"])
        with self.assertRaisesRegex(ValueError,"missing"):
            new.attach(fake_pairs(),x)
    def test_duplicate_runids_fails_closed(self):
        x=pd.concat([fake_history(),fake_history().iloc[[0]]],ignore_index=True)
        with self.assertRaisesRegex(ValueError,"duplicate"):
            new.attach(fake_pairs(),x)
    def test_reanalysis_current_value_must_agree_with_archive(self):
        x=fake_history();x.loc[0,"soil1_t"]+=.001
        with self.assertRaisesRegex(ValueError,"current"):
            new.attach(fake_pairs(),x)
    def test_no_zero_imputation_for_unjoined_runid(self):
        x=fake_history().iloc[:-1]
        with self.assertRaisesRegex(ValueError,"missing"):
            new.attach(fake_pairs(),x)
    def test_no_future_times(self):
        times=new.source_times(datetime(2013,7,12,19,12,tzinfo=ZoneInfo("UTC")))
        self.assertEqual(len(times),3)
        self.assertTrue(all(v<=times["now"] for v in times.values()))
    def test_unit_conversion_for_trajectory_beta(self):
        # Per 0.01 m3/m3, not per SD and not percent-points.
        self.assertAlmostEqual(new.per_001(12.5),.125,places=12)
    def test_null_historical_velocity_when_same_past_now(self):
        p=fake_pairs();h=fake_history()
        h["soil1_24h"]=h["soil1_t"];h["soil2_24h"]=h["soil2_t"]
        h["soil1_168h"]=h["soil1_t"];h["soil2_168h"]=h["soil2_t"]
        d=new.attach(p,h)
        self.assertTrue(np.all(d.h7_delta==0))
        self.assertTrue(np.all(d.h24_delta==0))
    def test_no_interaction_or_forced_threshold_fishing(self):
        self.assertEqual(new.TRAJECTORY_TERMS,("h7_delta","h24_delta"))
        self.assertEqual(new.PRIMARY_RESPONSE,"strong_new_count")

if __name__=="__main__":
    unittest.main()
