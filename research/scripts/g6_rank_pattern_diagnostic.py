"""Apply the original R1 rank contrast to fixed G5 held-out predictions.

This is a retrospective descriptive calibration diagnostic.  Spearman
correlations of smooth held-out probability means and noisy observed k/n are
not samples from an identical response distribution.  Their difference is
therefore neither a calibrated predictive-distribution test nor independent
mechanistic or causal validation.  No model, source parameter, group boundary
or prediction is fitted or selected here.

Low/high caudate bins are supplied from the original predictor-only tertiles.
All, V=0 and V=1 summaries keep those same bins.  Resampling draws whole blocks
from the complete background, including blocks outside a selected subset;
the identical draw is used for every response and both low/high groups.
Frequency-weighted midranks exactly equal literal duplicated-site ranks.
Intervals are conditional on the fixed predictions and defined resamples.
Undefined replicates are counted, never replaced by zero.  Groups failing the
original pragmatic 20-site/5-route/3-block/200-visit support limits retain their
point descriptions but receive no interval.  This does not reopen G4's failed
eight-corner four-sign gate.
"""
from __future__ import annotations

import numpy as np
import pandas as pd


CANDIDATES = (
    "env_add", "env_all", "flex_add", "flex_all", "flex_prior_00", "flex_prior_11"
)
RESPONSES = ("observed_rate",) + CANDIDATES
MIN_SITES, MIN_ROUTES, MIN_BLOCKS, MIN_VISITS = 20, 5, 3, 200


def _weighted_spearman(x, y, weights):
    """Spearman for integer frequency weights, one row per resampling draw.

Ranks are recomputed after weighting, including ties.  Using ranks from the
original unweighted sample would not equal a cluster bootstrap.  A zero-size
sample or constant x/y produces NaN rather than a spurious zero correlation.
"""
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    weights = np.asarray(weights, dtype=float)
    if (x.ndim != 1 or y.shape != x.shape or weights.ndim != 2
            or weights.shape[1] != len(x)):
        raise ValueError("Weighted rank input dimensions do not agree")
    if (not np.isfinite(x).all() or not np.isfinite(y).all()
            or not np.isfinite(weights).all() or (weights < 0).any()
            or not np.equal(weights, np.floor(weights)).all()):
        raise ValueError("Weighted ranks require finite values and integer frequencies")
    result = np.full(weights.shape[0], np.nan)
    if not len(x):
        return result

    totals = weights.sum(axis=1)
    # For frequency ranks 1,...,N, the weighted mean is (N+1)/2 even with ties.
    center = (totals + 1.)[:, None] / 2.
    ranked = []
    for values in (x, y):
        order = np.argsort(values, kind="stable")
        sorted_values = values[order]
        starts = np.r_[0, np.flatnonzero(np.diff(sorted_values) != 0) + 1]
        ends = np.r_[starts[1:], len(values)]
        cumulative = np.column_stack((
            np.zeros(len(weights)), np.cumsum(weights[:, order], axis=1)
        ))
        # Cumulative frequencies immediately before/after each tied group.
        tie_ranks = (cumulative[:, starts] + cumulative[:, ends] + 1.) / 2.
        in_sorted_order = np.repeat(tie_ranks, ends - starts, axis=1)
        ranks = np.empty_like(in_sorted_order)
        ranks[:, order] = in_sorted_order
        ranked.append(ranks - center)

    a, b = ranked
    covariance = (weights * a * b).sum(axis=1)
    variance_x = (weights * a * a).sum(axis=1)
    variance_y = (weights * b * b).sum(axis=1)
    denominator = np.sqrt(variance_x * variance_y)
    valid = (totals >= 2) & (variance_x > 0) & (variance_y > 0)
    np.divide(covariance, denominator, out=result, where=valid)
    return np.clip(result, -1., 1.)


def _validate_frame(frame):
    required = {
        "background", "site", "route", "spatial_block", "V",
        "caudata_tertile", "odonata_suitability", "n_completed", *RESPONSES,
    }
    missing = required.difference(frame.columns)
    if missing:
        raise ValueError("Missing fixed-prediction source columns: " + ", ".join(sorted(missing)))
    if frame.empty:
        raise ValueError("The original source frame is empty")
    if frame.duplicated(["site", "background"]).any():
        raise ValueError("Source site/background rows must be unique")
    if frame[list(required)].isna().any().any():
        raise ValueError("Source identifiers, outcomes and predictions must be present")
    if not frame.V.isin([0, 1]).all() or not frame.caudata_tertile.isin([0, 1, 2]).all():
        raise ValueError("Original binary vegetation and fixed tertile identities are invalid")
    rates = frame[list(RESPONSES)].to_numpy(dtype=float)
    if not np.isfinite(rates).all() or ((rates < 0) | (rates > 1)).any():
        raise ValueError("Observed rates and fixed predictions must be finite probabilities")
    visits = frame.n_completed.to_numpy(dtype=float)
    if (not np.isfinite(visits).all() or (visits <= 0).any()
            or not np.equal(visits, np.floor(visits)).all()):
        raise ValueError("Completed source visits must be positive integers")
    if not np.isfinite(frame.odonata_suitability.to_numpy(dtype=float)).all():
        raise ValueError("Original odonate suitability must be finite")
    # A source station cannot move between route/block/V definitions by SDM choice.
    identity = frame.groupby("site")[["route", "spatial_block", "V", "n_completed", "observed_rate"]].nunique()
    if (identity > 1).any().any():
        raise ValueError("Same physical site has inconsistent observational identity across backgrounds")


