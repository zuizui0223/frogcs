#!/usr/bin/env python3
import json, urllib.request, urllib.error

ITEM="609955c9d34ea221ce33c534"
META=f"https://www.sciencebase.gov/catalog/item/{ITEM}?format=json"

req=urllib.request.Request(META,headers={"User-Agent":"frogcs-dswemod-parent-zip/0.1","Accept":"application/json"})
with urllib.request.urlopen(req,timeout=60) as r:
    obj=json.loads(r.read().decode())

z=None
for f in obj.get("files") or []:
    if (f.get("name") or "")=="DSWEmod_ConterminousUS_2003_2019.zip":
        z=f;break
if z is None:
    raise RuntimeError("parent ZIP not found")
url=z.get("downloadUri") or z.get("url")
out={"analysis":"dswemod_parent_zip_range_preflight","url":url,"metadata_size":z.get("size"),"requests":{}}

for label,method,range_header in [
    ("head","HEAD",None),
    ("tail","GET","bytes=-65536"),
]:
    headers={"User-Agent":"frogcs-dswemod-parent-zip/0.1"}
    if range_header: headers["Range"]=range_header
    req=urllib.request.Request(url,method=method,headers=headers)
    try:
        with urllib.request.urlopen(req,timeout=120) as r:
            b=r.read(65536) if method=="GET" else b""
            out["requests"][label]={
              "status":getattr(r,"status",None),
              "content_length":r.headers.get("Content-Length"),
              "content_range":r.headers.get("Content-Range"),
              "accept_ranges":r.headers.get("Accept-Ranges"),
              "bytes_read":len(b),
              "zip_eocd_signature_present":b"PK\x05\x06" in b,
              "zip64_eocd_signature_present":b"PK\x06\x06" in b
            }
    except Exception as e:
        out["requests"][label]={"error":type(e).__name__+": "+str(e)}

print(json.dumps(out,indent=2))
