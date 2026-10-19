#!/usr/bin/env python3
"""Degree-preserving NAAMP species×stop null, rain-context checkerboard contrast.

This is a separate, exploratory co-detection / community-assembly analysis.
It tests nonrandom pair placement, NOT competition, true co-presence, mating
success, or compression of within-night calling schedules.

Design: research/FIXED_MARGIN_COMPETITION_NICHE_SPEC_2026-10-19.md.
The original source requires 3 SHA256-pinned USGS files. No source fallback,
species-list fishing, alternate nulls, or new JAE manuscript endpoints.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import platform
import random

import numpy as np
import pandas as pd
import scipy
import statsmodels
import statsmodels.formula.api as smf

ROOT=Path(__file__).resolve().parents[2]
BASE_SOURCE=ROOT/"scripts/naamp/run_naamp_ecological_pulse.py"
SPATIAL_SOURCE=ROOT/"scripts/naamp/run_naamp_spatial_taxonomic_activation_decomposition.py"
PRIMARY_METRIC="degree_conditioned_checkerboard_C"
BASE_SEED=20261019
DRAWS_PER_CHAIN=128
CHAINS=2
BURN_FACTOR=20
SPACING_FACTOR=10
MIN_INFO_PAIRS=200
MIN_INFO_ROUTES=80
MIN_EXACT_PAIRS=75
MIN_EXACT_ROUTES=40
N_SITES=10
N_RUNS_EXPECTED=7848
N_PAIR_EXPECTED=4236
N_ROUTE_EXPECTED=585
N_STATE_EXPECTED=21
Q=1.959963984540054


def load_module(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    mod=importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def incidence_masks(stop_order,stop_species):
    stops=list(stop_order)
    if len(stops)!=N_SITES or len(set(stops))!=N_SITES:
        raise ValueError("exactly ten unique surveyed stops required")
    masks={}
    for site,stop in enumerate(stops):
        for taxon in stop_species.get(stop,set()):
            if not isinstance(taxon,str) or not taxon.strip():
                raise ValueError("empty operational taxon identifier")
            masks[taxon]=masks.get(taxon,0)|(1<<site)
    return dict(sorted(masks.items()))


def total_pairwise_overlap(row_masks):
    # Fixed by site richness: Σ_i<j intersection = Σ_stop choose(column total,2)
    rows=list(row_masks)
    return sum((a&b).bit_count() for i,a in enumerate(rows)
               for b in rows[i+1:])


def cscore(row_masks):
    """Mean checkerboard score, distinct from total co-detections."""
    b=list(row_masks)
    m=len(b)
    if m<2 or all(x==0 for x in b):
        return None
    score=0.
    for i in range(m):
        ri=b[i].bit_count()
        for j in range(i+1,m):
            rj=b[j].bit_count()
            shared=(b[i]&b[j]).bit_count()
            score+=(ri-shared)*(rj-shared)
    return score/(m*(m-1)//2)


def curveball_trade(row_masks,rng):
    """Symmetric trade of row-exclusive sites; preserves row and column sums."""
    m=len(row_masks)
    if m<2:
        return 0
    a=rng.randrange(m)
    b=rng.randrange(m-1)
    if b>=a:
        b+=1
    A=row_masks[a]
    B=row_masks[b]
    exclusive_a=A&~B
    exclusive_b=B&~A
    if not exclusive_a or not exclusive_b:
        return 0
    pool=exclusive_a|exclusive_b
    k=exclusive_a.bit_count()
    choices=[site for site in range(N_SITES) if pool & (1<<site)]
    sampled=rng.sample(choices,k)
    samplemask=sum(1<<s for s in sampled)
    common=A&B
    row_masks[a]=common|samplemask
    row_masks[b]=common|(pool^samplemask)
    return int(row_masks[a]!=A or row_masks[b]!=B)


def seed_for(run_id,chain):
    seed=f"{BASE_SEED}|{run_id}|{chain}"
    return int.from_bytes(hashlib.sha256(seed.encode()).digest()[:8],"big")


def null_score(row_masks,run_id):
    original=list(row_masks)
    m=len(original)
    observed=cscore(original)
    if observed is None or m<3:
        return {"informative":False,"reason":"under_three_taxa",
                "n_draws":0,"observed_cscore":observed}
    row_degree=[r.bit_count() for r in original]
    col_degree=[sum((r>>j)&1 for r in original) for j in range(N_SITES)]
    overlap_total=total_pairwise_overlap(original)
    samples=[]
    chain_mean=[]
    acceptance=[]
    for chain in range(CHAINS):
        rng=random.Random(seed_for(run_id,chain))
        bits=original.copy()
        burn=BURN_FACTOR*max(3,m)
        spacing=SPACING_FACTOR*max(3,m)
        attempted=0
        moved=0
        for _ in range(burn):
            moved+=curveball_trade(bits,rng)
            attempted+=1
        chain_draws=[]
        for sample in range(DRAWS_PER_CHAIN):
            for _ in range(spacing):
                moved+=curveball_trade(bits,rng)
                attempted+=1
            score=cscore(bits)
            if score is None or not np.isfinite(score):
                raise RuntimeError("fixed-margin null produced nonfinite checkerboard")
            chain_draws.append(score)
        if [r.bit_count() for r in bits]!=row_degree:
            raise RuntimeError("curveball failed row margins")
        if [sum((r>>j)&1 for r in bits) for j in range(N_SITES)]!=col_degree:
            raise RuntimeError("curveball failed column margins")
        if total_pairwise_overlap(bits)!=overlap_total:
            raise RuntimeError("curveball modified fixed co-detection pair total")
        chain_mean.append(float(np.mean(chain_draws)))
        acceptance.append(float(moved/attempted))
        samples.extend(chain_draws)
    arr=np.asarray(samples,float)
    nullmean=float(arr.mean())
    sd=float(arr.std(ddof=1))
    return {
       "informative":bool(sd>1e-10),
       "reason":"null_cscore_variable" if sd>1e-10 else "structural_invariance",
       "n_draws":len(samples),
       "observed_cscore":float(observed),
       "null_mean":nullmean,"null_sd":sd,
       "excess":float(observed-nullmean),
       "chain_means":chain_mean,
       "chain_disagreement":abs(chain_mean[0]-chain_mean[1]),
       "acceptance_rates":acceptance,
       "m_taxa":m,
       "n_incidence":sum(row_degree),
       "n_active_stops":sum(x>0 for x in col_degree),
       "total_codetection_pairs":overlap_total,
       "null_se_of_mean_assuming_independence_lower_bound":sd/len(samples)**.5,
       "fixed_total_pairs_proven":True,
    }


def wet_minus_dry(wet,dry):
    return float(wet)-float(dry)


def route_equal_mean(route_value_pairs):
    grouped=defaultdict(list)
    for route,value in route_value_pairs:
        grouped[str(route)].append(float(value))
    if not grouped:
        raise ValueError("no eligible routes")
    return float(np.mean([np.mean(v) for v in grouped.values()]))


def coverage_gate(pairs,routes):
    return pairs>=MIN_INFO_PAIRS and routes>=MIN_INFO_ROUTES


def route_summary(df,metric,seed,bootstrap_n=2000):
    if df.empty:
        return {"status":"nonestimable"}
    route_values=df.groupby("route_cluster",sort=True)[metric].mean().to_numpy(dtype=float)
    route_values=route_values[np.isfinite(route_values)]
    n=len(route_values)
    if n<2:
        return {"status":"nonestimable"}
    observed=float(route_values.mean())
    rng=np.random.default_rng(seed)
    bs=route_values[rng.integers(0,n,size=(bootstrap_n,n))].mean(axis=1)
    low,high=np.quantile(bs,[.025,.975])
    # p uses the null-centered bootstrap distribution and is approximate;
    # wet/dry labels were observational and not exchangeable treatment labels.
    centered=bs-observed
    p=float((1+np.sum(np.abs(centered)>=abs(observed)))/(bootstrap_n+1))
    return {"status":"estimated","pairs":int(len(df)),"routes":n,
            "route_equal_mean":observed,
            "ci95_route_bootstrap":[float(low),float(high)],
            "p_two_sided_centered_cluster_bootstrap":p,
            "positive_route_fraction":float(np.mean(route_values>0)),
            "bootstrap_repetitions":bootstrap_n}


def regression(df,response="delta_excess"):
    form=f"{response} ~ rain_contrast + temp_difference + doy_difference + year_gap + C(State) + C(RunNumber)"
    fit=smf.ols(form,data=df).fit(cov_type="cluster",cov_kwds={"groups":df.route_cluster})
    if "rain_contrast" not in fit.params:
        raise ValueError("rain contrast term dropped")
    b=float(fit.params["rain_contrast"])
    se=float(fit.bse["rain_contrast"])
    return {"formula":form,"n_pairs":int(len(df)),
            "n_routes":int(df.route_cluster.nunique()),
            "beta":b,"se_route_cluster":se,
            "ci95":[float(b-Q*se),float(b+Q*se)],
            "p_two_sided":float(fit.pvalues["rain_contrast"]),
            "interpretation":"residual checkerboard units per species pair per unit log-rain-recency contrast"}


def build_sample(raw,runs,source):
    eligible=set(runs.RunID.astype(str))
    sampled,detected=source.stop_matrix(raw,eligible)
    run_sets={str(x.RunID):set() for x in runs.itertuples(index=False)}
    for (rid,st),t in detected.items():
        if rid in run_sets:
            run_sets[rid].update(t)
    if set(run_sets)!=eligible:
        raise RuntimeError("source eligible run universe changed")
    return sampled,detected,run_sets


def extra_identities(raw,needed_ids):
    observer={str(x.get("RunID") or "").strip():str(x.get("ObserverTrackingID") or "").strip()
              for x in raw["Runs.csv"] if str(x.get("RunID") or "").strip() in needed_ids}
    siteids={}
    for item in raw["Stops.csv"]:
        rid=str(item.get("RunID") or "").strip()
        if rid not in needed_ids or str(item.get("SkippedStop") or "").strip()!="0":
            continue
        st=str(item.get("StopNumber") or "").strip()
        sid=str(item.get("SiteID") or "").strip()
        if (rid,st) in siteids and siteids[(rid,st)]!=sid:
            raise ValueError("conflicting SiteID for identical run stop")
        siteids[(rid,st)]=sid
    return observer,siteids


def main(outdir):
    base=load_module("naamp_pinned_base",BASE_SOURCE)
    spatial=load_module("naamp_spatial",SPATIAL_SOURCE)
    raw=base.load()  # SHA256 hard fail, no fallback
    runs,route_sets=base.build_runs(raw)
    pairs=base.pair_runs(runs,route_sets).reset_index(drop=True)
    if len(runs)!=N_RUNS_EXPECTED or len(pairs)!=N_PAIR_EXPECTED:
        raise ValueError(f"original NAAMP population drift: {len(runs)} eligible, {len(pairs)} pairs")
    if pairs.route_cluster.nunique()!=N_ROUTE_EXPECTED or pairs.State.nunique()!=N_STATE_EXPECTED:
        raise ValueError("source route/state coverage drift")
    sampled,detected,localsets=build_sample(raw,runs,spatial)
    for r in runs.RunID.astype(str):
        if localsets[r]!=route_sets[r]:
            raise ValueError("derived taxon incidence differs from original route species list")
    need=set(pairs.wet_RunID.astype(str))|set(pairs.dry_RunID.astype(str))
    observer,siteids=extra_identities(raw,need)
    output={}
    reasons=Counter()
    for i,rid in enumerate(sorted(need),start=1):
        stops=sorted(sampled[rid])
        masks=incidence_masks(stops,{st:detected.get((rid,st),set()) for st in stops})
        if len(masks)<3:
            reasons["fewer_than_3_taxa"]+=1
            output[rid]={"RunID":rid,"informative":False,"reason":"fewer_than_3_taxa",
                         "m_taxa":len(masks),"n_draws":0}
        else:
            null=null_score(list(masks.values()),rid)
            output[rid]={"RunID":rid,**null}
            if not null["informative"]:
                reasons[null["reason"]]+=1
        if i%350==0 or i==len(need):
            print(json.dumps({"completed_run_nulls":i,"target":len(need),
                     "structural_gate_count":sum(v["informative"] for v in output.values())}),
                     flush=True)
    metrics=pd.DataFrame(list(output.values()))
    if metrics.RunID.duplicated().any() or len(metrics)!=len(need):
        raise RuntimeError("null RunID duplicates or missing runs")

    rows=[]
    exclusion=Counter()
    stable_n=0
    same_obs_n=0
    for p in pairs.itertuples(index=False):
        w=str(p.wet_RunID)
        d=str(p.dry_RunID)
        a=output[w]
        b=output[d]
        if not a["informative"] or not b["informative"]:
            exclusion["unidentifiable_margin_on_at_least_one_side"]+=1
            continue
        wet_sites=sorted(sampled[w])
        dry_sites=sorted(sampled[d])
        stable=(wet_sites==dry_sites and all(
            siteids.get((w,s)) and siteids.get((w,s))==siteids.get((d,s))
            for s in wet_sites))
        same_observer=bool(observer.get(w) and observer.get(w)==observer.get(d))
        stable_n+=int(stable)
        same_obs_n+=int(same_observer)
        row=p._asdict()
        row.update({"wet_gamma":a["m_taxa"],"dry_gamma":b["m_taxa"],
                    "wet_active_stops":a["n_active_stops"],
                    "dry_active_stops":b["n_active_stops"],
                    "wet_observed_cscore":a["observed_cscore"],
                    "dry_observed_cscore":b["observed_cscore"],
                    "wet_null_mean_cscore":a["null_mean"],
                    "dry_null_mean_cscore":b["null_mean"],
                    "delta_excess":wet_minus_dry(a["excess"],b["excess"]),
                    "delta_observed":wet_minus_dry(a["observed_cscore"],b["observed_cscore"]),
                    "delta_null_expected":wet_minus_dry(a["null_mean"],b["null_mean"]),
                    "delta_excess_chain_0":wet_minus_dry(
                        a["observed_cscore"]-a["chain_means"][0],
                        b["observed_cscore"]-b["chain_means"][0]),
                    "delta_excess_chain_1":wet_minus_dry(
                        a["observed_cscore"]-a["chain_means"][1],
                        b["observed_cscore"]-b["chain_means"][1]),
                    "stable_physical_siteids":stable,
                    "same_observer":same_observer})
        if not math.isclose(row["delta_excess"],
                            row["delta_observed"]-row["delta_null_expected"],
                            rel_tol=0,abs_tol=1e-10):
            raise RuntimeError("paired residual accounting identity failed")
        rows.append(row)
    valid=pd.DataFrame(rows)
    coverage={"input_runs":len(runs),"input_matched_pairs":len(pairs),
             "input_routes":int(pairs.route_cluster.nunique()),
             "input_states":int(pairs.State.nunique()),
             "unique_matched_runs":len(need),
             "null_informative_runs":int(sum(v["informative"] for v in output.values())),
             "excluded_run_reason":dict(reasons),
             "excluded_pair_reason":dict(exclusion),
             "informative_pairs":len(valid),
             "informative_routes":int(valid.route_cluster.nunique()) if len(valid) else 0,
             "informative_states":int(valid.State.nunique()) if len(valid) else 0,
             "stable_physical_siteid_pairs":stable_n,
             "same_observer_pairs":same_obs_n,
             "conditional_on_row_and_column_totals":True}
    outdir.mkdir(parents=True,exist_ok=True)
    metrics.to_csv(outdir/"run_fixed_margin_null.csv.gz",index=False,compression="gzip")
    if len(valid):
        cols=[c for c in valid if c not in ("ObserverTrackingID",)]
        valid[cols].to_csv(outdir/"matched_checkerboard_pairs.csv.gz",index=False,compression="gzip")
    primary_gate=coverage_gate(coverage["informative_pairs"],coverage["informative_routes"])
    exact=valid[valid.year_gap==1].copy() if len(valid) else valid
    exact_gate=(len(exact)>=MIN_EXACT_PAIRS and exact.route_cluster.nunique()>=MIN_EXACT_ROUTES) if len(valid) else False
    result={
        "analysis":"naamp_fixed_fixed_species_pair_checkerboard_niche_context_v0_1",
        "status":"nonestimable_below_precommitted_support" if not primary_gate
                 else "completed_exploratory_NAAMP_degree_conditioned_survey_comparison",
        "design":"research/FIXED_MARGIN_COMPETITION_NICHE_SPEC_2026-10-19.md",
        "original_NAAMP_source_SHA256":base.PINS,
        "main_source_commit":"0871da0c97d97e2a20156e75fda738d708c82883",
        "coverage":coverage,
        "sample_gates":{"primary":primary_gate,
                        "minimum_pairs":MIN_INFO_PAIRS,"minimum_routes":MIN_INFO_ROUTES,
                        "exact_consecutive_year_gate":bool(exact_gate),
                        "exact_minimum_pairs":MIN_EXACT_PAIRS,
                        "exact_minimum_routes":MIN_EXACT_ROUTES},
        "null":{"method":"Curveball identical taxon breadth/site richness",
                "taxon_minimum":3,"seed":BASE_SEED,
                "chains":CHAINS,"draws_per_chain":DRAWS_PER_CHAIN,
                "burn_per_chain_factor":BURN_FACTOR,
                "spacing_factor":SPACING_FACTOR,
                "metric":PRIMARY_METRIC,
                "all_multispecies_codetection_total_is_fixed":True,
                "explicitly_not_tested_that_total_pairwise_codetections_increase":True,
                "fixed_physical_site_habitat_preference_not_modeled":True},
        "inference_limitations":{
            "frog_interference_competition_not_identified":True,
            "spatiotemporal_niche_mechanism_not_identified":True,
            "matched_rain_recency_is_not_chronological_causal_pulse":True,
            "ten_stops_sequential_not_simultaneous":True,
            "acoustic_detection_not_true_occupancy":True,
            "is_not_independent_replication":True,
            "does_not_change_jae_main":True}}
    if primary_gate:
        result["primary"]={
            "name":"rain_nearer_minus_farther_change_in_degree_conditioned_pair_segregation",
            "primary_route_equal":route_summary(valid,"delta_excess",BASE_SEED+1),
            "wet_route_equal_excess":route_summary(valid,"wet_observed_cscore",BASE_SEED+2),
            "dry_route_equal_observed_cscore":route_summary(valid,"dry_observed_cscore",BASE_SEED+3),
            "no_excess_expected_under_fixed_margin_null":True}
        result["secondary"]=regression(valid)
        result["sensitivity"]={
            "exact_year":route_summary(exact,"delta_excess",BASE_SEED+4)
                         if exact_gate else {"status":"nonestimable_below_precommitted_exact_gate",
                                               "pairs":len(exact),
                                               "routes":int(exact.route_cluster.nunique())},
            "same_physical_siteids":route_summary(valid[valid.stable_physical_siteids],
                    "delta_excess",BASE_SEED+5),
            "same_observer":route_summary(valid[valid.same_observer],
                    "delta_excess",BASE_SEED+6),
            "chain_0":route_summary(valid,"delta_excess_chain_0",BASE_SEED+7),
            "chain_1":route_summary(valid,"delta_excess_chain_1",BASE_SEED+8)}
        null_sd=metrics.loc[metrics.informative,"null_sd"].dropna().to_numpy()
        result["null_diagnostics"]={
            "informative_run_null_sd_median":float(np.median(null_sd)),
            "chain_abs_mean_disagreement_median":float(
                metrics.loc[metrics.informative,"chain_disagreement"].median()),
            "acceptance_rate_chains_mean":float(np.mean([
                np.mean(z) for z in metrics.loc[metrics.informative,
                    "acceptance_rates"] if isinstance(z,list)])),
            "minimum_positive_null_sd":float(np.min(null_sd)),
            "route_equal_aggregate_delta_observed":route_equal_mean(
                list(zip(valid.route_cluster,valid.delta_observed))),
            "route_equal_aggregate_delta_null":route_equal_mean(
                list(zip(valid.route_cluster,valid.delta_null_expected)))}
    (outdir/"RESULT.json").write_text(json.dumps(result,indent=2,sort_keys=True,
                                      allow_nan=False)+"\n",encoding="utf8")
    digest={p.name:hashlib.sha256(p.read_bytes()).hexdigest()
            for p in outdir.glob("*") if p.is_file()}
    (outdir/"SHA256.json").write_text(json.dumps(digest,indent=2,sort_keys=True)+"\n")
    print("RESULT_BEGIN")
    print(json.dumps(result,indent=2,sort_keys=True,allow_nan=False),flush=True)
    print("RESULT_END")
    return result


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--outdir",type=Path,required=True)
    args=parser.parse_args()
    main(args.outdir)
