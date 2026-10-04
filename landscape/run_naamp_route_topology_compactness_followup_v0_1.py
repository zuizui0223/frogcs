#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import numpy as np

ROOT=Path(__file__).resolve().parents[1]
LAND=ROOT/"landscape"
BASE=LAND/"run_naamp_route_topology_geometry_v0_1.py"
OUT=LAND/"NAAMP_ROUTE_TOPOLOGY_COMPACTNESS_FOLLOWUP_RECEIPT_V0_1.json"

def loadmod(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    mod=importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(mod)
    return mod

geom=loadmod("route_topology_geometry",BASE)
rain=geom.rain
flex=geom.flex
joint=geom.joint
uniform=geom.uniform

B=2000
SEED=2840301
ANCHOR=0.75
EPS=1e-7

def lower_test(obs,sim):
    sim=np.asarray(sim,float)
    lo,hi=np.quantile(sim,[.025,.975])
    p=float((1+np.sum(sim<=obs))/(len(sim)+1))
    return {
        "observed":float(obs),
        "null_mean":float(np.mean(sim)),
        "null_ci95":[float(lo),float(hi)],
        "plus_one_lower_tail_p":p,
        "negative_compactness_supported":bool(obs<lo and p<0.05)
    }

def two_sided_sign_test(obs,sim):
    sim=np.asarray(sim,float)
    lo,hi=np.quantile(sim,[.025,.975])
    p_lo=float((1+np.sum(sim<=obs))/(len(sim)+1))
    p_hi=float((1+np.sum(sim>=obs))/(len(sim)+1))
    p=float(min(1.0,2*min(p_lo,p_hi)))
    return {
        "observed":float(obs),
        "null_mean":float(np.mean(sim)),
        "null_ci95":[float(lo),float(hi)],
        "plus_one_two_sided_p":p,
        "outside_95":bool(obs<lo or obs>hi)
    }

def main():
    contract=json.loads((LAND/"NAAMP_ROUTE_TOPOLOGY_COMPACTNESS_FOLLOWUP_CONTRACT_V0_1.json").read_text())
    prior=json.loads((LAND/"NAAMP_ROUTE_TOPOLOGY_GEOMETRY_RECEIPT_V0_1.json").read_text())
    if prior["primary"]["positive_dispersion_supported"] is not False:
        raise RuntimeError("follow-up trigger not met")
    if contract["Monte_Carlo"]["seed"]!=SEED or contract["Monte_Carlo"]["replicates"]!=B:
        raise RuntimeError("follow-up contract drift")

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

    runs_weather=runs[runs["RunID"].astype(str).isin(weather)].copy().reset_index(drop=True)
    runs_weather["rain72_mm"]=[weather[str(r)]["rain72_mm"] for r in runs_weather["RunID"].astype(str)]
    runs_weather["rain72_log"]=np.log1p(runs_weather["rain72_mm"].astype(float))
    all_species=sorted({sp for spp in pools.values() for sp in spp})
    pred_A,_,_=rain.fit_predict_amount_environment(runs_weather,sampled,ss,all_species,"A")
    pred_B,_,_=rain.fit_predict_amount_environment(runs_weather,sampled,ss,all_species,"B")
    pred_by_train={"A":pred_A,"B":pred_B}

    rng=np.random.default_rng(SEED)
    obs_all=np.zeros(3,float)
    sim_all=np.zeros((B,3),float)
    obs_deep=np.zeros(3,float)
    sim_deep=np.zeros((B,3),float)
    obs_shallow=np.zeros(3,float)
    sim_shallow=np.zeros((B,3),float)
    n_all=n_deep=n_shallow=0

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

        for si,_sp in enumerate(dct["species"]):
            if dry[si].any():
                continue
            active=np.flatnonzero(wet[si])
            k=int(len(active))
            if k<2:
                continue
            combos,probs,vals,expected=geom.exact_subset_distribution(q[si],k)
            observed=geom.topology_metrics(active)
            excess=observed-expected
            draws=rng.choice(len(probs),size=B,replace=True,p=probs)
            sim_excess=vals[draws]-expected[None,:]

            n_all+=1
            obs_all+=excess
            sim_all+=sim_excess
            if k>=4:
                n_deep+=1
                obs_deep+=excess
                sim_deep+=sim_excess
            else:
                n_shallow+=1
                obs_shallow+=excess
                sim_shallow+=sim_excess

    if (n_all,n_shallow,n_deep)!=(1693,926,767):
        raise RuntimeError(f"cluster-count drift {(n_all,n_shallow,n_deep)}")

    names=["mean_pairwise_stop_separation","topological_span","contiguous_component_count"]
    compactness={
        name:lower_test(obs_all[i]/n_all,sim_all[:,i]/n_all)
        for i,name in enumerate(names)
    }

    obs_contrast=(obs_deep[0]/n_deep)-(obs_shallow[0]/n_shallow)
    sim_contrast=(sim_deep[:,0]/n_deep)-(sim_shallow[:,0]/n_shallow)

    out={
        "analysis":"naamp_route_topology_compactness_followup_v0_1",
        "contract":"landscape/NAAMP_ROUTE_TOPOLOGY_COMPACTNESS_FOLLOWUP_CONTRACT_V0_1.json",
        "prior_receipt":"landscape/NAAMP_ROUTE_TOPOLOGY_GEOMETRY_RECEIPT_V0_1.json",
        "status":"post_readback_sign_reversal_quantification",
        "coverage":{
            "pairs":int(len(pw)),
            "routes":int(pw.route_cluster.nunique()),
            "eligible_clusters_k2plus":int(n_all),
            "shallow_k2_3_clusters":int(n_shallow),
            "deep_k4_10_clusters":int(n_deep)
        },
        "compactness_lower_tail":compactness,
        "deep_vs_shallow_mean_pairwise_excess":{
            "deep_mean_excess":float(obs_deep[0]/n_deep),
            "shallow_mean_excess":float(obs_shallow[0]/n_shallow),
            "deep_minus_shallow":two_sided_sign_test(obs_contrast,sim_contrast)
        },
        "null":{
            "same_generator_as_v0_1":True,
            "replicates":B,
            "seed":SEED,
            "exact_k_fixed":True,
            "fixed_q":True
        },
        "weather_provenance":{"era5_antecedent_amount_sha256":weather_sha},
        "interpretation_boundary":{
            "original_positive_dispersion_prediction_failed":True,
            "post_readback_followup":True,
            "route_topology_is_exact_geographic_distance":False,
            "mechanism_identified":False,
            "independent_confirmation":False,
            "can_upgrade_rc6":False
        }
    }
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
