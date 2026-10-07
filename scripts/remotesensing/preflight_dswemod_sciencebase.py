#!/usr/bin/env python3
import json, urllib.request

PARENT="609955c9d34ea221ce33c534"
urls=[
  f"https://www.sciencebase.gov/catalog/items?parentId={PARENT}&format=json&max=100",
  f"https://www.sciencebase.gov/catalog/item/{PARENT}?format=json"
]
out={}
for u in urls:
  req=urllib.request.Request(u,headers={"User-Agent":"frogcs-dswemod-preflight/0.1","Accept":"application/json"})
  try:
    with urllib.request.urlopen(req,timeout=60) as r:
      obj=json.loads(r.read().decode("utf-8"))
    # Keep metadata only; no raster values.
    if "items" in obj:
      out[u]={
        "type":"children",
        "count":len(obj.get("items") or []),
        "items":[
          {"id":x.get("id"),"title":x.get("title"),
           "files":[{"name":f.get("name"),"size":f.get("size"),"contentType":f.get("contentType"),
                     "downloadUri":f.get("downloadUri")} for f in (x.get("files") or [])]}
          for x in (obj.get("items") or [])
        ]
      }
    else:
      out[u]={
        "type":"item","id":obj.get("id"),"title":obj.get("title"),
        "hasChildren":obj.get("hasChildren"),
        "files":[{"name":f.get("name"),"size":f.get("size"),"contentType":f.get("contentType"),
                  "downloadUri":f.get("downloadUri")} for f in (obj.get("files") or [])]
      }
  except Exception as e:
    out[u]={"error":type(e).__name__+": "+str(e)}
print(json.dumps({"analysis":"dswemod_sciencebase_preflight","parent":PARENT,"probes":out,"raster_values_read":False,"frog_data_used":False},indent=2))
