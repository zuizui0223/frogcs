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

SOURCE_URL="https://raw.githubusercontent.com/panpipiens/amphibian-vulnerability-analysis/a7be17ae44b8a81349c37b3b38c767e6db5958f2/processed_data/master_iucn_spine_nearctic_anura.csv"
SOURCE_BLOB_SHA1="4a1fd99f9b815cc512ce3e680497b34e8c9c93e6"
ALIASES={"Hyla":"Dryophytes","Dryophytes":"Hyla","Lithobates":"Rana","Rana":"Lithobates"}
EXPECTED_SPECIES=29
Q95=1.959963984540054
B=100000
SEED=20260925

MONTHS={
    "january":1,"jan":1,
    "february":2,"feb":2,
    "march":3,"mar":3,
    "april":4,"apr":4,
    "may":5,
    "june":6,"jun":6,
    "july":7,"jul":7,
    "august":8,"aug":8,
    "september":9,"sept":9,"sep":9,
    "october":10,"oct":10,
    "november":11,"nov":11,
    "december":12,"dec":12,
}
SEASONS={
    "spring":{3,4,5},
    "summer":{6,7,8},
    "fall":{9,10,11},
    "autumn":{9,10,11},
    "winter":{12,1,2},
}
YEAR_ROUND=["year round","year-round","throughout the year","all year"]

MONTH_ALT="|".join(sorted((re.escape(k) for k in MONTHS),key=len,reverse=True))
RANGE_RE=re.compile(
    rf"\b(?:early\s+|mid\s+|late\s+)?({MONTH_ALT})\b\s*"
    rf"(?:-|to|through)\s*"
    rf"(?:early\s+|mid\s+|late\s+)?({MONTH_ALT})\b",
    re.I,
)
MONTH_RE=re.compile(rf"\b({MONTH_ALT})\b",re.I)

def fetch_bytes(url):
    req=urllib.request.Request(url,headers={"User-Agent":"frogcs-breeding-season-filter/0.1"})
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

def load_adjusted():
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

def load_traits():
    b=fetch_bytes(SOURCE_URL)
    got=git_blob_sha1(b)
    if got!=SOURCE_BLOB_SHA1:
        raise SystemExit(f"trait transport blob drift: {got}")
    d=pd.read_csv(io.BytesIO(b))
    required=["sci_clean","atraiu_n_records","atraiu_breeding_season"]
    miss=[x for x in required if x not in d.columns]
    if miss:
        raise SystemExit(f"missing source columns: {miss}")
    d["species_norm"]=d["sci_clean"].map(norm)
    if d["species_norm"].duplicated().any():
        dup=d.loc[d["species_norm"].duplicated(keep=False),"species_norm"].unique().tolist()
        raise SystemExit(f"duplicate trait species: {dup[:20]}")
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
            raise SystemExit(f"ambiguous match {sp}: {hits}")
        else:
            chosen=None

        base=r.to_dict()
        if chosen is None:
            base.update({"matched":False,"trait_species":None,"family":"","breeding_season_text":None})
            audit.append({"naamp_species":sp,"matched":False,"trait_species":None,"match_type":None})
        else:
            tr=traits.iloc[idx[chosen]]
            raw=tr.get("atraiu_breeding_season",np.nan)
            txt=None if pd.isna(raw) else str(raw).strip()
            base.update({
                "matched":True,
                "trait_species":chosen,
                "family":choose_family(tr),
                "breeding_season_text":txt,
                "atraiu_n_records":pd.to_numeric(tr.get("atraiu_n_records"),errors="coerce"),
            })
            audit.append({
                "naamp_species":sp,"matched":True,"trait_species":chosen,
                "match_type":"exact" if chosen==sp else "frozen_genus_alias",
                "family":base["family"]
            })
        rows.append(base)
    return pd.DataFrame(rows),audit

