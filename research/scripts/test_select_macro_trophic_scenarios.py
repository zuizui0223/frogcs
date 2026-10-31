"""Synthetic-only smoke tests; never treat fixtures as ecological observations."""
import itertools
import unittest

import numpy as np
import pandas as pd

from select_macro_trophic_scenarios import (
    CONTEXTS, EDGES, FAMILIES, LEVELS, NULLS, SEED,
    assign_folds, candidate_scores_at_sites, fixed_nested_comparison,
    load_cohort, neglog, observed_pattern_diagnostic, predictor_design,
    rank_bin, scenario_surfaces, score_selected, select_one_outer
)


def test_sites(block_count=15, sites_per_block=6):
    rng=np.random.default_rng(343343)
    sites=[];visits=[]
    for b in range(block_count):
        for p in range(sites_per_block):
            tag=f"site-{b}-{p}";n=8;succ=0
            for j in range(n):
                strong=int(rng.random()<.15+.3*b/block_count+.12*(p%2==0))
                succ+=strong
                visits.append(dict(site=tag,run=f"{tag}-{j}",timeout=0,strong=strong,
                                   any=int(strong or rng.random()<.4),
                                   season=j%4+1,doy=50+7*j))
            row=dict(site=tag,route=f"route-{b}",lat=26+2.1*b,lon=-110+.07*p,
                     n_visits=n,n_years=3,strong_rate=succ/n,
                     mean_air=rng.normal(10,2),mean_noise=rng.normal(2,1),
                     bio1=rng.normal(5,3),bio4=rng.normal(9,2),
                     bio12=rng.normal(7,1),bio15=rng.normal(4,1),
                     water_3000m_mean=rng.uniform(),herbaceous_3000m_mean=rng.uniform(),
                     flooded_3000m_mean=40 if p%2==0 else 0.)
            for bg in ("uniform","target_group"):
                row[f"mean_suitability_Odonata_{bg}"]=rng.uniform(.05,.95)
                row[f"mean_suitability_pond_breeding_Caudata_{bg}"]=rng.uniform(.05,.95)
            sites.append(row)
    return pd.DataFrame(sites),pd.DataFrame(visits)


def source_fixture():
    records=[];i=0
    for context,family,risk,edge in itertools.product(CONTEXTS,FAMILIES,(False,True),EDGES):
        for v,s,d in itertools.product((0.,1.),np.linspace(.25,2.,LEVELS),np.linspace(.25,2.,LEVELS)):
            f=1.+.05*i+.01*s-.02*d + .07*v + .01*(s-.5)*(d-.5) + (edge=="frog_reverse")*.03*s
            records.append(dict(case=i,context=context,family=family,risk=risk,edge=edge,
                                vegetation=v,S_source=s,D_source=d,F_B=f))
        i+=1
    return pd.DataFrame(records)


class ScenarioSelectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        sites,visits=test_sites()
        cls.data=load_cohort(sites,visits,expected=90)
        cls.cells=source_fixture()
        cls.surfaces,cls.meta=scenario_surfaces([cls.cells])
        cls.folds=assign_folds(cls.data,5)

    def test_all_24_scenarios_and_grid_errors(self):
        self.assertEqual(len(self.surfaces),24)
        self.assertEqual(len(self.meta),24)
        bad=self.cells.iloc[1:]
        with self.assertRaises(ValueError):
            scenario_surfaces([bad])
        duplicate=pd.concat([self.cells,self.cells.iloc[:1]])
        with self.assertRaises(ValueError):
            scenario_surfaces([duplicate])
        self.assertTrue(np.all(np.diff(rank_bin(np.arange(90)))>=0))

    def test_cohort_ledger_and_spatial_fold_independence(self):
        self.assertEqual(int(self.data.n.sum()),90*8)
        self.assertEqual(self.data.spatial_block.nunique(),15)
        self.assertEqual(len(np.unique(self.folds)),5)
        frame=self.data.assign(fold=self.folds)
        self.assertEqual(frame.groupby("route").fold.nunique().max(),1)
        for fold in range(5):
            self.assertGreater(frame.loc[frame.fold==fold,"V"].sum(),0)
        sites,visits=test_sites()
        with self.assertRaises(ValueError):
            load_cohort(sites,pd.concat([visits,visits.iloc[:1]]))
        with self.assertRaises(ValueError):
            load_cohort(sites,visits.iloc[1:])

    def test_observation_link_is_not_responding_to_outer_holdout_labels(self):
        bg="uniform"
        surface=candidate_scores_at_sites(self.data,bg,self.surfaces)
        design=predictor_design(self.data,bg,surface)
        shortlist=list(sorted(self.surfaces))[:3]
        a,ai,ac=select_one_outer(self.data,design,self.folds,outer=0,
                                  restrict_candidates=shortlist)
        changed=self.data.copy();held=self.folds==0
        changed.loc[held,"k"]=changed.loc[held,"n"]-changed.loc[held,"k"]
        b,bi,bc=select_one_outer(changed,design,self.folds,outer=0,
                                  restrict_candidates=shortlist)
        pd.testing.assert_frame_equal(ai,bi)
        self.assertEqual(ac["selected_scenario"],bc["selected_scenario"])
        self.assertEqual(ac["selected_null"],bc["selected_null"])
        pd.testing.assert_series_equal(a.predicted,b.predicted)
        self.assertTrue(a.predicted.between(0,1,inclusive="neither").all())

    def test_nested_comparison_and_alternative_benchmarks(self):
        shortlist=list(sorted(self.surfaces))[:3]
        p,inner,choices=fixed_nested_comparison(self.data,self.surfaces,self.folds,shortlist)
        self.assertEqual(len(choices),10)
        self.assertEqual(len(inner),10*(3+2))
        self.assertEqual(len(p),90*2*3)
        self.assertTrue(choices.selected_scenario.isin(shortlist).all())
        self.assertTrue(choices.selected_null.isin(NULLS).all())
        summary,gains=score_selected(p,choices,reps=39)
        self.assertEqual(len(summary),2*4)
        self.assertEqual(len(gains),2*3)
        self.assertTrue(np.isfinite(gains.gain_high_conditional).all())
        diagnostic=observed_pattern_diagnostic(self.data,p,choices)
        self.assertEqual(len(diagnostic),10)
        self.assertTrue(np.isfinite(diagnostic[["OS","OV","SV","OSV"]].to_numpy()).all())
        self.assertTrue((gains.n_visits==90*8).all())
        self.assertAlmostEqual(float(neglog(np.array([1,0]),np.array([1,1]),np.array([.9,.2])).sum()),
                               -np.log(.9)-np.log(.8))

    def test_transport_remains_outcome_blind(self):
        a=candidate_scores_at_sites(self.data,"uniform",self.surfaces)
        changed=self.data.copy()
        changed["k"]=changed.n-changed.k
        b=candidate_scores_at_sites(changed,"uniform",self.surfaces)
        for case in a:
            np.testing.assert_array_equal(a[case],b[case])


if __name__=="__main__":
    unittest.main()
