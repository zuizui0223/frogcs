"""G7: fixed, trait-motivated composition moderation of vegetation and calling.

The contrast is between species groups, not measured larval durations. Numerical
uncertainty is conditional on fixed SDMs and the prospectively specified design.
No real-data outcome association is calculated by ``--preflight-only``.
"""
from __future__ import annotations

import os
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("OMP_NUM_THREADS", "1")

import argparse
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import platform
import time

import numpy as np
import pandas as pd
from scipy.linalg import cho_factor, cho_solve
from scipy.special import expit

import acoustic_mechanism_cv as original_bridge
from acoustic_mechanism_cv import (
    prepare_sites, assign_spatial_folds, zrank, log_score,
    SURVEY, ENV, BACKGROUNDS, RIDGE,
)

ROOT = Path(__file__).resolve().parents[2]
SEED = 20261107
BOOTSTRAPS = 999
MAIN_SHA = "5e2f0a87c639df373fa2700b29403d2ab417a1cc"
BRIDGE_SHA = "a5ddc281ba17017a52b404a5725327f6e829824f"
HELPER_HASH = "8bfb608a90320b6193ca2c01ef5839141f457f3559cd011cf4695e2c0d161179"
PROTOCOL_HASH = "22ec3bfcb26175e01804e035e1ca5e6224b0c14beefc3e54242bb9089629860a"
SOURCE_PATHS = {
    "predictions": ROOT / "research/results/interaction_species_sdm_20261026/naamp_species_suitability.csv.gz",
    "sites": ROOT / "research/results/naamp_remote_vegetation_20261026/primary_site_landscape_context.csv.gz",
    "visits": ROOT / "research/results/naamp_three_guild_occurrence/full_naamp_history/naamp_completed_site_surveys.csv.gz",
}
SOURCE_HASHES = {
    "predictions": "a2a7018e747349ff94b0b98c36fed0958458f652bfa658568c3a498141bdb637",
    "sites": "cbb389264f8bf167f53b5dfd38c5e1a17aec6243cc6ce30cbb7ae3b5417f75ff",
    "visits": "74d28435ce6e1a842e003eaa6754c6db373e026728cfbf457784814c47cd997c",
}
TAXA = {
    "2431978": "Ambystoma mavortium", "2431993": "Ambystoma tigrinum",
    "2431951": "Ambystoma maculatum", "2432014": "Ambystoma laterale",
    "5218390": "Notophthalmus viridescens",
}
VARIANTS = ("primary", "pooled_newt_sensitivity")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def join_trait_predictors(sites, predictions):
    """Align the five pre-fixed species by ID; never silently drop a species."""
    require("site" in sites and sites.site.is_unique, "Duplicate or absent primary site IDs")
    required = {"site", "species_key", "species", "background", "suitability_percentile"}
    require(required.issubset(predictions), "Missing species-prediction columns")
    p = predictions.copy()
    p["species_key"] = p.species_key.astype(str)
    selected = p.species_key.isin(TAXA) | p.species.isin(TAXA.values())
    p = p.loc[selected & p.site.isin(sites.site)].copy()
    require(p.species_key.isin(TAXA).all(), "Species name and original key disagree")
    require(p.species.eq(p.species_key.map(TAXA)).all(), "Species name and original key disagree")
    require(set(p.background) == set(BACKGROUNDS), "Original SDM backgrounds missing or changed")
    require(not p.duplicated(["site", "species_key", "background"]).any(),
            "Duplicate site/species/background predictions")
    require(len(p) == len(sites)*5*2, "Incomplete five-species prediction grid")
    require(np.isfinite(p.suitability_percentile.to_numpy(float)).all(), "Nonfinite species suitability")
    require(p.suitability_percentile.between(0, 1).all(), "Suitability percentile outside [0,1]")
    d = sites.copy().reset_index(drop=True)
    for bg in BACKGROUNDS:
        q = p[p.background == bg].pivot(index="site", columns="species_key", values="suitability_percentile")
        require(set(q.columns) == set(TAXA) and len(q) == len(d), "Missing species/site predictions")
        q = q.reindex(d.site)
        require(not q.isna().any().any(), "Missing species after site-ID alignment")
        t = (q["2431978"].to_numpy() + q["2431993"].to_numpy())/2
        b = (q["2431951"].to_numpy() + q["2432014"].to_numpy())/2
        newt = q["5218390"].to_numpy()
        a, c = (t+b)/2, t-b
        rest = (2*b+newt)/3
        values = {"T": t, "B": b, "N": newt, "A": a, "C": c,
                  "R": rest, "A5": (2*t+3*rest)/5, "C5": t-rest}
        source_name = "mean_suitability_pond_breeding_Caudata_" + bg
        require(source_name in d, "Original five-species mean missing")
        require(np.allclose(.8*a+.2*newt, d[source_name].to_numpy(), rtol=0, atol=1e-12),
                "Five-species means no longer reproduce original pond-Caudata scores")
        for name, vector in values.items():
            d[name + "_" + bg] = vector
    return d


