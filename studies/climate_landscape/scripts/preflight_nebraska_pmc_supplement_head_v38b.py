#!/usr/bin/env python3
"""v3.8b: HEAD-only probe of openly published journal supplementary ZIP.

Find only archive existence/type/size. Do not download ZIP body, any CSV, any
amphibian calling outcome or unpublished data. Fails closed on wrong media.
"""
import json
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

SOURCES = (
    ("PMC supplementary candidate", "https://pmc.ncbi.nlm.nih.gov/articles/PMC7710638/bin/mmc1.zip"),
    ("NCBI legacy supplementary candidate", "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7710638/bin/mmc1.zip"),
)
def head(url):
    req=urllib.request.Request(url,method="HEAD",
        headers={"User-Agent":"frogcs-source-preflight/3.8b"})
    with urllib.request.urlopen(req,timeout=15) as response:
        final=response.url
        host=urllib.parse.urlparse(final).hostname or ""
        code=response.status
        typ=response.headers.get("content-type", "")
        size=response.headers.get("content-length")
        if len(final)>1000:
            raise ValueError("unexpected URL")
        return {"http_status":code,"mime_type":typ,
                "size_bytes_header":int(size) if size and size.isdigit() else None,
                "final_host":host,"final_url":final,
                "zip_type_plausible":("zip" in typ.lower() or final.lower().endswith(".zip"))}
def main():
    result={"analysis":"published_nebraska_supplemental_source_HEAD_only_v3_8b",
            "article_doi":"10.1016/j.dib.2020.106581",
            "published_supplement_label":"mmc1.zip, approximately 3MB",
            "candidates":[],"response_outcomes_downloaded":False,
            "archive_body_downloaded":False,"frog_data_read":False,
            "ecological_effect_estimated":False,"rc6_unchanged":True}
    for name,url in SOURCES:
        item={"name":name,"tested_url":url}
        try:
            item.update(head(url))
            item["status"]="HEAD_OK" if item["zip_type_plausible"] else "WRONG_CONTENT_TYPE"
        except urllib.error.HTTPError as e:
            item.update(status="HTTP_ERROR",http_status=e.code)
        except urllib.error.URLError as e:
            item.update(status="NETWORK_BLOCKED",error_type=type(e.reason).__name__)
        except (ValueError,TimeoutError) as e:
            item.update(status="SCHEMA_OR_TIMEOUT",error_type=type(e).__name__)
        result["candidates"].append(item)
    path=Path("studies/climate_landscape/receipts/NEBRASKA_PMC_SUPPLEMENT_HEAD_V38B.json")
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"supplement_source_results":[{"name":x["name"],"status":x["status"],
                    "http_status":x.get("http_status"),"mime_type":x.get("mime_type")} for x in result["candidates"]],
                    "archive_body_downloaded":False},sort_keys=True))
if __name__=="__main__":
    main()
