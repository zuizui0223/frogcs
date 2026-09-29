#!/usr/bin/env python3
from __future__ import annotations

import importlib.util,json
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

ROOT=Path(__file__).resolve().parents[1]
NAAMP=ROOT/"scripts"/"naamp"
OUT=ROOT/"exploration"/"NAAMP_FULL_CHORUS_SITE_MEMORY_RECEIPT_V0_1.json"
Q=1.959963984540054

def loadmod(name,path):
    s=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(s)
    assert s.loader
    s.loader.exec_module(m)
    return m

base=loadmod("base",NAAMP/"run_naamp_ecological_pulse.py")
spatial=loadmod("spatial",NAAMP/"run_naamp_spatial_taxonomic_activation_decomposition.py")

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
        raise RuntimeError(f"multiple SiteID values: {list(bad)[:10]}")
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
            ci=int(float((r.get("CallingIndex") or "").strip()))
        except Exception:
            continue
        if ci in (1,2,3):
            vals[(rid,st,sp)].append(ci)
    by=defaultdict(dict)
    for (rid,st,sp),vals in vals.items():
        by[(rid,st)][sp]=max(vals)
    return by

def stable_pair(p,sampled,site):
    w=str(p.wet_RunID); d=str(p.dry_RunID)
    ws=set(sampled[w]); ds=set(sampled[d])
    return len(ws)==10 and ws==ds and all(
        site.get((w,st)) is not None and site.get((w,st))==site.get((d,st))
        for st in ws
    )

def build_memory(runs,sampled,site,ci):
    meta={}
    by_stratum=defaultdict(list)
    site_ci=defaultdict(dict)
    route_species=defaultdict(set)
    for r in runs.itertuples(index=False):
        rid=str(r.RunID)
        key=(str(r.State),str(r.RouteNumber),str(r.RunNumber))
        meta[rid]={"key":key,"year":int(r.SurveyYear)}
        by_stratum[key].append(rid)
        for st in sorted(sampled.get(rid,set())):
            sid=site.get((rid,st))
            if sid is None:
                continue
            for sp,val in ci.get((rid,st),{}).items():
                site_ci[(rid,sid)][sp]=max(int(val),int(site_ci[(rid,sid)].get(sp,0)))
                route_species[rid].add(sp)
    for key in by_stratum:
        by_stratum[key]=sorted(by_stratum[key],key=lambda rid:(meta[rid]["year"],rid))
    return meta,by_stratum,site_ci,route_species

def classify_pair(p,sampled,site,ci,meta,by_stratum,site_ci,route_species,prior_only=False):
    w=str(p.wet_RunID); d=str(p.dry_RunID)
    key=meta[w]["key"]
    if prior_only:
        cutoff=int(p.year_earlier)
        other=[rid for rid in by_stratum[key] if meta[rid]["year"]<cutoff]
    else:
        other=[rid for rid in by_stratum[key] if rid not in (w,d)]
    if prior_only and not other:
        return None

    other_route=set()
    same_site_max=defaultdict(dict)
    for rid in other:
        other_route.update(route_species.get(rid,set()))
        for st in sampled.get(rid,set()):
            sid=site.get((rid,st))
            if sid is None: continue
            for sp,val in site_ci.get((rid,sid),{}).items():
                old=same_site_max[sid].get(sp,0)
                if val>old:
                    same_site_max[sid][sp]=int(val)

    full=othercall=routeonly=oneoff=0.0
    total=0.0
    for st in sorted(sampled[w]):
        sid=site.get((w,st))
        wm=ci.get((w,st),{})
        dm=ci.get((d,st),{})
        for sp in set(wm)|set(dm):
            wi=int(wm.get(sp,0)); di=int(dm.get(sp,0))
            if di!=0 or wi!=3:
                continue
            total+=1.0
            prev=int(same_site_max.get(sid,{}).get(sp,0))
            if prev==3:
                full+=1.0
            elif prev in (1,2):
                othercall+=1.0
            elif sp in other_route:
                routeonly+=1.0
            else:
                oneoff+=1.0

    if abs(total-full-othercall-routeonly-oneoff)>1e-12:
        raise RuntimeError("CI3 memory partition identity failed")
    return {
        "new_ci3_count":total,
        "same_site_prior_full_chorus":full,
        "same_site_other_call":othercall,
        "route_only_recurrent":routeonly,
        "one_off_stratum_record":oneoff,
        "same_site_recurrent":full+othercall,
        "any_recurrent":full+othercall+routeonly,
        "memory_runs":float(len(other)),
    }

