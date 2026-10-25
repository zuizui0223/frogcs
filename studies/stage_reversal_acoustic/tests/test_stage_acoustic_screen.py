"""No ecological claims from fixtures: contract and calculation tests only."""
import csv
import json
import sys
import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from stage_acoustic_screen import (GATES, correlation, execute, gate, parse_calls,
                                   parse_stages, read_edges, scan, week)


class StageAcousticTests(unittest.TestCase):
    def write(self, path, header, rows):
        with path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(header)
            writer.writerows(rows)

    def test_missing_source_gate_fail_closed(self):
        self.assertEqual(gate(None)["status"], "NOT_ESTIMABLE")
        self.assertEqual(execute(None, None, ROOT / "registry/source_screen_v0_2.csv",
                                 None, "Litoria aurea")["n_original_rows_analyzed"], 0)

    def test_ready_only_with_all_verified_sources(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "gate.json"
            path.write_text(json.dumps({key: True for key in GATES}), encoding="utf-8")
            self.assertEqual(gate(path)["status"], "READY_FOR_DESCRIPTIVE_SCREEN")
            self.assertEqual(execute(None, None, ROOT / "registry/source_screen_v0_2.csv",
                                     path, "Litoria aurea")["status"], "NOT_ESTIMABLE")

    def test_synthetic_rows_cannot_pass_empirical_gate(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "gate.json"
            path.write_text(json.dumps({**{key: True for key in GATES},
                                         "data_are_synthetic": True}), encoding="utf-8")
            self.assertIn("synthetic_fixture_not_empirical", gate(path)["missing"])

    def test_citation_registry_admits_only_direct_reciprocal_pairs(self):
        pairs = read_edges(ROOT / "registry/source_screen_v0_2.csv")
        self.assertEqual(set(pairs), {"LA_ANAX", "BLEAK_ASP"})
        self.assertNotIn("PIKE_STICKLEBACK", pairs)

    def test_not_direct_monodirectional_pair(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "r.csv"
            self.write(p, ["pair_id","predator_species","predator_stage","prey_species",
                           "prey_stage","evidence_class","doi","acoustic_eligible"],
                       [["a","a","adult","b","larva","DIRECT_PAIR_DIRECTION","doi","YES"]])
            self.assertEqual(read_edges(p), {})

    def test_call_denominator_conflict_fails(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "calls.csv"
            self.write(p, ["cell_id","season_id","week_start","species","positive_recordings","total_recordings"],
                       [["c","2019-2020","2019-10-07","Litoria aurea",2,10],
                        ["c","2019-2020","2019-10-07","Pseudophryne",1,9]])
            with self.assertRaisesRegex(ValueError, "inconsistent total recording"):
                parse_calls(p)

    def test_call_ratio_beyond_denominator_fails(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "calls.csv"
            self.write(p, ["cell_id","season_id","week_start","species","positive_recordings","total_recordings"],
                       [["c","2019-2020","2019-10-07","Litoria aurea",11,10]])
            with self.assertRaisesRegex(ValueError, "invalid numerator"):
                parse_calls(p)

    def test_stage_unknown_not_imputed_adult(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "stages.csv"
            self.write(p, ["cell_id","season_id","week_start","species","stage","count","total_annotated"],
                       [["c","2019-2020","2019-10-07","Anax papuensis","unknown",1,10]])
            with self.assertRaisesRegex(ValueError, "unrecognized stage"):
                parse_stages(p)

    def test_stage_double_count_denominator_fails(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "stages.csv"
            self.write(p, ["cell_id","season_id","week_start","species","stage","count","total_annotated"],
                       [["c","2019-2020","2019-10-07","Anax papuensis","larva",8,10],
                        ["c","2019-2020","2019-10-07","Anax papuensis","emerging",5,10]])
            with self.assertRaisesRegex(ValueError, "stage counts exceed"):
                parse_stages(p)

    def test_non_monday_fails(self):
        with self.assertRaisesRegex(ValueError, "not Monday"):
            week("2023-12-26")

    def test_calendar_boundary_keeps_same_breeding_season(self):
        d = date(2023, 12, 25)
        calls = {("a","2023-2024",d,"Litoria aurea"):0.4}
        stages = {("a","2023-2024",date(2024,1,8),"Anax papuensis","emerging"):0.8}
        r = scan(calls, stages, "Litoria aurea", "Anax papuensis", "emerging")
        self.assertEqual(r["2"]["status"], "NOT_ESTIMABLE")
        self.assertEqual(r["2"]["n_matched_weeks"], 0) # fewer than 4, not a fabricated zero

    def test_lag_requires_same_cell_season(self):
        dt = date(2023,10,2)
        calls = {("a","2023",dt,"Litoria aurea"):0.5}
        stages = {("b","2023",dt+timedelta(weeks=1),"Anax papuensis","larva"):0.7}
        r = scan(calls, stages, "Litoria aurea", "Anax papuensis", "larva")
        self.assertIsNone(r["1"]["r"])

    def test_no_automated_warning_or_reversal_claim(self):
        dt = date(2023,10,2)
        calls = {}
        stages = {}
        for j in range(3):
            for i in range(12):
                t = dt+timedelta(weeks=i)
                x = (i+1)/30
                calls[(str(j),"2023",t,"Litoria aurea")] = x
                stages[(str(j),"2023",t,"Anax papuensis","larva")] = x
        a=scan(calls,stages,"Litoria aurea","Anax papuensis","larva")
        self.assertEqual(a["0"]["n_cell_seasons"],3)
        self.assertEqual(a["0"]["r"],1.0)
        self.assertIn(a["asymmetry_2"]["status"],["DESCRIPTIVE_ONLY","NOT_ESTIMABLE"])

    def test_centered_correlation_zero_variance(self):
        x=correlation([("a","2023",0.5,v) for v in [0.1,0.2,0.3,0.4]])
        self.assertIsNone(x["r"])
        self.assertEqual(x["status"],"ZERO_VARIANCE")

    def test_insufficient_matched_groups_not_implicitly_confirmatory(self):
        y=correlation([("a","2023",x,x) for x in (0.1,0.2,0.3)])
        self.assertEqual(y["status"], "NOT_ESTIMABLE")


if __name__=="__main__":
    unittest.main()
