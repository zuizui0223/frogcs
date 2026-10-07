from __future__ import annotations

import math
import time
from contextlib import ExitStack
from datetime import datetime, timedelta

import planetary_computer
import rasterio
from pyproj import Transformer
from rasterio.windows import Window

REQ_ASSETS=("LST_Night_1km","QC_Night","Night_view_time")


def item_utc_date(item):
    dt=getattr(item,"datetime",None)
    if dt is None:
        s=(item.properties or {}).get("datetime")
        if s:
            dt=datetime.fromisoformat(str(s).replace("Z","+00:00"))
    if dt is None:
        raise RuntimeError(f"missing STAC datetime for {item.id}")
    return dt.date()


def reconstructed_local_solar_date(utc_day,lon,h_local):
    h_utc_unwrapped=float(h_local)-float(lon)/15.0
    day_shift=math.floor(h_utc_unwrapped/24.0)
    return utc_day-timedelta(days=day_shift)


def _items(client,collection,bbox,d):
    last=None
    ds=d.isoformat()
    for k in range(5):
        try:
            xs=list(client.search(
                collections=[collection],bbox=bbox,
                datetime=f"{ds}T00:00:00Z/{ds}T23:59:59Z"
            ).items())
            return sorted([x for x in xs if str(x.id).startswith("MOD11A1")],key=lambda z:str(z.id))
        except Exception as e:
            last=e
            time.sleep(2*(k+1))
    raise RuntimeError(f"STAC search failed {d}: {last}")


def read_common_local_solar_date(client,collection,target_date,siteids,coords):
    lats=[coords[s][0] for s in siteids]
    lons=[coords[s][1] for s in siteids]
    bbox=[min(lons)-.002,min(lats)-.002,max(lons)+.002,max(lats)+.002]

    raw=[]
    for off in (-1,0,1):
        raw.extend(_items(client,collection,bbox,target_date+timedelta(days=off)))
    byid={str(x.id):x for x in raw}
    items=[byid[k] for k in sorted(byid)]
    if not items:
        return None

    with ExitStack() as stack:
        opened=[]
        for raw_item in items:
            item=planetary_computer.sign(raw_item)
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
            opened.append((
                str(item.id),item_utc_date(raw_item),dsL,dsQ,dsT,
                Transformer.from_crs("EPSG:4326",dsL.crs,always_xy=True)
            ))

        vals={}
        for sid in siteids:
            lat,lon=coords[sid]
            candidates=[]
            for itemid,utc_day,dsL,dsQ,dsT,tf in opened:
                x,y=tf.transform(lon,lat)
                row,col=dsL.index(x,y)
                if not (0<=row<dsL.height and 0<=col<dsL.width):
                    continue
                dn=int(dsL.read(1,window=Window(col,row,1,1))[0,0])
                q=int(dsQ.read(1,window=Window(col,row,1,1))[0,0])
                vt=int(dsT.read(1,window=Window(col,row,1,1))[0,0])
                mandatory=q & 0b11
                err=(q>>6)&0b11
                if not (dn>0 and mandatory==0 and err==0 and 0<=vt<=240):
                    continue
                h_local=float(vt)*0.1
                if reconstructed_local_solar_date(utc_day,lon,h_local)!=target_date:
                    continue
                candidates.append((itemid,utc_day,row,col,dn,q,h_local))
            if not candidates:
                return None
            candidates.sort(key=lambda z:z[0])
            itemid,utc_day,row,col,dn,q,h_local=candidates[0]
            vals[sid]={
                "lst_kelvin":float(dn)*.02,
                "view_local_hour":h_local,
                "qc":int(q),
                "item_id":itemid,
                "utc_data_date":utc_day.isoformat(),
                "local_solar_date":target_date.isoformat(),
                "pixel_key":f"{itemid}:{row}:{col}"
            }
        return vals
