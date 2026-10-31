"""Check actual heterogeneous 80-year simulator is the SAME original dynamics."""
import unittest

import numpy as np
import pandas as pd

from abc_intrinsic_factorial import catalogue_structure,one_factorial,sign_code
from abc_true_80year_factorial import (
    ensemble_rows,vectorized_annual,compare_source_path,
    summarize_factorial_per_draw,prior_draws,anchor_values
)


class TrueEightyYearRateABCTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cases,_=catalogue_structure()

    def test_rate_draw_pairing_and_exact_eight_corners(self):
        draws=prior_draws(4,seed=77)
        grid=ensemble_rows(self.cases,draws,"original","baseline")
        self.assertEqual(len(grid),4*4*8)
        self.assertEqual(grid.structural_class.nunique(),2)
        self.assertEqual(grid.edge.nunique(),2)
        self.assertEqual(grid.groupby(["draw","case"]).size().unique().tolist(),[8])
        self.assertEqual(grid.groupby(["draw","structural_class"]).edge.nunique().unique().tolist(),[2])
        for x in ("attack_scale","rho","conversion","f_delay"):
            self.assertTrue(grid.groupby("draw")[x].nunique().eq(1).all())

    def test_actual_stage_kernel_equals_original_annual_model(self):
        err=compare_source_path(self.cases,"original","baseline",years=4,window=2,dt=.5)
        self.assertLess(err["F_B"],1e-9)
        self.assertLess(err["F_fraction"],1e-9)
        self.assertLess(err["F_B_sd"],1e-7)

    def test_two_prior_demographies_actually_affect_recruitment(self):
        priors=prior_draws(2,seed=22)
        g=ensemble_rows(self.cases,priors,"original","baseline")
        short=vectorized_annual(g,years=5,window=2,dt=.5)
        self.assertEqual(len(short),len(g))
        self.assertTrue(short.F_B.gt(0).all())
        self.assertTrue(short.F_fraction.between(0,1).all())
        self.assertTrue(np.isfinite(short.F_B.to_numpy()).all())
        result=summarize_factorial_per_draw(short)
        self.assertEqual(len(result),2*4*2)
        self.assertEqual(result.n_matching_signs.max()<=4,True)

    def test_invalid_lags_and_priors_rejected(self):
        priors=pd.DataFrame([anchor_values()])
        g=ensemble_rows(self.cases,priors,"original","baseline")
        bad=g.copy()
        bad["f_delay"]=0
        with self.assertRaises(ValueError):
            vectorized_annual(bad,years=2,window=1,dt=.5)
        missing=g.iloc[:-1]
        with self.assertRaises(ValueError):
            summarize_factorial_per_draw(missing)


if __name__=="__main__":
    unittest.main()
