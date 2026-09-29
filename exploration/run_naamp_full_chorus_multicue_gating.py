#!/usr/bin/env python3
from __future__ import annotations

import importlib.util, json
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import chi2
import statsmodels.formula.api as smf

ROOT=Path(__file__).resolve().parents[1]
NAAMP=ROOT/"scripts"/"naamp"
OUT=ROOT/"exploration"/"NAAMP_FULL_CHORUS_MULTICUE_GATING_RECEIPT_V0_1.json"
Q=1.959963984540054
ALPHA=0.025

def loadmod(name,path):
    s=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(s)
    assert s.loader
    s.loader.exec_module(m)
    return m

base=loadmod("base",NAAMP/"run_naamp_ecological_pulse.py")
spatial=loadmod("spatial",NAAMP/"run_naamp_spatial_taxonomic_activation_decomposition.py")
sameobs=loadmod("sameobs",NAAMP/"run_naamp_same_observer_robustness.py")

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
    for (rid,st,sp),x in vals.items():
        by[(rid,st)][sp]=max(x)
    return by

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
        raise RuntimeError(f"multiple SiteID values: {list(bad)[:10]}")
    return {k:next(iter(v)) for k,v in vals.items()}

def stable(p,sampled,site):
    w=str(p.wet_RunID); d=str(p.dry_RunID)
    ws=set(sampled[w]); ds=set(sampled[d])
    return len(ws)==10 and ws==ds and all(
        site.get((w,st)) is not None and site.get((w,st))==site.get((d,st))
        for st in ws
    )

def new_ci3_count(p,sampled,by):
    w=str(p.wet_RunID); d=str(p.dry_RunID)
    n=0
    for st in sorted(sampled[w]):
        wm=by.get((w,st),{})
        dm=by.get((d,st),{})
        for sp in set(wm)|set(dm):
            if int(dm.get(sp,0))==0 and int(wm.get(sp,0))==3:
                n+=1
    return float(n)

def clustered_fit(formula,d):
    return smf.ols(formula,data=d).fit(
        cov_type="cluster",cov_kwds={"groups":d.route_cluster.astype(str)}
    )

def joint_wald(fit,terms):
    names=list(fit.params.index)
    idx=[names.index(t) for t in terms]
    b=np.asarray(fit.params,float)[idx]
    cov=np.asarray(fit.cov_params(),float)[np.ix_(idx,idx)]
    inv=np.linalg.pinv(cov)
    stat=float(b@inv@b)
    df=len(idx)
    p=float(chi2.sf(stat,df))
    return {
        "terms":terms,
        "chi2":stat,
        "df":df,
        "p":p,
        "pass_alpha_0_025":bool(p<ALPHA),
        "coefficients":{terms[i]:float(b[i]) for i in range(df)}
    }

def slope_fit(d,formula):
    m=clustered_fit(formula,d)
    b=float(m.params["rain_contrast"]); se=float(m.bse["rain_contrast"])
    return {
        "n_pairs":int(len(d)),
        "n_routes":int(d.route_cluster.nunique()),
        "beta_rain":b,
        "se":se,
        "ci95":[b-Q*se,b+Q*se],
        "p":float(m.pvalues["rain_contrast"])
    }

