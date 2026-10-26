#!/usr/bin/env python3
"""85 French fishpond data: time-since-dry-out / macrophytes / food web screen.

Measured primary data Girard, Robin & Wezel (2023), DOI 10.5281/zenodo.8158543;
CC BY 1.0. NO frog chorus data. GroupKFold holds out complete ponds.
Primary comparisons are exploratory and cannot identify causal plant/predation.
"""
import argparse
import json
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.dummy import DummyRegressor
from sklearn.linear_model import Ridge
from sklearn.model_selection import GroupKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

SRC = "Girard, Robin & Wezel (2023), 10.5281/zenodo.8158543 (CC BY 1.0)"
HEADER=["Etangs","Annee.d.eau","Evolage","Mat..Org..Sed","N.sed",
        "pH.sed","chl..A","phosphates","richesse.plantes",
        "recouvrement.plantes","Densité.invertébrés","Rendement.piscicole.net"]
BASE=["Mat..Org..Sed","N.sed","pH.sed","chl..A","phosphates"]
AGE="log1p_years_since_dry"
PLANT="richesse.plantes"
COVER="recouvrement.plantes"
RNG_SEED=20261025


def require(cond, msg):
    if not cond: raise ValueError(msg)


def load(folder):
    p=Path(folder)/"Girard_2023_Dataset.tab"
    require(p.is_file(),"Missing CC BY Zenodo original")
    df=pd.read_csv(p,sep=";",decimal=",",na_values=["NA",""],encoding="utf-8")
    for col in HEADER:
        require(col in df.columns, f"Missing original column {col}")
    require(len(df)==134,"Unexpected Girard source observation count")
    require(df.Etangs.nunique()==85,"Unexpected unique fishpond count")
    for col in HEADER[2:]:
        df[col]=pd.to_numeric(df[col],errors="coerce")
    require(df["Evolage"].notna().all() and
            df["Evolage"].between(1,20).all(),"Dryout-history axis changed")
    df[AGE]=np.log1p(df["Evolage"])
    df[AGE+"_sq"]=df[AGE]**2
    return df


def eval_endpoint(df, outcome, predictors, n_boot=2000):
    needed=list({outcome,*sum(predictors.values(),[])})
    dat=df.dropna(subset=needed).copy().reset_index(drop=True)
    require(len(dat)>=20,f"Insufficient endpoint observations: {outcome}")
    groups=dat.Etangs.astype(str).to_numpy()
    G=int(pd.Series(groups).nunique())
    require(G>=5,f"Insufficient separate ponds: {G}")
    y=np.log1p(dat[outcome].to_numpy(dtype=float))
    require(np.isfinite(y).all() and (dat[outcome]>=0).all(),
            "Outcome invalid or below zero")
    splits=list(GroupKFold(n_splits=5).split(dat,y,groups))
    oof={};model_names=["null_fold_mean"]+list(predictors)
    for name in model_names:
        pred=np.empty(len(dat),dtype=float);pred[:]=np.nan
        for idx_train,idx_test in splits:
            model=(
                DummyRegressor(strategy="mean")
                if name=="null_fold_mean"
                else Pipeline([("scale",StandardScaler()),
                               ("ridge",Ridge(alpha=10.0))])
            )
            if name=="null_fold_mean":
                model.fit(np.zeros((len(idx_train),1)),y[idx_train])
                pred[idx_test]=model.predict(np.zeros((len(idx_test),1)))
            else:
                X=dat[predictors[name]].to_numpy(dtype=float)
                model.fit(X[idx_train],y[idx_train])
                pred[idx_test]=model.predict(X[idx_test])
        require(np.isfinite(pred).all(),"Unscored held-out event")
        oof[name]=pred
    # Each repeatedly sampled pond receives equal weight.
    pond_names=sorted(set(groups))
    errors={}
    for name,pred in oof.items():
        errs=(y-pred)**2
        errors[name]=np.array([np.mean(errs[groups==pond]) for pond in pond_names])
    result={
        "outcome":outcome,
        "outcome_transform":"log1p(observed field)",
        "observed_rows":len(dat),"distinct_ponds":G,
        "repeat_ponds":sum(np.sum(groups==p)>1 for p in pond_names),
        "missing_from_134":134-len(dat),
        "group_cv":"5-fold held-out by Etangs (entire pond)",
        "ridge_alpha_fixed":10,
        "outcome_range":[float(np.min(dat[outcome])),
                         float(np.max(dat[outcome]))],
        "models":{
            name:{
                "site_balanced_cv_mse_logscale":float(np.mean(v)),
                "observation_weighted_cv_mse_logscale":
                    float(np.mean((y-oof[name])**2))
            } for name,v in errors.items()
        },
        "comparisons":{},
    }
    rng=np.random.default_rng(RNG_SEED+len(dat))
    batch=rng.integers(0,G,size=(n_boot,G))
    baseline="baseline_environment_history"
    for name in predictors:
        if name==baseline:continue
        diff=errors[baseline]-errors[name]
        boot=np.mean(diff[batch],axis=1)
        result["comparisons"][f"{name}_vs_{baseline}"]={
            "positive_means_added_plant_variables_help":True,
            "site_balanced_cv_mse_gain":float(np.mean(diff)),
            "site_cluster_bootstrap_95ci_conditional_oof_predictions":
                list(np.quantile(boot,[.025,.975]).astype(float)),
            "fraction_boot_gain_positive":float(np.mean(boot>0)),
        }
    return result


