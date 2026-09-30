#!/usr/bin/env python3
import json
from pathlib import Path
import icechunk, xarray as xr

storage=icechunk.s3_storage(bucket="earthmover-icechunk-era5",prefix="icechunkV2",region="us-east-1",anonymous=True)
repo=icechunk.Repository.open(storage)
session=repo.readonly_session("main")
ds=xr.open_zarr(session.store,group="single/temporal",consolidated=False,chunks=None)
hits={}
for name,da in ds.data_vars.items():
    attrs=da.attrs
    hay=" ".join([
        str(name),str(attrs.get("GRIB_name","")),str(attrs.get("GRIB_shortName","")),
        str(attrs.get("long_name","")),str(attrs.get("standard_name",""))
    ]).lower()
    if any(x in hay for x in ("runoff","surface runoff","sub-surface runoff","snowmelt","evaporation")):
        hits[name]={
            "dims":list(da.dims),"units":str(attrs.get("units","")),
            "GRIB_paramId":str(attrs.get("GRIB_paramId","")),
            "GRIB_shortName":str(attrs.get("GRIB_shortName","")),
            "GRIB_name":str(attrs.get("GRIB_name","")),
            "long_name":str(attrs.get("long_name","")),
            "accumulation_comment":str(attrs.get("accumulation_comment","")),
        }
out={"analysis":"era5_runoff_schema_audit_v0_1","hits":hits,"response_data_read":False}
Path("exploration/ERA5_RUNOFF_SCHEMA_AUDIT_V0_1.json").write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
print(json.dumps(out,indent=2,sort_keys=True))
