#!/usr/bin/env python3
"""Metadata & byte-range-only smoke check for USGS NLCD C1V1 public STAC asset.
Historical C1V1 is NOT interchangeable with the desired C1V2 ecological data.
No frog outcomes are loaded. Never transfer an entire raster on an HTTP 200.
"""
import argparse
import json
import urllib.error
import urllib.request
from pathlib import Path

ITEM='Annual_NLCD_LndCov_2001_CU_C1V1'
STAC='https://api.water.usgs.gov/gdp/pygeoapi/stac/stac-collection/nlcd/nlcd-LndCov/'+ITEM+'?f=json'
UA='frogcs-outcome-blind-landcover-source-check/0.1'

def load_stac():
    req=urllib.request.Request(STAC,headers={'User-Agent':UA,'Accept':'application/json'})
    with urllib.request.urlopen(req,timeout=15) as resp:
        data=json.load(resp)
    if data.get('id')!=ITEM or 'Collection 1.1' not in str(data.get('properties',{}).get('description','')):
        raise ValueError('historical NLCD STAC item/version mismatch')
    asset=data['assets']['tif-s3-osn']['href']
    if asset!='s3://hytest/nlcd/annual-nlcd-cu-c1v1/mosaic/'+ITEM+'.tif':
        raise ValueError('unexpected historical asset URI')
    return data,'https://usgs.osn.mghpcc.org/'+asset[5:]

def small_range(url):
    result={'range_requested':'bytes=0-1023','status':None,'bytes_read':0,'raw_tiff_magic':None}
    req=urllib.request.Request(url,headers={'Range':'bytes=0-1023','User-Agent':UA})
    try:
        with urllib.request.urlopen(req,timeout=20) as resp:
            result['status']=int(resp.status)
            result['content_range']=resp.headers.get('Content-Range')
            result['content_type']=resp.headers.get('Content-Type')
            if result['status']==206:
                b=resp.read(1024)
                result['bytes_read']=len(b)
                result['raw_tiff_magic']=b[:4] in (b'II*\x00',b'MM\x00*',b'II+\x00',b'MM\x00+')
            else:
                result['detail']='range unsupported; skipped full raster'
    except (urllib.error.HTTPError,urllib.error.URLError,TimeoutError) as ex:
        result['detail']=type(ex).__name__+': '+str(getattr(ex,'code','')) 
    return result

def main():
    a=argparse.ArgumentParser(description=__doc__)
    a.add_argument('--out',type=Path,required=True)
    args=a.parse_args()
    receipt={'analysis':'nlcd_historical_raster_source_probe_v0_1',
             'desired_final_version':'USGS Annual NLCD Collection 1.2',
             'pilot_source_version':'USGS Annual NLCD Collection 1.1',
             'not_final_ecological_source':True,
             'frog_outcomes_read':False,
             'whole_raster_downloaded':False,
             'stac_url':STAC}
    try:
        metadata,url=load_stac()
        receipt.update({'stac_verified':True,
                        'original_asset_uri':metadata['assets']['tif-s3-osn']['href'],
                        'test_url':url,'probe':small_range(url)})
    except Exception as ex:
        receipt.update({'stac_verified':False,
                        'error':type(ex).__name__+': '+str(ex)[:150]})
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print(json.dumps(receipt,indent=2,sort_keys=True))
if __name__=='__main__':main()
