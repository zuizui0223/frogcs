from __future__ import annotations
import csv
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from prepare_survey_site_calendar import build
from summarize_dswe_visits import summarize


def make_csv(p, cols, rows):
    with Path(p).open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)


class TestCalendarDSWE(unittest.TestCase):
    def test_outcome_blind_site_calendar_and_strictly_earlier_water_scenes(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            runs = [{"RunID": "R1", "State": "VA", "RouteNumber": "101", "SurveyDate": "06/10/2007", "UnifiedProtocol": "1"},
                    {"RunID": "R2", "State": "VA", "RouteNumber": "101", "SurveyDate": "06/10/2007", "UnifiedProtocol": "0"}]
            stops = [{"RunID": "R1", "SiteID": "1", "StopNumber": "1", "SkippedStop": "0"},
                     {"RunID": "R1", "SiteID": "2", "StopNumber": "2", "SkippedStop": "0"},
                     {"RunID": "R2", "SiteID": "1", "StopNumber": "1", "SkippedStop": "0"}]
            coords = [{"RouteNumber": "101", "SiteID": "1", "status": "accepted"},
                      {"RouteNumber": "101", "SiteID": "2", "status": "accepted"}]
            make_csv(root / "Runs.csv", runs[0].keys(), runs)
            make_csv(root / "Stops.csv", stops[0].keys(), stops)
            make_csv(root / "accepted.csv", coords[0].keys(), coords)
            visits, report = build(root / "Runs.csv", root / "Stops.csv", root / "accepted.csv")
            self.assertEqual(len(visits), 2)
            self.assertFalse(report["counts_csv_opened"])
            scenes = [
                {"RouteNumber": "101", "SiteID": "1", "scene_id": "past1", "acquisition_date": "2007-06-05", "radius_m": "500", "valid_pixel_n": "60", "water_pixel_n": "30"},
                {"RouteNumber": "101", "SiteID": "1", "scene_id": "past2", "acquisition_date": "2007-06-09", "radius_m": "500", "valid_pixel_n": "100", "water_pixel_n": "70"},
                {"RouteNumber": "101", "SiteID": "1", "scene_id": "same_day", "acquisition_date": "2007-06-10", "radius_m": "500", "valid_pixel_n": "100", "water_pixel_n": "100"},
                {"RouteNumber": "101", "SiteID": "1", "scene_id": "future", "acquisition_date": "2007-06-12", "radius_m": "500", "valid_pixel_n": "100", "water_pixel_n": "100"},
                {"RouteNumber": "101", "SiteID": "1", "scene_id": "other_radius", "acquisition_date": "2007-06-09", "radius_m": "100", "valid_pixel_n": "100", "water_pixel_n": "100"},
            ]
            out, rpt = summarize(visits, scenes)
            self.assertEqual(out[0]["qc_status"], "ok")
            self.assertEqual(out[0]["scene_n"], 2)
            self.assertEqual(out[0]["valid_pixel_n"], 160)
            self.assertEqual(out[0]["water_pixel_n"], 100)
            self.assertAlmostEqual(float(out[0]["water_fraction"]), 0.625, places=6)
            self.assertEqual(out[1]["qc_status"], "no_valid_scene")
            self.assertEqual(out[1]["water_fraction"], "")
            self.assertFalse(rpt["frog_outcomes_read"])
            with self.assertRaisesRegex(ValueError, "duplicate scene"):
                summarize(visits, scenes + [scenes[0]])
            with self.assertRaisesRegex(ValueError, "pixel counts"):
                summarize(visits, [{**scenes[0], "water_pixel_n": "100"}])


if __name__ == "__main__":
    unittest.main()
