#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import itertools
import json
from collections import defaultdict
from pathlib import Path

import numpy as np
from scipy.special import logsumexp

ROOT=Path(__file__).resolve().parents[1]
EXP=ROOT/"exploration"
LAND=ROOT/"landscape"
OUT=LAND/"NAAMP_ROUTE_TOPOLOGY_GEOMETRY_RECEIPT_V0_1.json"

B=2000
SEED=2840241
BOOT_B=2000
BOOT_SEED=2840242
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

def topology_metrics(active_idx):
    x=np.sort(np.asarray(active_idx,dtype=int))
    k=len(x)
    if k==0:
        raise ValueError("empty active set")
    if k==1:
        return {"span":0.0,"holes":0.0,"components":1.0,"mean_pairwise_lag":0.0}
    dif=np.diff(x)
    span=float(x[-1]-x[0])
    holes=float(span+1-k)
    components=float(1+np.sum(dif>1))
    pairlags=[]
    for i in range(k):
        for j in range(i+1,k):
            pairlags.append(int(x[j]-x[i]))
    return {
        "span":span,
        "holes":holes,
        "components":components,
        "mean_pairwise_lag":float(np.mean(pairlags))
    }

def conditional_geometry(q,k):
    q=np.clip(np.asarray(q,float),EPS,1-EPS)
    combos=np.asarray(list(itertools.combinations(range(10),int(k))),dtype=int)
    if len(combos)==0:
        raise RuntimeError(f"no subsets for k={k}")
    logodds=np.log(q)-np.log1p(-q)
    logw=logodds[combos].sum(axis=1)
    probs=np.exp(logw-logsumexp(logw))
    names=["span","holes","components","mean_pairwise_lag"]
    vals={name:np.zeros(len(combos),float) for name in names}
    for i,c in enumerate(combos):
        m=topology_metrics(c)
        for name in names:
            vals[name][i]=m[name]
    expected={name:float(probs@vals[name]) for name in names}
    return combos,probs,vals,expected

def null_summary(obs,sim,tail="upper"):
    sim=np.asarray(sim,float)
    lo,hi=np.quantile(sim,[.025,.975])
    if tail=="upper":
        p=float((1+np.sum(sim>=obs))/(len(sim)+1))
    elif tail=="lower":
        p=float((1+np.sum(sim<=obs))/(len(sim)+1))
    else:
        p=float(min(1.0,2*min((1+np.sum(sim>=obs))/(len(sim)+1),(1+np.sum(sim<=obs))/(len(sim)+1))))
    return {
        "observed_mean_excess":float(obs),
        "null_mean":float(np.mean(sim)),
        "null_ci95":[float(lo),float(hi)],
        "plus_one_p":p,
        "tail":tail
    }

def route_bootstrap(route_sums,route_counts):
    routes=sorted(route_sums)
    sums=np.asarray([route_sums[r] for r in routes],float)
    counts=np.asarray([route_counts[r] for r in routes],float)
    rng=np.random.default_rng(BOOT_SEED)
    vals=np.zeros(BOOT_B,float)
    n=len(routes)
    for b in range(BOOT_B):
        idx=rng.integers(0,n,size=n)
        vals[b]=float(sums[idx].sum()/counts[idx].sum())
    lo,hi=np.quantile(vals,[.025,.975])
    return {
        "routes":int(n),
        "replicates":BOOT_B,
        "seed":BOOT_SEED,
        "ci95":[float(lo),float(hi)]
    }

