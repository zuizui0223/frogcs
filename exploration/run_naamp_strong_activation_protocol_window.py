#!/usr/bin/env python3
from __future__ import annotations
import importlib.util,json
from collections import defaultdict
from pathlib import Path
import numpy as np,pandas as pd,statsmodels.formula.api as smf

ROOT=Path(__file__).resolve().parents[1]; NAAMP=ROOT/"scripts"/"naamp"; OUT=ROOT/"exploration"/"NAAMP_STRONG_ACTIVATION_PROTOCOL_WINDOW_RECEIPT_V0_1.json"; Q=1.959963984540054

def loadmod(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);assert s.loader;s.loader.exec_module(m);return m
base=loadmod("base",NAAMP/"run_naamp_ecological_pulse.py"); spatial=loadmod("spatial",NAAMP/"run_naamp_spatial_taxonomic_activation_decomposition.py")

def ci(raw,eligible,sampled):
    v=defaultdict(list)
    for r in raw["Counts.csv"]:
        rid=(r.get("RunID") or "").strip();st=(r.get("StopNumber") or "").strip();sp=(r.get("Species") or "").strip()
        if rid not in eligible or st not in sampled.get(rid,set()) or not sp:continue
        try:x=int(float((r.get("CallingIndex") or "").strip()))
        except:continue
        if x in (1,2,3):v[(rid,st,sp)].append(x)
    by=defaultdict(dict)
    for (rid,st,sp),x in v.items():by[(rid,st)][sp]=max(x)
    return by

def metrics(p,sampled,by):
    w=str(p.wet_RunID);d=str(p.dry_RunID);score=0.;count=0
    for st in sorted(sampled[w]):
        wm=by.get((w,st),{});dm=by.get((d,st),{})
        for sp in set(wm)|set(dm):
            wi=int(wm.get(sp,0));di=int(dm.get(sp,0))
            if di==0 and wi>=2:score+=wi;count+=1
    return score,float(count)

def fit(d,response):
    f=f"{response} ~ rain_contrast + temp_difference + doy_difference + year_gap + C(State) + C(RunNumber)"
    m=smf.ols(f,data=d).fit(cov_type="cluster",cov_kwds={"groups":d["route_cluster"]})
    b=float(m.params["rain_contrast"]);se=float(m.bse["rain_contrast"])
    return {"beta":b,"se":se,"ci95":[b-Q*se,b+Q*se],"p":float(m.pvalues["rain_contrast"]),"n_pairs":int(len(d)),"n_routes":int(d.route_cluster.nunique())}

def pack(d):
    ms={x:fit(d,x) for x in ("strong_new_score","strong_new_count")}
    return {"n_pairs":int(len(d)),"n_routes":int(d.route_cluster.nunique()),"models":ms,"both_positive":all(v["beta"]>0 for v in ms.values()),"both_ci_positive":all(v["ci95"][0]>0 for v in ms.values())}

def main():
    raw=base.load();runs,sets=base.build_runs(raw);eligible=set(runs["RunID"].astype(str));sampled,_=spatial.stop_matrix(raw,eligible)
    d=base.pair_runs(runs,sets).copy().reset_index(drop=True);by=ci(raw,eligible,sampled)
    vals=[metrics(p,sampled,by) for p in d.itertuples(index=False)]
    d["strong_new_score"]=[x[0] for x in vals];d["strong_new_count"]=[x[1] for x in vals]
    primary=d[d["dry_days_since_rain"]>=4].copy()
    secondary=d[d["wet_days_since_rain"]>=4].copy()
    p=pack(primary);s=pack(secondary)
    out={"analysis":"naamp_strong_activation_protocol_window_v0_1","contract":"exploration/NAAMP_STRONG_ACTIVATION_PROTOCOL_WINDOW_CONTRACT_V0_1.json","source_pairs":int(len(d)),"primary_crosses_three_day_window":p,"secondary_both_outside_three_day_window":s,"classification":{"primary_pass":p["both_positive"],"primary_strong_pass":p["both_ci_positive"]},"interpretation_boundary":{"secondary_is_descriptive":True,"causal_rainfall_claim":False}}
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print(json.dumps(out,indent=2,sort_keys=True))
if __name__=="__main__":main()
