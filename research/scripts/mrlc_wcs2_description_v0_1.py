#!/usr/bin/env python3
"""WCS 2.0.1 DescribeCoverage for official Annual NLCD, no pixel access."""
from __future__ import annotations
import argparse
import hashlib
import json
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

HOST="dmsdata.cr.usgs.gov"
WORKSPACES={"landcover":"mrlc_Land-Cover-Native_conus_year_data",
            "confidence":"mrlc_Land-Cover-Confidence-Native_conus_year_data"}
MAX=2_500_000

def local(s):return s.rsplit("}",1)[-1]

def readxml(url):
    p=urllib.parse.urlsplit(url)
    if p.scheme!="https" or p.hostname!=HOST:
        raise ValueError("nonofficial service URL")
    req=urllib.request.Request(url,headers={
        "User-Agent":"frogcs-wcs2-coverage-description-source-v1"})
    with urllib.request.urlopen(req,timeout=50) as r:
        payload=r.read(MAX+1)
        status=r.status
        mime=r.headers.get("Content-Type","")
        final=urllib.parse.urlsplit(r.geturl())
    if final.hostname!=HOST or len(payload)>MAX:
        raise ValueError("oversized/redirected WCS source response")
    root=ET.fromstring(payload)
    exceptions=[x.text.strip() for x in root.iter()
        if local(x.tag) in ("ExceptionText","ServiceException") and x.text]
    if exceptions:
        raise ValueError("WCS exception: "+"; ".join(exceptions)[:320])
    return root,{"http_status":status,"mime":mime,"bytes":len(payload),
                 "sha256":hashlib.sha256(payload).hexdigest()}

def uri(workspace,req,cover=None):
    u=f"https://{HOST}/geoserver/{workspace}/wcs"
    params={"SERVICE":"WCS","VERSION":"2.0.1","REQUEST":req}
    if cover:
        params["COVERAGEID"]=cover
    return u+"?"+urllib.parse.urlencode(params)

def parse_summary(root):
    tags=("CoverageId","Identifier","Title","Name","axisLabels","srsName",
          "lowerCorner","upperCorner","timePosition","beginPosition",
          "endPosition","timeResolution","offsetVector")
    out={}
    for tag in tags:
        vals=[x.text.strip() for x in root.iter()
              if local(x.tag)==tag and x.text and x.text.strip()]
        out[tag]=list(dict.fromkeys(vals))[:22]
    return out

def run():
    out={}
    for product,w in WORKSPACES.items():
        item={"product":product,"workspace":w,"data_collection":"NOT_VERIFIED_C1V2"}
        try:
            cap,meta=readxml(uri(w,"GetCapabilities"))
            covers=[x.text.strip() for x in cap.iter()
                    if local(x.tag)=="CoverageId" and x.text and x.text.strip()]
            item["capabilities_metadata"]=meta
            item["covers"]=list(dict.fromkeys(covers))[:30]
            exact=[x for x in covers if x.startswith(w+"__") or x.startswith(w+":")]
            if len(exact)!=1:
                raise ValueError(f"expected one coverage in {w}: {item['covers'][:4]}")
            item["chosen_cover_id"]=exact[0]
            resp,dm=readxml(uri(w,"DescribeCoverage",exact[0]))
            item["description_metadata"]=dm
            item["description"]=parse_summary(resp)
            item["description_root_tag"]=local(resp.tag)
            item["result"]="DESCRIPTION_READ_NO_PIXEL"
        except Exception as e:
            item.update({"result":"INCONCLUSIVE_METADATA","error_type":type(e).__name__,
                         "error":str(e)[:340]})
        out[product]=item
        print(json.dumps(item,indent=2,sort_keys=True),flush=True)
    return {"study":"official_mrlc_WCS2_coverage_description_v0_1",
            "no_frog_outcomes":True,"no_pixels_read":True,"source_C1V2_confirmed":False,
            "source_rows":out}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,default=Path("research/output/MRLC_WCS2_DESCRIBE_2012_V0_1.json"))
    a=p.parse_args()
    o=run();a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(o,indent=2,sort_keys=True)+"\n")
if __name__=="__main__":main()
