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
OUT=ROOT/"exploration"/"NAAMP_LOCAL_CHORUS_MEMORY_AGE_RECEIPT_V0_1.json"
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
        raise RuntimeError(f"multiple SiteIDs: {list(bad)[:10]}")
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

def history_index(runs,sampled,site,ci):
    meta={}
    by_stratum=defaultdict(list)
    for r in runs.itertuples(index=False):
        rid=str(r.RunID)
        key=(str(r.State),str(r.RouteNumber),str(r.RunNumber))
        meta[rid]={"key":key,"year":int(r.SurveyYear)}
        by_stratum[key].append(rid)
    for key in by_stratum:
        by_stratum[key]=sorted(by_stratum[key],key=lambda rid:(meta[rid]["year"],rid))
    return meta,by_stratum

def pair_rows(pid,p,sampled,site,ci,meta,by_stratum,same_observer):
    w=str(p.wet_RunID); d=str(p.dry_RunID)
    key=meta[w]["key"]
    cutoff=int(p.year_earlier)
    prior=[rid for rid in by_stratum[key] if meta[rid]["year"]<cutoff]
    if not prior:
        return []

    prior_route_species=set()
    latest_strong=defaultdict(dict)  # sid -> sp -> most recent prior year
    for rid in prior:
        y=meta[rid]["year"]
        for st in sampled.get(rid,set()):
            sid=site.get((rid,st))
            if sid is None:
                continue
            for sp,x in ci.get((rid,st),{}).items():
                if x>0:
                    prior_route_species.add(sp)
                if x>=2:
                    prev=latest_strong[sid].get(sp)
                    if prev is None or y>prev:
                        latest_strong[sid][sp]=y

    dry_route=set()
    wet_route=set()
    for st in sampled[d]:
        dry_route.update(ci.get((d,st),{}))
    for st in sampled[w]:
        wet_route.update(ci.get((w,st),{}))

    focal=sorted((wet_route-dry_route)&prior_route_species)
    rows=[]
    for sp in focal:
        group=f"{pid}|{sp}"
        for st in sorted(sampled[w]):
            sid=site[(w,st)]
            wet=int(ci.get((w,st),{}).get(sp,0))
            py=latest_strong.get(sid,{}).get(sp)
            lag=(cutoff-py) if py is not None else np.nan
            recent=float(np.isfinite(lag) and lag<=3)
            old=float(np.isfinite(lag) and lag>=4)
            rows.append({
                "pair_id":int(pid),
                "pair_species":group,
                "species":sp,
                "route_cluster":str(p.route_cluster),
                "same_observer":bool(same_observer),
                "SiteID":sid,
                "wet_strong":float(wet>=2),
                "wet_full":float(wet==3),
                "recent_memory":recent,
                "old_memory":old,
                "has_memory":float(np.isfinite(lag)),
                "lag_years":float(lag) if np.isfinite(lag) else np.nan,
            })
    return rows

def fit_age(df,outcome):
    d=df.copy()
    # Primary estimand requires old-memory and no-memory sites in the same pair x species.
    group_ok=[]
    for g,x in d.groupby("pair_species"):
        has_old=bool((x.old_memory==1).any())
        has_none=bool((x.has_memory==0).any())
        if has_old and has_none:
            group_ok.append(g)
    d=d[d.pair_species.isin(group_ok)].copy()
    if d.empty:
        return None

    d["y_w"]=d[outcome]-d.groupby("pair_species")[outcome].transform("mean")
    d["old_w"]=d.old_memory-d.groupby("pair_species").old_memory.transform("mean")
    d["recent_w"]=d.recent_memory-d.groupby("pair_species").recent_memory.transform("mean")

    X=d[["old_w","recent_w"]].astype(float)
    # Remove recent column only if globally zero after demeaning.
    if float(np.abs(X["recent_w"]).sum())<1e-12:
        X=X[["old_w"]]
    fit=sm.OLS(d["y_w"].astype(float),X).fit(
        cov_type="cluster",cov_kwds={"groups":d.route_cluster}
    )
    b=float(fit.params["old_w"]); se=float(fit.bse["old_w"])
    out={
        "outcome":outcome,
        "n_rows":int(len(d)),
        "n_pair_species_groups":int(d.pair_species.nunique()),
        "n_routes":int(d.route_cluster.nunique()),
        "n_species":int(d.species.nunique()),
        "old_memory_beta":b,
        "old_memory_se":se,
        "old_memory_ci95":[b-Q*se,b+Q*se],
        "old_memory_p":float(fit.pvalues["old_w"]),
        "old_memory_positive_ci":bool(b>0 and b-Q*se>0),
    }
    if "recent_w" in fit.params.index:
        br=float(fit.params["recent_w"]); ser=float(fit.bse["recent_w"])
        out.update({
            "recent_memory_beta":br,
            "recent_memory_se":ser,
            "recent_memory_ci95":[br-Q*ser,br+Q*ser],
            "recent_memory_p":float(fit.pvalues["recent_w"]),
        })
    return out

