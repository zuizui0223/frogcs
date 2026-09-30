#!/usr/bin/env python3
from __future__ import annotations

import importlib.util, json, time, urllib.error
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy.stats import binomtest

ROOT=Path(__file__).resolve().parents[1]
NAAMP=ROOT/"scripts"/"naamp"
OUT=ROOT/"exploration"/"NAAMP_SITE_TEMPLATE_TAXON_GENERALITY_RECEIPT_V0_1.json"
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
    for k in by_stratum:
        by_stratum[k]=sorted(by_stratum[k],key=lambda rid:(meta[rid]["year"],rid))
    return meta,by_stratum

def pair_rows(pid,p,sampled,site,ci,meta,by_stratum,same_observer):
    w=str(p.wet_RunID); d=str(p.dry_RunID)
    key=meta[w]["key"]; cutoff=int(p.year_earlier)
    prior=[rid for rid in by_stratum[key] if meta[rid]["year"]<cutoff]
    if not prior:
        return []

    route_prior=set()
    for rid in prior:
        for st in sampled.get(rid,set()):
            route_prior.update(ci.get((rid,st),{}))

    dry_route=set(); wet_route=set()
    for st in sampled[d]:
        dry_route.update(ci.get((d,st),{}))
    for st in sampled[w]:
        wet_route.update(ci.get((w,st),{}))
    focal=sorted((wet_route-dry_route)&route_prior)
    if not focal:
        return []

    prior_site_runs=defaultdict(list)
    for rid in prior:
        seen=set()
        for st in sampled.get(rid,set()):
            sid=site.get((rid,st))
            if sid is None or sid in seen:
                continue
            seen.add(sid)
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
                "own_prior_strong":own,
                "generic_other_strong_rate":generic,
                "wet_strong":float(wet>=2),
            })
    return rows

def prep_design(df):
    d=df.copy()
    informative=d.groupby("pair_species")["own_prior_strong"].nunique()
    good=informative[informative>=2].index
    d=d[d.pair_species.isin(good)].copy()
    if d.empty:
        return d,[]
    d["own_x_rain"]=d.own_prior_strong*d.rain_contrast
    d["generic_x_rain"]=d.generic_other_strong_rate*d.rain_contrast
    for col in ("wet_strong","own_prior_strong","generic_other_strong_rate","own_x_rain","generic_x_rain"):
        d[col+"_w"]=d[col]-d.groupby("pair_species")[col].transform("mean")
    cols=["own_prior_strong_w"]
    for col in ["generic_other_strong_rate_w","own_x_rain_w","generic_x_rain_w"]:
        if float(np.abs(d[col]).sum())>1e-12:
            cols.append(col)
    return d,cols

def fit_one(df,min_groups=20,min_routes=10):
    d,cols=prep_design(df)
    ng=int(d.pair_species.nunique()) if len(d) else 0
    nr=int(d.route_cluster.nunique()) if len(d) else 0
    if ng<min_groups or nr<min_routes:
        return {
            "estimable":False,
            "n_pair_species_groups":ng,
            "n_routes":nr,
            "n_rows":int(len(d)),
        }
    X=d[cols].astype(float)
    fit=sm.OLS(d["wet_strong_w"].astype(float),X).fit(
        cov_type="cluster",cov_kwds={"groups":d.route_cluster}
    )
    b=float(fit.params["own_prior_strong_w"]); se=float(fit.bse["own_prior_strong_w"])
    return {
        "estimable":True,
        "n_pair_species_groups":ng,
        "n_routes":nr,
        "n_rows":int(len(d)),
        "beta":b,
        "se":se,
        "ci95":[b-Q*se,b+Q*se],
        "p":float(fit.pvalues["own_prior_strong_w"]),
        "ci_positive":bool(b>0 and b-Q*se>0),
    }

def fit_pooled(df):
    return fit_one(df,min_groups=1,min_routes=2)

def summarize_species(df):
    results={}
    for sp,g in df.groupby("species",sort=True):
        results[str(sp)]=fit_one(g.copy())
    est=[(sp,x) for sp,x in results.items() if x.get("estimable")]
    bet=np.asarray([x["beta"] for _,x in est],float)
    npos=int(np.sum(bet>0)) if len(bet) else 0
    sign_p=float(binomtest(npos,len(bet),0.5,alternative="greater").pvalue) if len(bet) else None
    return results,{
        "n_estimable_species":int(len(est)),
        "n_positive_species":npos,
        "positive_fraction":float(npos/len(est)) if est else None,
        "n_ci_positive_species":int(sum(x["ci_positive"] for _,x in est)),
        "ci_positive_fraction":float(np.mean([x["ci_positive"] for _,x in est])) if est else None,
        "sign_test_p":sign_p,
        "median_beta":float(np.median(bet)) if len(bet) else None,
        "q25_beta":float(np.quantile(bet,.25)) if len(bet) else None,
        "q75_beta":float(np.quantile(bet,.75)) if len(bet) else None,
        "beta_min":float(np.min(bet)) if len(bet) else None,
        "beta_max":float(np.max(bet)) if len(bet) else None,
    }

def leave_one_species_out(df,species_list):
    out={}
    for sp in species_list:
        x=fit_pooled(df[df.species.astype(str)!=str(sp)].copy())
        out[str(sp)]=x
    vals=[x["beta"] for x in out.values() if x.get("estimable")]
    return out,{
        "n_fits":int(len(vals)),
        "all_positive":bool(vals and all(v>0 for v in vals)),
        "min_beta":float(min(vals)) if vals else None,
        "max_beta":float(max(vals)) if vals else None,
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

    species_results,summary=summarize_species(d)
    estimable_species=[sp for sp,x in species_results.items() if x.get("estimable")]
    loo,loo_summary=leave_one_species_out(d,estimable_species)

    broad=bool(
        summary["n_estimable_species"]>=15
        and summary["sign_test_p"] is not None
        and summary["sign_test_p"]<0.05
        and loo_summary["all_positive"]
    )

    ds=d[d.same_observer].copy()
    same_results,same_summary=summarize_species(ds)
    same_gate=bool(same_summary["n_estimable_species"]>=12)
    same_support=bool(
        same_gate
        and same_summary["sign_test_p"] is not None
        and same_summary["sign_test_p"]<0.05
    )

    out={
        "analysis":"naamp_site_template_taxon_generality_v0_1",
        "contract":"exploration/NAAMP_SITE_TEMPLATE_TAXON_GENERALITY_CONTRACT_V0_1.json",
        "coverage":{
            "physically_stable_pairs":int(len(stable)),
            "candidate_rows":int(len(d)),
            "candidate_species":int(d.species.nunique()) if len(d) else 0,
        },
        "species_specific":species_results,
        "summary":summary,
        "leave_one_species_out":loo,
        "leave_one_species_out_summary":loo_summary,
        "same_observer_sensitivity":{
            "gate_pass":same_gate,
            "species_specific":same_results,
            "summary":same_summary,
            "support":same_support,
        },
        "classification":{
            "broad_taxonomic_template_generality_supported":broad,
            "same_observer_sign_generality_supported":same_support,
        },
        "interpretation_boundary":{
            "every_species_effect_required":False,
            "cross_continental_universality":False,
            "shared_physiological_mechanism_identified":False,
        }
    }
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
