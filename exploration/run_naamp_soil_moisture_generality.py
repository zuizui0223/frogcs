#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

ROOT=Path(__file__).resolve().parents[1]
EXP=ROOT/"exploration"
OUT=EXP/"NAAMP_SOIL_MOISTURE_GENERALITY_RECEIPT_V0_1.json"
Q=1.959963984540054

def loadmod(name,path):
    s=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(s)
    assert s.loader
    s.loader.exec_module(m)
    return m

soil=loadmod("soil_parent",EXP/"run_naamp_soil_moisture_cue.py")
hydric=soil.hydric
base=soil.base
spatial=soil.spatial
sameobs=soil.sameobs

def route_fold(route_cluster):
    b=hashlib.sha256(str(route_cluster).encode("utf-8")).digest()[0]
    return "A" if b<128 else "B"

def fit(d,include_state=True):
    x=d.copy()
    state=" + C(State)" if include_state else ""
    form=(
      "strong_new_score ~ rain_contrast + rain72_amount_difference_z + "
      "soil1_gain_difference_z + temp_difference + doy_difference + year_gap"
      +state+" + C(RunNumber)"
    )
    m=smf.ols(form,data=x).fit(cov_type="cluster",cov_kwds={"groups":x.route_cluster})
    def term(name):
        b=float(m.params[name]); se=float(m.bse[name])
        return {"beta":b,"se":se,"ci95":[b-Q*se,b+Q*se],"p":float(m.pvalues[name]),
                "positive_ci":bool(b-Q*se>0)}
    return {
      "formula":form,"n_pairs":int(len(x)),"n_routes":int(x.route_cluster.nunique()),
      "soil_moisture":term("soil1_gain_difference_z"),
      "rain72_amount":term("rain72_amount_difference_z"),
      "rain_contrast":term("rain_contrast")
    }

