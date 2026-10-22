#!/usr/bin/env python3
"""Response-blind, byte-bounded official NPS HTTP range diagnostics.

DOES NOT download an entire frog recording file, nor parse frog outcomes.
Only logs HTTP metadata and content-type/HTML classification, never raw lines.
"""
from __future__ import annotations
import json
import urllib.request
from pathlib import Path

URL="https://irma.nps.gov/DataStore/DownloadFile/763377?Reference=2320505"
SIZE=68581307
HEADERS={"User-Agent":"frogcs-NPS-GLKN-official-range-diagnostic-v0.5",
         "Accept":"text/csv,application/octet-stream,*/*"}

def test(method="GET",rng=None,limit=16384):
    hd=dict(HEADERS)
    if rng is not None:hd["Range"]=f"bytes={rng[0]}-{rng[1]}"
    req=urllib.request.Request(URL,method=method,headers=hd)
    try:
        with urllib.request.urlopen(req,timeout=50) as r:
            payload=r.read(limit) if method!="HEAD" else b""
            lo=payload[:256].lower()
            return {
              "status":"HTTP_response","method":method,
              "requested_range":rng,
              "http":int(r.status),
              "content_length":r.headers.get("Content-Length"),
              "content_range":r.headers.get("Content-Range"),
              "content_type":r.headers.get("Content-Type"),
              "final_host":urllib.request.urlparse(r.geturl()).hostname if hasattr(urllib.request,"urlparse") else __import__("urllib.parse",fromlist=["urlparse"]).urlparse(r.geturl()).hostname,
              "preview_bytes_read":len(payload),
              "looks_like_HTML_or_security_check":
                  any(x in lo for x in
                      (b"<html",b"<!doctype",b"captcha",b"access denied",b"checking your browser")),
              "source_raw_preview_discarded":True
            }
    except Exception as ex:
        return {"status":"HTTP_error","method":method,
                "requested_range":rng,
                "error_type":type(ex).__name__,
                "message":str(ex)[:190]}

def main():
    out=Path("build/nps_glkn_transfer_diag")
    out.mkdir(parents=True,exist_ok=True)
    checks={
       "head":test(method="HEAD"),
       "normal_GET_preview":test(limit=16384),
       "first_1024":test(rng=(0,1023),limit=1024),
       "last_1024":test(rng=(SIZE-1024,SIZE-1),limit=1024)
    }
    first=checks["first_1024"];last=checks["last_1024"]
    accepted=bool(
        first.get("http")==206 and last.get("http")==206 and
        first.get("content_range")==f"bytes 0-1023/{SIZE}" and
        last.get("content_range")==f"bytes {SIZE-1024}-{SIZE-1}/{SIZE}" and
        first.get("preview_bytes_read")==1024 and
        last.get("preview_bytes_read")==1024 and
        not first.get("looks_like_HTML_or_security_check") and
        not last.get("looks_like_HTML_or_security_check") and
        first.get("final_host")=="irma.nps.gov" and
        last.get("final_host")=="irma.nps.gov")
    report={
       "analysis":"official_NPS_response_blind_standard_HTTP_range_diagnostic_v0_5",
       "expected_bytes":SIZE,
       "expected_complete_SHA256":"b1c11cf70472a906e6c238a690a5a12373cdd20ef4d5e180fa3f376d520118c2",
       "source_url":URL,
       "checks":checks,
       "source_Range_eligible":accepted,
       "frog_outcomes_read":False,
       "source_bytes_persisted":False,
       "RC6_changed":False}
    (out/"report.json").write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    print("NPS_RANGE_DIAGNOSTIC_BEGIN")
    print(json.dumps(report,sort_keys=True))
    print("NPS_RANGE_DIAGNOSTIC_END")
if __name__=="__main__":main()
