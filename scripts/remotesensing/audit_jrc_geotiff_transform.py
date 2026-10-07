#!/usr/bin/env python3
import json, math
import rasterio
from rasterio.windows import Window

PTS=[(40.0,-90.0),(35.0,-85.0),(30.0,-95.0)]
YEAR,MONTH=2001,5
RES=.00025; PX=40000; OLON=-180.; OLAT=80.
HBASE="https://jeodpp.jrc.ec.europa.eu/ftp/jrc-opendata/GSWE/MonthlyHistory/VER1-0/tiles"

def tile(lat,lon):
    gc=int(math.floor((lon-OLON)/RES)); gr=int(math.floor((OLAT-lat)/RES))
    x=(gc//PX)*PX; y=(gr//PX)*PX
    return x,y

out=[]
with rasterio.Env(GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR",CPL_VSIL_CURL_ALLOWED_EXTENSIONS=".tif",GDAL_HTTP_MULTIRANGE="YES"):
  for lat,lon in PTS:
    x,y=tile(lat,lon); ym=f"{YEAR:04d}_{MONTH:02d}"
    u=f"{HBASE}/{YEAR}/{ym}/{ym}-{x:010d}-{y:010d}.tif"
    with rasterio.open(u) as ds:
      idx=ds.index(lon,lat)
      r,c=idx
      a=ds.read(1,window=Window(max(0,c-2),max(0,r-2),5,5))
      out.append({
        "lat":lat,"lon":lon,"tile":[x,y],"url":u,
        "crs":str(ds.crs),"transform":list(ds.transform)[:6],
        "bounds":[ds.bounds.left,ds.bounds.bottom,ds.bounds.right,ds.bounds.top],
        "dataset_index":[int(r),int(c)],
        "values":{"unique":[int(v) for v in sorted(set(a.ravel()))[:20]],"min":int(a.min()),"max":int(a.max())}
      })
print(json.dumps({"analysis":"jrc_geotiff_transform_audit","points":out,"frog_data_used":False},indent=2))
