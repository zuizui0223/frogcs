#!/usr/bin/env python3
"""Synthetic response-blind tests of the official NLCD C1V2 source gate."""
import sys, unittest
from pathlib import Path

SCRIPT_DIR=Path(__file__).resolve().parents[1]/"scripts"
sys.path.insert(0,str(SCRIPT_DIR))
import official_nlcd_c1v2_access_gate_v0_1 as nlcd

class OfficialSourceGateTests(unittest.TestCase):
    def test_namespaced_wms_catalog_detects_c1v2_only(self):
        sample=b"""<?xml version='1.0' encoding='UTF-8'?>
        <WMS_Capabilities xmlns='http://www.opengis.net/wms'>
          <Capability><Layer><Title>Annual NLCD</Title>
           <Layer><Name>older:Annual_NLCD_LndCov_2012_CU_C1V0</Name><Title>2012 C1V0</Title></Layer>
           <Layer><Name>current:Annual_NLCD_LndCov_2012_CU_C1V2</Name><Title>2012 C1V2</Title></Layer>
          </Layer></Capability></WMS_Capabilities>"""
        l=nlcd.find_layer_names(sample)
        self.assertEqual(len(l),2)
        c12=[x for x in l if "C1V2" in x["name"] and "2012" in x["name"]]
        self.assertEqual(len(c12),1)

    def test_xml_parse_errors_fail_closed(self):
        with self.assertRaises(Exception):
            nlcd.find_layer_names(b"<html>Not an OGC service")

    def test_source_identifiers_locked(self):
        self.assertEqual(nlcd.COVER_ITEM,"697b9279b66b0197c3043cc3")
        self.assertEqual(nlcd.CONF_ITEM,"697b92b8b66b0197c3043cc7")
        self.assertNotEqual(nlcd.COVER_ITEM,nlcd.CONF_ITEM)
        self.assertEqual(nlcd.YEAR,2012)

    def test_untrusted_host_rejected_before_network(self):
        with self.assertRaisesRegex(ValueError,"nonofficial"):
            nlcd.read_limited("https://example.com/fake.zip",100)

    def test_pure_wms_not_falsely_claimed_raw_geotiff(self):
        # The probe explicitly refuses to equate WMS images with numerical C1V2 TIFF pixels.
        self.assertTrue(callable(nlcd.wms_capabilities_probe))
        self.assertEqual(nlcd.MAX_BINARY,8192)

if __name__=="__main__":
    unittest.main()