def package(d):
    thermal_formula=(
        "new_ci3_count ~ rain_contrast * temp_context_z + "
        "rain_contrast * temp_context_z2 + temp_difference + doy_difference + "
        "year_gap + C(State) + C(RunNumber)"
    )
    tm=clustered_fit(thermal_formula,d)
    thermal_terms=[
        "rain_contrast:temp_context_z",
        "rain_contrast:temp_context_z2"
    ]
    thermal=joint_wald(tm,thermal_terms)
    thermal["formula"]=thermal_formula
    thermal["n_pairs"]=int(len(d))
    thermal["n_routes"]=int(d.route_cluster.nunique())

    seasonal_formula=(
        "new_ci3_count ~ rain_contrast * C(RunNumber) + "
        "temp_difference + doy_difference + year_gap + C(State)"
    )
    sm=clustered_fit(seasonal_formula,d)
    seasonal_terms=[
        name for name in sm.params.index
        if ":" in name and "rain_contrast" in name and "C(RunNumber)" in name
    ]
    if not seasonal_terms:
        raise RuntimeError("no seasonal interaction terms")
    seasonal=joint_wald(sm,seasonal_terms)
    seasonal["formula"]=seasonal_formula
    seasonal["n_pairs"]=int(len(d))
    seasonal["n_routes"]=int(d.route_cluster.nunique())

    by_run={}
    for rn,g in d.groupby("RunNumber",sort=True):
        if len(g)>=100 and g.route_cluster.nunique()>=30:
            by_run[str(rn)]=slope_fit(
                g,
                "new_ci3_count ~ rain_contrast + temp_difference + doy_difference + year_gap + C(State)"
            )
        else:
            by_run[str(rn)]={
                "estimable":False,"n_pairs":int(len(g)),
                "n_routes":int(g.route_cluster.nunique())
            }

    q=pd.qcut(d.temp_context_z,3,labels=["cool_context","mid_context","warm_context"],duplicates="drop")
    by_temp={}
    for level,g in d.assign(temp_tertile=q).groupby("temp_tertile",observed=True,sort=True):
        by_temp[str(level)]=slope_fit(
            g,
            "new_ci3_count ~ rain_contrast + temp_difference + doy_difference + year_gap + C(State) + C(RunNumber)"
        )

    return {
        "thermal_gating":thermal,
        "seasonal_window_gating":seasonal,
        "descriptive_rain_slopes_by_run_number":by_run,
        "descriptive_rain_slopes_by_thermal_tertile":by_temp,
        "classification":{
            "thermal_gate_pass":bool(thermal["pass_alpha_0_025"]),
            "seasonal_gate_pass":bool(seasonal["pass_alpha_0_025"]),
            "any_multicue_gate_pass":bool(
                thermal["pass_alpha_0_025"] or seasonal["pass_alpha_0_025"]
            )
        }
    }

def main():
    raw=base.load()
    runs,sets=base.build_runs(raw)
    eligible=set(runs.RunID.astype(str))
    sampled,_=spatial.stop_matrix(raw,eligible)
    by=ci_map(raw,eligible,sampled)

    pairs=base.pair_runs(runs,sets).copy().reset_index(drop=True)
    run_temp={str(r.RunID):float(r.mean_temp_c) for r in runs.itertuples(index=False)}
    pairs["pair_mean_temp"]=[
        0.5*(run_temp[str(p.wet_RunID)]+run_temp[str(p.dry_RunID)])
        for p in pairs.itertuples(index=False)
    ]
    pairs["new_ci3_count"]=[
        new_ci3_count(p,sampled,by) for p in pairs.itertuples(index=False)
    ]

    # Outcome-blind thermal-context construction.
    rf=smf.ols("pair_mean_temp ~ C(State) + C(RunNumber)",data=pairs).fit()
    resid=np.asarray(rf.resid,float)
    sd=float(np.std(resid,ddof=0))
    if not np.isfinite(sd) or sd<=0:
        raise RuntimeError("invalid thermal-context residual scale")
    pairs["temp_context_z"]=resid/sd
    pairs["temp_context_z2"]=pairs.temp_context_z**2

    allpairs_same,same= sameobs.same_observer_pairs(raw,runs,sets)
    same_keys={(str(p.wet_RunID),str(p.dry_RunID)) for p in same.itertuples(index=False)}
    site=site_map(raw,eligible)
    robust_mask=np.asarray([
        (str(p.wet_RunID),str(p.dry_RunID)) in same_keys and stable(p,sampled,site)
        for p in pairs.itertuples(index=False)
    ],bool)
    robust=pairs.loc[robust_mask].copy().reset_index(drop=True)

    full=package(pairs)
    rob=package(robust)

    out={
      "analysis":"naamp_full_chorus_multicue_gating_v0_1",
      "contract":"exploration/NAAMP_FULL_CHORUS_MULTICUE_GATING_CONTRACT_V0_1.json",
      "thermal_context":{
        "residual_sd_c":sd,
        "construction_model":"pair_mean_temp ~ C(State) + C(RunNumber)"
      },
      "coverage":{
        "full_pairs":int(len(pairs)),
        "full_routes":int(pairs.route_cluster.nunique()),
        "robust_pairs":int(len(robust)),
        "robust_routes":int(robust.route_cluster.nunique())
      },
      "full":full,
      "robust_same_observer_physical_stop":rob,
      "classification":{
        "full_any_multicue_gate":bool(full["classification"]["any_multicue_gate_pass"]),
        "robust_any_multicue_gate":bool(rob["classification"]["any_multicue_gate_pass"]),
        "joint_robust_multicue_gate":bool(
            full["classification"]["any_multicue_gate_pass"]
            and rob["classification"]["any_multicue_gate_pass"]
        )
      },
      "interpretation_boundary":{
        "unique_physiological_mediator_identified":False,
        "run_number_identical_across_states":False,
        "air_temperature_is_body_temperature":False,
        "causal_rainfall_claim":False
      }
    }
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