def main():
    raw,runs,psub,dsub,hsub,pools,sampled,ss=flex.prepare_subset()
    mid=rain.build_midpoints(raw,runs)
    weather,weather_sha=rain.antecedent_amounts(mid)

    keep=np.asarray([
        str(p.wet_RunID) in weather and str(p.dry_RunID) in weather
        for p in psub.itertuples(index=False)
    ],bool)
    idx=np.flatnonzero(keep)
    pw=psub.iloc[idx].copy().reset_index(drop=True)
    dw=[dsub[int(i)] for i in idx]
    hw=[hsub[int(i)] for i in idx]
    if len(pw)!=2835 or pw.route_cluster.nunique()!=428:
        raise RuntimeError(f"weather/history coverage drift pairs={len(pw)} routes={pw.route_cluster.nunique()}")

    runs_weather=runs[runs["RunID"].astype(str).isin(weather)].copy().reset_index(drop=True)
    runs_weather["rain72_mm"]=[weather[str(r)]["rain72_mm"] for r in runs_weather["RunID"].astype(str)]
    runs_weather["rain72_log"]=np.log1p(runs_weather["rain72_mm"].astype(float))
    all_species=sorted({sp for spp in pools.values() for sp in spp})

    pred_A,_,_=rain.fit_predict_amount_environment(runs_weather,sampled,ss,all_species,"A")
    pred_B,_,_=rain.fit_predict_amount_environment(runs_weather,sampled,ss,all_species,"B")
    pred_by_train={"A":pred_A,"B":pred_B}

    rng=np.random.default_rng(SEED)
    names=["span","holes","components","mean_pairwise_lag"]
    deep_obs_sum={n:0.0 for n in names}
    deep_sim_sum={n:np.zeros(B,float) for n in names}
    n_deep=0
    n_all=0
    route_hole_sum=defaultdict(float)
    route_hole_n=defaultdict(int)
    by_k=defaultdict(lambda:{
        "n":0,
        **{f"obs_{n}_sum":0.0 for n in names},
        **{f"exp_{n}_sum":0.0 for n in names}
    })

    for p,dct,p_hist in zip(pw.itertuples(index=False),dw,hw):
        test_fold=joint.fold_for_route(str(p.route_cluster))
        train_fold="B" if test_fold=="A" else "A"
        pred=pred_by_train[train_fold]
        wet_id=str(p.wet_RunID); dry_id=str(p.dry_RunID)
        delta=np.asarray([
            pred[wet_id].get(sp,0.0)-pred[dry_id].get(sp,0.0)
            for sp in dct["species"]
        ],float)

        dry=dct["dry"].astype(bool)
        wet=dct["wet"].astype(bool)
        p_anchor=(1.0-ANCHOR)*p_hist+ANCHOR*dry.astype(float)
        p_anchor=np.clip(p_anchor,EPS,1-EPS)
        pre=uniform.expit(uniform.logit(p_anchor)+delta[:,None])
        q=uniform.solve_shift(pre,dct["wet_k"])
        q=np.clip(q,EPS,1-EPS)

        for si,sp in enumerate(dct["species"]):
            if dry[si].any():
                continue
            active=np.flatnonzero(wet[si])
            k=int(len(active))
            if k<1:
                continue
            n_all+=1
            obs=topology_metrics(active)
            combos,probs,vals,expected=conditional_geometry(q[si],k)

            rec=by_k[k]
            rec["n"]+=1
            for name in names:
                rec[f"obs_{name}_sum"]+=obs[name]
                rec[f"exp_{name}_sum"]+=expected[name]

            if k<4:
                continue

            n_deep+=1
            draws=rng.choice(len(probs),size=B,replace=True,p=probs)
            for name in names:
                excess=float(obs[name]-expected[name])
                deep_obs_sum[name]+=excess
                deep_sim_sum[name]+=vals[name][draws]-expected[name]
            hole_ex=float(obs["holes"]-expected["holes"])
            route=str(p.route_cluster)
            route_hole_sum[route]+=hole_ex
            route_hole_n[route]+=1

    if n_deep<1:
        raise RuntimeError("no deep clusters")

    primary_obs=float(deep_obs_sum["holes"]/n_deep)
    primary_sim=deep_sim_sum["holes"]/n_deep
    primary=null_summary(primary_obs,primary_sim,"upper")
    boot=route_bootstrap(route_hole_sum,route_hole_n)
    primary["route_bootstrap"]=boot
    primary["supported"]=bool(
        primary_obs>primary["null_ci95"][1]
        and primary["plus_one_p"]<0.05
        and boot["ci95"][0]>0
    )

    secondary={}
    for name in ["span","components","mean_pairwise_lag"]:
        obs=float(deep_obs_sum[name]/n_deep)
        sim=deep_sim_sum[name]/n_deep
        secondary[name]=null_summary(obs,sim,"two-sided")

    exact_k={}
    for k in sorted(by_k):
        rec=by_k[k]
        n=rec["n"]
        row={"n_clusters":int(n)}
        for name in names:
            row[f"observed_mean_{name}"]=float(rec[f"obs_{name}_sum"]/n)
            row[f"q_expected_mean_{name}"]=float(rec[f"exp_{name}_sum"]/n)
            row[f"mean_excess_{name}"]=float((rec[f"obs_{name}_sum"]-rec[f"exp_{name}_sum"])/n)
        exact_k[str(k)]=row

    out={
        "analysis":"naamp_route_topology_geometry_v0_1",
        "contract":"landscape/NAAMP_ROUTE_TOPOLOGY_GEOMETRY_CONTRACT_V0_1.json",
        "status":"post_rc6_exploratory_topology_geometry_fixed_before_metric_readback",
        "coverage":{
            "pairs":int(len(pw)),
            "routes":int(pw.route_cluster.nunique()),
            "all_dry_route_silent_wet_active_clusters":int(n_all),
            "deep_k4plus_clusters":int(n_deep),
            "deep_routes":int(len(route_hole_sum))
        },
        "primary_deep_holes_excess":primary,
        "secondary_deep_geometry_excess":secondary,
        "exact_k_descriptives":exact_k,
        "metric_definitions":{
            "span":"max active StopNumber - min active StopNumber",
            "holes":"span + 1 - k",
            "components":"number of contiguous active StopNumber runs",
            "mean_pairwise_lag":"mean absolute StopNumber difference over active-stop pairs"
        },
        "null":{
            "exact_observed_k_fixed":True,
            "fixed_q":True,
            "conditional_independent_bernoulli_subset_weights":True,
            "replicates":B,
            "seed":SEED
        },
        "weather_provenance":{"era5_antecedent_amount_sha256":weather_sha},
        "interpretation_boundary":{
            "stop_number_is_exact_geographic_distance":False,
            "literal_synchrony":False,
            "movement_identified":False,
            "hydrological_connectivity_identified":False,
            "independent_confirmation":False,
            "changes_rc6":False
        }
    }
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
