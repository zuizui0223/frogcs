#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import importlib.util
import io
import json
import math
import urllib.request
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT=Path(__file__).resolve().parents[1]
NAAMP=ROOT/"scripts"/"naamp"
OUT=ROOT/"exploration"/"NAAMP_PHYSICAL_STOP_IDENTITY_AUDIT_RECEIPT_V0_1.json"
COORD_URL="https://www.sciencebase.gov/catalog/file/get/583dc314e4b0d1899f9dea8d?f=__disk__77%2F22%2F7e%2F77227ec46ac1c01592cd7d158d442cd8343a7536"
COORD_SHA="f71a87df9fc94e0d6c5d4466b4745c3bbaff874cbe7c28796b3f9eb44c2e6e83"
B=1000
SEED=2840223


def loadmod(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    mod=importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(mod)
    return mod


base=loadmod("pulse_base",NAAMP/"run_naamp_ecological_pulse.py")
spatial=loadmod("spatial_base",NAAMP/"run_naamp_spatial_taxonomic_activation_decomposition.py")
uniform=loadmod("uniform_base",NAAMP/"run_naamp_uniform_activation_null.py")
persistence=loadmod("persistence_base",NAAMP/"run_naamp_persistence_preserving_null.py")


def fetch_bytes(url):
    req=urllib.request.Request(url,headers={"User-Agent":"frogcs-physical-stop-audit/0.1"})
    with urllib.request.urlopen(req,timeout=180) as r:
        return r.read()


def coordinates():
    raw=fetch_bytes(COORD_URL)
    got=hashlib.sha256(raw).hexdigest()
    if got!=COORD_SHA:
        raise RuntimeError(f"Coordinates.csv hash drift: {got}")
    rows=list(csv.DictReader(io.StringIO(raw.decode("utf-8-sig"))))
    out={}
    duplicate=[]
    for r in rows:
        sid=(r.get("SiteID") or "").strip()
        if not sid:
            continue
        lat=float(r["lat"]); lon=float(r["lon"])
        if sid in out and out[sid]!=(lat,lon):
            duplicate.append(sid)
        out[sid]=(lat,lon)
    if duplicate:
        raise RuntimeError(f"SiteID coordinate conflicts: {duplicate[:10]}")
    return out,got,len(rows)


def haversine_m(a,b):
    lat1,lon1=a; lat2,lon2=b
    r=6371008.8
    p1=math.radians(lat1); p2=math.radians(lat2)
    dp=math.radians(lat2-lat1); dl=math.radians(lon2-lon1)
    h=math.sin(dp/2)**2+math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return 2*r*math.asin(min(1.0,math.sqrt(h)))


def site_map(raw, eligible):
    vals=defaultdict(set)
    for s in raw["Stops.csv"]:
        rid=(s.get("RunID") or "").strip()
        st=(s.get("StopNumber") or "").strip()
        sid=(s.get("SiteID") or "").strip()
        if rid not in eligible or not st:
            continue
        if (s.get("SkippedStop") or "").strip()!="0":
            continue
        if sid:
            vals[(rid,st)].add(sid)
    conflict={k:sorted(v) for k,v in vals.items() if len(v)>1}
    if conflict:
        raise RuntimeError(f"multiple SiteID values per run-stop: {list(conflict.items())[:10]}")
    return {k:next(iter(v)) for k,v in vals.items() if v}


def subset_nulls(pairs,pair_data,keep,pools,dry_ids,ss):
    idx=np.flatnonzero(np.asarray(keep,bool))
    psub=pairs.iloc[idx].copy().reset_index(drop=True)
    dsub=[pair_data[int(i)] for i in idx]
    comps=np.asarray([uniform.component_counts(d["wet"],d["dry"]) for d in dsub],float)
    r,den=uniform.design_residual(psub)
    obs=(r[:,None]*comps).sum(axis=0)/den
    obs_shares=obs/float(obs.sum())
    observed_boundary=float(1-obs_shares[3])

    # Restrict historical-null dictionaries to strata represented in the
    # stable physical-site subset; null_for_kappa otherwise asks for stop
    # layouts belonging to excluded strata.
    keys={d["key"] for d in dsub}
    pools_sub={k:pools[k] for k in keys}
    dry_ids_sub=defaultdict(set)
    for p in psub.itertuples(index=False):
        key=(str(p.State),str(p.RouteNumber),str(p.RunNumber))
        dry_ids_sub[key].add(str(p.dry_RunID))

    # Primary uniform comparator. Sørensen is not part of this audit.
    un=uniform.null_for_kappa(
        2.0,psub,dsub,pools_sub,dry_ids_sub,ss,r,den,obs,
        np.zeros(len(psub),dtype=bool),np.asarray([],float),1.0,0.0,
        simulate_sorensen=False,
    )

    stops_by_key={d["key"]:d["stops"] for d in dsub}
    hist=persistence.historical_cell_probs(pools_sub,dry_ids_sub,stops_by_key,ss)
    pn=persistence.null_for_anchor(0.75,dsub,hist,r,den,obs)

    names=["corner_expansion","spatial_spread","taxonomic_deepening","within_core_rearrangement"]
    return {
        "n_pairs":int(len(psub)),
        "n_routes":int(psub["route_cluster"].nunique()),
        "observed_component_betas":{names[i]:float(obs[i]) for i in range(4)},
        "observed_component_shares":{names[i]:float(obs_shares[i]) for i in range(4)},
        "observed_boundary_share":observed_boundary,
        "uniform_kappa2":{
            "p":float(un["primary_omnibus"]["monte_carlo_p"]),
            "boundary_null_mean":float(un["boundary_crossing_share"]["null_mean"]),
            "boundary_null_ci95":un["boundary_crossing_share"]["null_ci95"],
        },
        "persistence_anchor_0_75":{
            "p":float(pn["primary_omnibus"]["monte_carlo_p"]),
            "boundary_null_mean":float(pn["boundary_crossing_share"]["null_mean"]),
            "boundary_null_ci95":pn["boundary_crossing_share"]["null_ci95"],
        },
    }


def main():
    raw=base.load()
    runs,route_sets=base.build_runs(raw)
    eligible=set(runs["RunID"].astype(str))
    site=site_map(raw,eligible)
    coords,coord_sha,coord_rows=coordinates()

    (
        pairs,pair_data,pools,dry_ids,sampled,ss,r_all,den_all,obs_betas,
        beta_mask,r_beta,den_beta,obs_sor
    )=uniform.prepare()
    pairs=pairs.copy().reset_index(drop=True)

    pair_audit=[]
    stable=[]
    mismatch_dist=[]
    missing_siteid_pairs=0
    missing_coord_pairs=0
    mismatched_pairs=0
    mismatched_cells=0

    for p in pairs.itertuples(index=False):
        wet=str(p.wet_RunID); dry=str(p.dry_RunID)
        stops=sorted(sampled[wet])
        rec=[]
        pair_stable=True
        any_missing_sid=False
        any_missing_coord=False
        for st in stops:
            ws=site.get((wet,st)); ds=site.get((dry,st))
            same=(ws is not None and ds is not None and ws==ds)
            dist=None
            if ws is None or ds is None:
                any_missing_sid=True
                pair_stable=False
            elif not same:
                pair_stable=False
                mismatched_cells+=1
                if ws in coords and ds in coords:
                    dist=haversine_m(coords[ws],coords[ds])
                    mismatch_dist.append(dist)
                else:
                    any_missing_coord=True
            rec.append({"stop":st,"wet_siteid":ws,"dry_siteid":ds,"same_siteid":same,"displacement_m":dist})
        if any_missing_sid:
            missing_siteid_pairs+=1
        if any_missing_coord:
            missing_coord_pairs+=1
        if not pair_stable and not any_missing_sid:
            mismatched_pairs+=1
        stable.append(pair_stable)
        if not pair_stable:
            pair_audit.append({
                "State":str(p.State),"RouteNumber":str(p.RouteNumber),"RunNumber":str(p.RunNumber),
                "wet_RunID":wet,"dry_RunID":dry,
                "year_earlier":int(p.year_earlier),"year_later":int(p.year_later),
                "stops":rec,
            })

    stable=np.asarray(stable,bool)
    sensitivity=subset_nulls(pairs,pair_data,stable,pools,dry_ids,ss)

    dist_arr=np.asarray(mismatch_dist,float)
    output={
        "analysis":"naamp_physical_stop_identity_audit_v0_1",
        "submission_authority":"015a675324800f2e5ac9ab0985b080fe88adc375",
        "coordinates":{"sha256":coord_sha,"rows":coord_rows,"mapped_siteids":len(coords)},
        "population":{"pairs":int(len(pairs)),"routes":int(pairs["route_cluster"].nunique())},
        "identity":{
            "stable_same_siteid_pairs":int(stable.sum()),
            "stable_fraction":float(stable.mean()),
            "pairs_with_any_siteid_problem":int((~stable).sum()),
            "mismatched_complete_siteid_pairs":int(mismatched_pairs),
            "pairs_missing_siteid":int(missing_siteid_pairs),
            "mismatched_stop_cells":int(mismatched_cells),
            "mismatch_displacement_m":{
                "n_with_coordinates":int(len(dist_arr)),
                "median":float(np.median(dist_arr)) if len(dist_arr) else None,
                "q95":float(np.quantile(dist_arr,.95)) if len(dist_arr) else None,
                "max":float(np.max(dist_arr)) if len(dist_arr) else None,
            },
        },
        "stable_siteid_sensitivity":sensitivity,
        "mismatched_pair_examples":pair_audit[:25],
        "interpretation":{
            "pass_rule":"Physical-stop robustness is strong if >=95% of matched pairs preserve all ten SiteIDs and the stable-pair subset retains >90% observed boundary crossing with omnibus P<0.05 under both primary nulls.",
            "strong_pass":bool(
                stable.mean()>=.95
                and sensitivity["observed_boundary_share"]>.90
                and sensitivity["uniform_kappa2"]["p"]<.05
                and sensitivity["persistence_anchor_0_75"]["p"]<.05
            ),
            "boundary":"SiteID equality audits physical listening-station identity; it does not prove unchanged wetland habitat through time."
        }
    }
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(output,indent=2,sort_keys=True)+"\n")
    print(json.dumps(output,indent=2,sort_keys=True))


if __name__=="__main__":
    main()
