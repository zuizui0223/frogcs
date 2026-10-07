#!/usr/bin/env python3
from __future__ import annotations
import hashlib, importlib.util, json, os
from pathlib import Path
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[2]
EXP=ROOT/"exploration"
SCRIPT=ROOT/"scripts"/"remotesensing"/"run_naamp_dynamic_hydrology_mechanism.py"
INCSV=Path(os.environ.get("NAAMP_DSWEMOD_CSV",str(ROOT/"remotesensing"/"NAAMP_DSWEMOD_EXPOSURES_V0_1.csv")))
OUT=ROOT/"remotesensing"/"NAAMP_DSWEMOD_MECHANISM_RECEIPT_V0_1.json"

def loadmod(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);assert s.loader;s.loader.exec_module(m);return m

hyd=loadmod("hyd",SCRIPT)
flex=hyd.flex
mem=hyd.mem
joint=hyd.joint
uniform=hyd.uniform

def make_var(df,radius):
    out=df[["RunID","SiteID"]].copy()
    out["current_water_fraction_r250"]=pd.to_numeric(df[f"dswemod123_r{radius}"],errors="coerce")
    out["recent_wetness_3m_r250"]=np.nan
    out["hydro_sd_12m_r250"]=np.nan
    return out

def analyze_radius(df,radius):
    var=make_var(df,radius)
    raw,runs,psub,dsub,hsub,pools,sampled,ss=flex.prepare_subset()
    p1,d1,h1,hyd1,site,safe,fail1=hyd.build_complete_sample(raw,runs,psub,dsub,hsub,var,"M1")
    gate=bool(len(p1)>=1500 and len(p1)>0 and p1.route_cluster.nunique()>=300 and p1.State.nunique()>=15)
    cov={"pairs":int(len(p1)),"routes":int(p1.route_cluster.nunique()) if len(p1) else 0,
         "states":int(p1.State.nunique()) if len(p1) else 0,"failures":fail1,"gate_pass":gate}
    if not gate:
        return {"coverage":cov,"classification":"coverage_inconclusive","frog_endpoint_read":False}
    result=hyd.analyze_sample(f"DSWEmod r{radius}",p1,d1,h1,hyd1,runs,sampled,ss,pools,("M0","M1"))
    frac=result["fraction_removed_current"]
    if result["M1_sufficient"]:
        cls="dswemod_sufficient"
    elif frac is not None and frac>0:
        cls="dswemod_partial"
    else:
        cls="dswemod_not_supported"
    return {"coverage":cov,"frog_endpoint_read":True,"result":result,"classification":cls}

def main():
    if not INCSV.exists():raise RuntimeError(f"missing {INCSV}")
    df=pd.read_csv(INCSV)
    primary=analyze_radius(df,500)
    sensitivity=analyze_radius(df,250) if primary["coverage"]["gate_pass"] else {"classification":"not_run_primary_gate_failed"}
    out={
      "analysis":"naamp_dswemod_mechanism_v0_1",
      "contract":"revision/NAAMP_MODIS_DSWEMOD_MECHANISM_CONTRACT_V0_1.md",
      "source_csv_sha256":hashlib.sha256(INCSV.read_bytes()).hexdigest(),
      "primary_r500":primary,
      "sensitivity_r250":sensitivity,
      "interpretation_boundary":{
        "product":"MODIS DSWEmod monthly 250-m, not Landsat C2L3 DSWE",
        "reproductive_acoustic_activity":True,
        "reproductive_success_inferred":False,
        "causal_mediation_proven":False
      }
    }
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    summary={"analysis":out["analysis"],"primary_r500":primary,"sensitivity_r250":sensitivity}
    print(json.dumps(summary,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
