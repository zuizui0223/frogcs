#!/usr/bin/env python3
from __future__ import annotations
import importlib.util,json
from pathlib import Path
import numpy as np,pandas as pd,statsmodels.formula.api as smf

ROOT=Path(__file__).resolve().parents[1]
NAAMP=ROOT/"scripts"/"naamp"
OUT=ROOT/"exploration"/"NAAMP_HIGHER_ORDER_GEOGRAPHIC_GENERALITY_RECEIPT_V0_1.json"
Q=1.959963984540054

def loadmod(name,path):
    s=importlib.util.spec_from_file_location(name,path); m=importlib.util.module_from_spec(s)
    assert s.loader; s.loader.exec_module(m); return m
uniform=loadmod("uniform",NAAMP/"run_naamp_uniform_activation_null.py")

def endpoint(w,d):
    d_route=d.any(axis=1)
    route_new=(~d_route)&w.any(axis=1)
    if not np.any(route_new): return 0.0
    k=w[route_new].sum(axis=1).astype(float)
    e=np.maximum(k-1.,0.)
    return float(np.sum(e*np.maximum(e-1.,0.)/2.))

def fit(df,include_state=True):
    rhs="rain_contrast + temp_difference + doy_difference + year_gap + C(RunNumber)"
    if include_state: rhs += " + C(State)"
    m=smf.ols("higher_order_mass ~ "+rhs,data=df).fit(cov_type="cluster",cov_kwds={"groups":df["route_cluster"]})
    b=float(m.params["rain_contrast"]); se=float(m.bse["rain_contrast"])
    return {"beta":b,"se":se,"ci95":[b-Q*se,b+Q*se],"p":float(m.pvalues["rain_contrast"]),"n_pairs":int(len(df)),"n_routes":int(df.route_cluster.nunique())}

def main():
    pairs,pair_data,pools,dry_ids,sampled,ss,r,den,obs0,beta_mask,r_beta,den_beta,obs_sor=uniform.prepare()
    d=pairs.copy().reset_index(drop=True)
    d["higher_order_mass"]=[endpoint(x["wet"],x["dry"]) for x in pair_data]
    states=sorted(d.State.astype(str).unique())
    loo={}
    for st in states:
        sub=d[d.State.astype(str)!=st].copy()
        loo[st]=fit(sub,True)
    passed=all(v["beta"]>0 for v in loo.values())
    strong=all(v["ci95"][0]>0 for v in loo.values())
    estimable={}
    for st in states:
        sub=d[d.State.astype(str)==st].copy()
        if sub.route_cluster.nunique()<10 or len(sub)<30:
            estimable[st]={"estimable":False,"n_pairs":int(len(sub)),"n_routes":int(sub.route_cluster.nunique())}
            continue
        try:
            x=fit(sub,False); x["estimable"]=True; estimable[st]=x
        except Exception:
            estimable[st]={"estimable":False,"n_pairs":int(len(sub)),"n_routes":int(sub.route_cluster.nunique())}
    est=[v for v in estimable.values() if v.get("estimable")]
    out={
      "analysis":"naamp_higher_order_geographic_generality_v0_1",
      "n_pairs":int(len(d)),"n_routes":int(d.route_cluster.nunique()),"n_states":int(len(states)),
      "full_model":fit(d,True),
      "leave_one_state_out":loo,
      "loo_beta_range":[float(min(v["beta"] for v in loo.values())),float(max(v["beta"] for v in loo.values()))],
      "loo_ci_lower_min":float(min(v["ci95"][0] for v in loo.values())),
      "classification":{"pass":passed,"strong_pass":strong},
      "state_specific":{
        "fits":estimable,
        "n_estimable":int(len(est)),
        "positive_point_estimates":int(sum(v["beta"]>0 for v in est)),
        "positive_ci":int(sum(v["ci95"][0]>0 for v in est))
      }
    }
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n"); print(json.dumps(out,indent=2,sort_keys=True))
if __name__=="__main__": main()
