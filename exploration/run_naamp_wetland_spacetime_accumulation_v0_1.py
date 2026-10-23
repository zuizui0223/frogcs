#!/usr/bin/env python3
"""Exact two physical site × two seasonal round frog acoustic gamma hierarchy.

Observed, nonpredictive NAAMP(2001–15) × mapped NWI(250m) ecology.
Existing same-physical-10-site 2869-run/1115-route-year source is reused.
For each R>=2 source survey rounds, average all R choose 2 *within route-year*,
then average route-years within physical route. Route is independent inference.
Mapped emergent PEM is polygon overlap not botanical/causal intervention.
"""
from __future__ import annotations

import argparse
import itertools
import json
import math
from pathlib import Path
import importlib.util

import numpy as np
import pandas as pd
from scipy.stats import t as student_t

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"exploration/run_naamp_vegetation_withinyear_round_hierarchy_v0_1.py"
TWO_ROUND=ROOT/"exploration/run_naamp_wetland_seasonal_complementarity_v0_1.py"
SPEC="exploration/NAAMP_WETLAND_SPACETIME_ACOUSTIC_GAMMA_SPEC_2026_10_23.md"
MODES=(("any",1),("strong",2))
HABITATS=("PEM","other")
SECTIONS=("S","T","I")
TESTS=("delta_I_any","delta_I_strong","delta_S_any",
       "delta_S_strong","delta_T_any","delta_T_strong")
FLIPS=4999
SEED=26010236

def mod(label,path):
    s=importlib.util.spec_from_file_location(label,path)
    if s is None or s.loader is None:
        raise RuntimeError("Original source-backed acoustic script absent "+str(path))
    x=importlib.util.module_from_spec(s)
    s.loader.exec_module(x)
    return x

def exact_spacetime_2x2(before,after,two):
    """Expected species incidence Gij with i sites, j observation rounds."""
    if len(before)!=len(after) or len(before)<2:
        raise ValueError("Mismatched repeated physical site identity")
    n=len(before)
    a=[set(x) for x in before]
    b=[set(x) for x in after]
    original=two.exact_two_round_pool(a,b,2)
    G11=float((sum(len(x) for x in a)+sum(len(x) for x in b))/(2*n))
    G21=float(original["gamma_single_round_mean"])
    G12=float(sum(len(a[i]|b[i]) for i in range(n))/n)
    G22=float(original["gamma_union_two_rounds"])
    S=G21-G11
    T=G12-G11
    I=G22-G21-G12+G11
    if min(S,T,G11,G21,G12,G22)<-1e-10:
        raise RuntimeError("Negative expected sampled species richness / spatial / temporal accumulation")
    if abs(G22-(G11+S+T+I))>1e-10:
        raise RuntimeError("Space x temporal exact accumulation identity broken")
    if abs(G22-G21-original["bonus_temporal_complementarity"])>1e-10:
        raise RuntimeError("Two-round fixed two-site temporal bonus differs from original study")
    if G22+1e-10<max(G21,G12):
        raise RuntimeError("Union cannot have less richness than 1-sample subcombinations")
    return {"G11":G11,"G21":G21,"G12":G12,"G22":G22,"S":S,"T":T,"I":I}

def synthetic():
    two=mod("old_synthetic_grouper",TWO_ROUND)
    cases={
      "sparse_diagonal":([{"s"},set()],[set(),{"s"}]),
      "sparse_one_cell":([{"s"},set()],[set(),set()]),
      "persistent":([{"s"},{"a"}],[{"s"},{"a"}]),
      "silent":([set(),set()],[set(),set()]),
      "mixed":([{"a","b"},{"a"},{"c"},set()],
               [{"a"},{"d"},{"b","c"},{"d"}])
    }
    out={}
    for case,(a,b) in cases.items():
        x=exact_spacetime_2x2(a,b,two)
        n=len(a)
        allsites=list(itertools.combinations(range(n),2))
        q11=np.mean([len(z[i]) for z in (a,b) for i in range(n)])
        q21=np.mean([len(set().union(*(z[i] for i in inds)))
                     for z in (a,b) for inds in allsites])
        q12=np.mean([len(a[i]|b[i]) for i in range(n)])
        q22=np.mean([len(set().union(*(a[i]|b[i] for i in inds)))
                     for inds in allsites])
        for k,v in zip(("G11","G21","G12","G22"),(q11,q21,q12,q22)):
            if abs(x[k]-v)>1e-12:raise AssertionError(f"Incorrect exact expectation {case} {k}")
        out[case]=x["I"]
    if not (out["sparse_one_cell"]>0 and out["sparse_diagonal"]<0
         and abs(out["silent"])<1e-12 and abs(out["persistent"])<1e-12):
        raise AssertionError("Joint space×time cross term does not distinguish source-free seasonal architectures")
    return {"status":"PASS","bruteforce_fixed_two_site_two_round_expected_gamma":True,
            "space_and_temporal_accumulation_exact_identity":True,
            "positive_and_negative_cross_terms_can_occur_without_species_interactions":True,
            "source_free_cross_terms":out,
            "no_NAAMP_outcomes_used_in_QA":True}

