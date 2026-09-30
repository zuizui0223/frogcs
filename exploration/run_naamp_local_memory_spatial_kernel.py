#!/usr/bin/env python3
from __future__ import annotations
import importlib.util, json, time, urllib.error
from collections import defaultdict
from pathlib import Path
import numpy as np
import pandas as pd
import statsmodels.api as sm

ROOT=Path(__file__).resolve().parents[1]
NAAMP=ROOT/"scripts"/"naamp"
OUT=ROOT/"exploration"/"NAAMP_LOCAL_MEMORY_SPATIAL_KERNEL_RECEIPT_V0_1.json"
Q=1.959963984540054

def loadmod(name,path):
    s=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(s)
    assert s.loader
    s.loader.exec_module(m)
    return m

base=loadmod("base",NAAMP/"run_naamp_ecological_pulse.py")
spatial=loadmod("spatial",NAAMP/"run_naamp_spatial_taxonomic_activation_decomposition.py")
sameobs=loadmod("sameobs",NAAMP/"run_naamp_same_observer_robustness.py")

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
        raise RuntimeError(f"multiple SiteIDs {list(bad)[:10]}")
    return {k:next(iter(v)) for k,v in vals.items()}

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

def stable_pair(p,sampled,site):
    w=str(p.wet_RunID); d=str(p.dry_RunID)
    ws=set(sampled[w]); ds=set(sampled[d])
    return len(ws)==10 and ws==ds and all(
        site.get((w,st)) is not None and site.get((w,st))==site.get((d,st))
        for st in ws
    )

def build_history(runs):
    meta={}
    by_stratum=defaultdict(list)
    for r in runs.itertuples(index=False):
        rid=str(r.RunID)
        key=(str(r.State),str(r.RouteNumber),str(r.RunNumber))
        meta[rid]={"key":key,"year":int(r.SurveyYear)}
        by_stratum[key].append(rid)
    for k in by_stratum:
        by_stratum[k]=sorted(by_stratum[k],key=lambda rid:(meta[rid]["year"],rid))
    return meta,by_stratum

def pair_rows(pid,p,sampled,site,ci,meta,by_stratum,same_observer):
    w=str(p.wet_RunID); d=str(p.dry_RunID)
    key=meta[w]["key"]
    cutoff=int(p.year_earlier)
    prior=[rid for rid in by_stratum[key] if meta[rid]["year"]<cutoff]
    if not prior:
        return []

    prior_route_species=set()
    site_strong_species=defaultdict(set)
    site_effort=defaultdict(int)

    for rid in prior:
        seen_sites=set()
        for st in sampled.get(rid,set()):
            sid=site.get((rid,st))
            if sid is None:
                continue
            seen_sites.add(sid)
            for sp,x in ci.get((rid,st),{}).items():
                if x>0:
                    prior_route_species.add(sp)
                if x>=2:
                    site_strong_species[sid].add(sp)
        for sid in seen_sites:
            site_effort[sid]+=1

    dry_route=set()
    wet_route=set()
    for st in sampled[d]:
        dry_route.update(ci.get((d,st),{}))
    for st in sampled[w]:
        wet_route.update(ci.get((w,st),{}))

    focal=sorted((wet_route-dry_route)&prior_route_species)
    current={}
    for st in sorted(sampled[w],key=lambda x:int(float(x))):
        current[int(float(st))]=site[(w,st)]
    current_sids=set(current.values())

    rows=[]
    for sp in focal:
        group=f"{pid}|{sp}"
        strong_current={sn for sn,sid in current.items() if sp in site_strong_species.get(sid,set())}
        for sn,sid in current.items():
            wet=int(ci.get((w,str(sn)),{}).get(sp,0))
            same=float(sn in strong_current)
            adjacent=float(
                not same and any(abs(sn-z)==1 for z in strong_current)
            )
            distant=float(
                not same and not adjacent and len(strong_current)>0
            )
            other_rich=float(len(site_strong_species.get(sid,set())-{sp}))
            rows.append({
                "pair_species":group,
                "pair_id":int(pid),
                "species":sp,
                "route_cluster":str(p.route_cluster),
                "same_observer":bool(same_observer),
                "wet_strong":float(wet>=2),
                "wet_full":float(wet==3),
                "same_site_memory":same,
                "adjacent_site_memory_only":adjacent,
                "distant_route_memory_only":distant,
                "no_current_route_site_memory":float(not (same or adjacent or distant)),
                "other_species_prior_strong_richness":other_rich,
                "prior_site_effort":float(site_effort.get(sid,0)),
            })
    return rows

