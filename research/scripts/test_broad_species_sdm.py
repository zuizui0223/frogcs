import unittest
import numpy as np
from broad_species_sdm import thin, fold, evaluate, in_domain
from shapely.geometry import box


class SDMTests(unittest.TestCase):
    def test_records_and_background_use_same_domain_mask(self):
        rows = [dict(lon=-100,lat=40), dict(lon=-100,lat=55)]
        self.assertEqual(in_domain(box(-125,24,-66,50), rows).tolist(), [True,False])

    def test_duplicate_cell_does_not_increase_sample_size(self):
        rows = [dict(id='20', lon=-80.01, lat=35.01),
                dict(id='3', lon=-80.02, lat=35.02),
                dict(id='4', lon=-82.01, lat=35.01)]
        kept = thin(rows)
        self.assertEqual({r['id'] for r in kept}, {'3','4'})
        self.assertEqual(kept, thin(list(reversed(rows))))

    def test_whole_block_stays_together(self):
        for size in (2,4):
            self.assertEqual(fold(-79.9,32.1,size), fold(-78.1,33.9,size))

    def test_missing_heldout_positive_is_not_success(self):
        x = np.arange(360).reshape(60,6)
        y = np.r_[np.ones(30), np.zeros(30)]
        rows = [dict(lon=-80,lat=36)]*60
        result = evaluate(x,y,rows,2)
        self.assertTrue(all(r['auc'] is None for r in result))


if __name__ == '__main__':
    unittest.main()
