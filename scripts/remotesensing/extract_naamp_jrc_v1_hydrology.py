#!/usr/bin/env python3
from __future__ import annotations

import csv, hashlib, importlib.util, io, json, math, os, time, urllib.request
from collections import defaultdict, Counter
from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
import rasterio
from rasterio.windows import Window

ROOT=Path(__file__).resolve().parents[2]
EXP=ROOT/"exploration"
OUTCSV=ROOT/"remotesensing"/"NAAMP_JRC_V1_HYDROLOGY_EXPOSURES_V0_1.csv"
OUTJSON=ROOT/"remotesensing"/"NAAMP_JRC_V1_HYDROLOGY_COVERAGE_V0_1.json"

COORD_URL="https://www.sciencebase.gov/catalog/file/get/583dc314e4b0d1899f9dea8d?f=__disk__77%2F22%2F7e%2F77227ec46ac1c01592cd7d158d442cd8343a7536"
COORD_SHA="f71a87df9fc94e0d6c5d4466b4745c3bbaff874cbe7c28796b3f9eb44c2e6e83"
UNSAFE={"270107","270218","350414","720214","880113"}

HIST_BASE="https://jeodpp.jrc.ec.europa.eu/ftp/jrc-opendata/GSWE/MonthlyHistory/VER1-0/tiles"
REC_BASE="https://jeodpp.jrc.ec.europa.eu/ftp/jrc-opendata/GSWE/MonthlyRecurrence/VER1-0/tiles"

RES=0.00025
TILEPX=40000
ORIGIN_LON=-180.0
ORIGIN_LAT=80.0
BLOCK=256
RADII=(100,250,500)
PRIMARY_RADIUS=250
VALID_FRAC_MIN=0.50

def loadmod(name,path):
    s=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(s)
    assert s.loader
    s.loader.exec_module(m)
    return m

flex=loadmod("flex",EXP/"run_naamp_flexible_common_environment_null.py")
mem=flex.mem

def fetch(url):
    last=None
    for i in range(6):
        try:
            req=urllib.request.Request(url,headers={"User-Agent":"frogcs-jrc-hydrology-extractor/0.1"})
            with urllib.request.urlopen(req,timeout=180) as r:
                return r.read()
        except Exception as e:
            last=e; time.sleep(2*(i+1))
    raise RuntimeError(f"download failed: {url}: {last}")

def history_url(year,month,xoff,yoff):
    ym=f"{year:04d}_{month:02d}"
    return f"{HIST_BASE}/{year:04d}/{ym}/{ym}-{xoff:010d}-{yoff:010d}.tif"

def recurrence_url(month,xoff,yoff):
    return f"{REC_BASE}/monthlyRecurrence{month}/monthlyRecurrence{month}-{xoff:010d}-{yoff:010d}.tif"

def hasobs_url(month,xoff,yoff):
    return f"{REC_BASE}/has_observations{month}/has_observations{month}-{xoff:010d}-{yoff:010d}.tif"

