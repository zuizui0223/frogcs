#!/usr/bin/env python3
import json, math
import numpy as np, rasterio
from rasterio.windows import Window

# Arbitrary CONUS test points, unrelated to NAAMP response rows.
PTS=[(40.0,-90.0),(35.0,-85.0),(30.0,-95.0)]
YEAR,MONTH=2001,5
RES=.00025; PX=40000; OLON=-180.; OLAT=80.
HBASE="https://jeodpp.jrc.ec.europa.eu/ftp/jrc-opendata/GSWE/MonthlyHistory/VER1-0/tiles"
RBASE="https://jeodpp.jrc.ec.europa.eu/ftp/jrc-opendata/GSWE/MonthlyRecurrence/VER1-0/tiles"

def tile(lat,lon):
    gc=int(math.floor((lon-OLON)/RES)); gr=int(math.floor((OLAT-lat)/RES))
    rowoff=(gr//PX)*PX; coloff=(gc//PX)*PX
    return rowoff,coloff,gr-rowoff,gc-coloff

out=[]
with rasterio.Env(GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR",CPL_VSIL_CURL_ALLOWED_EXTENSIONS=".tif",GDAL_HTTP_MULTIRANGE="YES"):
  for lat,lon in PTS:
    rowoff,coloff,r,c=tile(lat,lon); ym=f"{YEAR:04d}_{MONTH:02d}"
    urls={
      "history":f"{HBASE}/{YEAR}/{ym}/{ym}-{rowoff:010d}-{coloff:010d}.tif",
      "recurrence":f"{RBASE}/monthlyRecurrence{MONTH}/monthlyRecurrence{MONTH}-{rowoff:010d}-{coloff:010d}.tif",
      "hasobs":f"{RBASE}/has_observations{MONTH}/has_observations{MONTH}-{rowoff:010d}-{coloff:010d}.tif",
    }
    vals={}
    for k,u in urls.items():
      with rasterio.open(u) as ds:
        a=ds.read(1,window=Window(max(0,c-2),max(0,r-2),5,5))
        vals[k]={"shape":list(a.shape),"unique":[int(v) for v in np.unique(a)[:20]],"min":int(a.min()),"max":int(a.max())}
    out.append({"lat":lat,"lon":lon,"tile_offsets_row_col":[rowoff,coloff],"values":vals})
print(json.dumps({"analysis":"jrc_three_product_io_smoke","points":out,"frog_data_used":False},indent=2))
