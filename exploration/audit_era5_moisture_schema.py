#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import icechunk
import xarray as xr
import zarr

OUT=Path("exploration/ERA5_MOISTURE_SCHEMA_AUDIT_V0_1.json")

storage=icechunk.s3_storage(
    bucket="earthmover-icechunk-era5",
    prefix="icechunkV2",
    region="us-east-1",
    anonymous=True,
)
repo=icechunk.Repository.open(storage)
session=repo.readonly_session("main")

hierarchy={}
hierarchy_error=None
try:
    root=zarr.open_group(session.store,mode="r")
    hierarchy["root_groups"]=sorted(list(root.group_keys()))
    if "single" in hierarchy["root_groups"]:
        single=root["single"]
        hierarchy["single_groups"]=sorted(list(single.group_keys()))
        hierarchy["single_arrays"]=sorted(list(single.array_keys()))
except Exception as e:
    hierarchy_error=repr(e)

ds=xr.open_zarr(session.store,group="single/temporal",consolidated=False,chunks=None)
spatial_ds=xr.open_zarr(session.store,group="single/spatial",consolidated=False,chunks=None)
spatial_layout={}
for name in ("t2m","d2m","swvl1"):
    if name in spatial_ds:
        var=spatial_ds[name]
        chunks=var.encoding.get("chunks")
        spatial_layout[name]={
            "dims":list(var.dims),
            "shape":[int(x) for x in var.shape],
            "encoding_chunks":None if chunks is None else [int(x) for x in chunks],
            "preferred_chunks":var.encoding.get("preferred_chunks"),
            "units":str(var.attrs.get("units","")),
            "GRIB_paramId":str(var.attrs.get("GRIB_paramId","")),
        }
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
        enc_chunks=var.encoding.get("chunks")
        pref=var.encoding.get("preferred_chunks")
        hits[name]={
            "dims":list(var.dims),
            "shape":[int(x) for x in var.shape],
            "dtype":str(var.dtype),
            "encoding_chunks":None if enc_chunks is None else [int(x) for x in enc_chunks],
            "preferred_chunks":pref,
            "attrs":{k:str(v) for k,v in var.attrs.items() if k in (
                "long_name","standard_name","units","GRIB_name","GRIB_shortName","GRIB_paramId",
                "accumulation_comment"
            )}
        }

out={
    "analysis":"era5_moisture_schema_audit_v0_2",
    "group":"single/temporal",
    "n_data_vars":len(ds.data_vars),
    "candidate_variables":hits,
    "hierarchy":hierarchy,
    "hierarchy_error":hierarchy_error,\n    "spatial_layout":spatial_layout,
    "response_data_read":False
}
OUT.parent.mkdir(parents=True,exist_ok=True)
OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
print(json.dumps(out,indent=2,sort_keys=True))
