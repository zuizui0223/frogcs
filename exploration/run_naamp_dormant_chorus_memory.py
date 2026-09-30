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
OUT=ROOT/"exploration"/"NAAMP_DORMANT_CHORUS_MEMORY_RECEIPT_V0_1.json"
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

def build_meta(runs):
    meta={}
    by=defaultdict(list)
    for r in runs.itertuples(index=False):
        rid=str(r.RunID)
        key=(str(r.State),str(r.RouteNumber),str(r.RunNumber))
        meta[rid]={"key":key,"year":int(r.SurveyYear)}
        by[key].append(rid)
    for k in by:
        by[k]=sorted(by[k],key=lambda rid:(meta[rid]["year"],rid))
    return meta,by

def pair_rows(pid,p,sampled,site,ci,meta,by,same_observer):
    w=str(p.wet_RunID); d=str(p.dry_RunID)
    key=meta[w]["key"]
    cutoff=int(p.year_earlier)
    prior=[rid for rid in by[key] if meta[rid]["year"]<cutoff]
    if not prior:
        return []

    prior_route_species=set()
    # sid -> sp -> list[(year, ci)] for every prior run that sampled sid
    site_history=defaultdict(lambda: defaultdict(list))
    site_effort=defaultdict(int)
    site_strong_species=defaultdict(set)

    for rid in prior:
        year=meta[rid]["year"]
        sampled_sids={}
        for st in sampled.get(rid,set()):
            sid=site.get((rid,st))
            if sid is None:
                continue
            sampled_sids[sid]=st
            site_effort[sid]+=1
            for sp,x in ci.get((rid,st),{}).items():
                if x>0:
                    prior_route_species.add(sp)
                if x>=2:
                    site_strong_species[sid].add(sp)
        # For every species in prior route pool so far, explicit zeros are not
        # materialized here. Instead queried focal species get 0 for sampled runs
        # where absent below.
        for sid,st in sampled_sids.items():
            # record positive calls now; zeros are filled for focal species later
            for sp,x in ci.get((rid,st),{}).items():
                site_history[sid][sp].append((year,int(x)))

    dry_route=set()
    wet_route=set()
    for st in sampled[d]:
        dry_route.update(ci.get((d,st),{}))
    for st in sampled[w]:
        wet_route.update(ci.get((w,st),{}))
    focal=sorted((wet_route-dry_route)&prior_route_species)

    # Cache prior sampling years per current SiteID regardless of species.
    prior_sample_years=defaultdict(list)
    prior_sid_to_st_by_run={}
    for rid in prior:
        for st in sampled.get(rid,set()):
            sid=site.get((rid,st))
            if sid is not None:
                prior_sample_years[sid].append((meta[rid]["year"],rid,st))
    for sid in prior_sample_years:
        prior_sample_years[sid].sort()

    rows=[]
    for sp in focal:
        group=f"{pid}|{sp}"
        for st in sorted(sampled[w],key=lambda x:int(float(x))):
            sid=site[(w,st)]
            wet=int(ci.get((w,st),{}).get(sp,0))
            sequence=[]
            for year,rid,pst in prior_sample_years.get(sid,[]):
                val=int(ci.get((rid,pst),{}).get(sp,0))
                sequence.append((year,val))

            strong_idx=[i for i,(_,x) in enumerate(sequence) if x>=2]
            any_strong=bool(strong_idx)
            latest_val=sequence[-1][1] if sequence else None
            dormant=False
            active=False
            silent_after_last=0
            if any_strong:
                last_i=max(strong_idx)
                after=sequence[last_i+1:]
                silent_after_last=sum(1 for _,x in after if x==0)
                dormant=bool(after and silent_after_last>=1 and latest_val==0)
                active=bool(latest_val is not None and latest_val>0)

            never_strong=not any_strong
            if dormant:
                cat="dormant_memory"
            elif active:
                cat="active_memory"
            elif never_strong:
                cat="never_strong"
            else:
                # Prior strong exists, but latest sampled state is zero without
                # satisfying the explicit post-strong sequence guard; keep out
                # of the three prespecified comparison classes.
                cat="other_history"

            rows.append({
                "pair_species":group,
                "pair_id":int(pid),
                "species":sp,
                "route_cluster":str(p.route_cluster),
                "same_observer":bool(same_observer),
                "SiteID":sid,
                "wet_strong":float(wet>=2),
                "wet_full":float(wet==3),
                "dormant_memory":float(cat=="dormant_memory"),
                "active_memory":float(cat=="active_memory"),
                "never_strong":float(cat=="never_strong"),
                "other_history":float(cat=="other_history"),
                "silent_prior_surveys_after_last_strong":float(silent_after_last),
                "other_species_prior_strong_richness":float(len(site_strong_species.get(sid,set())-{sp})),
                "prior_site_effort":float(site_effort.get(sid,0)),
            })
    return rows

