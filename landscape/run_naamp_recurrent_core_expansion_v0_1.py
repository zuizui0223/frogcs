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
OUT=LAND/"NAAMP_RECURRENT_CORE_EXPANSION_RECEIPT_V0_1.json"

B=2000
SEED=2840243
BOOT_B=2000
BOOT_SEED=2840244
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
mem=flex.mem
local=loadmod("local_targeting",EXP/"run_naamp_local_chorus_memory_targeting.py")

def core_metrics(combo,strong):
    combo=np.sort(np.asarray(combo,dtype=int))
    strong=np.asarray(strong,bool)
    astrong=combo[strong[combo]]
    anon=combo[~strong[combo]]
    if len(astrong)<1 or len(anon)<1:
        raise ValueError("core metric requires active strong and active non-strong sites")
    d=np.asarray([np.min(np.abs(astrong-x)) for x in anon],float)
    return {
        "core_distance":float(np.mean(d)),
        "adjacent_to_core_fraction":float(np.mean(d==1))
    }

def conditional_distribution(q,k,h,strong):
    q=np.clip(np.asarray(q,float),EPS,1-EPS)
    strong=np.asarray(strong,bool)
    combos=[]
    metrics={"core_distance":[],"adjacent_to_core_fraction":[]}
    logw=[]
    lod=np.log(q)-np.log1p(-q)
    for c in itertools.combinations(range(10),int(k)):
        arr=np.asarray(c,dtype=int)
        if int(strong[arr].sum())!=int(h):
            continue
        m=core_metrics(arr,strong)
        combos.append(arr)
        logw.append(float(lod[arr].sum()))
        for name in metrics:
            metrics[name].append(m[name])
    if not combos:
        raise RuntimeError(f"no exact-k/exact-h subsets for k={k}, h={h}")
    logw=np.asarray(logw,float)
    probs=np.exp(logw-logsumexp(logw))
    vals={k:np.asarray(v,float) for k,v in metrics.items()}
    expected={k:float(probs@vals[k]) for k in vals}
    return np.asarray(combos,dtype=int),probs,vals,expected

def null_summary(obs,sim,tail):
    sim=np.asarray(sim,float)
    lo,hi=np.quantile(sim,[.025,.975])
    if tail=="lower":
        p=float((1+np.sum(sim<=obs))/(len(sim)+1))
    elif tail=="upper":
        p=float((1+np.sum(sim>=obs))/(len(sim)+1))
    else:
        p=float(min(1.0,2*min((1+np.sum(sim<=obs))/(len(sim)+1),(1+np.sum(sim>=obs))/(len(sim)+1))))
    return {
        "observed_mean_excess":float(obs),
        "null_mean":float(np.mean(sim)),
        "null_ci95":[float(lo),float(hi)],
        "plus_one_p":p,
        "tail":tail
    }

