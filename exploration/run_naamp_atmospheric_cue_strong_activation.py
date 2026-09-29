#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import importlib.util
import json
import math
import time
import urllib.error
from collections import defaultdict
from datetime import date, timedelta
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
OUT=EXP/"NAAMP_ATMOSPHERIC_CUE_STRONG_ACTIVATION_RECEIPT_V0_1.json"
Q=1.959963984540054

def loadmod(name,path):
    s=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(s)
    assert s.loader
    s.loader.exec_module(m)
    return m

audit=loadmod("atm_audit",EXP/"audit_naamp_atmospheric_cue_eligibility.py")
base=audit.base
spatial=loadmod("spatial",NAAMP/"run_naamp_spatial_taxonomic_activation_decomposition.py")
sameobs=loadmod("sameobs",NAAMP/"run_naamp_same_observer_robustness.py")

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

def build_midpoints(raw,runs):
    eligible=set(runs["RunID"].astype(str))
    cmap=retry(audit.coords,"Coordinates load")
    cent=audit.route_midpoints(raw,eligible,cmap)
    tf=audit.TimezoneFinder(in_memory=True)
    run_raw={str(r.get("RunID") or "").strip():r for r in raw["Runs.csv"]}
    date_by={
        str(rr.RunID): date(int(rr.SurveyYear),1,1)+timedelta(days=int(rr.doy)-1)
        for rr in runs.itertuples(index=False)
    }
    rec={}
    for rid in sorted(eligible):
        row=run_raw.get(rid,{})
        st,_=audit.parse_clock(row.get("StartTime"))
        et,_=audit.parse_clock(row.get("EndTime"))
        if st is None or et is None or rid not in cent:
            continue
        lat,lon,n=cent[rid]
        tz=tf.timezone_at(lat=lat,lng=lon)
        if not tz:
            continue
        mid,dur=audit.localize_midpoint(date_by[rid],st,et,tz)
        if mid is None:
            continue
        rec[rid]={
            "lat":float(lat),"lon":float(lon),"timezone":str(tz),
            "midpoint":mid,"duration_h":float(dur),"n_coords":int(n)
        }
    return rec

def build_calling_index(raw,eligible,sampled):
    vals=defaultdict(list)
    for r in raw["Counts.csv"]:
        rid=(r.get("RunID") or "").strip()
        st=(r.get("StopNumber") or "").strip()
        sp=(r.get("Species") or "").strip()
        if rid not in eligible or st not in sampled.get(rid,set()) or not sp:
            continue
        try:
            ci=int(float((r.get("CallingIndex") or "").strip()))
        except Exception:
            continue
        if ci in (1,2,3):
            vals[(rid,st,sp)].append(ci)
    by=defaultdict(dict)
    for (rid,st,sp),v in vals.items():
        by[(rid,st)][sp]=max(v)
    return by

def strong_metrics(pair,sampled,by):
    wet=str(pair.wet_RunID); dry=str(pair.dry_RunID)
    stops=sorted(sampled[wet])
    if len(stops)!=10 or set(stops)!=set(sampled[dry]):
        raise RuntimeError("stop alignment drift")
    score=0.0; count=0.0
    for st in stops:
        wm=by.get((wet,st),{}); dm=by.get((dry,st),{})
        for sp in set(wm)|set(dm):
            w=int(wm.get(sp,0)); d=int(dm.get(sp,0))
            if d==0 and w>=2:
                score+=w
                count+=1
    return score,count

