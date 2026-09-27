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

SOURCE_URL="https://raw.githubusercontent.com/panpipiens/amphibian-vulnerability-analysis/a7be17ae44b8a81349c37b3b38c767e6db5958f2/processed_data/master_iucn_spine_nearctic_anura.csv"
SOURCE_BLOB_SHA1="4a1fd99f9b815cc512ce3e680497b34e8c9c93e6"
ALIASES={"Hyla":"Dryophytes","Dryophytes":"Hyla","Lithobates":"Rana","Rana":"Lithobates"}
EXPECTED_SPECIES=29
Q95=1.959963984540054
B=100000
SEED=20260925

def fetch_bytes(url):
    req=urllib.request.Request(url,headers={"User-Agent":"frogcs-hydroperiod-filter/0.1"})
    with urllib.request.urlopen(req,timeout=120) as r:
        return r.read()

def git_blob_sha1(b):
    h=hashlib.sha1()
    h.update(f"blob {len(b)}\0".encode())
    h.update(b)
    return h.hexdigest()

def norm(x):
    toks=str(x or "").strip().split()
    return " ".join(toks[:2]) if len(toks)>=2 else str(x or "").strip()

def load_adjusted_response():
    p=Path("NAAMP_SPECIES_PULSE_ADJUSTED_ROBUSTNESS_RECEIPT_V0_1.json")
    if not p.is_file():
        raise SystemExit("adjusted species-response receipt missing")
    obj=json.loads(p.read_text(encoding="utf-8"))
    if int(obj.get("fixed_species_family",-1))!=EXPECTED_SPECIES:
        raise SystemExit(f"species family drift: {obj.get('fixed_species_family')}")
    rows=[]
    for x in obj["species_results"]:
        if not x.get("estimable"):
            continue
        se=float(x["intercept_se_cluster"])
        if not np.isfinite(se) or se<=0:
            continue
        rows.append({
            "species":norm(x["species"]),
            "adjusted_log_odds":float(x["intercept_log_odds"]),
            "adjusted_se":se,
            "adjusted_wet_probability":float(x["adjusted_wet_probability"]),
            "weight":1.0/(se*se),
        })
    if len(rows)!=EXPECTED_SPECIES:
        raise SystemExit(f"estimable species drift: {len(rows)}")
    return pd.DataFrame(rows),obj

def load_trait_transport():
    b=fetch_bytes(SOURCE_URL)
    got=git_blob_sha1(b)
    if got!=SOURCE_BLOB_SHA1:
        raise SystemExit(f"trait transport blob drift: {got}")
    d=pd.read_csv(io.BytesIO(b))
    required=[
        "sci_clean","atraiu_n_records",
        "atraiu_perm_lentic","atraiu_perm_lotic",
        "atraiu_temp_lentic","atraiu_temp_lotic"
    ]
    miss=[x for x in required if x not in d.columns]
    if miss:
        raise SystemExit(f"missing source columns: {miss}")
    d["species_norm"]=d["sci_clean"].map(norm)
    if d["species_norm"].duplicated().any():
        dup=d.loc[d["species_norm"].duplicated(keep=False),"species_norm"].unique().tolist()
        raise SystemExit(f"duplicate trait transport species: {dup[:20]}")
    return d,got

def choose_family(row):
    for col in ["family_amphibio","Family"]:
        if col in row.index:
            s=str(row.get(col,"") or "").strip()
            if s and s.lower()!="nan":
                return s.title()
    return ""

def match(effects,traits):
    idx={s:i for i,s in enumerate(traits["species_norm"].tolist())}
    rows=[];audit=[]
    for _,r in effects.iterrows():
        sp=r["species"]
        candidates=[sp]
        toks=sp.split()
        if len(toks)==2 and toks[0] in ALIASES:
            candidates.append(ALIASES[toks[0]]+" "+toks[1])
        hits=[c for c in candidates if c in idx]
        if sp in hits:
            chosen=sp
        elif len(hits)==1:
            chosen=hits[0]
        elif len(hits)>1:
            raise SystemExit(f"ambiguous trait match {sp}: {hits}")
        else:
            chosen=None

        base=r.to_dict()
        if chosen is None:
            base.update({"matched":False,"trait_species":None,"family":"","atraiu_n_records":np.nan})
            for c in ["perm_lentic","perm_lotic","temp_lentic","temp_lotic"]:
                base[c]=np.nan
            audit.append({"naamp_species":sp,"matched":False,"trait_species":None,"match_type":None})
            rows.append(base)
            continue

        tr=traits.iloc[idx[chosen]]
        base.update({
            "matched":True,
            "trait_species":chosen,
            "family":choose_family(tr),
            "atraiu_n_records":pd.to_numeric(tr.get("atraiu_n_records"),errors="coerce"),
        })
        for src,dst in [
            ("atraiu_perm_lentic","perm_lentic"),
            ("atraiu_perm_lotic","perm_lotic"),
            ("atraiu_temp_lentic","temp_lentic"),
            ("atraiu_temp_lotic","temp_lotic"),
        ]:
            base[dst]=pd.to_numeric(tr.get(src),errors="coerce")
        audit.append({
            "naamp_species":sp,"matched":True,"trait_species":chosen,
            "match_type":"exact" if chosen==sp else "frozen_genus_alias",
            "family":base["family"]
        })
        rows.append(base)
    return pd.DataFrame(rows),audit

