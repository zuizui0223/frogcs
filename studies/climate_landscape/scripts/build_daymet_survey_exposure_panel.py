#!/usr/bin/env python3
"""Build response-blind NAAMP survey-event climate history from a COMPLETE Daymet pilot.

Input is the frozen independently selected route sample and 1981-2015 climate
pilot receipt, not frog Counts. Every predictor is based on information available
before the survey calendar year. Retrospective full-series trends never enter the
exposure panel. Climate exposure is at route-year grain; repeated runs/stops
must NOT be treated as independent climate change replications.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

from build_naamp_observation_panel import SOURCE_PINS, make as make_panel

BASE_YEARS = "1981-2000"
CLIMATE_KEYS = (
    "prior5_tmean_anomaly_c",
    "prior5_precip_ratio_to_1981_2000",
)


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def combine(sample: dict, receipt: dict, runs: pd.DataFrame, stops: pd.DataFrame):
    if receipt.get("status") != "complete_source_screening":
        raise ValueError("Daymet pilot is incomplete; do not use partial climate histories")
    if receipt.get("analysis") != "daymet_route_level_pilot_v0_1":
        raise ValueError("Unexpected Daymet climate pilot provenance")
    if receipt.get("reads_frog_calling_data") is not False:
        raise ValueError("Daymet pilot must be response blind")
    if sample.get("selection", {}).get("input_uses_count_data") is not False:
        raise ValueError("Sample selection must not depend on frog data")
    chosen = sample.get("routes", [])
    computed = receipt.get("routes", [])
    if not chosen or len(computed) != len(chosen) or receipt.get("n_requested") != len(chosen):
        raise ValueError("Incomplete Daymet route sample")
    chosen_ids = [r["route_id"] for r in chosen]
    result_ids = [r["route_id"] for r in computed]
    if len(set(chosen_ids)) != len(chosen_ids) or result_ids != chosen_ids:
        raise ValueError("Order, duplication, or site identity differs from source sample")
    if any(row.get("daymet_daily_rows") != 35 * 365 or
           row.get("annual_observations") != 35 or
           row.get("baseline_years") != BASE_YEARS or
           not row.get("retrospective_trend_is_not_an_early_year_predictor")
           for row in computed):
        raise ValueError("Invalid Daymet source completeness or future-leakage provenance")
    for chosen_route,actual in zip(chosen,computed):
        if (chosen_route["state"] != actual["state"] or
            actual.get("coordinate_geometry_status") != chosen_route.get("coordinate_status") or
            chosen_route.get("coordinate_status") != "route_median_geometry_pass_unverified"):
            raise ValueError("Route coordinate or sampling provenance mismatch")
    panel, input_receipt = make_panel(runs, stops)
    if panel.empty:
        raise ValueError("No valid surveyed NAAMP opportunities")
    if panel.duplicated(["run_id","route_id","site_id"]).any():
        raise ValueError("Duplicate surveyed station visits")
    survey = panel[["run_id", "route_id", "state", "survey_year", "survey_date",
                    "survey_round", "observer_id"]].drop_duplicates()
    if survey.duplicated(["run_id"]).any():
        raise ValueError("Run metadata inconsistent across its stops")
    survey = survey[survey.route_id.isin(chosen_ids)].copy()
    if survey.empty:
        raise ValueError("No NAAMP runs in selected climate routes")
    if set(survey.route_id) != set(chosen_ids):
        raise ValueError("Sampled route missing from reconstructed NAAMP survey panel")

    climate_rows=[]
    for route in computed:
        state = str(route["state"])
        per_year = route.get("climate_state_by_survey_year", {})
        if set(per_year) != {str(y) for y in range(2001, 2016)}:
            raise ValueError("Incomplete strictly-prior survey-year climate states")
        for y in range(2001, 2016):
            x = per_year[str(y)]
            if set(CLIMATE_KEYS) - set(x):
                raise ValueError("Missing Daymet climate state fields")
            warming=float(x[CLIMATE_KEYS[0]])
            rainfall=float(x[CLIMATE_KEYS[1]])
            if not np.isfinite([warming,rainfall]).all() or rainfall < 0:
                raise ValueError("Invalid climate state from Daymet pilot")
            climate_rows.append({"route_id":route["route_id"],"survey_year":y,
                "prior5_tmean_anomaly_c":warming,
                "prior5_precip_ratio_to_1981_2000":rainfall,
                "climate_history_start_year":y-5,
                "climate_history_last_year":y-1,
                "climate_baseline":BASE_YEARS,
                "climate_support":"route_median_approximately_1km_not_site_verified"})
    cl=pd.DataFrame(climate_rows)
    out=survey.merge(cl,on=["route_id","survey_year"],how="left",
                     validate="many_to_one",indicator=True)
    if not out._merge.eq("both").all():
        raise ValueError("Unmatched route-year Daymet history")
    out=out.drop(columns=["_merge"])
    if (out.climate_history_last_year >= out.survey_year).any():
        raise AssertionError("The climate exposure includes the survey year")
    out=out.sort_values(["route_id","survey_year","survey_round","run_id"]).reset_index(drop=True)
    counts={"input_surveyed_stop_visits":int(input_receipt["n_site_visits"]),
            "selected_survey_runs":len(out),
            "selected_routes":int(out.route_id.nunique()),
            "selected_states":int(out.state.nunique()),
            "distinct_climate_route_years":int(out[["route_id","survey_year"]].drop_duplicates().shape[0]),
            "earliest_survey_year":int(out.survey_year.min()),
            "latest_survey_year":int(out.survey_year.max()),
            "positive_frog_counts_opened":False,
            "route_level_climate_only":True,
            "independently_verified_30m_site_overlay":False,
            "retrospective_trends_excluded_from_predictors":True,
            "same_route_year_repeated_runs_are_not_independent_climate_replicates":True}
    return out,counts


def main():
    p=argparse.ArgumentParser()
    for name in ("sample","climate_receipt","runs","stops","out","receipt"):
        p.add_argument("--"+name.replace("_","-"),required=True)
    p.add_argument("--allow-synthetic-inputs",action="store_true")
    a=p.parse_args()
    checks={"Runs.csv":sha256(a.runs),"Stops.csv":sha256(a.stops)}
    if not a.allow_synthetic_inputs and checks != SOURCE_PINS:
        raise ValueError("NAAMP USGS source SHA256 mismatch")
    sample=json.loads(Path(a.sample).read_text())
    climate=json.loads(Path(a.climate_receipt).read_text())
    if (climate.get("sample_source_sha256") != sha256(a.sample)):
        raise ValueError("Sample JSON checksum not tied to climate receipt")
    if not a.allow_synthetic_inputs and sample.get("source_sha256",{}) != {
        **SOURCE_PINS,"Coordinates.csv":"f71a87df9fc94e0d6c5d4466b4745c3bbaff874cbe7c28796b3f9eb44c2e6e83"}:
        raise ValueError("NAAMP sampling source hashes mismatch")
    out,summary=combine(sample,climate,
        pd.read_csv(a.runs,dtype=str,keep_default_na=False),
        pd.read_csv(a.stops,dtype=str,keep_default_na=False))
    out_path=Path(a.out);out_path.parent.mkdir(parents=True,exist_ok=True)
    out.to_csv(out_path,index=False)
    audit={"schema":"frog_daymet_route_year_survey_panel_v0_1",
           **summary,
           "source_sha256":{"sample":sha256(a.sample),
                            "daymet_receipt":sha256(a.climate_receipt),**checks},
           "output_sha256":sha256(out_path)}
    rp=Path(a.receipt);rp.parent.mkdir(parents=True,exist_ok=True)
    rp.write_text(json.dumps(audit,indent=2,sort_keys=True)+'\n')
    print(json.dumps(audit,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
