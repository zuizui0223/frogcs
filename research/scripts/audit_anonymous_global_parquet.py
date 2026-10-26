#!/usr/bin/env python3
"""Read-only source audit of actual versioned full-world GloBI and anonymous GBIF data.

Uses HTTP Range to read the Parquet footer only, not gigabytes of occurrences.
Fulfils source-provenance gate before any ecological/cross-dataset modelling.
"""
from __future__ import annotations
import argparse
import io
import json
import struct
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

from pyarrow import parquet as pq
from pyarrow import BufferReader

GLOBAL_GLOBI = {
    "record": "https://zenodo.org/api/records/22691479/files",
    "parquet": "https://zenodo.org/api/records/22691479/files/interactions.parquet/content",
    "expected_size":2375721521,
    "expected_md5":"8212776b7ba0c4fa8de26a00b5ce8595",
    "version":"0.11",
    "doi":"10.5281/zenodo.22691479",
}
BUCKET="https://gbif-public-data.s3.amazonaws.com"
GBIF_PREFIX="development/2026-08-01-DWCA/p_taxon/"
GBIF_CITATION="https://gbif-open-data-us-east-1.s3.amazonaws.com/occurrence/2026-10-01/citation.txt"
PARTITIONS={
    "anurans":"Animalia_Chordata_Amphibia_Anura",
    "odonates":"Animalia_Arthropoda_Insecta_Odonata",
}
UA="frogcs-ecology-scientific-archive-audit/0.1 (public read-only)"
MAX_METADATA=30*1024*1024


def request(url,method="GET",byte_range=None):
    h={"User-Agent":UA}
    if byte_range:
        h["Range"]=f"bytes={byte_range[0]}-{byte_range[1]}"
    return urllib.request.urlopen(
        urllib.request.Request(url,headers=h,method=method),timeout=70)


def get_json(url):
    with request(url) as f:
        return json.load(f)


def list_prefix(prefix,max_keys=1000):
    url=BUCKET+"/?"+urllib.parse.urlencode(dict(
        **{"list-type":2},prefix=prefix,**{"max-keys":max_keys}))
    with request(url) as f:
        data=f.read(3_000_000)
    root=ET.fromstring(data)
    def el(node,child):
        n=node.find("{*}"+child)
        return n.text if n is not None else ""
    files=[]
    for obj in root.findall("{*}Contents"):
        files.append({"key":el(obj,"Key"),
                      "size":int(el(obj,"Size"))})
    return {"prefix":prefix,"files":files,
            "truncated":el(root,"IsTruncated")=="true"}


def parquet_footer(url):
    with request(url,method="HEAD") as head:
        length=int(head.headers["Content-Length"])
        ranges=head.headers.get("Accept-Ranges",None)
        etag=head.headers.get("ETag",None)
    if length <= 20:
        raise ValueError("Not a Parquet file")
    with request(url,byte_range=(length-8,length-1)) as r:
        status=getattr(r,"status",None)
        data=r.read(16)
    if status!=206 or len(data)!=8 or data[-4:]!=b"PAR1":
        raise RuntimeError(
            f"HTTP server lacks safe Parquet footer Range status={status}, got={data[:14]!r}")
    footer_len=struct.unpack("<I",data[:4])[0]
    if footer_len<10 or footer_len>MAX_METADATA:
        raise RuntimeError(f"metadata footer {footer_len} exceeds bounded parser cap")
    with request(url,byte_range=(length-footer_len-8,length-1)) as r:
        status=getattr(r,"status",None)
        tail=r.read(footer_len+16)
    if status!=206 or len(tail)!=footer_len+8 or tail[-4:]!=b"PAR1":
        raise RuntimeError("Range footer metadata response differs from expected size")
    # The Parquet footer can be parsed without actual row data.
    meta = pq.read_metadata(BufferReader(b"PAR1"+tail))
    fields=[{"name":name,
             "path":meta.schema.column(i).path,
             "type":str(meta.schema.column(i).physical_type),
             "logical":str(meta.schema.column(i).logical_type)}
            for i,name in enumerate(meta.schema.names)]
    return {
        "url":url,"http_bytes":length,"range_supported":True,
        "etag":etag,"reported_accept_ranges":ranges,
        "footer_bytes":footer_len,
        "num_rows":meta.num_rows,
        "num_row_groups":meta.num_row_groups,
        "schema_fields":fields,
        "first_row_group_rows":meta.row_group(0).num_rows if meta.num_row_groups else None,
        "first_row_group_compressed_bytes":(
            meta.row_group(0).total_byte_size if meta.num_row_groups else None)
    }


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",default="research/results/full_global_parquet_preflight")
    args=ap.parse_args()
    out=Path(args.out)
    out.mkdir(parents=True,exist_ok=True)
    receipt={
        "date":"2026-10-25",
        "status":"SOURCE_PREFLIGHT_ONLY_NO_GLOBAL_MODEL_FITTED",
        "globi":{},
        "gbif":{},
        "blockers":[],
        "provenance":{
            "globi_fixed_version":GLOBAL_GLOBI["doi"],
            "gbif_development_status":"EXPERIMENTAL_partitioned_snapshot_NOT_officially_promised_stable",
            "gbif_october_snapshot":"2026-10-01",
            "gbif_aws_doc":"https://github.com/gbif/occurrence/blob/dev/aws-public-data.md"
        },
    }
    try:
        listing=get_json(GLOBAL_GLOBI["record"])
        files=listing.get("entries",[])
        listed=next((x for x in files if x.get("key")=="interactions.parquet"),None)
        if listed:
            receipt["globi"]["archive_file"]={
                "size":listed.get("size"),"checksum":listed.get("checksum"),
                "status":listed.get("status"),"url":listed.get("links",{}).get("content")}
        if not listed or int(listed.get("size",0))!=GLOBAL_GLOBI["expected_size"]:
            receipt["blockers"].append("Version-specific archive size mismatch")
        receipt["globi"]["parquet"]=parquet_footer(GLOBAL_GLOBI["parquet"])
    except Exception as exc:
        receipt["globi"]["footer_error"]=str(exc)
        receipt["blockers"].append("GloBI full parquet footer unavailable")
    for tag,partition in PARTITIONS.items():
        pref=GBIF_PREFIX+"taxonpartition="+partition+"/"
        try:
            listing=list_prefix(pref)
            stats=dict(
                prefix=pref,number_files=len(listing["files"]),
                total_parquet_bytes=sum(x["size"] for x in listing["files"]),
                truncated=listing["truncated"],
                files=listing["files"])
            if listing["files"]:
                first=listing["files"][0]["key"]
                stats["sample"]=parquet_footer(BUCKET+"/"+urllib.parse.quote(first,safe="/"))
            receipt["gbif"][tag]=stats
        except Exception as exc:
            receipt["gbif"][tag]={"error":str(exc)}
            receipt["blockers"].append(f"GBIF {tag} partition scan unavailable")
    try:
        with request(GBIF_CITATION) as r:
            receipt["gbif"]["october_snapshot_citation"]=r.read(1000).decode("utf8")
    except Exception as exc:
        receipt["gbif"]["october_citation_error"]=str(exc)
    (out/"source_metadata.json").write_text(
        json.dumps(receipt,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    print("BEGIN_GLOBAL_PARQUET_SOURCE_METADATA")
    print(json.dumps(receipt,ensure_ascii=False,indent=2))
    print("END_GLOBAL_PARQUET_SOURCE_METADATA")


if __name__=="__main__":
    main()
