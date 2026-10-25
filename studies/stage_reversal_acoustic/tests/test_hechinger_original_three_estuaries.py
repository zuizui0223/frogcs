"""Hechinger three estuary exact-stage ontology and link-class guards."""
import importlib.util
import json
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]/"macro"
SOURCE=ROOT/"audit_hechinger_original_three_estuaries.py"
spec=importlib.util.spec_from_file_location("hechinger_three_original",SOURCE)
mod=importlib.util.module_from_spec(spec)
sys.modules[spec.name]=mod
spec.loader.exec_module(mod)

class OriginalThreeEstuaryStageQA(unittest.TestCase):
    def test_source_identity(self):
        self.assertEqual(len(mod.COMMIT),40)
        self.assertEqual(len(mod.FILE_SHA),2)
        self.assertEqual(mod.SITES,("CSM","EPB","BSQ"))
        self.assertTrue(all(len(x)==40 for x in mod.FILE_SHA.values()))

    def test_open_morphospecies_is_not_binomial(self):
        self.assertIsNone(mod.taxon({"Genus":"Himasthla","SpecificEpithet":"B"}))
        self.assertEqual(mod.taxon({"Genus":"Himasthla","SpecificEpithet":"B"},broad=True),"Himasthla B")
        self.assertEqual(mod.taxon({"Genus":"Macoma","SpecificEpithet":"secta"}),"Macoma secta")
        self.assertIsNone(mod.taxon({"Genus":"Macoma","SpecificEpithet":""}))

    def test_stages_require_observed_original_node_labels(self):
        nd={"1":{"Genus":"Anax","SpecificEpithet":"junius","Stage":"adult",
                 "OrganismalGroup":"odonate"},
            "2":{"Genus":"Rana","SpecificEpithet":"temporaria","Stage":"",
                 "OrganismalGroup":"frog"}}
        x=mod.stage_edges([{"ConsumerNodeID":"1","ResourceNodeID":"2","LinkType":"predation"}],nd)
        self.assertEqual(x,[])

    def test_proper_directed_reciprocal_stages(self):
        x={"pred":"A a","prey":"B b","ps":"adult","rs":"larva","pg":"fish",
           "rg":"fish","type":"predation","par":False}
        y={"pred":"B b","prey":"A a","ps":"adult","rs":"larva","pg":"fish",
           "rg":"fish","type":"predation","par":False}
        totals,rows=mod.reciprocal([x,y])
        self.assertEqual((totals["n_reciprocal"],totals["n_changed"]), (1,1))
        self.assertFalse(rows[0]["double_bivalve_adult_consumes_heterospecific_larva"])

    def test_larva_to_larva_not_stage_reversal(self):
        x={"pred":"A a","prey":"B b","ps":"larva","rs":"larva",
            "pg":"frog","rg":"dragonfly","type":"predation","par":False}
        y={**x,"pred":"B b","prey":"A a"}
        _,q=mod.reciprocal([x,y])
        self.assertFalse(q[0]["changed"])

    def test_typed_parasitism_not_predation(self):
        x={"pred":"A a","prey":"B b","ps":"adult","rs":"larva","pg":"frog","rg":"frog","type":"macroparasitism","par":True}
        y={"pred":"B b","prey":"A a","ps":"adult","rs":"larva","pg":"frog","rg":"frog","type":"predation","par":True}
        raw,_=mod.reciprocal([x,y])
        pred,_=mod.reciprocal([z for z in [x,y] if z["type"]=="predation"])
        self.assertEqual(raw["n_reciprocal"],1)
        self.assertEqual(pred["n_reciprocal"],0)

    def test_frozen_source_numbers(self):
        source=json.loads(mod.FROZEN.read_text(encoding="utf-8"))
        self.assertEqual(source["meta"]["n_meta_links"],11270)
        self.assertEqual(source["meta"]["n_present_any_site"],9247)
        self.assertEqual(source["meta"]["n_present_no_site"],2023)
        self.assertEqual(source["totals"]["stage_shift_strict_species_all_classes"],768)
        self.assertEqual(source["totals"]["stage_shift_with_morphospecies_placeholders"],803)
        self.assertEqual(source["totals"]["non_species_placeholder_excess"],35)
        self.assertEqual(source["totals"]["strict_predation_stage_shift_site_pairs"],20)
        self.assertEqual(source["totals"]["bivalve_module_site_pairs"],20)

    def test_two_five_species_modules_not_twenty_independent_trials(self):
        source=json.loads(mod.FROZEN.read_text())
        for site,expect in [("CSM",10),("EPB",10),("BSQ",0)]:
            motif=source["sites"][site]["bivalve_motif"]
            self.assertEqual(motif["n_pairs"],expect)
            self.assertEqual(motif["n_double_adult_to_other_species_larva"],expect)
            self.assertEqual(motif["species"].__len__(),5 if expect else 0)
            self.assertEqual(expect,(5*4//2 if site!="BSQ" else 0))

    def test_original_bivalve_body_mass_is_assigned_once_for_all_larvae(self):
        source=json.loads((ROOT/"results"/"HECHINGER2011_BIVALVE_MOTIF_STAGE_BODYMASS_SOURCE_AUDIT_V0_1.json").read_text())
        for site in ("CSM","EPB"):
            data=source["sites"][site]
            self.assertEqual(data["n_stage_motif_directed_links"],20)
            self.assertEqual(data["n_distinct_larval_mass_values"],1)
            self.assertEqual(data["larval_mass_values_g"],[0.0000363288])
            self.assertEqual(data["larval_mass_estimation_methods"],["approximation"])
            self.assertEqual(data["n_bilateral_species_pairs"],10)
        self.assertEqual(source["role_reversal_claim"],
                         "SIZE_CANDIDATE_ONLY_NO_DIRECT_PREDATION_RATE")

    def test_site_pair_directions_share_single_source_programme(self):
        source=json.loads(mod.FROZEN.read_text())
        self.assertEqual(set(source["sites"]),set(mod.SITES))
        self.assertEqual(source["meta"]["n_site_presence_links"],13966)
        self.assertTrue("not independent" in " ".join(source["validation_limitations"]).lower() or
                        "same source" in " ".join(source["validation_limitations"]).lower())

    def test_source_does_not_identify_attack_events(self):
        source=json.loads(mod.FROZEN.read_text())
        self.assertEqual(source["direct_observed_stage_switch_events"],"NOT_IDENTIFIABLE")
        self.assertEqual(source["acoustic_warning_events"],"NOT_IN_SOURCE")

if __name__=="__main__":
    unittest.main()
