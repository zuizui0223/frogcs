#!/usr/bin/env python3
from __future__ import annotations
import hashlib, importlib.util, json, math, os, time
from contextlib import ExitStack
from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
import planetary_computer
import rasterio
from pyproj import Transformer
from pystac_client import Client
from rasterio.windows import Window

ROOT=Path(__file__).resolve().parents[2]
EXP=ROOT/"exploration"
COORDS=Path(os.environ["NAAMP_LST_COORD_ASSIGNMENTS"])
OUTDIR=ROOT/"remotesensing"/"mod11a1_shards"
IDX=int(os.environ.get("MOD11A1_SHARD_INDEX","0"))
COUNT=int(os.environ.get("MOD11A1_SHARD_COUNT","16"))

API="https://planetarycomputer.microsoft.com/api/stac/v1"
COL="modis-11A1-061"
REQ_ASSETS=("LST_Night_1km","QC_Night","Night_view_time")

def loadmod(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);assert s.loader;s.loader.exec_module(m);return m
flex=loadmod("flex",EXP/"run_naamp_flexible_common_environment_null.py")
mem=flex.mem

def stac_items(client,bbox,d):
    last=None
    ds=d.isoformat()
    for k in range(5):
        try:
            items=list(client.search(
              collections=[COL],bbox=bbox,
              datetime=f"{ds}T00:00:00Z/{ds}T23:59:59Z"
            ).items())
            items=[x for x in items if str(x.id).startswith("MOD11A1")]
            return sorted(items,key=lambda x:str(x.id))
        except Exception as e:
            last=e;time.sleep(2*(k+1))
    raise RuntimeError(f"STAC search failed {d}: {last}")

def read_common_date(client,d,siteids,coords):
    lats=[coords[s][0] for s in siteids];lons=[coords[s][1] for s in siteids]
    bbox=[min(lons)-.002,min(lats)-.002,max(lons)+.002,max(lats)+.002]
    items=stac_items(client,bbox,d)
    if not items:return None

    opened=[]
    with ExitStack() as stack:
        for raw in items:
            item=planetary_computer.sign(raw)
            if any(k not in item.assets for k in REQ_ASSETS):
                continue
            try:
                dsL=stack.enter_context(rasterio.open(item.assets["LST_Night_1km"].href))
                dsQ=stack.enter_context(rasterio.open(item.assets["QC_Night"].href))
                dsT=stack.enter_context(rasterio.open(item.assets["Night_view_time"].href))
            except Exception:
                continue
            if dsL.crs is None or dsQ.crs!=dsL.crs or dsT.crs!=dsL.crs:
                continue
            opened.append((str(item.id),dsL,dsQ,dsT,Transformer.from_crs("EPSG:4326",dsL.crs,always_xy=True)))

        vals={}
        for sid in siteids:
            lat,lon=coords[sid]
            candidates=[]
            for itemid,dsL,dsQ,dsT,tf in opened:
                x,y=tf.transform(lon,lat)
                row,col=dsL.index(x,y)
                if 0<=row<dsL.height and 0<=col<dsL.width:
                    candidates.append((itemid,dsL,dsQ,dsT,row,col))
            if not candidates:
                return None
            candidates.sort(key=lambda z:z[0])
            itemid,dsL,dsQ,dsT,row,col=candidates[0]
            dn=int(dsL.read(1,window=Window(col,row,1,1))[0,0])
            q=int(dsQ.read(1,window=Window(col,row,1,1))[0,0])
            vt=int(dsT.read(1,window=Window(col,row,1,1))[0,0])
            mandatory=q & 0b11
            err=(q>>6)&0b11
            valid=bool(dn>0 and mandatory==0 and err==0)
            if not valid:
                return None
            vals[sid]={
              "lst_kelvin":float(dn*.02),
              "view_local_hour":float(vt*.1) if vt>0 else None,
              "qc":q,"item_id":itemid,
              "pixel_key":f"{itemid}:{row}:{col}"
            }
        return vals

coords_df=pd.read_csv(COORDS,dtype={"SiteID":str,"RouteNumber":str})
need={"SiteID","lat","lon"}
if not need.issubset(coords_df.columns):
    raise RuntimeError(f"coordinate artifact missing {sorted(need-set(coords_df.columns))}")
coords_df=coords_df.drop_duplicates("SiteID")
coords={str(r.SiteID):(float(r.lat),float(r.lon)) for r in coords_df.itertuples(index=False)}

