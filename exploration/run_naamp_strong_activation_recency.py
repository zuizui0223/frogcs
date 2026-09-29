#!/usr/bin/env python3
from __future__ import annotations
import importlib.util,json
from collections import defaultdict
from pathlib import Path
import numpy as np,pandas as pd,statsmodels.formula.api as smf

ROOT=Path(__file__).resolve().parents[1]; NAAMP=ROOT/"scripts"/"naamp"
OUT=ROOT/"exploration"/"NAAMP_STRONG_ACTIVATION_RECENCY_RECEIPT_V0_1.json"; Q=1.959963984540054

def loadmod(name,path):
    s=importlib.util.spec_from_file_location(name,path); m=importlib.util.module_from_spec(s)
    assert s.loader; s.loader.exec_module(m); return m

base=loadmod("base",NAAMP/"run_naamp_ecological_pulse.py")
spatial=loadmod("spatial",NAAMP/"run_naamp_spatial_taxonomic_activation_decomposition.py")

def ci_map(raw,eligible,sampled):
    vals=defaultdict(list)
    for r in raw["Counts.csv"]:
        rid=(r.get("RunID") or "").strip(); st=(r.get("StopNumber") or "").strip(); sp=(r.get("Species") or "").strip()
        if rid not in eligible or st not in sampled.get(rid,set()) or not sp: continue
        try: x=int(float((r.get("CallingIndex") or "").strip()))
        except Exception: continue
        if x in (1,2,3): vals[(rid,st,sp)].append(x)
    by=defaultdict(dict)
    for (rid,st,sp),v in vals.items(): by[(rid,st)][sp]=max(v)
    return by

def strong_score(p,sampled,by):
    w=str(p.wet_RunID); d=str(p.dry_RunID); score=0.0; count=0
    for st in sorted(sampled[w]):
        wm=by.get((w,st),{}); dm=by.get((d,st),{})
        for sp in set(wm)|set(dm):
            wi=int(wm.get(sp,0)); di=int(dm.get(sp,0))
            if di==0 and wi>=2:
                score+=wi; count+=1
    return score,float(count)

def fit_base(d):
    f="strong_new_score ~ rain_contrast + temp_difference + doy_difference + year_gap + C(State) + C(RunNumber)"
    m=smf.ols(f,data=d).fit(cov_type="cluster",cov_kwds={"groups":d["route_cluster"]})
    b=float(m.params["rain_contrast"]); se=float(m.bse["rain_contrast"])
    return {"n_pairs":int(len(d)),"n_routes":int(d.route_cluster.nunique()),"beta":b,"se":se,"ci95":[b-Q*se,b+Q*se],"p":float(m.pvalues["rain_contrast"])}

def fit_interaction(d):
    f="strong_new_score ~ rain_contrast * immediate + temp_difference + doy_difference + year_gap + C(State) + C(RunNumber)"
    m=smf.ols(f,data=d).fit(cov_type="cluster",cov_kwds={"groups":d["route_cluster"]})
    term="rain_contrast:immediate"
    b=float(m.params[term]); se=float(m.bse[term])
    return {"n_pairs":int(len(d)),"n_routes":int(d.route_cluster.nunique()),"interaction_beta":b,"se":se,"ci95":[b-Q*se,b+Q*se],"p":float(m.pvalues[term]),"support":bool(b>0 and b-Q*se>0)}

def bin_name(x):
    x=float(x)
    if x<=1: return "0-1"
    if x<=3: return "2-3"
    if x<=7: return "4-7"
    return ">=8"

def main():
    raw=base.load(); runs,sets=base.build_runs(raw); eligible=set(runs["RunID"].astype(str))
    sampled,_=spatial.stop_matrix(raw,eligible); by=ci_map(raw,eligible,sampled)
    pairs=base.pair_runs(runs,sets).copy().reset_index(drop=True)
    vals=[strong_score(p,sampled,by) for p in pairs.itertuples(index=False)]
    pairs["strong_new_score"]=[v[0] for v in vals]; pairs["strong_new_count"]=[v[1] for v in vals]
    pairs["recency_bin"]=[bin_name(x) for x in pairs["wet_days_since_rain"]]
    strata={}
    for bn in ("0-1","2-3","4-7",">=8"):
        d=pairs[pairs.recency_bin==bn].copy()
        strata[bn]=fit_base(d) if len(d)>=100 and d.route_cluster.nunique()>=30 else {"n_pairs":int(len(d)),"n_routes":int(d.route_cluster.nunique()),"estimable":False}
    primary=pairs[(pairs.wet_days_since_rain<=1)|(pairs.wet_days_since_rain>=4)].copy()
    primary["immediate"]=(primary.wet_days_since_rain<=1).astype(int)
    counts={
      "immediate_pairs":int((primary.immediate==1).sum()),
      "delayed_pairs":int((primary.immediate==0).sum()),
      "immediate_routes":int(primary.loc[primary.immediate==1,"route_cluster"].nunique()),
      "delayed_routes":int(primary.loc[primary.immediate==0,"route_cluster"].nunique())
    }
    gate=bool(counts["immediate_pairs"]>=300 and counts["delayed_pairs"]>=300 and counts["immediate_routes"]>=100 and counts["delayed_routes"]>=100)
    primary_fit=fit_interaction(primary) if gate else None
    exact=primary[primary.year_gap==1].copy()
    exact_fit=fit_interaction(exact) if len(exact)>=300 and exact.route_cluster.nunique()>=100 else None
    out={
      "analysis":"naamp_strong_activation_recency_v0_1",
      "contract":"exploration/NAAMP_STRONG_ACTIVATION_RECENCY_CONTRACT_V0_1.json",
      "coverage":{"all_pairs":int(len(pairs)),"recency_counts":pairs.recency_bin.value_counts().to_dict(),**counts,"primary_gate":gate},
      "primary_immediate_vs_delayed":primary_fit,
      "stratum_models":strata,
      "exact_consecutive_year_sensitivity":exact_fit,
      "classification":{"transient_activation_window_supported":bool(primary_fit and primary_fit["support"])},
      "interpretation_boundary":{"causal_rainfall_claim":False,"physiological_mechanism_identified":False,"recency_is_coarse":True}
    }
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n"); print(json.dumps(out,indent=2,sort_keys=True))
if __name__=="__main__": main()
