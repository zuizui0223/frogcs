#!/usr/bin/env python3
"""E3 NDMI formal response-blind pixel-coverage decision.

No NDMI and no CallingIndex endpoint are calculated here.
"""
from __future__ import annotations
import hashlib, importlib.util, json, os
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
EXP=ROOT/"exploration"
RS=ROOT/"scripts"/"remotesensing"
INDIR=Path(os.environ.get("E3_PIXEL_SHARD_DIR",
    str(ROOT/"remotesensing"/"e3_pixel_inputs")))
META=Path(os.environ.get("E3_METADATA_PATH",
    str(ROOT/"remotesensing"/"E3_NDMI_METADATA_COVERAGE_V0_1.json")))
OUT=ROOT/"remotesensing"/"E3_NDMI_FINAL_PIXEL_COVERAGE_V0_1.json"

def loadmod(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(spec); assert spec.loader; spec.loader.exec_module(m)
    return m

source=META.read_bytes()
meta=json.loads(source)
if meta.get("classification")!="metadata_necessary_gate_pass":
    raise RuntimeError("E3_metadata_gate_not_passed")
files=sorted(INDIR.glob("e3_ndmi_final_pixel_qa_shard_*.json"))
if len(files)!=16:
    raise RuntimeError("expected_16_completed_pixel_shards_found_"+str(len(files)))
rows=[]
idxs=set()
for path in files:
    obj=json.loads(path.read_text())
    if obj.get("analysis")!="e3_ndmi_final_pixel_qa_shard_v0_1":
        raise RuntimeError("wrong_pixel_receipt:"+str(path))
    if obj.get("diagnostic_run_limit")!=0:
        raise RuntimeError("diagnostic_shard_cannot_enter_formal_gate")
    if obj.get("source_metadata_sha256")!=hashlib.sha256(source).hexdigest():
        raise RuntimeError("metadata_source_drift")
    if int(obj["shard_count"])!=16:
        raise RuntimeError("pixel_shard_count_drift")
    i=int(obj["shard_index"])
    if i in idxs: raise RuntimeError("duplicate_shard")
    idxs.add(i)
    rows.extend(obj["rows"])
if idxs!=set(range(16)):raise RuntimeError("missing_shard_identity")
byrun={str(r["RunID"]):r for r in rows}
if len(byrun)!=len(rows):raise RuntimeError("duplicate_RunID")
mids={str(r["RunID"]) for r in meta["metadata_run_rows"]}
if set(byrun)!=mids:raise RuntimeError("coverage_identity_mismatch")

flex=loadmod("flex",EXP/"run_naamp_flexible_common_environment_null.py")
hyd=loadmod("hyd",RS/"run_naamp_dynamic_hydrology_mechanism.py")
mem=flex.mem
raw,runs,psub,dsub,hsub,pools,sampled,ss=flex.prepare_subset()
site=mem.site_map(raw,set(runs.RunID.astype(str)))
safe=hyd.strict_routes()
pairs=[]
for p,dct in zip(psub.itertuples(index=False),dsub):
    if str(p.RouteNumber) not in safe:continue
    ids=mem.focal_siteids(p,dct,site)
    if ids is None or len(ids)!=10:continue
    wet,dry=str(p.wet_RunID),str(p.dry_RunID)
    if wet not in byrun or dry not in byrun:raise RuntimeError("missing_run")
    pairs.append({"State":str(p.State),"route_cluster":str(p.route_cluster),
                  "wet_RunID":wet,"dry_RunID":dry})

def count_pairs(pred):
    a=[p for p in pairs if pred(byrun[p["wet_RunID"]]) and pred(byrun[p["dry_RunID"]])]
    return {"pairs":len(a),"routes":len({x["route_cluster"] for x in a}),
            "states":len({x["State"] for x in a})}
def pass_gate(c):
    return c["pairs"]>=1500 and c["routes"]>=300 and c["states"]>=15

lower=count_pairs(lambda r:r["status"]=="qa_pass")
upper=count_pairs(lambda r:r["status"] in ("qa_pass","source_unresolved"))
if pass_gate(lower):
    classification="E3_pixel_QA_coverage_gate_pass"
elif not pass_gate(upper):
    classification="E3_remote_moisture_coverage_inconclusive"
else:
    classification="E3_public_asset_access_inconclusive"

receipt={
 "analysis":"e3_ndmi_final_pixel_coverage_v0_1",
 "contract":"revision/NAAMP_E3_LANDSAT_NDMI_FINAL_ABIOTIC_CONTRACT_V0_1.md",
 "source_metadata_sha256":hashlib.sha256(source).hexdigest(),
 "classification":classification,
 "status_counts":dict(Counter(z["status"] for z in rows)),
 "source_error_attempts":sum(int(z.get("source_errors",0)) for z in rows),
 "qa_evaluated_scenes":sum(int(z.get("qa_evaluated",0)) for z in rows),
 "confirmed_coverage":lower,"possible_coverage":upper,
 "thresholds":{"pairs":1500,"routes":300,"states":15},
 "pixel_QA_calculated":True,
 "NDMI_values_read":False,"frog_endpoint_calculated":False,
 "selected_run_rows":[z for z in rows if z["status"]=="qa_pass"]
}
OUT.parent.mkdir(exist_ok=True)
OUT.write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n")
print(json.dumps({k:v for k,v in receipt.items() if k!="selected_run_rows"},indent=2))
