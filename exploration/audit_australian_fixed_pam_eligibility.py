#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import io
import json
import urllib.request
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "exploration" / "AUSTRALIAN_FIXED_PAM_ELIGIBILITY_RECEIPT_V0_1.json"
URL = "https://raw.githubusercontent.com/cheloniax/repo_PAM_frogs/v.2.0/data/frog_data.csv"
EXPECTED_PLOTS = {"DryA", "DryB", "WetA", "WetB"}
SITE_RECORDED_DAYS_FROM_PUBLISHED_CODE = {
    "Tarcutta": 986,
    "Duval": 679,
    "Mourachan": 783,
    "Wambiana": 1235,
    "Undara": 780,
    "Rinyirru": 488,
}


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "frogcs-australian-pam-audit/0.1"})
    with urllib.request.urlopen(req, timeout=180) as r:
        return r.read()


def main():
    raw = fetch(URL)
    sha256 = hashlib.sha256(raw).hexdigest()
    df = pd.read_csv(io.BytesIO(raw))
    pam = df[df["assessment.method"].astype(str) == "PAM.all"].copy()
    pam["date_parsed"] = pd.to_datetime(pam["date"], dayfirst=True, errors="coerce")

    required = {"date", "site", "plot", "scientific.name", "assessment.method", "SamplingDay"}
    missing = sorted(required - set(df.columns))

    site_report = {}
    all_four = True
    any_explicit_effort = False
    for site, g in pam.groupby("site"):
        plots = sorted(set(g["plot"].dropna().astype(str)))
        all_four = all_four and set(plots) == EXPECTED_PLOTS
        date_by_plot = {
            p: int(g.loc[g["plot"].astype(str) == p, "date_parsed"].nunique())
            for p in plots
        }
        site_dates = int(g["date_parsed"].nunique())
        sampling_days = pd.to_numeric(g["SamplingDay"], errors="coerce").dropna().astype(int)
        unique_sampling = sorted(set(sampling_days.tolist()))
        if unique_sampling:
            span = int(max(unique_sampling) - min(unique_sampling) + 1)
            gaps = int(span - len(unique_sampling))
        else:
            span = gaps = 0
        published_days = SITE_RECORDED_DAYS_FROM_PUBLISHED_CODE.get(str(site))
        site_report[str(site)] = {
            "plots": plots,
            "unique_detection_dates_any_plot": site_dates,
            "unique_detection_dates_by_plot": date_by_plot,
            "sampling_day_span": span,
            "sampling_day_values_with_any_frog_detection": int(len(unique_sampling)),
            "sampling_day_gaps_in_detection_table": gaps,
            "published_site_level_available_audio_days": published_days,
            "site_level_days_not_identified_as_detection_dates": (
                int(published_days - site_dates)
                if published_days is not None else None
            ),
        }

    effort_columns = [
        c for c in df.columns
        if any(k in c.lower() for k in ("effort", "recording", "available_audio", "sampled"))
        and c not in {"assessment.method"}
    ]
    any_explicit_effort = len(effort_columns) > 0

    # This released table is a detection-event table. Without a plot-day recording
    # effort table, absent rows cannot safely be converted into sampled zeroes.
    effort_zero_frame_reconstructable = bool(
        not missing and any_explicit_effort
    )
    eligible = bool(
        not missing
        and all_four
        and effort_zero_frame_reconstructable
    )

    output = {
        "analysis": "australian_fixed_pam_matrix_eligibility_v0_1",
        "contract": "exploration/MECHANISM_UNIVERSALITY_CONTRACT_V0_1.json#australian_fixed_pam_eligibility",
        "source": {
            "url": URL,
            "version": "v.2.0",
            "zenodo_doi": "10.5281/zenodo.21634473",
            "sha256_download": sha256,
        },
        "rows_all": int(len(df)),
        "rows_pam_all": int(len(pam)),
        "required_columns_missing": missing,
        "sites": sorted(pam["site"].dropna().astype(str).unique().tolist()),
        "all_sites_have_expected_four_plots": bool(all_four),
        "candidate_effort_columns": effort_columns,
        "explicit_plot_day_effort_field_present": bool(any_explicit_effort),
        "site_report": site_report,
        "matrix_replication_eligible": eligible,
        "decision": (
            "eligible_for_naamp_style_matrix_replication"
            if eligible
            else "not_eligible_without_plot_day_effort_frame"
        ),
        "reason": (
            "The public frog_data.csv is a detection-event table. It preserves site, plot and date, "
            "but does not provide a plot-day recording-effort frame that distinguishes a true sampled "
            "zero-frog day from missing audio. Site-level available-audio day totals in the published "
            "analysis do not identify plot-specific sampled zeroes. Therefore missing detection rows "
            "must not be treated as absences for a species x plot boundary analysis."
        ),
        "authorized_fallback": (
            "The dataset remains suitable for positive-detection or active-unit questions, but not "
            "for the NAAMP-style active/inactive plot matrix unless an effort table is obtained."
        ),
    }
    OUT.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(output, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