def expand_range(a,b):
    a=MONTHS[a.lower()];b=MONTHS[b.lower()]
    out={a}
    cur=a
    for _ in range(11):
        if cur==b:
            break
        cur=1 if cur==12 else cur+1
        out.add(cur)
        if cur==b:
            break
    return out

def parse_breeding_season(text):
    if text is None:
        return set()
    s=str(text).lower().replace("–","-").replace("—","-")
    if not s.strip() or s.strip()=="nan":
        return set()
    if any(p in s for p in YEAR_ROUND):
        return set(range(1,13))
    months=set()
    for m in RANGE_RE.finditer(s):
        months.update(expand_range(m.group(1),m.group(2)))
    for m in MONTH_RE.finditer(s):
        months.add(MONTHS[m.group(1).lower()])
    for word,vals in SEASONS.items():
        if re.search(rf"\b{word}\b",s):
            months.update(vals)
    return months

def derive(d):
    x=d.copy()
    parsed=[]
    for txt in x["breeding_season_text"].tolist():
        months=parse_breeding_season(txt)
        parsed.append({
            "months":sorted(months),
            "breadth":float(len(months)) if months else np.nan
        })
    x["breeding_months"]=[p["months"] for p in parsed]
    x["breeding_season_breadth_months"]=[p["breadth"] for p in parsed]
    x["breadth_group"]=np.select(
        [
            x["breeding_season_breadth_months"].between(1,3,inclusive="both"),
            x["breeding_season_breadth_months"].between(4,5,inclusive="both"),
            x["breeding_season_breadth_months"].between(6,12,inclusive="both"),
        ],
        ["short_1_3","intermediate_4_5","long_6_12"],
        default="unparsed"
    )
    return x

def fit_primary(d):
    x=d[d["matched"] & np.isfinite(pd.to_numeric(d["breeding_season_breadth_months"],errors="coerce"))].copy()
    if len(x)<15 or x["breeding_season_breadth_months"].nunique()<2:
        return {"estimable":False,"n_species":int(len(x)),"reason":"insufficient_coverage_or_variation"},x
    fit=smf.wls(
        "adjusted_log_odds ~ breeding_season_breadth_months",
        data=x,weights=x["weight"]
    ).fit(cov_type="HC3")
    b=float(fit.params["breeding_season_breadth_months"])
    se=float(fit.bse["breeding_season_breadth_months"])
    p=float(fit.pvalues["breeding_season_breadth_months"])
    lo=b-Q95*se;hi=b+Q95*se
    groups={}
    for cls,g in x.groupby("breadth_group"):
        w=np.asarray(g["weight"],float);y=np.asarray(g["adjusted_log_odds"],float)
        groups[str(cls)]={
            "n_species":int(len(g)),
            "mean_breadth_months":float(g["breeding_season_breadth_months"].mean()),
            "weighted_mean_adjusted_log_odds":float(np.sum(w*y)/np.sum(w)),
            "mean_adjusted_wet_probability":float(g["adjusted_wet_probability"].mean()),
            "species":sorted(g["species"].astype(str).tolist())
        }
    return {
        "estimable":True,"n_species":int(len(x)),
        "beta_per_month":b,"se_hc3":se,"ci95_beta":[lo,hi],"p_value":p,
        "negative_ci_support":bool(hi<0),
        "group_summary":groups
    },x

