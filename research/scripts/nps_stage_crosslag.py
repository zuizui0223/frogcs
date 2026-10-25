#!/usr/bin/env python3
"""Exploratory, frozen-design NPS other-species calendar-year call cross-lags.

Read frozen natural-history comparison design:
research/NPS_GREEN_FROG_WOOD_FROG_ACOUSTIC_CROSSLAG_SPEC_2026-10-26.md
SOURCE is one U.S. NPS public-domain CSV with pinned SHA via existing code.
The endpoint is adult CI>=2, never egg/larval survival or predator counts.
"""
from __future__ import annotations
import argparse
import json
import math
import tempfile
from pathlib import Path
import numpy as np
import pandas as pd
from nps_glkn_strict_history import fetch_csv, build_yearly
from nps_glkn_two_way_fe import absorb_two_way, group_codes

SOURCE_SHA = "b1c11cf70472a906e6c238a690a5a12373cdd20ef4d5e180fa3f376d520118c2"
SPEC = "research/NPS_GREEN_FROG_WOOD_FROG_ACOUSTIC_CROSSLAG_SPEC_2026-10-26.md"
GREEN = "Lithobates clamitans"
WOOD = "Lithobates sylvaticus"
BULL = "Lithobates catesbeianus"
TESTS = [
    ("primary_green_prior_to_wood_call", GREEN, WOOD, "primary_negative"),
    ("reverse_wood_prior_to_green_call", WOOD, GREEN, "reverse"),
    ("secondary_green_prior_to_peeper_call", GREEN, "Pseudacris crucifer", "secondary"),
    ("secondary_green_prior_to_american_toad_call", GREEN, "Anaxyrus americanus", "secondary"),
    ("gray_treefrog_context_control", GREEN, "Dryophytes versicolor", "context_control"),
    ("bullfrog_prior_to_wood_call", BULL, WOOD, "secondary_predator_guild"),
]
KEYS=["ParkCode", "SiteLocation", "EventYear"]

def require(ok,msg):
    if not ok: raise ValueError(msg)

def panel_for_pair(annual, exposure, target):
    dat=annual.copy()
    dat["EventYear"] = dat.EventYear.astype(int)
    curr=dat.loc[dat.ScientificName==target,
        KEYS+["strong", "n_species_recordings", "hydroperiod"]].copy()
    curr=curr.rename(columns={"strong":"current_target_strong",
       "n_species_recordings":"current_target_effort"})
    last_target=dat.loc[dat.ScientificName==target,
        KEYS+["strong", "n_species_recordings"]].copy()
    last_target["EventYear"] += 1
    last_target=last_target.rename(columns={"strong":"own_previous_strong",
        "n_species_recordings":"own_previous_effort"})
    last_expo=dat.loc[dat.ScientificName==exposure,
        KEYS+["strong", "n_species_recordings"]].copy()
    last_expo["EventYear"] += 1
    last_expo=last_expo.rename(columns={"strong":"exposure_previous_strong",
        "n_species_recordings":"exposure_previous_effort"})
    other=dat.loc[~dat.ScientificName.isin([exposure,target])].copy()
    generic=other.groupby(KEYS, as_index=False).agg(
        generic_previous_strong_fraction=("strong","mean"),
        generic_previous_taxa_scored=("ScientificName","nunique"))
    generic["EventYear"] += 1
    # Critically: INNER join never converts a species not surveyed in t-1
    # into a zero. Previous must be exactly t-1, not any older occurrence.
    d=curr.merge(last_target,on=KEYS,how="inner",validate="one_to_one")
    d=d.merge(last_expo,on=KEYS,how="inner",validate="one_to_one")
    d=d.merge(generic,on=KEYS,how="left",validate="one_to_one")
    d=d.loc[d.EventYear.between(2017,2023)].copy()
    d["generic_previous_missing"] = d.generic_previous_strong_fraction.isna().astype(int)
    d["generic_previous_strong_fraction"] = d.generic_previous_strong_fraction.fillna(0)
    for c in ("current_target_effort","own_previous_effort","exposure_previous_effort"):
        require((d[c]>0).all(),f"Bad effort in {c}")
        d["log_"+c] = np.log1p(d[c])
    d=d.reset_index(drop=True)
    require(not d.duplicated(KEYS).any(),"Duplicate physical station × year target")
    return d

def exposure_switch_count(d):
    switches=0
    for _,g in d.groupby(["ParkCode","SiteLocation"]):
        g=g.sort_values("EventYear")
        yrs=g.EventYear.to_numpy()
        xs=g.exposure_previous_strong.to_numpy()
        switches += int(np.sum((np.diff(yrs)==1) & (np.diff(xs)!=0)))
    return switches