def fit_within(df,outcome):
    d=df.copy()
    # Require at least two realized memory categories within pair x species.
    catcols=["same_site_memory","adjacent_site_memory_only","distant_route_memory_only","no_current_route_site_memory"]
    ncat=d.groupby("pair_species")[catcols].apply(
        lambda x: int((x.sum(axis=0)>0).sum())
    )
    good=ncat[ncat>=2].index
    d=d[d.pair_species.isin(good)].copy()
    if d.empty:
        return None

    d["other_log"]=np.log1p(d.other_species_prior_strong_richness)
    for col in [outcome,"same_site_memory","adjacent_site_memory_only","distant_route_memory_only","other_log","prior_site_effort"]:
        d[col+"_w"]=d[col]-d.groupby("pair_species")[col].transform("mean")

    cols=["same_site_memory_w","adjacent_site_memory_only_w","distant_route_memory_only_w","other_log_w","prior_site_effort_w"]
    X=d[cols].astype(float)
    keep=[]
    for c in cols:
        if c=="same_site_memory_w" or float(np.abs(X[c]).sum())>1e-12:
            keep.append(c)
    X=X[keep]
    y=d[outcome+"_w"].astype(float)
    m=sm.OLS(y,X).fit(cov_type="cluster",cov_kwds={"groups":d.route_cluster})

    def coef(name):
        if name not in m.params.index:
            return None
        b=float(m.params[name]); se=float(m.bse[name])
        return {"beta":b,"se":se,"ci95":[b-Q*se,b+Q*se],"p":float(m.pvalues[name])}

    same=coef("same_site_memory_w")
    adj=coef("adjacent_site_memory_only_w")
    distant=coef("distant_route_memory_only_w")
    generic=coef("other_log_w")
    effort=coef("prior_site_effort_w")

    contrast=None
    if adj is not None:
        names=list(m.params.index)
        v=np.zeros(len(names))
        v[names.index("same_site_memory_w")]=1.0
        v[names.index("adjacent_site_memory_only_w")]=-1.0
        est=float(v @ m.params.to_numpy())
        cov=np.asarray(m.cov_params())
        se=float(np.sqrt(max(v @ cov @ v,0)))
        contrast={
            "beta":est,"se":se,"ci95":[est-Q*se,est+Q*se],
            "z":est/se if se>0 else None
        }

    primary=bool(
        same is not None
        and same["beta"]>0
        and same["ci95"][0]>0
        and contrast is not None
        and contrast["beta"]>0
        and contrast["ci95"][0]>0
    )
    adjacent_support=bool(adj is not None and adj["beta"]>0 and adj["ci95"][0]>0)
    return {
        "outcome":outcome,
        "n_rows":int(len(d)),
        "n_pair_species_groups":int(d.pair_species.nunique()),
        "n_routes":int(d.route_cluster.nunique()),
        "n_species":int(d.species.nunique()),
        "same_site":same,
        "adjacent_site_only":adj,
        "distant_route_site_only":distant,
        "generic_other_species_site_quality":generic,
        "prior_site_effort":effort,
        "same_minus_adjacent":contrast,
        "classification":{
            "fine_scale_same_site_localization_supported":primary,
            "adjacent_neighborhood_propagation_supported":adjacent_support
        }
    }

def main():
    raw=load_retry()
    runs,sets=base.build_runs(raw)
    eligible=set(runs.RunID.astype(str))
    sampled,_=spatial.stop_matrix(raw,eligible)
    site=site_map(raw,eligible)
    ci=ci_map(raw,eligible,sampled)
    meta,by_stratum=build_history(runs)

    allpairs=base.pair_runs(runs,sets).copy().reset_index(drop=True)
    stable=allpairs.loc[
        np.asarray([stable_pair(p,sampled,site) for p in allpairs.itertuples(index=False)],bool)
    ].copy().reset_index(drop=True)
    _,same=sameobs.same_observer_pairs(raw,runs,sets)
    same_keys={(str(p.wet_RunID),str(p.dry_RunID)) for p in same.itertuples(index=False)}

    rows=[]
    for pid,p in enumerate(stable.itertuples(index=False)):
        rows.extend(pair_rows(
            pid,p,sampled,site,ci,meta,by_stratum,
            (str(p.wet_RunID),str(p.dry_RunID)) in same_keys
        ))
    d=pd.DataFrame(rows)

    primary=fit_within(d,"wet_strong")
    gate=bool(
        primary is not None
        and primary["n_pair_species_groups"]>=500
        and primary["n_routes"]>=250
        and primary["n_species"]>=20
    )
    out={
        "analysis":"naamp_local_memory_spatial_kernel_v0_1",
        "contract":"exploration/NAAMP_LOCAL_MEMORY_SPATIAL_KERNEL_CONTRACT_V0_1.json",
        "coverage":{
            "physically_stable_pairs":int(len(stable)),
            "candidate_rows":int(len(d)),
            "candidate_groups":int(d.pair_species.nunique()) if len(d) else 0,
            "candidate_species":int(d.species.nunique()) if len(d) else 0,
            "gate_pass":gate
        },
        "response_endpoints_read":False
    }
    if not gate:
        out["primary_precheck"]=primary
        OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
        print(json.dumps(out,indent=2,sort_keys=True))
        return

    full=primary
    full_chorus=fit_within(d,"wet_full")
    ds=d[d.same_observer].copy()
    same_fit=fit_within(ds,"wet_strong")

    out.update({
        "response_endpoints_read":True,
        "primary_wet_strong":full,
        "secondary_wet_full":full_chorus,
        "same_observer_sensitivity":same_fit,
        "classification":{
            "fine_scale_same_site_localization_supported":bool(full["classification"]["fine_scale_same_site_localization_supported"]),
            "adjacent_neighborhood_propagation_supported":bool(full["classification"]["adjacent_neighborhood_propagation_supported"]),
            "same_observer_same_site_localization":bool(
                same_fit and same_fit["classification"]["fine_scale_same_site_localization_supported"]
            )
        },
        "interpretation_boundary":{
            "route_order_adjacency_not_metric_distance":True,
            "continuous_occupancy_proven":False,
            "species_specific_local_template":True,
            "individual_movement_inferred":False,
            "causal_memory_claim":False
        }
    })
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
