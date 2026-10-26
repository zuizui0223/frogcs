import unittest
from naamp_three_guild_occurrence import overlap, schoener, quality, prior_fraction, matched_history, matched_history_all, summaries, overlay_occurrences

class Patterns(unittest.TestCase):
    def test_overlap(self):
        self.assertEqual(overlap({1,2},{2,3})['jaccard'],1/3)
        self.assertIsNone(overlap(set(),set())['jaccard'])
    def test_schoener(self):
        self.assertAlmostEqual(schoener([1,1],[0,2]),.5)
        self.assertEqual(schoener([2,0],[0,2]),0)
        self.assertIsNone(schoener([0,0],[1,0]))
    def test_stage_not_gate_and_unknown_precision_separate(self):
        self.assertEqual(quality({'coordinateUncertaintyInMeters':100,'lifeStage':None}),'strict')
        self.assertEqual(quality({}),'unknown')
        self.assertEqual(quality({'coordinateUncertaintyInMeters':2000}),'exclude')
    def test_history_strictly_past_same_season(self):
        rows=[dict(year=2007,season='2',strong=1),dict(year=2008,season='2',strong=0),dict(year=2009,season='2',strong=1),dict(year=2006,season='1',strong=1)]
        self.assertEqual(prior_fraction(rows,2009,'2'),(2,.5))
    def test_matched_history(self):
        rows=[dict(run='x',route='r',site='a',strong=1,any=1,prior_n=2,prior=.8,env=[1,5]),dict(run='x',route='r',site='b',strong=0,any=0,prior_n=2,prior=.2,env=[5,8])]
        self.assertAlmostEqual(matched_history(rows)[0]['history_difference'],.6)
        rows[1]['any']=1
        self.assertEqual(matched_history(rows),[])
    def test_unknown_month_stays_in_spatial_and_annual(self):
        records={g:dict(id=g,guild=g,species=g,species_key=g,year=2010,month=None,quality='strict',dataset='x',stage_raw='') for g in ('Anura','Caudata','Odonata')}
        members=[dict(center='c',id=g,distance_km=1) for g in records]
        queries=[dict(center='c',guild=g,status='COMPLETE') for g in records]
        result=summaries(records,members,queries,{'c':[0,0]})[0]
        self.assertEqual(result['three_guild_centers'],1)
        self.assertEqual(result['three_guild_center_year_months'],0)
        self.assertEqual(result['pairs'][0]['neighborhood_year']['jaccard'],1)
    def test_overlay_same_month_and_prior_never_future(self):
        records={str(y):dict(id=str(y),guild='Caudata',species='Test species',species_key=str(y),year=y,month=6,quality='strict') for y in (2007,2008,2009)}
        members=[dict(center='c',id=k,distance_km=3) for k in records]
        queries=[dict(center='c',status='COMPLETE')]
        out=overlay_occurrences(records,members,queries,[dict(site='c',year=2008,month=6,source_taxa='Test species')])[0]
        self.assertEqual(out['Caudata_prior_years_recorded_species'],1)
        self.assertEqual(out['Caudata_same_month_recorded_species'],1)
        self.assertEqual(out['same_month_exact_name_naamp_gbif_matches'],1)
    def test_environment_matching_disjoint_and_history_blind(self):
        common=dict(run='r',route='x',prior_n=3,env=[0,0],noise=0,timeout=0,air=20)
        rows=[dict(common,site='a',any=1,strong=1,prior=.9),dict(common,site='b',any=1,strong=1,prior=.1),dict(common,site='c',any=0,strong=0,prior=.8)]
        result=matched_history_all(rows)
        self.assertEqual(len(result),1)
        self.assertEqual(result[0]['chosen_site'],'a')
        rows[0]['prior']=0;rows[1]['prior']=1
        self.assertEqual(matched_history_all(rows)[0]['chosen_site'],'a')

if __name__=='__main__':unittest.main()
