#!/usr/bin/env python3
"""Pairwise frog co-calling associations after cross-fitted NWI PEM filtering.

Observational network edges are not causal interactions, attraction or competition.
Species complexes remain in null matrix margins but not candidate pair inference.
"""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
import math
import random
from collections import Counter,defaultdict
from pathlib import Path
import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.stats.multitest import multipletests

ROOT=Path(__file__).resolve().parents[1]
B=199
SEED=2840287
BURN=40
THIN=8
Q=1.959963984540054
PRIOR_FIVE={
"Hyla versicolor","Lithobates clamitans","Lithobates sylvaticus",
"Pseudacris crucifer","Pseudacris maculata/triseriata complex"}

def loadmod(label,path):
    spec=importlib.util.spec_from_file_location(label,path)
    o=importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(o)
    return o

prior=loadmod("frozen_habitat_null",ROOT/"exploration/run_naamp_nwi_conditional_checkerboard_v0_1.py")

def cov_matrix(rows):
    n=len(rows)
    arr=np.zeros((n,10),float)
    for i,ss in enumerate(rows):
        arr[i,list(ss)]=1.
    k=arr.sum(axis=1)/10.
    return (arr@arr.T)/10.-np.outer(k,k)

def rank_p(data):
    y=data.delta.to_numpy(float)
    if len(data)<60 or data.route.nunique()<20:
        return {"status":"insufficient"}
    model=sm.OLS(y,np.ones((len(data),1))).fit(
        cov_type="cluster",cov_kwds={"groups":data.route.astype(str)})
    b=float(model.params[0])
    se=float(model.bse[0])
    return {"status":"fitted","beta":b,"route_se":se,
            "ci95":[b-Q*se,b+Q*se],
            "p_two_sided":float(model.pvalues[0])}

def is_resolved(sp):
    return "/" not in sp and " complex" not in sp.lower()

def qa():
    rows=[{0,1,2},{1,3},{2,3,4},{0,4}]
    margin=prior.fixed_margins(rows)
    first=cov_matrix(rows)
    assert np.allclose(first,first.T)
    assert np.allclose(np.diag(first),np.asarray([.3,.2,.3,.2])*(1-np.asarray([.3,.2,.3,.2])))
    rnd=random.Random(2840289)
    variability=[]
    for i in range(300):
        prior.weighted_trade(rows,np.zeros((len(rows),10)),rnd)
        assert prior.fixed_margins(rows)==margin
        if i%5==0:
            variability.append(float(cov_matrix(rows)[0,1]))
    assert np.ptp(variability)>0,"Pair-specific overlap invariant even when fixed margins vary"
    # Because stop richness and row totals are fixed, the *sum* of pairwise
    # covariances over all taxa is fixed; never test that trivial summary.
    assert np.allclose(sum(cov_matrix(rows)[i,j]
                           for i in range(len(rows)) for j in range(i+1,len(rows))),
                       sum(first[i,j] for i in range(len(rows)) for j in range(i+1,len(rows))))
    return {"status":"PASS","margin_conservation":"PASS",
            "taxon_pair_covariance_nontrivial":"PASS",
            "total_pair_covariance_invariant_under_fixed_margins":"PASS"}

