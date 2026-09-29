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

def layout(group,names):
    ds=xr.open_zarr(session.store,group=group,consolidated=False,chunks=None)
    out={}
    for name in names:
        if name not in ds:
            continue
        var=ds[name]
        chunks=var.encoding.get("chunks")
        out[name]={
            "dims":list(var.dims),
            "shape":[int(x) for x in var.shape],
            "encoding_chunks":None if chunks is None else [int(x) for x in chunks],
            "preferred_chunks":var.encoding.get("preferred_chunks"),
            "units":str(var.attrs.get("units","")),
            "GRIB_paramId":str(var.attrs.get("GRIB_paramId","")),
            "GRIB_name":str(var.attrs.get("GRIB_name","")),
        }
    return ds,out

temporal_ds,temporal_layout=layout("single/temporal",("t2m","d2m","swvl1","sp","msl","tp"))
spatial_ds,spatial_layout=layout("single/spatial",("t2m","d2m","swvl1","sp","msl","tp"))

out={
    "analysis":"era5_moisture_schema_audit_v0_3",
    "hierarchy":hierarchy,
    "hierarchy_error":hierarchy_error,
    "temporal_layout":temporal_layout,
    "spatial_layout":spatial_layout,
    "response_data_read":False
}
OUT.parent.mkdir(parents=True,exist_ok=True)
OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
print(json.dumps(out,indent=2,sort_keys=True))
