#!/usr/bin/env python3
"""Post-hoc independent frog × NWI aquatic vegetation association tests.

Do not run unless the source-only geometry preflight has passed.
No claim of past vegetation, competition, causal site memory, or RC6 update.
"""
from __future__ import annotations
import argparse
import importlib.util
import json
import math
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf

ROOT=Path(__file__).resolve().parents[1]
Z=1.959963984540054
def mod(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(m)
    return m
hist=mod("history_vegetation",ROOT/"exploration/run_naamp_local_chorus_memory_targeting.py")
detect=mod("detect_vegetation",ROOT/"scripts/naamp/run_naamp_detection_quality_robustness.py")
base=hist.base
spatial=hist.spatial

def read_nwi(path,audit_path):
    audit=json.loads(Path(audit_path).read_text())
    if not audit.get("preflight_eligible"):
        raise RuntimeError("Refusing frog outcome linkage: NWI source-only geographic preflight has NOT PASSED")
    d=pd.read_csv(path,dtype={"SiteID":str,"RouteNumber":str,"State":str})
    cols=["State","RouteNumber","SiteID",
          "nwi_emergent_cover_250m","nwi_aquatic_bed_cover_250m",
          "nwi_woody_cover_250m","nwi_all_wetland_cover_250m"]
    for col in cols:
        if col not in d: raise RuntimeError("Missing required spatial site coverage "+col)
    if d.duplicated(["State","RouteNumber","SiteID"]).any():
        raise RuntimeError("Duplicate plant-site identity")
    if not d.nwi_service_success.astype(str).str.lower().eq("true").all():
        raise RuntimeError("Unsuccessful NWI GIS record leaked into modeling")
    return d.set_index(["State","RouteNumber","SiteID"]),audit

def get_temps_and_detection(raw,runs,sampled):
    out={}
    scales=dict(zip(runs.RunID.astype(str),runs.TempScale.astype(str)))
    for s in raw["Stops.csv"]:
        rid=str(s.get("RunID") or "").strip()
        st=str(s.get("StopNumber") or "").strip()
        if rid not in scales or st not in sampled.get(rid,set()):continue
        temp=detect.num(s.get("AirTemp"))
        sc=scales[rid]
        if np.isfinite(temp):
            if sc=="F":temp=(temp-32)*5/9
            elif sc!="C":temp=np.nan
            if not -10<=temp<=45:temp=np.nan
        bad=detect.num(s.get("MassNoiseIndex"))
        noise=detect.num(s.get("Noise"))
        sound=float(bad) if np.isfinite(bad) and 0<=bad<=4 else float(noise) if noise in (0,1) else np.nan
        out[(rid,st)]={"stop_air_temp_c":temp,"stop_sound_index":sound}
    return out

def build_history(raw,runs,sets,nwi):
    eligible=set(runs.RunID.astype(str))
    sampled,_=spatial.stop_matrix(raw,eligible)
    ci=hist.ci_map(raw,eligible,sampled)
    sites=hist.site_map(raw,eligible)
    meta,by_stratum=hist.build_history(runs,sampled,sites,ci)
    stopenv=get_temps_and_detection(raw,runs,sampled)
    pairs=base.pair_runs(runs,sets).reset_index(drop=True)
    stable=pairs.loc[np.asarray(
        [hist.stable_pair(p,sampled,sites) for p in pairs.itertuples(index=False)],bool)
    ].reset_index(drop=True)
    records=[]
    full_site_pairs=0
    for pid,p in enumerate(stable.itertuples(index=False)):
        w=str(p.wet_RunID)
        rowkey=(str(p.State),str(p.RouteNumber))
        stops=sorted(sampled[w],key=int)
        siteids=[sites.get((w,st)) for st in stops]
        if any(sid is None or (*rowkey,str(sid)) not in nwi.index for sid in siteids):
            continue
        full_site_pairs+=1
        block=hist.pair_rows(pid,p,sampled,sites,ci,meta,by_stratum,False)
        s2st=dict(zip(siteids,stops))
        for row in block:
            sid=str(row["SiteID"])
            st=s2st[sid]
            if isinstance(st,list):raise RuntimeError("Ambiguous physical SiteID-to-stop mapping")
            other=sum(1 for tax,v in ci.get((w,st),{}).items()
                      if tax!=row["species"] and v>=2)
            rec={**row,"State":rowkey[0],"RouteNumber":rowkey[1],
                 "stop_number":int(st),"other_taxa_strong":float(other)}
            rec.update(nwi.loc[(*rowkey,sid)].to_dict())
            rec.update(stopenv.get((w,st),{}))
            records.append(rec)
    out=pd.DataFrame(records)
    cov={"matched_pairs":len(pairs),"physically_stable_pairs":len(stable),
         "pairs_all_10_nwi_sites":full_site_pairs,
         "candidate_pair_species_groups":int(out.pair_species.nunique()) if len(out) else 0,
         "candidate_stop_cells":len(out),
         "candidate_routes":int(out.route_cluster.nunique()) if len(out) else 0}
    return out,cov,sites,sampled,pairs

def within_model(d,features,label):
    if len(d)==0:return {"status":"empty","model":label}
    data=d.copy()
    if "history_x_emergent" in features:
        data["history_x_emergent"]=data.prior_site_strong.astype(float)*(
            data.nwi_emergent_cover_250m.astype(float)-data.nwi_emergent_cover_250m.mean())
    data=data.dropna(subset=["prior_site_strong","wet_strong"]+features).copy()
    if data.empty:return {"status":"no_complete_case","model":label}
    info=data.groupby("pair_species")["prior_site_strong"].nunique()
    data=data[data.pair_species.isin(info[info>1].index)].copy()
    n=int(data.pair_species.nunique())
    k=int(data.route_cluster.nunique())
    if len(data)<500 or n<350 or k<200:
        return {"status":"insufficient_scope","model":label,
                "n_stop_cells":len(data),"n_pair_species":n,"n_routes":k,
                "requirement":"at least 350 informative pair-species and 200 routes"}
    # If historical strong calling and prior_any are collinear in this sample
    # reject rather than silently report a singular fitted effect.
    cols=["prior_site_strong"]+features
    grp=data.groupby("pair_species",sort=False)
    X=np.column_stack([
        (data[x].astype(float)-grp[x].transform("mean").astype(float)).to_numpy()
        for x in cols
    ])
    y=(data.wet_strong.astype(float)-grp.wet_strong.transform("mean")).to_numpy()
    rank=int(np.linalg.matrix_rank(X))
    if rank<len(cols):
        return {"status":"nonidentifiable","model":label,
                "n_stop_cells":len(data),"rank":rank,"n_predictors":len(cols)}
    if np.max(np.linalg.cond(X))>1e7:
        return {"status":"collinear","model":label}
    f=sm.OLS(y,X).fit(cov_type="cluster",
                      cov_kwds={"groups":data.route_cluster.astype(str)})
    results={}
    for i,name in enumerate(cols):
        beta=float(f.params[i]);se=float(f.bse[i])
        results[name]={"beta":beta,"se":se,"ci95":[beta-Z*se,beta+Z*se],
                       "p":float(f.pvalues[i])}
    return {"status":"fitted","model":label,"n_stop_cells":len(data),
            "n_pair_species":n,"n_routes":k,
            "coefficient":results,"model_type":"within species-by-survey-pair LPM, route clustered"}

def checkerboard_vegetation(raw,runs,ref,nwi,sites,sampled):
    # Run-level frog residual must originate from frozen independent checkerboard
    # test, and must not be recomputed or tuned after seeing vegetation.
    needed={"RunID","excess","observed_cscore","null_mean"}
    if not needed.issubset(set(ref.columns)):
        raise RuntimeError("Unverified checkerboard analysis reference input")
    runmap=runs.set_index("RunID",drop=False)
    features=[]
    for rr in ref.itertuples(index=False):
        rid=str(rr.RunID)
        if rid not in runmap.index:continue
        r=runmap.loc[rid]
        state=str(r.State);route=str(r.RouteNumber)
        stops=sorted(sampled[rid],key=int)
        if len(stops)!=10:continue
        sids=[sites.get((rid,st)) for st in stops]
        if any(sid is None or (state,route,str(sid)) not in nwi.index for sid in sids):
            continue
        arr=nwi.loc[[(state,route,str(sid)) for sid in sids]]
        emerg=arr.nwi_emergent_cover_250m.astype(float)
        aquatic=arr.nwi_aquatic_bed_cover_250m.astype(float)
        woody=arr.nwi_woody_cover_250m.astype(float)
        wetland=arr.nwi_all_wetland_cover_250m.astype(float)
        features.append({"RunID":rid,"route_cluster":r.route_cluster,
                         "State":state,"RunNumber":str(r.RunNumber),
                         "survey_year":float(r.SurveyYear),
                         "mean_air_c":float(r.mean_temp_c),
                         "days_since_rain":float(r.DaysSinceRain),
                         "nwi_emergent_variance":float(emerg.var(ddof=0)),
                         "nwi_emergent_mean":float(emerg.mean()),
                         "nwi_aquatic_bed_mean":float(aquatic.mean()),
                         "nwi_woody_variance":float(woody.var(ddof=0)),
                         "nwi_wetland_mean":float(wetland.mean()),
                         "nwi_num_aquatic_bed_stops":int((aquatic>0).sum()),
                         "excess":float(rr.excess)})
    df=pd.DataFrame(features)
    scope={"n_matched_runs":int(len(df)),
           "n_routes":int(df.route_cluster.nunique()) if len(df) else 0,
           "n_states":int(df.State.nunique()) if len(df) else 0}
    if len(df)<100 or df.route_cluster.nunique()<30:
        return {"status":"insufficient_geographic_coverage","scope":scope}
    if df.nwi_emergent_variance.nunique()<3 or (df.nwi_emergent_variance>0).sum()<30:
        return {"status":"insufficient_emergent_variation","scope":scope,
                "routes_with_vegetation_heterogeneity":
                int(df[df.nwi_emergent_variance>0].route_cluster.nunique())}
    # Residual C-score has fixed-fixed taxon and site incidence margins.
    # Route clustering is mandatory; static spatial predictors remain confounded
    # with unmeasured geographic route properties.
    rhs="nwi_emergent_variance + nwi_emergent_mean + nwi_aquatic_bed_mean + nwi_wetland_mean + nwi_woody_variance + mean_air_c + np.log1p(days_since_rain) + survey_year + C(State) + C(RunNumber)"
    fit=smf.ols("excess ~ "+rhs,data=df).fit(
        cov_type="cluster",cov_kwds={"groups":df.route_cluster.astype(str)})
    coef=float(fit.params["nwi_emergent_variance"])
    se=float(fit.bse["nwi_emergent_variance"])
    return {"status":"fitted","scope":scope,
            "mean_fixed_fixed_cscore_residual":float(df.excess.mean()),
            "nwi_emergent_variance_beta":coef,
            "ci95":[coef-Z*se,coef+Z*se],"p":float(fit.pvalues["nwi_emergent_variance"]),
            "note":"Exploratory BETWEEN-ROUTE association with static present-day vegetation; not a causal mechanism"}

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--nwi-sites",type=Path,required=True)
    parser.add_argument("--nwi-audit",type=Path,required=True)
    parser.add_argument("--checkerboard-run-level",type=Path,required=True)
    parser.add_argument("--out",type=Path,default=ROOT/"build"/"aquatic_vegetation_ecology"/"result.json")
    args=parser.parse_args()
    nwi,audit=read_nwi(args.nwi_sites,args.nwi_audit)
    raw=hist.load_retry()
    runs,sets=base.build_runs(raw)
    d,scope,sites,sampled,pairs=build_history(raw,runs,sets,nwi)
    for j in range(2,11):
        d["stop_number_"+str(j)]=(d.stop_number.astype(int)==j).astype(float) if len(d) else pd.Series(dtype=float)
    positions=["stop_number_"+str(j) for j in range(2,11)]
    predictors=["nwi_all_wetland_cover_250m","nwi_emergent_cover_250m",
                "nwi_aquatic_bed_cover_250m","nwi_woody_cover_250m",
                "stop_air_temp_c","stop_sound_index","other_taxa_strong"]+positions
    baseline=within_model(d,predictors[:0],"M0_historical_use_only")
    adjusted=within_model(d,predictors,"M1_environment_plus_historical_use")
    interaction=within_model(d,predictors+["history_x_emergent"],
                             "M2_emergent_modifier_of_historical_use")
    ref=pd.read_csv(args.checkerboard_run_level,dtype={"RunID":str})
    checker=checkerboard_vegetation(raw,runs,ref,nwi,sites,sampled)
    result={
        "analysis":"naamp_nwi_aquatic_vegetation_ecological_link_v0_1",
        "status":"new_posthoc_exploratory_beyond_RC6",
        "source_nwi_geometry_audit":audit,
        "frog_sample_coverage":scope,
        "models":{
            "historical_site_baseline":baseline,
            "vegetation_adjusted_historical_site_use":adjusted,
            "past_use_x_emergent_cover":interaction,
            "checkerboard_residual_x_emergent_heterogeneity":checker},
        "boundaries":{
            "aquatic_plant_species_measured":False,
            "vegetation_time_matched_to_frog_surveys":False,
            "water_level_hydroperiod_directly_measured":False,
            "causal_vegetation_effect":False,
            "interspecific_competition_inferred":False,
            "frog_site_fidelity_or_memory_inferred":False,
            "RC6_submission_modified":False}
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,indent=2,ensure_ascii=False,sort_keys=True)+"\n")
    print("AQUATIC_VEGETATION_ECOLOGICAL_RESULT_BEGIN")
    print(json.dumps(result,ensure_ascii=False,sort_keys=True))
    print("AQUATIC_VEGETATION_ECOLOGICAL_RESULT_END",flush=True)

if __name__=="__main__":
    main()
