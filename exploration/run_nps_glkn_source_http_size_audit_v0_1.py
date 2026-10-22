#!/usr/bin/env python3
"""Response-blind HEAD/Range audit of official NPS GLKN published CSV assets.

Never download full calling/temperature data, and never read frog outcome rows.
"""
from __future__ import annotations
import csv
import io
import json
import re
import urllib.request
import urllib.error
from pathlib import Path

FILES={
"frog":"https://irma.nps.gov/DataStore/DownloadFile/763377?Reference=2320505",
"temperature":"https://irma.nps.gov/DataStore/DownloadFile/763378?Reference=2320505",
"metadata":"https://irma.nps.gov/DataStore/DownloadFile/763466?Reference=2320505"}
USER="frogcs-NPS-GLKN-source-size-preflight/0.1"
CAP=512*1024*1024

def find_size(v):
    if v is None:return None
    try:return int(v)
    except (ValueError,TypeError):return None

def inspect(url):
    item={"official_url":url,"HEAD":{},"RANGE_first_1024":{}}
    try:
        req=urllib.request.Request(url,method="HEAD",headers={"User-Agent":USER})
        with urllib.request.urlopen(req,timeout=35) as h:
            item["HEAD"]={"http":h.status,
                 "length":h.headers.get("Content-Length"),
                 "accept_ranges":h.headers.get("Accept-Ranges"),
                 "content_type":h.headers.get("Content-Type"),
                 "content_encoding":h.headers.get("Content-Encoding")}
    except Exception as e:
        item["HEAD"]={"error":str(e)[:200]}
    try:
        req=urllib.request.Request(
            url,headers={"User-Agent":USER,"Range":"bytes=0-1023"})
        with urllib.request.urlopen(req,timeout=35) as r:
            part=r.read(1024)
            item["RANGE_first_1024"]={
                "http":r.status,
                "content_range":r.headers.get("Content-Range"),
                "content_length":r.headers.get("Content-Length"),
                "content_type":r.headers.get("Content-Type"),
                "bytes_read":len(part),
                "startswith_utf8_bom":part.startswith(b"\xef\xbb\xbf"),
                "looks_like_html":b"<html" in part[:500].lower(),
                "first_line_column_headers":None}
            if len(part)>30 and b"\n" in part[:1024]:
                try:
                    line=part.split(b"\n")[0].decode("utf-8-sig").strip()
                    cols=next(csv.reader([line]))
                    if not item["RANGE_first_1024"]["looks_like_html"]:
                        item["RANGE_first_1024"]["first_line_column_headers"]=cols
                except (UnicodeError,csv.Error):
                    pass
    except Exception as e:
        item["RANGE_first_1024"]={"error":str(e)[:260]}
    sizes=[find_size(item["HEAD"].get("length"))]
    cr=item["RANGE_first_1024"].get("content_range")
    if cr and "/" in cr:
        sizes.append(find_size(cr.split("/")[-1]))
    sizes=[s for s in sizes if s is not None]
    item["source_size_bytes"]=sizes[0] if sizes else None
    item["further_streaming_feasible_with_under_512MiB_cap"]=bool(
        sizes and sizes[0]<=CAP
        and not item["RANGE_first_1024"].get("looks_like_html"))
    return item

def main():
    out=Path("build/nps_glkn_frog_source_only");out.mkdir(parents=True,exist_ok=True)
    x={key:inspect(url) for key,url in FILES.items()}
    r={"analysis":"NPS_GLKN_response_blind_HTTP_file_size_preflight_v0_1",
       "files":x,
       "read_frog_detection_values":False,
       "frozen_RC6_modified":False,
       "any_main_frog_bytes_persisted":False,
       "decision":"metadata_only_not_biological_analysis"}
    (out/"http_size_preflight.json").write_text(json.dumps(r,indent=2,sort_keys=True)+"\n")
    print("NPS_GLKN_FILE_SIZE_BEGIN",flush=True)
    print(json.dumps(r,sort_keys=True),flush=True)
    print("NPS_GLKN_FILE_SIZE_END",flush=True)
if __name__=="__main__":main()
