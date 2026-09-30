#!/usr/bin/env python3
from __future__ import annotations

import importlib.util, json
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from scipy.stats import norm

ROOT=Path(__file__).resolve().parents[1]
EXP=ROOT/"exploration"
OUT=EXP/"NAAMP_SOIL_STATE_VS_CHANGE_RECEIPT_V0_1.json"
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

def fit_state(df,response,wet_term,dry_term):
    form=(
        f"{response} ~ rain_contrast + rain72_amount_difference_z + "
        f"{wet_term} + {dry_term} + temp_difference + doy_difference + year_gap + "
        "C(State) + C(RunNumber)"
    )
    m=smf.ols(form,data=df).fit(cov_type="cluster",cov_kwds={"groups":df.route_cluster})
    def term(name):
        b=float(m.params[name]); se=float(m.bse[name])
        return {"beta":b,"se":se,"ci95":[b-Q*se,b+Q*se],"p":float(m.pvalues[name]),"positive_ci":bool(b-Q*se>0)}

    bw=float(m.params[wet_term]); bd=float(m.params[dry_term])
    cov=m.cov_params()
    varsum=float(cov.loc[wet_term,wet_term]+cov.loc[dry_term,dry_term]+2*cov.loc[wet_term,dry_term])
    sesum=float(np.sqrt(max(varsum,0.0)))
    zsum=(bw+bd)/sesum if sesum>0 else np.nan
    psum=float(2*norm.sf(abs(zsum))) if np.isfinite(zsum) else np.nan

    dry_p=float(m.pvalues[dry_term])
    wet=term(wet_term); dry=term(dry_term)
    change_ok=bool(np.isfinite(psum) and psum>=0.05 and wet["positive_ci"])
    wet_state_ok=bool(dry_p>=0.05 and np.isfinite(psum) and psum<0.05 and wet["positive_ci"])
    mixed=bool(dry_p<0.05 and np.isfinite(psum) and psum<0.05 and wet["positive_ci"])
    if change_ok:
        cls="change_sufficient"
    elif wet_state_ok:
        cls="wet_state_favored"
    elif mixed:
        cls="mixed_state_and_change"
    else:
        cls="unresolved"

    return {
        "response":response,"formula":form,"n_pairs":int(len(df)),"n_routes":int(df.route_cluster.nunique()),
        "wet_soil":wet,"dry_soil":dry,
        "rain72":term("rain72_amount_difference_z"),
        "rain_contrast":term("rain_contrast"),
        "pure_change_restriction":{
            "estimate_beta_wet_plus_beta_dry":float(bw+bd),
            "se":sesum,"z":float(zsum) if np.isfinite(zsum) else None,
            "p":psum,"not_rejected_at_0_05":bool(np.isfinite(psum) and psum>=0.05),
        },
        "wet_state_only_restriction":{
            "dry_beta_zero_p":dry_p,
            "not_rejected_at_0_05":bool(dry_p>=0.05),
        },
        "classification":cls,
    }

def fit_transition(df,response):
    form=(
        f'{response} ~ rain_contrast + rain72_amount_difference_z + '
        'C(soil_transition, Treatment(reference="remain_low")) + '
        'temp_difference + doy_difference + year_gap + C(State) + C(RunNumber)'
    )
    m=smf.ols(form,data=df).fit(cov_type="cluster",cov_kwds={"groups":df.route_cluster})
    terms={}
    for name in m.params.index:
        if "soil_transition" in name:
            b=float(m.params[name]); se=float(m.bse[name])
            terms[name]={"beta":b,"se":se,"ci95":[b-Q*se,b+Q*se],"p":float(m.pvalues[name])}
    return {
        "response":response,"formula":form,
        "n_pairs":int(len(df)),"n_routes":int(df.route_cluster.nunique()),
        "category_counts":{str(k):int(v) for k,v in df.soil_transition.value_counts().items()},
        "terms_vs_remain_low":terms,
    }