def fit_pairwise(df,outcome,left,right):
    d=df.copy()
    sums=d.groupby("pair_species")[[left,right]].sum()
    good=sums[(sums[left]>0)&(sums[right]>0)].index
    d=d[d.pair_species.isin(good) & ((d[left]==1)|(d[right]==1))].copy()
    if d.empty:
        return None
    d["left_indicator"]=d[left].astype(float)
    d["other_log"]=np.log1p(d.other_species_prior_strong_richness.astype(float))
    for col in (outcome,"left_indicator","other_log","prior_site_effort"):
        d[col+"_w"]=d[col].astype(float)-d.groupby("pair_species")[col].transform("mean").astype(float)
    X=d[["left_indicator_w","other_log_w","prior_site_effort_w"]].astype(float)
    keep=["left_indicator_w"]+[c for c in ["other_log_w","prior_site_effort_w"] if float(np.abs(X[c]).sum())>1e-12]
    X=X[keep]
    m=sm.OLS(d[outcome+"_w"].astype(float),X).fit(
        cov_type="cluster",cov_kwds={"groups":d.route_cluster.astype(str)}
    )
    b=float(m.params["left_indicator_w"]);se=float(m.bse["left_indicator_w"])
    return {
        "outcome":outcome,
        "left_class":left,
        "right_reference":right,
        "n_rows":int(len(d)),
        "n_pair_species_groups":int(d.pair_species.nunique()),
        "n_routes":int(d.route_cluster.nunique()),
        "n_species":int(d.species.nunique()),
        "beta":b,
        "se":se,
        "ci95":[b-Q*se,b+Q*se],
        "p":float(m.pvalues["left_indicator_w"]),
        "positive_ci":bool(b>0 and b-Q*se>0),
        "median_silent_surveys_after_last_strong":float(
            d.loc[d[left]==1,"silent_prior_surveys_after_last_strong"].median()
        ) if left=="dormant_memory" else None,
    }

def main():
    raw=load_retry()
    runs,sets=base.build_runs(raw)
    eligible=set(runs.RunID.astype(str))
    sampled,_=spatial.stop_matrix(raw,eligible)
    site=site_map(raw,eligible)
    ci=ci_map(raw,eligible,sampled)
    meta,by=build_meta(runs)

    allpairs=base.pair_runs(runs,sets).copy().reset_index(drop=True)
    stable=allpairs.loc[
        np.asarray([stable_pair(p,sampled,site) for p in allpairs.itertuples(index=False)],bool)
    ].copy().reset_index(drop=True)
    _,same=sameobs.same_observer_pairs(raw,runs,sets)
    same_keys={(str(p.wet_RunID),str(p.dry_RunID)) for p in same.itertuples(index=False)}

    rows=[]
    for pid,p in enumerate(stable.itertuples(index=False)):
        rows.extend(pair_rows(
            pid,p,sampled,site,ci,meta,by,
            (str(p.wet_RunID),str(p.dry_RunID)) in same_keys
        ))
    d=pd.DataFrame(rows)

    primary=fit_pairwise(d,"wet_strong","dormant_memory","never_strong")
    gate=bool(
        primary is not None
        and primary["n_pair_species_groups"]>=300
        and primary["n_routes"]>=200
        and primary["n_species"]>=20
    )
    out={
      "analysis":"naamp_dormant_chorus_memory_v0_1",
      "contract":"exploration/NAAMP_DORMANT_CHORUS_MEMORY_CONTRACT_V0_1.json",
      "coverage":{
        "physically_stable_pairs":int(len(stable)),
        "candidate_rows":int(len(d)),
        "candidate_groups":int(d.pair_species.nunique()) if len(d) else 0,
        "candidate_species":int(d.species.nunique()) if len(d) else 0,
        "dormant_rows":int((d.dormant_memory==1).sum()) if len(d) else 0,
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
    full_chorus=fit_pairwise(d,"wet_full","dormant_memory","never_strong")
    dormant_vs_active=fit_pairwise(d,"wet_strong","dormant_memory","active_memory")
    ds=d[d.same_observer].copy()
    same_fit=fit_pairwise(ds,"wet_strong","dormant_memory","never_strong")

    out.update({
      "response_endpoints_read":True,
      "primary_dormant_vs_never_wet_strong":full,
      "secondary_dormant_vs_never_wet_full":full_chorus,
      "descriptive_dormant_vs_active_wet_strong":dormant_vs_active,
      "same_observer_sensitivity":same_fit,
      "classification":{
        "reactivation_after_observed_silence_supported":bool(full["positive_ci"]),
        "full_chorus_after_observed_silence_supported":bool(full_chorus and full_chorus["positive_ci"]),
        "same_observer_support":bool(same_fit and same_fit["positive_ci"])
      },
      "interpretation_boundary":{
        "intervening_acoustic_silence_observed":True,
        "demographic_absence_proven":False,
        "continuous_occupancy_excluded":False,
        "biological_memory_proven":False,
        "causal_rainfall_claim":False
      }
    })
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
