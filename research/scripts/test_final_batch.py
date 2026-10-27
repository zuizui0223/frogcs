import unittest
import numpy as np
import pandas as pd
from final_mechanism_common import catalog,design,evaluate,CONTEXTS
class BatchEquivalence(unittest.TestCase):
 def test_heterogeneous_demography_matches_separate_runs(self):
  m=catalog().query('model_id==1478');parts=[];expected=[]
  for i,(attack,rho,conversion,strength,order) in enumerate([(1.5,.25,2.,.5,'D'),(3.,.75,8.,1.,'S')]):
   d=design(m,[CONTEXTS[i]],[i]);expected.append(evaluate(d,years=3,window=2,dt=.5,attack=attack,rho=rho,conversion=conversion,strength=strength,refuge_order=order))
   d=d.assign(attack=attack,rho_test=rho,conv=conversion,strength=strength,order=order);parts.append(d)
  d=pd.concat(parts,ignore_index=True)
  got=evaluate(d,years=3,window=2,dt=.5,attack=d.attack.to_numpy(),rho=d.rho_test.to_numpy(),conversion=d.conv.to_numpy(),strength=d.strength.to_numpy(),refuge_order=d.order.to_numpy())
  e=pd.concat(expected,ignore_index=True)
  for col in ['F_B','S_B','D_B','F_fraction','audit_H_DS','audit_H_SD']:
   np.testing.assert_allclose(got[col],e[col],atol=1e-12,rtol=1e-12)
if __name__=='__main__':unittest.main()
