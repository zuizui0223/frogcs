#!/usr/bin/env python3
from __future__ import annotations
import hashlib, importlib.util, json, os
from datetime import date, timedelta
from pathlib import Path
import pandas as pd

ROOT=Path(__file__).resolve().parents[2]
EXP=ROOT/"exploration"
RS=ROOT/"scripts"/"remotesensing"
OUT=ROOT/"remotesensing"/"NAAMP_CURRENT_WATER_RADIUS_SENSITIVITY_RECEIPT_V0_1.json"
EXPOSURE=Path(os.environ.get(
    "NAAMP_HYDRO_EXPOSURE_CSV",
    str(ROOT/"remotesensing"/"NAAMP_JRC_V1_HYDROLOGY_EXPOSURES_V0_1.csv")
))

def loadmod(name,path):
    s=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(s); assert s.loader; s.loader.exec_module(m); return m

flex=loadmod("flex",EXP/"run_naamp_flexible_common_environment_null.py")
hyd=loadmod("hyd",RS/"run_naamp_dynamic_hydrology_mechanism.py")
mem=flex.mem

def pseudo_var_for_radius(radius,exposure,raw,runs,sampled):
    col=f"current_water_fraction_r{radius}"
    if col not in exposure.columns:
        raise RuntimeError(f"missing {col}")
    lookup={(str(r.SiteID),int(r.year),int(r.month)):getattr(r,col) for r in exposure.itertuples(index=False)}
    eligible=set(runs.RunID.astype(str))
    site=mem.site_map(raw,eligible)
    rows=[]
    for rr in runs.itertuples(index=False):
        rid=str(rr.RunID)
        y=int(rr.SurveyYear)
        m=(date(y,1,1)+timedelta(days=int(rr.doy)-1)).month
        for st in sorted(sampled.get(rid,set())):
            sid=site.get((rid,st))
            if sid is None:
                continue
            v=lookup.get((sid,y,m))
            rows.append({
                "RunID":rid,"SiteID":sid,
                "current_water_fraction_r250":v,
                "recent_wetness_3m_r250":float("nan"),
                "hydro_sd_12m_r250":float("nan")
            })
    return pd.DataFrame(rows)

def main():
    if not EXPOSURE.exists():
        raise RuntimeError(f"missing exposure CSV {EXPOSURE}")
    exposure=pd.read_csv(EXPOSURE)

    raw,runs,psub,dsub,hsub,pools,sampled,ss=flex.prepare_subset()
    results={}
    for radius in (100,500):
        var=pseudo_var_for_radius(radius,exposure,raw,runs,sampled)
        p1,d1,h1,hyd1,site,safe,fail=hyd.build_complete_sample(
            raw,runs,psub,dsub,hsub,var,"M1"
        )
        gate=bool(
            len(p1)>=1500 and len(p1)>0 and
            p1.route_cluster.nunique()>=300 and p1.State.nunique()>=15
        )
        rec={
          "radius_m":radius,
          "coverage":{"pairs":int(len(p1)),"routes":int(p1.route_cluster.nunique()) if len(p1) else 0,
                      "states":int(p1.State.nunique()) if len(p1) else 0,
                      "failures":fail,"gate_pass":gate}
        }
        if gate:
            ana=hyd.analyze_sample(
                f"M0-M1 current-water sensitivity r{radius}",
                p1,d1,h1,hyd1,runs,sampled,ss,pools,("M0","M1")
            )
            rec["analysis"]=ana
            rec["classification"]=(
                "sufficient" if ana["M1_sufficient"] else
                "partial" if ana["fraction_removed_current"] is not None and ana["fraction_removed_current"]>0 else
                "not_supported"
            )
        else:
            rec["classification"]="coverage_inconclusive"
        results[str(radius)]=rec

    out={
      "analysis":"naamp_current_water_radius_sensitivity_v0_1",
      "primary_radius_m":250,
      "named_sensitivity_radii_m":[100,500],
      "contract":"revision/NAAMP_DYNAMIC_HYDROLOGY_MECHANISM_EXTENSION_V0_4.md",
      "model_spec":"revision/NAAMP_DYNAMIC_HYDROLOGY_MODEL_SPEC_V0_1.md",
      "exposure_sha256":hashlib.sha256(EXPOSURE.read_bytes()).hexdigest(),
      "results":results,
      "primary_250m_result_changed":False
    }
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    summary={"analysis":out["analysis"],"results":{}}
    for k,v in results.items():
        z={"coverage":v["coverage"],"classification":v["classification"]}
        if "analysis" in v:
            z["observed"]=v["analysis"]["observed"]
            z["models"]=v["analysis"]["models"]
            z["fraction_removed_current"]=v["analysis"]["fraction_removed_current"]
        summary["results"][k]=z
    print(json.dumps(summary,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
