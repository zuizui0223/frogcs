#!/usr/bin/env python3
"""Exploratory frog acoustic pair network after cross-fitted NWI-based fixed-margin nulls.

Not a trophic interaction dataset. No measured fish, dragonflies or other
non-amphibian taxa. Fish/invertebrate-mediated biotic network is a future test.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import random
import re
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.stats.multitest import multipletests

ROOT=Path(__file__).resolve().parents[1]
SEED=2840279
N_SIM=199
BURN_PER_TAXON=40
THIN_PER_TAXON=8
Z=1.959963984540054
MIN_PAIR_RUNS=30
MIN_PAIR_ROUTES=15
MIN_INFORMATIVE_MATRIX=10
MODELS={"wetland":[0],"wetland_and_emergent":[0,1]}

def loader(name,path):
    sp=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(sp)
    assert sp.loader
    sp.loader.exec_module(module)
    return module

checker=loader("nwi_conditional_checkerboard",ROOT/"exploration/run_naamp_nwi_conditional_checkerboard_v0_1.py")

def taxon_components(name):
    """Explicit taxon-complex aliases only; do NOT collapse all same-genus taxa."""
    name=str(name)
    if "/" not in name:return {name}
    a=name.replace(" complex","").strip().split(None,1)
    if len(a)!=2:return {name}
    genus,rest=a
    return {genus+" "+part.strip() for part in rest.split("/") if part.strip()}

def ambiguous_taxa(a,b):
    """Avoid pseudo-interactions between a taxon unit and its species alias."""
    if a==b:return True
    components_a=taxon_components(a)
    components_b=taxon_components(b)
    return ("/" in a or "/" in b) and bool(components_a&components_b)

def test_synthetic():
    x=checker.synth_test()
    assert x["status"]=="PASS"
    r=[{0,1},{1,2},{1,3}]
    p=[(0,1),(0,2),(1,2)]
    count=[len(r[a]&r[b]) for a,b in p]
    assert count==[1,1,1]
    assert ambiguous_taxa("Hyla versicolor","Hyla chrysoscelis/versicolor complex")
    assert ambiguous_taxa("Pseudacris maculata","Pseudacris maculata/triseriata complex")
    assert not ambiguous_taxa("Hyla versicolor","Pseudacris crucifer")
    assert not ambiguous_taxa("Hyla versicolor","Hyla chrysoscelis")
    return {"status":"PASS","weighted_margins":"PASS",
            "weighted_sampler_stationarity":x,
            "pair_overlap_semantics":"PASS",
            "taxon_complex_alias_rejection":"PASS"}

def heldout_training_coefficients(path):
    raw=json.loads(Path(path).read_text())
    if sorted(raw)!=["A","B"]:
        raise RuntimeError("Frozen model coefficient output is not both route folds")
    result={}
    for fold,bytax in raw.items():
        result[fold]={}
        for taxon,values in bytax.items():
            result[fold][taxon]={}
            for model,which in MODELS.items():
                if model not in values:
                    raise RuntimeError(f"Missing frozen {model} for {taxon}")
                coeff=np.asarray(values[model],float)
                if coeff.shape!=(len(which),) or not np.isfinite(coeff).all():
                    raise RuntimeError("Coefficient shape, nonfinite or identity drift")
                result[fold][taxon][model]=coeff
    return result

def simulate_run_pairs(rows,score,pair_index,seed):
    current=[set(r) for r in rows]
    orig=checker.fixed_margins(current)
    rng=random.Random(seed)
    feasible=accepted=0
    n=len(rows)
    for _ in range(BURN_PER_TAXON*n):
        a,b=checker.weighted_trade(current,score,rng)
        feasible+=a;accepted+=b
    totals=np.zeros(len(pair_index),float)
    squares=np.zeros(len(pair_index),float)
    cscore_draws=[]
    for idx in range(N_SIM):
        for _ in range(THIN_PER_TAXON*n):
            a,b=checker.weighted_trade(current,score,rng)
            feasible+=a;accepted+=b
        ov=np.fromiter((len(current[a]&current[b]) for a,b in pair_index),
                       dtype=np.float64,count=len(pair_index))
        totals+=ov
        squares+=ov*ov
        cscore_draws.append(checker.cscore(current))
        if idx in (0,N_SIM//2,N_SIM-1):
            if orig!=checker.fixed_margins(current):
                raise RuntimeError("weighted Curveball violated taxon/stop margins")
    avg=totals/N_SIM
    variance=np.maximum(0,(squares-N_SIM*avg*avg)/(N_SIM-1))
    diag={"accepted_given_feasible":accepted/feasible if feasible else 0.,
          "feasible_proposals":feasible,
          "distinct_cscore_states":len(set(round(c,9) for c in cscore_draws))}
    return avg,np.sqrt(variance),diag

def build_pair_observation_ledger(records,reference,coefs,synthetic_limit=0):
    ref=pd.read_csv(reference,dtype={"RunID":str})
    required={"RunID","observed_cscore","null_mean","null_sd"}
    if not required.issubset(ref.columns):
        raise RuntimeError("Frozen strong checkerboard reference schema drift")
    if ref.RunID.duplicated().any():
        raise RuntimeError("Duplicated frozen run ID")
    ref=ref.set_index("RunID",drop=False)
    ids=sorted(set(ref.index)&set(records))
    if synthetic_limit:
        ids=ids[:synthetic_limit]
    else:
        if len(ids)!=1766 or len({records[rid]["route"] for rid in ids})!=398:
            raise RuntimeError(f"Source population changed; expected 1766/398, got {len(ids)}/{len({records[rid]['route'] for rid in ids})}")
    ledger=[]
    run_stats=[]
    aliases=Counter()
    for index,rid in enumerate(ids,1):
        run=records[rid]
        taxa=sorted(run["activity"]["strong"])
        rows=[run["activity"]["strong"][t] for t in taxa]
        if not checker.exchangeable(rows):
            raise RuntimeError("Frozen reference has nonexchangeable matrix")
        obs_c=checker.cscore(rows)
        old=ref.loc[rid]
        if abs(obs_c-float(old.observed_cscore))>1e-8:
            raise RuntimeError(f"Frozen Cscore mismatch {rid}: {obs_c}, {old.observed_cscore}")
        pair_index=[(a,b) for a in range(len(taxa)) for b in range(a+1,len(taxa))]
        pair_obs=[len(rows[a]&rows[b]) for a,b in pair_index]
        heldout=checker.complementary(run["fold"])
        trained=coefs[heldout]
        record={"RunID":rid,"route":run["route"],"fold":run["fold"],"n_species":len(taxa)}
        means={}
        sds={}
        for model,cols in MODELS.items():
            coeff=np.stack([trained.get(t,{}).get(model,np.zeros(len(cols)))
                           for t in taxa],axis=0)
            scores=coeff@run["v"][:,cols].T
            seedbytes=f"{SEED}|{model}|{rid}".encode()
            seed=int.from_bytes(hashlib.sha256(seedbytes).digest()[:8],"big")
            mean,sd,diag=simulate_run_pairs(rows,scores,pair_index,seed)
            means[model]=mean
            sds[model]=sd
            record[f"{model}_accepted_given_feasible"]=diag["accepted_given_feasible"]
            record[f"{model}_mix_flag"]=bool(float(old.null_sd)>1e-8 and diag["distinct_cscore_states"]<2)
        record["informative_fixedmargin_cscore"]=float(old.null_sd)>1e-8
        run_stats.append(record)
        for k,(a,b) in enumerate(pair_index):
            sp1,sp2=taxa[a],taxa[b]
            if ambiguous_taxa(sp1,sp2):
                aliases["explicit_taxon_complex_aliases_excluded"]+=1
                continue
            ledger.append({
                "RunID":rid,"route":run["route"],"fold":run["fold"],
                "taxon1":sp1,"taxon2":sp2,
                "pair":sp1+" || "+sp2,
                "taxon1_sites":len(rows[a]),"taxon2_sites":len(rows[b]),
                "observed_shared_stops":float(pair_obs[k]),
                "expected_shared_wetland_only":float(means["wetland"][k]),
                "expected_shared_with_emergent":float(means["wetland_and_emergent"][k]),
                "null_pairwise_shared_sd":float(sds["wetland_and_emergent"][k]),
                "residual_shared_stops":float(pair_obs[k]-means["wetland_and_emergent"][k]),
                "plant_predicted_shared_increment":
                    float(means["wetland_and_emergent"][k]-means["wetland"][k])})
        if index%350==0:
            print("PAIR_NETWORK_PROGRESS",index,len(ids),len(ledger),flush=True)
    ledger=pd.DataFrame(ledger)
    runstat=pd.DataFrame(run_stats)
    return ledger,runstat,dict(aliases)

def intercept_cluster(data,column):
    if data.route.nunique()<2:return {"status":"underidentified_routes"}
    fit=sm.OLS(data[column].to_numpy(float),
               np.ones((len(data),1),dtype=float)).fit(
                   cov_type="cluster",cov_kwds={"groups":data.route.astype(str)})
    b=float(fit.params[0]);se=float(fit.bse[0])
    return {"estimate":b,"route_cluster_se":se,
            "ci95":[b-Z*se,b+Z*se],
            "p_two_sided":float(fit.pvalues[0])}

def pair_network_ledger(ledger):
    if ledger.empty:return [],{"status":"empty"}
    result=[]
    for pair,g in ledger.groupby("pair",sort=True):
        observed=int(len(g))
        routes=int(g.route.nunique())
        null_eligible=int((g.null_pairwise_shared_sd>1e-8).sum())
        item={"pair":pair,"taxon1":str(g.taxon1.iloc[0]),"taxon2":str(g.taxon2.iloc[0]),
              "jointly_active_runs":observed,"routes":routes,
              "varying_fixed_margin_null_matrices":null_eligible,
              "observed_mean_shared_stops":float(g.observed_shared_stops.mean()),
              "PEM_null_mean_shared_stops":float(g.expected_shared_with_emergent.mean()),
              "wetland_null_mean_shared_stops":float(g.expected_shared_wetland_only.mean())}
        eligible=(observed>=MIN_PAIR_RUNS and routes>=MIN_PAIR_ROUTES and null_eligible>=MIN_INFORMATIVE_MATRIX)
        item["eligible"]=eligible
        if eligible:
            a=intercept_cluster(g,"residual_shared_stops")
            b=intercept_cluster(g,"plant_predicted_shared_increment")
            item["PEM_conditioned_residual"]=a
            item["PEM_increment_over_wetland_only"]=b
        result.append(item)
    tested=[x for x in result if x["eligible"]]
    if tested:
        raw_p=np.asarray([x["PEM_conditioned_residual"]["p_two_sided"] for x in tested],float)
        if not np.isfinite(raw_p).all():raise RuntimeError("Non-finite pair significance")
        q=multipletests(raw_p,alpha=.05,method="fdr_bh")[1]
        for item,val in zip(tested,q):
            item["BH_q"]=float(val)
            item["BH_supported"]=bool(val<.05)
            item["association_direction"]="excess_sharing" if item["PEM_conditioned_residual"]["estimate"]>0 else "segregation"
    supported=[x for x in tested if x.get("BH_supported")]
    summary={"status":"fitted","n_pair_units_observed":len(result),
             "n_eligible_pairs":len(tested),
             "n_BH_edges":len(supported),
             "n_BH_excess_sharing":sum(x["association_direction"]=="excess_sharing" for x in supported),
             "n_BH_segregation":sum(x["association_direction"]=="segregation" for x in supported),
             "top_supported_edges":sorted([{"pair":x["pair"],"jointly_active_runs":x["jointly_active_runs"],
                                            "routes":x["routes"],
                                            "excess_sharing_per_route_run":x["PEM_conditioned_residual"]["estimate"],
                                            "ci95":x["PEM_conditioned_residual"]["ci95"],
                                            "BH_q":x["BH_q"],"direction":x["association_direction"]}
                                           for x in supported],key=lambda a:a["BH_q"])[:25],
             "top_nominal_nonsupported":sorted([{"pair":x["pair"],"estimate":x["PEM_conditioned_residual"]["estimate"],
                                                 "BH_q":x["BH_q"]}
                                             for x in tested if not x.get("BH_supported")],key=lambda a:a["BH_q"])[:10]}
    graph=defaultdict(lambda:{"positive_edges":0,"negative_edges":0})
    for edge in supported:
        sign=edge["association_direction"]
        for taxon in (edge["taxon1"],edge["taxon2"]):
            graph[taxon]["positive_edges" if sign=="excess_sharing" else "negative_edges"]+=1
    summary["species_network_degrees"]={k:v for k,v in sorted(graph.items(),
                    key=lambda kv:-(kv[1]["positive_edges"]+kv[1]["negative_edges"]))}
    return result,summary

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--frozen-coefficients",type=Path)
    p.add_argument("--frozen-reference-strong",type=Path)
    p.add_argument("--outdir",type=Path,default=ROOT/"build"/"naamp_plant_conditioned_pair_network")
    p.add_argument("--synthetic-only",action="store_true")
    args=p.parse_args()
    qa=test_synthetic()
    print("PAIR_NETWORK_SYNTHETIC_QA",json.dumps(qa,sort_keys=True),flush=True)
    if args.synthetic_only:return
    if not(args.frozen_coefficients and args.frozen_reference_strong):
        raise SystemExit("--frozen-coefficients and --frozen-reference-strong required")
    trained=heldout_training_coefficients(args.frozen_coefficients)
    records,coverage=checker.load_run_context()
    ledger,stats,aliases=build_pair_observation_ledger(
        records,args.frozen_reference_strong,trained)
    if ledger.empty:raise RuntimeError("empty recorded acoustic pair overlap")
    reference_informative=int(stats.informative_fixedmargin_cscore.sum())
    mismatch=int(stats.wetland_and_emergent_mix_flag.sum())
    bad=bool(reference_informative and mismatch/reference_informative>.20)
    if bad:
        raise RuntimeError("Weighted null sampler C-score exploration inadequate")
    pair_data,results=pair_network_ledger(ledger)
    result={
        "analysis":"naamp_nwi_plant_conditioned_acoustic_pair_network_v0_1",
        "status":"posthoc_exploratory_not_interaction_causality",
        "contract":"exploration/NAAMP_PLANT_CONDITIONED_SPECIES_PAIR_NETWORK_CONTRACT_2026_10_21.md",
        "source":{"NWI_crosswalk_run":39450277196,
                  "crossfit_weighted_null_run":39516056663,
                  "frozen_strong_check_run":39436588431,
                  "all_route_train_coefficients_reused_no_refitting":True,
                  "fixed_margins":{"each_taxon_stop_count":True,
                                   "each_stop_species_richness":True}},
        "synthetic_QA":qa,"original_geospatial_coverage":coverage,
        "population":{"matched_frozen_strong_matrices":int(len(stats)),
                      "n_routes":int(stats.route.nunique()),
                      "pairwise_route_run_instances":int(len(ledger)),
                      "informative_original_Cscore_matrices":reference_informative,
                      "no_mixing_on_informative":mismatch,
                      "unreliable_sampling":bad,
                      "mean_accepted_fraction_PEM":float(stats.wetland_and_emergent_accepted_given_feasible.mean()),
                      "mean_accepted_fraction_wetland":float(stats.wetland_accepted_given_feasible.mean()),
                      "explicit_taxon_complex_alias_exclusions":aliases},
        "network":results,
        "thresholds":{"jointly_active_runs":MIN_PAIR_RUNS,
                      "independent_routes":MIN_PAIR_ROUTES,
                      "variable_fixed_margin_null_matrices":MIN_INFORMATIVE_MATRIX,
                      "FDR_method":"Benjamini-Hochberg 0.05 over all eligible pairs"},
        "interpretation_boundary":{"pair_edges_are_conditional_acoustic_associations":True,
            "direct_species_competition_measured":False,
            "fish_or_odonata_surveys_co_sampled":False,
            "trophic_interactions_identified":False,
            "contemporaneous_NWI_macrophytes_measured":False,
            "simultaneous_calls_across_stops_observed":False,
            "frog_calls_are_not_occupancy":True,
            "RC6_submission_modified":False}}
    args.outdir.mkdir(parents=True,exist_ok=True)
    (args.outdir/"result.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    pd.DataFrame(pair_data).to_csv(args.outdir/"all_species_pairs_BH_ledger.csv",index=False)
    ledger.to_csv(args.outdir/"all_same_route_acoustic_pair_nulls.csv",index=False)
    stats.to_csv(args.outdir/"run_level_margins_and_mixing.csv",index=False)
    print("PAIR_NETWORK_RESULT_BEGIN",flush=True)
    print(json.dumps(result,sort_keys=True),flush=True)
    print("PAIR_NETWORK_RESULT_END",flush=True)

if __name__=="__main__":
    main()
