#!/usr/bin/env python3
"""Compare original C1V0 five mapped loss pixels with independent USDA Science TCC.

Exactly 2 originally source-selected Iowa stops, 3 historical years (2011-13),
two source layers (USFS Science TCC and NLCD TCC). Pinned v2025_6 annual
catalog identity, raw single-band 30-m nearest pixels, complete three-year
eligibility. This is a diagnostic AFTER C1V0 environmental outcome exposure.
No frog Counts/CallingIndex used; no field-site-continuity certification.
"""
from __future__ import annotations
import argparse,hashlib,json,math,urllib.parse,urllib.request,sys,time
from pathlib import Path
import numpy as np,pandas as pd
from rasterio.io import MemoryFile
from rasterio.warp import transform as project
HERE=Path(__file__).resolve().parent
if str(HERE) not in sys.path:sys.path.insert(0,str(HERE))
from screen_seven_iowa_nlcd_c1v0_v22 import fixed_sources,shared_grid,source_year
from build_naamp_observation_panel import SOURCE_PINS
from run_public_naamp_feasibility import COORD_SHA

YEARS=(2011,2012,2013)
TARGETS={"360104":("6613",3,3),"360412":("7247",7,2)}
BASES={
 "Science_TCC":"https://imagery.geoplatform.gov/iipp/rest/services/Vegetation/USFS_EDW_Science_TCC_CONUS/ImageServer",
 "NLCD_TCC":"https://imagery.geoplatform.gov/iipp/rest/services/Vegetation/USFS_EDW_NLCD_TCC_CONUS/ImageServer"
}
EXPECTED_NAME_PREFIX={"Science_TCC":"science_tcc_conus_wgs84_v2025_6_",
                      "NLCD_TCC":"nlcd_tcc_conus_wgs84_v2025_6_"}
ROOT_COORDINATE_SHA=COORD_SHA

def sha(blob):return hashlib.sha256(blob).hexdigest()
def request(base,endpoint,params,max_bytes=1_000_000):
    url=base+endpoint+"?"+urllib.parse.urlencode(params)
    req=urllib.request.Request(url,headers={"User-Agent":"frogcs-USDA-ScienceTCC-NLCD-crosscheck/2.9",
          "Accept":"application/json,image/tiff"})
    last=None
    for n in range(3):
        try:
            with urllib.request.urlopen(req,timeout=110) as h:
                loc=urllib.parse.urlparse(h.geturl())
                if loc.scheme!="https" or loc.hostname!="imagery.geoplatform.gov":
                    raise ValueError("USFS ImageServer unexpected redirect")
                raw=h.read(max_bytes+1)
                if len(raw)>max_bytes:raise ValueError("Bounded original source response exceeded")
            return raw
        except (urllib.error.URLError,TimeoutError) as ex:
            last=ex
            if n<2:time.sleep(2*(n+1))
    raise RuntimeError("USFS source unavailable: "+str(last)[:120])

def get_catalog(name,year):
    if year not in YEARS or name not in BASES:raise ValueError("Nonfrozen source/year")
    params={"where":f"beginyear <= {year} AND endyear >= {year}",
     "outFields":"objectid,name,beginyear,endyear,dataset_name",
     "returnGeometry":"false","f":"json"}
    raw=request(BASES[name],"/query",params)
    obj=json.loads(raw)
    rows=[z.get("attributes",{}) for z in obj.get("features",[])]
    if (len(rows)!=1 or int(rows[0].get("beginyear",-1))!=year or
       int(rows[0].get("endyear",-1))!=year or
       rows[0].get("name")!=f"{EXPECTED_NAME_PREFIX[name]}{year}0101_{year}1231" or
       not isinstance(rows[0].get("objectid"),int)):
        raise ValueError(f"USFS 2025.6 original year/catalog drift: {name} {year} {rows[:2]}")
    return rows[0],sha(raw)

