#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import numpy as np

B=100000
SEED=20260925

ROOT=Path(__file__).resolve().parent
SRC=ROOT/"run_naamp_body_size_adjusted_species_robustness.py"
spec=importlib.util.spec_from_file_location("bs",SRC)
bs=importlib.util.module_from_spec(spec)
assert spec.loader
spec.loader.exec_module(bs)

def load_joined():
    adjusted,_=bs.load_adjusted()
    t,_=bs.trait.load_traits()
    d,_=bs.match_traits(adjusted,t)
    d=d[
        d.matched &
        np.isfinite(d.Body_size_mm) &
        (d.Body_size_mm>0) &
        (d.Family.astype(str)!="")
    ].copy().reset_index(drop=True)
    d["log_body_size"]=np.log(d.Body_size_mm.astype(float))
    if len(d)!=26:
        raise SystemExit(f"complete species drift: {len(d)}")
    return d

def observed_slope(d):
    num=0.0;den=0.0
    for fam,g in d.groupby("Family",sort=True):
        if len(g)<2:
            continue
        w=g.weight.to_numpy(float)
        x=g.log_body_size.to_numpy(float)
        y=g.adjusted_log_odds.to_numpy(float)
        xb=np.sum(w*x)/np.sum(w)
        yb=np.sum(w*y)/np.sum(w)
        xc=x-xb;yc=y-yb
        num+=float(np.sum(w*xc*yc))
        den+=float(np.sum(w*xc*xc))
    if den<=0:
        raise SystemExit("no within-family body-size variation")
    return num/den

def permutation_slopes(d):
    rng=np.random.default_rng(SEED)
    numer=np.zeros(B,float)
    denom=np.zeros(B,float)

    for fam,g in d.groupby("Family",sort=True):
        if len(g)<2:
            continue
        w=g.weight.to_numpy(float)
        x=g.log_body_size.to_numpy(float)
        y=g.adjusted_log_odds.to_numpy(float)
        ybar=np.sum(w*y)/np.sum(w)
        yc=y-ybar

        # Each row is an independent random permutation of x within this family.
        keys=rng.random((B,len(g)))
        order=np.argsort(keys,axis=1)
        xp=x[order]

        xbar=(xp*w[None,:]).sum(axis=1)/w.sum()
        xc=xp-xbar[:,None]
        numer+=(xc*(w*yc)[None,:]).sum(axis=1)
        denom+=(xc*xc*w[None,:]).sum(axis=1)

    if np.any(denom<=0):
        raise SystemExit("nonpositive permutation denominator")
    return numer/denom

def family_slopes(d):
    out=[]
    for fam,g in d.groupby("Family",sort=True):
        if len(g)<5:
            continue
        w=g.weight.to_numpy(float)
        x=g.log_body_size.to_numpy(float)
        y=g.adjusted_log_odds.to_numpy(float)
        xb=np.sum(w*x)/np.sum(w)
        yb=np.sum(w*y)/np.sum(w)
        den=np.sum(w*(x-xb)**2)
        slope=np.sum(w*(x-xb)*(y-yb))/den if den>0 else np.nan
        out.append({
            "family":str(fam),
            "n_species":int(len(g)),
            "weighted_slope":float(slope) if np.isfinite(slope) else None,
            "body_size_range_log":[float(np.min(x)),float(np.max(x))]
        })
    return out

def main():
    d=load_joined()
    obs=float(observed_slope(d))
    perm=permutation_slopes(d)

    two=(1+int(np.sum(np.abs(perm)>=abs(obs))))/(B+1)
    neg=(1+int(np.sum(perm<=obs)))/(B+1)

    result={
      "analysis":"naamp_body_size_within_family_permutation_v0_1",
      "contract":"NAAMP_BODY_SIZE_WITHIN_FAMILY_PERMUTATION_CONTRACT_V0_1.json",
      "implementation":"vectorized exact-contract implementation",
      "n_species":int(len(d)),
      "n_families":int(d.Family.nunique()),
      "family_counts":{str(k):int(v) for k,v in d.Family.value_counts().sort_index().items()},
      "observed_weighted_within_family_slope":obs,
      "permutations":B,
      "seed":SEED,
      "two_sided_p":float(two),
      "negative_tail_p":float(neg),
      "permutation_summary":{
        "mean":float(np.mean(perm)),
        "sd":float(np.std(perm,ddof=1)),
        "q025":float(np.quantile(perm,.025)),
        "q975":float(np.quantile(perm,.975))
      },
      "family_specific_descriptive":family_slopes(d),
      "negative_support":bool(obs<0 and two<.05),
      "interpretation_boundary":{
        "not_phylogenetic_model":True,
        "body_size_proxy":True,
        "post_discovery_robustness":True,
        "causal_claim_authorized":False
      }
    }
    Path("NAAMP_BODY_SIZE_WITHIN_FAMILY_PERMUTATION_RECEIPT_V0_1.json").write_text(
      json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8"
    )
    print(json.dumps(result,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
