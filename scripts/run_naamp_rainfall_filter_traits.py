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
import statsmodels.api as sm
import statsmodels.formula.api as smf

AMPHIBIO_URL="https://raw.githubusercontent.com/rdmpage/amphibio/c437acbc65b51b66e3dc4abd821ebe1cb06b200c/AmphiBIO_v1.csv"
AMPHIBIO_BLOB_SHA1="f98650972f3266c24962f70738799a39a8310e87"
EXPECTED_N=29
EXPECTED_WET=4483
EXPECTED_DRY=4104
ALIASES={"Hyla":"Dryophytes","Dryophytes":"Hyla","Lithobates":"Rana","Rana":"Lithobates"}
Q=1.959963984540054

def fetch_bytes(url: str) -> bytes:
    req=urllib.request.Request(url,headers={"User-Agent":"frogcs-trait-test/0.1"})
    with urllib.request.urlopen(req,timeout=120) as r:
        return r.read()

def git_blob_sha1(b: bytes) -> str:
    h=hashlib.sha1()
    h.update(f"blob {len(b)}\0".encode())
    h.update(b)
    return h.hexdigest()

def normalize_binomial(x: str) -> str:
    toks=str(x or "").strip().split()
    return " ".join(toks[:2]) if len(toks)>=2 else str(x or "").strip()

def parse_binary(v):
    if pd.isna(v):
        return np.nan
    s=str(v).strip()
    if s=="" or s.upper()=="NA":
        return np.nan
    try:
        x=float(s)
    except Exception:
        return np.nan
    if x in (0.0,1.0):
        return x
    return np.nan

def load_effects():
    p=Path("NAAMP_SPECIES_PULSE_HETEROGENEITY_RECEIPT_V0_1.json")
    if not p.is_file():
        raise SystemExit("species-response receipt missing; run species-pulse analysis first")
    obj=json.loads(p.read_text(encoding="utf-8"))
    g=obj["global"]
    if int(g["eligible_species"])!=EXPECTED_N:
        raise SystemExit(f"eligible species drift: {g['eligible_species']}")
    if int(g["eligible_wet_gains"])!=EXPECTED_WET or int(g["eligible_dry_losses"])!=EXPECTED_DRY:
        raise SystemExit("eligible gain/loss totals drift")
    rows=[]
    for x in obj["species_results"]:
        w=int(x["wet_gains"]); d=int(x["dry_losses"])
        logod=math.log((w+0.5)/(d+0.5))
        var=1.0/(w+0.5)+1.0/(d+0.5)
        rows.append({
            "species":normalize_binomial(x["species_code"]),
            "wet_gains":w,"dry_losses":d,
            "discordant_pairs":w+d,
            "wet_gain_share":w/(w+d),
            "log_odds":logod,
            "log_odds_var":var,
            "weight":1.0/var,
            "fdr_species":float(x["fdr_bh"]),
            "species_direction":x["direction"],
        })
    return pd.DataFrame(rows),obj

def load_traits():
    b=fetch_bytes(AMPHIBIO_URL)
    got=git_blob_sha1(b)
    if got!=AMPHIBIO_BLOB_SHA1:
        raise SystemExit(f"AmphiBIO blob drift: {got}")
    # Mirror is UTF-8 converted; fall back defensively.
    try:
        t=pd.read_csv(io.BytesIO(b),encoding="utf-8")
    except UnicodeDecodeError:
        t=pd.read_csv(io.BytesIO(b),encoding="cp1252")
    if "Species" not in t.columns:
        raise SystemExit(f"AmphiBIO Species column absent: {list(t.columns)}")
    t["species_norm"]=t["Species"].map(normalize_binomial)
    if t["species_norm"].duplicated().any():
        # Duplicate scientific names would make deterministic matching ambiguous.
        dups=t.loc[t["species_norm"].duplicated(keep=False),"species_norm"].unique().tolist()
        raise SystemExit(f"duplicate AmphiBIO Species names: {dups[:20]}")
    return t,got

def match_traits(effects,t):
    idx={s:i for i,s in enumerate(t["species_norm"].tolist())}
    matched=[]
    audit=[]
    for _,r in effects.iterrows():
        sp=r["species"]
        candidates=[sp]
        toks=sp.split()
        if len(toks)==2 and toks[0] in ALIASES:
            candidates.append(ALIASES[toks[0]]+" "+toks[1])
        hits=[c for c in candidates if c in idx]
        if len(hits)>1:
            # Exact match wins by frozen rule.
            chosen=sp if sp in hits else None
            if chosen is None:
                raise SystemExit(f"ambiguous alias match for {sp}: {hits}")
        elif len(hits)==1:
            chosen=hits[0]
        else:
            chosen=None

        base=r.to_dict()
        if chosen is None:
            audit.append({"naamp_species":sp,"matched":False,"amphibio_species":None,"match_type":None})
            base.update({"matched":False,"amphibio_species":None})
            matched.append(base)
            continue

        tr=t.iloc[idx[chosen]]
        audit.append({
            "naamp_species":sp,"matched":True,"amphibio_species":chosen,
            "match_type":"exact" if chosen==sp else "frozen_genus_alias"
        })
        base.update({"matched":True,"amphibio_species":chosen})
        for col in ["Wet_warm","Wet_cold","Dry_warm","Dry_cold","Fos","Aqu","Arb","Ter"]:
            base[col]=parse_binary(tr.get(col,np.nan))
        try:
            bs=float(tr.get("Body_size_mm",np.nan))
            base["Body_size_mm"]=bs if np.isfinite(bs) and bs>0 else np.nan
        except Exception:
            base["Body_size_mm"]=np.nan
        matched.append(base)
    return pd.DataFrame(matched),audit

