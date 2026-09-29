#!/usr/bin/env python3
from __future__ import annotations
import importlib.util,json,time,urllib.error
from collections import defaultdict
from pathlib import Path
import numpy as np,pandas as pd,statsmodels.formula.api as smf

ROOT=Path(__file__).resolve().parents[1]
NAAMP=ROOT/"scripts"/"naamp"
OUT=ROOT/"exploration"/"NAAMP_STRONG_ACTIVATION_SAME_OBSERVER_PHYSICAL_STOP_RECEIPT_V0_1.json"
Q=1.959963984540054

def loadmod(name,path):
    spec=importlib.util.spec_from_file_location(name,path); mod=importlib.util.module_from_spec(spec)
    assert spec.loader; spec.loader.exec_module(mod); return mod

base=loadmod("base",NAAMP/"run_naamp_ecological_pulse.py")
spatial=loadmod("spatial",NAAMP/"run_naamp_spatial_taxonomic_activation_decomposition.py")
sameobs=loadmod("sameobs",NAAMP/"run_naamp_same_observer_robustness.py")

def site_map(raw,eligible):
    vals=defaultdict(set)
    for s in raw["Stops.csv"]:
        rid=(s.get("RunID") or "").strip(); st=(s.get("StopNumber") or "").strip(); sid=(s.get("SiteID") or "").strip()
        if rid not in eligible or (s.get("SkippedStop") or "").strip()!="0" or not st: continue
        if sid: vals[(rid,st)].add(sid)
    bad={k:v for k,v in vals.items() if len(v)>1}
    if bad: raise RuntimeError(f"multiple SiteID values: {list(bad)[:10]}")
    return {k:next(iter(v)) for k,v in vals.items() if v}

def stable(p,sampled,site):
    w=str(p.wet_RunID); d=str(p.dry_RunID); ws=set(sampled[w]); ds=set(sampled[d])
    if len(ws)!=10 or ws!=ds: return False
    return all(site.get((w,st)) is not None and site.get((w,st))==site.get((d,st)) for st in ws)

def ci_map(raw,eligible,sampled):
    vals=defaultdict(list)
    for r in raw["Counts.csv"]:
        rid=(r.get("RunID") or "").strip(); st=(r.get("StopNumber") or "").strip(); sp=(r.get("Species") or "").strip()
        if rid not in eligible or st not in sampled.get(rid,set()) or not sp: continue
        try: ci=int(float((r.get("CallingIndex") or "").strip()))
        except Exception: continue
        if ci in (1,2,3): vals[(rid,st,sp)].append(ci)
    by=defaultdict(dict)
    for (rid,st,sp),v in vals.items(): by[(rid,st)][sp]=max(v)
    return by

def metrics(p,sampled,by):
    w=str(p.wet_RunID); d=str(p.dry_RunID); stops=sorted(sampled[w])
    strong_score=0.0; strong_count=0; weak_score=0.0
    for st in stops:
        wm=by.get((w,st),{}); dm=by.get((d,st),{})
        for sp in set(wm)|set(dm):
            wi=int(wm.get(sp,0)); di=int(dm.get(sp,0))
            if di==0 and wi>0:
                if wi>=2: strong_score+=wi; strong_count+=1
                else: weak_score+=1
    return {"strong_new_score":strong_score,"strong_new_count":float(strong_count),"weak_new_score":weak_score}

def fit(df,response):
    form=f"{response} ~ rain_contrast + temp_difference + doy_difference + year_gap + C(State) + C(RunNumber)"
    m=smf.ols(form,data=df).fit(cov_type="cluster",cov_kwds={"groups":df["route_cluster"]})
    b=float(m.params["rain_contrast"]); se=float(m.bse["rain_contrast"])
    return {"beta":b,"se":se,"ci95":[b-Q*se,b+Q*se],"p":float(m.pvalues["rain_contrast"]),"n_pairs":int(len(df)),"n_routes":int(df.route_cluster.nunique())}

def load_with_retry():
    last=None
    for i in range(6):
        try:
            return base.load()
        except urllib.error.HTTPError as e:
            last=e
            if getattr(e,"code",None) not in (403,429,500,502,503,504):
                raise
            time.sleep(2*(i+1))
    raise RuntimeError(f"ScienceBase load failed after retries: {last}")

def main():
    raw=load_with_retry(); runs,sets=base.build_runs(raw); eligible=set(runs["RunID"].astype(str))
    sampled,_=spatial.stop_matrix(raw,eligible)
    allpairs,same=sameobs.same_observer_pairs(raw,runs,sets)
    site=site_map(raw,eligible)
    mask=np.asarray([stable(p,sampled,site) for p in same.itertuples(index=False)],bool)
    selected=same.loc[mask].copy().reset_index(drop=True)
    by=ci_map(raw,eligible,sampled)
    rows=[]
    for p in selected.itertuples(index=False):
        r=p._asdict(); r.update(metrics(p,sampled,by)); rows.append(r)
    d=pd.DataFrame(rows)
    mods={x:fit(d,x) for x in ("strong_new_score","strong_new_count","weak_new_score")}
    passed=bool(mods["strong_new_score"]["ci95"][0]>0 and mods["strong_new_count"]["ci95"][0]>0)
    out={
      "analysis":"naamp_strong_activation_same_observer_physical_stop_v0_1",
      "contract":"exploration/NAAMP_STRONG_ACTIVATION_SAME_OBSERVER_PHYSICAL_STOP_CONTRACT_V0_1.json",
      "coverage":{
        "all_pairs":int(len(allpairs)),
        "same_observer_pairs":int(len(same)),
        "intersection_pairs":int(len(selected)),
        "intersection_fraction_all":float(len(selected)/len(allpairs)),
        "routes":int(selected.route_cluster.nunique()),
        "observers":int(selected["_observer_token"].nunique())
      },
      "models":mods,
      "classification":{"joint_robust_strong_new_activation":passed},
      "interpretation_boundary":{
        "observer_turnover_required":False if passed else None,
        "physical_stop_relocation_required":False if passed else None,
        "weak_call_only_detection_explanation_sufficient":False if passed else None,
        "all_detectability_bias_eliminated":False,
        "physiological_mechanism_identified":False,
        "causal_rainfall_claim":False
      }
    }
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n"); print(json.dumps(out,indent=2,sort_keys=True))

if __name__=="__main__": main()
