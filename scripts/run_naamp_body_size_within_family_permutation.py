#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

B=100000
SEED=20260925

def load_joined():
    adj=json.loads(Path("NAAMP_SPECIES_PULSE_ADJUSTED_ROBUSTNESS_RECEIPT_V0_1.json").read_text())
    bsz=json.loads(Path("NAAMP_BODY_SIZE_ADJUSTED_SPECIES_ROBUSTNESS_RECEIPT_V0_1.json").read_text())

    size_map={}
    for x in bsz["taxonomy_audit"]:
        if not x.get("matched"):
            continue
        size_map[x["naamp_species"]]=x["amphibio_species"]

    # Reconstruct body-size values from the detailed primary species list if available,
    # otherwise fail closed rather than re-open trait source here.
    # Current receipt primary does not carry species values, so use companion script to
    # rematch AmphiBIO deterministically.
    import importlib.util
    root=Path(__file__).resolve().parent
    src=root/"run_naamp_body_size_adjusted_species_robustness.py"
    spec=importlib.util.spec_from_file_location("bs",src)
    bs=importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(bs)

    adjusted,_=bs.load_adjusted()
    t,_=bs.trait.load_traits()
    d,_=bs.match_traits(adjusted,t)
    d=d[d.matched & np.isfinite(d.Body_size_mm) & (d.Body_size_mm>0) & (d.Family.astype(str)!="")].copy()
    d["log_body_size"]=np.log(d.Body_size_mm.astype(float))
    if len(d)!=26:
        raise SystemExit(f"complete species drift: {len(d)}")
    return d

def weighted_within_family_slope(d):
    x=d.copy()
    xc=np.zeros(len(x),float)
    yc=np.zeros(len(x),float)
    for fam,idx in x.groupby("Family").groups.items():
        ii=np.array(list(idx),dtype=int)
        w=x.loc[ii,"weight"].to_numpy(float)
        xx=x.loc[ii,"log_body_size"].to_numpy(float)
        yy=x.loc[ii,"adjusted_log_odds"].to_numpy(float)
        if len(ii)<2:
            xc[ii]=0.0
            yc[ii]=0.0
            continue
        xbar=np.sum(w*xx)/np.sum(w)
        ybar=np.sum(w*yy)/np.sum(w)
        xc[ii]=xx-xbar
        yc[ii]=yy-ybar
    w=x.weight.to_numpy(float)
    den=float(np.sum(w*xc*xc))
    if den<=0:
        raise SystemExit("no within-family body-size variation")
    return float(np.sum(w*xc*yc)/den)

def family_slopes(d):
    out=[]
    for fam,g in d.groupby("Family"):
        if len(g)<5:
            continue
        x=g.log_body_size.to_numpy(float)
        y=g.adjusted_log_odds.to_numpy(float)
        w=g.weight.to_numpy(float)
        xbar=np.sum(w*x)/np.sum(w)
        ybar=np.sum(w*y)/np.sum(w)
        den=np.sum(w*(x-xbar)**2)
        b=np.sum(w*(x-xbar)*(y-ybar))/den if den>0 else np.nan
        out.append({
            "family":str(fam),
            "n_species":int(len(g)),
            "weighted_slope":float(b) if np.isfinite(b) else None,
            "body_size_range_log":[float(np.min(x)),float(np.max(x))]
        })
    return sorted(out,key=lambda z:z["family"])

def main():
    d=load_joined().reset_index(drop=True)
    obs=weighted_within_family_slope(d)
    fam_indices={fam:np.array(list(idx),dtype=int) for fam,idx in d.groupby("Family").groups.items()}

    rng=np.random.default_rng(SEED)
    perm=np.empty(B,float)
    original=d.log_body_size.to_numpy(float).copy()
    for b in range(B):
        xp=original.copy()
        for fam,idx in fam_indices.items():
            if len(idx)>=2:
                xp[idx]=rng.permutation(xp[idx])
        d["log_body_size"]=xp
        perm[b]=weighted_within_family_slope(d)
    d["log_body_size"]=original

    two=(1+int(np.sum(np.abs(perm)>=abs(obs))))/(B+1)
    neg=(1+int(np.sum(perm<=obs)))/(B+1)

    result={
      "analysis":"naamp_body_size_within_family_permutation_v0_1",
      "contract":"NAAMP_BODY_SIZE_WITHIN_FAMILY_PERMUTATION_CONTRACT_V0_1.json",
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
