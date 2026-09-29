#!/usr/bin/env python3
from __future__ import annotations
import importlib.util,json,warnings
from collections import defaultdict
from pathlib import Path
import numpy as np,pandas as pd,statsmodels.formula.api as smf

ROOT=Path(__file__).resolve().parents[1]
NAAMP=ROOT/"scripts"/"naamp"
OUT=ROOT/"exploration"/"NAAMP_TEMPERATURE_GATED_STRONG_ACTIVATION_RECEIPT_V0_1.json"
Q=1.959963984540054

def loadmod(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s)
    assert s.loader;s.loader.exec_module(m);return m

base=loadmod("base",NAAMP/"run_naamp_ecological_pulse.py")
spatial=loadmod("spatial",NAAMP/"run_naamp_spatial_taxonomic_activation_decomposition.py")
sameobs=loadmod("sameobs",NAAMP/"run_naamp_same_observer_robustness.py")

def ci_map(raw,eligible,sampled):
    vals=defaultdict(list)
    for r in raw["Counts.csv"]:
        rid=(r.get("RunID") or "").strip();st=(r.get("StopNumber") or "").strip();sp=(r.get("Species") or "").strip()
        if rid not in eligible or st not in sampled.get(rid,set()) or not sp:continue
        try:x=int(float((r.get("CallingIndex") or "").strip()))
        except:continue
        if x in (1,2,3):vals[(rid,st,sp)].append(x)
    by=defaultdict(dict)
    for (rid,st,sp),v in vals.items():by[(rid,st)][sp]=max(v)
    return by

def site_map(raw,eligible):
    vals=defaultdict(set)
    for s in raw["Stops.csv"]:
        rid=(s.get("RunID") or "").strip();st=(s.get("StopNumber") or "").strip();sid=(s.get("SiteID") or "").strip()
        if rid in eligible and st and sid and (s.get("SkippedStop") or "").strip()=="0":vals[(rid,st)].add(sid)
    bad={k:v for k,v in vals.items() if len(v)>1}
    if bad:raise RuntimeError(f"site conflict {list(bad)[:5]}")
    return {k:next(iter(v)) for k,v in vals.items()}

def stable(p,sampled,site):
    w=str(p.wet_RunID);d=str(p.dry_RunID);ws=set(sampled[w]);ds=set(sampled[d])
    return len(ws)==10 and ws==ds and all(site.get((w,st)) is not None and site.get((w,st))==site.get((d,st)) for st in ws)

def metrics(p,sampled,ci):
    w=str(p.wet_RunID);d=str(p.dry_RunID);score=0.0;ci3=0.0
    for st in sorted(sampled[w]):
        wm=ci.get((w,st),{});dm=ci.get((d,st),{})
        for sp in set(wm)|set(dm):
            wi=int(wm.get(sp,0));di=int(dm.get(sp,0))
            if di==0 and wi>=2:
                score+=wi
                ci3+=int(wi==3)
    return score,ci3

def enrich(pairs,runs,sampled,ci):
    temp={str(r.RunID):float(r.mean_temp_c) for r in runs.itertuples(index=False)}
    d=pairs.copy().reset_index(drop=True)
    vals=[metrics(p,sampled,ci) for p in d.itertuples(index=False)]
    d["strong_new_score"]=[x[0] for x in vals]
    d["new_ci3_count"]=[x[1] for x in vals]
    d["pair_mean_temp_c"]=[
        (temp[str(p.wet_RunID)]+temp[str(p.dry_RunID)])/2
        for p in d.itertuples(index=False)
    ]
    mu=float(d.pair_mean_temp_c.mean());sd=float(d.pair_mean_temp_c.std(ddof=0))
    if sd<=0:raise RuntimeError("temperature scale invalid")
    d["pair_mean_temp_z"]=(d.pair_mean_temp_c-mu)/sd
    return d,mu,sd

