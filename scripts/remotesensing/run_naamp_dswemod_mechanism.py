#!/usr/bin/env python3
from __future__ import annotations
import hashlib, importlib.util, json, os
from pathlib import Path
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[2]
SCRIPT=ROOT/"scripts"/"remotesensing"/"run_naamp_dynamic_hydrology_mechanism.py"
INCSV=Path(os.environ.get(
    "NAAMP_DSWEMOD_CSV",
    str(ROOT/"remotesensing"/"NAAMP_DSWEMOD_RUN_SITE_METRICS_V0_1.csv")
))
OUT=ROOT/"remotesensing"/"NAAMP_DSWEMOD_MECHANISM_RECEIPT_V0_1.json"

def loadmod(name,path):
    s=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(s)
    assert s.loader
    s.loader.exec_module(m)
    return m

hyd=loadmod("hyd",SCRIPT)
flex=hyd.flex

def make_var(df,radius,full):
    out=df[["RunID","SiteID"]].copy()
    out["current_water_fraction_r250"]=pd.to_numeric(
        df[f"current_D_r{radius}"],errors="coerce"
    )
    if full:
        out["recent_wetness_3m_r250"]=pd.to_numeric(
            df[f"recent_D_3m_r{radius}"],errors="coerce"
        )
        out["hydro_sd_12m_r250"]=pd.to_numeric(
            df[f"DSWE_sd_12m_r{radius}"],errors="coerce"
        )
    else:
        out["recent_wetness_3m_r250"]=np.nan
        out["hydro_sd_12m_r250"]=np.nan
    return out

def coverage_of(p,fail):
    return {
      "pairs":int(len(p)),
      "routes":int(p.route_cluster.nunique()) if len(p) else 0,
      "states":int(p.State.nunique()) if len(p) else 0,
      "failures":fail,
      "gate_pass":bool(
          len(p)>=1500 and len(p)>0 and
          p.route_cluster.nunique()>=300 and p.State.nunique()>=15
      )
    }

def run_primary(df):
    raw,runs,psub,dsub,hsub,pools,sampled,ss=flex.prepare_subset()

    var1=make_var(df,500,False)
    p1,d1,h1,hyd1,site,safe,fail1=hyd.build_complete_sample(
        raw,runs,psub,dsub,hsub,var1,"M1"
    )
    cov1=coverage_of(p1,fail1)
    if not cov1["gate_pass"]:
        return {
          "M1_coverage":cov1,
          "M3_coverage":None,
          "frog_endpoint_read":False,
          "classification":"dswemod_primary_coverage_inconclusive"
        }

    var3=make_var(df,500,True)
    p3,d3,h3,hyd3,site,safe,fail3=hyd.build_complete_sample(
        raw,runs,psub,dsub,hsub,var3,"M3"
    )
    cov3=coverage_of(p3,fail3)

    if cov3["gate_pass"]:
        result=hyd.analyze_sample(
            "DSWEmod 500m M0-M3 common sample",
            p3,d3,h3,hyd3,runs,sampled,ss,pools,
            ("M0","M1","M2","M3")
        )
        decomp=result["residual_decomposition"]
        if result["M3_sufficient"]:
            cls="dswemod_dynamic_hydrology_sufficient"
        elif decomp["fraction_removed_total"] is not None and decomp["fraction_removed_total"]>0:
            cls="dswemod_dynamic_hydrology_partial"
        else:
            cls="dswemod_dynamic_hydrology_not_supported"
        return {
          "M1_coverage":cov1,
          "M3_coverage":cov3,
          "frog_endpoint_read":True,
          "full_sequence":result,
          "classification":cls
        }

    result=hyd.analyze_sample(
        "DSWEmod 500m current-state M0-M1 sample",
        p1,d1,h1,hyd1,runs,sampled,ss,pools,
        ("M0","M1")
    )
    frac=result["fraction_removed_current"]
    if result["M1_sufficient"]:
        cls="dswemod_current_sufficient_M3_inconclusive"
    elif frac is not None and frac>0:
        cls="dswemod_current_partial_M3_inconclusive"
    else:
        cls="dswemod_current_not_supported_M3_inconclusive"
    return {
      "M1_coverage":cov1,
      "M3_coverage":cov3,
      "frog_endpoint_read":True,
      "current_only":result,
      "classification":cls
    }

def run_250_sensitivity(df):
    raw,runs,psub,dsub,hsub,pools,sampled,ss=flex.prepare_subset()
    var=make_var(df,250,False)
    p,d,h,hydro,site,safe,fail=hyd.build_complete_sample(
        raw,runs,psub,dsub,hsub,var,"M1"
    )
    cov=coverage_of(p,fail)
    if not cov["gate_pass"]:
        return {
          "coverage":cov,
          "frog_endpoint_read":False,
          "classification":"dswemod_250m_coverage_inconclusive"
        }
    result=hyd.analyze_sample(
        "DSWEmod 250m current-state sensitivity",
        p,d,h,hydro,runs,sampled,ss,pools,
        ("M0","M1")
    )
    frac=result["fraction_removed_current"]
    if result["M1_sufficient"]:
        cls="dswemod_250m_sufficient"
    elif frac is not None and frac>0:
        cls="dswemod_250m_partial"
    else:
        cls="dswemod_250m_not_supported"
    return {
      "coverage":cov,
      "frog_endpoint_read":True,
      "result":result,
      "classification":cls
    }

def main():
    if not INCSV.exists():
        raise RuntimeError(f"missing DSWEmod run-site metrics: {INCSV}")
    df=pd.read_csv(INCSV)

    primary=run_primary(df)
    sensitivity=(
        run_250_sensitivity(df)
        if primary["M1_coverage"]["gate_pass"]
        else {"classification":"not_run_primary_gate_failed"}
    )

    out={
      "analysis":"naamp_dswemod_mechanism_v0_2",
      "contract":"revision/NAAMP_MODIS_DSWEMOD_SOURCE_REPAIR_V0_3.md",
      "source_csv_sha256":hashlib.sha256(INCSV.read_bytes()).hexdigest(),
      "primary_r500":primary,
      "sensitivity_r250":sensitivity,
      "interpretation_boundary":{
        "product":"USGS monthly MODIS DSWEmod 250-m; not Landsat C2L3 DSWE",
        "positive_classes_primary":[1,2,3],
        "reproductive_acoustic_activity":True,
        "reproductive_success_inferred":False,
        "causal_mediation_proven":False
      }
    }
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps({
      "analysis":out["analysis"],
      "primary_r500":primary,
      "sensitivity_r250":sensitivity
    },indent=2,sort_keys=True))

if __name__=="__main__":
    main()
