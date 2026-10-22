#!/usr/bin/env python3
"""Post-hoc macroecological network test (not a plant causal inference).

Existing NAAMP 2001-2015 + NWI 250m species PEM response estimates and exact
fixed-margin route-crossfitted weighted-null frog acoustic pair residuals.
Tests vegetation niche divergence on residual pair co-calling across 57 strong
(or 110 any-call) fitted taxon pairs; permutes plant-slope labels across taxa.
A pair is NOT an independent observation for a naive row-wise t-test.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from collections import Counter, defaultdict
from pathlib import Path
import numpy as np

THRESHOLDS={"min_active_runs":80,"min_positive_strong_sites":120,
            "min_routes":25,"min_within_PEM_variation_runs":30}
STRONG_PAIR_EXPECTED=57
ANY_PAIR_EXPECTED=110
PRIMARY_REPS=9999
GENUS_REPS=3999
SLOPE_SE_REPS=500
PRIMARY_SEED=2601023

def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))

def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def eligibility(data):
    if data.get("analysis")!="naamp_nwi_taxon_specific_aquatic_vegetation_v0_1":
        raise ValueError("Wrong source of original taxon slope estimates")
    if data.get("thresholds")!=THRESHOLDS:
        raise ValueError("Historical taxa eligibility threshold mismatch")
    all_taxa={}
    for x in data["all_taxa"]:
        if x["taxon"] in all_taxa:
            raise ValueError("Duplicate taxon identity")
        all_taxa[x["taxon"]]=x
    eligible={}
    for name,x in all_taxa.items():
        strong=x.get("primary_strong",{})
        if (strong.get("status")=="fitted" and
            x.get("active_runs",0)>=THRESHOLDS["min_active_runs"] and
            x.get("positive_strong_sites",0)>=THRESHOLDS["min_positive_strong_sites"] and
            x.get("routes",0)>=THRESHOLDS["min_routes"] and
            x.get("runs_with_PEM_variation",0)>=THRESHOLDS["min_within_PEM_variation_runs"]):
            beta=float(strong["pem_beta_per_10pp"])
            se=float(strong["se_route_cluster"])
            if not math.isfinite(beta) or not math.isfinite(se) or se<0:
                raise ValueError("Non-finite taxon slope or standard error")
            eligible[name]={"beta":beta,"se":se,"active_runs":x["active_runs"],
                            "routes":x["routes"],
                            "genus":name.split(" ",1)[0],
                            "composite_unit":("complex" in name.lower()),
                            "primary_BH_q":x.get("primary_BH_q")}
    if len(eligible)!=25:
        raise ValueError(f"Frozen primary plant niche 25 taxa expected, got {len(eligible)}")
    return eligible

def pair_rows(network, plant, mode):
    if network.get("analysis")!="naamp_nwi_pair_identity_acoustic_network_v0_1":
        raise ValueError("Wrong pairwise NWI macro network")
    rec=[]
    for p in network["modes"][mode]["all_pairs"]:
        if p.get("status")!="fitted" or p.get("estimate",{}).get("status")!="fitted":
            continue
        a,b=p["pair"]
        if a not in plant or b not in plant:
            continue
        if a==b:raise ValueError("Self pair in frog macro network")
        y=float(p["estimate"]["beta"])
        null=float(p["mean_null_pair_cov"])
        obs=float(p["mean_observed_pair_cov"])
        if not math.isfinite(y) or abs(obs-null-y)>1e-9:
            raise ValueError("Observed-minus-expected pair residual inconsistency")
        if not p.get("fold_deltas") or not all(x in p["fold_deltas"] for x in ("A","B")):
            raise ValueError("Missing frozen geographic fold results")
        d={"pair":[a,b],"label":p["pair_label"],"genus_same":int(plant[a]["genus"]==plant[b]["genus"]),
           "n_runs":int(p["n_runs"]),"n_routes":int(p["n_routes"]),
           "mean_null_pair_cov":null,"mean_observed_pair_cov":obs,
           "Y_pp":100*y,"fold_A_pp":100*float(p["fold_deltas"]["A"]),
           "fold_B_pp":100*float(p["fold_deltas"]["B"]),
           "frequency_disparity":abs(math.log(plant[a]["active_runs"]/plant[b]["active_runs"])),
           "signed_edge_supported":bool(p.get("signed_edge_supported")),
           "original_BH_q":p.get("BH_q"),"original_direction":p.get("direction")}
        if d["n_runs"]<1 or d["n_routes"]<1:
            raise ValueError("Inconsistent matched route sampling")
        rec.append(d)
    rec.sort(key=lambda x:x["label"])
    expected=STRONG_PAIR_EXPECTED if mode=="strong" else ANY_PAIR_EXPECTED
    if len(rec)!=expected:raise ValueError(f"Joined {mode} pair count drift {len(rec)} != {expected}")
    return rec

def design(rows, plant, slopes, subset=None):
    pids=list(range(len(rows))) if subset is None else subset
    kept=[rows[i] for i in pids]
    if len(kept)<12:raise ValueError("Insufficient network edges for this model")
    vals=np.asarray([
        [np.log1p(z["n_runs"]),z["mean_null_pair_cov"],
         z["genus_same"],z["frequency_disparity"]]
        for z in kept],dtype=float)
    if not np.isfinite(vals).all():raise ValueError("Covariate lacks a finite numeric value")
    mu=vals.mean(axis=0)
    sd=vals.std(axis=0)
    Z=(vals-mu)/np.where(sd>0,sd,1.)
    base=np.column_stack([np.ones(len(kept)),Z])
    return kept,base

def fit(kept,base,slopes,outcome="Y_pp",wtype=None):
    x=np.asarray([abs(slopes[z["pair"][0]]-slopes[z["pair"][1]])/0.1
                  for z in kept],dtype=float)
    y=np.asarray([z[outcome] for z in kept],dtype=float)
    M=np.column_stack([base[:,0],x,base[:,1:]])
    if wtype=="route_cap150":
        w=np.minimum(np.asarray([z["n_routes"] for z in kept],dtype=float),150)
    else:
        w=np.ones(len(kept))
    sw=np.sqrt(w)
    beta,residuals,rank,svals=np.linalg.lstsq(M*sw[:,None],y*sw,rcond=None)
    if rank<M.shape[1]:raise ValueError("Macro regression design not full rank")
    fitted=M@beta
    basebeta=np.linalg.lstsq(base*sw[:,None],y*sw,rcond=None)[0]
    sse_full=float(np.sum(w*(y-fitted)**2))
    sse_base=float(np.sum(w*(y-base@basebeta)**2))
    partial=1.-sse_full/sse_base if sse_base>0 else None
    return {"b_pp_per_0p1_PEM_slope_gap":float(beta[1]),
            "partial_R2_over_controls":None if partial is None else float(partial),
            "n_edges":len(kept),
            "x_niche_gap_mean":float(x.mean()),
            "x_niche_gap_sd":float(x.std()),
            "y_co_detection_residual_pp_mean":float(y.mean()),
            "y_co_detection_residual_pp_sd":float(y.std()),
            "fit_coefficients":{c:float(v) for c,v in zip(
                ("intercept","niche_divergence",
                 "z_log1p_pair_runs","z_expected_pair_co_detection",
                 "z_same_genus","z_taxon_active_run_disparity"),beta)}}

def permute(kept,base,alltaxa,plant,nrep,seed,by_genus=False,outcome="Y_pp"):
    original={name:plant[name]["beta"] for name in alltaxa}
    observed=fit(kept,base,original,outcome)["b_pp_per_0p1_PEM_slope_gap"]
    rng=np.random.default_rng(seed)
    vals=np.asarray([original[name] for name in alltaxa],float)
    genus_map=defaultdict(list)
    for i,name in enumerate(alltaxa):genus_map[plant[name]["genus"]].append(i)
    all_perms=np.empty(nrep,float)
    nontrivial=0
    for n in range(nrep):
        v=vals.copy()
        if by_genus:
            for indices in genus_map.values():
                if len(indices)>1:
                    ix=np.array(indices,dtype=int)
                    v[ix]=v[ix][rng.permutation(len(ix))]
        else:v=v[rng.permutation(len(v))]
        if not np.array_equal(v,vals):nontrivial+=1
        vdict={k:float(x) for k,x in zip(alltaxa,v)}
        all_perms[n]=fit(kept,base,vdict,outcome)["b_pp_per_0p1_PEM_slope_gap"]
    if nontrivial<.75*nrep:raise ValueError("Insufficient effective permutation support")
    # Directional hypothesis is NEGATIVE (greater divergence = more segregation).
    nleft=int(np.count_nonzero(all_perms<=observed+1e-12))
    ntwo=int(np.count_nonzero(np.abs(all_perms)>=abs(observed)-1e-12))
    return {"observed_b_pp_per_0p1_gap":observed,
            "one_sided_negative_p":(1+nleft)/(nrep+1),
            "two_sided_absolute_p":(1+ntwo)/(nrep+1),
            "permutations":nrep,"nontrivial_assignments":nontrivial,
            "null_quantiles_2p5_50_97p5":[float(x) for x in np.quantile(all_perms,[.025,.5,.975])],
            "null_mean":float(all_perms.mean()),"null_sd":float(all_perms.std())}

def node_loo(kept,slopes):
    out=[]
    taxa=sorted(set(t for row in kept for t in row["pair"]))
    for name in taxa:
        sub=[z for z in kept if name not in z["pair"]]
        if len(sub)<15:
            out.append({"omitted_taxon":name,"n_edges":len(sub),"status":"underpowered"})
            continue
        _,base=design(sub,{},slopes)
        value=fit(sub,base,slopes)["b_pp_per_0p1_PEM_slope_gap"]
        out.append({"omitted_taxon":name,"n_edges":len(sub),"beta":value,"status":"fitted"})
    fits=[x["beta"] for x in out if x["status"]=="fitted"]
    return {"outcomes":out,"valid":len(fits),
            "negative":sum(x<0 for x in fits),
            "negative_fraction":sum(x<0 for x in fits)/len(fits) if fits else None,
            "beta_min":min(fits) if fits else None,
            "beta_max":max(fits) if fits else None}

def noise_sensitivity(kept,base,plant,alltaxa,seed,nrep=SLOPE_SE_REPS):
    rng=np.random.default_rng(seed)
    vals=[]
    for _ in range(nrep):
        d={name:float(rng.normal(plant[name]["beta"],plant[name]["se"])) for name in alltaxa}
        vals.append(fit(kept,base,d)["b_pp_per_0p1_PEM_slope_gap"])
    return {"draws":nrep,"normal_SE_approximation_not_biological_resampling":True,
            "negative_fraction":sum(x<0 for x in vals)/nrep,
            "median":float(np.median(vals)),
            "quantiles_2p5_97p5":[float(x) for x in np.quantile(vals,[.025,.975])]}

def quantile_descriptive(kept,slopes):
    rows=[{"x":abs(slopes[r["pair"][0]]-slopes[r["pair"][1]])/0.1,**r} for r in kept]
    rows.sort(key=lambda z:(z["x"],z["label"]))
    ans=[]
    for j in range(3):
        sub=rows[(j*len(rows))//3:((j+1)*len(rows))//3]
        ans.append({"tertile":j+1,"pair_count":len(sub),"mean_gap_0p1_units":float(np.mean([z["x"] for z in sub])),
                    "mean_pair_residual_pp":float(np.mean([z["Y_pp"] for z in sub])),
                    "fraction_negative_residual":sum(z["Y_pp"]<0 for z in sub)/len(sub),
                    "original_BH_supported_pairs":sum(z["signed_edge_supported"] for z in sub)})
    return ans

def mode_model(rows,plant,alltaxa,mode):
    kept,base=design(rows,plant,{name:plant[name]["beta"] for name in alltaxa})
    vals={name:plant[name]["beta"] for name in alltaxa}
    results={"n_pairs":len(kept),"n_nodes":len(set(x for z in kept for x in z["pair"])),
             "preexisting_BH_signed_edges":sum(z["signed_edge_supported"] for z in kept),
             "statistic":fit(kept,base,vals),
             "node_label_permutation":permute(kept,base,alltaxa,plant,PRIMARY_REPS,PRIMARY_SEED if mode=="strong" else PRIMARY_SEED+1)}
    if mode=="strong":
        results.update({
            "within_genus_permutation":permute(kept,base,alltaxa,plant,GENUS_REPS,PRIMARY_SEED+3,by_genus=True),
            "weighted_route_count_sensitivity":fit(kept,base,vals,wtype="route_cap150"),
            "fold_A_sensitivity":fit(kept,base,vals,outcome="fold_A_pp"),
            "fold_B_sensitivity":fit(kept,base,vals,outcome="fold_B_pp"),
            "leave_one_taxon_out":node_loo(kept,vals),
            "slope_measurement_error_sensitivity":noise_sensitivity(kept,base,plant,alltaxa,PRIMARY_SEED+4),
            "niche_divergence_tertiles":quantile_descriptive(kept,vals)
        })
        no_composite=[z for z in kept if not any(plant[n]["composite_unit"] for n in z["pair"])]
        _,b2=design(no_composite,plant,vals)
        results["exclude_composite_taxa"]={"n_pairs":len(no_composite),
                                          "n_nodes":len(set(n for z in no_composite for n in z["pair"])),
                                          "fit":fit(no_composite,b2,vals)}
        test=results
        macro_neg=results["statistic"]["b_pp_per_0p1_PEM_slope_gap"]<0
        foldsneg=(results["fold_A_sensitivity"]["b_pp_per_0p1_PEM_slope_gap"]<0 and
                  results["fold_B_sensitivity"]["b_pp_per_0p1_PEM_slope_gap"]<0)
        results["macro_classification"]=(
            "supported_nodal_exploratory_macro_pattern" if macro_neg and foldsneg and
            results["node_label_permutation"]["one_sided_negative_p"]<.05 and
            results["within_genus_permutation"]["one_sided_negative_p"]<.05 and
            results["leave_one_taxon_out"]["negative_fraction"]>=.75
            else "nonconfirmatory_descriptive")
        results["decision_inputs"]={"direction_negative":macro_neg,
                                    "both_geo_folds_negative":foldsneg,
                                    "node_perm_below_0p05":results["node_label_permutation"]["one_sided_negative_p"]<.05,
                                    "within_genus_perm_below_0p05":results["within_genus_permutation"]["one_sided_negative_p"]<.05,
                                    "LOTO_negative_at_least_0p75":results["leave_one_taxon_out"]["negative_fraction"]>=.75}
    return results

def synthetic_qa():
    # A true slope effect is recovered in OLS after including nuisance covariates.
    plant={str(i):{"beta":i/100., "genus":str(i%5), "active_runs":100}
           for i in range(12)}
    rows=[]
    for i in range(12):
        for j in range(i+1,12):
            rows.append({"pair":[str(i),str(j)],"label":str(i)+"x"+str(j),
                         "n_runs":50+i+j,"n_routes":25+i+j,
                         "mean_null_pair_cov":.1+.001*(i+j),
                         "genus_same":int(i%5==j%5),
                         "frequency_disparity":0.,"Y_pp":-3*abs(i-j)/10.,
                         "fold_A_pp":-3*abs(i-j)/10.,
                         "fold_B_pp":-3*abs(i-j)/10.,
                         "signed_edge_supported":False})
    a,b=design(rows,plant,{k:v["beta"] for k,v in plant.items()})
    estimate=fit(a,b,{k:v["beta"] for k,v in plant.items()})
    if abs(estimate["b_pp_per_0p1_PEM_slope_gap"]+3)>1e-7:
        raise AssertionError("Synthetic partial coefficient recovery failed")
    return {"status":"PASS","known_negative_beta_recovery":estimate["b_pp_per_0p1_PEM_slope_gap"]}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--plant",type=Path,required=True)
    p.add_argument("--pairs",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    pl=read_json(a.plant)
    net=read_json(a.pairs)
    plant=eligibility(pl)
    alltaxa=sorted(plant)
    QA=synthetic_qa()
    rows_strong=pair_rows(net,plant,"strong")
    rows_any=pair_rows(net,plant,"any")
    strong=mode_model(rows_strong,plant,alltaxa,"strong")
    anycall=mode_model(rows_any,plant,alltaxa,"any")
    out={
        "analysis":"NAAMP_250m_mapped_PEM_niche_divergence_vs_pair_co_calling_macro_network",
        "status":"EXECUTED_posthoc_macro_NAAMP_empirical_analysis",
        "date":"2026-10-23",
        "protocol":"exploration/NAAMP_MACRO_NICHE_NETWORK_FROZEN_SPEC_2026_10_23.md",
        "input_sha256":{str(a.plant.name):sha256(a.plant),str(a.pairs.name):sha256(a.pairs)},
        "original_NAAMP_surveys_NWI_complete":6236,
        "n_vegetation_slope_eligible_taxa":len(plant),
        "taxon_names":alltaxa,
        "synthetic_QA":QA,
        "strong_primary":strong,
        "any_secondary":anycall,
        "ecological_limits":{
            "plant_source_NWI_not_contemporaneous":True,
            "first_order_NWI_weighted_fixed_margin_null":True,
            "node_permutation_requires_exchangeable_taxon_labels":True,
            "phylogenetic_independence_not_guaranteed":True,
            "pairwise_edges_not_independent_units":True,
            "NAAMP_acoustic_sites_sequential_not_simultaneous":True,
            "observational_plant_causal_effect_proven":False,
            "biotic_interactions_demonstrated":False,
            "fish_insect_path_measured":False,
            "higher_order_three_species_causality_identified":False,
            "RC6_main_or_SI_modified":False}}
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(out,sort_keys=True,indent=2,allow_nan=False)+"\n",encoding="utf-8")
    print("MACRO_NICHE_NETWORK_RESULT_BEGIN")
    print(json.dumps({"status":out["status"],"n_taxa":len(plant),
                      "strong":{k:v for k,v in strong.items() if k in ("n_pairs","n_nodes","statistic","node_label_permutation","within_genus_permutation","macro_classification","niche_divergence_tertiles","decision_inputs","weighted_route_count_sensitivity","fold_A_sensitivity","fold_B_sensitivity")},
                      "any":{k:v for k,v in anycall.items() if k in ("n_pairs","n_nodes","statistic","node_label_permutation")},
                      "synthetic_QA":QA},sort_keys=True))
    print("MACRO_NICHE_NETWORK_RESULT_END")

if __name__=="__main__":
    main()
