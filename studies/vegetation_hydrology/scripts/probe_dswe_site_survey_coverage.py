#!/usr/bin/env python3
"""DSWE 30-day prior-scene *metadata* feasibility at sampled NAAMP sites.
USGS Landsatlook STAC items, no image pixels or frog calling outcomes.
"""
from __future__ import annotations
import argparse
import csv
import datetime as dt
import hashlib
import json
import math
import urllib.error
import urllib.parse
import urllib.request
from collections import defaultdict
from pathlib import Path

COLLECTION="landsat-c2l3-dswe"
URL=f"https://landsatlook.usgs.gov/stac-server/collections/{COLLECTION}/items"
UA="frogcs-outcome-blind-survey-dswe-availability-v0.1"
YEARS=(2001,2008,2015)
STATES_PER_YEAR=3

def read_sites(coords,calendar):
    with open(coords,newline="",encoding="utf-8-sig") as f:
        sites={(r["RouteNumber"].strip(),r["SiteID"].strip()):r
               for r in csv.DictReader(f) if r.get("status")=="accepted"}
    by_sy=defaultdict(dict)
    with open(calendar,newline="",encoding="utf-8-sig") as f:
        rd=csv.DictReader(f)
        if not rd.fieldnames or not {"State","RouteNumber","SiteID","SurveyDate","SurveyYear"}.issubset(rd.fieldnames):
            raise ValueError("invalid source-only calendar")
        if "CallingIndex" in rd.fieldnames or "Species" in rd.fieldnames:raise ValueError("refuse frog outcomes")
        for r in rd:
            year=int(r["SurveyYear"])
            if year not in YEARS:continue
            key=(r["RouteNumber"].strip(),r["SiteID"].strip())
            if key not in sites:continue
            try: d=dt.date.fromisoformat(r["SurveyDate"])
            except ValueError:continue
            if year!=d.year:raise ValueError("source date-year mismatch")
            ident=(key,d)
            by_sy[(year,r["State"])][ident]=(sites[key],r,d)
    selected=[]
    for year in YEARS:
        states=sorted(s for y,s in by_sy if y==year)[:STATES_PER_YEAR]
        for state in states:
            candidates=by_sy[(year,state)]
            choice=min(candidates,key=lambda k:hashlib.sha256((k[0][0]+":"+k[0][1]+":"+k[1].isoformat()).encode()).hexdigest())
            position,row,date=candidates[choice]
            lat,lon=float(position["lat"]),float(position["lon"])
            if not (24<=lat<=51 and -126<=lon<=-66):raise ValueError("coordinates outside study scope")
            selected.append({"year":year,"state":state,"route":row["RouteNumber"],"site":row["SiteID"],
                             "date":date.isoformat(),"lat":lat,"lon":lon})
    if len(selected)!=len(YEARS)*STATES_PER_YEAR:raise RuntimeError("not enough year-state survey sites")
    return selected

def get_json(url):
    req=urllib.request.Request(url,headers={"User-Agent":UA,"Accept":"application/geo+json"})
    with urllib.request.urlopen(req,timeout=35) as r:
        blob=r.read(3_000_001)
        if len(blob)>3_000_000:raise RuntimeError("STAC result over 3 MB")
    return json.loads(blob)

def observe(entry):
    date=dt.date.fromisoformat(entry["date"])
    before=date-dt.timedelta(days=30)
    lon,lat=entry["lon"],entry["lat"]
    # Bounding the approximate 500-m study buffer: deliberately pad +/- 0.012 degrees.
    params=urllib.parse.urlencode({
        "bbox":",".join(format(z,".7f") for z in (lon-.012,lat-.012,lon+.012,lat+.012)),
        "datetime":before.isoformat()+"T00:00:00Z/"+date.isoformat()+"T00:00:00Z",
        "limit":100
    })
    url=URL+"?"+params
    r=dict(entry)
    r.update({"study_window":"strictly before survey date, 30 days",
              "stac_collection":COLLECTION,"query_url":url,
              "max_items":100,
              "numberMatched":None,"numberReturned":None,"candidate_scene_count":0,
              "all_items_enumerated":False,"sample_scene_ids":[],"has_allmask_asset":False,
              "qa_pixels_assessed":False,"water_fraction_estimated":False,
              "frog_outcomes_read":False})
    try:
        d=get_json(url)
        if d.get("type")!="FeatureCollection":raise ValueError("not a STAC FeatureCollection")
        r["numberMatched"]=d.get("numberMatched")
        scenes=d.get("features",[])
        r["numberReturned"]=len(scenes)
        good=[]
        for scene in scenes:
            event=dt.datetime.fromisoformat(scene["properties"]["datetime"].replace("Z","+00:00")).date()
            if not (before<=event<date):raise ValueError("scene not strictly before survey day")
            if "inwam" not in scene.get("assets",{}):raise ValueError("missing DSWE interpreted-with-all-masks")
            bbox=scene.get("bbox")
            if bbox and not(bbox[0]<=lon<=bbox[2] and bbox[1]<=lat<=bbox[3]):
                continue
            good.append({"id":scene["id"],"acquisition_date":event.isoformat(),
                         "inwam_url":scene["assets"]["inwam"]["href"]})
        r["candidate_scene_count"]=len(good)
        r["has_allmask_asset"]=bool(good)
        r["sample_scene_ids"]=[{"id":t["id"],"date":t["acquisition_date"]} for t in good[:7]]
        r["all_items_enumerated"]=len(scenes)<100 and not any(x.get("rel")=="next" for x in d.get("links",[]))
        r["status"]="metadata_candidates_found" if good else "no_prior_scene_candidates"
        if not r["all_items_enumerated"]:r["status"]="incomplete_pagination"
    except Exception as ex:
        r["status"]="metadata_error";r["error"]=type(ex).__name__+": "+str(ex)[:200]
    return r

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--accepted-coordinates",required=True,type=Path)
    p.add_argument("--site-calendar",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    args=p.parse_args()
    selected=read_sites(args.accepted_coordinates,args.site_calendar)
    out=[observe(row) for row in selected]
    report={"analysis":"naamp_pre_survey_dswe_stac_feasibility_v0_1",
            "purpose":"scene metadata coverage only, no wetland water/pixel inference",
            "dataset":"USGS Landsat Collection 2 Level-3 DSWE (INWAM)",
            "years":list(YEARS),"sites_selected":len(selected),
            "sites_with_candidate_scenes":sum(r["candidate_scene_count"]>0 for r in out),
            "sites_with_complete_pagination":sum(r["all_items_enumerated"] for r in out),
            "no_frog_calling_outcomes_read":True,"no_raster_pixels_read":True,
            "queries":out}
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({"analysis":report["analysis"],"sites_selected":len(selected),
                     "sites_with_candidate_scenes":report["sites_with_candidate_scenes"],
                     "sites_with_complete_pagination":report["sites_with_complete_pagination"],
                     "status_by_site":[{"year":r["year"],"state":r["state"],"status":r["status"],
                         "scenes":r["candidate_scene_count"]} for r in out]},indent=2))
if __name__=="__main__":main()
