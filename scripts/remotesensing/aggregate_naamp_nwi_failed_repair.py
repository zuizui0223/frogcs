#!/usr/bin/env python3
from __future__ import annotations
import hashlib, importlib.util, json, os, time, urllib.parse, urllib.request
from collections import Counter
from pathlib import Path
import pandas as pd

ROOT=Path(__file__).resolve().parents[2]
EXP=ROOT/"exploration"
RS=ROOT/"scripts"/"remotesensing"
BASE=Path(os.environ["NWI_BASE_ASSIGNMENTS"])
REPAIR_DIR=Path(os.environ["NWI_REPAIR_DIR"])
OUTCSV=ROOT/"remotesensing"/"NAAMP_NWI_SITE_ASSIGNMENTS_REPAIRED_V0_3.csv"
OUTJSON=ROOT/"remotesensing"/"NAAMP_NWI_COVERAGE_REPAIRED_V0_3.json"

NWI_CODES="https://fwspublicservices.wim.usgs.gov/wetlandsmapservice/rest/services/Wetlands/MapServer/1/query"

def loadmod(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);assert s.loader;s.loader.exec_module(m);return m
flex=loadmod("flex",EXP/"run_naamp_flexible_common_environment_null.py")
hyd=loadmod("hyd",RS/"run_naamp_dynamic_hydrology_mechanism.py")
mem=flex.mem

def fetch(url,timeout=120):
    last=None
    for i in range(10):
        try:
            req=urllib.request.Request(url,headers={"User-Agent":"frogcs-nwi-repair-aggregate/0.1"})
            with urllib.request.urlopen(req,timeout=timeout) as r:return r.read()
        except Exception as e:
            last=e;time.sleep(min(60.0,2.0*(i+1)))
    raise last

def fetch_code_table():
    rows=[];offset=0
    while True:
        params={"where":"1=1",
          "outFields":"OBJECTID,ATTRIBUTE,WATER_REGIME,WATER_REGIME_NAME,WATER_REGIME_SUBGROUP,SYSTEM_NAME,CLASS_NAME",
          "returnGeometry":"false","orderByFields":"OBJECTID",
          "resultOffset":str(offset),"resultRecordCount":"500","f":"json"}
        obj=json.loads(fetch(NWI_CODES+"?"+urllib.parse.urlencode(params)).decode("utf-8"))
        if "error" in obj:raise RuntimeError(json.dumps(obj["error"]))
        batch=[z.get("attributes") or {} for z in (obj.get("features") or [])]
        rows.extend(batch)
        if len(batch)<500 and not obj.get("exceededTransferLimit",False):break
        if not batch:break
        offset+=len(batch)
    out={}
    for a in rows:
        attr=str(a.get("ATTRIBUTE") or "").strip()
        if attr:
            out[attr]={k:str(a.get(k) or "").strip() for k in [
              "WATER_REGIME","WATER_REGIME_NAME","WATER_REGIME_SUBGROUP","SYSTEM_NAME","CLASS_NAME"
            ]}
    if not out:raise RuntimeError("empty NWI code table")
    return out

def bval(x):
    return str(x).strip().lower() in ("true","1","yes")

base=pd.read_csv(BASE,dtype={"SiteID":str,"RouteNumber":str})
repfiles=sorted(REPAIR_DIR.glob("NWI_FAILED_REPAIR_SHARD_*.csv"))
if len(repfiles)!=8:raise RuntimeError(f"expected 8 repair shards, found {len(repfiles)}")
rep=pd.concat([pd.read_csv(p,dtype={"SiteID":str,"RouteNumber":str}) for p in repfiles],ignore_index=True)
if rep.duplicated(["SiteID"]).any():raise RuntimeError("duplicate repaired SiteID")

# Replace only originally failed rows with their response-blind retry result.
base=base.set_index("SiteID",drop=False)
rep=rep.set_index("SiteID",drop=False)
for sid,row in rep.iterrows():
    for col,val in row.items():
        base.loc[sid,col]=val
df=base.reset_index(drop=True)

