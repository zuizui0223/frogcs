import unittest
import pandas as pd
from stage_vegetation_network import simulate
from multiyear_stage_network import simulate_years


class Timing(unittest.TestCase):
    def test_default_replay(self):
        pd.testing.assert_frame_equal(simulate([{}]),simulate([{}],stage_durations=(45,70,60),size_gate=None),check_exact=True)

    def test_zero_size_gate_removes_aquatic_predation(self):
        q=simulate([{}],size_gate=0).iloc[0]
        for g in ['F_killed_by_S','F_killed_by_D','S_killed_by_D','D_killed_by_S']:
            self.assertEqual(q[g],0)
        self.assertEqual(q.F_completed,1)

    def test_equal_duration_transition_before_drying(self):
        q=simulate([dict(f_arrival=10,s_arrival=10,d_arrival=10,water=70,attack_scale=0)],
                   stage_durations=(60,60,60)).iloc[0]
        self.assertEqual(q.F_completed,1);self.assertEqual(q.S_completed,1)
        self.assertEqual(q.D_dry,0)

    def test_annual_forwards_options(self):
        q=simulate_years([{}],years=1,seasonal_options={'size_gate':0})
        self.assertEqual(q.iloc[0].F_C,1)

    def test_invalid_controls(self):
        for kwargs in [dict(size_gate=-1),dict(size_gate=2),dict(size_gate=float('nan')),
                       dict(stage_durations=(45,-1,60)),dict(stage_durations=(1,2))]:
            with self.assertRaises(ValueError):simulate([{}],**kwargs)


if __name__=='__main__':unittest.main()