@dataclass
class Design:
    base: np.ndarray
    full: np.ndarray
    base_names: tuple
    full_names: tuple
    scaling_rows: list


def build_design(d, background, variant="primary"):
    """Freeze biological transformations on the full cohort, without outcomes."""
    require(background in BACKGROUNDS and variant in VARIANTS, "Unknown frozen comparison")
    raw_names = ("A", "C", "N") if variant == "primary" else ("A5", "C5")
    scaled, scales = {}, []
    for name in raw_names:
        raw = d[name+"_"+background].to_numpy(float)
        mean, sd = float(raw.mean()), float(raw.std())
        require(np.isfinite(raw).all() and sd > 1e-12, "Unvarying or nonfinite group index: "+name)
        scaled[name] = (raw-mean)/sd
        scales.append(dict(background=background, variant=variant, index=name, mean=mean, population_sd=sd))
    o = zrank(d["mean_suitability_Odonata_"+background])
    v = d.V.to_numpy(float)
    require(np.isin(v, [0., 1.]).all(), "Vegetation must retain the binary 3-km definition")
    if variant == "primary":
        a, c, n = (scaled[name] for name in ("A", "C", "N"))
        names = ["O", "A", "C", "N", "V", "OA", "OC", "ON", "OV", "VA", "VN", "OVA", "OVN"]
        columns = [o, a, c, n, v, o*a, o*c, o*n, o*v, v*a, v*n, o*v*a, o*v*n]
    else:
        a, c = scaled["A5"], scaled["C5"]
        names = ["O", "A5", "C5", "V", "OA5", "OC5", "OV", "VA5", "OVA5"]
        columns = [o, a, c, v, o*a, o*c, o*v, v*a, o*v*a]
    for name in SURVEY + ENV:
        names.append(name)
        columns.append(d[name].to_numpy(float))
    lat, lon = zrank(d[["lat", "lon"]].to_numpy(float)).T
    names += ["latitude_rank", "longitude_rank", "latitude_rank_squared", "latitude_longitude_rank", "longitude_rank_squared"]
    columns += [lat, lon, lat*lat, lat*lon, lon*lon]
    e = zrank(d[list(ENV)].to_numpy(float))
    for i, name in enumerate(ENV):
        names.append("rank_square_"+name)
        columns.append(e[:, i]*e[:, i])
    for i in range(len(ENV)):
        for j in range(i+1, len(ENV)):
            names.append("rank_product_"+ENV[i]+"_"+ENV[j])
            columns.append(e[:, i]*e[:, j])
    base = np.column_stack(columns)
    full = np.column_stack((base, v*c))
    require(np.isfinite(full).all(), "Nonfinite frozen design")
    return Design(base, full, tuple(names), tuple(names)+("VC" if variant == "primary" else "VC5",), scales)


def numerical_scaling(x):
    x = np.asarray(x, float)
    require(x.ndim == 2 and len(x) > 0 and np.isfinite(x).all(), "Invalid predictor matrix")
    return x.mean(axis=0), x.std(axis=0)


@dataclass
class BinomialFit:
    coefficients: np.ndarray
    standardized_coefficients: np.ndarray
    converged: bool
    iterations: int
    gradient_max: float
    objective: float

    def predict(self, x):
        return np.clip(expit(self.coefficients[0]+np.asarray(x)@self.coefficients[1:]), 1e-10, 1-1e-10)


