#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import importlib.util
import io
import json
import time
import urllib.error
import urllib.request
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from scipy.stats import spearmanr

ROOT=Path(__file__).resolve().parents[1]
NAAMP=ROOT/"scripts"/"naamp"
OUT=ROOT/"exploration"/"NAAMP_HYDRATION_BODY_SIZE_STRONG_ACTIVATION_RECEIPT_V0_1.json"
AMPHIBIO_URL="https://raw.githubusercontent.com/rdmpage/amphibio/c437acbc65b51b66e3dc4abd821ebe1cb06b200c/AmphiBIO_v1.csv"
AMPHIBIO_BLOB_SHA1="f98650972f3266c24962f70738799a39a8310e87"
ALIASES={"Hyla":"Dryophytes","Dryophytes":"Hyla","Lithobates":"Rana","Rana":"Lithobates"}
N_PERM=10000
SEED=2840223
Q=1.959963984540054

def loadmod(name,path):
    s=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(s)
    assert s.loader
    s.loader.exec_module(m)
    return m

base=loadmod("base",NAAMP/"run_naamp_ecological_pulse.py")
spatial=loadmod("spatial",NAAMP/"run_naamp_spatial_taxonomic_activation_decomposition.py")
uniform=loadmod("uniform",NAAMP/"run_naamp_uniform_activation_null.py")
sameobs=loadmod("sameobs",NAAMP/"run_naamp_same_observer_robustness.py")

def fetch(url,headers=None,retries=6):
    last=None
    for i in range(retries):
        try:
            req=urllib.request.Request(url,headers=headers or {"User-Agent":"frogcs-hydration-body-size/0.1"})
            with urllib.request.urlopen(req,timeout=180) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            last=e
            if e.code not in (403,429,500,502,503,504):
                raise
            time.sleep(2*(i+1))
        except Exception as e:
            last=e
            time.sleep(2*(i+1))
    raise RuntimeError(f"fetch failed after retries: {last}")

def load_raw_retry():
    last=None
    for i in range(6):
        try:
            return base.load()
        except urllib.error.HTTPError as e:
            last=e
            if e.code not in (403,429,500,502,503,504):
                raise
            time.sleep(2*(i+1))
    raise RuntimeError(f"NAAMP load failed: {last}")

def git_blob_sha1(b):
    h=hashlib.sha1()
    h.update(f"blob {len(b)}\0".encode())
    h.update(b)
    return h.hexdigest()

def norm_binomial(x):
    toks=str(x or "").strip().split()
    if len(toks)<2:
        return str(x or "").strip()
    if any(mark in toks[1] for mark in ("/","complex")):
        return str(x or "").strip()
    return " ".join(toks[:2])

def load_body_size():
    b=fetch(AMPHIBIO_URL,{"User-Agent":"frogcs-hydration-body-size/0.1"})
    got=git_blob_sha1(b)
    if got!=AMPHIBIO_BLOB_SHA1:
        raise RuntimeError(f"AmphiBIO blob drift: {got}")
    try:
        t=pd.read_csv(io.BytesIO(b),encoding="utf-8")
    except UnicodeDecodeError:
        t=pd.read_csv(io.BytesIO(b),encoding="cp1252")
    t["species_norm"]=t["Species"].map(norm_binomial)
    index={str(s):i for i,s in enumerate(t["species_norm"])}
    out={}
    audit={}
    for sp in sorted(index):
        pass
    return t,index,got

def match_body(sp,t,index):
    s=norm_binomial(sp)
    cands=[s]
    toks=s.split()
    if len(toks)==2 and toks[0] in ALIASES:
        cands.append(ALIASES[toks[0]]+" "+toks[1])
    hits=[c for c in cands if c in index]
    if s in hits:
        row=t.iloc[index[s]]
        kind="exact"
    elif len(hits)==1:
        row=t.iloc[index[hits[0]]]
        kind="alias"
    else:
        return None,None,None
    x=pd.to_numeric(pd.Series([row.get("Body_size_mm",np.nan)]),errors="coerce").iloc[0]
    if not np.isfinite(x) or x<=0:
        return None,kind,str(row.get("species_norm"))
    return float(x),kind,str(row.get("species_norm"))

def ci_map(raw,eligible,sampled):
    vals=defaultdict(list)
    for r in raw["Counts.csv"]:
        rid=(r.get("RunID") or "").strip()
        st=(r.get("StopNumber") or "").strip()
        sp=(r.get("Species") or "").strip()
        if rid not in eligible or st not in sampled.get(rid,set()) or not sp:
            continue
        try:
            x=int(float((r.get("CallingIndex") or "").strip()))
        except Exception:
            continue
        if x in (1,2,3):
            vals[(rid,st,sp)].append(x)
    by=defaultdict(dict)
    for (rid,st,sp),v in vals.items():
        by[(rid,st)][sp]=max(v)
    return by

