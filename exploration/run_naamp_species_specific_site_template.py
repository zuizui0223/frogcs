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
OUT=ROOT/"exploration"/"NAAMP_SPECIES_SPECIFIC_SITE_TEMPLATE_RECEIPT_V0_1.json"
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
    if bad: raise RuntimeError(f"multiple SiteIDs: {list(bad)[:10]}")
    return {k:next(iter(v)) for k,v in vals.items()}

def ci_map(raw,eligible,sampled):
    vals=defaultdict(list)
    for r in raw["Counts.csv"]:
        rid=(r.get("RunID") or "").strip()
        st=(r.get("StopNumber") or "").strip()
        sp=(r.get("Species") or "").strip()
        if rid not in eligible or st not in sampled.get(rid,set()) or not sp: continue
        try: x=int(float((r.get("CallingIndex") or "").strip()))
        except Exception: continue
        if x in (1,2,3): vals[(rid,st,sp)].append(x)
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
    for k in by_stratum:
        by_stratum[k]=sorted(by_stratum[k],key=lambda rid:(meta[rid]["year"],rid))
    return meta,by_stratum

def pair_rows(pid,p,sampled,site,ci,meta,by_stratum,same_observer):
    w=str(p.wet_RunID); d=str(p.dry_RunID)
    key=meta[w]["key"]; cutoff=int(p.year_earlier)
    prior=[rid for rid in by_stratum[key] if meta[rid]["year"]<cutoff]
    if not prior: return []

    # Prior route pool.
    route_prior=set()
    for rid in prior:
        for st in sampled.get(rid,set()):
            route_prior.update(ci.get((rid,st),{}))

    # Focal route-new species in wet survey.
    dry_route=set(); wet_route=set()
    for st in sampled[d]:
        dry_route.update(ci.get((d,st),{}))
    for st in sampled[w]:
        wet_route.update(ci.get((w,st),{}))
    focal=sorted((wet_route-dry_route)&route_prior)
    if not focal: return []

    # Site opportunities and strong species by prior run.
    prior_site_runs=defaultdict(list)  # sid -> list[set strong spp]
    for rid in prior:
        seen_sids=set()
        for st in sampled.get(rid,set()):
            sid=site.get((rid,st))
            if sid is None or sid in seen_sids: continue
            seen_sids.add(sid)
            strong={sp for sp,x in ci.get((rid,st),{}).items() if x>=2}
            prior_site_runs[sid].append(strong)

    rows=[]
    for sp in focal:
        group=f"{pid}|{sp}"
        for st in sorted(sampled[w]):
            sid=site[(w,st)]
            opportunities=prior_site_runs.get(sid,[])
            if not opportunities:
                continue
            own=float(any(sp in s for s in opportunities))
            generic=float(np.mean([len(s-{sp}) for s in opportunities]))
            wet=int(ci.get((w,st),{}).get(sp,0))
            rows.append({
                "pair_id":int(pid),
                "pair_species":group,
                "species":sp,
                "route_cluster":str(p.route_cluster),
                "rain_contrast":float(p.rain_contrast),
                "same_observer":bool(same_observer),
                "SiteID":sid,
                "prior_opportunities":float(len(opportunities)),
                "own_prior_strong":own,
                "generic_other_strong_rate":generic,
                "wet_strong":float(wet>=2),
                "wet_full":float(wet==3),
            })
    return rows

