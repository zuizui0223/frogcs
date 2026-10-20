import unittest
import sys
from pathlib import Path
import numpy as np
import pandas as pd
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root))
sys.path.insert(0,str(root/'scripts'))
import pair_environment as m

class PairEnvironmentTests(unittest.TestCase):
    def example(self):
        p=pd.DataFrame({'wet_RunID':['1','2'],'dry_RunID':['3','4'],
           'State':['S','S'],'RouteNumber':['1','1'],'RunNumber':['1','1'],
           'route_cluster':['S:1','S:1'],'year_earlier':[2005,2006],'year_later':[2006,2007],
           'wet_richness':[4,4],'dry_richness':[3,3],
           'wet_observed_cscore':[2.8,3.0],'wet_null_mean_cscore':[2.8,2.5],
           'dry_observed_cscore':[2.0,3.0],'dry_null_mean_cscore':[2.0,3.1],
           'delta_excess':[0.,.6],'stable_physical_siteids':[True,True],
           'same_observer':[True,False]})
        e=p.drop(columns=['wet_observed_cscore','wet_null_mean_cscore',
           'dry_observed_cscore','dry_null_mean_cscore','delta_excess','stable_physical_siteids']).copy()
        e['stable_sites']=True;e['soil1_w']=[.3,.4]
        return p,e
    def test_raw_positive_is_not_null_excess(self):
        p,_=self.example();d=m.correct_residuals(p)
        self.assertEqual(d.wet_excess.iloc[0],0)
        self.assertAlmostEqual(d.delta_excess.iloc[1],.6)
    def test_bad_old_difference_rejected(self):
        p,_=self.example();p.loc[0,'delta_excess']=2.8
        with self.assertRaisesRegex(ValueError,'residual identity'):m.correct_residuals(p)
    def test_duplicate_pairs_fail(self):
        p,e=self.example();e=pd.concat([e,e.iloc[[0]]])
        with self.assertRaisesRegex(ValueError,'duplicate'):m.strict_join(p,e)
    def test_reversed_pairs_not_silently_flipped(self):
        p,e=self.example();e=e.rename(columns={'wet_RunID':'dry_RunID','dry_RunID':'wet_RunID'})
        d,a=m.strict_join(p,e);self.assertEqual(len(d),0);self.assertEqual(a['missing_pairs'],2)
    def test_common_metadata_conflict_fail(self):
        p,e=self.example();e.loc[0,'State']='other'
        with self.assertRaisesRegex(ValueError,'metadata'):m.strict_join(p,e)
    def test_taxon_richness_conflict_fail(self):
        p,e=self.example();e.loc[0,'wet_richness']=100
        with self.assertRaisesRegex(ValueError,'metadata'):m.strict_join(p,e)
    def test_missing_not_zero(self):
        p,e=self.example();d,a=m.strict_join(p,e.iloc[[0]])
        self.assertEqual(len(d),1);self.assertEqual(a['missing_pairs'],1)
    def test_both_stability_gates(self):
        p,e=self.example();e.loc[0,'stable_sites']=False
        d,a=m.strict_join(p,e);self.assertEqual(len(d),1);self.assertEqual(a['unstable_pairs'],1)
    def test_route_equal_not_pair_equal(self):
        d=pd.DataFrame({'route_cluster':['a','b','b','b'],'v':[3,-1,-1,-1]})
        a=m.route_summary(d,'v');self.assertEqual(a['mean'],1)
    def test_zero_residual_with_nonzero_raw_has_no_segregation(self):
        d=pd.DataFrame({'route_cluster':['a','b'],'v':[0.,0.]})
        a=m.route_summary(d,'v');self.assertEqual(a['ci95'],[0.,0.])
    def test_absorbed_CR1_matches_explicit_dummy(self):
        rng=np.random.default_rng(74);g=np.repeat(np.arange(16),7);x=rng.normal(size=(len(g),3))
        y=2*x[:,0]-.5*x[:,1]+rng.normal(size=16)[g]+rng.normal(size=len(g))
        d=pd.DataFrame(x,columns=['x1','x2','x3']);d['y']=y;d['route_cluster']=g.astype(str)
        f=m.fit_within(d,['x1','x2','x3'],['y']);v=m.verify_explicit(d,['x1','x2','x3'],'y',f['y'])
        self.assertLess(v['max_beta_error'],1e-9);self.assertLess(v['max_se_error'],1e-9)
    def test_duplicate_design_names_fail(self):
        d=pd.DataFrame({'route_cluster':['a','a','b','b'],'x':[1,2,3,4],'y':[0,3,4,5]})
        with self.assertRaisesRegex(ValueError,'duplicate'):m.fit_within(d,['x','x'],['y'])
    def test_no_change_of_primary_family(self):
        self.assertEqual(m.PRIMARY,[('ERA5','layer_common'),('ERA5_MODIS','layer_common'),('ERA5_MODIS','surface_current_delta')])
    def test_holm(self):
        np.testing.assert_allclose(m.holm([.04,.005,.3]),[.08,.015,.3])

if __name__=='__main__':unittest.main()
