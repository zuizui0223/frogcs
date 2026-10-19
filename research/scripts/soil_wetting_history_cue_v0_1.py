#!/usr/bin/env python3
"""Antecedent ERA5 soil-water trajectory vs present hydric state, NAAMP 2001–15.

Executable protocol: research/NAAMP_HYDRIC_TRAJECTORY_CONTRACT_2026-10-19.md
This observational post hoc test does NOT imply an experimental dry→wet event,
soil moisture sensing by frogs, egg deposition, reproductive success, or JAE C.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import platform
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
import importlib.util

import numpy as np
import pandas as pd
import scipy
import statsmodels
import statsmodels.formula.api as smf
from scipy.stats import norm

import environment_within_route as core

ROOT=Path(__file__).resolve().parents[2]
PRIMARY_RESPONSE="strong_new_count"
TRAJECTORY_TERMS=("h7_delta","h24_delta")
MANIFEST=("paired_environment_and_chorus.csv.gz",
          "environment_by_run.csv.gz","RESULT.json","source_audit.json")
OLD_RUNS_SHA="ece570314de06bdee036920251ecb53c0556c4d609bc1ca72568581467cf1d02"
FULL_PAIR_N=4108
STABLE_PAIR_N=4045
STABLE_ROUTE_N=563
RUN_N=7559
DELTAS=(24,168)
MIN_PAIRS=3000
MIN_ROUTES=450
BASE_FORMULA=("strong_new_count ~ rain_contrast + rain72 + temp_difference"
              " + doy_difference + year_gap + C(State) + C(RunNumber)"
              " + vpd_relief + vpd_mid + air_mid + soil_mid"
              " + soil2_mid + layer_common + surface_excess")

def per_001(value):
    return float(value)*0.01

def source_times(local_midpoint:datetime):
    if local_midpoint.tzinfo is None or local_midpoint.utcoffset() is None:
        raise ValueError("source survey time missing timezone")
    utc=local_midpoint.astimezone(ZoneInfo("UTC")).replace(tzinfo=None)
    base=np.datetime64(pd.Timestamp(utc).floor("h").to_datetime64(),"ns")
    return {"now":base,
            "minus24":base-np.timedelta64(24,"h"),
            "minus168":base-np.timedelta64(168,"h")}

def verify_cache(path:Path):
    mfile=path/"SHA256.json"
    if not mfile.is_file():
        raise ValueError("missing original environment manifest")
    manifest=json.loads(mfile.read_text())
    if set(manifest)!=set(MANIFEST) or not all((path/n).is_file() for n in manifest):
        raise ValueError("missing or unexpected original environment members")
    for name,digest in manifest.items():
        got=hashlib.sha256((path/name).read_bytes()).hexdigest()
        if got!=digest:
            raise ValueError("cache original source checksum drift "+name)
    audit=json.loads((path/"source_audit.json").read_text())
    if audit.get("weather",{}).get("weather_sha256")!=OLD_RUNS_SHA:
        raise ValueError("original pinned ERA5 soil-water and rain values drift")
    source=pd.read_csv(path/"environment_by_run.csv.gz",dtype={"RunID":str})
    pairs=pd.read_csv(path/"paired_environment_and_chorus.csv.gz",dtype={
        "wet_RunID":str,"dry_RunID":str,"RouteNumber":str,"RunNumber":str})
    core.validate_outcome_identities(pairs)
    if len(source)!=RUN_N or source.RunID.duplicated().any():
        raise ValueError("original run environment cache support drift")
    if len(pairs)!=FULL_PAIR_N or pairs[["wet_RunID","dry_RunID"]].duplicated().any():
        raise ValueError("original pair cache support drift")
    if (int(pairs.stable_sites.sum()),int(pairs[pairs.stable_sites].route_cluster.nunique()))!=(
           STABLE_PAIR_N,STABLE_ROUTE_N):
        raise ValueError("original stable physical site subset drift")
    if not set(pairs.wet_RunID)|set(pairs.dry_RunID) <= set(source.RunID):
        raise ValueError("pair RunIDs absent from original weather cache")
    return source,pairs,audit

def validate_historical_s2(array):
    a=np.asarray(array,float)
    if not np.isfinite(a).all() or (a<-.02).any() or (a>.8).any():
        raise ValueError("nonfinite or implausible ERA5 soil value")
    return True

def extract(midpoints:dict,existing:pd.DataFrame,old)->pd.DataFrame:
    import icechunk
    import xarray as xr
    archived=dict(zip(existing.RunID.astype(str),existing[["swvl1","swvl2"]].to_numpy()))
    expected=set(archived)
    if not expected.issubset(midpoints):
        raise ValueError(f"missing original run midpoint: {len(expected-set(midpoints))}")
    ids=sorted(expected)
    storage=icechunk.s3_storage(bucket="earthmover-icechunk-era5",
        prefix="icechunkV2",region="us-east-1",anonymous=True)
    repo=icechunk.Repository.open(storage)
    session=repo.readonly_session("main")
    ds=xr.open_zarr(session.store,group="single/temporal",
                    consolidated=False,chunks=None)
    s1_name=old.hydric.find_grib_var(ds,39,["volumetric soil water layer 1","swvl1"])
    s2_name=old.hydric.find_grib_var(ds,40,["volumetric soil water layer 2","swvl2"])
    s1=ds[s1_name];s2=ds[s2_name]
    for var,pid in ((s1,39),(s2,40)):
        if str(var.attrs.get("GRIB_paramId"))!=str(pid):
            raise ValueError("wrong GRIB soil layer ID")
        if "m**3" not in str(var.attrs.get("units")):
            raise ValueError("wrong soil volumetric units")
    results=[]
    for start in range(0,len(ids),200):
        batch=ids[start:start+200]
        lat=xr.DataArray([midpoints[k]["lat"] for k in batch],dims="point")
        lon=xr.DataArray([midpoints[k]["lon"]%360 for k in batch],dims="point")
        times=[source_times(midpoints[k]["midpoint"]) for k in batch]
        stamps={label:xr.DataArray(np.asarray([q[label] for q in times],dtype="datetime64[ns]"),
                    dims="point") for label in ("now","minus24","minus168")}
        measurements={}
        for label,clock in stamps.items():
            for varname,var in (("soil1",s1),("soil2",s2)):
                arr=np.asarray(var.sel(latitude=lat,longitude=lon,
                    valid_time=clock,method="nearest").values,float)
                if arr.shape!=(len(batch),):
                    raise ValueError("unexpected soil extraction array shape")
                validate_historical_s2(arr)
                measurements[(varname,label)]=arr
        for i,rid in enumerate(batch):
            row={"RunID":rid}
            for var,idx in (("soil1",0),("soil2",1)):
                value=measurements[(var,"now")][i]
                old_value=float(archived[rid][idx])
                if not np.isclose(value,old_value,rtol=0,atol=1e-8):
                    raise ValueError(f"current ERA5 water drift for pinned RunID {rid}")
                row[var+"_t"]=float(value)
                row[var+"_24h"]=float(measurements[(var,"minus24")][i])
                row[var+"_168h"]=float(measurements[(var,"minus168")][i])
            results.append(row)
        print(json.dumps({"source_runs_processed":min(start+len(batch),len(ids)),
                          "source_runs_total":len(ids),"hours_pre_survey":[24,168]}),
              flush=True)
    return pd.DataFrame(results).sort_values("RunID").reset_index(drop=True)

def attach(pairs:pd.DataFrame,byrun:pd.DataFrame)->pd.DataFrame:
    required={"RunID","soil1_t","soil2_t","soil1_24h","soil2_24h",
              "soil1_168h","soil2_168h"}
    if not required.issubset(byrun):
        raise ValueError("missing historical soil columns")
    if byrun.RunID.astype(str).duplicated().any():
        raise ValueError("duplicate RunID in historical ERA5")
    x=pairs.copy().reset_index(drop=True)
    if not {"wet_RunID","dry_RunID","soil1_w","soil2_w","soil1_d","soil2_d"}.issubset(x):
        raise ValueError("missing original soil pair columns")
    byrun=byrun.copy()
    byrun["RunID"]=byrun.RunID.astype(str)
    if any(not np.isfinite(byrun[v].to_numpy(float)).all() for v in required-{"RunID"}):
        raise ValueError("missing or nonfinite lagged soil values")
    for side,key in (("w","wet_RunID"),("d","dry_RunID")):
        x[key]=x[key].astype(str)
        src=byrun.rename(columns={"RunID":key,**{
            n:n+"_"+side for n in required-{"RunID"}})
        x=x.merge(src,on=key,how="left",validate="many_to_one",sort=False,
                  indicator=True)
        if not (x["_merge"]=="both").all():
            raise ValueError("missing historical ERA5 RunID in original pair sample")
        x=x.drop(columns=["_merge"])
        for soil in ("soil1","soil2"):
            now=x[soil+"_t_"+side].to_numpy(float)
            base=x[soil+"_"+side].to_numpy(float)
            if not np.allclose(now,base,rtol=0,atol=1e-8):
                raise ValueError("current cached soil values disagree with trajectory source")
        x["h7_"+side]=(
             x["soil1_t_"+side]+x["soil2_t_"+side]
            -x["soil1_168h_"+side]-x["soil2_168h_"+side])/2
        x["h24_"+side]=(
             x["soil1_t_"+side]+x["soil2_t_"+side]
            -x["soil1_24h_"+side]-x["soil2_24h_"+side])/2
    x["h7_delta"]=x.h7_w-x.h7_d
    x["h24_delta"]=x.h24_w-x.h24_d
    x["soil2_mid"]=(x.soil2_w+x.soil2_d)/2
    x["current_soil_common_delta"]=(
       (x.soil1_w+x.soil2_w)-(x.soil1_d+x.soil2_d))/2
    if len(x)!=len(pairs) or not np.isfinite(
         x[["h7_delta","h24_delta","soil2_mid","current_soil_common_delta"]].to_numpy()).all():
        raise ValueError("missing or duplicated soil history pair attachment")
    return x

def study_design(pairs):
    a,columns=core.design(pairs)
    a["h7_delta"]=pairs["h7_delta"].to_numpy(float)
    a["h24_delta"]=pairs["h24_delta"].to_numpy(float)
    a["soil2_mid"]=pairs["soil2_mid"].to_numpy(float)
    newcols=columns+["soil2_mid"]
    if any((not np.isfinite(a[col]).all() or a[col].std(ddof=0)<=0)
           for col in ("h7_delta","h24_delta")):
        raise ValueError("historical changes do not have sufficient variation")
    return a,newcols

def main_results(a,cols):
    r0=core.absorb_fit(a,["strong_new_count"],cols)
    original=core.absorb_fit(a,["strong_new_count"],[c for c in cols if c!="soil2_mid"])
    orig_beta=original["strong_new_count"]["terms"]["layer_common"]["beta_per_0_01"]
    if abs(orig_beta-.0990725077169994)>1e-8:
        raise ValueError("frozen route FE common soil coefficient not reproduced")
    results={"previous_exact_soil_beta_per001":orig_beta,
             "present_state_only_with_two_layer_means":r0["strong_new_count"]}
    pvals=[]
    for term in TRAJECTORY_TERMS:
        fit=core.absorb_fit(a,["strong_new_count"],cols+[term])["strong_new_count"]
        if term not in fit["terms"]:
            raise ValueError(f"not identifiable: {term}")
        t=fit["terms"][term]
        pvals.append(t["p"])
        results[term]={"effect":t,"soil_delta_adjusted":fit["terms"]["layer_common"],
                       "n_pairs":fit["pairs"],"n_routes":fit["routes"],
                       "within_residual_rmse":fit["within_residual_rmse"]}
    results["holm_two"]=dict(zip(TRAJECTORY_TERMS,core.holm(pvals).tolist()))
    return results

def sensitivity(a,cols):
    out={}
    for label,subset,strata in [
        ("same_observer",a[a.same_observer].copy(),"route_cluster"),
        ("route_by_survey_round",a,"route_season"),
    ]:
        if len(subset)<2000 or subset.route_cluster.nunique()<250:
            out[label]={"status":"not_estimated_insufficient_original_coverage",
                        "pairs":len(subset)}
            continue
        fit=core.absorb_fit(subset,["strong_new_count"],
                            cols+["h7_delta"],strata)["strong_new_count"]
        out[label]={"pairs":fit["pairs"],"routes":fit["routes"],
                    "seven_day":fit["terms"].get("h7_delta")}
    ay,years=core.design(a,True)
    for key in ["h7_delta","h24_delta","soil2_mid"]:
        ay[key]=a[key].to_numpy()
    fitted=core.absorb_fit(ay,["strong_new_count"],years+["soil2_mid","h7_delta"])["strong_new_count"]
    out["route_and_both_survey_years"]={
        "pairs":fitted["pairs"],"routes":fitted["routes"],
        "seven_day":fitted["terms"].get("h7_delta")}
    return out

def temporal_test(a):
    train=a[a.year_later<=2008].copy()
    test=a[a.year_earlier>=2009].copy()
    expected=(1403,2111)
    if (len(train),len(test))!=expected:
        raise ValueError("original 2008 chronological time split changed")
    keep=test.State.astype(str).isin(train.State.astype(str).unique())&(
         test.RunNumber.astype(str).isin(train.RunNumber.astype(str).unique()))
    excluded=int((~keep).sum())
    test=test[keep].copy()
    if len(test)!=1519:
        raise ValueError("previous temporal validation population drift")
    pred={}
    for model_name,formula in (("present_only",BASE_FORMULA),
                               ("plus_7day",BASE_FORMULA+" + h7_delta"),
                               ("plus_24h",BASE_FORMULA+" + h24_delta")):
        fitted=smf.ols(formula,train).fit()
        pred[model_name]=np.asarray(fitted.predict(test),float)
    observed=test.strong_new_count.to_numpy(float)
    groups=test.route_cluster.astype(str).to_numpy()
    def score(mask):
        y=observed[mask]
        routes=groups[mask]
        result={}
        gains={}
        for label,x in pred.items():
            err=(y-x[mask])**2
            means=pd.DataFrame({"route":routes,"value":err}).groupby("route",sort=True).value.mean()
            result[label]=float(means.mean())
        for label in ("plus_7day","plus_24h"):
            gain=(y-pred["present_only"][mask])**2-(y-pred[label][mask])**2
            route_gains=pd.DataFrame({"route":routes,"value":gain}).groupby("route",sort=True).value.mean().to_numpy()
            rng=np.random.default_rng(20261019 if label=="plus_7day" else 20261020)
            boot=route_gains[rng.integers(0,len(route_gains),size=(2000,len(route_gains)))].mean(axis=1)
            gains[label]={"route_equal_MSE_reduction":float(route_gains.mean()),
                          "ci95_route_bootstrap_conditioned_training":np.quantile(boot,[.025,.975]).tolist()}
        return {"pairs":len(y),"routes":len(set(routes)),"mse":result,"gain_vs_present":gains}
    seen=np.isin(groups,train.route_cluster.astype(str).unique())
    return {"original_2008_cutoff_frozen":True,"train_pairs":len(train),
            "test_pairs":len(test),"source_unknown_category_excluded":excluded,
            "all":score(np.ones(len(test),bool)),
            "seen_routes":score(seen),"unseen_routes":score(~seen),
            "no_coefficients_refitted_on_test":True,
            "train_parameter_uncertainty_in_intervals":False,
            "not_independent_external_replication":True}

def run(args):
    cache=Path(args.environment_cache)
    original,pairs,source=verify_cache(cache)
    if args.reuse_lags:
        history=pd.read_csv(Path(args.reuse_lags),dtype={"RunID":str})
    else:
        old_path=Path(args.source_root)
        p=old_path/"exploration/run_naamp_soil_moisture_cue.py"
        s=importlib.util.spec_from_file_location("old_soil_source",p)
        old=importlib.util.module_from_spec(s)
        assert s.loader
        s.loader.exec_module(old)
        raw=old.hydric.retry(old.base.load,"pinned USGS NAAMP")
        runs,sets=old.base.build_runs(raw)
        mid=old.hydric.retry(lambda:old.hydric.build_midpoints(raw,runs),
                             "pinned USGS source coordinate midpoints")
        history=extract(mid,original,old)
    a=attach(pairs,history)
    sub=a[a.stable_sites].copy()
    if len(sub)<MIN_PAIRS or int(sub.route_cluster.nunique())<MIN_ROUTES:
        raise ValueError("predeclared historical ERA5 coverage minimum not met")
    x,cols=study_design(sub)
    result={
      "analysis":"NAAMP_current_equal_soil_antecedent_7d_24h_mechanism_2026_10_19",
      "source":{"environment_cache_manifest_sha256":
               hashlib.sha256((cache/"SHA256.json").read_bytes()).hexdigest(),
                "historical_soil_source":"same public Earthmover ERA5 0.25° grid",
                "historical_time_offsets_hours":[24,168],
                "original_source_weather_sha256":OLD_RUNS_SHA,
                "source_original_runs":len(original),
                "source_original_pairs":len(pairs)},
      "coverage":{"pairs":len(sub),"routes":int(sub.route_cluster.nunique()),
                  "states":int(sub.State.nunique()),
                  "lagged_runids":len(history)},
      "frozen_design":{"primary":"h7_delta","secondary":"h24_delta",
                       "past_only":True,"wet_dry_assignment_chronological":False,
                       "one_primary_test_plus_24h_sensitivity":True},
      "observational_association":main_results(x,cols),
      "sensitivity":sensitivity(x,cols),
      "fixed_2008_temporal_transfer":temporal_test(x),
      "source_boundaries":{"not_groundwater_or_substrate_measured_at_pools":True,
                           "not_actual_breeding_success":True,
                           "not_causal_hydric_trigger":True,
                           "not_original_JAE_concentration_C":True,
                           "not_sequential_wet_dry_survey":True,
                           "no_changes_to_main":True}
    }
    out=Path(args.outdir);out.mkdir(parents=True,exist_ok=True)
    history.to_csv(out/"lagged_soil_by_run.csv.gz",index=False,compression="gzip")
    a.to_csv(out/"paired_environment_soil_trajectory.csv.gz",index=False,compression="gzip")
    (out/"RESULT.json").write_text(json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+"\n")
    hashed={p.name:hashlib.sha256(p.read_bytes()).hexdigest()
            for p in out.iterdir() if p.is_file()}
    (out/"SHA256.json").write_text(json.dumps(hashed,sort_keys=True,indent=2)+"\n")
    print("RESULT_BEGIN")
    print(json.dumps({
       "analysis":result["analysis"],
       "coverage":result["coverage"],
       "old_original_soil":result["observational_association"]["previous_exact_soil_beta_per001"],
       "seven_day":result["observational_association"]["h7_delta"],
       "one_day":result["observational_association"]["h24_delta"],
       "holm":result["observational_association"]["holm_two"],
       "time_transfer":result["fixed_2008_temporal_transfer"],
       "same_observer":result["sensitivity"]["same_observer"]},
       indent=2,sort_keys=True,allow_nan=False))
    print("RESULT_END")
    return result

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--environment-cache",type=Path,required=True)
    p.add_argument("--source-root",type=Path,default=Path("_soil_original"))
    p.add_argument("--outdir",type=Path,default=Path("research/output/soil_history_20261019"))
    p.add_argument("--reuse-lags",type=Path,default=None)
    run(p.parse_args())
if __name__=="__main__":main()