def within_family_permutation(x):
    y=x[(x["family"].astype(str)!="")].copy()
    if len(y)<15:
        return {"estimable":False,"n_species":int(len(y)),"reason":"below_minimum"}

    fams={str(fam):g.index.to_numpy() for fam,g in y.groupby("family")}
    pos={idx:i for i,idx in enumerate(y.index)}
    yy=np.asarray(y["adjusted_log_odds"],float)
    ww=np.asarray(y["weight"],float)
    base=np.asarray(y["breeding_season_breadth_months"],float)

    def statistic(xx):
        xc=np.zeros(len(y));yc=np.zeros(len(y))
        for fam,idxs in fams.items():
            loc=np.array([pos[i] for i in idxs],int)
            wf=ww[loc]
            mx=np.sum(wf*xx[loc])/np.sum(wf)
            my=np.sum(wf*yy[loc])/np.sum(wf)
            xc[loc]=xx[loc]-mx
            yc[loc]=yy[loc]-my
        den=np.sum(ww*xc*xc)
        if den<=0:return np.nan
        return float(np.sum(ww*xc*yc)/den)

    observed=statistic(base)
    if not np.isfinite(observed):
        return {"estimable":False,"n_species":int(len(y)),"reason":"no_within_family_breadth_variation"}

    rng=np.random.default_rng(SEED)
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
    pneg=(1+np.sum(vals<=observed))/(1+len(vals))
    variation={}
    for fam,idxs in fams.items():
        loc=np.array([pos[i] for i in idxs],int)
        variation[fam]=sorted(set(float(v) for v in base[loc]))
    return {
        "estimable":True,"n_species":int(len(y)),"n_families":int(len(fams)),
        "family_breadth_values":variation,
        "observed_weighted_within_family_slope":observed,
        "permutations":int(len(vals)),"seed":SEED,
        "two_sided_p":float(p2),"negative_tail_p":float(pneg),
        "permutation_mean":float(np.mean(vals)),"permutation_sd":float(np.std(vals,ddof=1)),
        "q025":float(np.quantile(vals,.025)),"q975":float(np.quantile(vals,.975)),
        "negative_support":bool(pneg<0.05)
    }

def main():
    effects,adj=load_adjusted()
    traits,blob=load_traits()
    joined,audit=match(effects,traits)
    joined=derive(joined)

    primary,x=fit_primary(joined)
    fam=within_family_permutation(x) if primary.get("estimable") else {"estimable":False,"reason":"primary_nonestimable"}

    coverage={
        "response_species":int(len(joined)),
        "matched_trait_transport":int(joined["matched"].sum()),
        "parsed_breeding_season_species":int(np.isfinite(pd.to_numeric(joined["breeding_season_breadth_months"],errors="coerce")).sum()),
        "breadth_group_counts":{str(k):int(v) for k,v in joined["breadth_group"].value_counts(dropna=False).to_dict().items()},
    }

    result={
        "analysis":"naamp_breeding_season_filter_v0_1",
        "contract":"NAAMP_BREEDING_SEASON_FILTER_CONTRACT_V0_1.json",
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
            "transport_git_blob_sha1":blob,
            "field":"atraiu_breeding_season"
        },
        "taxonomy_audit":audit,
        "coverage":coverage,
        "primary":primary,
        "within_family_permutation":fam,
        "species_table":[
            {
                "species":str(r.species),
                "trait_species":None if pd.isna(r.trait_species) else str(r.trait_species),
                "family":str(r.family),
                "adjusted_log_odds":float(r.adjusted_log_odds),
                "adjusted_se":float(r.adjusted_se),
                "adjusted_wet_probability":float(r.adjusted_wet_probability),
                "breeding_season_text":None if r.breeding_season_text is None else str(r.breeding_season_text),
                "parsed_months":list(r.breeding_months),
                "breadth_months":None if not np.isfinite(r.breeding_season_breadth_months) else float(r.breeding_season_breadth_months),
                "breadth_group":str(r.breadth_group),
            }
            for r in joined.itertuples(index=False)
        ],
        "interpretation_boundary":{
            "status":"post-opening mechanistic follow-up frozen before full breeding-season join readback",
            "local_phenology_measured":False,
            "explosive_prolonged_directly_classified":False,
            "causal_claim_authorized":False,
            "other_traits_opened_for_inference":False
        }
    }
    Path("NAAMP_BREEDING_SEASON_FILTER_RECEIPT_V0_1.json").write_text(
        json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8"
    )
    print(json.dumps(result,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
