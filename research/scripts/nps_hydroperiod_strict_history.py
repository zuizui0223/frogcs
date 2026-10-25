#!/usr/bin/env python3
"""NPS frog acoustic history moderated by field-recorded Hydroperiod classes.

Exploratory after original past-call effects seen. The classes Ephemeral,
Semi-permanent, Permanent are NOT USFWS NWI PEM1A/C/F polygon labels.
Original 147913 scored public NPS 2016–2023 source SHA checked.
Contract research/NPS_HYDROPERIOD_HISTORY_MODERATION_SPEC_2026-10-25.md
"""
from __future__ import annotations
import argparse
import collections
import json
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd

from nps_glkn_strict_history import (
    fetch_csv, build_yearly, strict_prior_panel,
    informative_groups, fit_with_block_bootstrap, PERIOD
)

CLASSES=("Ephemeral","Semi-permanent","Permanent")
SEED=20261025


def three_way_model(panel,nboot=2000):
    d=panel.loc[panel.hydroperiod.isin(CLASSES)].copy()
    d["prior_strong_x_semi"]=(d.prior_strong *
                                  (d.hydroperiod=="Semi-permanent").astype(int))
    d["prior_strong_x_permanent"]=(d.prior_strong *
                                  (d.hydroperiod=="Permanent").astype(int))
    d["hydro_semi"]=(d.hydroperiod=="Semi-permanent").astype(int)
    d["hydro_permanent"]=(d.hydroperiod=="Permanent").astype(int)
    d["other_prior_missing"]=d.other_prior_strong_fraction.isna().astype(int)
    d["other_prior_fixed"]=d.other_prior_strong_fraction.fillna(0)

    core=["prior_strong","prior_strong_x_semi","prior_strong_x_permanent"]
    other=["hydro_semi","hydro_permanent",
           "other_prior_fixed","other_prior_missing",
           "log_current_effort","log_prior_effort","prior_years_seen"]
    cols=core+other
    grp=d.groupby(PERIOD,sort=False)
    de=d[cols+["strong"]].astype(float)-grp[cols+["strong"]].transform("mean")
    X0=de[core].to_numpy()
    y=de["strong"].to_numpy()
    if np.linalg.matrix_rank(X0,tol=1e-10)<3:
        return {"estimable":False,
                "reason":"Hydroperiod interaction directions not all identifiable",
                "n_rows":len(d),
                "n_focal_predictor_rank":int(np.linalg.matrix_rank(X0))}
    X=X0.copy()
    kept=[]
    dropped=[]
    for name in other:
        candidate=np.column_stack([X,de[name].to_numpy()])
        if np.linalg.matrix_rank(candidate,tol=1e-9)>X.shape[1]:
            X=candidate
            kept.append(name)
        else:
            dropped.append(name)
    p=X.shape[1]
    fit=np.linalg.lstsq(X,y,rcond=None)[0]
    clusters=(d.ParkCode.astype(str)+":"+
              d.ScientificName.astype(str)).to_numpy()
    ids=np.unique(clusters)
    gram=np.stack([X[clusters==cl].T @ X[clusters==cl] for cl in ids])
    cross=np.stack([X[clusters==cl].T @ y[clusters==cl] for cl in ids])
    rng=np.random.default_rng(SEED+len(d))
    sampled=rng.integers(0,len(ids),size=(nboot,len(ids)))
    vec=np.array([[1,0,0],[1,1,0],[1,0,1],[0,1,0],[0,0,1]],
                 dtype=float)
    vt=np.zeros((5,p));vt[:,:3]=vec
    names=["Ephemeral","Semi-permanent","Permanent",
           "Semi_minus_Ephemeral","Permanent_minus_Ephemeral"]
    point=vt@fit
    draws=[]
    for ix in sampled:
        xx=gram[ix].sum(axis=0)
        if np.linalg.matrix_rank(xx,tol=1e-9)<p:
            continue
        beta=np.linalg.solve(xx,cross[ix].sum(axis=0))
        draws.append(vt@beta)
    boot=np.stack(draws) if draws else np.empty((0,5))
    result={}
    for j,name in enumerate(names):
        result[name]={
            "coefficient_risk_difference_scale":float(point[j]),
            "cluster_bootstrap_ci95":list(np.quantile(boot[:,j],[.025,.975]).astype(float))
                 if len(boot)>=500 else None,
        }
    return {
        "estimable":True,
        "sample_rows":len(d),
        "strata_park_taxon_year":int(d.groupby(PERIOD).ngroups),
        "park_taxon_trajectory_clusters":len(ids),
        "nuisance_covariates_kept":kept,
        "nuisance_rank_dropped":dropped,
        "n_params":p,
        "valid_bootstrap_draws":len(draws),
        "hydroperiod_prior_strong_slope":result,
        "method":"within park×frog taxon×year demeaned LPM with prior-site "
                 "history × broad hydroperiod class and source-linked effort",
        "interpretation":"posthoc association only; no NWI PEM field assignment"
    }


