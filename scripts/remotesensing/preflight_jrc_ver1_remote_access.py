#!/usr/bin/env python3
from __future__ import annotations
import html.parser, json, re, urllib.request
from pathlib import Path

DIR="https://jeodpp.jrc.ec.europa.eu/ftp/jrc-opendata/GSWE/MonthlyHistory/VER1-0/tiles/2001/2001_05/"
OUT=Path("remotesensing/JRC_VER1_REMOTE_ACCESS_PREFLIGHT_V0_1.json")

class P(html.parser.HTMLParser):
    def __init__(self):
        super().__init__(); self.href=[]
    def handle_starttag(self,tag,attrs):
        if tag.lower()=="a":
            d=dict(attrs)
            if "href" in d:self.href.append(d["href"])

req=urllib.request.Request(DIR,headers={"User-Agent":"frogcs-jrc-access-preflight/0.1"})
with urllib.request.urlopen(req,timeout=120) as r:
    txt=r.read().decode("utf-8",errors="replace")
p=P(); p.feed(txt)
tifs=[h for h in p.href if h.lower().endswith(".tif")]
sample=tifs[0] if tifs else None
head={}
range_test={}
if sample:
    url=DIR+sample
    req=urllib.request.Request(url,method="HEAD",headers={"User-Agent":"frogcs-jrc-access-preflight/0.1"})
    with urllib.request.urlopen(req,timeout=120) as r:
        head={k.lower():v for k,v in r.headers.items()}
    req=urllib.request.Request(url,headers={
        "User-Agent":"frogcs-jrc-access-preflight/0.1",
        "Range":"bytes=0-65535"
    })
    with urllib.request.urlopen(req,timeout=120) as r:
        b=r.read()
        range_test={
            "status":getattr(r,"status",None),
            "bytes_read":len(b),
            "content_range":r.headers.get("Content-Range"),
            "accept_ranges":r.headers.get("Accept-Ranges"),
            "content_type":r.headers.get("Content-Type"),
            "starts_with_tiff_signature":bool(b[:4] in (b"II*\x00",b"MM\x00*"))
        }

out={
    "analysis":"jrc_ver1_remote_access_preflight_v0_1",
    "directory":DIR,
    "tif_count":len(tifs),
    "sample_filenames":tifs[:10],
    "sample":sample,
    "head":{
        "content_length":head.get("content-length"),
        "accept_ranges":head.get("accept-ranges"),
        "content_type":head.get("content-type"),
        "etag":head.get("etag")
    },
    "range_test":range_test,
    "raster_values_read":False
}
OUT.parent.mkdir(exist_ok=True)
OUT.write_text(json.dumps(out,indent=2)+"\n",encoding="utf-8")
print(json.dumps(out,indent=2))
