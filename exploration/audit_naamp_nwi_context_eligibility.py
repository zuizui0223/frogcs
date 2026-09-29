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
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from pyproj import CRS, Transformer
from shapely.geometry import Point, shape
from shapely.ops import transform

ROOT=Path(__file__).resolve().parents[1]
NAAMP=ROOT/"scripts"/"naamp"
OUT=ROOT/"exploration"/"NAAMP_NWI_CONTEXT_ELIGIBILITY_RECEIPT_V0_1.json"

COORD_URL="https://www.sciencebase.gov/catalog/file/get/583dc314e4b0d1899f9dea8d?f=__disk__77%2F22%2F7e%2F77227ec46ac1c01592cd7d158d442cd8343a7536"
COORD_SHA="f71a87df9fc94e0d6c5d4466b4745c3bbaff874cbe7c28796b3f9eb44c2e6e83"
NWI_QUERY="https://fwspublicservices.wim.usgs.gov/wetlandsmapservice/rest/services/Wetlands/MapServer/0/query"
PRIMARY_M=200.0
SENS_M=500.0


def loadmod(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    mod=importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(mod)
    return mod


base=loadmod("pulse_base",NAAMP/"run_naamp_ecological_pulse.py")


def fetch(url,timeout=180,retries=5):
    last=None
    for i in range(retries):
        try:
            req=urllib.request.Request(url,headers={
                "User-Agent":"frogcs-nwi-context-audit/0.1",
                "Accept":"application/json,application/geo+json,*/*",
            })
            with urllib.request.urlopen(req,timeout=timeout) as r:
                return r.read()
        except Exception as e:
            last=e
            time.sleep(1.5*(i+1))
    raise RuntimeError(f"fetch failed after retries: {url}: {last}")


def load_coordinates():
    raw=fetch(COORD_URL)
    got=hashlib.sha256(raw).hexdigest()
    if got!=COORD_SHA:
        raise RuntimeError(f"Coordinates.csv hash drift: {got}")
    rows=list(csv.DictReader(io.StringIO(raw.decode("utf-8-sig"))))
    coords={}
    route={}
    for r in rows:
        sid=(r.get("SiteID") or "").strip()
        rn=(r.get("RouteNumber") or "").strip()
        if not sid:
            continue
        lat=float(r["lat"]); lon=float(r["lon"])
        if not (-90<=lat<=90 and -180<=lon<=180):
            continue
        if sid in coords and coords[sid]!=(lat,lon):
            raise RuntimeError(f"coordinate conflict for SiteID {sid}")
        coords[sid]=(lat,lon)
        route[sid]=rn
    return coords,route,got,len(rows)


def pair_used_siteids(raw,runs,route_sets):
    pairs=base.pair_runs(runs,route_sets).copy().reset_index(drop=True)
    pair_run_ids=set(pairs["wet_RunID"].astype(str))|set(pairs["dry_RunID"].astype(str))
    used=set()
    site_route={}
    pair_sites=[]
    run_meta={str(r.RunID):(str(r.State),str(r.RouteNumber)) for r in runs.itertuples(index=False)}
    by_run_stop={}
    for s in raw["Stops.csv"]:
        rid=(s.get("RunID") or "").strip()
        if rid not in pair_run_ids or (s.get("SkippedStop") or "").strip()!="0":
            continue
        st=(s.get("StopNumber") or "").strip()
        sid=(s.get("SiteID") or "").strip()
        if not st or not sid:
            continue
        key=(rid,st)
        if key in by_run_stop and by_run_stop[key]!=sid:
            raise RuntimeError(f"multiple SiteID for {key}")
        by_run_stop[key]=sid
        used.add(sid)
        if rid in run_meta:
            site_route[sid]=run_meta[rid]
    for p in pairs.itertuples(index=False):
        wet=str(p.wet_RunID); dry=str(p.dry_RunID)
        stops=sorted({st for (rid,st) in by_run_stop if rid in (wet,dry)})
        pair_sites.append({
            "wet":wet,"dry":dry,
            "wet_sites":[by_run_stop.get((wet,st)) for st in stops],
            "dry_sites":[by_run_stop.get((dry,st)) for st in stops],
        })
    return pairs,used,site_route,pair_sites


def prop(props,suffix):
    suffix=suffix.upper()
    for k,v in props.items():
        ku=str(k).upper()
        if ku==suffix or ku.endswith("."+suffix) or ku.endswith("_"+suffix):
            return v
    return None


def query_envelope(minlon,minlat,maxlon,maxlat):
    params={
        "f":"geojson",
        "where":"1=1",
        "geometry":f"{minlon},{minlat},{maxlon},{maxlat}",
        "geometryType":"esriGeometryEnvelope",
        "inSR":"4326",
        "spatialRel":"esriSpatialRelIntersects",
        "outSR":"4326",
        "outFields":"*",
        "returnGeometry":"true",
    }
    url=NWI_QUERY+"?"+urllib.parse.urlencode(params)
    raw=fetch(url,timeout=120)
    obj=json.loads(raw.decode("utf-8"))
    if "error" in obj:
        raise RuntimeError(f"NWI query error: {obj['error']}")
    return obj.get("features") or []


def projected_distance(point_lonlat,geom,lat0,lon0):
    crs=CRS.from_proj4(
        f"+proj=aeqd +lat_0={lat0:.8f} +lon_0={lon0:.8f} +datum=WGS84 +units=m +no_defs"
    )
    tr=Transformer.from_crs("EPSG:4326",crs,always_xy=True).transform
    p=transform(tr,Point(point_lonlat[0],point_lonlat[1]))
    g=transform(tr,geom)
    return float(p.distance(g))


def route_features(site_ids,coords):
    pts=[coords[s] for s in site_ids if s in coords]
    if not pts:
        return []
    lats=[x[0] for x in pts]; lons=[x[1] for x in pts]
    lat0=float(np.mean(lats)); lon0=float(np.mean(lons))
    # >=1 km search margin, larger than the 500 m sensitivity radius.
    dlat=0.012
    dlon=0.012/max(0.25,math.cos(math.radians(lat0)))
    features=query_envelope(min(lons)-dlon,min(lats)-dlat,max(lons)+dlon,max(lats)+dlat)
    # A route-sized envelope should normally be far below the service limit.
    # If exactly at limit, use per-site small envelopes to avoid silent truncation.
    if len(features)>=1000:
        merged={}
        for sid in site_ids:
            if sid not in coords:
                continue
            lat,lon=coords[sid]
            dlat2=0.006
            dlon2=0.006/max(0.25,math.cos(math.radians(lat)))
            fs=query_envelope(lon-dlon2,lat-dlat2,lon+dlon2,lat+dlat2)
            for f in fs:
                pp=f.get("properties") or {}
                key=prop(pp,"GLOBALID") or prop(pp,"OBJECTID") or json.dumps(pp,sort_keys=True)
                merged[str(key)]=f
        features=list(merged.values())
    return features


def classify_site(sid,coords,features):
    lat,lon=coords[sid]
    best=None
    ties=[]
    for f in features:
        gj=f.get("geometry")
        if not gj:
            continue
        try:
            geom=shape(gj)
        except Exception:
            continue
        d=projected_distance((lon,lat),geom,lat,lon)
        props=f.get("properties") or {}
        rec={
            "distance_m":d,
            "ATTRIBUTE":prop(props,"ATTRIBUTE"),
            "WETLAND_TYPE":prop(props,"WETLAND_TYPE"),
            "WATER_REGIME":prop(props,"WATER_REGIME"),
            "WATER_REGIME_NAME":prop(props,"WATER_REGIME_NAME"),
        }
        if best is None or d<best["distance_m"]-1e-6:
            best=rec
            ties=[rec]
        elif abs(d-best["distance_m"])<=1.0:
            ties.append(rec)
    if best is None:
        return {
            "distance_m":None,"within_200m":False,"within_500m":False,
            "ambiguous_tie":False,
            "ATTRIBUTE":None,"WETLAND_TYPE":None,"WATER_REGIME":None,"WATER_REGIME_NAME":None,
        }
    best=dict(best)
    best["within_200m"]=bool(best["distance_m"]<=PRIMARY_M)
    best["within_500m"]=bool(best["distance_m"]<=SENS_M)
    best["ambiguous_tie"]=bool(len(ties)>1)
    return best


def main():
    raw=base.load()
    runs,route_sets=base.build_runs(raw)
    pairs,used,site_route,pair_sites=pair_used_siteids(raw,runs,route_sets)
    coords,coord_route,coord_sha,coord_rows=load_coordinates()

    missing_coords=sorted(s for s in used if s not in coords)
    by_route=defaultdict(list)
    for sid in sorted(used):
        if sid not in coords:
            continue
        key=site_route.get(sid)
        if key is None:
            rn=coord_route.get(sid)
            key=("UNKNOWN",rn or "UNKNOWN")
        by_route[key].append(sid)

    matched={}
    route_failures=[]
    for n,(key,sids) in enumerate(sorted(by_route.items()),start=1):
        try:
            fs=route_features(sids,coords)
            for sid in sids:
                matched[sid]=classify_site(sid,coords,fs)
        except Exception as e:
            route_failures.append({"route":list(key),"n_sites":len(sids),"error":str(e)[:500]})
        if n%50==0:
            print(json.dumps({"routes_processed":n,"routes_total":len(by_route),"sites_matched":len(matched)}))

    used_with_coord=[s for s in used if s in coords]
    primary=[s for s in used_with_coord if matched.get(s,{}).get("within_200m")]
    sens=[s for s in used_with_coord if matched.get(s,{}).get("within_500m")]
    regime=[s for s in primary if str(matched[s].get("WATER_REGIME_NAME") or "").strip()]
    wettype=[s for s in primary if str(matched[s].get("WETLAND_TYPE") or "").strip()]

    regime_counts=Counter(str(matched[s].get("WATER_REGIME_NAME")) for s in regime)
    type_counts=Counter(str(matched[s].get("WETLAND_TYPE")) for s in wettype)
    code_counts=Counter(str(matched[s].get("WATER_REGIME")) for s in regime if matched[s].get("WATER_REGIME") is not None)
    large_categories=sum(v>=250 for v in regime_counts.values())

    site_cov=(len(primary)/len(used_with_coord)) if used_with_coord else 0.0
    regime_cov=(len(regime)/len(primary)) if primary else 0.0
    gate=bool(site_cov>=.50 and regime_cov>=.80 and large_categories>=2)

    # Pair-level coverage: proportion of the up-to-20 physical SiteIDs appearing in each wet/dry pair
    # that have primary NWI classification. This is descriptive only.
    pair_cov=[]
    for rec in pair_sites:
        ids=[s for s in rec["wet_sites"]+rec["dry_sites"] if s]
        if not ids:
            continue
        n=sum(bool(matched.get(s,{}).get("within_200m")) for s in ids)
        pair_cov.append(n/len(ids))

    dists=[float(matched[s]["distance_m"]) for s in matched if matched[s].get("distance_m") is not None]
    output={
        "analysis":"naamp_nwi_context_eligibility_v0_1",
        "contract":"exploration/NAAMP_NWI_CONTEXT_ELIGIBILITY_CONTRACT_V0_1.json",
        "sources":{
            "coordinates_sha256":coord_sha,
            "coordinates_rows":coord_rows,
            "nwi_query_endpoint":NWI_QUERY,
        },
        "population":{
            "matched_pairs":int(len(pairs)),
            "pair_used_siteids":int(len(used)),
            "pair_used_siteids_with_coordinates":int(len(used_with_coord)),
            "missing_coordinate_siteids":int(len(missing_coords)),
            "routes_queried":int(len(by_route)),
            "route_query_failures":route_failures,
        },
        "coverage":{
            "nearest_polygon_found":int(len(dists)),
            "within_200m_sites":int(len(primary)),
            "within_200m_fraction_of_coordinate_sites":float(site_cov),
            "within_500m_sites":int(len(sens)),
            "within_500m_fraction_of_coordinate_sites":float(len(sens)/len(used_with_coord)) if used_with_coord else 0.0,
            "primary_water_regime_nonempty":int(len(regime)),
            "primary_water_regime_fraction":float(regime_cov),
            "primary_wetland_type_nonempty":int(len(wettype)),
            "pair_primary_coverage_mean":float(np.mean(pair_cov)) if pair_cov else None,
            "pair_primary_coverage_median":float(np.median(pair_cov)) if pair_cov else None,
            "nearest_distance_m_quantiles":{
                "median":float(np.median(dists)) if dists else None,
                "q75":float(np.quantile(dists,.75)) if dists else None,
                "q90":float(np.quantile(dists,.90)) if dists else None,
                "q95":float(np.quantile(dists,.95)) if dists else None,
            },
        },
        "variation":{
            "water_regime_name_counts":dict(regime_counts.most_common()),
            "water_regime_code_counts":dict(code_counts.most_common()),
            "wetland_type_counts":dict(type_counts.most_common()),
            "water_regime_categories_ge_250_sites":int(large_categories),
        },
        "feasibility_gate":{
            "site_coverage_pass":bool(site_cov>=.50),
            "hydrology_field_coverage_pass":bool(regime_cov>=.80),
            "variation_pass":bool(large_categories>=2),
            "overall_pass":gate,
        },
        "site_matches":{
            s:{
                "lat":coords[s][0],"lon":coords[s][1],
                **matched.get(s,{
                    "distance_m":None,"within_200m":False,"within_500m":False,
                    "ambiguous_tie":False,"ATTRIBUTE":None,"WETLAND_TYPE":None,
                    "WATER_REGIME":None,"WATER_REGIME_NAME":None,
                })
            }
            for s in sorted(used_with_coord)
        },
        "interpretation_boundary":{
            "response_endpoints_read":False,
            "nwi_is_survey_night_water_level":False,
            "nearest_polygon_proves_call_origin":False,
            "mechanism_test_authorized":gate,
        }
    }
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(output,indent=2,sort_keys=True)+"\n")
    print(json.dumps({k:v for k,v in output.items() if k!="site_matches"},indent=2,sort_keys=True))


if __name__=="__main__":
    main()
