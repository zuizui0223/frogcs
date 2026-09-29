#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
import icechunk,xarray as xr

OUT=Path("exploration/ERA5_MOISTURE_SCHEMA_AUDIT_V0_1.json")

storage=icechunk.s3_storage(
    bucket="earthmover-icechunk-era5",
    prefix="icechunkV2",
    region="us-east-1",
    anonymous=True,
)
repo=icechunk.Repository.open(storage)
session=repo.readonly_session("main")
ds=xr.open_zarr(session.store,group="single/temporal",consolidated=False,chunks=None)

terms=("temp","dew","humid","pressure","vapor","vapour","precip","soil","evap")
hits={}
for name,var in ds.data_vars.items():
    blob=" ".join([
        str(name),
        str(var.attrs.get("long_name","")),
        str(var.attrs.get("standard_name","")),
        str(var.attrs.get("GRIB_name","")),
        str(var.attrs.get("units","")),
    ]).lower()
    if any(t in blob for t in terms):
        hits[name]={
            "dims":list(var.dims),
            "dtype":str(var.dtype),
            "attrs":{k:str(v) for k,v in var.attrs.items() if k in (
                "long_name","standard_name","units","GRIB_name","GRIB_shortName","GRIB_paramId",
                "accumulation_comment"
            )}
        }

out={
    "analysis":"era5_moisture_schema_audit_v0_1",
    "group":"single/temporal",
    "n_data_vars":len(ds.data_vars),
    "candidate_variables":hits,
    "response_data_read":False
}
OUT.parent.mkdir(parents=True,exist_ok=True)
OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
print(json.dumps(out,indent=2,sort_keys=True))
