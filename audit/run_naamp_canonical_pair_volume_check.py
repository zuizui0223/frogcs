#!/usr/bin/env python3
from __future__ import annotations
import importlib.util
import json
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
BASE_PATH=ROOT/"scripts"/"naamp"/"run_naamp_ecological_pulse.py"
OUT=ROOT/"audit"/"NAAMP_CANONICAL_PAIR_VOLUME_CHECK_V0_1.json"

def loadmod(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    mod=importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(mod)
    return mod

def main():
    base=loadmod("naamp_base",BASE_PATH)
    raw=base.load()
    runs,sets=base.build_runs(raw)
    pairs=base.pair_runs(runs,sets).copy().reset_index(drop=True)

    pair_run_ids=set(pairs["wet_RunID"].astype(str)) | set(pairs["dry_RunID"].astype(str))
    ci=Counter()
    cells=0
    taxa=set()
    byrun=Counter()
    taxon_run=set()
    active_stop=set()
    for r in raw["Counts.csv"]:
        rid=(r.get("RunID") or "").strip()
        if rid not in pair_run_ids:
            continue
        c=(r.get("CallingIndex") or "").strip()
        sp=(r.get("Species") or "").strip()
        if c not in {"1","2","3"} or not sp:
            continue
        cells+=1
        ci[c]+=1
        taxa.add(sp)
        byrun[rid]+=1
        taxon_run.add((rid,sp))
        active_stop.add((rid,(r.get("StopNumber") or "").strip()))

    out={
        "analysis":"naamp_canonical_pair_volume_check_v0_1",
        "authority":"scripts/naamp/run_naamp_ecological_pulse.py::build_runs + pair_runs",
        "eligible_runs":int(len(runs)),
        "pairs":int(len(pairs)),
        "routes":int(pairs["route_cluster"].nunique()),
        "states":int(pairs["State"].nunique()),
        "unique_pair_side_runids":int(len(pair_run_ids)),
        "unique_stop_visits_at_10_per_run":int(10*len(pair_run_ids)),
        "positive_call_records_in_pair_side_runs":int(cells),
        "calling_index_distribution":{k:int(ci[k]) for k in ("1","2","3")},
        "positive_taxon_labels_in_pair_side_runs":int(len(taxa)),
        "positive_taxon_x_run_combinations":int(len(taxon_run)),
        "active_run_x_stop_combinations":int(len(active_stop)),
        "runs_with_at_least_one_positive_call":int(sum(1 for r in pair_run_ids if byrun.get(r,0)>0)),
        "completely_call_silent_pair_runs":int(sum(1 for r in pair_run_ids if byrun.get(r,0)==0)),
        "runid_sha256":__import__("hashlib").sha256(
            ("\n".join(sorted(pair_run_ids,key=lambda z:int(z) if z.isdigit() else z))+"\n").encode()
        ).hexdigest(),
        "min_positive_records_per_pair_run":int(min(byrun.get(r,0) for r in pair_run_ids)),
        "max_positive_records_per_pair_run":int(max(byrun.get(r,0) for r in pair_run_ids))
    }
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
