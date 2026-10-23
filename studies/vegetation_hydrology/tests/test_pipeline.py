from __future__ import annotations
import csv
import json
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np
import rasterio
from rasterio.transform import from_origin
from rasterio.warp import transform as transform_coords

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
from audit_site_coordinates import audit, write_output
from extract_nlcd_buffers import extract_point, run


def write_csv(path, fields, rows):
    with Path(path).open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


class TestCoordinateQC(unittest.TestCase):
    def test_missing_and_implausible_locations_are_held(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "coords.csv"
            write_csv(p, ("RouteNumber", "SiteID", "lat", "lon"), [
                {"RouteNumber": "101", "SiteID": "1", "lat": "40", "lon": "-80"},
                {"RouteNumber": "101", "SiteID": "2", "lat": "40.0075", "lon": "-80"},
                {"RouteNumber": "101", "SiteID": "3", "lat": "40", "lon": "83.302"},
                {"RouteNumber": "202", "SiteID": "1", "lat": "38", "lon": "-77"},
                {"RouteNumber": "202", "SiteID": "2", "lat": "39", "lon": "-77"},
                {"RouteNumber": "303", "SiteID": "1", "lat": "38", "lon": "-77"},
                {"RouteNumber": "303", "SiteID": "2", "lat": "38.00001", "lon": "-77"},
                {"RouteNumber": "404", "SiteID": "1", "lat": "39", "lon": "-80"},
                {"RouteNumber": "404", "SiteID": "1", "lat": "39.3", "lon": "-80"},
            ])
            r = audit(p)
            assert len(r["accepted"]) == 2, r
            held = {(x["RouteNumber"], x["SiteID"]): x for x in r["held"]}
            self.assertIn("outside_conus_bounds", held[("101", "3")]["reasons"])
            self.assertIn("route_span_gt_quarantine_km", held[("202", "1")]["reasons"])
            self.assertIn("distinct_sites_nearly_coincident", held[("303", "1")]["reasons"])
            self.assertIn("conflicting_duplicate_coordinates", held[("404", "1")]["reasons"])
            with self.assertRaisesRegex(ValueError, "SHA256 mismatch"):
                audit(p, expected_sha="0" * 64)
            out = Path(d) / "out"
            write_output(r, out)
            with (out / "accepted_coordinates.csv").open() as f:
                self.assertEqual(len(list(csv.DictReader(f))), 2)
            report = json.loads((out / "coordinate_qc_report.json").read_text())
            self.assertEqual(report["outcome_records_read"], False)
            self.assertEqual(report["input_rows"], 9)

    def test_valid_duplicates_are_collapsed(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "coords.csv"
            row = {"RouteNumber": "101", "SiteID": "1", "lat": "40", "lon": "-80"}
            write_csv(p, row.keys(), [row, row])
            r = audit(p)
            self.assertEqual(len(r["accepted"]), 1)
            self.assertEqual(r["report"]["input_rows"], 2)


class TestNLCD(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        lat, lon = 40.0, -80.0
        x, y = transform_coords("EPSG:4326", "EPSG:5070", [lon], [lat])
        self.lat, self.lon = lat, lon
        self.tiff = self.root / "annual_2001.tif"
        data = np.full((120, 120), 41, dtype=np.uint8)
        data[:, 60:] = 90
        with rasterio.open(self.tiff, "w", driver="GTiff", width=120, height=120,
                           count=1, dtype="uint8", crs="EPSG:5070", nodata=0,
                           transform=from_origin(x[0] - 60 * 30, y[0] + 60 * 30, 30, 30)) as ds:
            ds.write(data, 1)

    def tearDown(self):
        self.tmp.cleanup()

    def test_landcover_fraction_and_temporal_layout(self):
        with rasterio.open(self.tiff) as ds:
            r = extract_point(ds, self.lat, self.lon, radius_m=500)
        self.assertEqual(r["qc_status"], "ok")
        self.assertGreater(r["n_valid_pixels"], 100)
        self.assertAlmostEqual(r["frac_forest"] + r["frac_woody_wetland"], 1, places=5)
        self.assertAlmostEqual(r["frac_forest"], 0.5, delta=0.1)
        coords = self.root / "accepted.csv"
        write_csv(coords, ["RouteNumber", "SiteID", "lat", "lon", "status"], [
            {"RouteNumber": "101", "SiteID": "1", "lat": self.lat, "lon": self.lon, "status": "accepted"}
        ])
        result = run(coords, str(self.root / "annual_{year}.tif"), [2001], [100, 500], self.root / "panel.csv")
        self.assertEqual(result["rows"], 2)
        with (self.root / "panel.csv").open() as f:
            records = list(csv.DictReader(f))
        self.assertEqual([int(x["radius_m"]) for x in records], [100, 500])
        self.assertTrue(all(x["qc_status"] == "ok" for x in records))
        with self.assertRaisesRegex(FileNotFoundError, "no NLCD raster"):
            run(coords, str(self.root / "annual_{year}.tif"), [2002], [500], self.root / "missing.csv")

    def test_nodata_is_not_classified_as_habitat(self):
        with rasterio.open(self.tiff, "r+") as ds:
            data = ds.read(1)
            data[50:70, 50:70] = 0
            ds.write(data, 1)
        with rasterio.open(self.tiff) as ds:
            r = extract_point(ds, self.lat, self.lon, radius_m=100, min_coverage=0.8)
        self.assertEqual(r["qc_status"], "low_coverage")
        self.assertEqual(r["frac_forest"], "")


if __name__ == "__main__":
    unittest.main()

class TestSparseNLCD(unittest.TestCase):
    def test_sparse_calendar_prevents_all_year_and_unobserved_site_work(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            source=TestNLCD()
            source.setUp()
            try:
                coords=root/'sites.csv'
                write_csv(coords,['RouteNumber','SiteID','lat','lon','status'],[
                    {'RouteNumber':'101','SiteID':'1','lat':source.lat,'lon':source.lon,'status':'accepted'},
                    {'RouteNumber':'101','SiteID':'2','lat':source.lat+.02,'lon':source.lon+.02,'status':'accepted'}])
                calendar=root/'calendar.csv'
                write_csv(calendar,['RouteNumber','SiteID','SurveyYear'],[
                    {'RouteNumber':'101','SiteID':'1','SurveyYear':'2001'},
                    {'RouteNumber':'101','SiteID':'1','SurveyYear':'2001'}])
                template=str(source.root/'annual_{year}.tif')
                report=run(coords,template,[2001,2002],[100,500],root/'selected.csv',site_calendar_csv=calendar)
                self.assertEqual((report['rows'],report['site_years_extracted'],report['full_site_year_grid']),(2,1,4))
                self.assertTrue(report['sparse_calendar_applied'])
                with (root/'selected.csv').open() as f:
                    self.assertEqual({r['SiteID'] for r in csv.DictReader(f)},{'1'})
            finally: source.tearDown()

    def test_outcome_columns_in_calendar_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            coords=root/'sites.csv'
            write_csv(coords,['RouteNumber','SiteID','lat','lon','status'],[
                {'RouteNumber':'101','SiteID':'1','lat':40,'lon':-80,'status':'accepted'}])
            calendar=root/'calendar.csv'
            write_csv(calendar,['RouteNumber','SiteID','SurveyYear','CallingIndex'],[
                {'RouteNumber':'101','SiteID':'1','SurveyYear':'2001','CallingIndex':'3'}])
            with self.assertRaisesRegex(ValueError,'outcome-bearing'):
                run(coords,str(root/'annual_{year}.tif'),[2001],[100],root/'output.csv',site_calendar_csv=calendar)
