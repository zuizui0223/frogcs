#!/usr/bin/env python3
from __future__ import annotations
import importlib.util, json, os
from pathlib import Path
from collections import Counter
import pandas as pd

ROOT=Path(__file__).resolve().parents[2]
EXP=ROOT/"exploration"
RS=ROOT/"scripts"/"remotesensing"
INDIR=Path(os.environ.get("NWI_SHARD_DIR",str(ROOT/"remotesensing"/"nwi_inputs")))
OUTCSV=ROOT/"remotesensing"/"NAAMP_NWI_SITE_ASSIGNMENTS_V0_1.csv"
OUTJSON=ROOT/"remotesensing"/"NAAMP_NWI_COVERAGE_V0_1.json"

def loadmod(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);assert s.loader;s.loader.exec_module(m);return m
flex=loadmod("flex",EXP/"run_naamp_flexible_common_environment_null.py")
hyd=loadmod("hyd",RS/"run_naamp_dynamic_hydrology_mechanism.py")
mem=flex.mem

files=sorted(INDIR.glob("NWI_SITE_ASSIGNMENTS_SHARD_*.csv"))
if len(files)!=16: raise RuntimeError(f"expected 16 shards, found {len(files)}")
df=pd.concat([pd.read_csv(p,dtype={"SiteID":str,"RouteNumber":str}) for p in files],ignore_index=True)
if df.duplicated(["SiteID"]).any(): raise RuntimeError("duplicate SiteID assignment")
df.to_csv(OUTCSV,index=False)

assign={str(r.SiteID):r for r in df.itertuples(index=False) if bool(r.query_success) and pd.notna(r.WETLAND_TYPE)}
raw,runs,psub,dsub,hsub,pools,sampled,ss=flex.prepare_subset()
eligible=set(runs.RunID.astype(str)); site=mem.site_map(raw,eligible); safe=hyd.strict_routes()
pairs=[]; fail=Counter(); focal_siteids=set()
for p,dct in zip(psub.itertuples(index=False),dsub):
    if str(p.RouteNumber) not in safe:
        fail["strict_geometry"]+=1; continue
    ids=mem.focal_siteids(p,dct,site)
    if ids is None or len(ids)!=10:
        fail["siteid_identity"]+=1; continue
    focal_siteids.update(ids)
    if any(s not in assign for s in ids):
        fail["nwi_query_missing"]+=1; continue
    pairs.append((str(p.route_cluster),str(p.State),ids))

success_siteids=len(set(assign).intersection(focal_siteids))
site_success_fraction=success_siteids/len(focal_siteids) if focal_siteids else 0.0
routes=len({p[0] for p in pairs}); states=len({p[1] for p in pairs})
gate=bool(site_success_fraction>=.90 and len(pairs)>=1500 and routes>=300 and states>=15)

out={
 "analysis":"naamp_nwi_coverage_v0_1",
 "contract":"revision/NAAMP_NWI_RAIN_FILTER_MECHANISM_CONTRACT_V0_1.md",
 "site_assignment_rows":int(len(df)),
 "principal_focal_siteids":int(len(focal_siteids)),
 "query_success_focal_siteids":int(success_siteids),
 "query_success_fraction":site_success_fraction,
 "wetland_type_counts":{str(k):int(v) for k,v in df.loc[df.query_success==True,"WETLAND_TYPE"].value_counts(dropna=True).to_dict().items()},
 "pair_coverage":{"pairs":len(pairs),"routes":routes,"states":states,"failures":dict(fail)},
 "gate_pass":gate,
 "frog_endpoint_calculated":False
}
OUTJSON.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
print(json.dumps(out,indent=2,sort_keys=True))
