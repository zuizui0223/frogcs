"""Fail-closed fast tests for main's structural identity and original source design."""
import unittest
import pandas as pd

from run_main_mechanism_ontogeny_demography_80y import (
    DRAWS, ROLES, STAGES, NETWORKS, BASE_ROLE,
    verify_original_main_catalog, source_cube, controlled_plant,
)


class MainMechanismStageDemographyTests(unittest.TestCase):
    def test_main_1479_1455_exact_catalog_fingerprints(self):
        self.assertEqual(len(verify_original_main_catalog()), 64)
        self.assertEqual(NETWORKS["main1479"], {})
        self.assertEqual(NETWORKS["main1455"], {"edge_off": "SD"})

    def test_source_original_three_stages_and_all_original_theta(self):
        base, plants = source_cube()
        self.assertEqual(len(base), 96)
        self.assertEqual(set(base.context), set(STAGES))
        self.assertEqual(set(base.draw), set(DRAWS))
        self.assertEqual(set(base.plant_model), {BASE_ROLE})
        self.assertEqual(set(base.reverse_on), {0})
        self.assertEqual(set(base.risk), {False})
        self.assertEqual(len(plants), 12)
        for stage in STAGES:
            b = base[base.context.eq(stage)]
            self.assertEqual(len(b), 32)
            self.assertTrue(b.groupby("draw").vertex.nunique().eq(8).all())

    def test_legal_plants_only_edit_shelter_or_litter(self):
        base, plants = source_cube()
        g = base[base.context.eq("original")].copy()
        protected = [
            "context","draw","vertex","structure_id","plant_model",
            "sa","da","sg","dg","rho","conversion","attack_scale",
            "S_source","D_source","reverse_on",
        ]
        for role in ROLES:
            trial=controlled_plant(g,role,plants)
            pd.testing.assert_frame_equal(trial[protected],g[protected])
            for flag in ("cover_SF","cover_DF","cover_DS","litter"):
                self.assertTrue(trial[flag].eq(int(plants.loc[role,flag])).all())

    def test_original_source_matches_PR158_input(self):
        # Same source cube as PR158 for overlapping stages, rate IDs and
        # main plant. No ecological numerical result is being asserted.
        from run_D_E_common_engine_nuisance_80y import biological_cube
        x,_=source_cube()
        a=x[x.context.isin(("original","D_first_S_overtakes"))]
        b=biological_cube()
        b=b[b.plant_model.eq(BASE_ROLE)]
        keys=["context","draw","vertex"]
        a=a.sort_values(keys).reset_index(drop=True)
        b=b.sort_values(keys).reset_index(drop=True)
        self.assertEqual(len(a),len(b))
        for flag in ("sa","da","sg","dg","hs","hd","dduration",
                     "attack_scale","rho","conversion","S_source","D_source",
                     "cover_SF","cover_DS","litter","f_delay"):
            self.assertTrue((a[flag].to_numpy()==b[flag].to_numpy()).all(),flag)


if __name__=="__main__":
    unittest.main()
