#!/usr/bin/env python3
"""Taxon-specific strong-calling placement along fixed NAAMP routes versus NWI aquatic emergent cover.

This is exploratory acoustic activity, not vegetation preference behavior or site occupancy.
All eligible taxa are estimated and Benjamini-Hochberg adjusted without selecting significance.
"""
from __future__ import annotations
import argparse
import importlib.util
import json
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.stats.multitest import multipletests

ROOT=Path(__file__).resolve().parents[1]
Z=1.959963984540054
MIN_POSITIVE_STRONG=120
MIN_ACTIVE_RUNS=80
MIN_ROUTES=25
MIN_WITHIN_PEM_RUNS=30

def mod(path):
    spec=importlib.util.spec_from_file_location("nwi_frog_species",path)
    m=importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(m)
    return m

def fit_within_species(df,response):
    cols=["emergent_10pp","allwet_10pp","woody_10pp",
          "stop_temp_c","sound_index","standardized_stop_number"]
    group=df.groupby("RunID",sort=False)
    cols_np=[(df[col].astype(float)-group[col].transform("mean").astype(float)).to_numpy()
             for col in cols]
    X=np.column_stack(cols_np)
    y=(df[response].astype(float)-group[response].transform("mean")).to_numpy()
    rank=int(np.linalg.matrix_rank(X))
    if rank<len(cols):
        return {"status":"nonidentifiable","matrix_rank":rank,"n_predictors":len(cols)}
    fit=sm.OLS(y,X).fit(cov_type="cluster",cov_kwds={"groups":df.route_cluster.astype(str)})
    b=float(fit.params[0]);se=float(fit.bse[0])
    return {"status":"fitted","pem_beta_per_10pp":b,"se_route_cluster":se,
            "ci95":[b-Z*se,b+Z*se],"p_two_sided":float(fit.pvalues[0]),
            "design_rank":rank,"predictors":cols,
            "unit":"difference in probability of CallingIndex≥2 per +10 percentage-point mapped NWI PEM cover"}

def build(raw,runs,nwi,source):
    eligible=set(runs.RunID.astype(str))
    sampled,_=source.spatial.stop_matrix(raw,eligible)
    sites=source.hist.site_map(raw,eligible)
    ci=source.hist.ci_map(raw,eligible,sampled)
    stopenv=source.get_temps_and_detection(raw,runs,sampled)
    by_species=defaultdict(list)
    eligible_runs=0
    dropped={"missing_10_site_nwi_link":0,"duplicate_siteids":0,"missing_ten_stop_conditions":0}
    for run in runs.itertuples(index=False):
        rid=str(run.RunID)
        pair=(str(run.State),str(run.RouteNumber))
        stops=sorted(sampled[rid],key=int)
        if len(stops)!=10:raise RuntimeError("run stop drift")
        siteids=[sites.get((rid,st)) for st in stops]
        if any(sid is None or (*pair,str(sid)) not in nwi.index for sid in siteids):
            dropped["missing_10_site_nwi_link"]+=1
            continue
        if len(set(siteids))!=10:
            dropped["duplicate_siteids"]+=1
            continue
        env=[stopenv.get((rid,st),{}) for st in stops]
        if any(any(not np.isfinite(x.get(field,float("nan"))) for field in ("stop_air_temp_c","stop_sound_index"))
               for x in env):
            dropped["missing_ten_stop_conditions"]+=1
            continue
        plant=nwi.loc[[(pair[0],pair[1],str(sid)) for sid in siteids]]
        plant_250=plant["nwi_emergent_cover_250m"].astype(float).to_numpy()
        wet_250=plant["nwi_all_wetland_cover_250m"].astype(float).to_numpy()
        woody_250=plant["nwi_woody_cover_250m"].astype(float).to_numpy()
        active_taxa=sorted({tax for st in stops
                            for tax,idx in ci.get((rid,st),{}).items() if idx>=2})
        if not active_taxa:
            eligible_runs+=1
            continue
        for taxon in active_taxa:
            for index,st in enumerate(stops):
                intensity=int(ci.get((rid,st),{}).get(taxon,0))
                by_species[taxon].append({
                    "RunID":rid,"State":pair[0],"route_cluster":str(run.route_cluster),
                    "y_strong":int(intensity>=2),
                    "y_any":int(intensity>=1),
                    "emergent_10pp":10*plant_250[index],
                    "allwet_10pp":10*wet_250[index],
                    "woody_10pp":10*woody_250[index],
                    "stop_temp_c":env[index]["stop_air_temp_c"],
                    "sound_index":env[index]["stop_sound_index"],
                    "standardized_stop_number":(int(st)-5.5)/4.5,
                    "pem_raw":plant_250[index]
                })
        eligible_runs+=1
    scope={"eligible_source_runs":int(len(runs)),
           "all_sites_nwi_and_stop_conditions_runs":eligible_runs,
           "n_taxa_with_any_strong_call_on_linked_runs":len(by_species),
           "excluded_reason_counts":dropped}
    return by_species,scope