def derive_hydroperiod(d):
    x=d.copy()
    for c in ["perm_lentic","perm_lotic","temp_lentic","temp_lotic"]:
        x[c]=pd.to_numeric(x[c],errors="coerce")
    x["temp_any"]=x[["temp_lentic","temp_lotic"]].max(axis=1,skipna=True)
    x["perm_any"]=x[["perm_lentic","perm_lotic"]].max(axis=1,skipna=True)
    x["has_water_type"]=(x["temp_any"].fillna(0)>0)|(x["perm_any"].fillna(0)>0)
    x["hydroperiod_axis"]=x["temp_any"].fillna(0)-x["perm_any"].fillna(0)
    x["hydroperiod_class"]=np.select(
        [
            (x["temp_any"]==1)&(x["perm_any"]!=1),
            (x["temp_any"]==1)&(x["perm_any"]==1),
            (x["temp_any"]!=1)&(x["perm_any"]==1),
        ],
        ["temporary_only","flexible_both","permanent_only"],
        default="undocumented"
    )
    return x

def fit_primary(d):
    x=d[d["matched"] & d["has_water_type"] & np.isfinite(d["hydroperiod_axis"])].copy()
    if len(x)<15 or x["hydroperiod_axis"].nunique()<2:
        return {"estimable":False,"n_species":int(len(x)),"reason":"insufficient_coverage_or_variation"},x
    fit=smf.wls("adjusted_log_odds ~ hydroperiod_axis",data=x,weights=x["weight"]).fit(cov_type="HC3")
    b=float(fit.params["hydroperiod_axis"])
    se=float(fit.bse["hydroperiod_axis"])
    p=float(fit.pvalues["hydroperiod_axis"])
    lo=b-Q95*se;hi=b+Q95*se
    groups={}
    for cls,g in x.groupby("hydroperiod_class"):
        w=np.asarray(g["weight"],float);y=np.asarray(g["adjusted_log_odds"],float)
        groups[str(cls)]={
            "n_species":int(len(g)),
            "weighted_mean_adjusted_log_odds":float(np.sum(w*y)/np.sum(w)),
            "mean_adjusted_wet_probability":float(g["adjusted_wet_probability"].mean()),
            "species":sorted(g["species"].astype(str).tolist())
        }
    return {
        "estimable":True,"n_species":int(len(x)),
        "beta":b,"se_hc3":se,"ci95_beta":[lo,hi],"p_value":p,
        "positive_ci_support":bool(lo>0),
        "group_summary":groups
    },x

def descriptive_temp_perm(x):
    a=x[x["hydroperiod_class"]=="temporary_only"]
    b=x[x["hydroperiod_class"]=="permanent_only"]
    if len(a)==0 or len(b)==0:
        return {"estimable":False,"reason":"one_exact_group_absent"}
    def wm(g):
        w=np.asarray(g["weight"],float);y=np.asarray(g["adjusted_log_odds"],float)
        return float(np.sum(w*y)/np.sum(w))
    ma=wm(a);mb=wm(b)
    return {
        "estimable":True,
        "temporary_only_n":int(len(a)),
        "permanent_only_n":int(len(b)),
        "temporary_weighted_mean_log_odds":ma,
        "permanent_weighted_mean_log_odds":mb,
        "difference_temp_minus_perm":ma-mb
    }

