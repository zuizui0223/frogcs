#!/usr/bin/env python3
from __future__ import annotations
import json,time,urllib.parse,urllib.request
from pathlib import Path

OUT=Path("exploration/OPENMETEO_BATCH_EXACT_QUALIFICATION_RECEIPT_V0_1.json")
API="https://archive-api.open-meteo.com/v1/archive"
POINTS=[(41.75,-73.75),(38.0,-81.0)]
DATE="2012-03-24"

def fetch(params,retries=6):
    url=API+"?"+urllib.parse.urlencode(params)
    last=None
    for i in range(retries):
        try:
            req=urllib.request.Request(url,headers={"User-Agent":"frogcs-openmeteo-batch-qualification/0.1","Accept":"application/json"})
            with urllib.request.urlopen(req,timeout=120) as r:
                return json.loads(r.read().decode())
        except Exception as e:
            last=e; time.sleep(2*(i+1))
    raise RuntimeError(last)

common={
  "start_date":DATE,"end_date":DATE,
  "hourly":"vapour_pressure_deficit,temperature_2m,dew_point_2m",
  "models":"era5","cell_selection":"nearest","timezone":"GMT"
}
single=[]
for lat,lon in POINTS:
    p=dict(common);p.update({"latitude":lat,"longitude":lon,"elevation":"nan"})
    single.append(fetch(p))

multi_params=dict(common)
multi_params.update({
  "latitude":",".join(str(x[0]) for x in POINTS),
  "longitude":",".join(str(x[1]) for x in POINTS),
  "elevation":",".join("nan" for _ in POINTS),
  "timezone":",".join("GMT" for _ in POINTS),
})
multi=fetch(multi_params)
if not isinstance(multi,list) or len(multi)!=len(POINTS):
    raise RuntimeError(f"unexpected multi shape: {type(multi)} len={len(multi) if isinstance(multi,list) else None}")

maxdiff=0.0
rows=[]
for i,(a,b) in enumerate(zip(single,multi)):
    diffs={}
    for var in ("vapour_pressure_deficit","temperature_2m","dew_point_2m"):
        av=a["hourly"][var];bv=b["hourly"][var]
        if len(av)!=len(bv):
            raise RuntimeError("hourly length mismatch")
        d=max(abs(float(x)-float(y)) for x,y in zip(av,bv))
        diffs[var]=d;maxdiff=max(maxdiff,d)
    cell=max(abs(float(a["latitude"])-float(b["latitude"])),abs(float(a["longitude"])-float(b["longitude"])))
    maxdiff=max(maxdiff,cell)
    rows.append({"index":i,"value_diffs":diffs,"cell_coordinate_maxdiff":cell})

out={
 "analysis":"openmeteo_batch_exact_qualification_v0_1",
 "multi_shape_pass":True,
 "max_numeric_diff":maxdiff,
 "exact_match_pass":bool(maxdiff<1e-9),
 "comparisons":rows,
 "response_data_read":False
}
OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
print(json.dumps(out,indent=2,sort_keys=True))
