#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import math
from pathlib import Path

import numpy as np

ROOT=Path(__file__).resolve().parents[1]
EXP=ROOT/"exploration"
OUT=EXP/"NAAMP_ROUTE_NIGHT_RESIDUAL_DISTANCE_PROFILE_RECEIPT_V0_1.json"

B=1000
SEED=2840227
ANCHOR=0.75
EPS=1e-7
EARTH_KM=6371.0088

def loadmod(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    mod=importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(mod)
    return mod

dep=loadmod("dep",EXP/"run_naamp_species_route_night_residual_dependence.py")
rain=dep.rain
flex=dep.flex
joint=dep.joint
mem=joint.mem
uniform=dep.uniform

def haversine_km(a,b):
    lat1,lon1=map(math.radians,a)
    lat2,lon2=map(math.radians,b)
    dlat=lat2-lat1
    dlon=lon2-lon1
    h=math.sin(dlat/2)**2+math.cos(lat1)*math.cos(lat2)*math.sin(dlon/2)**2
    return 2*EARTH_KM*math.asin(min(1.0,math.sqrt(h)))

def build_geometry(raw,runs,pw,dw):
    eligible=set(runs["RunID"].astype(str))
    site=mem.site_map(raw,eligible)
    coords=rain.load_coords()
    geom=[]
    all_dist=[]
    known=0
    possible=0
    for p,dct in zip(pw.itertuples(index=False),dw):
        wet_id=str(p.wet_RunID)
        stops=list(dct["stops"])
        edges=[]
        for j in range(len(stops)):
            for k in range(j+1,len(stops)):
                possible+=1
                sj=site.get((wet_id,stops[j]))
                sk=site.get((wet_id,stops[k]))
                if sj is None or sk is None or sj not in coords or sk not in coords:
                    continue
                d=haversine_km(coords[sj],coords[sk])
                if not np.isfinite(d):
                    continue
                known+=1
                all_dist.append(d)
                edges.append((j,k,d))
        geom.append(edges)
    if not all_dist:
        raise RuntimeError("no coordinate-known stop-pair distances")
    arr=np.asarray(all_dist,float)
    cuts=np.quantile(arr,[0.25,0.50,0.75])
    # geometry-only bins fixed before residuals are evaluated
    binned=[]
    for edges in geom:
        cur=[]
        for j,k,d in edges:
            b=int(np.searchsorted(cuts,d,side="right"))
            b=min(3,max(0,b))
            cur.append((j,k,d,b))
        binned.append(cur)
    return binned,cuts,arr,known,possible

def summarize(obs_num,den,null_num):
    if den<=0:
        return {"estimable":False}
    D=float(obs_num/den)
    null=np.asarray(null_num,float)/den
    lo,hi=np.quantile(null,[0.025,0.975])
    p=float((1+np.sum(null>=D))/(len(null)+1))
    return {
        "estimable":True,
        "D":D,
        "null_mean":float(np.mean(null)),
        "null_ci95":[float(lo),float(hi)],
        "plus_one_upper_tail_p":p,
        "above_upper_95":bool(D>hi)
    }

def main():
    trigger=json.loads((EXP/"NAAMP_SPECIES_ROUTE_NIGHT_RESIDUAL_DEPENDENCE_RECEIPT_V0_1.json").read_text())
    if not trigger["residual_dependence"]["positive_dependence_supported"]:
        out={"analysis":"naamp_route_night_residual_distance_profile_v0_1","status":"not_run_trigger_not_met"}
        OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
        print(json.dumps(out,indent=2,sort_keys=True))
        return

    raw,runs,psub,dsub,hsub,pools,sampled,ss=flex.prepare_subset()
    mid=rain.build_midpoints(raw,runs)
    weather,weather_sha=rain.antecedent_amounts(mid)
    mask=np.asarray([
        str(p.wet_RunID) in weather and str(p.dry_RunID) in weather
        for p in psub.itertuples(index=False)
    ],bool)
    idx=np.flatnonzero(mask)
    pw=psub.iloc[idx].copy().reset_index(drop=True)
    dw=[dsub[int(i)] for i in idx]
    hw=[hsub[int(i)] for i in idx]
    if len(pw)!=2835:
        raise RuntimeError(f"weather subset drift {len(pw)} != 2835")

    # Geometry is fixed before residual outcomes are evaluated.
    geom,cuts,all_dist,known,possible=build_geometry(raw,runs,pw,dw)

    runs_weather=runs[runs["RunID"].astype(str).isin(weather)].copy().reset_index(drop=True)
    runs_weather["rain72_mm"]=[weather[str(r)]["rain72_mm"] for r in runs_weather["RunID"].astype(str)]
    runs_weather["rain72_log"]=np.log1p(runs_weather["rain72_mm"].astype(float))
    all_species=sorted({sp for spp in pools.values() for sp in spp})
    pred_A,audit_A,fold_A=rain.fit_predict_amount_environment(runs_weather,sampled,ss,all_species,"A")
    pred_B,audit_B,fold_B=rain.fit_predict_amount_environment(runs_weather,sampled,ss,all_species,"B")
    pred_by_train={"A":pred_A,"B":pred_B}

    rng=np.random.default_rng(SEED)
    obs_num=np.zeros(4,float)
    den=np.zeros(4,float)
    null_num=np.zeros((B,4),float)
    contrib_pairs=np.zeros(4,int)
    dist_by_bin=[[] for _ in range(4)]

    for p,dct,p_hist,edges in zip(pw.itertuples(index=False),dw,hw,geom):
        test_fold=joint.fold_for_route(str(p.route_cluster))
        train_fold="B" if test_fold=="A" else "A"
        pred=pred_by_train[train_fold]
        wet_id=str(p.wet_RunID); dry_id=str(p.dry_RunID)
        delta=np.asarray([
            pred[wet_id].get(sp,0.0)-pred[dry_id].get(sp,0.0)
            for sp in dct["species"]
        ],float)

        dry=dct["dry"].astype(float)
        p_anchor=(1.0-ANCHOR)*p_hist+ANCHOR*dry
        p_anchor=np.clip(p_anchor,EPS,1-EPS)
        pre=uniform.expit(uniform.logit(p_anchor)+delta[:,None])
        q=uniform.solve_shift(pre,dct["wet_k"])
        q=np.clip(q,EPS,1-EPS)
        y=dct["wet"].astype(float)
        e=y-q
        v=np.sqrt(q*(1.0-q))
        w=rng.random((B,)+q.shape)<q[None,:,:]
        en=w.astype(float)-q[None,:,:]

        for b in range(4):
            eb=[t for t in edges if t[3]==b]
            if not eb:
                continue
            jj=np.asarray([t[0] for t in eb],int)
            kk=np.asarray([t[1] for t in eb],int)
            dd=[float(t[2]) for t in eb]
            dist_by_bin[b].extend(dd)
            contrib_pairs[b]+=len(eb)
            obs_num[b]+=float(np.sum(e[:,jj]*e[:,kk]))
            den[b]+=float(np.sum(v[:,jj]*v[:,kk]))
            # B x species x edge, summed within this focal route-night.
            null_num[:,b]+=np.sum(en[:,:,jj]*en[:,:,kk],axis=(1,2))

    bins={}
    for b in range(4):
        z=summarize(obs_num[b],den[b],null_num[:,b])
        ds=np.asarray(dist_by_bin[b],float)
        z.update({
            "geometry_pair_instances":int(contrib_pairs[b]),
            "distance_median_km":float(np.median(ds)) if len(ds) else None,
            "distance_range_km":[float(np.min(ds)),float(np.max(ds))] if len(ds) else None
        })
        bins[f"Q{b+1}"]=z

    q1=bins["Q1"].get("D")
    q4=bins["Q4"].get("D")
    ratio=float(q4/q1) if q1 not in (None,0) and q4 is not None else None
    far=bins["Q4"]
    broad=bool(
        far.get("estimable") and far.get("above_upper_95") and
        far.get("plus_one_upper_tail_p",1)>=0 and
        far.get("plus_one_upper_tail_p",1)<0.05
    )

    out={
        "analysis":"naamp_route_night_residual_distance_profile_v0_1",
        "contract":"exploration/NAAMP_ROUTE_NIGHT_RESIDUAL_DISTANCE_PROFILE_CONTRACT_V0_1.json",
        "status":"posthoc_distance_profile_triggered",
        "coverage":{
            "pairs":int(len(pw)),
            "routes":int(pw.route_cluster.nunique()),
            "coordinate_known_stop_pair_instances":int(known),
            "possible_stop_pair_instances":int(possible),
            "coordinate_known_fraction":float(known/possible)
        },
        "geometry":{
            "quartile_cut_km":[float(x) for x in cuts],
            "overall_distance_median_km":float(np.median(all_dist)),
            "overall_distance_range_km":[float(np.min(all_dist)),float(np.max(all_dist))]
        },
        "distance_bins":bins,
        "farthest_to_nearest_D_ratio":ratio,
        "decision":{
            "broad_spatial_dependence_supported":broad
        },
        "weather_provenance":{
            "era5_antecedent_amount_sha256":weather_sha
        },
        "interpretation_boundary":{
            "local_social_facilitation_excluded":False,
            "shared_hydrology_excluded":False,
            "broad_environmental_forcing_excluded":False,
            "literal_simultaneity_inferred":False,
            "independent_confirmation":False
        }
    }
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
