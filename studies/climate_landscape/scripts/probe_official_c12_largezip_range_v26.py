#!/usr/bin/env python3
"""Probe official NLCD C1V2 land-cover 2012 ZIP central directory via HTTP Range.

Bounded metadata-only transfer. No national ZIP download, raw image pixel,
AWS requester-pays, frog calling response or anthropogenic causal claim.
"""
from __future__ import annotations
import argparse,hashlib,json,re,struct,urllib.parse,urllib.request
from pathlib import Path
ID="697b9279b66b0197c3043cc3"
FILENAME="Annual_NLCD_LndCov_2012_CU_C1V2.zip"
METADATA=f"https://www.sciencebase.gov/catalog/item/{ID}?format=json"
MAX_TAIL=131072
def getinfo():
    request=urllib.request.Request(METADATA,headers={'User-Agent':'frogcs-c12-archive-range-preflight/0.1'})
    with urllib.request.urlopen(request,timeout=55) as s:
        raw=s.read(500000)
    obj=json.loads(raw)
    if obj.get("id")!=ID or "Collection 1.2 Land Cover" not in obj.get("title",""):
        raise ValueError("Source item ID and C1V2 family mismatch")
    selected=[x for x in obj.get("files",[]) if x.get("name")==FILENAME]
    if len(selected)!=1:raise ValueError("Exactly one official 2012 C1V2 ZIP is required")
    item=selected[0]
    size=int(item.get("size",0))
    if not 1_000_000_000<size<2_000_000_000:raise ValueError("Unfrozen archive size")
    u=item.get("downloadUri")
    host=urllib.parse.urlparse(u).hostname if u else None
    if not u or not u.startswith("https://") or host not in ("sciencebase.usgs.gov","www.sciencebase.gov","sciencebase.gov"):
        raise ValueError("Unexpected original official ScienceBase download URL host")
    return {"official_source_item_id":ID,"source_name":FILENAME,
        "official_metadata_sha256":hashlib.sha256(raw).hexdigest(),
        "listed_zip_bytes":size,"download_url_host":host},u
def metadata_tail(url,total_expected):
    req=urllib.request.Request(url,headers={"Range":f"bytes=-{MAX_TAIL}",
        "User-Agent":"frogcs-c12-archive-central-directory-only/0.1"})
    with urllib.request.urlopen(req,timeout=65) as s:
        status=int(s.status)
        final=urllib.parse.urlparse(s.geturl())
        ctype=s.headers.get("Content-Type")
        content_range=s.headers.get("Content-Range","")
        raw=s.read(MAX_TAIL+1)
    info={"http_status":status,"final_host":final.hostname,
          "content_type":ctype,"content_range":content_range,
          "payload_bytes":len(raw),"payload_sha256":hashlib.sha256(raw).hexdigest(),
          "range_transfer_limit":MAX_TAIL}
    if len(raw)>MAX_TAIL or status!=206:raise ValueError("Server did not honor bounded byte range")
    cr=re.fullmatch(r"bytes (\d+)-(\d+)/(\d+)",content_range)
    if not cr:raise ValueError("Missing standard Content-Range")
    start,end,total=map(int,cr.groups())
    info.update({'actual_download_zip_size_from_Content_Range':total,
                 'catalog_zip_size':total_expected,
                 'range_start':start,'range_end':end,
                 'size_mismatch':total!=total_expected,
                 'range_payload_mismatch':end-start+1!=len(raw)})
    if total!=total_expected or end-start+1!=len(raw):
        info['status']='OFFICIAL_CATALOG_VS_RANGE_SIZE_MISMATCH_NO_PIXELS'
        return info
    idx=raw.rfind(b"PK\x05\x06")
    if idx<0:raise ValueError("ZIP End of Central Directory missing from bounded tail")
    if idx+22>len(raw):raise ValueError("Truncated ZIP EOCD")
    signature,disk,disk_cd,entries_disk,entries,cd_size,cd_off,comment=struct.unpack_from("<4s4H2LH",raw,idx)
    info.update({"zip_entries":entries,"central_directory_size":cd_size,
                 "central_directory_offset":cd_off,
                 "zip_comment_length":comment})
    if entries==65535 or cd_off==0xffffffff:
        info["zip64_central_directory"]="needed_not_implemented"
        return info
    startpos=cd_off-start
    if startpos<0 or startpos+cd_size>len(raw):
        info["status"]="CENTRAL_DIRECTORY_OUTSIDE_BOUNDED_TAIL"
        return info
    files=[]
    p=startpos
    for _ in range(entries):
        if raw[p:p+4]!=b"PK\x01\x02":raise ValueError("ZIP central entry corruption")
        method,packed,unpacked=struct.unpack_from("<H",raw,p+10)[0],struct.unpack_from("<L",raw,p+20)[0],struct.unpack_from("<L",raw,p+24)[0]
        namelen,extralen,commentlen=struct.unpack_from("<3H",raw,p+28)
        name=raw[p+46:p+46+namelen].decode("utf8","replace")
        files.append({"name":name[:220],"compression_method":method,
            "packed_bytes":packed,"uncompressed_bytes":unpacked,
            "uncompressed_tiff_is_range_addressable_without_ZIP_inflation":method==0 and name.lower().endswith(".tif")})
        p+=46+namelen+extralen+commentlen
    info["zip_members"]=files
    info["has_raw_stored_tiff"]=any(x["uncompressed_tiff_is_range_addressable_without_ZIP_inflation"] for x in files)
    info["status"]="ZIP_CENTRAL_DIRECTORY_INSPECTED_NO_LANDCOVER_PIXELS"
    return info
def main():
    p=argparse.ArgumentParser();p.add_argument("--out",required=True);a=p.parse_args()
    receipt={"analysis":"official_c12_landcover_2012_large_zip_bounded_range_v26",
             "status":"UNRESOLVED","source_only":True,"counts_csv_accessed":False,
             "image_pixel_values_read":False,"national_archive_downloaded":False,
             "aws_requester_pays_called":False}
    try:
        meta,url=getinfo()
        receipt.update(meta)
        receipt.update(metadata_tail(url,meta["listed_zip_bytes"]))
    except Exception as e:
        receipt.update({"status":"ZIP_RANGE_SOURCE_UNRESOLVED",
              "error_type":type(e).__name__,"error":str(e)[:300]})
    target=Path(a.out);target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n")
    print(json.dumps(receipt,indent=2,sort_keys=True))
if __name__=="__main__":main()
