#!/usr/bin/env python3
import json, math
import rasterio

PTS=[(40.0,-90.0),(35.0,-85.0),(30.0,-95.0)]
YEAR,MONTH=2001,5
RES=.00025; PX=40000; OLON=-180.; OLAT=80.
HBASE="https://jeodpp.jrc.ec.europa.eu/ftp/jrc-opendata/GSWE/MonthlyHistory/VER1-0/tiles"

def guessed_tile(lat,lon):
    gc=int(math.floor((lon-OLON)/RES)); gr=int(math.floor((OLAT-lat)/RES))
    x=(gc//PX)*PX; y=(gr//PX)*PX
    return x,y

out=[]
with rasterio.Env(GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR",CPL_VSIL_CURL_ALLOWED_EXTENSIONS=".tif",GDAL_HTTP_MULTIRANGE="YES"):
  for lat,lon in PTS:
    x,y=guessed_tile(lat,lon); ym=f"{YEAR:04d}_{MONTH:02d}"
    u=f"{HBASE}/{YEAR}/{ym}/{ym}-{x:010d}-{y:010d}.tif"
    with rasterio.open(u) as ds:
      r,c=ds.index(lon,lat)
      in_bounds=(0<=r<ds.height and 0<=c<ds.width)
      out.append({
        "lat":lat,"lon":lon,"guessed_tile":[x,y],"url":u,
        "width":ds.width,"height":ds.height,
        "crs":str(ds.crs),
        "transform":[float(ds.transform.a),float(ds.transform.b),float(ds.transform.c),float(ds.transform.d),float(ds.transform.e),float(ds.transform.f)],
        "bounds":[float(ds.bounds.left),float(ds.bounds.bottom),float(ds.bounds.right),float(ds.bounds.top)],
        "dataset_index":[int(r),int(c)],
        "index_in_bounds":bool(in_bounds)
      })
print(json.dumps({"analysis":"jrc_geotiff_transform_audit_v0_2","points":out,"frog_data_used":False,"raster_values_read":False},indent=2))