def main():
    raw=hydric.retry(base.load,"NAAMP load")
    runs,sets=base.build_runs(raw)
    eligible=set(runs.RunID.astype(str))
    mid=hydric.build_midpoints(raw,runs)
    weather,audit=soil.extract(mid)

    sampled,_=spatial.stop_matrix(raw,eligible)
    by=hydric.build_ci(raw,eligible,sampled)
    site=hydric.site_map(raw,eligible)
    pairs=base.pair_runs(runs,sets).copy().reset_index(drop=True)
    _,same=sameobs.same_observer_pairs(raw,runs,sets)
    same_keys={(str(p.wet_RunID),str(p.dry_RunID)) for p in same.itertuples(index=False)}

    rows=[]
    for p in pairs.itertuples(index=False):
        w=str(p.wet_RunID); d=str(p.dry_RunID)
        if w not in weather or d not in weather:
            continue
        score,count,ci3=hydric.metrics(p,sampled,by)
        r=p._asdict()
        r.update({
          "strong_new_score":score,
          "rain72_log_difference":float(np.log1p(weather[w]["rain72_mm"])-np.log1p(weather[d]["rain72_mm"])),
          "soil1_gain_difference":float(weather[w]["swvl1"]-weather[d]["swvl1"]),
          "same_observer_physical_stop":bool((w,d) in same_keys and hydric.stable_pair(p,sampled,site)),
        })
        rows.append(r)
    df=pd.DataFrame(rows)
    if len(df)<3500 or df.route_cluster.nunique()<500:
        raise RuntimeError("weather-qualified sample below parent gate")

    df["rain72_amount_difference_z"],m72,s72=hydric.zscore(df.rain72_log_difference)
    df["soil1_gain_difference_z"],m1,s1=hydric.zscore(df.soil1_gain_difference)
    df["route_fold"]=df.route_cluster.map(route_fold)

    route={}
    for fold in ("A","B"):
        d=df[df.route_fold==fold].copy()
        route[fold]={"gate":bool(len(d)>=1500 and d.route_cluster.nunique()>=250)}
        if route[fold]["gate"]:
            route[fold]["model"]=fit(d,True)

    temporal={}
    for name,mask in {
        "early_2001_2008":df.year_earlier<=2008,
        "late_2009_2015":df.year_earlier>=2009,
    }.items():
        d=df[mask].copy()
        temporal[name]={"gate":bool(len(d)>=1200 and d.route_cluster.nunique()>=250)}
        if temporal[name]["gate"]:
            temporal[name]["model"]=fit(d,True)

    loso={}
    for st in sorted(df.State.astype(str).unique()):
        d=df[df.State.astype(str)!=st].copy()
        loso[st]=fit(d,True)

    state_specific={}
    for st,g in df.groupby("State",sort=True):
        g=g.copy()
        gate=bool(len(g)>=100 and g.route_cluster.nunique()>=15)
        state_specific[str(st)]={"gate":gate,"n_pairs":int(len(g)),"n_routes":int(g.route_cluster.nunique())}
        if gate:
            try:
                state_specific[str(st)]["model"]=fit(g,False)
            except Exception as e:
                state_specific[str(st)]["error"]=str(e)[:300]

    robust=df[df.same_observer_physical_stop].copy()
    robust_route={}
    for fold in ("A","B"):
        d=robust[robust.route_fold==fold].copy()
        robust_route[fold]={"gate":bool(len(d)>=1000 and d.route_cluster.nunique()>=200)}
        if robust_route[fold]["gate"]:
            robust_route[fold]["model"]=fit(d,True)

    def both_ci(section):
        return bool(all(
          section[f].get("gate") and section[f]["model"]["soil_moisture"]["positive_ci"]
          for f in section
        ))
    route_pass=both_ci(route)
    temporal_pass=both_ci(temporal)
    robust_route_pass=both_ci(robust_route) if all(robust_route[f]["gate"] for f in robust_route) else False
    loso_all_positive=bool(all(v["soil_moisture"]["beta"]>0 for v in loso.values()))
    loso_all_ci=bool(all(v["soil_moisture"]["positive_ci"] for v in loso.values()))

    estimable=[v["model"] for v in state_specific.values() if v.get("gate") and "model" in v]
    state_pos=float(np.mean([x["soil_moisture"]["beta"]>0 for x in estimable])) if estimable else None
    state_ci=float(np.mean([x["soil_moisture"]["positive_ci"] for x in estimable])) if estimable else None

    out={
      "analysis":"naamp_soil_moisture_generality_v0_1",
      "contract":"exploration/NAAMP_SOIL_MOISTURE_GENERALITY_CONTRACT_V0_1.json",
      "coverage":{
        "pairs":int(len(df)),"routes":int(df.route_cluster.nunique()),
        "states":int(df.State.nunique()),
        "robust_pairs":int(len(robust)),"robust_routes":int(robust.route_cluster.nunique())
      },
      "standardization":{"rain72_mean":m72,"rain72_sd":s72,"soil1_gain_mean":m1,"soil1_gain_sd":s1},
      "weather_audit":audit,
      "deterministic_route_split":route,
      "temporal_split":temporal,
      "leave_one_state_out":loso,
      "state_specific_descriptive":state_specific,
      "robust_route_split":robust_route,
      "summary":{
        "route_split_both_ci_positive":route_pass,
        "temporal_split_both_ci_positive":temporal_pass,
        "robust_route_split_both_ci_positive":robust_route_pass,
        "loso_all_positive":loso_all_positive,
        "loso_all_ci_positive":loso_all_ci,
        "state_specific_positive_fraction":state_pos,
        "state_specific_ci_positive_fraction":state_ci,
        "n_state_specific_estimable":int(len(estimable))
      },
      "classification":{
        "naamp_domain_soil_moisture_generality_supported":bool(route_pass and temporal_pass and loso_all_positive),
        "strong_generality_supported":bool(route_pass and temporal_pass and loso_all_ci),
      },
      "interpretation_boundary":{
        "naamp_domain_only":True,
        "soil_water_is_body_hydration":False,
        "soil_water_is_pond_depth":False,
        "causal_mediation_established":False,
        "universal_claim":False
      }
    }
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
