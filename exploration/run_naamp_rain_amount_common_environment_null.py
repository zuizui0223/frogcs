#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import importlib.util
import io
import json
import re
import time
import urllib.error
import urllib.request
from collections import defaultdict
from datetime import date, datetime, time as dtime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import icechunk
import numpy as np
import pandas as pd
import patsy
import statsmodels.api as sm
import xarray as xr
from timezonefinder import TimezoneFinder

ROOT=Path(__file__).resolve().parents[1]
EXP=ROOT/"exploration"
OUT=EXP/"NAAMP_RAIN_AMOUNT_COMMON_ENVIRONMENT_NULL_RECEIPT_V0_1.json"

B=1000
SEED=2840223
ANCHOR=0.75
MIN_POSITIVE_CELLS=20
MIN_POSITIVE_ROUTES=5
EPS=1e-7
COORD_URL="https://www.sciencebase.gov/catalog/file/get/583dc314e4b0d1899f9dea8d?f=__disk__77%2F22%2F7e%2F77227ec46ac1c01592cd7d158d442cd8343a7536"
COORD_SHA="f71a87df9fc94e0d6c5d4466b4745c3bbaff874cbe7c28796b3f9eb44c2e6e83"

def loadmod(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    mod=importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(mod)
    return mod

flex=loadmod("flex_common",EXP/"run_naamp_flexible_common_environment_null.py")
joint=flex.joint
mem=flex.mem
uniform=flex.uniform

def retry(fn,label):
    last=None
    for i in range(6):
        try:
            return fn()
        except urllib.error.HTTPError as e:
            last=e
            if getattr(e,"code",None) not in (403,429,500,502,503,504):
                raise
        except Exception as e:
            last=e
            if i>=5:
                raise
        time.sleep(2*(i+1))
    raise RuntimeError(f"{label} failed after retries: {last}")

def fetch_bytes(url):
    req=urllib.request.Request(url,headers={"User-Agent":"frogcs-rain-amount-common-null/0.1"})
    with urllib.request.urlopen(req,timeout=180) as r:
        return r.read()

def load_coords():
    raw=retry(lambda:fetch_bytes(COORD_URL),"Coordinates load")
    got=hashlib.sha256(raw).hexdigest()
    if got!=COORD_SHA:
        raise RuntimeError(f"Coordinates hash drift {got}")
    out={}
    for r in csv.DictReader(io.StringIO(raw.decode("utf-8-sig"))):
        sid=(r.get("SiteID") or "").strip()
        if sid:
            out[sid]=(float(r["lat"]),float(r["lon"]))
    return out

def parse_clock(x):
    s=str(x or "").strip()
    if not s or s.upper()=="NULL":
        return None
    s2=re.sub(r"\s+"," ",s.upper().replace(".","")).strip()
    for fmt in ("%H:%M","%H:%M:%S","%H%M","%I:%M %p","%I:%M:%S %p","%I %p"):
        try:
            return datetime.strptime(s2,fmt).time()
        except Exception:
            pass
    try:
        v=float(s2)
        if 0<=v<24:
            h=int(v); mm=int(round((v-h)*60))
            if mm==60:
                h=(h+1)%24; mm=0
            return dtime(h,mm)
    except Exception:
        pass
    return None

def build_midpoints(raw,runs):
    eligible=set(runs["RunID"].astype(str))
    cmap=load_coords()
    byrun=defaultdict(list)
    for s in raw["Stops.csv"]:
        rid=(s.get("RunID") or "").strip()
        sid=(s.get("SiteID") or "").strip()
        if rid not in eligible or (s.get("SkippedStop") or "").strip()!="0":
            continue
        if sid in cmap:
            byrun[rid].append(cmap[sid])
    centers={}
    for rid,pts in byrun.items():
        if len(pts)>=8:
            centers[rid]=(float(np.mean([p[0] for p in pts])),float(np.mean([p[1] for p in pts])))
    tf=TimezoneFinder(in_memory=True)
    runraw={str(r.get("RunID") or "").strip():r for r in raw["Runs.csv"]}
    dates={
        str(rr.RunID):date(int(rr.SurveyYear),1,1)+timedelta(days=int(rr.doy)-1)
        for rr in runs.itertuples(index=False)
    }
    rec={}
    for rid in sorted(eligible):
        row=runraw.get(rid,{})
        st=parse_clock(row.get("StartTime")); et=parse_clock(row.get("EndTime"))
        if st is None or et is None or rid not in centers:
            continue
        a=datetime.combine(dates[rid],st); b=datetime.combine(dates[rid],et)
        if b<=a:
            b+=timedelta(days=1)
        dur=(b-a).total_seconds()/3600
        if not 0.25<=dur<=6.0:
            continue
        lat,lon=centers[rid]
        tz=tf.timezone_at(lat=lat,lng=lon)
        if not tz:
            continue
        mid=a+(b-a)/2
        z=mid.replace(tzinfo=ZoneInfo(tz))
        rt=z.astimezone(ZoneInfo("UTC")).astimezone(ZoneInfo(tz))
        if rt.replace(tzinfo=None)!=mid:
            continue
        rec[rid]={"lat":lat,"lon":lon,"midpoint":z}
    return rec

def antecedent_amounts(records):
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
    for b0 in range(0,len(ids),batch_size):
        batch=ids[b0:b0+batch_size]
        n=len(batch)
        lat=np.asarray([records[r]["lat"] for r in batch],float)
        lon=np.asarray([records[r]["lon"]%360 for r in batch],float)
        ends=[]
        for r in batch:
            utc=records[r]["midpoint"].astimezone(ZoneInfo("UTC")).replace(tzinfo=None)
            ts=pd.Timestamp(utc).floor("h")
            ends.append(np.datetime64(ts.to_datetime64(),"ns"))
        ends=np.asarray(ends)
        offsets=np.arange(71,-1,-1,dtype="timedelta64[h]")
        times=ends[:,None]-offsets[None,:]
        sel=tp.sel(
            latitude=xr.DataArray(np.repeat(lat,72),dims="point"),
            longitude=xr.DataArray(np.repeat(lon,72),dims="point"),
            valid_time=xr.DataArray(times.reshape(-1),dims="point"),
            method="nearest"
        )
        vals=np.asarray(sel.values,float).reshape(n,72)
        if not np.isfinite(vals).all():
            raise RuntimeError("nonfinite tp")
        if float(vals.min())<-1e-8:
            raise RuntimeError("negative tp beyond tolerance")
        vals[vals<0]=0.0
        mm=vals*1000.0
        sum72=mm.sum(axis=1)
        slat=np.asarray(sel["latitude"].values,float).reshape(n,72)[:,0]
        slon=np.asarray(sel["longitude"].values,float).reshape(n,72)[:,0]
        stime=np.asarray(sel["valid_time"].values).reshape(n,72)
        if np.max(np.abs(slat-lat))>0.126:
            raise RuntimeError("tp latitude mismatch")
        lon_delta=np.minimum(np.abs(slon-lon),360-np.abs(slon-lon))
        if np.max(lon_delta)>0.126:
            raise RuntimeError("tp longitude mismatch")
        if not np.array_equal(stime.astype("datetime64[h]"),times.astype("datetime64[h]")):
            raise RuntimeError("tp hourly-time mismatch")
        for i,rid in enumerate(batch):
            out[rid]={"rain72_mm":float(sum72[i])}
            h.update(f"{rid},{slat[i]:.4f},{slon[i]:.4f},{str(ends[i])},{sum72[i]:.8f}\n".encode())
        print(json.dumps({"weather_runs_processed":min(b0+batch_size,len(ids)),"weather_runs_total":len(ids)}),flush=True)
    return out,h.hexdigest()

def feature_matrix(runs,state_levels,run_levels):
    x=runs.copy().reset_index(drop=True)
    dry_x=np.log1p(x["DaysSinceRain"].astype(float).to_numpy())
    rain_x=x["rain72_log"].astype(float).to_numpy()
    temp=x["mean_temp_c"].astype(float).to_numpy()
    doy=x["doy"].astype(float).to_numpy()
    dry_basis=np.asarray(patsy.dmatrix(
        "bs(v, df=4, degree=3, include_intercept=False, lower_bound=0.0, upper_bound=5.198497031265826) - 1",
        {"v":dry_x},return_type="dataframe"
    ),float)
    rain_basis=np.asarray(patsy.dmatrix(
        "bs(v, df=4, degree=3, include_intercept=False, lower_bound=0.0, upper_bound=6.90875477931522) - 1",
        {"v":rain_x},return_type="dataframe"
    ),float)
    temp_basis=np.asarray(patsy.dmatrix(
        "bs(v, df=4, degree=3, include_intercept=False, lower_bound=-10.0, upper_bound=45.0) - 1",
        {"v":temp},return_type="dataframe"
    ),float)
    theta=2*np.pi*doy/365.25
    harmonics=np.column_stack([np.sin(theta),np.cos(theta),np.sin(2*theta),np.cos(2*theta)])
    interactions=np.column_stack([dry_x*rain_x,rain_x*temp])

    state=np.zeros((len(x),max(0,len(state_levels)-1)),float)
    state_index={v:i for i,v in enumerate(state_levels[1:])}
    for i,v in enumerate(x["State"].astype(str)):
        j=state_index.get(v)
        if j is not None: state[i,j]=1.0
    run=np.zeros((len(x),max(0,len(run_levels)-1)),float)
    run_index={v:i for i,v in enumerate(run_levels[1:])}
    for i,v in enumerate(x["RunNumber"].astype(str)):
        j=run_index.get(v)
        if j is not None: run[i,j]=1.0
    return np.column_stack([
        np.ones(len(x),float),dry_basis,rain_basis,temp_basis,
        harmonics,interactions,state,run
    ])

def fit_predict_amount_environment(runs_weather,sampled,ss,all_species,training_fold):
    x=runs_weather.copy().reset_index(drop=True)
    x["route_fold"]=x["route_cluster"].astype(str).map(joint.fold_for_route)
    state_levels=sorted(x["State"].astype(str).unique())
    run_levels=sorted(x["RunNumber"].astype(str).unique())
    X_all=feature_matrix(x,state_levels,run_levels)
    train=x["route_fold"].to_numpy()==training_fold
    X=X_all[train]
    counts=flex.run_species_counts(x,sampled,ss)
    train_routes=x.loc[train,"route_cluster"].astype(str).to_numpy()
    all_runids=x["RunID"].astype(str).to_numpy()
    eta_by_species={}
    audit={}

    for sp in sorted(all_species):
        y_all=np.asarray([counts[rid].get(sp,0) for rid in all_runids],float)
        y=y_all[train]
        pos_cells=int(y.sum())
        pos_routes=int(len(set(train_routes[y>0])))
        info={"positive_stop_cells":pos_cells,"positive_routes":pos_routes,"estimable":False,"method":"zero_environment_shift"}
        if pos_cells<MIN_POSITIVE_CELLS or pos_routes<MIN_POSITIVE_ROUTES:
            eta_by_species[sp]=np.zeros(len(x),float); audit[sp]=info; continue
        prop=y/10.0
        model=sm.GLM(prop,X,family=sm.families.Binomial(),freq_weights=np.repeat(10.0,len(prop)))
        method="glm"
        try:
            fit=model.fit(maxiter=200,disp=0)
            params=np.asarray(fit.params,float)
            if (not np.all(np.isfinite(params))) or np.max(np.abs(params))>50:
                raise RuntimeError("unstable coefficients")
        except Exception:
            method="ridge_fallback"
            fit=model.fit_regularized(alpha=0.01,L1_wt=0.0,maxiter=1000)
            params=np.asarray(fit.params,float)
            if not np.all(np.isfinite(params)):
                eta_by_species[sp]=np.zeros(len(x),float)
                info["method"]="zero_after_failed_regularization"; audit[sp]=info; continue
        eta=np.clip(X_all@params,-20,20)
        eta_by_species[sp]=eta
        info.update({"estimable":True,"method":method})
        audit[sp]=info

    pred={}
    for i,rid in enumerate(all_runids):
        pred[rid]={sp:float(eta_by_species[sp][i]) for sp in all_species}
    return pred,audit,{
        "training_fold":training_fold,
        "n_training_runs":int(train.sum()),
        "n_training_routes":int(x.loc[train,"route_cluster"].nunique()),
        "n_estimable_species":int(sum(1 for a in audit.values() if a["estimable"])),
        "feature_count":int(X.shape[1])
    }

def simulate_linear(psub,dsub,hsub,slopes_by_train,r,den,seed):
    rng=np.random.default_rng(seed)
    num=np.zeros((B,3),float)
    for i,(p,dct,p_hist) in enumerate(zip(psub.itertuples(index=False),dsub,hsub)):
        test_fold=joint.fold_for_route(str(p.route_cluster))
        train_fold="B" if test_fold=="A" else "A"
        slopes=slopes_by_train[train_fold]
        gamma=np.asarray([float(slopes.get(sp,0.0)) for sp in dct["species"]],float)
        dry=dct["dry"].astype(float)
        p_anchor=(1.0-ANCHOR)*p_hist+ANCHOR*dry
        p_anchor=np.clip(p_anchor,EPS,1-EPS)
        pre=uniform.expit(uniform.logit(p_anchor)+gamma[:,None]*float(p.rain_contrast))
        q=uniform.solve_shift(pre,dct["wet_k"])
        w=rng.random((B,)+q.shape)<q[None,:,:]
        num+=r[i]*flex.sim_metrics(w,dct["dry"])
    return num/den

def simulate_amount(psub,dsub,hsub,pred_by_train,r,den,seed):
    rng=np.random.default_rng(seed)
    num=np.zeros((B,3),float)
    deltas=[]
    for i,(p,dct,p_hist) in enumerate(zip(psub.itertuples(index=False),dsub,hsub)):
        test_fold=joint.fold_for_route(str(p.route_cluster))
        train_fold="B" if test_fold=="A" else "A"
        pred=pred_by_train[train_fold]
        wet_id=str(p.wet_RunID); dry_id=str(p.dry_RunID)
        delta=np.asarray([pred[wet_id].get(sp,0.0)-pred[dry_id].get(sp,0.0) for sp in dct["species"]],float)
        deltas.append(np.abs(delta))
        dry=dct["dry"].astype(float)
        p_anchor=(1.0-ANCHOR)*p_hist+ANCHOR*dry
        p_anchor=np.clip(p_anchor,EPS,1-EPS)
        pre=uniform.expit(uniform.logit(p_anchor)+delta[:,None])
        q=uniform.solve_shift(pre,dct["wet_k"])
        w=rng.random((B,)+q.shape)<q[None,:,:]
        num+=r[i]*flex.sim_metrics(w,dct["dry"])
    dd=np.concatenate(deltas) if deltas else np.asarray([],float)
    return num/den,{
        "mean_abs_species_pair_logit_shift":float(np.mean(dd)) if len(dd) else 0.0,
        "q95_abs_species_pair_logit_shift":float(np.quantile(dd,.95)) if len(dd) else 0.0
    }

def main():
    raw,runs,psub,dsub,hsub,pools,sampled,ss=flex.prepare_subset()
    mid=build_midpoints(raw,runs)
    weather,weather_sha=antecedent_amounts(mid)

    mask=np.asarray([
        str(p.wet_RunID) in weather and str(p.dry_RunID) in weather
        for p in psub.itertuples(index=False)
    ],bool)
    idx=np.flatnonzero(mask)
    pw=psub.iloc[idx].copy().reset_index(drop=True)
    dw=[dsub[int(i)] for i in idx]
    hw=[hsub[int(i)] for i in idx]
    if len(pw)<2700:
        raise RuntimeError(f"weather/prior-history intersection unexpectedly small: {len(pw)}")

    runs_weather=runs[runs["RunID"].astype(str).isin(weather)].copy().reset_index(drop=True)
    runs_weather["rain72_mm"]=[weather[str(r)]["rain72_mm"] for r in runs_weather["RunID"].astype(str)]
    runs_weather["rain72_log"]=np.log1p(runs_weather["rain72_mm"].astype(float))

    all_species=sorted({sp for spp in pools.values() for sp in spp})

    slopes_A,audit_linear_A,linear_fold_A=joint.fit_species_slopes(runs,sampled,ss,all_species,"A")
    slopes_B,audit_linear_B,linear_fold_B=joint.fit_species_slopes(runs,sampled,ss,all_species,"B")
    slopes_by_train={"A":slopes_A,"B":slopes_B}

    pred_A,audit_A,fold_A=fit_predict_amount_environment(runs_weather,sampled,ss,all_species,"A")
    pred_B,audit_B,fold_B=fit_predict_amount_environment(runs_weather,sampled,ss,all_species,"B")
    pred_by_train={"A":pred_A,"B":pred_B}

    obs_rows=np.asarray([flex.metrics(d["wet"],d["dry"]) for d in dw],float)
    r,den=uniform.design_residual(pw)
    obs=(r[:,None]*obs_rows).sum(axis=0)/den

    sim_linear=simulate_linear(pw,dw,hw,slopes_by_train,r,den,SEED+201)
    linear_result=flex.conditional(sim_linear,obs)

    sim_amount,shift_audit=simulate_amount(pw,dw,hw,pred_by_train,r,den,SEED+202)
    amount_result=flex.conditional(sim_amount,obs)

    base_res=float(linear_result["observed_conditional_residual"])
    amount_res=float(amount_result["observed_conditional_residual"])
    frac=(base_res-amount_res)/base_res if base_res!=0 else None

    decision=(
        "rain_amount_common_environment_sufficient"
        if not amount_result["above_upper_95"]
        else
        "residual_dependence_beyond_rain_amount_common_environment"
    )

    out={
        "analysis":"naamp_rain_amount_common_environment_null_v0_1",
        "contract":"exploration/NAAMP_RAIN_AMOUNT_COMMON_ENVIRONMENT_NULL_CONTRACT_V0_1.json",
        "status":"posthoc_second_stage_after_explicit_reopening",
        "coverage":{
            "prior_history_pairs":int(len(psub)),
            "weather_prior_history_pairs":int(len(pw)),
            "routes":int(pw.route_cluster.nunique()),
            "states":int(pw.State.nunique()),
            "weather_runs":int(len(weather))
        },
        "era5":{
            "antecedent_amount_sha256":weather_sha,
            "primary_window_hours":72
        },
        "observed":{
            "route_new_species_beta":float(obs[0]),
            "extra_stop_beta":float(obs[1]),
            "concentration_beta":float(obs[2])
        },
        "same_sample_existing_linear_comparator":linear_result,
        "rain_amount_common_environment_null":amount_result,
        "comparison":{
            "linear_residual":base_res,
            "rain_amount_residual":amount_res,
            "fraction_of_same_sample_linear_residual_removed":float(frac) if frac is not None else None,
            "linear_predicted_concentration_beta":float(linear_result["predicted_concentration_beta"]),
            "rain_amount_predicted_concentration_beta":float(amount_result["predicted_concentration_beta"])
        },
        "rain_amount_model_training":{
            "fold_A":fold_A,
            "fold_B":fold_B,
            "fold_A_species":audit_A,
            "fold_B_species":audit_B
        },
        "environment_shift_audit":shift_audit,
        "decision":decision,
        "interpretation_boundary":{
            "independent_confirmation":False,
            "posthoc_exploratory":True,
            "era5_is_local_hydrology":False,
            "unmeasured_hydroperiod_excluded":False,
            "social_facilitation_identified":False,
            "synchronous_breeding_identified":False,
            "unique_mechanism_identified":False
        }
    }
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
