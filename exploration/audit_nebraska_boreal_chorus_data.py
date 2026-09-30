#!/usr/bin/env python3
import hashlib, io, json
from pathlib import Path
import pandas as pd
import requests

DATASET_ID="p6nbn2hyz9"
VERSION=1
OUT=Path("exploration/NEBRASKA_BOREAL_CHORUS_DATA_AUDIT_V0_1.json")
REQ=["Site","Year","Date","Missing","Count","HYDRO","PRCP","PRCP7","PRCP1","TAVG","DOY"]
HEAD={"User-Agent":"frogcs-nebraska-audit/0.1","Accept":"application/json, application/vnd.mendeley-public-dataset.1+json"}

def norm(x):
    return str(x).strip().lower().replace(" ","").replace("_","")

def get_json(url):
    r=requests.get(url,headers=HEAD,timeout=60)
    r.raise_for_status()
    return r.json()

def discover():
    errors=[]
    urls=[
      f"https://api.data.mendeley.com/datasets/publics/{DATASET_ID}/files?version={VERSION}&$limit=100",
      f"https://api.data.mendeley.com/datasets/{DATASET_ID}/files?version={VERSION}&$limit=100",
    ]
    for url in urls:
        try:
            x=get_json(url)
            if isinstance(x,list) and x:
                return x,url
        except Exception as e:
            errors.append(f"{url}: {e}")
    raise RuntimeError("discovery failed: "+" | ".join(errors))

def download(meta):
    cd=meta.get("content_details") or {}
    urls=[
      cd.get("download_url"),meta.get("download_url"),
      f"https://api.data.mendeley.com/datasets/{DATASET_ID}/files/{meta.get('id')}/file_downloaded?version={VERSION}",
      f"https://api.data.mendeley.com/datasets/publics/{DATASET_ID}/files/{meta.get('id')}/file_downloaded?version={VERSION}",
    ]
    for url in urls:
        if not url or "None" in str(url):
            continue
        r=requests.get(url,headers={"User-Agent":HEAD["User-Agent"]},timeout=120,allow_redirects=True)
        if r.status_code==200 and r.content:
            return r.content,url
    raise RuntimeError("download failed")

def tables(name,b):
    low=name.lower()
    if low.endswith(".csv"):
        for enc in ("utf-8-sig","utf-8","cp1252"):
            try:
                return [("csv",pd.read_csv(io.BytesIO(b),encoding=enc))]
            except Exception:
                pass
    if low.endswith((".xlsx",".xls")):
        x=pd.ExcelFile(io.BytesIO(b))
        return [(s,x.parse(s)) for s in x.sheet_names]
    return []

def main():
    files,api=discover()
    inv=[]
    candidates=[]
    for meta in files:
        name=str(meta.get("filename") or meta.get("name") or "")
        row={"id":meta.get("id"),"filename":name,"size":meta.get("size") or (meta.get("content_details") or {}).get("size")}
        try:
            b,_=download(meta)
            row.update({"sha256":hashlib.sha256(b).hexdigest(),"bytes":len(b)})
            for sheet,df in tables(name,b):
                cmap={norm(c):str(c) for c in df.columns}
                found=[x for x in REQ if norm(x) in cmap]
                candidates.append((len(found),len(df),name,sheet,df,cmap,row["sha256"]))
        except Exception as e:
            row["error"]=f"{type(e).__name__}: {e}"
        inv.append(row)
    if not candidates:
        raise RuntimeError("no readable tables")
    candidates.sort(reverse=True,key=lambda x:(x[0],x[1]))
    _,_,name,sheet,df,cmap,sha=candidates[0]
    rename={cmap[norm(x)]:x for x in REQ if norm(x) in cmap}
    df=df.rename(columns=rename)
    allcols=all(x in df.columns for x in REQ)
    if allcols:
        for c in ["Year","Missing","Count","HYDRO","PRCP","PRCP7","PRCP1","TAVG","DOY"]:
            df[c]=pd.to_numeric(df[c],errors="coerce")
        valid=df[(df.Missing==0)&df.Count.notna()&(df.Count>=0)&(df.Count<=1)].copy()
        sites=sorted(valid.Site.astype(str).str.strip().unique().tolist())
        years=sorted(valid.Year.dropna().astype(int).unique().tolist())
        sy=valid.assign(_site=valid.Site.astype(str).str.strip(),_year=valid.Year.astype("Int64")).groupby(["_site","_year"]).size()
        active=int((valid.Count>0).sum())
        silent=int((valid.Count==0).sum())
        gate=bool(len(sites)>=2 and all(y in years for y in (2015,2016,2017)) and len(sy)>=6 and len(valid)>=250 and active>=50 and silent>=50)
    else:
        valid=pd.DataFrame()
        sites=[]
        years=[]
        sy=[]
        active=silent=0
        gate=False
    out={
      "analysis":"nebraska_boreal_chorus_data_audit_v0_1",
      "dataset_id":DATASET_ID,
      "version":VERSION,
      "api":api,
      "files":inv,
      "selected":{"filename":name,"sheet":sheet,"sha256":sha,"raw_rows":int(len(df)),"columns":[str(x) for x in df.columns]},
      "eligibility":{"all_required_columns":allcols,"valid_rows":int(len(valid)),"sites":sites,"years":years,"site_year_groups":int(len(sy)),"active_days":active,"silent_days":silent,"gate_pass":gate},
    }
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
