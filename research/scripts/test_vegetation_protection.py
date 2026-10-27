import unittest
import numpy as np
import pandas as pd
from stage_vegetation_network import simulate
class VegetationProtection(unittest.TestCase):
 def test_legacy_default_exact(self):
  rows=[dict(vegetation=v) for v in (0.,1.)]
  pd.testing.assert_frame_equal(simulate(rows),simulate(rows,pathway_controls={'cover_SD':0.}),check_exact=True)
 def test_protection_reduces_only_target_hazard_in_isolated_pair(self):
  row=dict(vegetation=1.,f_arrival=0.,s_arrival=0.,d_arrival=0.,cue=0.,reverse=False)
  control=dict(edge_SF=0.,edge_DF=0.,edge_DS=0.,cover_SD=0.)
  a=simulate([row],pathway_controls=control,diagnostics=True).iloc[0]
  b=simulate([row],pathway_controls={**control,'cover_SD':1.},diagnostics=True).iloc[0]
  self.assertAlmostEqual(b.audit_H_SD/a.audit_H_SD,np.exp(-.8),places=12)
  self.assertGreater(b.D_survived,a.D_survived)
  self.assertEqual(b.S_survived,a.S_survived)
  self.assertAlmostEqual(b.D_survived+b.D_dead,1.,places=12)
 def test_no_vegetation_means_no_protection(self):
  pd.testing.assert_frame_equal(simulate([{'vegetation':0}],pathway_controls={'cover_SD':0}),simulate([{'vegetation':0}],pathway_controls={'cover_SD':1}),check_exact=True)
if __name__=='__main__':unittest.main()
