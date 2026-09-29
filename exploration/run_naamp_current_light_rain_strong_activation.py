#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

ROOT=Path(__file__).resolve().parents[1]
NAAMP=ROOT/"scripts"/"naamp"
OUT=ROOT/"exploration"/"NAAMP_CURRENT_LIGHT_RAIN_STRONG_ACTIVATION_RECEIPT_V0_1.json"
Q=1.959963984540054
VALID_SKY={0,1,2,4,5,7,8}

def loadmod(name,path):
    s=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(s)
    assert s.loader
    s.loader.exec_module(m)
    return m

base=loadmod("base",NAAMP/"run_naamp_ecological_pulse.py")
spatial=loadmod("spatial",NAAMP/"run_naamp_spatial_taxonomic_activation_decomposition.py")
sameobs=loadmod("sameobs",NAAMP/"run_naamp_same_observer_robustness.py")

def numcode(x):
    try:
        v=float(str(x or "").strip())
    except Exception:
        return None
    if not np.isfinite(v) or abs(v-round(v))>1e-9:
        return None
    return int(round(v))

def sky_metrics(raw):
    out={}
    for r in raw["Runs.csv"]:
        rid=str(r.get("RunID") or "").strip()
        a=numcode(r.get("StartSky")); b=numcode(r.get("EndSky"))
        valid=bool(a in VALID_SKY and b in VALID_SKY)
        out[rid]={
            "valid":valid,
            "light_rain":(int(a==5 or b==5) if valid else None),
            "has_code8":bool(a==8 or b==8) if (a is not None and b is not None) else False,
            "start":a,"end":b,
        }
    return out

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
    for (rid,st,sp),v in vals.items():
        by[(rid,st)][sp]=max(v)
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
        raise RuntimeError(f"SiteID conflict: {list(bad)[:10]}")
    return {k:next(iter(v)) for k,v in vals.items()}

def stable(p,sampled,site):
    w=str(p.wet_RunID); d=str(p.dry_RunID)
    ws=set(sampled[w]); ds=set(sampled[d])
    return len(ws)==10 and ws==ds and all(
        site.get((w,st)) is not None and site.get((w,st))==site.get((d,st))
        for st in ws
    )

def responses(p,sampled,ci):
    w=str(p.wet_RunID); d=str(p.dry_RunID)
    score=0.0; ci3=0.0
    for st in sorted(sampled[w]):
        wm=ci.get((w,st),{})
        dm=ci.get((d,st),{})
        for sp in set(wm)|set(dm):
            wi=int(wm.get(sp,0)); di=int(dm.get(sp,0))
            if di==0 and wi>=2:
                score+=wi
                ci3+=int(wi==3)
    return score,ci3

def build_pairs(raw,runs,sets,sampled,ci):
    skies=sky_metrics(raw)
    d=base.pair_runs(runs,sets).copy().reset_index(drop=True)
    vals=[responses(p,sampled,ci) for p in d.itertuples(index=False)]
    d["strong_new_score"]=[x[0] for x in vals]
    d["new_ci3_count"]=[x[1] for x in vals]
    wet_lr=[]; dry_lr=[]; adv=[]; code8=[]
    for p in d.itertuples(index=False):
        w=skies.get(str(p.wet_RunID),{})
        r=skies.get(str(p.dry_RunID),{})
        if w.get("valid") and r.get("valid"):
            wl=int(w["light_rain"]); dl=int(r["light_rain"])
            wet_lr.append(wl); dry_lr.append(dl); adv.append(float(wl-dl))
        else:
            wet_lr.append(np.nan); dry_lr.append(np.nan); adv.append(np.nan)
        code8.append(bool(w.get("has_code8",False) or r.get("has_code8",False)))
    d["wet_current_light_rain"]=wet_lr
    d["dry_current_light_rain"]=dry_lr
    d["current_light_rain_advantage"]=adv
    d["any_code8"]=code8
    return d,skies

