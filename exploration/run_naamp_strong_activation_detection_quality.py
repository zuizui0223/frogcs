#!/usr/bin/env python3
from __future__ import annotations
import importlib.util,json
from collections import defaultdict
from pathlib import Path
import numpy as np,pandas as pd
import statsmodels.formula.api as smf

ROOT=Path(__file__).resolve().parents[1]
NAAMP=ROOT/"scripts"/"naamp"
OUT=ROOT/"exploration"/"NAAMP_STRONG_ACTIVATION_DETECTION_QUALITY_RECEIPT_V0_1.json"
Q=1.959963984540054

def loadmod(name,path):
    spec=importlib.util.spec_from_file_location(name,path); mod=importlib.util.module_from_spec(spec)
    assert spec.loader; spec.loader.exec_module(mod); return mod

base=loadmod("base",NAAMP/"run_naamp_ecological_pulse.py")
spatial=loadmod("spatial",NAAMP/"run_naamp_spatial_taxonomic_activation_decomposition.py")
detect=loadmod("detect",NAAMP/"run_naamp_detection_quality_robustness.py")

def build_ci(raw,eligible,sampled):
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

def strong_score(pair,sampled,by):
    wet=str(pair.wet_RunID); dry=str(pair.dry_RunID)
    stops=sorted(sampled[wet])
    if len(stops)!=10 or set(stops)!=set(sampled[dry]): raise RuntimeError("stop alignment")
    val=0.0; count=0
    for st in stops:
        wm=by.get((wet,st),{}); dm=by.get((dry,st),{})
        for sp,w in wm.items():
            if int(dm.get(sp,0))==0 and int(w) in (2,3):
                val+=int(w); count+=1
    return val,float(count)

def fit(d,response,covars):
    x=d[np.isfinite(pd.to_numeric(d[response],errors="coerce"))].copy()
    formula=f"{response} ~ " + " + ".join(covars) + " + C(State) + C(RunNumber)"
    m=smf.ols(formula,data=x).fit(cov_type="cluster",cov_kwds={"groups":x["route_cluster"]})
    b=float(m.params["rain_contrast"]); se=float(m.bse["rain_contrast"])
    return {"beta":b,"se":se,"ci95":[b-Q*se,b+Q*se],"p":float(m.pvalues["rain_contrast"]),"n_pairs":int(len(x)),"n_routes":int(x.route_cluster.nunique()),"positive_ci_support":bool(b-Q*se>0)}

def pack(d,covars):
    return {"strong_new_score":fit(d,"strong_new_score",covars),"strong_new_count":fit(d,"strong_new_count",covars)}

def main():
    raw=base.load()
    runs,pairs_det,metrics=detect.enrich_pairs(raw)
    eligible=set(runs["RunID"].astype(str))
    sampled,_=spatial.stop_matrix(raw,eligible)
    by=build_ci(raw,eligible,sampled)

    strong=[]
    for p in pairs_det.itertuples(index=False):
        score,count=strong_score(p,sampled,by); strong.append((score,count))
    pairs=pairs_det.copy()
    pairs["strong_new_score"]=[x[0] for x in strong]
    pairs["strong_new_count"]=[x[1] for x in strong]

    primary=detect.complete_sample(pairs,detect.BASE_COVARS)
    if not detect.gate(primary,1500,300): raise RuntimeError("primary gate failed")
    pmod=pack(primary,detect.BASE_COVARS)
    exact=primary[primary.year_gap==1].copy(); emod=pack(exact,detect.BASE_COVARS)

    car_cov=detect.BASE_COVARS+["car_count_difference"]
    car=detect.complete_sample(pairs,car_cov)
    car_pkg={"gate_pass":False,"n_pairs":int(len(car)),"n_routes":int(car.route_cluster.nunique())}
    if detect.gate(car,750,200):
        car_pkg={"gate_pass":True,"n_pairs":int(len(car)),"n_routes":int(car.route_cluster.nunique()),"models":pack(car,car_cov)}

    mass_cov=["rain_contrast","temp_difference","doy_difference","year_gap","mass_noise_difference","timeout_difference","wind_difference"]
    mass=detect.complete_sample(pairs,mass_cov)
    mass_pkg={"gate_pass":False,"n_pairs":int(len(mass)),"n_routes":int(mass.route_cluster.nunique())}
    if detect.gate(mass,300,75):
        mass_pkg={"gate_pass":True,"n_pairs":int(len(mass)),"n_routes":int(mass.route_cluster.nunique()),"models":pack(mass,mass_cov)}

    out={
      "analysis":"naamp_strong_activation_detection_quality_v0_1",
      "contract":"exploration/NAAMP_STRONG_ACTIVATION_DETECTION_QUALITY_CONTRACT_V0_1.json",
      "primary":{"n_pairs":int(len(primary)),"n_routes":int(primary.route_cluster.nunique()),"models":pmod,"support":bool(pmod["strong_new_score"]["positive_ci_support"])},
      "exact_consecutive_year":{"n_pairs":int(len(exact)),"n_routes":int(exact.route_cluster.nunique()),"models":emod},
      "car_count_sensitivity":car_pkg,
      "mass_noise_sensitivity":mass_pkg,
      "interpretation_boundary":{"measured_detection_conditions_explain_strong_activation":False if pmod["strong_new_score"]["positive_ci_support"] else None,"all_detectability_bias_eliminated":False,"physiological_mechanism_identified":False,"causal_rainfall_claim":False}
    }
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n"); print(json.dumps(out,indent=2,sort_keys=True))

if __name__=="__main__": main()
