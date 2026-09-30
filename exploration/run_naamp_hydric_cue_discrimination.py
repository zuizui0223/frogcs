#!/usr/bin/env python3
from __future__ import annotations

import csv, hashlib, importlib.util, io, json, math, re, time, urllib.error, urllib.request
from collections import defaultdict
from datetime import date, datetime, time as dtime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import icechunk
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
import xarray as xr
from timezonefinder import TimezoneFinder

ROOT=Path(__file__).resolve().parents[1]
NAAMP=ROOT/"scripts"/"naamp"
OUT=ROOT/"exploration"/"NAAMP_HYDRIC_CUE_DISCRIMINATION_RECEIPT_V0_1.json"
COORD_URL="https://www.sciencebase.gov/catalog/file/get/583dc314e4b0d1899f9dea8d?f=__disk__77%2F22%2F7e%2F77227ec46ac1c01592cd7d158d442cd8343a7536"
COORD_SHA="f71a87df9fc94e0d6c5d4466b4745c3bbaff874cbe7c28796b3f9eb44c2e6e83"
Q=1.959963984540054

def loadmod(name,path):
    s=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(s)
    assert s.loader
    s.loader.exec_module(m)
    return m

base=loadmod("base",NAAMP/"run_naamp_ecological_pulse.py")
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

def fetch_bytes(url):
    req=urllib.request.Request(url,headers={"User-Agent":"frogcs-hydric-cue/0.1"})
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
    dates={str(rr.RunID):date(int(rr.SurveyYear),1,1)+timedelta(days=int(rr.doy)-1) for rr in runs.itertuples(index=False)}
    rec={}
    for rid in sorted(eligible):
        row=runraw.get(rid,{})
        st=parse_clock(row.get("StartTime")); et=parse_clock(row.get("EndTime"))
        if st is None or et is None or rid not in centers:
            continue
        a=datetime.combine(dates[rid],st)
        b=datetime.combine(dates[rid],et)
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

def find_grib_var(ds,param_id,labels):
    hits=[]
    for name,da in ds.data_vars.items():
        attrs=da.attrs
        pid=str(attrs.get("GRIB_paramId",""))
        short=str(attrs.get("GRIB_shortName","")).lower()
        longn=str(attrs.get("long_name","")).lower()
        stdn=str(attrs.get("standard_name","")).lower()
        if pid==str(param_id) or any(lbl in short or lbl in longn or lbl in stdn for lbl in labels):
            hits.append(name)
    exact=[n for n in hits if str(ds[n].attrs.get("GRIB_paramId",""))==str(param_id)]
    chosen=exact if exact else hits
    chosen=list(dict.fromkeys(chosen))
    if len(chosen)!=1:
        raise RuntimeError(f"GRIB variable identification failed paramId={param_id}: {chosen[:20]}")
    return chosen[0]

def es_kpa(temp_c):
    return 0.61094*np.exp(17.625*temp_c/(temp_c+243.04))