def site_map(raw,eligible):
    vals=defaultdict(set)
    for s in raw["Stops.csv"]:
        rid=(s.get("RunID") or "").strip()
        st=(s.get("StopNumber") or "").strip()
        sid=(s.get("SiteID") or "").strip()
        if rid in eligible and st and sid and (s.get("SkippedStop") or "").strip()=="0":
            vals[(rid,st)].add(sid)
    bad={k:v for k,v in vals.items() if len(v)>1}
    if bad:
        raise RuntimeError(f"SiteID conflict: {list(bad)[:10]}")
    return {k:next(iter(v)) for k,v in vals.items()}

def stable_pair(p,sampled,site):
    w=str(p.wet_RunID); d=str(p.dry_RunID)
    ws=set(sampled[w]); ds=set(sampled[d])
    return len(ws)==10 and ws==ds and all(
        site.get((w,st)) is not None and site.get((w,st))==site.get((d,st))
        for st in ws
    )

def build_pair_species_matrix(pairs,sampled,ci):
    all_species=sorted({
        sp for p in pairs.itertuples(index=False)
        for rid in (str(p.wet_RunID),str(p.dry_RunID))
        for st in sampled[rid]
        for sp in ci.get((rid,st),{})
    })
    idx={sp:j for j,sp in enumerate(all_species)}
    Y=np.zeros((len(pairs),len(all_species)),float)
    focal_cells=np.zeros(len(all_species),int)
    focal_routes=[set() for _ in all_species]

    for i,p in enumerate(pairs.itertuples(index=False)):
        w=str(p.wet_RunID); d=str(p.dry_RunID)
        for st in sorted(sampled[w]):
            wm=ci.get((w,st),{})
            dm=ci.get((d,st),{})
            for sp in set(wm)|set(dm):
                wet=int(wm.get(sp,0)); dry=int(dm.get(sp,0))
                if dry==0 and wet>=2:
                    j=idx[sp]
                    Y[i,j]+=wet
                    focal_cells[j]+=1
                    focal_routes[j].add(str(p.route_cluster))
    return all_species,Y,focal_cells,np.asarray([len(x) for x in focal_routes],int)

def fit_species_betas(pairs,Y,species,eligible_mask):
    out={}
    for j,sp in enumerate(species):
        if not eligible_mask[j]:
            continue
        d=pairs.copy()
        d["response"]=Y[:,j]
        form="response ~ rain_contrast + temp_difference + doy_difference + year_gap + C(State) + C(RunNumber)"
        m=smf.ols(form,data=d).fit(cov_type="cluster",cov_kwds={"groups":d.route_cluster})
        out[sp]={
            "beta":float(m.params["rain_contrast"]),
            "se":float(m.bse["rain_contrast"]),
            "p":float(m.pvalues["rain_contrast"])
        }
    return out

def meta_outputs(species,betas,z):
    b=np.asarray([betas[sp]["beta"] for sp in species],float)
    se=np.asarray([betas[sp]["se"] for sp in species],float)
    X=sm.add_constant(z)
    ols=sm.OLS(b,X).fit(cov_type="HC3")
    w=1/np.maximum(se**2,1e-8)
    wls=sm.WLS(b,X,weights=w).fit(cov_type="HC3")
    rho,rhop=spearmanr(b,z)
    return {
        "ols_slope":float(ols.params[1]),
        "ols_se_hc3":float(ols.bse[1]),
        "ols_ci95":[float(ols.params[1]-Q*ols.bse[1]),float(ols.params[1]+Q*ols.bse[1])],
        "wls_inverse_variance_slope":float(wls.params[1]),
        "wls_se_hc3":float(wls.bse[1]),
        "wls_ci95":[float(wls.params[1]-Q*wls.bse[1]),float(wls.params[1]+Q*wls.bse[1])],
        "spearman_rho":float(rho),
        "spearman_p":float(rhop),
    }

def permutation_test(beta_vec,z):
    obs=float(beta_vec@z)
    rng=np.random.default_rng(SEED)
    null=np.empty(N_PERM,float)
    for i in range(N_PERM):
        null[i]=float(beta_vec@rng.permutation(z))
    p=float((1+np.sum(null<=obs))/(N_PERM+1))
    lo,hi=np.quantile(null,[.025,.975])
    return {
        "observed_size_load_beta":obs,
        "null_mean":float(null.mean()),
        "null_ci95":[float(lo),float(hi)],
        "one_sided_negative_permutation_p":p,
        "negative_prediction_pass":bool(obs<0 and p<0.05),
        "permutations":N_PERM,
        "seed":SEED,
    }

