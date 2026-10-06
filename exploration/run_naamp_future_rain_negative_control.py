#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
from zoneinfo import ZoneInfo

import icechunk
import numpy as np
import pandas as pd
import xarray as xr

ROOT=Path(__file__).resolve().parents[1]
EXP=ROOT/"exploration"
OUT=EXP/"NAAMP_FUTURE_RAIN_NEGATIVE_CONTROL_RECEIPT_V0_1.json"

B=1000
SEED=2840273
EXPECTED_ANTECEDENT_SHA="d27e743c98a2c6abf9a47590a1b1358b436b6f91966f2c7e14e8f6e9c3c179c1"

def loadmod(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    mod=importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(mod)
    return mod

rain=loadmod("rain_amount_existing",EXP/"run_naamp_rain_amount_common_environment_null.py")
flex=rain.flex
joint=rain.joint
uniform=rain.uniform

def future_amounts(records):
    ids=sorted(records)
    storage=icechunk.s3_storage(
        bucket="earthmover-icechunk-era5",prefix="icechunkV2",
        region="us-east-1",anonymous=True
    )
    repo=icechunk.Repository.open(storage)
    session=repo.readonly_session("main")
    ds=xr.open_zarr(session.store,group="single/temporal",consolidated=False,chunks=None)
    tp=ds["tp"]
    if tp.attrs.get("GRIB_paramId") not in (228,"228") or str(tp.attrs.get("units"))!="m":
        raise RuntimeError("ERA5 tp identity drift")
    if "1 hour" not in str(tp.attrs.get("accumulation_comment","")):
        raise RuntimeError("ERA5 tp accumulation semantics drift")

    out={}
    h=hashlib.sha256()
    batch_size=250
    offsets=np.arange(1,73,dtype="timedelta64[h]")
    for b0 in range(0,len(ids),batch_size):
        batch=ids[b0:b0+batch_size]
        n=len(batch)
        lat=np.asarray([records[r]["lat"] for r in batch],float)
        lon=np.asarray([records[r]["lon"]%360 for r in batch],float)
        starts=[]
        for rid in batch:
            utc=records[rid]["midpoint"].astimezone(ZoneInfo("UTC")).replace(tzinfo=None)
            starts.append(np.datetime64(pd.Timestamp(utc).floor("h").to_datetime64(),"ns"))
        starts=np.asarray(starts)
        times=starts[:,None]+offsets[None,:]
        sel=tp.sel(
            latitude=xr.DataArray(np.repeat(lat,72),dims="point"),
            longitude=xr.DataArray(np.repeat(lon,72),dims="point"),
            valid_time=xr.DataArray(times.reshape(-1),dims="point"),
            method="nearest"
        )
        vals=np.asarray(sel.values,float).reshape(n,72)
        if not np.isfinite(vals).all():
            raise RuntimeError("nonfinite future tp")
        if float(vals.min())<-1e-8:
            raise RuntimeError("negative future tp beyond tolerance")
        vals[vals<0]=0.0
        mm=vals*1000.0
        sum72=mm.sum(axis=1)
        slat=np.asarray(sel["latitude"].values,float).reshape(n,72)[:,0]
        slon=np.asarray(sel["longitude"].values,float).reshape(n,72)[:,0]
        stime=np.asarray(sel["valid_time"].values).reshape(n,72)
        if np.max(np.abs(slat-lat))>0.126:
            raise RuntimeError("future tp latitude mismatch")
        lon_delta=np.minimum(np.abs(slon-lon),360-np.abs(slon-lon))
        if np.max(lon_delta)>0.126:
            raise RuntimeError("future tp longitude mismatch")
        if not np.array_equal(stime.astype("datetime64[h]"),times.astype("datetime64[h]")):
            raise RuntimeError("future tp hourly-time mismatch")
        for i,rid in enumerate(batch):
            out[rid]={"rain72_future_mm":float(sum72[i])}
            h.update(f"{rid},{slat[i]:.4f},{slon[i]:.4f},{str(starts[i])},{sum72[i]:.8f}\n".encode())
        print(json.dumps({"future_weather_runs_processed":min(b0+batch_size,len(ids)),"weather_runs_total":len(ids)}),flush=True)
    return out,h.hexdigest()

def main():
    raw,runs,psub,dsub,hsub,pools,sampled,ss=flex.prepare_subset()
    mid=rain.build_midpoints(raw,runs)
    antecedent,antecedent_sha=rain.antecedent_amounts(mid)
    if antecedent_sha!=EXPECTED_ANTECEDENT_SHA:
        raise RuntimeError(
            f"antecedent weather reproduction failed: {antecedent_sha} != {EXPECTED_ANTECEDENT_SHA}"
        )
    future,future_sha=future_amounts(mid)

    mask=np.asarray([
        str(p.wet_RunID) in antecedent and str(p.dry_RunID) in antecedent and
        str(p.wet_RunID) in future and str(p.dry_RunID) in future
        for p in psub.itertuples(index=False)
    ],bool)
    idx=np.flatnonzero(mask)
    pw=psub.iloc[idx].copy().reset_index(drop=True)
    dw=[dsub[int(i)] for i in idx]
    hw=[hsub[int(i)] for i in idx]

    coverage={
        "pairs":int(len(pw)),
        "routes":int(pw.route_cluster.nunique()) if len(pw) else 0,
        "states":int(pw.State.nunique()) if len(pw) else 0,
        "weather_runs_both_windows":int(len(set(antecedent)&set(future))),
    }
    gate=coverage["pairs"]>=2700 and coverage["routes"]>=400 and coverage["states"]>=18
    out={
        "analysis":"naamp_future_rain_negative_control_v0_1",
        "contract":"exploration/NAAMP_FUTURE_RAIN_NEGATIVE_CONTROL_CONTRACT_V0_1.json",
        "coverage":{**coverage,"gate_pass":gate},
        "response_endpoint_read":False,
    }
    if not gate:
        OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
        print(json.dumps(out,indent=2,sort_keys=True))
        return

    common_runs=sorted(set(antecedent)&set(future))
    runs_base=runs[runs["RunID"].astype(str).isin(common_runs)].copy().reset_index(drop=True)

    runs_ant=runs_base.copy()
    runs_ant["rain72_mm"]=[antecedent[str(r)]["rain72_mm"] for r in runs_ant["RunID"].astype(str)]
    runs_ant["rain72_log"]=np.log1p(runs_ant["rain72_mm"].astype(float))

    runs_fut=runs_base.copy()
    runs_fut["rain72_mm"]=[future[str(r)]["rain72_future_mm"] for r in runs_fut["RunID"].astype(str)]
    runs_fut["rain72_log"]=np.log1p(runs_fut["rain72_mm"].astype(float))

    all_species=sorted({sp for spp in pools.values() for sp in spp})
    slopes_A,_,linear_fold_A=joint.fit_species_slopes(runs,sampled,ss,all_species,"A")
    slopes_B,_,linear_fold_B=joint.fit_species_slopes(runs,sampled,ss,all_species,"B")
    slopes_by_train={"A":slopes_A,"B":slopes_B}

    ant_A,ant_audit_A,ant_fold_A=rain.fit_predict_amount_environment(runs_ant,sampled,ss,all_species,"A")
    ant_B,ant_audit_B,ant_fold_B=rain.fit_predict_amount_environment(runs_ant,sampled,ss,all_species,"B")
    fut_A,fut_audit_A,fut_fold_A=rain.fit_predict_amount_environment(runs_fut,sampled,ss,all_species,"A")
    fut_B,fut_audit_B,fut_fold_B=rain.fit_predict_amount_environment(runs_fut,sampled,ss,all_species,"B")
    ant_by_train={"A":ant_A,"B":ant_B}
    fut_by_train={"A":fut_A,"B":fut_B}

    obs_rows=np.asarray([flex.metrics(d["wet"],d["dry"]) for d in dw],float)
    r,den=uniform.design_residual(pw)
    obs=(r[:,None]*obs_rows).sum(axis=0)/den

    sim_linear=rain.simulate_linear(pw,dw,hw,slopes_by_train,r,den,SEED+101)
    linear_result=flex.conditional(sim_linear,obs)

    # Use identical random seed for the two amount models to reduce Monte Carlo noise
    # in their descriptive comparison.
    sim_ant,ant_shift=rain.simulate_amount(pw,dw,hw,ant_by_train,r,den,SEED+202)
    sim_fut,fut_shift=rain.simulate_amount(pw,dw,hw,fut_by_train,r,den,SEED+202)
    ant_result=flex.conditional(sim_ant,obs)
    fut_result=flex.conditional(sim_fut,obs)

    base_res=float(linear_result["observed_conditional_residual"])
    ant_res=float(ant_result["observed_conditional_residual"])
    fut_res=float(fut_result["observed_conditional_residual"])
    ant_frac=(base_res-ant_res)/base_res if base_res!=0 else None
    fut_frac=(base_res-fut_res)/base_res if base_res!=0 else None

    # Descriptive pair-level amount relationships.
    run_ant=np.asarray([antecedent[r]["rain72_mm"] for r in common_runs],float)
    run_fut=np.asarray([future[r]["rain72_future_mm"] for r in common_runs],float)
    corr=float(np.corrcoef(np.log1p(run_ant),np.log1p(run_fut))[0,1]) if len(run_ant)>2 else None

    classification=(
        "future_placebo_rejected"
        if bool(fut_result["above_upper_95"])
        else "future_placebo_sufficient"
    )

    out.update({
        "response_endpoint_read":True,
        "status":"complete",
        "era5":{
            "antecedent_sha256":antecedent_sha,
            "future_sha256":future_sha,
            "antecedent_window_hours":72,
            "future_window_hours":72,
            "future_window_offset_hours":[1,72],
        },
        "observed":{
            "route_new_species_beta":float(obs[0]),
            "extra_stop_beta":float(obs[1]),
            "concentration_beta":float(obs[2]),
        },
        "same_sample_linear_comparator":linear_result,
        "antecedent_72h_amount_model":ant_result,
        "future_72h_placebo_model":fut_result,
        "residual_comparison":{
            "linear_residual":base_res,
            "antecedent_residual":ant_res,
            "future_residual":fut_res,
            "antecedent_fraction_removed":float(ant_frac) if ant_frac is not None else None,
            "future_fraction_removed":float(fut_frac) if fut_frac is not None else None,
            "antecedent_minus_future_fraction_removed":float(ant_frac-fut_frac) if ant_frac is not None and fut_frac is not None else None,
            "run_level_log1p_antecedent_future_correlation":corr,
        },
        "environment_shift_audit":{
            "antecedent":ant_shift,
            "future":fut_shift,
        },
        "model_training":{
            "linear":{"fold_A":linear_fold_A,"fold_B":linear_fold_B},
            "antecedent":{"fold_A":ant_fold_A,"fold_B":ant_fold_B,
                           "n_estimable_A":int(sum(v["estimable"] for v in ant_audit_A.values())),
                           "n_estimable_B":int(sum(v["estimable"] for v in ant_audit_B.values()))},
            "future":{"fold_A":fut_fold_A,"fold_B":fut_fold_B,
                       "n_estimable_A":int(sum(v["estimable"] for v in fut_audit_A.values())),
                       "n_estimable_B":int(sum(v["estimable"] for v in fut_audit_B.values()))},
        },
        "classification":classification,
        "interpretation_boundary":{
            "posthoc_negative_control":True,
            "causal_rainfall_claim":False,
            "future_rain_can_proxy_persistent_wet_regime":True,
            "future_placebo_failure_proves_causality":False,
            "days_since_rain_retained_in_both_amount_models":True,
        }
    })
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(out,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
