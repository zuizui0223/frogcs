#!/usr/bin/env python3
"""Response-blind public Dryad data-transfer audit for wetland macrophyte datasets.

Only probes official public URLs. Never invent a successful raw-data reanalysis.
"""
import hashlib, json
from urllib.request import Request,urlopen
from urllib.error import HTTPError,URLError

URLS={
 "Hamer55_api_site":"https://datadryad.org/api/v2/files/453628/download",
 "Hamer55_web_site":"https://datadryad.org/downloads/file_stream/453628",
 "Hamer55_whole_zip":"https://datadryad.org/api/v2/datasets/doi%3A10.5061%2Fdryad.b8gtht7b5/download",
 "Lishawa_Typha_workbook":"https://datadryad.org/api/v2/files/2825922/download",
}
result=[]
for name, url in URLS.items():
    receipt={"name":name,"url":url}
    try:
        req=Request(url,headers={"User-Agent":"Mozilla/5.0 (public open-data audit)","Accept":"*/*"})
        with urlopen(req,timeout=30) as r:
            pre=r.read(100000)
            receipt.update(status=getattr(r,"status",200),
                           final_url=r.geturl(),
                           content_type=r.headers.get("Content-Type"),
                           first_32_bytes_hex=pre[:32].hex(),
                           first_kb_sha256=hashlib.sha256(pre[:1024]).hexdigest(),
                           content_looks_binary=(pre[:2]==b"PK"),
                           csv_probable=pre.startswith(b"site,") or pre.startswith(b'"site",'),
                           html_blocked=(b"<html" in pre[:1000].lower()
                                         or b"<h1>Just a moment" in pre[:2000]))
    except (HTTPError,URLError,TimeoutError) as e:
        receipt["error"]=str(e)[:350]
    result.append(receipt)
print("DRYAD_SOURCE_ACCESS_AUDIT")
print(json.dumps(result,indent=2))
