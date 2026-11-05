"""Source-free regression guards for G3 egg-stage reporting preflight."""
from __future__ import annotations
import unittest

from g3_gbif_egg_stage_source_preflight_20261105 import (
    EGG_LABELS, explicit_egg, facet_params, gate,
    raw_facet_counts, source_taxa
)


class G3EggStageSourceGateTests(unittest.TestCase):
    def test_darwin_core_stage_labels_not_adult_first_sightings(self):
        self.assertTrue(explicit_egg("Egg"))
        self.assertTrue(explicit_egg("  eGgS  "))
        self.assertTrue(explicit_egg("ovum"))
        self.assertFalse(explicit_egg("Adult"))
        self.assertFalse(explicit_egg("breeding adult"))
        self.assertFalse(explicit_egg("Larva"))
        self.assertFalse(explicit_egg("embryo"))
        self.assertFalse(explicit_egg("early March"))
        self.assertFalse(explicit_egg("eggs (?)"))

    def test_source_query_excludes_partial_2026_and_has_explicit_US_filters(self):
        q=facet_params(2431951)
        self.assertEqual(q["year"],"2010,2025")
        self.assertEqual(q["country"],"US")
        self.assertEqual(q["hasGeospatialIssue"],"false")
        self.assertEqual(q["hasCoordinate"],"true")
        self.assertEqual(q["occurrenceStatus"],"PRESENT")
        self.assertEqual(q["facet"],"lifeStage")
        self.assertEqual(q["limit"],0)

    def test_gbif_facet_normalization_keeps_ambiguous_labels_visible(self):
        r={"status":"SUCCESS","facets":[
            {"field":"LIFE_STAGE","counts":[
                {"name":"Egg","count":25},
                {"name":"larva","count":40},
                {"name":"adult","count":19},
                {"name":"egg mass?","count":11}
            ]}
        ]}
        values=raw_facet_counts(r,"lifeStage")
        self.assertEqual(len(values),4)
        self.assertEqual(sum(n for label,n in values if explicit_egg(label)),25)

    def test_unavailable_facets_never_counted_as_biological_zero(self):
        r=[dict(role="frog_original_15",species=f"frog{i}",
                status="SUCCESS",explicit_egg_stage_reports=100) for i in range(15)]
        r+=[dict(role="pond_caudata_original_5",species=f"pond{i}",
                 status="SUCCESS",explicit_egg_stage_reports=100) for i in range(5)]
        r+=[dict(role="nonpond_caudata_control_2",species=f"control{i}",
                 status="SUCCESS",explicit_egg_stage_reports=0) for i in range(2)]
        x=gate(r)
        self.assertTrue(x["next_phase_response_blind_date_effort_inventory_allowed"])
        self.assertFalse(x["field_test_allowed"])
        r[0]["status"]="API_ERROR_UNVERIFIED"
        x=gate(r)
        self.assertEqual(x["status"],"UNKNOWN_API_OR_SOURCE_INCOMPLETE")
        self.assertFalse(x["field_test_allowed"])

    def test_minimum_real_breeding_labels_gate_is_fail_closed(self):
        r=[dict(role="frog_original_15",species=f"frog{i}",
                status="SUCCESS",explicit_egg_stage_reports=50 if i<4 else 0)
           for i in range(15)]
        r+=[dict(role="pond_caudata_original_5",species=f"pond{i}",
                status="SUCCESS",explicit_egg_stage_reports=50 if i<2 else 0)
            for i in range(5)]
        r+=[dict(role="nonpond_caudata_control_2",species=f"control{i}",
                status="SUCCESS",explicit_egg_stage_reports=0) for i in range(2)]
        x=gate(r)
        self.assertEqual(x["status"],"G0_NOT_QUALIFIED_INSUFFICIENT_EXPLICIT_EGG_STAGE")
        self.assertFalse(x["field_test_allowed"])


if __name__=="__main__":
    unittest.main()