def main():
    raw=hydric.retry(base.load,"NAAMP load")
    runs,sets=base.build_runs(raw)
    eligible=set(runs.RunID.astype(str))
    sampled,_=spatial.stop_matrix(raw,eligible)
    by=hydric.build_ci(raw,eligible,sampled)
    site=hydric.site_map(raw,eligible)

    mid=hydric.build_midpoints(raw,runs)
    weather,audit=soil.extract(mid)

    all_s1=np.asarray([v["swvl1"] for v in weather.values()],float)
    all_s2=np.asarray([v["swvl2"] for v in weather.values()],float)
    m1=float(all_s1.mean()); s1=float(all_s1.std(ddof=0))
    m2=float(all_s2.mean()); s2=float(all_s2.std(ddof=0))
    if not s1>0 or not s2>0:
        raise RuntimeError("invalid environmental soil SD")
    q1=np.quantile(all_s1,[.25,.50,.75])
    q2=np.quantile(all_s2,[.25,.50,.75])
    q75=float(q1[2])

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
        score,count,ci3=hydric.metrics(p,sampled,by)
        sw=float(weather[w]["swvl1"]); sd=float(weather[d]["swvl1"])
        if sd<q75<=sw:
            cat="cross_up"
        elif sw>=q75 and sd>=q75:
            cat="remain_high"
        elif sw<q75 and sd<q75:
            cat="remain_low"
        else:
            cat="cross_down"
        r=p._asdict()
        r.update({
            "strong_new_score":float(score),
            "strong_new_count":float(count),
            "new_ci3_count":float(ci3),
            "wet_swvl1_z":float((sw-m1)/s1),
            "dry_swvl1_z":float((sd-m1)/s1),
            "wet_swvl2_z":float((weather[w]["swvl2"]-m2)/s2),
            "dry_swvl2_z":float((weather[d]["swvl2"]-m2)/s2),
            "rain72_log_difference":float(np.log1p(weather[w]["rain72_mm"])-np.log1p(weather[d]["rain72_mm"])),
            "soil_transition":cat,
            "same_observer":bool((w,d) in same_keys),
        })
        rows.append(r)
    df=pd.DataFrame(rows)

    if len(df)<3500 or df.route_cluster.nunique()<500:
        out={"analysis":"naamp_soil_state_vs_change_v0_1","status":"not_run_due_to_prefixed_gate",
             "coverage":{"pairs":int(len(df)),"routes":int(df.route_cluster.nunique())},"weather_audit":audit}
        OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
        print(json.dumps(out,indent=2,sort_keys=True))
        return

    df["rain72_amount_difference_z"],mr,sr=hydric.zscore(df.rain72_log_difference)

    primary=fit_state(df,"strong_new_score","wet_swvl1_z","dry_swvl1_z")
    full=fit_state(df,"new_ci3_count","wet_swvl1_z","dry_swvl1_z")
    layer2=fit_state(df,"strong_new_score","wet_swvl2_z","dry_swvl2_z")
    transition=fit_transition(df,"strong_new_score")

    ds=df[df.same_observer].copy()
    samefit=fit_state(ds,"strong_new_score","wet_swvl1_z","dry_swvl1_z") if len(ds)>=2500 and ds.route_cluster.nunique()>=450 else None

    out={
      "analysis":"naamp_soil_state_vs_change_v0_1",
      "contract":"exploration/NAAMP_SOIL_STATE_VS_CHANGE_CONTRACT_V0_1.json",
      "status":"completed_after_prefixed_gate",
      "coverage":{"pairs":int(len(df)),"routes":int(df.route_cluster.nunique()),"same_observer_pairs":int(len(ds)),"same_observer_routes":int(ds.route_cluster.nunique())},
      "weather_audit":audit,
      "environmental_reference":{
        "swvl1_n_runs":int(len(all_s1)),
        "swvl1_mean":m1,"swvl1_sd":s1,
        "swvl1_q25_q50_q75":[float(x) for x in q1],
        "swvl2_mean":m2,"swvl2_sd":s2,
        "swvl2_q25_q50_q75":[float(x) for x in q2],
        "rain72_difference_mean":mr,"rain72_difference_sd":sr,
      },
      "primary_strong_new_score_swvl1":primary,
      "secondary_full_chorus_swvl1":full,
      "secondary_strong_score_swvl2":layer2,
      "threshold_q75_diagnostic":transition,
      "same_observer_sensitivity":samefit,
      "classification":{
        "primary":primary["classification"],
        "same_observer":samefit["classification"] if samefit else "not_run",
      },
      "interpretation_boundary":{
        "soil_state_is_pond_depth":False,
        "soil_state_is_body_hydration":False,
        "fixed_biological_threshold_proven":False,
        "causal_mediation_established":False,
      }
    }
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
