#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import io
import json
import math
import re
import urllib.request
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from scipy.stats import spearmanr

SOURCE_URL="https://raw.githubusercontent.com/panpipiens/amphibian-vulnerability-analysis/a7be17ae44b8a81349c37b3b38c767e6db5958f2/processed_data/master_iucn_spine_nearctic_anura.csv"
SOURCE_BLOB_SHA1="4a1fd99f9b815cc512ce3e680497b34e8c9c93e6"
ALIASES={"Hyla":"Dryophytes","Dryophytes":"Hyla","Lithobates":"Rana","Rana":"Lithobates"}
EXPECTED_SPECIES=29
Q=1.959963984540054
B=100000
SEED=20260926

MONTHS={
    "january":1,"jan":1,
    "february":2,"feb":2,
    "march":3,"mar":3,
    "april":4,"apr":4,
    "may":5,
    "june":6,"jun":6,
    "july":7,"jul":7,
    "august":8,"aug":8,
    "september":9,"sep":9,"sept":9,
    "october":10,"oct":10,
    "november":11,"nov":11,
    "december":12,"dec":12,
}
MONTH_RE="(?:"+"|".join(sorted((re.escape(k) for k in MONTHS),key=len,reverse=True))+")"

def fetch_bytes(url):
    req=urllib.request.Request(url,headers={"User-Agent":"frogcs-breeding-season/0.1"})
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

def month_num(token):
    return MONTHS[token.lower().strip(".")]

def inclusive_months(a,b):
    out=[a]
    cur=a
    while cur!=b:
        cur=1 if cur==12 else cur+1
        out.append(cur)
        if len(out)>12:
            raise RuntimeError("month range overflow")
    return out

def parse_breeding_months(raw):
    if raw is None or (isinstance(raw,float) and np.isnan(raw)):
        return []
    s=str(raw).lower().replace("–","-").replace("—","-")
    s=re.sub(r"\s+"," ",s).strip()
    if not s or s=="nan":
        return []

    months=set()
    occupied=[]

    range_pat=re.compile(
        rf"\b({MONTH_RE})\.?\s*(?:-|to|through)\s*({MONTH_RE})\.?\b",
        flags=re.I
    )
    for m in range_pat.finditer(s):
        a=month_num(m.group(1));b=month_num(m.group(2))
        months.update(inclusive_months(a,b))
        occupied.append((m.start(),m.end()))

    # Explicit standalone month mentions not already inside ranges.
    month_pat=re.compile(rf"\b({MONTH_RE})\.?\b",flags=re.I)
    for m in month_pat.finditer(s):
        if any(a<=m.start()<b for a,b in occupied):
            continue
        months.add(month_num(m.group(1)))

    return sorted(months)

def load_adjusted_response():
    p=Path("NAAMP_SPECIES_PULSE_ADJUSTED_ROBUSTNESS_RECEIPT_V0_1.json")
    if not p.is_file():
        raise SystemExit("adjusted species-response receipt missing")
    obj=json.loads(p.read_text(encoding="utf-8"))
    if int(obj.get("fixed_species_family",-1))!=EXPECTED_SPECIES:
        raise SystemExit("fixed species family drift")
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
    required=["sci_clean","atraiu_n_records","atraiu_breeding_season"]
    miss=[c for c in required if c not in d.columns]
    if miss:
        raise SystemExit(f"missing trait columns: {miss}")
    d["species_norm"]=d["sci_clean"].map(norm)
    if d["species_norm"].duplicated().any():
        dup=d.loc[d["species_norm"].duplicated(keep=False),"species_norm"].unique().tolist()
        raise SystemExit(f"duplicate trait species: {dup[:20]}")
    return d,got