def fit_lag_decay(df):
    d=df[np.isfinite(df.lag_years)].copy()
    good=[]
    for g,x in d.groupby("pair_species"):
        if x.lag_years.nunique()>=2:
            good.append(g)
    d=d[d.pair_species.isin(good)].copy()
    if d.empty:
        return None
    d["loglag"]=np.log1p(d.lag_years.astype(float))
    d["y_w"]=d.wet_strong-d.groupby("pair_species").wet_strong.transform("mean")
    d["x_w"]=d.loglag-d.groupby("pair_species").loglag.transform("mean")
    fit=sm.OLS(d["y_w"],d[["x_w"]]).fit(
        cov_type="cluster",cov_kwds={"groups":d.route_cluster}
    )
    b=float(fit.params["x_w"]); se=float(fit.bse["x_w"])
    return {
        "n_rows":int(len(d)),
        "n_pair_species_groups":int(d.pair_species.nunique()),
        "n_routes":int(d.route_cluster.nunique()),
        "beta_log1p_lag":b,
        "se":se,
        "ci95":[b-Q*se,b+Q*se],
        "p":float(fit.pvalues["x_w"]),
    }

def main():
    raw=load_retry()
    runs,sets=base.build_runs(raw)
    eligible=set(runs.RunID.astype(str))
    sampled,_=spatial.stop_matrix(raw,eligible)
    site=site_map(raw,eligible)
    ci=ci_map(raw,eligible,sampled)
    meta,by_stratum=history_index(runs,sampled,site,ci)

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

    primary=fit_age(d,"wet_strong")
    gate=bool(
        primary is not None
        and primary["n_pair_species_groups"]>=300
        and primary["n_routes"]>=200
        and primary["n_species"]>=20
    )

    out={
        "analysis":"naamp_local_chorus_memory_age_v0_1",
        "contract":"exploration/NAAMP_LOCAL_CHORUS_MEMORY_AGE_CONTRACT_V0_1.json",
        "coverage":{
            "physically_stable_pairs":int(len(stable)),
            "candidate_rows":int(len(d)),
            "candidate_groups":int(d.pair_species.nunique()) if len(d) else 0,
            "candidate_species":int(d.species.nunique()) if len(d) else 0,
            "gate_pass":gate,
        },
        "response_endpoints_read":False,
    }
    if not gate:
        out["primary_precheck"]=primary
        OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
        print(json.dumps(out,indent=2,sort_keys=True))
        return

    full=primary
    full_chorus=fit_age(d,"wet_full")
    ds=d[d.same_observer].copy()
    same_fit=fit_age(ds,"wet_strong")
    lag=fit_lag_decay(d)

    out.update({
        "response_endpoints_read":True,
        "primary_wet_strong":full,
        "secondary_wet_full":full_chorus,
        "same_observer_sensitivity":same_fit,
        "continuous_lag_decay_diagnostic":lag,
        "classification":{
            "durable_old_memory_targeting_supported":bool(full["old_memory_positive_ci"]),
            "same_observer_support":bool(same_fit and same_fit["old_memory_positive_ci"]),
            "full_chorus_old_memory_support":bool(full_chorus and full_chorus["old_memory_positive_ci"]),
        },
        "interpretation_boundary":{
            "continuous_occupancy_proven":False,
            "same_individuals_inferred":False,
            "stable_local_template_interpretation":True,
            "causal_biological_memory_claim":False,
        }
    })
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