def route_bootstrap(route_sums,route_counts,seed):
    routes=sorted(route_sums)
    sums=np.asarray([route_sums[r] for r in routes],float)
    counts=np.asarray([route_counts[r] for r in routes],float)
    rng=np.random.default_rng(seed)
    vals=np.zeros(BOOT_B,float)
    n=len(routes)
    for b in range(BOOT_B):
        idx=rng.integers(0,n,size=n)
        vals[b]=float(sums[idx].sum()/counts[idx].sum())
    lo,hi=np.quantile(vals,[.025,.975])
    return {"routes":int(n),"replicates":BOOT_B,"seed":seed,"ci95":[float(lo),float(hi)]}

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
        raise RuntimeError("weather/history coverage drift")

    eligible=set(runs.RunID.astype(str))
    site=mem.site_map(raw,eligible)
    meta,by_stratum,run_sites,run_site_species=mem.build_history_index(runs,sampled,ss,site)
    ci=local.ci_map(raw,eligible,sampled)

    runs_weather=runs[runs["RunID"].astype(str).isin(weather)].copy().reset_index(drop=True)
    runs_weather["rain72_mm"]=[weather[str(r)]["rain72_mm"] for r in runs_weather["RunID"].astype(str)]
    runs_weather["rain72_log"]=np.log1p(runs_weather["rain72_mm"].astype(float))
    all_species=sorted({sp for spp in pools.values() for sp in spp})
    pred_A,_,_=rain.fit_predict_amount_environment(runs_weather,sampled,ss,all_species,"A")
    pred_B,_,_=rain.fit_predict_amount_environment(runs_weather,sampled,ss,all_species,"B")
    pred_by_train={"A":pred_A,"B":pred_B}

    rng=np.random.default_rng(SEED)
    names=["core_distance","adjacent_to_core_fraction"]
    obs_sum={n:0.0 for n in names}
    sim_sum={n:np.zeros(B,float) for n in names}
    route_sum={n:defaultdict(float) for n in names}
    route_n={n:defaultdict(int) for n in names}
    by_k=defaultdict(lambda:{"n":0,"core_excess_sum":0.0,"adj_excess_sum":0.0})
    n_clusters=0
    species=set()
    h_counts=defaultdict(int)

    for p,dct,p_hist in zip(pw.itertuples(index=False),dw,hw):
        ids=mem.focal_siteids(p,dct,site)
        if ids is None:
            continue
        prior=mem.eligible_prior_runs(p,dct,ids,meta,by_stratum,run_sites)
        if not prior:
            continue

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

        strong=np.zeros_like(dry,dtype=bool)
        for t,sid in enumerate(ids):
            for rid in prior:
                for st in sampled.get(rid,set()):
                    if site.get((rid,st))!=sid:
                        continue
                    cmap=ci.get((rid,st),{})
                    for si,sp in enumerate(dct["species"]):
                        if int(cmap.get(sp,0))>=2:
                            strong[si,t]=True

        for si,sp in enumerate(dct["species"]):
            if dry[si].any():
                continue
            active=np.flatnonzero(wet[si])
            k=int(len(active))
            if k<4:
                continue
            m=int(strong[si].sum())
            if m<1 or m>=10:
                continue
            h=int(strong[si,active].sum())
            if h<1 or k-h<1:
                continue

            obs=core_metrics(active,strong[si])
            combos,probs,vals,expected=conditional_distribution(q[si],k,h,strong[si])
            draws=rng.choice(len(probs),size=B,replace=True,p=probs)
            route=str(p.route_cluster)
            for name in names:
                ex=float(obs[name]-expected[name])
                obs_sum[name]+=ex
                sim_sum[name]+=vals[name][draws]-expected[name]
                route_sum[name][route]+=ex
                route_n[name][route]+=1

            n_clusters+=1
            species.add(str(sp))
            h_counts[str(h)]+=1
            by_k[k]["n"]+=1
            by_k[k]["core_excess_sum"]+=obs["core_distance"]-expected["core_distance"]
            by_k[k]["adj_excess_sum"]+=obs["adjacent_to_core_fraction"]-expected["adjacent_to_core_fraction"]

    if n_clusters<1:
        raise RuntimeError("no eligible recurrent-core clusters")

    core_obs=float(obs_sum["core_distance"]/n_clusters)
    core_sim=sim_sum["core_distance"]/n_clusters
    core=null_summary(core_obs,core_sim,"lower")
    core_boot=route_bootstrap(route_sum["core_distance"],route_n["core_distance"],BOOT_SEED)
    core["route_bootstrap"]=core_boot
    core["supported"]=bool(
        core_obs<core["null_ci95"][0]
        and core["plus_one_p"]<0.05
        and core_boot["ci95"][1]<0
    )

    adj_obs=float(obs_sum["adjacent_to_core_fraction"]/n_clusters)
    adj_sim=sim_sum["adjacent_to_core_fraction"]/n_clusters
    adj=null_summary(adj_obs,adj_sim,"upper")
    adj["route_bootstrap"]=route_bootstrap(route_sum["adjacent_to_core_fraction"],route_n["adjacent_to_core_fraction"],BOOT_SEED+1)

    out={
        "analysis":"naamp_recurrent_core_expansion_v0_1",
        "contract":"landscape/NAAMP_RECURRENT_CORE_EXPANSION_CONTRACT_V0_1.json",
        "status":"stage_a2_generated_after_stage_a1_fixed_before_core_distance_readback",
        "coverage":{
            "pairs":int(len(pw)),
            "routes":int(pw.route_cluster.nunique()),
            "eligible_deep_core_clusters":int(n_clusters),
            "eligible_routes":int(len(route_sum["core_distance"])),
            "species":int(len(species)),
            "active_prior_strong_count_h":dict(sorted(h_counts.items(),key=lambda z:int(z[0])))
        },
        "primary_core_distance_excess":core,
        "secondary_adjacent_to_core_excess":adj,
        "by_exact_k":{
            str(k):{
                "n_clusters":int(v["n"]),
                "mean_core_distance_excess":float(v["core_excess_sum"]/v["n"]),
                "mean_adjacent_fraction_excess":float(v["adj_excess_sum"]/v["n"])
            } for k,v in sorted(by_k.items())
        },
        "conditioning":{
            "exact_k":True,
            "exact_h_active_prior_strong":True,
            "fixed_q":True,
            "fixed_prior_strong_mask":True,
            "subset_weight":"product of fixed q/(1-q) odds",
            "replicates":B,
            "seed":SEED
        },
        "weather_provenance":{"era5_antecedent_amount_sha256":weather_sha},
        "interpretation_boundary":{
            "generated_after_stage_a1":True,
            "post_rc6":True,
            "independent_confirmation":False,
            "movement_or_propagation_identified":False,
            "individual_fidelity_identified":False,
            "stop_number_is_exact_distance":False,
            "changes_rc6":False
        }
    }
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
