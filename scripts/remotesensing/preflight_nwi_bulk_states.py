#!/usr/bin/env python3
import json, urllib.request

states=["DE","IN","MD","MS","NJ","NC","PA","TX","VA","WV"]
base="https://documentst.ecosphere.fws.gov/wetlands/data/State-Downloads/{st}_geopackage_wetlands.zip"
out={"analysis":"nwi_bulk_state_preflight_v0_1","states":{},"frog_endpoint_read":False}
for st in states:
    url=base.format(st=st)
    try:
        req=urllib.request.Request(url,method="HEAD",headers={"User-Agent":"frogcs-nwi-bulk-preflight/0.1"})
        with urllib.request.urlopen(req,timeout=60) as r:
            out["states"][st]={
              "status":getattr(r,"status",None),
              "content_length":int(r.headers.get("Content-Length")) if r.headers.get("Content-Length") else None,
              "content_type":r.headers.get("Content-Type"),
              "url":r.geturl()
            }
    except Exception as e:
        out["states"][st]={"error":type(e).__name__+": "+str(e),"url":url}
print(json.dumps(out,indent=2,sort_keys=True))
