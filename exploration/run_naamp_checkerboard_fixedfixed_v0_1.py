#!/usr/bin/env python3
"""New, non-RC6 NAAMP checkerboard C-score analysis; fixed-fixed curveball null."""
from __future__ import annotations
import importlib.util
import json
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"build"/"naamp_checkerboard"/"result.json"
SEED=2840260
B=399
Z=1.959963984540054

def loadmod(label, path):
    sp=importlib.util.spec_from_file_location(label,path)
    mod=importlib.util.module_from_spec(sp)
    assert sp.loader
    sp.loader.exec_module(mod)
    return mod

base=loadmod("naamp_checker_base",ROOT/"scripts/naamp/run_naamp_ecological_pulse.py")
spatial=loadmod("naamp_checker_spatial",ROOT/"scripts/naamp/run_naamp_spatial_taxonomic_activation_decomposition.py")

def cscore(rows,nsite=10):
    n=len(rows)
    if n<2:
        return float("nan")
    mat=np.zeros((n,nsite),dtype=np.int16)
    for i,s in enumerate(rows):
        if s:
            mat[i,list(s)]=1
    counts=mat.sum(axis=1)
    overlap=mat@mat.T
    a,b=np.triu_indices(n,1)
    return float(np.mean((counts[a]-overlap[a,b])*(counts[b]-overlap[a,b])))

def exchangeable(rows):
    return any((rows[i]-rows[j]) and (rows[j]-rows[i])
               for i in range(len(rows)) for j in range(i+1,len(rows)))

def curveball(rows,rng,ntrades):
    n=len(rows)
    for _ in range(ntrades):
        i=int(rng.integers(n))
        j=int(rng.integers(n-1))
        if j>=i:
            j+=1
        a=rows[i]-rows[j]
        b=rows[j]-rows[i]
        if not a or not b:
            continue
        common=rows[i]&rows[j]
        pool=sorted(a|b)
        rng.shuffle(pool)
        rows[i]=common|set(pool[:len(a)])
        rows[j]=common|set(pool[len(a):])

def synthetic_qa():
    rng=np.random.default_rng(7726)
    rows=[{0,1,2},{1,3},{2,3,4},{0,4}]
    before_row=[len(r) for r in rows]
    before_col=[sum(j in r for r in rows) for j in range(10)]
    assert exchangeable(rows)
    for _ in range(70):
        curveball(rows,rng,11)
        assert [len(r) for r in rows]==before_row
        assert [sum(j in r for r in rows) for j in range(10)]==before_col
    assert cscore([{0},{1},{2}])>cscore([{0},{0},{0}])
    return "PASS"

def prep_rows(rid, stops, by_stop):
    taxa=sorted(set().union(*(by_stop.get((rid,st),set()) for st in stops)))
    if len(taxa)<3:
        return None,"lt3_taxa"
    index={st:i for i,st in enumerate(stops)}
    rows=[set(index[st] for st in stops if taxon in by_stop.get((rid,st),set()))
          for taxon in taxa]
    if sum(len(z)>=2 for z in rows)<2:
        return None,"lt2_multisite_taxa"
    if len(set().union(*rows))<3:
        return None,"lt3_active_stops"
    if not exchangeable(rows):
        return None,"nonexchangeable"
    return rows,"eligible"

