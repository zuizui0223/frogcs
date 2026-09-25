#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import io
import json
import math
import urllib.request
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

HUANG_URL="https://raw.githubusercontent.com/rdmpage/amphibian-traits-database/7b80dc0bb7f5e9ca363f5cdbcd526e658473f7a0/Anura.csv"
HUANG_BLOB_SHA1="208dd19658da1b342c067d1af9ea08f671cd8443"
ALIASES={"Hyla":"Dryophytes","Dryophytes":"Hyla","Lithobates":"Rana","Rana":"Lithobates"}
EXPECTED_N=29
EXPECTED_WET=4483
EXPECTED_DRY=4104
Q=1.959963984540054

def fetch_bytes(url):
    req=urllib.request.Request(url,headers={"User-Agent":"frogcs-huang-validation/0.1"})
    with urllib.request.urlopen(req,timeout=120) as r:
        return r.read()

def git_blob_sha1(b):
    h=hashlib.sha1()
    h.update(f"blob {len(b)}\0".encode())
    h.update(b)
    return h.hexdigest()

def norm_binomial(x):
    toks=str(x or "").strip().split()
    return " ".join(toks[:2]) if len(toks)>=2 else str(x or "").strip()

def load_effects():
    p=Path("NAAMP_SPECIES_PULSE_HETEROGENEITY_RECEIPT_V0_1.json")
    obj=json.loads(p.read_text(encoding="utf-8"))
    g=obj["global"]
    if int(g["eligible_species"])!=EXPECTED_N or int(g["eligible_wet_gains"])!=EXPECTED_WET or int(g["eligible_dry_losses"])!=EXPECTED_DRY:
        raise SystemExit("species-effect source drift")
    rows=[]
    for x in obj["species_results"]:
        w=int(x["wet_gains"]);d=int(x["dry_losses"])
        rows.append({
          "species":norm_binomial(x["species_code"]),
          "wet_gains":w,"dry_losses":d,
          "wet_gain_share":w/(w+d),
          "log_odds":math.log((w+0.5)/(d+0.5)),
          "var":1/(w+0.5)+1/(d+0.5)
        })
    d=pd.DataFrame(rows)
    d["weight"]=1/d["var"]
    return d

def load_huang():
    b=fetch_bytes(HUANG_URL)
    got=git_blob_sha1(b)
    if got!=HUANG_BLOB_SHA1:
        raise SystemExit(f"Huang blob drift: {got}")
    try:
        d=pd.read_csv(io.BytesIO(b),encoding="utf-8")
    except UnicodeDecodeError:
        d=pd.read_csv(io.BytesIO(b),encoding="cp1252")
    required=["Family","Genus","Species","Sex","SVL"]
    missing=[x for x in required if x not in d.columns]
    if missing:
        raise SystemExit(f"Huang schema missing: {missing}; columns={list(d.columns)}")
    d["species_norm"]=d["Species"].map(norm_binomial)
    d["SVL_num"]=pd.to_numeric(d["SVL"],errors="coerce")
    d.loc[~np.isfinite(d["SVL_num"]) | (d["SVL_num"]<=0),"SVL_num"]=np.nan
    return d,got

def build_summary(h):
    out={}
    for sp,g in h.groupby("species_norm"):
        vals=g["SVL_num"].dropna()
        adult=g[g["Sex"].astype(str).str.upper().isin(["M","F"])]["SVL_num"].dropna()
        fam=[str(x).strip() for x in g["Family"].dropna().tolist() if str(x).strip()]
        gen=[str(x).strip() for x in g["Genus"].dropna().tolist() if str(x).strip()]
        out[sp]={
          "median_svl":float(vals.median()) if len(vals) else np.nan,
          "n_svl_rows":int(len(vals)),
          "adult_median_svl":float(adult.median()) if len(adult) else np.nan,
          "n_adult_svl_rows":int(len(adult)),
          "Family":fam[0] if fam else "",
          "Genus":gen[0] if gen else ""
        }
    return out

def match(effects,summary):
    rows=[];audit=[]
    for _,r in effects.iterrows():
        sp=r["species"]; toks=sp.split()
        candidates=[sp]
        if len(toks)==2 and toks[0] in ALIASES:
            candidates.append(ALIASES[toks[0]]+" "+toks[1])
        hits=[x for x in candidates if x in summary]
        if sp in hits:
            chosen=sp
        elif len(hits)==1:
            chosen=hits[0]
        elif len(hits)>1:
            raise SystemExit(f"ambiguous Huang match: {sp} {hits}")
        else:
            chosen=None
        base=r.to_dict()
        if chosen is None:
            base.update({"matched":False,"huang_species":None,"Family":"","Genus":"","median_svl":np.nan,"adult_median_svl":np.nan})
            audit.append({"naamp_species":sp,"matched":False,"huang_species":None,"match_type":None})
        else:
            x=summary[chosen]
            base.update({"matched":True,"huang_species":chosen,**x})
            audit.append({"naamp_species":sp,"matched":True,"huang_species":chosen,"match_type":"exact" if chosen==sp else "frozen_genus_alias"})
        rows.append(base)
    return pd.DataFrame(rows),audit

