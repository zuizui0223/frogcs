#!/usr/bin/env python3
"""Verify MRLC official C1V2 ZIP central directory via HTTP byte ranges.

The remote TIFF may be used in a /vsizip//vsicurl/ workflow only when
compression method for the TIFF is STORED (0). Never download 20 GB blindly.
"""
from __future__ import annotations
import argparse
import json
import re
import struct
from pathlib import Path
from probe_official_nlcd_c1v2 import list_c1v2, request_data, parse_zip_tail

BASE="https://www.mrlc.gov/downloads/sciweb1/shared/mrlc/data-bundles/"
def header(headers,name):
    return next((v for k,v in headers.items() if k.lower()==name.lower()),None)

def inspect(year,official):
    name=official['file']
    url=BASE+name
    out={'year':year,'name':name,'url':url,'size_from_USGS_ScienceBase':official['bytes']}
    try:
        code,headers,tail=request_data(url,"bytes=-65536",65536)
        out['http_status']=code
        out['content_range']=header(headers,'Content-Range')
        out['tail_bytes']=len(tail)
        expected=str(official['bytes'])
        if code!=206 or not out['content_range'] or not out['content_range'].endswith('/'+expected):
            out['status']='fail_closed_bad_byte_range_or_length'
            return out
        tailinfo=parse_zip_tail(tail)
        out.update(tailinfo)
        if not tailinfo.get('zip_end_record_found'):
            out['status']='fail_closed_not_zip'
            return out
        size=tailinfo['central_directory_bytes']
        off=tailinfo['central_directory_offset']
        if size<=0 or size>131072 or off<0 or off+size>official['bytes']:
            out['status']='fail_closed_central_directory_dimensions'
            return out
        code2,h,cd=request_data(url,f"bytes={off}-{off+size-1}",131072)
        if code2!=206 or len(cd)!=size:
            out['status']='fail_closed_central_directory_unavailable'
            return out
        idx=0;files=[]
        while idx<len(cd):
            if cd[idx:idx+4]!=b"PK\x01\x02":
                out['status']='fail_closed_invalid_central_signature'
                return out
            head=struct.unpack_from("<4s6H3I5H2I",cd,idx)
            fnlen,exlen,cmlen=head[10],head[11],head[12]
            name=cd[idx+46:idx+46+fnlen].decode('utf-8','replace')
            files.append({'name':name,'method':head[4],'compressed_bytes':head[8],
                          'uncompressed_bytes':head[9],'local_header_offset':head[16]})
            idx+=46+fnlen+exlen+cmlen
        out['entries']=files
        tiffs=[f for f in files if f['name'].lower().endswith('.tif')]
        out['tiff_stored_random_access_possible']=any(f['method']==0 for f in tiffs)
        out['status']='zip_index_verified'
    except Exception as ex:
        out['status']='probe_error'
        out['error']=type(ex).__name__+': '+str(ex)[:230]
    return out
def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--out',type=Path,required=True)
    args=p.parse_args()
    meta=list_c1v2()
    report={'analysis':'c1v2_public_mrlc_zip_random_access_index_v0_1',
            'all_2001_2015_in_official_inventory':all(y in meta for y in range(2001,2016)),
            'expected_all_year_source_GB':round(sum(meta[y]['bytes'] for y in range(2001,2016))/1e9,3),
            'no_frog_outcomes_read':True,'all_zips_downloaded':False,
            'probes':[inspect(y,meta[y]) for y in (2001,2008,2015)]}
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print(json.dumps(report,indent=2,sort_keys=True))
if __name__=='__main__':main()
