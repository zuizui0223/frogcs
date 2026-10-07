#!/usr/bin/env python3
from __future__ import annotations
import importlib.util, json, os
from collections import defaultdict
from pathlib import Path
import pandas as pd

ROOT=Path(__file__).resolve().parents[2]
EXP=ROOT/"exploration"
BASE=Path(os.environ["NWI_BASE_ASSIGNMENTS"])

def loadmod(name,path):
    s=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(s); assert s.loader; s.loader.exec_module(m); return m

flex=loadmod("flex",EXP/"run_naamp_flexible_common_environment_null.py")
df=pd.read_csv(BASE,dtype={"SiteID":str,"RouteNumber":str})
q=df["query_success"].map(lambda x:str(x).strip().lower() in ("true","1","yes"))
failed_routes=sorted(set(df.loc[~q,"RouteNumber"].astype(str)))

raw,runs,psub,dsub,hsub,pools,sampled,ss=flex.prepare_subset()
m=defaultdict(set)
for r in runs.itertuples(index=False):
    m[str(r.RouteNumber)].add(str(r.State))

route_rows=[]
state_routes=defaultdict(list)
unmapped=[]
for rid in failed_routes:
    states=sorted(m.get(rid,set()))
    if len(states)==1:
        st=states[0]; state_routes[st].append(rid)
    else:
        unmapped.append({"RouteNumber":rid,"states":states})
    sub=df[(df.RouteNumber.astype(str)==rid)&(~q)]
    route_rows.append({
      "RouteNumber":rid,
      "states":states,
      "failed_siteids":int(len(sub)),
      "lat_median":float(pd.to_numeric(sub.lat).median()),
      "lon_median":float(pd.to_numeric(sub.lon).median()),
    })

out={
 "analysis":"nwi_failed_route_state_audit_v0_1",
 "failed_routes":len(failed_routes),
 "failed_siteids":int((~q).sum()),
 "states":{st:{"routes":len(rs),"route_numbers":sorted(rs)} for st,rs in sorted(state_routes.items())},
 "state_count":len(state_routes),
 "unmapped":unmapped,
 "routes":route_rows,
 "frog_endpoint_calculated":False
}
print(json.dumps(out,indent=2,sort_keys=True))
