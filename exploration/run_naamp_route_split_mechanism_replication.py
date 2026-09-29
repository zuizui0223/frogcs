#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
NAAMP=ROOT/"scripts"/"naamp"
EXP=ROOT/"exploration"
OUT=EXP/"NAAMP_ROUTE_SPLIT_MECHANISM_REPLICATION_RECEIPT_V0_1.json"
B=1000
KAPPA=2.0
ANCHOR=0.75
SEED=2840223


def loadmod(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    mod=importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(mod)
    return mod


base=loadmod("pulse_base",NAAMP/"run_naamp_ecological_pulse.py")
spatial=loadmod("spatial_base",NAAMP/"run_naamp_spatial_taxonomic_activation_decomposition.py")
uniform=loadmod("uniform_base",NAAMP/"run_naamp_uniform_activation_null.py")
persistence=loadmod("persistence_base",NAAMP/"run_naamp_persistence_preserving_null.py")
calling=loadmod("calling_base",EXP/"run_naamp_calling_index_decomposition.py")


def fold(route_cluster):
    b=hashlib.sha256(str(route_cluster).encode("utf-8")).digest()[0]
    return "A" if b<128 else "B"


def summarize(v,observed):
    lo,hi=np.quantile(v,[0.025,0.975])
    return {
        "null_mean":float(np.mean(v)),
        "null_ci95":[float(lo),float(hi)],
        "observed":float(observed),
        "upper_tail_monte_carlo_p":float((1+np.sum(v>=observed))/(len(v)+1)),
    }


def subset_components(pair_data):
    return np.asarray([uniform.component_counts(d["wet"],d["dry"]) for d in pair_data],float)


def simulate_uniform(pair_data,probs,r,den,seed):
    rng=np.random.default_rng(seed)
    numer=np.zeros((B,4),float)
    for i,d in enumerate(pair_data):
        p=probs[d["key"]]
        q=uniform.solve_shift(p,d["wet_k"])
        wsim=rng.random((B,)+q.shape)<q[None,:,:]
        numer += r[i]*uniform.simulated_components(wsim,d["dry"])
    return numer/den


def simulate_persistence(pair_data,hist,r,den,seed):
    rng=np.random.default_rng(seed)
    numer=np.zeros((B,4),float)
    for i,d in enumerate(pair_data):
        p_hist=hist[d["key"]]
        dry=d["dry"].astype(float)
        p_anchor=(1-ANCHOR)*p_hist+ANCHOR*dry
        p_anchor=np.clip(p_anchor,1e-8,1-1e-8)
        q=uniform.solve_shift(p_anchor,d["wet_k"])
        wsim=rng.random((B,)+q.shape)<q[None,:,:]
        numer += r[i]*uniform.simulated_components(wsim,d["dry"])
    return numer/den


def contrast(betas):
    total=betas.sum(axis=1)
    ok=np.isfinite(total)&(np.abs(total)>1e-12)
    shares=betas[ok]/total[ok,None]
    return shares[:,2]-shares[:,1]


def calling_fold(df):
    endpoints=["ci_total","ci_activation","ci_deactivation","ci_shared_intensity"]
    models={x:calling.fit(df,x) for x in endpoints}
    total=models["ci_total"]["beta_rain_contrast"]
    act=models["ci_activation"]["beta_rain_contrast"]
    shared=models["ci_shared_intensity"]["beta_rain_contrast"]
    act_share=float(act/total) if abs(total)>1e-12 else None
    passed=bool(
        total>0 and models["ci_activation"]["ci95"][0]>0
        and act_share is not None and act_share>0.5 and act>shared
    )
    return {
        "n_pairs":int(len(df)),
        "n_routes":int(df["route_cluster"].nunique()),
        "models":models,
        "activation_share_of_total":act_share,
        "threshold_dominant":passed,
    }


def main():
    # CallingIndex pair table
    raw=base.load()
    runs,route_sets=base.build_runs(raw)
    eligible=set(runs["RunID"].astype(str))
    sampled,_=spatial.stop_matrix(raw,eligible)
    pairs_ci=base.pair_runs(runs,route_sets).copy().reset_index(drop=True)
    _,ci_by_run_stop,_=calling.build_calling_index(raw,eligible,sampled)
    rows=[]
    for p in pairs_ci.itertuples(index=False):
        row=p._asdict()
        row.update(calling.pair_components(p,sampled,ci_by_run_stop))
        rows.append(row)
    ci_df=pd.DataFrame(rows)
    ci_df["fold"]=ci_df["route_cluster"].map(fold)

    # Four-component pair data and null ingredients
    (
        pairs,pair_data,pools,dry_ids,sampled2,ss,r_all0,den_all0,obs_betas0,
        beta_mask,r_beta,den_beta,obs_sor
    )=uniform.prepare()
    pairs=pairs.copy().reset_index(drop=True)
    pairs["fold"]=pairs["route_cluster"].map(fold)
    stops_by_key={d["key"]:d["stops"] for d in pair_data}
    probs=uniform.baseline_probs(KAPPA,pools,dry_ids,stops_by_key,ss)
    hist=persistence.historical_cell_probs(pools,dry_ids,stops_by_key,ss)

    out={}
    for j,fname in enumerate(("A","B")):
        # Calling
        csub=ci_df[ci_df["fold"]==fname].copy()
        c_report=calling_fold(csub)

        # Axis contrast and fold-specific null
        idx=np.flatnonzero(pairs["fold"].to_numpy()==fname)
        psub=pairs.iloc[idx].copy().reset_index(drop=True)
        dsub=[pair_data[int(i)] for i in idx]
        r,den=uniform.design_residual(psub)
        comps=subset_components(dsub)
        obs_betas=(r[:,None]*comps).sum(axis=0)/den
        obs_shares=obs_betas/float(obs_betas.sum())
        observed=float(obs_shares[2]-obs_shares[1])

        ub=simulate_uniform(dsub,probs,r,den,SEED+10000+j)
        pb=simulate_persistence(dsub,hist,r,den,SEED+20000+j)
        ur=summarize(contrast(ub),observed)
        pr=summarize(contrast(pb),observed)
        axis_pass=bool(observed>ur["null_ci95"][1] and observed>pr["null_ci95"][1])

        out[fname]={
            "calling_index":c_report,
            "taxonomic_axis":{
                "observed_component_betas":{
                    "corner":float(obs_betas[0]),
                    "spatial":float(obs_betas[1]),
                    "taxonomic":float(obs_betas[2]),
                    "within_core":float(obs_betas[3]),
                },
                "observed_taxonomic_minus_spatial":observed,
                "uniform_kappa2":ur,
                "persistence_anchor_0_75":pr,
                "taxonomic_axis_excess":axis_pass,
            },
            "fold_pass":bool(c_report["threshold_dominant"] and axis_pass),
        }

    output={
        "analysis":"naamp_route_split_mechanism_replication_v0_1",
        "contract":"exploration/MECHANISM_UNIVERSALITY_CONTRACT_V0_1.json#route_split_mechanism_replication",
        "folds":out,
        "classification":{
            "both_folds_pass":bool(out["A"]["fold_pass"] and out["B"]["fold_pass"]),
            "meaning":"Internal replication across disjoint route sets only; not cross-continental universality."
        },
        "interpretation_boundary":{
            "causal_rainfall_claim":False,
            "physiological_mechanism_identified":False,
            "submission_story_change_authorized":False,
        }
    }
    OUT.write_text(json.dumps(output,indent=2,sort_keys=True)+"\n")
    print(json.dumps(output,indent=2,sort_keys=True))


if __name__=="__main__":
    main()