def within_class_stratified(panel,nboot=2000):
    out=[]
    for category in CLASSES:
        d=panel.loc[panel.hydroperiod==category].copy()
        qual, ngroups=informative_groups(d)   # original ≥4 + history variation
        z=fit_with_block_bootstrap(
            qual, "strong",True,nboot,seed=SEED+33)
        out.append({
            "NPS_Hydroperiod":category,
            "all_original_informative_rows_in_class":len(d),
            "ever_strong_before":int(d.prior_strong.sum()),
            "later_strong_total":int(d.strong.sum()),
            "distinct_sites":int(d.SiteLocation.nunique()),
            "candidate_strata":ngroups,
            "within_category_informative_rows":len(qual),
            "within_category_informative_strata":int(
                qual.groupby(PERIOD).ngroups) if len(qual) else 0,
            "strict_prior_strong_slope_after_covariates":z,
        })
    return out


def selftest():
    rng=np.random.default_rng(20)
    tmp=[]
    for cl in CLASSES:
        for k in range(5):
            for name in ["Anaxyrus americanus","Pseudacris crucifer"]:
                for site in range(8):
                    history=int(site%2==0)
                    y=int(rng.random()<(.1+.5*history))
                    tmp.append({
                        "ParkCode":"P",
                        "SiteLocation":f"{cl}{site}",
                        "ScientificName":name,
                        "EventYear":2017+k,
                        "hydroperiod":cl,
                        "strong":y,"prior_strong":history,
                        "other_prior_strong_fraction":.2,
                        "log_current_effort":1.7,
                        "log_prior_effort":1.8,
                        "prior_years_seen":1
                    })
    d=pd.DataFrame(tmp)
    o=three_way_model(d,nboot=30)
    assert o["estimable"] and o["sample_rows"]==len(d)
    for name in CLASSES:
        assert o["hydroperiod_prior_strong_slope"][name]["coefficient_risk_difference_scale"]>0
    assert within_class_stratified(d,nboot=20)[0]["distinct_sites"]==8
    print("NPS_HYDROPERIOD_STRONG_SITE_HISTORY_SYNTHETIC_QA_PASS")


def main():
    a=argparse.ArgumentParser()
    a.add_argument("--output",default="research/results/nps_hydroperiod_history")
    a.add_argument("--bootstrap",type=int,default=2000)
    a.add_argument("--self-test",action="store_true")
    opt=a.parse_args()
    if opt.self_test:
        selftest()
        return
    with tempfile.TemporaryDirectory() as td:
        temp=Path(td)/"source.csv"
        source_bytes=fetch_csv(temp)
        annual,source_qc=build_yearly(temp)
    panel=strict_prior_panel(annual)
    informative,noriginal=informative_groups(panel)
    if len(informative)!=1815:
        raise RuntimeError(f"Original 1815-row tested sample changed: {len(informative)}")
    observed_hydro=set(informative.hydroperiod)
    if observed_hydro!=set(CLASSES):
        raise RuntimeError(f"Observed Hydroperiod classes do not match: {observed_hydro}")
    census=[]
    for cat in CLASSES:
        sub=informative.loc[informative.hydroperiod==cat]
        for prior in [0,1]:
            ss=sub.loc[sub.prior_strong==prior]
            census.append({
                "NPS_Hydroperiod":cat,
                "strict_prior_strong_ci2plus":prior,
                "site_taxon_year_cells":len(ss),
                "later_strong_ci2plus_cells":int(ss.strong.sum()),
                "later_strong_fraction":float(ss.strong.mean()) if len(ss) else None,
                "distinct_siteIDs":int(ss.SiteLocation.nunique()),
                "park_taxon_trajectories":int(ss.groupby(
                    ["ParkCode","ScientificName"]).ngroups),
            })
    combined=three_way_model(informative,opt.bootstrap)
    stratified=within_class_stratified(informative,opt.bootstrap)
    report={
        "source":"NPS GLKN public-domain DOI 10.57830/2320505",
        "method":"Posthoc hydrological-broad-class moderation of prior own-species strong acoustic site",
        "not_nwi_pem":True,
        "source_sha256":"b1c11cf70472a906e6c238a690a5a12373cdd20ef4d5e180fa3f376d520118c2",
        "input_original_audio_file_bytes":source_bytes,
        "original_strict_prior_sample_1815":len(informative),
        "original_eligible_strata":int(informative.groupby(PERIOD).ngroups),
        "source_qc_summary":source_qc,
        "original_samples_hydroperiod_and_history":census,
        "main_interaction":combined,
        "additional_within_hydroperiod_strata":stratified,
        "constraints":[
            "These are NPS field Hydroperiod labels, not USFWS NWI PEM1A/C/F map codes and not contemporaneous pond water depths.",
            "Fixed recorder SiteLocation strings have no verified geocoordinates in NPS audio CSV; do not assign to arbitrary NWI polygons.",
            "The original NPS strong-site history effect may reflect persistent species-specific habitat and detectability, not same frog revisiting a pond.",
            "Interaction and within-class results are exploratory after main NPS effect was seen, not independently prespecified JAE endpoints.",
            "65+ reported station/taxon/year cells are not independent reproducing breeding populations.",
            "No salamander/dragonfly aquatic stage observation, aquatic predator attack, emergent stem density or adult chorus to tadpole recruitment data.",
        ]
    }
    out=Path(opt.output);out.mkdir(parents=True,exist_ok=True)
    (out/"observed_results.json").write_text(
        json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf8")
    print("BEGIN_NPS_HYDROPERIOD_HISTORY_EFFECT")
    print(json.dumps(report,indent=2,ensure_ascii=False))
    print("END_NPS_HYDROPERIOD_HISTORY_EFFECT")


if __name__=="__main__":
    main()
