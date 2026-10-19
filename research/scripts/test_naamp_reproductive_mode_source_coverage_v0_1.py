#!/usr/bin/env python3
"""Tests for post-discovery reproduction-mode source coverage; no effect model."""
import unittest
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import naamp_reproductive_mode_source_coverage_v0_1 as s

class ReproductiveCoverageTests(unittest.TestCase):
    def test_two_biological_categories_not_conflated(self):
        self.assertEqual(s.MODE["Eleutherodactylus planirostris"],
                         "terrestrial_eggs_direct_development")
        self.assertEqual(s.MODE["Pseudacris streckeri"],
                         "burrowing_adult_aquatic_eggs")
        self.assertEqual(s.MODE["Scaphiopus holbrookii"],
                         "burrowing_adult_aquatic_eggs")
    def test_not_all_other_taxa_assumed_nonburrowing(self):
        self.assertNotIn("Anaxyrus americanus",s.MODE)
    def test_prior_spadefoot_gate_not_modified(self):
        self.assertEqual(len(s.SPADEFOOT),4)
    def test_counts_valid_eligible_run_only(self):
        rows=[{"RunID":"r1","Species":"Eleutherodactylus planirostris","CallingIndex":"3"},
              {"RunID":"r2","Species":"Pseudacris streckeri","CallingIndex":"2"},
              {"RunID":"r3","Species":"Eleutherodactylus planirostris","CallingIndex":"3"}]
        runs={"r1":{"route_cluster":"FL:1","SurveyYear":2010},
              "r2":{"route_cluster":"TX:2","SurveyYear":2010}}
        x=s.summary(rows,runs)
        self.assertEqual(x["terrestrial_eggs_direct_development"]["strong_record_count"],1)
        self.assertEqual(x["burrowing_adult_aquatic_eggs"]["strong_record_count"],1)
    def test_ci1_not_considered_strong(self):
        z=s.summary([{"RunID":"r1","Species":"Pseudacris streckeri","CallingIndex":"1"}],
                    {"r1":{"route_cluster":"TX:2","SurveyYear":2010}})
        self.assertEqual(z["burrowing_adult_aquatic_eggs"]["strong_record_count"],0)
    def test_egg_data_not_inferred_from_call_data(self):
        self.assertFalse(s.EGGS_OBSERVED)
    def test_taxa_count_target(self):
        self.assertEqual(s.MODE["Scaphiopus couchii"],
                         "burrowing_adult_aquatic_eggs")

if __name__=="__main__":unittest.main()
