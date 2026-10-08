#!/usr/bin/env python3
"""Climate-only 1981–2015 site trend diagnostics (not survey predictors).

Input: route_id,site_id,date,tmin_c,tmax_c,precip_mm,coordinate_qc_status.
No frog data, event-level joins or climate-change attribution.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import theilslopes

FIRST, LAST = 1981, 2015
MIN_VALID_DAYS = 350
MIN_YEARS = 30


def summarize(daily: pd.DataFrame) -> pd.DataFrame:
    need = {"route_id", "site_id", "date", "tmin_c", "tmax_c", "precip_mm", "coordinate_qc_status"}
    missing = need - set(daily.columns)
    if missing:
        raise ValueError(f"missing daily columns {sorted(missing)}")
    d = daily[sorted(need)].copy()
    if not d.coordinate_qc_status.eq("verified_external").all():
        raise ValueError("unverified site coordinate/identity")
    d.date = pd.to_datetime(d.date, errors="raise")
    if d.date.isna().any() or d.duplicated(["route_id", "site_id", "date"]).any():
        raise ValueError("null or duplicate dates")
    for c in ("tmin_c", "tmax_c", "precip_mm"):
        d[c] = pd.to_numeric(d[c], errors="raise")
        if not np.isfinite(d[c]).all():
            raise ValueError(f"nonfinite {c}")
    if (d.tmax_c < d.tmin_c).any() or (d.precip_mm < 0).any():
        raise ValueError("invalid meteorology")
    d["year"] = d.date.dt.year
    d = d[d.year.between(FIRST, LAST)].copy()
    d["tmean_c"] = (d.tmin_c + d.tmax_c) / 2
    rows = []
    for (route,site), g in d.groupby(["route_id", "site_id"], sort=True):
        a = g.groupby("year").agg(days=("date", "size"), annual_tmean_c=("tmean_c", "mean"),
                                  annual_precip_mm=("precip_mm", "sum"))
        a = a[a.days >= MIN_VALID_DAYS]
        if len(a) < MIN_YEARS:
            rows.append({"route_id":route, "site_id":site, "n_valid_years":len(a),
                         "trend_status":"insufficient_years", "warming_c_decade":np.nan,
                         "annual_precip_change_mm_decade":np.nan})
            continue
        years=a.index.to_numpy(dtype=float)
        s_temp=float(theilslopes(a.annual_tmean_c.to_numpy(dtype=float), years)[0])*10
        s_precip=float(theilslopes(a.annual_precip_mm.to_numpy(dtype=float), years)[0])*10
        rows.append({"route_id":route, "site_id":site, "n_valid_years":len(a),
                     "trend_status":"descriptive_only", "warming_c_decade":s_temp,
                     "annual_precip_change_mm_decade":s_precip})
    return pd.DataFrame(rows)


def main() -> None:
    ap=argparse.ArgumentParser()
    ap.add_argument("--daily",required=True)
    ap.add_argument("--out",required=True)
    args=ap.parse_args()
    trend=summarize(pd.read_csv(args.daily,dtype={"route_id":str,"site_id":str}))
    out=Path(args.out)
    out.parent.mkdir(parents=True,exist_ok=True)
    trend.to_csv(out,index=False)

if __name__=="__main__":
    main()
