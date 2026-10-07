#!/usr/bin/env python3
from __future__ import annotations
import hashlib, importlib.util, json, os
from pathlib import Path
import pandas as pd

ROOT=Path(__file__).resolve().parents[2]
RS=ROOT/"scripts"/"remotesensing"
EXP=ROOT/"exploration"
INCSV=Path(os.environ.get("NAAMP_DSWEMOD_1234_CSV",str(ROOT/"remotesensing"/"NAAMP_DSWEMOD_1234_CURRENT_SECONDARY_INPUT.csv")))
OUT=ROOT/"remotesensing"/"NAAMP_DSWEMOD_1234_SECONDARY_RECEIPT_V0_1.json"

def loadmod(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);assert s.loader;s.loader.exec_module(m);return m
hyd=loadmod("hyd",RS/"run_naamp_dynamic_hydrology_mechanism.py")
flex=hyd.flex

def main():
    if not INCSV.exists(): raise RuntimeError(f"missing {INCSV}")
    var=pd.read_csv(INCSV)
    raw,runs,psub,dsub,hsub,pools,sampled,ss=flex.prepare_subset()
    p,d,h,hh,site,safe,fail=hyd.build_complete_sample(raw,runs,psub,dsub,hsub,var,"M1")
    cov={
      "pairs":int(len(p)),
      "routes":int(p.route_cluster.nunique()) if len(p) else 0,
      "states":int(p.State.nunique()) if len(p) else 0,
      "failures":fail
    }
    gate=bool(cov["pairs"]>=1500 and cov["routes"]>=300 and cov["states"]>=15)
    out={
      "analysis":"naamp_dswemod_1234_secondary_v0_1",
      "contract":"revision/NAAMP_DSWEMOD_1234_SECONDARY_V0_1.md",
      "source_csv_sha256":hashlib.sha256(INCSV.read_bytes()).hexdigest(),
      "coverage":{**cov,"gate_pass":gate},
      "frog_endpoint_read":False
    }
    if not gate:
        out["classification"]="dswemod_1234_secondary_coverage_inconclusive"
    else:
        out["frog_endpoint_read"]=True
        res=hyd.analyze_sample("DSWEmod 1234 500m current-state secondary",p,d,h,hh,runs,sampled,ss,pools,("M0","M1"))
        frac=res["fraction_removed_current"]
        if res["M1_sufficient"]:
            cls="dswemod_1234_secondary_sufficient"
        elif frac is not None and frac>0:
            cls="dswemod_1234_secondary_partial"
        else:
            cls="dswemod_1234_secondary_not_supported"
        out.update({
          "result":res,
          "classification":cls,
          "interpretation_boundary":{
            "secondary_only":True,
            "cannot_replace_classes_123_primary":True,
            "positive_classes":[1,2,3,4]
          }
        })
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,indent=2,sort_keys=True))
if __name__=="__main__": main()
