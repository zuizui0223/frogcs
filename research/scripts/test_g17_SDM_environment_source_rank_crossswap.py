"""Fixed algebra, input splitting and geographic-block pairing checks for G17."""
import unittest
import numpy as np
import pandas as pd
from g17_SDM_environment_source_rank_crossswap import (
    factorial, original_spatial_bootstrap, split_templates, PAIR_CELLS,
    N_TEMPLATES, N_NULLS, NSHARDS, N_SITE, N_BLOCK, N_VISITS, BLOCK_BOOT,
    BLOCK_SEED, ACCEPTED, SIGN_ONLY
)

class TestG17CrossedEnvironmentAndRank(unittest.TestCase):
    def test_predeclared_two_by_two_and_counts(self):
        self.assertEqual(PAIR_CELLS,(
            ("uniform","uniform"),("uniform","target_group"),
            ("target_group","uniform"),("target_group","target_group")))
        self.assertEqual(N_TEMPLATES,201)
        self.assertEqual(N_NULLS,199)
        self.assertEqual(NSHARDS,4)
        self.assertEqual(N_TEMPLATES*N_SITE*len(PAIR_CELLS),3415392)
        self.assertEqual(N_BLOCK,56)
        self.assertEqual(N_VISITS,63180)
        self.assertEqual(BLOCK_BOOT,9999)
        self.assertEqual(BLOCK_SEED,20261108)

    def test_exact_crossed_factorial_identity(self):
        d=pd.DataFrame([
            dict(env_bg="uniform",rank_bg="uniform",ABC_minus_null_gain=.6),
            dict(env_bg="uniform",rank_bg="target_group",ABC_minus_null_gain=.1),
            dict(env_bg="target_group",rank_bg="uniform",ABC_minus_null_gain=-.2),
            dict(env_bg="target_group",rank_bg="target_group",ABC_minus_null_gain=-.1),
        ])
        x=factorial(d)
        self.assertAlmostEqual(x["original_diagonal_difference"],.7)
        self.assertAlmostEqual(x["environment_main_effect"],.5)
        self.assertAlmostEqual(x["source_rank_main_effect"],.2)
        self.assertAlmostEqual(x["crossed_nonlinear_interaction"],.6)
        self.assertAlmostEqual(x["environment_fraction_of_signed_diagonal"]+
                               x["rank_fraction_of_signed_diagonal"],1)

    def test_original_199_null_ids_plus_both_controls_partition_exactly(self):
        records=[dict(candidate=f"STRAT_NULL_{i:03d}",null_id=i,
                      model_draws=794) for i in range(N_NULLS)]
        records += [dict(candidate=ACCEPTED,null_id=-1,model_draws=794),
                    dict(candidate=SIGN_ONLY,null_id=-2,model_draws=0)]
        t=pd.DataFrame(records)
        assigned=[]
        for shard in range(NSHARDS):
            sub,ids=split_templates(t,shard)
            self.assertEqual(set(sub.candidate)-{ACCEPTED,SIGN_ONLY},
                             {f"STRAT_NULL_{i:03d}" for i in ids})
            if shard==0:self.assertEqual(list(sub.candidate.tail(2)),[ACCEPTED,SIGN_ONLY])
            assigned.extend(ids)
        self.assertEqual(sorted(assigned),list(range(N_NULLS)))
        with self.assertRaises(AssertionError):
            split_templates(t,4)

    def test_shared_56block_bootstrap_cannot_change_factorial_baseline(self):
        rows=[]
        # A perfectly constant score per block gives exactly degenerate bootstrap CI.
        gain={("uniform","uniform"):1.5,
              ("uniform","target_group"):.7,
              ("target_group","uniform"):-.4,
              ("target_group","target_group"):-1.1}
        for (e,r),offset in gain.items():
            for j in range(N_BLOCK):
                rows.append(dict(candidate=ACCEPTED,env_bg=e,rank_bg=r,
                                 spatial_block=f"block{j:02d}",visits=100,
                                 total_loss=300.))
                rows.append(dict(candidate=SIGN_ONLY,env_bg=e,rank_bg=r,
                                 spatial_block=f"block{j:02d}",visits=100,
                                 total_loss=300.))
                for k in range(N_NULLS):
                    rows.append(dict(candidate=f"STRAT_NULL_{k:03d}",env_bg=e,
                                     rank_bg=r,spatial_block=f"block{j:02d}",
                                     visits=100,total_loss=300.+offset))
        t=pd.DataFrame(rows)
        est=original_spatial_bootstrap(t)
        x=est["original_diagonal_difference"]
        self.assertEqual(len(x),BLOCK_BOOT)
        self.assertTrue(np.allclose(x,(1.5-(-1.1))/100,atol=1e-12))
        self.assertTrue(np.allclose(est["environment_main_effect"]+
                                    est["source_rank_main_effect"],x,atol=1e-12))

if __name__=="__main__":
    unittest.main()
