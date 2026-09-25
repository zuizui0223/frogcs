#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from scipy.stats import spearmanr

ROOT=Path(__file__).resolve().parent
TRAIT_SCRIPT=ROOT/"run_naamp_rainfall_filter_traits.py"
spec=importlib.util.spec_from_file_location("trait_base",TRAIT_SCRIPT)
trait=importlib.util.module_from_spec(spec)
assert spec.loader
spec.loader.exec_module(trait)

Q=1.959963984540054

def load_adjusted():
    p=Path("NAAMP_SPECIES_PULSE_ADJUSTED_ROBUSTNESS_RECEIPT_V0_1.json")
    if not p.is_file():
        raise SystemExit("adjusted species receipt missing")
    obj=json.loads(p.read_text(encoding="utf-8"))
    if int(obj.get("fixed_species_family",-1))!=29 or int(obj.get("estimable_species",-1))!=29:
        raise SystemExit("adjusted species family drift")
    rows=[]
    for x in obj["species_results"]:
        if not x.get("estimable"):
            continue
        se=float(x["intercept_se_cluster"])
        if not np.isfinite(se) or se<=0:
            continue
        rows.append({
            "species":trait.normalize_binomial(x["species"]),
            "adjusted_log_odds":float(x["intercept_log_odds"]),
            "adjusted_se":se,
            "weight":1.0/(se*se),
            "adjusted_wet_probability":float(x["adjusted_wet_probability"])
        })
    return pd.DataFrame(rows),obj

def match_traits(effects,t):
    idx={s:i for i,s in enumerate(t["species_norm"].tolist())}
    rows=[];audit=[]
    for _,r in effects.iterrows():
        sp=r["species"]; candidates=[sp]
        toks=sp.split()
        if len(toks)==2 and toks[0] in trait.ALIASES:
            candidates.append(trait.ALIASES[toks[0]]+" "+toks[1])
        hits=[c for c in candidates if c in idx]
        if sp in hits:
            chosen=sp
        elif len(hits)==1:
            chosen=hits[0]
        elif len(hits)>1:
            raise SystemExit(f"ambiguous AmphiBIO match {sp}: {hits}")
        else:
            chosen=None
        base=r.to_dict()
        if chosen is None:
            base.update({"matched":False,"amphibio_species":None,"Body_size_mm":np.nan,"Family":""})
            audit.append({"naamp_species":sp,"matched":False,"amphibio_species":None,"match_type":None})
        else:
            tr=t.iloc[idx[chosen]]
            try:
                bs=float(tr.get("Body_size_mm",np.nan))
                if not np.isfinite(bs) or bs<=0:bs=np.nan
            except Exception:
                bs=np.nan
            fam=str(tr.get("Family","") or "").strip()
            base.update({"matched":True,"amphibio_species":chosen,"Body_size_mm":bs,"Family":fam})
            audit.append({"naamp_species":sp,"matched":True,"amphibio_species":chosen,"match_type":"exact" if chosen==sp else "frozen_genus_alias"})
        rows.append(base)
    return pd.DataFrame(rows),audit

def fit_primary(x):
    y=x[np.isfinite(x.Body_size_mm) & (x.Body_size_mm>0)].copy()
    y["log_body_size"]=np.log(y.Body_size_mm.astype(float))
    if len(y)<15:
        return {"estimable":False,"n_species":int(len(y)),"reason":"below_minimum"},y
    f=smf.wls("adjusted_log_odds ~ log_body_size",data=y,weights=y.weight).fit(cov_type="HC3")
    b=float(f.params["log_body_size"]);se=float(f.bse["log_body_size"]);p=float(f.pvalues["log_body_size"])
    lo=b-Q*se;hi=b+Q*se
    return {
      "estimable":True,"n_species":int(len(y)),
      "beta":b,"se_hc3":se,"ci95_beta":[lo,hi],"p_value":p,
      "negative_ci_support":bool(hi<0)
    },y

