#!/usr/bin/env python3
"""Synthetic-only verification of the NAAMP paper metadata/landscape overlap bridge."""
import csv
import io
import sys
import unittest
from pathlib import Path

SCRIPT_DIR=Path(__file__).resolve().parents[1]/"scripts"
sys.path.insert(0,str(SCRIPT_DIR))
import naamp_focal_metadata_geometry_join_v0_1 as join

def fixtures(relocate=False, fewer_prior_sites=False):
    runs=[]
    stops=[]
    for year,rain in [(2003,3.0),(2005,10.0),(2007,1.0)]:
        rid=str(year)
        runs.append({"SurveyYear":str(year),"SurveyDate":f"05/01/{year}",
                    "UnifiedProtocol":"1","RunID":rid,"RunNumber":"1",
                    "State":"Iowa","RouteNumber":"360417","RouteType":"stratified",
                    "DaysSinceRain":str(rain),"TempScale":"C"})
        for st in range(1,11):
            sid=str(1000+st)
            if relocate and year==2007 and st==10:
                sid="2000"
            if fewer_prior_sites and year==2003 and st in (9,10,8):
                sid=str(3000+st)
            stops.append({"RunID":rid,"StopNumber":str(st),"SkippedStop":"0",
                          "SiteID":sid,"AirTemp":"18"})
    coords=io.StringIO()
    writer=csv.DictWriter(coords,fieldnames=["RouteNumber","SiteID","lat","lon"])
    writer.writeheader()
    for st in range(1,11):
        writer.writerow({"RouteNumber":"360417","SiteID":str(1000+st),
                         "lat":40 + st*0.0072,"lon":-82})
    return {"Runs.csv":runs,"Stops.csv":stops},coords.getvalue().encode()

class PaperMetadataJoinTests(unittest.TestCase):
    def test_consecutive_runs_exact_metadata_cohort(self):
        data,coords=fixtures()
        result=join.produce(data,coords,enforce_pins=False)
        self.assertEqual(result["reproduction"]["full_pairs"],2)
        self.assertEqual(result["reproduction"]["history_pairs"],1)
        self.assertEqual(result["intersection"]["source_exact10_pairs"],1)
        self.assertEqual(result["intersection"]["source_exact10_routes"],1)
        self.assertEqual(result["intersection"]["source_siteid_exact10_pairs"],1)
        self.assertEqual(result["intersection"]["source_siteid_exact10_routes"],1)
        self.assertFalse(result["analysis_caveats"]["frog_Counts_csv_opened"])

    def test_pre_history_missing_does_not_count(self):
        data,coords=fixtures(fewer_prior_sites=True)
        result=join.produce(data,coords,enforce_pins=False)
        self.assertEqual(result["reproduction"]["history_pairs"],0)

    def test_focal_siteid_relocation_is_excluded(self):
        data,coords=fixtures(relocate=True)
        result=join.produce(data,coords,enforce_pins=False)
        self.assertEqual(result["reproduction"]["full_pairs"],2)
        self.assertEqual(result["reproduction"]["history_pairs"],0)

    def test_geometry_only_excludes_missing_ten(self):
        data,coords=fixtures()
        lines=coords.decode().splitlines()
        cropped="\n".join(lines[:-1])+"\n"
        result=join.produce(data,cropped.encode(),enforce_pins=False)
        self.assertEqual(result["reproduction"]["history_pairs"],1)
        self.assertEqual(result["intersection"]["source_exact10_pairs"],0)

    def test_exact_ten_coordinate_route_does_not_imply_survey_siteid_identity(self):
        data,coords=fixtures()
        lines=coords.decode().splitlines()
        # Keep ten georeferenced stop coordinates, but mutate one physical
        # SiteID as an outcome-independent geometry/source identity error.
        rows=list(csv.DictReader(io.StringIO(coords.decode())))
        rows[0]["SiteID"]="9999"
        out=io.StringIO()
        writer=csv.DictWriter(out,fieldnames=["RouteNumber","SiteID","lat","lon"])
        writer.writeheader()
        writer.writerows(rows)
        result=join.produce(data,out.getvalue().encode(),enforce_pins=False)
        self.assertEqual(result["intersection"]["source_exact10_pairs"],1)
        self.assertEqual(result["intersection"]["source_siteid_exact10_pairs"],0)
        self.assertEqual(result["intersection"]["geometry_pass_but_unmatched_siteid_pairs"],1)
        self.assertEqual(result["coordinate_vs_survey_siteid_overlap_histogram"]["9"],1)

    def test_rain_tie_not_paired(self):
        data,coords=fixtures()
        data["Runs.csv"][2]["DaysSinceRain"]=data["Runs.csv"][1]["DaysSinceRain"]
        result=join.produce(data,coords,enforce_pins=False)
        self.assertEqual(result["reproduction"]["full_pairs"],1)
        self.assertEqual(result["reproduction"]["history_pairs"],0)

    def test_no_counts_needed_even_with_unobserved_route(self):
        data,coords=fixtures()
        self.assertEqual(set(data),{"Runs.csv","Stops.csv"})
        result=join.produce(data,coords,enforce_pins=False)
        self.assertFalse(result["analysis_caveats"]["frog_species_identity_used"])
        self.assertFalse(result["analysis_caveats"]["frog_effect_estimated"])

if __name__=="__main__":
    unittest.main()