# Normalize booleans and join official water-regime codes once.
df["query_success"]=df["query_success"].map(bval)
if "code_join_success" not in df.columns:df["code_join_success"]=False
df["code_join_success"]=df["code_join_success"].map(bval)
for col in ["WATER_REGIME","WATER_REGIME_NAME","WATER_REGIME_SUBGROUP","SYSTEM_NAME","CLASS_NAME"]:
    if col not in df.columns:df[col]=None

codes=fetch_code_table()
for i,r in df.loc[df["query_success"]].iterrows():
    wt=str(r.get("WETLAND_TYPE") or "")
    attr=str(r.get("ATTRIBUTE") or "").strip()
    if wt=="no_NWI_wetland_500m" or attr=="no_NWI_wetland_500m":
        for col in ["WATER_REGIME","WATER_REGIME_NAME","WATER_REGIME_SUBGROUP","SYSTEM_NAME","CLASS_NAME"]:
            df.at[i,col]="no_NWI_wetland_500m"
        df.at[i,"code_join_success"]=True
    else:
        z=codes.get(attr)
        if z is not None and z.get("WATER_REGIME_NAME"):
            for col,val in z.items():df.at[i,col]=val
            df.at[i,"code_join_success"]=True
        else:
            df.at[i,"code_join_success"]=False

df.to_csv(OUTCSV,index=False)

assign={
  str(r.SiteID):r for r in df.itertuples(index=False)
  if bool(r.query_success) and bool(r.code_join_success)
  and pd.notna(r.WATER_REGIME_NAME) and str(r.WATER_REGIME_NAME).strip()
  and pd.notna(r.WETLAND_TYPE) and str(r.WETLAND_TYPE).strip()
}
raw,runs,psub,dsub,hsub,pools,sampled,ss=flex.prepare_subset()
eligible=set(runs.RunID.astype(str));site=mem.site_map(raw,eligible);safe=hyd.strict_routes()
pairs=[];fail=Counter();focal=set()
for p,dct in zip(psub.itertuples(index=False),dsub):
    if str(p.RouteNumber) not in safe:
        fail["strict_geometry"]+=1;continue
    ids=mem.focal_siteids(p,dct,site)
    if ids is None or len(ids)!=10:
        fail["siteid_identity"]+=1;continue
    focal.update(ids)
    if any(str(s) not in assign for s in ids):
        fail["nwi_primary_missing"]+=1;continue
    pairs.append((str(p.route_cluster),str(p.State),ids))

success=len(set(assign).intersection({str(x) for x in focal}))
frac=success/len(focal) if focal else 0.0
routes=len({x[0] for x in pairs});states=len({x[1] for x in pairs})
gate=bool(frac>=.90 and len(pairs)>=1500 and routes>=300 and states>=15)
out={
 "analysis":"naamp_nwi_coverage_repaired_v0_3",
 "contract":"revision/NAAMP_NWI_RETRIEVAL_REPAIR_V0_3.md",
 "base_assignment_sha256":hashlib.sha256(BASE.read_bytes()).hexdigest(),
 "repair_rows":int(len(rep)),
 "site_assignment_rows":int(len(df)),
 "principal_focal_siteids":int(len(focal)),
 "primary_complete_focal_siteids":int(success),
 "primary_complete_fraction":frac,
 "raw_query_success_focal_siteids":int(df.loc[df.SiteID.astype(str).isin({str(x) for x in focal}),"query_success"].sum()),
 "code_join_success_focal_siteids":int(df.loc[df.SiteID.astype(str).isin({str(x) for x in focal}),"code_join_success"].sum()),
 "water_regime_counts":{str(k):int(v) for k,v in df.loc[df.SiteID.astype(str).isin({str(x) for x in focal}),"WATER_REGIME_NAME"].value_counts(dropna=True).to_dict().items()},
 "wetland_type_counts":{str(k):int(v) for k,v in df.loc[df.SiteID.astype(str).isin({str(x) for x in focal}),"WETLAND_TYPE"].value_counts(dropna=True).to_dict().items()},
 "pair_coverage":{"pairs":len(pairs),"routes":routes,"states":states,"failures":dict(fail)},
 "gate_pass":gate,
 "frog_endpoint_calculated":False,
 "assignment_csv_sha256":hashlib.sha256(OUTCSV.read_bytes()).hexdigest()
}
OUTJSON.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
print(json.dumps(out,indent=2,sort_keys=True))