def fit_family(y):
    x=y[y.Family.astype(str)!=""].copy()
    if len(x)<18 or x.Family.nunique()<2:
        return {"estimable":False,"n_species":int(len(x)),"reason":"insufficient_species_or_family_variation"}
    formula="adjusted_log_odds ~ log_body_size + C(Family)"
    f=smf.wls(formula,data=x,weights=x.weight).fit(cov_type="HC3")
    if f.df_resid<10:
        return {"estimable":False,"n_species":int(len(x)),"n_families":int(x.Family.nunique()),"df_resid":float(f.df_resid),"reason":"residual_df_below_10"}
    b=float(f.params["log_body_size"]);se=float(f.bse["log_body_size"]);p=float(f.pvalues["log_body_size"])
    lo=b-Q*se;hi=b+Q*se
    return {
      "estimable":True,"n_species":int(len(x)),"n_families":int(x.Family.nunique()),"df_resid":float(f.df_resid),
      "beta":b,"se_hc3":se,"ci95_beta":[lo,hi],"p_value":p,"negative_ci_support":bool(hi<0)
    }

def leave_family(y):
    out=[]
    counts=y.Family.value_counts()
    families=sorted([str(f) for f,n in counts.items() if str(f) and int(n)>=2])
    for fam in families:
        x=y[y.Family!=fam].copy()
        if len(x)<15:
            out.append({"excluded_family":fam,"estimable":False,"n_species":int(len(x)),"reason":"below_minimum"})
            continue
        f=smf.wls("adjusted_log_odds ~ log_body_size",data=x,weights=x.weight).fit(cov_type="HC3")
        b=float(f.params["log_body_size"]);se=float(f.bse["log_body_size"]);p=float(f.pvalues["log_body_size"])
        lo=b-Q*se;hi=b+Q*se
        out.append({
          "excluded_family":fam,"estimable":True,"n_species":int(len(x)),
          "beta":b,"ci95_beta":[lo,hi],"p_value":p,"negative":bool(b<0),"negative_ci_support":bool(hi<0)
        })
    return out

def main():
    adjusted,adj_obj=load_adjusted()
    t,blob=trait.load_traits()
    d,audit=match_traits(adjusted,t)
    primary,y=fit_primary(d)

    if len(y)>=3:
        rho,prho=spearmanr(np.log(y.Body_size_mm.astype(float)),y.adjusted_log_odds.astype(float))
        spearman={"n_species":int(len(y)),"rho":float(rho),"p_value":float(prho)}
    else:
        spearman=None

    fam=fit_family(y)
    loo=leave_family(y)
    result={
      "analysis":"naamp_body_size_adjusted_species_robustness_v0_1",
      "contract":"NAAMP_BODY_SIZE_ADJUSTED_SPECIES_ROBUSTNESS_CONTRACT_V0_1.json",
      "trait_source":{
        "dataset":"AmphiBIO v1",
        "mirror_commit":"c437acbc65b51b66e3dc4abd821ebe1cb06b200c",
        "git_blob_sha1":blob,
        "trait":"Body_size_mm"
      },
      "adjusted_response_source":{
        "contract":adj_obj.get("contract"),
        "estimable_species":adj_obj.get("estimable_species"),
        "heterogeneity_test":adj_obj.get("heterogeneity_test"),
        "raw_adjusted_concordance":adj_obj.get("raw_adjusted_concordance")
      },
      "matched_species":int(d.matched.sum()),
      "unmatched_species":[str(x) for x in d.loc[~d.matched,"species"].tolist()],
      "taxonomy_audit":audit,
      "primary":primary,
      "spearman_sensitivity":spearman,
      "family_adjusted_sensitivity":fam,
      "leave_one_family_out":loo,
      "all_leave_one_family_slopes_negative":bool(all((not x.get("estimable")) or x.get("negative") for x in loo)),
      "boundary":{
        "body_size_proxy":True,
        "direct_hydric_mechanism_tested":False,
        "causal_claim_authorized":False
      }
    }
    Path("NAAMP_BODY_SIZE_ADJUSTED_SPECIES_ROBUSTNESS_RECEIPT_V0_1.json").write_text(
      json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8"
    )
    print(json.dumps(result,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