def fit_binomial(x, k, n, *, ridge=RIDGE, multiplicity=None, scaling=None, initial=None, maxiter=80):
    """Unrestricted binomial ridge fit, with block-frequency weights.

    The intercept is unpenalized. Return coefficients in the supplied feature
    units, undoing only this numerical centering/scaling. A supplied ``scaling``
    stays fixed when block multiplicities change in a coefficient bootstrap.
    """
    x, k, n = np.asarray(x, float), np.asarray(k, float), np.asarray(n, float)
    require(x.ndim == 2 and k.shape == n.shape == (len(x),), "Invalid binomial dimensions")
    require(np.isfinite(x).all() and np.isfinite(k).all() and np.isfinite(n).all(),
            "Nonfinite binomial data")
    require(np.all(n > 0) and np.all((k >= 0) & (k <= n)), "Invalid binomial counts")
    require(ridge >= 0, "Negative ridge penalty")
    w = np.ones(len(x)) if multiplicity is None else np.asarray(multiplicity, float)
    require(w.shape == k.shape and np.isfinite(w).all() and np.all(w >= 0) and w.sum() > 0,
            "Invalid bootstrap multiplicities")
    mu, sd = numerical_scaling(x) if scaling is None else (np.asarray(q, float) for q in scaling)
    require(mu.shape == sd.shape == (x.shape[1],) and np.isfinite(mu).all() and np.isfinite(sd).all()
            and np.all(sd >= 0), "Invalid frozen numerical scaling")
    good = sd > 1e-12
    z = np.column_stack((np.ones(len(x)), (x[:, good]-mu[good])/sd[good]))
    wn, wk = w*n, w*k
    if initial is None:
        p0 = np.clip(wk.sum()/wn.sum(), 1e-6, 1-1e-6)
        beta = np.zeros(z.shape[1])
        beta[0] = np.log(p0/(1-p0))
    else:
        beta = np.array(initial, dtype=float, copy=True)
        require(beta.shape == (z.shape[1],) and np.isfinite(beta).all(), "Invalid fixed-scale warm start")
    penalty = np.full(z.shape[1], float(ridge))
    penalty[0] = 0.

    def objective(b):
        eta = z@b
        return float(wn@np.logaddexp(0, eta)-wk@eta + .5*np.dot(penalty*b, b))

    converged = False
    tolerance = 1e-7 + 1e-9*wn.sum()
    iteration = 0
    for iteration in range(1, maxiter+1):
        probability = expit(z@beta)
        gradient = z.T@(wn*probability-wk)+penalty*beta
        gradient_max = float(np.max(np.abs(gradient)))
        if gradient_max <= tolerance:
            converged = True
            break
        fisher = z.T@(z*(wn*probability*(1-probability))[:, None])
        fisher.flat[::len(fisher)+1] += penalty
        try:
            step = cho_solve(cho_factor(fisher, lower=True, check_finite=False), gradient, check_finite=False)
        except np.linalg.LinAlgError:
            break
        old = objective(beta)
        decrement = float(gradient@step)
        if not np.isfinite(step).all() or decrement < 0:
            break
        alpha = 1.
        accepted = False
        for _ in range(30):
            proposal = beta-alpha*step
            value = objective(proposal)
            if np.isfinite(value) and value <= old-1e-4*alpha*decrement+1e-12*max(1., abs(old)):
                beta = proposal
                accepted = True
                break
            alpha *= .5
        if not accepted:
            break
    probability = expit(z@beta)
    gradient = z.T@(wn*probability-wk)+penalty*beta
    gradient_max = float(np.max(np.abs(gradient)))
    converged = bool(np.isfinite(beta).all() and gradient_max <= tolerance)
    coefficients = np.zeros(x.shape[1]+1)
    coefficients[1:][good] = beta[1:]/sd[good]
    coefficients[0] = beta[0]-mu@coefficients[1:]
    return BinomialFit(coefficients, beta, converged, iteration, gradient_max, objective(beta))


def block_multiplicities(site_blocks, replicates=BOOTSTRAPS, seed=SEED):
    """One paired resampling schedule, reused for every model/background."""
    site_blocks = np.asarray(site_blocks)
    require(site_blocks.ndim == 1 and len(site_blocks) > 0 and replicates > 0, "Empty bootstrap input")
    labels, codes = np.unique(site_blocks, return_inverse=True)
    rng = np.random.default_rng(seed)
    selected = rng.integers(0, len(labels), size=(replicates, len(labels)))
    counts = np.zeros((replicates, len(labels)), dtype=np.int64)
    for i, row in enumerate(selected):
        counts[i] = np.bincount(row, minlength=len(labels))
    return labels, codes, counts


