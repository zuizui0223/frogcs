import unittest, importlib.util
from pathlib import Path
import numpy as np
import pandas as pd
P=Path(__file__).with_name('environment_state_response.py')
class EnvironmentalTests(unittest.TestCase):
 def mod(self):
  self.assertTrue(P.exists(), 'Environment-state analysis implementation missing')
  s=importlib.util.spec_from_file_location('envtest',P);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
 def data(self,n=240):
  r=np.random.default_rng(101);d=pd.DataFrame({'soil1_w':r.uniform(.15,.5,n),'soil1_d':r.uniform(.1,.4,n),'soil2_w':r.uniform(.15,.5,n),'soil2_d':r.uniform(.1,.4,n),'vpd_w':r.uniform(.1,1.2,n),'vpd_d':r.uniform(.1,1.5,n),'rain72_w':r.uniform(0,30,n),'rain72_d':r.uniform(0,30,n),'rain_contrast':r.uniform(.2,3,n),'temp_difference':r.normal(0,3,n),'doy_difference':r.normal(0,10,n),'year_gap':r.integers(1,4,n),'State':['A']*n,'RunNumber':['1']*n,'route_cluster':[str(i//4) for i in range(n)]});return d
 def test_training_only_scaling(self):
  m=self.mod();d=self.data();z,sc=m.features(d.iloc[:120]);_,testsc=m.features(d.iloc[120:],sc);self.assertEqual(sc,testsc)
 def test_state_is_symmetric_not_chronological(self):
  m=self.mod();d=self.data();a=m.raw_features(d);e=d.copy()
  for prefix in ['soil1','soil2','vpd','rain72']:e[prefix+'_w'],e[prefix+'_d']=d[prefix+'_d'],d[prefix+'_w']
  b=m.raw_features(e);np.testing.assert_allclose(a['soil_mid'],b['soil_mid']);np.testing.assert_allclose(a['soil_delta'],-b['soil_delta'])
 def test_subsurface_contrast(self):
  m=self.mod();d=self.data();a=m.raw_features(d);np.testing.assert_allclose(a['layer_common']+a['surface_excess']/2,d.soil1_w-d.soil1_d)
 def test_fixed_holm_family(self):
  m=self.mod();self.assertEqual(len(m.PRIMARY),3);np.testing.assert_allclose(m.holm([.01,.04,.2]),[.03,.08,.2])
 def test_no_zero_missing_environment(self):
  m=self.mod();d=self.data();d.loc[0,'soil1_w']=np.nan
  with self.assertRaises(ValueError):m.features(d)
 def test_interaction_and_cluster_inference(self):
  m=self.mod();d=self.data();z,_=m.features(d);z['strong_new_score']=3+2*z.soil_delta_z-1.5*z.soil_delta_z*z.soil_mid_z+np.random.default_rng(42).normal(0,.05,len(z));f=m.fit_model(z,m.PRIMARY[0]['formula']);t=m.term(f,m.PRIMARY[0]['term']);self.assertLess(t['beta'],-1.4);self.assertLess(t['ci95'][1],0)
if __name__=='__main__':unittest.main()
