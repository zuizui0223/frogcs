#!/usr/bin/env python3
import csv, io, json, urllib.parse, urllib.request

# One previously failed route from the response-blind audit.
ROUTE="460107"
COORD_URL="https://www.sciencebase.gov/catalog/file/get/583dc314e4b0d1899f9dea8d?f=__disk__77%2F22%2F7e%2F77227ec46ac1c01592cd7d158d442cd8343a7536"
NWI="https://fwspublicservices.wim.usgs.gov/wetlandsmapservice/rest/services/Wetlands/MapServer/0/query"

req=urllib.request.Request(COORD_URL,headers={"User-Agent":"frogcs-nwi-multipoint-preflight/0.1"})
with urllib.request.urlopen(req,timeout=120) as r:
    b=r.read()
pts=[]
for row in csv.DictReader(io.StringIO(b.decode("utf-8-sig"))):
    if str(row.get("RouteNumber") or "").strip()==ROUTE:
        pts.append([float(row["lon"]),float(row["lat"])])
if not pts: raise RuntimeError("route coords not found")

params={
 "where":"1=1",
 "geometry":json.dumps({"points":pts},separators=(",",":")),
 "geometryType":"esriGeometryMultipoint",
 "inSR":"4326",
 "spatialRel":"esriSpatialRelIntersects",
 "distance":"700",
 "units":"esriSRUnit_Meter",
 "outFields":"OBJECTID,ATTRIBUTE,WETLAND_TYPE",
 "returnGeometry":"true",
 "outSR":"5070",
 "resultRecordCount":"1000",
 "f":"json"
}
url=NWI+"?"+urllib.parse.urlencode(params)
req=urllib.request.Request(url,headers={"User-Agent":"frogcs-nwi-multipoint-preflight/0.1"})
with urllib.request.urlopen(req,timeout=120) as r:
    obj=json.loads(r.read().decode("utf-8"))
if "error" in obj: raise RuntimeError(json.dumps(obj["error"]))
out={
 "analysis":"nwi_failed_route_multipoint_preflight_v0_1",
 "route":ROUTE,"points":len(pts),
 "feature_count":len(obj.get("features") or []),
 "exceeded":bool(obj.get("exceededTransferLimit",False)),
 "frog_endpoint_read":False
}
print(json.dumps(out,indent=2))
