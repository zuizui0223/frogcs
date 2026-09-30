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
OUT=EXP/"NAAMP_SOIL_MOISTURE_CUE_RECEIPT_V0_1.json"
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
        bucket="earthmover-icechunk-era5",
        prefix="icechunkV2",
        region="us-east-1",
        anonymous=True,
    )
    repo=icechunk.Repository.open(storage)
    session=repo.readonly_session("main")
    ds=xr.open_zarr(session.store,group="single/temporal",consolidated=False,chunks=None)

    tp_name=hydric.find_grib_var(ds,228,["total precipitation","precipitation"])
    s1_name=hydric.find_grib_var(ds,39,["volumetric soil water layer 1","swvl1"])
    s2_name=hydric.find_grib_var(ds,40,["volumetric soil water layer 2","swvl2"])
    tp=ds[tp_name]; s1=ds[s1_name]; s2=ds[s2_name]

    if str(tp.attrs.get("units"))!="m":
        raise RuntimeError(f"tp units drift {tp.attrs.get('units')}")
    if "1 hour" not in str(tp.attrs.get("accumulation_comment","")):
        raise RuntimeError("tp accumulation semantics drift")
    for name,da,pid in [(s1_name,s1,39),(s2_name,s2,40)]:
        if str(da.attrs.get("GRIB_paramId",""))!=str(pid):
            raise RuntimeError(f"{name} paramId drift")
        if "m**3" not in str(da.attrs.get("units","")):
            raise RuntimeError(f"{name} units drift {da.attrs.get('units')}")

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
        flat_lat=np.repeat(lat,72)
        flat_lon=np.repeat(lon,72)
        flat_time=times.reshape(-1)

        sel_tp=tp.sel(
            latitude=xr.DataArray(flat_lat,dims="point"),
            longitude=xr.DataArray(flat_lon,dims="point"),
            valid_time=xr.DataArray(flat_time,dims="point"),
            method="nearest",
        )
        rain=np.asarray(sel_tp.values,float).reshape(n,72)
        if not np.isfinite(rain).all():
            raise RuntimeError("nonfinite tp")
        rain[rain<0]=0
        rain72=(rain*1000).sum(axis=1)

        def sel_soil(da):
            x=da.sel(
                latitude=xr.DataArray(lat,dims="run"),
                longitude=xr.DataArray(lon,dims="run"),
                valid_time=xr.DataArray(ends,dims="run"),
                method="nearest",
            )
            return np.asarray(x.values,float)

        v1=sel_soil(s1); v2=sel_soil(s2)
        if not np.isfinite(v1).all() or not np.isfinite(v2).all():
            raise RuntimeError("nonfinite soil moisture")
        if float(v1.min())<-0.02 or float(v1.max())>0.8 or float(v2.min())<-0.02 or float(v2.max())>0.8:
            raise RuntimeError(f"soil moisture range implausible: swvl1 {v1.min()}..{v1.max()} swvl2 {v2.min()}..{v2.max()}")

        for i,rid in enumerate(batch):
            out[rid]={"rain72_mm":float(rain72[i]),"swvl1":float(v1[i]),"swvl2":float(v2[i])}
            h.update(f"{rid},{rain72[i]:.8f},{v1[i]:.8f},{v2[i]:.8f}\n".encode())
        print(json.dumps({"runs_processed":min(b0+batch_size,len(ids)),"runs_total":len(ids)}),flush=True)

    return out,{
        "tp_variable":tp_name,
        "swvl1_variable":s1_name,
        "swvl2_variable":s2_name,
        "swvl1_units":str(s1.attrs.get("units")),
        "swvl2_units":str(s2.attrs.get("units")),
        "weather_sha256":h.hexdigest(),
        "swvl1_range":[float(min(v["swvl1"] for v in out.values())),float(max(v["swvl1"] for v in out.values()))],
        "swvl2_range":[float(min(v["swvl2"] for v in out.values())),float(max(v["swvl2"] for v in out.values()))],
    }