def extract_weather(records):
    ids=sorted(records)
    storage=icechunk.s3_storage(bucket="earthmover-icechunk-era5",prefix="icechunkV2",region="us-east-1",anonymous=True)
    repo=icechunk.Repository.open(storage)
    session=repo.readonly_session("main")
    ds=xr.open_zarr(session.store,group="single/temporal",consolidated=False,chunks=None)

    tp_name=find_grib_var(ds,228,["total precipitation","precipitation"])
    t_name=find_grib_var(ds,167,["2m temperature","2 metre temperature","2 meter temperature"])
    td_name=find_grib_var(ds,168,["2m dewpoint","2 metre dewpoint","dewpoint temperature","dew point temperature"])
    tp=ds[tp_name]; t2=ds[t_name]; td2=ds[td_name]

    if str(tp.attrs.get("units"))!="m":
        raise RuntimeError(f"ERA5 tp units drift: {tp.attrs.get('units')}")
    if "1 hour" not in str(tp.attrs.get("accumulation_comment","")):
        raise RuntimeError("ERA5 tp accumulation semantics drift")
    if str(t2.attrs.get("units")).lower() not in ("k","kelvin"):
        raise RuntimeError(f"ERA5 t2m units drift: {t2.attrs.get('units')}")
    if str(td2.attrs.get("units")).lower() not in ("k","kelvin"):
        raise RuntimeError(f"ERA5 d2m units drift: {td2.attrs.get('units')}")

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
            method="nearest"
        )
        vals=np.asarray(sel_tp.values,float).reshape(n,72)
        if not np.isfinite(vals).all():
            raise RuntimeError("nonfinite tp")
        if float(vals.min())<-1e-8:
            raise RuntimeError("negative tp beyond tolerance")
        vals[vals<0]=0
        rain72=(vals*1000).sum(axis=1)

        sel_t=t2.sel(
            latitude=xr.DataArray(lat,dims="run"),
            longitude=xr.DataArray(lon,dims="run"),
            valid_time=xr.DataArray(ends,dims="run"),
            method="nearest"
        )
        sel_td=td2.sel(
            latitude=xr.DataArray(lat,dims="run"),
            longitude=xr.DataArray(lon,dims="run"),
            valid_time=xr.DataArray(ends,dims="run"),
            method="nearest"
        )
        T=np.asarray(sel_t.values,float)-273.15
        Td=np.asarray(sel_td.values,float)-273.15
        if not np.isfinite(T).all() or not np.isfinite(Td).all():
            raise RuntimeError("nonfinite t2m/d2m")
        if np.max(Td-T)>1.5:
            raise RuntimeError(f"dewpoint exceeds T implausibly: {float(np.max(Td-T))}")
        ea=es_kpa(Td); es=es_kpa(T)
        vpd=np.maximum(es-ea,0.0)
        rh=100.0*ea/es
        if np.nanmin(rh)<-0.5 or np.nanmax(rh)>101.5:
            raise RuntimeError(f"RH implausible {float(np.nanmin(rh))} {float(np.nanmax(rh))}")
        rh=np.clip(rh,0,100)

        for i,rid in enumerate(batch):
            out[rid]={
                "rain72_mm":float(rain72[i]),
                "t2m_c":float(T[i]),
                "d2m_c":float(Td[i]),
                "vpd_kpa":float(vpd[i]),
                "rh_percent":float(rh[i]),
            }
            h.update(f"{rid},{rain72[i]:.8f},{T[i]:.5f},{Td[i]:.5f},{vpd[i]:.8f},{rh[i]:.5f}\n".encode())
        print(json.dumps({"weather_runs_processed":min(b0+batch_size,len(ids)),"weather_runs_total":len(ids)}),flush=True)

    audit={
        "tp_variable":tp_name,"tp_param_id":str(tp.attrs.get("GRIB_paramId")),
        "t2m_variable":t_name,"t2m_param_id":str(t2.attrs.get("GRIB_paramId")),
        "d2m_variable":td_name,"d2m_param_id":str(td2.attrs.get("GRIB_paramId")),
        "weather_sha256":h.hexdigest(),
    }
    return out,audit

def build_ci(raw,eligible,sampled):
    vals=defaultdict(list)
    for r in raw["Counts.csv"]:
        rid=(r.get("RunID") or "").strip(); st=(r.get("StopNumber") or "").strip(); sp=(r.get("Species") or "").strip()
        if rid not in eligible or st not in sampled.get(rid,set()) or not sp:
            continue
        try: ci=int(float((r.get("CallingIndex") or "").strip()))
        except Exception: continue
        if ci in (1,2,3): vals[(rid,st,sp)].append(ci)
    by=defaultdict(dict)
    for (rid,st,sp),v in vals.items(): by[(rid,st)][sp]=max(v)
    return by

def metrics(p,sampled,by):
    w=str(p.wet_RunID); d=str(p.dry_RunID)
    score=count=ci3=0.0
    for st in sorted(sampled[w]):
        wm=by.get((w,st),{}); dm=by.get((d,st),{})
        for sp in set(wm)|set(dm):
            wi=int(wm.get(sp,0)); di=int(dm.get(sp,0))
            if di==0 and wi>=2:
                score+=wi; count+=1
                ci3+=int(wi==3)
    return score,count,ci3

def site_map(raw,eligible):
    vals=defaultdict(set)
    for s in raw["Stops.csv"]:
        rid=(s.get("RunID") or "").strip(); st=(s.get("StopNumber") or "").strip(); sid=(s.get("SiteID") or "").strip()
        if rid in eligible and st and sid and (s.get("SkippedStop") or "").strip()=="0":
            vals[(rid,st)].add(sid)
    bad={k:v for k,v in vals.items() if len(v)>1}
    if bad: raise RuntimeError(f"site conflicts {list(bad)[:10]}")
    return {k:next(iter(v)) for k,v in vals.items()}

def stable_pair(p,sampled,site):
    w=str(p.wet_RunID); d=str(p.dry_RunID); ws=set(sampled[w]); ds=set(sampled[d])
    return len(ws)==10 and ws==ds and all(site.get((w,st)) is not None and site.get((w,st))==site.get((d,st)) for st in ws)

def zscore(x):
    a=np.asarray(x,float); mu=float(a.mean()); sd=float(a.std(ddof=0))
    if not np.isfinite(sd) or sd<=0: raise RuntimeError("invalid zscore")
    return (a-mu)/sd,mu,sd

def fit(df,response,moisture):
    formula=f"{response} ~ rain_contrast + rain72_amount_difference_z + {moisture} + temp_difference + doy_difference + year_gap + C(State) + C(RunNumber)"
    m=smf.ols(formula,data=df).fit(cov_type="cluster",cov_kwds={"groups":df.route_cluster})
    def term(name):
        b=float(m.params[name]); se=float(m.bse[name])
        return {"beta":b,"se":se,"ci95":[b-Q*se,b+Q*se],"p":float(m.pvalues[name]),"positive_ci":bool(b-Q*se>0)}
    return {
        "formula":formula,"response":response,
        "n_pairs":int(len(df)),"n_routes":int(df.route_cluster.nunique()),
        "rain_contrast":term("rain_contrast"),
        "rain72_amount":term("rain72_amount_difference_z"),
        "moisture":term(moisture),
    }

