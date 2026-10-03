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
NAAMP=ROOT/"scripts"/"naamp"
OUT=EXP/"NAAMP_DEEP_HISTORICAL_TEMPLATE_ALIGNMENT_RECEIPT_V0_1.json"

B=1000
SEED=2840233
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

def conditional_subset_distribution(q,k,strong):
    q=np.clip(np.asarray(q,float),EPS,1-EPS)
    strong=np.asarray(strong,bool)
    combos=np.asarray(list(itertools.combinations(range(10),int(k))),dtype=int)
    if len(combos)==0:
        raise RuntimeError(f"no subsets for k={k}")
    logodds=np.log(q)-np.log1p(-q)
    logw=logodds[combos].sum(axis=1)
    logw=logw-logsumexp(logw)
    probs=np.exp(logw)
    hvals=strong[combos].sum(axis=1).astype(float)
    expected=float(probs@hvals)
    return combos,probs,hvals,expected

def main():
    raw,runs,psub,dsub,hsub,pools,sampled,ss=flex.prepare_subset()
    mid=rain.build_midpoints(raw,runs)
    weather,weather_sha=rain.antecedent_amounts(mid)

    # Intersect exactly with the same ERA5-eligible set used by the strongest comparator.
    mask=np.asarray([
        str(p.wet_RunID) in weather and str(p.dry_RunID) in weather
        for p in psub.itertuples(index=False)
    ],bool)
    idx=np.flatnonzero(mask)
    pw=psub.iloc[idx].copy().reset_index(drop=True)
    dw=[dsub[int(i)] for i in idx]
    hw=[hsub[int(i)] for i in idx]
    if len(pw)!=2835 or pw.route_cluster.nunique()!=428:
        raise RuntimeError(f"weather subset drift: pairs={len(pw)} routes={pw.route_cluster.nunique()}")

    eligible=set(runs.RunID.astype(str))
    site=mem.site_map(raw,eligible)
    meta,by_stratum,run_sites,run_site_species=mem.build_history_index(
        runs,sampled,ss,site
    )
    ci=local.ci_map(raw,eligible,sampled)

    runs_weather=runs[runs["RunID"].astype(str).isin(weather)].copy().reset_index(drop=True)
    runs_weather["rain72_mm"]=[weather[str(r)]["rain72_mm"] for r in runs_weather["RunID"].astype(str)]
    runs_weather["rain72_log"]=np.log1p(runs_weather["rain72_mm"].astype(float))

    all_species=sorted({sp for spp in pools.values() for sp in spp})
    pred_A,audit_A,fold_A=rain.fit_predict_amount_environment(
        runs_weather,sampled,ss,all_species,"A"
    )
    pred_B,audit_B,fold_B=rain.fit_predict_amount_environment(
        runs_weather,sampled,ss,all_species,"B"
    )
    pred_by_train={"A":pred_A,"B":pred_B}

    rng=np.random.default_rng(SEED)
    r,den=uniform.design_residual(pw)
    obs_pair_deep=np.zeros(len(pw),float)
    obs_pair_all=np.zeros(len(pw),float)
    sim_num_deep=np.zeros(B,float)
    sim_num_all=np.zeros(B,float)

    cluster_rows=[]
    prior_run_counts=[]

    for pair_i,(p,dct,p_hist) in enumerate(zip(pw.itertuples(index=False),dw,hw)):
        ids=mem.focal_siteids(p,dct,site)
        if ids is None:
            raise RuntimeError("weather/history pair lost physical SiteID stability")
        prior=mem.eligible_prior_runs(p,dct,ids,meta,by_stratum,run_sites)
        if not prior:
            raise RuntimeError("weather/history pair lost strictly prior history")
        prior_run_counts.append(len(prior))

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

        # Strictly-prior strong-site mask at the ten focal physical SiteIDs.
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

            combos,probs,hvals,expected=conditional_subset_distribution(
                q[si],k,strong[si]
            )
            h=float(np.sum(wet[si]&strong[si]))
            excess=float(h-expected)
            uniform_excess=float(h-(k*m/10.0))
            is_deep=bool(k>=4)

            draws=rng.choice(len(probs),size=B,replace=True,p=probs)
            sim_excess=hvals[draws]-expected

            obs_pair_all[pair_i]+=excess
            sim_num_all+=r[pair_i]*sim_excess
            if is_deep:
                obs_pair_deep[pair_i]+=excess
                sim_num_deep+=r[pair_i]*sim_excess

            cluster_rows.append({
                "pair_index":int(pair_i),
                "species":str(sp),
                "k":k,
                "m_prior_strong":m,
                "h_observed_overlap":h,
                "q_conditional_expected_overlap":expected,
                "q_conditioned_overlap_excess":excess,
                "uniform_hypergeometric_overlap_excess":uniform_excess,
                "deep_k4plus":is_deep,
                "route_cluster":str(p.route_cluster)
            })

    if not cluster_rows:
        raise RuntimeError("no eligible template-alignment clusters")

    obs_beta_deep=float((r*obs_pair_deep).sum()/den)
    obs_beta_all=float((r*obs_pair_all).sum()/den)
    sim_beta_deep=sim_num_deep/den
    sim_beta_all=sim_num_all/den

    def test(obs,sim):
        lo,hi=np.quantile(sim,[.025,.975])
        p=float((1+np.sum(sim>=obs))/(B+1))
        return {
            "observed_beta":float(obs),
            "null_mean":float(np.mean(sim)),
            "null_ci95":[float(lo),float(hi)],
            "plus_one_upper_tail_p":p,
            "positive_alignment_supported":bool(obs>hi and p<0.05)
        }

    deep=[x for x in cluster_rows if x["deep_k4plus"]]
    shallow=[x for x in cluster_rows if not x["deep_k4plus"]]
    all_ex=np.asarray([x["q_conditioned_overlap_excess"] for x in cluster_rows],float)
    deep_ex=np.asarray([x["q_conditioned_overlap_excess"] for x in deep],float)
    shallow_ex=np.asarray([x["q_conditioned_overlap_excess"] for x in shallow],float)
    uniform_all=np.asarray([x["uniform_hypergeometric_overlap_excess"] for x in cluster_rows],float)
    uniform_deep=np.asarray([x["uniform_hypergeometric_overlap_excess"] for x in deep],float)

    out={
        "analysis":"naamp_deep_activation_historical_template_alignment_v0_1",
        "contract":"exploration/NAAMP_DEEP_HISTORICAL_TEMPLATE_ALIGNMENT_CONTRACT_V0_1.json",
        "status":"posthoc_fast_gate_slow_template_alignment_triggered",
        "coverage":{
            "pairs":int(len(pw)),
            "routes":int(pw.route_cluster.nunique()),
            "eligible_clusters":int(len(cluster_rows)),
            "deep_k4plus_clusters":int(len(deep)),
            "shallow_k1to3_clusters":int(len(shallow)),
            "species":int(len({x["species"] for x in cluster_rows})),
            "median_prior_runs":float(np.median(prior_run_counts))
        },
        "primary_deep_k4plus":test(obs_beta_deep,sim_beta_deep),
        "secondary_all_k1plus":test(obs_beta_all,sim_beta_all),
        "cluster_alignment":{
            "mean_q_conditioned_excess_all":float(np.mean(all_ex)),
            "mean_q_conditioned_excess_deep":float(np.mean(deep_ex)) if len(deep_ex) else None,
            "mean_q_conditioned_excess_shallow":float(np.mean(shallow_ex)) if len(shallow_ex) else None,
            "deep_minus_shallow_mean_excess":float(np.mean(deep_ex)-np.mean(shallow_ex)) if len(deep_ex) and len(shallow_ex) else None,
            "fraction_deep_positive_q_conditioned_excess":float(np.mean(deep_ex>0)) if len(deep_ex) else None,
            "mean_uniform_overlap_excess_all":float(np.mean(uniform_all)),
            "mean_uniform_overlap_excess_deep":float(np.mean(uniform_deep)) if len(uniform_deep) else None
        },
        "q_conditioning":{
            "exact_k_fixed_per_observed_cluster":True,
            "conditional_independent_bernoulli_weights":"subset probability proportional to product of q/(1-q) odds",
            "enumerated_subsets_max":252,
            "simulations":B,
            "seed":SEED
        },
        "weather_provenance":{"era5_antecedent_amount_sha256":weather_sha},
        "interpretation_boundary":{
            "individual_fidelity_identified":False,
            "social_attraction_identified":False,
            "hydrological_causality_identified":False,
            "unique_lower_level_mechanism_identified":False,
            "independent_confirmation":False
        }
    }
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
