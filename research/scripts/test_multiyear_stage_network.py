import unittest
import numpy as np
import pandas as pd
from stage_vegetation_network import simulate
from multiyear_stage_network import simulate_years, summarize, paired

class InitialCohorts(unittest.TestCase):
    def test_default_compatibility(self):
        a=simulate([{}])
        b=simulate([{}],initial_cohorts=[[1,1,1]])
        pd.testing.assert_frame_equal(a,b,check_exact=True)

    def test_arbitrary_density_accounting(self):
        initial=np.array([[2,.3,4],[0,2,0]])
        out=simulate([{},{}],initial_cohorts=initial)
        for k,g in enumerate('FSD'):
            np.testing.assert_allclose(out[g+'_survived']+out[g+'_dead'],initial[:,k],atol=1e-11)
        self.assertEqual(out.iloc[1].F_completed,0)

    def test_invalid_or_absent_density(self):
        for init in ([[1,-1,1]],[[1,1,float('nan')]],[[1,1]],[[1,1,1],[1,1,1]]):
            with self.assertRaises(ValueError): simulate([{}],initial_cohorts=init)
        with self.assertRaises(ValueError): simulate([{'community':'FD'}],initial_cohorts=[[1,1,1]])

class AnnualFeedback(unittest.TestCase):
    def test_pairing_rejects_duplicate_contexts(self):
        d=simulate_years([{'reverse':False},{'reverse':True}],years=1,dt=1)
        s=summarize(d)
        with self.assertRaises(ValueError):paired(pd.concat([s,s],ignore_index=True))

    def test_delayed_pulse_and_no_phantom_immature_history(self):
        d=simulate_years([{'community':'F','rho':1,'attack_scale':0}],years=4,dt=1,
                         survival=(0,0,0),delays=(3,3,3),juvenile=(1,1,1))
        np.testing.assert_allclose(d.F_B,[1,0,0,2])
        self.assertTrue((d.S_B==0).all())
        self.assertTrue((d.D_B==0).all())

    def test_zero_local_return_fixed_input_control(self):
        d=simulate_years([{'community':'FD','rho':0,'reverse':r}for r in (False,True)],years=4,dt=1)
        self.assertTrue((d.F_B==1).all())
        self.assertTrue((d.D_B==1).all())
        a=d[d.scenario_id==0];b=d[d.scenario_id==1]
        np.testing.assert_allclose(a.F_C,b.F_C)
        self.assertTrue((d.S_B==0).all())

    def test_later_feedback_but_not_first_season_frog_effect(self):
        d=simulate_years([{'community':'FD','rho':1,'reverse':r}for r in (False,True)],years=5,dt=1)
        a=d[d.scenario_id==0].reset_index();b=d[d.scenario_id==1].reset_index()
        self.assertEqual(a.loc[0,'F_C'],b.loc[0,'F_C'])
        self.assertLess(b.loc[1,'D_B'],a.loc[1,'D_B'])
        self.assertGreater(b.loc[1,'F_C'],a.loc[1,'F_C'])

    def test_simple_density_regulation_equilibrium(self):
        d=simulate_years([{'community':'F','rho':1,'attack_scale':0}],years=30,dt=1,
                         delays=(1,1,1),juvenile=(1,1,1))
        self.assertAlmostEqual(d.iloc[-1].F_B,4/.6-1,places=4)
        self.assertTrue((d.F_B>=0).all())
        self.assertLessEqual(d.F_B.max(),4/.6)

    def test_invalid_demography(self):
        for kwargs in ({'delays':(0,1,1)},{'survival':(1.1,.5,0)},
                       {'conversion':(-1,4,4)},{'juvenile':(.8,.8,float('nan'))},{'years':0}):
            with self.assertRaises(ValueError):simulate_years([{}],**kwargs)
        with self.assertRaises(ValueError):simulate_years([{'rho':1.1}])

if __name__=='__main__': unittest.main()
