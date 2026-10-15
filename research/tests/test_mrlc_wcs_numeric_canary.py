#!/usr/bin/env python3
"""Purely synthetic test for bounded USGS WCS pixel inspection."""
import sys
import unittest
from pathlib import Path

import numpy as np
from rasterio.io import MemoryFile
from rasterio.transform import from_origin

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
import mrlc_wcs_numeric_canary_v0_1 as canary

class CanaryTests(unittest.TestCase):
    def test_version_and_year_fixed_and_technical_only(self):
        for work in canary.WORKSPACES.values():
            url=canary.url_for_workspace(work)
            self.assertIn("REQUEST=GetCoverage",url)
            self.assertIn("2012-01-01",url)
            self.assertIn("SUBSET=X%28",url)
            self.assertIn("SUBSET=Y%28",url)
            self.assertIn("image%2Ftiff",url)
            self.assertIn("COVERAGEID=",url)
            self.assertIn("VERSION=2.0.1",url)
        self.assertEqual(canary.bbox5070(),canary.bbox5070())

    def test_numeric_tiff_values_extract(self):
        pixels=np.full((64,64),71,dtype=np.uint8)
        pixels[0:40,0:30]=41
        with MemoryFile() as m:
            with m.open(driver="GTiff",height=64,width=64,count=1,
                        dtype="uint8",crs="EPSG:5070",
                        transform=from_origin(-100000,100000,30,30),
                        nodata=255) as ds:
                ds.write(pixels,1)
            raw=m.read()
        r=canary.inspect_numeric_raster(raw,"image/tiff")
        self.assertEqual(r["shape"],[64,64])
        self.assertEqual(r["unique_values"]["41"],1200)
        self.assertEqual(r["valid_pixels"],4096)

    def test_html_not_permitted_as_geotiff(self):
        with self.assertRaisesRegex(ValueError,"non-TIFF"):
            canary.inspect_numeric_raster(b"<html>Too Many Requests</html>","image/tiff")

    def test_unknown_host_rejected_without_network(self):
        with self.assertRaisesRegex(ValueError,"nonofficial"):
            canary.bounded_get("https://example.org/?request=GetCoverage")

if __name__=="__main__":unittest.main()
