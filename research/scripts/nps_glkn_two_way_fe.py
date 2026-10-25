#!/usr/bin/env python3
"""NPS GLKN two-way species-year × station-year fixed-effect site-history test.

POST-HOC exploratory sensitivity: research/NPS_TWO_WAY_SITE_YEAR_HISTORY_SPEC_V0_1.md
Study: Casper et al. NPS GLKN (2026), DOI 10.57830/2320505.
This is independent NPS acoustic history, NOT a NAAMP rainfall/C result.
"""
import argparse
import json
import math
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd

from nps_glkn_strict_history import (
    build_yearly, fetch_csv, informative_groups, strict_prior_panel
)

SEED = 20261025
BY_SPECIES_YEAR = ["ParkCode", "ScientificName", "EventYear"]
BY_SITE_YEAR = ["ParkCode", "SiteLocation", "EventYear"]
NUISANCES = ["other_prior_fixed", "other_prior_missing",
             "log_current_effort", "log_prior_effort", "prior_years_seen"]


def require(cond, msg):
    if not cond:
        raise ValueError(msg)


def group_codes(df, keys):
    ix = pd.MultiIndex.from_frame(df[keys])
    return pd.factorize(ix, sort=True)[0]


def residualize_groups(v, labels, n_groups):
    """Mean subtract matrix columns within cluster labels."""
    num = np.bincount(labels, minlength=n_groups).astype(float)
    means = np.stack(
        [np.bincount(labels, weights=v[:, j], minlength=n_groups) / num
         for j in range(v.shape[1])], axis=1)
    return v - means[labels]


def absorb_two_way(values, g1, g2, maxiter=1200, tol=1e-9):
    """
    Alternating orthogonal projections onto complements of two FE spaces.
    Store convergence diagnostics; fail closed if not converged.
    """
    r = np.asarray(values, dtype=float).copy()
    n1, n2 = int(g1.max()) + 1, int(g2.max()) + 1
    last = None
    for iteration in range(maxiter):
        old = r.copy()
        r = residualize_groups(r, g1, n1)
        r = residualize_groups(r, g2, n2)
        diff = float(np.max(np.abs(r - old)))
        last = diff
        if diff < tol:
            check = residualize_groups(r, g1, n1)
            if np.max(np.abs(check - r)) < 2e-7:
                return r, dict(iterations=iteration+1, error=diff,
                               max_group1_demean_error=float(np.max(np.abs(check-r))))
    raise RuntimeError("Two-way FE projection failed to converge: max change "
                       + str(last))


def clustered_standard_error(residual_x, response_residual, labels):
    score = residual_x * response_residual
    gr, groups = pd.factorize(labels, sort=True)
    G = len(groups)
    sxx = float(np.dot(residual_x, residual_x))
    scores = np.bincount(gr, weights=score, minlength=G)
    se = math.sqrt(G / (G-1) * float(np.dot(scores, scores)) / (sxx*sxx))
    return {"clusters": G, "se": se,
            "ci95_normal_approx": None if not math.isfinite(se) else None}


def fit_model(df, two_way, adjusted, name):
    if df.empty:
        return {"name": name, "estimable": False, "reason": "empty filtered panel"}
    d = df.reset_index(drop=True).copy()
    r1 = group_codes(d, BY_SPECIES_YEAR)
    r2 = group_codes(d, BY_SITE_YEAR)
    covars = NUISANCES if adjusted else []
    V = np.column_stack([d["strong"].astype(float).to_numpy(),
                         d["prior_strong"].astype(float).to_numpy()]
                        + [d[c].astype(float).to_numpy() for c in covars])
    if not np.isfinite(V).all():
        return {"name": name, "estimable": False,
                "reason": "missing measured history/effort"}
    try:
        if two_way:
            W, convergence = absorb_two_way(V, r1, r2)
        else:
            W = residualize_groups(V, r1, int(r1.max()) + 1)
            convergence = {"iterations": 1, "error": 0.0}
    except RuntimeError as e:
        return {"name":name, "estimable":False, "reason":str(e)}
    y, x = W[:, 0], W[:, 1]
    if np.dot(x, x) < 1e-10:
        return {"name": name, "estimable": False,
                "reason": "focal prior strong indicator absorbed by fixed effects"}
    X = x[:, None]
    kept = []
    dropped = []
    for j, col in enumerate(covars):
        candidate = W[:, j+2]
        test = np.column_stack([X, candidate])
        if np.linalg.matrix_rank(test, tol=1e-8) == test.shape[1]:
            X = test
            kept.append(col)
        else:
            dropped.append(col)
    coeff, *_ = np.linalg.lstsq(X, y, rcond=None)
    fitted_resid = y - X @ coeff
    if X.shape[1] == 1:
        focus_resid = x
    else:
        focus_resid = x - X[:, 1:] @ np.linalg.lstsq(
            X[:, 1:], x, rcond=None)[0]
    gsite = (d.ParkCode.astype(str) + "/" + d.SiteLocation.astype(str)).to_numpy()
    gtaxon = (d.ParkCode.astype(str) + "/" + d.ScientificName.astype(str)).to_numpy()
    ses = {}
    for key, labels in [("station", gsite), ("park_taxon", gtaxon)]:
        seinfo = clustered_standard_error(focus_resid, fitted_resid, labels)
        se = seinfo["se"]
        ses[key] = {
            "clusters": seinfo["clusters"],
            "se": se,
            "normal_approx_95ci": [float(coeff[0] - 1.96*se),
                                   float(coeff[0] + 1.96*se)],
        }
    return {
        "name":name, "estimable":True,
        "n_site_taxon_year":int(len(d)),
        "n_park_taxon_year_fe":int(r1.max()+1),
        "n_park_station_year_fe":int(r2.max()+1),
        "n_park_taxon_trajectories":int(len(set(gtaxon))),
        "n_stations":int(len(set(gsite))),
        "prior_history_covariates_kept":kept,
        "nuisance_rank_dropped":dropped,
        "coefficient_prior_same_species_strong":float(coeff[0]),
        "coefficients_nuisance":{k:float(v) for k,v in zip(kept,coeff[1:])},
        "cluster_se":ses,
        "convergence":convergence,
        "interpretation":"Post-hoc descriptive LPM with species×park×year"
                         + (" and station×park×year fixed effects" if two_way
                            else " fixed effects only")
                         + "; no individual memory or plant/predator cause",
    }


