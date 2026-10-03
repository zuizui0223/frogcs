#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

AUTHORITY="revision/WFTS_PROSPECTIVE_COMMON_ENVIRONMENT_DIAGNOSTIC_V0_2.json"

def sha256_file(path: Path) -> str:
    h=hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda:fh.read(1024*1024),b""):
            h.update(chunk)
    return h.hexdigest()

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--runs",required=True)
    ap.add_argument("--output-runs",required=True)
    ap.add_argument("--receipt",required=True)
    args=ap.parse_args()

    inp=Path(args.runs)
    x=pd.read_csv(inp)
    required={"route_id","survey_period","survey_year","survey_date"}
    if not required<=set(x.columns):
        raise RuntimeError(f"synthetic input missing {sorted(required-set(x.columns))}")
    forbidden=[c for c in x.columns if any(t in c.lower() for t in ("taxon","species","call_index","calling","concentration"))]
    if forbidden:
        raise RuntimeError(f"response-like columns forbidden: {forbidden}")

    x=x.copy()
    x["route_id"]=x.route_id.astype(str)
    x["survey_period"]=x.survey_period.astype(str)
    x["survey_year"]=x.survey_year.astype(int)
    x["survey_date"]=pd.to_datetime(x.survey_date,errors="raise").dt.date.astype(str)

    route_num=x.route_id.str.extract(r"(\d+)",expand=False).fillna("0").astype(int)
    period_code=x.survey_period.map({"early_spring":0,"late_spring":1,"summer":2}).fillna(0).astype(int)
    year=x.survey_year.astype(int)

    # Deterministic, response-free synthetic weather with non-degenerate support.
    p1=((year+route_num+period_code)%6).astype(float)
    p3=p1+((2*year+route_num+3*period_code)%11).astype(float)/2.0
    p7=p3+((year+3*route_num+period_code)%17).astype(float)/3.0

    out=x[["route_id","survey_period","survey_year","survey_date"]].copy()
    out["prcp_1d_exposure"]=np.log1p(p1)
    out["prcp_3d_exposure"]=np.log1p(p3)
    out["prcp_7d_exposure"]=np.log1p(p7)
    out=out.sort_values(["route_id","survey_period","survey_year"]).reset_index(drop=True)

    out_path=Path(args.output_runs)
    out_path.parent.mkdir(parents=True,exist_ok=True)
    out.to_csv(out_path,index=False)

    receipt={
        "analysis":"wfts_synthetic_common_environment_runs_for_code_qa",
        "authority":AUTHORITY,
        "response_columns_read":False,
        "synthetic_only":True,
        "input_sha256":sha256_file(inp),
        "output_sha256":{"runs":sha256_file(out_path)},
        "counts":{"route_runs":int(len(out)),"routes":int(out.route_id.nunique())}
    }
    Path(args.receipt).write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n")
    print(json.dumps(receipt,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