def within_pond_age_slope(df,n_boot=2000):
    d=df.dropna(subset=[PLANT,AGE]).copy()
    d["out"]=np.log1p(d[PLANT])
    g=d.groupby("Etangs")
    d["x"]=d[AGE]-g[AGE].transform("mean")
    d["y"]=d["out"]-g["out"].transform("mean")
    data=d.groupby("Etangs").agg(
        observations=(AGE,"size"),xx=("x",lambda z:float(np.sum(z**2))),
        xy=("x",lambda z:float(np.dot(z,d.loc[z.index,"y"]))))
    eligible=data.loc[(data.observations>=2)&(data.xx>1e-8)]
    if len(eligible)<7:
        return {"estimable":False,"reason":"Insufficient repeated ponds with differing dryout age",
                "n_eligible_ponds":len(eligible)}
    B=float(eligible.xy.sum()/eligible.xx.sum())
    rng=np.random.default_rng(RNG_SEED)
    bb=rng.integers(0,len(eligible),size=(n_boot,len(eligible)))
    x=eligible.xx.to_numpy(); y=eligible.xy.to_numpy()
    boots=np.sum(y[bb],axis=1)/np.sum(x[bb],axis=1)
    return {
        "estimable":True,
        "estimand":"within same pond descriptive plant-richness log1p slope per log1p years since last dryout",
        "n_eligible_ponds":int(len(eligible)),
        "n_eligible_rows":int(eligible.observations.sum()),
        "beta":B,
        "site_cluster_bootstrap_95ci":
            list(np.quantile(boots,[.025,.975]).astype(float)),
        "boundary":"No known calendar year nor randomized dryout and cannot identify vegetation succession cause.",
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source",default="research/external/zenodo_8158543")
    p.add_argument("--out",default="research/results/french_ponds_hydro_plant")
    args=p.parse_args()
    df=load(args.source)
    groupped=df.groupby("Etangs").size()
    cover=df[COVER]
    c={"total_rows":len(df),"distinct_ponds":int(df.Etangs.nunique()),
       "repeated_ponds":int((groupped>=2).sum()),
       "repeat_pond_rows":int(groupped[groupped>=2].sum()),
       "max_visits_per_pond":int(groupped.max()),
       "plants_richness_n":int(df[PLANT].notna().sum()),
       "plants_cover_n":int(cover.notna().sum()),
       "cover_gt100_n":int((cover>100).sum()),
       "cover_range":[float(cover.min()),float(cover.max())],
       "inverts_n":int(df["Densité.invertébrés"].notna().sum()),
       "net_fish_yield_n":int(df["Rendement.piscicole.net"].notna().sum()),
       "dry_categories":{str(k):int(v)
                         for k,v in df["Annee.d.eau"].value_counts().items()},
       "plant_richness_mean_by_dry_bin":{
          str(k):float(v) for k,v in
          df.groupby("Annee.d.eau")[PLANT].mean().items()
       },
    }
    predictorsPlant={
        "baseline_environment_history":BASE,
        "plus_dryout_history":BASE+[AGE],
        "plus_nonlinear_history":BASE+[AGE,AGE+"_sq"],
    }
    predOther={
        "baseline_environment_history":BASE+[AGE],
        "plus_macrophyte_richness":BASE+[AGE,PLANT],
        "plus_macrophyte_cover_index":BASE+[AGE,COVER],
        "plus_both_plant_metrics":BASE+[AGE,PLANT,COVER],
    }
    # Do NOT treat plant.cover percentage >100 as bounded percent.
    outputs={
        "source":SRC,"license":"CC BY 1.0 Generic",
        "source_file":"Girard_2023_Dataset.tab",
        "schema_QC":c,
        "within_pond_plant_age":within_pond_age_slope(df),
        "macrophyte_richness":eval_endpoint(df,PLANT,predictorsPlant),
        "benthic_invertebrate_index":eval_endpoint(
            df,"Densité.invertébrés",predOther),
        "fish_net_yield":eval_endpoint(
            df,"Rendement.piscicole.net",predOther),
        "limitations":[
            "No anurans, frog calling, water-edge stem densities, or confirmed predation rates.",
            "No sampling calendar year in data rows and many repeated ponds.",
            "Cover >100 despite percent unit: treat as unbounded plant COVER INDEX, not fraction.",
            "Metadata transformation for benthos conflicts with magnitude in source; log1p recorded density field is descriptive only.",
            "Fish yield includes pond stocking/fishery management and is not natural fish population abundance.",
            "Site-bootstraps condition on fixed held-out predictions; not full uncertainty refitting.",
            "Missingness differs by endpoint and no missing value imputation was used.",
            "Post-study, exploratory and not a preregistered plant-mediated species interaction test.",
        ]
    }
    dest=Path(args.out);dest.mkdir(parents=True,exist_ok=True)
    (dest/"observed_results.json").write_text(
        json.dumps(outputs,indent=2,ensure_ascii=False)+"\n",encoding="utf8")
    print("BEGIN_FRENCH_POND_HYDRO_MACRO_RESULTS")
    print(json.dumps(outputs,indent=2,ensure_ascii=False))
    print("END_FRENCH_POND_HYDRO_MACRO_RESULTS")


if __name__=="__main__":
    main()