def prior_any_panel(annual, panel):
    dat=[]
    for (p,s,t), d in annual.groupby(
        ["ParkCode","SiteLocation","ScientificName"], sort=False
    ):
        any_previous = 0
        for item in d.sort_values("EventYear").itertuples():
            dat.append((p,s,t,int(item.EventYear),int(any_previous)))
            any_previous = max(any_previous, int(item.any_call))
    past=pd.DataFrame(dat,columns=[
        "ParkCode","SiteLocation","ScientificName","EventYear","prior_any"])
    return panel.merge(past,how="left",
                       on=["ParkCode","SiteLocation",
                           "ScientificName","EventYear"],
                       validate="one_to_one")


def run():
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",default="research/results/nps_glkn_two_way")
    args=ap.parse_args()
    with tempfile.TemporaryDirectory() as temp:
        src=Path(temp)/"glkn.csv"
        n_bytes=fetch_csv(src)
        annual, source_audit = build_yearly(src)
    panel=strict_prior_panel(annual)
    informative,_=informative_groups(panel)
    require(len(informative)==1815,"Frozen informative sample changed")
    result={
        "source":"NPS GLKN 2016–2023 DOI 10.57830/2320505",
        "status":"exploratory_posthoc_not_preregistered",
        "source_sha256":"b1c11cf70472a906e6c238a690a5a12373cdd20ef4d5e180fa3f376d520118c2",
        "source_bytes":n_bytes,
        "spec":"research/NPS_TWO_WAY_SITE_YEAR_HISTORY_SPEC_V0_1.md",
        "question":"Does same-species historical chorus persist after exact common station×year and species×park×year environment?",
        "source_audit":source_audit,
        "base_sample":len(informative),
        "main_models":{
            "one_way_original_unadjusted":fit_model(informative,False,False,"one_way_unadjusted"),
            "one_way_exact_adjustment":fit_model(informative,False,True,"one_way_adjusted_same_sample"),
            "two_way_unadjusted":fit_model(informative,True,False,"two_way_unadjusted"),
            "two_way_adjusted":fit_model(informative,True,True,"two_way_adjusted")
        },
        "same_species_weak_vs_strong":{},
        "leave_one_park_out":[],
        "limits":[
            "Observed acoustic persistence, not same-individual fidelity.",
            "Station-year FE removes generic station-state but NOT taxon-specific plant preference or abundance.",
            "Fixed annual maximum CIV depends on effort and phenology; coefficients are predictive associations.",
            "NPS does not measure emergent macrophyte structure, predator stages or rainfall recency.",
            "This analysis was conceived after primary NPS result was seen; not a new independent confirmatory test.",
            "Site and park×species cluster normal intervals are diagnostic rather than causal.",
            "No NAAMP conditional C or live pond geometry is estimated."
        ]
    }
    panel=prior_any_panel(annual,panel)
    sub, _=informative_groups(panel.loc[panel.prior_any==1])
    result["same_species_weak_vs_strong"]={
        "n_eligible_rows":len(sub),
        "two_way_unadjusted":fit_model(sub,True,False,"prior_weak_vs_strong_two_way"),
        "two_way_adjusted":fit_model(sub,True,True,"prior_weak_vs_strong_two_way_adjusted")
    }
    for park in sorted(informative.ParkCode.unique()):
        other=informative.loc[informative.ParkCode!=park].copy()
        z=fit_model(other,True,True,f"exclude_{park}")
        result["leave_one_park_out"].append({
            "park_excluded":str(park),"n":len(other),
            "estimable":z.get("estimable"),
            "estimate":z.get("coefficient_prior_same_species_strong"),
            "reason":z.get("reason")
        })
    out=Path(args.out);out.mkdir(parents=True, exist_ok=True)
    (out/"observed_results.json").write_text(
        json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf8")
    print("BEGIN_NPS_TWO_WAY_RESULTS")
    print(json.dumps(result,indent=2,ensure_ascii=False))
    print("END_NPS_TWO_WAY_RESULTS")


if __name__=="__main__":
    run()
