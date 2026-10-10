#!/usr/bin/env python3
"""v5.5 public government MDMS 2022 GeoJSON PROPERTY SCHEMA only.

Download public small GeoJSON from trusted CKAN official URL and parse feature
property KEYS and attribute MISSINGNESS. Never serialize or print geometry,
coordinates, site labels, or any attribute values. Site-name join comes LATER.
"""
from __future__ import annotations
import collections
import json
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

API="https://data.gov.au/data/api/3/action/resource_show"
ID="35b2b6d7-2557-49c9-bcc0-af98d17cb49a"
MAX_BYTES=1_200_000
ALLOWED_HOSTS={"data.gov.au","www.data.gov.au"}

def safe_request(url, cap=MAX_BYTES):
    parts=urllib.parse.urlparse(url)
    if parts.scheme!="https" or parts.hostname not in ALLOWED_HOSTS:
        raise ValueError("not an official trusted HTTPS data.gov.au host")
    req=urllib.request.Request(url,headers={"Accept":"application/json",
         "User-Agent":"frogcs-mdms-public-schema-no-geocoordinates-v55"})
    with urllib.request.urlopen(req,timeout=40) as response:
        final=urllib.parse.urlparse(response.geturl())
        if final.scheme!="https" or final.hostname not in ALLOWED_HOSTS:
            raise ValueError("unexpected redirect host")
        raw=response.read(cap+1)
        if response.status!=200 or len(raw)>cap:
            raise ValueError("unbounded source JSON")
    return json.loads(raw.decode("utf-8-sig"))

def metadata(obj):
    if not isinstance(obj,dict) or obj.get("success") is not True:
        raise ValueError("CKAN resource metadata failed")
    r=obj.get("result") or {}
    if r.get("id")!=ID or str(r.get("format","")).lower()!="geojson":
        raise ValueError("resource ID or file type mismatch")
    declared=r.get("size")
    if isinstance(declared,(int,float)) and declared>MAX_BYTES:
        raise ValueError("declared GeoJSON file too large")
    url=str(r.get("url") or "")
    if not url:return None
    p=urllib.parse.urlparse(url)
    if p.scheme!="https" or p.hostname not in ALLOWED_HOSTS:
        raise ValueError("untrusted official resource file host")
    return url

def schema(blob):
    if not isinstance(blob,dict) or blob.get("type")!="FeatureCollection":
        raise ValueError("not a GeoJSON feature collection")
    features=blob.get("features")
    if not isinstance(features,list) or not 0<len(features)<=15000:
        raise ValueError("unexpected feature count")
    props_count=collections.Counter()
    nonmissing=collections.Counter()
    geom_types=collections.Counter()
    no_props=0
    for f in features:
        if not isinstance(f,dict) or f.get("type")!="Feature":
            raise ValueError("invalid feature")
        geometry=f.get("geometry")
        if geometry is None:
            geom_types["NULL"]+=1
        elif isinstance(geometry,dict):
            geom_types[str(geometry.get("type") or "UNKNOWN")[:30]]+=1
        else:
            raise ValueError("bad geometry")
        p=f.get("properties")
        if not isinstance(p,dict):
            no_props+=1
            continue
        for key,value in p.items():
            if not isinstance(key,str) or len(key)>100:
                raise ValueError("unexpected property")
            props_count[key]+=1
            if value is not None and str(value).strip():
                nonmissing[key]+=1
    candidates=sorted(k for k in props_count if any(
       part in k.lower() for part in ("sample","point","site","name","code","id","area","wetland","program")))
    return {
        "status":"PUBLIC_MDMS_GEOJSON_ATTRIBUTE_SCHEMA_ONLY",
        "source_resource_id":ID,
        "n_features":len(features),
        "feature_geometry_types_NO_COORDINATES":dict(sorted(geom_types.items())),
        "n_features_without_properties":no_props,
        "all_property_names_sorted":sorted(props_count),
        "n_features_with_property":dict(sorted(props_count.items())),
        "n_nonmissing_by_property_name":dict(sorted(nonmissing.items())),
        "candidate_sample_location_field_NAMES_ONLY":candidates,
        "geometry_or_feature_values_saved_or_printed":False,
        "frog_source_rows_accessed":False,
        "original_physical_site_wetland_identity_verified":False,
        "rc6_unchanged":True
    }

def synthetic_test():
    fixture={"type":"FeatureCollection","features":[
        {"type":"Feature","geometry":{"type":"Point","coordinates":[7,55]},
           "properties":{"SamplePoint":"PRIVATE","SiteID":"A","LocationName":None}},
        {"type":"Feature","geometry":{"type":"Point","coordinates":[9,52]},
           "properties":{"SamplePoint":"PRIVATE2","SiteID":"B","LocationName":"X"}},
    ]}
    x=schema(fixture)
    assert x["n_features"]==2
    assert x["n_nonmissing_by_property_name"]["LocationName"]==1
    assert "PRIVATE" not in json.dumps(x)
    assert "coordinates" not in json.dumps(x)
    for z in ({"features":[],"type":"FeatureCollection"}, {"type":"FeatureCollection","features":[{"type":"Bad"}]}):
        try:schema(z)
        except ValueError:pass
        else:raise AssertionError("invalid official dataset accepted")
    print("PASS: strictly government GeoJSON attribute keys only, never site labels or geometry")

def main():
    synthetic_test()
    result={"status":"SOURCE_UNAVAILABLE","resource_id":ID,"no_animal_or_location_output":True}
    try:
        meta=safe_request(API+"?"+urllib.parse.urlencode({"id":ID}))
        url=metadata(meta)
        if not url:raise ValueError("no original source download URL")
        result.update(schema(safe_request(url)))
    except urllib.error.HTTPError as exc:
        result.update(status="HTTP_UNAVAILABLE",http_status=exc.code)
    except (urllib.error.URLError,TimeoutError) as exc:
        result.update(status="NETWORK_UNAVAILABLE",error_type=type(exc).__name__)
    except (ValueError,TypeError,KeyError,json.JSONDecodeError) as exc:
        result.update(status="SCHEMA_FAILED_CLOSED",error_type=type(exc).__name__,
                      message=str(exc)[:150])
    p=Path("studies/climate_landscape/receipts/MDMS_GEOJSON_ATTRIBUTE_SCHEMA_V55.json")
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps(result,sort_keys=True))

if __name__=="__main__":
    main()