def era5_at_midpoints(records):
    ids=sorted(records)
    lat=np.asarray([records[x]["lat"] for x in ids],float)
    lon=np.asarray([records[x]["lon"]%360.0 for x in ids],float)
    utc=np.asarray([
        np.datetime64(records[x]["midpoint"].astimezone(ZoneInfo("UTC")).replace(tzinfo=None),"ns")
        for x in ids
    ])

    storage=icechunk.s3_storage(
        bucket="earthmover-icechunk-era5",prefix="icechunkV2",
        region="us-east-1",anonymous=True,
    )
    repo=icechunk.Repository.open(storage)
    session=repo.readonly_session("main")
    ds=xr.open_zarr(session.store,group="single/temporal",consolidated=False,chunks=None)
    for v,pid,unit in (("t2m",167,"K"),("d2m",168,"K"),("sp",134,"Pa")):
        if v not in ds:
            raise RuntimeError(f"missing ERA5 variable {v}")
        if ds[v].attrs.get("GRIB_paramId") not in (pid,str(pid)):
            raise RuntimeError(f"{v} parameter identity drift")
        if str(ds[v].attrs.get("units"))!=unit:
            raise RuntimeError(f"{v} unit drift")

    lat_da=xr.DataArray(lat,dims="point")
    lon_da=xr.DataArray(lon,dims="point")
    time_da=xr.DataArray(utc,dims="point")
    sel=ds[["t2m","d2m","sp"]].sel(
        latitude=lat_da,longitude=lon_da,valid_time=time_da,method="nearest"
    )
    t=np.asarray(sel["t2m"].values,float).reshape(-1)
    td=np.asarray(sel["d2m"].values,float).reshape(-1)
    sp=np.asarray(sel["sp"].values,float).reshape(-1)
    slat=np.asarray(sel["latitude"].values,float).reshape(-1)
    slon=np.asarray(sel["longitude"].values,float).reshape(-1)
    stime=np.asarray(sel["valid_time"].values).reshape(-1)
    if not (np.isfinite(t).all() and np.isfinite(td).all() and np.isfinite(sp).all()):
        raise RuntimeError("nonfinite atmospheric values")
    if np.max(np.abs(slat-lat))>0.126:
        raise RuntimeError("ERA5 latitude nearest-cell mismatch")
    lon_delta=np.minimum(np.abs(slon-lon),360-np.abs(slon-lon))
    if np.max(lon_delta)>0.126:
        raise RuntimeError("ERA5 longitude nearest-cell mismatch")
    dt_hours=np.abs((stime.astype("datetime64[s]")-utc.astype("datetime64[s]")).astype("timedelta64[s]").astype(float))/3600.0
    if np.max(dt_hours)>0.51:
        raise RuntimeError(f"ERA5 time mismatch max={np.max(dt_hours)} h")

    tc=t-273.15
    tdc=td-273.15
    rh=100.0*np.exp((17.625*tdc)/(243.04+tdc)-(17.625*tc)/(243.04+tc))
    if np.min(rh)<-0.1 or np.max(rh)>100.1:
        raise RuntimeError(f"RH outside numerical tolerance: {np.min(rh)}, {np.max(rh)}")
    rh=np.clip(rh,0,100)

    h=hashlib.sha256()
    out={}
    for i,rid in enumerate(ids):
        h.update(f"{rid},{slat[i]:.4f},{slon[i]:.4f},{str(stime[i])},{t[i]:.6f},{td[i]:.6f},{sp[i]:.3f},{rh[i]:.6f}\n".encode())
        out[rid]={
            "t2m_k":float(t[i]),"d2m_k":float(td[i]),"sp_pa":float(sp[i]),
            "rh_pct":float(rh[i]),"era5_lat":float(slat[i]),
            "era5_lon":float(((slon[i]+180)%360)-180),
            "era5_time":str(stime[i]),"time_offset_h":float(dt_hours[i]),
        }
    return out,h.hexdigest(),{
        "runs":len(ids),
        "unique_cells":len({(round(x["era5_lat"],3),round(x["era5_lon"],3)) for x in out.values()}),
        "max_time_offset_h":float(np.max(dt_hours)),
        "rh_min":float(np.min(rh)),"rh_max":float(np.max(rh)),
        "sp_min_pa":float(np.min(sp)),"sp_max_pa":float(np.max(sp)),
    }

def zscore(x):
    a=np.asarray(x,float)
    mu=float(np.mean(a)); sd=float(np.std(a,ddof=0))
    if not np.isfinite(sd) or sd<=0:
        raise RuntimeError("invalid standardization")
    return (a-mu)/sd,mu,sd

def fit(df,response,weather=("rh_difference_z","pressure_difference_z")):
    weather=list(weather)
    rhs=["rain_contrast","temp_difference","doy_difference","year_gap"]+weather+["C(State)","C(RunNumber)"]
    formula=f"{response} ~ "+" + ".join(rhs)
    m=smf.ols(formula,data=df).fit(
        cov_type="cluster",cov_kwds={"groups":df["route_cluster"]}
    )
    def term(name):
        b=float(m.params[name]); se=float(m.bse[name])
        return {"beta":b,"se":se,"ci95":[b-Q*se,b+Q*se],"p":float(m.pvalues[name])}
    report={
        "response":response,"formula":formula,
        "n_pairs":int(len(df)),"n_routes":int(df.route_cluster.nunique()),
        "rain_contrast":term("rain_contrast"),
    }
    if "rh_difference_z" in weather:
        report["rh_difference_z"]=term("rh_difference_z")
    if "pressure_difference_z" in weather:
        report["pressure_difference_z"]=term("pressure_difference_z")
    if len(weather)==2:
        names=list(m.params.index)
        R=np.zeros((2,len(names)),float)
        R[0,names.index("rh_difference_z")]=1.0
        R[1,names.index("pressure_difference_z")]=1.0
        wt=m.wald_test(R,scalar=True)
        report["atmospheric_joint_wald"]={
            "statistic":float(np.asarray(wt.statistic).reshape(-1)[0]),
            "df":2,
            "p":float(np.asarray(wt.pvalue).reshape(-1)[0]),
        }
    return report

