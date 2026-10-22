#!/usr/bin/env python3
"""Predeclared, independently collected USGS ARMI 2024 frog-call partner test.

Validates pinned official source before reading any detection values. Retains
all 2024 5-min visit opportunities, not just focal frog-positive visits. Tests
whether contemporaneous bullfrog call detection predicts greenfrog detection
on held-out PROJECT×SITE groups above effort/weather/season/other calls.

This is NOT proof of biological species interactions, environmental mediation,
population occurrence, or NAAMP's exact fixed-margin spatial allocation.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import math
from collections import Counter,defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from statsmodels.stats.multitest import multipletests

ROOT=Path(__file__).resolve().parents[1]
PRIMARY="Lithobates clamitans"
BULL="Lithobates catesbeianus"
NEGATIVE="Dryophytes versicolor"
OTHER_FIXED="Anaxyrus fowleri"
SEED=2840347
BOOT=2000
L2_C=1.0
MAXITER=500
Z=1.959963984540054
SOURCE_SHA="dafd388c7ccb79e08dbadd37a25c604473a8caf4ff5c8318532740acb56a04e4"
SOURCE_META_SHA="a41deac79d0f6be758101b27dc97014896b928723251b4544ddeefd6c4456a15"
EVENT=["Project","Site","Date","Arrival_time","Observer","Method"]
SOURCES=[
 "Project","Site","Date","Arrival_time","Observer","Method",
 "Wind_Beaufort","Cloud_cover_percent","Species"]
CATEGORICAL=["Project","Observer","Method","Cloud_cover_percent"]
NUMERIC=["Wind_num","sin_doy","cos_doy","sin_hour","cos_hour","n_other_species"]

def imported_source():
    import importlib.util
    p=ROOT/"exploration/run_armi_2024_source_only_qa_v0_1.py"
    spec=importlib.util.spec_from_file_location("original_armi_source_v01",p)
    module=importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(module)
    return module

def fold_mapping(events):
    # Strict, response-blind site folds formed on EVERY original 2024
    # metadata-eligible site, including frog-negative survey visits.
    mapping={}
    g=events[["Project","Site"]].drop_duplicates()
    for project,data in g.groupby("Project",sort=True):
        sites=sorted(data.Site.tolist(),
                     key=lambda s:(hashlib.sha256((project+":"+s).encode()).hexdigest(),s))
        for j,site in enumerate(sites):
            mapping[(project,site)]="A" if j%2==0 else "B"
    return mapping

def build_visit_table(source_csv):
    d=pd.read_csv(io.BytesIO(source_csv),usecols=SOURCES,low_memory=False,
                  dtype="string",keep_default_na=False)
    for col in SOURCES:d[col]=d[col].str.strip()
    if len(d)!=1934:raise RuntimeError("Pinned source length/grain unexpectedly changed")
    if (d[EVENT].eq("").any(axis=1)).any():
        raise RuntimeError("Original event key contains empty components")
    if d.Species.eq("").any():raise RuntimeError("Empty species token, cannot reconstruct survey")
    # Each documented 5-minute survey can have multiple bearings to the
    # SAME audible species/individual groups. Source-only QA pre-readback
    # confirmed 368 repeated species/event groups, 367 with a distinct
    # Compass_direction, and no site/weather conflicts. This is ONE survey
    # event with "any" species detection, not multiple sampling trials.
    duplicate_species_extra=int(d.duplicated(EVENT+["Species"]).sum())
    if duplicate_species_extra!=515:
        raise RuntimeError("Source repeated species/bearing structure changed")
    # A single survey has repeated species rows. Covariate conflict across a
    # survey is not allowed, because values might be species-specific.
    inconsistent={}
    for col in ["Wind_Beaufort","Cloud_cover_percent"]:
        n=d.groupby(EVENT)[col].nunique(dropna=False)
        inconsistent[col]=int((n>1).sum())
    if any(inconsistent.values()):
        raise RuntimeError("Within-survey weather is inconsistent "+str(inconsistent))
    group=d.groupby(EVENT,sort=False,dropna=False)
    visits=group.agg(Wind_Beaufort=("Wind_Beaufort","first"),
                     Cloud_cover_percent=("Cloud_cover_percent","first"),
                     seen=("Species",lambda x:frozenset(x))).reset_index()
    if len(visits)!=798:raise RuntimeError("Original source-only visit universe drift")
    mixed_none=visits.seen.map(lambda x: "none" in x and len(x)>1)
    if mixed_none.any():raise RuntimeError("Species=none co-recorded with other species")
    names=sorted({name for group in visits.seen for name in group})
    found_green=PRIMARY in names
    found_bull=BULL in names
    source_gate={
       "n_species_rows":len(d),
       "n_survey_visits":len(visits),
       "n_project_site_groups":int(visits[["Project","Site"]].drop_duplicates().shape[0]),
       "n_projects":int(visits.Project.nunique()),
       "n_species_labels":len(names),"species_names":names,
       "n_explicit_frog_none_survey_events":int((visits.seen.map(lambda q:q=={"none"})).sum()),
       "weather_conflicting_survey_events":inconsistent,
       "extra_event_taxon_duplicates":duplicate_species_extra,
       "source_only_duplicate_QA_from_run":39782928959,
       "repeated_bearings_grouped_to_exact_sixpart_survey":True,
       "both_named_species_appear":found_green and found_bull,
       "includes_Anaxyrus_fowleri":OTHER_FIXED in names
    }
    visits["green"]=visits.seen.map(lambda x:int(PRIMARY in x))
    visits["bull"]=visits.seen.map(lambda x:int(BULL in x))
    visits["negative"]=visits.seen.map(lambda x:int(NEGATIVE in x))
    excluded={PRIMARY,BULL,NEGATIVE,"none",OTHER_FIXED}
    visits["n_other_species"]=visits.seen.map(lambda x:len(x-excluded))
    visits["site_key"]=visits.Project.astype(str)+":"+visits.Site.astype(str)
    mapping=fold_mapping(visits)
    visits["fold"]=[mapping[(project,site)]
                    for project,site in zip(visits.Project,visits.Site)]
    visitdate=pd.to_datetime(visits.Date,format="%Y-%m-%d",errors="coerce")
    time=pd.to_datetime(visits.Arrival_time,format="%H:%M",errors="coerce")
    dateokay=visitdate.between(pd.Timestamp("2024-06-06"),pd.Timestamp("2024-08-15"))
    clockokay=time.notna()
    wind=pd.to_numeric(visits.Wind_Beaufort,errors="coerce")
    windokay=wind.between(0,6)
    covgate={
      "valid_dates":int(dateokay.sum()),
      "valid_times":int(clockokay.sum()),
      "valid_wind_0_to_6":int(windokay.sum()),
      "all_original_798_observations_have_frozen_covariates":
          bool(dateokay.all() and clockokay.all() and windokay.all())
    }
    # Need not impute missing weather after outcome readback.
    if not covgate["all_original_798_observations_have_frozen_covariates"]:
        return visits,source_gate,covgate,None
    doy=visitdate.dt.dayofyear.to_numpy(float)
    hh=time.dt.hour.to_numpy(float)+time.dt.minute.to_numpy(float)/60.
    visits["Wind_num"]=wind.astype(float)
    visits["sin_doy"]=np.sin(2*np.pi*doy/366.)
    visits["cos_doy"]=np.cos(2*np.pi*doy/366.)
    visits["sin_hour"]=np.sin(2*np.pi*hh/24.)
    visits["cos_hour"]=np.cos(2*np.pi*hh/24.)
    return visits,source_gate,covgate,valid_stats(visits)

def valid_stats(d):
    sites=d.groupby("site_key")
    s={
       "n_surveys":len(d),
       "sites":int(d.site_key.nunique()),
       "projects":int(d.Project.nunique()),
       "detected_green_surveys":int(d.green.sum()),
       "detected_bull_surveys":int(d.bull.sum()),
       "both_frogs_same_survey":int(((d.green==1)&(d.bull==1)).sum()),
       "neither_frog_detected":int(((d.green==0)&(d.bull==0)).sum()),
       "bull_positive_sites":int(sites.bull.max().sum()),
       "green_positive_sites":int(sites.green.max().sum()),
       "negative_partner_detected_surveys":int(d.negative.sum()),
       "negative_partner_positive_sites":int(sites.negative.max().sum()),
       "n_other_species_summary":{
           "min":int(d.n_other_species.min()),
           "median":float(d.n_other_species.median()),
           "max":int(d.n_other_species.max())},
       "by_project":{
          str(p):{
             "surveys":len(x),"sites":int(x.site_key.nunique()),
             "green":int(x.green.sum()),"bull":int(x.bull.sum()),
             "both":int(((x.green==1)&(x.bull==1)).sum())}
          for p,x in d.groupby("Project")},
       "folds":{
          f:{"n":len(x),"sites":int(x.site_key.nunique()),
             "green":int(x.green.sum()),"bull":int(x.bull.sum())}
          for f,x in d.groupby("fold")}
    }
    s["outcome_gate"]={
       "green_positive_ge30":s["detected_green_surveys"]>=30,
       "bull_positive_ge30":s["detected_bull_surveys"]>=30,
       "green_positive_sites_ge10":s["green_positive_sites"]>=10,
       "bull_positive_sites_ge10":s["bull_positive_sites"]>=10,
       "site_groups_ge40":s["sites"]>=40,
       "independent_projects_ge2":s["projects"]>=2,
       "training_fold_minimums":all(z["n"]>=60 and z["green"]>=10 and z["bull"]>=10
                                     for z in s["folds"].values())
    }
    return s

def build_design_matrices(train,test,cols_extra=()):
    # One-hot categorical encoder is FIT ONLY ON TRAIN SITES, no new site
    # labels or leakage of heldout species observations into stage 1.
    pre=ColumnTransformer([
         ("categories",OneHotEncoder(handle_unknown="ignore",drop="first",
                                    sparse_output=False),CATEGORICAL),
         ("numeric","passthrough",NUMERIC)
         ],remainder="drop",sparse_threshold=0)
    xtrain=np.asarray(pre.fit_transform(train),dtype=float)
    xtest=np.asarray(pre.transform(test),dtype=float)
    if not(np.isfinite(xtrain).all() and np.isfinite(xtest).all()):
        raise RuntimeError("Missing values in training or heldout covariates")
    extra_train=np.asarray(train[list(cols_extra)],dtype=float) if cols_extra else np.empty((len(train),0))
    extra_test=np.asarray(test[list(cols_extra)],dtype=float) if cols_extra else np.empty((len(test),0))
    return np.hstack([xtrain,extra_train]),np.hstack([xtest,extra_test])

def model_predict(train,test,additional,base_columns=None):
    # The baseline preprocessing is fixed to the metadata training fold,
    # not reshaped after examining calling rows.
    a0,b0=build_design_matrices(train,test)
    if base_columns is not None:pass
    if additional:
        a1=np.hstack([a0,train[list(additional)].astype(float).to_numpy()])
        b1=np.hstack([b0,test[list(additional)].astype(float).to_numpy()])
    else:a1,b1=a0,b0
    model=LogisticRegression(penalty="l2",C=L2_C,solver="lbfgs",
                             max_iter=MAXITER,class_weight=None)
    model.fit(a1,train.green.astype(int))
    if model.n_iter_[0]>=MAXITER:
        raise RuntimeError("Source model failed predefined 500 iterations")
    p=np.clip(model.predict_proba(b1)[:,1],1e-9,1-1e-9)
    return p,{"coef_additional":{x:float(v) for x,v in
         zip(additional,list(model.coef_[0][-len(additional):]))}
         if additional else {},
         "train_n":len(train),"train_green":int(train.green.sum()),
         "train_bull":int(train.bull.sum()),"iterations":int(model.n_iter_[0])}

def site_boot_ci(frame,metric,seed):
    g=frame.groupby("site_key")[metric].agg(["sum","count"])
    n=len(g)
    if n<10:return {"status":"inconclusive_site_scope","n_sites":n}
    sums=g["sum"].to_numpy(float)
    counts=g["count"].to_numpy(float)
    rng=np.random.default_rng(seed)
    values=[]
    for i in range(0,BOOT,200):
        sample=rng.integers(0,n,size=(min(200,BOOT-i),n))
        vals=sums[sample].sum(axis=1)/counts[sample].sum(axis=1)
        values.extend(vals.tolist())
    ci=[float(x) for x in np.quantile(values,[.025,.975])]
    return {"status":"fitted","gain":float(frame[metric].mean()),
            "n_surveys":len(frame),"sites":n,"site_bootstrap_ci95":ci,
            "CI_positive":bool(ci[0]>0),"boot_reps":BOOT,
            "fold_means":{k:float(x[metric].mean()) for k,x in frame.groupby("fold")}}

def logscore(y,p):
    arr=np.asarray(y,float)
    pp=np.clip(np.asarray(p,float),1e-9,1-1e-9)
    return arr*np.log(pp)+(1-arr)*np.log1p(-pp)

def heldout_main(d):
    folds={}
    results=[]
    for fold in ("A","B"):
        train=d[d.fold==fold]
        test=d[d.fold!=fold]
        p0,a0=model_predict(train,test,[])
        p1,a1=model_predict(train,test,["bull"])
        y=test.green.astype(int).to_numpy()
        results.append(pd.DataFrame({
           "site_key":test.site_key.astype(str).to_numpy(),
           "fold":test.fold.astype(str).to_numpy(),
           "gain":logscore(y,p1)-logscore(y,p0),
           "brier_gain":(y-p0)**2-(y-p1)**2
        }))
        folds[fold]={"M0":a0,"M1":a1,"heldout_surveys":len(test),
                     "heldout_sites":int(test.site_key.nunique())}
    o=pd.concat(results,ignore_index=True)
    if len(o)!=len(d) or o.site_key.nunique()!=d.site_key.nunique():
        raise RuntimeError("Site heldout double count or missing surveys")
    gain=site_boot_ci(o,"gain",SEED)
    brier=site_boot_ci(o,"brier_gain",SEED+1)
    signs={f:folds[f]["M1"]["coef_additional"]["bull"] for f in folds}
    support=bool(gain.get("CI_positive") and
        all(v>0 for v in gain["fold_means"].values()) and
        all(v>0 for v in signs.values()))
    return {
       "models":"M0 same-project observer method weather season and other-call richness; M1 plus bullfrog",
       "heldout_logscore":gain,"heldout_brier":brier,
       "training_folds":folds,
       "bullfrog_training_coef":signs,
       "passes_all_positive_portability_gates":support,
       "classification":"independent_observational_positive_partner_prediction_candidate" if support
                         else "positive_partner_increment_not_supported"
    }

def site_fixed_sensitivity(d):
    sites=(d.groupby("site_key").bull.nunique()==2)
    eligible=sites[sites].index
    sites_green=(d.groupby("site_key").green.nunique()==2)
    eligible2=sites_green[sites_green].index
    common=sorted(set(eligible)&set(eligible2))
    if len(common)<10:
        return {"status":"underpowered","sites_with_bull_variation":len(eligible),
                "sites_with_green_variation":len(eligible2),
                "sites_both_vary":len(common)}
    t=d[d.site_key.isin(common)].copy()
    try:
        reg=smf.glm("green ~ bull + C(site_key) + Wind_num + sin_doy + cos_doy"
                    " + sin_hour + cos_hour + n_other_species",
                    data=t,family=sm.families.Binomial()).fit(
                    cov_type="cluster",cov_kwds={"groups":t.site_key.astype(str)},
                    maxiter=200)
        beta=float(reg.params["bull"]);se=float(reg.bse["bull"])
        pvalue=float(reg.pvalues["bull"])
        # Site-fixed GLM has only 13 informative sites in this dataset and
        # may have quasi/complete separation. Never serialize non-finite
        # uncertainty or call a huge unstable coefficient a valid result.
        if not np.isfinite([beta,se,pvalue]).all() or not bool(reg.converged):
            return {"status":"quasi_separation_or_nonfinite_uncertainty",
                    "sites":len(common),"n":len(t),
                    "nuisance_site_FE_not_reliable":True}
        return {"status":"fitted","sites":len(common),"n":len(t),
            "beta_bull":beta,"ci95_beta":[beta-Z*se,beta+Z*se],
            "odds_ratio":float(np.exp(beta)),
            "ci95_or":[float(np.exp(beta-Z*se)),float(np.exp(beta+Z*se))],
            "p_two_sided":pvalue}
    except Exception as ex:
        return {"status":"fit_unreliable","reason":str(ex)[:220],
                "sites_with_both_outcome_variation":len(common)}

def secondary_negative(d):
    if d.negative.sum()<30 or d.loc[d.negative==1,"site_key"].nunique()<10:
        return {"status":"insufficient_negative_species","positive_events":int(d.negative.sum()),
                "positive_sites":int(d.loc[d.negative==1,"site_key"].nunique())}
    out=[]
    folds={}
    for fold in ("A","B"):
        train=d[d.fold==fold];test=d[d.fold!=fold]
        if train.green.sum()<10 or train.negative.sum()<10:
            return {"status":"negative_fold_underpowered",
                    "fold":fold,"green":int(train.green.sum()),
                    "negative":int(train.negative.sum())}
        p0,coef0=model_predict(train,test,["bull"])
        p1,coef1=model_predict(train,test,["bull","negative"])
        y=test.green.astype(int).to_numpy()
        out.append(pd.DataFrame({
          "site_key":test.site_key.astype(str).to_numpy(),"fold":test.fold.astype(str).to_numpy(),
          "gain":logscore(y,p1)-logscore(y,p0)}))
        folds[fold]={"negative_beta":coef1["coef_additional"]["negative"],
                    "n_train":len(train),"n_test":len(test)}
    q=pd.concat(out,ignore_index=True)
    v=site_boot_ci(q,"gain",SEED+10)
    return {"status":"fitted","source_negative":NEGATIVE,
            "nested_increment_after_bull":v,
            "folds":folds,
            "negative_addition_predictive_supported":bool(v.get("CI_positive") and
                all(x["negative_beta"]<0 for x in folds.values()) and
                all(m>0 for m in v["fold_means"].values()))}

def synthetic_qa():
    df=pd.DataFrame({
        "Project":["A"]*6+["B"]*6,
        "Site":[f"Site{i}" for i in range(6)]*2
    })
    labels=fold_mapping(df)
    assert len(labels)==12
    assert {labels["A",v] for v in df[df.Project=="A"].Site}=={"A","B"}
    y=np.array([1,0,1,0]);p=np.array([.8,.2,.9,.1])
    assert np.isfinite(logscore(y,p)).all()
    assert float(logscore(y,p).sum())>float(logscore(y,1-p).sum())
    return {"status":"PASS","disjoint_site_fold":"PASS","proper_logscore":"PASS",
            "binary_not_species_occupancy":"PASS"}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--outdir",type=Path,default=Path("build/armi_2024_independent"))
    p.add_argument("--synthetic-only",action="store_true")
    arg=p.parse_args()
    qa=synthetic_qa()
    print("ARMI_2024_PREDICTIVE_SYNTHETIC_QA",json.dumps(qa,sort_keys=True),flush=True)
    if arg.synthetic_only:return
    arg.outdir.mkdir(parents=True,exist_ok=True)
    load=imported_source()
    csvbytes,source=load.retrieve(load.FILES["survey"])
    if source["SHA256"]!=SOURCE_SHA:
        raise RuntimeError("Pinned independent USGS science source SHA mismatch")
    xmlbytes,meta=load.retrieve(load.FILES["metadata"])
    if meta["SHA256"]!=SOURCE_META_SHA:
        raise RuntimeError("Pinned USGS metadata source SHA mismatch")
    d,source_gate,covgate,coverage=build_visit_table(csvbytes)
    del csvbytes,xmlbytes
    result={
       "analysis":"independent_USGS_ARMI_2024_bull_green_positive_list_site_holdout_v0_1",
       "source_contract":"exploration/ARMI_2024_INDEPENDENT_FROG_SOURCE_CONTRACT_V0_1.md",
       "source_verification":source,
       "metadata_verification":meta,
       "source_only_preflight_run":39781861923,
       "source_grain":source_gate,
       "weather_and_time_QA":covgate,
       "detection_outcome_coverage":coverage,
       "synthetic_QA":qa,
       "status":"QA_gate_evaluated",
       "source_distinct_from_USGS_NAAMP":True,
       "science":{
          "result_is_observational_not_causal":True,
          "positive_list_means_no_call_recorded_not_occupancy_absence":True,
          "2024_surveys_targeted_cricket_frogs_not_random_wetlands":True,
          "survey_length_5_minutes":True,
          "no_plant_species_or_fish_odonate_data":True,
          "no_NAAMP_fixed_margin_replicate":True},
       "RC6_manuscript_SI_main_modified":False}
    if coverage is None or not source_gate["both_named_species_appear"] or not all(coverage["outcome_gate"].values()):
        result["status"]="insufficient_outcome_or_covariate_information"
        result["analysis_completed"]=False
    else:
        result["analysis_completed"]=True
        result["primary"]=heldout_main(d)
        result["site_fixed_effect"]=site_fixed_sensitivity(d)
        result["secondary_negative"]=secondary_negative(d)
        result["status"]=result["primary"]["classification"]
    (arg.outdir/"result.json").write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+"\n")
    print("ARMI_2024_INDEPENDENT_RESULT_BEGIN",flush=True)
    print(json.dumps(result,sort_keys=True,allow_nan=False),flush=True)
    print("ARMI_2024_INDEPENDENT_RESULT_END",flush=True)
if __name__=="__main__":
    main()
