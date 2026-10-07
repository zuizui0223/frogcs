#!/usr/bin/env python3
from __future__ import annotations
import json, os
from pathlib import Path

INDIR=Path(os.environ.get("DSWE_COVERAGE_SHARD_DIR","remotesensing/dswe_coverage_inputs"))
OUT=Path("remotesensing/NAAMP_DSWE_METADATA_COVERAGE_V0_1.json")

files=sorted(INDIR.glob("dswe_metadata_coverage_shard_*.json"))
if len(files)!=16:
    raise RuntimeError(f"expected 16 shards, found {len(files)}")
rows=[]
for p in files:
    x=json.loads(p.read_text())
    rows.extend(x["rows"])

byrun={r["RunID"]:r for r in rows}
if len(byrun)!=len(rows):
    raise RuntimeError("duplicate RunID across DSWE coverage shards")

# Reconstruct pair completion using wet/dry RunIDs recorded in the frozen principal-pair universe
# by importing the same response-blind pair constructor and strict coordinate gate.
import importlib.util
ROOT=Path(__file__).resolve().parents[2]
EXP=ROOT/"exploration"; RS=ROOT/"scripts"/"remotesensing"
def loadmod(name,path):
    s=importlib.util.spec_from_file_location(name,path); m=importlib.util.module_from_spec(s); assert s.loader; s.loader.exec_module(m); return m
flex=loadmod("flex",EXP/"run_naamp_flexible_common_environment_null.py")
hyd=loadmod("hyd",RS/"run_naamp_dynamic_hydrology_mechanism.py")
mem=flex.mem

raw,runs,psub,dsub,hsub,pools,sampled,ss=flex.prepare_subset()
eligible=set(runs.RunID.astype(str)); site=mem.site_map(raw,eligible); safe=hyd.strict_routes()
pairs=[]
for p,dct in zip(psub.itertuples(index=False),dsub):
    if str(p.RouteNumber) not in safe: continue
    ids=mem.focal_siteids(p,dct,site)
    if ids is None or len(ids)!=10: continue
    wr,dr=str(p.wet_RunID),str(p.dry_RunID)
    if wr not in byrun or dr not in byrun: continue
    pairs.append({
      "route_cluster":str(p.route_cluster),"State":str(p.State),
      "wet_RunID":wr,"dry_RunID":dr,
      "complete":bool(byrun[wr]["all10_metadata_candidate"] and byrun[dr]["all10_metadata_candidate"])
    })

complete=[p for p in pairs if p["complete"]]
all_lags=[]
for r in rows:
    all_lags.extend([v for v in r["nearest_lag_days"].values() if v is not None])

payload={
 "analysis":"naamp_dswe_metadata_coverage_v0_1",
 "contract":"revision/NAAMP_LANDSAT_DSWE_MECHANISM_CONTRACT_V0_1.md",
 "lookback_days":16,
 "unique_focal_runs":len(rows),
 "runs_all10_metadata_candidate":sum(bool(r["all10_metadata_candidate"]) for r in rows),
 "run_candidate_fraction":sum(bool(r["all10_metadata_candidate"]) for r in rows)/len(rows) if rows else None,
 "strict_geometry_pairs_with_run_metadata":len(pairs),
 "metadata_complete_pairs":len(complete),
 "metadata_complete_routes":len({p["route_cluster"] for p in complete}),
 "metadata_complete_states":len({p["State"] for p in complete}),
 "coverage_gate_thresholds":{"pairs":1500,"routes":300,"states":15},
 "metadata_gate_pass":bool(len(complete)>=1500 and len({p["route_cluster"] for p in complete})>=300 and len({p["State"] for p in complete})>=15),
 "nearest_candidate_lag_days":{
    "n":len(all_lags),
    "median":float(__import__("numpy").median(all_lags)) if all_lags else None,
    "q90":float(__import__("numpy").quantile(all_lags,.9)) if all_lags else None,
    "max":int(max(all_lags)) if all_lags else None
 },
 "frog_endpoint_values_emitted":False,
 "dswe_raster_values_read":False
}
OUT.parent.mkdir(exist_ok=True)
OUT.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n")
print(json.dumps(payload,indent=2,sort_keys=True))
