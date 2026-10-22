#!/usr/bin/env python3
"""Independent NPS GLKN 2016–2023 frog acoustic validation of bullfrog-green frog.

A separate observational dataset from NAAMP. Data-source integrity, expert
outcome coding, site-disjoint split and analysis rules predeclared in the
v0.4 contract. No animal interaction or trophic mediation is inferred.

Raw NPS files and event/station identifiers never leave the transient runner:
only aggregated, de-identified data quality and model evidence are archived.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import math
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from sklearn.linear_model import LogisticRegression
from scipy.special import xlogy
from statsmodels.stats.multitest import multipletests

ROOT=Path(__file__).resolve().parents[1]
SOURCE_SHA="b1c11cf70472a906e6c238a690a5a12373cdd20ef4d5e180fa3f376d520118c2"
SOURCE_LEN=68581307
CENTRAL="Lithobates clamitans"
PARTNER="Lithobates catesbeianus"
NEGATIVES=("Anaxyrus fowleri","Dryophytes versicolor")
EVENT=("ParkCode","SiteLocation","FileName","StartTime")
FROG_FIELDS=list(EVENT)+[
    "EventYear","ScientificName","ManualCIV","SurveyorDetectedStatus",
    "SoftwareDetectedStatus","Hydroperiod","AvgTemperature_C"]
B=2000
SEED=2840337
Z=1.959963984540054
NFEATURES=["year_center","sin_doy","cos_doy","sin_hour","cos_hour","temp_per10",
           "hydro_permanent","hydro_semipermanent"]
MODEL_YEARS=range(2016,2024)
REGULARIZATION=1.0
ABSENT_STATUS={"NO"}
PRESENT_STATUS={"YES"}
VALID_CI={"0","1","2","3"}

def imp(path):
    import importlib.util
    spec=importlib.util.spec_from_file_location("NPS_source_verified_v02",path)
    v=importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(v)
    return v

def hash_fold(site):
    dig=hashlib.sha256(site.encode("utf-8")).digest()
    return "A" if dig[0]%2==0 else "B"

def split_sites_by_park(frame):
    sites=frame[["ParkCode","SiteLocation"]].drop_duplicates().copy()
    mapping={}
    for park,g in sites.groupby("ParkCode",sort=True):
        ordered=sorted(g.SiteLocation.tolist(),
                       key=lambda st:(hashlib.sha256((str(park)+":"+str(st)).encode()).hexdigest(),str(st)))
        for ix,st in enumerate(ordered):
            mapping[(str(park),str(st))]="A" if ix%2==0 else "B"
    return mapping

def safe_json(v):
    if isinstance(v,np.generic):return v.item()
    if isinstance(v,np.ndarray):return v.tolist()
    if isinstance(v,pd.Timestamp):return v.isoformat()
    raise TypeError(type(v).__name__)

def site_bootstrap(frame,column,seed):
    if frame.empty:return {"status":"empty"}
    routes=frame.groupby("site_key")[column].agg(["sum","size"])
    n=len(routes)
    if n<2:return {"status":"insufficient_sites"}
    sums=routes["sum"].to_numpy(float)
    sizes=routes["size"].to_numpy(float)
    rng=np.random.default_rng(seed)
    # Batch to avoid unnecessary memory for large site resampling.
    values=[]
    for i in range(0,B,250):
        it=min(250,B-i)
        idx=rng.integers(0,n,size=(it,n))
        values.extend((sums[idx].sum(axis=1)/sizes[idx].sum(axis=1)).tolist())
    ci=np.quantile(np.asarray(values),[.025,.975])
    out={
      "status":"fitted","mean_gain":float(frame[column].mean()),
      "ci95_site_bootstrap":[float(ci[0]),float(ci[1])],
      "positive_CI":bool(ci[0]>0),
      "n_recordings":int(len(frame)),
      "n_sites":int(n),
      "n_bootstrap":B,
      "fold_means":{str(k):float(z[column].mean()) for k,z in frame.groupby("fold")}
    }
    return out

def build_source_frame(blob):
    header=blob[:6000].decode("utf-8-sig").splitlines()[0].split(",")
    if len(set(header))!=len(header):raise RuntimeError("Official source headers duplicated")
    if not set(FROG_FIELDS).issubset(set(header)):
        raise RuntimeError("Frog source required columns drifted")
    # Retain response columns only AFTER source SHA validation.
    frame=pd.read_csv(io.BytesIO(blob),usecols=FROG_FIELDS,low_memory=False,
            dtype={z:"string" for z in FROG_FIELDS
                   if z not in ("AvgTemperature_C",)})
    if len(frame)!=147913:raise RuntimeError("Original source row count drift")
    for col in FROG_FIELDS:
        if col!="AvgTemperature_C":
            frame[col]=frame[col].str.strip()
    if frame.duplicated(list(EVENT)+["ScientificName"]).any():
        raise RuntimeError("Original source recording×taxon key no longer unique")
    if frame[list(EVENT)+["ScientificName"]].isna().any().any():
        raise RuntimeError("Null recording identity or taxon label")
    frame["CI_clean"]=frame.ManualCIV.where(frame.ManualCIV.isin(VALID_CI))
    frame["CI_valid"]=frame.CI_clean.notna()
    frame["CI_numeric"]=pd.to_numeric(frame.CI_clean,errors="coerce")
    frame["manual_presence"]=(frame.CI_numeric>=1).where(frame.CI_valid)
    frame["manual_strong"]=(frame.CI_numeric>=2).where(frame.CI_valid)
    frame["status_clean"]=frame.SurveyorDetectedStatus.fillna("").str.upper()
    frame["status_binary"]=frame.status_clean.isin({"YES","NO"})
    frame["expert_presence"]=frame.status_clean.eq("YES").where(frame.status_binary)
    frame["detector_clean"]=frame.SoftwareDetectedStatus.fillna("").str.upper()
    return frame

def validate_recorder_outcomes(df):
    panel=df.groupby(list(EVENT),sort=False).ScientificName.agg(frozenset).reset_index(name="taxa")
    park_target=df.groupby("ParkCode").ScientificName.agg(frozenset).to_dict()
    panel["park_target"]=[park_target[str(p)] for p in panel.ParkCode]
    panel["complete_park_panel"]=panel.taxa.eq(panel.park_target)
    taxa=df[df.ScientificName.isin([CENTRAL,PARTNER]+list(NEGATIVES))].copy()
    if taxa.empty:raise RuntimeError("No named focal taxa")
    diag={}
    for name in [CENTRAL,PARTNER]+list(NEGATIVES):
        sub=taxa[taxa.ScientificName==name]
        counts={
            "n_rows":len(sub),
            "n_numeric_CI_0_3":int(sub.CI_valid.sum()),
            "fraction_numeric_CI_0_3":float(sub.CI_valid.mean()),
            "manual_zero_count":int((sub.CI_numeric==0).sum()),
            "manual_positive_CI1plus_count":int((sub.CI_numeric>=1).sum()),
            "manual_strong_CI2plus_count":int((sub.CI_numeric>=2).sum()),
            "status_labels":{str(k):int(v) for k,v in sub.status_clean.value_counts(dropna=False).items()},
            "detector_labels":{str(k):int(v) for k,v in sub.detector_clean.value_counts(dropna=False).items()},
            "manual_CI_labels":{str(k):int(v) for k,v in sub.ManualCIV.fillna("<NA>").value_counts().items()}
        }
        s=sub[sub.CI_valid&sub.status_binary]
        counts["expert_status_CI_comparable_rows"]=len(s)
        counts["expert_status_CI_discordant"]=int((s.manual_presence.astype(bool)!=s.expert_presence.astype(bool)).sum())
        counts["expert_status_CI_discordance_rate"]=counts["expert_status_CI_discordant"]/len(s) if len(s) else None
        diag[name]=counts
    left=taxa[taxa.ScientificName==CENTRAL].copy()
    right=taxa[taxa.ScientificName==PARTNER].copy()
    right=right.rename(columns={z:z+"_P" for z in ("ScientificName","CI_valid","CI_numeric",
                                 "manual_presence","manual_strong",
                                 "status_clean","status_binary","expert_presence")})
    cols=list(EVENT)+[
       "ScientificName_P","CI_valid_P","CI_numeric_P","manual_presence_P","manual_strong_P",
       "status_clean_P","status_binary_P","expert_presence_P"]
    both=left.merge(right[cols],on=list(EVENT),how="inner",validate="one_to_one")
    both=both.merge(panel[list(EVENT)+["complete_park_panel"]],
                    on=list(EVENT),how="left",validate="one_to_one")
    if len(both)!=12499:
        raise RuntimeError("Pair source-only recording eligibility drift")
    both["site_key"]=both.ParkCode.astype(str)+":"+both.SiteLocation.astype(str)
    both["CI_both_valid"]=both.CI_valid&both.CI_valid_P
    both["status_both_valid"]=both.status_binary&both.status_binary_P
    checked=both[both.CI_both_valid].copy()
    valid_status=checked[checked.status_both_valid]
    if len(valid_status):
        bad=(valid_status.manual_presence.astype(bool)!=valid_status.expert_presence.astype(bool)) | (valid_status.manual_presence_P.astype(bool)!=valid_status.expert_presence_P.astype(bool))
        disagreement=float(bad.mean())
    else:disagreement=None
    valid_temp=pd.to_numeric(checked.AvgTemperature_C,errors="coerce")
    temp_ok=valid_temp.between(-20.,45.)
    date=pd.to_datetime(checked.StartTime,errors="coerce")
    calendar_ok=date.notna()&pd.to_numeric(checked.EventYear,errors="coerce").between(2016,2023)
    hydro_ok=checked.Hydroperiod.isin(["Permanent","Semi-permanent","Ephemeral"])
    complete=checked[temp_ok&calendar_ok&hydro_ok].copy()
    complete["temp_c"]=valid_temp.loc[complete.index].astype(float)
    complete["timestamp"]=date.loc[complete.index]
    complete["year"]=pd.to_numeric(complete.EventYear).astype(int)
    complete["green"]=complete.manual_presence.astype(int)
    complete["bull"]=complete.manual_presence_P.astype(int)
    complete["green_strong"]=complete.manual_strong.astype(int)
    complete["bull_strong"]=complete.manual_strong_P.astype(int)
    outcome={
      "named_source_pair_row_opportunities":len(both),
      "both_ManualCIV_0_3_recordings":len(checked),
      "fraction_both_valid_ManualCIV":float(len(checked)/len(both)),
      "both_expert_status_binary_recordings":int(both.status_both_valid.sum()),
      "validated_manual_and_status_recordings":len(valid_status),
      "joint_recording_expert_status_discordance_rate":disagreement,
      "n_valid_after_temperature_year_hydroperiod":len(complete),
      "n_missing_or_implausible_temperature_given_both_CI":int((~temp_ok).sum()),
      "n_invalid_date_year_given_both_CI":int((~calendar_ok).sum()),
      "n_invalid_hydroperiod_given_both_CI":int((~hydro_ok).sum()),
      "n_sites_complete":int(complete.site_key.nunique()),
      "n_parks_complete":int(complete.ParkCode.nunique()),
      "n_green_detected":int(complete.green.sum()),
      "n_bull_detected":int(complete.bull.sum()),
      "n_green_strong":int(complete.green_strong.sum()),
      "n_bull_strong":int(complete.bull_strong.sum()),
      "bull_positive_recording_sites":int(complete.loc[complete.bull==1,"site_key"].nunique()),
      "complete_park_panel_recordings":int(complete.complete_park_panel.sum()),
      "outcome_by_park":{},
      "outcome_by_year":{}
    }
    for park,z in complete.groupby("ParkCode"):
        outcome["outcome_by_park"][str(park)]={
            "recordings":len(z),"sites":int(z.site_key.nunique()),
            "green_positive":int(z.green.sum()),"bull_positive":int(z.bull.sum()),
            "complete_park_panel_recordings":int(z.complete_park_panel.sum())}
    for year,z in complete.groupby("year"):
        outcome["outcome_by_year"][str(year)]={
            "recordings":len(z),"green_positive":int(z.green.sum()),
            "bull_positive":int(z.bull.sum())}
    gate={
        "ManualCIV_validity_ge90percent":len(checked)/len(both)>=.90,
        "expert_status_discordance_le1percent":bool(disagreement is not None and disagreement<=.01),
        "n_pair_complete_recordings_ge1000":len(complete)>=1000,
        "n_green_positive_ge150":int(complete.green.sum())>=150,
        "n_bull_positive_ge100":int(complete.bull.sum())>=100,
        "site_count_ge20":complete.site_key.nunique()>=20,
        "park_count_ge2":complete.ParkCode.nunique()>=2,
        "bull_positive_ge100_at10_sites":int(complete.bull.sum())>=100 and
          complete.loc[complete.bull==1,"site_key"].nunique()>=10}
    return diag,outcome,gate,complete,taxa,panel

def add_features(frame):
    d=frame.copy()
    t=d["timestamp"]
    doy=t.dt.dayofyear.to_numpy(dtype=float)
    hour=t.dt.hour.to_numpy(dtype=float)+t.dt.minute.to_numpy(dtype=float)/60.
    d["year_center"]=(d.year.to_numpy(float)-2019.)/5.
    d["sin_doy"]=np.sin(2*np.pi*doy/365.25)
    d["cos_doy"]=np.cos(2*np.pi*doy/365.25)
    d["sin_hour"]=np.sin(2*np.pi*hour/24.)
    d["cos_hour"]=np.cos(2*np.pi*hour/24.)
    d["temp_per10"]=d.temp_c.astype(float)/10.
    d["hydro_permanent"]=(d.Hydroperiod=="Permanent").astype(int)
    d["hydro_semipermanent"]=(d.Hydroperiod=="Semi-permanent").astype(int)
    for park in sorted(d.ParkCode.astype(str).unique())[1:]:
        d["park_"+park]=(d.ParkCode==park).astype(int)
    d["fold"]=[None]*len(d)
    mapping=split_sites_by_park(d)
    d["fold"]=[mapping[(str(p),str(s))] for p,s in zip(d.ParkCode,d.SiteLocation)]
    expectedcols=NFEATURES+[z for z in d.columns if z.startswith("park_")]
    if d[expectedcols].isna().any().any():
        raise RuntimeError("Independent NPS regression baseline predictors are incomplete")
    return d,expectedcols

def fit_predict(train,test,cols,outcome="green"):
    if len(train)<100 or len(test)<100:
        return None,{"status":"insufficient_split"}
    if train[outcome].nunique()!=2:
        return None,{"status":"single_response_class"}
    model=LogisticRegression(C=REGULARIZATION,solver="lbfgs",max_iter=500,class_weight=None)
    model.fit(train[cols].astype(float),train[outcome].astype(int))
    if int(model.n_iter_[0])>=500:
        return None,{"status":"max_iter_reached","iterations":500}
    pred=model.predict_proba(test[cols].astype(float))[:,1]
    return np.clip(pred,1e-12,1-1e-12),{
        "status":"fitted","intercept":float(model.intercept_[0]),
        "coef_by_name":{name:float(v) for name,v in zip(cols,model.coef_[0])},
        "n_train":len(train),"n_test":len(test),
        "train_event_positive":int(train[outcome].sum()),
        "trained_n_iter":int(model.n_iter_[0])}

def bernoulli_logscore(y,p):
    yy=np.asarray(y,float)
    pp=np.clip(np.asarray(p,float),1e-12,1-1e-12)
    return yy*np.log(pp)+(1-yy)*np.log1p(-pp)

def evaluate_folds(data,cols,train_gate=True,outcome="green",partner="bull",
                   seed=SEED,additional=None):
    hold=[]
    training={}
    for trainfold in ("A","B"):
        train=data[data.fold==trainfold].copy()
        test=data[data.fold!=trainfold].copy()
        if train_gate and (train[outcome].sum()<50 or train[partner].sum()<30 or len(test)<100):
            return None,{"status":"insufficient_training_fold",
                         "fold":trainfold,"n_train":len(train),
                         "n_test":len(test),"response_train":int(train[outcome].sum()),
                         "partner_train":int(train[partner].sum())}
        p0,m0=fit_predict(train,test,cols,outcome)
        p1,m1=fit_predict(train,test,cols+[partner]+(additional or []),outcome)
        training[trainfold]={"M0":m0,"M1":m1}
        if p0 is None or p1 is None:
            return None,{"status":"optimizer_or_class_failure","fold":trainfold,"fits":training[trainfold]}
        y=test[outcome].astype(int).to_numpy()
        score=bernoulli_logscore(y,p1)-bernoulli_logscore(y,p0)
        bs=(y-p0)**2-(y-p1)**2
        hold.append(pd.DataFrame({
            "site_key":test.site_key.to_numpy(),
            "fold":test.fold.to_numpy(),
            "gain":score,"brier_gain":bs,
            "Y":y,"X":test[partner].astype(int).to_numpy(),
            "park":test.ParkCode.to_numpy(),"complete_panel":test.complete_park_panel.to_numpy()
        }))
    result=pd.concat(hold,ignore_index=True)
    if result.shape[0]!=len(data):raise RuntimeError("Site fold prediction missed or doubled rows")
    beta=[training[z]["M1"]["coef_by_name"].get(partner) for z in ("A","B")]
    if any(z is None for z in beta):raise RuntimeError("Partner coefficient absent")
    metrics={
        "status":"fitted","n_train_test_total":len(result),
        "n_unique_sites":int(result.site_key.nunique()),
        "full_model_train":training,
        "partner_coefficients_A_B":beta,
        "partner_coefficient_both_positive":bool(all(z>0 for z in beta)),
        "logscore":site_bootstrap(result,"gain",seed),
        "brier":site_bootstrap(result,"brier_gain",seed+1)}
    metrics["supported_positive_partner_prediction"]=bool(
        metrics["partner_coefficient_both_positive"]
        and metrics["logscore"]["positive_CI"]
        and all(v>0 for v in metrics["logscore"]["fold_means"].values()))
    return result,metrics

def site_FE_sensitivity(frame,cols):
    change=frame.groupby("site_key").bull.nunique()
    eligible=change[change==2].index
    if len(eligible)<15:
        return {"status":"underpowered","n_sites_with_bull_variation":len(eligible)}
    # Defer if all sites contain single class of green frog;
    # complete separation would make FE GLM meaningless.
    df=frame.copy()
    if df.groupby("site_key").green.nunique().gt(1).sum()<15:
        return {"status":"green_outcome_low_within_site_variation"}
    formula=("green ~ bull + C(site_key) + year_center + sin_doy + cos_doy"
             " + sin_hour + cos_hour + temp_per10")
    try:
        fit=smf.glm(formula,data=df,family=sm.families.Binomial()).fit(
            cov_type="cluster",cov_kwds={"groups":df.site_key.astype(str)},
            maxiter=200)
        b=float(fit.params["bull"])
        se=float(fit.bse["bull"])
        if not(np.isfinite(b) and np.isfinite(se)):
            raise RuntimeError("Nonfinite coefficient or SE")
        return {"status":"fitted","formula":formula,
                "beta_bull_log_odds":b,"se_site_cluster":se,
                "CI95_beta":[b-Z*se,b+Z*se],
                "odds_ratio":float(np.exp(b)),
                "CI95_odds_ratio":[float(np.exp(b-Z*se)),float(np.exp(b+Z*se))],
                "p_two_sided":float(fit.pvalues["bull"]),
                "n_sites_with_bull_variation":len(eligible),
                "n_sites_with_green_variation":int(df.groupby("site_key").green.nunique().gt(1).sum())}
    except Exception as ex:
        return {"status":"fit_unreliable","message":str(ex)[:280]}

def negative_increment(data,cols,base_source,neg_taxes):
    comparisons={}
    for ix,neg in enumerate(NEGATIVES):
        source=neg_taxes[neg]
        sr=source[list(EVENT)+["CI_numeric","CI_valid"]].rename(
            columns={"CI_numeric":"neg_CI","CI_valid":"neg_valid"})
        subset=data.merge(sr,on=list(EVENT),how="inner",validate="one_to_one")
        subset=subset[subset.neg_valid].copy()
        subset["negative"]=(subset.neg_CI>=1).astype(int)
        positives=int(subset.negative.sum())
        nsites=int(subset.loc[subset.negative==1,"site_key"].nunique())
        if positives<60 or nsites<10 or len(subset)<150:
            comparisons[neg]={"status":"insufficient",
                "n_pair_valid_recordings":len(subset),
                "n_negative_detected":positives,
                "sites_with_negative_detected":nsites}
            continue
        p0,m0=evaluate_folds(subset,cols,train_gate=True,partner="bull",
                         seed=SEED+20+ix,additional=[])
        p1,m1=evaluate_folds(subset,cols,train_gate=True,partner="bull",
                         seed=SEED+21+ix,additional=["negative"])
        # Difference of two folds' same-test scores requires prediction
        # arrays; m1's aggregate gain above M0 implicitly includes negative,
        # so subtract the M_P-vs-M0 increment on identical cases.
        if p0 is None or p1 is None:
            comparisons[neg]={"status":"prediction_fit_unavailable",
                              "full_status":m1.get("status"),"n":len(subset)}
            continue
        merged=p1[["site_key","fold","gain"]].rename(columns={"gain":"new"})\
          .join(p0[["gain"]].rename(columns={"gain":"old"}))
        merged["neg_gain"]=merged["new"]-merged["old"]
        ci=site_bootstrap(merged.rename(columns={"neg_gain":"gain"}),"gain",SEED+50+ix)
        # Cluster the same-recording negative incremental scores by NPS site.
        model=sm.OLS(merged["neg_gain"].astype(float).to_numpy(),
                     np.ones((len(merged),1))).fit(
                    cov_type="cluster",cov_kwds={"groups":merged.site_key.astype(str)})
        beta=float(model.params[0])
        se=float(model.bse[0])
        coefs=[float(m1["full_model_train"][fold]["M1"]["coef_by_name"].get("negative",np.nan))
               for fold in ("A","B")]
        comparisons[neg]={"status":"fitted","n":len(subset),
            "n_sites":int(subset.site_key.nunique()),
            "negative_manual_positive":positives,
            "increment_after_bullfrog":ci,
            "site_cluster_inference":{
                "beta_gain":beta,"se":se,"CI95":[beta-Z*se,beta+Z*se],
                "p_two_sided":float(model.pvalues[0])},
            "negative_regression_coefficients_by_training_fold":coefs,
            "nuisance_baseline":m0["logscore"],
            "full_partner_model":m1["logscore"]}
    eligible=[(n,r) for n,r in comparisons.items() if r.get("status")=="fitted"]
    if eligible:
        qs=multipletests([r["site_cluster_inference"]["p_two_sided"]
                         for n,r in eligible],method="fdr_bh")[1]
        for (name,item),q in zip(eligible,qs):
            item["BH_q"]=float(q)
            item["negative_increment_supported"]=bool(
                q<.05 and item["increment_after_bullfrog"]["positive_CI"]
                and all(v<0 for v in item["negative_regression_coefficients_by_training_fold"])
                and all(v>0 for v in item["increment_after_bullfrog"]["fold_means"].values()))
    return comparisons

def synthetic_qa():
    y=np.array([0,1,1,0])
    p0=np.array([.1,.65,.45,.55])
    p1=np.array([.05,.7,.7,.3])
    assert np.all(np.isfinite(bernoulli_logscore(y,p0)))
    assert (bernoulli_logscore(y,p1)-bernoulli_logscore(y,p0)).mean()>0
    f=pd.DataFrame({"ParkCode":["A","A","A","A","B","B"],
        "SiteLocation":["a","b","c","d","a","b"]})
    spl=split_sites_by_park(f)
    assert {spl["A","a"],spl["A","b"],spl["A","c"],spl["A","d"]}=={"A","B"}
    assert len(set(spl))==6
    return {"status":"PASS","bernoulli_proper_logscore":"PASS",
            "park_stratified_site_split":"PASS","no_source_required":"PASS"}

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--outdir",type=Path,default=ROOT/"build"/"nps_frog_pair_independent_v04")
    parser.add_argument("--synthetic-only",action="store_true")
    args=parser.parse_args()
    args.outdir.mkdir(parents=True,exist_ok=True)
    qa=synthetic_qa()
    print("NPS_FROG_HELDOUT_SYNTHETIC_QA",json.dumps(qa),flush=True)
    if args.synthetic_only:return
    source=imp(ROOT/"exploration/run_nps_glkn_independent_source_only_qa_v0_2.py")
    payload,src=source.source(source.SRC["frog"]["url"],SOURCE_LEN,
                                source.SRC["frog"]["max_bytes"],SOURCE_SHA)
    df=build_source_frame(payload)
    del payload
    species_qa,qa_info,gates,complete,alltaxa,panel=validate_recorder_outcomes(df)
    scope={
      "source_sha256":src["sha256"],"source_file_bytes":src["n_bytes"],
      "original_rows":len(df),"original_recordings":16561,
      "named_species_scored":species_qa,
      "paired_recording_quality":qa_info,
      "predeclared_QA_gates":gates,
      "all_required_gates_pass":bool(all(gates.values())),
      "expert_manual_values_not_replaced_by_AI_detector":True,
      "source_park_target_panels_derived_without_outcome":True}
    result={
      "analysis":"NPS_GLKN_independent_bullfrog_greenfrog_site_heldout_v0_4",
      "contract":"exploration/NPS_GLKN_BULLFROG_GREENFROG_HELDOUT_VALIDATION_CONTRACT_V0_4.md",
      "NPS_IRMA_reference":2320505,
      "source_coverage_and_outcome_QA":scope,
      "synthetic_QA":qa,
      "status":"source_qa_evaluated_before_any_model",
      "inference_boundaries":{
          "NPS_monitoring_independent_of_USGS_NAAMP":True,
          "same_recording_does_not_prove_simultaneous_calls":True,
          "environment_hydroperiod_not_aquatic_plant_species":True,
          "predator_fish_and_insect_census_not_available":True,
          "NAAMP_conditional_fixed_margin_not_replicated":True,
          "causal_interaction_proven":False,
          "original_RC6_main_and_submission_untouched":True
      }}
    if not all(gates.values()):
        result["status"]="measurement_QA_or_sample_gate_inconclusive"
        result["analysis_completed"]=False
    else:
        result["analysis_completed"]=True
        data,cols=add_features(complete)
        folds=split_sites_by_park(data)
        score,main=evaluate_folds(data,cols,seed=SEED)
        result["site_fold_scheme"]={
           "type":"site_disjoint_alternating_SHA256_within_each_park",
           "counts":{f:{"recordings":int((data.fold==f).sum()),
                         "sites":int(data.loc[data.fold==f,"site_key"].nunique()),
                         "park_count":int(data.loc[data.fold==f,"ParkCode"].nunique()),
                         "green_positive":int(data.loc[data.fold==f,"green"].sum()),
                         "bull_positive":int(data.loc[data.fold==f,"bull"].sum())}
                         for f in ("A","B")}
        }
        result["primary_recording_logscore"]=main
        if score is None:
            result["status"]="primary_predictive_training_inconclusive"
        else:
            result["status"]=(
                "independent_recording_partner_prediction_candidate"
                if main.get("supported_positive_partner_prediction") else
                "independent_partner_increment_not_supported")
            result["site_FE_sensitivity"]=site_FE_sensitivity(data,cols)
            full=data[data.complete_park_panel]
            if len(full)>=1000 and full.site_key.nunique()>=20:
                _score,cc=evaluate_folds(full,cols,seed=SEED+3)
                result["full_park_panel_sensitivity"]=cc
            else:
                result["full_park_panel_sensitivity"]={
                    "status":"underpowered","n":len(full),"n_sites":int(full.site_key.nunique())}
            strong=data.copy()
            if (strong.green_strong.sum()>=100 and strong.bull_strong.sum()>=100
                and strong.site_key.nunique()>=20):
                strong["green"]=strong.green_strong
                strong["bull"]=strong.bull_strong
                _z,ss=evaluate_folds(strong,cols,seed=SEED+10)
                result["strong_chorus_sensitivity"]=ss
            else:
                result["strong_chorus_sensitivity"]={
                    "status":"underpowered","n_green_strong":int(strong.green_strong.sum()),
                    "n_bull_strong":int(strong.bull_strong.sum())}
            # Additional negative partners optional secondary; no original
            # per-site frogs are substituted, and invalid scored rows dropped.
            negatives={}
            for neg in NEGATIVES:
                negs=alltaxa[alltaxa.ScientificName==neg]
                negatives[neg]=negs
            result["negative_partner_secondary"]=negative_increment(
                data,cols,score,negatives)
    (args.outdir/"result.json").write_text(
        json.dumps(result,indent=2,sort_keys=True,default=safe_json)+"\n")
    print("NPS_FROG_INDEPENDENT_RESULT_BEGIN",flush=True)
    print(json.dumps(result,sort_keys=True,default=safe_json),flush=True)
    print("NPS_FROG_INDEPENDENT_RESULT_END",flush=True)

if __name__=="__main__":
    main()
