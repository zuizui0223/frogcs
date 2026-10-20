#!/usr/bin/env python3
"""Measured stop conditions vs prior strong-chorus SiteID reuse (new exploratory sensitivity)."""
from __future__ import annotations

import importlib.util
import json
from collections import defaultdict
from pathlib import Path
import numpy as np
import pandas as pd
import statsmodels.api as sm

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"build"/"naamp_history_environment"/"result.json"
Z=1.959963984540054

def loadmod(label,path):
    spec=importlib.util.spec_from_file_location(label,path)
    mod=importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(mod)
    return mod

local=loadmod("local_site_memory",ROOT/"exploration/run_naamp_local_chorus_memory_targeting.py")
base=local.base
spatial=local.spatial
sameobs=local.sameobs

def num(x):
    try:
        val=float(str(x or "").strip())
        return val if np.isfinite(val) else np.nan
    except (ValueError,TypeError):
        return np.nan

def construct_stop_covariates(raw,eligible,runs):
    scales={str(r.RunID):str(r.TempScale) for r in runs.itertuples(index=False)}
    result={}
    valid_n=defaultdict(int)
    for rec in raw["Stops.csv"]:
        rid=(rec.get("RunID") or "").strip()
        st=(rec.get("StopNumber") or "").strip()
        if rid not in eligible or not st or (rec.get("SkippedStop") or "").strip()!="0":
            continue
        t=num(rec.get("AirTemp"))
        scale=scales.get(rid)
        if np.isfinite(t):
            t=(t-32)*5/9 if scale=="F" else t if scale=="C" else np.nan
            if np.isfinite(t) and not -10<=t<=45:
                t=np.nan
        mass=num(rec.get("MassNoiseIndex"))
        noise=num(rec.get("Noise"))
        if np.isfinite(mass) and 0<=mass<=4:
            sound=float(mass)
        elif noise in (0.,1.):
            sound=float(noise)
        else:
            sound=np.nan
        timeout=num(rec.get("TimeOut"))
        timeout=timeout if timeout in (0.,1.) else np.nan
        car=num(rec.get("CarCount"))
        car=np.log1p(car) if np.isfinite(car) and 0<=car<=10000 else np.nan
        key=(rid,st)
        if key in result:
            raise RuntimeError(f"duplicate stop environment record: {key}")
        result[key]={"air_temp_c":t,"sound_masking":sound,
                     "timeout":timeout,"log_car_count":car}
        for name,v in result[key].items():
            valid_n[name]+=int(np.isfinite(v))
    return result,dict(valid_n)

def build_analysis_rows(raw):
    runs,sets=base.build_runs(raw)
    eligible=set(runs.RunID.astype(str))
    sampled,_=spatial.stop_matrix(raw,eligible)
    site=local.site_map(raw,eligible)
    ci=local.ci_map(raw,eligible,sampled)
    meta,by_stratum=local.build_history(runs,sampled,site,ci)
    env,availability=construct_stop_covariates(raw,eligible,runs)
    pairs=base.pair_runs(runs,sets)
    stable=pairs.loc[np.asarray(
        [local.stable_pair(p,sampled,site) for p in pairs.itertuples(index=False)],bool)
    ].copy().reset_index(drop=True)
    _,same=sameobs.same_observer_pairs(raw,runs,sets)
    samekeys={(str(p.wet_RunID),str(p.dry_RunID)) for p in same.itertuples(index=False)}
    out=[]
    duplicates=0
    for pid,p in enumerate(stable.itertuples(index=False)):
        w=str(p.wet_RunID)
        site_to_stop=defaultdict(list)
        for st in sorted(sampled[w],key=int):
            site_to_stop[site[(w,st)]].append(st)
        if any(len(v)!=1 for v in site_to_stop.values()):
            duplicates+=1
            continue
        sameobs_key=(w,str(p.dry_RunID)) in samekeys
        block=local.pair_rows(pid,p,sampled,site,ci,meta,by_stratum,sameobs_key)
        for row in block:
            st=site_to_stop[row["SiteID"]][0]
            actual=ci.get((w,st),{})
            other=sum(1 for taxon,v in actual.items() if taxon!=row["species"] and v>=2)
            entry={**row,"stop_number":int(st),"other_strong_taxa":float(other)}
            entry.update(env.get((w,st),{}))
            out.append(entry)
    result=pd.DataFrame(out)
    return result,{"eligible_runs":int(len(runs)),"matched_pairs":int(len(pairs)),
                   "stable_pairs":int(len(stable)),"excluded_pairs_duplicate_SiteID":duplicates,
                   "candidate_rows":int(len(result)),
                   "candidate_pair_species":int(result.pair_species.nunique()) if len(result) else 0,
                   "candidate_routes":int(result.route_cluster.nunique()) if len(result) else 0,
                   "stop_environment_raw_record_coverage":availability}

def eligible(d,columns):
    x=d.copy()
    x=x.replace([np.inf,-np.inf],np.nan)
    x=x.dropna(subset=["prior_site_strong","wet_strong"]+columns)
    if x.empty:
        return x
    ng=x.groupby("pair_species")["prior_site_strong"].nunique()
    x=x[x.pair_species.isin(ng[ng>1].index)].copy()
    return x

