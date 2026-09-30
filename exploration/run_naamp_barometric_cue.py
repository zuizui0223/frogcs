#!/usr/bin/env python3
from __future__ import annotations

import importlib.util, json, hashlib
from collections import defaultdict
from pathlib import Path
from zoneinfo import ZoneInfo

import icechunk
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
import xarray as xr

ROOT=Path(__file__).resolve().parents[1]
NAAMP=ROOT/"scripts"/"naamp"
EXP=ROOT/"exploration"
OUT=EXP/"NAAMP_BAROMETRIC_CUE_RECEIPT_V0_1.json"
Q=1.959963984540054

def loadmod(name,path):
    s=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(s)
    assert s.loader
    s.loader.exec_module(m)
    return m

hydric=loadmod("hydric",EXP/"run_naamp_hydric_cue_discrimination.py")
base=hydric.base
spatial=hydric.spatial
sameobs=hydric.sameobs

def extract(records):
    ids=sorted(records)
    storage=icechunk.s3_storage(
        bucket="earthmover-icechunk-era5",prefix="icechunkV2",region="us-east-1",anonymous=True
    )
    repo=icechunk.Repository.open(storage)
    session=repo.readonly_session("main")
    ds=xr.open_zarr(session.store,group="single/temporal",consolidated=False,chunks=None)
    tp_name=hydric.find_grib_var(ds,228,["total precipitation","precipitation"])
    msl_name=hydric.find_grib_var(ds,151,["mean sea level pressure","msl"])
    tp=ds[tp_name]; msl=ds[msl_name]
    if str(tp.attrs.get("units"))!="m" or "1 hour" not in str(tp.attrs.get("accumulation_comment","")):
        raise RuntimeError("tp semantics drift")
    if str(msl.attrs.get("GRIB_paramId",""))!="151" or str(msl.attrs.get("units",""))!="Pa":
        raise RuntimeError(f"msl semantics drift {msl.attrs}")

    out={}
    h=hashlib.sha256()
    batch_size=200
    for b0 in range(0,len(ids),batch_size):
        batch=ids[b0:b0+batch_size]
        n=len(batch)
        lat=np.asarray([records[r]["lat"] for r in batch],float)
        lon=np.asarray([records[r]["lon"]%360 for r in batch],float)
        ends=[]
        for r in batch:
            utc=records[r]["midpoint"].astimezone(ZoneInfo("UTC")).replace(tzinfo=None)
            ends.append(np.datetime64(pd.Timestamp(utc).floor("h").to_datetime64(),"ns"))
        ends=np.asarray(ends)

        offsets=np.arange(71,-1,-1,dtype="timedelta64[h]")
        times=ends[:,None]-offsets[None,:]
        sel_tp=tp.sel(
            latitude=xr.DataArray(np.repeat(lat,72),dims="point"),
            longitude=xr.DataArray(np.repeat(lon,72),dims="point"),
            valid_time=xr.DataArray(times.reshape(-1),dims="point"),
            method="nearest",
        )
        rv=np.asarray(sel_tp.values,float).reshape(n,72)
        if not np.isfinite(rv).all():
            raise RuntimeError("nonfinite tp")
        rv[rv<0]=0
        rain72=(rv*1000).sum(axis=1)

        def p_at(timearr):
            x=msl.sel(
                latitude=xr.DataArray(lat,dims="run"),
                longitude=xr.DataArray(lon,dims="run"),
                valid_time=xr.DataArray(timearr,dims="run"),
                method="nearest",
            )
            return np.asarray(x.values,float)/100.0

        p0=p_at(ends)
        p6=p_at(ends-np.timedelta64(6,"h"))
        p24=p_at(ends-np.timedelta64(24,"h"))
        if not np.isfinite(p0).all() or not np.isfinite(p6).all() or not np.isfinite(p24).all():
            raise RuntimeError("nonfinite msl")
        if min(p0.min(),p6.min(),p24.min())<850 or max(p0.max(),p6.max(),p24.max())>1100:
            raise RuntimeError("implausible msl hPa")

        drop6=p6-p0
        drop24=p24-p0
        for i,rid in enumerate(batch):
            out[rid]={
                "rain72_mm":float(rain72[i]),
                "msl_hpa":float(p0[i]),
                "pressure_drop6_hpa":float(drop6[i]),
                "pressure_drop24_hpa":float(drop24[i]),
            }
            h.update(f"{rid},{rain72[i]:.8f},{p0[i]:.4f},{drop6[i]:.4f},{drop24[i]:.4f}\n".encode())
        print(json.dumps({"runs_processed":min(b0+batch_size,len(ids)),"runs_total":len(ids)}),flush=True)

    return out,{
        "tp_variable":tp_name,"msl_variable":msl_name,
        "msl_units":"hPa_after_conversion",
        "weather_sha256":h.hexdigest(),
        "msl_range_hpa":[float(min(v["msl_hpa"] for v in out.values())),float(max(v["msl_hpa"] for v in out.values()))],
    }

