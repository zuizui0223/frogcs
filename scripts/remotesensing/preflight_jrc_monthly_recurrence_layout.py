#!/usr/bin/env python3
from __future__ import annotations
import html.parser, json, urllib.request
from pathlib import Path

BASE="https://jeodpp.jrc.ec.europa.eu/ftp/jrc-opendata/GSWE/MonthlyRecurrence/VER1-0/"
OUT=Path("remotesensing/JRC_MONTHLY_RECURRENCE_LAYOUT_PREFLIGHT_V0_1.json")

class P(html.parser.HTMLParser):
    def __init__(self): super().__init__(); self.href=[]
    def handle_starttag(self,tag,attrs):
        if tag.lower()=="a":
            d=dict(attrs)
            if "href" in d:self.href.append(d["href"])

def listing(url):
    req=urllib.request.Request(url,headers={"User-Agent":"frogcs-jrc-recurrence-preflight/0.1"})
    with urllib.request.urlopen(req,timeout=120) as r:
        txt=r.read().decode("utf-8",errors="replace")
    p=P(); p.feed(txt)
    return p.href

root=listing(BASE)
tiles_url=None
for h in root:
    if h.rstrip("/").endswith("tiles"):
        tiles_url=BASE+h
        break
if tiles_url is None:
    raise RuntimeError(f"tiles directory not found: {root[:30]}")
links=listing(tiles_url)

# Follow first directory, if layout is nested.
nested={}
dirs=[h for h in links if h.endswith("/") and h not in ("../","./")]
if dirs:
    first=tiles_url+dirs[0]
    try:
        nested={"url":first,"links":listing(first)[:40]}
    except Exception as e:
        nested={"url":first,"error":type(e).__name__+": "+str(e)}

out={
  "analysis":"jrc_monthly_recurrence_layout_preflight_v0_1",
  "base":BASE,
  "root_links":root[:40],
  "tiles_url":tiles_url,
  "tile_links_sample":links[:80],
  "nested_sample":nested,
  "raster_values_read":False,
  "frog_outcomes_read":False
}
OUT.parent.mkdir(exist_ok=True)
OUT.write_text(json.dumps(out,indent=2)+"\n")
print(json.dumps(out,indent=2))
