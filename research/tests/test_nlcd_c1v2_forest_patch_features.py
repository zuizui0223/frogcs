#!/usr/bin/env python3
"""Forest patch graph tests with synthetic categorical C1V2-style pixels only."""
import sys,unittest
from pathlib import Path
import numpy as np
from rasterio.transform import Affine

P=Path(__file__).resolve().parents[1]/"scripts"
sys.path.insert(0,str(P))
import nlcd_c1v2_forest_patch_features_v0_1 as forest

class PatchTests(unittest.TestCase):
    def setUp(self):
        self.tr=Affine.translation(0,9600)*Affine.scale(30,-30)
        self.cover=np.full((320,320),71,dtype=np.uint8)
        self.conf=np.full((320,320),80,dtype=np.uint8)
        self.stops=[(1800+600*j,4800) for j in range(10)]

    def test_all_open_ground_despite_nearby_stops_not_connected_forest(self):
        r=forest.derive_features(self.cover,self.conf,self.tr,self.stops)
        self.assertEqual(r["connected_site_pair_count"],0)
        self.assertEqual(r["forest_patch_count_in_hullplus1km"],0)
        self.assertEqual(len(r["forest_300m_fraction"]),10)
        self.assertFalse(r["proximity_derived"])

    def test_one_contiguous_30m_forest_patch_links_nonoverlapping_stops(self):
        self.cover[159:161,60:241]=41
        r=forest.derive_features(self.cover,self.conf,self.tr,self.stops)
        self.assertEqual(r["connected_site_pair_count"],45)
        self.assertEqual(r["forest_patch_count_in_hullplus1km"],1)
        self.assertTrue(all(x>0 for x in r["forest_300m_fraction"]))
        self.assertTrue(all(x<1 for x in r["forest_300m_fraction"]))

    def test_cutting_corridor_breaks_between_distant_stops(self):
        self.cover[159:161,60:241]=42
        r1=forest.derive_features(self.cover,self.conf,self.tr,self.stops)
        self.cover[159:161,151:155]=71
        r2=forest.derive_features(self.cover,self.conf,self.tr,self.stops)
        self.assertEqual(r1["connected_site_pair_count"],45)
        self.assertLess(r2["connected_site_pair_count"],45)
        self.assertGreaterEqual(r2["forest_patch_count_in_hullplus1km"],2)

    def test_woody_wetland_and_grassland_not_counted_as_primary_forest(self):
        self.cover[159:161,60:241]=90
        r=forest.derive_features(self.cover,self.conf,self.tr,self.stops)
        self.assertEqual(r["connected_site_pair_count"],0)
        self.assertEqual(sum(r["forest_300m_fraction"]),0)

    def test_confidence_is_required_but_not_dichotomized_by_value(self):
        self.cover[159:161,60:241]=43
        lo=forest.derive_features(self.cover,np.full((320,320),15,dtype=np.uint8),self.tr,self.stops)
        hi=forest.derive_features(self.cover,self.conf,self.tr,self.stops)
        self.assertEqual(lo["connected_site_pair_count"],hi["connected_site_pair_count"])
        self.assertLess(lo["class_confidence_median"][0],hi["class_confidence_median"][0])
        with self.assertRaisesRegex(ValueError,"confidence"):
            forest.derive_features(self.cover,np.full((320,320),255,dtype=np.uint8),self.tr,self.stops)

    def test_misaligned_or_truncated_geography_fails(self):
        with self.assertRaisesRegex(ValueError,"matched"):
            forest.derive_features(self.cover,self.conf[:10],self.tr,self.stops)
        with self.assertRaisesRegex(ValueError,"truncated"):
            forest.derive_features(self.cover,self.conf,self.tr,
                                   [(float(x-900),float(y)) for x,y in self.stops])

    def test_resolution_and_duplicate_stops_fail(self):
        with self.assertRaisesRegex(ValueError,"30m"):
            forest.derive_features(self.cover,self.conf,
                                   Affine.translation(0,9600)*Affine.scale(60,-60),
                                   self.stops)
        with self.assertRaisesRegex(ValueError,"ten unique"):
            forest.derive_features(self.cover,self.conf,self.tr,[self.stops[0]]*10)

    def test_class_missingness_excluded_not_interpreted_as_no_forest(self):
        self.cover[:,:]=0
        with self.assertRaisesRegex(ValueError,"categorical"):
            forest.derive_features(self.cover,self.conf,self.tr,self.stops)

if __name__=="__main__":
    unittest.main()
