import unittest
from naamp_three_guild_occurrence import overlap, schoener, quality, prior_fraction, matched_history

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

if __name__=='__main__':unittest.main()
