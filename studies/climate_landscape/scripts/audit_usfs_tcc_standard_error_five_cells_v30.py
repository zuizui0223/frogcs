#!/usr/bin/env python3
"""At five preselected Iowa C1V0 loss pixels, read USDA Science TCC SE.

Frozen five nominal pixel positions and 2011/12/13. USDA source SE is U16
with ×100 scaling. The SE corresponds to tree ensemble dispersion, not a
paired-year, independently calibrated standard error of canopy change.
NEVER compute an unjustified P value, independence test or causal effect.
"""
from __future__ import annotations
import argparse,hashlib,json,math,sys,time
from pathlib import Path
import numpy as np,pandas as pd
from rasterio.io import MemoryFile
from rasterio.warp import transform as project
HERE=Path(__file__).resolve().parent
if str(HERE) not in sys.path:sys.path.insert(0,str(HERE))
from screen_seven_iowa_nlcd_c1v0_v22 import fixed_sources,shared_grid,source_year
from extract_usfs_science_tcc_at_five_nlcd_cells_v29 import TARGETS,YEARS,BASES,request as usfs_request,get_catalog
from build_naamp_observation_panel import SOURCE_PINS
from run_public_naamp_feasibility import COORD_SHA

SE_BASE="https://imagery.geoplatform.gov/iipp/rest/services/Vegetation/USFS_EDW_TCC_Science_SE_CONUS/ImageServer"
NODATA_CODES={65534,65535}
EXPECTED_POINTS=5
def sha(raw):return hashlib.sha256(raw).hexdigest()

def validate_standard_error(array):
    a=np.asarray(array)
    if a.dtype!=np.dtype('uint16'):raise ValueError("Official U16 standard error was truncated")
    invalid=(a==65534)|(a==65535)
    if np.any((a[~invalid]>12000)):raise ValueError("Implausible original 100-scaled SE values")
    values=a.astype(float)/100
    values[invalid]=np.nan
    return values,~invalid

def inspect_catalog(year):
    if year not in YEARS:raise ValueError("Unfrozen source year")
    params={"where":f"beginyear <= {year} AND endyear >= {year}",
       "outFields":"objectid,name,beginyear,endyear,dataset_name",
       "returnGeometry":"false","f":"json"}
    raw=usfs_request(SE_BASE,"/query",params)
    obj=json.loads(raw)
    if obj.get('error'):raise ValueError("Official SE catalog service error")
    records=[x.get("attributes",{}) for x in obj.get("features",[])]
    if len(records)!=1:raise ValueError(f"USFS SE year {year} has {len(records)} catalog records")
    record=records[0]
    if not (isinstance(record.get("objectid"),int) and
        int(record.get("beginyear",-1))==year and
        int(record.get("endyear",-1))==year and
        "v2025_6" in str(record.get("name","")) and
        str(year) in str(record.get("name",""))):
        raise ValueError("USFS SE frozen version/year drift")
    return record,sha(raw)

def se_image(year,bbox,width,height):
    row,qsha=inspect_catalog(year)
    mosaic={"mosaicMethod":"esriMosaicByAttribute",
        "where":f"objectid={row['objectid']} AND beginyear={year} AND endyear={year}",
        "sortField":"beginyear","sortValue":year,"ascending":True}
    params={"bbox":",".join(map(str,bbox)),"bboxSR":"5070","imageSR":"5070",
       "size":f"{width},{height}","format":"tiff","pixelType":"U16",
       "interpolation":"RSP_NearestNeighbor",
       "mosaicRule":json.dumps(mosaic,separators=(",",":")),
       "renderingRule":json.dumps({"rasterFunction":"None"}),"f":"image"}
    raw=usfs_request(SE_BASE,"/exportImage",params,max_bytes=8_000_000)
    if raw[:4] not in (b'II*\x00',b'MM\x00*',b'II+\x00',b'MM\x00+'):
        raise ValueError("USFS SE source returned nonTIFF")
    with MemoryFile(raw) as mem:
        with mem.open() as ds:
            tr=ds.transform
            actual=(tr.a,tr.b,tr.c,tr.d,tr.e,tr.f)
            expected=(30,0,bbox[0],0,-30,bbox[3])
            if (ds.count!=1 or ds.crs is None or ds.crs.to_epsg()!=5070
                or (ds.width,ds.height)!=(width,height)
                or not np.allclose(actual,expected,atol=1e-7,rtol=0)):
                raise ValueError("SE source pixel grid not exactly matched to NLCD")
            img=ds.read(1)
    values,valid=validate_standard_error(img)
    return values,valid,{"catalog":row,"catalog_sha256":qsha,
       "geotiff_sha256":sha(raw),"bytes":len(raw),
       "original_dtype":str(img.dtype),
       "n_valid":int(valid.sum()),"valid_fraction":float(valid.mean()),
       "encoding":"U16 divided by 100 in percentage-points SE units"}

def positions_at_nominal_site(site,bbox,shape):
    x,y=project("EPSG:4326","EPSG:5070",
        [float(site.longitude)],[float(site.latitude)])
    rr,cc=np.indices(shape)
    gx=bbox[0]+30*(cc+.5);gy=bbox[3]-30*(rr+.5)
    return (gx-x[0])**2+(gy-y[0])**2<=250**2

