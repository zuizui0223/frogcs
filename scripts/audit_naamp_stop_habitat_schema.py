#!/usr/bin/env python3
from __future__ import annotations
import importlib.util, json
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("pulse",ROOT/"run_naamp_ecological_pulse.py")
base=importlib.util.module_from_spec(spec);assert spec.loader;spec.loader.exec_module(base)

def summarize(rows):
    fields=list(rows[0].keys()) if rows else []
    out={}
    for c in fields:
        vals=[str(r.get(c) or "").strip() for r in rows]
        non=[x for x in vals if x!=""]
        ctr=Counter(non)
        out[c]={
          "nonempty":len(non),
          "n_unique_nonempty":len(ctr),
          "top_values":[{"value":k,"n":v} for k,v in ctr.most_common(8)]
        }
    return {"fields":fields,"field_summary":out}

def main():
    raw=base.load()
    result={
      "analysis":"naamp_stop_habitat_schema_audit_v0_1",
      "Stops.csv":summarize(raw["Stops.csv"]),
      "Runs.csv":summarize(raw["Runs.csv"]),
      "outcome_models_fit":False
    }
    Path("NAAMP_STOP_HABITAT_SCHEMA_AUDIT_V0_1.json").write_text(
      json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2,sort_keys=True))
if __name__=="__main__":main()