def paired_holdout_gain(null, full, block_labels, multiplicities):
    """Pair identical site outcomes before resampling summed loss/visit totals."""
    needed = {"site", "spatial_block", "k", "n", "predicted"}
    require(needed.issubset(null) and needed.issubset(full), "Missing paired prediction columns")
    require(null.site.is_unique and full.site.is_unique, "Duplicate held-out site predictions")
    require(len(null) == len(full) and set(null.site) == set(full.site), "Unpaired held-out sites")
    a = null.set_index("site").sort_index()
    b = full.set_index("site").reindex(a.index)
    for name in ("spatial_block", "k", "n"):
        require(np.array_equal(a[name].to_numpy(), b[name].to_numpy()), "Unpaired held-out "+name)
    require(np.isfinite(a.predicted).all() and np.isfinite(b.predicted).all(), "Nonfinite held-out probability")
    labels, counts = np.asarray(block_labels), np.asarray(multiplicities)
    require(labels.ndim == 1 and len(np.unique(labels)) == len(labels)
            and set(labels) == set(a.spatial_block), "Bootstrap blocks do not match predictions")
    require(counts.ndim == 2 and counts.shape[1] == len(labels) and np.all(counts >= 0)
            and np.all(counts.sum(axis=1) == len(labels)), "Invalid paired block resampling")
    delta = log_score(a.k.to_numpy(), a.n.to_numpy(), a.predicted.to_numpy())
    delta -= log_score(b.k.to_numpy(), b.n.to_numpy(), b.predicted.to_numpy())
    block = a.assign(delta=delta).groupby("spatial_block").agg(delta=("delta", "sum"), n=("n", "sum")).reindex(labels)
    numerators = counts@block.delta.to_numpy()
    denominators = counts@block.n.to_numpy()
    require(np.all(denominators > 0), "Empty paired-score bootstrap denominator")
    draw = numerators/denominators
    low, high = np.quantile(draw, [.025, .975])
    return dict(gain_nll_per_survey=float(delta.sum()/a.n.sum()), bootstrap_95_low=float(low),
                bootstrap_95_high=float(high), n_sites=len(a), n_surveys=int(a.n.sum()),
                n_blocks=len(labels), n_bootstrap=len(counts))


def residual_information_ratio(base, target):
    """Fraction of centred target information remaining after the whole base."""
    base, target = np.asarray(base, float), np.asarray(target, float)
    require(base.ndim == 2 and target.shape == (len(base),), "Invalid residual-information dimensions")
    require(np.isfinite(base).all() and np.isfinite(target).all(), "Nonfinite residual-information input")
    total = float(np.sum((target-target.mean())**2))
    if total <= 1e-20:
        return 0.
    mu, sd = numerical_scaling(base)
    good = sd > 1e-12
    x = np.column_stack((np.ones(len(base)), (base[:, good]-mu[good])/sd[good]))
    residual = target-x@np.linalg.lstsq(x, target, rcond=1e-10)[0]
    return float(np.clip(np.sum(residual*residual)/total, 0., 1.))


def validate_folds(d, folds, expected_folds=5):
    folds = np.asarray(folds)
    require(folds.shape == (len(d),) and set(np.unique(folds)) == set(range(expected_folds)), "Missing original spatial fold")
    require(d.site.is_unique, "Duplicate site in spatial holdout")
    check = d.assign(fold=folds)
    require(check.groupby("route").fold.nunique().max() == 1, "Route leaked across folds")
    require(check.groupby("spatial_block").fold.nunique().max() == 1, "Geographical block leaked across folds")


def verify_source_hashes(paths, expected=SOURCE_HASHES):
    rows = []
    require(set(paths) == set(expected), "Missing immutable source path")
    for label, path in paths.items():
        actual = sha256(path)
        require(actual == expected[label], "Immutable source hash mismatch: "+label)
        rows.append(dict(source=label, path=str(Path(path).resolve()), sha256=actual,
                         n_bytes=Path(path).stat().st_size))
    return rows


