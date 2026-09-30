#!/usr/bin/env python3
from __future__ import annotations
import importlib.util, json, math
from collections import defaultdict
from functools import lru_cache
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm

ROOT=Path(__file__).resolve().parents[1]
NAAMP=ROOT/"scripts"/"naamp"
OUT=ROOT/"exploration"/"NAAMP_EXACT_CONDITIONAL_HIGHER_ORDER_DIRECTIONAL_RECEIPT_V0_1.json"
Q=1.959963984540054

def loadmod(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    mod=importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(mod)
    return mod

base=loadmod("base",NAAMP/"run_naamp_ecological_pulse.py")
uniform=loadmod("uniform",NAAMP/"run_naamp_uniform_activation_null.py")

@lru_cache(maxsize=None)
def conditional_moments(n:int,k_total:int):
    if n<=0:
        return (0.0,0.0)
    if k_total<n or k_total>10*n:
        raise ValueError((n,k_total))
    # Dynamic program over exact binary configurations. Each row has
    # k=1..10 occupied sites with multiplicity C(10,k).
    count=[0]*(10*n+1)
    hsum=[0]*(10*n+1)
    h2sum=[0]*(10*n+1)
    count[0]=1
    max_t=0
    for _ in range(n):
        nc=[0]*(10*n+1); nh=[0]*(10*n+1); nh2=[0]*(10*n+1)
        for t in range(max_t+1):
            if count[t]==0:
                continue
            for kk in range(1,11):
                w=math.comb(10,kk)
                h=math.comb(kk-1,2)
                tt=t+kk
                nc[tt]+=count[t]*w
                nh[tt]+=(hsum[t]+count[t]*h)*w
                nh2[tt]+=(h2sum[t]+2*h*hsum[t]+count[t]*h*h)*w
        count,hsum,h2sum=nc,nh,nh2
        max_t+=10
    den=count[k_total]
    if den==0:
        raise RuntimeError(f"zero conditional count n={n} k={k_total}")
    mean=hsum[k_total]/den
    second=h2sum[k_total]/den
    var=max(0.0,second-mean*mean)
    return float(mean),float(math.sqrt(var))

def direction_metrics(target,reference):
    ref_route=reference.any(axis=1)
    target_route=target.any(axis=1)
    new=(~ref_route)&target_route
    if not np.any(new):
        return {"N":0,"K":0,"H":0.0,"expected_H":0.0,"sd_H":0.0,"raw_excess":0.0,"z_excess":0.0}
    k=target[new].sum(axis=1).astype(int)
    n=int(len(k)); kt=int(k.sum())
    H=float(sum(math.comb(int(x)-1,2) for x in k))
    mean,sd=conditional_moments(n,kt)
    raw=H-mean
    z=raw/sd if sd>0 else 0.0
    return {"N":n,"K":kt,"H":H,"expected_H":mean,"sd_H":sd,"raw_excess":raw,"z_excess":z}

def observer_map(raw):
    return {(r.get("RunID") or "").strip():(r.get("ObserverTrackingID") or "").strip() for r in raw["Runs.csv"] if (r.get("RunID") or "").strip()}

def site_map(raw):
    vals=defaultdict(set)
    for s in raw["Stops.csv"]:
        rid=(s.get("RunID") or "").strip()
        st=(s.get("StopNumber") or "").strip()
        sid=(s.get("SiteID") or "").strip()
        if rid and st and sid and (s.get("SkippedStop") or "").strip()=="0":
            vals[(rid,st)].add(sid)
    bad={k:v for k,v in vals.items() if len(v)>1}
    if bad:
        raise RuntimeError(f"multiple SiteID values: {list(bad)[:5]}")
    return {k:next(iter(v)) for k,v in vals.items()}

def joint_robust_mask(pairs,pair_data,raw):
    obs=observer_map(raw); site=site_map(raw)
    keep=[]
    for p,d in zip(pairs.itertuples(index=False),pair_data):
        wet=str(p.wet_RunID); dry=str(p.dry_RunID)
        same_obs=bool(obs.get(wet)) and obs.get(wet)==obs.get(dry)
        stops=d["stops"]
        same_site=len(stops)==10 and all(site.get((wet,st)) is not None and site.get((wet,st))==site.get((dry,st)) for st in stops)
        keep.append(bool(same_obs and same_site))
    return np.asarray(keep,bool)

def fit_directional(rows,response,mask=None):
    d=pd.DataFrame(rows)
    if mask is not None:
        ids=set(np.flatnonzero(mask).tolist())
        d=d[d["pair_id"].isin(ids)].copy()
    # Exact pair demeaning.
    d["x_dm"]=d["target_rain_advantage"]-d.groupby("pair_id")["target_rain_advantage"].transform("mean")
    d["y_dm"]=d[response]-d.groupby("pair_id")[response].transform("mean")
    model=sm.OLS(d["y_dm"].to_numpy(float),d[["x_dm"]].to_numpy(float)).fit(
        cov_type="cluster",cov_kwds={"groups":d["route_cluster"].astype(str).to_numpy()}
    )
    b=float(model.params[0]); se=float(model.bse[0])
    return {
        "beta":b,"se":se,"ci95":[b-Q*se,b+Q*se],"p":float(model.pvalues[0]),
        "n_pairs":int(d["pair_id"].nunique()),"n_routes":int(d["route_cluster"].nunique())
    }

def main():
    raw=base.load()
    uniform.base.load=lambda:raw
    pairs,pair_data,pools,dry_ids,sampled,ss,r,den,obs0,beta_mask,r_beta,den_beta,obs_sor=uniform.prepare()
    pairs=pairs.copy().reset_index(drop=True)
    rows=[]
    audit={"wet":{"N":0,"K":0,"H":0.0},"dry":{"N":0,"K":0,"H":0.0}}
    for i,(p,d) in enumerate(zip(pairs.itertuples(index=False),pair_data)):
        wet=direction_metrics(d["wet"],d["dry"])
        dry=direction_metrics(d["dry"],d["wet"])
        for label,m,sign in [("wet",wet,1.0),("dry",dry,-1.0)]:
            rows.append({
                "pair_id":i,"route_cluster":str(p.route_cluster),
                "direction":label,
                "target_rain_advantage":sign*float(p.rain_contrast),
                **m
            })
            audit[label]["N"]+=m["N"]; audit[label]["K"]+=m["K"]; audit[label]["H"]+=m["H"]
    mask=joint_robust_mask(pairs,pair_data,raw)
    full_raw=fit_directional(rows,"raw_excess")
    full_z=fit_directional(rows,"z_excess")
    robust_raw=fit_directional(rows,"raw_excess",mask)
    robust_z=fit_directional(rows,"z_excess",mask)
    primary=bool(full_raw["ci95"][0]>0)
    strong=bool(primary and full_z["ci95"][0]>0 and robust_raw["ci95"][0]>0)
    out={
      "analysis":"naamp_exact_conditional_higher_order_directional_v0_1",
      "coverage":{"all_pairs":int(len(pairs)),"all_routes":int(pairs.route_cluster.nunique()),"joint_robust_pairs":int(mask.sum()),"joint_robust_routes":int(pairs.loc[mask,"route_cluster"].nunique())},
      "directional_totals":audit,
      "full_sample":{"raw_excess":full_raw,"z_excess":full_z},
      "joint_same_observer_same_site":{"raw_excess":robust_raw,"z_excess":robust_z},
      "classification":{"primary_support":primary,"strong_support":strong},
      "interpretation_boundary":{"exact_first_order_conditioning":True,"regression_extrapolation_used":False,"literal_synchrony_inferred":False,"causal_rainfall_claim":False}
    }
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
