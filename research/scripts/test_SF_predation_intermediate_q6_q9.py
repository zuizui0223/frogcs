"""Source invariants for exploratory q6/q9 80-year stochastic cohort sensitivity."""
import unittest
import numpy as np
from run_predator_edge_recruitment_80y import source_by_recruitment_regime
from run_SF_predation_intermediate_q6_q9_80y import SCALES, NETWORK_ACTIVE, NETWORKS
from finite_n_source_cohort_bridge import simulate_finite_group, summarize_finite_group
from spatial_cohort_80y_bridge import replay_gate


def group():
    s=source_by_recruitment_regime("rate12_rho0")
    x=s[(s.context=="original")&
        s.plant_model.eq("SF0_DF0_DS1_L0")&
        s.reverse_on.eq(1)].reset_index(drop=True)
    assert len(x)==8
    return x


class TrueIntermediatePopulationScaleTests(unittest.TestCase):

    def test_exact_original_source_replay(self):
        errors=replay_gate(source_by_recruitment_regime("rate12_rho0"),
                           years=4,window=2,dt=.25)
        self.assertTrue(all(x<=1e-8 for x in errors.values()))

    def test_q6_q9_valid_scales_and_non_negative_integer_mass(self):
        g=group()
        for q in SCALES:
            for arm in NETWORKS:
                for mode in ("off","both"):
                    o=simulate_finite_group(
                        g,scale=q,seed=101,mode=mode,immigration=False,
                        years=4,dt=.25,transfer=.15,
                        active_edges=NETWORK_ACTIVE[arm]
                    )
                    self.assertTrue(np.issubdtype(o["hist"].dtype,np.integer))
                    self.assertTrue((o["hist"]>=0).all())
                    self.assertFalse(o["external"].any())
                    np.testing.assert_array_equal(
                        o["arrivals"].sum(axis=2),o["departures"].sum(axis=2))
                    summary,events=summarize_finite_group(
                        g,o,scale=q,seed=101,mode=mode,
                        immigration=False,years=4
                    )
                    self.assertEqual(len(summary),8*3)
                    self.assertEqual(int(summary.n_local_returns.sum()),len(events))

    def test_q6_q9_network_definition_matches_old_default_legacy_controls(self):
        g=group()
        for q in SCALES:
            kw=dict(scale=q,seed=101,mode="both",immigration=False,
                    years=4,dt=.25,transfer=.15)
            original=simulate_finite_group(g,**kw)
            allon=simulate_finite_group(g,active_edges=("SF","DF","DS","SD"),**kw)
            off_sf=simulate_finite_group(g,edge_off="SF",**kw)
            only_rest=simulate_finite_group(g,active_edges=("DF","DS","SD"),**kw)
            for name in original:
                np.testing.assert_array_equal(original[name],allon[name])
                np.testing.assert_array_equal(off_sf[name],only_rest[name])

    def test_q6_q9_scale_is_real_stochastic_count_manipulation(self):
        g=group()
        a=simulate_finite_group(g,scale=6,seed=101,mode="both",
                               immigration=False,years=4,active_edges=("SF",))
        b=simulate_finite_group(g,scale=9,seed=101,mode="both",
                               immigration=False,years=4,active_edges=("SF",))
        self.assertFalse(np.array_equal(a["hist"][0],b["hist"][0]))
        self.assertEqual(int(b["hist"][0,0,0,0])*2,int(a["hist"][0,0,0,0])*3)


if __name__=="__main__":
    unittest.main()
