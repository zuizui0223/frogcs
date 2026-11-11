"""Mouritsen et al. 2011 Otago typed interaction and parasite stage QA."""
import importlib.util
import json
import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]/"macro"
FILE=ROOT/"audit_otago_original_stage_edges.py"
spec=importlib.util.spec_from_file_location("otago_stages",FILE)
mod=importlib.util.module_from_spec(spec)
sys.modules[spec.name]=mod
spec.loader.exec_module(mod)

def node(i,name,stage,group):
    a,b=name.split(" ")
    return {"NodeID":str(i),"Genus":a,"SpecificEpithet":b,"Stage":stage,
            "OrganismalGroup":group}

def link(pred,prey,kind,evidence=""):
    return {"ConsumerNodeID":str(pred),"ResourceNodeID":str(prey),
            "LinkType":kind,"LinkEvidence":evidence}

class OriginalFoodWebTypeIntegrity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source=json.loads(mod.RESULT.read_text(encoding="utf-8"))

    def test_original_noninvented_source_totals(self):
        r=self.source["totals"]
        self.assertEqual(r["n_source_links"],1924)
        self.assertEqual(r["n_source_nodes"],180)
        self.assertEqual(r["original_interaction_categories"]["Predation"],1206)
        self.assertEqual(r["source_link_evidence"],{"BLANK":1924})

    def test_mixed_interaction_and_parasitic_stages_are_not_free_living_reversal(self):
        t=self.source["totals"]
        self.assertEqual(t["n_structural_reciprocal_species_pairs_mixed_types"],50)
        self.assertEqual(t["n_reciprocal_stage_shift_candidates_mixed_types"],27)
        self.assertEqual(t["n_mixed_stage_shift_candidates_including_parasite"],27)
        self.assertEqual(t["n_mixed_stage_shift_candidates_nonparasite"],0)
        self.assertEqual(t["n_nonparasite_structural_reciprocal_pairs_mixed_types"],12)

    def test_predation_type_filter_changes_candidate(self):
        t=self.source["totals"]
        self.assertEqual(t["n_structural_reciprocal_species_pairs_predation_only"],12)
        self.assertEqual(t["n_reciprocal_stage_shift_candidates_predation_only"],0)
        self.assertEqual(t["n_nonparasite_structural_reciprocal_pairs"],12)
        self.assertEqual(t["n_nonparasite_stage_shift_candidates"],0)

    def test_explicit_parasitism_not_predation(self):
        n=[
            node(1,"Trematodus fakeus","Adult","Trematode"),
            node(2,"Trematodus fakeus","Cystacanth","Trematode"),
            node(3,"Avium fakensis","Adult","Bird")
        ]
        l=[link(1,3,"Macroparasitism"),link(3,2,"Trophic Transmission")]
        result,pairs,strict,extra=mod.build(l,n)
        self.assertEqual(result["n_structural_reciprocal_species_pairs_mixed_types"],1)
        self.assertEqual(result["n_reciprocal_stage_shift_candidates_mixed_types"],1)
        self.assertEqual(result["n_reciprocal_stage_shift_candidates_predation_only"],0)
        self.assertEqual(result["n_certified_direct_attack_stage_switches"],0)
        self.assertEqual(len(strict),0)

    def test_true_predation_only_may_change_stages_but_not_be_certified_from_blank_evidence(self):
        n=[
            node(1,"Anaxa examplea","larvae","Dragonfly"),
            node(2,"Anaxa examplea","adult","Dragonfly"),
            node(3,"Frogsus exampleus","larvae","Frog"),
            node(4,"Frogsus exampleus","adult","Frog")
        ]
        l=[link(1,3,"Predation"),link(4,2,"Predation")]
        totals,pairs,strict,_=mod.build(l,n)
        self.assertEqual(totals["n_reciprocal_stage_shift_candidates_predation_only"],1)
        self.assertEqual(totals["n_certified_direct_attack_stage_switches"],0)

    def test_genus_only_not_unique_species_pair(self):
        self.assertIsNone(mod.taxon({"Genus":"Anax","SpecificEpithet":"sp."}))
        self.assertIsNone(mod.taxon({"Genus":"","SpecificEpithet":"junius"}))

    def test_all_source_original_mixed_candidates_can_be_inspected(self):
        allc=self.source["mixed_interaction_type_reciprocity"]
        pred=self.source["predation_only_reciprocity"]
        self.assertEqual(len(allc),50)
        self.assertEqual(len(pred),12)
        self.assertTrue(all(x["includes_parasite_source_group_or_stage"] for x in allc if x["structural_stage_difference"]))
        self.assertFalse(any(x["structural_stage_difference"] for x in pred))

    def test_pinned_original_external_source(self):
        self.assertEqual(len(mod.COMMIT),40)
        self.assertEqual(mod.BLOBS["Otago_Data_Links.csv"],"d2c2765a8a798bbd72029c328302f095f97d095c")
        self.assertEqual(mod.BLOBS["Otago_Data_Nodes.csv"],"9303b47b997945cd37842df5fd23879fe864d114")

if __name__=="__main__":unittest.main()
