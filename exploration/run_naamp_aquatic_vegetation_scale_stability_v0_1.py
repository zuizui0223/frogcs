#!/usr/bin/env python3
"""Pre-specified radius sensitivity (100/250/500m) + post-hoc State-block stability.

Runs on frozen source-only full NWI crosswalk and frozen NAAMP checkerboard
responses; does not optimize radii or edit RC6 evidence.
"""
from __future__ import annotations
import argparse
import importlib.util
import json
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

ROOT=Path(__file__).resolve().parents[1]
Z=1.959963984540054
RADII=(100,250,500)
CATEGORIES=("all_wetland","emergent","aquatic_bed","woody")
FORMULA=("excess ~ nwi_emergent_variance + nwi_emergent_mean + "
         "nwi_aquatic_bed_mean + nwi_wetland_mean + nwi_woody_variance + "
         "mean_air_c + np.log1p(days_since_rain) + survey_year + "
         "C(State) + C(RunNumber)")

def getmodule(path):
    spec=importlib.util.spec_from_file_location("aquatic_veg_full_ecology",path)
    m=importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(m)
    return m

def checkerboard_rows(source,runs,ref,nwi,sites,sampled,radius):
    # Replicates source function's fixed-run sample with explicit radius.
    runmap=runs.set_index("RunID",drop=False)
    out=[]
    for rr in ref.itertuples(index=False):
        rid=str(rr.RunID)
        if rid not in runmap.index:
            continue
        row=runmap.loc[rid]
        state=str(row.State);route=str(row.RouteNumber)
        stops=sorted(sampled[rid],key=int)
        if len(stops)!=10:
            continue
        sid=[sites.get((rid,st)) for st in stops]
        if any(x is None or (state,route,str(x)) not in nwi.index for x in sid):
            continue
        v=nwi.loc[[(state,route,str(x)) for x in sid]]
        em=v[f"nwi_emergent_cover_{radius}m"].astype(float)
        bed=v[f"nwi_aquatic_bed_cover_{radius}m"].astype(float)
        woody=v[f"nwi_woody_cover_{radius}m"].astype(float)
        allwet=v[f"nwi_all_wetland_cover_{radius}m"].astype(float)
        out.append({
            "RunID":rid,"route_cluster":str(row.route_cluster),
            "State":state,"RunNumber":str(row.RunNumber),
            "survey_year":float(row.SurveyYear),
            "mean_air_c":float(row.mean_temp_c),
            "days_since_rain":float(row.DaysSinceRain),
            "nwi_emergent_variance":float(em.var(ddof=0)),
            "nwi_emergent_mean":float(em.mean()),
            "nwi_aquatic_bed_mean":float(bed.mean()),
            "nwi_wetland_mean":float(allwet.mean()),
            "nwi_woody_variance":float(woody.var(ddof=0)),
            "excess":float(rr.excess)
        })
    return pd.DataFrame(out)

def checkerboard_fit(d,cluster):
    if d.empty or d.route_cluster.nunique()<30 or d.State.nunique()<8:
        return {"status":"insufficient"}
    if d.nwi_emergent_variance.nunique()<3:
        return {"status":"no_spatial_variation"}
    fit=smf.ols(FORMULA,data=d).fit(cov_type="cluster",
                                  cov_kwds={"groups":d[cluster].astype(str)})
    name="nwi_emergent_variance"
    b=float(fit.params[name]);se=float(fit.bse[name])
    return {
        "status":"fitted","cluster":cluster,
        "n_runs":int(len(d)),"n_routes":int(d.route_cluster.nunique()),
        "n_states":int(d.State.nunique()),
        "beta":b,"route_or_state_cluster_se":se,
        "ci95":[b-Z*se,b+Z*se],
        "p":float(fit.pvalues[name]),
        "emergent_variance_sd":float(d.nwi_emergent_variance.std(ddof=0)),
        "one_sd_change_in_cscore_residual":float(b*d.nwi_emergent_variance.std(ddof=0)),
        "emergent_variance_q25_q75":[float(x) for x in d.nwi_emergent_variance.quantile([.25,.75])],
        "emergent_variance_q10_q90":[float(x) for x in d.nwi_emergent_variance.quantile([.1,.9])]
    }

