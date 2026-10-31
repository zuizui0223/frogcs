"""Synthetic-only invariants for the acoustic bridge, not empirical results."""
import unittest
import numpy as np
import pandas as pd
from acoustic_mechanism_cv import (
    ARMS, BACKGROUNDS, assign_spatial_folds, extract_frozen_surfaces,
    candidate_surface, log_score, out_of_block_predictions, paired_block_interval,
    pattern_diagnostic, prepare_sites, rank_bin,
)


def fixture():
    rng = np.random.default_rng(1234)
    sites, visits = [], []
    for block in range(12):
        for site in range(8):
            ident = f's{block}_{site}'
            x = (block * 8 + site) / 96
            flooded = 30. if site % 3 == 0 else 0.
            n = 9
            k = 0
            for run in range(n):
                strong = int(rng.random() < .18 + .3*x + (flooded > 0)*.15)
                k += strong
                visits.append(dict(site=ident, run=f'{ident}-{run}', timeout=0, strong=strong,
                                   any=1 if strong or rng.random() < .2 else 0,
                                   season=1+run%4, doy=70+run*7))
            sites.append(dict(site=ident, route=f'r{block}', lat=25+2.1*block, lon=-105+site*.01,
                              strong_rate=k/n, n_visits=n, n_years=3, mean_air=10+x+rng.normal(0,1),
                              mean_noise=1+x+rng.normal(0,1), bio1=10+x+rng.normal(0,1), bio4=20+x+rng.normal(0,1), bio12=30+x+rng.normal(0,1),
                              bio15=40+x+rng.normal(0,1), water_3000m_mean=.1+x+rng.normal(0,.1),
                              herbaceous_3000m_mean=.2+x+rng.normal(0,.1),
                              flooded_3000m_mean=flooded,
                              mean_suitability_Odonata_uniform=rng.uniform(),
                              mean_suitability_pond_breeding_Caudata_uniform=rng.uniform(),
                              mean_suitability_Odonata_target_group=rng.uniform(),
                              mean_suitability_pond_breeding_Caudata_target_group=rng.uniform()))
    return pd.DataFrame(sites), pd.DataFrame(visits)


def grid_fixture():
    rows=[]
    for arm in ARMS:
        for v in (0., 1.):
            for s in np.linspace(.25,2.,21):
                for o in np.linspace(.25,2.,21):
                    rows.append(dict(arm=arm,vegetation=v,S_source=s,D_source=o,
                                     F_B=np.exp(.1 + .03*int(arm,2)+v*.15-.3*o+.2*s-.04*o*s)))
    return pd.DataFrame(rows)


class AcousticBridgeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        sites,visits=fixture()
        cls.d=prepare_sites(sites,visits,expected_sites=96)
        cls.surfaces=extract_frozen_surfaces(grid_fixture())
        cls.folds=assign_spatial_folds(cls.d)

    def test_site_ledger_and_route_block_protection(self):
        self.assertEqual(int(self.d.n.sum()), 96*9)
        self.assertEqual(self.d.groupby('route').spatial_block.nunique().max(),1)
        self.assertEqual(len(np.unique(self.folds)),5)
        self.assertEqual(self.d.assign(fold=self.folds).groupby('route').fold.nunique().max(),1)
        for fold in range(5):
            self.assertGreater(self.d.V[self.folds==fold].sum(),0)

    def test_reject_incorrect_site_visits(self):
        sites,visits=fixture()
        with self.assertRaises(ValueError):
            prepare_sites(sites,pd.concat([visits,visits.iloc[:1]]))
        bad=visits.copy();bad.loc[0,'strong']=2
        with self.assertRaises(ValueError):
            prepare_sites(sites,bad)

    def test_grid_integrity_and_predictor_only_transport(self):
        bad=grid_fixture().iloc[:-1]
        with self.assertRaises(ValueError):
            extract_frozen_surfaces(bad)
        self.assertTrue(np.all(np.diff(rank_bin(np.arange(96),21))>=0))
        values=candidate_surface(self.d,'uniform',self.surfaces)
        self.assertEqual(set(values),set(ARMS))
        for v in values.values():
            self.assertTrue(np.isfinite(v).all())

    def test_heldout_predictions_do_not_use_heldout_outcomes(self):
        a=out_of_block_predictions(self.d,self.surfaces,self.folds)
        modified=self.d.copy()
        target=self.folds==0
        modified.loc[target,'k']=modified.loc[target,'n']-modified.loc[target,'k']
        b=out_of_block_predictions(modified,self.surfaces,self.folds)
        qa=a[a.fold==0].sort_values(['background','candidate','site'])
        qb=b[b.fold==0].sort_values(['background','candidate','site'])
        np.testing.assert_allclose(qa.predicted,qb.predicted,rtol=0,atol=1e-13)
        self.assertEqual(len(a),len(self.d)*len(BACKGROUNDS)*(len(ARMS)+2))
        self.assertTrue(a.predicted.between(0,1,inclusive='neither').all())

    def test_paired_scores_and_observed_pattern(self):
        predictions=out_of_block_predictions(self.d,self.surfaces,self.folds)
        scores,foldscores=paired_block_interval(predictions,reps=199)
        self.assertEqual(len(scores),len(BACKGROUNDS)*(len(ARMS)+2))
        self.assertEqual(len(foldscores),len(scores)*5)
        self.assertTrue(scores.nll_per_survey.between(0,np.inf,inclusive='neither').all())
        self.assertTrue(scores[scores.candidate.isin(ARMS)].gain_low_conditional.notna().all())
        diag=pattern_diagnostic(self.d,predictions)
        self.assertEqual(len(diag),len(scores)+2)
        self.assertTrue(np.isfinite(diag[['OV','OS','SV','OSV']].to_numpy()).all())
        np.testing.assert_allclose(log_score([1,0],[1,1],[.8,.3]),[-np.log(.8),-np.log(.7)])


if __name__ == '__main__':
    unittest.main()