def fit(d,response):
    x=d[np.isfinite(pd.to_numeric(d["current_light_rain_advantage"],errors="coerce"))].copy()
    form=f"{response} ~ rain_contrast + current_light_rain_advantage + temp_difference + doy_difference + year_gap + C(State) + C(RunNumber)"
    m=smf.ols(form,data=x).fit(cov_type="cluster",cov_kwds={"groups":x.route_cluster})
    br=float(m.params["rain_contrast"]); ser=float(m.bse["rain_contrast"])
    bc=float(m.params["current_light_rain_advantage"]); sec=float(m.bse["current_light_rain_advantage"])
    # same-sample base rain effect for attenuation
    bform=f"{response} ~ rain_contrast + temp_difference + doy_difference + year_gap + C(State) + C(RunNumber)"
    bfit=smf.ols(bform,data=x).fit(cov_type="cluster",cov_kwds={"groups":x.route_cluster})
    b0=float(bfit.params["rain_contrast"])
    attenuation=float(1-br/b0) if abs(b0)>1e-12 else None
    return {
        "response":response,
        "n_pairs":int(len(x)),
        "n_routes":int(x.route_cluster.nunique()),
        "rain_contrast_beta_adjusted":br,
        "rain_contrast_ci95":[br-Q*ser,br+Q*ser],
        "rain_contrast_p":float(m.pvalues["rain_contrast"]),
        "current_light_rain_beta":bc,
        "current_light_rain_ci95":[bc-Q*sec,bc+Q*sec],
        "current_light_rain_p":float(m.pvalues["current_light_rain_advantage"]),
        "same_sample_base_rain_beta":b0,
        "rain_beta_fractional_attenuation":attenuation,
        "current_light_rain_support":bool(bc>0 and bc-Q*sec>0),
        "rain_remains_supported":bool(br>0 and br-Q*ser>0),
    }

def main():
    raw=base.load()
    runs,sets=base.build_runs(raw)
    eligible=set(runs.RunID.astype(str))
    sampled,_=spatial.stop_matrix(raw,eligible)
    ci=ci_map(raw,eligible,sampled)
    d,skies=build_pairs(raw,runs,sets,sampled,ci)

    complete=d[np.isfinite(d.current_light_rain_advantage)].copy()
    gate=bool(len(complete)>=2500 and complete.route_cluster.nunique()>=400)
    out={
      "analysis":"naamp_current_light_rain_strong_activation_v0_1",
      "contract":"exploration/NAAMP_CURRENT_LIGHT_RAIN_STRONG_ACTIVATION_CONTRACT_V0_1.json",
      "coverage":{
        "all_pairs":int(len(d)),
        "complete_sky_pairs":int(len(complete)),
        "complete_sky_routes":int(complete.route_cluster.nunique()),
        "wet_current_light_rain_pairs":int((complete.wet_current_light_rain==1).sum()),
        "dry_current_light_rain_pairs":int((complete.dry_current_light_rain==1).sum()),
        "pairs_with_code8":int(d.any_code8.sum()),
        "gate_pass":gate
      },
      "response_endpoints_read":False
    }
    if not gate:
        OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
        print(json.dumps(out,indent=2,sort_keys=True))
        return

    primary=fit(complete,"strong_new_score")
    ci3=fit(complete,"new_ci3_count")

    site=site_map(raw,eligible)
    _,same=sameobs.same_observer_pairs(raw,runs,sets)
    stable_mask=np.asarray([stable(p,sampled,site) for p in same.itertuples(index=False)],bool)
    robust_keys={(str(p.wet_RunID),str(p.dry_RunID)) for p in same.loc[stable_mask].itertuples(index=False)}
    robust=complete[
        [(str(p.wet_RunID),str(p.dry_RunID)) in robust_keys for p in complete.itertuples(index=False)]
    ].copy()
    robust_fit=fit(robust,"strong_new_score") if len(robust)>=1500 and robust.route_cluster.nunique()>=300 else None

    no8=complete[~complete.any_code8].copy()
    no8_fit=fit(no8,"strong_new_score")

    out.update({
      "response_endpoints_read":True,
      "primary_strong_score":primary,
      "secondary_full_chorus_ci3":ci3,
      "robust_same_observer_physical_stop":robust_fit,
      "sensitivity_excluding_code8":no8_fit,
      "classification":{
        "immediate_light_rain_cue_supported":bool(primary["current_light_rain_support"]),
        "antecedent_rain_signal_retained":bool(primary["rain_remains_supported"])
      },
      "interpretation_boundary":{
        "light_rain_is_categorical":True,
        "humidity_measured":False,
        "causal_mediation_identified":False
      }
    })
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
