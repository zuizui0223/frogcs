#!/usr/bin/env python3
from __future__ import annotations
import json, urllib.parse, urllib.request
from pathlib import Path

OUT=Path("exploration/NWI_API_DIAGNOSTIC_RECEIPT_V0_1.json")
BASE="https://fwspublicservices.wim.usgs.gov/wetlandsmapservice/rest/services/Wetlands/MapServer/0/query"
ENV="-68.14,45.39,-68.12,45.41"
ENVJSON=json.dumps({"xmin":-68.14,"ymin":45.39,"xmax":-68.12,"ymax":45.41,"spatialReference":{"wkid":4326}},separators=(",",":"))

variants=[
  ("json_count_simple",{
    "f":"json","where":"1=1","geometry":ENV,"geometryType":"esriGeometryEnvelope",
    "inSR":"4326","spatialRel":"esriSpatialRelIntersects","returnCountOnly":"true"
  }),
  ("pjson_count_simple",{
    "f":"pjson","where":"1=1","geometry":ENV,"geometryType":"esriGeometryEnvelope",
    "inSR":"4326","spatialRel":"esriSpatialRelIntersects","returnCountOnly":"true"
  }),
  ("json_count_jsongeom",{
    "f":"json","where":"1=1","geometry":ENVJSON,"geometryType":"esriGeometryEnvelope",
    "inSR":"4326","spatialRel":"esriSpatialRelIntersects","returnCountOnly":"true"
  }),
  ("json_features_min",{
    "f":"json","where":"1=1","geometry":ENV,"geometryType":"esriGeometryEnvelope",
    "inSR":"4326","spatialRel":"esriSpatialRelIntersects",
    "outFields":"Wetlands.OBJECTID,Wetlands.ATTRIBUTE,Wetlands.WETLAND_TYPE,NWI_Wetland_Codes.WATER_REGIME,NWI_Wetland_Codes.WATER_REGIME_NAME",
    "returnGeometry":"true","outSR":"4326","resultRecordCount":"10"
  }),
  ("geojson_features_min",{
    "f":"geojson","where":"1=1","geometry":ENV,"geometryType":"esriGeometryEnvelope",
    "inSR":"4326","spatialRel":"esriSpatialRelIntersects",
    "outFields":"Wetlands.OBJECTID,Wetlands.ATTRIBUTE,Wetlands.WETLAND_TYPE,NWI_Wetland_Codes.WATER_REGIME,NWI_Wetland_Codes.WATER_REGIME_NAME",
    "returnGeometry":"true","outSR":"4326","resultRecordCount":"10"
  }),
  ("geojson_features_star",{
    "f":"geojson","where":"1=1","geometry":ENV,"geometryType":"esriGeometryEnvelope",
    "inSR":"4326","spatialRel":"esriSpatialRelIntersects",
    "outFields":"*","returnGeometry":"true","outSR":"4326","resultRecordCount":"10"
  }),
  ("json_features_unqualified",{
    "f":"json","where":"1=1","geometry":ENV,"geometryType":"esriGeometryEnvelope",
    "inSR":"4326","spatialRel":"esriSpatialRelIntersects",
    "outFields":"OBJECTID,ATTRIBUTE,WETLAND_TYPE,WATER_REGIME,WATER_REGIME_NAME",
    "returnGeometry":"false","resultRecordCount":"10"
  }),
]

def get(params):
    url=BASE+"?"+urllib.parse.urlencode(params)
    req=urllib.request.Request(url,headers={"User-Agent":"frogcs-nwi-api-diagnostic/0.1","Accept":"application/json,*/*"})
    try:
      with urllib.request.urlopen(req,timeout=60) as r:
        raw=r.read()
        code=r.status
    except urllib.error.HTTPError as e:
      raw=e.read(); code=e.code
    text=raw.decode("utf-8",errors="replace")
    try: obj=json.loads(text)
    except Exception: obj=None
    return {"status":code,"url":url,"bytes":len(raw),"json":obj,"text_head":text[:1000]}

def main():
    reports={}
    for name,p in variants:
      reports[name]=get(p)
      print(name,json.dumps({k:v for k,v in reports[name].items() if k not in ("url","json","text_head")}),flush=True)
      if isinstance(reports[name]["json"],dict):
        print(json.dumps(reports[name]["json"])[:500],flush=True)
    out={"analysis":"nwi_api_diagnostic_v0_1","variants":reports}
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
if __name__=="__main__": main()
