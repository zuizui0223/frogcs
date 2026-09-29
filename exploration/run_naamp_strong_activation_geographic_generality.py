#!/usr/bin/env python3
from __future__ import annotations
import importlib.util,json
from collections import defaultdict
from pathlib import Path
import numpy as np,pandas as pd,statsmodels.formula.api as smf

ROOT=Path(__file__).resolve().parents[1]; NAAMP=ROOT/"scripts"/"naamp"
OUT=ROOT/"exploration"/"NAAMP_STRONG_ACTIVATION_GEOGRAPHIC_GENERALITY_RECEIPT_V0_1.json"; Q=1.959963984540054

def loadmod(name,path):
    s=importlib.util.spec_from_file_location(name,path); m=importlib.util.module_from_spec(s); assert s.loader; s.loader.exec_module(m); return m
base=loadmod("base",NAAMP/"run_naamp_ecological_pulse.py")
spatial=loadmod("spatial",NAAMP/"run_naamp_spatial_taxonomic_activation_decomposition.py")

def ci(raw,eligible,sampled):
    v=defaultdict(list)
    for r in raw["Counts.csv"]:
        rid=(r.get("RunID") or "").strip(); st=(r.get("StopNumber") or "").strip(); sp=(r.get("Species") or "").strip()
        if rid not in eligible or st not in sampled.get(rid,set()) or not sp: continue
        try: x=int(float((r.get("CallingIndex") or "").strip()))
        except: continue
        if x in (1,2,3): v[(rid,st,sp)].append(x)
    by=defaultdict(dict)
    for (rid,st,sp),x in v.items(): by[(rid,st)][sp]=max(x)
    return by

def score(p,sampled,by):
    w=str(p.wet_RunID); d=str(p.dry_RunID); s=0.0
    for st in sorted(sampled[w]):
        wm=by.get((w,st),{}); dm=by.get((d,st),{})
        for sp in set(wm)|set(dm):
            wi=int(wm.get(sp,0)); di=int(dm.get(sp,0))
            if di==0 and wi>=2: s+=wi
    return s

def fit(d):
    f="strong_new_score ~ rain_contrast + temp_difference + doy_difference + year_gap + C(State) + C(RunNumber)"
    m=smf.ols(f,data=d).fit(cov_type="cluster",cov_kwds={"groups":d["route_cluster"]})
    b=float(m.params["rain_contrast"]); se=float(m.bse["rain_contrast"])
    return {"beta":b,"se":se,"ci95":[b-Q*se,b+Q*se],"p":float(m.pvalues["rain_contrast"]),"n_pairs":int(len(d)),"n_routes":int(d.route_cluster.nunique())}

def main():
    raw=base.load(); runs,sets=base.build_runs(raw); eligible=set(runs["RunID"].astype(str))
    sampled,_=spatial.stop_matrix(raw,eligible); pairs=base.pair_runs(runs,sets).copy().reset_index(drop=True); by=ci(raw,eligible,sampled)
    pairs["strong_new_score"]=[score(p,sampled,by) for p in pairs.itertuples(index=False)]
    full=fit(pairs); states=sorted(pairs.State.astype(str).unique()); loo={}
    for st in states: loo[st]=fit(pairs[pairs.State.astype(str)!=st].copy())
    allpos=all(v["beta"]>0 for v in loo.values()); allci=all(v["ci95"][0]>0 for v in loo.values())
    out={"analysis":"naamp_strong_activation_geographic_generality_v0_1","contract":"exploration/NAAMP_STRONG_ACTIVATION_GEOGRAPHIC_GENERALITY_CONTRACT_V0_1.json","full":full,"n_states":len(states),"leave_one_state_out":loo,"classification":{"pass_all_positive":allpos,"strong_pass_all_ci_positive":allci,"min_beta":min(v["beta"] for v in loo.values()),"min_ci_lower":min(v["ci95"][0] for v in loo.values())},"interpretation_boundary":{"universal_claim":False,"every_state_claim":False}}
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n"); print(json.dumps(out,indent=2,sort_keys=True))
if __name__=="__main__": main()
