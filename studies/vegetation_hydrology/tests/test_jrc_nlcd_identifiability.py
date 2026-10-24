import importlib.util,sys,unittest
from pathlib import Path
S=Path(__file__).resolve().parents[1]/"scripts"
sp=importlib.util.spec_from_file_location("cov",S/"audit_jrc_nlcd_identifiability.py")
m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
import numpy as np
import pandas as pd

class TestEnvironmentOnlyIdentifiability(unittest.TestCase):
    def test_precipitation_not_in_classification(self):
        self.assertEqual(m.JRC_REQUIRE,172153)
        self.assertEqual(m.NLCD_REQUIRE,64779)
        self.assertTrue({"Species","CallingIndex"}.issubset(m.NO_FROG_FIELDS))
    def test_wetland_vegetation_not_conflated_with_open_water(self):
        x=pd.DataFrame([
          {"frac_open_water":.11,"frac_woody_wetland":.0,"frac_emergent_wetland":.0},
          {"frac_open_water":0,"frac_woody_wetland":.30,"frac_emergent_wetland":.0},
          {"frac_open_water":0,"frac_woody_wetland":0,"frac_emergent_wetland":0}
        ])
        self.assertEqual(list(m.habitat_kind(x)),["open_water_ge10","vegetated_wetland_ge25","low_mapped_wetland"])
if __name__=="__main__":unittest.main()