def fit_model(df,outcome):
    d=df.copy()
    informative=d.groupby("pair_species")["own_prior_strong"].nunique()
    good=informative[informative>=2].index
    d=d[d.pair_species.isin(good)].copy()
    if d.empty: return None

    d["own_x_rain"]=d.own_prior_strong*d.rain_contrast
    d["generic_x_rain"]=d.generic_other_strong_rate*d.rain_contrast
    for col in (outcome,"own_prior_strong","generic_other_strong_rate","own_x_rain","generic_x_rain"):
        d[col+"_w"]=d[col]-d.groupby("pair_species")[col].transform("mean")

    X=d[["own_prior_strong_w","generic_other_strong_rate_w","own_x_rain_w","generic_x_rain_w"]].astype(float)
    # Drop numerically constant columns if needed, but never drop own memory.
    keep=["own_prior_strong_w"]
    for col in ["generic_other_strong_rate_w","own_x_rain_w","generic_x_rain_w"]:
        if float(np.abs(X[col]).sum())>1e-12:
            keep.append(col)
    X=X[keep]
    fit=sm.OLS(d[outcome+"_w"].astype(float),X).fit(
        cov_type="cluster",cov_kwds={"groups":d.route_cluster}
    )

    b=float(fit.params["own_prior_strong_w"]); se=float(fit.bse["own_prior_strong_w"])
    out={
        "outcome":outcome,
        "n_rows":int(len(d)),
        "n_pair_species_groups":int(d.pair_species.nunique()),
        "n_routes":int(d.route_cluster.nunique()),
        "n_species":int(d.species.nunique()),
        "own_memory_beta":b,
        "own_memory_se":se,
        "own_memory_ci95":[b-Q*se,b+Q*se],
        "own_memory_p":float(fit.pvalues["own_prior_strong_w"]),
        "own_memory_positive_ci":bool(b>0 and b-Q*se>0),
        "included_columns":keep,
    }
    if "generic_other_strong_rate_w" in fit.params.index:
        bg=float(fit.params["generic_other_strong_rate_w"]); seg=float(fit.bse["generic_other_strong_rate_w"])
        out.update({
            "generic_site_beta":bg,
            "generic_site_ci95":[bg-Q*seg,bg+Q*seg],
            "generic_site_p":float(fit.pvalues["generic_other_strong_rate_w"])
        })
    if "own_x_rain_w" in fit.params.index:
        bi=float(fit.params["own_x_rain_w"]); sei=float(fit.bse["own_x_rain_w"])
        out.update({
            "own_memory_x_rain_beta":bi,
            "own_memory_x_rain_ci95":[bi-Q*sei,bi+Q*sei],
            "own_memory_x_rain_p":float(fit.pvalues["own_x_rain_w"])
        })
    if "generic_x_rain_w" in fit.params.index:
        bj=float(fit.params["generic_x_rain_w"]); sej=float(fit.bse["generic_x_rain_w"])
        out.update({
            "generic_site_x_rain_beta":bj,
            "generic_site_x_rain_ci95":[bj-Q*sej,bj+Q*sej],
            "generic_site_x_rain_p":float(fit.pvalues["generic_x_rain_w"])
        })
    return out

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

    primary=fit_model(d,"wet_strong")
    gate=bool(
        primary is not None
        and primary["n_pair_species_groups"]>=500
        and primary["n_routes"]>=250
        and primary["n_species"]>=20
    )
    out={
      "analysis":"naamp_species_specific_site_template_v0_1",
      "contract":"exploration/NAAMP_SPECIES_SPECIFIC_SITE_TEMPLATE_CONTRACT_V0_1.json",
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
    full_chorus=fit_model(d,"wet_full")
    ds=d[d.same_observer].copy()
    same_fit=fit_model(ds,"wet_strong")

    out.update({
      "response_endpoints_read":True,
      "primary_wet_strong":full,
      "secondary_wet_full":full_chorus,
      "same_observer_sensitivity":same_fit,
      "classification":{
        "species_specific_template_supported":bool(full["own_memory_positive_ci"]),
        "same_observer_support":bool(same_fit and same_fit["own_memory_positive_ci"]),
        "full_chorus_support":bool(full_chorus and full_chorus["own_memory_positive_ci"])
      },
      "interpretation_boundary":{
        "generic_other_species_site_quality_controlled":True,
        "persistent_population_vs_species_specific_habitat_unresolved":True,
        "individual_site_fidelity_inferred":False,
        "causal_rainfall_claim":False
      }
    })
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
