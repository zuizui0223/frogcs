#!/usr/bin/env python3
"""Offline, response-blind source and geometry regression tests."""
import hashlib
import importlib.util
import math
from pathlib import Path
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "naamp_terrestrial_geometry_preflight_v1.py"
spec = importlib.util.spec_from_file_location("landscape_preflight", SCRIPT)
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)

def fixture_route(n=10, route="100101", delta_lat=0.0072, origin_lat=40.0):
    return [
        {"RouteNumber": route, "SiteID": str(100 + j),
         "lat": str(origin_lat + j * delta_lat), "lon": "-82.0"}
        for j in range(n)
    ]

class OutcomeBlindGeometryTests(unittest.TestCase):
    def test_exact_ten_route_and_300m_separation(self):
        r = audit.summarize(fixture_route())
        self.assertEqual(r["summary"]["legacy_8plus_geometry_pass"], 1)
        self.assertEqual(r["summary"]["complete_10_siteid_source_pass"], 1)
        item = r["route_records"][0]
        self.assertEqual(item["buffer_300m_overlap_pairs"], 0)
        self.assertGreater(item["buffer_1km_overlap_pairs"], 0)
        self.assertEqual(item["buffer_1km_overlap_components"], 1)
        self.assertFalse(r["boundary"]["frog_calling_records_read"])
        self.assertFalse(r["boundary"]["forest_patches_or_connectivity_measured"])

    def test_eight_or_nine_sites_pass_legacy_only(self):
        for n in (8, 9):
            with self.subTest(n=n):
                r = audit.summarize(fixture_route(n=n))
                self.assertEqual(r["summary"]["legacy_8plus_geometry_pass"], 1)
                self.assertEqual(r["summary"]["complete_10_siteid_source_pass"], 0)

    def test_known_gross_longitude_error_excluded(self):
        points = fixture_route()
        points[5]["lon"] = "+83.302"
        r = audit.summarize(points)
        self.assertEqual(r["summary"]["complete_10_siteid_source_pass"], 0)
        self.assertIn("outside_conus_bounds", r["route_records"][0]["issues"])

    def test_siteid_conflict_fails_closed(self):
        points = fixture_route()
        changed = dict(points[0])
        changed["lat"] = "41"
        points.append(changed)
        r = audit.summarize(points)
        self.assertEqual(r["summary"]["complete_10_siteid_source_pass"], 0)
        self.assertIn("coordinate_conflict", r["route_records"][0]["issues"])

    def test_no_sham_forest_connectivity_and_synthetic_disconnection(self):
        points = fixture_route(n=5, delta_lat=0.0020)
        points += fixture_route(n=5, delta_lat=0.0020, origin_lat=41.0)[0:5]
        for j, item in enumerate(points):
            item["SiteID"] = str(100 + j)
        r = audit.summarize(points)
        # Route is invalid (about 111 km across) so there is no misleading graph readout.
        self.assertEqual(r["summary"]["complete_10_siteid_source_pass"], 0)
        self.assertIn("span_gt_30km", r["route_records"][0]["issues"])
        self.assertIsNone(r["route_records"][0]["buffer_1km_overlap_components"])

    def test_pinned_source_sha_validation(self):
        with self.assertRaises(ValueError):
            audit.validate_sha(b"fake-coordinate-table")

    def test_incomplete_source_fails_size_gate(self):
        with self.assertRaisesRegex(ValueError, "unexpectedly changed"):
            audit.summarize(fixture_route(), enforce_source_size=True)

    def test_buffer_threshold_is_not_patch_connectivity(self):
        self.assertLess(audit.km_between((40, -82), (40.0072, -82)), 2)
        self.assertGreater(audit.km_between((40, -82), (40.0072, -82)), 0.6)
        self.assertEqual(audit.components(4, [(0, 1), (2, 3)]), 2)

if __name__ == "__main__":
    unittest.main()
