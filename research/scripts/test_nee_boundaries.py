import unittest
import numpy as np
import pandas as pd
from nee_boundaries import phi,phi_prime,hazard,elasticities,shapley_state
from nee_existing_strata import seasonal_outcomes

class BoundaryTests(unittest.TestCase):
 def test_general_hill_boundary(self):
  from nee_boundaries import hill_hazard,hill_elasticity
  f=np.array([.2,1.,3.]);s=np.array([.3,2.,4.]);e=1e-6
  for q in [1.,1.5,2.,3.]:
   numeric=(np.log(hill_hazard(f*np.exp(e),1.,s,q,.7))-np.log(hill_hazard(f*np.exp(-e),1.,s,q,.7)))/(2*e)
   np.testing.assert_allclose(hill_elasticity(f,s,q,.7),numeric,atol=1e-9)
 def test_trace_replays_kernel(self):
  from stage_handling_factorial_20261029 import simulate
  from stage_boundary_trace_20261029 import simulate as trace
  rows=[dict(cue=0,vegetation=0),dict(cue=0,vegetation=1)];saved=[]
  pd.testing.assert_frame_equal(simulate(rows,diagnostics=True,s_handling_matrix=[1,0,1,0]),trace(rows,diagnostics=True,s_handling_matrix=[1,0,1,0],observer=lambda t,q:saved.append(q)))
  self.assertEqual(len(saved),480)
 def test_derivative(self):
  f=np.array([.2,.7,1.,2.,5.]);v=np.array([0.,.3,1.,.8,1.]);e=1e-6
  np.testing.assert_allclose(phi_prime(f,v),(phi(f+e,v)-phi(f-e,v))/(2*e),atol=1e-9)
 def test_handling_threshold(self):
  f=np.array([1.,2.,4.]);s=np.array([3.,3.,3.]);ef,es=elasticities(f,s,1.,1.)
  self.assertGreater(ef[0],0);self.assertAlmostEqual(ef[1],0);self.assertLess(ef[2],0)
 def test_exact_shapley(self):
  lo=np.array([[3.,2.,.2],[.5,.1,2.]]);hi=np.array([[1.,1.,2.],[1.,.8,3.]])
  q=shapley_state(lo,hi,np.array([0.,1.]),np.array([.5,1.]))
  np.testing.assert_allclose(q.sum(axis=1),hazard(*hi.T,np.array([0.,1.]),np.array([.5,1.]))-hazard(*lo.T,np.array([0.,1.]),np.array([.5,1.])),atol=1e-12)
 def test_season_denominator(self):
  d=pd.DataFrame(dict(site=['a']*4+['b']*2,season=[1,1,1,2,1,1],year=[1,1,2,2,1,2],strong=[0,1,0,1,1,1]))
  r=seasonal_outcomes(d,1);self.assertEqual(list(r.index),['a']);self.assertAlmostEqual(r.iloc[0],1/3)

if __name__=='__main__':unittest.main()
