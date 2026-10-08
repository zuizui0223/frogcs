#!/usr/bin/env python3
"""Extract annual *official USGS Collection 1.2* NLCD class areas from
locally available, reprojected or mosaic GeoTIFFs by verified physical site.

Uses native projected metric raster pixels; does NOT assume a nonexistent
Google Earth Engine official Collection 1.2 asset. Data procurement is separate.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd
import rasterio
from rasterio.windows import from_bounds
from rasterio.features import geometry_mask
from rasterio.warp import transform
from shapely.geometry import Point, mapping

NLCD_CLASSES={11,12,21,22,23,24,31,41,42,43,52,71,81,82,90,95}
GROUPS={"forest":{41,42,43},"agriculture":{81,82},"developed":{21,22,23,24},
        "wetland":{90,95},"openwater":{11}}


def extract_one(src, longitude:float, latitude:float, radius:int)->dict:
    if src.crs is None or not src.crs.is_projected:
        raise ValueError("NLCD raster must be projected to metric equal-area CRS")
    if str(src.crs.linear_units).lower() not in {"metre","meter","metres","meters"}:
        raise ValueError("NLCD projected units must be metres")
    if src.count!=1:
        raise ValueError("one categorical landcover band expected")
    cx,cy=transform("EPSG:4326",src.crs,[longitude],[latitude]);cx=cx[0];cy=cy[0]
    poly=Point(cx,cy).buffer(radius,quad_segs=64)
    win=from_bounds(cx-radius,cy-radius,cx+radius,cy+radius,transform=src.transform)
    win=win.round_offsets().round_lengths()
    band=src.read(1,window=win,boundless=True,fill_value=src.nodata if src.nodata is not None else 0)
    affine=src.window_transform(win)
    inside=geometry_mask([mapping(poly)],out_shape=band.shape,transform=affine,invert=True,all_touched=False)
    if not inside.any():
        raise ValueError("no pixels intersect the site buffer")
    area=abs(affine.a*affine.e-affine.b*affine.d)
    all_classified=np.isin(band,list(NLCD_CLASSES))
    unknown=band[inside & ~all_classified & ~((band==src.nodata) if src.nodata is not None else np.zeros(band.shape,dtype=bool))]
    if len(unknown):
        raise ValueError(f"unexpected NLCD categorical codes {np.unique(unknown)[:8].tolist()}")
    known_inside=inside & all_classified
    out={}
    total_known=0
    for group,codes in GROUPS.items():
        n=int((known_inside & np.isin(band,list(codes))).sum())
        out[f"{group}_area_m2"]=n*area
        total_known+=n
    valid_n=int(known_inside.sum())
    out["other_area_m2"]=(valid_n-total_known)*area
    out["nodata_area_m2"]=int(inside.sum()-valid_n)*area
    out["raster_pixel_area_m2"]=float(area)
    out["sampled_pixels"]=int(inside.sum())
    return out


def extract(requests:pd.DataFrame,index:pd.DataFrame)->pd.DataFrame:
    req={"route_id","site_id","longitude","latitude","buffer_m","year"}
    idx={"year","raster_path","source_image_id","source_version"}
    if req-set(requests.columns):raise ValueError(f"missing requests columns {sorted(req-set(requests.columns))}")
    if idx-set(index.columns):raise ValueError(f"missing raster index columns {sorted(idx-set(index.columns))}")
    q=requests[sorted(req)].copy();i=index[sorted(idx)].copy()
    if q.duplicated(["route_id","site_id","buffer_m","year"]).any():
        raise ValueError("duplicate site/year/buffer requests")
    if i.duplicated(["year"]).any():raise ValueError("duplicate raster year in index")
    if not i.source_version.astype(str).str.contains("ANNUAL_NLCD_C1_2",regex=False).all():
        raise ValueError("unsupported land cover source/version")
    q["year"]=pd.to_numeric(q.year,errors="raise").astype(int)
    q["buffer_m"]=pd.to_numeric(q.buffer_m,errors="raise").astype(int)
    if not q.buffer_m.isin([250,1000]).all():raise ValueError("unexpected buffer")
    merged=q.merge(i,on="year",validate="many_to_one",how="left",indicator=True)
    if not merged._merge.eq("both").all():
        raise ValueError("year missing official NLCD raster; no silent fallback to other dataset")
    rows=[]
    for raster_path,frame in merged.groupby("raster_path",sort=True):
        if not Path(raster_path).exists():raise FileNotFoundError(raster_path)
        with rasterio.open(raster_path) as src:
            for r in frame.itertuples(index=False):
                features=extract_one(src,float(r.longitude),float(r.latitude),int(r.buffer_m))
                rows.append({"route_id":str(r.route_id),"site_id":str(r.site_id),"buffer_m":int(r.buffer_m),
                             "year":int(r.year),"source_image_id":str(r.source_image_id),
                             "source_version":str(r.source_version),**features})
    return pd.DataFrame(rows).sort_values(["route_id","site_id","buffer_m","year"]).reset_index(drop=True)


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--year-requests",required=True)
    p.add_argument("--raster-index",required=True)
    p.add_argument("--out",required=True)
    a=p.parse_args()
    table=extract(pd.read_csv(a.year_requests,dtype={"route_id":str,"site_id":str}),pd.read_csv(a.raster_index))
    o=Path(a.out);o.parent.mkdir(parents=True,exist_ok=True);table.to_csv(o,index=False)
    print(json.dumps({"year_buffer_rows":len(table),"sites":int(table[["route_id","site_id"]].drop_duplicates().shape[0]),
                      "reads_frog_responses":False,"official_NLCD_download_not_automated":True}))

if __name__=="__main__":main()