def sample_fixed_fixed(rows, rng):
    original_row=tuple(len(z) for z in rows)
    original_cols=tuple(sum(j in z for z in rows) for j in range(10))
    obs=cscore(rows)
    current=[set(z) for z in rows]
    curveball(current,rng,20*len(rows))
    sim=np.empty(B,dtype=float)
    for b in range(B):
        curveball(current,rng,8*len(rows))
        sim[b]=cscore(current)
        if b in (0,B//2,B-1):
            assert tuple(map(len,current))==original_row, "row-sum drift"
            assert tuple(sum(j in z for z in current) for j in range(10))==original_cols, "column-sum drift"
    return obs,sim

def fit_intercept(d,label):
    if d.empty or d.route_cluster.nunique()<30:
        return {"status":"insufficient_routes"}
    x=np.ones((len(d),1),float)
    fit=sm.OLS(d.excess.astype(float).to_numpy(),x).fit(
        cov_type="cluster",cov_kwds={"groups":d.route_cluster.astype(str)}
    )
    beta=float(fit.params[0]); se=float(fit.bse[0])
    return {"status":"fitted","label":label,
            "n_runs":int(len(d)),"n_routes":int(d.route_cluster.nunique()),
            "mean_excess":beta,"route_cluster_se":se,
            "route_cluster_ci95":[beta-Z*se,beta+Z*se],
            "p_two_sided":float(fit.pvalues[0])}

def fit_wetdry(d,pairs):
    t=pairs.merge(d[["RunID","excess"]].rename(
        columns={"RunID":"wet_RunID","excess":"wet_excess"}),
        on="wet_RunID",how="inner")
    t=t.merge(d[["RunID","excess"]].rename(
        columns={"RunID":"dry_RunID","excess":"dry_excess"}),
        on="dry_RunID",how="inner")
    if t.empty or t.route_cluster.nunique()<30:
        return {"status":"insufficient","n_pairs":int(len(t))}
    t["delta_excess"]=t.wet_excess-t.dry_excess
    fit=smf.ols("delta_excess ~ rain_contrast + temp_difference + doy_difference + year_gap + C(State) + C(RunNumber)",data=t).fit(
        cov_type="cluster",cov_kwds={"groups":t.route_cluster.astype(str)})
    beta=float(fit.params["rain_contrast"])
    se=float(fit.bse["rain_contrast"])
    return {"status":"fitted","n_pairs":int(len(t)),"n_routes":int(t.route_cluster.nunique()),
            "mean_wet_minus_dry_excess":float(t.delta_excess.mean()),
            "rain_contrast_beta":beta,
            "route_cluster_se":se,"route_cluster_ci95":[beta-Z*se,beta+Z*se],
            "p_two_sided":float(fit.pvalues["rain_contrast"]),
            "adjustment":"temperature difference, day-of-year difference, year gap, State, RunNumber"}

def run_mode(mode,runs,sampled,by_stop,rng):
    rows_out=[]
    excluded=defaultdict(int)
    simsum=np.zeros(B,dtype=float)
    n_processed=0
    n_zero_variance=0
    for run in runs.itertuples(index=False):
        rid=str(run.RunID)
        stops=sorted(sampled[rid],key=lambda k:int(k))
        if len(stops)!=10:
            raise RuntimeError("complete-run stop drift")
        rows,reason=prep_rows(rid,stops,by_stop)
        if rows is None:
            excluded[reason]+=1
            continue
        observed,sim=sample_fixed_fixed(rows,rng)
        excess=float(observed-np.mean(sim))
        n_zero_variance+=int(np.ptp(sim)<1e-12)
        simsum+=sim
        n_processed+=1
        rows_out.append({
            "RunID":rid,"route_cluster":str(run.route_cluster),
            "State":str(run.State),"RunNumber":str(run.RunNumber),
            "n_taxa":int(len(rows)),
            "n_active_stops":int(len(set().union(*rows))),
            "observed_cscore":observed,"null_mean":float(np.mean(sim)),
            "null_sd":float(np.std(sim,ddof=1)),
            "excess":excess
        })
        if n_processed%1000==0:
            print(f"{mode}: {n_processed} eligible run nulls completed",flush=True)
    df=pd.DataFrame(rows_out)
    result={"mode":mode,"source_complete_runs":int(len(runs)),
            "eligible_runs":int(len(df)),
            "excluded":dict(sorted(excluded.items())),
            "null_zero_variance_runs":n_zero_variance,
            "minimum_coverage_gate":bool(len(df)>=100 and df.route_cluster.nunique()>=30) if len(df) else False}
    if result["minimum_coverage_gate"]:
        global_obs=float(df.observed_cscore.mean())
        global_null=simsum/len(df)
        result.update({
            "observed_mean_cscore":global_obs,
            "null_mean_cscore":float(global_null.mean()),
            "mean_excess":float(df.excess.mean()),
            "global_fixed_fixed_null_ci95":list(map(float,np.quantile(global_null,[0.025,0.975]))),
            "upper_tail_p":float((1+np.sum(global_null>=global_obs))/(B+1)),
            "lower_tail_p":float((1+np.sum(global_null<=global_obs))/(B+1)),
            "route_clustered_mean_excess":fit_intercept(df,mode)})
    return df,result

def main():
    print("Curveball synthetic margin QA",synthetic_qa(),flush=True)
    raw=base.load()
    runs,sets=base.build_runs(raw)
    eligible=set(runs.RunID.astype(str))
    sampled,all_positive=spatial.stop_matrix(raw,eligible)
    strong=defaultdict(set)
    for rec in raw["Counts.csv"]:
        rid=(rec.get("RunID") or "").strip()
        st=(rec.get("StopNumber") or "").strip()
        sp=(rec.get("Species") or "").strip()
        try:
            ci=int(float((rec.get("CallingIndex") or "").strip()))
        except (TypeError,ValueError):
            continue
        if ci>=2 and ci<=3 and sp and rid in eligible and st in sampled.get(rid,set()):
            strong[(rid,st)].add(sp)
    rng=np.random.default_rng(SEED)
    anydf,anyresult=run_mode("CI1_to_3_primary",runs,sampled,all_positive,rng)
    strongdf,strongresult=run_mode("CI2_to_3_sensitivity",runs,sampled,strong,rng)
    pairs=base.pair_runs(runs,sets)
    anyresult["wet_minus_dry_secondary"]=fit_wetdry(anydf,pairs)
    strongresult["wet_minus_dry_secondary"]=fit_wetdry(strongdf,pairs)
    output={
        "analysis":"naamp_species_checkerboard_v0_1",
        "contract":"exploration/NAAMP_CHECKERBOARD_ENVIRONMENT_CONTRACT_2026_10_20.md",
        "status":"new_exploratory_non_RC6",
        "data":{"standardized_runs":int(len(runs)),"matched_wetter_drier_pairs":int(len(pairs)),
                "routes":int(runs.route_cluster.nunique())},
        "null":{"method":"fixed_fixed_curveball","simulations":B,
                "burn_in_proposals_per_taxon":20,"thinning_proposals_per_taxon":8,
                "random_seed":SEED,"preserve_taxon_depth":True,"preserve_stop_richness":True,
                "synthetic_margins":"PASS"},
        "primary_any_calling":anyresult,
        "secondary_strong_calling":strongresult,
        "interpretation_boundary":{
            "species_competition_identified":False,
            "physical_occupancy_inferred":False,
            "all_environment_controlled":False,
            "local_hydrology_measured":False,
            "global_weather_causality_inferred":False,
            "independent_external_replication":False,
            "RC6_submission_updated":False,
            "fixed_fixed_conditions_on_site_richness_not_full_environment":True}}
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(output,ensure_ascii=False,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    anydf.to_csv(OUT.parent/"primary_run_level.csv",index=False)
    strongdf.to_csv(OUT.parent/"strong_run_level.csv",index=False)
    print("CHECKERBOARD_RESULT_BEGIN")
    print(json.dumps(output,ensure_ascii=False,sort_keys=True))
    print("CHECKERBOARD_RESULT_END",flush=True)

if __name__=="__main__":
    main()