def _counts(group, prefix):
    return {
        prefix + "_sites": int(len(group)),
        prefix + "_routes": int(group.route.nunique()),
        prefix + "_blocks": int(group.spatial_block.nunique()),
        prefix + "_visits": int(group.n_completed.sum()),
    }


def _supported(counts):
    return all(
        counts[prefix + "_sites"] >= MIN_SITES
        and counts[prefix + "_routes"] >= MIN_ROUTES
        and counts[prefix + "_blocks"] >= MIN_BLOCKS
        and counts[prefix + "_visits"] >= MIN_VISITS
        for prefix in ("low", "high")
    )


def _interval(values, enabled):
    finite = np.asarray(values, dtype=float)
    finite = finite[np.isfinite(finite)]
    if not enabled or len(finite) < 2:
        return np.nan, np.nan
    low, high = np.quantile(finite, [.025, .975])
    return float(low), float(high)


def summarize_rank_patterns(frame, bootstrap=999, seed=20261106):
    """Return all/V0/V1 × background × observed/six-predictor R1 diagnostics.

    Required inputs are one unique row per physical site and background:
    ``site, background, route, spatial_block, V, caudata_tertile,
    odonata_suitability, n_completed, observed_rate`` and the six column names
    in ``CANDIDATES``.  The supplied fixed tertiles are never re-estimated.

    ``supported`` is only the low/high marginal sample geometry, not evidence
    for a mechanism or permission to compute G4's full factorial sign claim.
    All prediction discrepancies use the same bootstrap draw as observed.
    Confidence intervals condition on fixed held-out fits and on nondegenerate
    draws; ``bootstrap_invalid`` and ``discrepancy_bootstrap_invalid`` make any
    excluded degeneracies visible.  Unsupported strata have NaN intervals.
    """
    _validate_frame(frame)
    if isinstance(bootstrap, bool) or int(bootstrap) != bootstrap or bootstrap < 2:
        raise ValueError("At least two integer block-bootstrap draws are required")
    bootstrap = int(bootstrap)
    rows = []
    for background in sorted(frame.background.unique()):
        original = frame[frame.background.eq(background)].copy()
        blocks = sorted(original.spatial_block.unique())
        draw = np.random.default_rng(seed).integers(
            0, len(blocks), size=(bootstrap, len(blocks))
        )
        multiplicity = np.zeros((bootstrap, len(blocks)), dtype=int)
        np.add.at(multiplicity, (np.arange(bootstrap)[:, None], draw), 1)
        block_index = {block: i for i, block in enumerate(blocks)}

        for subset, selected in (
            ("all", original),
            ("V0", original[original.V.eq(0)]),
            ("V1", original[original.V.eq(1)]),
        ):
            counts = {}
            correlations = []
            for label, tertile in (("low", 0), ("high", 2)):
                group = selected[selected.caudata_tertile.eq(tertile)]
                counts.update(_counts(group, label))
                group_blocks = group.spatial_block.map(block_index).to_numpy(dtype=int)
                weights = np.vstack((
                    np.ones((1, len(group))), multiplicity[:, group_blocks]
                ))
                x = group.odonata_suitability.to_numpy(dtype=float)
                correlations.append(np.column_stack([
                    _weighted_spearman(x, group[name].to_numpy(dtype=float), weights)
                    for name in RESPONSES
                ]))

            low, high = correlations
            contrast = high - low
            support = _supported(counts)
            for column, name in enumerate(RESPONSES):
                samples = contrast[1:, column]
                discrepancy = contrast[:, column] - contrast[:, 0]
                boot_discrepancy = discrepancy[1:]
                contrast_defined = bool(np.isfinite(contrast[0, column]))
                discrepancy_defined = bool(np.isfinite(discrepancy[0]))
                lower, upper = _interval(samples, support and contrast_defined)
                discrepancy_lower, discrepancy_upper = _interval(
                    boot_discrepancy, support and discrepancy_defined
                )
                rows.append(dict(
                    background=background, subset=subset, response=name,
                    **counts, supported=support, point_estimable=contrast_defined,
                    rho_low=float(low[0, column]), rho_high=float(high[0, column]),
                    contrast_high_minus_low=float(contrast[0, column]),
                    contrast_ci_low=lower, contrast_ci_high=upper,
                    predicted_minus_observed=float(discrepancy[0]),
                    discrepancy_ci_low=discrepancy_lower,
                    discrepancy_ci_high=discrepancy_upper,
                    source_blocks=len(blocks), bootstrap_repetitions=bootstrap,
                    bootstrap_seed=int(seed),
                    bootstrap_valid=int(np.isfinite(samples).sum()),
                    bootstrap_invalid=int((~np.isfinite(samples)).sum()),
                    discrepancy_bootstrap_valid=int(np.isfinite(boot_discrepancy).sum()),
                    discrepancy_bootstrap_invalid=int((~np.isfinite(boot_discrepancy)).sum()),
                ))
    result = pd.DataFrame(rows)
    result.attrs["interpretation"] = (
        "Retrospective fixed-prediction descriptive rank calibration; no refitting, "
        "independent replication, calibrated predictive distribution or causal validation."
    )
    return result
