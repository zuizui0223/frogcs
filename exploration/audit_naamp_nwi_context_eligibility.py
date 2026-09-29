#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import importlib.util
from concurrent.futures import ThreadPoolExecutor, as_completed
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
from shapely.strtree import STRtree

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
    # First ask ArcGIS only for intersecting object IDs. returnIdsOnly is not
    # subject to the feature-page MaxRecordCount and avoids pagination order issues.
    id_params={
        "f":"json",
        "where":"1=1",
        "geometry":f"{minlon},{minlat},{maxlon},{maxlat}",
        "geometryType":"esriGeometryEnvelope",
        "inSR":"4326",
        "spatialRel":"esriSpatialRelIntersects",
        "returnIdsOnly":"true",
        "returnGeometry":"false",
    }
    raw=fetch(NWI_QUERY+"?"+urllib.parse.urlencode(id_params),timeout=120)
    obj=json.loads(raw.decode("utf-8"))
    if "error" in obj:
        raise RuntimeError(f"NWI ID query error: {obj['error']}")
    ids=[int(x) for x in (obj.get("objectIds") or [])]
    if not ids:
        return []

    features=[]
    seen=set()
    for i in range(0,len(ids),500):
        chunk=ids[i:i+500]
        params={
            "f":"geojson",
            "objectIds":",".join(str(x) for x in chunk),
            "outSR":"4326",
            "outFields":"*",
            "returnGeometry":"true",
        }
        raw=fetch(NWI_QUERY+"?"+urllib.parse.urlencode(params),timeout=120)
        page=json.loads(raw.decode("utf-8"))
        if "error" in page:
            raise RuntimeError(f"NWI feature query error: {page['error']}")
        for feat in page.get("features") or []:
            pp=feat.get("properties") or {}
            key=prop(pp,"OBJECTID") or prop(pp,"GLOBALID") or hashlib.sha1(
                json.dumps(feat,sort_keys=True,separators=(",",":")).encode()
            ).hexdigest()
            key=str(key)
            if key in seen:
                continue
            seen.add(key)
            features.append(feat)
    if len(features) < len(set(ids)):
        # Geometry-less or otherwise omitted records are allowed, but large losses
        # would make nearest-wetland assignment unsafe.
        missing=len(set(ids))-len(features)
        if missing > max(5,int(0.01*len(set(ids)))):
            raise RuntimeError(f"NWI feature retrieval lost {missing}/{len(set(ids))} object IDs")
    return features