def real_source():
    src=mod("original_same_site_season_source",BASE)
    good,calling,rare,source=src.source()
    coh,meta=src.build_rounds(good,calling,rare)
    if (len(good)!=6236 or len(coh)!=2869 or coh.route_year_id.nunique()!=1115
         or coh.route.nunique()!=274 or coh.state.nunique()!=20
         or source["source_NWI_original_physical_SiteIDs"]!=5147):
        raise RuntimeError("Original seasonally repeated NAAMP NWI wetland source sample drift")
    return good,calling,coh,source,meta

def source_matrix(good,calling,original):
    two=mod("previous_verified_gamma_bonus",TWO_ROUND)
    rows=[]
    for gid,source_runs in original.groupby("route_year_id",sort=True):
        ordered=source_runs.sort_values("round")
        runs=[good[str(rid)] for rid in ordered.rid]
        if len(runs)<2:raise RuntimeError("Source route-year lost 2+ distinct seasonal visits")
        first=runs[0]
        for r in runs[1:]:
            if (r["physical_sites"]!=first["physical_sites"]
                or r["stoplabels"]!=first["stoplabels"]
                or r["pem"]!=first["pem"]
                or r["wet"]!=first["wet"]):
                raise RuntimeError("Same site source changed across seasonal visits")
        P=np.asarray(first["pem"],bool)
        W=np.asarray(first["wet"],bool)
        pos=np.flatnonzero(P&W)
        neg=np.flatnonzero(W&~P)
        if min(len(pos),len(neg))<2:
            raise RuntimeError("Source m>=2 positive and negative PEM sites lost")
        roundsets={}
        for run in runs:
            this={}
            for mode,threshold in MODES:
                this[mode]=[
                   {str(tax) for tax,index in calling.get((run["rid"],s),{}).items()
                    if int(index)>=threshold}
                   for s in first["stoplabels"]]
            roundsets[run["round"]]=this
        for r1,r2 in itertools.combinations(runs,2):
            row={"route_year_id":gid,"route":first["route"],"state":first["state"],
                 "year":first["year"],"round_pair":str(r1["round"])+"-"+str(r2["round"]),
                 "n_source_rounds_in_route_year":len(runs),
                 "n_mapped_PEM_stops":int(len(pos)),
                 "n_mapped_other_wetland_stops":int(len(neg))}
            for mode,_ in MODES:
                a=roundsets[r1["round"]][mode];b=roundsets[r2["round"]][mode]
                for h,idx in (("PEM",pos),("other",neg)):
                    pair=exact_spacetime_2x2([a[i] for i in idx],[b[i] for i in idx],two)
                    for key,v in pair.items():
                        row[f"{h}_{key}_{mode}"]=v
                for key in ("G11","G21","G12","G22","S","T","I"):
                    row[f"delta_{key}_{mode}"]=row[f"PEM_{key}_{mode}"]-row[f"other_{key}_{mode}"]
                if abs((row[f"delta_G22_{mode}"]-row[f"delta_G11_{mode}"])
                       -row[f"delta_S_{mode}"]-row[f"delta_T_{mode}"]
                       -row[f"delta_I_{mode}"])>1e-10:
                    raise RuntimeError("Ecological-space/time delta accumulation contrast is not additive")
            rows.append(row)
    if not rows:raise RuntimeError("No NAAMP same-route-year two-round ecology")
    pair=pd.DataFrame(rows)
    n_expected=sum(math.comb(len(group),2) for gid,group in original.groupby("route_year_id"))
    if (len(pair)!=n_expected or pair.route_year_id.nunique()!=1115
          or pair.route.nunique()!=274 or pair.state.nunique()!=20):
        raise RuntimeError("Source previous exactly 1115 route-year two-round comparisons do not match")
    columns=[x for x in pair.columns if x.startswith(("PEM_","other_","delta_"))]
    year=pair.groupby(["state","route","route_year_id"],sort=False)[columns].mean().reset_index()
    if len(year)!=1115:raise RuntimeError("An observational group was lost when averaging pair combinations")
    meta={"same_original_route_year_groups":int(len(year)),
          "original_source_same_site_seasonal_run_nights":int(len(original)),
          "source_paired_round_comparisons_all_R_choose_2":int(len(pair)),
          "n_physical_routes":int(year.route.nunique()),
          "n_states":int(year.state.nunique()),
          "source_route_year_pairwise_seasonal_repeated_sample":True,
          "round_pair_counts":{str(k):int(v) for k,v in pair.round_pair.value_counts().items()},
          "independent_inference_grain":"physical monitoring route",
          "same_fixed_2_site_m_for_both_vegetation_classes":True,
          "same_two_actual_rounds_for_both_habitats":True,
          "no_frog_outcome_selection_for_site_eligibility":True}
    return pair,year,meta

