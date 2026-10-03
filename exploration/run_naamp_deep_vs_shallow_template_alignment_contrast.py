#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import numpy as np

ROOT=Path(__file__).resolve().parents[1]
EXP=ROOT/"exploration"
OUT=EXP/"NAAMP_DEEP_VS_SHALLOW_TEMPLATE_ALIGNMENT_CONTRAST_RECEIPT_V0_1.json"

B=1000
SEED=2840234
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
align=loadmod("template_alignment",EXP/"run_naamp_deep_historical_template_alignment.py")

def test_upper(obs,sim):
    sim=np.asarray(sim,float)
    lo,hi=np.quantile(sim,[.025,.975])
    p=float((1+np.sum(sim>=obs))/(len(sim)+1))
    return {
        "observed":float(obs),
        "null_mean":float(np.mean(sim)),
        "null_ci95":[float(lo),float(hi)],
        "plus_one_upper_tail_p":p,
        "positive_supported":bool(obs>hi and p<0.05)
    }

def main():
    prior_receipt=json.loads((EXP/"NAAMP_DEEP_HISTORICAL_TEMPLATE_ALIGNMENT_RECEIPT_V0_1.json").read_text())
    if prior_receipt.get("coverage",{}).get("eligible_clusters")!=1247:
        raise RuntimeError("alignment-receipt coverage drift")

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
    meta,by_stratum,run_sites,run_site_species=mem.build_history_index(
        runs,sampled,ss,site
    )
    ci=local.ci_map(raw,eligible,sampled)

    runs_weather=runs[runs["RunID"].astype(str).isin(weather)].copy().reset_index(drop=True)
    runs_weather["rain72_mm"]=[
        weather[str(r)]["rain72_mm"] for r in runs_weather["RunID"].astype(str)
    ]
    runs_weather["rain72_log"]=np.log1p(runs_weather["rain72_mm"].astype(float))
    all_species=sorted({sp for spp in pools.values() for sp in spp})
    pred_A,_,_=rain.fit_predict_amount_environment(runs_weather,sampled,ss,all_species,"A")
    pred_B,_,_=rain.fit_predict_amount_environment(runs_weather,sampled,ss,all_species,"B")
    pred_by_train={"A":pred_A,"B":pred_B}

    r,den=uniform.design_residual(pw)
    obs_pair_deep=np.zeros(len(pw),float)
    obs_pair_shallow=np.zeros(len(pw),float)
    sim_beta_num_deep=np.zeros(B,float)
    sim_beta_num_shallow=np.zeros(B,float)
    sim_sum_deep=np.zeros(B,float)
    sim_sum_shallow=np.zeros(B,float)
    obs_sum_deep=0.0
    obs_sum_shallow=0.0
    n_deep=0
    n_shallow=0
    species=set()

    rng=np.random.default_rng(SEED)

    for pair_i,(p,dct,p_hist) in enumerate(zip(pw.itertuples(index=False),dw,hw)):
        ids=mem.focal_siteids(p,dct,site)
        if ids is None:
            raise RuntimeError("lost physical SiteID stability")
        prior=mem.eligible_prior_runs(p,dct,ids,meta,by_stratum,run_sites)
        if not prior:
            raise RuntimeError("lost strictly prior history")

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
            k=int(wet[si].sum())
            if k<1:
                continue
            m=int(strong[si].sum())
            if m<1 or m>9:
                continue

            _,probs,hvals,expected=align.conditional_subset_distribution(
                q[si],k,strong[si]
            )
            h=float(np.sum(wet[si]&strong[si]))
            excess=float(h-expected)
            draws=rng.choice(len(probs),size=B,replace=True,p=probs)
            sim_excess=hvals[draws]-expected
            species.add(str(sp))

            if k>=4:
                n_deep+=1
                obs_sum_deep+=excess
                obs_pair_deep[pair_i]+=excess
                sim_sum_deep+=sim_excess
                sim_beta_num_deep+=r[pair_i]*sim_excess
            else:
                n_shallow+=1
                obs_sum_shallow+=excess
                obs_pair_shallow[pair_i]+=excess
                sim_sum_shallow+=sim_excess
                sim_beta_num_shallow+=r[pair_i]*sim_excess

    if (n_deep,n_shallow)!=(409,838):
        raise RuntimeError(f"cluster-count drift deep={n_deep} shallow={n_shallow}")

    obs_beta_deep=float((r*obs_pair_deep).sum()/den)
    obs_beta_shallow=float((r*obs_pair_shallow).sum()/den)
    obs_beta_contrast=float(obs_beta_deep-obs_beta_shallow)
    sim_beta_deep=sim_beta_num_deep/den
    sim_beta_shallow=sim_beta_num_shallow/den
    sim_beta_contrast=sim_beta_deep-sim_beta_shallow

    obs_mean_deep=float(obs_sum_deep/n_deep)
    obs_mean_shallow=float(obs_sum_shallow/n_shallow)
    obs_mean_contrast=float(obs_mean_deep-obs_mean_shallow)
    sim_mean_contrast=sim_sum_deep/n_deep-sim_sum_shallow/n_shallow

    out={
        "analysis":"naamp_deep_vs_shallow_template_alignment_contrast_v0_1",
        "contract":"exploration/NAAMP_DEEP_VS_SHALLOW_TEMPLATE_ALIGNMENT_CONTRAST_CONTRACT_V0_1.json",
        "status":"posthoc_direct_contrast_triggered",
        "coverage":{
            "pairs":int(len(pw)),
            "routes":int(pw.route_cluster.nunique()),
            "deep_k4plus_clusters":int(n_deep),
            "shallow_k1to3_clusters":int(n_shallow),
            "species":int(len(species))
        },
        "rainfall_coefficient_contrast":{
            "beta_deep":obs_beta_deep,
            "beta_shallow":obs_beta_shallow,
            "beta_deep_minus_shallow":test_upper(obs_beta_contrast,sim_beta_contrast)
        },
        "cluster_mean_contrast":{
            "mean_deep":obs_mean_deep,
            "mean_shallow":obs_mean_shallow,
            "mean_deep_minus_shallow":test_upper(obs_mean_contrast,sim_mean_contrast)
        },
        "null":{
            "exact_observed_k_fixed":True,
            "fixed_q_and_prior_strong_mask":True,
            "replicates":B,
            "seed":SEED,
            "tail":"upper"
        },
        "decision":{
            "template_coupling_stronger_in_deep_tail":bool(
                test_upper(obs_beta_contrast,sim_beta_contrast)["positive_supported"]
            )
        },
        "weather_provenance":{
            "era5_antecedent_amount_sha256":weather_sha
        },
        "interpretation_boundary":{
            "posthoc_direct_contrast":True,
            "deep_shallow_descriptive_difference_known_before_contract":True,
            "unique_lower_level_mechanism_identified":False,
            "independent_confirmation":False
        }
    }
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
