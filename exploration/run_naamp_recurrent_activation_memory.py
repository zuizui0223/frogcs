#!/usr/bin/env python3
from __future__ import annotations

import importlib.util, json
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

ROOT=Path(__file__).resolve().parents[1]
NAAMP=ROOT/"scripts"/"naamp"
OUT=ROOT/"exploration"/"NAAMP_RECURRENT_ACTIVATION_MEMORY_RECEIPT_V0_1.json"
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

def stable_pair(p,sampled,site):
    w=str(p.wet_RunID); d=str(p.dry_RunID)
    ws=set(sampled[w]); ds=set(sampled[d])
    if len(ws)!=10 or ws!=ds:
        return False
    return all(
        site.get((w,st)) is not None and site.get((w,st))==site.get((d,st))
        for st in ws
    )

def build_run_memory(runs,sampled,stop_species,site):
    meta={}
    by_stratum=defaultdict(list)
    site_species=defaultdict(set)
    route_species=defaultdict(set)

    for r in runs.itertuples(index=False):
        rid=str(r.RunID)
        key=(str(r.State),str(r.RouteNumber),str(r.RunNumber))
        year=int(r.SurveyYear)
        meta[rid]={"key":key,"year":year}
        by_stratum[key].append(rid)
        for st in sorted(sampled.get(rid,set())):
            sid=site.get((rid,st))
            if sid is None:
                continue
            spp=set(stop_species.get((rid,st),set()))
            site_species[(rid,sid)].update(spp)
            route_species[rid].update(spp)

    for key in by_stratum:
        by_stratum[key]=sorted(by_stratum[key],key=lambda rid:(meta[rid]["year"],rid))
    return meta,by_stratum,site_species,route_species

def classify_pair(p,sampled,stop_species,site,meta,by_stratum,site_species,route_species,prior_only=False):
    w=str(p.wet_RunID); d=str(p.dry_RunID)
    key=meta[w]["key"]
    if meta[d]["key"]!=key:
        raise RuntimeError("stratum mismatch")

    if prior_only:
        cutoff=int(p.year_earlier)
        other=[rid for rid in by_stratum[key] if meta[rid]["year"]<cutoff]
    else:
        other=[rid for rid in by_stratum[key] if rid not in (w,d)]

    if prior_only and len(other)==0:
        return None

    other_route_species=set()
    other_site_species=defaultdict(set)
    for rid in other:
        other_route_species.update(route_species.get(rid,set()))
        for st in sampled.get(rid,set()):
            sid=site.get((rid,st))
            if sid is not None:
                other_site_species[sid].update(site_species.get((rid,sid),set()))

    dry_route=set()
    for st in sampled[d]:
        dry_route.update(stop_species.get((d,st),set()))

    same=route_only=oneoff=0.0
    total=0.0
    route_new_species=set()
    for st in sorted(sampled[w]):
        sid=site.get((w,st))
        if sid is None:
            raise RuntimeError("missing stable site in focal wet run")
        for sp in stop_species.get((w,st),set()):
            if sp in dry_route:
                continue
            route_new_species.add(sp)
            total+=1.0
            if sp in other_site_species.get(sid,set()):
                same+=1.0
            elif sp in other_route_species:
                route_only+=1.0
            else:
                oneoff+=1.0

    if abs(total-same-route_only-oneoff)>1e-12:
        raise RuntimeError("memory partition identity failed")

    return {
        "route_new_wet_incidence":total,
        "same_site_recurrent":same,
        "route_only_recurrent":route_only,
        "one_off_stratum_record":oneoff,
        "recurrent_sum":same+route_only,
        "route_new_species_count":float(len(route_new_species)),
        "memory_runs":float(len(other)),
    }

def fit(d,response):
    x=d[np.isfinite(pd.to_numeric(d[response],errors="coerce"))].copy()
    form=f"{response} ~ rain_contrast + temp_difference + doy_difference + year_gap + C(State) + C(RunNumber)"
    m=smf.ols(form,data=x).fit(cov_type="cluster",cov_kwds={"groups":x.route_cluster})
    b=float(m.params["rain_contrast"]); se=float(m.bse["rain_contrast"])
    return {
        "beta":b,"se":se,"ci95":[b-Q*se,b+Q*se],
        "p":float(m.pvalues["rain_contrast"]),
        "n_pairs":int(len(x)),"n_routes":int(x.route_cluster.nunique())
    }