def run():
    p=argparse.ArgumentParser()
    p.add_argument("--nwi-sites",required=True,type=Path)
    p.add_argument("--nwi-audit",required=True,type=Path)
    p.add_argument("--checkerboard",required=True,type=Path)
    p.add_argument("--out",type=Path,default=ROOT/"build"/"aquatic_vegetation_ecology"/"scale_stability_v0_1.json")
    args=p.parse_args()
    full=getmodule(ROOT/"exploration/run_naamp_aquatic_vegetation_ecological_tests_v0_2.py")
    nwi,audit=full.read_nwi(args.nwi_sites,args.nwi_audit)
    assert audit["mode"]=="full" and len(audit["overlay"]["shards"])==12,"not full geometry"
    raw=full.hist.load_retry()
    runs,sets=full.base.build_runs(raw)
    d,coverage,sites,sampled,pairs=full.build_history(raw,runs,sets,nwi)
    if d.empty:raise RuntimeError("No history pairs with full validated vegetation crosswalk")
    for j in range(2,11):
        d[f"stop_number_{j}"]=(d.stop_number.astype(int)==j).astype(float)
    positions=[f"stop_number_{j}" for j in range(2,11)]
    basecov=["stop_air_temp_c","stop_sound_index","other_taxa_strong"]+positions
    allcov=[f"nwi_{cat}_cover_{radius}m" for radius in RADII for cat in CATEGORIES]
    complete=d.dropna(subset=["prior_site_strong","wet_strong"]+basecov+allcov).copy()
    informative=complete.groupby("pair_species").prior_site_strong.nunique()
    complete=complete[complete.pair_species.isin(informative[informative>1].index)].copy()
    base=full.within_model(complete,[],"common_all_three_radii_history_baseline")
    if base["status"]!="fitted":
        raise RuntimeError("History sensitivity sample insufficient, no radius inference")
    ref=pd.read_csv(args.checkerboard,dtype={"RunID":str})
    results={}
    details={}
    for radius in RADII:
        present=complete.copy()
        nwiradius=nwi.copy()
        for category in CATEGORIES:
            c250=f"nwi_{category}_cover_250m"
            current=f"nwi_{category}_cover_{radius}m"
            present[c250]=present[current]
            nwiradius[c250]=nwiradius[current]
        histpred=[f"nwi_{category}_cover_250m" for category in CATEGORIES]+basecov
        m1=full.within_model(present,histpred,f"{radius}m_adjusted_history")
        m2=full.within_model(present,histpred+["history_x_emergent"],f"{radius}m_history_emergent_interaction")
        bd=checkerboard_rows(full,runs,ref,nwi,sites,sampled,radius)
        route_model=checkerboard_fit(bd,"route_cluster")
        state_model=checkerboard_fit(bd,"State")
        results[str(radius)]={
            "historical_vegetation_adjusted":m1,
            "historical_use_x_emergent_vegetation":m2,
            "checkerboard_emergent_variance_route_cluster":route_model,
            "checkerboard_emergent_variance_state_cluster":state_model
        }
        if radius==250:
            omit=[]
            for state in sorted(bd.State.unique()):
                more=bd.loc[bd.State!=state].copy()
                z=checkerboard_fit(more,"route_cluster")
                if z["status"]=="fitted":
                    omit.append({"omitted_state":state,"beta":z["beta"],
                                 "ci95":z["ci95"],"p":z["p"],"n_routes":z["n_routes"]})
            details["leave_one_state_out_250m"]=omit
            details["leave_state_summary_250m"]={
                "n_fits":len(omit),
                "negative_coefficients":sum(x["beta"]<0 for x in omit),
                "negative_ci_excluding_zero":sum(x["ci95"][1]<0 for x in omit),
                "range_beta":[min(x["beta"] for x in omit),max(x["beta"] for x in omit)] if omit else None,
                "max_p":max((x["p"] for x in omit),default=None)}
    out={
        "analysis":"naamp_aquatic_vegetation_scale_stability_v0_1",
        "status":"posthoc_exploratory_sensitivity_not_independent_confirmation",
        "source_full_run":39450277196,
        "checkerboard_source_run":39436588431,
        "study_coverage":coverage,
        "identical_history_sample_across_radii":{
            "n_stop_rows":int(len(complete)),
            "n_species_pair_groups":int(complete.pair_species.nunique()),
            "n_routes":int(complete.route_cluster.nunique())},
        "historical_use_same_sample_baseline":base,
        "radii":results,
        "checkerboard_leave_one_state_out":details,
        "inferential_boundaries":{
            "fixed_radii_before_result_readback":[100,250,500],
            "leave_state_out_is_posthoc_stability_diagnostic":True,
            "reselect_radius_by_lowest_p":False,
            "NWI_time_matched_to_frog_survey":False,
            "local_hydrology_observed":False,
            "species_competition_caused_by_plants":False,
            "RC6_paper_changed":False
        }}
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(out,indent=2,ensure_ascii=False,sort_keys=True)+"\n")
    print("NAAMP_AQUATIC_VEG_SCALE_RESULT_BEGIN",flush=True)
    print(json.dumps(out,sort_keys=True,ensure_ascii=False),flush=True)
    print("NAAMP_AQUATIC_VEG_SCALE_RESULT_END",flush=True)

if __name__=="__main__":
    run()
