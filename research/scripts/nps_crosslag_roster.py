#!/usr/bin/env python3
"""Response-blind NPS taxon/coverage inventory, no crosslag outcome estimates.

Original NPS source DOI 10.57830/2320505, pinned checksum inherited from
nps_glkn_strict_history.py. Prints roster and effort availability ONLY.
Do not select a species or model direction based on outcome coefficients.
"""
import json
import tempfile
from pathlib import Path
from nps_glkn_strict_history import fetch_csv, build_yearly
def main():
    with tempfile.TemporaryDirectory() as wd:
        p=Path(wd)/"nps.csv"
        fetch_csv(p)
        annual,qc=build_yearly(p)
    roster=[]
    for name, g in annual.groupby("ScientificName"):
        roster.append({
            "scientific_name":str(name),
            "parks_with_scored_rows":int(g.ParkCode.nunique()),
            "physical_stations_with_scored_rows":int(g.SiteLocation.nunique()),
            "years_with_scored_rows": sorted([int(v) for v in g.EventYear.unique()]),
            "species_station_year_coverage_rows":int(len(g))
        })
    print("BEGIN_NPS_STAGE_CROSS_LAG_BLIND_ROSTER")
    print(json.dumps({"source":"US NPS DOI 10.57830/2320505",
                     "source_sha256":"b1c11cf70472a906e6c238a690a5a12373cdd20ef4d5e180fa3f376d520118c2",
                     "source_total_taxon_tokens":qc["taxa"],
                     "roster":roster,
                     "response_fields_inspected":False,
                     "activity_response_estimates_computed":False},
                      ensure_ascii=False,indent=2))
    print("END_NPS_STAGE_CROSS_LAG_BLIND_ROSTER")
if __name__=="__main__": main()
