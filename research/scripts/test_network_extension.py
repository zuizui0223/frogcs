import unittest
import numpy as np
import pandas as pd
from stage_vegetation_network import simulate as original
from stage_network_extension_20261029 import simulate


class NetworkExtensionTests(unittest.TestCase):
    def test_zero_extension_replays_original(self):
        rows=[dict(vegetation=v,cue=0) for v in [0.,1.]]
        for response in [None,'litter']:
            pd.testing.assert_frame_equal(original(rows,diagnostics=True,functional_response=response),simulate(rows,diagnostics=True,functional_response=response),check_exact=True)

    def test_shared_handling_and_frozen_gates_conserve_cohorts(self):
        r=simulate([dict(vegetation=1,cue=0)],handling_s=1,handling_d=1,sd_size_mode='frozen',initial_cohorts=np.array([[2.,3.,4.]]))
        for g,n in zip('FSD',[2.,3.,4.]):
            self.assertAlmostEqual(float(r[g+'_survived'].iloc[0]+r[g+'_dead'].iloc[0]),n)

    def test_deleted_edge_stays_zero_with_shared_handling(self):
        r=simulate([dict(cue=0)],handling_s=1,handling_d=1,pathway_controls={'edge_DS':0,'edge_SD':0}).iloc[0]
        self.assertEqual(r.S_killed_by_D,0);self.assertEqual(r.D_killed_by_S,0)

    def test_no_shared_frog_response_change_without_salamander(self):
        kw=dict(functional_response='litter')
        a=simulate([dict(community='FD',cue=0)],**kw)
        b=simulate([dict(community='FD',cue=0)],handling_d=1,**kw)
        np.testing.assert_allclose(a.F_completed,b.F_completed,atol=1e-12)

    def test_invalid_extension_values(self):
        for kw in [dict(handling_s=-1),dict(s_growth=float('nan')),dict(sd_size_mode='bad')]:
            with self.assertRaises(ValueError):simulate([{}],**kw)

    def test_mixed_batches_equal_scalar_runs(self):
        rows=[dict(cue=0,vegetation=1)]*2
        both=simulate(rows,handling_s=np.array([0.,1.]),handling_d=np.array([0.,1.]))
        for i,h in enumerate([0.,1.]):
            one=simulate([rows[i]],handling_s=h,handling_d=h)
            np.testing.assert_allclose(both.iloc[i][['F_completed','S_completed','D_completed']].to_numpy(float),one.iloc[0][['F_completed','S_completed','D_completed']].to_numpy(float),atol=1e-12)

    def test_actual_predation_dominance_reverses_only_with_dynamic_sizes(self):
        row=dict(f_arrival=20,s_arrival=20,d_arrival=0,cue=0,attack_scale=.5)
        opts=dict(stage_durations=(45,80,60),s_growth=.03,d_growth=.015,diagnostics=True,extension_diagnostics=True)
        dynamic=simulate([row],**opts).iloc[0]
        frozen=simulate([row],sd_size_mode='frozen',**opts).iloc[0]
        self.assertGreater(dynamic.audit_DS_dominant_days,0)
        self.assertGreater(dynamic.audit_SD_dominant_days,0)
        self.assertEqual(frozen.audit_SD_dominant_days,0)


if __name__=='__main__':unittest.main()
