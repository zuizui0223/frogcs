import unittest
import numpy as np
from stage_vegetation_network import simulate


class StageVegetation(unittest.TestCase):
    def run_one(self, **kwargs):
        return simulate([kwargs], dt=.25).iloc[0]

    def test_closed_cohort_accounting(self):
        for water in [60,120]:
            r=self.run_one(water=water,vegetation=1)
            for g in ['F','S','D']:
                self.assertAlmostEqual(r[g+'_survived']+r[g+'_dead'],1,places=12)
                self.assertGreaterEqual(r[g+'_survived'],0)

    def test_absent_predators(self):
        r=self.run_one(community='F',cue=30)
        self.assertAlmostEqual(r.F_completed,1)
        self.assertEqual(r.S_survived,0)
        self.assertEqual(r.D_survived,0)

    def test_no_structure_path_no_effect(self):
        a=self.run_one(roles=0,vegetation=0)
        b=self.run_one(roles=0,vegetation=1)
        np.testing.assert_allclose(a[['F_completed','S_completed','D_completed']].astype(float),
                                   b[['F_completed','S_completed','D_completed']].astype(float))

    def test_drying_before_frog_transition(self):
        self.assertEqual(self.run_one(f_arrival=50,water=60).F_completed,0)

    def test_no_cue_without_dragonfly(self):
        self.assertEqual(self.run_one(community='FS',cue=0).F_completed,
                         self.run_one(community='FS',cue=30).F_completed)

    def test_reverse_edge_only_emergence(self):
        a=self.run_one(f_arrival=10,d_arrival=35,reverse=True)
        b=self.run_one(f_arrival=10,d_arrival=35,reverse=False)
        self.assertGreater(a.D_killed_by_F,0)
        self.assertEqual(b.D_killed_by_F,0)
        self.assertAlmostEqual(a.F_completed,b.F_completed)
        self.assertLess(a.D_completed,b.D_completed)

    def test_no_reverse_when_no_postmetamorph_overlap(self):
        self.assertEqual(self.run_one(f_arrival=50,d_arrival=10).D_killed_by_F,0)

    def test_reciprocal_edge_removal(self):
        a=self.run_one(s_arrival=0,d_arrival=35,reciprocal=True)
        b=self.run_one(s_arrival=0,d_arrival=35,reciprocal=False)
        self.assertGreater(a.D_killed_by_S,0)
        self.assertEqual(b.D_killed_by_S,0)

    def test_emergence_only_does_not_change_frog_larval_survival(self):
        a=self.run_one(roles=8,vegetation=0)
        b=self.run_one(roles=8,vegetation=1)
        self.assertEqual(a.F_completed,b.F_completed)

    def test_half_step(self):
        a=simulate([{}],dt=.25).iloc[0]
        b=simulate([{}],dt=.125).iloc[0]
        self.assertLess(max(abs(a[g+'_completed']-b[g+'_completed']) for g in ['F','S','D']),.005)

    def test_invalid_inputs(self):
        for p in [{'vegetation':-1},{'f_arrival':.1},{'cue':float('nan')},{'community':'X'}]:
            with self.assertRaises(ValueError):simulate([p])

    def test_independent_predators_multiplicative_null(self):
        values={c:self.run_one(community=c,intraguild=False,cue=0).F_completed for c in ['F','FS','FD','FSD']}
        self.assertAlmostEqual(values['FSD']*values['F'],values['FS']*values['FD'],places=12)

if __name__=='__main__':unittest.main()
