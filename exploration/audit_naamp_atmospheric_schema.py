#!/usr/bin/env python3
from __future__ import annotations
import importlib.util, json, re
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
NAAMP=ROOT/"scripts"/"naamp"
OUT=ROOT/"exploration"/"NAAMP_ATMOSPHERIC_SCHEMA_AUDIT_V0_1.json"

def loadmod(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    mod=importlib.util.module_from_spec(spec); assert spec.loader; spec.loader.exec_module(mod); return mod

base=loadmod("pulse",NAAMP/"run_naamp_ecological_pulse.py")

TOKENS=("time","hour","start","end","humid","dew","baro","press","cloud","sky","weather","wind","temp","rain")

def profile(rows):
    cols=sorted({k for r in rows for k in r})
    candidates=[c for c in cols if any(t in c.lower() for t in TOKENS)]
    p={}
    for c in candidates:
        vals=[str(r.get(c) or "").strip() for r in rows]
        non=[x for x in vals if x!=""]
        counts=Counter(non)
        p[c]={
            "nonempty":len(non),
            "fraction_nonempty":len(non)/len(rows) if rows else 0,
            "unique":len(counts),
            "examples":[x for x,_ in counts.most_common(12)]
        }
    return {"n_rows":len(rows),"columns":cols,"candidate_fields":p}

def main():
    raw=base.load()
    out={"analysis":"naamp_atmospheric_schema_audit_v0_1","tables":{k:profile(v) for k,v in raw.items()}}
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,indent=2,sort_keys=True))

if __name__=="__main__": main()
