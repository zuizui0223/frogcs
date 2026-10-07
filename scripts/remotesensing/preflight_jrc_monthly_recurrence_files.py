#!/usr/bin/env python3
from __future__ import annotations
import html.parser,json,urllib.request
from pathlib import Path

BASE="https://jeodpp.jrc.ec.europa.eu/ftp/jrc-opendata/GSWE/MonthlyRecurrence/VER1-0/tiles/"
OUT=Path("remotesensing/JRC_MONTHLY_RECURRENCE_FILE_PREFLIGHT_V0_1.json")

class P(html.parser.HTMLParser):
    def __init__(self):super().__init__();self.href=[]
    def handle_starttag(self,tag,attrs):
        if tag.lower()=="a":
            d=dict(attrs)
            if "href" in d:self.href.append(d["href"])

def ls(url):
    req=urllib.request.Request(url,headers={"User-Agent":"frogcs-jrc-recurrence-file-preflight/0.1"})
    with urllib.request.urlopen(req,timeout=120) as r:
        txt=r.read().decode("utf-8",errors="replace")
    p=P();p.feed(txt);return p.href

out={"analysis":"jrc_monthly_recurrence_file_preflight_v0_1","months":{},"raster_values_read":False}
for m in [1,5,6,10]:
    u=BASE+f"monthlyRecurrence{m}/"
    links=ls(u)
    tifs=[x for x in links if x.lower().endswith(".tif")]
    out["months"][str(m)]={"url":u,"tif_count":len(tifs),"sample":tifs[:8]}
OUT.parent.mkdir(exist_ok=True)
OUT.write_text(json.dumps(out,indent=2)+"\n")
print(json.dumps(out,indent=2))
