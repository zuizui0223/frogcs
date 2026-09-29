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
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import icechunk
import numpy as np
import pandas as pd
import xarray as xr
from timezonefinder import TimezoneFinder

ROOT=Path(__file__).resolve().parents[1]
NAAMP=ROOT/"scripts"/"naamp"
OUT=ROOT/"exploration"/"OPENMETEO_ERA5_VPD_QUALIFICATION_RECEIPT_V0_1.json"
COORD_URL="https://www.sciencebase.gov/catalog/file/get/583dc314e4b0d1899f9dea8d?f=__disk__77%2F22%2F7e%2F77227ec46ac1c01592cd7d158d442cd8343a7536"
COORD_SHA="f71a87df9fc94e0d6c5d4466b4745c3bbaff874cbe7c28796b3f9eb44c2e6e83"
API="https://archive-api.open-meteo.com/v1/archive"
TOL_C=0.5
TOL_VPD=0.03
TOL_CELL=0.13
N=12


def loadmod(name,path):
    s=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(s)
    assert s.loader
    s.loader.exec_module(m)
    return m


base=loadmod("base",NAAMP/"run_naamp_ecological_pulse.py")


def fetch(url,retries=6):
    last=None
    for i in range(retries):
        try:
            req=urllib.request.Request(url,headers={"User-Agent":"frogcs-openmeteo-era5-qualification/0.1","Accept":"application/json,*/*"})
            with urllib.request.urlopen(req,timeout=180) as r:
                return r.read()
        except Exception as e:
            last=e
            time.sleep(2*(i+1))
    raise RuntimeError(f"fetch failed {url}: {last}")


def parse_time(s):
    raw=str(s or "").strip()
    for fmt in ("%H:%M","%H:%M:%S","%I:%M %p","%I:%M:%S %p"):
        try:
            return datetime.strptime(raw,fmt).time()
        except Exception:
            pass
    return None


def parse_date(s):
    raw=str(s or "").strip()
    for fmt in ("%m/%d/%Y","%m/%d/%y","%Y-%m-%d","%Y/%m/%d"):
        try:
            return datetime.strptime(raw,fmt).date()
        except Exception:
            pass
    return None


def mean_coords(raw,eligible_run_ids):
    b=fetch(COORD_URL)
    got=hashlib.sha256(b).hexdigest()
    if got!=COORD_SHA:
        raise RuntimeError(f"Coordinates hash drift {got}")
    coord={}
    for r in csv.DictReader(io.StringIO(b.decode("utf-8-sig"))):
        sid=(r.get("SiteID") or "").strip()
        if sid:
            coord[sid]=(float(r["lat"]),float(r["lon"]))

    sites={}
    for s in raw["Stops.csv"]:
        rid=(s.get("RunID") or "").strip()
        if rid not in eligible_run_ids or (s.get("SkippedStop") or "").strip()!="0":
            continue
        st=(s.get("StopNumber") or "").strip()
        sid=(s.get("SiteID") or "").strip()
        if st and sid:
            sites[(rid,st)]=sid

    out={}
    for rid in eligible_run_ids:
        vals=[]
        for st in sorted([st for (x,st) in sites if x==rid]):
            sid=sites[(rid,st)]
            if sid in coord:
                vals.append(coord[sid])
        if len(vals)==10:
            out[rid]=(float(np.mean([x[0] for x in vals])),float(np.mean([x[1] for x in vals])))
    return out


def midpoint_utc(run_row,lat,lon,tf):
    d=parse_date(run_row.get("SurveyDate"))
    a=parse_time(run_row.get("StartTime"))
    b=parse_time(run_row.get("EndTime"))
    if d is None or a is None or b is None:
        return None,None
    start=datetime.combine(d,a)
    end=datetime.combine(d,b)
    if end<start:
        end+=timedelta(days=1)
    mid=start+(end-start)/2
    tz=tf.timezone_at(lat=lat,lng=lon)
    if not tz:
        return None,None
    aware=mid.replace(tzinfo=ZoneInfo(tz))
    return aware.astimezone(ZoneInfo("UTC")).replace(tzinfo=None),tz


