#!/usr/bin/env python3
from __future__ import annotations
import hashlib, importlib.util, json, os
from collections import Counter
from pathlib import Path
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[2]
EXP=ROOT/"exploration"
INDIR=Path(os.environ.get("MOD11A1_SHARD_DIR",str(ROOT/"remotesensing"/"mod11a1_inputs")))
OUTCSV=ROOT/"remotesensing"/"NAAMP_MOD11A1_NIGHT_LST_EXPOSURES_V0_1.csv"
OUTJSON=ROOT/"remotesensing"/"NAAMP_MOD11A1_NIGHT_LST_COVERAGE_V0_1.json"

def loadmod(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);assert s.loader;s.loader.exec_module(m);return m
flex=loadmod("flex",EXP/"run_naamp_flexible_common_environment_null.py")
mem=flex.mem

files=sorted(INDIR.glob("MOD11A1_NIGHT_LST_SHARD_*.csv"))
if len(files)!=16:raise RuntimeError(f"expected 16 shards, found {len(files)}")
df=pd.concat([pd.read_csv(p,dtype={"RunID":str,"SiteID":str,"RouteNumber":str}) for p in files],ignore_index=True)
if df.duplicated(["RunID","SiteID"]).any():raise RuntimeError("duplicate RunID/SiteID LST rows")
for col in ("A_complete","B_complete"):
    df[col]=df[col].map(lambda x:str(x).strip().lower() in ("true","1","yes"))

runA={};runB={}
for rid,g in df.groupby("RunID",sort=False):
    a=bool(len(g)==10 and g.A_complete.all() and g.A_lst_kelvin.notna().all() and g.A_date.nunique(dropna=True)==1)
    b=bool(len(g)==10 and g.B_complete.all() and g.B_lst_kelvin.notna().all() and g.B_date.nunique(dropna=True)==1)
    runA[str(rid)]=a;runB[str(rid)]=b

raw,runs,psub,dsub,hsub,pools,sampled,ss=flex.prepare_subset()
eligible=set(runs.RunID.astype(str));site=mem.site_map(raw,eligible)

def pair_coverage(runok):
    keep=[];fail=Counter()
    for p,dct in zip(psub.itertuples(index=False),dsub):
        ids=mem.focal_siteids(p,dct,site)
        if ids is None or len(ids)!=10:
            fail["siteid_identity"]+=1;continue
        wr,dr=str(p.wet_RunID),str(p.dry_RunID)
        if not runok.get(wr,False) or not runok.get(dr,False):
            fail["run_lst_incomplete"]+=1;continue
        keep.append((str(p.route_cluster),str(p.State),wr,dr))
    routes=len({x[0] for x in keep});states=len({x[1] for x in keep})
    gate=bool(len(keep)>=1500 and routes>=300 and states>=15)
    return {"pairs":len(keep),"routes":routes,"states":states,"failures":dict(fail),"gate_pass":gate}

covA=pair_coverage(runA)
covB=pair_coverage(runB)
if covA["gate_pass"]:
    chosen="A"
elif covB["gate_pass"]:
    chosen="B"
else:
    chosen=None

outdf=df.copy()
if chosen=="A":
    outdf["lst_night_K"]=pd.to_numeric(outdf["A_lst_kelvin"],errors="coerce")
    outdf["view_local_hour"]=pd.to_numeric(outdf["A_view_local_hour"],errors="coerce")
    outdf["satellite_date"]=outdf["A_date"]
    outdf["lag_days"]=0
    outdf["pixel_key"]=outdf["A_pixel_key"]
    outdf["unique_pixels_run"]=pd.to_numeric(outdf["A_unique_pixels_run"],errors="coerce")
    outdf["temporal_rule"]="A_same_date"
elif chosen=="B":
    outdf["lst_night_K"]=pd.to_numeric(outdf["B_lst_kelvin"],errors="coerce")
    outdf["view_local_hour"]=pd.to_numeric(outdf["B_view_local_hour"],errors="coerce")
    outdf["satellite_date"]=outdf["B_date"]
    outdf["lag_days"]=pd.to_numeric(outdf["B_lag_days"],errors="coerce")
    outdf["pixel_key"]=outdf["B_pixel_key"]
    outdf["unique_pixels_run"]=pd.to_numeric(outdf["B_unique_pixels_run"],errors="coerce")
    outdf["temporal_rule"]="B_common_lookback"
else:
    outdf["lst_night_K"]=np.nan;outdf["view_local_hour"]=np.nan
    outdf["satellite_date"]=None;outdf["lag_days"]=np.nan
    outdf["pixel_key"]=None;outdf["unique_pixels_run"]=np.nan
    outdf["temporal_rule"]="coverage_inconclusive"

cols=["RunID","SiteID","route_cluster","RouteNumber","State","RunNumber","survey_date",
      "lst_night_K","view_local_hour","satellite_date","lag_days","pixel_key",
      "unique_pixels_run","temporal_rule"]
outdf[cols].to_csv(OUTCSV,index=False,float_format="%.8g")

if chosen is not None:
    complete_runs=set(rid for rid,ok in (runA.items() if chosen=="A" else runB.items()) if ok)
    gd=outdf.loc[outdf.RunID.astype(str).isin(complete_runs)]
    runpix=gd.groupby("RunID")["unique_pixels_run"].first().dropna()
    views=gd["view_local_hour"].dropna()
    lags=gd.groupby("RunID")["lag_days"].first().dropna()
    diag={
      "complete_runs":len(complete_runs),
      "unique_pixels_run_quantiles":{str(q):float(runpix.quantile(q)) for q in [0,.1,.5,.9,1]} if len(runpix) else {},
      "view_local_hour_median":float(views.median()) if len(views) else None,
      "lag_days_counts":{str(int(k)):int(v) for k,v in lags.value_counts().sort_index().to_dict().items()}
    }
else:
    diag={}

out={
 "analysis":"naamp_mod11a1_night_lst_coverage_v0_1",
 "spec":"revision/NAAMP_MODIS_NIGHT_LST_PROSPECTIVE_SPEC_V0_1.md",
 "rule_A":covA,"rule_B":covB,"selected_rule":chosen,
 "diagnostics":diag,
 "exposure_csv_sha256":hashlib.sha256(OUTCSV.read_bytes()).hexdigest(),
 "frog_endpoint_calculated":False
}
OUTJSON.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
print(json.dumps(out,indent=2,sort_keys=True))
