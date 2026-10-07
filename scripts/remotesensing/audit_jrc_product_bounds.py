#!/usr/bin/env python3
import json, math
import rasterio

PTS=[
  {"name":"inland_IL","lat":40.0,"lon":-90.0},
  {"name":"inland_TN","lat":35.0,"lon":-85.0},
  {"name":"Lake_Michigan","lat":43.5,"lon":-87.0},
]
YEAR,MONTH=2001,5
RES=.00025; PX=40000; OLON=-180.; OLAT=80.
HBASE="https://jeodpp.jrc.ec.europa.eu/ftp/jrc-opendata/GSWE/MonthlyHistory/VER1-0/tiles"
RBASE="https://jeodpp.jrc.ec.europa.eu/ftp/jrc-opendata/GSWE/MonthlyRecurrence/VER1-0/tiles"

def offsets(lat,lon):
    gc=int(math.floor((lon-OLON)/RES)); gr=int(math.floor((OLAT-lat)/RES))
    return (gr//PX)*PX,(gc//PX)*PX

out=[]
with rasterio.Env(GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR",CPL_VSIL_CURL_ALLOWED_EXTENSIONS=".tif",GDAL_HTTP_MULTIRANGE="YES"):
  for p in PTS:
    ro,co=offsets(p["lat"],p["lon"]); ym=f"{YEAR:04d}_{MONTH:02d}"
    urls={
      "history":f"{HBASE}/{YEAR}/{ym}/{ym}-{ro:010d}-{co:010d}.tif",
      "recurrence":f"{RBASE}/monthlyRecurrence{MONTH}/monthlyRecurrence{MONTH}-{ro:010d}-{co:010d}.tif",
      "hasobs":f"{RBASE}/has_observations{MONTH}/has_observations{MONTH}-{ro:010d}-{co:010d}.tif",
    }
    rec={"name":p["name"],"lat":p["lat"],"lon":p["lon"],"offsets_row_col":[ro,co],"products":{}}
    for k,u in urls.items():
      with rasterio.open(u) as ds:
        r,c=ds.index(p["lon"],p["lat"])
        inb=0<=r<ds.height and 0<=c<ds.width
        val=None
        if inb:
          val=int(ds.read(1,window=((r,r+1),(c,c+1)))[0,0])
        rec["products"][k]={
          "bounds":[float(ds.bounds.left),float(ds.bounds.bottom),float(ds.bounds.right),float(ds.bounds.top)],
          "transform":[float(ds.transform.a),float(ds.transform.e),float(ds.transform.c),float(ds.transform.f)],
          "index":[int(r),int(c)],"in_bounds":bool(inb),"value":val
        }
    out.append(rec)
print(json.dumps({"analysis":"jrc_product_bounds_and_point_audit","points":out,"frog_data_used":False},indent=2))