def image_raster(name,year,bbox,width,height):
    identity,qsha=get_catalog(name,year)
    mosaic={"mosaicMethod":"esriMosaicByAttribute",
     "where":f"objectid={identity['objectid']} AND beginyear={year} AND endyear={year}",
     "sortField":"beginyear","sortValue":year,"ascending":True}
    params={"bbox":",".join(map(str,bbox)),"bboxSR":"5070","imageSR":"5070",
        "size":f"{width},{height}","format":"tiff","pixelType":"U8",
        "interpolation":"RSP_NearestNeighbor",
        "mosaicRule":json.dumps(mosaic,separators=(",",":")),
        "renderingRule":json.dumps({"rasterFunction":"None"}),
        "f":"image"}
    raw=request(BASES[name],"/exportImage",params, max_bytes=4_000_000)
    if raw[:4] not in (b'II*\x00',b'MM\x00*',b'II+\x00',b'MM\x00+'):
        raise ValueError("USFS original numeric raster source not TIFF: "+raw[:150].decode("utf-8","replace"))
    with MemoryFile(raw) as handle:
        with handle.open() as ds:
            actual=(ds.transform.a,ds.transform.b,ds.transform.c,
                    ds.transform.d,ds.transform.e,ds.transform.f)
            expected=(30,0,bbox[0],0,-30,bbox[3])
            if (ds.crs is None or ds.crs.to_epsg()!=5070 or
                ds.count!=1 or ds.width!=width or ds.height!=height or
                not np.allclose(actual,expected,atol=1e-7,rtol=0)):
                raise ValueError("USFS tree canopy image not on the prespecified aligned 30m pixel grid")
            arr=ds.read(1)
            valid=(arr<=100)
            invalid=~valid & ~np.isin(arr,[254,255])
            if invalid.any():raise ValueError("Unrecognized USFS TCC value codes")
    meta={"original_USFS_catalog":identity,"catalog_response_sha256":qsha,
           "source_tiff_sha256":sha(raw),"source_bytes":len(raw),
           "n_valid_tree_cover_pixels":int(valid.sum()),
           "valid_image_fraction":float(valid.mean()),
           "source_version_frozen":"v2025_6"}
    return arr,valid,meta

def summarize_site(station,bbox,old,new,series,expected_loss):
    site=station.iloc[0]
    x,y=project("EPSG:4326","EPSG:5070",
          [float(site.longitude)],[float(site.latitude)])
    rr,cc=np.indices(old[0].shape)
    old_bbox=old[2]
    gx=old_bbox[0]+(cc+.5)*30
    gy=old_bbox[3]-(rr+.5)*30
    circle=(gx-x[0])**2+(gy-y[0])**2<=250**2
    loss=circle&old[1]&new[1]&np.isin(old[0],[41,42,43])&~np.isin(new[0],[41,42,43])
    indices=np.argwhere(loss)
    if len(indices)!=expected_loss:raise ValueError("Original C1V0 loss pixels changed on re-fetch")
    mapped=[]
    for iy,ix in indices:
        cx=old_bbox[0]+(ix+.5)*30
        cy=old_bbox[3]-(iy+.5)*30
        col=int(math.floor((cx-bbox[0])/30))
        row=int(math.floor((bbox[3]-cy)/30))
        mapped.append((row,col,iy,ix))
    table={}
    for product,layers in series.items():
        vals={}
        for year in YEARS:
            arr,valid,meta=layers[year]
            yr_values=[]
            for row,col,iy,ix in mapped:
                if not(0<=row<arr.shape[0] and 0<=col<arr.shape[1] and valid[row,col]):
                    raise ValueError("Missing USFS TCC values for selected loss cell")
                yr_values.append(int(arr[row,col]))
            valid_area=int(valid.sum())
            vals[str(year)]={"mapped_loss_cell_tree_cover_pct":yr_values,
                "site_buffer_canopy":None}
        # Three-year valid area at source site mask.
        ny,nx=series[product][2011][0].shape
        sr,sc=np.indices((ny,nx))
        sx=bbox[0]+(sc+.5)*30
        sy=bbox[3]-(sr+.5)*30
        crop_circle=(sx-x[0])**2+(sy-y[0])**2<=250**2
        shared=crop_circle.copy()
        for year in YEARS:shared &= layers[year][1]
        if shared.sum()<0.8*crop_circle.sum():
            raise ValueError("USFS Science TCC 3-year full-circle QA below 80%")
        for year in YEARS:
            arr=layers[year][0]
            vals[str(year)]["250m_mean_tree_canopy_pct"]=float(arr[shared].mean())
            vals[str(year)]["valid_250m_pixels_common"]=int(shared.sum())
        a=np.array(vals["2011"]["mapped_loss_cell_tree_cover_pct"])
        b=np.array(vals["2012"]["mapped_loss_cell_tree_cover_pct"])
        c=np.array(vals["2013"]["mapped_loss_cell_tree_cover_pct"])
        table[product]={"years":vals,
            "loss_cell_delta_2011_2012_pct_points":(b-a).astype(int).tolist(),
            "loss_cell_delta_2011_2013_pct_points":(c-a).astype(int).tolist(),
            "loss_cells_with_declining_canopy_2011_2012":int((b<a).sum()),
            "loss_cells_with_declining_canopy_2011_2013":int((c<a).sum()),
            "site_250m_mean_delta_2011_2013_pct_points":float(
               vals["2013"]["250m_mean_tree_canopy_pct"]-vals["2011"]["250m_mean_tree_canopy_pct"])}
    return {"site_id":str(site.site_id),"route_id":str(site.route_id),
        "stop_number":int(site.stop_number),"n_original_C1V0_forest_loss_cells":expected_loss,
        "USFS_annual_tree_canopy_comparison":table,
        "historical_field_site_verified":False,
        "target_selected_after_C1V0_label_result":True}