def package(d):
    names=[
        "route_new_wet_incidence",
        "same_site_recurrent",
        "route_only_recurrent",
        "one_off_stratum_record",
        "recurrent_sum",
        "route_new_species_count",
    ]
    models={x:fit(d,x) for x in names}
    total=models["route_new_wet_incidence"]["beta"]
    recur=models["recurrent_sum"]["beta"]
    share=float(recur/total) if abs(total)>1e-12 else None
    beta_err=float(
        total
        -models["same_site_recurrent"]["beta"]
        -models["route_only_recurrent"]["beta"]
        -models["one_off_stratum_record"]["beta"]
    )
    support=bool(
        recur>0
        and models["recurrent_sum"]["ci95"][0]>0
        and share is not None
        and share>0.5
    )
    return {
        "models":models,
        "recurrent_share_of_total_route_new_incidence_beta":share,
        "beta_identity_error":beta_err,
        "classification":{"recurrent_activation_supported":support},
        "descriptive":{
            "mean_memory_runs":float(d.memory_runs.mean()),
            "median_memory_runs":float(d.memory_runs.median()),
        }
    }

def main():
    raw=base.load()
    runs,sets=base.build_runs(raw)
    eligible=set(runs.RunID.astype(str))
    sampled,stop_species=spatial.stop_matrix(raw,eligible)
    site=site_map(raw,eligible)

    allpairs=base.pair_runs(runs,sets).copy().reset_index(drop=True)
    stable_mask=np.asarray([stable_pair(p,sampled,site) for p in allpairs.itertuples(index=False)],bool)
    pairs=allpairs.loc[stable_mask].copy().reset_index(drop=True)

    meta,by_stratum,site_species,route_species=build_run_memory(
        runs,sampled,stop_species,site
    )

    rows=[]
    for p in pairs.itertuples(index=False):
        m=classify_pair(
            p,sampled,stop_species,site,meta,by_stratum,site_species,route_species,
            prior_only=False
        )
        r=p._asdict(); r.update(m); rows.append(r)
    d=pd.DataFrame(rows)

    pair_err=float(np.max(np.abs(
        d.route_new_wet_incidence
        -d.same_site_recurrent
        -d.route_only_recurrent
        -d.one_off_stratum_record
    )))
    if pair_err>1e-12:
        raise RuntimeError(f"leave-pair-out identity drift {pair_err}")

    full=package(d)

    prior_rows=[]
    for p in pairs.itertuples(index=False):
        m=classify_pair(
            p,sampled,stop_species,site,meta,by_stratum,site_species,route_species,
            prior_only=True
        )
        if m is None:
            continue
        r=p._asdict(); r.update(m); prior_rows.append(r)
    prior=pd.DataFrame(prior_rows)
    prior_gate=bool(
        len(prior)>=1500
        and prior.route_cluster.nunique()>=300
    )
    prior_pkg=package(prior) if prior_gate else {
        "status":"not_run_due_to_prefixed_gate",
        "n_pairs":int(len(prior)),
        "n_routes":int(prior.route_cluster.nunique()) if len(prior) else 0
    }

    out={
      "analysis":"naamp_recurrent_activation_memory_v0_1",
      "contract":"exploration/NAAMP_RECURRENT_ACTIVATION_MEMORY_CONTRACT_V0_1.json",
      "coverage":{
        "all_pairs":int(len(allpairs)),
        "physically_stable_pairs":int(len(pairs)),
        "stable_fraction":float(len(pairs)/len(allpairs)),
      },
      "leave_pair_out_memory":full,
      "prior_only_sensitivity":{
        "gate_pass":prior_gate,
        "n_pairs":int(len(prior)),
        "n_routes":int(prior.route_cluster.nunique()) if len(prior) else 0,
        "result":prior_pkg
      },
      "identity_checks":{"max_pair_error":pair_err},
      "interpretation_boundary":{
        "continuous_occupancy_proven":False,
        "literal_colonization_tested":False,
        "acoustic_reactivation_interpretation":True,
        "causal_rainfall_claim":False
      }
    }
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
