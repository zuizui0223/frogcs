import unittest
from ecology.dryad_takahashi.reanalyse_original_factorial import summarize

class PublishedLabFactorialSafeguards(unittest.TestCase):
    def test_known_direction_and_independent_egg_mass_unit(self):
        raw={}
        levels=("No","Low","Medium","High")
        for layer in ("Yes","No"):
            for pred in levels:
                h=0 if layer=="No" and pred in ("Medium","High") else (.9 if layer=="Yes" else .8)
                raw[layer,pred]=[{"hatching":h,"days":40. if h else None} for _ in range(4)]
        cells,r=summarize(raw,nboot=100)
        self.assertEqual(len(cells),8)
        self.assertEqual(r["n_egg_masses"],32)
        self.assertEqual(r["n_independent_egg_masses_per_cell"],4)
        self.assertTrue(r["cannot_infer_predation_in_Mohonk"])
        self.assertTrue(all(c["mean_incubation_days_missing_by_design"] for c in cells if not c["jelly_layer_intact"] and c["tadpole_density_treatment"] in ("Medium","High")))
    def test_original_shape_known(self):
        from ecology.dryad_takahashi.reanalyse_original_factorial import LEVELS,EXPECTED_SHA
        self.assertEqual(len(LEVELS),4)
        self.assertEqual(len(EXPECTED_SHA),64)

if __name__=="__main__":unittest.main()
