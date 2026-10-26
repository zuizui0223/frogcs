import unittest
import numpy as np
from rasterio.transform import from_origin
from naamp_remote_vegetation_context import circular_summary


class CircularSummaryTests(unittest.TestCase):
    def test_circle_excludes_corners_and_missing_is_not_zero(self):
        transform=from_origin(-.015,.015,.01,.01)
        data=np.array([[99,0,99],[0,255,0],[99,0,99]],dtype=np.uint8)
        r=circular_summary(data,transform,0,0,1200)
        self.assertEqual(r['total_cells'],5)
        self.assertEqual(r['valid_cells'],4)
        self.assertEqual(r['mean'],0)
        self.assertEqual(r['positive_fraction'],0)

    def test_all_missing_remains_missing(self):
        r=circular_summary(np.full((3,3),255,dtype=np.uint8),from_origin(-.015,.015,.01,.01),0,0,1200)
        self.assertIsNone(r['mean'])
        self.assertEqual(r['valid_cells'],0)

    def test_constant_field_has_zero_heterogeneity(self):
        r=circular_summary(np.full((3,3),40,dtype=np.uint8),from_origin(-.015,.015,.01,.01),0,0,2000)
        self.assertAlmostEqual(r['mean'],40)
        self.assertAlmostEqual(r['sd'],0)
        self.assertEqual(r['positive_fraction'],1)


if __name__=='__main__':unittest.main()