def main():
    raw=retry(base.load,"NAAMP load")
    runs,sets=base.build_runs(raw)
    eligible=set(runs["RunID"].astype(str))
    mid=build_midpoints(raw,runs)
    if len(mid)<7500:
        raise RuntimeError(f"midpoint coverage drift {len(mid)}")
    weather,weather_sha,weather_audit=era5_at_midpoints(mid)

    sampled,_=spatial.stop_matrix(raw,eligible)
    by=build_calling_index(raw,eligible,sampled)
    pairs=base.pair_runs(runs,sets).copy().reset_index(drop=True)

    rows=[]
    for p in pairs.itertuples(index=False):
        w=str(p.wet_RunID); d=str(p.dry_RunID)
        if w not in weather or d not in weather:
            continue
        score,count=strong_metrics(p,sampled,by)
        row=p._asdict()
        row.update({
            "strong_new_score":score,"strong_new_count":count,
            "rh_difference":weather[w]["rh_pct"]-weather[d]["rh_pct"],
            "pressure_difference":weather[w]["sp_pa"]-weather[d]["sp_pa"],
        })
        rows.append(row)
    df=pd.DataFrame(rows)
    if len(df)!=4108:
        raise RuntimeError(f"eligible pair drift {len(df)} != 4108")
    df["rh_difference_z"],rh_mu,rh_sd=zscore(df["rh_difference"])
    df["pressure_difference_z"],sp_mu,sp_sd=zscore(df["pressure_difference"])

    primary=fit(df,"strong_new_score")
    count=fit(df,"strong_new_count")
    humidity_only=fit(df,"strong_new_score",("rh_difference_z",))
    pressure_only=fit(df,"strong_new_score",("pressure_difference_z",))
    exact=fit(df[df["year_gap"]==1].copy(),"strong_new_score")

    allpairs,same= sameobs.same_observer_pairs(raw,runs,sets)
    same_ids={(str(p.wet_RunID),str(p.dry_RunID)) for p in same.itertuples(index=False)}
    dsame=df[[ (str(r.wet_RunID),str(r.dry_RunID)) in same_ids for r in df.itertuples(index=False) ]].copy()
    same_report=fit(dsame,"strong_new_score")

    rain=primary["rain_contrast"]
    rh=primary["rh_difference_z"]
    joint=primary["atmospheric_joint_wald"]
    out={
        "analysis":"naamp_atmospheric_cue_strong_activation_v0_1",
        "contract":"exploration/NAAMP_ATMOSPHERIC_CUE_STRONG_ACTIVATION_CONTRACT_V0_1.json",
        "coverage":{
            "eligible_pairs":int(len(df)),"routes":int(df.route_cluster.nunique()),
            "same_observer_pairs":int(len(dsame)),
        },
        "era5":{
            "required_hourly_weather_sha256":weather_sha,
            **weather_audit
        },
        "standardization":{
            "rh_difference_mean":rh_mu,"rh_difference_sd":rh_sd,
            "pressure_difference_mean_pa":sp_mu,"pressure_difference_sd_pa":sp_sd,
        },
        "primary_strong_new_score":primary,
        "secondary_strong_new_count":count,
        "diagnostic_humidity_only":humidity_only,
        "diagnostic_pressure_only":pressure_only,
        "diagnostic_exact_consecutive_year":exact,
        "diagnostic_same_observer":same_report,
        "classification":{
            "rainfall_robustness":bool(rain["beta"]>0 and rain["ci95"][0]>0),
            "humidity_support":bool(rh["beta"]>0 and rh["ci95"][0]>0),
            "atmospheric_joint_information":bool(joint["p"]<0.05),
        },
        "interpretation_boundary":{
            "causal_mediation":False,
            "hourly_era5_is_on_site_measurement":False,
            "submission_story_change_authorized":False,
        }
    }
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
