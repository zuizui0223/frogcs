#!/usr/bin/env python3
import json, urllib.request, urllib.error

API="https://landsatlook.usgs.gov/stac-server/search"
BODY={
  "collections":["landsat-c2l3-dswe"],
  "bbox":[-85.1,34.9,-84.9,35.1],
  "datetime":"2010-05-01T00:00:00Z/2010-06-30T23:59:59Z",
  "limit":10
}
req=urllib.request.Request(
    API,
    data=json.dumps(BODY).encode(),
    headers={"Content-Type":"application/json","Accept":"application/geo+json","User-Agent":"frogcs-dswe-preflight/0.1"},
    method="POST"
)
with urllib.request.urlopen(req,timeout=60) as r:
    obj=json.loads(r.read().decode())

items=[]
for f in obj.get("features",[])[:10]:
    assets={}
    for k,a in (f.get("assets") or {}).items():
        href=a.get("href")
        assets[k]={
          "href_scheme":href.split(":",1)[0] if isinstance(href,str) and ":" in href else None,
          "roles":a.get("roles"),
          "type":a.get("type"),
          "title":a.get("title"),
          "href":href
        }
    items.append({
      "id":f.get("id"),
      "datetime":(f.get("properties") or {}).get("datetime"),
      "platform":(f.get("properties") or {}).get("platform"),
      "asset_keys":sorted(assets),
      "assets":assets
    })

out={
  "analysis":"landsat_c2l3_dswe_stac_preflight_v0_1",
  "query":BODY,
  "matched":obj.get("context",{}).get("matched"),
  "returned":len(items),
  "items":items,
  "frog_data_used":False,
  "naamp_coordinates_used":False
}
print(json.dumps(out,indent=2))
