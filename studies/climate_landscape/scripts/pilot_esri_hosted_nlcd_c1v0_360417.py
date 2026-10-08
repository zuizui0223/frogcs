#!/usr/bin/env python3
"""Independent environmental 2004/2009/2014 NLCD Collection 1.0 pixel pilot.

Read-only USGS-authored, Esri-hosted public ImageServer. The service per-year
catalog labels these 2004/2014 rasters as CU_C1V0, i.e. Collection 1.0,
NOT the desired current Collection 1.2. Source-only; no frog responses read.
A later state map cannot independently verify 2001-2015 physical continuity.
"""
from __future__ import annotations
import argparse, hashlib, importlib.util, json, time
import urllib.error, urllib.parse, urllib.request
from pathlib import Path
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
HELPER=ROOT/'scripts/pilot_official_nlcd_wcs_360417.py'
_spec=importlib.util.spec_from_file_location('raw_pixels',HELPER)
helper=importlib.util.module_from_spec(_spec);_spec.loader.exec_module(helper)
SOURCE=ROOT/'reference_routes/iowa_dnr_360417_source_only_stops_v16.csv'
BASE='https://di-nlcd.img.arcgis.com/arcgis/rest/services/USA_NLCD_Annual_LandCover/ImageServer'
YEARS=(2004,2009,2014)
BBOX=helper.BBOX
SIZE=((BBOX[2]-BBOX[0])//30,(BBOX[3]-BBOX[1])//30)
MAX_BYTES=8_000_000


def fetch(url,params):
    if not url.startswith(BASE) or urllib.parse.urlparse(url).hostname!='di-nlcd.img.arcgis.com':
        raise ValueError('Non-authoritative server endpoint')
    full=url+'?'+urllib.parse.urlencode(params)
    error=None
    for attempt in range(4):
        try:
            request=urllib.request.Request(full,headers={'User-Agent':'frogcs-source-only-nlcd-c1v0-2026/1.6'})
            with urllib.request.urlopen(request, timeout=100) as response:
                if urllib.parse.urlparse(response.geturl()).hostname!='di-nlcd.img.arcgis.com':
                    raise ValueError('Unexpected redirect outside public ImageServer')
                blob=response.read(MAX_BYTES+1)
                content_type=response.headers.get('Content-Type','')
            if len(blob)>MAX_BYTES:raise ValueError('Exceeded fixed source crop byte limit')
            return blob,content_type
        except (urllib.error.URLError, TimeoutError, ConnectionError) as e:
            error=e
            if attempt<3:time.sleep((attempt+1)*3)
    raise RuntimeError(f'Public image server unavailable after four fixed attempts: {type(error).__name__}')


def record_for_year(year):
    if year not in YEARS:raise ValueError('Frozen study year required')
    data,mime=fetch(BASE+'/query',{'where':f'Year={year}','outFields':'OBJECTID,Name,Year,Version',
                                   'returnGeometry':'false','f':'json'})
    obj=json.loads(data)
    if obj.get('error'):raise ValueError('Image catalog error: '+str(obj['error'])[:200])
    items=[r['attributes'] for r in obj.get('features',[]) if r.get('attributes')]
    if len(items)!=1 or int(items[0]['Year'])!=year:
        raise ValueError('Not exactly one year-specific catalog raster')
    record=items[0]
    if not str(record['Name']).endswith(f'{year}_CU_C1V0') or '1.0' not in str(record['Version']):
        raise ValueError('Source is not declared annual NLCD Collection 1.0')
    return {'year':year,'OBJECTID':int(record['OBJECTID']),
            'catalog_source_name':str(record['Name']),'catalog_version':str(record['Version']),
            'catalog_query_sha256':hashlib.sha256(data).hexdigest()}


def request_raster(year):
    rule={'mosaicMethod':'esriMosaicByAttribute','where':f'Year={year}',
          'sortField':'Year','sortValue':year,'ascending':True}
    params={'bbox':','.join(str(z) for z in BBOX),'bboxSR':'5070','imageSR':'5070',
            'size':f'{SIZE[0]},{SIZE[1]}','format':'tiff','pixelType':'U8',
            'mosaicRule':json.dumps(rule,separators=(',',':')),
            'renderingRule':json.dumps({'rasterFunction':'None'}),
            'f':'image'}
    blob,mime=fetch(BASE+'/exportImage',params)
    if blob[:4] not in (b'II*\x00',b'MM\x00*',b'II+\x00',b'MM\x00+'):
        raise ValueError('ExportImage not TIFF: '+blob[:160].decode('utf8','replace'))
    return blob,mime


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--output-dir',required=True)
    args=parser.parse_args()
    output=Path(args.output_dir);output.mkdir(parents=True,exist_ok=True)
    station=pd.read_csv(SOURCE,dtype={'route_id':str,'site_id':str})
    if len(station)!=10 or sorted(station.stop_number.to_list())!=list(range(1,11)) or \
       station.historical_site_verified.astype(str).str.lower().ne('false').any():
        raise ValueError('Current state-map nominal site table invalid or wrongly verified')
    report={'analysis':'iowa_360417_arcgis_image_service_collection_1_0_source_only_v16',
            'source_url':BASE,'study_years':list(YEARS),'study_bbox_epsg5070':list(BBOX),
            'source_version':'Annual_NLCD_Collection_1.0_CU_C1V0',
            'not_collection_1_2':True,'not_nlcd_1_2_model_compatible':True,
            'site_identity_historically_independently_verified':0,'frog_counts_read':False,
            'original_station_table_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            'years':{},'status':'incomplete','errors':{}}
    layers={}
    for year in YEARS:
        try:
            catalog=record_for_year(year)
            img,mime=request_raster(year)
            path=output/f'arcgis_nlcd_C1V0_{year}_iowa_360417.tif'
            path.write_bytes(img)
            array,affine,good,meta=helper.inspect_tif(path)
            if array.shape!=(SIZE[1],SIZE[0]):
                raise ValueError('Returned raster shape disagrees with predeclared 30m grid')
            layers[year]=(array,affine,good,meta)
            report['years'][str(year)]={'catalog':catalog,'data_sha256':hashlib.sha256(img).hexdigest(),
                     'bytes':len(img),'mime_type':mime,'raster':meta}
            print(json.dumps({'year':year,'categorical_source_verified':True,'codes':meta['pixel_codes']}),flush=True)
        except Exception as e:
            report['errors'][str(year)]={'exception_type':type(e).__name__,
                                          'error_detail':str(e)[:400]}
            print(json.dumps({'year':year,'source_error':type(e).__name__,'detail':str(e)[:200]}),flush=True)
        (output/'receipt.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    if sorted(layers)==list(YEARS):
        report['site_radii']=helper.summarize_pixels(layers,station)
        report['status']='all_three_years_raw_C1V0_pixels_available_environment_only'
    else:
        report['status']='incomplete_original_C1V0_years_do_not_fit_any_biological_model'
    (output/'receipt.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    if not layers:
        raise RuntimeError('No annual categorical land cover retrieved')
    print(json.dumps({'status':report['status'],'number_of_valid_years':len(layers),
                      'site_buffers':len(report.get('site_radii',[]))}),flush=True)

if __name__=='__main__':main()