def preflight_diagnostics(d, designs, folds):
    """Support and design geometry only; no outcome correlations or model fits."""
    validate_folds(d, folds)
    support, information, variation = [], [], []
    gates = {}
    for (background, variant), design in designs.items():
        contrast = "C" if variant == "primary" else "C5"
        c = d[contrast+"_"+background].to_numpy(float)
        low, high = np.quantile(c, [1/3, 2/3])
        eligible_cutpoints = bool(low < high)
        bins = np.searchsorted([low, high], c, side="left")
        cell_passes = []
        for v in (0, 1):
            for tier, label in ((0, "low"), (2, "high")):
                g = d.loc[(d.V.to_numpy() == v) & (bins == tier)]
                counts = dict(n_sites=len(g), n_routes=int(g.route.nunique()),
                              n_blocks=int(g.spatial_block.nunique()), n_surveys=int(g.n.sum()))
                passed = bool(eligible_cutpoints and counts["n_sites"] >= 20 and counts["n_routes"] >= 5
                              and counts["n_blocks"] >= 3 and counts["n_surveys"] >= 200)
                cell_passes.append(passed)
                support.append(dict(background=background, variant=variant, V=v, contrast_tertile=label,
                                    low_cutpoint=float(low), high_cutpoint=float(high), **counts, passed=passed))
        information_passes = []
        for fold in (-1, *range(5)):
            subset = np.ones(len(d), dtype=bool) if fold == -1 else folds != fold
            ratio = residual_information_ratio(design.base[subset], design.full[subset, -1])
            passed = bool(ratio >= .01)
            information_passes.append(passed)
            information.append(dict(background=background, variant=variant, held_out_fold=fold,
                                    scope="full_cohort" if fold == -1 else "training",
                                    n_sites=int(subset.sum()), residual_information_ratio=ratio,
                                    base_projection_r_squared=1-ratio, passed=passed))
        cframe = pd.DataFrame(dict(c=c, block=d.spatial_block.to_numpy()))
        block_mean = cframe.groupby("block").c.transform("mean").to_numpy()
        within = float(np.mean((c-block_mean)**2))
        between = float(np.mean((block_mean-c.mean())**2))
        variation.append(dict(background=background, variant=variant, contrast=contrast,
                              population_variance=float(np.var(c)), within_block_variance=within,
                              between_block_variance=between,
                              n_varying_blocks=int(cframe.groupby("block").c.nunique().gt(1).sum())))
        gates[(background, variant)] = bool(all(cell_passes) and all(information_passes))
    return pd.DataFrame(support), pd.DataFrame(information), pd.DataFrame(variation), gates


def heldout_predictions(d, designs, folds):
    """Train numerical scaling and both acoustic candidates within training rows."""
    validate_folds(d, folds)
    k, n = d.k.to_numpy(), d.n.to_numpy()
    predictions, diagnostics = [], []
    for (background, variant), design in designs.items():
        for fold in range(5):
            test = folds == fold
            train = ~test
            for candidate, x, names in (("null", design.base, design.base_names),
                                         ("full", design.full, design.full_names)):
                fitted = fit_binomial(x[train], k[train], n[train])
                probability = fitted.predict(x[test])
                v_index = names.index("V")+1
                theta = float(fitted.coefficients[-1]) if candidate == "full" else np.nan
                diagnostics.append(dict(background=background, variant=variant, fold=fold,
                    candidate=candidate, n_training_sites=int(train.sum()), n_test_sites=int(test.sum()),
                    theta=theta, vegetation_coefficient=float(fitted.coefficients[v_index]),
                    converged=fitted.converged, iterations=fitted.iterations,
                    gradient_max=fitted.gradient_max, penalized_training_objective=fitted.objective))
                rows = d.loc[test, ["site", "route", "spatial_block", "k", "n", "V"]].copy()
                rows["fold"] = fold
                rows["background"] = background
                rows["variant"] = variant
                rows["candidate"] = candidate
                rows["predicted"] = probability
                predictions.append(rows)
    output = pd.concat(predictions, ignore_index=True)
    require(not output.duplicated(["site", "background", "variant", "candidate"]).any(),
            "Duplicate holdout predictions")
    require(output.groupby(["background", "variant", "candidate"]).site.nunique().eq(len(d)).all(),
            "Incomplete holdout predictions")
    return output, pd.DataFrame(diagnostics)


