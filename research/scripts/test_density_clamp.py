import unittest
import numpy as np
import pandas as pd
from stage_density_clamp_20261029 import simulate
from stage_refuge_generality_20261029 import simulate as original

class DensityClampTests(unittest.TestCase):
 def test_default_replay(self):
  p=[dict(cue=0,vegetation=v) for v in [0,1]]
  pd.testing.assert_frame_equal(simulate(p,response_family='mixed',diagnostics=True),original(p,response_family='mixed',diagnostics=True),check_exact=True)
 def test_replacement_accounting_and_sentinel(self):
  a=simulate([dict(cue=0,water=120)],clamp_guilds='F',response_family='II',diagnostics=True).iloc[0]
  self.assertGreater(a.F_replaced,0)
  self.assertAlmostEqual(a.F_survived,1)
  self.assertAlmostEqual(a.F_dead+a.F_survived,1+a.F_replaced)
  self.assertGreater(a.audit_H_SF+a.audit_H_DF,0)
  self.assertLess(np.exp(-a.audit_H_SF-a.audit_H_DF),1)
 def test_all_clamped_DS_edge_has_no_frog_hazard_effect(self):
  p=[dict(cue=0,vegetation=v) for v in [0,1]]
  a=simulate(p,clamp_guilds='FSD',response_family='mixed',diagnostics=True,pathway_controls={'edge_DS':1})
  b=simulate(p,clamp_guilds='FSD',response_family='mixed',diagnostics=True,pathway_controls={'edge_DS':0})
  np.testing.assert_allclose(a[['audit_H_SF','audit_H_DF']],b[['audit_H_SF','audit_H_DF']],atol=1e-12)
  self.assertTrue((a.S_replaced>0).all());self.assertTrue((b.S_replaced==0).all())
 def test_absent_guild_stays_absent(self):
  a=simulate([dict(community='FD',cue=0)],clamp_guilds='FSD',diagnostics=True).iloc[0]
  self.assertEqual(a.S_replaced,0);self.assertEqual(a.S_survived,0)
 def test_invalid_clamp(self):
  with self.assertRaises(ValueError):simulate([{}],clamp_guilds='fish')

if __name__=='__main__':unittest.main()
