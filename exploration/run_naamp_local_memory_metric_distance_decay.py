#!/usr/bin/env python3
from __future__ import annotations

import csv, hashlib, io, json, math, time, urllib.error, urllib.request
from collections import defaultdict
from pathlib import Path
import importlib.util

import numpy as np
import pandas as pd
import statsmodels.api as sm

ROOT=Path(__file__).resolve().parents[1]
EXP=ROOT/"exploration"
NAAMP=ROOT/"scripts"/"naamp"
OUT=EXP/"NAAMP_LOCAL_MEMORY_METRIC_DISTANCE_DECAY_RECEIPT_V0_1.json"
COORD_URL="https://www.sciencebase.gov/catalog/file/get/583dc314e4b0d1899f9dea8d?f=__disk__77%2F22%2F7e%2F77227ec46ac1c01592cd7d158d442cd8343a7536"
COORD_SHA="f71a87df9fc94e0d6c5d4466b4745c3bbaff874cbe7c28796b3f9eb44c2e6e83"
Q=1.959963984540054

def loadmod(name,path):
    s=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(s)
    assert s.loader
    s.loader.exec_module(m)
    return m

mem=loadmod("mem",EXP/"run_naamp_species_specific_site_memory.py")

def fetch_bytes(url):
    last=None
    for i in range(6):
        try:
            req=urllib.request.Request(url,headers={"User-Agent":"frogcs-memory-distance/0.1"})
            with urllib.request.urlopen(req,timeout=180) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            last=e
            if e.code not in (403,429,500,502,503,504):
                raise
            time.sleep(2*(i+1))
    raise RuntimeError(f"coordinate fetch failed after retries: {last}")

def load_coords():
    raw=fetch_bytes(COORD_URL)
    got=hashlib.sha256(raw).hexdigest()
    if got!=COORD_SHA:
        raise RuntimeError(f"Coordinates hash drift {got}")
    rows=list(csv.DictReader(io.StringIO(raw.decode("utf-8-sig"))))
    out={}
    for r in rows:
        sid=(r.get("SiteID") or "").strip()
        if not sid:
            continue
        xy=(float(r["lat"]),float(r["lon"]))
        if sid in out and out[sid]!=xy:
            raise RuntimeError(f"coordinate conflict {sid}")
        out[sid]=xy
    return out

def hav_km(a,b):
    lat1,lon1=a;lat2,lon2=b
    rr=6371.0088
    p1=math.radians(lat1);p2=math.radians(lat2)
    dp=math.radians(lat2-lat1);dl=math.radians(lon2-lon1)
    h=math.sin(dp/2)**2+math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return 2*rr*math.asin(min(1.0,math.sqrt(h)))

def build_data():
    raw=mem.load_retry()
    runs,sets=mem.base.build_runs(raw)
    eligible=set(runs.RunID.astype(str))
    sampled,_=mem.spatial.stop_matrix(raw,eligible)
    site=mem.site_map(raw,eligible)
    ci=mem.ci_map(raw,eligible,sampled)
    meta,by_stratum=mem.build_history(runs)
    coords=load_coords()

    allpairs=mem.base.pair_runs(runs,sets).copy().reset_index(drop=True)
    stable=allpairs.loc[
        np.asarray([mem.stable_pair(p,sampled,site) for p in allpairs.itertuples(index=False)],bool)
    ].copy().reset_index(drop=True)
    _,same=mem.sameobs.same_observer_pairs(raw,runs,sets)
    same_keys={(str(p.wet_RunID),str(p.dry_RunID)) for p in same.itertuples(index=False)}

    rows=[]
    for pid,p in enumerate(stable.itertuples(index=False)):
        w=str(p.wet_RunID);d=str(p.dry_RunID)
        key=meta[w]["key"]
        cutoff=int(p.year_earlier)
        prior=[rid for rid in by_stratum[key] if meta[rid]["year"]<cutoff]
        if not prior:
            continue

        prior_route_species=set()
        prior_strong_sites=defaultdict(set)
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
                        prior_strong_sites[sp].add(sid)
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
        for sp in focal:
            sources=[sid for sid in prior_strong_sites.get(sp,set()) if sid in coords]
            if not sources:
                continue
            group=f"{pid}|{sp}"
            for st in sorted(sampled[w],key=lambda x:int(float(x))):
                sid=site[(w,st)]
                if sid not in coords:
                    continue
                dist=min(hav_km(coords[sid],coords[src]) for src in sources)
                wet=int(ci.get((w,st),{}).get(sp,0))
                rows.append({
                    "pair_species":group,
                    "pair_id":int(pid),
                    "species":sp,
                    "route_cluster":str(p.route_cluster),
                    "same_observer":bool((w,d) in same_keys),
                    "wet_strong":float(wet>=2),
                    "wet_full":float(wet==3),
                    "nearest_prior_strong_km":float(dist),
                    "other_species_prior_strong_richness":float(len(site_strong_species.get(sid,set())-{sp})),
                    "prior_site_effort":float(site_effort.get(sid,0)),
                })
    return pd.DataFrame(rows),stable

