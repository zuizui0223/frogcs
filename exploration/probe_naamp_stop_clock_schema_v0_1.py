#!/usr/bin/env python3
"""Source-only stop-clock schema audit on pinned official NAAMP 2001–2015 data.

No frog species, detection results or vegetation outcomes inspected.
"""
import importlib.util,json
from pathlib import Path
from collections import Counter,defaultdict
ROOT=Path(__file__).resolve().parents[1]
p=ROOT/"exploration/run_naamp_aquatic_vegetation_ecological_tests_v0_2.py"
spec=importlib.util.spec_from_file_location("naamp_clock_schema",p)
mod=importlib.util.module_from_spec(spec)
assert spec.loader
spec.loader.exec_module(mod)
raw=mod.hist.load_retry()
runs,_=mod.base.build_runs(raw)
valid=set(runs.RunID.astype(str))
names=["StartTime","TimeOut"]
valid_rows=[x for x in raw["Stops.csv"] if str(x.get("RunID") or "").strip() in valid and str(x.get("SkippedStop") or "").strip()=="0"]
out={"status":"NAAMP_pinned_source_time_fields_coverage_audited","eligible_standardized_runs":len(valid),
"valid_stop_rows":len(valid_rows),"field_names":sorted(raw["Stops.csv"][0].keys()),"clock_fields":{}}
for field in names:
    vals=[str(x.get(field) or "").strip() for x in valid_rows]
    present=[s for s in vals if s]
    out["clock_fields"][field]={
      "nonempty":len(present),"empty":len(vals)-len(present),
      "nonempty_fraction":len(present)/len(vals),
      "examples_unique_first20":list(dict.fromkeys(present))[:20],
      "string_lengths":dict(Counter(map(len,present)).most_common(10)),
      "contains_colon_fraction":sum(":" in s for s in present)/len(present) if present else 0,
      "digit_only_fraction":sum(s.isdigit() for s in present)/len(present) if present else 0}
print("NAAMP_STOP_TIME_SCHEMA_BEGIN")
print(json.dumps(out,ensure_ascii=False,sort_keys=True))
print("NAAMP_STOP_TIME_SCHEMA_END")
assert out["eligible_standardized_runs"]==7848
