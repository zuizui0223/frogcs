#!/usr/bin/env python3
"""Official Annual NLCD C1.2 categorical+confidence access preflight.

Read-only / response-blind. No frog outcomes or imagery downloaded. Metadata
from official ScienceBase, Annual NLCD WMS capabilities from the link on the
MRLC federal data-services page, and a *small* guarded binary signature probe.
A WMS map is NOT automatically a categorical GeoTIFF.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

COVER_ITEM="697b9279b66b0197c3043cc3"
CONF_ITEM="697b92b8b66b0197c3043cc7"
YEAR=2012
WMS={
  "landcover":"https://dmsdata.cr.usgs.gov/geoserver/mrlc_Land-Cover-Native_conus_year_data/wms",
  "confidence":"https://dmsdata.cr.usgs.gov/geoserver/mrlc_Land-Cover-Confidence-Native_conus_year_data/wms"
}
OFFICIAL_HOSTS={"www.sciencebase.gov","sciencebase.gov","sciencebase.usgs.gov",
                "dmsdata.cr.usgs.gov"}
ACCEPTABLE_VERSION=("C1V2","Collection 1.2")
MAX_META=4_000_000
MAX_WMS=5_000_000
MAX_BINARY=8192

def read_limited(url,max_size,*,headers=None,timeout=35):
    parsed=urllib.parse.urlsplit(url)
    if parsed.scheme!="https" or parsed.hostname not in OFFICIAL_HOSTS:
        raise ValueError(f"nonofficial requested host {parsed.hostname}")
    req=urllib.request.Request(url,headers={"User-Agent":"frogcs-official-C1V2-source-only/1.0",
                                           **(headers or {})})
    with urllib.request.urlopen(req,timeout=timeout) as r:
        raw=r.read(max_size+1)
        status=r.status
        final=urllib.parse.urlsplit(r.geturl())
        ctype=r.headers.get("Content-Type","")
        crange=r.headers.get("Content-Range","")
    if final.scheme!="https" or final.hostname not in OFFICIAL_HOSTS:
        raise ValueError("nonofficial redirect target")
    if len(raw)>max_size:
        raise ValueError("unexpectedly large upstream response: NO unbounded downloads")
    return {"raw":raw,"status":status,"content_type":ctype,
            "content_range":crange,"actual_host":final.hostname,
            "sha256":hashlib.sha256(raw).hexdigest(),"bytes":len(raw)}

def check_archive_metadata(product,item_id,prefix):
    url=f"https://www.sciencebase.gov/catalog/item/{item_id}?format=json"
    r=read_limited(url,MAX_META)
    data=json.loads(r["raw"])
    title=str(data.get("title") or "")
    if data.get("id")!=item_id or "Collection 1.2" not in title:
        raise ValueError(f"incorrect USGS Collection 1.2 item identity: {product}")
    name=f"Annual_NLCD_{prefix}_{YEAR}_CU_C1V2.zip"
    options=[f for f in data.get("files",[]) if f.get("name")==name]
    if len(options)!=1:
        raise ValueError(f"missing or duplicated C1V2 archive {name}")
    row=options[0]
    size=int(row.get("size",0))
    if size<1_000_000:
        raise ValueError("archive metadata size implausibly small")
    uri=row.get("downloadUri")
    parsed=urllib.parse.urlsplit(uri or "")
    if parsed.scheme!="https" or parsed.hostname not in OFFICIAL_HOSTS:
        raise ValueError("untrusted ScienceBase binary URL")
    return {"product":product,"item_id":item_id,"title":title,
            "original_archive_name":name,"catalog_bytes":size,
            "metadata_sha256":r["sha256"],
            "source_url_verified":True,
            "archive_direct_uri":uri}

def archive_signature_probe(uri,catalog_bytes):
    # A bounded suffix probe never downloads any national imagery.
    try:
        r=read_limited(uri,MAX_BINARY,
                 headers={"Range":"bytes=-4096"},timeout=65)
        signature=r["raw"][:4]
        crange=r["content_range"]
        return {"http_status":r["status"],"content_type":r["content_type"],
                "content_range":crange,"probe_bytes":r["bytes"],
                "first_four_hex":signature.hex(),
                "is_zip_local_header":signature.startswith(b"PK\x03\x04"),
                "is_zip_tail_or_central":(b"PK\x05\x06" in r["raw"] or b"PK\x01\x02" in r["raw"]),
                "is_html":("text/html" in r["content_type"].lower() or r["raw"].lstrip().lower().startswith((b"<!doctype html",b"<html"))),
                "actual_host":r["actual_host"],
                "catalog_bytes":catalog_bytes,"sha256_of_probe":r["sha256"],
                "raw_C1V2_pixel_verified":False}
    except Exception as e:
        return {"status":"binary_probe_unavailable","error_type":type(e).__name__,
                "error":str(e)[:260],"raw_C1V2_pixel_verified":False}

def find_layer_names(xml):
    root=ET.fromstring(xml)
    names=[]
    for layer in root.iter():
        if layer.tag.split("}")[-1]!="Layer":
            continue
        name=None; title=None
        for child in layer:
            tag=child.tag.split("}")[-1]
            if tag=="Name":
                name=child.text
            elif tag=="Title":
                title=child.text
        if name:
            names.append({"name":name,"title":title})
    return names

def wms_capabilities_probe(kind,service):
    url=service+"?service=WMS&request=GetCapabilities&version=1.3.0"
    try:
        r=read_limited(url,MAX_WMS,timeout=55)
        layers=find_layer_names(r["raw"])
        year=str(YEAR)
        visible=[x for x in layers if year in (x["name"] or "") or year in (x["title"] or "")]
        c12=[x for x in visible if "C1V2" in (x["name"] or "").upper() or
             "C1V2" in (x["title"] or "").upper()]
        return {"product":kind,"layers_total":len(layers),"year_layers":visible[:35],
                "explicit_C1V2_year_layers":c12[:20],
                "wms_http_status":r["status"],"capabilities_sha256":r["sha256"],
                "response_bytes":r["bytes"],"is_categorical_geotiff":False,
                "raw_C1V2_pixel_verified":False}
    except Exception as e:
        return {"product":kind,"status":"wms_capabilities_unavailable",
                "error_type":type(e).__name__,"error":str(e)[:260],
                "raw_C1V2_pixel_verified":False}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--output",type=Path,default=Path("research/output/OFFICIAL_NLCD_C1V2_ACCESS_GATE_V0_1.json"))
    args=p.parse_args()
    results={"study":"official_nlcd_C1V2_2012_categorical_source_only_preflight",
       "status":"NOT_YET_RAW_VERIFIED","year":YEAR,"collection":"C1V2",
       "source_read_only":True,"no_aws_or_requester_pays_calls":True,
       "no_full_archive_download":True,"no_frog_Counts_read":True,
       "no_forest_patch_inference":True,"no_actual_categorical_pixel_verified":True,
       "records":[]}
    for product,item,prefix in (("landcover",COVER_ITEM,"LndCov"),
                                ("confidence",CONF_ITEM,"LndCnf")):
        rec={"product":product}
        try:
            metadata=check_archive_metadata(product,item,prefix)
            uri=metadata.pop("archive_direct_uri")
            rec.update(metadata)
            rec["zip_range_probe"]=archive_signature_probe(uri,metadata["catalog_bytes"])
        except Exception as e:
            rec.update({"catalog_status":"source_inconclusive",
                        "error_type":type(e).__name__,"error":str(e)[:260]})
        rec["wms_capabilities"]=wms_capabilities_probe(product,WMS[product])
        results["records"].append(rec)
    # Even C1V2-labelled WMS layers cannot establish original TIFF pixel identity.
    results["status"]="OFFICIAL_CATALOGUE_AND_SERVICE_CHECKED_NO_CATEGORICAL_TIFF"
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(results,indent=2,sort_keys=True)+"\n",encoding="utf8")
    print(json.dumps(results,indent=2,sort_keys=True))
if __name__=="__main__":
    main()
