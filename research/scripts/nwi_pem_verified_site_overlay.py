#!/usr/bin/env python3
"""USFWS NWI PEM1A/C/F source-audited POINT → wetland polygon overlay.

Only accepts independently verified field wetland/recorder points. Historical
frogcs NAAMP site coordinate file has acknowledged errors, and public NPS
acoustics source has no latitude/longitude; DO NOT invent a PEM assignment.
Recorder position is not necessarily the breeding waterbody polygon.

Official layer (2026) https://fwspublicservices.wim.usgs.gov/
wetlandsmapservice/rest/services/Wetlands/MapServer/0
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import time
import urllib.parse
import urllib.request
from pathlib import Path

BASE="https://fwspublicservices.wim.usgs.gov/wetlandsmapservice/rest/services/Wetlands/MapServer/0"
FIELDS={"ATTRIBUTE","WETLAND_TYPE","ACRES"}
CODES={
    "PEM1A":"persistent_emergent_temporarily_flooded",
    "PEM1C":"persistent_emergent_seasonally_flooded",
    "PEM1F":"persistent_emergent_semipermanently_flooded",
    "PEM2A":"nonpersistent_emergent_temporarily_flooded",
    "PEM2C":"nonpersistent_emergent_seasonally_flooded",
    "PEM2F":"nonpersistent_emergent_semipermanently_flooded",
}
ALLOWED_ROLE={"independently_surveyed_wetland_point",
              "verified_recorder_location"}
SOURCES={"USGS_OFFICIAL_GEOMETRY_QA",
         "NPS_OFFICIAL_SITE_GIS",
         "FIELD_GPS_AND_INDEPENDENT_QA"}


def get_json(url):
    req=urllib.request.Request(url,headers={
        "User-Agent":"Frogcs-NWI-PEM-source-QA/0.1 (public field-site overlay)",
        "Accept":"application/json"})
    with urllib.request.urlopen(req,timeout=35) as f:
        return json.loads(f.read().decode("utf8"))


def decode(code):
    # Modifiers e.g. 'PEM1Ch' (impounded) should be retained, not silently
    # treated as identical to basic code for hydroperiod/canopy responses.
    c=str(code or "").strip().upper()
    if c in CODES:
        return {"raw_nwi_code":c,"subclass":CODES[c],
                "has_modifier":False,"exact":True}
    root=next((x for x in CODES if c.startswith(x)),None)
    return {"raw_nwi_code":c,
            "subclass":CODES[root] if root else None,
            "has_modifier":bool(root and c!=root),
            "exact":False}


def validate(row):
    req={"station_id","latitude","longitude","coordinate_source",
         "independently_verified","point_role","verified_date"}
    missing=req-set(row)
    if missing:
        raise ValueError("Missing necessary verified-source columns: "+str(sorted(missing)))
    name=row["station_id"].strip()
    if not name: raise ValueError("Empty wetland station ID")
    if row["coordinate_source"] not in SOURCES:
        raise ValueError("Unknown point provenance "+row["coordinate_source"])
    if str(row["independently_verified"]).strip().lower() not in {"true","1","yes"}:
        raise ValueError("Reject unverified coordinates from frogcs archived CSV")
    if row["point_role"] not in ALLOWED_ROLE:
        raise ValueError("Unknown point role: whether recorder or actual waterbody")
    try:
        lat=float(row["latitude"]);lon=float(row["longitude"])
        date=dt.date.fromisoformat(row["verified_date"])
    except (ValueError,TypeError) as e:
        raise ValueError("Invalid coordinates/date") from e
    if not (-90<=lat<=90 and -180<=lon<=180):
        raise ValueError("Invalid global latitude/longitude")
    if not (2000<=date.year<=2100):
        raise ValueError("Location mapping date not valid")
    return name,lon,lat


def query_wetlands(lon,lat):
    q={
        "f":"json",
        "geometry":f"{lon:.8f},{lat:.8f}",
        "geometryType":"esriGeometryPoint",
        "inSR":"4326",
        "spatialRel":"esriSpatialRelIntersects",
        "outFields":"ATTRIBUTE,WETLAND_TYPE,ACRES,GlobalID",
        "returnGeometry":"false",
        "where":"1=1"
    }
    target=BASE+"/query?"+urllib.parse.urlencode(q)
    v=get_json(target)
    if "error" in v:
        raise RuntimeError("NWI point query error "+str(v["error"]))
    features=v.get("features")
    if not isinstance(features,list):
        raise RuntimeError("Unexpected wetland polygon query response")
    return [f.get("attributes",{}) for f in features]


def layer_audit():
    layer=get_json(BASE+"?f=pjson")
    if "error" in layer:
        raise RuntimeError("Official FWS layer not available")
    cols={c.get("name") for c in layer.get("fields",[])}
    if not FIELDS.issubset(cols) or layer.get("geometryType")!="esriGeometryPolygon":
        raise RuntimeError("Official NWI schema mismatch")
    return {
        "official_service":BASE,"layer":layer.get("name"),
        "fields":sorted(cols),"schema_ok":True,
        "this_is_not_a_site_join":True,
        "mapping_version_volatile":True,
    }


def analyze(inputcsv,out):
    metadata=layer_audit()
    source=list(csv.DictReader(Path(inputcsv).open(encoding="utf8",newline="")))
    if not source or len(source)>500:
        raise ValueError("Require 1..500 independently verified points")
    ids=set()
    output=[]
    for i,row in enumerate(source):
        name,lon,lat=validate(row)
        if name in ids:
            raise ValueError("Duplicate station id")
        ids.add(name)
        polygons=query_wetlands(lon,lat)
        quality="NO_INTERSECTING_MAPPED_NWI_POLYGON"
        code=None
        if len(polygons)==1:
            code=decode(polygons[0].get("ATTRIBUTE"))
            quality="UNIQUE_MAPPED_POLYGON_INTERSECTION"
        elif len(polygons)>1:
            quality="MULTIPLE_OVERLAPPING_NWI_POLYGONS"
        output.append({
            "station_id":name,
            "n_nwi_intersecting_polygons":len(polygons),
            "geometry_quality":quality,
            "nwi_attribute":code["raw_nwi_code"] if code else "",
            "nwi_plain_cowardin_subclass":code["subclass"] if code else "",
            "nwi_exact_pem_code":bool(code and code["exact"]),
            "nwi_has_modifier":bool(code and code["has_modifier"]),
            "original_source":row["coordinate_source"],
            "surveyed_location_role":row["point_role"],
            "interpretation":"SITE_OF_MEASURED_POINT_NOT_PROVEN_AUDIO_SOURCE_WATERBODY",
        })
        if i<len(source)-1:time.sleep(.06)
    dest=Path(out);dest.mkdir(parents=True,exist_ok=True)
    with (dest/"wetland_point_intersects.csv").open("w",newline="",encoding="utf8") as f:
        writer=csv.DictWriter(f,fieldnames=list(output[0]))
        writer.writeheader();writer.writerows(output)
    report={
        "license":"USFWS NWI official public-source mapped Cowardin wetland classification",
        "source":metadata,
        "n_supplied_independently_verified_points":len(source),
        "unique_intersected_single_polygon":sum(x["geometry_quality"]=="UNIQUE_MAPPED_POLYGON_INTERSECTION" for x in output),
        "nwi_PEM1A_C_F_exact":sum(x["nwi_attribute"] in ("PEM1A","PEM1C","PEM1F") for x in output),
        "warnings":[
            "An NWI polygon at exact recorder coordinates is not necessarily the body of water generating frog calls.",
            "Broad Hydroperiod categories in NPS acoustic CSV and Cowardin PEM code are different variables.",
            "NAAMP USGS source coordinates include source errors, may not be used until independent repair and pond affiliation.",
            "NWI polygons have heterogeneous mapping dates and are not date-specific flooded-water observations.",
            "PEM1 persistent wetland class does not measure precise emergent stem height, density or submerged structure.",
            "No live tadpole-odonate-salamander interactions or predator phase inferred from NWI class.",
        ]}
    (dest/"source_quality.json").write_text(
        json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    print("NWI_PEM_SITE_MATCH_ORIGINAL_VERIFIED_SOURCE_ONLY")
    print(json.dumps(report,ensure_ascii=False,indent=2))


def selftest():
    assert decode("PEM1A")["subclass"].endswith("temporarily_flooded")
    assert decode("PEM1C")["subclass"].endswith("seasonally_flooded")
    assert decode("PEM1F")["subclass"].endswith("semipermanently_flooded")
    assert decode("PEM1Fx")["has_modifier"]
    assert not decode("PEM1Fx")["exact"]
    assert decode("PUBH")["subclass"] is None
    test=dict(station_id="x",latitude="43",longitude="-89",
              coordinate_source="FIELD_GPS_AND_INDEPENDENT_QA",
              independently_verified="true",
              point_role="independently_surveyed_wetland_point",
              verified_date="2025-09-01")
    assert validate(test)==("x",-89.,43.)
    test["independently_verified"]="false"
    try:validate(test)
    except ValueError:pass
    else:raise AssertionError("Unverified source accepted")
    print("NWI_PEM_CODE_SOURCE_AND_COORDINATE_QA_PASS")


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--source",help="verified site/actual wetland points only")
    p.add_argument("--out",default="research/results/nwi_pem_site_join")
    p.add_argument("--self-test",action="store_true")
    p.add_argument("--schema-audit",action="store_true")
    a=p.parse_args()
    if a.self_test:selftest()
    elif a.schema_audit:
        print(json.dumps(layer_audit(),ensure_ascii=False,indent=2))
    elif a.source:analyze(a.source,a.out)
    else:p.error("--self-test / --schema-audit or verified --source CSV required")
