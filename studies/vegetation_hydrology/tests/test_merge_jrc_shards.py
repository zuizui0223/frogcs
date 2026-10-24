import importlib.util
import sys
import unittest
from pathlib import Path
S=Path(__file__).resolve().parents[1]/"scripts"
sys.path.insert(0,str(S))
spec=importlib.util.spec_from_file_location("merge_jrc",S/"merge_jrc_shards.py")
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

def row(v,w):
    return {"n_buffer_pixels":"100","n_valid_pixels":str(v),"n_water_pixels":str(w),
            "n_no_observation":str(100-v),
            "valid_fraction":str(round(v/100,6)),
            "water_fraction_among_observed":str(round(w/v,6)) if v else "",
            "coverage_ge_50pct":str(v/100>=.5),"coverage_ge_80pct":str(v/100>=.8),
            "status":"ok" if v/100>=.5 else "insufficient_clear_pixels"}
class TestJRCShards(unittest.TestCase):
    def test_sentinel_no_observation_not_nonwater(self):
        r=row(0,0)
        out=m.check_pixel_row(r)
        self.assertEqual(out["observed"],0)
        self.assertFalse(out["valid_50"])
    def test_observed_water_fraction_denominator(self):
        r=row(60,12)
        out=m.check_pixel_row(r)
        self.assertEqual(out["water"],12)
        r["water_fraction_among_observed"]="0.12"
        with self.assertRaisesRegex(ValueError,"water fraction"):
            m.check_pixel_row(r)
    def test_inconsistent_coverage_fails_closed(self):
        r=row(80,20)
        r["coverage_ge_80pct"]="False"
        with self.assertRaisesRegex(ValueError,"coverage gate"):
            m.check_pixel_row(r)
if __name__=="__main__":unittest.main()
