#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import itertools
import json
from pathlib import Path

import numpy as np
from scipy.special import logsumexp

ROOT=Path(__file__).resolve().parents[2]
WFTS=ROOT/"scripts"/"wfts"
EXP=ROOT/"revision"
B=1000
SEED=2840236
EPS=1e-7

def loadmod(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    mod=importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(mod)
    return mod

sec=loadmod("wfts_secondary",WFTS/"run_wfts_secondary_route_night_diagnostics_v0_2.py")
base=sec.base

def conditional_subset(q,k,strong):
    q=np.clip(np.asarray(q,float),EPS,1-EPS)
    strong=np.asarray(strong,bool)
    combos=np.asarray(list(itertools.combinations(range(10),int(k))),dtype=int)
    logodds=np.log(q)-np.log1p(-q)
    lw=logodds[combos].sum(axis=1)
    probs=np.exp(lw-logsumexp(lw))
    hvals=strong[combos].sum(axis=1).astype(float)
    return probs,hvals,float(probs@hvals)

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
    ap=argparse.ArgumentParser()
    ap.add_argument("--runs",required=True)
    ap.add_argument("--matrix",required=True)
    ap.add_argument("--preflight-receipt",required=True)
    ap.add_argument("--primary-result",required=True)
    ap.add_argument("--common-env-runs",required=True)
    ap.add_argument("--common-env-receipt",required=True)
    ap.add_argument("--secondary-result",required=True)
    ap.add_argument("--output",required=True)
    args=ap.parse_args()

    runs_path=Path(args.runs); matrix_path=Path(args.matrix)
    primary=json.loads(Path(args.primary_result).read_text())
    secondary=json.loads(Path(args.secondary_result).read_text())
    preflight=json.loads(Path(args.preflight_receipt).read_text())
    weather_receipt=json.loads(Path(args.common_env_receipt).read_text())

    input_sha={"runs":base.sha256_file(runs_path),"matrix":base.sha256_file(matrix_path)}
    if primary.get("response_endpoints_read") is not True:
        raise RuntimeError("primary result not complete")
    if primary.get("input_sha256")!=input_sha:
        raise RuntimeError("primary input hash mismatch")
    if secondary.get("status")!="prospective_secondary_executed_after_primary":
        raise RuntimeError("prospective common-environment secondary must run first")
    if secondary.get("provenance",{}).get("primary_input_sha256")!=input_sha:
        raise RuntimeError("secondary/primary input hash mismatch")
    if preflight.get("coverage",{}).get("gate_pass") is not True:
        raise RuntimeError("preflight gate did not pass")
    if weather_receipt.get("response_columns_read") is not False:
        raise RuntimeError("common-environment weather was not response-free")

    runs_full,taxa,psub,phs,drys,wets,wet_k,species_list,r,den,obs=sec.prepare_analysis(
        runs_path,matrix_path,Path(args.common_env_runs),primary
    )

    # Reconstruct binary run matrices for the frozen 3-day q generator.
    _,runs0,matrix0,taxa0=base.load_inputs(runs_path,matrix_path)
    ci_mats,sites,_=base.build_run_matrices(runs0,matrix0,taxa0)
    binary_mats={k:(v>0) for k,v in ci_mats.items()}
    sec.run_common_env_window.run_mats=binary_mats
    _,q_list,_=sec.run_common_env_window(
        runs_full,taxa,psub,phs,drys,wets,wet_k,species_list,r,den,obs,
        "prcp_3d_exposure",2840226,True
    )
    if len(q_list)!=len(psub):
        raise RuntimeError("q-list length mismatch")

    tax_idx={sp:i for i,sp in enumerate(taxa)}
    rng=np.random.default_rng(SEED)
    obs_pair_deep=np.zeros(len(psub),float)
    obs_pair_shallow=np.zeros(len(psub),float)
    sim_num_deep=np.zeros(B,float)
    sim_num_shallow=np.zeros(B,float)
    cluster_rows=[]
    eligible_routes=set()
    eligible_taxa=set()

    for pair_i,(p,q,wet,dry,species) in enumerate(zip(
        psub.itertuples(index=False),q_list,wets,drys,species_list
    )):
        focal_sites=sites[p.wet_key]
        g=runs0[
            (runs0.route_id.astype(str)==str(p.route_id))&
            (runs0.survey_period.astype(str)==str(p.survey_period))&
            (runs0.survey_year.astype(int)<int(p.year_earlier))
        ].sort_values("survey_year")
        prior=[]
        for rr in g.itertuples(index=False):
            key=base.run_key(rr.route_id,rr.survey_period,rr.survey_year)
            if len(set(focal_sites)&set(sites[key]))>=8:
                prior.append(key)
        if not prior:
            raise RuntimeError("principal pair lost prior history")

        strong=np.zeros_like(dry,dtype=bool)
        for key in prior:
            current_sites=sites[key]
            pos={sid:i for i,sid in enumerate(current_sites)}
            mat=ci_mats[key]
            for t,sid in enumerate(focal_sites):
                if sid not in pos:
                    continue
                j=pos[sid]
                for si,sp in enumerate(species):
                    if int(mat[tax_idx[sp],j])>=2:
                        strong[si,t]=True

        for si,sp in enumerate(species):
            if dry[si].any():
                continue
            k=int(wet[si].sum())
            if k<1:
                continue
            m=int(strong[si].sum())
            if m<1 or m>9:
                continue
            probs,hvals,expected=conditional_subset(q[si],k,strong[si])
            h=float(np.sum(wet[si]&strong[si]))
            excess=float(h-expected)
            sim_excess=hvals[rng.choice(len(probs),size=B,replace=True,p=probs)]-expected
            deep=bool(k>=4)
            eligible_routes.add(str(p.route_id))
            eligible_taxa.add(str(sp))
            if deep:
                obs_pair_deep[pair_i]+=excess
                sim_num_deep+=r[pair_i]*sim_excess
            else:
                obs_pair_shallow[pair_i]+=excess
                sim_num_shallow+=r[pair_i]*sim_excess
            cluster_rows.append({
                "route_id":str(p.route_id),
                "taxon":str(sp),
                "k":k,
                "deep":deep,
                "excess":excess
            })

    deep=[z for z in cluster_rows if z["deep"]]
    shallow=[z for z in cluster_rows if not z["deep"]]
    n_deep=len(deep); n_shallow=len(shallow)
    gate=bool(
        n_deep>=50 and n_shallow>=100 and
        len(eligible_taxa)>=5 and len(eligible_routes)>=20
    )

    if n_deep and n_shallow:
        beta_deep=float((r*obs_pair_deep).sum()/den)
        beta_shallow=float((r*obs_pair_shallow).sum()/den)
        sim_deep=sim_num_deep/den
        sim_shallow=sim_num_shallow/den
        deep_test=test_upper(beta_deep,sim_deep)
        contrast=test_upper(beta_deep-beta_shallow,sim_deep-sim_shallow)
    else:
        beta_deep=beta_shallow=None
        deep_test=contrast=None

    if not gate:
        decision="inconclusive_secondary_template_link"
    elif deep_test["positive_supported"] and contrast["positive_supported"]:
        decision="template_link_support"
    else:
        decision="template_link_non_support"

    out={
        "analysis":"wfts_prospective_deep_template_alignment_v0_1",
        "authority":"revision/WFTS_PROSPECTIVE_DEEP_TEMPLATE_ALIGNMENT_V0_1.json",
        "status":"prospective_secondary_after_primary_and_common_environment",
        "coverage":{
            "pairs":int(len(psub)),
            "routes":int(psub.route_id.nunique()),
            "eligible_alignment_routes":int(len(eligible_routes)),
            "eligible_alignment_taxa":int(len(eligible_taxa)),
            "deep_k4plus_clusters":int(n_deep),
            "shallow_k1to3_clusters":int(n_shallow),
            "informativeness_gate_pass":gate
        },
        "primary_deep_minus_shallow":contrast,
        "secondary_deep_only":deep_test,
        "observed_beta_deep":beta_deep,
        "observed_beta_shallow":beta_shallow,
        "decision":decision,
        "fixed_gate":{
            "minimum_deep_k4plus_clusters":50,
            "minimum_shallow_k1to3_clusters":100,
            "minimum_taxa":5,
            "minimum_routes":20
        },
        "provenance":{
            "input_sha256":input_sha,
            "primary_decision":primary.get("decision"),
            "secondary_common_environment_status":secondary.get("status"),
            "q_weather_window":"3 complete pre-survey Daymet days",
            "simulation_replicates":B,
            "seed":SEED
        },
        "interpretation_boundary":{
            "can_change_primary_replication_classification":False,
            "individual_fidelity_identified":False,
            "hydrological_causality_identified":False,
            "social_attraction_identified":False,
            "unique_lower_level_mechanism_identified":False
        }
    }
    Path(args.output).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
