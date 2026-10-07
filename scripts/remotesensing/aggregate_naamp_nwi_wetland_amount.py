#!/usr/bin/env python3
from __future__ import annotations
import hashlib, importlib.util, json, os
from collections import Counter
from pathlib import Path
import pandas as pd

ROOT=Path(__file__).resolve().parents[2]
EXP=ROOT/"exploration"
INDIR=Path(os.environ.get("NWI_AMOUNT_SHARD_DIR",str(ROOT/"remotesensing"/"nwi_amount_inputs")))
OUTCSV=ROOT/"remotesensing"/"NAAMP_NWI_WETLAND_AMOUNT_V0_1.csv"
OUTJSON=ROOT/"remotesensing"/"NAAMP_NWI_WETLAND_AMOUNT_COVERAGE_V0_1.json"

def loadmod(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);assert s.loader;s.loader.exec_module(m);return m
flex=loadmod("flex",EXP/"run_naamp_flexible_common_environment_null.py")
mem=flex.mem

files=sorted(INDIR.glob("NWI_WETLAND_AMOUNT_SHARD_*.csv"))
if len(files)!=8:raise RuntimeError(f"expected 8 shards, found {len(files)}")
df=pd.concat([pd.read_csv(p,dtype={"SiteID":str,"RouteNumber":str}) for p in files],ignore_index=True)
if df.duplicated(["SiteID"]).any():raise RuntimeError("duplicate SiteID wetland-amount assignment")
df["query_success"]=df["query_success"].map(lambda x:str(x).strip().lower() in ("true","1","yes"))
df.to_csv(OUTCSV,index=False)

assign={
 str(r.SiteID):float(r.wetland_area_fraction_500m)
 for r in df.itertuples(index=False)
 if bool(r.query_success) and pd.notna(r.wetland_area_fraction_500m)
}

raw,runs,psub,dsub,hsub,pools,sampled,ss=flex.prepare_subset()
eligible=set(runs.RunID.astype(str));site=mem.site_map(raw,eligible)
pairs=[];focal=set();fail=Counter()
for p,dct in zip(psub.itertuples(index=False),dsub):
    ids=mem.focal_siteids(p,dct,site)
    if ids is None or len(ids)!=10:
        fail["siteid_identity"]+=1;continue
    focal.update(str(s) for s in ids)
    if any(str(s) not in assign for s in ids):
        fail["wetland_amount_missing"]+=1;continue
    pairs.append((str(p.route_cluster),str(p.State),[str(s) for s in ids]))

success=len(set(assign).intersection(focal))
frac=success/len(focal) if focal else 0.0
routes=len({x[0] for x in pairs});states=len({x[1] for x in pairs})
gate=bool(frac>=.90 and len(pairs)>=1500 and routes>=300 and states>=15)
out={
 "analysis":"naamp_nwi_wetland_amount_coverage_v0_1",
 "contract":"revision/NAAMP_NWI_WETLAND_AMOUNT_RAIN_MECHANISM_CONTRACT_V0_1.md",
 "site_rows":int(len(df)),
 "principal_focal_siteids":int(len(focal)),
 "successful_focal_siteids":int(success),
 "success_fraction":frac,
 "pair_coverage":{"pairs":len(pairs),"routes":routes,"states":states,"failures":dict(fail)},
 "gate_pass":gate,
 "metric_summary":{
   "median":float(df.loc[df.query_success,"wetland_area_fraction_500m"].median()),
   "q10":float(df.loc[df.query_success,"wetland_area_fraction_500m"].quantile(.10)),
   "q90":float(df.loc[df.query_success,"wetland_area_fraction_500m"].quantile(.90)),
   "zero_fraction":float((df.loc[df.query_success,"wetland_area_fraction_500m"]==0).mean())
 },
 "frog_endpoint_calculated":False,
 "assignment_csv_sha256":hashlib.sha256(OUTCSV.read_bytes()).hexdigest()
}
OUTJSON.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
print(json.dumps(out,indent=2,sort_keys=True))