def choose_family(row):
    for col in ["family_amphibio","Family"]:
        if col in row.index:
            v=str(row.get(col,"") or "").strip()
            if v and v.lower()!="nan":
                return v.title()
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
        hits=[x for x in candidates if x in idx]
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
            base.update({
                "matched":False,"trait_species":None,"family":"",
                "breeding_season_text":None,"breeding_months":[],"breeding_season_months":np.nan,
                "atraiu_n_records":np.nan
            })
            audit.append({"naamp_species":sp,"matched":False,"trait_species":None})
        else:
            tr=traits.iloc[idx[chosen]]
            raw=tr.get("atraiu_breeding_season")
            months=parse_breeding_months(raw)
            base.update({
                "matched":True,"trait_species":chosen,"family":choose_family(tr),
                "breeding_season_text":None if pd.isna(raw) else str(raw),
                "breeding_months":months,
                "breeding_season_months":float(len(months)) if months else np.nan,
                "atraiu_n_records":pd.to_numeric(tr.get("atraiu_n_records"),errors="coerce")
            })
            audit.append({
                "naamp_species":sp,"matched":True,"trait_species":chosen,
                "match_type":"exact" if chosen==sp else "frozen_genus_alias",
                "parsed_months":months,
                "parsed_n_months":len(months)
            })
        rows.append(base)
    return pd.DataFrame(rows),audit

def fit_primary(d):
    x=d[d["matched"] & np.isfinite(pd.to_numeric(d["breeding_season_months"],errors="coerce"))].copy()
    if len(x)<15 or x["breeding_season_months"].nunique()<2:
        return {"estimable":False,"n_species":int(len(x)),"reason":"insufficient_coverage_or_variation"},x
    fit=smf.wls("adjusted_log_odds ~ breeding_season_months",data=x,weights=x["weight"]).fit(cov_type="HC3")
    b=float(fit.params["breeding_season_months"])
    se=float(fit.bse["breeding_season_months"])
    p=float(fit.pvalues["breeding_season_months"])
    lo=b-Q*se;hi=b+Q*se
    rho,prho=spearmanr(x["breeding_season_months"],x["adjusted_log_odds"])
    return {
        "estimable":True,"n_species":int(len(x)),
        "beta":b,"se_hc3":se,"ci95_beta":[lo,hi],"p_value":p,
        "negative_ci_support":bool(hi<0),
        "spearman_rho":float(rho),"spearman_p":float(prho),
        "breadth_summary":{
            "min":float(x["breeding_season_months"].min()),
            "median":float(x["breeding_season_months"].median()),
            "max":float(x["breeding_season_months"].max())
        }
    },x

def weighted_mean(g):
    w=np.asarray(g["weight"],float);y=np.asarray(g["adjusted_log_odds"],float)
    return float(np.sum(w*y)/np.sum(w))

def exact_groups(x):
    short=x[x["breeding_season_months"]<=3]
    long=x[x["breeding_season_months"]>=6]
    if len(short)==0 or len(long)==0:
        return {"estimable":False,"short_n":int(len(short)),"long_n":int(len(long))}
    a=weighted_mean(short);b=weighted_mean(long)
    return {
        "estimable":True,
        "short_n":int(len(short)),"long_n":int(len(long)),
        "short_weighted_mean_log_odds":a,
        "long_weighted_mean_log_odds":b,
        "short_minus_long":a-b,
        "short_species":sorted(short["species"].astype(str).tolist()),
        "long_species":sorted(long["species"].astype(str).tolist())
    }

