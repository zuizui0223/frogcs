#!/usr/bin/env python3
"""Unit tests for named reproductive-mode leaveout, distinct from trait causality."""
import unittest
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import naamp_fossorial_leaveout_soil_effect_v0_1 as m

class ReproductiveModeLeaveoutTests(unittest.TestCase):
    def test_predefined_traits_separate_terrestrial_eggs_from_burrowing(self):
        self.assertIn("Eleutherodactylus planirostris",m.TERRESTRIAL_EGGS)
        self.assertNotIn("Eleutherodactylus planirostris",m.FOSSORIAL_AQUATIC)
        self.assertIn("Pseudacris streckeri",m.FOSSORIAL_AQUATIC)
    def test_strong_new_gates_dry_absence(self):
        events={
            ("wet","1"):{"Scaphiopus holbrookii":2,"Anaxyrus americanus":2},
            ("dry","1"):{"Scaphiopus holbrookii":1}}
        vals=m.event_count("wet","dry",["1"],events)
        self.assertEqual(vals["all"],1)
        self.assertEqual(vals["burrowers_water_eggs"],0)
        self.assertEqual(vals["all_excluding_named_special_modes"],1)
    def test_when_taxon_is_new_strong_correctly_removed(self):
        events={("wet","1"):{"Scaphiopus holbrookii":3,
                             "Eleutherodactylus planirostris":2,
                             "Anaxyrus americanus":2},
                ("dry","1"):{}}
        z=m.event_count("wet","dry",["1"],events)
        self.assertEqual(z["all"],3)
        self.assertEqual(z["burrowers_water_eggs"],1)
        self.assertEqual(z["terrestrial_egg_direct_developer"],1)
        self.assertEqual(z["all_excluding_named_special_modes"],1)
    def test_no_frog_names_are_called_nonfossorial_in_control(self):
        self.assertEqual(m.RESULT_NAME,"OTHER_NAAMP_TAXA_NOT_NECESSARILY_NONFOSSORIAL")
    def test_no_egg_inference_is_allowed(self):
        self.assertFalse(m.CAN_DETECT_OVIPOSITION)
    def test_empty_current_stop_has_no_false_positive(self):
        self.assertEqual(m.event_count("wet","dry",["2"],{} )["all"],0)
if __name__=="__main__":unittest.main()