def signflips(v,seed):
    n=len(v);target=abs(float(np.mean(v)))
    rng=np.random.default_rng(seed)
    extreme=0
    for b in range(0,FLIPS,250):
        k=min(250,FLIPS-b)
        means=(rng.choice(np.array([-1.,1.]),size=(k,n))@v)/n
        extreme+=int(np.count_nonzero(np.abs(means)>=target-1e-14))
    return {"n_flips":FLIPS,"extreme":extreme,
            "two_sided_plus_one_P":(1+extreme)/(1+FLIPS),
            "whole_route_flipped_not_individual_round_pairs_or_frogs":True}

def test(year,column,seed):
    route=year.groupby(["state","route"],sort=False)[column].mean().reset_index()
    n=len(route);S=int(route.state.nunique())
    if n<50 or S<5 or len(year)<150:
        raise ValueError("Source independent route/geographic coverage below frozen gate")
    x=route[column].to_numpy(float)
    if not np.isfinite(x).all():raise ValueError("Nonfinite ecology component")
    mu=float(x.mean())
    se=float(x.std(ddof=1)/math.sqrt(n))
    if se<=1e-12:raise RuntimeError("No route-to-route variation; CI not identifiable")
    t=float(student_t.ppf(.975,n-1))
    p=float(2*student_t.sf(abs(mu/se),n-1))
    ss=route.groupby("state")[column].mean()
    v=ss.to_numpy(float)
    sm=float(v.mean());se_s=float(v.std(ddof=1)/math.sqrt(S))
    tc=float(student_t.ppf(.975,S-1))
    loo={k:float(route.loc[route.state!=k,column].mean()) for k in ss.index}
    return {"outcome":column,
            "route_equal_mean":mu,"route_se":se,"CI95_route":[mu-t*se,mu+t*se],
            "route_Student_t_P":p,"route_signflip":signflips(x,seed),
            "n_physical_routes":n,"States":S,
            "route_years":len(year),
            "state_equal_mean":sm,"CI95_States":[sm-tc*se_s,sm+tc*se_s],
            "positive_State_means":int(np.sum(v>0)),
            "omit_one_State":{"n_estimable":len(loo),
                             "n_positive":sum(k>0 for k in loo.values()),
                             "n_negative":sum(k<0 for k in loo.values()),
                             "min":min(loo.values()),"max":max(loo.values())},
            "noncausal_acoustic_species_pool_effect":True}

def adjust_family(out):
    if set(out)!=set(TESTS):raise ValueError("Six predetermined ecological endpoints changed")
    p=[out[k]["route_Student_t_P"] for k in TESTS]
    order=sorted(range(6),key=lambda i:p[i])
    q=1.
    for rank in range(6,0,-1):
        idx=order[rank-1]
        q=min(q,6*p[idx]/rank)
        out[TESTS[idx]]["BH_q_six_frozen"]=q
    for name in TESTS:
        x=out[name]
        cr=x["CI95_route"];cs=x["CI95_States"]
        sign=1 if x["route_equal_mean"]>0 else -1
        out[name]["supported_robust_signed_context"]=bool(
            (cr[0]>0 and cs[0]>0 if sign>0 else cr[1]<0 and cs[1]<0)
            and x["BH_q_six_frozen"]<.05
            and x["route_signflip"]["two_sided_plus_one_P"]<.05
            and max(x["omit_one_State"]["n_positive"],x["omit_one_State"]["n_negative"])>=
                 .75*x["omit_one_State"]["n_estimable"])
    return ("exploratory_space_time_cross_context_difference"
         if out["delta_I_any"]["supported_robust_signed_context"]
         else "no_robust_PEM_specific_space_time_accumulation_cross_difference")

