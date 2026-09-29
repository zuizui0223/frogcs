#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import importlib.util
import json
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT=Path(__file__).resolve().parents[1]
NAAMP=ROOT/"scripts"/"naamp"
OUT=ROOT/"exploration"/"NAAMP_STRONG_NEW_ACTIVATION_TAXONOMIC_DISTRIBUTION_RECEIPT_V0_1.json"


def loadmod(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    mod=importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(mod)
    return mod


base=loadmod("pulse_base",NAAMP/"run_naamp_ecological_pulse.py")
spatial=loadmod("spatial_base",NAAMP/"run_naamp_spatial_taxonomic_activation_decomposition.py")
uniform=loadmod("uniform_base",NAAMP/"run_naamp_uniform_activation_null.py")


def fold(route_cluster):
    return "A" if hashlib.sha256(str(route_cluster).encode()).digest()[0] < 128 else "B"


def build_ci(raw,eligible,sampled):
    vals=defaultdict(list)
    for r in raw["Counts.csv"]:
        rid=(r.get("RunID") or "").strip()
        st=(r.get("StopNumber") or "").strip()
        sp=(r.get("Species") or "").strip()
        if rid not in eligible or st not in sampled.get(rid,set()) or not sp:
            continue
        try: ci=int(float((r.get("CallingIndex") or "").strip()))
        except Exception: continue
        if ci in (1,2,3):
            vals[(rid,st,sp)].append(ci)
    by=defaultdict(dict)
    for (rid,st,sp),v in vals.items():
        by[(rid,st)][sp]=max(v)
    return by


def response_matrix(pairs,sampled,ci,species):
    idx={sp:j for j,sp in enumerate(species)}
    Y=np.zeros((len(pairs),len(species)),float)
    for i,p in enumerate(pairs.itertuples(index=False)):
        wet=str(p.wet_RunID); dry=str(p.dry_RunID)
        stops=sorted(sampled[wet])
        if len(stops)!=10 or set(stops)!=set(sampled[dry]):
            raise RuntimeError("stop alignment failed")
        for st in stops:
            wm=ci.get((wet,st),{}); dm=ci.get((dry,st),{})
            for sp,w in wm.items():
                d=int(dm.get(sp,0)); w=int(w)
                if d==0 and w>=2:
                    Y[i,idx[sp]]+=float(w)
    return Y


def coefficients(pairs,Y):
    r,den=uniform.design_residual(pairs.reset_index(drop=True))
    return (r[:,None]*Y).sum(axis=0)/den


def concentration(species,betas):
    b=np.asarray(betas,float)
    pos=np.flatnonzero(b>0)
    neg=np.flatnonzero(b<0)
    zer=np.flatnonzero(np.abs(b)<=1e-15)
    order=pos[np.argsort(b[pos])[::-1]]
    pvals=b[order]
    psum=float(pvals.sum())
    nsum=float(b[neg].sum()) if len(neg) else 0.0
    net=float(b.sum())
    if psum>0:
        shares=pvals/psum
        cs=np.cumsum(shares)
        n50=int(np.searchsorted(cs,.5)+1)
        n80=int(np.searchsorted(cs,.8)+1)
        eff=float(1.0/np.sum(shares**2))
        top1=float(shares[0]) if len(shares) else None
        top5=float(shares[:5].sum()) if len(shares) else None
    else:
        shares=np.asarray([],float); n50=n80=0; eff=top1=top5=None
    top=[]
    for rank,j in enumerate(order[:15],start=1):
        top.append({
            "rank":rank,
            "species":species[int(j)],
            "beta":float(b[int(j)]),
            "share_of_positive_contribution":float(b[int(j)]/psum) if psum>0 else None,
            "share_of_net_total":float(b[int(j)]/net) if abs(net)>1e-12 else None,
        })
    return {
        "species_total":len(species),
        "positive_species":int(len(pos)),
        "negative_species":int(len(neg)),
        "zero_species":int(len(zer)),
        "positive_contribution_sum":psum,
        "negative_contribution_sum":nsum,
        "net_beta_sum":net,
        "top1_share_positive":top1,
        "top5_share_positive":top5,
        "n_species_for_50pct_positive":n50,
        "n_species_for_80pct_positive":n80,
        "effective_number_positive":eff,
        "top_contributors":top,
    }


def main():
    raw=base.load()
    runs,sets=base.build_runs(raw)
    eligible=set(runs["RunID"].astype(str))
    sampled,_=spatial.stop_matrix(raw,eligible)
    pairs=base.pair_runs(runs,sets).copy().reset_index(drop=True)
    ci=build_ci(raw,eligible,sampled)
    species=sorted({sp for m in ci.values() for sp in m})
    Y=response_matrix(pairs,sampled,ci,species)
    b=coefficients(pairs,Y)

    total=Y.sum(axis=1)
    r,den=uniform.design_residual(pairs)
    total_beta=float((r*total).sum()/den)
    identity_error=float(total_beta-b.sum())
    if abs(identity_error)>1e-10:
        raise RuntimeError(f"species coefficient identity failed {identity_error}")

    fold_reports={}
    fold_betas={}
    pair_folds=np.asarray([fold(x) for x in pairs["route_cluster"].astype(str)])
    for f in ("A","B"):
        mask=pair_folds==f
        psub=pairs.loc[mask].copy().reset_index(drop=True)
        ysub=Y[mask]
        bf=coefficients(psub,ysub)
        fold_betas[f]=bf
        fold_reports[f]={
            "n_pairs":int(len(psub)),
            "n_routes":int(psub["route_cluster"].nunique()),
            "concentration":concentration(species,bf),
        }

    informative=(np.abs(fold_betas["A"])+np.abs(fold_betas["B"]))>1e-12
    if informative.sum()>=3 and np.std(fold_betas["A"][informative])>0 and np.std(fold_betas["B"][informative])>0:
        corr=float(np.corrcoef(fold_betas["A"][informative],fold_betas["B"][informative])[0,1])
    else:
        corr=None

    output={
        "analysis":"naamp_strong_new_activation_taxonomic_distribution_v0_1",
        "contract":"exploration/NAAMP_STRONG_NEW_ACTIVATION_TAXONOMIC_DISTRIBUTION_CONTRACT_V0_1.json",
        "n_pairs":int(len(pairs)),
        "n_routes":int(pairs["route_cluster"].nunique()),
        "total_strong_new_score_beta":total_beta,
        "species_beta_identity_error":identity_error,
        "full_sample":concentration(species,b),
        "route_folds":fold_reports,
        "crossfold_species_contribution":{
            "n_informative_species":int(informative.sum()),
            "pearson_beta_correlation":corr,
        },
        "interpretation_boundary":{
            "descriptive_contribution_audit":True,
            "species_rank_is_rainfall_trait":False,
            "causal_mechanism_identified":False,
            "cross_continental_universality":False
        }
    }
    OUT.write_text(json.dumps(output,indent=2,sort_keys=True)+"\n")
    print(json.dumps(output,indent=2,sort_keys=True))


if __name__=="__main__":
    main()
