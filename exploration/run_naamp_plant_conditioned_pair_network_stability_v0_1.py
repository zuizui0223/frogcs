#!/usr/bin/env python3
"""Post-result stability checks on fixed taxon-pair acoustic network, no null refit.

Import from frozen prior artifact only; do not generate new main results.
"""
from __future__ import annotations
import argparse
import importlib.util
import json
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm

ROOT=Path(__file__).resolve().parents[1]
Z=1.959963984540054

def mod(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    o=importlib.util.module_from_spec(spec);assert spec.loader;spec.loader.exec_module(o);return o

base=mod("frozen_naamp_runs_for_pair_qa",ROOT/"scripts/naamp/run_naamp_ecological_pulse.py")

def cluster(d):
    n=int(len(d));routes=int(d.route.nunique())
    if n<12 or routes<7:
        return {"status":"insufficient","n":n,"routes":routes}
    f=sm.OLS(d.residual_shared_stops.to_numpy(float),
             np.ones((n,1),float)).fit(cov_type="cluster",cov_kwds={"groups":d.route.astype(str)})
    b=float(f.params[0]);se=float(f.bse[0])
    return {"status":"fitted","n":n,"routes":routes,
            "mean_residual":b,"ci95":[b-Z*se,b+Z*se],
            "p":float(f.pvalues[0])}

def time_and_fold(g,expected_sign):
    subsets={
        "early_2001_2008":g[g.SurveyYear<=2008],
        "late_2009_2015":g[g.SurveyYear>=2009],
        "route_fold_A":g[g.fold=="A"],
        "route_fold_B":g[g.fold=="B"]
    }
    result={name:cluster(part) for name,part in subsets.items()}
    fit=[x for x in result.values() if x["status"]=="fitted"]
    complete=len(fit)==4
    same_sign=complete and all(
        x["mean_residual"]*expected_sign>0 for x in fit)
    clear_ci=complete and all(
        (x["ci95"][0]>0 if expected_sign>0 else x["ci95"][1]<0)
        for x in fit)
    return {"subsets":result,"n_eligible_subsets":len(fit),
            "direction_stable":bool(same_sign),
            "interval_stable":bool(clear_ci),
            "classification":"same_sign_all_four" if same_sign else
                ("sign_disagreement" if complete else "insufficient_subsets")}

def leave_one_state(g,expected_sign):
    vals=[]
    for st in sorted(g.State.unique()):
        d=g[g.State!=st]
        if len(d)<30 or d.route.nunique()<15:
            continue
        z=cluster(d)
        if z["status"]=="fitted":
            vals.append({"omitted_state":st,"mean":z["mean_residual"],
                         "same_sign":bool(z["mean_residual"]*expected_sign>0),
                         "ci95":z["ci95"],"n":z["n"],"routes":z["routes"]})
    return {"n_state_omissions":len(vals),
            "n_same_sign":sum(x["same_sign"] for x in vals),
            "all_state_omission_signs_stable":bool(vals and all(x["same_sign"] for x in vals)),
            "min_max_beta":[min(x["mean"] for x in vals),max(x["mean"] for x in vals)] if vals else None,
            "state_details":vals}

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--run-ledger",required=True,type=Path)
    parser.add_argument("--pair-ledger",required=True,type=Path)
    parser.add_argument("--out",default=ROOT/"build"/"naamp_plant_pair_network_stability"/"result.json",type=Path)
    args=parser.parse_args()
    run=pd.read_csv(args.run_ledger,dtype={"RunID":str})
    pair=pd.read_csv(args.pair_ledger)
    if len(run)!=13175:raise RuntimeError(f"Frozen pair-run sample drift: {len(run)}")
    if run.RunID.nunique()!=1766:raise RuntimeError("Expected original 1766 source matrices")
    if int(pair.eligible.astype(bool).sum())!=112:
        raise RuntimeError("Original BH family changed")
    supported=pair[pair.BH_supported.fillna(False).astype(bool)].copy()
    if len(supported)!=21:raise RuntimeError("Original 21 supported pairs changed")
    raw=base.load()
    runs,_=base.build_runs(raw)
    lookup=dict(zip(runs.RunID.astype(str),runs.SurveyYear.astype(int)))
    if any(i not in lookup for i in run.RunID.unique()):
        raise RuntimeError("Historical RunID-to-year identity drift")
    run["SurveyYear"]=run.RunID.map(lookup).astype(int)
    run["State"]=run.route.astype(str).str.split(":").str[0]
    prior_pairs=pair[pair.eligible.astype(bool)].copy()
    pair_lookup={s:g for s,g in run.groupby("pair",sort=False)}
    allitems=[]
    for rr in prior_pairs.itertuples(index=False):
        name=str(rr.pair)
        if name not in pair_lookup:raise RuntimeError("Source pair missing "+name)
        g=pair_lookup[name]
        direction=1 if float(rr.PEM_conditioned_residual if isinstance(rr.PEM_conditioned_residual,float) else 0)>0 else 0
        # Existing pair CSV flattens JSON dict into text; derive signed direction from
        # *original frozen run-level mean*, which must match original output.
        orig=float(g.residual_shared_stops.mean())
        sign=1 if orig>0 else -1
        source_p=float(rr.BH_q) if pd.notna(rr.BH_q) else None
        z=time_and_fold(g,sign)
        h=leave_one_state(g,sign) if bool(rr.BH_supported) else None
        item={
            "pair":name,"taxon1":str(rr.taxon1),"taxon2":str(rr.taxon2),
            "original_BH_q":source_p,
            "original_BH_supported":bool(rr.BH_supported),
            "n_run_instances":int(len(g)),"routes":int(g.route.nunique()),
            "original_mean_residual":orig,
            "direction":"positive_acoustic_overlap" if sign>0 else "residual_acoustic_segregation",
            "temporal_and_route_fold":z,
            "leave_one_state_out":h,
            "cross_genus":str(rr.taxon1).split()[0]!=str(rr.taxon2).split()[0]
        }
        allitems.append(item)
    main=[x for x in allitems if x["original_BH_supported"]]
    out={"analysis":"naamp_acoustic_pair_network_temporal_geo_posthoc_audit_v0_1",
         "status":"post_result_sensitivity_not_independent_confirmation",
         "sources":{"original_pair_network_run":39520831924,
                    "NWI_crossfit_run":39516056663,
                    "NAAMP_Runs_pinned_SHA256":base.PINS["Runs.csv"]},
         "coverage":{"source_pair_run_rows":len(run),
                     "source_network_pairs_tested":112,
                     "source_BH_supported_edges":21,
                     "runs_early":int(run[run.SurveyYear<=2008].RunID.nunique()),
                     "runs_late":int(run[run.SurveyYear>=2009].RunID.nunique())},
         "supported_edge_stability":{
             "original_21_edges":len(main),
             "direction_stable_both_time_and_route_folds":sum(x["temporal_and_route_fold"]["direction_stable"] for x in main),
             "interval_stable_both_time_and_route_folds":sum(x["temporal_and_route_fold"]["interval_stable"] for x in main),
             "incomplete_time_or_route_fold_coverage":sum(x["temporal_and_route_fold"]["n_eligible_subsets"]<4 for x in main),
             "cross_genus_original_edges":sum(x["cross_genus"] for x in main),
             "all_leave_state_omission_signs_stable":sum(x["leave_one_state_out"]["all_state_omission_signs_stable"] for x in main)
         },
         "original_supported_edges":main,
         "all_112_network_pairs":allitems,
         "boundaries":{"time_split_after_observing_primary_network":True,
                       "same_USGS_archive_not_external_replication":True,
                       "no_contemporaneous_fish_odonate_plant_species_counts":True,
                       "no_direct_species_competition_inferred":True,
                       "RC6_manuscript_unmodified":True}}
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(out,sort_keys=True,indent=2)+"\n")
    print("PAIR_NETWORK_STABILITY_BEGIN")
    print(json.dumps({"analysis":out["analysis"],"coverage":out["coverage"],
                      "supported_edge_stability":out["supported_edge_stability"],
                      "supported_edges":[{
                            "pair":x["pair"],"mean":x["original_mean_residual"],
                            "BH_q":x["original_BH_q"],
                            "direction_stable":x["temporal_and_route_fold"]["direction_stable"],
                            "interval_stable":x["temporal_and_route_fold"]["interval_stable"],
                            "time_early":x["temporal_and_route_fold"]["subsets"]["early_2001_2008"],
                            "time_late":x["temporal_and_route_fold"]["subsets"]["late_2009_2015"],
                            "all_omit_state_sign_stable":x["leave_one_state_out"]["all_state_omission_signs_stable"]
                          } for x in main]},sort_keys=True))
    print("PAIR_NETWORK_STABILITY_END")

if __name__=="__main__":
    main()
