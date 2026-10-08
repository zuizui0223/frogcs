#!/usr/bin/env python3
"""Check official Annual NLCD Collection 1.2 public catalog access.

Metadata/URLs only. No archive file downloading, no AWS requester-pays,
no ESA/land use change pixel inference, and no frog outcomes.
"""
from __future__ import annotations
import argparse
from html.parser import HTMLParser
import hashlib,json,re,time,urllib.parse,urllib.request
from pathlib import Path

M=(
("mrlc","https://www.mrlc.gov/data?f%5B0%5D=project_tax_term_term_parents_tax_term_name%3AAnnual+NLCD"),
("usgs_archive","https://www.sciencebase.gov/catalog/item/655ceb8ad34ee4b6e05cc51a?format=json"),
("gee_community","https://gee-community-catalog.org/projects/annual_nlcd/"),
)
HOSTS={
 "mrlc":{"www.mrlc.gov","mrlc.gov"},
 "usgs_archive":{"www.sciencebase.gov","sciencebase.gov"},
 "gee_community":{"gee-community-catalog.org","www.gee-community-catalog.org"},
}
GEE_ID={
 "land_cover":"projects/sat-io/open-datasets/USGS/ANNUAL_NLCD/LANDCOVER",
 "confidence":"projects/sat-io/open-datasets/USGS/ANNUAL_NLCD/LANDCOVER_CONFIDENCE",
}
LIMIT=2_500_000

class Parser(HTMLParser):
    def __init__(self):
        super().__init__();self.links=[];self.text=[];self.current=None
    def handle_starttag(self,tag,attrs):
        if tag=="a":self.current=dict(attrs).get("href")
    def handle_endtag(self,tag):
        if tag=="a":self.current=None
    def handle_data(self,data):
        if data.strip():
            s=" ".join(data.split())
            self.text.append(s)
            if self.current:self.links.append((s,self.current))

def fetch(name,url):
    req=urllib.request.Request(url,headers={"User-Agent":"frogcs-C1V2-official-metadata-only-QC/2.4",
        "Accept":"text/html, application/json"})
    with urllib.request.urlopen(req,timeout=50) as s:
        final=urllib.parse.urlparse(s.geturl())
        if final.scheme!="https" or final.hostname not in HOSTS[name]:
            raise ValueError(f"Unapproved catalog redirect: {final.hostname}")
        raw=s.read(LIMIT+1);mime=s.headers.get("Content-Type","")
    if len(raw)>LIMIT:raise ValueError("Catalog response exceeds 2.5MB; do not silently truncate")
    return raw,mime

def extract(name,raw):
    body=raw.decode("utf-8-sig")
    if name=="usgs_archive":
        obj=json.loads(body)
        child_links=[{"id":x.get("id"),"title":x.get("title")} for x in obj.get("hasChildren",[]) if isinstance(x,dict)] if isinstance(obj.get("hasChildren"),list) else []
        # May be a parent with hasChildren=true and no inline children.
        return {"item_id":obj.get("id"),"title":obj.get("title"),
                "hasChildren":obj.get("hasChildren"),
                "available_inline_files":[{"name":z.get("name"),"size":z.get("size"),
                   "mimeType":z.get("contentType")}
                    for z in obj.get("files",[])[:25]],
                "version_tokens":sorted(set(re.findall(r"C1V[012]|Collection\s+1[.][012]",json.dumps(obj),re.I)))[:12],
                "inline_child_links":child_links[:20]}
    p=Parser();p.feed(body)
    rendered=" ".join(p.text)
    sample_links=[{"label":t[:90],"href":u[:500]} for t,u in p.links
                  if re.search(r"Download|Land Cover|Confidence|Metadata",t,re.I)][:90]
    return {"html_title":re.search(r"<title>(.*?)</title>",body,re.I|re.S).group(1).strip()
                  if re.search(r"<title>(.*?)</title>",body,re.I|re.S) else None,
            "mentions_C1V2":bool(re.search(r"C1V2|Collection\s+1(?:[.]|\s+Version\s*)2|\b1[.]2\b",rendered,re.I)),
            "mentions_old_C1V0":bool(re.search(r"C1V0|Collection\s+1[.]0",rendered,re.I)),
            "year_2012_mentioned":bool(re.search(r"(?<!\d)2012(?!\d)",rendered)),
            "public_links":sample_links,
            "gee_assets_mentioned":{k:v in body for k,v in GEE_ID.items()},
            "inline_download_links_truncated_for_safety":len(sample_links)>=90}

def run():
    result={"analysis":"Annual_NLCD_C1_2_original_metadata_access_gate_v24",
        "access_mode":"public metadata, bounded HTTP responses only",
        "status":"NO_C1V2_RAW_TIFF_VERIFIED",
        "no_frog_counts_read":True,
        "no_NLCD_original_raster_downloaded":True,
        "no_AWS_requester_pays_calls":True,
        "community_GEE_asset_is_not_official_USGS_product_hash":True,
        "gee_asset_identifiers_from_public_catalog":GEE_ID,
        "not_a_class_change_accuracy_assessment":True,
        "records":[]}
    for name,url in M:
        entry={"name":name,"url":url,"status":"source_unavailable"}
        try:
            data,mime=fetch(name,url)
            entry.update({"status":"metadata_returned","bytes":len(data),
                "content_type":mime,"sha256":hashlib.sha256(data).hexdigest(),
                "details":extract(name,data)})
        except Exception as e:
            entry.update({"error_type":type(e).__name__,"error":str(e)[:300]})
        result["records"].append(entry)
        print(json.dumps({k:v for k,v in entry.items() if k!="details"},sort_keys=True),flush=True)
        time.sleep(.3)
    return result

def main():
    p=argparse.ArgumentParser();p.add_argument("--out",required=True)
    x=p.parse_args()
    data=run();path=Path(x.out)
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(data,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({"status":data["status"],"successes":sum(r["status"]=="metadata_returned"
          for r in data["records"])},sort_keys=True))

if __name__=="__main__":main()
