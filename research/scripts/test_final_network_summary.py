import unittest
import numpy as np
from multiyear_stage_network import simulate_years
from final_network_summary import summarize_years
class StreamSummary(unittest.TestCase):
 def test_matches_reference(self):
  rows=[dict(vegetation=v,rho=r,cue=0.,reverse=True) for v in (0.,1.) for r in (.25,.75)]
  src=np.array([[1.,.25,2.]]*4)
  opt=dict(diagnostics=True,pathway_controls={'cover_SD':.5})
  tr=simulate_years(rows,years=8,dt=.5,source_cohorts=src,seasonal_options=opt)
  expected=tr[tr.year>=4].groupby('scenario_id').mean(numeric_only=True)
  got=summarize_years(rows,years=8,window=4,dt=.5,source_cohorts=src,seasonal_options=opt)
  for col in ['F_B','S_B','D_B','F_fraction','S_fraction','D_fraction','audit_H_SF','audit_H_DF','audit_H_DS','audit_H_SD']:
   np.testing.assert_allclose(got[col],expected[col],rtol=1e-12,atol=1e-12)
  np.testing.assert_allclose(got.F_B_sd,tr[tr.year>=4].groupby('scenario_id').F_B.std(ddof=0),atol=1e-12)
 def test_zero_return_constant_source(self):
  q=summarize_years([dict(rho=0.,cue=0)],years=80,window=20,source_cohorts=np.array([[1.,.5,2.]]))
  np.testing.assert_allclose(q[['F_B','S_B','D_B']].to_numpy(),[[1,.5,2]],atol=1e-10)
if __name__=='__main__':unittest.main()
