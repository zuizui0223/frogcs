#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import time
import urllib.error
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm

ROOT=Path(__file__).resolve().parents[1]
NAAMP=ROOT/"scripts"/"naamp"
OUT=ROOT/"exploration"/"NAAMP_LOCAL_CHORUS_MEMORY_TARGETING_RECEIPT_V0_1.json"
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
    if len(ws)!=10 or ws!=ds:
        return False
    return all(
        site.get((w,st)) is not None and site.get((w,st))==site.get((d,st))
        for st in ws
    )

def build_history(runs,sampled,site,ci):
    meta={}
    by_stratum=defaultdict(list)
    for r in runs.itertuples(index=False):
        rid=str(r.RunID)
        key=(str(r.State),str(r.RouteNumber),str(r.RunNumber))
        meta[rid]={"key":key,"year":int(r.SurveyYear)}
        by_stratum[key].append(rid)
    for key in by_stratum:
        by_stratum[key]=sorted(by_stratum[key],key=lambda x:(meta[x]["year"],x))
    return meta,by_stratum

def pair_rows(pid,p,sampled,site,ci,meta,by_stratum,same_obs):
    w=str(p.wet_RunID); d=str(p.dry_RunID)
    key=meta[w]["key"]
    cutoff=int(p.year_earlier)
    prior=[rid for rid in by_stratum[key] if meta[rid]["year"]<cutoff]
    if not prior:
        return []

    prior_route_runs_with_species=defaultdict(int)
    prior_site_any=defaultdict(set)
    prior_site_strong=defaultdict(set)
    prior_route_species=set()

    for rid in prior:
        seen_route=set()
        for st in sampled.get(rid,set()):
            sid=site.get((rid,st))
            if sid is None:
                continue
            for sp,x in ci.get((rid,st),{}).items():
                if x>0:
                    prior_site_any[sid].add(sp)
                    prior_route_species.add(sp)
                    seen_route.add(sp)
                if x>=2:
                    prior_site_strong[sid].add(sp)
        for sp in seen_route:
            prior_route_runs_with_species[sp]+=1

    dry_route=set()
    wet_route=set()
    for st in sampled[d]:
        dry_route.update(ci.get((d,st),{}))
    for st in sampled[w]:
        wet_route.update(ci.get((w,st),{}))

    focal=sorted((wet_route-dry_route)&prior_route_species)
    rows=[]
    stops=sorted(sampled[w])
    for sp in focal:
        group=f"{pid}|{sp}"
        freq=prior_route_runs_with_species[sp]/len(prior)
        for st in stops:
            sid=site[(w,st)]
            wet=int(ci.get((w,st),{}).get(sp,0))
            rows.append({
                "pair_id":int(pid),
                "pair_species":group,
                "species":sp,
                "route_cluster":str(p.route_cluster),
                "rain_contrast":float(p.rain_contrast),
                "same_observer":bool(same_obs),
                "SiteID":sid,
                "prior_site_strong":float(sp in prior_site_strong.get(sid,set())),
                "prior_site_any":float(sp in prior_site_any.get(sid,set())),
                "wet_strong":float(wet>=2),
                "wet_full":float(wet==3),
                "wet_presence":float(wet>0),
                "prior_route_frequency":float(freq),
            })
    return rows

