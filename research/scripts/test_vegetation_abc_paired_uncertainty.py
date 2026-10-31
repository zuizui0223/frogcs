"""Synthetic checks for full-256-rate paired vegetation role intervals."""
import unittest

import pandas as pd
import numpy as np

from test_summarize_model_native_vegetation_abc import synthetic_reference
from summarize_model_native_vegetation_abc import paired_role_effects
from vegetation_abc_paired_uncertainty import (
    paired_draw_interval,factorial_subgroup_stats,structural_ablation_interaction
)


class VegetationPairedBootstrapTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        source=synthetic_reference()
        cls.source=pd.concat([source.assign(draw=source.draw+64*k)
                              for k in range(4)],ignore_index=True)
        cls.pairs=pd.concat([paired_role_effects(cls.source,scale)[0]
                             for scale in ("log","raw")],ignore_index=True)

    def test_every_role_uses_all_256_real_rate_draws_not_4096_independent_units(self):
        effect=factorial_subgroup_stats(self.pairs)
        main=effect[(effect.grouping=="all_legal_pairs")&
                    (effect.endpoint=="gain_acceptance")]
        self.assertEqual(len(main),8)
        self.assertTrue(main.n_independent_rate_draws.eq(256).all())
        sf=main[(main.scale=="log")&(main.plant_axis=="cover_SF")].iloc[0]
        self.assertAlmostEqual(sf["mean"],1.)
        self.assertAlmostEqual(sf.lower,1.)
        self.assertAlmostEqual(sf.upper,1.)
        lit=main[(main.scale=="raw")&(main.plant_axis=="litter")].iloc[0]
        self.assertAlmostEqual(lit["mean"],1.)
        self.assertAlmostEqual(lit.lower,1.)

    def test_plant_pathway_interactions_are_matched_on_same_rate_draws(self):
        for scale,plant,modifier in [("log","cover_SF","litter"),
                                     ("log","cover_DS","litter"),
                                     ("raw","litter","cover_SF"),
                                     ("raw","litter","cover_DS")]:
            q=structural_ablation_interaction(self.pairs,scale,plant,modifier)
            self.assertEqual(q.draw.nunique(),256)
            self.assertTrue(np.isfinite(q.delta_of_on_off_gain).all())
            self.assertAlmostEqual(q.delta_of_on_off_gain.mean(),0.)
        with self.assertRaises(ValueError):
            structural_ablation_interaction(self.pairs,"log","litter","cover_DF")

    def test_missing_independent_rate_draw_is_rejected(self):
        x=self.pairs[(self.pairs.scale=="log")&(self.pairs.axis=="cover_SF")]
        with self.assertRaises(ValueError):
            paired_draw_interval(x[x.draw!=255])
        self.assertEqual(len(paired_draw_interval(x)),5)


if __name__=="__main__":
    unittest.main()
