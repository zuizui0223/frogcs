#!/usr/bin/env python3
"""Independent 2016–2023 NPS GLKN historical frog-chorus site targeting.

FROZEN before seeing NPS outcome estimates: research/NPS_GLKN_STRICT_HISTORY_HYDROPERIOD_CONTRACT_V0_1.md
Input: NPS DOI 10.57830/2320505 / public domain.
Unit: site×taxon×year, annual max ManualCIV 0..3. History uses years
strictly before focal year. Same-taxon prior strong vs prior other-taxon
acoustic hotness, hydroperiod, recording effort. Within park×species×year
comparisons and park×species block bootstrap.
NOT the frogcs RC6 rain-conditioned multi-stop concentration statistic C.
"""
import argparse
import hashlib
import json
import math
import tempfile
from pathlib import Path
from urllib.request import Request, urlopen

import numpy as np
import pandas as pd

URL = "https://irma.nps.gov/DataStore/DownloadFile/763377?Reference=2320505"
SHA256 = "b1c11cf70472a906e6c238a690a5a12373cdd20ef4d5e180fa3f376d520118c2"
SEED = 20261025
COLUMNS = [
    "FileName", "ParkCode", "SiteLocation", "StartTime",
    "EventYear", "ManualCIV", "ScientificName", "Hydroperiod",
    "SurveyorDetectedStatus",
]
GRAIN = ["ParkCode", "SiteLocation", "ScientificName", "EventYear"]
PERIOD = ["ParkCode", "ScientificName", "EventYear"]


def require(b, why):
    if not b:
        raise ValueError(why)


def fetch_csv(destination):
    req = Request(URL, headers={
        "User-Agent": "AmphibianEcologyAudit/1.0 (open-data scientific validation)"
    })
    h = hashlib.sha256()
    count = 0
    with urlopen(req, timeout=120) as resp, open(destination, "wb") as f:
        while True:
            chunk = resp.read(1 << 20)
            if not chunk:
                break
            count += len(chunk)
            require(count <= 125_000_000, "Unexpected huge NPS download")
            h.update(chunk)
            f.write(chunk)
    require(h.hexdigest() == SHA256,
            "NPS source checksum changed: abort rather than mix editions")
    return count


def mode_nonempty(seq):
    ss = pd.Series(seq).dropna().astype(str)
    ss = ss[~ss.str.lower().isin(["", "nan", "na"])]
    if ss.empty:
        return "unreported"
    return str(ss.mode().iloc[0])


def build_yearly(path):
    raw = pd.read_csv(path, usecols=COLUMNS, low_memory=False)
    require(len(raw) == 147913, "NPS source row count changed")
    raw["EventYear"] = pd.to_numeric(raw.EventYear, errors="coerce")
    raw["ManualCIV"] = pd.to_numeric(raw.ManualCIV, errors="coerce")
    valid = raw.dropna(subset=["FileName", "ParkCode", "SiteLocation",
                               "ScientificName", "EventYear", "ManualCIV"]).copy()
    require(valid.ManualCIV.isin([0, 1, 2, 3]).all(),
            "ManualCIV unexpectedly outside 0..3")
    require(valid.EventYear.between(2016, 2023).all(),
            "Year range differs from NPS 2016-2023 release")
    valid["EventYear"] = valid["EventYear"].astype(int)
    valid["ManualCIV"] = valid["ManualCIV"].astype(int)
    valid["date"] = pd.to_datetime(valid.StartTime, errors="coerce").dt.date
    # One scored species per recording; if duplicate, use conservatively max.
    fields = ["ParkCode", "SiteLocation", "EventYear",
              "ScientificName", "FileName"]
    duplicated = int(valid.duplicated(fields).sum())
    per_audio = valid.groupby(fields, as_index=False, sort=False).agg(
        civ=("ManualCIV", "max"),
        date=("date", "first"),
        hydroperiod=("Hydroperiod", mode_nonempty),
    )
    annual = per_audio.groupby(GRAIN, as_index=False, sort=False).agg(
        max_civ=("civ", "max"),
        n_species_recordings=("FileName", "nunique"),
        n_survey_days=("date", "nunique"),
        hydroperiod=("hydroperiod", mode_nonempty),
    )
    annual["strong"] = (annual.max_civ >= 2).astype(int)
    annual["any_call"] = (annual.max_civ >= 1).astype(int)
    annual["full"] = (annual.max_civ == 3).astype(int)
    return annual, {
        "rows_raw": len(raw), "rows_valid": len(valid),
        "duplicate_audio_species_records": duplicated,
        "scored_species_audio_rows": len(per_audio),
        "annual_species_site_year_rows": len(annual),
        "parks": int(annual.ParkCode.nunique()),
        "physical_station_ids": int(annual.SiteLocation.nunique()),
        "taxa": int(annual.ScientificName.nunique()),
        "years": sorted(annual.EventYear.unique().tolist()),
        "hydroperiod_annual_counts": {
            str(k): int(v) for k, v in annual.hydroperiod.value_counts().items()},
        "annual_strong_rate": float(annual.strong.mean()),
    }