def fit_within(d,additional,label):
    if d.empty:
        return {"status":"no_rows","label":label}
    data=d.copy()
    group=data.groupby("pair_species",sort=False)
    names=["prior_site_strong"]+additional
    for col in names+["wet_strong"]:
        data["w_"+col]=data[col].astype(float)-group[col].transform("mean").astype(float)
    # Stop-number position effects, not site fixed effects: spatially static site
    # attributes can still cause historical recurrences.
    chosen=[]
    X=np.empty((len(data),0),float)
    excluded_features=[]
    for name in names:
        col=data["w_"+name].to_numpy(dtype=float)[:,None]
        if np.max(np.abs(col))<1e-12:
            excluded_features.append({"feature":name,"reason":"no_within_group_variation"})
            continue
        test=np.column_stack([X,col])
        if np.linalg.matrix_rank(test,tol=1e-9)>len(chosen):
            X=test
            chosen.append(name)
        else:
            excluded_features.append({"feature":name,"reason":"linearly_redundant"})
    if not chosen or chosen[0]!="prior_site_strong":
        return {"status":"history_predictor_unidentified","label":label}
    routes=data.route_cluster.astype(str)
    if len(data)<500 or routes.nunique()<30:
        return {"status":"insufficient_sample","label":label,
                "n_rows":int(len(data)),"n_routes":int(routes.nunique())}
    y=data["w_wet_strong"].to_numpy(dtype=float)
    fit=sm.OLS(y,X).fit(cov_type="cluster",cov_kwds={"groups":routes})
    beta=float(fit.params[0]);se=float(fit.bse[0])
    return {"status":"fitted","label":label,"n_rows":int(len(data)),
            "n_groups":int(data.pair_species.nunique()),"n_routes":int(routes.nunique()),
            "n_species":int(data.species.nunique()),"same_observer_pairs":int(data.loc[data.same_observer,"pair_id"].nunique()),
            "prior_strong_probability_difference":beta,"route_cluster_se":se,
            "route_cluster_ci95":[beta-Z*se,beta+Z*se],
            "p_two_sided":float(fit.pvalues[0]),
            "included_covariates":chosen[1:],"removed_nonidentifiable_covariates":excluded_features,
            "condition_number":float(np.linalg.cond(X))}

def prepare_position(d):
    x=d.copy()
    for j in range(2,11):
        x[f"stop_{j}"]=(x.stop_number.astype(int)==j).astype(float)
    return x

def main():
    raw=local.load_retry()
    d,cov=build_analysis_rows(raw)
    if d.empty:
        raise RuntimeError("No eligible prior-site history data: cannot run history analysis")
    d=prepare_position(d)
    positions=[f"stop_{j}" for j in range(2,11)]
    temp_data=eligible(d,["air_temp_c"])
    basic=fit_within(temp_data,[],"same_sample_unadjusted_baseline")
    env_model=fit_within(temp_data,["air_temp_c","prior_site_any","other_strong_taxa"]+positions,
                         "site_air_temperature_prior_any_other_taxa_stop_position")
    all_data=eligible(d,["air_temp_c","sound_masking","timeout","log_car_count"])
    full_basic=fit_within(all_data,[],"complete_environment_same_sample_baseline")
    full=fit_within(all_data,["air_temp_c","sound_masking","timeout","log_car_count",
                             "prior_site_any","other_strong_taxa"]+positions,
                    "complete_stop_environment_adjusted")
    sameobs_data=temp_data[temp_data.same_observer].copy()
    sameobs_model=fit_within(sameobs_data,["air_temp_c","prior_site_any","other_strong_taxa"]+positions,
                             "same_observer_site_air_temperature_adjusted")
    out={
        "analysis":"naamp_history_site_reuse_environment_sensitivity_v0_1",
        "status":"new_posthoc_exploratory_not_RC6_confirmation",
        "coverage":{**cov,
                    "air_temperature_model_rows":int(len(temp_data)),
                    "complete_detection_environment_rows":int(len(all_data))},
        "model_same_sample_baseline":basic,
        "model_measured_site_temperature_adjusted":env_model,
        "model_full_environment_completecase_baseline":full_basic,
        "model_full_measured_environment_adjusted":full,
        "same_observer_sensitivity":sameobs_model,
        "interpretation_boundary":{
            "within_pair_species_fixed_effects":True,
            "species_identity_and_shared_route_night_weather_controlled":True,
            "site_air_temperature_measured":True,
            "other_species_stop_night_activity_adjusted":True,
            "local_water_level_or_hydroperiod_measured":False,
            "persistent_habitat_quality_excluded":False,
            "causal_memory_or_philopatry_identified":False,
            "environment_independence_claim":False,
            "RC6_manuscript_or_submission_updated":False}}
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print("ENVIRONMENT_HISTORY_RESULT_BEGIN")
    print(json.dumps(out,sort_keys=True))
    print("ENVIRONMENT_HISTORY_RESULT_END",flush=True)

if __name__=="__main__":
    main()
