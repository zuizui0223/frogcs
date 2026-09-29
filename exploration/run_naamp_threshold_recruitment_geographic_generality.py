#!/usr/bin/env python3
from __future__ import annotations
import importlib.util,json
from collections import defaultdict
from pathlib import Path
import numpy as np,pandas as pd
import statsmodels.formula.api as smf

ROOT=Path(__file__).resolve().parents[1]
NAAMP=ROOT/"scripts"/"naamp"
OUT=ROOT/"exploration"/"NAAMP_THRESHOLD_RECRUITMENT_GEOGRAPHIC_GENERALITY_RECEIPT_V0_1.json"
Q=1.959963984540054

def loadmod(name,path):
    spec=importlib.util.spec_from_file_location(name,path); mod=importlib.util.module_from_spec(spec)
    assert spec.loader; spec.loader.exec_module(mod); return mod

base=loadmod("base",NAAMP/"run_naamp_ecological_pulse.py")
spatial=loadmod("spatial",NAAMP/"run_naamp_spatial_taxonomic_activation_decomposition.py")

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
    wet=str(p.wet_RunID); dry=str(p.dry_RunID); stops=sorted(sampled[wet])
    if len(stops)!=10 or set(stops)!=set(sampled[dry]): raise RuntimeError("stop alignment")
    activation=deactivation=shared=total=strong=0.0
    for st in stops:
        wm=by.get((wet,st),{}); dm=by.get((dry,st),{})
        for sp in set(wm)|set(dm):
            w=int(wm.get(sp,0)); d=int(dm.get(sp,0)); diff=w-d; total+=diff
            if d==0 and w>0:
                activation+=w
                if w in (2,3): strong+=w
            elif d>0 and w==0: deactivation-=d
            elif d>0 and w>0: shared+=diff
    if abs(total-activation-deactivation-shared)>1e-12: raise RuntimeError("CI identity")
    return {"ci_total":total,"ci_activation":activation,"ci_deactivation":deactivation,"ci_shared_intensity":shared,"strong_new_score":strong}

def fit(df,response,include_state=True):
    state_term=" + C(State)" if include_state else ""
    formula=f"{response} ~ rain_contrast + temp_difference + doy_difference + year_gap{state_term} + C(RunNumber)"
    m=smf.ols(formula,data=df).fit(cov_type="cluster",cov_kwds={"groups":df["route_cluster"]})
    b=float(m.params["rain_contrast"]); se=float(m.bse["rain_contrast"])
    return {"beta":b,"se":se,"ci95":[b-Q*se,b+Q*se],"p":float(m.pvalues["rain_contrast"]),"n_pairs":int(len(df)),"n_routes":int(df.route_cluster.nunique())}

def package(df,include_state=True):
    mods={x:fit(df,x,include_state) for x in ["ci_total","ci_activation","ci_shared_intensity","strong_new_score"]}
    total=mods["ci_total"]["beta"]; act=mods["ci_activation"]["beta"]; shared=mods["ci_shared_intensity"]["beta"]
    share=float(act/total) if abs(total)>1e-12 else None
    gate=bool(total>0 and mods["ci_activation"]["ci95"][0]>0 and share is not None and share>0.5 and act>shared)
    return {"models":mods,"activation_share":share,"threshold_dominant":gate}

def main():
    raw=base.load(); runs,sets=base.build_runs(raw); eligible=set(runs["RunID"].astype(str))
    sampled,_=spatial.stop_matrix(raw,eligible); by=build_ci(raw,eligible,sampled)
    pairs=base.pair_runs(runs,sets).copy().reset_index(drop=True)
    rows=[]
    for p in pairs.itertuples(index=False):
        r=p._asdict(); r.update(metrics(p,sampled,by)); rows.append(r)
    df=pd.DataFrame(rows)
    states=sorted(df.State.astype(str).unique())

    full=package(df,True)
    loo=[]
    for st in states:
        d=df[df.State.astype(str)!=st].copy()
        z=package(d,True)
        loo.append({
          "omitted_state":st,
          **z,
          "strong_new_ci_positive":bool(z["models"]["strong_new_score"]["ci95"][0]>0)
        })
    no_single=all(x["threshold_dominant"] for x in loo)
    strong=bool(no_single and all(x["strong_new_ci_positive"] for x in loo))

    state_specific=[]
    for st in states:
        d=df[df.State.astype(str)==st].copy()
        if len(d)<50 or d.route_cluster.nunique()<10:
            state_specific.append({"state":st,"n_pairs":int(len(d)),"n_routes":int(d.route_cluster.nunique()),"estimable_gate":False})
            continue
        z=package(d,False)
        state_specific.append({
          "state":st,"n_pairs":int(len(d)),"n_routes":int(d.route_cluster.nunique()),"estimable_gate":True,
          "activation_beta":z["models"]["ci_activation"]["beta"],
          "activation_ci95":z["models"]["ci_activation"]["ci95"],
          "strong_new_beta":z["models"]["strong_new_score"]["beta"],
          "strong_new_ci95":z["models"]["strong_new_score"]["ci95"],
          "threshold_dominant":z["threshold_dominant"]
        })

    estim=[x for x in state_specific if x["estimable_gate"]]
    out={
      "analysis":"naamp_threshold_recruitment_geographic_generality_v0_1",
      "contract":"exploration/NAAMP_THRESHOLD_RECRUITMENT_GEOGRAPHIC_GENERALITY_CONTRACT_V0_1.json",
      "coverage":{"pairs":int(len(df)),"routes":int(df.route_cluster.nunique()),"states":len(states)},
      "full":full,
      "leave_one_state_out":{
        "results":loo,
        "all_threshold_dominant":bool(no_single),
        "all_strong_new_ci_positive":bool(all(x["strong_new_ci_positive"] for x in loo)),
        "strong_pass":strong,
        "minimum_activation_share":float(min(x["activation_share"] for x in loo)),
        "minimum_activation_ci_lower":float(min(x["models"]["ci_activation"]["ci95"][0] for x in loo)),
        "minimum_strong_new_ci_lower":float(min(x["models"]["strong_new_score"]["ci95"][0] for x in loo))
      },
      "state_specific":{
        "results":state_specific,
        "n_estimable_states":len(estim),
        "positive_activation_fraction":float(np.mean([x["activation_beta"]>0 for x in estim])) if estim else None,
        "positive_strong_new_fraction":float(np.mean([x["strong_new_beta"]>0 for x in estim])) if estim else None,
        "threshold_dominant_fraction":float(np.mean([x["threshold_dominant"] for x in estim])) if estim else None
      },
      "classification":{
        "no_single_state_threshold_dependence":bool(no_single),
        "strong_geographic_robustness":strong,
        "worldwide_universality_authorized":False
      },
      "interpretation_boundary":{"state_specific_significance_is_not_gate":True,"causal_rainfall_claim":False,"submission_story_change_authorized":False}
    }
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n"); print(json.dumps({k:v for k,v in out.items() if k not in ("leave_one_state_out","state_specific")},indent=2)); print(json.dumps({"LOO":out["leave_one_state_out"],"state_summary":{k:v for k,v in out["state_specific"].items() if k!="results"}},indent=2))

if __name__=="__main__": main()
