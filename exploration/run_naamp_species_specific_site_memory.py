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
    rows=[]
    for sp in focal:
        group=f"{pid}|{sp}"
        for st in sorted(sampled[w]):
            sid=site[(w,st)]
            wet=int(ci.get((w,st),{}).get(sp,0))
            strong_set=site_strong_species.get(sid,set())
            rows.append({
                "pair_species":group,
                "pair_id":int(pid),
                "species":sp,
                "route_cluster":str(p.route_cluster),
                "rain_contrast":float(p.rain_contrast),
                "same_observer":bool(same_observer),
                "SiteID":sid,
                "wet_strong":float(wet>=2),
                "wet_full":float(wet==3),
                "same_species_prior_strong":float(sp in strong_set),
                "other_species_prior_strong_richness":float(len(strong_set-{sp})),
                "prior_site_effort":float(site_effort.get(sid,0)),
            })
    return rows

def fit_within(df,outcome,interaction=False):
    d=df.copy()
    inf=d.groupby("pair_species")["same_species_prior_strong"].nunique()
    good=inf[inf>=2].index
    d=d[d.pair_species.isin(good)].copy()
    if d.empty:
        return None

    d["other_log"]=np.log1p(d.other_species_prior_strong_richness)
    for col in (outcome,"same_species_prior_strong","other_log","prior_site_effort"):
        d[col+"_w"]=d[col]-d.groupby("pair_species")[col].transform("mean")
    cols=["same_species_prior_strong_w","other_log_w","prior_site_effort_w"]
    if interaction:
        d["same_x_rain"]=d.same_species_prior_strong*d.rain_contrast
        d["same_x_rain_w"]=d.same_x_rain-d.groupby("pair_species").same_x_rain.transform("mean")
        cols.append("same_x_rain_w")

    X=d[cols].astype(float)
    # Remove globally invariant nuisance columns but never the focal memory predictor.
    keep=["same_species_prior_strong_w"]
    for c in cols[1:]:
        if float(np.abs(X[c]).sum())>1e-12:
            keep.append(c)
    X=X[keep]
    y=d[outcome+"_w"].astype(float)
    m=sm.OLS(y,X).fit(cov_type="cluster",cov_kwds={"groups":d.route_cluster})

    b=float(m.params["same_species_prior_strong_w"])
    se=float(m.bse["same_species_prior_strong_w"])
    out={
        "outcome":outcome,
        "n_rows":int(len(d)),
        "n_pair_species_groups":int(d.pair_species.nunique()),
        "n_routes":int(d.route_cluster.nunique()),
        "n_species":int(d.species.nunique()),
        "same_species_memory_beta":b,
        "same_species_memory_se":se,
        "same_species_memory_ci95":[b-Q*se,b+Q*se],
        "same_species_memory_p":float(m.pvalues["same_species_prior_strong_w"]),
        "same_species_memory_positive_ci":bool(b>0 and b-Q*se>0),
    }
    if "other_log_w" in m.params.index:
        bo=float(m.params["other_log_w"]); seo=float(m.bse["other_log_w"])
        out.update({
            "generic_other_species_memory_beta":bo,
            "generic_other_species_memory_ci95":[bo-Q*seo,bo+Q*seo],
            "generic_other_species_memory_p":float(m.pvalues["other_log_w"]),
        })
    if "prior_site_effort_w" in m.params.index:
        be=float(m.params["prior_site_effort_w"]); see=float(m.bse["prior_site_effort_w"])
        out.update({
            "prior_site_effort_beta":be,
            "prior_site_effort_ci95":[be-Q*see,be+Q*see],
            "prior_site_effort_p":float(m.pvalues["prior_site_effort_w"]),
        })
    if interaction and "same_x_rain_w" in m.params.index:
        bi=float(m.params["same_x_rain_w"]); sei=float(m.bse["same_x_rain_w"])
        out.update({
            "rain_x_same_species_memory_beta":bi,
            "rain_x_same_species_memory_ci95":[bi-Q*sei,bi+Q*sei],
            "rain_x_same_species_memory_p":float(m.pvalues["same_x_rain_w"]),
        })
    return out

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

    primary=fit_within(d,"wet_strong",False)
    gate=bool(
        primary is not None
        and primary["n_pair_species_groups"]>=500
        and primary["n_routes"]>=250
        and primary["n_species"]>=20
    )
    out={
        "analysis":"naamp_species_specific_site_memory_v0_1",
        "contract":"exploration/NAAMP_SPECIES_SPECIFIC_SITE_MEMORY_CONTRACT_V0_1.json",
        "coverage":{
            "physically_stable_pairs":int(len(stable)),
            "candidate_rows":int(len(d)),
            "candidate_pair_species_groups":int(d.pair_species.nunique()) if len(d) else 0,
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
    full_chorus=fit_within(d,"wet_full",False)
    inter=fit_within(d,"wet_strong",True)
    ds=d[d.same_observer].copy()
    same_fit=fit_within(ds,"wet_strong",False)

    out.update({
        "response_endpoints_read":True,
        "primary_wet_strong":full,
        "secondary_wet_full":full_chorus,
        "rain_interaction_diagnostic":inter,
        "same_observer_sensitivity":same_fit,
        "classification":{
            "species_specific_memory_beyond_generic_site_quality_supported":bool(full["same_species_memory_positive_ci"]),
            "full_chorus_species_specific_memory_supported":bool(full_chorus and full_chorus["same_species_memory_positive_ci"]),
            "same_observer_support":bool(same_fit and same_fit["same_species_memory_positive_ci"]),
        },
        "interpretation_boundary":{
            "generic_site_quality_adjusted":True,
            "continuous_occupancy_proven":False,
            "species_specific_habitat_matching_or_local_population_recurrence":True,
            "individual_site_fidelity_proven":False,
            "causal_rainfall_claim":False,
        }
    })
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
