import unittest
import numpy as np
import pandas as pd
from stage_handling_factorial_20261029 import simulate,handling_denominators
from stage_network_extension_20261029 import simulate as previous


class HandlingFactorialTests(unittest.TestCase):
    def test_full_matrix_replays_previous_shared_model(self):
        rows=[dict(vegetation=0,cue=0),dict(vegetation=1,cue=0)]
        for h in [0.,1.]:
            pd.testing.assert_frame_equal(simulate(rows,s_handling_matrix=np.full(4,h),diagnostics=True),previous(rows,handling_s=h,diagnostics=True),check_exact=True)

    def test_directional_controls_do_not_change_other_denominator(self):
        matrix=np.eye(4)
        sf,sd=handling_denominators(2.,3.,matrix)
        np.testing.assert_array_equal(sf,[3,4,1,1]);np.testing.assert_array_equal(sd,[1,1,3,4])

    def test_no_D_processing_when_D_capture_removed(self):
        rows=[dict(cue=0,vegetation=1)]
        a=simulate(rows,pathway_controls={'edge_SD':0},s_handling_matrix=[0,1,0,1])
        b=simulate(rows,pathway_controls={'edge_SD':0},s_handling_matrix=[0,0,0,0])
        pd.testing.assert_frame_equal(a,b,check_exact=True)

    def test_asymmetric_controls_conserve_cohorts(self):
        a=simulate([dict(cue=0)],s_handling_matrix=[1,0,0,1]).iloc[0]
        for g in 'FSD':self.assertAlmostEqual(a[g+'_dead']+a[g+'_survived'],1.)


if __name__=='__main__':unittest.main()
