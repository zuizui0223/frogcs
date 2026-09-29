#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
import importlib.util

ROOT=Path(__file__).resolve().parents[1]
NAAMP=ROOT/"scripts"/"naamp"
OUT=ROOT/"exploration"/"NAAMP_STOP_CONTEXT_SCHEMA_RECEIPT_V0_1.json"

def loadmod(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    mod=importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(mod)
    return mod

base=loadmod("pulse_base",NAAMP/"run_naamp_ecological_pulse.py")

def main():
    raw=base.load()
    report={}
    for name,rows in raw.items():
        keys=sorted({k for row in rows for k in row})
        report[name]={
            "n_rows":len(rows),
            "columns":keys,
            "context_candidates":[k for k in keys if any(tok in k.lower() for tok in [
                "hab","wet","water","pond","marsh","forest","land","cover","road","route",
                "lat","lon","elev","site","stop","temp","wind","noise","car","sky","cloud"
            ])]
        }
    out={"analysis":"naamp_stop_context_schema_audit_v0_1","report":report}
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