def compare_annual_se(canopy_years,se_years):
    """No z-test: bound annual SE sum without assuming temporal independence."""
    if set(canopy_years)!=set(YEARS) or set(se_years)!=set(YEARS):
        raise ValueError("Incomplete years at mapped pixel")
    if any(not np.isfinite([canopy_years[y],se_years[y]]).all() for y in YEARS):
        raise ValueError("Missing original annual canopy or error at selected pixel")
    if any(x<0 for x in se_years.values()):raise ValueError("Negative USDA SE")
    delta12=float(canopy_years[2012]-canopy_years[2011])
    delta13=float(canopy_years[2013]-canopy_years[2011])
    return {"canopy_2011":int(canopy_years[2011]),
            "canopy_2012":int(canopy_years[2012]),
            "canopy_2013":int(canopy_years[2013]),
            "SE_2011":round(float(se_years[2011]),4),
            "SE_2012":round(float(se_years[2012]),4),
            "SE_2013":round(float(se_years[2013]),4),
            "canopy_delta_2011_2012_pp":delta12,
            "canopy_delta_2011_2013_pp":delta13,
            "sum_marginal_SE_2011_2012":round(se_years[2011]+se_years[2012],4),
            "sum_marginal_SE_2011_2013":round(se_years[2011]+se_years[2013],4),
            "diff_exceeds_sum_SE_2011_2012":bool(abs(delta12)>(se_years[2011]+se_years[2012])),
            "diff_exceeds_sum_SE_2011_2013":bool(abs(delta13)>(se_years[2011]+se_years[2013])),
            "not_a_calibrated_uncertainty_interval":True}

def main():
    ap=argparse.ArgumentParser()
    for key in ("runs","stops","coords","out"):ap.add_argument("--"+key,required=True)
    a=ap.parse_args()
    paths={"Runs.csv":Path(a.runs),"Stops.csv":Path(a.stops),"Coordinates.csv":Path(a.coords)}
    if {k:sha(p.read_bytes()) for k,p in paths.items()}!={**SOURCE_PINS,"Coordinates.csv":COORD_SHA}:
        raise ValueError("Frozen NAAMP metadata SHA drift")
    selected,_=fixed_sources(pd.read_csv(a.runs,dtype=str,keep_default_na=False),
       pd.read_csv(a.stops,dtype=str,keep_default_na=False),
       pd.read_csv(a.coords,dtype={"RouteNumber":str,"SiteID":str}))
    out={"analysis":"USFS_v2025_6_Science_TCC_pixel_SE_at_five_C1V0_loss_cells_v30",
         "selection_post_C1V0_environment_readback":True,
         "no_new_frog_calls_read":True,"historical_sites_field_verified":0,
         "not_a_significance_test":True,"year_endpoints":list(YEARS),
         "source_SE_divisor":100,"status":"RUNNING","sites":[],"failures":[]}
    target=Path(a.out);target.parent.mkdir(parents=True,exist_ok=True)
    for route,(site_id,stopnum,expected) in TARGETS.items():
        try:
            group=selected[selected.route_id.eq(route)]
            bbox,width,height=shared_grid(group)
            q=group[(group.site_id==site_id)&(group.stop_number==stopnum)]
            if len(q)!=1:raise ValueError("Frozen site key missing")
            a2011,valid2011,_=source_year(2011,bbox,width,height)
            a2012,valid2012,_=source_year(2012,bbox,width,height)
            circ=positions_at_nominal_site(q.iloc[0],bbox,a2011.shape)
            loss=circ&valid2011&valid2012&np.isin(a2011,[41,42,43])&~np.isin(a2012,[41,42,43])
            positions=np.argwhere(loss)
            if len(positions)!=expected:raise ValueError("Frozen loss pixel count differs")
            # Match tree-cover model and U16 SE product on exact original grid.
            canopy={};se={};metas={}
            for year in YEARS:
                from extract_usfs_science_tcc_at_five_nlcd_cells_v29 import image_raster
                tcc,tccvalid,tccmeta=image_raster("Science_TCC",year,bbox,width,height)
                searr,sevalid,semeta=se_image(year,bbox,width,height)
                if tcc.shape!=searr.shape:raise ValueError("SE/TCC source grid size discrepancy")
                canopy[year]=(tcc,tccvalid)
                se[year]=(searr,sevalid)
                metas[str(year)]={"canopy":tccmeta,"SE":semeta}
                print(json.dumps({"route":route,"year":year,"SE_valid_fraction":semeta["valid_fraction"]}),flush=True)
            rows=[]
            for iy,ix in positions:
                if any(not canopy[year][1][iy,ix] or not se[year][1][iy,ix] for year in YEARS):
                    raise ValueError("Missing Science TCC or SE at original selected pixel")
                value={year:int(canopy[year][0][iy,ix]) for year in YEARS}
                error={year:float(se[year][0][iy,ix]) for year in YEARS}
                rows.append({"row":int(iy),"col":int(ix),
                    "land_cover_code_2011":int(a2011[iy,ix]),
                    "land_cover_code_2012":int(a2012[iy,ix]),
                    **compare_annual_se(value,error)})
            out["sites"].append({"route":route,"site_id":site_id,
                 "stop_number":stopnum,"n_original_mapped_C1V0_loss_pixels":len(rows),
                 "pixels":rows,"source_metadata":metas,
                 "historical_physical_station_independently_verified":False})
        except Exception as e:
            out["failures"].append({"route":route,"error_type":type(e).__name__,"error":str(e)[:250]})
        target.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    out["status"]="FIVE_PIXELS_WITH_COMPLETE_TCC_AND_SE" if len(out["sites"])==2 else "SOURCE_INCOMPLETE_DO_NOT_INFER"
    target.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"status":out["status"],"n_sites":len(out["sites"]),"errors":out["failures"]}),flush=True)
    if not out["sites"]:raise RuntimeError("No mapped pixels with complete SE source")

if __name__=="__main__":main()
