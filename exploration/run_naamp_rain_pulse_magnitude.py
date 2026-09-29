#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import importlib.util
import io
import json
import math
import time
import urllib.parse
import urllib.request
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date, datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

ROOT=Path(__file__).resolve().parents[1]
NAAMP=ROOT/"scripts"/"naamp"
OUT=ROOT/"exploration"/"NAAMP_RAIN_PULSE_MAGNITUDE_RECEIPT_V0_1.json"
Q=1.959963984540054
COORD_URL="https://www.sciencebase.gov/catalog/file/get/583dc314e4b0d1899f9dea8d?f=__disk__77%2F22%2F7e%2F77227ec46ac1c01592cd7d158d442cd8343a7536"
COORD_SHA="f71a87df9fc94e0d6c5d4466b4745c3bbaff874cbe7c28796b3f9eb44c2e6e83"
API="https://archive-api.open-meteo.com/v1/archive"
WET_MM=1.0
DRY_CAP=30
BATCH=12


def loadmod(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    mod=importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(mod)
    return mod


base=loadmod("pulse_base",NAAMP/"run_naamp_ecological_pulse.py")
spatial=loadmod("spatial_base",NAAMP/"run_naamp_spatial_taxonomic_activation_decomposition.py")


def fetch(url,timeout=180,retries=6):
    last=None
    for i in range(retries):
        try:
            req=urllib.request.Request(url,headers={
                "User-Agent":"frogcs-rain-pulse-magnitude/0.1",
                "Accept":"application/json,*/*",
            })
            with urllib.request.urlopen(req,timeout=timeout) as r:
                return r.read()
        except Exception as e:
            last=e
            time.sleep(min(20,1.5*(i+1)**2))
    raise RuntimeError(f"fetch failed after retries: {last}")


def parse_date(x):
    s=str(x or "").strip()
    for fmt in ("%m/%d/%Y","%m/%d/%y","%Y-%m-%d","%Y/%m/%d"):
        try:
            return datetime.strptime(s,fmt).date()
        except Exception:
            pass
    raise ValueError(f"unparseable date {x!r}")


def load_coordinates():
    raw=fetch(COORD_URL)
    got=hashlib.sha256(raw).hexdigest()
    if got!=COORD_SHA:
        raise RuntimeError(f"Coordinates.csv hash drift: {got}")
    rows=list(csv.DictReader(io.StringIO(raw.decode("utf-8-sig"))))
    coords={}
    for r in rows:
        sid=(r.get("SiteID") or "").strip()
        if not sid:
            continue
        lat=float(r["lat"]); lon=float(r["lon"])
        if not (-90<=lat<=90 and -180<=lon<=180):
            continue
        if sid in coords and coords[sid]!=(lat,lon):
            raise RuntimeError(f"coordinate conflict {sid}")
        coords[sid]=(lat,lon)
    return coords,got,len(rows)


def physical_site_map(raw,eligible):
    vals=defaultdict(set)
    sampled=defaultdict(set)
    for s in raw["Stops.csv"]:
        rid=(s.get("RunID") or "").strip()
        if rid not in eligible or (s.get("SkippedStop") or "").strip()!="0":
            continue
        st=(s.get("StopNumber") or "").strip()
        sid=(s.get("SiteID") or "").strip()
        if not st:
            continue
        sampled[rid].add(st)
        if sid:
            vals[(rid,st)].add(sid)
    conflict={k:v for k,v in vals.items() if len(v)>1}
    if conflict:
        raise RuntimeError(f"multiple SiteID per run-stop: {list(conflict)[:10]}")
    site={k:next(iter(v)) for k,v in vals.items() if v}
    return sampled,site


def stable_pair(p,sampled,site):
    wet=str(p.wet_RunID); dry=str(p.dry_RunID)
    ws=set(sampled[wet]); ds=set(sampled[dry])
    if len(ws)!=10 or ws!=ds:
        return False
    for st in sorted(ws):
        a=site.get((wet,st)); b=site.get((dry,st))
        if a is None or b is None or a!=b:
            return False
    return True


def run_centroid(rid,sampled,site,coords):
    ids=[site.get((rid,st)) for st in sorted(sampled[rid])]
    if len(ids)!=10 or any(x is None or x not in coords for x in ids):
        return None
    pts=np.asarray([coords[x] for x in ids],float)
    return float(pts[:,0].mean()),float(pts[:,1].mean())


def run_metadata(raw):
    out={}
    for r in raw["Runs.csv"]:
        rid=(r.get("RunID") or "").strip()
        if not rid:
            continue
        try:
            d=parse_date(r.get("SurveyDate"))
            rain=float((r.get("DaysSinceRain") or "").strip())
        except Exception:
            continue
        out[rid]={"survey_date":d,"days_since_rain":rain}
    return out


def open_meteo_batch(year,items):
    # items: list[(coord_key, lat, lon)]
    start=date(year,1,1)-timedelta(days=DRY_CAP+2)
    end=date(year,12,31)
    lats=",".join(f"{x[1]:.6f}" for x in items)
    lons=",".join(f"{x[2]:.6f}" for x in items)
    params={
        "latitude":lats,
        "longitude":lons,
        "start_date":start.isoformat(),
        "end_date":end.isoformat(),
        "daily":"precipitation_sum",
        "precipitation_unit":"mm",
        "timezone":"auto",
        "models":"era5",
        "cell_selection":"nearest",
    }
    url=API+"?"+urllib.parse.urlencode(params)
    raw=fetch(url,timeout=180)
    obj=json.loads(raw.decode("utf-8"))
    if isinstance(obj,dict) and obj.get("error"):
        raise RuntimeError(f"Open-Meteo error: {obj}")
    arr=obj if isinstance(obj,list) else [obj]
    if len(arr)!=len(items):
        raise RuntimeError(f"Open-Meteo response count {len(arr)} != request {len(items)}")
    out={}
    normalized=hashlib.sha256()
    for requested,res in zip(items,arr):
        key,lat,lon=requested
        rlat=float(res["latitude"]); rlon=float(res["longitude"])
        if abs(rlat-lat)>0.20 or abs(rlon-lon)>0.20:
            raise RuntimeError(f"returned ERA5 cell too far: req={(lat,lon)} got={(rlat,rlon)}")
        daily=res.get("daily") or {}
        times=daily.get("time") or []
        vals=daily.get("precipitation_sum") or []
        if len(times)!=len(vals) or not times:
            raise RuntimeError(f"missing daily precipitation for {key}")
        series={}
        for ds,v in zip(times,vals):
            if v is None or not np.isfinite(float(v)) or float(v)<0:
                raise RuntimeError(f"invalid precipitation {key} {ds} {v}")
            dd=date.fromisoformat(str(ds))
            series[dd]=float(v)
            normalized.update(f"{key}|{dd.isoformat()}|{float(v):.6f}\n".encode())
        out[key]={
            "requested":[lat,lon],
            "returned":[rlat,rlon],
            "timezone":res.get("timezone"),
            "utc_offset_seconds":res.get("utc_offset_seconds"),
            "series":series,
            "hash":normalized.hexdigest(),
        }
    return out,hashlib.sha256(raw).hexdigest()


def retrieve_weather(run_need):
    # run_need rid -> {coord,event_day}; group unique coordinate-year series
    groups=defaultdict(dict)
    for rec in run_need.values():
        lat,lon=rec["coord"]
        key=f"{lat:.6f},{lon:.6f},{rec['event_day'].year}"
        groups[rec["event_day"].year][key]=(key,lat,lon)

    tasks=[]
    for year,mp in sorted(groups.items()):
        vals=list(mp.values())
        for i in range(0,len(vals),BATCH):
            tasks.append((year,vals[i:i+BATCH]))

    weather={}
    raw_hashes=[]
    failures=[]
    with ThreadPoolExecutor(max_workers=4) as ex:
        futs={ex.submit(open_meteo_batch,y,it):(y,it) for y,it in tasks}
        done=0
        for fut in as_completed(futs):
            y,it=futs[fut]
            try:
                res,h=fut.result()
                weather.update(res); raw_hashes.append(h)
            except Exception as e:
                failures.append({"year":y,"n":len(it),"error":str(e)[:500]})
            done+=1
            if done%25==0:
                print(json.dumps({"weather_batches_done":done,"weather_batches_total":len(tasks),"series":len(weather),"failures":len(failures)}),flush=True)
    if failures:
        raise RuntimeError(f"weather batch failures: {failures[:5]}")

    normalized=hashlib.sha256()
    for key in sorted(weather):
        rec=weather[key]
        for d in sorted(rec["series"]):
            normalized.update(f"{key}|{d.isoformat()}|{rec['series'][d]:.6f}\n".encode())
    return weather,{
        "n_coordinate_year_series":len(weather),
        "n_api_batches":len(tasks),
        "normalized_daily_sha256":normalized.hexdigest(),
        "raw_response_hashes_sha256":hashlib.sha256("".join(sorted(raw_hashes)).encode()).hexdigest(),
    }


def weather_for_runs(run_need,weather):
    out={}
    for rid,rec in run_need.items():
        lat,lon=rec["coord"]; ed=rec["event_day"]
        key=f"{lat:.6f},{lon:.6f},{ed.year}"
        w=weather.get(key)
        if w is None:
            raise RuntimeError(f"missing weather series {key}")
        series=w["series"]
        if ed not in series:
            raise RuntimeError(f"missing event day {rid} {ed}")
        event_mm=float(series[ed])
        ante=0
        for off in range(1,DRY_CAP+1):
            dd=ed-timedelta(days=off)
            if dd not in series:
                raise RuntimeError(f"missing antecedent day {rid} {dd}")
            if float(series[dd])>=WET_MM:
                break
            ante+=1
        out[rid]={
            "event_day":ed,
            "event_mm":event_mm,
            "antecedent_dry_days":int(ante),
            "returned_grid":w["returned"],
            "timezone":w["timezone"],
        }
    return out


def build_ci(raw,eligible,sampled):
    vals=defaultdict(list)
    for r in raw["Counts.csv"]:
        rid=(r.get("RunID") or "").strip()
        st=(r.get("StopNumber") or "").strip()
        sp=(r.get("Species") or "").strip()
        if rid not in eligible or st not in sampled.get(rid,set()) or not sp:
            continue
        try: ci=int(float((r.get("CallingIndex") or "").strip()))
        except Exception: continue
        if ci in (1,2,3):
            vals[(rid,st,sp)].append(ci)
    by=defaultdict(dict)
    for (rid,st,sp),v in vals.items():
        by[(rid,st)][sp]=max(v)
    return by


def response_metrics(p,sampled,ci):
    wet=str(p.wet_RunID); dry=str(p.dry_RunID)
    stops=sorted(sampled[wet])
    strong_gain=strong_loss=0.0
    weak_gain=weak_loss=0.0
    bin_gain=bin_loss=0.0
    for st in stops:
        wm=ci.get((wet,st),{}); dm=ci.get((dry,st),{})
        for sp in set(wm)|set(dm):
            w=int(wm.get(sp,0)); d=int(dm.get(sp,0))
            if d==0 and w>0:
                bin_gain+=1
                if w==1: weak_gain+=1
                elif w>=2: strong_gain+=w
            if w==0 and d>0:
                bin_loss+=1
                if d==1: weak_loss+=1
                elif d>=2: strong_loss+=d
    return {
        "strong_activation_net":strong_gain-strong_loss,
        "weak_activation_net":weak_gain-weak_loss,
        "binary_activation_net":bin_gain-bin_loss,
        "strong_gain_score":strong_gain,
        "strong_loss_score":strong_loss,
    }


def fit(df,response,omit_ante=False):
    terms=[
        "rain_contrast",
        "event_amount_contrast",
    ]
    if not omit_ante:
        terms.append("antecedent_dryness_contrast")
    terms += ["temp_difference","doy_difference","year_gap","C(State)","C(RunNumber)"]
    formula=f"{response} ~ "+" + ".join(terms)
    m=smf.ols(formula,data=df).fit(cov_type="cluster",cov_kwds={"groups":df["route_cluster"]})
    out={"response":response,"formula":formula,"n_pairs":int(len(df)),"n_routes":int(df.route_cluster.nunique())}
    for term in ("rain_contrast","event_amount_contrast","antecedent_dryness_contrast"):
        if term in m.params:
            b=float(m.params[term]); se=float(m.bse[term])
            out[term]={"beta":b,"se":se,"ci95":[b-Q*se,b+Q*se],"p":float(m.pvalues[term])}
    return out


def main():
    raw=base.load()
    runs,route_sets=base.build_runs(raw)
    eligible=set(runs["RunID"].astype(str))
    sampled,site=physical_site_map(raw,eligible)
    pairs_all=base.pair_runs(runs,route_sets).copy().reset_index(drop=True)
    stable=np.asarray([stable_pair(p,sampled,site) for p in pairs_all.itertuples(index=False)],bool)
    pairs=pairs_all.loc[stable].copy().reset_index(drop=True)
    if len(pairs)!=4172:
        raise RuntimeError(f"stable pair count drift {len(pairs)} != 4172")

    coords,coord_sha,coord_rows=load_coordinates()
    meta=run_metadata(raw)

    candidate=[]
    run_need={}
    integer_fail=0
    centroid_fail=0
    for p in pairs.itertuples(index=False):
        wr=str(p.wet_RunID); dr=str(p.dry_RunID)
        wm=meta.get(wr); dm=meta.get(dr)
        if wm is None or dm is None:
            continue
        vals=[wm["days_since_rain"],dm["days_since_rain"]]
        if any(abs(x-round(x))>1e-9 for x in vals):
            integer_fail+=1
            continue
        if any(x<1 for x in vals):
            continue
        wc=run_centroid(wr,sampled,site,coords); dc=run_centroid(dr,sampled,site,coords)
        if wc is None or dc is None:
            centroid_fail+=1
            continue
        # Physical stability should imply identical centroids to numerical tolerance.
        if abs(wc[0]-dc[0])>1e-10 or abs(wc[1]-dc[1])>1e-10:
            raise RuntimeError(f"stable pair centroid mismatch {wr} {dr}")
        for rid,m,c in ((wr,wm,wc),(dr,dm,dc)):
            event=m["survey_date"]-timedelta(days=int(round(m["days_since_rain"])))
            run_need[rid]={"coord":c,"event_day":event}
        candidate.append(p)

    candidate_df=pd.DataFrame([p._asdict() for p in candidate])
    if candidate_df.empty:
        raise RuntimeError("no candidate pairs before weather")

    weather_series,weather_audit=retrieve_weather(run_need)
    rw=weather_for_runs(run_need,weather_series)

    rows=[]
    concordant_runs=set()
    for rid,v in rw.items():
        if v["event_mm"]>=WET_MM:
            concordant_runs.add(rid)
    for p in candidate:
        wet=str(p.wet_RunID); dry=str(p.dry_RunID)
        if wet not in concordant_runs or dry not in concordant_runs:
            continue
        row=p._asdict()
        w=rw[wet]; d=rw[dry]
        row.update({
            "event_mm_wet":w["event_mm"],
            "event_mm_dry":d["event_mm"],
            "antecedent_dry_wet":w["antecedent_dry_days"],
            "antecedent_dry_dry":d["antecedent_dry_days"],
            "event_amount_contrast":float(np.log1p(w["event_mm"])-np.log1p(d["event_mm"])),
            "antecedent_dryness_contrast":float(np.log1p(w["antecedent_dry_days"])-np.log1p(d["antecedent_dry_days"])),
        })
        rows.append(row)
    primary=pd.DataFrame(rows)

    gate={
        "stable_pairs":int(len(pairs)),
        "candidate_pairs_days_since_rain_ge1":int(len(candidate_df)),
        "primary_concordant_pairs":int(len(primary)),
        "primary_concordant_routes":int(primary["route_cluster"].nunique()) if len(primary) else 0,
        "eligible_run_concordance_fraction":float(len(concordant_runs)/len(rw)) if rw else 0.0,
        "days_since_rain_noninteger_pairs":int(integer_fail),
        "centroid_fail_pairs":int(centroid_fail),
    }
    gate["pass"]=bool(gate["primary_concordant_pairs"]>=1000 and gate["primary_concordant_routes"]>=250)

    output={
        "analysis":"naamp_rain_pulse_magnitude_test_v0_1",
        "contract":"exploration/NAAMP_RAIN_PULSE_MAGNITUDE_CONTRACT_V0_1.json",
        "source":{
            "coordinates_sha256":coord_sha,
            "coordinates_rows":coord_rows,
            "weather_model":"ERA5",
            "retrieval_api":API,
            "retrieval_parameters":{
                "daily":"precipitation_sum","models":"era5","precipitation_unit":"mm",
                "timezone":"auto","cell_selection":"nearest"
            },
            **weather_audit,
        },
        "feasibility_gate":gate,
    }

    if not gate["pass"]:
        output["status"]="not_run_due_to_prefixed_feasibility_gate"
        output["response_endpoints_read"]=False
        OUT.write_text(json.dumps(output,indent=2,sort_keys=True)+"\n")
        print(json.dumps(output,indent=2,sort_keys=True))
        return

    ci=build_ci(raw,eligible,sampled)
    response_rows=[]
    pair_lookup={(str(p.wet_RunID),str(p.dry_RunID)):p for p in pairs.itertuples(index=False)}
    for r in primary.itertuples(index=False):
        p=pair_lookup[(str(r.wet_RunID),str(r.dry_RunID))]
        row=r._asdict()
        row.update(response_metrics(p,sampled,ci))
        response_rows.append(row)
    df=pd.DataFrame(response_rows)

    endpoints=["strong_activation_net","weak_activation_net","binary_activation_net"]
    models={x:fit(df,x) for x in endpoints}
    noante=fit(df,"strong_activation_net",omit_ante=True)
    exact=df[df["year_gap"]==1].copy()
    exact_model=fit(exact,"strong_activation_net") if len(exact)>=100 else None

    b=models["strong_activation_net"]["event_amount_contrast"]
    support=bool(b["beta"]>0 and b["ci95"][0]>0)

    output.update({
        "status":"completed_after_prefixed_feasibility_gate",
        "weather_descriptives":{
            "event_mm_wet_mean":float(df.event_mm_wet.mean()),
            "event_mm_dry_mean":float(df.event_mm_dry.mean()),
            "event_amount_contrast_mean":float(df.event_amount_contrast.mean()),
            "antecedent_dry_wet_mean":float(df.antecedent_dry_wet.mean()),
            "antecedent_dry_dry_mean":float(df.antecedent_dry_dry.mean()),
        },
        "primary_models":models,
        "strong_activation_without_antecedent_adjustment":noante,
        "exact_consecutive_year":exact_model,
        "classification":{
            "event_magnitude_supports_strong_activation":support,
            "rule":"event_amount_contrast beta >0 with complete 95% CI >0 for strong_activation_net"
        },
        "interpretation_boundary":{
            "hydrological_threshold_consistent":support,
            "survey_night_inundation_observed":False,
            "causal_rainfall_claim":False,
            "submission_story_change_authorized":False,
        }
    })
    OUT.write_text(json.dumps(output,indent=2,sort_keys=True)+"\n")
    print(json.dumps(output,indent=2,sort_keys=True))


if __name__=="__main__":
    main()
