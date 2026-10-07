#!/usr/bin/env python3
from pathlib import Path
import hashlib, json, os
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[2]
INDIR=Path(os.environ.get("DSWEMOD_V01_DIR",str(ROOT/"remotesensing"/"dswemod_v01_inputs")))
OUTCSV=ROOT/"remotesensing"/"NAAMP_DSWEMOD_RUN_SITE_METRICS_CURRENT_ONLY_V0_1.csv"
OUTJSON=ROOT/"remotesensing"/"NAAMP_DSWEMOD_CURRENT_ONLY_COVERAGE_INPUT_V0_1.json"

files=sorted(INDIR.glob("NAAMP_DSWEMOD_20*.csv"))
years=sorted(int(p.stem.rsplit("_",1)[1]) for p in files)
expected=[2003]+list(range(2005,2016))
if years!=expected:
    raise RuntimeError(f"expected source-available years {expected}, got {years}")

df=pd.concat([pd.read_csv(p) for p in files],ignore_index=True)
if df.duplicated(["RunID","SiteID"]).any():
    raise RuntimeError("duplicate RunID/SiteID rows")

out=df[["RunID","SiteID","State","RouteNumber","route_cluster","RunNumber","year","month"]].copy()
out["current_D_r500"]=pd.to_numeric(df["dswemod123_r500"],errors="coerce")
out["recent_D_3m_r500"]=np.nan
out["DSWE_sd_12m_r500"]=np.nan
out["current_D_r250"]=pd.to_numeric(df["dswemod123_r250"],errors="coerce")
out["recent_D_3m_r250"]=np.nan
out["DSWE_sd_12m_r250"]=np.nan
out.to_csv(OUTCSV,index=False,float_format="%.8g")

rec={
  "analysis":"naamp_dswemod_current_only_input_v0_1",
  "repair":"revision/NAAMP_MODIS_DSWEMOD_SOURCE_REPAIR_V0_3.md",
  "years":years,
  "rows":int(len(out)),
  "runids":int(out.RunID.nunique()),
  "nonmissing_r500":int(out.current_D_r500.notna().sum()),
  "nonmissing_r250":int(out.current_D_r250.notna().sum()),
  "csv_sha256":hashlib.sha256(OUTCSV.read_bytes()).hexdigest(),
  "frog_endpoint_calculated":False
}
OUTJSON.write_text(json.dumps(rec,indent=2)+"\n")
print(json.dumps(rec,indent=2))
