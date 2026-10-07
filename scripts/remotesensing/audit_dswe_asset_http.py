#!/usr/bin/env python3
import json, urllib.request, urllib.error

URL="https://landsatlook.usgs.gov/level-3/collection02/DSWE/2010/CU/027/019/LE07_CU_027019_20100624_20210430_02_DSWE/LE07_CU_027019_20100624_20210430_02_INWAM.TIF"

out={}
for method in ("HEAD","GET"):
    req=urllib.request.Request(URL,method=method,headers={
        "User-Agent":"frogcs-dswe-http-audit/0.1",
        "Accept":"image/tiff,application/octet-stream,*/*",
        "Range":"bytes=0-1023" if method=="GET" else ""
    })
    try:
        with urllib.request.urlopen(req,timeout=60) as r:
            b=r.read(1024) if method=="GET" else b""
            out[method]={
              "status":getattr(r,"status",None),
              "final_url":r.geturl(),
              "content_type":r.headers.get("Content-Type"),
              "content_length":r.headers.get("Content-Length"),
              "content_range":r.headers.get("Content-Range"),
              "accept_ranges":r.headers.get("Accept-Ranges"),
              "first16_hex":b[:16].hex(),
              "first100_text":b[:100].decode("utf-8",errors="replace") if b else None
            }
    except urllib.error.HTTPError as e:
        b=e.read(1024)
        out[method]={
          "error":"HTTPError","code":e.code,"url":e.geturl(),
          "content_type":e.headers.get("Content-Type"),
          "first16_hex":b[:16].hex(),
          "first100_text":b[:100].decode("utf-8",errors="replace")
        }
print(json.dumps({"analysis":"dswe_asset_http_audit","asset_url":URL,"requests":out,"frog_data_used":False},indent=2))