def main():
    p=argparse.ArgumentParser()
    for name in ("runs","stops","coords","out"):
        p.add_argument("--"+name,required=True)
    a=p.parse_args()
    paths={"Runs.csv":Path(a.runs),"Stops.csv":Path(a.stops),
           "Coordinates.csv":Path(a.coords)}
    sources={k:sha(v.read_bytes()) for k,v in paths.items()}
    if sources!={**SOURCE_PINS,"Coordinates.csv":ROOT_COORDINATE_SHA}:
        raise ValueError("Original NAAMP source SHA256 drift")
    allsites,_=fixed_sources(pd.read_csv(a.runs,dtype=str,keep_default_na=False),
                    pd.read_csv(a.stops,dtype=str,keep_default_na=False),
                    pd.read_csv(a.coords,dtype={"RouteNumber":str,"SiteID":str}))
    out={"analysis":"independent_USFS_TCC_v2025_6_vs_C1V0_5_forested_class_loss_cells_v29",
        "no_frog_outcomes_read":True,
        "historical_field_sites_externally_verified":0,
        "target_selection_after_C1V0_landcover_readback":True,
        "not_a_predeclared_independent_inferential_sample":True,
        "NAAMP_source_sha256":sources,
        "years":[2011,2012,2013],"collection_version":"2025_6",
        "source_raster_metadata":[],"sites":[],"failures":[],
        "status":"STARTED"}
    target=Path(a.out);target.parent.mkdir(parents=True,exist_ok=True)
    for route,(site_id,stopnum,loss_n) in TARGETS.items():
        try:
            group=allsites[allsites.route_id==route]
            bbox,width,height=shared_grid(group)
            oldlab,ov,om=source_year(2011,bbox,width,height)
            newlab,nv,nm=source_year(2012,bbox,width,height)
            x=group[(group.site_id==site_id)&(group.stop_number==stopnum)]
            if len(x)!=1:raise ValueError("Pre-frozen source site missing")
            # Use same 30m grid from the full route to preclude silent geographic shifts.
            layers={}
            for product in BASES:
                layers[product]={}
                for year in YEARS:
                    arr,v,meta=image_raster(product,year,bbox,width,height)
                    layers[product][year]=(arr,v,meta)
                    out["source_raster_metadata"].append({
                      "route_id":route,"product":product,"year":year,
                      **meta})
                    print(json.dumps({"route":route,"product":product,"year":year,
                      "valid_fraction":meta["valid_image_fraction"]}),flush=True)
            record=summarize_site(x,bbox,(oldlab,ov,bbox),
                 (newlab,nv,bbox),layers,loss_n)
            out["sites"].append(record)
        except Exception as ex:
            out["failures"].append({"route":route,"error_type":type(ex).__name__,
                "error":str(ex)[:250]})
        target.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    out["status"]="BOTH_SITES_TCC_VERIFIED" if len(out["sites"])==2 else "PARTIAL_OR_FAILED_TCC_SOURCE"
    target.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"status":out["status"],"n_sites":len(out["sites"]),
        "errors":out["failures"]}),flush=True)
    if not out["sites"]:
        raise RuntimeError("No source-pixel TCC study sites matched and verified")

if __name__=="__main__":main()
