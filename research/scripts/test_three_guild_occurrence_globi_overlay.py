import unittest
from three_guild_occurrence_globi_overlay import edge_overlap, source_sets

class Overlay(unittest.TestCase):
    def test_unknown_month_not_false_contact(self):
        r=edge_overlap({('x',2008,None)},{('x',2008,None)})
        self.assertEqual(r['shared_center_years'],1);self.assertEqual(r['shared_center_year_months'],0)
    def test_identity_and_spatial_precision(self):
        records={'a':dict(species_key='1',quality='strict',year='2008',month='6')}
        members=[dict(id='a',center='x',distance_km=10)]
        self.assertEqual(len(source_sets(records,members,5)),0)
        self.assertEqual(source_sets(records,members,25)['1'],{('x',2008,6)})

if __name__=='__main__':unittest.main()
