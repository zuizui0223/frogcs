#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
EXP=ROOT/"exploration"
NAAMP=ROOT/"scripts"/"naamp"
OUT=EXP/"NAAMP_BOUNDED_ROUTE_NIGHT_SAME_OBSERVER_RECEIPT_V0_1.json"

B=1000
SEED=2840229
ANCHOR=0.75
EPS=1e-7

def loadmod(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    mod=importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(mod)
    return mod

rain=loadmod("rain_amount_common",EXP/"run_naamp_rain_amount_common_environment_null.py")
flex=rain.flex
joint=rain.joint
uniform=rain.uniform
sameobs=loadmod("sameobs",NAAMP/"run_naamp_same_observer_robustness.py")

def terms(y,q):
    e=np.asarray(y,float)-np.asarray(q,float)
    s=float(e.sum()); ss=float(np.sum(e*e))
    return s*s-ss, 9.0*ss

def sim_terms(w,q):
    e=w.astype(float)-q[None,:]
    s=e.sum(axis=1); ss=np.sum(e*e,axis=1)
    return s*s-ss, 9.0*ss

def finish(obs_num,obs_den,null_num,null_den,clusters):
    if obs_den<=0 or np.any(null_den<=0):
        raise RuntimeError("nonpositive denominator")
    obs=float(obs_num/obs_den)
    null=null_num/null_den
    lo,hi=np.quantile(null,[.025,.975])
    p=float((1+np.sum(null>=obs))/(B+1))
    return {
        "clusters":int(clusters),
        "rho_bounded":obs,
        "null_mean":float(np.mean(null)),
        "null_ci95":[float(lo),float(hi)],
        "plus_one_upper_tail_p":p,
        "positive_dependence_supported":bool(obs>hi and p<0.05)
    }

def main():
    raw,runs,psub,dsub,hsub,pools,sampled,ss=flex.prepare_subset()
    mid=rain.build_midpoints(raw,runs)
    weather,weather_sha=rain.antecedent_amounts(mid)

    obs_map=sameobs.observer_map(raw)
    keep=[]
    for p in psub.itertuples(index=False):
        w=str(p.wet_RunID); d=str(p.dry_RunID)
        ow=obs_map.get(w,""); od=obs_map.get(d,"")
        keep.append(w in weather and d in weather and ow!="" and ow==od)
    keep=np.asarray(keep,bool)
    idx=np.flatnonzero(keep)
    pw=psub.iloc[idx].copy().reset_index(drop=True)
    dw=[dsub[int(i)] for i in idx]
    hw=[hsub[int(i)] for i in idx]

    if len(pw)<1500:
        raise RuntimeError(f"same-observer weather/history subset unexpectedly small: {len(pw)}")

    runs_weather=runs[runs["RunID"].astype(str).isin(weather)].copy().reset_index(drop=True)
    runs_weather["rain72_mm"]=[weather[str(r)]["rain72_mm"] for r in runs_weather["RunID"].astype(str)]
    runs_weather["rain72_log"]=np.log1p(runs_weather["rain72_mm"].astype(float))

    all_species=sorted({sp for spp in pools.values() for sp in spp})
    pred_A,audit_A,fold_A=rain.fit_predict_amount_environment(runs_weather,sampled,ss,all_species,"A")
    pred_B,audit_B,fold_B=rain.fit_predict_amount_environment(runs_weather,sampled,ss,all_species,"B")
    pred_by_train={"A":pred_A,"B":pred_B}

    rng=np.random.default_rng(SEED)
    stats={
      "all":{"on":0.0,"od":0.0,"nn":np.zeros(B),"nd":np.zeros(B),"clusters":0},
      "dry_route_silent":{"on":0.0,"od":0.0,"nn":np.zeros(B),"nd":np.zeros(B),"clusters":0}
    }

    for p,dct,p_hist in zip(pw.itertuples(index=False),dw,hw):
        test_fold=joint.fold_for_route(str(p.route_cluster))
        train_fold="B" if test_fold=="A" else "A"
        pred=pred_by_train[train_fold]
        wet_id=str(p.wet_RunID); dry_id=str(p.dry_RunID)
        delta=np.asarray([
            pred[wet_id].get(sp,0.0)-pred[dry_id].get(sp,0.0)
            for sp in dct["species"]
        ],float)
        dry=dct["dry"].astype(float)
        p_anchor=(1.0-ANCHOR)*p_hist+ANCHOR*dry
        p_anchor=np.clip(p_anchor,EPS,1-EPS)
        pre=uniform.expit(uniform.logit(p_anchor)+delta[:,None])
        q=uniform.solve_shift(pre,dct["wet_k"])
        q=np.clip(q,EPS,1-EPS)
        y=dct["wet"].astype(float)

        for i in range(q.shape[0]):
            labels=["all"]
            if dry[i].sum()==0:
                labels.append("dry_route_silent")
            on,od=terms(y[i],q[i])
            w=rng.random((B,10))<q[i][None,:]
            nn,nd=sim_terms(w,q[i])
            for lab in labels:
                s=stats[lab]
                s["on"]+=on; s["od"]+=od
                s["nn"]+=nn; s["nd"]+=nd
                s["clusters"]+=1

    out={
      "analysis":"naamp_bounded_route_night_same_observer_sensitivity_v0_1",
      "contract":"exploration/NAAMP_BOUNDED_ROUTE_NIGHT_SAME_OBSERVER_CONTRACT_V0_1.json",
      "status":"posthoc_detection_sensitivity_triggered",
      "coverage":{
        "pairs":int(len(pw)),
        "routes":int(pw.route_cluster.nunique()),
        "states":int(pw.State.nunique())
      },
      "results":{
        lab:finish(s["on"],s["od"],s["nn"],s["nd"],s["clusters"])
        for lab,s in stats.items()
      },
      "weather_provenance":{"era5_antecedent_amount_sha256":weather_sha},
      "interpretation_boundary":{
        "observer_turnover_required":False,
        "within_observer_error_excluded":False,
        "independent_confirmation":False,
        "unique_lower_level_mechanism_identified":False
      }
    }
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
