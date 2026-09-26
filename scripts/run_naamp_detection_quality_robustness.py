#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

ROOT=Path(__file__).resolve().parent

def loadmod(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    mod=importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(mod)
    return mod

base=loadmod("pulse_base",ROOT/"run_naamp_ecological_pulse.py")
spatial=loadmod("spatial_base",ROOT/"run_naamp_spatial_taxonomic_activation_decomposition.py")
Q=1.959963984540054

def num(v):
    try:
        x=float(str(v or "").strip())
        return x if np.isfinite(x) else np.nan
    except Exception:
        return np.nan

def valid01(v):
    x=num(v)
    return x if x in (0.0,1.0) else np.nan

def run_detection_metrics(raw,eligible_ids,sampled,stop_species):
    run_raw={}
    for r in raw["Runs.csv"]:
        rid=str(r.get("RunID") or "").strip()
        if rid in eligible_ids:
            sw=num(r.get("StartWind")); ew=num(r.get("EndWind"))
            wind=np.mean([sw,ew]) if (
                np.isfinite(sw) and np.isfinite(ew) and 0<=sw<=5 and 0<=ew<=5
            ) else np.nan
            run_raw[rid]={"mean_wind":float(wind) if np.isfinite(wind) else np.nan}

    stop_raw=defaultdict(dict)
    for s in raw["Stops.csv"]:
        rid=str(s.get("RunID") or "").strip()
        st=str(s.get("StopNumber") or "").strip()
        if rid not in eligible_ids or st not in sampled.get(rid,set()):
            continue
        mass=num(s.get("MassNoiseIndex"))
        noise=valid01(s.get("Noise"))
        if np.isfinite(mass) and 0<=mass<=4:
            impaired=float(mass>=2)
            mass_valid=mass
        elif np.isfinite(noise):
            impaired=float(noise)
            mass_valid=np.nan
        else:
            impaired=np.nan
            mass_valid=np.nan
        timeout=valid01(s.get("TimeOut"))
        car=num(s.get("CarCount"))
        if not (np.isfinite(car) and car>=0):
            car=np.nan
        stop_raw[rid][st]={
            "impaired":impaired,
            "mass_noise":mass_valid,
            "timeout":timeout,
            "car":car
        }

    rows=[]
    for rid in sorted(eligible_ids):
        stops=sorted(sampled[rid])
        if len(stops)!=10:
            raise RuntimeError(f"eligible run lacks 10 sampled stops: {rid}")
        rec=[stop_raw[rid].get(st,{}) for st in stops]
        imp=np.array([x.get("impaired",np.nan) for x in rec],float)
        mass=np.array([x.get("mass_noise",np.nan) for x in rec],float)
        timeout=np.array([x.get("timeout",np.nan) for x in rec],float)
        car=np.array([x.get("car",np.nan) for x in rec],float)

        by={st:set(stop_species.get((rid,st),set())) for st in stops}
        counts=np.array([len(by[st]) for st in stops],float)
        active=counts[counts>=1]
        n_active=int(len(active))
        alpha=float(np.mean(active)) if n_active else np.nan

        rows.append({
            "RunID":rid,
            "hearing_impairment_fraction":float(np.nanmean(imp)) if np.isfinite(imp).sum()>=8 else np.nan,
            "timeout_fraction":float(np.nanmean(timeout)) if np.isfinite(timeout).sum()>=8 else np.nan,
            "mean_mass_noise_index":float(np.nanmean(mass)) if np.isfinite(mass).sum()>=8 else np.nan,
            "mean_car_count":float(np.nanmean(car)) if np.isfinite(car).sum()>=8 else np.nan,
            "mean_wind":run_raw.get(rid,{}).get("mean_wind",np.nan),
            "active_stops":n_active,
            "alpha_active":alpha
        })
    return pd.DataFrame(rows).set_index("RunID")

def enrich_pairs(raw):
    runs,sets=base.build_runs(raw)
    eligible=set(runs["RunID"].astype(str))
    sampled,stop_species=spatial.stop_matrix(raw,eligible)
    metrics=run_detection_metrics(raw,eligible,sampled,stop_species)
    pairs=base.pair_runs(runs,sets).copy()

    rows=[]
    for p in pairs.itertuples(index=False):
        w=str(p.wet_RunID); d=str(p.dry_RunID)
        W=metrics.loc[w];D=metrics.loc[d]
        row=p._asdict()
        row.update({
            "delta_active_stops":float(W.active_stops-D.active_stops),
            "delta_alpha_active":float(W.alpha_active-D.alpha_active)
                if np.isfinite(W.alpha_active) and np.isfinite(D.alpha_active) else np.nan,
            "hearing_impairment_difference":float(W.hearing_impairment_fraction-D.hearing_impairment_fraction)
                if np.isfinite(W.hearing_impairment_fraction) and np.isfinite(D.hearing_impairment_fraction) else np.nan,
            "timeout_difference":float(W.timeout_fraction-D.timeout_fraction)
                if np.isfinite(W.timeout_fraction) and np.isfinite(D.timeout_fraction) else np.nan,
            "wind_difference":float(W.mean_wind-D.mean_wind)
                if np.isfinite(W.mean_wind) and np.isfinite(D.mean_wind) else np.nan,
            "mass_noise_difference":float(W.mean_mass_noise_index-D.mean_mass_noise_index)
                if np.isfinite(W.mean_mass_noise_index) and np.isfinite(D.mean_mass_noise_index) else np.nan,
            "car_count_difference":float(W.mean_car_count-D.mean_car_count)
                if np.isfinite(W.mean_car_count) and np.isfinite(D.mean_car_count) else np.nan
        })
        rows.append(row)
    return runs,pd.DataFrame(rows),metrics

BASE_COVARS=[
    "rain_contrast","temp_difference","doy_difference","year_gap",
    "hearing_impairment_difference","timeout_difference","wind_difference"
]

def complete_sample(d,covars):
    mask=np.ones(len(d),dtype=bool)
    for c in covars:
        mask &= np.isfinite(pd.to_numeric(d[c],errors="coerce"))
    return d.loc[mask].copy()

def fit(d,response,covars):
    x=d[np.isfinite(pd.to_numeric(d[response],errors="coerce"))].copy()
    rhs=" + ".join(covars)+" + C(State) + C(RunNumber)"
    formula=f"{response} ~ {rhs}"
    f=smf.ols(formula,data=x).fit(
        cov_type="cluster",cov_kwds={"groups":x["route_cluster"]}
    )
    b=float(f.params["rain_contrast"]);se=float(f.bse["rain_contrast"]);p=float(f.pvalues["rain_contrast"])
    lo=b-Q*se;hi=b+Q*se
    return {
        "response":response,"formula":formula,
        "n_pairs":int(len(x)),"n_routes":int(x["route_cluster"].nunique()),
        "beta_rain_contrast":b,"se_cluster":se,"ci95":[lo,hi],"p_value":p,
        "positive_ci_support":bool(lo>0)
    }

def package(d,covars):
    return {
        "delta_active_stops":fit(d,"delta_active_stops",covars),
        "delta_alpha_active":fit(d,"delta_alpha_active",covars),
        "richness_gain":fit(d,"richness_gain",covars)
    }

def gate(d,min_pairs,min_routes):
    return bool(len(d)>=min_pairs and d["route_cluster"].nunique()>=min_routes)

def main():
    raw=base.load()
    runs,pairs,metrics=enrich_pairs(raw)

    primary=complete_sample(pairs,BASE_COVARS)
    if not gate(primary,1500,300):
        raise SystemExit(
            f"primary detection gate failed pairs={len(primary)} routes={primary.route_cluster.nunique()}"
        )
    primary_models=package(primary,BASE_COVARS)

    exact=primary[primary["year_gap"]==1].copy()
    exact_models=package(exact,BASE_COVARS)

    car_covars=BASE_COVARS+["car_count_difference"]
    car=complete_sample(pairs,car_covars)
    car_pkg=None
    if gate(car,750,200):
        car_pkg={
            "gate_pass":True,
            "n_pairs":int(len(car)),
            "n_routes":int(car["route_cluster"].nunique()),
            "models":package(car,car_covars)
        }
    else:
        car_pkg={
            "gate_pass":False,
            "n_pairs":int(len(car)),
            "n_routes":int(car["route_cluster"].nunique())
        }

    mass_covars=[
        "rain_contrast","temp_difference","doy_difference","year_gap",
        "mass_noise_difference","timeout_difference","wind_difference"
    ]
    mass=complete_sample(pairs,mass_covars)
    mass_pkg=None
    if gate(mass,300,75):
        mass_pkg={
            "gate_pass":True,
            "n_pairs":int(len(mass)),
            "n_routes":int(mass["route_cluster"].nunique()),
            "models":package(mass,mass_covars)
        }
    else:
        mass_pkg={
            "gate_pass":False,
            "n_pairs":int(len(mass)),
            "n_routes":int(mass["route_cluster"].nunique())
        }

    run_cov={
        "eligible_runs":int(len(metrics)),
        "hearing_impairment_available_runs":int(np.isfinite(metrics["hearing_impairment_fraction"]).sum()),
        "timeout_available_runs":int(np.isfinite(metrics["timeout_fraction"]).sum()),
        "wind_available_runs":int(np.isfinite(metrics["mean_wind"]).sum()),
        "car_count_available_runs":int(np.isfinite(metrics["mean_car_count"]).sum()),
        "mass_noise_available_runs":int(np.isfinite(metrics["mean_mass_noise_index"]).sum()),
        "mean_hearing_impairment_fraction":float(metrics["hearing_impairment_fraction"].mean()),
        "mean_timeout_fraction":float(metrics["timeout_fraction"].mean())
    }

    result={
        "analysis":"naamp_detection_quality_robustness_v0_1",
        "contract":"NAAMP_DETECTION_QUALITY_ROBUSTNESS_CONTRACT_V0_1.json",
        "run_covariate_coverage":run_cov,
        "primary_sample":{
            "n_pairs":int(len(primary)),
            "n_routes":int(primary["route_cluster"].nunique()),
            "models":primary_models,
            "all_three_positive_ci":bool(all(x["positive_ci_support"] for x in primary_models.values()))
        },
        "exact_consecutive_year":{
            "n_pairs":int(len(exact)),
            "n_routes":int(exact["route_cluster"].nunique()),
            "models":exact_models,
            "all_three_positive_ci":bool(all(x["positive_ci_support"] for x in exact_models.values()))
        },
        "car_count_sensitivity":car_pkg,
        "mass_noise_index_sensitivity":mass_pkg,
        "interpretation_boundary":{
            "noise":"Recorded NAAMP hearing-impairment conditions, not a complete acoustic detection model.",
            "timeout":"Major recorded noise interruptions; surveys resumed after disturbance.",
            "causal_rainfall_claim_authorized":False,
            "all_detectability_confounding_excluded":False,
            "endpoint_retuning_after_readback_authorized":False
        }
    }
    Path("NAAMP_DETECTION_QUALITY_ROBUSTNESS_RECEIPT_V0_1.json").write_text(
        json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8"
    )
    print(json.dumps(result,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
