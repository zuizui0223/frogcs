#!/usr/bin/env python3
"""NAAMP spatial acoustic turnover: geodesic distance versus stop survey order.

Uses original 2001-2015 USGS source, validated NWI 12-shard coordinates,
and exactly the same route-night station-pairs as previous turnover run.
Post-hoc follow-up: ecological association, not causal vegetation or dispersal.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import math
from collections import Counter
from pathlib import Path

import numpy as np

ROOT=Path(__file__).resolve().parents[1]
EARTH_KM=6371.0088
EXPECTED={
 "any":{"n_surveys":3249,"n_routes":282,"n_pairs":106615,
        "matched_surveys":3130,"matched_routes":282,"matched_pairs":88147},
 "strong":{"n_surveys":2481,"n_routes":275,"n_pairs":70385,
        "matched_surveys":2422,"matched_routes":274,"matched_pairs":64674}
}
NAME="log1p_geographic_distance_km"

def load_module(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(module)
    return module

def haversine(lat_a,lon_a,lat_b,lon_b):
    a1=math.radians(lat_a)
    a2=math.radians(lat_b)
    da=a2-a1
    dl=math.radians(lon_b-lon_a)
    v=math.sin(da/2)**2+math.cos(a1)*math.cos(a2)*math.sin(dl/2)**2
    return EARTH_KM*2*math.asin(min(1.,math.sqrt(max(0.,v))))

def audit_sites(records,source):
    raw=source.hist.load_retry()
    runs,_=source.base.build_runs(raw)
    eligible=set(runs.RunID.astype(str))
    site_ids=source.hist.site_map(raw,eligible)
    indexed_runs={str(r.RunID):r for r in runs.itertuples(index=False)}
    nwi,audit=source.read_nwi(
        ROOT/"build/vegetation_context/site_nwi_vegetation_context.csv",
        ROOT/"build/vegetation_context/geometry_nwi_preflight.json")
    if not audit["preflight_eligible"] or audit["overlay"]["site_records"]!=5147:
        raise RuntimeError("Previously validated source coordinate gate changed")
    if not {"latitude","longitude"}.issubset(set(nwi.columns)):
        raise RuntimeError("Original validated NWI overlay lacks site coordinates")
    geom={}
    for rid in sorted(records):
        r=indexed_runs[rid]
        state=str(r.State); route=str(r.RouteNumber)
        vec=[]
        for i in range(1,11):
            sid=site_ids.get((rid,str(i)))
            if sid is None:
                raise RuntimeError("Missing physical site identity at NAAMP stop: "+rid)
            ident=(state,route,str(sid))
            if ident not in nwi.index:
                raise RuntimeError("Source-only verified physical site NWI link lost: "+rid)
            loc=nwi.loc[ident]
            lat=float(loc["latitude"])
            lon=float(loc["longitude"])
            if not (24<=lat<=50 and -126<=lon<=-65):
                raise RuntimeError("Validated NAAMP site has invalid lat/lon")
            vec.append((lat,lon))
        distances=np.zeros((10,10),dtype=float)
        for i in range(10):
            for j in range(i+1,10):
                km=haversine(*vec[i],*vec[j])
                if km>50:
                    raise RuntimeError("Source preflight geometry >50km physical stop pair")
                distances[i,j]=km
                distances[j,i]=km
        geom[rid]=distances
    keys=set(raw["Stops.csv"][0].keys())
    timekeys=sorted(x for x in keys if ("time" in x.lower() or "minute" in x.lower()))
    return geom,{"matched_complete_NAAMP_runs_with_verified_physical_coords":len(geom),
                  "max_pair_km":max(float(x.max()) for x in geom.values()),
                  "source_stop_time_or_minute_column_names":timekeys,
                  "site_ids_from_actual_run_stop_rows":True,
                  "geodesic_distances_recomputed_from_validated_physical_site_coordinates":True,
                  "source_NWI_validation_actions_run":39450277196}

def add_distances(records,geo,mode,turnover,matched=False):
    groups=[]
    counts=Counter()
    gap=[];dist=[]
    for rid in sorted(records):
        run=records[rid]
        g,reason,_,_=turnover.run_pairs(run,mode,matched_richness=matched)
        if g is None:
            counts[reason]+=1
            continue
        rich=[0]*10
        for indices in run["activity"][mode].values():
            for i in indices:rich[i]+=1
        col=[]
        for i in range(10):
            for j in range(i+1,10):
                if rich[i]==0 or rich[j]==0:
                    continue
                if matched and abs(rich[i]-rich[j])>1:
                    continue
                col.append(math.log1p(float(geo[rid][i,j])))
                if not matched:
                    gap.append((j-i)/9.)
                    dist.append(float(geo[rid][i,j]))
        new=np.asarray(col,float)
        if len(new)!=len(g["Y"]):
            raise RuntimeError("Loss of identical original NAAMP station-pair membership")
        g["X"]=np.column_stack([g["X"],new-new.mean()])
        groups.append(g)
    return groups,counts,{"sitepair_stopindex_gap_vs_logdist_correlation":(
        float(np.corrcoef(np.asarray(gap),np.log1p(np.asarray(dist)))[0,1]) if gap else None),
        "raw_pair_geo_distance_km_quantiles":[float(x) for x in np.quantile(dist,[0,.25,.5,.75,1.])] if dist else [],
        "geodesic_distances_derived_from_coordinates_not_stop_numbers":True}

def model_bundle(groups,turnover,mode,matched=False):
    main=turnover.regression(groups)
    if main["status"]!="fitted":raise RuntimeError("Geographic regression design failed")
    r=main["estimates"][NAME]
    cross=main["estimates"]["different_mapped_PEM_overlap"]
    stop=main["estimates"]["stop_index_gap_div_9"]
    folds={}
    for fold in ("A","B"):
        g=[x for x in groups if x["fold"]==fold]
        fit=turnover.regression(g,minimum_routes=15)
        folds[fold]={"routes":fit.get("n_independent_routes"),"status":fit["status"],
                     "physical_km":fit.get("estimates",{}).get(NAME),
                     "ordinal_stop_gap":fit.get("estimates",{}).get("stop_index_gap_div_9")}
    vals=[]
    for state in sorted(set(g["state"] for g in groups)):
        fitted=turnover.regression([g for g in groups if g["state"]!=state])
        v=fitted.get("estimates",{}).get(NAME,{})
        vals.append({"omitted_state":state,"n_routes":fitted.get("n_independent_routes"),
                     "distance_beta":v.get("beta"),"status":fitted["status"]})
    good=[z["distance_beta"] for z in vals if z["status"]=="fitted"]
    return {"fit":main,"physical_log_distance":r,
            "effect_1km_to_10km":float(r["beta"]*(math.log(11)-math.log(2))),
            "ordinal_stop_gap_adjusted":stop,
            "different_PEM_adjusted":cross,
            "geographic_folds":folds,
            "leave_one_state_out":{"results":vals,
                                   "valid_states":len(good),
                                   "positive_fraction":sum(v>0 for v in good)/len(good) if good else None,
                                   "min":min(good) if good else None,"max":max(good) if good else None},
            "matched_richness":matched}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",type=Path,required=True)
    a=ap.parse_args()
    turnover=load_module("naamp_turnover_pem_previously_fixed",ROOT/"exploration/run_naamp_macro_pem_community_turnover_v0_1.py")
    original_QA=turnover.synthetic_QA()
    source=turnover.module()
    records,orig=source.load_run_context()
    if len(records)!=6236 or orig["source_complete_runs"]!=7848:
        raise RuntimeError("Original pinned NAAMP source changed")
    geom,source_receipt=audit_sites(records,source.getmod(
        "macro_geographic_source",ROOT/"exploration/run_naamp_aquatic_vegetation_ecological_tests_v0_2.py"))
    # Preserve the original 5 predictors in order; add geodesic as the 6th.
    turnover.PREDICTORS=tuple(turnover.PREDICTORS)+(NAME,)
    modes={}
    for mode in ("any","strong"):
        groups,exclusions,geometry_QA=add_distances(records,geom,mode,turnover)
        model=model_bundle(groups,turnover,mode)
        g_rich,exclusions_rich,_=add_distances(records,geom,mode,turnover,matched=True)
        richness=model_bundle(g_rich,turnover,mode,matched=True)
        equal=turnover.regression(groups,route_equal=True)
        expected=EXPECTED[mode]
        if (model["fit"]["n_surveys"]!=expected["n_surveys"] or
            model["fit"]["n_independent_routes"]!=expected["n_routes"] or
            model["fit"]["n_station_pairs"]!=expected["n_pairs"]):
            raise RuntimeError("Geodesic analysis modified original case/population or station-pair membership")
        if (richness["fit"]["n_surveys"]!=expected["matched_surveys"] or
            richness["fit"]["n_independent_routes"]!=expected["matched_routes"] or
            richness["fit"]["n_station_pairs"]!=expected["matched_pairs"]):
            raise RuntimeError("Richness-matched sensitivity modified original 250m sample")
        dist=model["physical_log_distance"]
        folds=model["geographic_folds"]
        frac=model["leave_one_state_out"]["positive_fraction"]
        selected=bool(mode=="any" and dist["ci95"][0]>0 and
                      all(folds[x]["physical_km"] is not None and folds[x]["physical_km"]["beta"]>0 for x in ("A","B")) and
                      frac is not None and frac>=.8 and
                      richness["physical_log_distance"]["beta"]>0)
        modes[mode]={"original_identical_case_gates":expected,"model":model,
                     "strict_richness_matched":richness,"route_equal_sensitivity":equal,
                     "geo_QA":geometry_QA,
                     "classification":"exploratory_conditional_distance_association" if selected else "nonconfirmatory"}
    out={"analysis":"NAAMP_original_site_geodesic_vs_sequential_stop_order_macroscale_acoustic_turnover",
         "status":"EXECUTED_real_macro_geographic_distance_discrimination",
         "date":"2026-10-23",
         "contract":"exploration/NAAMP_MACRO_PHYSICAL_DISTANCE_DISCRIMINATION_SPEC_2026_10_23.md",
         "source_original_NAAMP":orig,"source_geographic_coordinates":source_receipt,
         "previous_turnover_synthetic_QA":original_QA,
         "modes":modes,
         "causal_boundaries":{"not_preregistered_before_stop_index_result":True,
                              "NWI_plant_time_contemporaneous":False,
                              "stop_number_elapsed_time_proxy_not_measured_minutes":True,
                              "acoustic_detection_not_occurrence":True,
                              "species_dispersal_or_biotic_interactions_inferred":False,
                              "frog_population_causality_identified":False,
                              "no_change_to_frozen_RC6":True}}
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(out,indent=2,sort_keys=True,allow_nan=False)+"\n")
    print("MACRO_GEODESIC_DISCRIMINATION_BEGIN")
    print(json.dumps({"status":out["status"],"source":source_receipt,
                      "modes":{mode:{"n_station_pairs":v["model"]["fit"]["n_station_pairs"],
                                    "n_routes":v["model"]["fit"]["n_independent_routes"],
                                    "physical_km":v["model"]["physical_log_distance"],
                                    "effect_1_to_10km":v["model"]["effect_1km_to_10km"],
                                    "ordinal_stop_gap":v["model"]["ordinal_stop_gap_adjusted"],
                                    "PEM":v["model"]["different_PEM_adjusted"],
                                    "folds":{k:v["model"]["geographic_folds"][k]["physical_km"] for k in ("A","B")},
                                    "state_loo":{k:v["model"]["leave_one_state_out"][k] for k in ("positive_fraction","min","max")},
                                    "matched":v["strict_richness_matched"]["physical_log_distance"],
                                    "route_equal":v["route_equal_sensitivity"]["estimates"][NAME],
                                    "classification":v["classification"],
                                    "geo_QA":v["geo_QA"]} for mode,v in modes.items()}},
                     sort_keys=True))
    print("MACRO_GEODESIC_DISCRIMINATION_END")
if __name__=="__main__":main()
