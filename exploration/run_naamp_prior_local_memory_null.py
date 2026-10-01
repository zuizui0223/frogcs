#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import importlib.util
import json
import time
import urllib.error
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT=Path(__file__).resolve().parents[1]
NAAMP=ROOT/"scripts"/"naamp"
OUT=ROOT/"exploration"/"NAAMP_PRIOR_LOCAL_MEMORY_NULL_RECEIPT_V0_1.json"

B=1000
SEED=2840223
KAPPA=2.0
ANCHOR=0.75


def loadmod(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    mod=importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(mod)
    return mod


base=loadmod("base",NAAMP/"run_naamp_ecological_pulse.py")
uniform=loadmod("uniform",NAAMP/"run_naamp_uniform_activation_null.py")


def load_retry():
    last=None
    for i in range(6):
        try:
            return base.load()
        except urllib.error.HTTPError as e:
            last=e
            if e.code not in (403,429,500,502,503,504):
                raise
            time.sleep(2*(i+1))
    raise RuntimeError(f"NAAMP source failed after retries: {last}")


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
        raise RuntimeError(f"multiple SiteIDs: {list(bad)[:10]}")
    return {k:next(iter(v)) for k,v in vals.items()}


def build_history_index(runs,sampled,ss,site):
    meta={}
    by_stratum=defaultdict(list)
    run_sites=defaultdict(set)
    run_site_species=defaultdict(set)

    for r in runs.itertuples(index=False):
        rid=str(r.RunID)
        key=(str(r.State),str(r.RouteNumber),str(r.RunNumber))
        meta[rid]={"key":key,"year":int(r.SurveyYear)}
        by_stratum[key].append(rid)

        for st in sampled.get(rid,set()):
            sid=site.get((rid,st))
            if sid is None:
                continue
            run_sites[rid].add(sid)
            run_site_species[(rid,sid)].update(ss.get((rid,st),set()))

    for key in by_stratum:
        by_stratum[key]=sorted(by_stratum[key],key=lambda rid:(meta[rid]["year"],rid))
    return meta,by_stratum,run_sites,run_site_species


def focal_siteids(p,dct,site):
    w=str(p.wet_RunID)
    d=str(p.dry_RunID)
    ids=[]
    for st in dct["stops"]:
        ws=site.get((w,st))
        ds=site.get((d,st))
        if ws is None or ds is None or ws!=ds:
            return None
        ids.append(ws)
    return ids


def eligible_prior_runs(p,dct,siteids,meta,by_stratum,run_sites):
    key=dct["key"]
    cutoff=int(p.year_earlier)
    out=[]
    wanted=set(siteids)
    for rid in by_stratum[key]:
        if meta[rid]["year"]>=cutoff:
            continue
        overlap=len(wanted & run_sites.get(rid,set()))
        if overlap>=8:
            out.append(rid)
    return out


def prior_probs(dct,siteids,prior_runs,run_sites,run_site_species):
    species=dct["species"]
    ns=len(species)
    idx={sp:i for i,sp in enumerate(species)}
    y=np.zeros((ns,10),float)
    exposure=np.zeros(10,float)

    for rid in prior_runs:
        sites=run_sites.get(rid,set())
        for t,sid in enumerate(siteids):
            if sid not in sites:
                continue
            exposure[t]+=1.0
            for sp in run_site_species.get((rid,sid),set()):
                j=idx.get(sp)
                if j is not None:
                    y[j,t]+=1.0

    total_site_exposure=float(exposure.sum())
    if total_site_exposure<=0:
        raise RuntimeError("eligible prior history has zero focal-site exposure")

    total_slots=max(1.0,total_site_exposure*max(ns,1))
    mu0=(float(y.sum())+0.5)/(total_slots+1.0)
    ys=y.sum(axis=1)
    mus=(ys+KAPPA*mu0)/(total_site_exposure+KAPPA)
    p=(y+KAPPA*mus[:,None])/(exposure[None,:]+KAPPA)
    p=np.clip(p,1e-8,1-1e-8)
    return p,{
        "prior_runs":int(len(prior_runs)),
        "site_exposure_min":float(exposure.min()),
        "site_exposure_median":float(np.median(exposure)),
        "site_exposure_max":float(exposure.max()),
        "mean_prior_cell_probability":float(p.mean()) if p.size else 0.0,
    }


def permutation_for_pair(p,tag):
    key=f"{p.State}|{p.RouteNumber}|{p.RunNumber}|{int(p.year_earlier)}|{tag}"
    seed=int.from_bytes(hashlib.sha256(key.encode()).digest()[:8],"big",signed=False)
    rng=np.random.default_rng(seed)
    return rng.permutation(10)


def summarize_sim(betas,obs_betas):
    names=["corner_expansion","spatial_spread","taxonomic_deepening","within_core_rearrangement"]
    mean=betas.mean(axis=0)
    cov=np.cov(betas,rowvar=False,ddof=1)
    inv=np.linalg.pinv(cov)
    centered=betas-mean[None,:]
    dnull=np.einsum("bi,ij,bj->b",centered,inv,centered)
    dv=obs_betas-mean
    dobs=float(dv@inv@dv)
    p=float((1+np.sum(dnull>=dobs))/(len(betas)+1))

    total=betas.sum(axis=1)
    valid=np.isfinite(total)&(np.abs(total)>1e-12)
    shares=betas[valid]/total[valid,None]
    obs_shares=obs_betas/float(obs_betas.sum())
    boundary=1-shares[:,3]
    obs_boundary=float(1-obs_shares[3])
    tax_minus_spatial=shares[:,2]-shares[:,1]
    obs_tax_minus_spatial=float(obs_shares[2]-obs_shares[1])

    def stat(v,o):
        lo,hi=np.quantile(v,[.025,.975])
        return {
            "null_mean":float(np.mean(v)),
            "null_ci95":[float(lo),float(hi)],
            "observed":float(o),
            "observed_percentile":float((1+np.sum(v<=o))/(len(v)+1)),
        }

    return {
        "primary_omnibus":{
            "observed_mahalanobis":dobs,
            "monte_carlo_p":p,
            "reject":bool(p<.05),
        },
        "observed_component_betas":{names[j]:float(obs_betas[j]) for j in range(4)},
        "null_component_beta_mean":{names[j]:float(mean[j]) for j in range(4)},
        "component_shares":{names[j]:stat(shares[:,j],obs_shares[j]) for j in range(4)},
        "boundary_crossing_share":stat(boundary,obs_boundary),
        "taxonomic_minus_spatial_share":stat(tax_minus_spatial,obs_tax_minus_spatial),
        "valid_share_replicates":int(valid.sum()),
    }


def simulate_variant(psub,dsub,hist_probs,r,den,obs_betas,variant,seed):
    rng=np.random.default_rng(seed)
    numer=np.zeros((B,4),float)

    for i,(p,dct,p_hist) in enumerate(zip(psub.itertuples(index=False),dsub,hist_probs)):
        if variant=="true":
            ph=p_hist
        elif variant in ("perm1","perm2"):
            perm=permutation_for_pair(p,variant)
            ph=p_hist[:,perm]
        else:
            raise ValueError(variant)

        dry=dct["dry"].astype(float)
        p_anchor=(1-ANCHOR)*ph+ANCHOR*dry
        p_anchor=np.clip(p_anchor,1e-8,1-1e-8)
        q=uniform.solve_shift(p_anchor,dct["wet_k"])
        wsim=rng.random((B,)+q.shape)<q[None,:,:]
        comps=uniform.simulated_components(wsim,dct["dry"])
        numer += r[i]*comps

    betas=numer/den
    return summarize_sim(betas,obs_betas)


def main():
    raw=load_retry()
    runs,sets=base.build_runs(raw)
    eligible=set(runs.RunID.astype(str))

    # Reuse the already fetched, pinned source tables inside uniform.prepare()
    # to avoid a second network fetch and guarantee byte-identical input.
    uniform.base.load=lambda: raw

    (
        pairs,pair_data,pools,dry_ids,sampled,ss,r0,den0,obs0,
        beta_mask,r_beta,den_beta,obs_sor
    )=uniform.prepare()
    pairs=pairs.copy().reset_index(drop=True)

    site=site_map(raw,eligible)
    meta,by_stratum,run_sites,run_site_species=build_history_index(
        runs,sampled,ss,site
    )

    keep=[]
    histories=[]
    history_audit=[]
    for p,dct in zip(pairs.itertuples(index=False),pair_data):
        ids=focal_siteids(p,dct,site)
        if ids is None:
            keep.append(False)
            histories.append(None)
            history_audit.append(None)
            continue

        prior=eligible_prior_runs(
            p,dct,ids,meta,by_stratum,run_sites
        )
        if not prior:
            keep.append(False)
            histories.append(None)
            history_audit.append(None)
            continue

        ph,audit=prior_probs(
            dct,ids,prior,run_sites,run_site_species
        )
        keep.append(True)
        histories.append(ph)
        history_audit.append(audit)

    keep=np.asarray(keep,bool)
    idx=np.flatnonzero(keep)
    psub=pairs.iloc[idx].copy().reset_index(drop=True)
    dsub=[pair_data[int(i)] for i in idx]
    hsub=[histories[int(i)] for i in idx]
    asub=[history_audit[int(i)] for i in idx]

    gate=bool(len(psub)>=1500 and psub.route_cluster.nunique()>=300)
    output={
        "analysis":"naamp_prior_local_memory_activation_null_v0_1",
        "contract":"exploration/NAAMP_PRIOR_LOCAL_MEMORY_NULL_CONTRACT_V0_1.json",
        "coverage":{
            "all_pairs":int(len(pairs)),
            "eligible_pairs":int(len(psub)),
            "eligible_routes":int(psub.route_cluster.nunique()),
            "eligible_states":int(psub.State.nunique()),
            "gate_pass":gate,
        },
        "response_endpoints_read":False,
    }
    if not gate:
        OUT.write_text(json.dumps(output,indent=2,sort_keys=True)+"\n")
        print(json.dumps(output,indent=2,sort_keys=True))
        return

    obs_rows=np.asarray([
        uniform.component_counts(d["wet"],d["dry"])
        for d in dsub
    ],float)
    r,den=uniform.design_residual(psub)
    obs_betas=(r[:,None]*obs_rows).sum(axis=0)/den

    true_result=simulate_variant(
        psub,dsub,hsub,r,den,obs_betas,"true",SEED+81000
    )
    perm1=simulate_variant(
        psub,dsub,hsub,r,den,obs_betas,"perm1",SEED+82001
    )
    perm2=simulate_variant(
        psub,dsub,hsub,r,den,obs_betas,"perm2",SEED+82002
    )

    ptrue=true_result["primary_omnibus"]["monte_carlo_p"]
    p1=perm1["primary_omnibus"]["monte_carlo_p"]
    p2=perm2["primary_omnibus"]["monte_carlo_p"]

    if ptrue<.05:
        classification="prior_local_memory_insufficient"
    elif p1<.05 and p2<.05:
        classification="physical_site_identity_specific_memory_sufficient"
    else:
        classification="generic_prior_history_heterogeneity_sufficient"

    prior_counts=np.asarray([x["prior_runs"] for x in asub],float)
    exp_min=np.asarray([x["site_exposure_min"] for x in asub],float)

    output.update({
        "response_endpoints_read":True,
        "history_audit":{
            "median_prior_runs":float(np.median(prior_counts)),
            "q25_prior_runs":float(np.quantile(prior_counts,.25)),
            "q75_prior_runs":float(np.quantile(prior_counts,.75)),
            "median_min_site_exposure":float(np.median(exp_min)),
        },
        "true_prior_local_memory":true_result,
        "identity_permuted_controls":{
            "perm1":perm1,
            "perm2":perm2,
        },
        "classification":classification,
        "interpretation_boundary":{
            "failure_to_reject_is_sufficiency_not_proof":True,
            "probability_weights_use_strictly_prior_history":True,
            "stratum_species_pool_used_as_support_only":True,
            "continuous_occupancy_proven":False,
            "causal_rainfall_claim":False,
            "submission_story_change_authorized":False,
        }
    })

    OUT.write_text(json.dumps(output,indent=2,sort_keys=True)+"\n")
    print(json.dumps(output,indent=2,sort_keys=True))


if __name__=="__main__":
    main()
