#!/usr/bin/env python3
"""Small source-only WCS/WMS identity checks; no network, no frogs."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
import nlcd_c1v2_official_ogc_wcs_preflight_v0_1 as mod

def wcs(title="Annual NLCD Land Cover C1V2 year 2012"):
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<wcs:Capabilities xmlns:wcs="http://www.opengis.net/wcs/2.0">
  <ows:ServiceIdentification xmlns:ows="http://www.opengis.net/ows/2.0">
    <ows:Title>{title}</ows:Title></ows:ServiceIdentification>
  <wcs:Contents><wcs:CoverageSummary>
    <wcs:CoverageId>mrlc_2012_landcover</wcs:CoverageId>
  </wcs:CoverageSummary></wcs:Contents></wcs:Capabilities>""".encode()

class OGCSourceContractTests(unittest.TestCase):
    def test_version_and_year_required_for_positive_source_identity(self):
        actual=mod.inspect_capabilities(wcs(),"WCS")
        self.assertTrue(actual["original_identity_explicit_C1V2_in_OGC"])
        self.assertTrue(actual["year_2012_visible"])
        old=mod.inspect_capabilities(wcs("Annual NLCD C1V0 year 2012"),"WCS")
        self.assertFalse(old["original_identity_explicit_C1V2_in_OGC"])
        no_year=mod.inspect_capabilities(wcs("Annual NLCD C1V2"),"WCS")
        # CoverageId includes 2012 in this synthetic template.
        self.assertTrue(no_year["year_2012_visible"])

    def test_named_ogc_exception_is_not_source(self):
        data=b'<ows:ExceptionReport xmlns:ows="http://www.opengis.net/ows/2.0"/>'
        with self.assertRaisesRegex(ValueError,"OGC service reported"):
            mod.inspect_capabilities(data,"WCS")

    def test_html_fail_closed(self):
        with self.assertRaises(Exception):
            mod.inspect_capabilities(b"<html>200 OK, not a raster service</html>","WCS")

    def test_wrong_protocol_root_fail_closed(self):
        with self.assertRaisesRegex(ValueError,"not a WMS"):
            mod.inspect_capabilities(wcs(),"WMS")

    def test_official_domain_locked_and_no_cloud_payments(self):
        with self.assertRaisesRegex(ValueError,"outside official"):
            mod.read_capped("https://example.net/geoserver/wcs?x=1")
        for product,workspace in mod.SERVICES.items():
            u=mod.caps_url(workspace,"WCS","2.0.1")
            self.assertTrue(u.startswith("https://dmsdata.cr.usgs.gov/geoserver/"))
            self.assertIn("request=GetCapabilities",u)

if __name__=="__main__":unittest.main()
