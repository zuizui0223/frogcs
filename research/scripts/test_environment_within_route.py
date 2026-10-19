import unittest
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from environment_within_route import raw_features,absorb_fit,error_decomposition,validate_outcome_identities,holm

class WithinTests(unittest.TestCase):
    def frame(self):
        rng=np.random.default_rng(881)
        g=np.repeat(np.arange(18),7);x=rng.normal(size=len(g));z=rng.normal(size=len(g))
        y=2*x-z+rng.normal(size=18)[g]*3+rng.normal(size=len(g))
        return pd.DataFrame({'route_cluster':g.astype(str),'x':x,'z':z,'y':y})
    def test_absorbed_coefficients_and_covariance_match_explicit_fixed_effects(self):
        d=self.frame(); a=absorb_fit(d,['y'],['x','z'])['y']
        f=smf.ols('y ~ x+z+C(route_cluster)',d).fit(cov_type='cluster',cov_kwds={'groups':d.route_cluster})
        for k in ['x','z']:
            self.assertAlmostEqual(a['terms'][k]['beta'],f.params[k],places=11)
            self.assertAlmostEqual(a['terms'][k]['se'],f.bse[k],places=11)
    def test_within_slopes_do_not_change_after_arbitrary_route_shift(self):
        d=self.frame();a=absorb_fit(d,['y'],['x','z'])['y']
        d.y+=d.route_cluster.astype(int)*20
        b=absorb_fit(d,['y'],['x','z'])['y']
        self.assertAlmostEqual(a['terms']['x']['beta'],b['terms']['x']['beta'],places=10)
    def test_time_invariant_predictor_is_not_estimable(self):
        d=self.frame();d['fixed']=d.route_cluster.astype(int)
        a=absorb_fit(d,['y'],['x','z','fixed'])['y']
        self.assertIn('fixed',a['dropped_columns'])
        self.assertNotIn('fixed',a['terms'])
    def test_count_identity_and_direction(self):
        d=pd.DataFrame({'strong_new_score':[0.,7.],'strong_new_count':[0.,3.],
                        'new_ci3_count':[0.,1.],'richness_gain':[0,2],
                        'wet_only':[1,3],'dry_only':[1,1],
                        'wet_richness':[3,5],'dry_richness':[3,3]})
        self.assertTrue(validate_outcome_identities(d))
        d.loc[1,'strong_new_score']=6
        with self.assertRaises(ValueError): validate_outcome_identities(d)
    def test_layer_definition_not_chronological(self):
        d=pd.DataFrame({'soil1_w':[.3],'soil1_d':[.2],'soil2_w':[.35],'soil2_d':[.3],
             'vpd_w':[.4],'vpd_d':[.6],'rain72_w':[3.],'rain72_d':[4.],
             'air_w':[15.],'air_d':[13.]})
        x=raw_features(d)
        self.assertAlmostEqual(x.layer_common.iloc[0],.075)
        self.assertAlmostEqual(x.surface_excess.iloc[0],.05)
        self.assertAlmostEqual(x.soil_mid.iloc[0],.25)
        d.loc[0,'soil1_w']=np.nan
        with self.assertRaises(ValueError): raw_features(d)
    def test_equal_route_mse_exact_bias_variation_identity(self):
        r=np.array(['a','a','a','b']);y=np.array([1.,3,5,9]);p=np.array([0.,0,0,3])
        e=error_decomposition(y,p,r)
        self.assertAlmostEqual(e['mse'],(.5*(1+9+25)/3+.5*36))
        self.assertAlmostEqual(e['bias_squared']+e['centered_mse'],e['mse'])
        self.assertAlmostEqual(e['mean_error_y_minus_prediction'],4.5)
    def test_holm_order_invariant(self):
        self.assertTrue(np.allclose(holm([.02,.001,.6]),[.04,.003,.6]))
    def test_linear_outcome_decomposition(self):
        d=self.frame();d['a']=d.y;d['b']=d.z*3;d['net']=d.a-d.b
        f=absorb_fit(d,['a','b','net'],['x','z'])
        self.assertAlmostEqual(f['net']['terms']['x']['beta'],f['a']['terms']['x']['beta']-f['b']['terms']['x']['beta'],places=10)
if __name__=='__main__':unittest.main()