def within_family_permutation(x):
    y=x[x["family"].astype(str)!=""].copy()
    if len(y)<15:
        return {"estimable":False,"n_species":int(len(y)),"reason":"below_minimum"}
    families={str(f):g.index.to_numpy() for f,g in y.groupby("family")}
    pos={idx:i for i,idx in enumerate(y.index)}
    xx0=np.asarray(y["breeding_season_months"],float)
    yy=np.asarray(y["adjusted_log_odds"],float)
    ww=np.asarray(y["weight"],float)

    def statistic(xx):
        xc=np.zeros(len(y));yc=np.zeros(len(y))
        for fam,idxs in families.items():
            loc=np.array([pos[i] for i in idxs],int)
            wf=ww[loc]
            mx=np.sum(wf*xx[loc])/np.sum(wf)
            my=np.sum(wf*yy[loc])/np.sum(wf)
            xc[loc]=xx[loc]-mx
            yc[loc]=yy[loc]-my
        den=np.sum(ww*xc*xc)
        if den<=0:return np.nan
        return float(np.sum(ww*xc*yc)/den)

    obs=statistic(xx0)
    if not np.isfinite(obs):
        return {"estimable":False,"n_species":int(len(y)),"reason":"no_within_family_variation"}

    rng=np.random.default_rng(SEED)
    vals=np.empty(B,float)
    for b in range(B):
        xx=xx0.copy()
        for fam,idxs in families.items():
            loc=np.array([pos[i] for i in idxs],int)
            if len(loc)>1:
                xx[loc]=rng.permutation(xx[loc])
        vals[b]=statistic(xx)
    vals=vals[np.isfinite(vals)]
    p2=(1+np.sum(np.abs(vals)>=abs(obs)))/(1+len(vals))
    pneg=(1+np.sum(vals<=obs))/(1+len(vals))
    return {
        "estimable":True,"n_species":int(len(y)),"n_families":int(len(families)),
        "observed_weighted_within_family_slope":obs,
        "permutations":int(len(vals)),"seed":SEED,
        "two_sided_p":float(p2),"negative_tail_p":float(pneg),
        "negative_support":bool(pneg<0.05),
        "q025":float(np.quantile(vals,.025)),"q975":float(np.quantile(vals,.975))
    }

def main():
    effects,adj=load_adjusted_response()
    traits,blob=load_trait_transport()
    joined,audit=match(effects,traits)
    primary,x=fit_primary(joined)
    groups=exact_groups(x) if primary.get("estimable") else {"estimable":False}
    fam=within_family_permutation(x) if primary.get("estimable") else {"estimable":False}

    result={
        "analysis":"naamp_breeding_season_breadth_v0_1",
        "contract":"NAAMP_BREEDING_SEASON_BREADTH_CONTRACT_V0_1.json",
        "response_source":{
            "contract":adj.get("contract"),
            "fixed_species_family":adj.get("fixed_species_family"),
            "estimable_species":adj.get("estimable_species")
        },
        "trait_source":{
            "scientific_source":"ATraiU",
            "doi":"10.1002/ecy.3261",
            "transport_repository":"panpipiens/amphibian-vulnerability-analysis",
            "transport_commit":"a7be17ae44b8a81349c37b3b38c767e6db5958f2",
            "transport_git_blob_sha1":blob,
            "field":"atraiu_breeding_season"
        },
        "taxonomy_and_parser_audit":audit,
        "coverage":{
            "response_species":int(len(joined)),
            "matched_transport":int(joined["matched"].sum()),
            "parsed_breeding_season_species":int(np.isfinite(pd.to_numeric(joined["breeding_season_months"],errors="coerce")).sum())
        },
        "primary":primary,
        "short_vs_long_descriptive":groups,
        "within_family_permutation":fam,
        "species_table":[
            {
                "species":str(r.species),
                "trait_species":None if pd.isna(r.trait_species) else str(r.trait_species),
                "family":str(r.family),
                "adjusted_log_odds":float(r.adjusted_log_odds),
                "adjusted_wet_probability":float(r.adjusted_wet_probability),
                "breeding_season_text":None if pd.isna(r.breeding_season_text) else str(r.breeding_season_text),
                "breeding_months":r.breeding_months,
                "breeding_season_months":None if not np.isfinite(r.breeding_season_months) else float(r.breeding_season_months),
            }
            for r in joined.itertuples(index=False)
        ],
        "interpretation_boundary":{
            "proxy":"breeding-season breadth is a phenological proxy, not direct explosive-breeding classification",
            "post_opening":True,
            "causal_claim_authorized":False
        }
    }
    Path("NAAMP_BREEDING_SEASON_BREADTH_RECEIPT_V0_1.json").write_text(
        json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8"
    )
    print(json.dumps(result,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
