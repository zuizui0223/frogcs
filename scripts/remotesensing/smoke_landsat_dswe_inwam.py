#!/usr/bin/env python3
from __future__ import annotations

import json, math, urllib.request
import numpy as np
import rasterio
from rasterio.warp import transform

API="https://landsatlook.usgs.gov/stac-server/search"
PTS=[
  {"name":"Everglades","lat":25.55,"lon":-80.65,"date":"2010-06-15"},
  {"name":"Tennessee_inland","lat":35.0,"lon":-85.0,"date":"2010-06-15"}
]
RADIUS=250.0

def search(p):
    body={
      "collections":["landsat-c2l3-dswe"],
      "bbox":[p["lon"]-.03,p["lat"]-.03,p["lon"]+.03,p["lat"]+.03],
      "datetime":"2010-06-01T00:00:00Z/2010-06-30T23:59:59Z",
      "limit":100
    }
    req=urllib.request.Request(API,data=json.dumps(body).encode(),method="POST",
        headers={"Content-Type":"application/json","Accept":"application/geo+json","User-Agent":"frogcs-dswe-inwam-smoke/0.1"})
    with urllib.request.urlopen(req,timeout=60) as r:
        return json.loads(r.read().decode()).get("features") or []

def buffer_values(href,lat,lon):
    with rasterio.Env(GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR",CPL_VSIL_CURL_ALLOWED_EXTENSIONS=".TIF,.tif",GDAL_HTTP_MULTIRANGE="YES"):
      with rasterio.open(href) as ds:
        xs,ys=transform("EPSG:4326",ds.crs,[lon],[lat])
        x,y=float(xs[0]),float(ys[0])
        # Pixel window around 250 m, then geodesic-equivalent Euclidean mask in projected ARD CRS.
        row,col=ds.index(x,y)
        pix=max(abs(ds.transform.a),abs(ds.transform.e))
        n=int(math.ceil(RADIUS/pix))+2
        r0=max(0,row-n); r1=min(ds.height,row+n+1)
        c0=max(0,col-n); c1=min(ds.width,col+n+1)
        a=ds.read(1,window=((r0,r1),(c0,c1)))
        rr,cc=np.meshgrid(np.arange(r0,r1),np.arange(c0,c1),indexing="ij")
        xx,yy=rasterio.transform.xy(ds.transform,rr,cc,offset="center")
        xx=np.asarray(xx,float); yy=np.asarray(yy,float)
        mask=(xx-x)**2+(yy-y)**2<=RADIUS**2
        v=a[mask]
        return {
          "crs":str(ds.crs),"pixel_size":float(pix),"n_buffer_pixels":int(len(v)),
          "unique_counts":{str(int(k)):int(n) for k,n in zip(*np.unique(v,return_counts=True))},
          "valid_0_4":int(np.isin(v,[0,1,2,3,4]).sum()),
          "positive_123":int(np.isin(v,[1,2,3]).sum()),
          "positive_1234":int(np.isin(v,[1,2,3,4]).sum())
        }

out=[]
for p in PTS:
    feats=search(p)
    chosen=None
    for f in feats:
        bb=f.get("bbox") or []
        if len(bb)>=4 and bb[0]<=p["lon"]<=bb[2] and bb[1]<=p["lat"]<=bb[3] and "inwam" in (f.get("assets") or {}):
            chosen=f;break
    if chosen is None:
        out.append({**p,"status":"no_covering_item","returned":len(feats)})
        continue
    href=chosen["assets"]["inwam"]["href"]
    z=buffer_values(href,p["lat"],p["lon"])
    out.append({**p,"status":"read","item_id":chosen.get("id"),"href":href,**z})

print(json.dumps({"analysis":"landsat_dswe_inwam_cog_smoke_v0_1","points":out,"frog_data_used":False,"naamp_coordinates_used":False},indent=2))