def fit(df,response,pterm):
    form=f"{response} ~ rain_contrast + rain72_amount_difference_z + {pterm} + temp_difference + doy_difference + year_gap + C(State) + C(RunNumber)"
    m=smf.ols(form,data=df).fit(cov_type="cluster",cov_kwds={"groups":df.route_cluster})
    def term(name):
        b=float(m.params[name]); se=float(m.bse[name])
        return {"beta":b,"se":se,"ci95":[b-Q*se,b+Q*se],"p":float(m.pvalues[name]),"positive_ci":bool(b-Q*se>0)}
    return {
        "response":response,"formula":form,"n_pairs":int(len(df)),"n_routes":int(df.route_cluster.nunique()),
        "rain_contrast":term("rain_contrast"),
        "rain72_amount":term("rain72_amount_difference_z"),
        "pressure":term(pterm),
    }

def main():
    raw=hydric.retry(base.load,"NAAMP load")
    runs,sets=base.build_runs(raw)
    eligible=set(runs.RunID.astype(str))
    mid=hydric.build_midpoints(raw,runs)
    if len(mid)<7500:
        raise RuntimeError(f"midpoint coverage too low {len(mid)}")
    weather,audit=extract(mid)

    sampled,_=spatial.stop_matrix(raw,eligible)
    by=hydric.build_ci(raw,eligible,sampled)
    site=hydric.site_map(raw,eligible)
    pairs=base.pair_runs(runs,sets).copy().reset_index(drop=True)
    _,same=sameobs.same_observer_pairs(raw,runs,sets)
    same_keys={(str(p.wet_RunID),str(p.dry_RunID)) for p in same.itertuples(index=False)}

    rows=[]
    for p in pairs.itertuples(index=False):
        w=str(p.wet_RunID); d=str(p.dry_RunID)
        if w not in weather or d not in weather:
            continue
        score,count,ci3=hydric.metrics(p,sampled,by)
        r=p._asdict()
        r.update({
            "strong_new_score":score,
            "strong_new_count":count,
            "new_ci3_count":ci3,
            "rain72_log_difference":float(np.log1p(weather[w]["rain72_mm"])-np.log1p(weather[d]["rain72_mm"])),
            "pressure6_advantage":float(weather[w]["pressure_drop6_hpa"]-weather[d]["pressure_drop6_hpa"]),
            "pressure24_advantage":float(weather[w]["pressure_drop24_hpa"]-weather[d]["pressure_drop24_hpa"]),
            "same_observer_physical_stop":bool((w,d) in same_keys and hydric.stable_pair(p,sampled,site)),
        })
        rows.append(r)
    df=pd.DataFrame(rows)

    if len(df)<3500 or df.route_cluster.nunique()<500:
        out={"analysis":"naamp_barometric_cue_discrimination_v0_1","status":"not_run_due_to_prefixed_gate",
             "coverage":{"pairs":int(len(df)),"routes":int(df.route_cluster.nunique())},"weather_audit":audit}
        OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
        print(json.dumps(out,indent=2,sort_keys=True))
        return

    df["rain72_amount_difference_z"],mr,sr=hydric.zscore(df.rain72_log_difference)
    df["pressure6_advantage_z"],m6,s6=hydric.zscore(df.pressure6_advantage)
    df["pressure24_advantage_z"],m24,s24=hydric.zscore(df.pressure24_advantage)

    primary=fit(df,"strong_new_score","pressure6_advantage_z")
    p24=fit(df,"strong_new_score","pressure24_advantage_z")
    ci3=fit(df,"new_ci3_count","pressure6_advantage_z")
    robust=df[df.same_observer_physical_stop].copy()
    robust_fit=fit(robust,"strong_new_score","pressure6_advantage_z") if len(robust)>=2500 and robust.route_cluster.nunique()>=450 else None

    rain_support=bool(primary["rain72_amount"]["positive_ci"])
    p_support=bool(primary["pressure"]["positive_ci"])
    if rain_support and not p_support:
        cls="accumulated_hydric_over_barometric_cue"
    elif rain_support and p_support:
        cls="mixed_accumulated_hydric_and_barometric_cues"
    elif p_support and not rain_support:
        cls="barometric_over_accumulated_hydric"
    else:
        cls="neither_independently_supported"

    out={
      "analysis":"naamp_barometric_cue_discrimination_v0_1",
      "contract":"exploration/NAAMP_BAROMETRIC_CUE_CONTRACT_V0_1.json",
      "status":"completed_after_prefixed_gate",
      "coverage":{"pairs":int(len(df)),"routes":int(df.route_cluster.nunique()),"robust_pairs":int(len(robust)),"robust_routes":int(robust.route_cluster.nunique())},
      "weather_audit":audit,
      "standardization":{
        "rain72_mean":mr,"rain72_sd":sr,"pressure6_mean":m6,"pressure6_sd":s6,"pressure24_mean":m24,"pressure24_sd":s24,
        "rain72_pressure6_correlation":float(np.corrcoef(df.rain72_log_difference,df.pressure6_advantage)[0,1]),
        "rain72_pressure24_correlation":float(np.corrcoef(df.rain72_log_difference,df.pressure24_advantage)[0,1]),
      },
      "primary_pressure6":primary,
      "secondary_pressure24":p24,
      "secondary_full_chorus_ci3":ci3,
      "robust_same_observer_physical_stop":robust_fit,
      "classification":{"cue_result":cls,"rain72_supported_after_pressure6":rain_support,"pressure6_supported":p_support},
      "interpretation_boundary":{"pressure_is_storm_cue":True,"causal_mediation_established":False,"submission_story_change_authorized":False}
    }
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
