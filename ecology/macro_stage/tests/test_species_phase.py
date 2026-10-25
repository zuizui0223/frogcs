import unittest
import numpy as np
from ecology.macro_stage.scripts.macro_species_phase_sensitivity import overlap_and_excess,year_by_year,species_balanced,STAGES
from collections import defaultdict

class StagePhenologyMacroNegativeControls(unittest.TestCase):
    def test_phase_null_same_month_concordance(self):
        frog=np.array([1]+[0]*11)
        egg=np.array([1]+[0]*11)
        obs,excess=overlap_and_excess(frog,egg)
        self.assertAlmostEqual(obs,1.)
        self.assertAlmostEqual(excess,11/12)
    def test_uniform_stage_is_phase_indifferent(self):
        frog=np.ones(12)
        egg=np.array([0,1]+[0]*10)
        obs,excess=overlap_and_excess(frog,egg)
        self.assertAlmostEqual(excess,0,places=12)
    def test_missing_yearly_data_are_not_zero_overlap(self):
        b=defaultdict(lambda:np.zeros(12,int))
        self.assertEqual(year_by_year(b),[])
    def test_species_replication_requires_three_species_per_group(self):
        b={}
        for t in STAGES:
            for i in range(2):b[("US35_40",t,str(i))]=np.array([10,10]+[0]*10)
        self.assertEqual(species_balanced(b),[])
if __name__=="__main__":unittest.main()
