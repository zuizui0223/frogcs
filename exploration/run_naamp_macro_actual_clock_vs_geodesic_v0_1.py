#!/usr/bin/env python3
"""Original NAAMP all-taxon beta diversity: physical km vs actual stop StartTime.

A post-hoc geographic robustness test on authentic NAAMP records, distinct from
the previous stop-index analysis. NWI cover is not time-matched; calling
assemblage detections are not concurrent observations or direct interactions.
"""
from __future__ import annotations
import argparse
import importlib.util
import json
import math
import re
from collections import Counter,defaultdict
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
EARTH_KM=6371.0088
GEO="log1p_geographic_distance_km"
CLOCK="log1p_observed_elapsed_minutes"
TIME=re.compile(r"^([01]?\d|2[0-3]):([0-5]\d)$")
OLD_COVARS=("different_mapped_PEM_overlap","stop_index_gap_div_9",
            "absolute_total_NWI_wetland_cover_gap_x10",
            "taxon_richness_gap","mean_pair_taxon_richness")
SIX=OLD_COVARS+(GEO,)
SEVEN=SIX+(CLOCK,)

def mod(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(m)
    return m

def hhmm(value):
    v=str(value or "").strip()
    m=TIME.fullmatch(v)
    if m is None:return None
    return 60*int(m.group(1))+int(m.group(2))

def distance(a,b):
    lat1,lon1=a;lat2,lon2=b
    p1=math.radians(lat1);p2=math.radians(lat2)
    dlat=p2-p1;dlon=math.radians(lon2-lon1)
    q=math.sin(dlat/2)**2+math.cos(p1)*math.cos(p2)*math.sin(dlon/2)**2
    return 2*EARTH_KM*math.asin(min(1.,math.sqrt(max(0.,q))))

def load_geo_clock(records,source):
    raw=source.hist.load_retry()
    runs,_=source.base.build_runs(raw)
    eligible=set(runs.RunID.astype(str))
    records_meta={str(x.RunID):x for x in runs.itertuples(index=False)}
    sites=source.hist.site_map(raw,eligible)
    nwi,audit=source.read_nwi(
        ROOT/"build/vegetation_context/site_nwi_vegetation_context.csv",
        ROOT/"build/vegetation_context/geometry_nwi_preflight.json")
    assert audit["preflight_eligible"] and audit["overlay"]["site_records"]==5147
    assert {"latitude","longitude"}.issubset(nwi.columns)
    clocks={}
    duplicate_count=0
    for r in raw["Stops.csv"]:
        rid=str(r.get("RunID") or "").strip()
        if rid not in records:continue
        st=str(r.get("StopNumber") or "").strip()
        if st not in [str(k) for k in range(1,11)]:continue
        minute=hhmm(r.get("StartTime"))
        key=(rid,st)
        if key in clocks:
            duplicate_count+=1
            if clocks[key]!=minute:raise RuntimeError("Conflicting source stop start clock")
        clocks[key]=minute
    if duplicate_count:raise RuntimeError("Original eligible ten-stop structure has duplicate stop clock rows")
    geo={}
    start={}
    n_missing=0;n_parsed=0
    for rid in sorted(records):
        r=records_meta[rid]
        s=str(r.State);route=str(r.RouteNumber)
        pts=[];times=[]
        for k in range(1,11):
            sid=sites.get((rid,str(k)))
            if sid is None:raise RuntimeError("Physical run/site mapping missing")
            idx=(s,route,str(sid))
            if idx not in nwi.index:raise RuntimeError("Source-only response-blind coordinate mapping drift")
            p=nwi.loc[idx]
            xy=(float(p["latitude"]),float(p["longitude"]))
            if not (24<=xy[0]<=50 and -126<=xy[1]<=-65):
                raise RuntimeError("NAAMP site geographic coordinate invalid")
            pts.append(xy)
            t=clocks.get((rid,str(k)))
            times.append(t)
            n_parsed+=int(t is not None)
            n_missing+=int(t is None)
        matrix=np.zeros((10,10))
        for i in range(10):
            for j in range(i+1,10):
                km=distance(pts[i],pts[j])
                if km>50:raise RuntimeError("Geography source QA impossible site separation")
                matrix[i,j]=matrix[j,i]=km
        geo[rid]=matrix
        start[rid]=times
    return geo,start,{"source_qualified_NAAMP_stop_rows":10*len(records),
                      "parsed_HHMM_start_clocks":n_parsed,
                      "missing_or_nonHHMM_clocks":n_missing,
                      "fraction_parsed":n_parsed/(n_parsed+n_missing),
                      "time_out_is_binary_not_elapsed":True,
                      "max_plausible_pair_elapsed_minutes":360,
                      "night_midnight_wrap_allowed":True,
                      "time_source":"Original NAAMP Stops.csv StartTime",
                      "site_coordinates":"Validated USFWS NWI crosswalk raw latitude+longitude",
                      "original_geometry_actions":39450277196}

def sample(groups,records,geo,clocks,mode,matched=False):
    for rid in sorted(records):
        run=records[rid]
        pem=(run["v"][:,1]>0).astype(int)
        if not (2<=int(pem.sum())<=8):
            groups["not_mixed_PEM"]+=1
            continue
        # Keep original 2026-10-23 run/site acoustic criteria first.
        original,reason,_,_=turnover.run_pairs(run,mode,matched_richness=matched)
        if original is None:
            groups["baseline_"+reason]+=1
            continue
        site=[set() for _ in range(10)]
        for sp,positions in run["activity"][mode].items():
            for i in positions:site[i].add(sp)
        X=[];Y=[]
        localclock=clocks[rid]
        for i in range(10):
            for j in range(i+1,10):
                a,b=site[i],site[j]
                na,nb=len(a),len(b)
                if na==0 or nb==0:continue
                if matched and abs(na-nb)>1:continue
                if localclock[i] is None or localclock[j] is None:
                    groups["dropped_pair_missing_clock"]+=1
                    continue
                # Real recorded clock minutes: forward chronological j after i.
                minutes=(localclock[j]-localclock[i])%1440
                if minutes>360:
                    groups["dropped_pair_implausible_elapsed_over_360min"]+=1
                    continue
                km=float(geo[rid][i,j])
                if not 0<=km<=50:raise ValueError("Broken original geographic pair")
                Y.append(1.-2.*len(a&b)/(na+nb))
                X.append([float(pem[i]!=pem[j]),(j-i)/9.,
                           abs(float(run["v"][i,0]-run["v"][j,0])),
                           abs(na-nb),(na+nb)/2.,
                           math.log1p(km),math.log1p(minutes)])
        if len(X)<10:
            groups["clock_fewer_than_10_eligible_pairs"]+=1
            continue
        X=np.asarray(X,dtype=float);Y=np.asarray(Y,dtype=float)
        nc=int(np.count_nonzero(X[:,0]))
        if nc<2 or len(X)-nc<2:
            groups["clock_too_few_PEM_cross_or_same_pairs"]+=1
            continue
        Xm=X-X.mean(axis=0);Ym=Y-Y.mean()
        if max(abs(Xm.mean(axis=0)))>1e-10 or abs(float(Ym.mean()))>1e-10:
            raise RuntimeError("Invalid run fixed-effect transform")
        groups["rows"].append({"route":run["route"],"state":run["state"],
                               "fold":run["fold"],"X":Xm,"Y":Ym,
                               "clock_available_pair_count":len(X),
                               "raw_cross_count":nc,
                               "raw_within_count":len(X)-nc,
                               "raw_cross_sum":float(Y[X[:,0]==1].sum()),
                               "raw_same_sum":float(Y[X[:,0]==0].sum()),
                               "mean_logkm":float(X[:,5].mean()),
                               "mean_logminutes":float(X[:,6].mean())})
        groups["number_valid_clock_pairs"]+=len(Y)
        groups["n_runs_included"]+=1

def fit(groups,columns,route_equal=False,route_min=30):
    turnover.PREDICTORS=tuple(columns)
    records=groups
    if len(columns)==7:return turnover.regression(records,route_equal=route_equal,minimum_routes=route_min)
    if len(columns)==6:
        records=[{**g,"X":g["X"][:,:6]} for g in groups]
        return turnover.regression(records,route_equal=route_equal,minimum_routes=route_min)
    raise RuntimeError("Unexpected frozen model covariates")

def assess(groups,mode):
    full=fit(groups,SEVEN)
    reduced=fit(groups,SIX)
    if full["status"]!="fitted" or reduced["status"]!="fitted":
        return {"status":"clock_coverage_or_rank_gate_blocked",
                "full":full,"geodesic_without_clock_same_sample":reduced}
    b=full["estimates"][GEO]
    tm=full["estimates"][CLOCK]
    folds={}
    for fold in ("A","B"):
        f=fit([g for g in groups if g["fold"]==fold],SEVEN,route_min=15)
        folds[fold]={"status":f["status"],"n_routes":f.get("n_independent_routes"),
                     "geodesic":f.get("estimates",{}).get(GEO),
                     "elapsed_clock":f.get("estimates",{}).get(CLOCK)}
    states=sorted(set(g["state"] for g in groups))
    loso=[]
    for state in states:
        res=fit([g for g in groups if g["state"]!=state],SEVEN)
        loso.append({"omitted_state":state,"beta":res.get("estimates",{}).get(GEO,{}).get("beta"),
                     "status":res["status"]})
    values=[x["beta"] for x in loso if x["status"]=="fitted"]
    corr=np.concatenate([g["X"][:,[1,5,6]] for g in groups],axis=0)
    C=np.corrcoef(corr,rowvar=False)
    return {"status":"fitted","mode":mode,
            "n_clock_runs":full["n_surveys"],"n_routes":full["n_independent_routes"],
            "n_same_night_pairs":full["n_station_pairs"],
            "full_physical_and_clock":full,
            "geodesic_without_clock_same_sample":reduced,
            "full_geodesic":b,"full_elapsed_clock":tm,
            "physical_1km_to_10km_dissimilarity_difference":float(b["beta"]*(math.log(11)-math.log(2))),
            "time_10min_to_60min_dissimilarity_difference":float(tm["beta"]*(math.log(61)-math.log(11))),
            "clock_to_geo_correlation_matrix":{
              "variables":["ordinal_stop_index_gap","log1p_geographic_km","log1p_elapsed_minutes"],
              "correlation":C.tolist()},
            "geographic_fold_estimates":folds,
            "leave_one_state_out":{"n_states":len(values),
                                   "all":loso,
                                   "positive_fraction":sum(x>0 for x in values)/len(values) if values else None,
                                   "min":min(values) if values else None,
                                   "max":max(values) if values else None}}

def mode_output(records,geo,clocks,mode):
    bag=defaultdict(int)
    bag["rows"]=[]
    sample(bag,records,geo,clocks,mode,matched=False)
    rows=bag.pop("rows")
    base=assess(rows,mode)
    m=defaultdict(int)
    m["rows"]=[]
    sample(m,records,geo,clocks,mode,matched=True)
    matchrows=m.pop("rows")
    matched=assess(matchrows,mode)
    weighted=fit(rows,SEVEN,route_equal=True)
    if base["status"]!="fitted":return {"status":"clock_coverage_or_rank_gate_blocked",
                                       "sample":bag,"fit":base,"matched_sample":m,"matched":matched}
    est=base["full_geodesic"]
    folds=base["geographic_fold_estimates"]
    frac=base["leave_one_state_out"]["positive_fraction"]
    mp=matched.get("full_geodesic",{}).get("beta") if matched.get("status")=="fitted" else None
    sufficient=base["n_routes"]>=100 and base["n_same_night_pairs"]>=20000
    supported=bool(mode=="any" and sufficient and est["ci95"][0]>0 and
                   all(folds[k]["geodesic"] is not None and folds[k]["geodesic"]["beta"]>0 for k in ("A","B")) and
                   frac is not None and frac>=.8 and mp is not None and mp>0)
    return {"status":"fitted","sample":bag,"fit":base,
            "matched_sample":m,"matched":matched,
            "route_equal":weighted,
            "classification":("exploratory_distance_after_clock_supported" if supported else
                              "time_coverage_underpowered" if not sufficient else "nonconfirmatory")}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    global turnover
    turnover=mod("clock_naamp_previously_frozen_turnover",ROOT/"exploration/run_naamp_macro_pem_community_turnover_v0_1.py")
    QA=turnover.synthetic_QA()
    source=turnover.module()
    records,cov=source.load_run_context()
    assert cov["source_complete_runs"]==7848 and len(records)==6236
    src=source.getmod("clock_naamp_original_geo",ROOT/"exploration/run_naamp_aquatic_vegetation_ecological_tests_v0_2.py")
    geom,clocks,clockqa=load_geo_clock(records,src)
    out={"analysis":"NAAMP_real_recorded_clock_time_vs_geodesic_mapped_PEM_community_turnover",
         "status":"EXECUTED_time_pair_macro_check",
         "date":"2026-10-23",
         "contract":"exploration/NAAMP_MACRO_CLOCK_VS_GEODESIC_FROZEN_SPEC_2026_10_23.md",
         "source_population":cov,"clock_source_gate":clockqa,
         "original_5term_synthetic_QA":QA,
         "modes":{mode:mode_output(records,geom,clocks,mode) for mode in ("any","strong")},
         "boundaries":{"actual_stop_time_used_not_ordinal_proxy":True,
                       "original_2001_2015_NWI_vegetation_time_matched":False,
                       "directional_sitepair_minutes_not_species_interaction":True,
                       "ecological_or_causal_frog_to_frog_interaction_proven":False,
                       "individual_dispersal_inferred":False,
                       "no_change_JAE_RC6_main_SI":True}}
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(out,sort_keys=True,indent=2,allow_nan=False)+"\n")
    print("NAAMP_GEO_CLOCK_REAL_RESULT_BEGIN")
    print(json.dumps({"status":out["status"],"clock_gate":clockqa,
       "modes":{k:{"status":v["status"],"class":v.get("classification"),
           "clock_sample":v.get("sample"),
           "primary":v.get("fit",{}).get("full_geodesic"),
           "elapsed":v.get("fit",{}).get("full_elapsed_clock"),
           "physical_1km_to_10km":v.get("fit",{}).get("physical_1km_to_10km_dissimilarity_difference"),
           "minutes_10to60":v.get("fit",{}).get("time_10min_to_60min_dissimilarity_difference"),
           "physical_without_clock_on_same_pop":v.get("fit",{}).get("geodesic_without_clock_same_sample",{}).get("estimates",{}).get(GEO),
           "geo_folds":{f:v.get("fit",{}).get("geographic_fold_estimates",{}).get(f,{}).get("geodesic") for f in ("A","B")},
           "LOSO":{z:v.get("fit",{}).get("leave_one_state_out",{}).get(z) for z in ("positive_fraction","min","max","n_states")},
           "richness_match":v.get("matched",{}).get("full_geodesic"),
           "route_equal":v.get("route_equal",{}).get("estimates",{}).get(GEO),
           "geo_time_correlation":v.get("fit",{}).get("clock_to_geo_correlation_matrix")} for k,v in out["modes"].items()}},sort_keys=True))
    print("NAAMP_GEO_CLOCK_REAL_RESULT_END")
if __name__=="__main__":main()
