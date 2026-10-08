#!/usr/bin/env python3
"""Outcome-blind stability of mapped NLCD C1V0 2004-2014 land transitions.

Inputs are the pinned 360417 three-year ORIGINAL 30m TIFF artifact and
published nominal site coordinates. No frog response or SiteID history outcome
may be used in this module. This is a POST-READBACK descriptive sensitivity,
not an independent confirmation, nor historical site identity proof.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
from pathlib import Path
import zipfile

import numpy as np
import pandas as pd
import rasterio
from rasterio.io import MemoryFile
from rasterio.warp import transform as project

YEARS=(2004,2009,2014)
ALLOWED={11,12,21,22,23,24,31,41,42,43,52,71,81,82,90,95}
FOREST={41,42,43}
DEVELOPED={21,22,23,24}
AGRICULTURE={81,82}
WETLAND={90,95}
WATER={11}
RADII=(250,1000)
# 6m slightly exceeds the archived-vs-later-map 5.84m maximum discrepancy;
# 15m is half a 30m pixel; 30m is one native pixel.
SHIFTS_M=(0,6,15,30)
DIRECTIONS=8
MIN_VALID=.8
EXPECTED_VERSION='Annual_NLCD_Collection_1.0_CU_C1V0'
EXPECTED_BBOX=(179220,2044410,184320,2056680)


def sha(data:bytes)->str:
    return hashlib.sha256(data).hexdigest()


def read_archive(path:Path):
    with zipfile.ZipFile(path) as z:
        names=set(z.namelist())
        if 'receipt.json' not in names:
            raise ValueError('Original source receipt missing')
        receipt=json.loads(z.read('receipt.json'))
        if receipt.get('source_version')!=EXPECTED_VERSION:
            raise ValueError('Source version differs from fixed NLCD C1V0')
        if receipt.get('status')!='all_three_years_raw_C1V0_pixels_available_environment_only':
            raise ValueError('Expected complete original-source three-year receipt')
        if receipt.get('frog_counts_read') is not False:
            raise ValueError('Source receipt not response-blind')
        if tuple(receipt.get('study_bbox_epsg5070',[]))!=EXPECTED_BBOX:
            raise ValueError('Unfrozen source extent')
        if set(map(int,receipt.get('years',{})))!=set(YEARS):
            raise ValueError('Source-year set mismatch')
        arrs={};tr=None;crs=None
        for year in YEARS:
            matches=[n for n in names if n.endswith('.tif') and str(year) in n]
            if len(matches)!=1:
                raise ValueError(f'Ambiguous original TIFF for {year}')
            payload=z.read(matches[0]);h=sha(payload)
            if h!=receipt['years'][str(year)].get('data_sha256'):
                raise ValueError(f'Raster hash mismatch {year}')
            catalog=receipt['years'][str(year)]['catalog']
            if not catalog['catalog_source_name'].endswith(f'_LndCov_{year}_CU_C1V0'):
                raise ValueError(f'Unexpected dated source product {year}')
            with MemoryFile(payload) as mem:
                with mem.open() as src:
                    if src.count!=1 or src.crs is None or src.crs.to_epsg()!=5070:
                        raise ValueError('Not a 1-band EPSG:5070 NLCD source')
                    if src.width!=170 or src.height!=409 or any(abs(p-30)>1e-6 for p in src.res):
                        raise ValueError('Wrong 30m source array shape/grid')
                    t=src.transform
                    if not (abs(t.c-EXPECTED_BBOX[0])<1e-7 and
                            abs(t.f-EXPECTED_BBOX[3])<1e-7):
                        raise ValueError('Invalid source grid origin')
                    if tr is not None and t!=tr:
                        raise ValueError('Unaligned source-year pixels')
                    tr=t;crs=src.crs
                    arr=src.read(1)
                    codes=set(map(int,np.unique(arr)))
                    if not codes.issubset(ALLOWED | {0,255}):
                        raise ValueError(f'Unexpected coded classes in {year}')
                    arrs[year]=arr
    return arrs,tr,receipt


def site_coordinates(path:Path,expected_hash:str):
    payload=path.read_bytes()
    if sha(payload)!=expected_hash:
        raise ValueError('Station location source SHA differs from original')
    d=pd.read_csv(io.BytesIO(payload),dtype={'route_id':str,'site_id':str})
    if (len(d)!=10 or sorted(d.stop_number.tolist())!=list(range(1,11)) or
        not d.route_id.eq('360417').all() or
        not d.historical_site_verified.astype(str).str.lower().eq('false').all()):
        raise ValueError('Site table not the frozen ten unverified nominal stations')
    return d


def offsets(radius_m:float):
    if radius_m==0:
        return [(0.,0.)]
    return [(float(radius_m*math.cos(2*math.pi*i/DIRECTIONS)),
             float(radius_m*math.sin(2*math.pi*i/DIRECTIONS)))
            for i in range(DIRECTIONS)]


def spatial_values(arrs:dict,coordinates:pd.DataFrame,transform):
    first=arrs[2004]
    rr,cc=np.indices(first.shape)
    xgrid=transform.c+(cc+.5)*transform.a
    ygrid=transform.f+(rr+.5)*transform.e
    lons=coordinates.longitude.astype(float).tolist()
    lats=coordinates.latitude.astype(float).tolist()
    xs,ys=project('EPSG:4326','EPSG:5070',lons,lats)
    valid={year:np.isin(img,tuple(ALLOWED)) for year,img in arrs.items()}
    out=[]
    for station,x,y in zip(coordinates.itertuples(index=False),xs,ys):
        for radius in RADII:
            for shift in SHIFTS_M:
                for dx,dy in offsets(shift):
                    ox=float(x+dx);oy=float(y+dy)
                    if (ox-radius<EXPECTED_BBOX[0] or ox+radius>EXPECTED_BBOX[2] or
                        oy-radius<EXPECTED_BBOX[1] or oy+radius>EXPECTED_BBOX[3]):
                        raise ValueError('Shifted circle extends beyond requested source crop')
                    inside=(xgrid-ox)**2+(ygrid-oy)**2 <=radius**2
                    nominal=int(inside.sum())
                    if nominal<30:
                        raise ValueError('Buffer contains too few native pixels')
                    vals={'site_id':str(station.site_id),'stop_number':int(station.stop_number),
                          'radius_m':radius,'shift_m':shift,'dx_m':round(dx,6),'dy_m':round(dy,6),
                          'nominal_pixels':nominal}
                    for year in YEARS:
                        img=arrs[year];good=inside&valid[year]
                        n=int(good.sum());vals[f'valid_{year}']=n/nominal
                        if n/nominal<MIN_VALID:raise ValueError('Invalid water/land spatial coverage')
                        for cls,codes in [('forest',FOREST),('developed',DEVELOPED),
                                          ('agriculture',AGRICULTURE),('wetland',WETLAND),('water',WATER)]:
                            vals[f'{cls}_{year}_pct']=100*(good&np.isin(img,tuple(codes))).sum()/n
                    for y0,y1 in [(2004,2009),(2009,2014),(2004,2014)]:
                        a=arrs[y0];b=arrs[y1];joint=inside&valid[y0]&valid[y1]
                        n=int(joint.sum());
                        if n/nominal<MIN_VALID:raise ValueError('Insufficient paired valid class pixels')
                        f0=np.isin(a,tuple(FOREST));f1=np.isin(b,tuple(FOREST))
                        k=f'{y0}_{y1}'
                        vals[f'changed_{k}']=int((joint&(a!=b)).sum())
                        vals[f'forest_loss_{k}']=int((joint&f0&~f1).sum())
                        vals[f'forest_gain_{k}']=int((joint&~f0&f1).sum())
                        vals[f'forest_to_agri_{k}']=int((joint&f0&np.isin(b,tuple(AGRICULTURE))).sum())
                        vals[f'forest_to_developed_{k}']=int((joint&f0&np.isin(b,tuple(DEVELOPED))).sum())
                        vals[f'net_forest_delta_{k}_pp']=float(100*((joint&f1).sum()-(joint&f0).sum())/n)
                    out.append(vals)
    return pd.DataFrame(out)


def summarize_sensitivity(raw:pd.DataFrame):
    items=[]
    for (site,radius),g in raw.groupby(['stop_number','radius_m'],sort=True):
        if len(g)!=25:raise ValueError('Expected one original centre + 8 shifts at each of 3 displacement radii')
        orig=g[g.shift_m.eq(0)].iloc[0]
        row={'stop_number':int(site),'site_id':str(orig.site_id),'radius_m':int(radius),
             'original_center_forest_pct_2004':orig.forest_2004_pct,
             'original_center_forest_pct_2009':orig.forest_2009_pct,
             'original_center_forest_pct_2014':orig.forest_2014_pct,
             'original_center_net_forest_delta_pp_2004_2014':orig.net_forest_delta_2004_2014_pp,
             'original_center_change_pixels_2004_2014':int(orig.changed_2004_2014),
             'original_center_forest_loss_pixels_2004_2014':int(orig.forest_loss_2004_2014),
             'original_center_forest_gain_pixels_2004_2014':int(orig.forest_gain_2004_2014),
             'original_center_forest_to_agri_pixels_2004_2014':int(orig.forest_to_agri_2004_2014),
             'original_center_forest_to_developed_pixels_2004_2014':int(orig.forest_to_developed_2004_2014)}
        for displacement in SHIFTS_M[1:]:
            z=g[g.shift_m.eq(displacement)]
            delta=z.net_forest_delta_2004_2014_pp
            row[f'delta_min_{displacement}m_pp']=float(delta.min())
            row[f'delta_max_{displacement}m_pp']=float(delta.max())
            row[f'all_negative_{displacement}m']=bool((delta<0).all())
            row[f'all_nonpositive_{displacement}m']=bool((delta<=0).all())
            row[f'all_positive_{displacement}m']=bool((delta>0).all())
            row[f'all_zero_{displacement}m']=bool((delta==0).all())
            row[f'changed_pixels_range_{displacement}m']=f'{int(z.changed_2004_2014.min())}-{int(z.changed_2004_2014.max())}'
        items.append(row)
    return pd.DataFrame(items).sort_values(['radius_m','stop_number']).reset_index(drop=True)


def run(archive:Path,site_csv:Path,outdir:Path):
    arrs,tr,original=read_archive(archive)
    sites=site_coordinates(site_csv,original['original_station_table_sha256'])
    raw=spatial_values(arrs,sites,tr)
    agg=summarize_sensitivity(raw)
    outdir.mkdir(parents=True,exist_ok=True)
    raw.to_csv(outdir/'full_shift_grid.csv',index=False)
    agg.to_csv(outdir/'site_scale_sensitivity.csv',index=False)
    receipt={'analysis':'iowa360417_annual_nlcd_C1V0_center_shift_sensitivity_v18',
             'role':'postreadback_descriptive_geolocation_stress_test_not_confirmatory',
             'source_artifact_sha256':sha(archive.read_bytes()),
             'source_station_sha256':original['original_station_table_sha256'],
             'source_year_sha256':{str(y):original['years'][str(y)]['data_sha256'] for y in YEARS},
             'n_stops':10,'n_buffer_radii':len(RADII),
             'n_shift_centers_per_buffer':25,'n_total_center_buffer_rows':len(raw),
             'years':list(YEARS),'shift_radii_m':list(SHIFTS_M),
             'all_2004_2014_forest_change_is_mapping_proxy':True,
             'data_source_is_C1V0_not_C1V2':True,
             'independent_historical_station_verifications':0,
             'frog_response_read':False,'landcover_confidence_raster_read':False,
             'site_level_250m_30m_consistency_count':int(agg[(agg.radius_m==250)&agg.all_negative_30m].shape[0]),
             'site_level_250m_6m_consistency_count':int(agg[(agg.radius_m==250)&agg.all_negative_6m].shape[0]),
             'pixel_classification_uncertainty_NOT_measured':True,
             'interpretation':'Coordinate displacement stress test only; shift robustness cannot validate class changes against newest collection or independent field checks.'}
    (outdir/'receipt.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
    return raw,agg,receipt


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--artifact-zip',required=True)
    ap.add_argument('--station-csv',required=True)
    ap.add_argument('--outdir',required=True)
    a=ap.parse_args()
    _,agg,receipt=run(Path(a.artifact_zip),Path(a.station_csv),Path(a.outdir))
    print(json.dumps(receipt,indent=2,sort_keys=True))
    print(agg[['stop_number','radius_m','original_center_net_forest_delta_pp_2004_2014',
               'delta_min_6m_pp','delta_max_6m_pp','delta_min_30m_pp','delta_max_30m_pp']].to_string(index=False))

if __name__=='__main__':main()
