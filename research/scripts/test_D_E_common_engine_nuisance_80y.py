"""Fail-closed source checks for ONE D+E model and its original 80y outputs."""
import unittest
import numpy as np
import pandas as pd

from run_D_E_common_engine_nuisance_80y import (
    biological_cube,score_model_native_four_signs,NETWORKS,NETWORK_OPTIONS,
    RATE_IDS,CONTEXTS,PLANTS
)
from finite_n_source_cohort_bridge import (
    simulate_finite_group,summarize_finite_group
)
from spatial_cohort_80y_bridge import replay_gate


class CommonEngineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cube=biological_cube()
        cls.group=cls.cube[
            (cls.cube.context=="original") &
            (cls.cube.plant_model=="SF0_DF0_DS1_L0") &
            (cls.cube.draw==0)
        ].sort_values("vertex").reset_index(drop=True)

    def test_source_full_shared_structure_rate_vertices(self):
        a=self.cube
        self.assertEqual(len(a),2*2*4*8)
        self.assertEqual(set(a.draw),set(RATE_IDS))
        self.assertEqual(set(a.context),set(CONTEXTS))
        self.assertEqual(set(a.plant_model),set(PLANTS))
        self.assertTrue(a.reverse_on.eq(0).all())
        self.assertTrue(a.da.eq(0).all())
        self.assertTrue(a.sa.eq(20).all())
        for _,g in a.groupby(["structure_id","draw"]):
            self.assertEqual(set(g.vertex),set(range(8)))

    def test_same_original_source_deterministic_four_year_replay(self):
        errors=replay_gate(self.cube,years=4,window=2,dt=.25)
        self.assertTrue(all(v<=1e-8 for v in errors.values()))

    def test_original_no_SF_equivalent_to_only_other_three(self):
        for q in (3,12):
            kw=dict(scale=q,seed=101,mode="both",immigration=False,
                    years=4,dt=.25,transfer=.15)
            x=simulate_finite_group(self.group,**kw,edge_off="SF")
            y=simulate_finite_group(self.group,**kw,
                active_edges=("DF","DS","SD"))
            for key in x:
                np.testing.assert_array_equal(x[key],y[key])

    def test_all_networks_actual_one_source_shard_and_exact_return_mass(self):
        for name in NETWORKS:
            z=simulate_finite_group(
                self.group,scale=3,seed=101,mode="recruits",
                immigration=False,years=4,dt=.25,transfer=.15,
                **NETWORK_OPTIONS[name])
            f,e=summarize_finite_group(
                self.group,z,scale=3,seed=101,mode="recruits",
                immigration=False,years=4)
            self.assertEqual(len(f),8*3)
            self.assertEqual(len(e),int(f.n_local_returns.sum()))
            self.assertTrue(f.n_external_immigrants.eq(0).all())
            self.assertTrue((z["hist"]>=0).all())
            self.assertTrue(np.issubdtype(z["hist"].dtype,np.integer))
            np.testing.assert_array_equal(
                z["arrivals"].sum(axis=2),z["departures"].sum(axis=2))
            if len(e):
                self.assertFalse(e.cause_label.eq("unclassified").any())

    def test_raw_and_log1p_effects_are_model_native_not_field_statistics(self):
        # Construct exactly 8 V×S×D source vertices with 4 genuine
        # factorial directions. This is an algebraic control, not data.
        a=self.group.copy()
        y=[]
        for v,s,d in ((v,s,d) for v in (0,1) for s in (0,1) for d in (0,1)):
            y.append(4-.5*d*s-.4*v*d+.3*v*s+.2*v*s*d)
        a["mean_cohort_B_last_window"]=y
        a["final_occupied_patches"]=4
        a["n_local_returns"]=0
        a["n_local_extinctions"]=0
        a["network"]="all_active"
        a["scale"]=3
        a["seed"]=101
        a["movement"]="off"
        score=score_model_native_four_signs(a)
        self.assertEqual(len(score),1)
        self.assertTrue(bool(score.matches_raw.iat[0]))
        self.assertTrue(bool(score.matches_log1p.iat[0]))
        a.loc[a.vertex==7,"mean_cohort_B_last_window"]=0
        score2=score_model_native_four_signs(a)
        self.assertTrue(np.isfinite(
            score2[[c for c in score2.columns if c.startswith("beta_")]].values
        ).all())
        self.assertEqual(int(score2.n_f_vertices_zero.iat[0]),1)

    def test_q_and_mobility_definitions_are_original_source_not_stage_movement(self):
        self.assertEqual(set(NETWORKS),{
          "all_active","SF_only","no_SF","no_DF","no_DS","all_off"})
        self.assertEqual(set(RATE_IDS),{0,4,8,12})


if __name__=="__main__":
    unittest.main()