def strict_prior_panel(annual):
    records = []
    # Strictly previous *years* at each species×physical listening station.
    for (park, site, sp), grp in annual.groupby(
            ["ParkCode", "SiteLocation", "ScientificName"], sort=False):
        seen_strong, years_seen, files_seen = 0, 0, 0
        for x in grp.sort_values("EventYear").itertuples():
            records.append(dict(
                ParkCode=park, SiteLocation=site, ScientificName=sp,
                EventYear=int(x.EventYear), max_civ=int(x.max_civ),
                strong=int(x.strong), any_call=int(x.any_call), full=int(x.full),
                hydroperiod=str(x.hydroperiod),
                n_species_recordings=int(x.n_species_recordings),
                prior_strong=int(seen_strong),
                prior_years_seen=years_seen, prior_recordings=files_seen))
            seen_strong = max(seen_strong, int(x.strong))
            years_seen += 1
            files_seen += int(x.n_species_recordings)
    df = pd.DataFrame.from_records(records)
    require(len(df) == len(annual), "Panel rows changed")
    # Another-taxons' strictly prior strong history at the same station.
    other = {}
    for (park, site), group in annual.groupby(
            ["ParkCode", "SiteLocation"], sort=False):
        history = {}  # taxon -> ever score, updated only after each entire year
        for year, rows in group.groupby("EventYear", sort=True):
            for x in rows.itertuples():
                all_other = [v for t, v in history.items()
                             if t != x.ScientificName]
                other[(park, site, x.ScientificName, int(year))] = (
                    float(np.mean(all_other)) if all_other else np.nan)
            for x in rows.itertuples():
                name = x.ScientificName
                history[name] = max(history.get(name, 0), int(x.strong))
    df["other_prior_strong_fraction"] = [
        other[(r.ParkCode, r.SiteLocation, r.ScientificName, int(r.EventYear))]
        for r in df.itertuples()]
    df = df.loc[(df.EventYear >= 2017) & (df.prior_years_seen > 0)].copy()
    df["log_current_effort"] = np.log1p(df.n_species_recordings)
    df["log_prior_effort"] = np.log1p(df.prior_recordings)
    # Missing other-taxon propensity is genuine missingness; retain as
    # explicit unknown only for extended adjusted model sensitivity.
    df["other_prior_missing"] = df.other_prior_strong_fraction.isna().astype(int)
    df["other_prior_fixed"] = df.other_prior_strong_fraction.fillna(0)
    return df


def informative_groups(panel):
    accepted = []
    total = 0
    for group, grp in panel.groupby(PERIOD, sort=False):
        total += 1
        if (grp.SiteLocation.nunique() >= 4
                and grp.prior_strong.nunique() == 2):
            accepted.append(grp)
    if not accepted:
        return pd.DataFrame(), total
    return pd.concat(accepted, ignore_index=True), total


def demean_frame(df, target, additional):
    # Within park×taxon×year FE (do not assume same species across parks).
    grp = df.groupby(PERIOD, sort=False)
    columns = ["prior_strong"] + additional + [target]
    means = grp[columns].transform("mean")
    data = df[columns].subtract(means)
    if not np.all(np.isfinite(data.to_numpy())):
        raise RuntimeError("Nonfinite within-stratum design")
    return data


def make_linear_design(df, target, adjusted):
    d = df.copy()
    if adjusted:
        # Site hydroperiod is physical habitat class, *not* local event water
        # level. Treat unfamiliar classes as observed categorical values.
        dummies = pd.get_dummies(d.hydroperiod.astype(str),
                                prefix="hydro", dtype=float)
        if dummies.shape[1] > 1:
            d = pd.concat([d, dummies.iloc[:, 1:]], axis=1)
            dummy_names = list(dummies.columns[1:])
        else:
            dummy_names = []
        extras = ["other_prior_fixed", "other_prior_missing",
                  "log_current_effort", "log_prior_effort",
                  "prior_years_seen"] + dummy_names
    else:
        extras = []
    demeaned = demean_frame(d, target, extras)
    X = demeaned[["prior_strong"] + extras].to_numpy(dtype=float)
    Y = demeaned[target].to_numpy(dtype=float)
    return X, Y, ["own_prior_strong"] + extras


