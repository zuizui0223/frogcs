#!/usr/bin/env python3
from pathlib import Path
import hashlib, json, os
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[2]
INDIR=Path(os.environ.get("DSWEMOD_SECONDARY_DIR",str(ROOT/"remotesensing"/"dswemod_secondary_inputs")))
OUT123=ROOT/"remotesensing"/"NAAMP_DSWEMOD_123_CURRENT_SECONDARY_INPUT.csv"
OUT1234=ROOT/"remotesensing"/"NAAMP_DSWEMOD_1234_CURRENT_SECONDARY_INPUT.csv"
OUTJSON=ROOT/"remotesensing"/"NAAMP_DSWEMOD_SECONDARY_INPUT_RECEIPT_V0_1.json"

files=sorted(INDIR.glob("NAAMP_DSWEMOD_20*.csv"))
years=sorted(int(p.stem.rsplit("_",1)[1]) for p in files)
expected=[2003]+list(range(2005,2016))
if years!=expected:
    raise RuntimeError(f"expected source-available years {expected}, got {years}")

df=pd.concat([pd.read_csv(p) for p in files],ignore_index=True)
if df.duplicated(["RunID","SiteID"]).any():
    raise RuntimeError("duplicate RunID/SiteID rows")

base=df[["RunID","SiteID"]].copy()
def write_var(col,path):
    out=base.copy()
    out["current_water_fraction_r250"]=pd.to_numeric(df[col],errors="coerce")
    out["recent_wetness_3m_r250"]=np.nan
    out["hydro_sd_12m_r250"]=np.nan
    out.to_csv(path,index=False,float_format="%.8g")
    return {
      "rows":int(len(out)),
      "runids":int(out.RunID.nunique()),
      "nonmissing":int(out.current_water_fraction_r250.notna().sum()),
      "sha256":hashlib.sha256(path.read_bytes()).hexdigest()
    }

a=write_var("dswemod123_r500",OUT123)
b=write_var("dswemod1234_r500",OUT1234)
rec={
 "analysis":"naamp_dswemod_secondary_input_v0_1",
 "source_repair":"revision/NAAMP_MODIS_DSWEMOD_SOURCE_REPAIR_V0_3.md",
 "years":years,
 "DSWEmod_123_r500":a,
 "DSWEmod_1234_r500":b,
 "frog_endpoint_calculated":False
}
OUTJSON.write_text(json.dumps(rec,indent=2)+"\n")
print(json.dumps(rec,indent=2))