def coefficient_bootstrap(d, designs, block_codes, multiplicities):
    """Refit the entire model under paired whole-block multiplicities."""
    k, n = d.k.to_numpy(), d.n.to_numpy()
    draws, full_coefficients, scaling_rows, points = [], [], [], {}
    for key, design in designs.items():
        background, variant = key
        scaling = numerical_scaling(design.full)
        point = fit_binomial(design.full, k, n, scaling=scaling)
        points[key] = point
        for i, name in enumerate(design.full_names):
            scaling_rows.append(dict(background=background, variant=variant, feature=name,
                                     numerical_mean=float(scaling[0][i]), numerical_sd=float(scaling[1][i])))
        for i, name in enumerate(("intercept",)+design.full_names):
            full_coefficients.append(dict(background=background, variant=variant, term=name,
                                          coefficient=float(point.coefficients[i]), converged=point.converged,
                                          iterations=point.iterations, gradient_max=point.gradient_max))
        v_index = design.full_names.index("V")+1
        for draw_index, block_count in enumerate(multiplicities):
            weights = block_count[block_codes]
            record = dict(background=background, variant=variant, draw=draw_index,
                          weighted_sites=int(weights.sum()), weighted_visits=int(weights@n))
            try:
                fitted = fit_binomial(design.full, k, n, multiplicity=weights, scaling=scaling,
                                      initial=point.standardized_coefficients)
                record.update(theta=float(fitted.coefficients[-1]),
                              vegetation_coefficient=float(fitted.coefficients[v_index]),
                              converged=fitted.converged, iterations=fitted.iterations,
                              gradient_max=fitted.gradient_max,
                              error="" if fitted.converged else "Newton convergence criterion unmet")
            except (ValueError, np.linalg.LinAlgError, FloatingPointError) as error:
                record.update(theta=np.nan, vegetation_coefficient=np.nan, converged=False,
                              iterations=0, gradient_max=np.nan,
                              error=type(error).__name__+": "+str(error))
            draws.append(record)
            if (draw_index+1) % 100 == 0 or draw_index+1 == len(multiplicities):
                print("G7 coefficient refits", background, variant, draw_index+1, "/", len(multiplicities), flush=True)
    return points, pd.DataFrame(draws), pd.DataFrame(full_coefficients), pd.DataFrame(scaling_rows)


def summarize_coefficients(points, draws, designs, gates, replicates):
    rows = []
    for (background, variant), point in points.items():
        group = draws[(draws.background == background) & (draws.variant == variant)]
        valid = group.converged & np.isfinite(group.theta) & np.isfinite(group.vegetation_coefficient)
        n_valid = int(valid.sum())
        if n_valid:
            low, high = np.quantile(group.loc[valid, "theta"], [.025, .975])
            v_low, v_high = np.quantile(group.loc[valid, "vegetation_coefficient"], [.025, .975])
        else:
            low = high = v_low = v_high = np.nan
        design = designs[(background, variant)]
        v_index = design.full_names.index("V")+1
        convergence_gate = bool(point.converged and n_valid >= 990 and replicates == BOOTSTRAPS)
        support_gate = bool(gates[(background, variant)])
        positive = bool(support_gate and convergence_gate and np.isfinite(low) and low > 0)
        rows.append(dict(background=background, variant=variant, theta=float(point.coefficients[-1]),
                         bootstrap_95_low=float(low), bootstrap_95_high=float(high),
                         vegetation_coefficient=float(point.coefficients[v_index]),
                         vegetation_bootstrap_95_low=float(v_low), vegetation_bootstrap_95_high=float(v_high),
                         point_converged=point.converged, point_gradient_max=point.gradient_max,
                         n_bootstrap=replicates, n_valid_bootstrap=n_valid, n_failed_bootstrap=int(len(group)-n_valid),
                         predictor_support_gate=support_gate, convergence_gate=convergence_gate,
                         positive_association_qualified=positive))
    return pd.DataFrame(rows)


def summarize_holdouts(predictions, diagnostics, block_labels, multiplicities):
    scores, gains = [], []
    for (background, variant, candidate), group in predictions.groupby(["background", "variant", "candidate"]):
        k, n, p = (group[name].to_numpy() for name in ("k", "n", "predicted"))
        scores.append(dict(background=background, variant=variant, candidate=candidate,
                           n_sites=len(group), n_surveys=int(n.sum()), n_blocks=int(group.spatial_block.nunique()),
                           nll_per_survey=float(log_score(k, n, p).sum()/n.sum()),
                           brier_per_survey=float(np.sum(k*(1-p)**2+(n-k)*p*p)/n.sum())))
    for (background, variant), group in predictions.groupby(["background", "variant"]):
        result = paired_holdout_gain(group[group.candidate == "null"], group[group.candidate == "full"],
                                     block_labels, multiplicities)
        fit = diagnostics[(diagnostics.background == background) & (diagnostics.variant == variant)]
        converged = bool(fit.converged.all())
        result.update(background=background, variant=variant, all_holdout_fits_converged=converged,
                      positive_predictive_gain_qualified=bool(converged and len(multiplicities) == BOOTSTRAPS
                                                               and result["bootstrap_95_low"] > 0))
        gains.append(result)
    return pd.DataFrame(scores), pd.DataFrame(gains)


