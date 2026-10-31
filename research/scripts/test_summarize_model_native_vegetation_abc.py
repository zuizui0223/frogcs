"""Synthetic source tests for pilot vegetation-role matched ABC aggregation."""
import unittest

import numpy as np
import pandas as pd

from model_native_vegetation_abc import legal_plant_inventory
from summarize_model_native_vegetation_abc import (
    N_DRAWS,bootstrap_abc,paired_role_effects,class_draw_matrix
)


def synthetic_reference():
    rec=[]
    for role in legal_plant_inventory().to_dict("records"):
        for risk in (False,True):
            for draw in range(N_DRAWS):
                for edge in (0,1):
                    sf,df,ds,litter=[int(role[x]) for x in (
                        "cover_SF","cover_DF","cover_DS","litter")]
                    # Deliberately invented output for checking exact pairing:
                    # log match iff frog shelter from S; raw match iff litter ON.
                    record=dict(structure_id=f"original__baseline__risk{int(risk)}__"+
                                role["plant_model"],
                                plant_model=role["plant_model"],risk=risk,
                                draw=draw,reverse_on=edge,
                                cover_SF=sf,cover_DF=df,cover_DS=ds,litter=litter,
                                matches_log=bool(sf),matches_raw=bool(litter))
                    for scale in ("log","raw"):
                        for metric in ("OS","OV","SV","OSV"):
                            record[f"beta_{scale}_{metric}"]=float(
                                1.+sf*1.5+df*.5+ds*.3+litter*.2)
                    rec.append(record)
    return pd.DataFrame(rec)


class PlantABCAggregatorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ref=synthetic_reference()

    def test_all_model_states_and_exact_shared_rate_edges_are_kept(self):
        a=self.ref
        self.assertEqual(len(a),12*2*64*2)
        c,ids,m=class_draw_matrix(a,"log")
        self.assertEqual(len(c),24)
        self.assertEqual(len(ids),64)
        self.assertEqual(m.shape,(64,24))
        self.assertTrue(np.isin(m,[0.,1.]).all())

    def test_abc_shares_and_paired_rate_draw_confidence(self):
        model,plants=bootstrap_abc(self.ref,99)
        self.assertEqual(len(model),24*2)
        self.assertEqual(len(plants),12*2)
        self.assertTrue(model.groupby("scale").conditional_abc_share.sum().between(
            .999999,1.000001).all())
        self.assertTrue(plants.groupby("scale").conditional_abc_plant_share.sum().between(
            .999999,1.000001).all())
        self.assertEqual(int(model.n_independent_rate_draws.max()),64)
        expected=model[(model.scale=="log")&(model.cover_SF==1)]
        self.assertTrue(expected.acceptance.eq(1).all())
        denied=model[(model.scale=="log")&(model.cover_SF==0)]
        self.assertTrue(denied.acceptance.eq(0).all())

    def test_paired_ablation_only_with_legal_main_combinations(self):
        log,summary=paired_role_effects(self.ref,"log")
        self.assertEqual(set(summary.plant_axis),
                         {"cover_SF","cover_DF","cover_DS","litter"})
        self.assertTrue(summary.n_independent_draws.eq(64).all())
        self.assertEqual(float(summary.loc[
            summary.plant_axis=="cover_SF","mean_acceptance_gain"].iloc[0]),1.)
        self.assertEqual(float(summary.loc[
            summary.plant_axis=="litter","mean_acceptance_gain"].iloc[0]),0.)
        self.assertTrue(log[log.axis=="litter"].cover_DF.eq(0).all())
        self.assertTrue(log[log.axis=="cover_DF"].litter.eq(0).all())
        raw,rawsumm=paired_role_effects(self.ref,"raw")
        self.assertEqual(float(rawsumm.loc[
            rawsumm.plant_axis=="litter","mean_acceptance_gain"].iloc[0]),1.)
        self.assertTrue(np.isfinite(raw[["gain_acceptance","delta_beta_OS"]]).all().all())


    def test_256_bootstrap_uses_the_entire_rate_draw_index_not_just_first64(self):
        # Regression test: if the old hardcoded 0..63 bootstrap index is used,
        # a group with early 64 acceptances is spuriously assigned rate 1
        # instead of the real 64/256, and the CI misses the point estimate.
        sections=[self.ref.assign(draw=self.ref.draw+64*i)
                  for i in range(4)]
        full=pd.concat(sections,ignore_index=True)
        mask=(full.plant_model=="SF1_DF0_DS0_L1")&(full.risk==False)
        full.loc[mask,"matches_log"]=(full.loc[mask,"draw"]<64)
        table,_=bootstrap_abc(full,n_boot=399,n=256)
        row=table[(table.scale=="log")&
                  (table.plant_model=="SF1_DF0_DS0_L1")&
                  (table.risk==False)]
        self.assertEqual(len(row),1)
        x=row.iloc[0]
        self.assertAlmostEqual(x.acceptance,.25)
        self.assertLess(x.acceptance_boot_ci_low,.25)
        self.assertGreater(x.acceptance_boot_ci_high,.25)
        self.assertLess(x.acceptance_boot_ci_high,.40)

    def test_lost_partner_is_fatal_not_silently_averaged(self):
        r=self.ref.iloc[:-1]
        with self.assertRaises((AssertionError,ValueError)):
            paired_role_effects(r,"log")
        with self.assertRaises((AssertionError,ValueError)):
            class_draw_matrix(r,"log")


if __name__=="__main__":
    unittest.main()