def fit(df,size_col,formula_extra=""):
    x=df[np.isfinite(pd.to_numeric(df[size_col],errors="coerce")) & (pd.to_numeric(df[size_col],errors="coerce")>0)].copy()
    x["log_svl"]=np.log(pd.to_numeric(x[size_col],errors="coerce"))
    if len(x)<15:
        return {"estimable":False,"n_species":int(len(x)),"reason":"below_minimum"}
    formula="log_odds ~ log_svl"+formula_extra
    fit=smf.wls(formula,data=x,weights=x["weight"]).fit(cov_type="HC3")
    b=float(fit.params["log_svl"]);se=float(fit.bse["log_svl"]);p=float(fit.pvalues["log_svl"])
    lo=b-Q*se;hi=b+Q*se
    return {
      "estimable":True,"n_species":int(len(x)),"formula":formula,
      "beta":b,"se_hc3":se,"ci95_beta":[lo,hi],"p_value":p,
      "negative_ci_support":bool(hi<0),
      "df_resid":float(fit.df_resid),
      "species":[
        {"species":str(r.species),"huang_species":str(r.huang_species),"family":str(r.Family),
         "svl_mm":float(getattr(r,size_col)),"log_odds":float(r.log_odds),
         "wet_gain_share":float(r.wet_gain_share)}
        for r in x.itertuples(index=False)
      ]
    }

def family_fit(df):
    x=df[np.isfinite(pd.to_numeric(df["median_svl"],errors="coerce")) & (pd.to_numeric(df["median_svl"],errors="coerce")>0) & (df["Family"].astype(str)!="")].copy()
    x["log_svl"]=np.log(x["median_svl"].astype(float))
    if len(x)<18 or x["Family"].nunique()<2:
        return {"estimable":False,"n_species":int(len(x)),"reason":"insufficient_species_or_family_variation"}
    formula="log_odds ~ log_svl + C(Family)"
    fit=smf.wls(formula,data=x,weights=x["weight"]).fit(cov_type="HC3")
    if fit.df_resid<10:
        return {"estimable":False,"n_species":int(len(x)),"n_families":int(x.Family.nunique()),"df_resid":float(fit.df_resid),"reason":"residual_df_below_10"}
    b=float(fit.params["log_svl"]);se=float(fit.bse["log_svl"]);p=float(fit.pvalues["log_svl"])
    lo=b-Q*se;hi=b+Q*se
    return {
      "estimable":True,"n_species":int(len(x)),"n_families":int(x.Family.nunique()),
      "df_resid":float(fit.df_resid),"formula":formula,
      "beta":b,"se_hc3":se,"ci95_beta":[lo,hi],"p_value":p,"negative_ci_support":bool(hi<0)
    }

def main():
    effects=load_effects()
    h,blob=load_huang()
    summary=build_summary(h)
    d,audit=match(effects,summary)

    primary=fit(d,"median_svl")
    adult=fit(d,"adult_median_svl")
    fam=family_fit(d)

    validation_pass=bool(
      primary.get("estimable") and primary.get("negative_ci_support") and
      (not adult.get("estimable") or adult.get("beta",0)<0)
    )

    result={
      "analysis":"naamp_body_size_filter_independent_validation_v0_1",
      "contract":"NAAMP_BODY_SIZE_FILTER_VALIDATION_CONTRACT_V0_1.json",
      "source":{
        "dataset":"Huang et al. Amphibian traits database",
        "paper_doi":"10.1111/geb.13656",
        "data_doi":"10.6084/m9.figshare.21159229.v3",
        "mirror_commit":"7b80dc0bb7f5e9ca363f5cdbcd526e658473f7a0",
        "git_blob_sha1":blob,
        "metric":"SVL"
      },
      "matched_species":int(d.matched.sum()),
      "unmatched_species":[str(x) for x in d.loc[~d.matched,"species"].tolist()],
      "taxonomy_audit":audit,
      "primary_all_rows_median_svl":primary,
      "adult_only_median_svl":adult,
      "family_adjusted_sensitivity":fam,
      "validation_pass":validation_pass,
      "interpretation_boundary":{
        "independence":"Independent trait compilation, same NAAMP species response.",
        "mechanism":"Body size may proxy other life-history axes.",
        "phylogeny":"Family adjustment is coarse; no phylogenetic comparative model.",
        "causality":"No causal rainfall claim."
      }
    }
    Path("NAAMP_BODY_SIZE_FILTER_VALIDATION_RECEIPT_V0_1.json").write_text(
      json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8"
    )
    print(json.dumps(result,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
