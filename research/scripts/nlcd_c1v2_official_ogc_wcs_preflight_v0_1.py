#!/usr/bin/env python3
"""Official MRLC Annual NLCD WMS/WCS source identity: response-blind, no pixels.

Avoid repeating the false HTTP 206 HTML-as-ZIP result by interrogating an OGC
coverage protocol. Do not infer Collection 1.2 from the words 'Annual NLCD'.
This source QA can authorize a future GetCoverage only when the underlying
layer has explicit original product year AND C1V2 source provenance.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

HOST="dmsdata.cr.usgs.gov"
SERVICES={
 "landcover":"mrlc_Land-Cover-Native_conus_year_data",
 "confidence":"mrlc_Land-Cover-Confidence-Native_conus_year_data"
}
VERSIONS=[("WMS","1.3.0"),("WCS","2.0.1"),("WCS","1.0.0")]
LIMIT=4_000_000

def caps_url(workspace,service,version):
    endpoint="wms" if service=="WMS" else "wcs"
    base=f"https://{HOST}/geoserver/{workspace}/{endpoint}"
    return base+"?"+urllib.parse.urlencode(
        {"service":service,"request":"GetCapabilities","version":version})

def read_capped(url):
    p=urllib.parse.urlsplit(url)
    if p.scheme!="https" or p.hostname!=HOST:
        raise ValueError("endpoint outside official MRLC host")
    request=urllib.request.Request(url,headers={
        "User-Agent":"frogcs-original-C1V2-OGC-metadata-v0.1",
        "Accept":"text/xml,application/xml"})
    with urllib.request.urlopen(request,timeout=55) as response:
        body=response.read(LIMIT+1)
        status=response.status
        final=urllib.parse.urlsplit(response.geturl())
        mime=response.headers.get("Content-Type","")
    if final.hostname!=HOST or len(body)>LIMIT:
        raise ValueError("unexpected redirect or oversized GetCapabilities response")
    return body,status,mime

def local(tag):return tag.rsplit("}",1)[-1]

def nested_text(root,tag):
    out=[]
    for elem in root.iter():
        if local(elem.tag)==tag and elem.text and elem.text.strip():
            out.append(elem.text.strip())
    return out

def inspect_capabilities(body,service):
    # Fail closed on text/html or nonXML. OGC errors are XML too, so inspect root.
    root=ET.fromstring(body)
    r=local(root.tag)
    if r in ("ServiceExceptionReport","ExceptionReport"):
        raise ValueError("OGC service reported an exception, not raster capabilities")
    if service=="WCS" and "Capabilities" not in r:
        raise ValueError("not a WCS Capabilities response")
    if service=="WMS" and r not in ("WMS_Capabilities","WMT_MS_Capabilities"):
        raise ValueError("not a WMS Capabilities response")
    names=nested_text(root,"Name")+nested_text(root,"CoverageId")+nested_text(root,"Identifier")
    titles=nested_text(root,"Title")
    abstracts=nested_text(root,"Abstract")
    keywords=nested_text(root,"Keyword")
    dates=nested_text(root,"Dimension")+nested_text(root,"Extent")
    metadata=nested_text(root,"OnlineResource")
    original_metadata=" ".join(titles+abstracts+keywords+names)
    explicit_c12=bool(re.search(r"(C1V2|collection[\s_-]*1[.]2)",original_metadata,re.I))
    year2012=any("2012" in x for x in names+titles+dates+abstracts)
    return {
        "root_tag":r,
        "layer_or_coverage_names":sorted(set(names))[:60],
        "titles":list(dict.fromkeys(titles))[:50],
        "abstracts":list(dict.fromkeys(abstracts))[:12],
        "sample_keywords":list(dict.fromkeys(keywords))[:35],
        "dimensions":list(dict.fromkeys(dates))[:25],
        "original_identity_explicit_C1V2_in_OGC":explicit_c12,
        "year_2012_visible":year2012,
        "layer_count":len(set(names)),
        "metadata_resource_count":len(metadata)
    }

def run():
    records=[]
    for product,workspace in SERVICES.items():
        for service,version in VERSIONS:
            url=caps_url(workspace,service,version)
            rec={"product":product,"service":service,"version":version,
                 "workspace":workspace,"endpoint_url":url,"status":"unavailable"}
            try:
                body,status,mime=read_capped(url)
                info=inspect_capabilities(body,service)
                rec.update({"status":"valid_ogc_capabilities","http_status":status,
                            "content_type":mime,"capabilities_sha256":hashlib.sha256(body).hexdigest(),
                            "bytes":len(body),"details":info})
            except Exception as exc:
                rec.update({"error_type":type(exc).__name__,
                            "error":str(exc)[:260]})
            records.append(rec)
            print(json.dumps({k:v for k,v in rec.items() if k!="details"},sort_keys=True),flush=True)
    eligible=[r for r in records if r.get("status")=="valid_ogc_capabilities"
              and r["service"]=="WCS"
              and r["details"]["original_identity_explicit_C1V2_in_OGC"]
              and r["details"]["year_2012_visible"]]
    both=all(any(r["product"]==kind for r in eligible) for kind in SERVICES)
    return {"analysis":"annual_nlcd_C1V2_official_ogc_identity_preflight_v0_1",
            "read_counts_or_taxa":False,"read_raster_pixels":False,
            "no_paid_aws":True,"requested_year":2012,
            "wcs_explicit_C1V2_2012_identified_both":both,
            "source_only_WCS_readiness":"eligible_for_later_bounded_pixel_test" if both
                else "NOT_AUTHORIZED_C1V2_VERSION_OR_COVERAGE_UNCONFIRMED",
            "source_rows":records}
def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--out",type=Path,
        default=Path("research/output/NLCD_C1V2_OFFICIAL_OGC_WCS_IDENTITY_V0_1.json"))
    args=parser.parse_args()
    out=run()
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"wcs_explicit_C1V2_2012_identified_both":
                      out["wcs_explicit_C1V2_2012_identified_both"],
                      "source_only_WCS_readiness":out["source_only_WCS_readiness"]},
                     indent=2,sort_keys=True))
if __name__=="__main__":main()
