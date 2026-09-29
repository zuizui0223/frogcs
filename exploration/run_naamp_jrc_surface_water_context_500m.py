#!/usr/bin/env python3
from __future__ import annotations
import importlib.util,json
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
EXP=ROOT/"exploration"
BASE=EXP/"run_naamp_jrc_surface_water_context.py"
OUT=EXP/"NAAMP_JRC_SURFACE_WATER_CONTEXT_500M_RECEIPT_V0_1.json"

def loadmod(name,path):
    s=importlib.util.spec_from_file_location(name,path); m=importlib.util.module_from_spec(s)
    assert s.loader; s.loader.exec_module(m); return m
basej=loadmod("jrc_base",BASE)

def main():
    raw=basej.base.load()
    runs,sets=basej.base.build_runs(raw)
    pairs,site,used=basej.pair_used_siteids(raw,runs,sets)
    coords=basej.load_coords()
    used_coord={s for s in used if s in coords}
    c500=basej.context_all(used_coord,coords,500)
    classified={s:m for s,m in c500.items() if m}
    pulse=np.asarray([100-m["mean_occurrence"] for m in classified.values()],float)
    rows=basej.response_rows(raw,runs,sets,site,c500,"mean_occurrence")
    pair_var=rows.groupby("pair_id")["pulse_raw"].std() if len(rows) else None
    if pair_var is not None:
        ids=pair_var[pair_var>1e-12].index
        informative=rows[rows.pair_id.isin(ids)]
    else:
        informative=rows
    coverage=len(classified)/len(used_coord) if used_coord else 0.0
    variation=float(np.std(pulse,ddof=0)) if len(pulse) else 0.0
    gate=bool(
        coverage>=.50 and variation>=10
        and informative.pair_id.nunique()>=1000
        and informative.route_cluster.nunique()>=300
    )
    out={
      "analysis":"naamp_jrc_surface_water_context_500m_v0_1",
      "contract":"exploration/NAAMP_JRC_SURFACE_WATER_CONTEXT_500M_CONTRACT_V0_1.json",
      "eligibility":{
        "pair_used_siteids":int(len(used)),
        "with_coordinates":int(len(used_coord)),
        "classified_500m":int(len(classified)),
        "coverage_500m":float(coverage),
        "pulse_index_sd":variation,
        "informative_pairs":int(informative.pair_id.nunique()) if len(informative) else 0,
        "informative_routes":int(informative.route_cluster.nunique()) if len(informative) else 0,
        "overall_pass":gate
      },
      "response_endpoints_read":False
    }
    if gate:
        primary=basej.fit(rows,"net_route_new")
        p90rows=basej.response_rows(raw,runs,sets,site,c500,"p90_occurrence")
        p90=basej.fit(p90rows,"net_route_new")
        out.update({
          "response_endpoints_read":True,
          "primary_500m_mean_occurrence":primary,
          "sensitivity_500m_p90_occurrence":p90,
          "classification":{"pulse_limited_recruitment_supported":bool(primary and primary["support"])}
        })
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,indent=2,sort_keys=True))
if __name__=="__main__": main()
