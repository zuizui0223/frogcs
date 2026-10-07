#!/usr/bin/env python3
import json, re, urllib.request
import rasterio
from rasterio.windows import Window

PARENT="609955c9d34ea221ce33c534"
YEAR=2010
PTS=[
  {"name":"inland_TN","lat":35.0,"lon":-85.0},
  {"name":"Lake_Michigan","lat":43.5,"lon":-87.0},
]

def get_json(url):
    req=urllib.request.Request(url,headers={"User-Agent":"frogcs-dswemod-raster-audit/0.1","Accept":"application/json"})
    with urllib.request.urlopen(req,timeout=60) as r:
        return json.loads(r.read().decode())

children=get_json(f"https://www.sciencebase.gov/catalog/items?parentId={PARENT}&format=json&max=100").get("items") or []
child=None
for x in children:
    if re.search(rf"\b{YEAR}\b",x.get("title") or ""):
        child=x;break
if child is None:
    raise RuntimeError("year child not found")
item=get_json(f"https://www.sciencebase.gov/catalog/item/{child['id']}?format=json")
tif=None
for f in item.get("files") or []:
    if (f.get("name") or "").lower().endswith(".tif"):
        tif=f;break
if tif is None:
    raise RuntimeError("tif not found")
url=tif.get("downloadUri") or tif.get("url")
if not url:
    raise RuntimeError("no download URL")

out={"analysis":"dswemod_raster_io_audit_v0_1","year":YEAR,"url":url,"file_name":tif.get("name"),"file_size":tif.get("size"),"points":[],"frog_data_used":False}
with rasterio.Env(GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR",CPL_VSIL_CURL_ALLOWED_EXTENSIONS=".tif",GDAL_HTTP_MULTIRANGE="YES"):
    with rasterio.open(url) as ds:
        out["dataset"]={
          "count":ds.count,"width":ds.width,"height":ds.height,"crs":str(ds.crs),
          "transform":[float(ds.transform.a),float(ds.transform.b),float(ds.transform.c),float(ds.transform.d),float(ds.transform.e),float(ds.transform.f)],
          "bounds":[float(ds.bounds.left),float(ds.bounds.bottom),float(ds.bounds.right),float(ds.bounds.top)],
          "dtypes":list(ds.dtypes),"nodata":ds.nodata,
          "descriptions":list(ds.descriptions)
        }
        for p in PTS:
            row,col=ds.index(p["lon"],p["lat"])
            rec={**p,"index":[int(row),int(col)],"in_bounds":bool(0<=row<ds.height and 0<=col<ds.width),"bands":[]}
            if rec["in_bounds"]:
                for b in (1,5,12):
                    a=ds.read(b,window=Window(max(0,col-1),max(0,row-1),3,3))
                    rec["bands"].append({"band":b,"unique":[int(v) for v in sorted(set(a.ravel()))[:20]],"center":int(ds.read(b,window=Window(col,row,1,1))[0,0])})
            out["points"].append(rec)

print(json.dumps(out,indent=2))
