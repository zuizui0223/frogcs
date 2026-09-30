#!/usr/bin/env python3
from __future__ import annotations

import importlib.util, json
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

ROOT=Path(__file__).resolve().parents[1]
EXP=ROOT/"exploration"
NAAMP=ROOT/"scripts"/"naamp"
OUT=EXP/"NAAMP_SOIL_SPATIAL_DEPTH_RECEIPT_V0_1.json"
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

def pair_depth_metrics(p,sampled,by):
    w=str(p.wet_RunID); d=str(p.dry_RunID)
    stops=sorted(sampled[w])

    dry_route=set()
    wet_by_species=defaultdict(dict)
    for st in stops:
        dry_route.update(by.get((d,st),{}))
        for sp,x in by.get((w,st),{}).items():
            if x>0:
                wet_by_species[sp][st]=int(x)

    route_new=second=third=strong_third=full_third=0.0
    for sp,occ in wet_by_species.items():
        if sp in dry_route:
            continue
        route_new+=1.0
        k=len(occ)
        second+=float(k>=2)
        dep=float(max(k-2,0))
        third+=dep
        m=max(occ.values())
        if m>=2:
            strong_third+=dep
        if m==3:
            full_third+=dep

    return {
        "route_new_species":route_new,
        "second_stop_incidence":second,
        "third_plus_depth":third,
        "strong_third_plus_depth":strong_third,
        "full_chorus_third_plus_depth":full_third,
    }

def fit(df,response,soil_term):
    form=f"{response} ~ rain_contrast + rain72_amount_difference_z + {soil_term} + temp_difference + doy_difference + year_gap + C(State) + C(RunNumber)"
    m=smf.ols(form,data=df).fit(cov_type="cluster",cov_kwds={"groups":df.route_cluster})
    def term(name):
        b=float(m.params[name]); se=float(m.bse[name])
        return {"beta":b,"se":se,"ci95":[b-Q*se,b+Q*se],"p":float(m.pvalues[name]),"positive_ci":bool(b-Q*se>0)}
    return {
        "response":response,"formula":form,"n_pairs":int(len(df)),"n_routes":int(df.route_cluster.nunique()),
        "rain_contrast":term("rain_contrast"),
        "rain72_amount":term("rain72_amount_difference_z"),
        "soil_moisture":term(soil_term),
    }

def fit_standardized(df,response):
    x=df.copy()
    sd=float(x[response].std(ddof=0))
    if not np.isfinite(sd) or sd<=0:
        return None
    x["response_z"]=(x[response]-float(x[response].mean()))/sd
    m=fit(x,"response_z","soil1_gain_difference_z")
    return {"response_sd":sd,**m["soil_moisture"]}

