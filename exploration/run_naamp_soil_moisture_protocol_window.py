#!/usr/bin/env python3
from __future__ import annotations
import importlib.util,json
from pathlib import Path
import numpy as np,pandas as pd

ROOT=Path(__file__).resolve().parents[1]
EXP=ROOT/"exploration"
OUT=EXP/"NAAMP_SOIL_MOISTURE_PROTOCOL_WINDOW_RECEIPT_V0_1.json"

def loadmod(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s)
    assert s.loader;s.loader.exec_module(m);return m

soil=loadmod("soil_parent",EXP/"run_naamp_soil_moisture_cue.py")
hydric=soil.hydric;base=soil.base;spatial=soil.spatial;sameobs=soil.sameobs

def build():
    raw=hydric.retry(base.load,"NAAMP load")
    runs,sets=base.build_runs(raw);eligible=set(runs.RunID.astype(str))
    mid=hydric.build_midpoints(raw,runs);weather,audit=soil.extract(mid)
    sampled,_=spatial.stop_matrix(raw,eligible);by=hydric.build_ci(raw,eligible,sampled);site=hydric.site_map(raw,eligible)
    pairs=base.pair_runs(runs,sets).copy().reset_index(drop=True)
    _,same=sameobs.same_observer_pairs(raw,runs,sets)
    same_keys={(str(p.wet_RunID),str(p.dry_RunID)) for p in same.itertuples(index=False)}
    rows=[]
    for p in pairs.itertuples(index=False):
        w=str(p.wet_RunID);d=str(p.dry_RunID)
        if w not in weather or d not in weather:continue
        score,count,ci3=hydric.metrics(p,sampled,by)
        r=p._asdict();r.update({
          "strong_new_score":score,
          "rain72_log_difference":float(np.log1p(weather[w]["rain72_mm"])-np.log1p(weather[d]["rain72_mm"])),
          "soil1_gain_difference":float(weather[w]["swvl1"]-weather[d]["swvl1"]),
          "same_observer_physical_stop":bool((w,d) in same_keys and hydric.stable_pair(p,sampled,site)),
        });rows.append(r)
    d=pd.DataFrame(rows)
    d["rain72_amount_difference_z"],m72,s72=hydric.zscore(d.rain72_log_difference)
    d["soil1_gain_difference_z"],m1,s1=hydric.zscore(d.soil1_gain_difference)
    return d,audit,{"rain72_mean":m72,"rain72_sd":s72,"soil1_gain_mean":m1,"soil1_gain_sd":s1}

def main():
    d,audit,std=build()
    primary=d[d.dry_days_since_rain>=4].copy()
    secondary=d[d.wet_days_since_rain>=4].copy()
    robust=primary[primary.same_observer_physical_stop].copy()

    pgate=bool(len(primary)>=1500 and primary.route_cluster.nunique()>=300)
    sgate=bool(len(secondary)>=150 and secondary.route_cluster.nunique()>=100)
    rgate=bool(len(robust)>=1000 and robust.route_cluster.nunique()>=250)

    pfit=soil.fit(primary,"strong_new_score","soil1_gain_difference_z") if pgate else None
    sfit=soil.fit(secondary,"strong_new_score","soil1_gain_difference_z") if sgate else None
    rfit=soil.fit(robust,"strong_new_score","soil1_gain_difference_z") if rgate else None

    out={
      "analysis":"naamp_soil_moisture_protocol_window_v0_1",
      "contract":"exploration/NAAMP_SOIL_MOISTURE_PROTOCOL_WINDOW_CONTRACT_V0_1.json",
      "coverage":{
        "source_pairs":int(len(d)),"source_routes":int(d.route_cluster.nunique()),
        "primary_pairs":int(len(primary)),"primary_routes":int(primary.route_cluster.nunique()),"primary_gate":pgate,
        "secondary_pairs":int(len(secondary)),"secondary_routes":int(secondary.route_cluster.nunique()),"secondary_gate":sgate,
        "robust_primary_pairs":int(len(robust)),"robust_primary_routes":int(robust.route_cluster.nunique()),"robust_gate":rgate
      },
      "weather_audit":audit,"standardization":std,
      "primary_crosses_three_day_window":pfit,
      "secondary_both_outside_three_day_window":sfit,
      "same_observer_physical_stop_primary":rfit,
      "classification":{
        "primary_soil_support":bool(pfit and pfit["soil_moisture"]["positive_ci"]),
        "robust_primary_soil_support":bool(rfit and rfit["soil_moisture"]["positive_ci"]) if rgate else None
      },
      "interpretation_boundary":{
        "protocol_selection_eliminated":False,
        "all_time_varying_confounding_eliminated":False,
        "soil_water_is_body_hydration":False,
        "causal_mediation_established":False
      }
    }
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,indent=2,sort_keys=True))
if __name__=="__main__":main()