def fit_fixed_effect_model(df, adjusted=True, override_thresholds=False):
    result={
        "eligible_rows":int(len(df)),
        "parks":int(df.ParkCode.nunique()),
        "stations":int(df.groupby(["ParkCode","SiteLocation"]).ngroups),
        "years":sorted(int(x) for x in df.EventYear.unique()),
        "yearly_park_strata":int(df.groupby(["ParkCode","EventYear"]).ngroups),
        "site_lag_exposure_transitions":exposure_switch_count(df),
        "exposure_levels":{str(k):int(v) for k,v in
            df.exposure_previous_strong.value_counts().items()},
    }
    if (result["parks"] < 3 or result["stations"] < 20
        or result["site_lag_exposure_transitions"] < 10
        or df.exposure_previous_strong.nunique()<2):
        return {**result,"estimable":False,
                "reason":"Insufficient independent parks/stations or within-site previous-year exposure transitions"}
    cols=["current_target_strong","exposure_previous_strong","own_previous_strong"]
    extras=[
       "generic_previous_strong_fraction",
       "log_current_target_effort",
       "log_own_previous_effort",
       "log_exposure_previous_effort",
    ] if adjusted else []
    cols += extras
    z=df[cols].to_numpy(dtype=float)
    require(np.isfinite(z).all(),"Missing or nonfinite acoustic rows")
    a=group_codes(df,["ParkCode","EventYear"])
    b=group_codes(df,["ParkCode","SiteLocation"])
    try:
        w, convergence=absorb_two_way(z,a,b,maxiter=2000,tol=1e-10)
    except Exception as e:
        return {**result,"estimable":False,"reason":"fixed-effect residualization: "+str(e)}
    y=w[:,0]
    core=w[:,1:3]
    if np.linalg.matrix_rank(core,tol=1e-9)!=2:
        return {**result,"estimable":False,
                "reason":"Pair exposure and own-species prior history not independently identified after both fixed effects",
                "core_rank":int(np.linalg.matrix_rank(core,tol=1e-9))}
    keep=[1,2]; dropped=[]
    for j,name in enumerate(extras,3):
        test=w[:,keep+[j]]
        if np.linalg.matrix_rank(test,tol=1e-9)>len(keep):
            keep.append(j)
        else:
            dropped.append(name)
    X=w[:,keep]
    xtx=X.T@X
    if np.linalg.cond(xtx)>1e12:
        return {**result,"estimable":False,"reason":"Rank/conditioning warning",
                "condition":float(np.linalg.cond(xtx))}
    beta=np.linalg.lstsq(X,y,rcond=None)[0]
    e=y-X@beta
    cluster=(df.ParkCode.astype(str)+":"+df.SiteLocation.astype(str)).to_numpy()
    names=np.unique(cluster)
    scores=np.stack([np.einsum("ij,i->j",X[cluster==s],e[cluster==s])
                      for s in names])
    G=len(names); n=len(df); k=X.shape[1]
    bread=np.linalg.inv(xtx)
    cov=(G/(G-1))*((n-1)/(n-k))*(bread@scores.T@scores@bread)
    se=float(math.sqrt(max(0,cov[0,0])))
    baseline=X[:,1:]
    fit_base=np.linalg.lstsq(baseline,y,rcond=None)[0]
    rss0=float(np.sum((y-baseline@fit_base)**2))
    rss1=float(np.sum(e**2))
    return {
        **result,"estimable":True,
        "primary_exposure_previous_year_beta_risk_difference":float(beta[0]),
        "site_cluster_cr1_se":se,
        "site_cluster_approx_ci95":[float(beta[0]-1.96*se),float(beta[0]+1.96*se)],
        "own_previous_year_beta":float(beta[1]),
        "nuisance_kept":[cols[i] for i in keep[2:]],
        "nuisance_dropped":dropped,
        "partial_in_sample_R2_add_exposure_after_own_and_nuisance":
            None if rss0<=0 else float((rss0-rss1)/rss0),
        "residualization":convergence,
        "notes":"Exploratory within-park×year and physical-station FE LPM; in-sample association only. CR1 normal CI diagnostic with few parks, not causal.",
    }

def run_one(annual,label,exposure,target,role):
    d=panel_for_pair(annual,exposure,target)
    primary=fit_fixed_effect_model(d,adjusted=True)
    unadj=fit_fixed_effect_model(d,adjusted=False)
    lopo={}
    for park in sorted(d.ParkCode.unique()):
        dd=d.loc[d.ParkCode!=park]
        v=fit_fixed_effect_model(dd,adjusted=True)
        lopo[str(park)]={"estimable":v["estimable"],
                         "beta":v.get("primary_exposure_previous_year_beta_risk_difference"),
                         "reason":v.get("reason")}
    return {"comparison":label,"role":role,"lag_species":exposure,
            "response_species":target,
            "no_missing_exposure_imputed_to_zero":True,
            "lag_exact_previous_calendar_year":True,
            "main_adjusted":primary,"unadjusted":unadj,
            "leave_one_park_out":lopo}

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--out",type=Path)
    args=parser.parse_args()
    with tempfile.TemporaryDirectory() as d:
        source=Path(d)/"nps_GLKN.csv"
        bytes_read=fetch_csv(source)
        annual,qc=build_yearly(source)
    taxa=set(annual.ScientificName)
    all_named={sp for _,ex,ta,_ in TESTS for sp in (ex,ta)}
    require(all_named.issubset(taxa),
        f"Source-independent frozen species absent: {sorted(all_named-taxa)}")
    outputs=[run_one(annual,*t) for t in TESTS]
    obj={
       "source":"US NPS GLKN DOI 10.57830/2320505, 2016–2023, public domain",
       "source_sha256":SOURCE_SHA,"downloaded_bytes":bytes_read,
       "protocol":SPEC,
       "status":"exploratory_after_frogcs_Rc6_and_NPS_results",
       "source_checks":qc,
       "comparison_count":len(outputs),
       "comparisons":outputs,
       "main_claim_ceiling":"Acoustic year-lag association, not verified aquatic predators, direct predation or recruitment",
       "dryad_carroll_independent_larval_validation":False,
       "RC6_manuscript_reanalysed":False,
    }
    if args.out:
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(json.dumps(obj,indent=2,ensure_ascii=False)+"\n",
                            encoding="utf-8")
    print("BEGIN_NPS_STAGE_CROSSLAG_RESULTS")
    print(json.dumps(obj,indent=2,ensure_ascii=False))
    print("END_NPS_STAGE_CROSSLAG_RESULTS")
if __name__=="__main__":main()
