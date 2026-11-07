"""G16 paired geographic-block audit helper guards."""
import unittest

import numpy as np
import pandas as pd

from g16_original_SDM_background_reversal import paired_bootstrap, leave_one_out, BLOCKS, BOOT, SEED

class TestG16GeographicPairing(unittest.TestCase):
    def fixture(self):
        return pd.DataFrame(dict(
            spatial_block=[f"block_{i:02d}" for i in range(BLOCKS)],
            n_sites=np.full(BLOCKS,10,int),
            n_completed=np.full(BLOCKS,100,int),
            uniform_gain_sum=np.full(BLOCKS,4.),
            target_group_gain_sum=np.full(BLOCKS,-2.),
        ))

    def test_original_geographic_block_resampling_uses_shared_denominator(self):
        z=paired_bootstrap(self.fixture(),draws=23,seed=11)
        self.assertEqual(len(z),3)
        x=z.set_index("metric")
        self.assertAlmostEqual(x.loc["uniform_ABC_minus_mean_null_gain","estimate"],.04)
        self.assertAlmostEqual(x.loc["target_group_ABC_minus_mean_null_gain","estimate"],-.02)
        self.assertAlmostEqual(x.loc["uniform_minus_target_background_difference","estimate"],.06)
        self.assertAlmostEqual(x.loc["uniform_minus_target_background_difference","pointwise_MC95_low"],.06)
        self.assertEqual(x.loc["uniform_minus_target_background_difference","bootstrap_draws"],23)

    def test_full_leave_one_block_out_and_no_background_relabeling(self):
        x=leave_one_out(self.fixture())
        self.assertEqual(len(x),BLOCKS)
        self.assertTrue(x.uniform_gain_after_removal.gt(0).all())
        self.assertTrue(x.target_group_gain_after_removal.lt(0).all())
        np.testing.assert_allclose(x.paired_background_difference_after_removal,.06,
                                   atol=1e-15,rtol=0)
        self.assertTrue(x.retained_blocks.eq(BLOCKS-1).all())

    def test_incomplete_or_duplicate_block_stops(self):
        d=self.fixture()
        with self.assertRaises(AssertionError):
            paired_bootstrap(d.iloc[:-1],draws=3)
        d.loc[0,"spatial_block"]=d.loc[1,"spatial_block"]
        with self.assertRaises(AssertionError):
            leave_one_out(d)

    def test_source_fixed_seed_and_counts(self):
        self.assertEqual(BOOT,9999)
        self.assertEqual(SEED,20261108)
        self.assertEqual(BLOCKS,56)

if __name__=="__main__":
    unittest.main()
