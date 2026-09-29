#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
NAAMP=ROOT/"scripts"/"naamp"
EXP=ROOT/"exploration"
OUT=EXP/"NAAMP_CROSSFIT_SITE_AND_ADDITIVE_NULL_RECEIPT_V0_1.json"
B=1000
SEED=2840223
KAPPA=2.0
EARLY=range(2001,2008)
LATE=range(2009,2016)
MIN_RUNS=8
MIN_POS=10
MIN_NEG=10
MAX_ABS_BETA=5.0


def loadmod(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    mod=importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(mod)
    return mod


base=loadmod("pulse_base",NAAMP/"run_naamp_ecological_pulse.py")
spatial=loadmod("spatial_base",NAAMP/"run_naamp_spatial_taxonomic_activation_decomposition.py")
uniform=loadmod("uniform_base",NAAMP/"run_naamp_uniform_activation_null.py")
species_mod=loadmod("species_null",EXP/"run_naamp_crossfit_species_shift_null.py")


def block(year):
    y=int(year)
    if y in EARLY: return "early"
    if y in LATE: return "late"
    return None


def logit_scalar(p):
    p=min(max(float(p),1e-12),1-1e-12)
    return float(np.log(p)-np.log1p(-p))


def residual_slope(x,y,cov):
    x=np.asarray(x,float); y=np.asarray(y,float); z=np.asarray(cov,float)
    bx=np.linalg.lstsq(z,x,rcond=None)[0]
    by=np.linalg.lstsq(z,y,rcond=None)[0]
    rx=x-z@bx
    ry=y-z@by
    den=float(rx@rx)
    if not np.isfinite(den) or den<=1e-10:
        return None
    b=float((rx@ry)/den)
    return b if np.isfinite(b) else None


def fit_site_shifts(runs,sampled,ss,training_block):
    tr=runs[runs["SurveyYear"].map(block)==training_block].copy()
    theta=2*np.pi*tr["doy"].astype(float)/365.25
    tr["sin_doy"]=np.sin(theta)
    tr["cos_doy"]=np.cos(theta)
    tr["dry_x"]=np.log1p(tr["DaysSinceRain"].astype(float))

    route_pools=defaultdict(set)
    ids=set(tr["RunID"].astype(str))
    for (rid,st),spp in ss.items():
        if rid in ids:
            rr=tr.loc[tr["RunID"].astype(str)==rid]
            if rr.empty: continue
            route=str(rr.iloc[0]["route_cluster"])
            route_pools[route].update(spp)

    by_route=defaultdict(list)
    for r in tr.itertuples(index=False):
        by_route[str(r.route_cluster)].append(r)

    shifts={}
    audit={}
    for route,rr in by_route.items():
        pool=sorted(route_pools.get(route,set()))
        n_pool=len(pool)
        for stop in sorted({st for r in rr for st in sampled.get(str(r.RunID),set())}):
            key=f"{route}:{stop}"
            rows=[]
            for r in rr:
                rid=str(r.RunID)
                if stop not in sampled.get(rid,set()):
                    continue
                y=sum(sp in ss.get((rid,stop),set()) for sp in pool)
                rows.append((r,y))
            n_runs=len(rows)
            pos=int(sum(y for _,y in rows))
            neg=int(n_runs*n_pool-pos)
            info={
                "n_runs":n_runs,"training_pool_species":n_pool,
                "positive_cells":pos,"negative_cells":neg,
                "estimable":False,"dryness_beta":0.0,"wet_shift_gamma":0.0,
            }
            if n_runs<MIN_RUNS or n_pool<3 or pos<MIN_POS or neg<MIN_NEG:
                shifts[key]=0.0; audit[key]=info; continue

            x=[]; yv=[]; runnums=[]
            for r,y in rows:
                x.append(float(np.log1p(r.DaysSinceRain)))
                p=(y+0.5)/(n_pool+1.0)
                yv.append(logit_scalar(p))
                runnums.append(str(r.RunNumber))

            levels=sorted(set(runnums))
            cov=[]
            for (r,_),rn in zip(rows,runnums):
                row=[
                    1.0,
                    float(r.mean_temp_c),
                    float(np.sin(2*np.pi*float(r.doy)/365.25)),
                    float(np.cos(2*np.pi*float(r.doy)/365.25)),
                ]
                row.extend([1.0 if rn==lev else 0.0 for lev in levels[1:]])
                cov.append(row)
            beta=residual_slope(x,yv,cov)
            if beta is None or abs(beta)>MAX_ABS_BETA:
                shifts[key]=0.0
                info["unstable_or_unidentified"]=True
                audit[key]=info
                continue
            gamma=-float(beta)
            shifts[key]=gamma
            info.update({"estimable":True,"dryness_beta":float(beta),"wet_shift_gamma":gamma})
            audit[key]=info

    return shifts,audit,{
        "training_block":training_block,
        "n_runs":int(len(tr)),
        "n_routes":int(tr["route_cluster"].nunique()),
        "n_sites_total":int(len(audit)),
        "n_sites_estimable":int(sum(v["estimable"] for v in audit.values())),
    }


def subset_pairs_and_data(pairs,pair_data):
    keep=[]
    test_block=[]
    for i,p in pairs.iterrows():
        b1=block(p["year_earlier"]); b2=block(p["year_later"])
        if b1 is not None and b1==b2:
            keep.append(i); test_block.append(b1)
    psub=pairs.iloc[keep].copy().reset_index(drop=True)
    dsub=[pair_data[int(i)] for i in keep]
    psub["test_block"]=test_block
    for d,b in zip(dsub,test_block):
        d["test_block"]=b
    return psub,dsub


def observed_betas(psub,dsub):
    comps=np.asarray([uniform.component_counts(d["wet"],d["dry"]) for d in dsub],float)
    r,den=uniform.design_residual(psub)
    betas=(r[:,None]*comps).sum(axis=0)/den
    return r,den,betas


def simulate(psub,dsub,probs,site_shifts,species_shifts_by_train_fold,r,den,obs_betas,mode,seed):
    rng=np.random.default_rng(seed)
    numer=np.zeros((B,4),float)
    nonzero_sites=[]
    nonzero_species=[]

    for i,d in enumerate(dsub):
        route=str(psub.iloc[i]["route_cluster"])
        test_block=str(psub.iloc[i]["test_block"])
        train_block="late" if test_block=="early" else "early"
        sshift=site_shifts[train_block]
        site_gamma=np.asarray([float(sshift.get(f"{route}:{st}",0.0)) for st in d["stops"]],float)

        eta=uniform.logit(probs[d["key"]]).copy()
        rain=float(psub.iloc[i]["rain_contrast"])
        if mode in ("site","additive"):
            eta += site_gamma[None,:]*rain
        if mode=="additive":
            test_route_fold=species_mod.fold_for_route(route)
            train_route_fold="B" if test_route_fold=="A" else "A"
            spmap=species_shifts_by_train_fold[train_route_fold]
            species_gamma=np.asarray([float(spmap.get(sp,0.0)) for sp in d["species"]],float)
            eta += species_gamma[:,None]*rain
            nonzero_species.append(int(np.sum(np.abs(species_gamma)>0)))
        nonzero_sites.append(int(np.sum(np.abs(site_gamma)>0)))

        pre=uniform.expit(eta)
        q=uniform.solve_shift(pre,d["wet_k"])
        wsim=rng.random((B,)+q.shape)<q[None,:,:]
        numer += r[i]*uniform.simulated_components(wsim,d["dry"])

    betas=numer/den
    mean=betas.mean(axis=0)
    cov=np.cov(betas,rowvar=False,ddof=1)
    inv=np.linalg.pinv(cov)
    cen=betas-mean[None,:]
    dnull=np.einsum("bi,ij,bj->b",cen,inv,cen)
    dv=obs_betas-mean
    dobs=float(dv@inv@dv)
    p=float((1+np.sum(dnull>=dobs))/(B+1))

    total=betas.sum(axis=1)
    valid=np.isfinite(total)&(np.abs(total)>1e-12)
    shares=betas[valid]/total[valid,None]
    obs_shares=obs_betas/float(obs_betas.sum())
    boundary=1-shares[:,3]
    obs_boundary=float(1-obs_shares[3])

    def stat(v,obs):
        lo,hi=np.quantile(v,[.025,.975])
        return {"null_mean":float(np.mean(v)),"null_ci95":[float(lo),float(hi)],"observed":float(obs)}

    names=["corner_expansion","spatial_spread","taxonomic_deepening","within_core_rearrangement"]
    return {
        "mode":mode,
        "primary_omnibus":{"monte_carlo_p":p,"reject":bool(p<.05),"observed_mahalanobis":dobs},
        "observed_component_betas":{names[j]:float(obs_betas[j]) for j in range(4)},
        "null_component_beta_mean":{names[j]:float(mean[j]) for j in range(4)},
        "boundary_crossing_share":stat(boundary,obs_boundary),
        "mean_nonzero_site_shifts_per_pair":float(np.mean(nonzero_sites)) if nonzero_sites else 0.0,
        "mean_nonzero_species_shifts_per_pair":float(np.mean(nonzero_species)) if nonzero_species else None,
    }


def main():
    raw=base.load()
    runs,route_sets=base.build_runs(raw)
    eligible=set(runs["RunID"].astype(str))
    sampled,ss=spatial.stop_matrix(raw,eligible)

    (
        pairs,pair_data,pools,dry_ids,sampled0,ss0,r0,den0,obs0,
        beta_mask,r_beta,den_beta,obs_sor
    )=uniform.prepare()
    pairs=pairs.copy().reset_index(drop=True)
    psub,dsub=subset_pairs_and_data(pairs,pair_data)
    r,den,obs_betas=observed_betas(psub,dsub)

    site_early,audit_early,rep_early=fit_site_shifts(runs,sampled,ss,"early")
    site_late,audit_late,rep_late=fit_site_shifts(runs,sampled,ss,"late")
    site_shifts={"early":site_early,"late":site_late}

    all_species=sorted({sp for species in pools.values() for sp in species})
    slopes_A,audit_A,fold_A=species_mod.fit_species_slopes(runs,sampled,ss,all_species,"A")
    slopes_B,audit_B,fold_B=species_mod.fit_species_slopes(runs,sampled,ss,all_species,"B")
    species_shifts={"A":slopes_A,"B":slopes_B}

    stops_by_key={d["key"]:d["stops"] for d in pair_data}
    probs=uniform.baseline_probs(KAPPA,pools,dry_ids,stops_by_key,ss0)

    site_result=simulate(psub,dsub,probs,site_shifts,species_shifts,r,den,obs_betas,"site",SEED+31000)
    add_result=simulate(psub,dsub,probs,site_shifts,species_shifts,r,den,obs_betas,"additive",SEED+32000)

    coverage={
        "n_test_pairs":int(len(psub)),
        "n_test_routes":int(psub["route_cluster"].nunique()),
        "early_test_pairs":int((psub["test_block"]=="early").sum()),
        "late_test_pairs":int((psub["test_block"]=="late").sum()),
        "excluded_pairs":int(len(pairs)-len(psub)),
    }

    output={
        "analysis":"naamp_crossfit_site_and_additive_null_v0_1",
        "contracts":[
            "exploration/MECHANISM_UNIVERSALITY_CONTRACT_V0_1.json#crossfit_site_shift_null",
            "exploration/MECHANISM_UNIVERSALITY_CONTRACT_V0_1.json#crossfit_species_plus_site_additive_null"
        ],
        "coverage":coverage,
        "site_training":{"early":rep_early,"late":rep_late},
        "species_training":{"A":fold_A,"B":fold_B},
        "site_shift_null":site_result,
        "species_plus_site_additive_null":add_result,
        "decision":{
            "stable_site_shift_insufficient":bool(site_result["primary_omnibus"]["reject"]),
            "additive_species_plus_site_insufficient":bool(add_result["primary_omnibus"]["reject"]),
            "nonadditive_context_required_by_hierarchy":bool(add_result["primary_omnibus"]["reject"]),
        },
        "interpretation_boundary":{
            "nonadditive_species_x_site_interaction_directly_estimated":False,
            "habitat_or_hydrology_measured":False,
            "causal_rainfall_claim":False,
            "submission_story_change_authorized":False,
        }
    }
    OUT.write_text(json.dumps(output,indent=2,sort_keys=True)+"\n")
    print(json.dumps(output,indent=2,sort_keys=True))


if __name__=="__main__":
    main()
