#!/usr/bin/env python3
"""Summarize the frozen E3 same-scene *metadata* necessary gate only."""
from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
EXP=ROOT/"exploration"
RS=ROOT/"scripts"/"remotesensing"
INDIR=Path(os.environ.get("E3_SHARD_DIR",
    str(ROOT/"remotesensing"/"e3_ndmi_shard_inputs")))
OUT=ROOT/"remotesensing"/"E3_NDMI_METADATA_COVERAGE_V0_1.json"

def loadmod(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(m)
    return m

flex=loadmod("flex",EXP/"run_naamp_flexible_common_environment_null.py")
hyd=loadmod("hyd",RS/"run_naamp_dynamic_hydrology_mechanism.py")
mem=flex.mem

files=sorted(INDIR.glob("e3_ndmi_metadata_shard_*.json"))
if len(files)!=8:
    raise RuntimeError(f"expected 8 E3 metadata shards, got {len(files)}")

rows=[]
counts=set()
for f in files:
    obj=json.loads(f.read_text())
    if obj.get("analysis")!="naamp_e3_ndmi_metadata_shard_v0_1":
        raise RuntimeError("E3_metadata_shard_identity_drift")
    counts.add(int(obj["frozen_principal_pairs_total"]))
    rows.extend(obj["rows"])

if len(counts)!=1:
    raise RuntimeError("frozen_pair_population_mismatch")
byrun={str(r["RunID"]):r for r in rows}
if len(byrun)!=len(rows):
    raise RuntimeError("duplicated_focal_RunID")

raw,runs,psub,dsub,hsub,pools,sampled,ss=flex.prepare_subset()
if len(psub)!=next(iter(counts)):
    raise RuntimeError("frozen_principal_pair_count_drift")
site=mem.site_map(raw,set(runs.RunID.astype(str)))
safe=hyd.strict_routes()
pairs=[]
for p,dct in zip(psub.itertuples(index=False),dsub):
    if str(p.RouteNumber) not in safe:
        continue
    ids=mem.focal_siteids(p,dct,site)
    if ids is None or len(ids)!=10:
        continue
    wr,dr=str(p.wet_RunID),str(p.dry_RunID)
    if wr not in byrun or dr not in byrun:
        continue
    pair={
        "State":str(p.State),"route_cluster":str(p.route_cluster),
        "wet_RunID":wr,"dry_RunID":dr
    }
    wet,dry=byrun[wr],byrun[dr]
    pair["confirmed"]=bool(
        wet["resolved"] and dry["resolved"]
        and wet["all10_one_product_candidate"]
        and dry["all10_one_product_candidate"]
    )
    pair["possible"]=bool(
        (not wet["resolved"] or wet["all10_one_product_candidate"])
        and (not dry["resolved"] or dry["all10_one_product_candidate"])
    )
    pairs.append(pair)

confirmed=[p for p in pairs if p["confirmed"]]
possible=[p for p in pairs if p["possible"]]
def summary(z):
    return {"pairs":len(z),
      "routes":len({p["route_cluster"] for p in z}),
      "states":len({p["State"] for p in z})}
def gate(z):
    x=summary(z)
    return bool(x["pairs"]>=1500 and x["routes"]>=300 and x["states"]>=15)

lower=summary(confirmed)
upper=summary(possible)
if gate(confirmed):
    cls="metadata_necessary_gate_pass"
elif not gate(possible):
    cls="E3_remote_moisture_coverage_inconclusive_metadata_upper_bound"
else:
    cls="metadata_unresolved"

out={
  "analysis":"naamp_e3_ndmi_metadata_coverage_v0_1",
  "contract":"revision/NAAMP_E3_NDMI_METADATA_COVERAGE_CONTRACT_V0_1.md",
  "source_access_gate":"https://github.com/zuizui0223/frogcs/actions/runs/37711481855",
  "classification":cls,
  "frozen_principal_pairs":len(psub),
  "strict_geometry_pairs_with_metadata_run_identity":len(pairs),
  "unique_focal_runs":len(rows),
  "resolved_focal_runs":sum(bool(r["resolved"]) for r in rows),
  "all10_same_product_metadata_runs":sum(bool(r["all10_one_product_candidate"]) for r in rows),
  "unresolved_runs":sum(not bool(r["resolved"]) for r in rows),
  "footprint_bbox_fallback_count":sum(int(r["bbox_fallback_count"]) for r in rows),
  "confirmed_lower_bound":lower,
  "possible_upper_bound":upper,
  "thresholds":{"pairs":1500,"routes":300,"states":15},
  "pixel_QA_coverage_calculated":False,
  "NDMI_values_read":False,
  "frog_endpoint_calculated":False,
  "metadata_run_rows":rows,
}
OUT.parent.mkdir(parents=True,exist_ok=True)
OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
print(json.dumps({k:out[k] for k in out if k!="metadata_run_rows"},indent=2))