def round_hour_earlier(dt):
    baseh=dt.replace(minute=0,second=0,microsecond=0)
    # nearest hour, exactly :30 goes earlier
    if dt.minute>30 or (dt.minute==30 and (dt.second>0 or dt.microsecond>0)):
        return baseh+timedelta(hours=1)
    return baseh


def om_url(lat,lon,d):
    params={
        "latitude":f"{lat:.6f}",
        "longitude":f"{lon:.6f}",
        "start_date":d.isoformat(),
        "end_date":d.isoformat(),
        "hourly":"temperature_2m,dew_point_2m,vapour_pressure_deficit",
        "models":"era5",
        "cell_selection":"nearest",
        "elevation":"nan",
        "timezone":"GMT",
    }
    return API+"?"+urllib.parse.urlencode(params)


def openmeteo_point(lat,lon,utc_hour):
    # Request both UTC calendar dates if necessary to cover the rounded hour.
    d=utc_hour.date()
    obj=json.loads(fetch(om_url(lat,lon,d)).decode("utf-8"))
    if obj.get("error"):
        raise RuntimeError(obj)
    hours=obj["hourly"]
    target=utc_hour.strftime("%Y-%m-%dT%H:%M")
    try:
        j=hours["time"].index(target)
    except ValueError:
        raise RuntimeError(f"target hour {target} absent")
    return {
        "returned_lat":float(obj["latitude"]),
        "returned_lon":float(obj["longitude"]),
        "temperature_C":float(hours["temperature_2m"][j]),
        "dewpoint_C":float(hours["dew_point_2m"][j]),
        "vpd_kPa":float(hours["vapour_pressure_deficit"][j]),
        "time":target,
        "timezone":str(obj.get("timezone")),
    }


def vpd(T,Td):
    es=0.6108*math.exp(17.27*T/(T+237.3))
    ea=0.6108*math.exp(17.27*Td/(Td+237.3))
    return max(0.0,es-ea)