def main():
    raw=load_raw_retry()
    runs,sets=base.build_runs(raw)
    eligible_runs=set(runs.RunID.astype(str))
    sampled,_=spatial.stop_matrix(raw,eligible_runs)
    ci=ci_map(raw,eligible_runs,sampled)
    site=site_map(raw,eligible_runs)

    pairs=base.pair_runs(runs,sets).copy().reset_index(drop=True)
    species,Y,focal_cells,focal_routes=build_pair_species_matrix(pairs,sampled,ci)
    response_ok=(focal_cells>=20)&(focal_routes>=5)

    traits,tidx,trait_sha=load_body_size()
    body={}
    tax_audit={}
    for sp in species:
        x,kind,matched=match_body(sp,traits,tidx)
        tax_audit[sp]={"match_type":kind,"matched_species":matched,"body_size_mm":x}
        if x is not None:
            body[sp]=x

    use_idx=[
        j for j,sp in enumerate(species)
        if response_ok[j] and sp in body
    ]
    use_species=[species[j] for j in use_idx]
    gate=bool(len(use_species)>=20)
    sizes=np.asarray([body[sp] for sp in use_species],float)
    logsize=np.log(sizes) if len(sizes) else np.asarray([])
    if len(logsize) and np.std(logsize,ddof=0)<=0:
        gate=False

    out={
        "analysis":"naamp_hydration_body_size_strong_activation_v0_1",
        "contract":"exploration/NAAMP_HYDRATION_BODY_SIZE_STRONG_ACTIVATION_CONTRACT_V0_1.json",
        "trait_source":{"amphibio_blob_sha1":trait_sha},
        "coverage":{
            "all_species":int(len(species)),
            "response_eligible_species":int(response_ok.sum()),
            "body_size_matched_response_eligible_species":int(len(use_species)),
            "coverage_gate":gate,
        },
        "response_endpoints_read":False,
        "taxonomy_audit":tax_audit,
    }
    if not gate:
        OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
        print(json.dumps({k:v for k,v in out.items() if k!="taxonomy_audit"},indent=2,sort_keys=True))
        return

    z=(logsize-logsize.mean())/logsize.std(ddof=0)
    eligible_mask=np.zeros(len(species),bool)
    eligible_mask[use_idx]=True
    beta_full=fit_species_betas(pairs,Y,species,eligible_mask)
    beta_vec=np.asarray([beta_full[sp]["beta"] for sp in use_species],float)
    primary=permutation_test(beta_vec,z)
    meta=meta_outputs(use_species,beta_full,z)

    _,same=sameobs.same_observer_pairs(raw,runs,sets)
    stable=np.asarray([stable_pair(p,sampled,site) for p in same.itertuples(index=False)],bool)
    robust_pairs=same.loc[stable].copy().reset_index(drop=True)
    # map full-pair response rows to robust pair keys without redefining species eligibility
    key_to_row={
        (str(p.wet_RunID),str(p.dry_RunID)):i
        for i,p in enumerate(pairs.itertuples(index=False))
    }
    ridx=[key_to_row[(str(p.wet_RunID),str(p.dry_RunID))] for p in robust_pairs.itertuples(index=False)]
    Yrob=Y[np.asarray(ridx,int),:]
    beta_rob=fit_species_betas(robust_pairs,Yrob,species,eligible_mask)
    rob_vec=np.asarray([beta_rob[sp]["beta"] for sp in use_species],float)
    robust_perm=permutation_test(rob_vec,z)
    robust_meta=meta_outputs(use_species,beta_rob,z)

    trait_table=[
        {
            "species":sp,
            "body_size_mm":float(body[sp]),
            "z_log_body_size":float(z[i]),
            "strong_activation_beta_full":float(beta_full[sp]["beta"]),
            "strong_activation_se_full":float(beta_full[sp]["se"]),
            "strong_activation_beta_robust":float(beta_rob[sp]["beta"]),
            "focal_cells_full":int(focal_cells[species.index(sp)]),
            "focal_routes_full":int(focal_routes[species.index(sp)]),
        }
        for i,sp in enumerate(use_species)
    ]

    out.update({
        "response_endpoints_read":True,
        "primary_full_sample":primary,
        "species_meta_regression_full":meta,
        "robust_same_observer_physical_stop":{
            "n_pairs":int(len(robust_pairs)),
            "n_routes":int(robust_pairs.route_cluster.nunique()),
            "permutation":robust_perm,
            "meta_regression":robust_meta,
            "sign_concordant_with_primary":bool(
                np.sign(robust_perm["observed_size_load_beta"])==
                np.sign(primary["observed_size_load_beta"])
            )
        },
        "classification":{
            "body_size_hydration_prediction_supported":bool(primary["negative_prediction_pass"]),
            "robust_sign_concordant":bool(
                np.sign(robust_perm["observed_size_load_beta"])==
                np.sign(primary["observed_size_load_beta"])
            )
        },
        "trait_response_table":trait_table,
        "interpretation_boundary":{
            "hydration_mediation_identified":False,
            "body_size_is_multifunctional_trait":True,
            "phylogenetic_nonindependence_fully_resolved":False,
            "causal_rainfall_claim":False
        }
    })
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps({k:v for k,v in out.items() if k not in ("taxonomy_audit","trait_response_table")},indent=2,sort_keys=True))

if __name__=="__main__":
    main()
