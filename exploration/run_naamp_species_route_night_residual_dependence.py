#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import numpy as np

ROOT=Path(__file__).resolve().parents[1]
EXP=ROOT/"exploration"
OUT=EXP/"NAAMP_SPECIES_ROUTE_NIGHT_RESIDUAL_DEPENDENCE_RECEIPT_V0_1.json"
TRIGGER_RECEIPT=EXP/"NAAMP_RAIN_AMOUNT_COMMON_ENVIRONMENT_NULL_RECEIPT_V0_1.json"

B=1000
SEED=2840225
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
mem=rain.mem
uniform=rain.uniform

def pair_corr_numerator(y,q):
    e=np.asarray(y,float)-np.asarray(q,float)
    # Sum over species of all unordered within-species stop-pair products.
    s=e.sum(axis=1)
    ss=(e*e).sum(axis=1)
    return float(np.sum((s*s-ss)/2.0))

def pair_corr_denominator(q):
    q=np.asarray(q,float)
    v=np.clip(q*(1.0-q),EPS,None)
    z=np.sqrt(v)
    s=z.sum(axis=1)
    ss=(z*z).sum(axis=1)
    return float(np.sum((s*s-ss)/2.0))

def simulated_pair_numerators(w,q):
    # w: B x species x stops; q: species x stops
    e=w.astype(float)-q[None,:,:]
    s=e.sum(axis=2)
    ss=(e*e).sum(axis=2)
    return ((s*s-ss)/2.0).sum(axis=1)

def main():
    trigger=json.loads(TRIGGER_RECEIPT.read_text())
    if trigger.get("decision")!="residual_dependence_beyond_rain_amount_common_environment":
        out={
            "analysis":"naamp_species_route_night_residual_dependence_v0_1",
            "status":"not_run_trigger_not_met",
            "trigger_decision":trigger.get("decision")
        }
        OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
        print(json.dumps(out,indent=2,sort_keys=True))
        return

    raw,runs,psub,dsub,hsub,pools,sampled,ss=flex.prepare_subset()
    mid=rain.build_midpoints(raw,runs)
    weather,weather_sha=rain.antecedent_amounts(mid)

    mask=np.asarray([
        str(p.wet_RunID) in weather and str(p.dry_RunID) in weather
        for p in psub.itertuples(index=False)
    ],bool)
    idx=np.flatnonzero(mask)
    pw=psub.iloc[idx].copy().reset_index(drop=True)
    dw=[dsub[int(i)] for i in idx]
    hw=[hsub[int(i)] for i in idx]

    if len(pw)!=int(trigger["coverage"]["weather_prior_history_pairs"]):
        raise RuntimeError(
            f"weather subset drift {len(pw)} != {trigger['coverage']['weather_prior_history_pairs']}"
        )

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
    observed_num=0.0
    null_num=np.zeros(B,float)
    denominator=0.0
    n_clusters=0
    n_clusters_with_observed_positive=0
    n_species_stop_cells=0
    q_values=[]

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

        observed_num+=pair_corr_numerator(y,q)
        denominator+=pair_corr_denominator(q)
        w=rng.random((B,)+q.shape)<q[None,:,:]
        null_num+=simulated_pair_numerators(w,q)

        n_clusters+=int(q.shape[0])
        n_clusters_with_observed_positive+=int(np.sum(y.sum(axis=1)>0))
        n_species_stop_cells+=int(q.size)
        q_values.append(q.ravel())

    if denominator<=0:
        raise RuntimeError("nonpositive residual-correlation denominator")

    rho_obs=float(observed_num/denominator)
    rho_null=null_num/denominator
    lo,hi=np.quantile(rho_null,[.025,.975])
    p=float((1+np.sum(rho_null>=rho_obs))/(B+1))
    supported=bool(rho_obs>hi and p<0.05)

    qv=np.concatenate(q_values) if q_values else np.asarray([],float)
    design_effect=float(1+9*rho_obs) if rho_obs>0 else None
    n_eff=float(10/design_effect) if design_effect and design_effect>0 else None

    out={
        "analysis":"naamp_species_route_night_residual_dependence_v0_1",
        "contract":"exploration/NAAMP_SPECIES_ROUTE_NIGHT_RESIDUAL_DEPENDENCE_CONTRACT_V0_1.json",
        "trigger":"residual_dependence_beyond_rain_amount_common_environment",
        "status":"posthoc_exploratory_triggered",
        "coverage":{
            "pairs":int(len(pw)),
            "routes":int(pw.route_cluster.nunique()),
            "states":int(pw.State.nunique()),
            "species_x_route_night_clusters":int(n_clusters),
            "clusters_with_at_least_one_observed_positive_stop":int(n_clusters_with_observed_positive),
            "species_x_stop_cells":int(n_species_stop_cells)
        },
        "prediction_provenance":{
            "era5_antecedent_amount_sha256":weather_sha,
            "fold_A":fold_A,
            "fold_B":fold_B,
            "mean_q":float(np.mean(qv)) if len(qv) else None,
            "q05_q95":[float(np.quantile(qv,.05)),float(np.quantile(qv,.95))] if len(qv) else None
        },
        "residual_dependence":{
            "rho_resid":rho_obs,
            "null_mean":float(np.mean(rho_null)),
            "null_ci95":[float(lo),float(hi)],
            "plus_one_upper_tail_p":p,
            "positive_dependence_supported":supported
        },
        "monitoring_translation":{
            "exchangeable_ten_stop_design_effect_heuristic":design_effect,
            "effective_stop_count_heuristic":n_eff,
            "exact_design_effect_for_published_occupancy_model":False
        },
        "interpretation":{
            "conditional_stop_independence_rejected":supported,
            "measured_weather_and_site_history_exhaust_shared_environment":False,
            "social_facilitation_identified":False,
            "synchronous_breeding_identified":False,
            "movement_identified":False,
            "causal_rainfall_claim":False,
            "independent_confirmation":False
        }
    }
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
