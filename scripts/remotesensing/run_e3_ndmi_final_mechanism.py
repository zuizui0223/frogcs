#!/usr/bin/env python3
"""Frozen E3 M0/M_NDMI mechanism — read no frog endpoint unless QA gate passes."""
from __future__ import annotations
import hashlib,importlib.util,json,os
from pathlib import Path
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[2]
EXP=ROOT/"exploration"
RS=ROOT/"scripts"/"remotesensing"
GATE=Path(os.environ.get("E3_PIXEL_GATE_PATH",str(ROOT/"remotesensing"/"E3_NDMI_FINAL_PIXEL_COVERAGE_V0_1.json")))
SOURCE=Path(os.environ.get("E3_NDMI_TABLE",str(ROOT/"remotesensing"/"NAAMP_E3_NDMI_RUN_SITE_V0_1.csv")))
RECEIPT=Path(os.environ.get("E3_EXPOSURE_RECEIPT",str(ROOT/"remotesensing"/"NAAMP_E3_NDMI_EXTRACTED_COVERAGE_V0_1.json")))
OUT=ROOT/"remotesensing"/"NAAMP_E3_NDMI_MECHANISM_RECEIPT_V0_1.json"
CONTRACT="revision/NAAMP_E3_LANDSAT_NDMI_FINAL_ABIOTIC_CONTRACT_V0_1.md"

def loadmod(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(spec)
    assert spec.loader;spec.loader.exec_module(m);return m

if not GATE.exists():raise RuntimeError("E3_QA_gate_missing")
gate_bytes=GATE.read_bytes();gate=json.loads(gate_bytes)
out={"analysis":"naamp_e3_ndmi_final_mechanism_v0_1","contract":CONTRACT,
     "pixel_gate_classification":gate.get("classification"),
     "pixel_gate_sha256":hashlib.sha256(gate_bytes).hexdigest(),
     "frog_endpoint_read":False}
if gate.get("classification")!="E3_pixel_QA_coverage_gate_pass":
    out["classification"]="E3_remote_moisture_coverage_inconclusive"
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,indent=2,sort_keys=True))
    raise SystemExit(0)

if not SOURCE.exists() or not RECEIPT.exists():
    raise RuntimeError("E3_passed_but_exposure_missing")
receipt=json.loads(RECEIPT.read_text())
if receipt.get("pixel_gate_sha256")!=hashlib.sha256(gate_bytes).hexdigest():
    raise RuntimeError("E3_extraction_gate_hash_mismatch")
if receipt.get("exposure_sha256")!=hashlib.sha256(SOURCE.read_bytes()).hexdigest():
    raise RuntimeError("E3_extraction_table_hash_mismatch")
if receipt.get("frog_endpoint_calculated") is not False:
    raise RuntimeError("wrong_pre_endpoint_E3_artifact")
df=pd.read_csv(SOURCE,dtype={"RunID":str,"SiteID":str})
if df.duplicated(["RunID","SiteID"]).any():raise RuntimeError("duplicate_E3_NDMI_site")
vals=pd.to_numeric(df["NDMI_r500"],errors="coerce")
if not np.isfinite(vals).all() or not vals.between(-1,1).all():
    raise RuntimeError("unphysical_E3_NDMI")

# Common generator implementation is independent of the meaning of covariate H.
# Adapter uses the software's historical H field name only at the API boundary.
# H is *NDMI*, never water fraction, throughout this test and its reporting.
var=df[["RunID","SiteID"]].copy()
var["current_water_fraction_r250"]=vals
var["recent_wetness_3m_r250"]=np.nan
var["hydro_sd_12m_r250"]=np.nan

hyd=loadmod("hyd",RS/"run_naamp_dynamic_hydrology_mechanism.py")
flex=hyd.flex
raw,runs,psub,dsub,hsub,pools,sampled,ss=flex.prepare_subset()
p,d,h,exposures,site,safe,fail=hyd.build_complete_sample(
    raw,runs,psub,dsub,hsub,var,"M1")
cov={"pairs":int(len(p)), "routes":int(p.route_cluster.nunique()) if len(p) else 0,
     "states":int(p.State.nunique()) if len(p) else 0,"missingness":fail}
out["coverage"]=cov
out["exposure_sha256"]=hashlib.sha256(SOURCE.read_bytes()).hexdigest()
lower=gate.get("confirmed_coverage") or {}
if (cov["pairs"],cov["routes"],cov["states"]) != (
    int(lower.get("pairs",-1)),int(lower.get("routes",-1)),int(lower.get("states",-1))):
    raise RuntimeError("E3_QA_and_mechanism_population_drift")
if cov["pairs"]<1500 or cov["routes"]<300 or cov["states"]<15:
    out["classification"]="E3_remote_moisture_coverage_inconclusive"
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,indent=2,sort_keys=True))
    raise SystemExit(0)

# This is the sole boundary at which the frozen frog concentration outcome is evaluated.
out["frog_endpoint_read"]=True
result=hyd.analyze_sample(
   "E3 Landsat NDMI 500m, frozen pixel-QA sample",
    p,d,h,exposures,runs,sampled,ss,pools,("M0","M1"))
m0=result["models"]["M0"];m1=result["models"]["M1"]
raw_fraction=result["fraction_removed_current"]
fraction=float(raw_fraction) if raw_fraction is not None else None
suff=bool(result["M1_sufficient"])
out.update({
 "observed_concentration_beta":float(result["observed"]["concentration_beta"]),
 "models":{"M0":m0,"M_E3_NDMI":m1},
 "fraction_residual_removed":fraction,
 "E3_sufficient":suff,
 "classification":("E3_local_vegetation_moisture_sufficient" if suff
     else "E3_residual_denominator_indeterminate" if fraction is None
     else "E3_local_vegetation_moisture_partial" if fraction>0
     else "E3_local_vegetation_moisture_not_supported"),
 "interpretation_boundary":{
  "predictor":"Landsat spectral vegetation moisture NDMI, not soil moisture or water depth",
  "route_fold_crossfit":True,"same_sample_comparison":True,
  "causal_mediation_proven":False,"reproductive_success_inferred":False
 }
})
OUT.parent.mkdir(exist_ok=True)
OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
print(json.dumps({k:v for k,v in out.items() if k not in ("hydrology_training",)},indent=2,sort_keys=True))
