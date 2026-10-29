import unittest
import numpy as np
from nee_shared_environment_crossfit import folds_for,cross_residuals


class SpatialCrossfitTests(unittest.TestCase):
    def test_blocks_are_not_split_and_all_rows_held_out_once(self):
        groups=np.repeat(np.arange(15),np.arange(1,16))
        folds=folds_for(groups)
        self.assertEqual(len(set(folds)),5)
        for g in set(groups):self.assertEqual(len(set(folds[groups==g])),1)

    def test_heldout_outcomes_do_not_change_own_predictions(self):
        rng=np.random.default_rng(4);x=rng.normal(size=(100,3));y=rng.normal(size=(100,2));folds=np.repeat(np.arange(5),20)
        _,a=cross_residuals(x,y,folds,'linear');changed=y.copy();changed[folds==2]+=1000
        _,b=cross_residuals(x,changed,folds,'linear')
        np.testing.assert_allclose(a[folds==2],b[folds==2],atol=1e-12)


if __name__=='__main__':unittest.main()
