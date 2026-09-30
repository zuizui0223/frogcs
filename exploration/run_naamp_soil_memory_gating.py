#!/usr/bin/env python3
from __future__ import annotations

import importlib.util, json
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm

ROOT=Path(__file__).resolve().parents[1]
EXP=ROOT/"exploration"
NAAMP=ROOT/"scripts"/"naamp"
OUT=EXP/"NAAMP_SOIL_MEMORY_GATING_RECEIPT_V0_1.json"
Q=1.959963984540054

def loadmod(name,path):
    s=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(s)
    assert s.loader
    s.loader.exec_module(m)
    return m

soil=loadmod("soil",EXP/"run_naamp_soil_moisture_cue.py")
hydric=soil.hydric
base=hydric.base
spatial=hydric.spatial
sameobs=hydric.sameobs

def build_history(runs):
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

def pair_rows(pid,p,sampled,site,ci,meta,by_stratum,soil1z,soil2z,same_observer):
    w=str(p.wet_RunID); d=str(p.dry_RunID)
    key=meta[w]["key"]
    cutoff=int(p.year_earlier)
    prior=[rid for rid in by_stratum[key] if meta[rid]["year"]<cutoff]
    if not prior:
        return []

    prior_route=set()
    prior_site_strong=defaultdict(set)
    for rid in prior:
        for st in sampled.get(rid,set()):
            sid=site.get((rid,st))
            if sid is None:
                continue
            for sp,x in ci.get((rid,st),{}).items():
                if x>0:
                    prior_route.add(sp)
                if x>=2:
                    prior_site_strong[sid].add(sp)

    dry_route=set()
    wet_route=set()
    for st in sampled[d]:
        dry_route.update(ci.get((d,st),{}))
    for st in sampled[w]:
        wet_route.update(ci.get((w,st),{}))

    focal=sorted((wet_route-dry_route)&prior_route)
    rows=[]
    for sp in focal:
        group=f"{pid}|{sp}"
        for st in sorted(sampled[w]):
            sid=site[(w,st)]
            wet=int(ci.get((w,st),{}).get(sp,0))
            mem=float(sp in prior_site_strong.get(sid,set()))
            rows.append({
                "pair_id":int(pid),
                "pair_species":group,
                "species":sp,
                "route_cluster":str(p.route_cluster),
                "same_observer":bool(same_observer),
                "prior_site_strong":mem,
                "soil1_gain_z":float(soil1z),
                "soil2_gain_z":float(soil2z),
                "wet_strong":float(wet>=2),
                "wet_full":float(wet==3),
            })
    return rows

def fit(df,outcome,soil_col):
    d=df.copy()
    informative=d.groupby("pair_species")["prior_site_strong"].nunique()
    good=informative[informative>=2].index
    d=d[d.pair_species.isin(good)].copy()
    if d.empty:
        return None

    d["y_w"]=d[outcome]-d.groupby("pair_species")[outcome].transform("mean")
    d["m_w"]=d.prior_site_strong-d.groupby("pair_species").prior_site_strong.transform("mean")
    d["mx"]=d.prior_site_strong*d[soil_col]
    d["mx_w"]=d.mx-d.groupby("pair_species").mx.transform("mean")

    X=d[["m_w","mx_w"]].astype(float)
    m=sm.OLS(d.y_w.astype(float),X).fit(cov_type="cluster",cov_kwds={"groups":d.route_cluster})
    bm=float(m.params["m_w"]); sem=float(m.bse["m_w"])
    bi=float(m.params["mx_w"]); sei=float(m.bse["mx_w"])
    return {
        "outcome":outcome,
        "soil_gate":soil_col,
        "n_rows":int(len(d)),
        "n_pair_species_groups":int(d.pair_species.nunique()),
        "n_routes":int(d.route_cluster.nunique()),
        "n_species":int(d.species.nunique()),
        "memory_beta":bm,
        "memory_ci95":[bm-Q*sem,bm+Q*sem],
        "memory_p":float(m.pvalues["m_w"]),
        "soil_x_memory_beta":bi,
        "soil_x_memory_se":sei,
        "soil_x_memory_ci95":[bi-Q*sei,bi+Q*sei],
        "soil_x_memory_p":float(m.pvalues["mx_w"]),
        "interaction_positive_ci":bool(bi>0 and bi-Q*sei>0),
    }