def main():
    raw=hydric.retry(base.load,"NAAMP load")
    runs,sets=base.build_runs(raw)
    eligible=set(runs.RunID.astype(str))
    sampled,_=spatial.stop_matrix(raw,eligible)
    by=hydric.build_ci(raw,eligible,sampled)
    site=hydric.site_map(raw,eligible)

    mid=hydric.build_midpoints(raw,runs)
    weather,audit=soil.extract(mid)

    pairs=base.pair_runs(runs,sets).copy().reset_index(drop=True)
    _,same=sameobs.same_observer_pairs(raw,runs,sets)
    same_keys={(str(p.wet_RunID),str(p.dry_RunID)) for p in same.itertuples(index=False)}

    rows=[]
    for p in pairs.itertuples(index=False):
        w=str(p.wet_RunID); d=str(p.dry_RunID)
        if w not in weather or d not in weather:
            continue
        if not hydric.stable_pair(p,sampled,site):
            continue
        r=p._asdict()
        r.update(pair_depth_metrics(p,sampled,by))
        r.update({
            "rain72_log_difference":float(np.log1p(weather[w]["rain72_mm"])-np.log1p(weather[d]["rain72_mm"])),
            "soil1_gain_difference":float(weather[w]["swvl1"]-weather[d]["swvl1"]),
            "soil2_gain_difference":float(weather[w]["swvl2"]-weather[d]["swvl2"]),
            "same_observer":bool((w,d) in same_keys),
        })
        rows.append(r)
    df=pd.DataFrame(rows)

    if len(df)<3500 or df.route_cluster.nunique()<500:
        out={
            "analysis":"naamp_soil_moisture_spatial_depth_v0_1",
            "status":"not_run_due_to_prefixed_gate",
            "coverage":{"pairs":int(len(df)),"routes":int(df.route_cluster.nunique())},
            "weather_audit":audit
        }
        OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
        print(json.dumps(out,indent=2,sort_keys=True))
        return

    df["rain72_amount_difference_z"],mr,sr=hydric.zscore(df.rain72_log_difference)
    df["soil1_gain_difference_z"],m1,s1=hydric.zscore(df.soil1_gain_difference)
    df["soil2_gain_difference_z"],m2,s2=hydric.zscore(df.soil2_gain_difference)

    responses=[
        "route_new_species",
        "second_stop_incidence",
        "third_plus_depth",
        "strong_third_plus_depth",
        "full_chorus_third_plus_depth",
    ]
    primary={x:fit(df,x,"soil1_gain_difference_z") for x in responses}
    swvl2={x:fit(df,x,"soil2_gain_difference_z") for x in ("third_plus_depth","strong_third_plus_depth")}
    standardized={x:fit_standardized(df,x) for x in responses}

    robust=df[df.same_observer].copy()
    robust_fit=fit(robust,"strong_third_plus_depth","soil1_gain_difference_z") if len(robust)>=2500 and robust.route_cluster.nunique()>=450 else None

    strong_support=bool(primary["strong_third_plus_depth"]["soil_moisture"]["positive_ci"])
    total_support=bool(primary["third_plus_depth"]["soil_moisture"]["positive_ci"])
    taxa_support=bool(primary["route_new_species"]["soil_moisture"]["positive_ci"])
    second_support=bool(primary["second_stop_incidence"]["soil_moisture"]["positive_ci"])

    if strong_support and total_support and not taxa_support:
        cls="hydric_release_of_spatial_depth_more_than_taxon_number"
    elif strong_support and total_support:
        cls="broad_hydric_recruitment_and_spatial_depth"
    elif strong_support:
        cls="strong_chorus_spatial_depth_only"
    else:
        cls="soil_moisture_spatial_depth_not_supported"

    out={
      "analysis":"naamp_soil_moisture_spatial_depth_v0_1",
      "contract":"exploration/NAAMP_SOIL_SPATIAL_DEPTH_CONTRACT_V0_1.json",
      "status":"completed_after_prefixed_gate",
      "coverage":{"pairs":int(len(df)),"routes":int(df.route_cluster.nunique()),"same_observer_pairs":int(len(robust)),"same_observer_routes":int(robust.route_cluster.nunique())},
      "weather_audit":audit,
      "standardization":{
        "rain72_mean":mr,"rain72_sd":sr,
        "soil1_gain_mean":m1,"soil1_gain_sd":s1,
        "soil2_gain_mean":m2,"soil2_gain_sd":s2,
      },
      "primary_swvl1":primary,
      "secondary_swvl2":swvl2,
      "standardized_response_effects":standardized,
      "same_observer_strong_depth":robust_fit,
      "classification":{
        "result":cls,
        "strong_third_plus_soil_support":strong_support,
        "third_plus_soil_support":total_support,
        "route_new_species_soil_support":taxa_support,
        "second_stop_soil_support":second_support,
      },
      "interpretation_boundary":{
        "individual_movement_inferred":False,
        "soil_water_is_pond_depth":False,
        "causal_mediation_established":False,
        "submission_story_change_authorized":False
      }
    }
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
