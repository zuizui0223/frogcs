#!/usr/bin/env python3
"""Find verified USGS ScienceBase Annual NLCD C1V2 ZIPs; probe range/ZIP layout.

NO frog calling data. Metadata and <=64 KiB end-of-file + <=256 KiB
central directory per selected year, never download a full ~1.4 GB ZIP.
"""
from __future__ import annotations
import argparse
import json
import re
import struct
import urllib.error
import urllib.request
from pathlib import Path

ITEM_ID = "697b9279b66b0197c3043cc3"
METADATA_URL = f"https://www.sciencebase.gov/catalog/item/{ITEM_ID}?format=json"
UA = "frogcs-landcover-c1v2-source-audit/0.1"

def request_data(url, byte_range=None, cap=262144):
    headers={"User-Agent":UA,"Accept":"application/json" if byte_range is None else "*/*"}
    if byte_range is not None: headers["Range"]=byte_range
    with urllib.request.urlopen(urllib.request.Request(url,headers=headers),timeout=35) as response:
        code=int(response.status)
        if byte_range is not None and code != 206:
            return code,{"Content-Range":response.headers.get("Content-Range")},b""
        raw=response.read(cap+1)
        if len(raw)>cap: raise RuntimeError("size cap exceeded")
        return code,dict(response.headers),raw

def list_c1v2():
    _,_,content=request_data(METADATA_URL,None,cap=2_000_000)
    raw=json.loads(content)
    if raw.get("id")!=ITEM_ID or "Collection 1.2 Land Cover" not in raw.get("title",""):
        raise RuntimeError("metadata does not identify official C1.2 Land Cover")
    files={}
    for f in raw.get("files",[]):
        match=re.fullmatch(r"Annual_NLCD_LndCov_(20\d\d)_CU_C1V2\.zip",f.get("name",""))
        if not match: continue
        y=int(match.group(1))
        files[y]={"file":f["name"],"bytes":int(f["size"]),
                  "download_uri":f.get("downloadUri"),
                  "date_uploaded":f.get("dateUploaded"),"metadata_item_id":ITEM_ID}
    if any(y not in files for y in range(2001,2016)):
        raise RuntimeError("not all 2001-2015 C1V2 years found in official metadata")
    return files

def parse_zip_tail(data):
    pos=data.rfind(b"PK\x05\x06")
    if pos<0 or pos+22>len(data):
        return {"zip_end_record_found":False}
    eocd=struct.unpack_from("<4s4H2IH",data,pos)
    return {"zip_end_record_found":True,"entries":eocd[4],
            "central_directory_bytes":eocd[5],"central_directory_offset":eocd[6],
            "zip_comment_bytes":eocd[7]}

def inspect_year(entry):
    result={"year":int(entry["file"].split("_")[3]),"file":entry["file"],
            "bytes":entry["bytes"],"source_item":ITEM_ID,"distribution":entry["download_uri"]}
    try:
        code,headers,tail=request_data(entry["download_uri"],"bytes=-65536",65536)
        result["http_status"]=code
        result["content_range"]=headers.get("Content-Range")
        result["tail_bytes_read"]=len(tail)
        if code!=206: return result
        if not result["content_range"] or not result["content_range"].endswith("/"+str(entry["bytes"])):
            result["error"]="source length does not match metadata";return result
        result.update(parse_zip_tail(tail))
        if not result.get("zip_end_record_found"):return result
        sz=result["central_directory_bytes"]
        off=result["central_directory_offset"]
        if sz>262144 or off<0 or off+sz>entry["bytes"]:
            result["error"]="central directory too large or offset invalid";return result
        _,h,cd=request_data(entry["download_uri"],f"bytes={off}-{off+sz-1}",262144)
        result["central_directory_range"]=h.get("Content-Range")
        files=[]
        p=0
        while p<len(cd):
            if cd[p:p+4]!=b"PK\x01\x02": break
            header=struct.unpack_from("<4s6H3I5H2I",cd,p)
            method=header[4]
            compressed,uncompressed=header[8],header[9]
            name_len,ext_len,comment_len=header[10],header[11],header[12]
            name=cd[p+46:p+46+name_len].decode("utf-8","replace")
            files.append({"file":name,"zip_method":method,
                          "compressed_bytes":compressed,"uncompressed_bytes":uncompressed})
            p+=46+name_len+ext_len+comment_len
        result["central_directory_files"]=files[:30]
        result["n_central_directory_files"]=len(files)
        result["tiff_random_access_possible"]=any(x["file"].lower().endswith(".tif") and x["zip_method"]==0 for x in files)
    except Exception as ex:
        result["error"]=type(ex).__name__+": "+str(ex)[:200]
    return result

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    output={"analysis":"usgs_sciencebase_official_c1v2_zip_random_access_v0_1",
            "version":"Annual NLCD Collection 1.2","source":METADATA_URL,
            "no_calling_data_read":True,"full_zips_downloaded":False}
    try:
        matches=list_c1v2()
        output["all_study_years_listed"]=True
        output["study_years"]=list(range(2001,2016))
        output["total_zip_bytes_2001_2015"]=sum(matches[y]["bytes"] for y in range(2001,2016))
        output["selected_year_probes"]=[inspect_year(matches[y]) for y in (2001,2008,2015)]
    except Exception as ex:
        output["error"]=type(ex).__name__+": "+str(ex)[:250]
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(output,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(output,indent=2,sort_keys=True))
if __name__=="__main__":
    main()
