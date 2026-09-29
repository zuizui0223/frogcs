#!/usr/bin/env python3
from __future__ import annotations
import importlib.util,json
from collections import defaultdict
from pathlib import Path
import numpy as np,pandas as pd
import statsmodels.formula.api as smf

ROOT=Path(__file__).resolve().parents[1]
NAAMP=ROOT/"scripts"/"naamp"
OUT=ROOT/"exploration"/"NAAMP_NEW_ACTIVATION_STRENGTH_RECEIPT_V0_1.json"
Q=1.959963984540054

def loadmod(name,path):
    spec=importlib.util.spec_from_file_location(name,path); mod=importlib.util.module_from_spec(spec)
    assert spec.loader; spec.loader.exec_module(mod); return mod

base=loadmod("base",NAAMP/"run_naamp_ecological_pulse.py")
spatial=loadmod("spatial",NAAMP/"run_naamp_spatial_taxonomic_activation_decomposition.py")
sameobs=loadmod("sameobs",NAAMP/"run_naamp_same_observer_robustness.py")

def build_ci(raw,eligible,sampled):
    vals=defaultdict(list)
    for r in raw["Counts.csv"]:
        rid=(r.get("RunID") or "").strip(); st=(r.get("StopNumber") or "").strip(); sp=(r.get("Species") or "").strip()
        if rid not in eligible or st not in sampled.get(rid,set()) or not sp: continue
        try: ci=int(float((r.get("CallingIndex") or "").strip()))
        except Exception: continue
        if ci in (1,2,3): vals[(rid,st,sp)].append(ci)
    by=defaultdict(dict)
    for (rid,st,sp),v in vals.items(): by[(rid,st)][sp]=max(v)
    return by

def metrics(p,sampled,by):
    wet=str(p.wet_RunID); dry=str(p.dry_RunID)
    stops=sorted(sampled[wet])
    if set(stops)!=set(sampled[dry]) or len(stops)!=10: raise RuntimeError("unaligned stops")
    weak_score=strong_score=0.0; weak_count=strong_count=0
    activation=0.0
    for st in stops:
        wm=by.get((wet,st),{}); dm=by.get((dry,st),{})
        for sp in set(wm)|set(dm):
            w=int(wm.get(sp,0)); d=int(dm.get(sp,0))
            if d==0 and w>0:
                activation+=w
                if w==1: weak_score+=1; weak_count+=1
                else: strong_score+=w; strong_count+=1
    if abs(activation-weak_score-strong_score)>1e-12: raise RuntimeError("activation identity failed")
    return {
      "ci_activation":activation,
      "weak_new_score":weak_score,
      "strong_new_score":strong_score,
      "weak_new_count":float(weak_count),
      "strong_new_count":float(strong_count)
    }

def fit(df,response):
    x=df[np.isfinite(pd.to_numeric(df[response],errors="coerce"))].copy()
    formula=f"{response} ~ rain_contrast + temp_difference + doy_difference + year_gap + C(State) + C(RunNumber)"
    m=smf.ols(formula,data=x).fit(cov_type="cluster",cov_kwds={"groups":x["route_cluster"]})
    b=float(m.params["rain_contrast"]); se=float(m.bse["rain_contrast"])
    return {"beta":b,"se":se,"ci95":[b-Q*se,b+Q*se],"p":float(m.pvalues["rain_contrast"]),"n_pairs":len(x),"n_routes":int(x.route_cluster.nunique())}

def package(pairs,sampled,by):
    rows=[]
    for p in pairs.itertuples(index=False):
        r=p._asdict(); r.update(metrics(p,sampled,by)); rows.append(r)
    d=pd.DataFrame(rows)
    mods={x:fit(d,x) for x in ["ci_activation","weak_new_score","strong_new_score","weak_new_count","strong_new_count"]}
    ba=mods["ci_activation"]["beta"]; bs=mods["strong_new_score"]["beta"]
    share=float(bs/ba) if abs(ba)>1e-12 else None
    strong=bool(bs>0 and mods["strong_new_score"]["ci95"][0]>0)
    count=bool(mods["strong_new_count"]["beta"]>0 and mods["strong_new_count"]["ci95"][0]>0)
    return {
      "models":mods,
      "strong_score_share_of_activation_beta":share,
      "classification":{"strong_new_activation_supported":strong,"strong_new_count_supported":count}
    }

def main():
    raw=base.load(); runs,sets=base.build_runs(raw); eligible=set(runs["RunID"].astype(str))
    sampled,_=spatial.stop_matrix(raw,eligible); by=build_ci(raw,eligible,sampled)
    allpairs=base.pair_runs(runs,sets).copy().reset_index(drop=True)
    _,same=sameobs.same_observer_pairs(raw,runs,sets)
    full=package(allpairs,sampled,by); sobs=package(same,sampled,by)
    out={
      "analysis":"naamp_new_activation_strength_v0_1",
      "contract":"exploration/NAAMP_NEW_ACTIVATION_STRENGTH_CONTRACT_V0_1.json",
      "coverage":{"all_pairs":int(len(allpairs)),"same_observer_pairs":int(len(same))},
      "full_sample":full,
      "same_observer":sobs,
      "classification":{
        "strong_new_activation_supported_full":bool(full["classification"]["strong_new_activation_supported"]),
        "observer_robust_strong_new_activation":bool(full["classification"]["strong_new_activation_supported"] and sobs["classification"]["strong_new_activation_supported"])
      },
      "interpretation_boundary":{
        "simple_weak_call_detection_only_explanation_weakened":bool(full["classification"]["strong_new_activation_supported"]),
        "all_detectability_bias_eliminated":False,
        "physiological_mechanism_identified":False,
        "causal_rainfall_claim":False
      }
    }
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n"); print(json.dumps(out,indent=2,sort_keys=True))

if __name__=="__main__": main()