def within_family_permutation(x):
    y=x[(x["family"].astype(str)!="")].copy()
    if len(y)<15:
        return {"estimable":False,"n_species":int(len(y)),"reason":"below_minimum"}

    # weighted within-family centering
    fams={}
    for fam,g in y.groupby("family"):
        fams[str(fam)]=g.index.to_numpy()

    def statistic(axis_values):
        xx=np.asarray(axis_values,float)
        yy=np.asarray(y["adjusted_log_odds"],float)
        ww=np.asarray(y["weight"],float)
        xc=np.zeros(len(y));yc=np.zeros(len(y))
        pos={idx:i for i,idx in enumerate(y.index)}
        for fam,idxs in fams.items():
            loc=np.array([pos[i] for i in idxs],int)
            wf=ww[loc]
            mx=np.sum(wf*xx[loc])/np.sum(wf)
            my=np.sum(wf*yy[loc])/np.sum(wf)
            xc[loc]=xx[loc]-mx
            yc[loc]=yy[loc]-my
        denom=np.sum(ww*xc*xc)
        if denom<=0:
            return np.nan
        return float(np.sum(ww*xc*yc)/denom)

    observed=statistic(y["hydroperiod_axis"].to_numpy())
    if not np.isfinite(observed):
        return {"estimable":False,"n_species":int(len(y)),"reason":"no_within_family_hydroperiod_variation"}

    rng=np.random.default_rng(SEED)
    base=np.asarray(y["hydroperiod_axis"],float)
    pos={idx:i for i,idx in enumerate(y.index)}
    vals=np.empty(B,float)
    for b in range(B):
        perm=base.copy()
        for fam,idxs in fams.items():
            loc=np.array([pos[i] for i in idxs],int)
            if len(loc)>1:
                perm[loc]=rng.permutation(perm[loc])
        vals[b]=statistic(perm)
    vals=vals[np.isfinite(vals)]
    p2=(1+np.sum(np.abs(vals)>=abs(observed)))/(1+len(vals))
    ppos=(1+np.sum(vals>=observed))/(1+len(vals))
    counts={fam:int(len(idxs)) for fam,idxs in fams.items()}
    variation={}
    for fam,idxs in fams.items():
        loc=np.array([pos[i] for i in idxs],int)
        variation[fam]=sorted(set(float(v) for v in base[loc]))
    return {
        "estimable":True,"n_species":int(len(y)),"n_families":int(len(fams)),
        "family_counts":counts,"family_axis_values":variation,
        "observed_weighted_within_family_slope":observed,
        "permutations":int(len(vals)),"seed":SEED,
        "two_sided_p":float(p2),"positive_tail_p":float(ppos),
        "permutation_mean":float(np.mean(vals)),"permutation_sd":float(np.std(vals,ddof=1)),
        "q025":float(np.quantile(vals,.025)),"q975":float(np.quantile(vals,.975)),
        "positive_support":bool(ppos<0.05)
    }

def main():
    effects,adj=load_adjusted_response()
    traits,blob=load_trait_transport()
    joined,audit=match(effects,traits)
    joined=derive_hydroperiod(joined)

    primary,x=fit_primary(joined)
    exact=descriptive_temp_perm(x) if primary.get("estimable") else {"estimable":False,"reason":"primary_nonestimable"}
    fam=within_family_permutation(x) if primary.get("estimable") else {"estimable":False,"reason":"primary_nonestimable"}

    coverage={
        "response_species":int(len(joined)),
        "matched_trait_transport":int(joined["matched"].sum()),
        "atraiu_records_present":int((pd.to_numeric(joined["atraiu_n_records"],errors="coerce").fillna(0)>0).sum()),
        "primary_hydroperiod_species":int(len(x)) if primary.get("estimable") else int((joined["matched"]&joined["has_water_type"]).sum()),
        "hydroperiod_class_counts":{str(k):int(v) for k,v in joined["hydroperiod_class"].value_counts(dropna=False).to_dict().items()}
    }

    result={
        "analysis":"naamp_hydroperiod_filter_v0_1",
        "contract":"NAAMP_HYDROPERIOD_FILTER_CONTRACT_V0_1.json",
        "response_source":{
            "contract":adj.get("contract"),
            "fixed_species_family":adj.get("fixed_species_family"),
            "estimable_species":adj.get("estimable_species"),
            "heterogeneity_test":adj.get("heterogeneity_test")
        },
        "trait_source":{
            "scientific_source":"ATraiU",
            "doi":"10.1002/ecy.3261",
            "transport_repository":"panpipiens/amphibian-vulnerability-analysis",
            "transport_commit":"a7be17ae44b8a81349c37b3b38c767e6db5958f2",
            "transport_git_blob_sha1":blob
        },
        "taxonomy_audit":audit,
        "coverage":coverage,
        "primary":primary,
        "temporary_vs_permanent_descriptive":exact,
        "within_family_permutation":fam,
        "species_table":[
            {
                "species":str(r.species),
                "trait_species":None if pd.isna(r.trait_species) else str(r.trait_species),
                "family":str(r.family),
                "adjusted_log_odds":float(r.adjusted_log_odds),
                "adjusted_se":float(r.adjusted_se),
                "adjusted_wet_probability":float(r.adjusted_wet_probability),
                "temp_any":None if not np.isfinite(r.temp_any) else float(r.temp_any),
                "perm_any":None if not np.isfinite(r.perm_any) else float(r.perm_any),
                "hydroperiod_axis":None if not np.isfinite(r.hydroperiod_axis) else float(r.hydroperiod_axis),
                "hydroperiod_class":str(r.hydroperiod_class),
            }
            for r in joined.itertuples(index=False)
        ],
        "interpretation_boundary":{
            "status":"post-opening mechanistic follow-up frozen before full trait join readback",
            "local_hydroperiod_measured":False,
            "causal_claim_authorized":False,
            "other_atraiu_traits_opened_for_inference":False
        }
    }
    Path("NAAMP_HYDROPERIOD_FILTER_RECEIPT_V0_1.json").write_text(
        json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8"
    )
    print(json.dumps(result,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
