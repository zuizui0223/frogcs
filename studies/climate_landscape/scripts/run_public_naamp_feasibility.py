#!/usr/bin/env python3
"""Actual public NAAMP run/stop/coordinate feasibility without frog responses.

This audits original public records and never auto-certifies physical station
positions. Source bytes are pinned to frozen RC6 source SHA256 hashes.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import pandas as pd

from audit_coordinates import audit as geometry_audit
from build_naamp_observation_panel import SOURCE_PINS, make as observation_panel

COORD_SHA = "f71a87df9fc94e0d6c5d4466b4745c3bbaff874cbe7c28796b3f9eb44c2e6e83"


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def season_index(s):
    d = pd.Timestamp(s)
    if d.month == 2 and d.day == 29:
        return 59
    return (pd.Timestamp(year=2001, month=d.month, day=d.day) -
            pd.Timestamp("2001-01-01")).days


def yearly_pairs(panel, max_day_shift=21):
    columns = ["route_id", "site_id", "survey_round", "from_year",
               "to_year", "season_day_difference"]
    if panel.empty:
        return pd.DataFrame(columns=columns)
    grouped = []
    for key, g in panel.groupby(["route_id", "site_id", "survey_round"], sort=True):
        g = g.drop_duplicates(["survey_year"], keep=False).sort_values("survey_year")
        for a, b in zip(g.iloc[:-1].itertuples(index=False),
                        g.iloc[1:].itertuples(index=False)):
            if int(b.survey_year) - int(a.survey_year) != 1:
                continue
            delta = abs(season_index(a.survey_date)-season_index(b.survey_date))
            if delta <= max_day_shift:
                grouped.append({
                    "route_id": key[0], "site_id": key[1],
                    "survey_round": int(key[2]),
                    "from_year": int(a.survey_year), "to_year": int(b.survey_year),
                    "season_day_difference": int(delta)
                })
    return pd.DataFrame(grouped, columns=columns)


def summarize(runs, stops, rawcoords):
    panel, cohort = observation_panel(runs, stops)
    locs, geom = geometry_audit(rawcoords)
    if panel.empty:
        raise ValueError("No standardized NAAMP opportunities")
    locs = locs.rename(columns={"route_id":"route_number"})
    rstate = panel[["route_number", "state"]].drop_duplicates()
    reused = set(rstate.groupby("route_number").state.nunique()
                 .loc[lambda x: x > 1].index.astype(str))
    merged = panel.merge(locs[["route_number", "site_id", "geometry_qc_status"]],
                 on=["route_number", "site_id"], how="left",
                 validate="many_to_one", indicator=True)
    merged["ambiguous_route_number"] = merged.route_number.isin(reused)
    merged["geometry_qc_status"] = merged.geometry_qc_status.fillna("no_coordinate_match")
    matched = merged._merge.eq("both")
    provisional = merged.geometry_qc_status.eq("pass_unverified") & ~merged.ambiguous_route_number
    year_counts = (panel.groupby("survey_year").agg(
        n_runs=("run_id","nunique"), n_stops=("site_id","size"),
        n_site_ids=("site_id","nunique")).reset_index().to_dict(orient="records"))
    pairs_all = yearly_pairs(panel)
    pairs_provisional = yearly_pairs(merged.loc[provisional, panel.columns])
    return {
      "public_records_actual":True,
      "frog_positive_count_file_opened":False,
      "external_coordinate_verification_performed":False,
      "n_externally_verified_sites":0,
      "n_candidate_ten_stop_runs":int(panel.run_id.nunique()),
      "n_surveyed_stop_opportunities":len(panel),
      "n_route_site_keys":int(panel[["route_id","site_id"]].drop_duplicates().shape[0]),
      "n_routes":int(panel.route_id.nunique()),
      "n_states":int(panel.state.nunique()),
      "n_coordinate_rows_source":len(rawcoords),
      "n_coordinate_route_site_keys":len(locs),
      "n_stop_visits_matching_source_coordinates":int(matched.sum()),
      "n_stop_visits_unmatched_coordinates":int((~matched).sum()),
      "n_stop_visits_geometry_pass_but_unverified":int(provisional.sum()),
      "n_stop_visits_geometry_review_failed_or_ambiguous":int((~provisional).sum()),
      "n_route_numbers_reused_between_states":len(reused),
      "n_potential_same_site_consecutive_year_same_season_pairs":len(pairs_all),
      "n_potential_pairs_geometry_pass_but_unverified":len(pairs_provisional),
      "n_actual_satellite_overlays":0,"n_actual_climate_site_series":0,
      "cohort_receipt":cohort,
      "coordinate_source_geometry_receipt":geom,
      "survey_year_counts":year_counts,
      "interpretation":"Geometry-only pass is not independently verified. Do not regard candidate site-year pairs as an inferential sample."
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", required=True)
    ap.add_argument("--stops", required=True)
    ap.add_argument("--coords", required=True)
    ap.add_argument("--receipt", required=True)
    ap.add_argument("--skip-pins-for-fixtures", action="store_true")
    a=ap.parse_args()
    digest = {"Runs.csv":sha256(a.runs),"Stops.csv":sha256(a.stops)}
    cdigest=sha256(a.coords)
    if not a.skip_pins_for_fixtures and (digest != SOURCE_PINS or cdigest != COORD_SHA):
        raise ValueError("NAAMP source hashes differ from pinned authoritative inputs")
    run=pd.read_csv(a.runs,dtype=str,keep_default_na=False)
    stop=pd.read_csv(a.stops,dtype=str,keep_default_na=False)
    coords=pd.read_csv(a.coords,dtype={"RouteNumber":str,"SiteID":str})
    receipt=summarize(run,stop,coords)
    receipt["source_sha256"]={**digest,"coordinates":cdigest}
    out=Path(a.receipt)
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(receipt,sort_keys=True,indent=2,default=int)+"\n",encoding="utf-8")
    print(json.dumps({k:v for k,v in receipt.items() if not isinstance(v,(dict,list))},
          sort_keys=True,indent=2))


if __name__=="__main__":
    main()
