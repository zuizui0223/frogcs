#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import numpy as np

ROOT=Path(__file__).resolve().parents[1]
EXP=ROOT/"exploration"
OUT=ROOT/"audit"/"NAAMP_DEEP_VS_SHALLOW_TEMPLATE_ALIGNMENT_MC_STABILITY_RECEIPT_V0_1.json"

B=1000
SEEDS=list(range(2840300,2840320))
ANCHOR=0.75
EPS=1e-7
OBS=0.0296974698534744

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

def main():
    primary=json.loads((EXP/"NAAMP_DEEP_VS_SHALLOW_TEMPLATE_ALIGNMENT_CONTRAST_RECEIPT_V0_1.json").read_text())
    got=float(primary["rainfall_coefficient_contrast"]["beta_deep_minus_shallow"]["observed"])
    if abs(got-OBS)>1e-12:
        raise RuntimeError(f"primary observed contrast drift: {got}")

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
    cluster_specs=[]
    n_deep=n_shallow=0

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
            deep=bool(k>=4)
            cluster_specs.append((pair_i,deep,probs,hvals,expected))
            if deep:
                n_deep+=1
            else:
                n_shallow+=1

    if (n_deep,n_shallow)!=(409,838):
        raise RuntimeError(f"cluster-count drift deep={n_deep} shallow={n_shallow}")

    batches=[]
    pooled_exceed=0
    pooled_n=0
    pooled_sum=0.0
    q975=[]
    pvals=[]
    pass_flags=[]

    for seed in SEEDS:
        rng=np.random.default_rng(seed)
        num_deep=np.zeros(B,float)
        num_shallow=np.zeros(B,float)
        for pair_i,deep,probs,hvals,expected in cluster_specs:
            draws=rng.choice(len(probs),size=B,replace=True,p=probs)
            sim_excess=hvals[draws]-expected
            if deep:
                num_deep+=r[pair_i]*sim_excess
            else:
                num_shallow+=r[pair_i]*sim_excess
        sim=num_deep/den-num_shallow/den
        hi=float(np.quantile(sim,.975))
        p=float((1+np.sum(sim>=OBS))/(B+1))
        passed=bool(OBS>hi and p<0.05)
        batches.append({
            "seed":int(seed),
            "null_mean":float(np.mean(sim)),
            "null_q975":hi,
            "plus_one_upper_tail_p":p,
            "observed_above_q975":bool(OBS>hi),
            "primary_rule_pass":passed
        })
        q975.append(hi); pvals.append(p); pass_flags.append(passed)
        pooled_exceed+=int(np.sum(sim>=OBS))
        pooled_n+=int(len(sim))
        pooled_sum+=float(np.sum(sim))

    out={
        "analysis":"naamp_deep_vs_shallow_template_alignment_monte_carlo_stability_v0_1",
        "contract":"audit/NAAMP_DEEP_VS_SHALLOW_TEMPLATE_ALIGNMENT_MC_STABILITY_CONTRACT_V0_1.json",
        "status":"posthoc_numerical_stability_audit",
        "authoritative_primary":{
            "observed_beta_deep_minus_shallow":OBS,
            "primary_plus_one_p":0.02097902097902098,
            "primary_null_ci95":[-0.02531719865771154,0.028888371572041494],
            "primary_seed":2840234,
            "primary_replicates":1000
        },
        "coverage":{
            "pairs":int(len(pw)),
            "routes":int(pw.route_cluster.nunique()),
            "deep_clusters":int(n_deep),
            "shallow_clusters":int(n_shallow)
        },
        "audit":{
            "batches":len(SEEDS),
            "replicates_per_batch":B,
            "seeds":SEEDS,
            "batch_results":batches,
            "fraction_batches_primary_rule_pass":float(np.mean(pass_flags)),
            "batch_p_median":float(np.median(pvals)),
            "batch_p_range":[float(np.min(pvals)),float(np.max(pvals))],
            "batch_q975_median":float(np.median(q975)),
            "batch_q975_range":[float(np.min(q975)),float(np.max(q975))],
            "pooled_descriptive_tail_fraction":float(pooled_exceed/pooled_n),
            "pooled_descriptive_null_mean":float(pooled_sum/pooled_n)
        },
        "interpretation":{
            "primary_inference_replaced":False,
            "numerically_stable_by_contract":bool(
                np.mean(pass_flags)>=0.8 and (pooled_exceed/pooled_n)<0.05
            )
        },
        "weather_provenance":{
            "era5_antecedent_amount_sha256":weather_sha
        }
    }
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