def query_near_points(points_lonlat,distance_m=500.0):
    if not points_lonlat:
        return []
    geom={
        "points":[[float(lon),float(lat)] for lon,lat in points_lonlat],
        "spatialReference":{"wkid":4326},
    }
    id_params={
        "f":"json",
        "where":"1=1",
        "geometry":json.dumps(geom,separators=(",",":")),
        "geometryType":"esriGeometryMultipoint",
        "inSR":"4326",
        "spatialRel":"esriSpatialRelIntersects",
        "distance":str(float(distance_m)),
        "units":"esriSRUnit_Meter",
        "returnIdsOnly":"true",
        "returnGeometry":"false",
    }
    raw=fetch(NWI_QUERY+"?"+urllib.parse.urlencode(id_params),timeout=120)
    obj=json.loads(raw.decode("utf-8"))
    if "error" in obj:
        raise RuntimeError(f"NWI multipoint ID query error: {obj['error']}")
    ids=[int(x) for x in (obj.get("objectIds") or [])]
    if not ids:
        return []
    features=[]
    seen=set()
    for i in range(0,len(ids),500):
        chunk=ids[i:i+500]
        params={
            "f":"geojson",
            "objectIds":",".join(str(x) for x in chunk),
            "outSR":"4326",
            "outFields":"*",
            "returnGeometry":"true",
        }
        raw=fetch(NWI_QUERY+"?"+urllib.parse.urlencode(params),timeout=120)
        page=json.loads(raw.decode("utf-8"))
        if "error" in page:
            raise RuntimeError(f"NWI feature query error: {page['error']}")
        for feat in page.get("features") or []:
            pp=feat.get("properties") or {}
            key=prop(pp,"OBJECTID") or prop(pp,"GLOBALID") or hashlib.sha1(
                json.dumps(feat,sort_keys=True,separators=(",",":")).encode()
            ).hexdigest()
            key=str(key)
            if key in seen:
                continue
            seen.add(key)
            features.append(feat)
    return features


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
    # Query only wetlands within the largest contracted sensitivity radius.
    # ArcGIS distance queries support multipoint geometry, so one route request
    # covers all physical listening sites without downloading distant polygons.
    points_lonlat=[(lon,lat) for lat,lon in pts]
    return query_near_points(points_lonlat,SENS_M)


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
    route_items=sorted(by_route.items())

    def work(item):
        key,sids=item
        fs=route_features(sids,coords)

        # Contract-matched route-centred local projection. Transform each NWI
        # polygon once per route instead of rebuilding a projection for every
        # site x polygon distance calculation.
        pts=[coords[s] for s in sids if s in coords]
        lat0=float(np.mean([x[0] for x in pts]))
        lon0=float(np.mean([x[1] for x in pts]))
        crs=CRS.from_proj4(
            f"+proj=aeqd +lat_0={lat0:.8f} +lon_0={lon0:.8f} +datum=WGS84 +units=m +no_defs"
        )
        tr=Transformer.from_crs("EPSG:4326",crs,always_xy=True).transform
        projected=[]
        for feature in fs:
            gj=feature.get("geometry")
            if not gj:
                continue
            try:
                geom=transform(tr,shape(gj))
            except Exception:
                continue
            pp=feature.get("properties") or {}
            projected.append((geom,{
                "ATTRIBUTE":prop(pp,"ATTRIBUTE"),
                "WETLAND_TYPE":prop(pp,"WETLAND_TYPE"),
                "WATER_REGIME":prop(pp,"WATER_REGIME"),
                "WATER_REGIME_NAME":prop(pp,"WATER_REGIME_NAME"),
            }))

        local={}
        geoms=[x[0] for x in projected]
        props_by_index=[x[1] for x in projected]
        tree=STRtree(geoms) if geoms else None
        for sid in sids:
            lat,lon=coords[sid]
            point=transform(tr,Point(lon,lat))
            if tree is None:
                local[sid]={
                    "distance_m":None,"within_200m":False,"within_500m":False,
                    "ambiguous_tie":False,
                    "ATTRIBUTE":None,"WETLAND_TYPE":None,
                    "WATER_REGIME":None,"WATER_REGIME_NAME":None,
                }
                continue

            nearest_idx=int(tree.nearest(point))
            nearest_geom=geoms[nearest_idx]
            nearest_d=float(point.distance(nearest_geom))
            candidate_idx=np.asarray(tree.query(point.buffer(nearest_d+1.000001)),dtype=int)
            tie_idx=[]
            best_idx=nearest_idx
            best_d=nearest_d
            for idx in candidate_idx:
                d=float(point.distance(geoms[int(idx)]))
                if d<best_d-1e-6:
                    best_d=d
                    best_idx=int(idx)
            for idx in candidate_idx:
                d=float(point.distance(geoms[int(idx)]))
                if abs(d-best_d)<=1.0:
                    tie_idx.append(int(idx))

            best={
                "distance_m":best_d,
                **props_by_index[best_idx],
            }
            best["within_200m"]=bool(best_d<=PRIMARY_M)
            best["within_500m"]=bool(best_d<=SENS_M)
            best["ambiguous_tie"]=bool(len(set(tie_idx))>1)
            local[sid]=best
        return key,sids,local

    completed=0
    with ThreadPoolExecutor(max_workers=6) as ex:
        futs={ex.submit(work,item):item for item in route_items}
        for fut in as_completed(futs):
            key,sids=futs[fut]
            try:
                _,_,local=fut.result()
                matched.update(local)
            except Exception as e:
                route_failures.append({"route":list(key),"n_sites":len(sids),"error":str(e)[:500]})
            completed+=1
            if completed%50==0:
                print(json.dumps({"routes_processed":completed,"routes_total":len(route_items),"sites_matched":len(matched)}),flush=True)

    used_with_coord=[s for s in used if s in coords]
    primary=[
        s for s in used_with_coord
        if matched.get(s,{}).get("within_200m")
        and not matched.get(s,{}).get("ambiguous_tie",False)
    ]
    sens=[
        s for s in used_with_coord
        if matched.get(s,{}).get("within_500m")
        and not matched.get(s,{}).get("ambiguous_tie",False)
    ]
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
        n=sum(
            bool(matched.get(s,{}).get("within_200m"))
            and not bool(matched.get(s,{}).get("ambiguous_tie",False))
            for s in ids
        )
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