def main():
    raw=base.load()
    runs,_=base.build_runs(raw)
    eligible=set(runs["RunID"].astype(str))
    coords=mean_coords(raw,eligible)
    raw_run={str(r.get("RunID") or "").strip():r for r in raw["Runs.csv"]}

    tf=TimezoneFinder()
    candidates=[]
    for r in runs.itertuples(index=False):
        rid=str(r.RunID)
        if rid not in coords or rid not in raw_run:
            continue
        lat,lon=coords[rid]
        utc,tz=midpoint_utc(raw_run[rid],lat,lon,tf)
        if utc is None:
            continue
        candidates.append((hashlib.sha256(rid.encode()).hexdigest(),rid,lat,lon,utc,tz))
    candidates=sorted(candidates)[:N]
    if len(candidates)!=N:
        raise RuntimeError(f"qualification candidates {len(candidates)} != {N}")

    # Verify multi-coordinate API response shape using the first two points on the first point's date.
    latlist=",".join(f"{x[2]:.6f}" for x in candidates[:2])
    lonlist=",".join(f"{x[3]:.6f}" for x in candidates[:2])
    d=candidates[0][4].date()
    params={
        "latitude":latlist,"longitude":lonlist,
        "start_date":d.isoformat(),"end_date":d.isoformat(),
        "hourly":"vapour_pressure_deficit",
        "models":"era5","cell_selection":"nearest","elevation":"nan","timezone":"GMT",
    }
    multi=json.loads(fetch(API+"?"+urllib.parse.urlencode(params)).decode("utf-8"))
    multi_shape_pass=bool(isinstance(multi,list) and len(multi)==2 and all("hourly" in x for x in multi))

    storage=icechunk.s3_storage(bucket="earthmover-icechunk-era5",prefix="icechunkV2",region="us-east-1",anonymous=True)
    repo=icechunk.Repository.open(storage)
    session=repo.readonly_session("main")
    ds=xr.open_zarr(session.store,group="single/temporal",consolidated=False,chunks=None)
    t2m=ds["t2m"]; d2m=ds["d2m"]
    times=np.asarray(ds.valid_time.values)
    lats=np.asarray(ds.latitude.values,float); lons=np.asarray(ds.longitude.values,float)

    rows=[]
    all_pass=multi_shape_pass
    for _,rid,lat,lon,utc,tz in candidates:
        hour=round_hour_earlier(utc)
        om=openmeteo_point(lat,lon,hour)

        yi=int(np.abs(lats-lat).argmin())
        lon360=lon%360.0
        xi=int(np.abs(lons-lon360).argmin())
        era_lat=float(lats[yi])
        era_lon=float(((lons[xi]+180)%360)-180)
        ti=int(np.searchsorted(times,np.datetime64(hour),"left"))
        if ti>=len(times) or np.datetime64(times[ti])!=np.datetime64(hour):
            raise RuntimeError(f"ERA5 time {hour} not exact")

        T=float(np.asarray(t2m.isel(valid_time=ti,latitude=yi,longitude=xi).values).reshape(-1)[0])-273.15
        Td=float(np.asarray(d2m.isel(valid_time=ti,latitude=yi,longitude=xi).values).reshape(-1)[0])-273.15
        om_calc=vpd(om["temperature_C"],om["dewpoint_C"])

        # longitude wrap-safe differences
        om_lon=((om["returned_lon"]+180)%360)-180
        dl=abs(((om_lon-era_lon+180)%360)-180)
        cell_ok=bool(abs(om["returned_lat"]-era_lat)<=TOL_CELL and dl<=TOL_CELL)
        t_ok=bool(abs(om["temperature_C"]-T)<=TOL_C)
        td_ok=bool(abs(om["dewpoint_C"]-Td)<=TOL_C)
        vpd_ok=bool(abs(om["vpd_kPa"]-om_calc)<=TOL_VPD)
        passed=bool(cell_ok and t_ok and td_ok and vpd_ok)
        all_pass=all_pass and passed

        rows.append({
            "RunID":rid,"route_mean_lat":lat,"route_mean_lon":lon,
            "timezone":tz,"survey_midpoint_utc":utc.isoformat(),
            "comparison_hour_utc":hour.isoformat(),
            "earthmover_cell":[era_lat,era_lon],
            "openmeteo_cell":[om["returned_lat"],om_lon],
            "earthmover_temperature_C":T,
            "openmeteo_temperature_C":om["temperature_C"],
            "temperature_abs_diff_C":abs(om["temperature_C"]-T),
            "earthmover_dewpoint_C":Td,
            "openmeteo_dewpoint_C":om["dewpoint_C"],
            "dewpoint_abs_diff_C":abs(om["dewpoint_C"]-Td),
            "openmeteo_vpd_kPa":om["vpd_kPa"],
            "recalculated_openmeteo_vpd_kPa":om_calc,
            "vpd_abs_diff_kPa":abs(om["vpd_kPa"]-om_calc),
            "cell_pass":cell_ok,"temperature_pass":t_ok,"dewpoint_pass":td_ok,"vpd_pass":vpd_ok,
            "passed":passed,
        })

    out={
        "analysis":"openmeteo_era5_vpd_qualification_v0_1",
        "contract":"exploration/OPENMETEO_ERA5_VPD_QUALIFICATION_CONTRACT_V0_1.json",
        "n_points":N,
        "multi_coordinate_shape_pass":multi_shape_pass,
        "qualification_pass":bool(all_pass),
        "max_temperature_abs_diff_C":float(max(x["temperature_abs_diff_C"] for x in rows)),
        "max_dewpoint_abs_diff_C":float(max(x["dewpoint_abs_diff_C"] for x in rows)),
        "max_vpd_recalc_abs_diff_kPa":float(max(x["vpd_abs_diff_kPa"] for x in rows)),
        "comparisons":rows,
        "response_data_read":False,
    }
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
