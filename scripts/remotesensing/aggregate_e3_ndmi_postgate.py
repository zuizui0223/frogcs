#!/usr/bin/env python3
"""Combine only frozen E3 NDMI pixel-QA-qualified extraction shards.

No frog concentration endpoint is calculated. Gate and artifact identity
must be exact before any NDMI table is authorized downstream.
"""
from __future__ import annotations
import hashlib,json,os
from pathlib import Path
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[2]
INDIR=Path(os.environ.get("E3_EXTRACTION_DIR",str(ROOT/"remotesensing"/"e3_extracted_inputs")))
GATE=Path(os.environ.get("E3_PIXEL_GATE_PATH",str(ROOT/"remotesensing"/"E3_NDMI_FINAL_PIXEL_COVERAGE_V0_1.json")))
OUTCSV=ROOT/"remotesensing"/"NAAMP_E3_NDMI_RUN_SITE_V0_1.csv"
OUTJSON=ROOT/"remotesensing"/"NAAMP_E3_NDMI_EXTRACTED_COVERAGE_V0_1.json"

if not GATE.exists():raise RuntimeError("frozen_E3_pixel_gate_missing")
b=GATE.read_bytes();gate=json.loads(b)
if gate.get("classification")!="E3_pixel_QA_coverage_gate_pass":
    raise RuntimeError("E3_pixel_gate_not_passed")
expected={str(r["RunID"]) for r in gate.get("selected_run_rows",[])}
if not expected:raise RuntimeError("empty_QA_qualified_run_set")

files=sorted(INDIR.glob("E3_NDMI_RUN_SITE_SHARD_*.csv"))
receipts=sorted(INDIR.glob("E3_NDMI_RUN_SITE_SHARD_*.json"))
if len(files)!=16 or len(receipts)!=16:
    raise RuntimeError(f"requires_all_16_extraction_shards:csv={len(files)},receipts={len(receipts)}")
gsha=hashlib.sha256(b).hexdigest()
seen=set();frames=[]
for path in receipts:
    z=json.loads(path.read_text())
    if z.get("analysis")!="e3_ndmi_outcome_blind_extraction_shard_v0_1":
        raise RuntimeError("wrong_shard_receipt")
    if z.get("pixel_coverage_sha256")!=gsha or z.get("shards")!=16:
        raise RuntimeError("frozen_QA_receipt_drift")
    k=int(z["shard"])
    if k in seen:raise RuntimeError("duplicate_shard")
    seen.add(k)
    p=INDIR/f"E3_NDMI_RUN_SITE_SHARD_{k:02d}.csv"
    if not p.exists() or hashlib.sha256(p.read_bytes()).hexdigest()!=z["csv_sha256"]:
        raise RuntimeError("shard_content_hash_mismatch")
    f=pd.read_csv(p,dtype={"RunID":str,"SiteID":str})
    if len(f)!=int(z["rows"]):raise RuntimeError("shard_row_count_mismatch")
    frames.append(f)
if seen!=set(range(16)):raise RuntimeError("missing_E3_shards")
df=pd.concat(frames,ignore_index=True)
if df.duplicated(["RunID","SiteID"]).any():raise RuntimeError("duplicate_run_site")
if set(df.RunID)!=expected:raise RuntimeError("selected_run_set_mismatch")
nper=df.groupby("RunID").SiteID.nunique()
if len(df)!=10*len(expected) or not (nper==10).all():
    raise RuntimeError("E3_not_ten_valid_stops_per_run")
ndmi=pd.to_numeric(df.NDMI_r500,errors="coerce")
frac=pd.to_numeric(df.valid_pixel_fraction,errors="coerce")
if not np.isfinite(ndmi).all() or not ndmi.between(-1,1).all():
    raise RuntimeError("invalid_NDMI_values")
if not np.isfinite(frac).all() or (frac<.70).any():
    raise RuntimeError("pixel_quality_regression")
# Explicitly retain semantic NDMI column. No relabelling as surface water.
df=df.sort_values(["RunID","SiteID"]).reset_index(drop=True)
OUTCSV.parent.mkdir(exist_ok=True)
df.to_csv(OUTCSV,index=False,float_format="%.9g")
receipt={
 "analysis":"naamp_e3_ndmi_extracted_coverage_v0_1",
 "contract":"revision/NAAMP_E3_LANDSAT_NDMI_FINAL_ABIOTIC_CONTRACT_V0_1.md",
 "pixel_gate_sha256":gsha,
 "source":"USGS Landsat C2 Level-2 Surface Reflectance NDMI",
 "source_data":"post-QA selected 500m site medians, 70%-valid, pre-survey 32d",
 "extracted_runids":len(expected),"extracted_run_site_rows":len(df),
 "ndmi_min":float(ndmi.min()),"ndmi_max":float(ndmi.max()),
 "min_valid_pixel_fraction":float(frac.min()),
 "exposure_sha256":hashlib.sha256(OUTCSV.read_bytes()).hexdigest(),
 "frog_endpoint_calculated":False
}
OUTJSON.write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n")
print(json.dumps(receipt,indent=2,sort_keys=True))