def tile_offsets_from_global(grow,gcol):
    return (gcol//TILEPX)*TILEPX,(grow//TILEPX)*TILEPX

def circle_pixels(lat,lon,radius_m):
    # Candidate pixel-centre bounds on the fixed JRC EPSG:4326 global grid.
    lat_rad=radius_m/110574.0
    coslat=max(0.15,math.cos(math.radians(lat)))
    lon_rad=radius_m/(111320.0*coslat)
    c0=math.ceil((lon-lon_rad-ORIGIN_LON)/RES-0.5)
    c1=math.floor((lon+lon_rad-ORIGIN_LON)/RES-0.5)
    r0=math.ceil((ORIGIN_LAT-(lat+lat_rad))/RES-0.5)
    r1=math.floor((ORIGIN_LAT-(lat-lat_rad))/RES-0.5)
    rows=np.arange(r0,r1+1,dtype=np.int64)
    cols=np.arange(c0,c1+1,dtype=np.int64)
    rr,cc=np.meshgrid(rows,cols,indexing="ij")
    plats=ORIGIN_LAT-(rr+0.5)*RES
    plons=ORIGIN_LON+(cc+0.5)*RES
    p1=math.radians(lat)
    p2=np.radians(plats)
    dphi=p2-p1
    dlambda=np.radians(plons-lon)
    a=np.sin(dphi/2.0)**2+math.cos(p1)*np.cos(p2)*np.sin(dlambda/2.0)**2
    dist=2*6371008.8*np.arcsin(np.minimum(1.0,np.sqrt(a)))
    mask=dist<=radius_m
    return rr[mask],cc[mask]

class RemoteRasterSet:
    def __init__(self,url_fn):
        self.url_fn=url_fn
        self.datasets={}
        self.blocks={}
    def close(self):
        for ds in self.datasets.values():
            try: ds.close()
            except Exception: pass
        self.datasets.clear(); self.blocks.clear()
    def _ds(self,xoff,yoff):
        k=(xoff,yoff)
        if k not in self.datasets:
            url=self.url_fn(xoff,yoff)
            last=None
            for i in range(4):
                try:
                    self.datasets[k]=rasterio.open(url)
                    break
                except Exception as e:
                    last=e; time.sleep(2*(i+1))
            else:
                raise RuntimeError(f"raster open failed {url}: {last}")
        return self.datasets[k]
    def block(self,xoff,yoff,brow,bcol):
        k=(xoff,yoff,brow,bcol)
        if k in self.blocks:
            return self.blocks[k]
        ds=self._ds(xoff,yoff)
        row0=brow*BLOCK; col0=bcol*BLOCK
        h=min(BLOCK,ds.height-row0); w=min(BLOCK,ds.width-col0)
        last=None
        for i in range(4):
            try:
                a=ds.read(1,window=Window(col0,row0,w,h))
                self.blocks[k]=a
                return a
            except Exception as e:
                last=e; time.sleep(2*(i+1))
        raise RuntimeError(f"block read failed {k}: {last}")
    def values(self,grows,gcols):
        vals=np.empty(len(grows),dtype=np.uint8)
        groups=defaultdict(list)
        for i,(gr,gc) in enumerate(zip(grows,gcols)):
            xoff,yoff=tile_offsets_from_global(int(gr),int(gc))
            lr=int(gr-yoff); lc=int(gc-xoff)
            groups[(xoff,yoff,lr//BLOCK,lc//BLOCK)].append((i,lr,lc))
        for (xoff,yoff,br,bc),items in groups.items():
            a=self.block(xoff,yoff,br,bc)
            r0=br*BLOCK; c0=bc*BLOCK
            for i,lr,lc in items:
                vals[i]=a[lr-r0,lc-c0]
        return vals

def extract_history_for_sites(year,month,sites):
    rs=RemoteRasterSet(lambda x,y:history_url(year,month,x,y))
    result={}
    try:
        for sid,lat,lon in sites:
            rec={"SiteID":sid,"year":year,"month":month}
            for radius in RADII:
                rr,cc=circle_pixels(lat,lon,radius)
                vals=rs.values(rr,cc)
                valid=(vals==1)|(vals==2)
                vf=float(valid.mean()) if len(vals) else 0.0
                wf=float((vals[valid]==2).mean()) if valid.any() else None
                rec[f"current_valid_frac_r{radius}"]=vf
                rec[f"current_water_fraction_r{radius}"]=wf if vf>=VALID_FRAC_MIN else None
            result[sid]=rec
    finally:
        rs.close()
    return result

def extract_recurrence_for_sites(month,sites):
    rrset=RemoteRasterSet(lambda x,y:recurrence_url(month,x,y))
    hoset=RemoteRasterSet(lambda x,y:hasobs_url(month,x,y))
    result={}
    try:
        for sid,lat,lon in sites:
            rec={"SiteID":sid,"month":month}
            for radius in RADII:
                rr,cc=circle_pixels(lat,lon,radius)
                rvals=rrset.values(rr,cc).astype(float)
                hvals=hoset.values(rr,cc)
                valid=(hvals & 1)==1
                vf=float(valid.mean()) if len(hvals) else 0.0
                exp=float(np.mean(rvals[valid])/100.0) if valid.any() else None
                rec[f"expected_valid_frac_r{radius}"]=vf
                rec[f"expected_water_fraction_r{radius}"]=exp if vf>=VALID_FRAC_MIN else None
            result[sid]=rec
    finally:
        rrset.close(); hoset.close()
    return result

# Reconstruct frozen principal sample membership, without using the focal concentration value.
raw,runs,psub,dsub,hsub,pools,sampled,ss=flex.prepare_subset()
eligible=set(runs.RunID.astype(str))
site_map=mem.site_map(raw,eligible)

coord_bytes=fetch(COORD_URL)
if hashlib.sha256(coord_bytes).hexdigest()!=COORD_SHA:
    raise RuntimeError("coordinate SHA drift")
coords={}
for r in csv.DictReader(io.StringIO(coord_bytes.decode("utf-8-sig"))):
    sid=(r.get("SiteID") or "").strip()
    rid=(r.get("RouteNumber") or "").strip()
    if sid:
        coords[sid]=(rid,float(r["lat"]),float(r["lon"]))

runmeta={
    str(r.RunID):{
        "year":int(r.SurveyYear),
        "month":(date(int(r.SurveyYear),1,1)+timedelta(days=int(r.doy)-1)).month
    }
    for r in runs.itertuples(index=False)
}

request_by_ym=defaultdict(set)
safe_pair_specs=[]
prefail=Counter()
for p,dct in zip(psub.itertuples(index=False),dsub):
    rid=str(p.RouteNumber)
    if rid in UNSAFE:
        prefail["unsafe_route_geometry"]+=1; continue
    ids=mem.focal_siteids(p,dct,site_map)
    if ids is None or len(ids)!=10:
        prefail["siteid_identity_missing"]+=1; continue
    if any(sid not in coords for sid in ids):
        prefail["coordinate_missing"]+=1; continue
    wet=runmeta.get(str(p.wet_RunID)); dry=runmeta.get(str(p.dry_RunID))
    if wet is None or dry is None:
        prefail["run_date_missing"]+=1; continue
    safe_pair_specs.append({
        "route_cluster":str(p.route_cluster),
        "State":str(p.State),
        "RouteNumber":rid,
        "wet_RunID":str(p.wet_RunID),
        "dry_RunID":str(p.dry_RunID),
        "siteids":list(ids),
        "wet":wet,"dry":dry
    })
    for sid in ids:
        request_by_ym[(wet["year"],wet["month"])].add(sid)
        request_by_ym[(dry["year"],dry["month"])].add(sid)

all_sids=sorted({sid for ssids in request_by_ym.values() for sid in ssids})
months=sorted({m for y,m in request_by_ym})

# Extract climatological recurrence first (only 9 month x 4,245 possible site requests).
expected={}
with rasterio.Env(
    GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR",
    CPL_VSIL_CURL_ALLOWED_EXTENSIONS=".tif",
    GDAL_HTTP_MULTIRANGE="YES",
    VSI_CACHE="TRUE",
    VSI_CACHE_SIZE="67108864",
    GDAL_CACHEMAX="256",
):
    for month in months:
        sids=sorted({sid for (y,m),v in request_by_ym.items() if m==month for sid in v})
        sites=[(sid,coords[sid][1],coords[sid][2]) for sid in sids]
        z=extract_recurrence_for_sites(month,sites)
        for sid,rec in z.items():
            expected[(sid,month)]=rec
        print(json.dumps({"stage":"recurrence","month":month,"sites":len(sites)}),flush=True)

    rows=[]
    for k,(year,month) in enumerate(sorted(request_by_ym)):
        sids=sorted(request_by_ym[(year,month)])
        sites=[(sid,coords[sid][1],coords[sid][2]) for sid in sids]
        z=extract_history_for_sites(year,month,sites)
        for sid in sids:
            cur=z[sid]; exp=expected.get((sid,month),{})
            row={"SiteID":sid,"year":year,"month":month}
            for radius in RADII:
                cw=cur.get(f"current_water_fraction_r{radius}")
                ew=exp.get(f"expected_water_fraction_r{radius}")
                row[f"current_valid_frac_r{radius}"]=cur.get(f"current_valid_frac_r{radius}")
                row[f"expected_valid_frac_r{radius}"]=exp.get(f"expected_valid_frac_r{radius}")
                row[f"current_water_fraction_r{radius}"]=cw
                row[f"expected_water_fraction_r{radius}"]=ew
                row[f"hydrology_anomaly_r{radius}"]=(cw-ew) if cw is not None and ew is not None else None
            rows.append(row)
        print(json.dumps({"stage":"monthly_history","fileset_index":k+1,"fileset_total":len(request_by_ym),"year":year,"month":month,"sites":len(sids)}),flush=True)

df=pd.DataFrame(rows)
OUTCSV.parent.mkdir(exist_ok=True)
df.to_csv(OUTCSV,index=False,float_format="%.8g")

lookup={(str(r.SiteID),int(r.year),int(r.month)):r for r in df.itertuples(index=False)}
complete=[]
incomplete_reasons=Counter()
for p in safe_pair_specs:
    ok=True
    for sid in p["siteids"]:
        for rm in (p["wet"],p["dry"]):
            row=lookup.get((sid,int(rm["year"]),int(rm["month"])))
            if row is None:
                incomplete_reasons["missing_site_month_row"]+=1; ok=False; break
            h=getattr(row,f"hydrology_anomaly_r{PRIMARY_RADIUS}")
            if pd.isna(h):
                incomplete_reasons["invalid_primary_hydrology"]+=1; ok=False; break
        if not ok: break
    if ok:
        complete.append(p)

csv_sha=hashlib.sha256(OUTCSV.read_bytes()).hexdigest()
out={
    "analysis":"naamp_jrc_v1_hydrology_coverage_v0_1",
    "contract":"revision/NAAMP_DYNAMIC_HYDROLOGY_MECHANISM_EXTENSION_V0_2.md",
    "sources":{
        "coordinate_sha256":COORD_SHA,
        "jrc_product":"Global Surface Water v1.0",
        "monthly_history_base":HIST_BASE,
        "monthly_recurrence_base":REC_BASE
    },
    "extraction":{
        "radii_m":list(RADII),
        "primary_radius_m":PRIMARY_RADIUS,
        "valid_pixel_fraction_min":VALID_FRAC_MIN,
        "monthly_history_classes":{"0":"no_data","1":"non_water","2":"water"},
        "recurrence_validity":"has_observations bit0 == 1",
        "hydrology_anomaly":"current monthly water fraction minus monthly recurrence fraction"
    },
    "rows":{
        "hydrology_site_month_rows":int(len(df)),
        "unique_siteids":int(df.SiteID.nunique()),
        "years":[int(df.year.min()),int(df.year.max())],
        "months":sorted(int(x) for x in df.month.unique())
    },
    "coverage":{
        "frozen_principal_pairs":int(len(psub)),
        "coordinate_safe_pair_specs":int(len(safe_pair_specs)),
        "hydrology_complete_pairs":int(len(complete)),
        "hydrology_complete_routes":int(len({p["route_cluster"] for p in complete})),
        "hydrology_complete_states":int(len({p["State"] for p in complete})),
        "pre_hydrology_failures":dict(prefail),
        "hydrology_incomplete_reasons":dict(incomplete_reasons),
        "pair_threshold":1500,
        "route_threshold":300,
        "gate_pass":bool(len(complete)>=1500 and len({p["route_cluster"] for p in complete})>=300)
    },
    "primary_hydrology_distribution_response_blind":{
        "nonmissing_site_month_rows":int(df[f"hydrology_anomaly_r{PRIMARY_RADIUS}"].notna().sum()),
        "missing_site_month_rows":int(df[f"hydrology_anomaly_r{PRIMARY_RADIUS}"].isna().sum()),
        "median_current_valid_fraction":float(df[f"current_valid_frac_r{PRIMARY_RADIUS}"].median()),
        "median_expected_valid_fraction":float(df[f"expected_valid_frac_r{PRIMARY_RADIUS}"].median())
    },
    "exposure_csv":"remotesensing/NAAMP_JRC_V1_HYDROLOGY_EXPOSURES_V0_1.csv",
    "exposure_csv_sha256":csv_sha,
    "frog_endpoint_calculated":False,
    "mechanism_result_calculated":False
}
OUTJSON.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
print(json.dumps(out,indent=2,sort_keys=True))
