"""Verify frozen trilinear site emission and real observational source estimands."""
import unittest

import numpy as np
import pandas as pd

from D_E_same_theta_4248_site_proxy_POM import (
    original_sites,trilinear_source_site_weights,VERTICES
)
from pattern_oriented_abc_pilot import get_design,stats_from_y,compare_frozen_macro


class ActualSourceFcohortEmissionChecks(unittest.TestCase):
    def test_frozen_trilinear_weights_are_convex_and_exact_at_vertices(self):
        # Three repeated source-rank predictors, original V flags alternate.
        d=pd.DataFrame(dict(V=[0,0,1,1],
            mean_suitability_Odonata_uniform=[1,2,3,4],
            mean_suitability_pond_breeding_Caudata_uniform=[2,4,1,3]))
        weights=trilinear_source_site_weights(d,"uniform")
        self.assertEqual(weights.shape,(4,8))
        np.testing.assert_allclose(weights.sum(axis=1),1,rtol=0,atol=1e-12)
        self.assertTrue((weights>=0).all())
        for i in range(len(d)):
            for j,(v,s,o) in enumerate(VERTICES):
                if v!=d.V.iat[i]:self.assertEqual(weights[i,j],0.)
        predicted=weights@np.arange(8,dtype=float)
        self.assertTrue(np.isfinite(predicted).all())
        self.assertTrue((predicted>=0).all())
        self.assertTrue((predicted<=7).all())

    def test_vegetation_off_sites_are_not_interpolated_to_vegetation_on(self):
        d=pd.DataFrame(dict(V=[0,0,1,1],
            mean_suitability_Odonata_target_group=[1,2,3,4],
            mean_suitability_pond_breeding_Caudata_target_group=[4,3,2,1]))
        w=trilinear_source_site_weights(d,"target_group")
        F=np.asarray([1.,1.,1.,1.,8.,8.,8.,8.])
        np.testing.assert_allclose(w@F,np.asarray([1,1,8,8]),atol=1e-12)

    def test_real_four_thousand_sites_and_exact_original_six_statistic_definitions(self):
        d=original_sites()
        self.assertEqual(len(d),4248)
        self.assertEqual(int(d.n.sum()),63180)
        for background in ("uniform","target_group"):
            w=trilinear_source_site_weights(d,background)
            self.assertEqual(w.shape,(4248,8))
            np.testing.assert_allclose(w.sum(axis=1),1,rtol=0,atol=1e-12)
            observed=stats_from_y(d.strong_rate,get_design(d,background))
            self.assertEqual(len(observed),6)
            self.assertTrue(np.isfinite(observed).all())
            compare_frozen_macro(observed,background)

    def test_invalid_nonbiological_vegetation_source_rejected(self):
        d=pd.DataFrame(dict(V=[-1,1,2],
            mean_suitability_Odonata_uniform=[1,2,3],
            mean_suitability_pond_breeding_Caudata_uniform=[1,2,3]))
        with self.assertRaises(ValueError):
            trilinear_source_site_weights(d,"uniform")


if __name__=="__main__":
    unittest.main()
