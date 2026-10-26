import unittest
from datetime import date
from inbo_prior_larvae_exploratory import construct, contrast, HYLA

class PriorLarvaeTest(unittest.TestCase):
    def test_temporal_join_never_fills_unsampled_species_or_sites(self):
        a = {('s',2021,HYLA):[(date(2021,5,1),'a',1)],
             ('t',2021,HYLA):[(date(2021,5,1),'b',0)]}
        l = {('s',2020,HYLA):[(date(2020,7,1),'c',0)],
             ('t',2021,HYLA):[(date(2021,7,1),'d',1)]}
        rows = construct(a,l,{'s','t'},HYLA,1)
        self.assertEqual(len(rows),1)
        self.assertEqual((rows[0]['x'],rows[0]['y']), (0,1))
        self.assertGreater(rows[0]['gap_days'],0)
        self.assertIsNone(rows[0]['history'])
        self.assertEqual(construct(a,l,{'s','t'},'unrecorded',1),[])

    def test_first_survey_and_any_differ(self):
        a = {('s',2021,HYLA):[(date(2021,5,1),'a',0),(date(2021,5,2),'b',1)]}
        l = {('s',2020,HYLA):[(date(2020,7,1),'c',1)]}
        self.assertEqual(construct(a,l,{'s'},HYLA,1)[0]['y'],1)
        self.assertEqual(construct(a,l,{'s'},HYLA,1,True)[0]['y'],0)

    def test_same_day_subsamples_are_not_separate_survey_days(self):
        a={('s',2021,HYLA):[(date(2021,5,1),'a',0),(date(2021,5,1),'b',1)]}
        l={('s',2020,HYLA):[(date(2020,7,1),'c',1)]}
        row=construct(a,l,{'s'},HYLA,1,True)[0]
        self.assertEqual(row['y'],1)
        self.assertEqual(row['adult_surveys'],1)
        self.assertEqual(row['adult_events'],2)

    def test_missing_group_is_not_zero_effect(self):
        r = contrast([{'site':'a','year':2020,'x':1,'y':0,'adult_surveys':1,'larval_surveys':1,'gap_days':300}])
        self.assertIsNone(r['difference_presence_minus_absence'])

    def test_site_replicates_and_cells(self):
        rows = [{'site':s,'year':2020+i,'x':x,'y':y,'adult_surveys':1,'larval_surveys':1,'gap_days':300}
                for s,i,x,y in [('a',0,0,0),('a',1,1,1),('b',0,0,1),('b',1,1,1)]]
        r=contrast(rows,100)
        self.assertEqual(r['difference_presence_minus_absence'],.5)
        self.assertEqual(r['within_site_exposure_switchers'],2)
        self.assertEqual(r['bootstrap_valid'],100)

if __name__ == '__main__': unittest.main()
