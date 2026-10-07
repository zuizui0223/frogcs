#!/usr/bin/env python3
from pathlib import Path
import hashlib, json, os
import pandas as pd

ROOT=Path(__file__).resolve().parents[2]
INDIR=Path(os.environ.get("NWI_AMOUNT_RECOVERY_DIR",str(ROOT/"remotesensing"/"nwi_amount_recovery_inputs")))
OUTDIR=ROOT/"remotesensing"/"nwi_amount_shards"

files=sorted(INDIR.glob("NWI_WETLAND_AMOUNT_SHARD_*.csv"))
if len(files)!=4:
    raise RuntimeError(f"expected 4 recovery subshards, found {len(files)}: {[p.name for p in files]}")

df=pd.concat([pd.read_csv(p,dtype={"SiteID":str,"RouteNumber":str}) for p in files],ignore_index=True)
if df.duplicated(["SiteID"]).any():
    raise RuntimeError("duplicate SiteID across shard-5 recovery subshards")

# Verify that all recovered routes belong exactly to the original hash%8 == 5 partition.
bad=[]
for rid in sorted(df.RouteNumber.dropna().astype(str).unique()):
    h=int(hashlib.sha256(rid.encode()).hexdigest()[:8],16)
    if h%8!=5:
        bad.append(rid)
if bad:
    raise RuntimeError(f"recovery contains routes outside original shard 5: {bad[:20]}")

OUTDIR.mkdir(parents=True,exist_ok=True)
csvout=OUTDIR/"NWI_WETLAND_AMOUNT_SHARD_05.csv"
jsonout=OUTDIR/"NWI_WETLAND_AMOUNT_SHARD_05.json"
df.to_csv(csvout,index=False)
rec={
  "analysis":"nwi_wetland_amount_shard5_timeout_recovery_v0_1",
  "scientific_contract":"revision/NAAMP_NWI_WETLAND_AMOUNT_RAIN_MECHANISM_CONTRACT_V0_1.md",
  "retrieval_change_only":True,
  "original_partition":"sha256(RouteNumber) % 8 == 5",
  "recovery_subpartitions":[5,13,21,29],
  "recovery_modulus":32,
  "rows":int(len(df)),
  "routes":int(df.RouteNumber.nunique()),
  "query_success":int(df.query_success.map(lambda x:str(x).lower() in ("true","1","yes")).sum()),
  "frog_endpoint_calculated":False
}
jsonout.write_text(json.dumps(rec,indent=2)+"\n")
print(json.dumps(rec,indent=2))
