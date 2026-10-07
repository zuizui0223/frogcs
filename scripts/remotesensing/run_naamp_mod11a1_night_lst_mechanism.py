#!/usr/bin/env python3
from __future__ import annotations
import hashlib, importlib.util, json, os
from pathlib import Path
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[2]
EXP=ROOT/"exploration"
RS=ROOT/"scripts"/"remotesensing"
INCSV=Path(os.environ.get("NAAMP_LST_EXPOSURES",str(ROOT/"remotesensing"/"NAAMP_MOD11A1_NIGHT_LST_EXPOSURES_V0_1.csv")))
COVERAGE=Path(os.environ.get("NAAMP_LST_COVERAGE",str(ROOT/"remotesensing"/"NAAMP_MOD11A1_NIGHT_LST_COVERAGE_V0_1.json")))
OUT=ROOT/"remotesensing"/"NAAMP_MOD11A1_NIGHT_LST_MECHANISM_RECEIPT_V0_1.json"

def loadmod(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);assert s.loader;s.loader.exec_module(m);return m
hyd=loadmod("hyd",RS/"run_naamp_dynamic_hydrology_mechanism.py")
flex=hyd.flex

def main():
    if not INCSV.exists() or not COVERAGE.exists():raise RuntimeError("missing LST inputs")
    cov=json.load(open(COVERAGE))
    out={
      "analysis":"naamp_mod11a1_night_lst_mechanism_v0_1",
      "spec":"revision/NAAMP_MODIS_NIGHT_LST_PROSPECTIVE_SPEC_V0_1.md",
      "coverage":cov,
      "exposure_sha256":hashlib.sha256(INCSV.read_bytes()).hexdigest(),
      "frog_endpoint_read":False
    }
    rule=cov.get("selected_rule")
    if rule not in ("A","B"):
        out["classification"]="night_lst_coverage_inconclusive"
        OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
        print(json.dumps(out,indent=2,sort_keys=True));return

    src=pd.read_csv(INCSV,dtype={"RunID":str,"SiteID":str,"RouteNumber":str})
    src["lst_night_K"]=pd.to_numeric(src["lst_night_K"],errors="coerce")
    var=src[["RunID","SiteID"]].copy()
    var["current_water_fraction_r250"]=src["lst_night_K"]
    var["recent_wetness_3m_r250"]=np.nan
    var["hydro_sd_12m_r250"]=np.nan

    # Exposure rows originate only from the strict-coordinate focal universe.
    safe=set(src.loc[src.lst_night_K.notna(),"RouteNumber"].dropna().astype(str).unique())
    hyd.strict_routes=lambda:safe
    hyd.SEEDS["M0"]=2840350
    hyd.SEEDS["M1"]=2840351

    raw,runs,psub,dsub,hsub,pools,sampled,ss=flex.prepare_subset()
    p,d,h,lst,site,safe2,fail=hyd.build_complete_sample(raw,runs,psub,dsub,hsub,var,"M1")
    gate=bool(len(p)>=1500 and p.route_cluster.nunique()>=300 and p.State.nunique()>=15)
    out["analysis_sample"]={
      "pairs":int(len(p)),"routes":int(p.route_cluster.nunique()) if len(p) else 0,
      "states":int(p.State.nunique()) if len(p) else 0,"failures":fail,"gate_pass":gate
    }
    if not gate:
        out["classification"]="night_lst_analysis_sample_inconclusive"
        OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
        print(json.dumps(out,indent=2,sort_keys=True));return

    out["frog_endpoint_read"]=True
    res=hyd.analyze_sample(
      f"MOD11A1 nighttime LST rule {rule}",
      p,d,h,lst,runs,sampled,ss,pools,("M0","M1")
    )
    m0=res["models"]["M0"];m1=res["models"]["M1"]
    frac=res["fraction_removed_current"]
    sufficient=bool(res["M1_sufficient"])
    out.update({
      "observed":res["observed"],
      "models":{"M0":m0,"M_LST":m1},
      "fraction_residual_removed":frac,
      "LST_sufficient":sufficient,
      "thermal_shift_audit":{
        "M_LST":res["hydrology_shift_audit"]["M1"]
      },
      "thermal_training":{
        "M_LST":res["hydrology_training"]["M1"]
      },
      "classification":"night_lst_filter_sufficient" if sufficient else ("night_lst_filter_partial" if frac is not None and frac>0 else "night_lst_filter_not_supported"),
      "interpretation_boundary":{
        "nighttime_land_surface_temperature":True,
        "water_temperature_measured":False,
        "reproductive_success_inferred":False,
        "unique_causal_mediation_proven":False
      }
    })
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps({
      "analysis":out["analysis"],"coverage":cov,"analysis_sample":out["analysis_sample"],
      "observed":out["observed"],"models":out["models"],
      "fraction_residual_removed":frac,"classification":out["classification"]
    },indent=2,sort_keys=True))

if __name__=="__main__":main()
