#!/usr/bin/env python3
from __future__ import annotations
import json
from datetime import datetime, timezone

import numpy as np
import planetary_computer
import rasterio
from pyproj import Transformer
from pystac_client import Client
from rasterio.windows import Window

API="https://planetarycomputer.microsoft.com/api/stac/v1"
COL="modis-11A1-061"

TESTS=[
  {"name":"Illinois","lon":-90.0,"lat":40.0,"date":"2010-05-15"},
  {"name":"NorthCarolina","lon":-79.0,"lat":35.5,"date":"2012-04-20"},
]

client=Client.open(API)
out={"analysis":"mod11a1_night_lst_pc_smoke_v0_1","collection":COL,"frog_data_used":False,"tests":[]}

for t in TESTS:
    d=t["date"]
    items=list(client.search(
        collections=[COL],
        bbox=[t["lon"]-0.01,t["lat"]-0.01,t["lon"]+0.01,t["lat"]+0.01],
        datetime=f"{d}T00:00:00Z/{d}T23:59:59Z",
        query={"platform":{"eq":"terra"}}
    ).items())
    if not items:
        raise RuntimeError(f"no Terra MOD11A1 item for {t}")
    # A point should map to one tile; fail if ambiguous rather than selecting by value.
    terra=[x for x in items if str(x.id).startswith("MOD11A1")]
    if len(terra)!=1:
        raise RuntimeError(f"expected one Terra tile, got {[x.id for x in items]}")
    item=planetary_computer.sign(terra[0])
    req_assets=["LST_Night_1km","QC_Night","Night_view_time"]
    if any(k not in item.assets for k in req_assets):
        raise RuntimeError(f"missing assets {item.id}: {sorted(item.assets)}")
    rec={**t,"item_id":item.id,"assets":{}}
    for key in req_assets:
        href=item.assets[key].href
        with rasterio.open(href) as ds:
            tf=Transformer.from_crs("EPSG:4326",ds.crs,always_xy=True)
            x,y=tf.transform(t["lon"],t["lat"])
            row,col=ds.index(x,y)
            if not (0<=row<ds.height and 0<=col<ds.width):
                raise RuntimeError(f"point out of tile for {item.id} {key}")
            val=int(ds.read(1,window=Window(col,row,1,1))[0,0])
            rec["assets"][key]={
              "value":val,"crs":str(ds.crs),
              "shape":[ds.height,ds.width],
              "transform":[float(ds.transform.a),float(ds.transform.e),float(ds.transform.c),float(ds.transform.f)]
            }
    q=rec["assets"]["QC_Night"]["value"]
    mandatory=q & 0b11
    err=(q>>6)&0b11
    dn=rec["assets"]["LST_Night_1km"]["value"]
    vt=rec["assets"]["Night_view_time"]["value"]
    rec["decoded"]={
      "mandatory_qa_bits":int(mandatory),
      "lst_error_bits":int(err),
      "valid_under_frozen_qc":bool(dn>0 and mandatory==0 and err==0),
      "lst_kelvin":float(dn*0.02) if dn>0 else None,
      "night_view_local_solar_hour":float(vt*0.1) if vt>0 else None
    }
    out["tests"].append(rec)

print(json.dumps(out,indent=2))