def fit(df,response,soil):
    form=f"{response} ~ rain_contrast + rain72_amount_difference_z + {soil} + temp_difference + doy_difference + year_gap + C(State) + C(RunNumber)"
    m=smf.ols(form,data=df).fit(cov_type="cluster",cov_kwds={"groups":df.route_cluster})
    def term(name):
        b=float(m.params[name]); se=float(m.bse[name])
        return {"beta":b,"se":se,"ci95":[b-Q*se,b+Q*se],"p":float(m.pvalues[name]),"positive_ci":bool(b-Q*se>0)}
    return {
        "response":response,"formula":form,"n_pairs":int(len(df)),"n_routes":int(df.route_cluster.nunique()),
        "rain_contrast":term("rain_contrast"),
        "rain72_amount":term("rain72_amount_difference_z"),
        "soil_moisture":term(soil),
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
            "soil1_gain_difference":float(weather[w]["swvl1"]-weather[d]["swvl1"]),
            "soil2_gain_difference":float(weather[w]["swvl2"]-weather[d]["swvl2"]),
            "same_observer_physical_stop":bool((w,d) in same_keys and hydric.stable_pair(p,sampled,site)),
        })
        rows.append(r)
    df=pd.DataFrame(rows)

    if len(df)<3500 or df.route_cluster.nunique()<500:
        out={"analysis":"naamp_soil_moisture_cue_discrimination_v0_1","status":"not_run_due_to_prefixed_gate",
             "coverage":{"pairs":int(len(df)),"routes":int(df.route_cluster.nunique())},"weather_audit":audit}
        OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
        print(json.dumps(out,indent=2,sort_keys=True))
        return

    df["rain72_amount_difference_z"],m72,s72=hydric.zscore(df.rain72_log_difference)
    df["soil1_gain_difference_z"],m1,s1=hydric.zscore(df.soil1_gain_difference)
    df["soil2_gain_difference_z"],m2,s2=hydric.zscore(df.soil2_gain_difference)

    primary=fit(df,"strong_new_score","soil1_gain_difference_z")
    soil2=fit(df,"strong_new_score","soil2_gain_difference_z")
    ci3=fit(df,"new_ci3_count","soil1_gain_difference_z")

    robust=df[df.same_observer_physical_stop].copy()
    robust_fit=fit(robust,"strong_new_score","soil1_gain_difference_z") if len(robust)>=2500 and robust.route_cluster.nunique()>=450 else None

    rain_support=bool(primary["rain72_amount"]["positive_ci"])
    soil_support=bool(primary["soil_moisture"]["positive_ci"])
    if soil_support and not rain_support:
        cls="shallow_soil_moisture_over_antecedent_rain"
    elif rain_support and not soil_support:
        cls="antecedent_rain_beyond_shallow_soil_moisture"
    elif rain_support and soil_support:
        cls="mixed_antecedent_rain_and_shallow_soil_moisture"
    else:
        cls="neither_independently_supported"

    out={
      "analysis":"naamp_soil_moisture_cue_discrimination_v0_1",
      "contract":"exploration/NAAMP_SOIL_MOISTURE_CUE_CONTRACT_V0_1.json",
      "status":"completed_after_prefixed_gate",
      "coverage":{"pairs":int(len(df)),"routes":int(df.route_cluster.nunique()),"robust_pairs":int(len(robust)),"robust_routes":int(robust.route_cluster.nunique())},
      "weather_audit":audit,
      "standardization":{
        "rain72_mean":m72,"rain72_sd":s72,
        "soil1_gain_mean":m1,"soil1_gain_sd":s1,
        "soil2_gain_mean":m2,"soil2_gain_sd":s2,
        "rain72_soil1_correlation":float(np.corrcoef(df.rain72_log_difference,df.soil1_gain_difference)[0,1]),
        "rain72_soil2_correlation":float(np.corrcoef(df.rain72_log_difference,df.soil2_gain_difference)[0,1]),
        "soil1_soil2_correlation":float(np.corrcoef(df.soil1_gain_difference,df.soil2_gain_difference)[0,1]),
      },
      "primary_swvl1":primary,
      "secondary_swvl2":soil2,
      "secondary_full_chorus_ci3":ci3,
      "robust_same_observer_physical_stop":robust_fit,
      "classification":{"cue_result":cls,"rain72_supported_after_swvl1":rain_support,"swvl1_supported":soil_support},
      "interpretation_boundary":{
        "soil_water_is_body_hydration":False,
        "soil_water_is_pond_depth":False,
        "causal_mediation_established":False,
        "submission_story_change_authorized":False
      }
    }
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