def description(year,pairs,source):
    summary={}
    for mode,_ in MODES:
        summary[mode]={}
        for habitat in HABITATS:
            summary[mode][habitat]={key:float(year.groupby("route")[f"{habitat}_{key}_{mode}"].mean().mean())
                    for key in ("G11","G21","G12","G22","S","T","I")}
            x=summary[mode][habitat]
            if abs(x["G22"]-x["G11"]-x["S"]-x["T"]-x["I"])>1e-10:
                raise RuntimeError("Route-balanced means lost exact space/time source identity")
        summary[mode]["PEM_minus_other"]={key:float(year.groupby("route")[f"delta_{key}_{mode}"].mean().mean())
                for key in ("G11","G21","G12","G22","S","T","I")}
    roundpairs={}
    for label,part in pairs.groupby("round_pair"):
        rr=part.groupby("route").mean(numeric_only=True)
        roundpairs[label]={"route_year_round_pairs":len(part),
             "independent_routes":int(part.route.nunique()),
             "states":int(part.state.nunique()),
             "deltas":{mode:{key:float(rr[f"delta_{key}_{mode}"].mean())
                               for key in ("S","T","I")}
                       for mode,_ in MODES},
             "no_posthoc_P_tests":True}
    return {"habitat_spacetime_decomposition":summary,
            "by_survey_round_pair_descriptive":roundpairs,
            "four_gamma_levels_not_causal_interaction":True,
            "all_class_difference_means_use_same_1115_route_years":True}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--outdir",type=Path,
         default=ROOT/"build/naamp_wetland_spacetime_accumulation")
    ap.add_argument("--synthetic-only",action="store_true")
    args=ap.parse_args()
    qa=synthetic()
    if args.synthetic_only:
        print(json.dumps(qa,sort_keys=True));return
    good,ci,orig,source,orig_scope=real_source()
    pairs,year,scope=source_matrix(good,ci,orig)
    results={key:test(year,key,SEED+i) for i,key in enumerate(TESTS)}
    judgement=adjust_family(results)
    desc=description(year,pairs,source)
    for mode,_ in MODES:
        for key in ("G11","G21","G12","G22","S","T","I"):
            expected=desc["habitat_spacetime_decomposition"][mode]["PEM"][key] - desc["habitat_spacetime_decomposition"][mode]["other"][key]
            reported=desc["habitat_spacetime_decomposition"][mode]["PEM_minus_other"][key]
            if abs(expected-reported)>1e-10:raise RuntimeError("Ecological vegetation context aggregate drift")
    out={"analysis":"NAAMP_NWI_mapped_PEM_vs_other_wetland_spatial_x_withinyear_acoustic_gamma_hierarchy",
         "status":"real_source_verified_NAAMP_spacetime_acoustic_taxon_accumulation_completed",
         "date":"2026-10-23",
         "pre_locked_protocol":SPEC,
         "post_hoc_same_previously_explored_USGS_NAAMP_archive":True,
         "synthetic_QA":qa,
         "original_source_coverage":source,
         "source_2869_withinyear_cohort":orig_scope,
         "two_round_2site_source_geographic_hierarchy":scope,
         "six_fixed_route_clustered_spacetime_endpoints":results,
         "primary_decision":judgement,
         "ecological_hierarchical_descriptives":desc,
         "scientific_boundaries":{
            "not_a_prediction":True,
            "mapped_250m_NWI_not_live_botanical_vegetation":True,
            "acoustic_taxon_label_not_true_demographic_occupancy":True,
            "observational_SxT_gamma_cross_term_not_biological_species_interaction":True,
            "no_plant_causal_inference":True,
            "no_irreducible_higher_order_species_community_interaction_measured":True,
            "JAE_RC6_main_manuscript_SI_submission_unchanged":True}}
    args.outdir.mkdir(parents=True,exist_ok=True)
    (args.outdir/"result.json").write_text(json.dumps(out,indent=2,sort_keys=True,allow_nan=False)+"\n")
    print("NAAMP_WETLAND_SPACETIME_BEGIN",flush=True)
    print(json.dumps({"status":out["status"],"QA":qa,"source":scope,
       "decision":judgement,
       "results":results,
       "description":desc},sort_keys=True,allow_nan=False),flush=True)
    print("NAAMP_WETLAND_SPACETIME_END",flush=True)

if __name__=="__main__":
    main()
