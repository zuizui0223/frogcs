import unittest
import numpy as np
from ecology.macro_stage.scripts.analyze_gbif_macro import overlap,season,GUILDS,EDGES

class MacroStageEcology(unittest.TestCase):
    def test_exact_full_overlap(self):
        p=np.array([1]+[0]*11,dtype=float)
        self.assertEqual(overlap(p,p),1)
        self.assertEqual(overlap(p,np.roll(p,1)),0)
    def test_empty_stage_is_nonestimable_not_zero_biological_overlap(self):
        raw,adj=season(np.zeros(12),np.full(12,100))
        self.assertIsNone(raw)
        self.assertIsNone(adj)
    def test_month_order_effort_adjusted(self):
        e=np.ones(12)*100
        c=np.zeros(12);c[0]=30;c[1]=5
        p,q=season(c,e)
        self.assertAlmostEqual(p.sum(),1)
        self.assertAlmostEqual(q.sum(),1)
        self.assertGreater(q[0],q[1])
    def test_group_and_edge_types_frozen(self):
        self.assertEqual(len(EDGES),3)
        self.assertIn("frog_larva",GUILDS)
        self.assertEqual(GUILDS["odonate_larva"],("odonate_larva","odonate_nymph"))
if __name__=="__main__":unittest.main()
