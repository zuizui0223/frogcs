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
OUT=ROOT/"exploration"/"NAAMP_RAIN_SELECTIVE_LOCAL_MEMORY_RECEIPT_V0_1.json"
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

def direction_endpoint(target,reference,stops,site,ci,prior_route_species,prior_strong):
    target_route=set()
    reference_route=set()
    for st in stops:
        target_route.update(ci.get((target,st),{}))
        reference_route.update(ci.get((reference,st),{}))

    focal=sorted((target_route-reference_route)&prior_route_species)
    if not focal:
        return None

    n_rec=n_non=0
    ci3_rec=ci3_non=0
    ci2_rec=ci2_non=0
    for sp in focal:
        for st in stops:
            sid=site[(target,st)]
            memory=sp in prior_strong.get(sid,set())
            val=int(ci.get((target,st),{}).get(sp,0))
            if memory:
                n_rec+=1
                ci3_rec+=int(val==3)
                ci2_rec+=int(val>=2)
            else:
                n_non+=1
                ci3_non+=int(val==3)
                ci2_non+=int(val>=2)

    if n_rec<=0 or n_non<=0:
        return None

    return {
        "n_focal_species":int(len(focal)),
        "recurrent_candidates":int(n_rec),
        "nonrecurrent_candidates":int(n_non),
        "ci3_rate_difference":float(ci3_rec/n_rec-ci3_non/n_non),
        "ci2plus_rate_difference":float(ci2_rec/n_rec-ci2_non/n_non),
        "ci3_recurrent_rate":float(ci3_rec/n_rec),
        "ci3_nonrecurrent_rate":float(ci3_non/n_non),
        "ci2plus_recurrent_rate":float(ci2_rec/n_rec),
        "ci2plus_nonrecurrent_rate":float(ci2_non/n_non),
    }

def pair_direction_rows(pid,p,sampled,site,ci,meta,by_stratum,same_observer):
    w=str(p.wet_RunID); d=str(p.dry_RunID)
    key=meta[w]["key"]
    cutoff=int(p.year_earlier)
    prior=[rid for rid in by_stratum[key] if meta[rid]["year"]<cutoff]
    if not prior:
        return []

    prior_route_species=set()
    prior_strong=defaultdict(set)
    for rid in prior:
        for st in sampled.get(rid,set()):
            sid=site.get((rid,st))
            if sid is None:
                continue
            for sp,x in ci.get((rid,st),{}).items():
                if x>0:
                    prior_route_species.add(sp)
                if x>=2:
                    prior_strong[sid].add(sp)

    stops=sorted(sampled[w])
    wet=direction_endpoint(w,d,stops,site,ci,prior_route_species,prior_strong)
    dry=direction_endpoint(d,w,stops,site,ci,prior_route_species,prior_strong)
    if wet is None or dry is None:
        return []

    rows=[]
    for direction,target,out,adv in [
        ("wet",w,wet,float(p.rain_contrast)),
        ("dry",d,dry,-float(p.rain_contrast))
    ]:
        row={
            "pair_id":int(pid),
            "direction":direction,
            "route_cluster":str(p.route_cluster),
            "same_observer":bool(same_observer),
            "target_rain_advantage":adv,
        }
        row.update(out)
        rows.append(row)
    return rows

def fit_pair_fixed(df,response):
    d=df.copy()
    counts=d.groupby("pair_id").size()
    good=counts[counts==2].index
    d=d[d.pair_id.isin(good)].copy()
    if d.empty:
        return None

    d["y_w"]=d[response]-d.groupby("pair_id")[response].transform("mean")
    d["x_w"]=d.target_rain_advantage-d.groupby("pair_id").target_rain_advantage.transform("mean")
    m=sm.OLS(d.y_w.astype(float),d[["x_w"]].astype(float)).fit(
        cov_type="cluster",cov_kwds={"groups":d.route_cluster.astype(str)}
    )
    b=float(m.params["x_w"]);se=float(m.bse["x_w"])
    wide=d.pivot(index="pair_id",columns="direction",values=response)
    asym=(wide["wet"]-wide["dry"]).dropna()
    return {
        "response":response,
        "n_direction_rows":int(len(d)),
        "n_pairs":int(d.pair_id.nunique()),
        "n_routes":int(d.route_cluster.nunique()),
        "beta_target_rain_advantage":b,
        "se":se,
        "ci95":[b-Q*se,b+Q*se],
        "p":float(m.pvalues["x_w"]),
        "positive_ci":bool(b>0 and b-Q*se>0),
        "mean_wet_minus_dry_targeting":float(asym.mean()),
        "median_wet_minus_dry_targeting":float(asym.median()),
    }

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
        rows.extend(pair_direction_rows(
            pid,p,sampled,site,ci,meta,by_stratum,
            (str(p.wet_RunID),str(p.dry_RunID)) in same_keys
        ))
    d=pd.DataFrame(rows)

    primary=fit_pair_fixed(d,"ci3_rate_difference")
    gate=bool(
        primary is not None
        and primary["n_pairs"]>=750
        and primary["n_routes"]>=250
    )
    out={
        "analysis":"naamp_rain_selective_local_memory_v0_1",
        "contract":"exploration/NAAMP_RAIN_SELECTIVE_LOCAL_MEMORY_CONTRACT_V0_1.json",
        "coverage":{
            "all_pairs":int(len(allpairs)),
            "physically_stable_pairs":int(len(stable)),
            "both_direction_rows":int(len(d)),
            "both_direction_pairs":int(d.pair_id.nunique()) if len(d) else 0,
            "gate_pass":gate
        },
        "response_endpoints_read":False
    }
    if not gate:
        out["primary_precheck"]=primary
        OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
        print(json.dumps(out,indent=2,sort_keys=True))
        return

    ci3=primary
    ci2=fit_pair_fixed(d,"ci2plus_rate_difference")
    ds=d[d.same_observer].copy()
    same_fit=fit_pair_fixed(ds,"ci3_rate_difference")
    out.update({
        "response_endpoints_read":True,
        "primary_ci3":ci3,
        "secondary_ci2plus":ci2,
        "same_observer_sensitivity":same_fit,
        "classification":{
            "rain_selectively_reads_local_memory_ci3":bool(ci3["positive_ci"]),
            "rain_selectively_reads_local_memory_ci2plus":bool(ci2 and ci2["positive_ci"]),
            "same_observer_ci3_support":bool(same_fit and same_fit["positive_ci"])
        },
        "interpretation_boundary":{
            "generic_recurrence_cancelled_by_direction_pairing":True,
            "continuous_occupancy_proven":False,
            "causal_rainfall_claim":False,
            "biological_memory_claim":False
        }
    })
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
