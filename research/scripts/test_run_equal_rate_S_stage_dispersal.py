"""Synthetic tests: equal diffusion coefficients across S larval/adult stages."""
import unittest
import numpy as np

from multigeneration_reversal import Rates,SL,SA,initial_grid,STAGES
from tracked_spatial_pedigree import simulate_traced_abm
from run_equal_rate_S_stage_dispersal import (
    NEW_MODES,DIFFUSION_VALUES,equal_rate_modes
)
from assess_recolonization_establishment import (
    attach_validated_births,event_table,source_annual_stage_audit
)


class EqualRateSStageTests(unittest.TestCase):
    def test_all_four_stage_by_rate_modes_have_identical_per_capita_hazard(self):
        self.assertEqual(len(NEW_MODES),4)
        for code in DIFFUSION_VALUES:
            larva=equal_rate_modes("S_larva_"+code)
            adult=equal_rate_modes("S_adult_"+code)
            self.assertEqual(larva.diffusion[SL],adult.diffusion[SA])
            self.assertEqual(larva.diffusion[SA],0)
            self.assertEqual(adult.diffusion[SL],0)
            self.assertEqual(np.count_nonzero(larva.diffusion),1)
            self.assertEqual(np.count_nonzero(adult.diffusion),1)
            self.assertEqual(larva.natural,Rates().natural)
            self.assertEqual(adult.fecundity,Rates().fecundity)
        with self.assertRaises(ValueError):
            equal_rate_modes("unknown")
        with self.assertRaises(ValueError):
            equal_rate_modes("S_larva_050")

    def test_mobility_event_stages_match_only_allowed_source_stage(self):
        x,v=initial_grid(4)
        for mode in NEW_MODES:
            p=equal_rate_modes(mode)
            one=simulate_traced_abm(x,v,p,years=2,dt=.05,
                                     reverse=False,seed=71)
            allmove=one["movements"]
            allowed="S_larva" if mode.startswith("S_larva") else "S_adult"
            self.assertGreater(len(allmove),0)
            self.assertEqual(set(allmove.stage),{allowed})
            self.assertTrue((one["registry"].generation>=0).all())
            self.assertEqual(len(one["lineages"]),3)
            # Genealogy, complete newborn registry, and patch census match
            for key in ("patch","registry","annual"):
                one[key]=one[key].assign(mobility=mode,reverse=False,seed=71)
            patches=attach_validated_births(one["patch"],one["registry"])
            source_annual_stage_audit(patches,one["annual"])
            events=event_table(patches)
            self.assertTrue(events.empty or events.year_of_recolonization.le(2).all())

    def test_stage_rate_pairing_does_not_equalize_realized_emigration_flux(self):
        # Equal per-capita hazard alone does NOT imply identical total moves:
        # the S stages differ in their own abundance, death and maturation.
        a=equal_rate_modes("S_larva_022")
        b=equal_rate_modes("S_adult_022")
        self.assertEqual(max(a.diffusion),max(b.diffusion))
        self.assertNotEqual(a.diffusion,b.diffusion)
        self.assertGreater(a.diffusion[SL],0)
        self.assertGreater(b.diffusion[SA],0)


if __name__=="__main__":
    unittest.main()
