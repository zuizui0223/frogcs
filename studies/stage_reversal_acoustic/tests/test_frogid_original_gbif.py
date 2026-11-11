"""Source-grain and privacy-preserving aggregation tests; all inputs are synthetic."""
import importlib.util
import sys
import unittest
from pathlib import Path
FILE=Path(__file__).resolve().parents[1]/"src"/"reproduce_gbif_frogid_coarse.py"
spec=importlib.util.spec_from_file_location("frogid_gbif_source_repro",FILE)
mod=importlib.util.module_from_spec(spec)
sys.modules[spec.name]=mod
spec.loader.exec_module(mod)


def row(day,event,taxon=123):
    return {"datasetKey":mod.DATASET,"eventDate":day,"eventID":event,"acceptedTaxonKey":taxon}


class FrogIDOriginalSourceTests(unittest.TestCase):
    def test_source_window_exactly_frozen(self):
        self.assertEqual(mod.DATES,"2018-09-04,2019-04-09")
        self.assertEqual(mod.FOCAL_TAXON_KEY,10595763)

    def test_week_alignment_around_year_boundary(self):
        self.assertEqual(mod.week_start("2018-10-18"),"2018-10-15")
        self.assertEqual(mod.week_start("2019-01-01"),"2018-12-31")

    def test_recording_event_ids_dedup_across_species(self):
        x=mod.aggregate([row("2018-10-18","X",mod.FOCAL_TAXON_KEY),
                         row("2018-10-18","X",39),row("2018-10-19","Y",13)])
        a=next(k for k in x if k["week_start"]=="2018-10-15")
        self.assertEqual(a["species_rows"],3)
        self.assertEqual(a["unique_recording_events"],2)
        self.assertEqual(a["focal_positive_recording_events"],1)

    def test_unlinked_records_not_in_recording_denominator(self):
        x=mod.aggregate([row("2018-11-01",None),row("2018-11-01","W")])
        a=next(k for k in x if k["week_start"]=="2018-10-29")
        self.assertEqual(a["species_rows"],2)
        self.assertEqual(a["records_with_event_id"],1)
        self.assertEqual(a["unique_recording_events"],1)

    def test_unlinked_focal_record_fails(self):
        with self.assertRaisesRegex(ValueError,"eventID absent"):
            mod.aggregate([row("2018-11-01",None,mod.FOCAL_TAXON_KEY)])

    def test_calendar_outside_frozen_gate_fails(self):
        with self.assertRaisesRegex(ValueError,"outside frozen window"):
            mod.aggregate([row("2019-08-19","P")])

    def test_source_version_drift_is_explicit(self):
        observed=mod.aggregate([row("2018-10-18","A",mod.FOCAL_TAXON_KEY)])
        expected={"weekly_source_aggregate":[{"week_start":a["week_start"],"species_rows":0,
             "records_with_event_id":0,"unique_recording_events":0,"focal_positive_recording_events":0}
               for a in observed]}
        result=mod.validate(observed,expected)
        self.assertEqual(result["status"],"SOURCE_VERSION_DRIFT")
        self.assertFalse(result["matched_frozen_2026_10_25_readback"])


if __name__=="__main__":unittest.main()
