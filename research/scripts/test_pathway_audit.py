import unittest
import numpy as np
import pandas as pd
from stage_vegetation_network import simulate
from multiyear_stage_network import simulate_years


class PathwayAudit(unittest.TestCase):
    def test_instrumentation_preserves_original_outputs(self):
        rows=[dict(f_arrival=50,vegetation=v,attack_scale=1.5) for v in (0,1)]
        old=simulate(rows)
        new=simulate(rows,diagnostics=True,pathway_controls={})
        pd.testing.assert_frame_equal(old,new[old.columns],check_exact=True)

    def test_integrated_hazard_predicts_frog_completion(self):
        r=simulate([dict(f_arrival=50,vegetation=1)],diagnostics=True).iloc[0]
        self.assertAlmostEqual(r.F_completed,np.exp(-r.audit_H_SF-r.audit_H_DF),places=12)
        self.assertAlmostEqual(r.F_completed+r.F_killed_by_S+r.F_killed_by_D,1,places=12)

    def test_each_directed_edge_can_be_disabled(self):
        pairs={'edge_SF':'F_killed_by_S','edge_DF':'F_killed_by_D',
               'edge_DS':'S_killed_by_D','edge_SD':'D_killed_by_S','edge_FE':'D_killed_by_F'}
        for edge,col in pairs.items():
            base=simulate([dict(f_arrival=50)]).iloc[0]
            alt=simulate([dict(f_arrival=50)],pathway_controls={edge:0}).iloc[0]
            self.assertGreater(base[col],0)
            self.assertEqual(alt[col],0)

    def test_cue_to_frog_feeding_is_separate_from_cue_to_odonate_feeding(self):
        p=[dict(f_arrival=50)]
        a=simulate(p,diagnostics=True).iloc[0]
        b=simulate(p,diagnostics=True,pathway_controls={'cue_SF':0}).iloc[0]
        self.assertEqual(a.D_killed_by_S,b.D_killed_by_S)
        self.assertEqual(a.S_killed_by_D,b.S_killed_by_D)
        self.assertGreater(b.F_killed_by_S,a.F_killed_by_S)

    def test_emergence_functions_separate_and_do_not_change_same_season_f(self):
        p=[dict(f_arrival=50,vegetation=1)]
        a=simulate(p).iloc[0]
        survival=simulate(p,pathway_controls={'emerge_survival':0}).iloc[0]
        exposure=simulate(p,pathway_controls={'emerge_exposure':0}).iloc[0]
        self.assertEqual(a.F_completed,survival.F_completed)
        self.assertEqual(a.F_completed,exposure.F_completed)
        self.assertLess(survival.D_completed,a.D_completed)
        self.assertGreater(exposure.D_completed,a.D_completed)

    def test_vector_controls_and_annual_diagnostics(self):
        r=simulate([{},{}],pathway_controls={'edge_SF':[0,1]},diagnostics=True)
        self.assertEqual(r.iloc[0].F_killed_by_S,0)
        self.assertGreater(r.iloc[1].F_killed_by_S,0)
        tr=simulate_years([{}],years=2,dt=1,seasonal_options={'diagnostics':True})
        self.assertIn('audit_H_SF',tr)
        self.assertIn('D_failure',tr)
        np.testing.assert_allclose(tr.D_B,tr.D_C+tr.D_killed_by_S+tr.D_killed_by_F+tr.D_failure,atol=1e-12)

    def test_invalid_controls(self):
        for controls in ({'unknown':0},{'edge_SF':-1},{'cue_SD':float('nan')},{'edge_DS':[1,0]}):
            with self.assertRaises(ValueError):simulate([{}],pathway_controls=controls)


if __name__=='__main__':unittest.main()
