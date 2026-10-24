"""Synthetic JRC GeoTIFF tests: no-data is not dry; water denominator uses observed pixels."""
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np
import rasterio
from rasterio.transform import from_origin

S=Path(__file__).resolve().parent
sys.path.insert(0,str(S.parent/"scripts"))
from pilot_jrc_prior_month import water_fraction

class JRCWaterPixelSemantics(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.path=Path(self.temp.name)/"jrc_monthly.tif"
        self.lat,self.lon=39.4,-79.3
        self.values=np.ones((200,200),dtype=np.uint8)
        self.transform=from_origin(self.lon-.025,self.lat+.025,.00025,.00025)

    def tearDown(self):
        self.temp.cleanup()

    def read(self):
        with rasterio.open(self.path,"w",driver="GTiff",height=200,width=200,
                           count=1,dtype="uint8",crs="EPSG:4326",transform=self.transform) as out:
            out.write(self.values,1)
        with rasterio.open(self.path) as src:
            return water_fraction(src,self.lat,self.lon,500)

    def test_all_zero_is_missing_not_dry(self):
        self.values.fill(0)
        r=self.read()
        self.assertEqual(r["n_valid_pixels"],0)
        self.assertEqual(r["n_water_pixels"],0)
        self.assertIsNone(r["water_fraction_among_observed"])
        self.assertFalse(r["coverage_ge_50pct"])

    def test_all_land_is_observed_nonwater(self):
        self.values.fill(1)
        r=self.read()
        self.assertGreater(r["n_valid_pixels"],0)
        self.assertEqual(r["n_water_pixels"],0)
        self.assertEqual(r["water_fraction_among_observed"],0)
        self.assertTrue(r["coverage_ge_80pct"])

    def test_all_water_is_observed_water(self):
        self.values.fill(2)
        r=self.read()
        self.assertEqual(r["n_water_pixels"],r["n_valid_pixels"])
        self.assertEqual(r["water_fraction_among_observed"],1)
        self.assertTrue(r["coverage_ge_80pct"])

    def test_missing_pixels_excluded_from_denominator(self):
        self.values.fill(1)
        self.values[:,:100]=0
        self.values[:,100:]=2
        r=self.read()
        self.assertGreater(r["n_no_observation"],0)
        self.assertGreater(r["n_water_pixels"],0)
        self.assertEqual(r["water_fraction_among_observed"],1)
        self.assertLess(r["valid_fraction"],1)

if __name__=="__main__": unittest.main()
