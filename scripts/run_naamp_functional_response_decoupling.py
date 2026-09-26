#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import io
import json
import math
import urllib.request
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf

ROOT=Path(__file__).resolve().parent

def loadmod(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    mod=importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(mod)
    return mod

base=loadmod("pulse_base",ROOT/"run_naamp_ecological_pulse.py")
func=loadmod("functional_base",ROOT/"run_naamp_functional_community_expansion.py")

N_PERM=100000
SEED_ALL=2842026
SEED_FAMILY=2842027

def species_universe():
    obj=json.loads(Path("NAAMP_RESPONSE_ELIGIBLE_SPECIES_UNIVERSE_V0_1.json").read_text())
    spp=[str(x) for x in obj["species"]]
    if len(spp)!=29 or len(set(spp))!=29:
        raise RuntimeError("species universe drift")
    return spp

def fit_response(sp,events):
    x=pd.DataFrame(events)
    if len(x)<40 or x["route_cluster"].nunique()<10:
        return None
    for c in ["rain_contrast","temp_difference","doy_difference","year_gap"]:
        x["c_"+c]=x[c]-x[c].mean()
    form="y ~ c_rain_contrast + c_temp_difference + c_doy_difference + c_year_gap"
    try:
        f=smf.glm(form,data=x,family=sm.families.Binomial()).fit(
            cov_type="cluster",cov_kwds={"groups":x["route_cluster"]}
        )
        b=float(f.params["Intercept"]);se=float(f.bse["Intercept"])
        if not np.isfinite(b) or not np.isfinite(se) or se<=0:return None
        return {"species":sp,"log_odds":b,"se":se,"n_events":int(len(x)),
                "n_routes":int(x["route_cluster"].nunique())}
    except Exception:
        return None

def adjusted_responses(runs,sets,pairs,species):
    family=set(species)
    events=defaultdict(list)
    for r in pairs.itertuples(index=False):
        W=sets[str(r.wet_RunID)];D=sets[str(r.dry_RunID)]
        for sp in (W^D)&family:
            events[sp].append({
              "y":int(sp in W),"route_cluster":str(r.route_cluster),
              "rain_contrast":float(r.rain_contrast),
              "temp_difference":float(r.temp_difference),
              "doy_difference":float(r.doy_difference),
              "year_gap":float(r.year_gap)
            })
    out={}
    audit=[]
    for sp in species:
        z=fit_response(sp,events.get(sp,[]))
        audit.append({"species":sp,"estimable":z is not None,
                      "n_events":0 if z is None else z["n_events"],
                      "n_routes":0 if z is None else z["n_routes"]})
        if z is not None:out[sp]=z["log_odds"]
    return out,audit

def family_map(species):
    b=func.getb(func.URL)
    if func.blobsha(b)!=func.BLOB:
        raise RuntimeError("AmphiBIO drift")
    try:t=pd.read_csv(io.BytesIO(b),encoding="utf-8")
    except UnicodeDecodeError:t=pd.read_csv(io.BytesIO(b),encoding="cp1252")
    t["sp"]=t["Species"].map(func.norm)
    idx={s:i for i,s in enumerate(t["sp"])}
    out={}
    for sp0 in species:
        sp=func.norm(sp0);cands=[sp];tok=sp.split()
        if len(tok)==2 and tok[0] in func.ALIASES:
            cands.append(func.ALIASES[tok[0]]+" "+tok[1])
        hits=[c for c in cands if c in idx]
        chosen=sp if sp in hits else (hits[0] if len(hits)==1 else None)
        out[sp0]="" if chosen is None else str(t.iloc[idx[chosen]].get("Family","") or "").strip()
    return out

def corr_fast(x,y):
    xx=x-x.mean();yy=y-y.mean()
    den=math.sqrt(float(xx@xx)*float(yy@yy))
    return float((xx@yy)/den) if den>0 else np.nan

def unrestricted_null(values,i_idx,j_idx,x_centered,x_den,rng,nperm,chunk=1000):
    n=len(values);obs=[]
    for start in range(0,nperm,chunk):
        m=min(chunk,nperm-start)
        P=np.empty((m,n),dtype=int)
        for r in range(m):
            P[r]=rng.permutation(n)
        vp=values[P]
        yd=np.abs(vp[:,i_idx]-vp[:,j_idx])
        yc=yd-yd.mean(axis=1,keepdims=True)
        den=np.sqrt(np.sum(yc*yc,axis=1))*x_den
        num=yc@x_centered
        obs.extend(np.divide(num,den,out=np.full(m,np.nan),where=den>0).tolist())
    return np.asarray(obs,float)

def family_null(values,families,i_idx,j_idx,x_centered,x_den,rng,nperm,chunk=1000):
    n=len(values)
    groups=[]
    for fam in sorted(set(families)):
        idx=np.where(np.asarray(families)==fam)[0]
        if len(idx)>=2:groups.append(idx)
    out=[]
    base_idx=np.arange(n)
    for start in range(0,nperm,chunk):
        m=min(chunk,nperm-start)
        P=np.tile(base_idx,(m,1))
        for g in groups:
            ranks=rng.random((m,len(g)))
            order=np.argsort(ranks,axis=1)
            P[:,g]=g[order]
        vp=values[P]
        yd=np.abs(vp[:,i_idx]-vp[:,j_idx])
        yc=yd-yd.mean(axis=1,keepdims=True)
        den=np.sqrt(np.sum(yc*yc,axis=1))*x_den
        num=yc@x_centered
        out.extend(np.divide(num,den,out=np.full(m,np.nan),where=den>0).tolist())
    return np.asarray(out,float)

def main():
    raw=base.load();runs,sets=base.build_runs(raw);pairs=base.pair_runs(runs,sets)
    fixed=species_universe()
    responses,audit=adjusted_responses(runs,sets,pairs,fixed)

    all_active=set().union(*sets.values())
    vec,_=func.load_trait_vectors(all_active)
    fam=family_map(fixed)

    species=sorted([sp for sp in fixed if sp in responses and func.norm(sp) in vec])
    if len(species)<20:
        raise SystemExit(f"functional-response intersection too small: {len(species)}")

    values=np.array([responses[sp] for sp in species],float)
    families=[fam.get(sp,"") for sp in species]
    i_idx=[];j_idx=[];fd=[];rd=[];opp=[];samefam=[]
    for i in range(len(species)):
        for j in range(i+1,len(species)):
            i_idx.append(i);j_idx.append(j)
            fd.append(func.dist(vec[func.norm(species[i])],vec[func.norm(species[j])]))
            rd.append(abs(values[i]-values[j]))
            opp.append(bool(np.sign(values[i])!=np.sign(values[j])))
            samefam.append(bool(families[i] and families[i]==families[j]))
    i_idx=np.asarray(i_idx,int);j_idx=np.asarray(j_idx,int)
    fd=np.asarray(fd,float);rd=np.asarray(rd,float);opp=np.asarray(opp,bool);samefam=np.asarray(samefam,bool)

    observed=corr_fast(fd,rd)
    xc=fd-fd.mean();xden=math.sqrt(float(xc@xc))

    null_all=unrestricted_null(values,i_idx,j_idx,xc,xden,np.random.default_rng(SEED_ALL),N_PERM)
    p_all=float((1+np.sum(np.abs(null_all)>=abs(observed)))/(N_PERM+1))

    null_fam=family_null(values,np.asarray(families),i_idx,j_idx,xc,xden,
                         np.random.default_rng(SEED_FAMILY),N_PERM)
    p_fam=float((1+np.sum(np.abs(null_fam)>=abs(observed)))/(N_PERM+1))

    q1=float(np.quantile(fd,.25));q3=float(np.quantile(fd,.75))
    low=fd<=q1;high=fd>=q3
    within=rd[samefam];between=rd[~samefam]

    result={
      "analysis":"naamp_functional_response_decoupling_v0_1",
      "contract":"NAAMP_FUNCTIONAL_RESPONSE_DECOUPLING_CONTRACT_V0_1.json",
      "n_response_eligible_species":29,
      "n_adjusted_response_estimable":int(len(responses)),
      "n_complete_functional_response_species":int(len(species)),
      "species":species,
      "response_fit_audit":audit,
      "primary":{
        "mantel_style_correlation":observed,
        "n_species_pairs":int(len(fd)),
        "unrestricted_permutations":N_PERM,
        "unrestricted_two_sided_p":p_all,
        "null_mean":float(np.nanmean(null_all)),
        "null_sd":float(np.nanstd(null_all,ddof=0))
      },
      "family_stratified_sensitivity":{
        "permutations":N_PERM,
        "two_sided_p":p_fam,
        "null_mean":float(np.nanmean(null_fam)),
        "null_sd":float(np.nanstd(null_fam,ddof=0)),
        "families":{f:int(families.count(f)) for f in sorted(set(families))}
      },
      "secondary":{
        "functional_distance_q25":q1,
        "functional_distance_q75":q3,
        "opposite_sign_fraction_lowest_distance_quartile":float(np.mean(opp[low])),
        "opposite_sign_fraction_highest_distance_quartile":float(np.mean(opp[high])),
        "mean_response_dissimilarity_within_family":float(np.mean(within)) if len(within) else None,
        "mean_response_dissimilarity_between_family":float(np.mean(between)) if len(between) else None
      },
      "interpretation_boundary":{
        "trait_space":"four frozen AmphiBIO life-history/reproductive axes",
        "pairwise_nonindependence_handled_by_label_permutation":True,
        "causal_rainfall_claim_authorized":False,
        "evolutionary_mechanism_claim_authorized":False,
        "endpoint_retuning_after_readback_authorized":False
      }
    }
    Path("NAAMP_FUNCTIONAL_RESPONSE_DECOUPLING_RECEIPT_V0_1.json").write_text(
      json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