def run():
    a=argparse.ArgumentParser()
    a.add_argument("--nwi-sites",type=Path,required=True)
    a.add_argument("--nwi-audit",type=Path,required=True)
    a.add_argument("--output",type=Path,default=ROOT/"build"/"aquatic_vegetation_ecology"/"taxon_specific_vegetation_v0_1.json")
    args=a.parse_args()
    source=mod(ROOT/"exploration/run_naamp_aquatic_vegetation_ecological_tests_v0_2.py")
    nwi,audit=source.read_nwi(args.nwi_sites,args.nwi_audit)
    if audit.get("mode")!="full" or len(audit.get("overlay",{}).get("shards",[]))!=12:
        raise RuntimeError("Species analysis requires the geometrically validated FULL 12-shard NWI crosswalk")
    raw=source.hist.load_retry()
    runs,_=source.base.build_runs(raw)
    by_species,scope=build(raw,runs,nwi,source)
    entries=[]
    for taxon in sorted(by_species):
        d=pd.DataFrame(by_species[taxon])
        n_pos=int(d.y_strong.sum())
        nruns=int(d.RunID.nunique())
        nroutes=int(d.route_cluster.nunique())
        varying=int((d.groupby("RunID").pem_raw.nunique()>1).sum())
        record={"taxon":taxon,"positive_strong_sites":n_pos,
                "active_runs":nruns,"routes":nroutes,
                "runs_with_PEM_variation":varying,
                "n_stop_rows":int(len(d))}
        if n_pos<MIN_POSITIVE_STRONG or nruns<MIN_ACTIVE_RUNS or nroutes<MIN_ROUTES or varying<MIN_WITHIN_PEM_RUNS:
            record.update({"status":"ineligible","eligibility_rule_failed":[
                name for name,ok in [
                    ("positive_strong_sites",n_pos>=MIN_POSITIVE_STRONG),
                    ("active_runs",nruns>=MIN_ACTIVE_RUNS),
                    ("routes",nroutes>=MIN_ROUTES),
                    ("runs_with_PEM_variation",varying>=MIN_WITHIN_PEM_RUNS)] if not ok]})
            entries.append(record)
            continue
        primary=fit_within_species(d,"y_strong")
        secondary=fit_within_species(d,"y_any")
        record.update({"status":primary["status"],"primary_strong":primary,
                       "same_runs_any_calling_sensitivity":secondary})
        entries.append(record)
    selected=[x for x in entries if x["status"]=="fitted"]
    if selected:
        p=[x["primary_strong"]["p_two_sided"] for x in selected]
        _,q,_,_=multipletests(p,method="fdr_bh",alpha=.05)
        for entry,qval in zip(selected,q):
            entry["primary_BH_q"]=float(qval)
            entry["primary_BH_significant"]=bool(qval<.05)
    positive=sum(x["primary_strong"]["pem_beta_per_10pp"]>0 for x in selected)
    negative=len(selected)-positive
    supported=[{"taxon":x["taxon"],
                "beta_10pp":x["primary_strong"]["pem_beta_per_10pp"],
                "ci95":x["primary_strong"]["ci95"],"BH_q":x["primary_BH_q"]}
               for x in selected if x["primary_BH_significant"]]
    output={
        "analysis":"naamp_nwi_taxon_specific_aquatic_vegetation_v0_1",
        "status":"posthoc_exploratory_not_RC6",
        "contract":"exploration/NAAMP_FROG_TAXON_VEGETATION_PREFERENCE_CONTRACT_V0_1.md",
        "source_crosswalk":"USFWS NWI response-blind 12-shard run 39450277196",
        "sampling":scope,
        "thresholds":{"min_positive_strong_sites":MIN_POSITIVE_STRONG,
                      "min_active_runs":MIN_ACTIVE_RUNS,
                      "min_routes":MIN_ROUTES,"min_within_PEM_variation_runs":MIN_WITHIN_PEM_RUNS},
        "primary_population":"species×run stop-level Strong CI>=2, restricted to species active on the route-run",
        "model":"within survey-run LPM, route-cluster SE; controls total mapped wetland, woody wetland, air temperature, masking and stop number",
        "summary":{"eligible_taxa":len(selected),"total_taxa_with_strong_calls":len(entries),
                   "positive_PEM_slopes":positive,"negative_PEM_slopes":negative,
                   "BH_FDR_05_taxa":supported},
        "all_taxa":entries,
        "boundaries":{"frog_occupancy_inferred":False,"plant_species_or_real_cover_measured":False,
                      "contemporaneous_2001_2015_plant_vegetation_measured":False,
                      "individual_preference_proven":False,"sampling_conditioned_on_strong_calling":True,
                      "BH_multiplicity_over_all_eligible_taxa":True,
                      "RC6_paper_changed":False}
    }
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(output,indent=2,sort_keys=True,ensure_ascii=False)+"\n",encoding="utf-8")
    print("TAXON_VEGETATION_RESULT_BEGIN",flush=True)
    print(json.dumps(output,sort_keys=True,ensure_ascii=False),flush=True)
    print("TAXON_VEGETATION_RESULT_END",flush=True)

if __name__=="__main__":
    run()
