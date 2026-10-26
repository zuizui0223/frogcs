import unittest
import numpy as np
from rasterio.transform import from_origin,Affine
from naamp_prior_water_context import tile_keys,circle_sums


class PriorWaterTests(unittest.TestCase):
    def test_circle_crossing_tile_boundaries_requests_both_axes(self):
        self.assertEqual(set(tile_keys(-80,40)),{(40,-90),(40,-80),(50,-90),(50,-80)})
        self.assertEqual(tile_keys(-75,35),[(40,-80)])

    def test_mosaic_sums_equal_unsplit_raster(self):
        data=np.arange(16,dtype=np.uint8).reshape(4,4)
        transform=from_origin(-.02,.02,.01,.01)
        full=circle_sums(data,transform,0,0,3000)
        left=circle_sums(data[:,:2],transform,0,0,3000)
        right=circle_sums(data[:,2:],transform*Affine.translation(2,0),0,0,3000)
        for key in full:self.assertAlmostEqual(full[key],left[key]+right[key])

    def test_missing_and_invalid_are_distinct_from_dry(self):
        data=np.array([[0,100],[255,150]],dtype=np.uint8)
        r=circle_sums(data,from_origin(-.01,.01,.01,.01),0,0,3000)
        self.assertEqual(r['total_cells'],4)
        self.assertEqual(r['valid_cells'],2)
        self.assertEqual(r['unknown_codes'],1)
        self.assertAlmostEqual(r['water_weight']/r['valid_weight'],.5)
        self.assertAlmostEqual(r['water_value_sum']/r['water_weight'],100)


if __name__=='__main__':unittest.main()
