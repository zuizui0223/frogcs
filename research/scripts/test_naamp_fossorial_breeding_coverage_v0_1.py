#!/usr/bin/env python3
"""Synthetic-only tests for predeclared NAAMP spadefoot-burrowing trait audit.

The trait means adult fossorial habits with AQUATIC oviposition, NOT
subterranean egg-laying. Do not label all other taxa as nonfossorial.
"""
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import naamp_fossorial_breeding_coverage_v0_1 as m

class CoverageContractTests(unittest.TestCase):
    def test_named_spadefoot_label(self):
        self.assertEqual(m.group("Scaphiopus holbrookii"),"fossorial_aquatic_breeder")
        self.assertEqual(m.group("Spea bombifrons"),"fossorial_aquatic_breeder")
        self.assertEqual(m.group("Spea_intermodana"),"fossorial_aquatic_breeder")
    def test_terrestrial_nesting_other_genus_not_spadefoot(self):
        self.assertEqual(m.group("Leptodactylus fuscus"),"other_named_taxon")
    def test_control_is_not_labeled_nonburrowing(self):
        self.assertEqual(m.group("Anaxyrus americanus"),"other_named_taxon")
        self.assertEqual(m.group("Pseudacris crucifer"),"other_named_taxon")
    def test_nonbinomial_is_unresolved(self):
        self.assertEqual(m.group("SCAP"),"unresolved_taxon_label")
        self.assertEqual(m.group("1"),"unresolved_taxon_label")
        self.assertEqual(m.group(""),"unresolved_taxon_label")
    def test_latin_genus_case_and_whitespace(self):
        self.assertEqual(m.group("  scaphiopus  holbrookii "),"fossorial_aquatic_breeder")
    def test_unknown_identification_rejected_as_control(self):
        self.assertNotEqual(m.group("Anaxyrus sp."),"fossorial_aquatic_breeder")
    def test_count_strong_and_route_spanning(self):
        runs={"r1":{"route_cluster":"TX:11","SurveyYear":2010},
              "r2":{"route_cluster":"TX:11","SurveyYear":2011},
              "r3":{"route_cluster":"OK:22","SurveyYear":2011}}
        rows=[{"RunID":"r1","Species":"Scaphiopus holbrookii","CallingIndex":"2"},
              {"RunID":"r1","Species":"Scaphiopus holbrookii","CallingIndex":"3"},
              {"RunID":"r2","Species":"Scaphiopus holbrookii","CallingIndex":"1"},
              {"RunID":"r3","Species":"Spea bombifrons","CallingIndex":"3"},
              {"RunID":"r3","Species":"Pseudacris crucifer","CallingIndex":"3"}]
        summary=m.count_support(rows,runs)
        self.assertEqual(summary["burrowing_aquatic"]["strong_ci2plus_records"],3)
        self.assertEqual(summary["burrowing_aquatic"]["distinct_routes_with_strong"],2)
        self.assertEqual(summary["burrowing_aquatic"]["unique_taxa_with_strong"],2)
        self.assertEqual(summary["burrowing_aquatic"]["distinct_years_with_strong"],2)
    def test_threshold_gate_fixed(self):
        self.assertFalse(m.support_gate(199,30))
        self.assertFalse(m.support_gate(200,29))
        self.assertTrue(m.support_gate(200,30))
    def test_no_data_is_not_coded_as_zero_breeding(self):
        runs={"r1":{"route_cluster":"TX:11","SurveyYear":2010}}
        summary=m.count_support([{"RunID":"r1","Species":"Spea bombifrons","CallingIndex":""}],runs)
        self.assertEqual(summary["burrowing_aquatic"]["strong_ci2plus_records"],0)
        self.assertEqual(summary["uninterpretable_callindex_count"],1)
    def test_not_egg_evidence(self):
        self.assertTrue(m.SPADEFOOT_TRAIT["oviposition_in_water"])
        self.assertFalse(m.SPADEFOOT_TRAIT["oviposition_in_burrow"])
        self.assertFalse(m.SPADEFOOT_TRAIT["test_can_prove_causal_mating_or_eggs"])

if __name__=="__main__":unittest.main()
