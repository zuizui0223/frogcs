import unittest
import pandas as pd
from naamp_site_use_associations import aggregate_sites, rank_association, canonicalize_routes


class SiteUseTests(unittest.TestCase):
    def test_shared_physical_site_connects_route_labels(self):
        d=pd.DataFrame(dict(site=['x','x','y','z'],route=['a','b','b','c']))
        result,mapping=canonicalize_routes(d)
        self.assertEqual(result.route.tolist(),['a','a','a','c'])
        self.assertEqual(len(set(mapping.values())),2)

    def test_year_denominator_and_season_equal_weighting(self):
        d=pd.DataFrame(dict(site=['a']*4,route=['r']*4,year=[2001,2001,2001,2002],
                            season=[1,1,2,1],strong=[1,1,0,0],any=[1,1,1,0],noise=[1]*4,air=[10]*4))
        r=aggregate_sites(d).iloc[0]
        self.assertEqual(r.n_visits,4)
        self.assertEqual(r.strong_rate,.5)
        self.assertEqual(r.strong_year_fraction,.5)
        self.assertAlmostEqual(r.season_equal_strong_rate,1/3)
        self.assertEqual(r.n_years,2)

    def test_route_adjustment_removes_between_route_only_signal(self):
        x=[0,0,0,10,10,10]; y=[0,1,2,10,11,12]; routes=['a']*3+['b']*3
        self.assertGreater(rank_association(x,y,routes,False),.8)
        self.assertIsNone(rank_association(x,y,routes,True))

    def test_within_route_association_can_oppose_whole_sample(self):
        x=[0,1,2,10,11,12]; y=[2,1,0,12,11,10]; routes=['a']*3+['b']*3
        self.assertGreater(rank_association(x,y,routes,False),0)
        self.assertAlmostEqual(rank_association(x,y,routes,True),-1)


if __name__=='__main__':
    unittest.main()
