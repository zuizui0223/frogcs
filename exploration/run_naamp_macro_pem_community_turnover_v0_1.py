#!/usr/bin/env python3
"""Within-route-night acoustic frog community turnover across mapped NWI PEM.

FULL NAAMP+NWI linked records, all taxon units. No third-party raw files
redistributed. Primary endpoint is Sørensen dissimilarity between two
acoustically active listening stops, analyzed with run-fixed effects and
route-clustered uncertainty, not plant causality or frog-frog competition.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from scipy.stats import t as student_t

ROOT=Path(__file__).resolve().parents[1]
PREDICTORS=("different_mapped_PEM_overlap","stop_index_gap_div_9",
            "absolute_total_NWI_wetland_cover_gap_x10",
            "taxon_richness_gap","mean_pair_taxon_richness")

def module():
    path=ROOT/"exploration/run_naamp_nwi_conditional_checkerboard_v0_1.py"
    spec=importlib.util.spec_from_file_location("naamp_nwi_macro_turnover_source",path)
    m=importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(m)
    return m

def run_pairs(run,mode,matched_richness=False):
    pem=(run["v"][:,1]>0).astype(int)
    if not (2<=int(pem.sum())<=8):
        return None,"insufficient_PEM_and_nonPEM_station_coverage",0,0
    sets=[set() for _ in range(10)]
    for species,indices in run["activity"][mode].items():
        for i in indices:
            if i<0 or i>=10:raise ValueError("NAAMP site index outside full ten-stop route")
            sets[i].add(species)
    richness=[len(s) for s in sets]
    xs=[];ys=[]
    n_one_or_more=0;n_both_silent=0
    for i in range(10):
        for j in range(i+1,10):
            n1,n2=richness[i],richness[j]
            if n1==0 or n2==0:
                n_one_or_more+=int(bool(n1 or n2))
                n_both_silent+=int(not (n1 or n2))
                continue
            if matched_richness and abs(n1-n2)>1:
                continue
            shared=len(sets[i]&sets[j])
            d=1.-2.*shared/(n1+n2)
            if not 0.-1e-12<=d<=1.+1e-12:
                raise ValueError("Invalid station pair Sørensen")
            xs.append([float(pem[i]!=pem[j]),(j-i)/9.,
                       abs(float(run["v"][i,0]-run["v"][j,0])),
                       abs(n1-n2),(n1+n2)/2.])
            ys.append(d)
    if len(xs)<10:
        return None,"fewer_than_ten_both_active_station_pairs",n_one_or_more,n_both_silent
    X=np.asarray(xs,float)
    Y=np.asarray(ys,float)
    n_cross=int(np.count_nonzero(X[:,0]))
    if n_cross<2 or len(X)-n_cross<2:
        return None,"too_few_cross_or_same_PEM_station_pairs",n_one_or_more,n_both_silent
    if not np.isfinite(X).all() or not np.isfinite(Y).all():
        raise ValueError("Invalid numeric NAAMP turnover record")
    # Survey run fixed effect removes every shared 10-stop nightly covariate.
    Xm=X-X.mean(axis=0)
    Ym=Y-Y.mean()
    assert np.abs(Xm.mean(axis=0)).max()<1e-10
    assert abs(float(Ym.mean()))<1e-10
    return {"route":run["route"],"state":run["state"],"fold":run["fold"],
            "X":Xm,"Y":Ym,
            "raw_cross_count":n_cross,"raw_within_count":len(X)-n_cross,
            "raw_cross_sum":float(Y[X[:,0]==1].sum()),
            "raw_same_sum":float(Y[X[:,0]==0].sum()),
            "n_stations_both_active":int(sum(bool(r) for r in richness)),
            "n_observed_taxa":len(run["activity"][mode])},
            "ok",n_one_or_more,n_both_silent

def assemble(records,mode,matched_richness=False):
    groups=[]
    excluded=Counter()
    eligible=0
    n_one_or_more=0;n_both_silent=0
    pooled_taxa=set()
    for rid in sorted(records):
        run=records[rid]
        pem=(run["v"][:,1]>0).astype(int)
        if 2<=int(pem.sum())<=8:
            eligible+=1
        grp,reason,one,silent=run_pairs(run,mode,matched_richness)
        n_one_or_more+=one
        n_both_silent+=silent
        if grp is None:
            excluded[reason]+=1
            continue
        groups.append(grp)
        pooled_taxa.update(run["activity"][mode].keys())
    covered_routes=set(x["route"] for x in groups)
    covered_states=set(x["state"] for x in groups)
    coverage={"data_linked_ten_stop_runs":len(records),
              "mapped_PEM_contrast_runs_with_2plus_each":eligible,
              "complete_valid_runs":len(groups),
              "independent_routes":len(covered_routes),
              "states":len(covered_states),
              "taxon_units_on_valid_runs":len(pooled_taxa),
              "within_run_station_pair_records":int(sum(len(g["Y"]) for g in groups)),
              "raw_cross_sitepair_comparisons":int(sum(g["raw_cross_count"] for g in groups)),
              "raw_same_sitepair_comparisons":int(sum(g["raw_within_count"] for g in groups)),
              "one_active_one_silent_pairs_excluded":n_one_or_more,
              "both_silent_pairs_excluded":n_both_silent,
              "excluded_run_reasons":dict(excluded)}
    return groups,coverage

def regression(groups,route_equal=False,minimum_routes=30):
    if not groups:
        return {"status":"underpowered_no_eligible_survey_runs"}
    n=sum(len(g["Y"]) for g in groups)
    route_counts=Counter()
    route_to_groups=defaultdict(list)
    for g in groups:
        route_counts[g["route"]]+=len(g["Y"])
        route_to_groups[g["route"]].append(g)
    G=len(route_counts)
    if G<minimum_routes or n<250 or G<=len(PREDICTORS)+1:
        return {"status":"underpowered_route_gate","n_routes":G,"n_pairs":n}
    p=len(PREDICTORS)
    XX=np.zeros((p,p))
    XY=np.zeros(p)
    weighted_sum=0.
    crosssum=0.;samesum=0.;crossn=0;samen=0
    for g in groups:
        w=1./route_counts[g["route"]] if route_equal else 1.
        XX+=w*(g["X"].T @ g["X"])
        XY+=w*(g["X"].T @ g["Y"])
        weighted_sum+=w*len(g["Y"])
        crosssum+=g["raw_cross_sum"];samesum+=g["raw_same_sum"]
        crossn+=g["raw_cross_count"];samen+=g["raw_within_count"]
    if np.linalg.matrix_rank(XX)<p:
        return {"status":"underpowered_design_rank","n_routes":G,"n_pairs":n}
    beta=np.linalg.solve(XX,XY)
    meat=np.zeros((p,p))
    for route,part in route_to_groups.items():
        w=1./route_counts[route] if route_equal else 1.
        score=np.zeros(p)
        for g in part:
            score+=w*g["X"].T @ (g["Y"]-g["X"] @ beta)
        meat+=np.outer(score,score)
    xxinv=np.linalg.inv(XX)
    # Route is independent observational sampling cluster; no sitepair pseudo-n.
    V=(G/(G-1))*xxinv @ meat @ xxinv
    diag=np.diag(V)
    if np.any(diag<0): raise ValueError("Negative clustered covariance")
    SE=np.sqrt(diag)
    crit=float(student_t.ppf(.975,G-1))
    pvals=np.where(SE>1e-15, np.abs(beta/np.where(SE>0,SE,1.)),0.)
    probs=[float(2*student_t.sf(float(t),G-1)) for t in pvals]
    return {"status":"fitted","response":"Sørensen station-pair dissimilarity, conditional both stations have at least one recorded calling taxon",
            "model":"within survey-run fixed effect; route-clustered t uncertainty",
            "n_independent_routes":G,"n_surveys":len(groups),"n_station_pairs":n,
            "estimates":{name:{"beta":float(beta[i]),"se_route":float(SE[i]),
                                "ci95":[float(beta[i]-crit*SE[i]),float(beta[i]+crit*SE[i])],
                                "p_two_sided":probs[i]} for i,name in enumerate(PREDICTORS)},
            "unadjusted_cross_PEM_mean_dissimilarity":crosssum/crossn,
            "unadjusted_same_PEM_mean_dissimilarity":samesum/samen,
            "unadjusted_cross_minus_same":crosssum/crossn-samesum/samen,
            "route_equal_weighting":route_equal}

def synthetic_QA():
    rng=np.random.default_rng(17)
    groups=[]
    truth=np.array([.18,.05,-.02,.03,.015])
    for route_i in range(40):
        for rep in range(2):
            X=rng.normal(size=(24,5))
            X[:,0]=rng.integers(0,2,size=24)
            intercept=.1*route_i
            Y=X@truth+intercept
            Xm=X-X.mean(axis=0);Ym=Y-Y.mean()
            groups.append({"route":str(route_i),"state":"S","fold":"A" if route_i%2 else "B",
                           "X":Xm,"Y":Ym,
                           "raw_cross_count":int(np.sum(X[:,0]==1)),
                           "raw_within_count":int(np.sum(X[:,0]==0)),
                           "raw_cross_sum":float(Y[X[:,0]==1].sum()),
                           "raw_same_sum":float(Y[X[:,0]==0].sum())})
    fit=regression(groups)
    estimated=np.array([fit["estimates"][name]["beta"] for name in PREDICTORS])
    if np.max(np.abs(estimated-truth))>1e-9:
        raise RuntimeError("Synthetic known 5-predictor effect not recovered")
    return {"status":"PASS","known_cross_boundary_beta":float(estimated[0]),
            "all_five_predictors_within_run_recovered":True}

def mode_results(records,mode):
    groups,coverage=assemble(records,mode,matched_richness=False)
    primary=regression(groups)
    if primary["status"]!="fitted":
        raise RuntimeError("Original ten-stop macro sample unexpectedly underpowered: "+str(coverage))
    folds={}
    for fold in ("A","B"):
        part=[g for g in groups if g["fold"]==fold]
        folds[fold]=regression(part,minimum_routes=15)
    states=sorted(set(g["state"] for g in groups))
    loo=[]
    for state in states:
        res=regression([g for g in groups if g["state"]!=state])
        v=res.get("estimates",{}).get("different_mapped_PEM_overlap",{})
        loo.append({"omitted_state":state,"n_routes":res.get("n_independent_routes"),"status":res["status"],
                    "beta":v.get("beta"),"ci95":v.get("ci95")})
    matched_groups,matched_coverage=assemble(records,mode,matched_richness=True)
    matched=regression(matched_groups)
    route_equal=regression(groups,route_equal=True)
    est=primary["estimates"]["different_mapped_PEM_overlap"]
    fold_beta=[folds[f].get("estimates",{}).get("different_mapped_PEM_overlap",{}).get("beta") for f in ("A","B")]
    loo_valid=[x["beta"] for x in loo if x["status"]=="fitted"]
    frac=sum(x>0 for x in loo_valid)/len(loo_valid) if loo_valid else None
    richbeta=matched.get("estimates",{}).get("different_mapped_PEM_overlap",{}).get("beta")
    classified=bool(mode=="any" and est["ci95"][0]>0 and all(x is not None and x>0 for x in fold_beta)
                    and frac is not None and frac>=.8 and richbeta is not None and richbeta>0)
    return {"mode":mode,"coverage":coverage,"primary_model":primary,
            "geographic_fold_models":{k:{"n_routes":v.get("n_independent_routes"),
                   "status":v["status"],
                   "cross_PEM_estimate":v.get("estimates",{}).get("different_mapped_PEM_overlap")} for k,v in folds.items()},
            "leave_one_state_out":{"results":loo,"valid_states":len(loo_valid),
                                   "positive_fraction":frac,
                                   "min_beta":min(loo_valid) if loo_valid else None,
                                   "max_beta":max(loo_valid) if loo_valid else None},
            "richness_matched_coverage":matched_coverage,
            "richness_matched_model":matched,
            "route_equal_model":route_equal,
            "interpretation_classification":("exploratory_macro_boundary_association" if classified else "nonconfirmatory")}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    QA=synthetic_QA()
    source=module()
    records,coverage=source.load_run_context()
    if len(records)!=6236 or coverage["source_complete_runs"]!=7848:
        raise RuntimeError("Pinned 2026-10-21 NAAMP complete-case run counts drift")
    results={m:mode_results(records,m) for m in ("any","strong")}
    out={"analysis":"NAAMP_within_night_full_taxon_sorensen_turnover_x_mapped_PEM_boundary",
         "status":"EXECUTED_real_macro_community_turnover",
         "date":"2026-10-23",
         "contract":"exploration/NAAMP_MACRO_PEM_COMMUNITY_TURNOVER_FROZEN_SPEC_2026_10_23.md",
         "original_data_scope":coverage,
         "synthetic_QA":QA,
         "modes":results,
         "inference_limits":{
             "plant_NWI_time_matched_to_2001_2015":False,
             "NWI_zero_means_no_mapped_polygon_not_true_plant_absence":True,
             "station_spacing_measured_physically":False,
             "same_route_night_stops_sequential":True,
             "frog_species_competition_established":False,
             "plant_causes_turnover":False,
             "three_species_interaction_established":False,
             "RC6_main_manuscript_SI_modified":False}}
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(out,sort_keys=True,indent=2,allow_nan=False)+"\n",encoding="utf-8")
    print("MACRO_PEM_TURNOVER_RESULT_BEGIN")
    print(json.dumps({"status":out["status"],"source":coverage,"synthetic_QA":QA,
        "modes":{k:{"coverage":v["coverage"],"primary":v["primary_model"],
                     "fold_A":v["geographic_fold_models"]["A"],
                     "fold_B":v["geographic_fold_models"]["B"],
                     "LOSO":{k1:v["leave_one_state_out"][k1] for k1 in ("positive_fraction","min_beta","max_beta","valid_states")},
                     "richness_matched":v["richness_matched_model"],
                     "route_equal":v["route_equal_model"],
                     "class":v["interpretation_classification"]} for k,v in results.items()}},sort_keys=True))
    print("MACRO_PEM_TURNOVER_RESULT_END")
if __name__=="__main__":
    main()
