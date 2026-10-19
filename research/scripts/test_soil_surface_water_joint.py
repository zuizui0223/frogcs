import importlib.util,unittest
from pathlib import Path
import numpy as np,pandas as pd
import statsmodels.formula.api as smf
HERE=Path(__file__).parent
MOD=None
if (HERE/'soil_surface_water_joint.py').is_file():
 spec=importlib.util.spec_from_file_location('joint',HERE/'soil_surface_water_joint.py');MOD=importlib.util.module_from_spec(spec);spec.loader.exec_module(MOD)

def fixture():
 pairs=pd.DataFrame([dict(wet_RunID='2',dry_RunID='1',State='Test',RouteNumber='10',route_cluster='Test:10',RunNumber='1',year_earlier=2005,year_later=2006,stable_sites=True,same_observer=True)])
 rows=[]
 for rid,year,current,recent in [('1',2005,0.1,0.3),('2',2006,0.3,0.5)]:
  for sid in range(10):rows.append(dict(RunID=rid,SiteID=str(sid),State='Test',RouteNumber='10',route_cluster='Test:10',RunNumber='1',year=year,month=5,current_D_r500=current,recent_D_3m_r500=recent,DSWE_sd_12m_r500=.1))
 return pairs,pd.DataFrame(rows)

class TestJoint(unittest.TestCase):
 def setUp(self):self.assertIsNotNone(MOD,'joint implementation is required')
 def test_historical_decomposition(self):
  now=np.array([.1,.3,0,1]);past=np.array([.4,.6,0,1]);recent=(now+2*past)/3
  np.testing.assert_allclose(MOD.prior_two(now,recent),past,atol=1e-12)
  with self.assertRaises(ValueError):MOD.prior_two(np.array([1.]),np.array([0.]))
 def test_csv_eight_decimal_boundary_rounding(self):
  np.testing.assert_allclose(MOD.prior_two(np.array([1.,.25]),np.array([.33333333,.08333333])),[0.,0.],atol=1e-12)
  with self.assertRaises(ValueError):MOD.prior_two(np.array([1.]),np.array([.333]))
 def test_all_sites_zero_is_valid(self):
  p,w=fixture();w[['current_D_r500','recent_D_3m_r500']]=0
  d,a=MOD.join(p,w,500);self.assertEqual(len(d),1);self.assertEqual(d.iloc[0].surface_current_w,0)
 def test_exact_join_and_no_expansion(self):
  p,w=fixture();d,a=MOD.join(p,w,500);self.assertEqual(len(d),1);self.assertAlmostEqual(d.iloc[0].surface_prior_w,.6)
 def test_missingness_not_partial_mean(self):
  p,w=fixture();w.loc[0,'DSWE_sd_12m_r500']=np.nan
  d,a=MOD.join(p,w,500);self.assertEqual(len(d),0);self.assertGreater(a['failures'].get('M3_missing',0),0)
 def test_duplicate_site_rejected(self):
  p,w=fixture();w=pd.concat([w,w.iloc[[0]]])
  with self.assertRaises(ValueError):MOD.join(p,w,500)
 def test_same_ten_site_ids_required(self):
  p,w=fixture();w.loc[0,'SiteID']='different'
  d,a=MOD.join(p,w,500);self.assertEqual(len(d),0);self.assertEqual(a['failures']['siteid_mismatch'],1)
 def test_year_route_alignment_required(self):
  p,w=fixture();w.loc[w.RunID=='2','year']=2007
  with self.assertRaises(ValueError):MOD.join(p,w,500)
 def test_absorbed_model_matches_explicit_dummy_CR1(self):
  rng=np.random.default_rng(33);n=240;d=pd.DataFrame({'route_cluster':np.repeat(np.arange(20).astype(str),12),'State':'s','x':rng.normal(size=n),'y':rng.normal(size=n)})
  z=MOD.core.absorb_fit(d,['y'],['x'])['y']['terms']['x']
  f=smf.ols('y ~ x + C(route_cluster)',d).fit(cov_type='cluster',cov_kwds={'groups':d.route_cluster})
  self.assertAlmostEqual(z['beta'],f.params.x,places=11);self.assertAlmostEqual(z['se'],f.bse.x,places=11)
 def test_holm_family_size(self):
  np.testing.assert_allclose(MOD.core.holm([.001,.03,.2,.7]),[.004,.09,.4,.7])

if __name__=='__main__':unittest.main()
