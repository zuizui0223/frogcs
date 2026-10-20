#!/usr/bin/env python3
"""Source-only NAAMP x NWI x survey-month-inclusive DSWEmod vegetation/wetness audit.

Do NOT load Counts.csv or infer frog-outcome-dependent inclusion at this stage.
"""
from __future__ import annotations
import argparse
import datetime
import hashlib
import importlib.util
import json
import math
from collections import Counter,defaultdict
from pathlib import Path

import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
EXPECTED_RUNS=7848
EXPECTED_PAIRS=4236
EXPECTED_ROUTES=585
REQUIRED_NWI=["nwi_all_wetland_cover_250m","nwi_emergent_cover_250m","nwi_woody_cover_250m"]
REQUIRED_DSWE=["current_D_r500","recent_D_3m_r500"]
EARLY={2003,2005,2006,2007,2008,2009}
LATE={2010,2011,2012,2013,2014,2015}

def loadmodule(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(module)
    return module

def reconstruct(runs,stops):
    candidates={}
    for r in runs:
        rid=str(r.get("RunID") or "").strip()
        year=r.get("SurveyYear") or r.get("SurveyDate")
        import re
        found=re.search(r"(?<!\d)((?:19|20)\d{2})(?!\d)",str(year))
        if not found:continue
        year=int(found.group(1))
        if year<2001 or year>2015:continue
        if (r.get("UnifiedProtocol") or "").strip()!="1":continue
        runno=(r.get("RunNumber") or "").strip()
        state=(r.get("State") or "").strip()
        route=(r.get("RouteNumber") or "").strip()
        rtype=(r.get("RouteType") or "").strip()
        if not(rid and state and route and rtype and runno in {"1","2","3","4"}):
            continue
        try:
            rain=float((r.get("DaysSinceRain") or "").strip())
        except ValueError:
            continue
        if not math.isfinite(rain) or not (0<=rain<=180):continue
        day=None
        for fmt in ("%m/%d/%Y","%m/%d/%y","%Y-%m-%d","%Y/%m/%d"):
            try:day=datetime.datetime.strptime(str(r.get("SurveyDate") or "").strip(),fmt).date();break
            except ValueError:pass
        if day is None:continue
        if day.year!=year:continue
        candidates[rid]={"RunID":rid,"State":state,"RouteNumber":route,
                         "RunNumber":runno,"SurveyYear":year,"month":day.month,
                         "TempScale":(r.get("TempScale") or "").strip()}
    byrun=defaultdict(dict)
    temps=defaultdict(list)
    for s in stops:
        rid=str(s.get("RunID") or "").strip()
        if rid not in candidates or (s.get("SkippedStop") or "").strip()!="0":continue
        st=str(s.get("StopNumber") or "").strip()
        sid=str(s.get("SiteID") or "").strip()
        if not st:continue
        if st in byrun[rid] and byrun[rid][st]!=sid:
            raise RuntimeError("NAAMP duplicate stop-number with conflicting SiteID")
        byrun[rid][st]=sid
        try:x=float((s.get("AirTemp") or "").strip())
        except ValueError:continue
        scale=candidates[rid]["TempScale"]
        if scale=="F":x=(x-32)*5/9
        elif scale!="C":continue
        if math.isfinite(x):temps[rid].append(x)
    out={}
    for rid,meta in candidates.items():
        v=byrun.get(rid,{})
        t=temps.get(rid,[])
        if len(v)!=10 or len(t)<8:continue
        mean=float(np.mean(t))
        if not -10<=mean<=45:continue
        keys=sorted(v,key=lambda a:int(a))
        meta=dict(meta)
        meta["stop_numbers"]=keys
        meta["site_ids"]=[str(v[x]) for x in keys]
        out[rid]=meta
    if len(out)!=EXPECTED_RUNS:
        raise RuntimeError(f"Reconstruction drift {len(out)} instead of {EXPECTED_RUNS}")
    return out

def read_nwi(path):
    x=pd.read_csv(path,dtype={"State":str,"RouteNumber":str,"SiteID":str},
                  low_memory=False)
    expected=["State","RouteNumber","SiteID","nwi_service_success"]+REQUIRED_NWI
    if any(k not in x.columns for k in expected):raise RuntimeError("Missing NWI columns")
    if x.duplicated(["State","RouteNumber","SiteID"]).any():
        raise RuntimeError("Duplicate NWI State Route Site key")
    if not x.nwi_service_success.astype(str).str.lower().eq("true").all():
        raise RuntimeError("NWI network failures improperly coded as absence")
    for k in REQUIRED_NWI:
        x[k]=pd.to_numeric(x[k],errors="coerce")
        if x[k].isna().any() or not x[k].between(0,1).all():
            raise RuntimeError("Nonfinite or out-of-range NWI "+k)
    return x.set_index(["State","RouteNumber","SiteID"])

def read_dswe(path):
    x=pd.read_csv(path,dtype={"RunID":str,"SiteID":str,"State":str,"RouteNumber":str},
                  low_memory=False)
    need=["RunID","SiteID","State","RouteNumber","year","month"]+REQUIRED_DSWE
    if any(k not in x.columns for k in need):raise RuntimeError("missing DSWEmod source field")
    if x.duplicated(["RunID","SiteID"]).any():
        raise RuntimeError("DSWEmod duplicate RunID SiteID")
    for k in REQUIRED_DSWE:x[k]=pd.to_numeric(x[k],errors="coerce")
    return x.set_index(["RunID","SiteID"])

def test_gates(stats):
    return {
        "complete_runs_ge600":stats["complete_runs"]>=600,
        "routes_ge100":stats["routes"]>=100,
        "states_ge12":stats["states"]>=12,
        "early_runs_ge100":stats["early_runs"]>=100,
        "late_runs_ge200":stats["late_runs"]>=200,
        "plant_var_plus_recent_nonzero_runs_ge80":stats["plant_var_recent_positive_runs"]>=80
    }

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--nwi",type=Path,required=True)
    parser.add_argument("--nwi-audit",type=Path,required=True)
    parser.add_argument("--dswe",type=Path,required=True)
    parser.add_argument("--outdir",type=Path,default=ROOT/"build"/"plant_wetness_interaction")
    args=parser.parse_args()
    check=json.loads(args.nwi_audit.read_text())
    if not(check["preflight_eligible"] and check["mode"]=="full"
           and len(check["overlay"]["shards"])==12
           and check["matched_route_source_only_audit"]["n_matched_pairs"]==EXPECTED_PAIRS
           and check["matched_route_source_only_audit"]["n_matched_routes"]==EXPECTED_ROUTES):
        raise RuntimeError("NWI immutable geometry QA fails")
    source=loadmodule("nwi_source_only",ROOT/"exploration/run_naamp_nwi_aquatic_vegetation_preflight_v0_1.py")
    raw=source.read_source_only()
    assert "Counts.csv" not in raw,"Preflight must not read frog outcomes"
    runs=reconstruct(raw["Runs.csv"],raw["Stops.csv"])
    nwi=read_nwi(args.nwi)
    dswe=read_dswe(args.dswe)
    selected=[]
    skip=Counter()
    for rid,info in sorted(runs.items()):
        if info["SurveyYear"] not in EARLY|LATE:
            skip["not_valid_dswe_year"]+=1;continue
        if len(set(info["site_ids"]))!=10:
            skip["duplicate_SiteID_in_run"]+=1;continue
        nwi_ids=[(info["State"],info["RouteNumber"],sid) for sid in info["site_ids"]]
        if any(k not in nwi.index for k in nwi_ids):
            skip["not_ten_NWI_sites"]+=1;continue
        water_ids=[(rid,sid) for sid in info["site_ids"]]
        if any(k not in dswe.index for k in water_ids):
            skip["not_ten_DSWE_run_sites"]+=1;continue
        dh=dswe.loc[water_ids]
        if any(str(z.State)!=info["State"] or str(z.RouteNumber)!=info["RouteNumber"]
               for z in dh.itertuples(index=False)):
            skip["site_route_identity_mismatch"]+=1;continue
        if not ((dh.year.astype(int)==info["SurveyYear"]).all() and
                (dh.month.astype(int)==info["month"]).all()):
            skip["site_month_mismatch"]+=1;continue
        val=dh[REQUIRED_DSWE].to_numpy(dtype=float)
        if not np.isfinite(val).all():
            skip["water_missing_current_or_three_month"]+=1;continue
        if np.min(val)<-1e-6 or np.max(val)>1.000001:
            skip["DSWE_wet_fraction_not_0_to_1"]+=1;continue
        plant=nwi.loc[nwi_ids,REQUIRED_NWI].to_numpy(dtype=float)
        if not np.isfinite(plant).all():raise RuntimeError("NWI complete source is nonfinite")
        # v site covariates W,E,D0,D3, with coefficients expressed per 0.1 cover
        v=np.column_stack([10*plant[:,0],10*plant[:,1],
                           10*val[:,0],10*val[:,1]])
        # Note that the survey-month-inclusive recent3 summary can include
        # satellite observations after the frog's survey day.
        routewet=float(v[:,3].mean())
        has_covariation=bool(np.ptp(v[:,1])>1e-8 and np.any(v[:,3]>1e-8))
        selected.append({
            "RunID":rid,"State":info["State"],
            "RouteNumber":info["RouteNumber"],
            "route_cluster":info["State"]+":"+info["RouteNumber"],
            "run_fold":"A" if hashlib.sha256((info["State"]+":"+info["RouteNumber"]).encode()).digest()[0]%2==0 else "B",
            "SurveyYear":info["SurveyYear"],"month":info["month"],
            "stop_numbers":info["stop_numbers"],"site_ids":info["site_ids"],
            "v4":v.tolist(),
            "PEM_route_spread":float(np.ptp(v[:,1])),
            "recent_wet_3m_route_mean":routewet,
            "PEM_var_and_recent_nonzero":has_covariation
        })
    st={
        "complete_runs":len(selected),
        "routes":len(set(z["route_cluster"] for z in selected)),
        "states":len(set(z["State"] for z in selected)),
        "early_runs":sum(z["SurveyYear"] in EARLY for z in selected),
        "late_runs":sum(z["SurveyYear"] in LATE for z in selected),
        "plant_var_recent_positive_runs":sum(z["PEM_var_and_recent_nonzero"] for z in selected),
        "survey_month_inclusive_water_summary":True
    }
    gates=test_gates(st)
    eligible=all(gates.values())
    out={
        "analysis":"NAAMP_plant_x_recent_wetness_source_only_preflight_v0_1",
        "source":{"NAAMP_Runs_sha256":source.PINS["Runs.csv"],
                  "NAAMP_Stops_sha256":source.PINS["Stops.csv"],
                  "NWI_full_area_run":39450277196,
                  "DSWEmod_original_artifact_run":37615425574,
                  "DSWEmod_file_sha256":hashlib.sha256(args.dswe.read_bytes()).hexdigest()},
        "eligibility":st,"gates":gates,"preflight_eligible":eligible,
        "excluded":dict(skip),"source_runs":len(runs),
        "rows_with_site_and_environment":10*len(selected),
        "counts_outcome_file_read":False,
        "interpretation":{"NWI_not_historical_vegetation":True,
                         "survey_month_inclusive_3m_is_not_strict_antecedent":True,
                         "2004_DSWE_source_unavailable":True,
                         "RC6_unmodified":True}}
    args.outdir.mkdir(parents=True,exist_ok=True)
    (args.outdir/"preflight.json").write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    with (args.outdir/"response_blind_source_runs.jsonl").open("w") as f:
        for row in selected:f.write(json.dumps(row,sort_keys=True)+"\n")
    print("PLANT_WETNESS_PREFLIGHT_BEGIN",flush=True)
    print(json.dumps(out,sort_keys=True),flush=True)
    print("PLANT_WETNESS_PREFLIGHT_END",flush=True)
    import os
    if os.environ.get("GITHUB_OUTPUT"):
        with open(os.environ["GITHUB_OUTPUT"],"a") as f:
            f.write("eligible="+("true" if eligible else "false")+"\n")
if __name__=="__main__":
    main()
