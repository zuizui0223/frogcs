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
OUT=ROOT/"exploration"/"NAAMP_SPECIES_SPECIFIC_SITE_MEMORY_RECEIPT_V0_1.json"
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

def history_index(runs):
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
    site_exposure=defaultdict(int)
    focal_any=defaultdict(set)
    focal_strong=defaultdict(set)
    site_sum_any=defaultdict(float)
    site_sum_strong=defaultdict(float)

    for rid in prior:
        for st in sampled.get(rid,set()):
            sid=site.get((rid,st))
            if sid is None:
                continue
            site_exposure[sid]+=1
            cmap=ci.get((rid,st),{})
            any_spp={sp for sp,x in cmap.items() if x>0}
            strong_spp={sp for sp,x in cmap.items() if x>=2}
            prior_route_species.update(any_spp)
            focal_any[sid].update(any_spp)
            focal_strong[sid].update(strong_spp)
            site_sum_any[sid]+=float(len(any_spp))
            site_sum_strong[sid]+=float(len(strong_spp))

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
            exp=site_exposure.get(sid,0)
            if exp<1:
                continue
            wet=int(ci.get((w,st),{}).get(sp,0))

            any_total=site_sum_any[sid]
            strong_total=site_sum_strong[sid]
            focal_any_count=0.0
            focal_strong_count=0.0
            for rid in prior:
                # subtract focal species contribution only when this SiteID was sampled in the run
                if sid not in {site.get((rid,x)) for x in sampled.get(rid,set()) if site.get((rid,x)) is not None}:
                    continue
                found_ci=0
                for pst in sampled.get(rid,set()):
                    if site.get((rid,pst))==sid:
                        found_ci=max(found_ci,int(ci.get((rid,pst),{}).get(sp,0)))
                focal_any_count+=float(found_ci>0)
                focal_strong_count+=float(found_ci>=2)

            general_any=(any_total-focal_any_count)/exp
            general_strong=(strong_total-focal_strong_count)/exp

            rows.append({
                "pair_id":int(pid),
                "pair_species":group,
                "species":sp,
                "route_cluster":str(p.route_cluster),
                "same_observer":bool(same_observer),
                "SiteID":sid,
                "focal_prior_site_strong":float(sp in focal_strong.get(sid,set())),
                "prior_site_exposure":float(exp),
                "log1p_exposure":float(np.log1p(exp)),
                "general_strong_richness":float(general_strong),
                "general_any_richness":float(general_any),
                "wet_strong":float(wet>=2),
                "wet_full":float(wet==3),
            })
    return rows

def informative_groups(df):
    good=[]
    for g,x in df.groupby("pair_species"):
        if x.focal_prior_site_strong.nunique()>=2:
            good.append(g)
    return good

def coverage(df,groups):
    d=df[df.pair_species.isin(groups)]
    return {
        "n_rows":int(len(d)),
        "n_pair_species_groups":int(len(groups)),
        "n_routes":int(d.route_cluster.nunique()) if len(d) else 0,
        "n_species":int(d.species.nunique()) if len(d) else 0,
    }

def fit_model(df,outcome,groups,use_any=False):
    d=df[df.pair_species.isin(groups)].copy()
    if d.empty:
        return None

    cols_raw=["focal_prior_site_strong","log1p_exposure","general_strong_richness"]
    if use_any:
        cols_raw.append("general_any_richness")

    d["y_w"]=d[outcome]-d.groupby("pair_species")[outcome].transform("mean")
    cols=[]
    for c in cols_raw:
        wc=c+"_w"
        d[wc]=d[c]-d.groupby("pair_species")[c].transform("mean")
        if float(np.abs(d[wc]).sum())>1e-12:
            cols.append(wc)
    if "focal_prior_site_strong_w" not in cols:
        return None

    fit=sm.OLS(d["y_w"].astype(float),d[cols].astype(float)).fit(
        cov_type="cluster",cov_kwds={"groups":d.route_cluster}
    )
    term="focal_prior_site_strong_w"
    b=float(fit.params[term]); se=float(fit.bse[term])
    return {
        "outcome":outcome,
        **coverage(df,groups),
        "formula_terms":cols,
        "focal_memory_beta":b,
        "focal_memory_se":se,
        "focal_memory_ci95":[b-Q*se,b+Q*se],
        "focal_memory_p":float(fit.pvalues[term]),
        "focal_memory_positive_ci":bool(b>0 and b-Q*se>0),
        "covariate_betas":{c:float(fit.params[c]) for c in cols if c!=term},
    }

def main():
    raw=load_retry()
    runs,sets=base.build_runs(raw)
    eligible=set(runs.RunID.astype(str))
    sampled,_=spatial.stop_matrix(raw,eligible)
    site=site_map(raw,eligible)
    ci=ci_map(raw,eligible,sampled)
    meta,by_stratum=history_index(runs)

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

    groups=informative_groups(d)
    cov=coverage(d,groups)
    gate=bool(
        cov["n_pair_species_groups"]>=500
        and cov["n_routes"]>=250
        and cov["n_species"]>=20
    )

    out={
        "analysis":"naamp_species_specific_site_memory_v0_1",
        "contract":"exploration/NAAMP_SPECIES_SPECIFIC_SITE_MEMORY_CONTRACT_V0_1.json",
        "coverage":{
            "all_pairs":int(len(allpairs)),
            "physically_stable_pairs":int(len(stable)),
            "candidate_rows":int(len(d)),
            **cov,
            "primary_gate_pass":gate,
        },
        "response_endpoints_read":False,
    }
    if not gate:
        OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
        print(json.dumps(out,indent=2,sort_keys=True))
        return

    primary=fit_model(d,"wet_strong",groups,False)
    any_control=fit_model(d,"wet_strong",groups,True)
    full=fit_model(d,"wet_full",groups,False)

    ds=d[d.same_observer].copy()
    same_groups=informative_groups(ds)
    same_cov=coverage(ds,same_groups)
    same_gate=bool(
        same_cov["n_pair_species_groups"]>=300
        and same_cov["n_routes"]>=200
        and same_cov["n_species"]>=20
    )
    same_fit=fit_model(ds,"wet_strong",same_groups,False) if same_gate else None

    out.update({
        "response_endpoints_read":True,
        "primary_wet_strong_general_strong_control":primary,
        "sensitivity_add_general_any_control":any_control,
        "secondary_wet_full":full,
        "same_observer_sensitivity":{
            "gate_pass":same_gate,
            "coverage":same_cov,
            "result":same_fit,
        },
        "classification":{
            "species_specific_memory_beyond_site_quality_supported":bool(primary and primary["focal_memory_positive_ci"]),
            "general_any_control_support":bool(any_control and any_control["focal_memory_positive_ci"]),
            "full_chorus_support":bool(full and full["focal_memory_positive_ci"]),
            "same_observer_support":bool(same_fit and same_fit["focal_memory_positive_ci"]),
        },
        "interpretation_boundary":{
            "generic_site_productivity_controlled":True,
            "prior_site_sampling_effort_controlled":True,
            "persistent_habitat_matching_excluded":False,
            "continuous_occupancy_proven":False,
            "same_individuals_inferred":False,
            "causal_rainfall_claim":False,
        }
    })
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
