#!/usr/bin/env python3
import hashlib, html, io, json, re
from pathlib import Path
from urllib.parse import urljoin
import pandas as pd
import requests

OUT=Path("exploration/KOREA_EXTERNAL_ELIGIBILITY_RECEIPT_V0_1.json")
URLS=[
  "https://doi.org/10.7717/peerj.5568/supp-1",
  "https://peerj.com/articles/5568/supp-1/",
  "https://peerj.com/articles/5568/supp-1",
]
TOKENS=("site","year","date","time","lat","lon","coord","rain","precip","temperature","humidity","pressure","suweon","dryophytes","individual","count","number","calling","index","encroach")

def fetch():
    errors=[]
    # Prefer public archival mirrors over the PeerJ page, which can be bot-protected.
    xml_urls=[
      "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC6151124/fullTextXML",
      "https://www.ncbi.nlm.nih.gov/research/bionlp/RESTful/pmcoa.cgi/BioC_xml/PMC6151124/unicode",
    ]
    archive_candidates=[]
    for xu in xml_urls:
        try:
            xr=requests.get(xu,headers={"User-Agent":"frogcs-korea-audit/0.1"},timeout=90)
            if xr.status_code==200:
                xt=xr.text
                for href in re.findall(r'(?:xlink:href|href)=["\\\']([^"\\\']+)["\\\']',xt,re.I):
                    if any(x in href.lower() for x in ("5568","supp","xlsx")):
                        archive_candidates.extend([
                          urljoin("https://pmc.ncbi.nlm.nih.gov/articles/PMC6151124/",href),
                          urljoin(xu,href),
                        ])
        except Exception as e:
            errors.append({"url":xu,"error":f"{type(e).__name__}: {e}"})
    archive_candidates += [
      "https://pmc.ncbi.nlm.nih.gov/articles/PMC6151124/bin/peerj-06-5568-s001.xlsx",
      "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6151124/bin/peerj-06-5568-s001.xlsx",
      "https://pmc.ncbi.nlm.nih.gov/articles/instance/6151124/bin/peerj-06-5568-s001.xlsx",
    ]
    for url in list(dict.fromkeys(archive_candidates+URLS)):
        try:
            r=requests.get(url,headers={"User-Agent":"Mozilla/5.0 frogcs-korea-audit/0.1"},timeout=90,allow_redirects=True)
            b=r.content
            ctype=(r.headers.get("content-type") or "").lower()
            if r.status_code==200 and (b[:2]==b"PK" or "spreadsheet" in ctype or "excel" in ctype):
                return b,url,r.url,r.headers.get("content-type")
            # PMC serves binary attachments through an intermediate HTML download page.
            if r.status_code==200 and "html" in ctype and ".xlsx" in url.lower():
                txt=r.text
                hrefs=re.findall(r'href=["\\\']([^"\\\']+)["\\\']',txt,re.I)
                next_urls=[]
                for href in hrefs:
                    h=html.unescape(href)
                    if ".xlsx" in h.lower() or "cdn.ncbi.nlm.nih.gov" in h.lower() or "download" in h.lower():
                        next_urls.append(urljoin(r.url,h))
                for u2 in list(dict.fromkeys(next_urls)):
                    try:
                        r2=requests.get(u2,headers={"User-Agent":"Mozilla/5.0 frogcs-korea-audit/0.1","Referer":r.url},timeout=90,allow_redirects=True)
                        b2=r2.content
                        ct2=(r2.headers.get("content-type") or "").lower()
                        if r2.status_code==200 and (b2[:2]==b"PK" or "spreadsheet" in ct2 or "excel" in ct2):
                            return b2,url,r2.url,r2.headers.get("content-type")
                        errors.append({"url":u2,"status":r2.status_code,"final":r2.url,"content_type":r2.headers.get("content-type"),"bytes":len(b2),"stage":"pmc_html_follow"})
                    except Exception as e2:
                        errors.append({"url":u2,"error":f"{type(e2).__name__}: {e2}","stage":"pmc_html_follow"})
            errors.append({"url":url,"status":r.status_code,"final":r.url,"content_type":r.headers.get("content-type"),"bytes":len(b)})
        except Exception as e:
            errors.append({"url":url,"error":f"{type(e).__name__}: {e}"})
    raise RuntimeError("supplement download failed: "+json.dumps(errors))

def norm(x):
    return str(x).strip().lower().replace("_"," ").replace("-"," ")

def main():
    b,source,final,ctype=fetch()
    sha=hashlib.sha256(b).hexdigest()
    xl=pd.ExcelFile(io.BytesIO(b))
    sheets=[]
    all_candidates=[]
    for sheet in xl.sheet_names:
        d=xl.parse(sheet)
        cols=[str(c) for c in d.columns]
        candidates=[]
        for c in cols:
            n=norm(c)
            if any(t in n for t in TOKENS):
                s=d[c]
                rec={"column":c,"nonmissing":int(s.notna().sum()),"unique_nonmissing":int(s.dropna().astype(str).nunique())}
                num=pd.to_numeric(s,errors="coerce")
                if int(num.notna().sum())>0:
                    rec["numeric_nonmissing"]=int(num.notna().sum())
                    rec["numeric_min"]=float(num.min())
                    rec["numeric_max"]=float(num.max())
                    rec["numeric_zero_count"]=int((num==0).sum())
                    rec["numeric_positive_count"]=int((num>0).sum())
                candidates.append(rec)
                all_candidates.append({"sheet":sheet,**rec})
        sheets.append({"sheet":sheet,"rows":int(len(d)),"columns":cols,"candidate_columns":candidates})
    names=[norm(x["column"]) for x in all_candidates]
    has_site=any("site" in x for x in names)
    has_time=any(("year" in x or "date" in x) for x in names)
    has_response=any(any(t in x for t in ("suweon","dryophytes","count","number","individual")) for x in names)
    has_coord=any(("lat" in x or "lon" in x or "coord" in x) for x in names)
    out={
      "analysis":"korea_suweon_treefrog_external_eligibility_v0_1",
      "contract":"exploration/KOREA_EXTERNAL_ELIGIBILITY_CONTRACT_V0_1.json",
      "source":{"requested_url":source,"resolved_url":final,"content_type":ctype,"sha256":sha,"bytes":len(b)},
      "sheets":sheets,
      "schema_screen":{"has_site_candidate":has_site,"has_date_or_year_candidate":has_time,"has_response_candidate":has_response,"has_coordinate_candidate":has_coord},
      "response_models_fit":False
    }
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
