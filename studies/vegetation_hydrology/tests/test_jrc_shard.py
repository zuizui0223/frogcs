import importlib.util
import sys
import unittest
from pathlib import Path
S=Path(__file__).resolve().parents[1]/"scripts"
sys.path.insert(0,str(S))
spec=importlib.util.spec_from_file_location("jrcshard",S/"run_jrc_prior_month_shard.py")
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

class TestShards(unittest.TestCase):
    def test_every_source_once_and_deterministic(self):
        sample={"https://example.org/source_{}.tif".format(i):{i:i} for i in range(124)}
        for n in (1,3,6,9):
            actual=[]
            for i in range(n):actual+=list(m.partition(sample,n,i))
            self.assertEqual(set(actual),set(sample))
            self.assertEqual(len(actual),len(set(actual)))
            self.assertEqual(m.shard_of(next(iter(sample)),n),m.shard_of(next(iter(sample)),n))
    def test_reject_out_of_range_shard(self):
        with self.assertRaises(ValueError):m.partition({"x":{}},6,6)
        with self.assertRaises(ValueError):m.partition({"x":{}},6,-1)
        with self.assertRaises(ValueError):m.shard_of("x",0)
    def test_placeholder_is_explicit_missing(self):
        row={"State":"VA","RouteNumber":"1","SiteID":"2","SurveyYear":2001,"PreviousMonth":"2000-12"}
        r=m._blank(row,"source_unavailable")
        self.assertEqual(r["status"],"source_unavailable")
        self.assertEqual(r["n_water_pixels"],"")
        self.assertFalse(r["coverage_ge_50pct"])
if __name__=="__main__":unittest.main()
