#!/usr/bin/env python3
"""Response-blind climate features for a separate NAAMP climate/landscape study.

Input tables (UTF-8 CSV):
  surveys: run_id, route_id, site_id, survey_date, coordinate_qc_status
  daily: route_id, site_id, date, tmin_c, tmax_c, precip_mm

Coordinate QC must precede extraction. Daymet/PRISM source provenance is
external to this script; source IDs, versions and download hashes must be logged.
No frog response columns are accepted or read.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd

BASE_START, BASE_END = 1981, 2000
MIN_BASE_YEARS = 15
MIN_DAYS_PER_BASE_MONTH_YEAR = 20
MIN_DAYS_PER_COMPLETE_YEAR = 350
WINDOWS = (7, 30, 90)


def _validate_columns(df: pd.DataFrame, needed: set[str], name: str) -> None:
    missing = needed.difference(df.columns)
    if missing:
        raise ValueError(f"{name} missing columns: {sorted(missing)}")


def _safe_unique(df: pd.DataFrame, keys: list[str], name: str) -> None:
    if df.duplicated(keys).any():
        raise ValueError(f"duplicate {name} keys: {keys}")


def prepare_inputs(surveys: pd.DataFrame, daily: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    survey_cols = {"run_id", "route_id", "site_id", "survey_date", "coordinate_qc_status"}
    daily_cols = {"route_id", "site_id", "date", "tmin_c", "tmax_c", "precip_mm"}
    _validate_columns(surveys, survey_cols, "surveys")
    _validate_columns(daily, daily_cols, "daily")
    s = surveys[list(sorted(survey_cols))].copy()
    d = daily[list(sorted(daily_cols))].copy()
    for frame in (s, d):
        for c in ("route_id", "site_id"):
            frame[c] = frame[c].astype("string").str.strip()
            if frame[c].isna().any() or (frame[c] == "").any():
                raise ValueError(f"missing {c}")
    s["run_id"] = s["run_id"].astype("string").str.strip()
    if s["run_id"].isna().any() or (s["run_id"] == "").any():
        raise ValueError("missing run_id")
    s["survey_date"] = pd.to_datetime(s["survey_date"], errors="raise").dt.normalize()
    d["date"] = pd.to_datetime(d["date"], errors="raise").dt.normalize()
    if s[["survey_date"]].isna().any().any() or d[["date"]].isna().any().any():
        raise ValueError("null date")
    if not s["coordinate_qc_status"].eq("verified_external").all():
        raise ValueError("surveys contain coordinates without externally verified site identity")
    for c in ("tmin_c", "tmax_c", "precip_mm"):
        d[c] = pd.to_numeric(d[c], errors="raise")
        if not np.isfinite(d[c]).all():
            raise ValueError(f"non-finite {c}")
    if (d["precip_mm"] < 0).any() or (d["tmax_c"] < d["tmin_c"]).any():
        raise ValueError("invalid daily meteorology")
    _safe_unique(s, ["run_id", "route_id", "site_id"], "survey")
    _safe_unique(d, ["route_id", "site_id", "date"], "daily")
    d["year"] = d.date.dt.year
    d["month"] = d.date.dt.month
    d["tmean_c"] = (d.tmin_c + d.tmax_c) / 2
    return s, d


def site_climatology(d: pd.DataFrame) -> tuple[pd.DataFrame, float, float]:
    """Fixed 1981-2000 daily-month climatology; do not use outcome-period years."""
    b = d[d.year.between(BASE_START, BASE_END)].copy()
    monthly_count = b.groupby(["year", "month"]).size().reset_index(name="ndays")
    good = monthly_count[monthly_count.ndays >= MIN_DAYS_PER_BASE_MONTH_YEAR]
    qualifying = b.merge(good[["year", "month"]], on=["year", "month"])
    if qualifying.groupby("month").year.nunique().reindex(range(1, 13), fill_value=0).min() < MIN_BASE_YEARS:
        raise ValueError("insufficient 1981-2000 monthly climatology coverage")
    ref = qualifying.groupby("month", as_index=False).agg(
        reference_tmean_c=("tmean_c", "mean"),
        reference_precip_mm_day=("precip_mm", "mean"),
    )
    qualifying_years = b.groupby("year").size()
    years = qualifying_years[qualifying_years >= MIN_DAYS_PER_COMPLETE_YEAR].index
    if len(years) < MIN_BASE_YEARS:
        raise ValueError("insufficient 1981-2000 annual climatology coverage")
    agg = b[b.year.isin(years)].groupby("year").agg(
        mean_t=("tmean_c", "mean"), total_p=("precip_mm", "sum")
    )
    return ref, float(agg.mean_t.mean()), float(agg.total_p.mean())


def _prior_year_features(d: pd.DataFrame, survey_year: int, annual_t_ref: float, annual_p_ref: float) -> dict:
    yearly = d.groupby("year").agg(n=("tmean_c", "size"), t=("tmean_c", "mean"), p=("precip_mm", "sum"))
    need = list(range(survey_year - 5, survey_year))
    prior = yearly.reindex(need)
    if prior.n.isna().any() or (prior.n < MIN_DAYS_PER_COMPLETE_YEAR).any():
        raise ValueError("prior five full years not available")
    return {
        "climate_shift_5y_tmean_c": float(prior.t.mean() - annual_t_ref),
        "climate_shift_5y_precip_ratio": float(prior.p.mean() / annual_p_ref) if annual_p_ref > 0 else np.nan,
    }


def build_features(surveys: pd.DataFrame, daily: pd.DataFrame) -> pd.DataFrame:
    s, d = prepare_inputs(surveys, daily)
    # Deliberately intended for pilot batches (e.g. one route/region at a time).
    # Precompute each site's reference once rather than for every survey run.
    site_inputs = {}
    for key, group in d.groupby(["route_id", "site_id"], sort=True):
        reference, annual_t_ref, annual_p_ref = site_climatology(group)
        indexed = group.merge(reference, on="month", validate="many_to_one").set_index("date").sort_index()
        site_inputs[key] = (indexed, annual_t_ref, annual_p_ref)
    rows = []
    for row in s.itertuples(index=False):
        key = (row.route_id, row.site_id)
        if key not in site_inputs:
            raise ValueError(f"missing daily site {key}")
        ds, annual_t_ref, annual_p_ref = site_inputs[key]
        survey_date = row.survey_date
        result = {
            "run_id": str(row.run_id), "route_id": str(row.route_id),
            "site_id": str(row.site_id), "survey_date": survey_date.date().isoformat(),
            "coordinate_qc_status": "verified_external",
            "climate_baseline": "1981-2000",
            "survey_day_weather_used": False,
        }
        for window in WINDOWS:
            dates = pd.date_range(end=survey_date - pd.Timedelta(days=1), periods=window, freq="D")
            q = ds.reindex(dates)
            if q[["tmean_c", "precip_mm", "reference_tmean_c", "reference_precip_mm_day"]].isna().any().any():
                raise ValueError(f"missing prior {window} days at {key} on {survey_date.date()}")
            result[f"tmean_anomaly_{window}d_c"] = float((q.tmean_c-q.reference_tmean_c).mean())
            result[f"precip_sum_{window}d_mm"] = float(q.precip_mm.sum())
            result[f"precip_anomaly_{window}d_mm"] = float((q.precip_mm-q.reference_precip_mm_day).sum())
            result[f"days_lt1mm_rain_{window}d"] = int((q.precip_mm < 1.0).sum())
        result.update(_prior_year_features(ds, survey_date.year, annual_t_ref, annual_p_ref))
        rows.append(result)
    return pd.DataFrame(rows).sort_values(["run_id", "route_id", "site_id"]).reset_index(drop=True)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--surveys", required=True)
    ap.add_argument("--daily", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--receipt", required=True)
    args = ap.parse_args()
    result = build_features(pd.read_csv(args.surveys, dtype={"run_id":str,"route_id":str,"site_id":str}),
                            pd.read_csv(args.daily, dtype={"route_id":str,"site_id":str}))
    out = Path(args.out); out.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(out, index=False)
    receipt = {"response_columns_read": False, "climate_baseline": "1981-2000",
               "n_survey_site_rows": len(result), "n_distinct_sites": len(set(zip(result.route_id, result.site_id))),
               "survey_day_weather_used": False, "requires_externally_verified_coordinates": True,
               "not_a_climate_change_attribution_estimate": True}
    Path(args.receipt).write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
