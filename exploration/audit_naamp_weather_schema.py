#!/usr/bin/env python3
from __future__ import annotations
import importlib.util,json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
NAAMP=ROOT/"scripts"/"naamp"
OUT=ROOT/"exploration"/"NAAMP_WEATHER_SCHEMA_AUDIT_V0_1.json"

def loadmod(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s)
    assert s.loader;s.loader.exec_module(m);return m

base=loadmod("base",NAAMP/"run_naamp_ecological_pulse.py")
raw=base.load()
terms=("humid","dew","press","baro","weather","sky","cloud","wind","temp","rain","precip","moist","time")
out={"analysis":"naamp_weather_schema_audit_v0_1","response_data_read":False,"files":{}}
for name,rows in raw.items():
    cols=list(rows[0].keys()) if rows else []
    hits=[c for c in cols if any(t in c.lower() for t in terms)]
    examples={}
    for c in hits:
        vals=[]
        seen=set()
        for r in rows:
            v=str(r.get(c) or "").strip()
            if v and v not in seen:
                seen.add(v);vals.append(v)
            if len(vals)>=12:break
        examples[c]=vals
    out["files"][name]={"n_rows":len(rows),"columns":cols,"weather_candidate_columns":hits,"example_nonempty_values":examples}
OUT.parent.mkdir(parents=True,exist_ok=True)
OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
print(json.dumps(out,indent=2,sort_keys=True))
