#!/usr/bin/env python3
import json, urllib.parse, urllib.request, time

URL="https://fwspublicservices.wim.usgs.gov/wetlandsmapservice/rest/services/Wetlands/MapServer/0/query"
PTS=[
  ("failed_MD_1",-75.84406,39.63913),
  ("failed_MD_2",-75.86057,39.60569),
  ("control_TN",-85.0,35.0),
]
out={"analysis":"nwi_point_distance_preflight_v0_1","points":[],"frog_endpoint_read":False}
for name,lon,lat in PTS:
    params={
      "where":"1=1",
      "geometry":f"{lon},{lat}",
      "geometryType":"esriGeometryPoint",
      "inSR":"4326",
      "spatialRel":"esriSpatialRelIntersects",
      "distance":"700",
      "units":"esriSRUnit_Meter",
      "outFields":"OBJECTID,ATTRIBUTE,WETLAND_TYPE",
      "returnGeometry":"true",
      "outSR":"5070",
      "resultRecordCount":"1000",
      "f":"json",
    }
    url=URL+"?"+urllib.parse.urlencode(params)
    last=None
    for i in range(5):
        try:
            req=urllib.request.Request(url,headers={"User-Agent":"frogcs-nwi-point-preflight/0.1"})
            with urllib.request.urlopen(req,timeout=90) as r:
                obj=json.loads(r.read().decode("utf-8"))
            if "error" in obj:
                raise RuntimeError(obj["error"])
            out["points"].append({
              "name":name,"feature_count":len(obj.get("features") or []),
              "exceeded":bool(obj.get("exceededTransferLimit",False))
            })
            break
        except Exception as e:
            last=e; time.sleep(2*(i+1))
    else:
        out["points"].append({"name":name,"error":type(last).__name__+": "+str(last)})
print(json.dumps(out,indent=2))
