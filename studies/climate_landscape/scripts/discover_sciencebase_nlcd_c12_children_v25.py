#!/usr/bin/env python3
"""Enumerate ver.1.2 USGS ScienceBase child catalog for raw NLCD source files.

No national ZIP bytes, raster pixels, GEE, AWS requester-pays or frog calls.
Metadata inventory only; close ambiguous/version-drifted paths without guessing.
"""
from __future__ import annotations
import argparse,hashlib,json,re,time,urllib.parse,urllib.request
from pathlib import Path
ROOT_ITEM="655ceb8ad34ee4b6e05cc51a"
BASE="https://www.sciencebase.gov/catalog/"
MAX_BYTES=2_000_000
EXPECTED_FAMILY=("Land Cover","Land Cover Confidence")
def get(relative):
    url=BASE+relative
    req=urllib.request.Request(url,headers={"Accept":"application/json","User-Agent":"frogcs-annual-nlcd-C1V2-source-catalog-2026"})
    with urllib.request.urlopen(req,timeout=60) as s:
        u=urllib.parse.urlparse(s.geturl())
        if u.scheme!="https" or u.hostname not in ("www.sciencebase.gov","sciencebase.gov"):
            raise ValueError("ScienceBase redirected off official host")
        raw=s.read(MAX_BYTES+1)
        if len(raw)>MAX_BYTES:raise ValueError("ScienceBase metadata response too large")
    return json.loads(raw),hashlib.sha256(raw).hexdigest()
def entries(obj):
    if isinstance(obj,list):return obj
    for k in ("items","results","records"):
        if isinstance(obj.get(k),list):return obj[k]
    return []
def main():
    p=argparse.ArgumentParser();p.add_argument("--out",required=True)
    a=p.parse_args()
    record={"analysis":"official_USGS_sciencebase_annual_nlcd_C1V2_child_download_inventory_v25",
        "official_parent_item_id":ROOT_ITEM,"status":"UNVERIFIED_C1V2_RASTER_ACCESS",
        "counts_csv_opened":False,"original_raster_bytes_downloaded":0,
        "collection_1_2_is_not_assumed_from_filename":True,
        "no_AWS_requester_pays":True,"queries":[],"children":[],"candidate_files":[]}
    # Multiple documented index forms; no arbitrary web crawling.
    queries=[
        "items?"+urllib.parse.urlencode({"parentId":ROOT_ITEM,"max":100,"format":"json"}),
        "items?"+urllib.parse.urlencode({"parentId":ROOT_ITEM,"max":100}),
        "search?"+urllib.parse.urlencode({"q":"parentId:"+ROOT_ITEM,"max":100,"format":"json"})
    ]
    collected={}
    for path in queries:
        q={"path":path}
        try:
            data,digest=get(path)
            children=entries(data)
            q.update({"sha256":digest,"top_level_keys":sorted(data)[:20] if isinstance(data,dict) else [],
                      "items_returned":len(children),
                      "total":data.get("total") if isinstance(data,dict) else None})
            for child in children:
                if isinstance(child,dict) and re.fullmatch(r"[a-z0-9]{24}",str(child.get("id",""))):
                    collected[child["id"]]=child.get("title","")
        except Exception as e:q.update({"error_type":type(e).__name__,"error":str(e)[:230]})
        record["queries"].append(q)
        print(json.dumps(q,sort_keys=True),flush=True)
        if len(collected)>=3:break
        time.sleep(.7)
    record["immediate_child_count"]=len(collected)
    for itemid,title in sorted(collected.items(),key=lambda x:x[1]):
        if len(record["children"])>=30:break
        child={"id":itemid,"index_title":title}
        try:
            data,digest=get("item/"+itemid+"?format=json")
            child.update({"metadata_sha256":digest,"title":data.get("title"),
                "parent_id":data.get("parentId"),"hasChildren":data.get("hasChildren"),
                "n_files":len(data.get("files",[])),
                "files":[{"name":f.get("name"),"size":f.get("size"),
                     "contentType":f.get("contentType"),"url_host":urllib.parse.urlparse(f.get("downloadUri") or "").hostname}
                     for f in data.get("files",[])[:50]]})
            record["candidate_files"].extend({"item_id":itemid,"item_title":data.get("title"),
                  "file":f} for f in child["files"] if re.search(r"NLCD|LndCov|LndCnf|zip|tif",str(f.get("name")),re.I))
        except Exception as e:child.update({"error_type":type(e).__name__,"error":str(e)[:180]})
        record["children"].append(child)
        time.sleep(.4)
    # A catalog child listing is not yet proof of a precisely versioned, aligned 30m raster.
    record["status"]="OFFICIAL_CHILD_METADATA_FOUND_NO_PIXELS" if record["children"] else "NO_CHILD_METADATA_RETRIEVED"
    output=Path(a.out);output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(record,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"status":record["status"],"children":len(record["children"]),
       "files":len(record["candidate_files"])},sort_keys=True))
if __name__=="__main__":main()
