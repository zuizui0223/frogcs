#!/usr/bin/env python3
from __future__ import annotations
import importlib.util, json
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parent

def loadmod(name,path):
    s=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(s)
    assert s.loader
    s.loader.exec_module(m)
    return m

meta=loadmod("meta",ROOT/"run_naamp_metacommunity_alpha_beta_gamma.py")
RESPONSES=["delta_active_stops","delta_alpha_active","delta_gamma"]

def fitset(d):
    out={}
    for r in RESPONSES:
        out[r]=meta.fit(d,r)
    return {
        "n_pairs":int(len(d)),
        "n_routes":int(d.route_cluster.nunique()),
        "n_states":int(d.State.nunique()),
        "models":out
    }

def main():
    d=meta.build()
    primary=d[d["dry_days_since_rain"]>=4].copy()
    outside=d[d["wet_days_since_rain"]>=4].copy()

    p=fitset(primary)
    b=fitset(outside)

    p_all_positive=all(p["models"][r]["beta_rain_contrast"]>0 for r in RESPONSES)
    p_all_ci_positive=all(p["models"][r]["ci95"][0]>0 for r in RESPONSES)

    result={
      "analysis":"rc7_protocol_window_sensitivity_v0_1",
      "contract":"provenance/CURRENT_ANALYSIS_SPECIFICATIONS.json#items/NAAMP_PROTOCOL_WINDOW_SENSITIVITY_CONTRACT_V0_1",
      "source_pairs":int(len(d)),
      "primary_crosses_three_day_window":p,
      "secondary_both_outside_three_day_window":b,
      "decision":{
        "pass":bool(p_all_positive),
        "strong_pass":bool(p_all_ci_positive),
        "primary_rule":"dry_days_since_rain >= 4",
        "secondary_rule":"wet_days_since_rain >= 4"
      },
      "boundaries":{
        "causal_claim_authorized":False,
        "protocol_selection_eliminated":False,
        "state_protocol_membership_inferred":False,
        "endpoint_retuning_after_readback_authorized":False
      }
    }
    Path("provenance/receipts/NAAMP_PROTOCOL_WINDOW_SENSITIVITY_RECEIPT_V0_1.json").write_text(
      json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8"
    )
    print(json.dumps(result,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
