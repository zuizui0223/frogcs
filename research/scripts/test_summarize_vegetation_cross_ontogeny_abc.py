"""Synthetic controls for matched biological-rate stage×vegetation ABC.

These tests validate structure and paired bootstrap algebra, not whether the
four main macro-sign associations are biologically causal in the field.
"""
import unittest
import numpy as np
import pandas as pd

from run_vegetation_cross_ontogeny_80y import (
    CONTEXTS,FAMILIES,N_DRAWS
)
from model_native_vegetation_abc import legal_plant_inventory
from summarize_vegetation_cross_ontogeny_abc import (
    N_CLASSES,N_RAW_MODELS,class_draw_matrix,marginalize_sources,
    paired_vegetation_differences
)


def fake_all_stage_sources():
    roles=legal_plant_inventory()
    rows=[]
    for context in CONTEXTS:
        for family in FAMILIES:
            for risk in (False,True):
                for r in roles.itertuples(index=False):
                    label=f"{context}__{family}__risk{int(risk)}__{r.plant_model}"
                    for draw in np.arange(0,256,4):
                        for reverse in (0,1):
                            # Synthetic repeated positive matches only under
                            # frog shelter + litter: simulates a pathway effect.
                            yes=bool(r.cover_SF and r.litter)
                            records=dict(structure_id=label,context=context,
                                family=family,risk=risk,plant_model=r.plant_model,
                                draw=int(draw),reverse_on=reverse,
                                cover_SF=int(r.cover_SF),cover_DF=int(r.cover_DF),
                                cover_DS=int(r.cover_DS),litter=int(r.litter),
                                matches_log=yes,matches_raw=bool(r.litter))
                            for scale in ("log","raw"):
                                for term in ("OS","OV","SV","OSV"):
                                    records[f"beta_{scale}_{term}"]=float(
                                        int(r.litter)+.3*int(r.cover_SF)-
                                        .15*int(r.cover_DF)+.05*int(r.cover_DS))
                            rows.append(records)
    return pd.DataFrame(rows)


class CrossStageVegetationAggregationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.x=fake_all_stage_sources()

    def test_complete_144x64x2_factorial_and_paired_4bit_acceptance(self):
        x=self.x
        self.assertEqual(len(x),N_RAW_MODELS)
        self.assertEqual(x.structure_id.nunique(),N_CLASSES)
        mat=class_draw_matrix(x,"log")
        self.assertEqual(mat.shape,(N_DRAWS,N_CLASSES))
        self.assertTrue(mat.isin((0,1)).all().all())
        for role in ("SF1_DF0_DS0_L1","SF1_DF0_DS1_L1"):
            labels=[z for z in mat.columns if z.endswith(role)]
            self.assertEqual(len(labels),12)
            self.assertTrue(mat[labels].eq(1).all().all())

    def test_abc_marginal_probs_and_stage_specific_plant_roles(self):
        models,marginals,conditional=marginalize_sources(self.x,n_boot=99)
        self.assertEqual(len(models),N_CLASSES*2)
        self.assertEqual(models.n_original_rate_vectors.nunique(),1)
        self.assertEqual(int(models.n_original_rate_vectors.iloc[0]),64)
        self.assertTrue(models.groupby("scale").conditional_model_share.sum().between(
            .9999999,1.0000001).all())
        for (scale,dimension),g in marginals.groupby(["scale","dimension"]):
            self.assertAlmostEqual(float(g.conditional_share.sum()),1.,places=9)
        self.assertEqual(len(conditional),2*3*2*12)
        self.assertTrue(conditional.n_original_rate_draws.eq(64).all())
        self.assertTrue(conditional[conditional.scale=="log"].
                        conditional_plant_share.dropna().between(0,1).all())

    def test_plant_shelter_and_litter_paired_mean_effects_recovered(self):
        differences,summary=paired_vegetation_differences(self.x,n_boot=99)
        self.assertEqual(len(summary),2*3*2*4)
        self.assertTrue(summary.n_independent_draws.eq(64).all())
        self.assertTrue(differences.delta_acceptance.between(-1,1).all())
        a=summary[(summary.scale=="log")&(summary.plant_axis=="cover_SF")]
        self.assertTrue(a.paired_mean_acceptance_gain.gt(0).all())
        b=summary[(summary.scale=="log")&(summary.plant_axis=="litter")]
        self.assertTrue(b.paired_mean_acceptance_gain.gt(0).all())
        c=summary[(summary.scale=="log")&(summary.plant_axis=="cover_DF")]
        self.assertTrue(c.paired_mean_acceptance_gain.eq(0).all())

    def test_unpaired_reverse_or_rate_draw_fails_closed(self):
        a=self.x.iloc[:-1]
        with self.assertRaises(AssertionError):
            class_draw_matrix(a,"log")
        with self.assertRaises(AssertionError):
            paired_vegetation_differences(a,n_boot=99)
        bad=self.x.drop_duplicates(["structure_id","draw"],keep="first")
        with self.assertRaises(AssertionError):
            class_draw_matrix(bad,"log")


if __name__=="__main__":
    unittest.main()