def write_csv(table, path):
    if str(path).endswith(".gz"):
        table.to_csv(path, index=False, compression={"method": "gzip", "mtime": 0})
    else:
        table.to_csv(path, index=False)


def write_json(value, path):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False)+"\n", encoding="utf-8")


def run(*, protocol, out, bootstrap=BOOTSTRAPS, preflight_only=False):
    """Use only the frozen sources and preserve every fitted comparison."""
    started = time.monotonic()
    require(bootstrap > 0, "Bootstrap count must be positive")
    source_receipt = verify_source_hashes(SOURCE_PATHS)
    require(sha256(protocol) == PROTOCOL_HASH, "Frozen G7 protocol hash mismatch")
    helper_path = Path(original_bridge.__file__).resolve()
    require(sha256(helper_path) == HELPER_HASH, "Original acoustic helper bytes differ from verified source")
    raw_sites = pd.read_csv(SOURCE_PATHS["sites"], dtype={"site": str})
    visits = pd.read_csv(SOURCE_PATHS["visits"], dtype={"site": str})
    prediction_source = pd.read_csv(SOURCE_PATHS["predictions"], dtype={"site": str, "species_key": str})
    d = prepare_sites(raw_sites, visits, expected_sites=4248)
    require(d.site.is_unique and d.route.nunique() == 432 and d.n.sum() == 63180
            and d.spatial_block.nunique() == 56 and d.V.sum() == 506,
            "Original site/route/visit/block/vegetation ledger changed")
    d = join_trait_predictors(d, prediction_source)
    folds = assign_spatial_folds(d)
    validate_folds(d, folds)
    designs = {(bg, variant): build_design(d, bg, variant) for bg in BACKGROUNDS for variant in VARIANTS}
    support, information, variation, gates = preflight_diagnostics(d, designs, folds)
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    selected = prediction_source[prediction_source.species_key.isin(TAXA) & prediction_source.site.isin(d.site)]
    audit = selected.groupby(["species_key", "species", "background"]).agg(
        n_rows=("site", "size"), n_unique_sites=("site", "nunique"),
        missing_suitability=("suitability_percentile", lambda values: int(values.isna().sum()))).reset_index()
    write_csv(audit, out/"G7_species_prediction_coverage.csv")
    manifest_columns = ["site", "route", "spatial_block", "V", "n"]
    manifest_columns += [name+"_"+bg for bg in BACKGROUNDS for name in ("T", "B", "N", "A", "C", "R", "A5", "C5")]
    manifest = d[manifest_columns].copy()
    manifest["fold"] = folds
    write_csv(manifest, out/"G7_site_group_predictor_manifest.csv.gz")
    write_csv(pd.DataFrame([row for design in designs.values() for row in design.scaling_rows]),
              out/"G7_group_index_standardization.csv")
    write_csv(support, out/"G7_predictor_cell_support.csv")
    write_csv(information, out/"G7_residual_information.csv")
    write_csv(variation, out/"G7_contrast_geographic_variance.csv")
    receipt = dict(
        status="G7_PREFLIGHT_COMPLETE", protocol_path=str(Path(protocol).resolve()),
        protocol_sha256=sha256(protocol), implementation_sha256=sha256(Path(__file__)),
        original_main_sha=MAIN_SHA, original_acoustic_helper_commit=BRIDGE_SHA,
        original_acoustic_helper_sha256=sha256(helper_path), original_sources=source_receipt,
        n_sites=len(d), n_completed_visits=int(d.n.sum()), n_canonical_routes=int(d.route.nunique()),
        n_geographic_blocks=int(d.spatial_block.nunique()), n_folds=5,
        vegetation_positive_sites=int(d.V.sum()), vegetation_zero_sites=int((d.V == 0).sum()),
        source_integrity_passed=True, species_prediction_rows=len(selected),
        support_gates=[dict(background=bg, variant=variant, passed=bool(passed))
                       for (bg, variant), passed in gates.items()],
        new_outcome_associations_computed=False, grouping_changed_after_outcomes=False,
        sdm_refits=0, ridge=RIDGE, bootstrap_seed=SEED, requested_bootstraps=bootstrap,
        species_group_is_measured_duration=False, independent_field_replication=False,
        runtime={"python": platform.python_version(), "numpy": np.__version__, "pandas": pd.__version__},
    )
    write_json(receipt, out/"G7_preflight_receipt.json")
    print("G7 source/predictor preflight complete", json.dumps(receipt["support_gates"]), flush=True)
    if preflight_only:
        return receipt

    labels, codes, multiplicities = block_multiplicities(d.spatial_block.to_numpy(), bootstrap, SEED)
    schedule = pd.DataFrame(multiplicities, columns=labels)
    schedule.insert(0, "draw", np.arange(bootstrap))
    write_csv(schedule, out/"G7_paired_block_multiplicities.csv.gz")
    points, draws, coefficients, numerical_scales = coefficient_bootstrap(d, designs, codes, multiplicities)
    estimates = summarize_coefficients(points, draws, designs, gates, bootstrap)
    write_csv(draws, out/"G7_bootstrap_coefficients.csv.gz")
    write_csv(coefficients, out/"G7_all_fitted_coefficients.csv")
    write_csv(numerical_scales, out/"G7_fixed_bootstrap_numerical_scaling.csv")
    write_csv(estimates, out/"G7_coefficient_summary.csv")
    predictions, fit_diagnostics = heldout_predictions(d, designs, folds)
    scores, gains = summarize_holdouts(predictions, fit_diagnostics, labels, multiplicities)
    write_csv(predictions, out/"G7_heldout_site_predictions.csv.gz")
    write_csv(fit_diagnostics, out/"G7_heldout_fit_diagnostics.csv")
    write_csv(gains, out/"G7_heldout_paired_gains.csv")
    reference = ROOT/"research/results/g6_observation_context_20261106/source/G5_original_site_binomial_acoustic_scores.csv"
    if reference.exists():
        saved = pd.read_csv(reference)
        saved = saved[saved.candidate == "env_add"].set_index("background")
        require(set(saved.index) == set(BACKGROUNDS) and saved.index.is_unique,
                "Original additive-environment score reference is incomplete")
        require(saved.sites.eq(4248).all() and saved.surveys.eq(63180).all() and saved.blocks.eq(56).all(),
                "Original additive-environment score has different denominators")
        scores["original_additive_environment_nll"] = scores.background.map(saved.nll_per_visit)
        scores["gain_vs_original_additive_environment"] = scores.original_additive_environment_nll-scores.nll_per_survey
        receipt["original_additive_environment_score_sha256"] = sha256(reference)
    write_csv(scores, out/"G7_heldout_scores.csv")
    primary = estimates[estimates.variant == "primary"]
    primary_prediction = gains[gains.variant == "primary"]
    receipt.update(
        status="G7_FIXED_COMPOSITION_ANALYSIS_COMPLETE", new_outcome_associations_computed=True,
        completed_bootstraps_per_comparison=bootstrap,
        protocol_bootstrap_count_used=bool(bootstrap == BOOTSTRAPS),
        valid_bootstraps=[dict(background=row.background, variant=row.variant,
                              n_valid=int(row.n_valid_bootstrap), n_failed=int(row.n_failed_bootstrap))
                          for row in estimates.itertuples()],
        primary_positive_association_both_backgrounds=bool(len(primary) == 2 and primary.positive_association_qualified.all()),
        primary_positive_predictive_gain_both_backgrounds=bool(len(primary_prediction) == 2
                                                             and primary_prediction.positive_predictive_gain_qualified.all()),
        heldout_fits_all_converged=bool(fit_diagnostics.converged.all()),
        duration_or_joint_arrival_mechanism_identified=False,
        bootstrap_uncertainty="penalized-model percentile intervals, conditional on fixed SDMs, group definitions and covariates",
        score_uncertainty="paired whole-block resampling conditional on saved held-out predictions",
        elapsed_seconds=round(time.monotonic()-started, 3),
    )
    receipt["output_sha256"] = {path.name: sha256(path) for path in sorted(out.iterdir()) if path.is_file()
                                and path.name != "G7_execution_receipt.json"}
    write_json(receipt, out/"G7_execution_receipt.json")
    print("G7 fixed analysis complete", json.dumps({name: receipt[name] for name in (
        "primary_positive_association_both_backgrounds", "primary_positive_predictive_gain_both_backgrounds",
        "heldout_fits_all_converged", "elapsed_seconds")}), flush=True)
    return receipt


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--bootstrap", type=int, default=BOOTSTRAPS)
    parser.add_argument("--preflight-only", action="store_true")
    args = parser.parse_args()
    run(protocol=args.protocol, out=args.out, bootstrap=args.bootstrap, preflight_only=args.preflight_only)
