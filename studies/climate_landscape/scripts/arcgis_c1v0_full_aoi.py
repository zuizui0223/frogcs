#!/usr/bin/env python3
"""Response-blind, source-verified Annual NLCD C1V0 full-AOI pilot.

Read-only ArcGIS ImageServer. Output is an environmental source screen for the
nominally matching Iowa 360417 DNR and NAAMP coordinates, not evidence of
historical physical-site continuity and not a C1.2 source.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

import numpy as np
import pandas as pd
import rasterio
from rasterio.warp import transform as project

BASE = 'https://di-nlcd.img.arcgis.com/arcgis/rest/services/USA_NLCD_Annual_LandCover/ImageServer'
YEARS = (2004, 2009, 2014)
BBOX = (179220, 2044410, 184320, 2056680)  # EPSG:5070, exact 30m grid
WIDTH = (BBOX[2]-BBOX[0]) // 30
HEIGHT = (BBOX[3]-BBOX[1]) // 30
CODES = {11,12,21,22,23,24,31,41,42,43,52,71,81,82,90,95}
FOREST = {41,42,43}
DEVELOPED = {21,22,23,24}
AGRICULTURE = {81,82}
WETLAND = {90,95}
WATER = {11}
MAX_BYTES = 4_000_000
RETRIES = 4


def sha(data):
    return hashlib.sha256(data).hexdigest()


def source_request(endpoint: str, params: dict, limit: int = MAX_BYTES):
    if endpoint not in ('', '/query', '/exportImage'):
        raise ValueError('Only frozen ArcGIS endpoints allowed')
    url = BASE + endpoint + '?' + urllib.parse.urlencode(params)
    last = None
    for attempt in range(RETRIES):
        try:
            req = urllib.request.Request(url, headers={
                'User-Agent': 'frogcs-360417-annual-NLCD-C1V0-full-AOI-20261008',
                'Accept': 'application/json, image/tiff'})
            with urllib.request.urlopen(req, timeout=115) as response:
                final = urllib.parse.urlparse(response.geturl())
                if final.scheme != 'https' or final.hostname != 'di-nlcd.img.arcgis.com':
                    raise ValueError('Raster service redirects to untrusted host')
                raw = response.read(limit+1)
                if len(raw) > limit:
                    raise ValueError('Response exceeds bounded raster crop limit')
                return raw, response.headers.get('Content-Type', '')
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as exc:
            last = exc
            if isinstance(exc, urllib.error.HTTPError) and exc.code not in (408,429,500,502,503,504):
                break
            if attempt < RETRIES-1:
                time.sleep(4 * (attempt+1))
    raise RuntimeError(f'Original service unavailable after bounded retries: {type(last).__name__}: {str(last)[:160]}')


def source_identity_for_year(year: int):
    raw, mime = source_request('/query', {
        'where': f'Year={year}', 'outFields':'OBJECTID,Name,Year,Version',
        'returnGeometry':'false', 'f':'json'}, 2_000_000)
    obj = json.loads(raw)
    if obj.get('error'):
        raise ValueError('ArcGIS item query returned error')
    rows = [z.get('attributes', {}) for z in obj.get('features', [])]
    if len(rows) != 1:
        raise ValueError(f'Expected exactly one year {year} raster item; found {len(rows)}')
    row = rows[0]
    if (int(row.get('Year',-1)) != year or
        not str(row.get('Name','')).endswith(f'_LndCov_{year}_CU_C1V0') or
        '1.0' not in str(row.get('Version',''))):
        raise ValueError('Raster item is not original homogeneous Collection 1.0 (C1V0)')
    if not isinstance(row.get('OBJECTID'), int):
        raise ValueError('Raster OBJECTID missing')
    return row, sha(raw)


def request_year(year: int):
    if year not in YEARS:
        raise ValueError('Only original 2004/2009/2014 years allowed')
    row, query_hash = source_identity_for_year(year)
    rule = {'mosaicMethod':'esriMosaicByAttribute',
            'where':f'OBJECTID={row["OBJECTID"]} AND Year={year}',
            'sortField':'Year','sortValue':year,'ascending':True}
    params = {'bbox':','.join(str(x) for x in BBOX),
              'bboxSR':'5070', 'imageSR':'5070',
              'size':f'{WIDTH},{HEIGHT}', 'format':'tiff',
              'pixelType':'U8',
              'interpolation':'RSP_NearestNeighbor',
              'mosaicRule':json.dumps(rule,separators=(',',':')),
              'renderingRule':json.dumps({'rasterFunction':'None'}),
              'f':'image'}
    data, mime = source_request('/exportImage', params)
    if data[:4] not in (b'II*\x00',b'MM\x00*',b'II+\x00',b'MM\x00+'):
        raise ValueError('ImageServer did not return native categorical TIFF: '+data[:150].decode('utf-8','replace'))
    return data, {'name':row['Name'],'version':row['Version'],
                  'objectid':row['OBJECTID'],'query_sha256':query_hash,'tiff_sha256':sha(data),
                  'bytes':len(data),'mime':mime,'product_series':'C1V0',
                  'service_is_not_C1V2':True}


def inspect(path: Path):
    with rasterio.open(path) as src:
        if (src.count != 1 or src.crs is None or src.crs.to_epsg() != 5070 or
            src.width != WIDTH or src.height != HEIGHT or
            not all(abs(v-30)<1e-6 for v in src.res)):
            raise ValueError('Unexpected raster dimensions, CRS, resolution or band count')
        t = src.transform
        if (abs(t.a-30)>1e-8 or abs(t.e+30)>1e-8 or abs(t.c-BBOX[0])>1e-8 or
            abs(t.f-BBOX[3])>1e-8 or abs(t.b)>1e-9 or abs(t.d)>1e-9):
            raise ValueError('Source image not on precisely frozen and shared pixel grid')
        img = src.read(1)
        invalid_codes = set(np.unique(img).astype(int)) - CODES - {0,255}
        if invalid_codes:
            raise ValueError('Unexpected raw thematic codes: '+str(invalid_codes))
        valid = np.isin(img, sorted(CODES))
        c,n = np.unique(img[valid],return_counts=True)
        info = {'pixel_codes':sorted(int(x) for x in np.unique(img)),
                'class_histogram':{str(int(x)):int(y) for x,y in zip(c,n)},
                'valid_fraction':float(valid.mean()),
                'n_missing_or_unknown_pixels':int((~valid).sum()),
                'pixel_shape':list(img.shape),
                'transform':list(t)[:6],
                'dtype':str(img.dtype),
                'original_raster_nodata':src.nodata}
    return img, valid, info


def summarize_layers(layer: dict, sites: pd.DataFrame):
    yy,xx = np.indices((HEIGHT,WIDTH))
    centers_x = BBOX[0] + (xx+0.5)*30.0
    centers_y = BBOX[3] - (yy+0.5)*30.0
    px,py = project('EPSG:4326','EPSG:5070',sites.longitude.tolist(),sites.latitude.tolist())
    results = []
    keys = sorted(layer)
    for s,x,y in zip(sites.itertuples(index=False),px,py):
        for radius in (250,1000):
            # The entire buffer must be represented in the downloaded AOI.
            if (x-radius < BBOX[0] or x+radius > BBOX[2] or
                y-radius < BBOX[1] or y+radius > BBOX[3]):
                raise ValueError('Station buffer truncated by nominal full-AOI crop')
            circle = (centers_x-x)**2+(centers_y-y)**2 <= radius**2
            nominal = int(circle.sum())
            if nominal < 35:raise ValueError('Insufficient 30m nominal circle coverage')
            row={'site_id':str(s.site_id),'stop_number':int(s.stop_number),
                 'radius_m':radius,'sampled_nominal_pixels':nominal,
                 'years':{},'pairs':{},'historical_physical_site_verified':False}
            for year in keys:
                img, valid = layer[year]
                selected=valid&circle
                n=int(selected.sum())
                classes={
                    'forest':FOREST,'developed':DEVELOPED,'agriculture':AGRICULTURE,
                    'wetland':WETLAND,'water':WATER}
                row['years'][str(year)]={
                    'valid_pixels':n,'valid_fraction':n/nominal,
                    **{group+'_fraction_of_valid':float((np.isin(img,list(classeset))&selected).sum()/n) if n else None
                       for group,classeset in classes.items()}}
            for i,early in enumerate(keys):
                for late in keys[i+1:]:
                    first,valid1=layer[early]; last,valid2=layer[late]
                    both=circle&valid1&valid2
                    n=int(both.sum()); sufficient=n>=0.8*nominal
                    metrics={'pairwise_valid_pixels':n,'pairwise_valid_fraction':n/nominal,
                             'passes_80pct':bool(sufficient)}
                    if sufficient:
                        f0=np.isin(first,list(FOREST));f1=np.isin(last,list(FOREST))
                        metrics.update({
                            'changed_class_pixels':int((both&(first!=last)).sum()),
                            'forest_loss_pixels':int((both&f0&~f1).sum()),
                            'forest_gain_pixels':int((both&~f0&f1).sum()),
                            'forest_to_developed_pixels':int((both&f0&np.isin(last,list(DEVELOPED))).sum()),
                            'forest_to_agriculture_pixels':int((both&f0&np.isin(last,list(AGRICULTURE))).sum()),
                            'wetland_to_nonwetland_pixels':int((both&np.isin(first,list(WETLAND))&~np.isin(last,list(WETLAND))).sum()),
                            'nonwetland_to_wetland_pixels':int((both&~np.isin(first,list(WETLAND))&np.isin(last,list(WETLAND))).sum()),
                        })
                        metrics['forest_mass_balance_verified']=(
                            metrics['forest_gain_pixels']-metrics['forest_loss_pixels'] ==
                            int((both&f1).sum())-int((both&f0).sum()))
                        if not metrics['forest_mass_balance_verified']:
                            raise ValueError('Forest change mass balance invariant violated')
                    row['pairs'][f'{early}_{late}']=metrics
            results.append(row)
    if len(results)!=20:raise ValueError('Expected ten sites at two buffer radii')
    return results


def run(output:Path, sites_path:Path):
    sites = pd.read_csv(sites_path,dtype={'route_id':str,'site_id':str})
    if (len(sites)!=10 or sorted(sites.stop_number.tolist())!=list(range(1,11)) or
        not sites.historical_site_verified.astype(str).str.lower().eq('false').all()):
        raise ValueError('Station source file not frozen or invalid field-verification flag')
    output.mkdir(parents=True,exist_ok=True)
    receipt={'analysis':'iowa360417_arcgis_homogeneous_C1V0_full_AOI_source_only_v17',
        'status':'NOT_STARTED','years_required':list(YEARS),
        'source':'https://di-nlcd.img.arcgis.com/arcgis/rest/services/USA_NLCD_Annual_LandCover/ImageServer',
        'data_is_C1_2':False,'data_is_C1_0':True,
        'station_source_sha256':sha(sites_path.read_bytes()),
        'historical_field_site_identity_externally_verified':0,
        'frog_outcomes_read':False,'confidence_product_read':False,
        'pixelwise_change_is_descriptive_not_biological':True,
        'requested_epsg5070_bbox':list(BBOX),
        'full_aoi_image_size':[WIDTH,HEIGHT],
        'original_year_files':{},'site_buffers':[]}
    layers={}
    for year in YEARS:
        try:
            tiff,ident = request_year(year)
            target=output / f'iowa360417_NLCD_C1V0_{year}_30m.tif'
            target.write_bytes(tiff)
            img,valid,qa=inspect(target)
            receipt['original_year_files'][str(year)]={**ident,**qa}
            layers[year]=(img,valid)
            receipt['status']='PARTIAL_SOURCE_ONLY'
            (output/'receipt.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
            print(json.dumps({'year':year,'bytes':len(tiff),
                'valid_fraction':qa['valid_fraction'],'product':ident['name']}),flush=True)
        except Exception as e:
            receipt['source_failures']=receipt.get('source_failures',[])+[{
                'year':year,'error_type':type(e).__name__,'error':str(e)[:500]}]
            (output/'receipt.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
            print(json.dumps({'year':year,'status':'FAILED','error_type':type(e).__name__,
                'error':str(e)[:120]}),flush=True)
    if len(layers)>=2:
        receipt['site_buffers']=summarize_layers(layers,sites)
        receipt['status']='THREE_YEAR_RAW_C1V0_SOURCE_ONLY' if len(layers)==3 else 'PARTIAL_TWO_YEAR_C1V0_SOURCE_ONLY'
    else:
        receipt['status']='SOURCE_UNAVAILABLE'
    (output/'receipt.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'status':receipt['status'],'n_complete_years':len(layers),
          'n_site_buffers':len(receipt['site_buffers'])}))
    if len(layers)<2:
        raise RuntimeError('No usable multi-year same-pixel NLCD source for this pilot')


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--out',required=True)
    parser.add_argument('--stations',required=True)
    args=parser.parse_args()
    run(Path(args.out),Path(args.stations))

if __name__=='__main__':main()
