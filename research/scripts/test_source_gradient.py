import unittest
import numpy as np
import pandas as pd
from multiyear_stage_network import simulate_years
from run_source_gradient import grid,contrasts,METRICS


class Sources(unittest.TestCase):
    def test_explicit_boolean_grid(self):
        d=grid()
        self.assertFalse(d[['reverse','intraguild']].isna().any().any())
        self.assertTrue(d.loc[d.variant=='full',['reverse','intraguild']].all().all())
    def test_default_identical(self):
        a=simulate_years([{}],years=2,dt=1)
        b=simulate_years([{}],years=2,dt=1,source_cohorts=[[1,1,1]])
        pd.testing.assert_frame_equal(a,b[a.columns],check_exact=True)

    def test_external_mass_balance(self):
        d=simulate_years([{'rho':0}],years=2,dt=1,source_cohorts=[[1,2,.25]])
        np.testing.assert_allclose(d.iloc[0][['F_immigrant','S_immigrant','D_immigrant']].to_numpy(float),[.6,1,.25])
        np.testing.assert_allclose(d.iloc[1][['F_B','S_B','D_B']].to_numpy(float),[1,1.5,.25])

    def test_closed_system_unaffected(self):
        a=simulate_years([{'rho':1}],years=3,dt=1)
        b=simulate_years([{'rho':1}],years=3,dt=1,source_cohorts=[[3,4,5]])
        pd.testing.assert_frame_equal(a,b[a.columns],check_exact=True)

    def test_invalid_sources(self):
        for sources in ([[1,-1,1]],[[1,float('nan'),1]],[[1,1]],[[1,1,1],[1,1,1]]):
            with self.assertRaises(ValueError):simulate_years([{}],years=1,source_cohorts=sources)
        with self.assertRaises(ValueError):
            simulate_years([{'community':'FD'}],years=1,source_cohorts=[[1,1,1]])

    def test_known_interaction_and_order_invariance(self):
        d=grid((15,))
        for metric in METRICS:d[metric]=10-d.D_source-d.S_source*d.D_source
        a,b=contrasts(d)
        np.testing.assert_allclose(b.S_change_slope_F_B,-1.75,atol=1e-12)
        c,e=contrasts(d.sample(frac=1,random_state=4))
        pd.testing.assert_frame_equal(a,c)
        pd.testing.assert_frame_equal(b,e)


if __name__=='__main__':unittest.main()
