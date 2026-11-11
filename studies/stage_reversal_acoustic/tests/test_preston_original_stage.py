"""Original food-web evidence tiers: mocked link data and frozen original receipt."""
import importlib.util
import json
import sys
import unittest
from pathlib import Path
P=Path(__file__).resolve().parents[1]/"macro"
MODULE=P/"audit_preston_original_stage_edges.py"
spec=importlib.util.spec_from_file_location("preston_stage",MODULE)
mod=importlib.util.module_from_spec(spec)
sys.modules[spec.name]=mod
spec.loader.exec_module(mod)

def node(i,species,stage):
    genus,specific=species.split(" ")
    return {"NodeID":str(i),"Genus":genus,"SpecificEpithet":specific,"Stage":stage}
def link(pred,prey,source="observed",kind="predation"):
    return {"ConsumerNodeID":str(pred),"ResourceNodeID":str(prey),
            "LinkType":kind,"LinkEvidence":source,"LinkEvidenceNotes":""}

class SourceFoodWeb(unittest.TestCase):
    def setUp(self):
        self.a=node(1,"Anaxyrus boreas","adult")
        self.b=node(2,"Anaxyrus boreas","larvae")
        self.c=node(3,"Anax junius","adult")
        self.d=node(4,"Anax junius","larvae")
        self.nodes=[self.a,self.b,self.c,self.d]
        
    def test_original_evidence_counts_frozen(self):
        obj=json.loads((P/"results"/"PRESTON2012_ORIGINAL_STAGE_RECIPROCITY_EVIDENCE_TIER_V0_1.json").read_text())
        t=obj["totals"]
        self.assertEqual(t["n_all_link_rows"],1905)
        self.assertEqual(t["n_predation_link_rows"],1000)
        self.assertEqual(t["predation_link_evidence"],{"modelled":910,"inferred":40,"observed":50})
        self.assertEqual(t["n_named_species_pairs_with_links_in_both_directions"],11)
        self.assertEqual(t["n_reciprocal_pairs_with_both_source_class_observed_and_stage_change"],0)

    def test_any_modelled_reverse_is_not_direct(self):
        t,pairs=mod.build([link(1,4,"modelled"),link(4,2,"observed")],self.nodes)
        self.assertEqual(t["n_named_species_pairs_with_links_in_both_directions"],1)
        self.assertEqual(t["n_reciprocal_species_pairs_both_directions_source_class_observed"],0)
        self.assertEqual(t["n_reciprocal_pairs_with_both_source_class_observed_and_stage_change"],0)

    def test_both_observed_but_only_larvae_is_not_ontogenetic(self):
        t,pairs=mod.build([link(2,4),link(4,2)],self.nodes)
        self.assertEqual(t["n_reciprocal_species_pairs_both_directions_source_class_observed"],1)
        self.assertEqual(t["n_reciprocal_pairs_with_both_source_class_observed_and_stage_change"],0)

    def test_opposed_direct_stages_would_qualify(self):
        t,pairs=mod.build([link(1,4),link(4,2)],self.nodes)
        self.assertEqual(t["n_reciprocal_pairs_with_both_source_class_observed_and_stage_change"],1)

    def test_self_cannibalism_excluded_from_species_reciprocal(self):
        t,pairs=mod.build([link(1,2),link(2,1)],self.nodes)
        self.assertEqual(t["n_unique_species_pairs_any_one_direction"],0)

    def test_indexed_inferred_not_observed(self):
        t,_=mod.build([link(1,4,"inferred"),link(4,2)],self.nodes)
        self.assertEqual(t["n_reciprocal_species_pairs_both_directions_source_class_observed"],0)

    def test_no_silent_family_level_resolution(self):
        self.assertIsNone(mod.label({"NodeID":"5","Genus":"Anax","SpecificEpithet":"","Stage":"adult"}))

    def test_original_repo_stable_sha(self):
        self.assertEqual(len(mod.COMMIT),40)
        self.assertEqual(mod.SOURCE_SHA["Quick_Pond_Links.csv"],"98c45c7a2081976f0a4c31db3c6646686b8277fa")
        self.assertEqual(mod.SOURCE_SHA["Quick_Pond_Nodes.csv"],"201dc6ace08a26d4d07825f6bae6a295bd735adc")

if __name__=="__main__":
    unittest.main()