def main():
    raw=hydric.retry(base.load,"NAAMP load")
    runs,sets=base.build_runs(raw)
    eligible=set(runs.RunID.astype(str))
    sampled,_=spatial.stop_matrix(raw,eligible)
    site=hydric.site_map(raw,eligible)
    ci=hydric.build_ci(raw,eligible,sampled)
    meta,by_stratum=build_history(runs)

    mid=hydric.build_midpoints(raw,runs)
    weather,audit=soil.extract(mid)

    pairs=base.pair_runs(runs,sets).copy().reset_index(drop=True)
    _,same=sameobs.same_observer_pairs(raw,runs,sets)
    same_keys={(str(p.wet_RunID),str(p.dry_RunID)) for p in same.itertuples(index=False)}

    qualified=[]
    for pid,p in enumerate(pairs.itertuples(index=False)):
        w=str(p.wet_RunID); d=str(p.dry_RunID)
        if w not in weather or d not in weather:
            continue
        if not hydric.stable_pair(p,sampled,site):
            continue
        qualified.append({
            "pid":pid,
            "soil1":float(weather[w]["swvl1"]-weather[d]["swvl1"]),
            "soil2":float(weather[w]["swvl2"]-weather[d]["swvl2"]),
            "rain72":float(np.log1p(weather[w]["rain72_mm"])-np.log1p(weather[d]["rain72_mm"])),
        })
    q=pd.DataFrame(qualified)
    if len(q)<3500:
        raise RuntimeError(f"qualified pair coverage too low {len(q)}")
    q["soil1_z"],m1,s1=hydric.zscore(q.soil1)
    q["soil2_z"],m2,s2=hydric.zscore(q.soil2)
    q["rain72_z"],mr,sr=hydric.zscore(q.rain72)
    qmap=q.set_index("pid").to_dict("index")

    rows=[]
    for pid,p in enumerate(pairs.itertuples(index=False)):
        if pid not in qmap:
            continue
        z=qmap[pid]
        rows.extend(pair_rows(
            pid,p,sampled,site,ci,meta,by_stratum,
            z["soil1_z"],z["soil2_z"],
            (str(p.wet_RunID),str(p.dry_RunID)) in same_keys,
        ))
    d=pd.DataFrame(rows)

    primary=fit(d,"wet_strong","soil1_gain_z")
    gate=bool(primary and primary["n_pair_species_groups"]>=750 and primary["n_routes"]>=250 and primary["n_species"]>=20)

    out={
        "analysis":"naamp_soil_moisture_local_memory_gating_v0_1",
        "contract":"exploration/NAAMP_SOIL_MEMORY_GATING_CONTRACT_V0_1.json",
        "coverage":{
            "weather_physical_pairs":int(len(q)),
            "candidate_rows":int(len(d)),
            "candidate_pair_species":int(d.pair_species.nunique()) if len(d) else 0,
            "candidate_species":int(d.species.nunique()) if len(d) else 0,
            "primary_gate_pass":gate,
        },
        "weather_audit":audit,
        "standardization":{
            "soil1_gain_mean":m1,"soil1_gain_sd":s1,
            "soil2_gain_mean":m2,"soil2_gain_sd":s2,
            "rain72_mean":mr,"rain72_sd":sr,
            "soil1_rain72_correlation":float(np.corrcoef(q.soil1,q.rain72)[0,1]),
        },
        "response_endpoints_read":False,
    }
    if not gate:
        out["primary_precheck"]=primary
        OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
        print(json.dumps(out,indent=2,sort_keys=True))
        return

    full=primary
    full_chorus=fit(d,"wet_full","soil1_gain_z")
    soil2fit=fit(d,"wet_strong","soil2_gain_z")
    ds=d[d.same_observer].copy()
    samefit=fit(ds,"wet_strong","soil1_gain_z")

    out.update({
        "response_endpoints_read":True,
        "primary_wet_strong_swvl1_gate":full,
        "secondary_wet_full_swvl1_gate":full_chorus,
        "secondary_wet_strong_swvl2_gate":soil2fit,
        "same_observer_sensitivity":samefit,
        "classification":{
            "soil_moisture_releases_local_memory":bool(full["interaction_positive_ci"]),
            "full_chorus_support":bool(full_chorus and full_chorus["interaction_positive_ci"]),
            "same_observer_support":bool(samefit and samefit["interaction_positive_ci"]),
        },
        "interpretation_boundary":{
            "soil_water_is_body_hydration":False,
            "soil_water_is_pond_depth":False,
            "continuous_occupancy_proven":False,
            "causal_mediation_established":False,
        }
    })
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
