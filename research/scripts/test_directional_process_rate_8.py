"""Structure and numerical identity checks for the actual eight-draw POM reuse."""
import unittest
import numpy as np
import pandas as pd

from directional_process_rate_8 import recover_grid, LEVELS


class ActualProcessDirectionalTests(unittest.TestCase):
    def test_source_grid_roundtrip_and_reject_corruption(self):
        rows=[]
        for v in (0.,1.):
            for s in np.linspace(.25,2.,LEVELS):
                for o in np.linspace(.25,2.,LEVELS):
                    rows.append(dict(vegetation=v,S_source=s,D_source=o,
                                     F_B=2+.1*s-.04*o+.02*v))
        a=pd.DataFrame(rows)
        grid=recover_grid(a)
        self.assertEqual(grid.shape,(2,LEVELS,LEVELS))
        np.testing.assert_array_equal(grid.reshape(-1),a.F_B.to_numpy())
        with self.assertRaises(ValueError):
            recover_grid(a.iloc[:-1])
        with self.assertRaises(ValueError):
            recover_grid(pd.concat([a,a.iloc[[0]]]))
        bad=a.copy();bad.loc[0,"F_B"]=-1
        with self.assertRaises(ValueError):
            recover_grid(bad)

    def test_missing_exact_frog_demography_is_rejected(self):
        a=pd.DataFrame(dict(vegetation=[0.],S_source=[.25],D_source=[.25],F_B=[1.]))
        with self.assertRaises(ValueError):
            recover_grid(a)


if __name__=="__main__":
    unittest.main()