def main():
    raw=retry(base.load,"NAAMP load")
    runs,sets=base.build_runs(raw)
    eligible=set(runs.RunID.astype(str))
    mid=build_midpoints(raw,runs)
    if len(mid)<7500: raise RuntimeError(f"midpoint coverage too low {len(mid)}")
    weather,audit=extract_weather(mid)

    sampled,_=spatial.stop_matrix(raw,eligible)
    by=build_ci(raw,eligible,sampled)
    site=site_map(raw,eligible)
    pairs=base.pair_runs(runs,sets).copy().reset_index(drop=True)
    _,same=sameobs.same_observer_pairs(raw,runs,sets)
    same_keys={(str(p.wet_RunID),str(p.dry_RunID)) for p in same.itertuples(index=False)}

    rows=[]
    for p in pairs.itertuples(index=False):
        w=str(p.wet_RunID); d=str(p.dry_RunID)
        if w not in weather or d not in weather: continue
        score,count,ci3=metrics(p,sampled,by)
        r=p._asdict()
        r.update({
            "strong_new_score":score,"strong_new_count":count,"new_ci3_count":ci3,
            "rain72_log_difference":float(np.log1p(weather[w]["rain72_mm"])-np.log1p(weather[d]["rain72_mm"])),
            "vpd_relief_difference":float(weather[d]["vpd_kpa"]-weather[w]["vpd_kpa"]),
            "rh_gain_difference":float(weather[w]["rh_percent"]-weather[d]["rh_percent"]),
            "same_observer_physical_stop":bool((w,d) in same_keys and stable_pair(p,sampled,site)),
        })
        rows.append(r)
    df=pd.DataFrame(rows)
    if len(df)<3500 or df.route_cluster.nunique()<500:
        out={"analysis":"naamp_hydric_cue_discrimination_v0_1","status":"not_run_due_to_prefixed_gate",
             "coverage":{"pairs":int(len(df)),"routes":int(df.route_cluster.nunique())},"weather_audit":audit}
        OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n"); print(json.dumps(out,indent=2,sort_keys=True)); return

    df["rain72_amount_difference_z"],m72,s72=zscore(df.rain72_log_difference)
    df["vpd_relief_difference_z"],mv,sv=zscore(df.vpd_relief_difference)
    df["rh_gain_difference_z"],mr,sr=zscore(df.rh_gain_difference)

    primary=fit(df,"strong_new_score","vpd_relief_difference_z")
    rh=fit(df,"strong_new_score","rh_gain_difference_z")
    ci3=fit(df,"new_ci3_count","vpd_relief_difference_z")
    robust=df[df.same_observer_physical_stop].copy()
    robust_fit=fit(robust,"strong_new_score","vpd_relief_difference_z") if len(robust)>=2500 and robust.route_cluster.nunique()>=450 else None

    amount_support=bool(primary["rain72_amount"]["positive_ci"])
    vpd_support=bool(primary["moisture"]["positive_ci"])
    if amount_support and not vpd_support: cls="accumulated_hydric_over_instantaneous_vpd"
    elif amount_support and vpd_support: cls="mixed_accumulated_and_instantaneous_hydric_cues"
    elif vpd_support and not amount_support: cls="instantaneous_vpd_over_accumulated_rain"
    else: cls="neither_hydric_proxy_independently_supported"

    out={
      "analysis":"naamp_hydric_cue_discrimination_v0_1",
      "contract":"exploration/NAAMP_HYDRIC_CUE_DISCRIMINATION_CONTRACT_V0_1.json",
      "status":"completed_after_prefixed_gate",
      "coverage":{"pairs":int(len(df)),"routes":int(df.route_cluster.nunique()),"robust_pairs":int(len(robust)),"robust_routes":int(robust.route_cluster.nunique())},
      "weather_audit":audit,
      "standardization":{"rain72_mean":m72,"rain72_sd":s72,"vpd_relief_mean":mv,"vpd_relief_sd":sv,"rh_gain_mean":mr,"rh_gain_sd":sr,
                         "rain72_vpd_relief_correlation":float(np.corrcoef(df.rain72_log_difference,df.vpd_relief_difference)[0,1])},
      "primary_strong_score_vpd":primary,
      "secondary_rh":rh,
      "secondary_full_chorus_ci3":ci3,
      "robust_same_observer_physical_stop":robust_fit,
      "classification":{"hydric_cue_result":cls,"rain72_supported_after_vpd":amount_support,"vpd_relief_supported":vpd_support},
      "interpretation_boundary":{"vpd_is_direct_hydration":False,"rain72_is_direct_water_level":False,"causal_mediation_established":False}
    }
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
