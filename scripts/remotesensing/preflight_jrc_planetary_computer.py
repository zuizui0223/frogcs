#!/usr/bin/env python3
from __future__ import annotations
import json, urllib.request
from pathlib import Path

BASE="https://planetarycomputer.microsoft.com/api/stac/v1"
OUT=Path("remotesensing/JRC_PLANETARY_COMPUTER_STAC_PREFLIGHT_V0_1.json")

def get(url):
    req=urllib.request.Request(url,headers={"User-Agent":"frogcs-hydrology-stac-preflight/0.1","Accept":"application/json"})
    with urllib.request.urlopen(req,timeout=120) as r:
        return json.loads(r.read().decode("utf-8"))

cols=get(BASE+"/collections")
matches=[]
for c in cols.get("collections",[]):
    blob=" ".join([
        str(c.get("id","")),str(c.get("title","")),str(c.get("description",""))
    ]).lower()
    if "jrc" in blob or ("surface water" in blob and "global" in blob):
        matches.append({
            "id":c.get("id"),
            "title":c.get("title"),
            "description":c.get("description"),
            "extent":c.get("extent"),
            "item_assets":sorted((c.get("item_assets") or {}).keys()),
            "summaries":c.get("summaries")
        })

# Inspect a few items for every matching collection without downloading raster values.
for m in matches:
    try:
        d=get(BASE+f"/collections/{m['id']}/items?limit=3")
        m["sample_items"]=[
            {
                "id":f.get("id"),
                "datetime":(f.get("properties") or {}).get("datetime"),
                "start_datetime":(f.get("properties") or {}).get("start_datetime"),
                "end_datetime":(f.get("properties") or {}).get("end_datetime"),
                "asset_keys":sorted((f.get("assets") or {}).keys())
            }
            for f in d.get("features",[])
        ]
    except Exception as e:
        m["sample_item_error"]=type(e).__name__+": "+str(e)[:300]

out={
    "analysis":"jrc_planetary_computer_stac_preflight_v0_1",
    "stac_base":BASE,
    "matching_collections":matches,
    "raster_values_read":False
}
OUT.parent.mkdir(exist_ok=True)
OUT.write_text(json.dumps(out,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
print(json.dumps(out,indent=2,ensure_ascii=False))
