#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[2]
SCHEMA=json.loads((ROOT/"revision"/"WFTS_CANONICAL_SCHEMA_V0_1.json").read_text())


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--outdir",required=True)
    args=ap.parse_args()
    out=Path(args.outdir)
    out.mkdir(parents=True,exist_ok=True)

    rng=np.random.default_rng(20261001)
    taxa=SCHEMA["taxa"]
    periods=[
        ("early_spring",4,15,8.0),
        ("late_spring",5,28,16.0),
        ("summer",7,7,22.0),
    ]

    run_rows=[]
    matrix_rows=[]
    n_routes=30
    years=range(2010,2018)

    species_base=np.linspace(-2.4,-0.6,len(taxa))
    species_rain=np.linspace(0.10,0.55,len(taxa))

    for route in range(1,n_routes+1):
        route_id=f"R{route:03d}"
        route_eff=rng.normal(0,0.35)
        site_eff=rng.normal(0,0.55,10)

        for pidx,(period,month,day,temp0) in enumerate(periods):
            for year in years:
                date=pd.Timestamp(year=year,month=month,day=day)
                dry_days=((year-2000)+route+2*pidx)%12 + 1
                rain_recency=float(np.log1p(dry_days)+0.015*(route%5))
                tmean=float(temp0+0.12*(year-2010)+rng.normal(0,0.6))

                run_rows.append({
                    "route_id":route_id,
                    "survey_period":period,
                    "survey_year":year,
                    "survey_date":date.date().isoformat(),
                    "rain_recency":rain_recency,
                    "tmean_run":tmean,
                })

                for station in range(1,11):
                    sid=f"{route_id}_S{station:02d}"
                    for j,sp in enumerate(taxa):
                        eta=(
                            species_base[j]+route_eff+site_eff[station-1]
                            - species_rain[j]*rain_recency
                            + 0.08*pidx
                        )
                        p=1/(1+np.exp(-eta))
                        active=rng.random()<p
                        if not active:
                            ci=0
                        else:
                            z=rng.random()
                            ci=1 if z<0.58 else (2 if z<0.86 else 3)
                        matrix_rows.append({
                            "route_id":route_id,
                            "survey_period":period,
                            "survey_year":year,
                            "survey_date":date.date().isoformat(),
                            "station_order":station,
                            "physical_site_id":sid,
                            "taxon_key":sp,
                            "call_index":ci,
                        })

    pd.DataFrame(run_rows).to_csv(out/"runs.csv",index=False)
    pd.DataFrame(matrix_rows).to_csv(out/"matrix.csv",index=False)
    print({"runs":len(run_rows),"matrix_rows":len(matrix_rows),"routes":n_routes})


if __name__=="__main__":
    main()
