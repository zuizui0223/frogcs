#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import itertools
import json
from pathlib import Path

import numpy as np
from scipy.special import logsumexp

ROOT=Path(__file__).resolve().parents[1]
EXP=ROOT/"exploration"
LAND=ROOT/"landscape"
OUT=LAND/"NAAMP_ROUTE_TOPOLOGY_GEOMETRY_RECEIPT_V0_1.json"

B=2000
SEED=2840301
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

def topology_metrics(combo):
    pos=np.asarray(combo,dtype=int)+1
    if len(pos)<2:
        raise ValueError("topology metrics require k>=2")
    diffs=[]
    for i in range(len(pos)):
        for j in range(i+1,len(pos)):
            diffs.append(abs(int(pos[j])-int(pos[i])))
    diffs=np.asarray(diffs,float)
    span=float(pos.max()-pos.min())
    mean_pairwise=float(diffs.mean())
    components=float(1+np.sum(np.diff(pos)>1))
    return np.asarray([mean_pairwise,span,components],float)

def exact_subset_distribution(q,k):
    q=np.clip(np.asarray(q,float),EPS,1-EPS)
    combos=np.asarray(list(itertools.combinations(range(10),int(k))),dtype=int)
    if len(combos)==0:
        raise RuntimeError(f"no subsets for k={k}")
    logodds=np.log(q)-np.log1p(-q)
    logw=logodds[combos].sum(axis=1)
    logw=logw-logsumexp(logw)
    probs=np.exp(logw)
    vals=np.asarray([topology_metrics(c) for c in combos],float)
    expected=probs@vals
    return combos,probs,vals,expected

def test_primary(obs,sim):
    sim=np.asarray(sim,float)
    lo,hi=np.quantile(sim,[.025,.975])
    p=float((1+np.sum(sim>=obs))/(len(sim)+1))
    return {
        "observed_mean_excess":float(obs),
        "null_mean":float(np.mean(sim)),
        "null_ci95":[float(lo),float(hi)],
        "plus_one_upper_tail_p":p,
        "positive_dispersion_supported":bool(obs>hi and p<0.05)
    }

def summarize_metric(obs_sum,sim_sum,n):
    obs=float(obs_sum/n)
    sim=np.asarray(sim_sum,float)/n
    lo,hi=np.quantile(sim,[.025,.975])
    return {
        "clusters":int(n),
        "observed_mean_excess":obs,
        "null_mean":float(np.mean(sim)),
        "null_ci95":[float(lo),float(hi)]
    }

def main():
    contract=json.loads((LAND/"NAAMP_ROUTE_TOPOLOGY_GEOMETRY_CONTRACT_V0_1.json").read_text())
    if contract.get("null",{}).get("seed")!=SEED or contract.get("null",{}).get("Monte_Carlo_replicates")!=B:
        raise RuntimeError("contract/implementation drift")

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
    obs_sum=np.zeros(3,float)
    sim_sum=np.zeros((B,3),float)
    obs_shallow=np.zeros(3,float)
    obs_deep=np.zeros(3,float)
    sim_shallow=np.zeros((B,3),float)
    sim_deep=np.zeros((B,3),float)
    n_all=n_shallow=n_deep=0
    species=set()
    k_counts={str(k):0 for k in range(2,11)}

    raw_metric_sum=np.zeros(3,float)
    expected_metric_sum=np.zeros(3,float)

    for p,dct,p_hist in zip(pw.itertuples(index=False),dw,hw):
        if len(dct.get("stops",[]))!=10:
            raise RuntimeError("aligned route lost 10-stop topology")
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
            if k<2:
                continue

            combos,probs,vals,expected=exact_subset_distribution(q[si],k)
            observed=topology_metrics(active)
            excess=observed-expected
            draws=rng.choice(len(probs),size=B,replace=True,p=probs)
            sim_excess=vals[draws]-expected[None,:]

            n_all+=1
            k_counts[str(k)]+=1
            species.add(str(sp))
            obs_sum+=excess
            sim_sum+=sim_excess
            raw_metric_sum+=observed
            expected_metric_sum+=expected

            if k>=4:
                n_deep+=1
                obs_deep+=excess
                sim_deep+=sim_excess
            else:
                n_shallow+=1
                obs_shallow+=excess
                sim_shallow+=sim_excess

    if n_all==0 or n_shallow==0 or n_deep==0:
        raise RuntimeError("empty topology stratum")

    names=["mean_pairwise_stop_separation","topological_span","contiguous_component_count"]
    overall={}
    for mi,name in enumerate(names):
        overall[name]=summarize_metric(obs_sum[mi],sim_sum[:,mi],n_all)

    primary=test_primary(
        obs_sum[0]/n_all,
        sim_sum[:,0]/n_all
    )

    strata={}
    for label,n,obs,sim in [
        ("shallow_k2_3",n_shallow,obs_shallow,sim_shallow),
        ("deep_k4_10",n_deep,obs_deep,sim_deep)
    ]:
        strata[label]={
            names[mi]:summarize_metric(obs[mi],sim[:,mi],n)
            for mi in range(3)
        }

    out={
        "analysis":"naamp_route_topology_geometry_v0_1",
        "contract":"landscape/NAAMP_ROUTE_TOPOLOGY_GEOMETRY_CONTRACT_V0_1.json",
        "separation_authority":"revision/NAAMP_LANDSCAPE_BEHAVIOUR_SEPARATION_2026-10-05.md",
        "status":"posthoc_landscape_hypothesis_generation",
        "coverage":{
            "pairs":int(len(pw)),
            "routes":int(pw.route_cluster.nunique()),
            "eligible_clusters_k2plus":int(n_all),
            "shallow_k2_3_clusters":int(n_shallow),
            "deep_k4_10_clusters":int(n_deep),
            "species":int(len(species)),
            "k_counts":k_counts
        },
        "primary":primary,
        "overall_metrics":overall,
        "raw_vs_expected":{
            names[i]:{
                "observed_mean":float(raw_metric_sum[i]/n_all),
                "fixed_q_exact_k_expected_mean":float(expected_metric_sum[i]/n_all)
            }
            for i in range(3)
        },
        "fixed_strata_descriptive":strata,
        "null":{
            "exact_observed_k_fixed":True,
            "fixed_q":True,
            "subset_distribution":"independent Bernoulli conditional on exact k, weights proportional to q/(1-q) odds",
            "replicates":B,
            "seed":SEED
        },
        "weather_provenance":{"era5_antecedent_amount_sha256":weather_sha},
        "interpretation_boundary":{
            "route_topology_is_exact_geographic_distance":False,
            "stop_number_confounded_with_survey_order":True,
            "movement_identified":False,
            "hydrological_connectivity_identified":False,
            "acoustic_propagation_identified":False,
            "social_process_identified":False,
            "independent_confirmation":False,
            "can_upgrade_rc6":False
        }
    }
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