def analyze_mode(mode,records,reference,fold_coefs,outdir):
    ref=reference.copy()
    if ref.RunID.duplicated().any():raise RuntimeError("Previous NWI run-level evidence contains duplicate RunIDs")
    ref=ref.set_index("RunID")
    common=sorted(set(records)&set(ref.index.astype(str)))
    pairs=defaultdict(list)
    incomplete=0
    low_mix=0
    all_run_records=[]
    for index,rid in enumerate(common,1):
        item=records[rid]
        tax,rows=prior.ref_rows(item,mode)
        n=len(tax)
        observed_c=prior.cscore(rows)
        if not np.isclose(observed_c,float(ref.loc[rid,"observed"]),atol=1e-8,rtol=0):
            raise RuntimeError("Original C-score and matrix identity mismatched: "+rid)
        m=prior.fixed_margins(rows)
        train=fold_coefs[prior.complementary(item["fold"])]
        beta=np.stack([
            np.asarray(train.get(sp,{}).get("wetland_and_emergent",np.zeros(2)),float)
            for sp in tax])
        score=beta@item["v"][:,[0,1]].T
        data=[set(x) for x in rows]
        seed=int.from_bytes(hashlib.sha256(f"{SEED}|{mode}|{rid}".encode()).digest()[:8],"big")
        rng=random.Random(seed)
        attempts=accepted=0
        for _ in range(BURN*n):
            f,a=prior.weighted_trade(data,score,rng);attempts+=f;accepted+=a
        mat_obs=cov_matrix(rows)
        null_sum=np.zeros((n,n),float)
        null_sq=np.zeros((n,n),float)
        for b in range(B):
            for _ in range(THIN*n):
                f,a=prior.weighted_trade(data,score,rng);attempts+=f;accepted+=a
            mat=cov_matrix(data)
            null_sum+=mat
            null_sq+=mat**2
            if b in (0,B//2,B-1) and prior.fixed_margins(data)!=m:
                raise RuntimeError("Pairwise null changed fixed margins")
        if attempts<10 or accepted==0:low_mix+=1
        null_mean=null_sum/B
        null_var=np.maximum(null_sq/B-null_mean**2,0.)
        kept=0
        variable=0
        for i in range(n):
            if not is_resolved(tax[i]):continue
            for j in range(i+1,n):
                if not is_resolved(tax[j]):continue
                var=bool(null_var[i,j]>1e-14)
                variable+=int(var)
                pair=f"{tax[i]} || {tax[j]}"
                pairs[pair].append({
                   "route":item["route"],"fold":item["fold"],
                   "observed":float(mat_obs[i,j]),
                   "null":float(null_mean[i,j]),
                   "delta":float(mat_obs[i,j]-null_mean[i,j]),
                   "varies":var
                })
                kept+=1
        all_run_records.append({
            "RunID":rid,"route":item["route"],"fold":item["fold"],
            "n_resolved_pairs":kept,
            "n_pairwise_variable_under_null":variable,
            "null_move_acceptance":accepted/attempts if attempts else 0})
        if index%550==0:
            print(f"{mode}: pair-identity null complete {index}/{len(common)}",flush=True)
    if len(all_run_records)<500:raise RuntimeError("Too few original NWI matrices")
    summary=[]
    for key,values in sorted(pairs.items()):
        g=pd.DataFrame(values)
        n=int(len(g)); n_routes=int(g.route.nunique())
        v=int(g.varies.sum())
        taxa=key.split(" || ")
        row={"pair":taxa,"pair_label":key,"n_runs":n,"n_routes":n_routes,"n_variable_null_runs":v}
        if n<60 or n_routes<20 or v<15:
            row["status"]="ineligible"
        else:
            fit=rank_p(g)
            row.update({"status":"fitted","estimate":fit,
                        "mean_observed_pair_cov":float(g.observed.mean()),
                        "mean_null_pair_cov":float(g.null.mean()),
                        "fold_deltas":{str(x):float(d.delta.mean()) for x,d in g.groupby("fold")},
                        "n_in_PEM_BH_taxa":sum(x in PRIOR_FIVE for x in taxa)})
        summary.append(row)
    test=[x for x in summary if x["status"]=="fitted"]
    if test:
        qs=multipletests([x["estimate"]["p_two_sided"] for x in test],method="fdr_bh")[1]
        for x,q in zip(test,qs):
            x["BH_q"]=float(q)
            lo,hi=x["estimate"]["ci95"]
            crossfold=x["fold_deltas"].get("A",0)*x["fold_deltas"].get("B",0)>0
            x["signed_edge_supported"]=bool(q<.05 and (lo>0 or hi<0) and crossfold)
            x["direction"]="aggregated_same_stop" if x["estimate"]["beta"]>0 else "segregated_different_stop"
    supported=[x for x in test if x.get("signed_edge_supported")]
    degree=Counter()
    for row in supported:
        degree[row["pair"][0]]+=1
        degree[row["pair"][1]]+=1
    accepted_edges=[
      {"species_a":z["pair"][0],"species_b":z["pair"][1],
       "direction":z["direction"],"delta":z["estimate"]["beta"],
       "route_ci95":z["estimate"]["ci95"],"q":z["BH_q"],
       "route_fold_deltas":z["fold_deltas"],"n_runs":z["n_runs"],
       "n_routes":z["n_routes"],"n_plant_BH_species":z["n_in_PEM_BH_taxa"]}
      for z in sorted(supported,key=lambda x:x["BH_q"])
    ]
    summary_out={
      "mode":mode,
      "null_source":"route-crossfit NWI wetland+PEM fixed-margin weighted Curveball",
      "coverage":{"original_test_runs":len(common),
                  "original_routes":len(set(x["route"] for x in all_run_records)),
                  "matrix_no_successful_trade":low_mix,
                  "all_unordered_species_pairs_with_positive_route_coactivation":len(summary),
                  "n_eligible_species_pairs":len(test),
                  "n_supported_edges":len(supported),
                  "positive_supported_edges":sum(x["estimate"]["beta"]>0 for x in supported),
                  "negative_supported_edges":sum(x["estimate"]["beta"]<0 for x in supported)},
      "thresholds":{"joint_positive_runs":60,"n_routes":20,
                    "null_dynamic_run_count":15,"BH_FDR_q":.05,
                    "route_fold_direction_agreement":True,
                    "only_unambiguous_species_names_for_pair_inference":True},
      "supported_edges":accepted_edges,
      "supported_node_degrees":sorted(
          [{"taxon":sp,"degree":n,"plant_BH_taxon_from_prior_study":sp in PRIOR_FIVE}
           for sp,n in degree.items()],key=lambda x:-x["degree"]),
      "all_pairs":summary,
      "interpretation":{"spatial_pairwise_association_not_direct_interaction":True,
                        "total_pairwise_covariance_invariant_under_fixed_margins":True,
                        "plant_positive_taxa_preselected_from_same_NAAMP_archive":True,
                        "RC6_untouched":True}
    }
    outdir.mkdir(parents=True,exist_ok=True)
    pd.DataFrame(all_run_records).to_csv(outdir/f"{mode}_pair_null_matrix_QA.csv",index=False)
    print("PAIR_NETWORK_MODE_COMPLETE",mode,json.dumps({
         "tested_pairs":len(test),"supported_edges":len(supported),
         "positive":summary_out["coverage"]["positive_supported_edges"],
         "negative":summary_out["coverage"]["negative_supported_edges"],
         "top_edges":accepted_edges[:8]
    }),flush=True)
    return summary_out

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--previous-nwi",type=Path)
    parser.add_argument("--outdir",type=Path,default=ROOT/"build"/"nwi_pair_network")
    parser.add_argument("--synthetic-only",action="store_true")
    args=parser.parse_args()
    test=qa()
    print("FROG_PAIR_NETWORK_QA",json.dumps(test),flush=True)
    if args.synthetic_only:return
    if args.previous_nwi is None:raise RuntimeError("Missing frozen previous NWI run and coefficient artifact")
    items,refs,coefs,coverage=prior_inputs(args.previous_nwi)
    result={"analysis":"naamp_nwi_pair_identity_acoustic_network_v0_1",
            "contract":"exploration/NAAMP_PLANT_CONDITIONED_FROG_PAIR_NETWORK_CONTRACT_2026_10_21.md",
            "status":"posthoc_exploratory_no_causal_interaction_inference",
            "source_frozen_NWI_train_and_run":39516056663,
            "source_NWI_GEOMETRY":39450277196,
            "synthetic_QA":test,
            "settings":{"simulations":B,"seed":SEED,"burn":BURN,"thin":THIN,
                        "opposite_route_fold_coefficient_reuse":True,
                        "sample_same_as_third_taxon_moment_result":True},
            "source_coverage":coverage,
            "modes":{},
            "inference_boundaries":{"biological_interaction_established":False,
                                    "network_directed":False,"third_species_causal_mediator_identified":False,
                                    "observational_same_stop_co_calling":True,
                                    "RC6_paper_changed":False}}
    for mode in ("any","strong"):
        result["modes"][mode]=analyze_mode(mode,items,refs[mode],coefs[mode],args.outdir)
    (args.outdir/"result.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("FROG_PLANT_PAIR_NETWORK_RESULT_BEGIN",flush=True)
    print(json.dumps(result,sort_keys=True),flush=True)
    print("FROG_PLANT_PAIR_NETWORK_RESULT_END",flush=True)

def prior_inputs(path):
    records,scope=prior.load_run_context()
    refs={}
    coef={}
    for mode in ("any","strong"):
        ref=pd.read_csv(path/f"{mode}_heldout_run_diagnostics.csv",
                        dtype={"RunID":str})
        if ref.RunID.duplicated().any():raise RuntimeError("Repeated old RunID")
        j=json.loads((path/f"{mode}_train_coefficients.json").read_text())
        assert set(j)=={"A","B"}
        coef[mode]={fold:{sp:{name:np.asarray(b,dtype=float)
                              for name,b in co.items()}
                             for sp,co in taxa.items()}
                    for fold,taxa in j.items()}
        refs[mode]=ref
    return records,refs,coef,scope

if __name__=="__main__":
    main()