def fit(d,response):
    form=f"{response} ~ rain_contrast * pair_mean_temp_z + temp_difference + doy_difference + year_gap + C(State) + C(RunNumber)"
    m=smf.ols(form,data=d).fit(cov_type="cluster",cov_kwds={"groups":d.route_cluster})
    term="rain_contrast:pair_mean_temp_z";b=float(m.params[term]);se=float(m.bse[term])
    return {"response":response,"n_pairs":int(len(d)),"n_routes":int(d.route_cluster.nunique()),
            "interaction_beta":b,"se":se,"ci95":[b-Q*se,b+Q*se],"p":float(m.pvalues[term]),
            "prediction_pass":bool(b>0 and b-Q*se>0),
            "rain_main_at_mean_temp":float(m.params["rain_contrast"])}

def mixed_sd(d,interaction):
    if interaction:
        form="strong_new_score ~ rain_contrast * pair_mean_temp_z + temp_difference + doy_difference + year_gap + C(RunNumber)"
    else:
        form="strong_new_score ~ rain_contrast + pair_mean_temp_z + temp_difference + doy_difference + year_gap + C(RunNumber)"
    with warnings.catch_warnings(record=True) as ws:
        warnings.simplefilter("always")
        try:
            m=smf.mixedlm(form,d,groups=d["State"],re_formula="~rain_contrast").fit(reml=True,method="lbfgs",maxiter=1000,disp=False)
            cov=m.cov_re;sd=float(np.sqrt(max(float(cov.loc["rain_contrast","rain_contrast"]),0)))
            return {"converged":bool(m.converged),"rain_slope_sd":sd,"population_rain_beta":float(m.params["rain_contrast"]),"warnings":[str(w.message) for w in ws]}
        except Exception as e:return {"converged":False,"error":repr(e),"warnings":[str(w.message) for w in ws]}

def main():
    raw=base.load();runs,sets=base.build_runs(raw);eligible=set(runs.RunID.astype(str))
    sampled,_=spatial.stop_matrix(raw,eligible);ci=ci_map(raw,eligible,sampled)
    allpairs=base.pair_runs(runs,sets).copy().reset_index(drop=True)
    full,mu,sd=enrich(allpairs,runs,sampled,ci)

    _,same=sameobs.same_observer_pairs(raw,runs,sets);site=site_map(raw,eligible)
    robust=same.loc[np.asarray([stable(p,sampled,site) for p in same.itertuples(index=False)],bool)].copy().reset_index(drop=True)
    rob,_,_=enrich(robust,runs,sampled,ci)
    # Use full-sample temperature centering for robustness comparability.
    rob["pair_mean_temp_z"]=(rob.pair_mean_temp_c-mu)/sd

    primary=fit(full,"strong_new_score")
    ci3=fit(full,"new_ci3_count")
    robfit=fit(rob,"strong_new_score")
    m0=mixed_sd(full,False);m1=mixed_sd(full,True)
    reduction=None
    if m0.get("converged") and m1.get("converged") and m0["rain_slope_sd"]>0:
        reduction=float(1-m1["rain_slope_sd"]/m0["rain_slope_sd"])

    out={"analysis":"naamp_temperature_gated_strong_activation_v0_1",
         "contract":"exploration/NAAMP_TEMPERATURE_GATED_STRONG_ACTIVATION_CONTRACT_V0_1.json",
         "temperature":{"mean_c":mu,"sd_c":sd,"min_c":float(full.pair_mean_temp_c.min()),"max_c":float(full.pair_mean_temp_c.max())},
         "primary_strong_score":primary,
         "secondary_full_chorus_ci3":ci3,
         "robust_same_observer_physical_stop":robfit,
         "state_random_slope":{"without_interaction":m0,"with_interaction":m1,"fractional_sd_reduction":reduction},
         "classification":{"warm_temperature_gating_supported":bool(primary["prediction_pass"]),
                           "robust_same_sign":bool(np.sign(robfit["interaction_beta"])==np.sign(primary["interaction_beta"]))},
         "interpretation_boundary":{"temperature_is_moderator_not_mediator":True,"causal_claim":False}}
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print(json.dumps(out,indent=2,sort_keys=True))
if __name__=="__main__":main()