def wls_trait(df,trait,min_n=12):
    x=df[np.isfinite(df[trait].astype(float)) & np.isfinite(df["log_odds"])].copy()
    if len(x)<min_n:
        return {"trait":trait,"estimable":False,"reason":"complete_species_below_minimum","n_species":int(len(x))}
    if x[trait].nunique()<2:
        return {"trait":trait,"estimable":False,"reason":"no_trait_variation","n_species":int(len(x))}
    formula=f"log_odds ~ {trait}"
    fit=smf.wls(formula,data=x,weights=x["weight"]).fit(cov_type="HC3")
    b=float(fit.params[trait]); se=float(fit.bse[trait]); p=float(fit.pvalues[trait])
    lo=b-Q*se; hi=b+Q*se
    return {
        "trait":trait,"estimable":True,"n_species":int(len(x)),
        "beta":b,"se_hc3":se,"ci95_beta":[lo,hi],"p_value":p,
        "weighted_mean_trait":float(np.average(x[trait],weights=x["weight"])),
        "species":[
            {"species":str(r.species),"trait":float(getattr(r,trait)),"log_odds":float(r.log_odds),
             "wet_gain_share":float(r.wet_gain_share),"weight":float(r.weight)}
            for r in x.itertuples(index=False)
        ]
    }

def bh(results):
    idx=[i for i,r in enumerate(results) if r.get("estimable")]
    if not idx:
        return results
    order=sorted(idx,key=lambda i:results[i]["p_value"])
    m=len(order); running=1.0
    adj={}
    for rr,pos in enumerate(reversed(order),start=1):
        rank=m-rr+1
        val=min(1.0,results[pos]["p_value"]*m/rank)
        running=min(running,val)
        adj[pos]=running
    for i in idx:
        results[i]["fdr_bh"]=float(adj[i])
    return results

def main():
    effects,effect_obj=load_effects()
    traits,blob=load_traits()
    d,audit=match_traits(effects,traits)

    # Frozen climatic activity axis.
    for c in ["Wet_warm","Wet_cold","Dry_warm","Dry_cold"]:
        d[c]=pd.to_numeric(d[c],errors="coerce")
    wet=d[["Wet_warm","Wet_cold"]].max(axis=1,skipna=True)
    dry=d[["Dry_warm","Dry_cold"]].max(axis=1,skipna=True)
    # Require at least one observed wet category and one observed dry category;
    # otherwise axis is missing rather than assuming absent.
    wet_known=d[["Wet_warm","Wet_cold"]].notna().any(axis=1)
    dry_known=d[["Dry_warm","Dry_cold"]].notna().any(axis=1)
    d["climatic_activity_axis"]=np.where(wet_known & dry_known,wet-dry,np.nan)
    d["log_body_size_mm"]=np.log(pd.to_numeric(d["Body_size_mm"],errors="coerce"))

    primary=wls_trait(d,"climatic_activity_axis",12)
    if primary.get("estimable"):
        primary["expected_sign"]="positive"
        primary["direction_support"]=bool(primary["ci95_beta"][0]>0)

    secondary=[wls_trait(d,t,12) for t in ["Fos","Aqu","Arb","Ter","log_body_size_mm"]]
    secondary=bh(secondary)

    missing={}
    for trait in ["climatic_activity_axis","Fos","Aqu","Arb","Ter","log_body_size_mm"]:
        missing[trait]={
            "complete":int(np.isfinite(pd.to_numeric(d[trait],errors="coerce")).sum()),
            "missing":int((~np.isfinite(pd.to_numeric(d[trait],errors="coerce"))).sum())
        }

    result={
        "analysis":"naamp_rainfall_filter_trait_test_v0_1",
        "contract":"NAAMP_RAINFALL_FILTER_TRAIT_CONTRACT_V0_1.json",
        "trait_source":{
            "dataset":"AmphiBIO v1",
            "mirror_commit":"c437acbc65b51b66e3dc4abd821ebe1cb06b200c",
            "git_blob_sha1":blob,
            "paper_doi":"10.1038/sdata.2017.123",
            "data_doi":"10.6084/m9.figshare.4644424.v5"
        },
        "effect_source":{
            "eligible_species":int(len(effects)),
            "wet_gains":int(effects.wet_gains.sum()),
            "dry_losses":int(effects.dry_losses.sum())
        },
        "taxonomy_audit":audit,
        "matched_species":int(d.matched.sum()),
        "unmatched_species":[str(x) for x in d.loc[~d.matched,"species"].tolist()],
        "missingness":missing,
        "primary":primary,
        "secondary":secondary,
        "interpretation_boundary":{
            "seasonality":"AmphiBIO climatic activity seasonality, not pond hydroperiod.",
            "phylogeny":"No phylogenetic correction; blocks evolutionary generalization.",
            "causality":"No causal rainfall claim.",
            "status":"Post-opening trait explanation frozen before external trait readback."
        }
    }
    Path("NAAMP_RAINFALL_FILTER_TRAIT_RECEIPT_V0_1.json").write_text(
        json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8"
    )
    print(json.dumps(result,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
