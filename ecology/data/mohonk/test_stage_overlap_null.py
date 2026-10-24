import unittest
from ecology.data.mohonk.analyze_stage_overlap_null import fixed_marginal_pmf,circular_pmf,summarize_groups
import numpy as np

class StageOverlapExactNull(unittest.TestCase):
    def test_n3_single_stage_each_has_one_third_cooccurrence_probability(self):
        a=[True,False,False];b=[True,False,False]
        p=fixed_marginal_pmf(a,b)
        self.assertTrue(np.allclose(p,[2/3,1/3]))
        self.assertTrue(np.allclose(circular_pmf(a,b),[2/3,1/3]))
    def test_all_dates_positive_is_deterministic(self):
        a=[True]*5;b=[True,True,False,True,False]
        self.assertTrue(np.allclose(fixed_marginal_pmf(a,b),[0,0,0,1]))
    def test_exactly_two_group_convolution(self):
        g=[{"frog":np.array([True,False,False]),"partner":np.array([True,False,False]),"joint":1}]*2
        r=summarize_groups(g)
        self.assertEqual(r["observed"],2)
        self.assertAlmostEqual(r["expected"],2/3,places=6)
        self.assertAlmostEqual(r["conditional_one_sided_upper_tail"],1/9,places=7)
    def test_never_impute_unassessed_to_false(self):
        from ecology.data.mohonk.analyze_stage_overlap_null import stage_sequences,WOOD,SPOT
        raw=[
            {"eventDate":"2019-04-01","decimalLatitude":"40","decimalLongitude":"-70","scientificName":WOOD,"lifeStage":"tadpole","individualCount":"1"},
            {"eventDate":"2019-04-02","decimalLatitude":"40","decimalLongitude":"-70","scientificName":WOOD,"lifeStage":"tadpole","individualCount":"0"},
            {"eventDate":"2019-04-02","decimalLatitude":"40","decimalLongitude":"-70","scientificName":SPOT,"lifeStage":"egg","individualCount":"1"}]
        g,_,_=stage_sequences(raw,SPOT)
        self.assertEqual(len(g),1)
        self.assertEqual(len(next(iter(g.values()))),1)
    def test_marginals_never_break(self):
        a=[True,True,False,False,False,False];b=[True,False,True,False,False,False]
        p=fixed_marginal_pmf(a,b)
        self.assertAlmostEqual(sum(p),1,places=12)
        self.assertEqual(len(p),3)

if __name__=="__main__":
    unittest.main()