def fit_within(df,outcome):
    d=df.copy()
    # Keep only groups with within-group metric distance variation.
    nu=d.groupby("pair_species")["nearest_prior_strong_km"].nunique()
    good=nu[nu>=2].index
    d=d[d.pair_species.isin(good)].copy()
    if d.empty:
        return None

    d["logdist"]=np.log1p(d.nearest_prior_strong_km.astype(float))
    d["other_log"]=np.log1p(d.other_species_prior_strong_richness.astype(float))
    for col in (outcome,"logdist","other_log","prior_site_effort"):
        d[col+"_w"]=d[col].astype(float)-d.groupby("pair_species")[col].transform("mean").astype(float)

    X=d[["logdist_w","other_log_w","prior_site_effort_w"]].astype(float)
    keep=["logdist_w"]+[c for c in ["other_log_w","prior_site_effort_w"] if float(np.abs(X[c]).sum())>1e-12]
    X=X[keep]
    m=sm.OLS(d[outcome+"_w"].astype(float),X).fit(
        cov_type="cluster",cov_kwds={"groups":d.route_cluster.astype(str)}
    )

    b=float(m.params["logdist_w"]);se=float(m.bse["logdist_w"])
    # A within-group slope translates directly to a difference from distance 0.
    pred5=b*math.log1p(5.0)
    pred10=b*math.log1p(10.0)
    return {
        "outcome":outcome,
        "n_rows":int(len(d)),
        "n_pair_species_groups":int(d.pair_species.nunique()),
        "n_routes":int(d.route_cluster.nunique()),
        "n_species":int(d.species.nunique()),
        "beta_log1p_distance":b,
        "se":se,
        "ci95":[b-Q*se,b+Q*se],
        "p":float(m.pvalues["logdist_w"]),
        "negative_ci":bool(b<0 and b+Q*se<0),
        "predicted_change_0_to_5km":float(pred5),
        "predicted_change_0_to_10km":float(pred10),
        "generic_other_species_beta":float(m.params["other_log_w"]) if "other_log_w" in m.params.index else None,
        "prior_site_effort_beta":float(m.params["prior_site_effort_w"]) if "prior_site_effort_w" in m.params.index else None,
        "distance_descriptive":{
            "median_km":float(d.nearest_prior_strong_km.median()),
            "q90_km":float(d.nearest_prior_strong_km.quantile(.90)),
            "max_km":float(d.nearest_prior_strong_km.max())
        }
    }

def main():
    d,stable=build_data()
    primary=fit_within(d,"wet_strong")
    gate=bool(
        primary is not None
        and primary["n_pair_species_groups"]>=500
        and primary["n_routes"]>=250
        and primary["n_species"]>=20
    )
    out={
      "analysis":"naamp_local_memory_metric_distance_decay_v0_1",
      "contract":"exploration/NAAMP_LOCAL_MEMORY_METRIC_DISTANCE_DECAY_CONTRACT_V0_1.json",
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
    full_chorus=fit_within(d,"wet_full")
    sameobs=d[d.same_observer].copy()
    same_fit=fit_within(sameobs,"wet_strong")
    out.update({
      "response_endpoints_read":True,
      "primary_wet_strong":full,
      "secondary_wet_full":full_chorus,
      "same_observer_sensitivity":same_fit,
      "classification":{
        "metric_distance_decay_supported":bool(full["negative_ci"]),
        "full_chorus_distance_decay_supported":bool(full_chorus and full_chorus["negative_ci"]),
        "same_observer_support":bool(same_fit and same_fit["negative_ci"])
      },
      "interpretation_boundary":{
        "metric_spatial_kernel_identified":True,
        "continuous_occupancy_proven":False,
        "individual_movement_inferred":False,
        "causal_memory_claim":False
      }
    })
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