def fit_with_block_bootstrap(panel, target="strong", adjusted=False,
                             reps=2000, seed=SEED):
    if panel.empty:
        return {"estimable": False, "why": "No variation in prior site use"}
    xx, yy, cols = make_linear_design(panel, target, adjusted)
    k = xx.shape[1]
    if not np.isfinite(xx).all() or not np.isfinite(yy).all():
        return {"estimable": False, "why": "Missing adjusted covariates"}
    XtX, Xty = xx.T@xx, xx.T@yy
    rank = int(np.linalg.matrix_rank(XtX))
    if rank < k:
        return {"estimable": False, "why": f"Rank deficiency ({rank}/{k})"}
    est = np.linalg.solve(XtX, Xty)
    cluster = (panel.ParkCode.astype(str) + ":" +
               panel.ScientificName.astype(str)).to_numpy()
    clusters = sorted(set(cluster))
    gram = np.stack([xx[cluster == key].T@xx[cluster == key]
                     for key in clusters])
    cross = np.stack([xx[cluster == key].T@yy[cluster == key]
                      for key in clusters])
    rng = np.random.default_rng(seed + int(adjusted)*10 + len(panel))
    bs = []
    for _ in range(reps):
        ix = rng.integers(0, len(clusters), size=len(clusters))
        g = gram[ix].sum(axis=0)
        y = cross[ix].sum(axis=0)
        if np.linalg.matrix_rank(g) < k:
            continue
        bs.append(float(np.linalg.solve(g, y)[0]))
    valid = np.asarray(bs)
    return {
        "estimable": True,
        "outcome": target,
        "adjusted": adjusted,
        "n_site_taxon_year_rows": len(panel),
        "n_park_species_clusters": len(clusters),
        "n_park_species_year_strata": int(panel.groupby(PERIOD).ngroups),
        "coefficients": {name: float(v) for name, v in zip(cols, est)},
        "own_prior_strong_beta": float(est[0]),
        "ci95_park_species_block": [
            float(np.quantile(valid, .025)),
            float(np.quantile(valid, .975))] if len(valid) >= 500 else None,
        "valid_boot_replicates": int(len(valid)),
        "note": ("Within species×park×year risk-difference-style slope, "
                 "cluster bootstrap by species×park trajectories; "
                 "not randomization or causal individual fidelity"),
    }


def run():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="research/results/nps_glkn_history")
    parser.add_argument("--bootstrap", type=int, default=2000)
    args = parser.parse_args()
    with tempfile.TemporaryDirectory() as work:
        inp = Path(work)/"NPS_GLKN_2016_2023.csv"
        bytes_read = fetch_csv(inp)
        annual, qc = build_yearly(inp)
    panel = strict_prior_panel(annual)
    inform, n_groups = informative_groups(panel)
    require(not inform.empty,
            "Non-estimable: no within-park×species×year historical contrast")
    result = {
        "source": "US NPS GLKN, DOI 10.57830/2320505, public domain",
        "source_sha256": SHA256, "source_bytes": bytes_read,
        "contract": "research/NPS_GLKN_STRICT_HISTORY_HYDROPERIOD_CONTRACT_V0_1.md",
        "schema_check": qc,
        "strictly_prior_year_rows": int(len(panel)),
        "all_candidate_park_taxon_year_groups": int(n_groups),
        "informative_site_taxon_year_rows": int(len(inform)),
        "informative_strata": int(inform.groupby(PERIOD).ngroups),
        "informative_species": int(inform.ScientificName.nunique()),
        "informative_sites": int(inform.SiteLocation.nunique()),
        "informative_years": sorted(inform.EventYear.unique().tolist()),
        "informative_hydroperiod_counts": {
            str(k): int(v) for k,v in inform.hydroperiod.value_counts().items()},
        "crude_prior_strong_risk": {
            str(k):float(v) for k,v in inform.groupby("prior_strong").strong.mean().items()},
        "main_strict_prior_strong": fit_with_block_bootstrap(
            inform, "strong", False, args.bootstrap),
        "adjusted_strict_prior_strong": fit_with_block_bootstrap(
            inform, "strong", True, args.bootstrap),
        "temporal_subgroups": {},
        "secondary_thresholds": {},
        "falsification_limits": [
            "Not NPS rainfall-conditioned activation geometry or frogcs RC6 C.",
            "Max call index increases mechanically with recordings per year.",
            "Site use = acoustic use; no individuals, breeding success, fish or emergent plant density.",
            "Hydroperiod is categorical; not measured water level at each recording.",
            "Residual association can arise from stable unmeasured habitat suitability.",
            "Within park×taxon×year selection requires historical contrast; external generality restricted.",
        ],
    }
    for nm, yr in [("early_2017_2020", inform.EventYear <= 2020),
                   ("later_2021_2023", inform.EventYear >= 2021)]:
        d = inform.loc[yr].copy()
        result["temporal_subgroups"][nm] = fit_with_block_bootstrap(
            d, "strong", False, args.bootstrap, SEED+85)
    for outcome in ["any_call", "full"]:
        result["secondary_thresholds"][outcome] = fit_with_block_bootstrap(
            inform, outcome, False, args.bootstrap, SEED+123)
    # Hydroperiod taxon-year stratification is not a causal hydration
    # treatment; profile only the presence of variation in informative set.
    Path(args.out).mkdir(parents=True, exist_ok=True)
    (Path(args.out)/"observed_results.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2)+"\n",encoding="utf-8")
    print("BEGIN_NPS_STRICT_HISTORY_RESULTS")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    print("END_NPS_STRICT_HISTORY_RESULTS")


if __name__ == "__main__":
    run()