def fit(d,response):
    form=f"{response} ~ rain_contrast + temp_difference + doy_difference + year_gap + C(State) + C(RunNumber)"
    m=smf.ols(form,data=d).fit(cov_type="cluster",cov_kwds={"groups":d.route_cluster})
    b=float(m.params["rain_contrast"]); se=float(m.bse["rain_contrast"])
    return {
        "beta":b,"se":se,"ci95":[b-Q*se,b+Q*se],
        "p":float(m.pvalues["rain_contrast"]),
        "n_pairs":int(len(d)),"n_routes":int(d.route_cluster.nunique())
    }

def package(d):
    names=[
        "new_ci3_count",
        "same_site_prior_full_chorus",
        "same_site_other_call",
        "route_only_recurrent",
        "one_off_stratum_record",
        "same_site_recurrent",
        "any_recurrent",
    ]
    models={x:fit(d,x) for x in names}
    total=models["new_ci3_count"]["beta"]
    same=models["same_site_recurrent"]["beta"]
    anyr=models["any_recurrent"]["beta"]
    same_share=float(same/total) if abs(total)>1e-12 else None
    any_share=float(anyr/total) if abs(total)>1e-12 else None
    beta_err=float(
        total
        -models["same_site_prior_full_chorus"]["beta"]
        -models["same_site_other_call"]["beta"]
        -models["route_only_recurrent"]["beta"]
        -models["one_off_stratum_record"]["beta"]
    )
    support=bool(
        same>0
        and models["same_site_recurrent"]["ci95"][0]>0
        and same_share is not None
        and same_share>0.5
    )
    return {
        "models":models,
        "same_site_recurrent_share_of_new_ci3_beta":same_share,
        "any_recurrent_share_of_new_ci3_beta":any_share,
        "beta_identity_error":beta_err,
        "classification":{"known_site_full_chorus_reactivation_supported":support},
        "descriptive":{
            "mean_memory_runs":float(d.memory_runs.mean()),
            "median_memory_runs":float(d.memory_runs.median())
        }
    }

def main():
    raw=base.load()
    runs,sets=base.build_runs(raw)
    eligible=set(runs.RunID.astype(str))
    sampled,_=spatial.stop_matrix(raw,eligible)
    site=site_map(raw,eligible)
    ci=ci_map(raw,eligible,sampled)
    pairs_all=base.pair_runs(runs,sets).copy().reset_index(drop=True)
    mask=np.asarray([stable_pair(p,sampled,site) for p in pairs_all.itertuples(index=False)],bool)
    pairs=pairs_all.loc[mask].copy().reset_index(drop=True)

    meta,by_stratum,site_ci,route_species=build_memory(runs,sampled,site,ci)

    rows=[]
    for p in pairs.itertuples(index=False):
        m=classify_pair(p,sampled,site,ci,meta,by_stratum,site_ci,route_species,False)
        r=p._asdict(); r.update(m); rows.append(r)
    d=pd.DataFrame(rows)

    err=np.max(np.abs(
        d.new_ci3_count
        -d.same_site_prior_full_chorus
        -d.same_site_other_call
        -d.route_only_recurrent
        -d.one_off_stratum_record
    ))
    if err>1e-12:
        raise RuntimeError(f"pair identity drift {err}")

    full=package(d)

    prior_rows=[]
    for p in pairs.itertuples(index=False):
        m=classify_pair(p,sampled,site,ci,meta,by_stratum,site_ci,route_species,True)
        if m is None: continue
        r=p._asdict(); r.update(m); prior_rows.append(r)
    prior=pd.DataFrame(prior_rows)
    gate=bool(len(prior)>=1500 and prior.route_cluster.nunique()>=300)
    prior_result=package(prior) if gate else {
        "status":"not_run_due_to_prefixed_gate",
        "n_pairs":int(len(prior)),
        "n_routes":int(prior.route_cluster.nunique()) if len(prior) else 0
    }

    out={
      "analysis":"naamp_full_chorus_site_memory_v0_1",
      "contract":"exploration/NAAMP_FULL_CHORUS_SITE_MEMORY_CONTRACT_V0_1.json",
      "coverage":{
        "all_pairs":int(len(pairs_all)),
        "physically_stable_pairs":int(len(pairs)),
        "stable_fraction":float(len(pairs)/len(pairs_all))
      },
      "leave_pair_out_memory":full,
      "prior_only_sensitivity":{
        "gate_pass":gate,
        "n_pairs":int(len(prior)),
        "n_routes":int(prior.route_cluster.nunique()) if len(prior) else 0,
        "result":prior_result
      },
      "identity_checks":{"max_pair_error":float(err)},
      "interpretation_boundary":{
        "continuous_occupancy_proven":False,
        "reproductive_success_measured":False,
        "recurrent_chorus_site_use_supported_if_gate_passes":True,
        "causal_rainfall_claim":False
      }
    }
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
