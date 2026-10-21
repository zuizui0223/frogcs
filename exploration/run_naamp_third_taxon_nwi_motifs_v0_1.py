#!/usr/bin/env python3
"""Non-causal third-species co-calling geometry against route-held-out NWI null.

Not a genuine three-body interaction test: nonzero centered third moments can
result from pairwise associations and unmeasured microhabitat. Separate from RC6.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import itertools
import json
import math
import random
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.stats.multitest import multipletests

ROOT=Path(__file__).resolve().parents[1]
B=199
BURN=40
THIN=8
SEED=2840279
Q=1.959963984540054
CACHE={}

def mod(path,label):
    spec=importlib.util.spec_from_file_location(label,path)
    o=importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(o)
    return o

prior=mod(ROOT/"exploration/run_naamp_nwi_conditional_checkerboard_v0_1.py",
          "nwi_prev_weighted")
NAMES=("pair_sq","triad_sq","pem_triad_sq")

def index_combos(n):
    if n not in CACHE:
        pairs=np.asarray(list(itertools.combinations(range(n),2)),dtype=int)
        triads=np.asarray(list(itertools.combinations(range(n),3)),dtype=int)
        CACHE[n]=(pairs,triads)
    return CACHE[n]

def moments(rows,pem):
    n=len(rows)
    if n<3:raise ValueError("Need 3 taxon units for the third-order moment")
    array=np.zeros((n,10),dtype=float)
    for i,sites in enumerate(rows):
        array[i,list(sites)]=1.
    centered=array-array.mean(axis=1,keepdims=True)
    pairs,triads=index_combos(n)
    pair_product=centered[pairs[:,0]]*centered[pairs[:,1]]
    pair_moment=pair_product.mean(axis=1)
    tri_product=centered[triads[:,0]]*centered[triads[:,1]]*centered[triads[:,2]]
    third=tri_product.mean(axis=1)
    demeaned=np.asarray(pem,float)-float(np.mean(pem))
    localized=(tri_product@demeaned)/10.
    pair_sq=float(np.mean(pair_moment**2))
    triad_sq=float(np.mean(third**2))
    pem_triad_sq=float(np.mean(localized**2))
    per_taxon=np.zeros(n,float)
    triple_sq=third**2
    for col in range(3):
        np.add.at(per_taxon,triads[:,col],triple_sq)
    per_taxon/=math.comb(n-1,2)
    return {"pair_sq":pair_sq,"triad_sq":triad_sq,
            "pem_triad_sq":pem_triad_sq},per_taxon

def synthetic_qa():
    rng=random.Random(2840278)
    rows=[{0,1,2},{1,3,4},{2,3,5},{0,6,7},{4,7,8},{5,8,9}]
    margin=prior.fixed_margins(rows)
    pem=np.asarray([.00,.10,.25,.00,.17,.04,.20,.06,.13,.0])
    v=[]
    for j in range(450):
        prior.weighted_trade(rows,np.zeros((len(rows),10)),rng)
        if j%10==0:
            assert prior.fixed_margins(rows)==margin
            v.append(moments(rows,pem)[0]["triad_sq"])
    assert max(v)-min(v)>1e-8,"Third-order statistic invariant despite nontrivial fixed margins"
    # A stop-column-only triplet count is invariant: rejected as trivial.
    colsum=margin[1]
    col_triples=sum(math.comb(x,3) if x>=3 else 0 for x in colsum)
    assert col_triples==sum(math.comb(x,3) if x>=3 else 0
                            for x in prior.fixed_margins(rows)[1])
    test_moments,role=moments(rows,pem)
    assert role.shape==(len(rows),) and all(x>=0 for x in role)
    return {"status":"PASS","fixed_fixed_margins":"PASS",
            "nontrivial_third_moment":"PASS",
            "column_richness_only_triples_invariant":"PASS"}

def json_convert(x):
    if isinstance(x,np.generic):return x.item()
    if isinstance(x,np.ndarray):return x.tolist()
    raise TypeError(type(x).__name__)

def load_frozen_inputs(source_dir,coef_dir):
    runs,scope=prior.load_run_context()
    name_to_file={"any":"any_train_coefficients.json",
                  "strong":"strong_train_coefficients.json"}
    refs={}
    coefs={}
    for mode in name_to_file:
        reference=Path(source_dir)/(mode+"_heldout_run_diagnostics.csv")
        if not reference.is_file():raise RuntimeError(f"missing frozen {reference}")
        df=pd.read_csv(reference,dtype={"RunID":str})
        if df.RunID.duplicated().any():raise RuntimeError("Duplicated prior heldout run ID")
        frozen=Path(coef_dir)/name_to_file[mode]
        if not frozen.is_file():raise RuntimeError("Missing frozen cross-fit coefficients: "+str(frozen))
        dd=json.loads(frozen.read_text())
        if set(dd)!={"A","B"}:raise RuntimeError("Frozen route folds absent")
        coefs[mode]={
          fold:{sp:{name:np.asarray(vals,dtype=float)
                     for name,vals in item.items()}
                     for sp,item in panel.items()}
          for fold,panel in dd.items()}
        refs[mode]=df.set_index("RunID")
    return runs,refs,coefs,scope

def ols_cluster(values,routes):
    arr=np.asarray(values,dtype=float)
    g=np.asarray(routes,dtype=str)
    if len(arr)<30 or len(set(g))<10:
        return {"status":"insufficient"}
    fit=sm.OLS(arr,np.ones((len(arr),1))).fit(
        cov_type="cluster",cov_kwds={"groups":g})
    b=float(fit.params[0]);se=float(fit.bse[0])
    return {"status":"fitted","delta":b,"se_route":se,
            "ci95":[b-Q*se,b+Q*se],
            "p_two_sided":float(fit.pvalues[0]),
            "n_runs":len(arr),"n_routes":len(set(g))}

def run_mode(mode,runs,ref,coef,output_dir):
    ids=sorted(set(runs)&set(ref.index.astype(str)))
    assert len(ids)>=500 and len({runs[x]["route"] for x in ids})>=100
    total={stat:np.zeros(B,float) for stat in NAMES}
    role_records=defaultdict(list)
    run_records=[]
    no_variation=0
    low_accept=0
    for rid_index,rid in enumerate(ids,1):
        r=runs[rid]
        taxa,rows=prior.ref_rows(r,mode)
        if len(taxa)<3 or not prior.exchangeable(rows):
            raise RuntimeError("Prior source contains a nonexchangeable or too-small matrix")
        expected_c=float(ref.loc[rid,"observed"])
        actual_c=prior.cscore(rows)
        if not np.isclose(expected_c,actual_c,atol=1e-8,rtol=0):
            raise RuntimeError("Frozen observed C-score or row sample drift "+rid)
        pem=np.asarray(r["v"][:,1],dtype=float)/10.
        obs,role_obs=moments(rows,pem)
        beta=coef[prior.complementary(r["fold"])]
        scores=np.stack([
            np.asarray(beta.get(t,{}).get("wetland_and_emergent",np.zeros(2)),float)
            for t in taxa])@r["v"][:,[0,1]].T
        seedstr=f"{SEED}|{mode}|{rid}"
        seed=int.from_bytes(hashlib.sha256(seedstr.encode()).digest()[:8],"big")
        rng=random.Random(seed)
        state=[set(s) for s in rows]
        fixed=prior.fixed_margins(state)
        feasible=accepted=0
        for z in range(BURN*len(taxa)):
            f,a=prior.weighted_trade(state,scores,rng)
            feasible+=f;accepted+=a
        sim={name:np.zeros(B,float) for name in NAMES}
        simrole=np.zeros(len(taxa),float)
        for b in range(B):
            for z in range(THIN*len(taxa)):
                f,a=prior.weighted_trade(state,scores,rng)
                feasible+=f;accepted+=a
            z,role=moments(state,pem)
            for name in NAMES:
                sim[name][b]=z[name]
            simrole+=role
            if b in (0,B//2,B-1) and prior.fixed_margins(state)!=fixed:
                raise RuntimeError("NWI-weighted null moved fixed row or column margins")
        if feasible<15 or accepted==0:
            low_accept+=1
        expected={name:float(sim[name].mean()) for name in NAMES}
        null_role=simrole/B
        varying=bool(np.ptp(sim["triad_sq"])>1e-13)
        no_variation+=int(not varying)
        record={"RunID":rid,"route":r["route"],"fold":r["fold"],
                "n_taxa":len(taxa),"PEM_heterogeneity":float(np.ptp(pem)),
                "triad_null_varies":varying,
                "accepted_fraction":accepted/feasible if feasible else 0}
        for name in NAMES:
            record["observed_"+name]=obs[name]
            record["null_"+name]=expected[name]
            record["excess_"+name]=obs[name]-expected[name]
            total[name]+=sim[name]
        run_records.append(record)
        for k,sp in enumerate(taxa):
            role_records[sp].append({
                "route":r["route"],"fold":r["fold"],
                "observed":float(role_obs[k]),"null":float(null_role[k]),
                "excess":float(role_obs[k]-null_role[k]),
                "variable_run":varying
            })
        if rid_index%500==0:
            print(f"{mode}: {rid_index}/{len(ids)} third-taxon matrices completed",flush=True)
    data=pd.DataFrame(run_records)
    if data.RunID.duplicated().any():raise RuntimeError("duplicated matrix")
    region_n=int(data[data.triad_null_varies].route.nunique())
    informative_runs=int(data.triad_null_varies.sum())
    main_gate=informative_runs>=100 and region_n>=30
    null_info={}
    for name in NAMES:
        dist=total[name]/len(data)
        null_info[name]={
           "observed_mean":float(data["observed_"+name].mean()),
           "null_mean":float(dist.mean()),
           "mean_delta":float(data["excess_"+name].mean()),
           "null_ci95":[float(x) for x in np.quantile(dist,[.025,.975])],
           "upper_tail_mc_p":float((1+sum(dist>=data["observed_"+name].mean()))/(B+1)),
           "cluster_inference":ols_cluster(data["excess_"+name],data.route),
           "folds":{str(f):{
              "n_runs":len(d),"n_routes":int(d.route.nunique()),
              "excess":float(d["excess_"+name].mean())}
              for f,d in data.groupby("fold")}
        }
    roles=[]
    for sp,entries in sorted(role_records.items()):
        rr=pd.DataFrame(entries)
        nroute=int(rr.route.nunique())
        vary=int(rr.variable_run.sum())
        row={"taxon":sp,"n_runs":len(rr),"n_routes":nroute,
             "variable_triad_runs":vary}
        if len(rr)<80 or nroute<25 or vary<20:
            row["status"]="ineligible"
        else:
            fit=ols_cluster(rr.excess,rr.route)
            row.update({"status":"fitted","stat":fit,
                        "mean_observed_role":float(rr.observed.mean()),
                        "mean_expected_role":float(rr.null.mean()),
                        "fold_deltas":{
                            str(f):float(d.excess.mean())
                            for f,d in rr.groupby("fold")}})
        roles.append(row)
    eligible=[a for a in roles if a["status"]=="fitted"]
    if eligible:
        q=multipletests([a["stat"]["p_two_sided"] for a in eligible],
                        method="fdr_bh")[1]
        for a,value in zip(eligible,q):
            a["BH_q"]=float(value)
            a["positive_hub_candidate"]=bool(
                a["stat"]["ci95"][0]>0 and
                a["fold_deltas"].get("A",0)>0 and
                a["fold_deltas"].get("B",0)>0 and value<.05)
    classification={
        "T3_identifiable":main_gate,
        "centered_triplet_excess_over_crossfit_NWI":bool(
            main_gate and null_info["triad_sq"]["cluster_inference"]["ci95"][0]>0
            and null_info["triad_sq"]["upper_tail_mc_p"]<.05),
        "plant_localized_triple_excess":bool(
            main_gate and null_info["pem_triad_sq"]["cluster_inference"]["ci95"][0]>0
            and null_info["pem_triad_sq"]["upper_tail_mc_p"]<.05),
        "causal_irreducible_three_body_interaction_supported":False
    }
    output={
       "mode":mode,
       "coverage":{
          "n_runs":len(data),"n_routes":int(data.route.nunique()),
          "n_runs_with_variable_null_T3":informative_runs,
          "routes_with_variable_null_T3":region_n,
          "n_runs_with_null_T3_invariant":no_variation,
          "n_runs_with_no_successful_trade":low_accept,
          "n_runs_with_PEM_heterogeneity":int((data.PEM_heterogeneity>0).sum()),
          "sample_from_prior_exact_Cscore_NWI":True},
       "global_motifs":null_info,
       "taxon_roles":{
         "min_counts":{"runs":80,"routes":25,"variable_null_runs":20},
         "eligible_taxon_units":len(eligible),
         "candidate_hub_taxa":[{key:a[key] for key in
                  ("taxon","n_runs","n_routes","stat","fold_deltas","BH_q")}
                  for a in eligible if a.get("positive_hub_candidate")],
         "all_taxon_units":roles
       },
       "classification":classification,
       "notes":[
         "Third centered moment is a three-taxon pattern, NOT proof of an irreducible three-way biological interaction.",
         "T2 departure is separately reported. Pairwise interactions can induce T3 departures even when pairwise terms are subtracted algebraically.",
         "NWI habitat context is not temporally synchronized with NAAMP survey nights.",
         "Sequential listening stops do not demonstrate simultaneous chorus interactions."]
    }
    data.to_csv(output_dir/f"{mode}_triplet_by_run.csv",index=False)
    print("MOTIF_MODE_COMPLETE",mode,json.dumps({
       "n_runs":len(data),"n_routes":output["coverage"]["n_routes"],
       "T3_delta":null_info["triad_sq"]["mean_delta"],
       "T3_p":null_info["triad_sq"]["upper_tail_mc_p"],
       "T3_PEM_delta":null_info["pem_triad_sq"]["mean_delta"],
       "taxa_with_role":len(eligible),
       "candidate_taxa":[x["taxon"] for x in output["taxon_roles"]["candidate_hub_taxa"]]
    }),flush=True)
    return output

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--frozen-outputs",type=Path)
    parser.add_argument("--frozen-coefficients",type=Path)
    parser.add_argument("--outdir",type=Path,default=ROOT/"build"/"naamp_third_taxon_plant")
    parser.add_argument("--synthetic-only",action="store_true")
    args=parser.parse_args()
    qa=synthetic_qa()
    print("THIRD_TAXON_QA",json.dumps(qa),flush=True)
    if args.synthetic_only:return
    if not(args.frozen_outputs and args.frozen_coefficients):
        raise RuntimeError("Frozen previous run-level diagnostic and NWI coefficients required")
    args.outdir.mkdir(parents=True,exist_ok=True)
    runs,refs,coeff,scope=load_frozen_inputs(
        args.frozen_outputs,args.frozen_coefficients)
    result={
      "analysis":"naamp_nwi_three_taxon_acoustic_motifs_v0_1",
      "status":"new_posthoc_exploratory_not_RC6",
      "contract":"exploration/NAAMP_THIRD_TAXON_AQUATIC_PLANT_CONTRACT_2026_10_21.md",
      "source_prior_weighted_NWI_crossfit_run":39516056663,
      "source_original_fixed_fixed_run":39436588431,
      "source_geometric_NWI_overlay_run":39450277196,
      "source":scope,
      "sampling":{"B":B,"burn_in":BURN,"thin":THIN,
                  "weighted":True,"preserves_taxon_row_margins":True,
                  "preserves_site_richness":True,"seed":SEED,
                  "route_fold_coefficients_reused_without_refit":True},
      "synthetic_QA":qa,
      "modes":{},
      "causal_biotic_interactions_inferred":False,
      "genuine_irreducible_higher_order_interaction_inferred":False,
      "RC6_scientific_or_submission_package_changed":False
    }
    for mode in ("any","strong"):
        result["modes"][mode]=run_mode(
            mode,runs,refs[mode],coeff[mode],args.outdir)
    (args.outdir/"result.json").write_text(
        json.dumps(result,indent=2,sort_keys=True,default=json_convert)+"\n")
    print("THIRD_TAXON_PLANT_RESULT_BEGIN",flush=True)
    print(json.dumps(result,sort_keys=True,default=json_convert),flush=True)
    print("THIRD_TAXON_PLANT_RESULT_END",flush=True)
if __name__=="__main__":
    main()