raw,runs,psub,dsub,hsub,pools,sampled,ss=flex.prepare_subset()
eligible=set(runs.RunID.astype(str));site=mem.site_map(raw,eligible)
runrow={str(r.RunID):r for r in runs.itertuples(index=False)}
specs={}
for p,dct in zip(psub.itertuples(index=False),dsub):
    ids=mem.focal_siteids(p,dct,site)
    if ids is None or len(ids)!=10 or any(str(s) not in coords for s in ids):
        continue
    for rid in (str(p.wet_RunID),str(p.dry_RunID)):
        rr=runrow.get(rid)
        if rr is None:continue
        sp={
          "RunID":rid,"route_cluster":str(rr.route_cluster),"RouteNumber":str(rr.RouteNumber),
          "State":str(rr.State),"RunNumber":str(rr.RunNumber),
          "year":int(rr.SurveyYear),"doy":int(rr.doy),"siteids":[str(s) for s in ids]
        }
        if rid in specs and specs[rid]["siteids"]!=sp["siteids"]:
            raise RuntimeError(f"RunID SiteID drift {rid}")
        specs[rid]=sp

assigned=[
 s for s in specs.values()
 if int(hashlib.sha256(s["route_cluster"].encode()).hexdigest()[:8],16)%COUNT==IDX
]
assigned=sorted(assigned,key=lambda z:(z["route_cluster"],z["year"],z["doy"],z["RunID"]))

client=Client.open(API)
rows=[]
for n,sp in enumerate(assigned,1):
    survey=date(sp["year"],1,1)+timedelta(days=sp["doy"]-1)
    result={}
    for lag in (0,1,2):
        d=survey-timedelta(days=lag)
        v=read_common_date(client,d,sp["siteids"],coords)
        if v is not None:
            result[lag]=(d,v)
        if lag==0:
            # Rule A is only same nominal date.
            pass

    Aval=result.get(0)
    Bsel=None
    for lag in (0,1,2):
        if lag in result:
            Bsel=(lag,*result[lag]);break

    A_pixels=len(set(x["pixel_key"] for x in Aval[1].values())) if Aval else 0
    B_pixels=len(set(x["pixel_key"] for x in Bsel[2].values())) if Bsel else 0

    for sid in sp["siteids"]:
        lat,lon=coords[sid]
        rec={
          "RunID":sp["RunID"],"SiteID":sid,"route_cluster":sp["route_cluster"],
          "RouteNumber":sp["RouteNumber"],"State":sp["State"],"RunNumber":sp["RunNumber"],
          "survey_date":survey.isoformat(),"lat":lat,"lon":lon,
          "A_complete":bool(Aval is not None),"A_date":Aval[0].isoformat() if Aval else None,
          "A_lst_kelvin":Aval[1][sid]["lst_kelvin"] if Aval else None,
          "A_view_local_hour":Aval[1][sid]["view_local_hour"] if Aval else None,
          "A_item_id":Aval[1][sid]["item_id"] if Aval else None,
          "A_pixel_key":Aval[1][sid]["pixel_key"] if Aval else None,
          "A_unique_pixels_run":A_pixels,
          "B_complete":bool(Bsel is not None),"B_lag_days":int(Bsel[0]) if Bsel else None,
          "B_date":Bsel[1].isoformat() if Bsel else None,
          "B_lst_kelvin":Bsel[2][sid]["lst_kelvin"] if Bsel else None,
          "B_view_local_hour":Bsel[2][sid]["view_local_hour"] if Bsel else None,
          "B_item_id":Bsel[2][sid]["item_id"] if Bsel else None,
          "B_pixel_key":Bsel[2][sid]["pixel_key"] if Bsel else None,
          "B_unique_pixels_run":B_pixels
        }
        rows.append(rec)
    if n==1 or n%10==0 or n==len(assigned):
        print(json.dumps({"shard":IDX,"run":n,"runs":len(assigned),"RunID":sp["RunID"],
                          "A":bool(Aval),"B":bool(Bsel)}),flush=True)

OUTDIR.mkdir(parents=True,exist_ok=True)
csvout=OUTDIR/f"MOD11A1_NIGHT_LST_SHARD_{IDX:02d}.csv"
jsonout=OUTDIR/f"MOD11A1_NIGHT_LST_SHARD_{IDX:02d}.json"
df=pd.DataFrame(rows);df.to_csv(csvout,index=False,float_format="%.8g")
receipt={
 "analysis":"naamp_mod11a1_night_lst_shard_v0_1",
 "spec":"revision/NAAMP_MODIS_NIGHT_LST_PROSPECTIVE_SPEC_V0_1.md",
 "shard_index":IDX,"shard_count":COUNT,
 "runs":len(assigned),"rows":len(df),
 "A_complete_runs":int(df.loc[df.A_complete==True,"RunID"].nunique()) if len(df) else 0,
 "B_complete_runs":int(df.loc[df.B_complete==True,"RunID"].nunique()) if len(df) else 0,
 "frog_endpoint_calculated":False
}
jsonout.write_text(json.dumps(receipt,indent=2)+"\n")
print(json.dumps(receipt,indent=2))