def fit_within(df,outcome,memory,with_interaction=False):
    d=df.copy()
    informative=d.groupby("pair_species")[memory].nunique()
    good=informative[informative>=2].index
    d=d[d.pair_species.isin(good)].copy()
    if d.empty:
        return None
    # demean exactly within focal pair x species
    d["y_w"]=d[outcome]-d.groupby("pair_species")[outcome].transform("mean")
    d["m_w"]=d[memory]-d.groupby("pair_species")[memory].transform("mean")
    cols=["m_w"]
    if with_interaction:
        d["mr"]=d[memory]*d.rain_contrast
        d["mr_w"]=d["mr"]-d.groupby("pair_species")["mr"].transform("mean")
        cols.append("mr_w")
    X=d[cols].astype(float)
    y=d["y_w"].astype(float)
    fit=sm.OLS(y,X).fit(cov_type="cluster",cov_kwds={"groups":d.route_cluster})
    bm=float(fit.params["m_w"]); sem=float(fit.bse["m_w"])
    out={
        "outcome":outcome,"memory":memory,
        "n_rows":int(len(d)),
        "n_pair_species_groups":int(d.pair_species.nunique()),
        "n_routes":int(d.route_cluster.nunique()),
        "n_species":int(d.species.nunique()),
        "memory_beta":bm,
        "memory_se":sem,
        "memory_ci95":[bm-Q*sem,bm+Q*sem],
        "memory_p":float(fit.pvalues["m_w"]),
        "memory_positive_ci":bool(bm>0 and bm-Q*sem>0),
    }
    if with_interaction:
        bi=float(fit.params["mr_w"]); sei=float(fit.bse["mr_w"])
        out.update({
            "rain_x_memory_beta":bi,
            "rain_x_memory_se":sei,
            "rain_x_memory_ci95":[bi-Q*sei,bi+Q*sei],
            "rain_x_memory_p":float(fit.pvalues["mr_w"]),
        })
    return out

def main():
    raw=load_retry()
    runs,sets=base.build_runs(raw)
    eligible=set(runs.RunID.astype(str))
    sampled,_=spatial.stop_matrix(raw,eligible)
    site=site_map(raw,eligible)
    ci=ci_map(raw,eligible,sampled)
    meta,by_stratum=build_history(runs,sampled,site,ci)

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

    primary=fit_within(d,"wet_strong","prior_site_strong",False)
    gate=bool(
        primary is not None
        and primary["n_pair_species_groups"]>=500
        and primary["n_routes"]>=250
        and primary["n_species"]>=20
    )
    out={
        "analysis":"naamp_local_chorus_memory_targeting_v0_1",
        "contract":"exploration/NAAMP_LOCAL_CHORUS_MEMORY_TARGETING_CONTRACT_V0_1.json",
        "coverage":{
            "physically_stable_pairs":int(len(stable)),
            "candidate_rows":int(len(d)),
            "candidate_pair_species_groups":int(d.pair_species.nunique()) if len(d) else 0,
            "candidate_species":int(d.species.nunique()) if len(d) else 0,
            "gate_pass":gate,
        },
        "response_endpoints_read":False
    }
    if not gate:
        out["primary_precheck"]=primary
        OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
        print(json.dumps(out,indent=2,sort_keys=True))
        return

    primary_inter=fit_within(d,"wet_strong","prior_site_strong",True)
    full=fit_within(d,"wet_full","prior_site_strong",False)
    anymem=fit_within(d,"wet_strong","prior_site_any",False)
    presence=fit_within(d,"wet_presence","prior_site_strong",False)
    dsame=d[d.same_observer].copy()
    same_primary=fit_within(dsame,"wet_strong","prior_site_strong",False)

    out.update({
        "response_endpoints_read":True,
        "primary_wet_strong_prior_site_strong":primary,
        "secondary_wet_full_prior_site_strong":full,
        "sensitivity_prior_site_any":anymem,
        "secondary_wet_presence":presence,
        "rain_interaction_diagnostic":primary_inter,
        "same_observer_sensitivity":same_primary,
        "classification":{
            "local_strong_chorus_memory_targeting_supported":bool(primary["memory_positive_ci"]),
            "full_chorus_memory_targeting_supported":bool(full and full["memory_positive_ci"]),
            "same_observer_support":bool(same_primary and same_primary["memory_positive_ci"])
        },
        "interpretation_boundary":{
            "species_fixed_exactly_within_group":True,
            "focal_pair_fixed_exactly_within_group":True,
            "continuous_occupancy_proven":False,
            "same_individuals_inferred":False,
            "causal_memory_claim":False
        }
    })
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
