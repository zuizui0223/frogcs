#!/usr/bin/env python3
"""Exact-k conditional acoustic-site placement kernel (method only).

No field observations, source URLs, or NAAMP outcomes are loaded here.
q is a previously frozen baseline site probability (including site history).
New history coefficients are therefore ADDITIONAL residual effects beyond q.

The forest connection matrix must represent mapped forest-patch connections,
not geometric proximity or overlap of buffers. Users must supply it externally.

The frozen q for CI>=1 must NOT be reused with observed CI>=2/CI=3:
the q_response_state and response_state are required to match exactly.
"""
from __future__ import annotations
from functools import lru_cache
from itertools import combinations
import math

import numpy as np
from scipy.optimize import minimize
from scipy.special import logsumexp

N_STOPS = 10
FEATURE_NAMES = ("extra_history", "soil_by_history", "forest_cover",
                 "terrestrial_guild_by_forest", "connected_forest_pairs")
RIDGE_PENALTY = 1.0  # development default; freeze separately for real outcomes

@lru_cache(maxsize=20)
def choices_for_k(k):
    if not 1 <= k < N_STOPS:
        raise ValueError("informative conditional events require 1 <= k <= 9")
    return np.asarray(list(combinations(range(N_STOPS), k)), dtype=int)

def verified(event):
    """Validate a single externally prepared acoustic event.

    The fixed observation vector must have length ten; empty/full events are
    valid source records but have no conditional placement information.
    """
    needed = {"q", "observed", "history", "forest", "connection",
              "soil_change_z", "guild", "response_state",
              "q_response_state", "connection_source"}
    missing = needed - set(event)
    if missing:
        raise ValueError(f"missing required event fields: {sorted(missing)}")
    states = {"CI_ge_1", "CI_ge_2", "CI_eq_3"}
    if event["response_state"] not in states or event["q_response_state"] != event["response_state"]:
        raise ValueError("q probabilities and observed acoustic threshold must match")
    if event["connection_source"] not in ("synthetic", "official_nlcd_forest_patch"):
        raise ValueError("forest connections require independently classified patch data")
    q = np.asarray(event["q"], float)
    y = np.asarray(event["observed"], float)
    h = np.asarray(event["history"], float)
    forest = np.asarray(event["forest"], float)
    c = np.asarray(event["connection"], float)
    if any(x.shape != (N_STOPS,) for x in (q, y, h, forest)):
        raise ValueError("ten physical stop positions are mandatory")
    if c.shape != (N_STOPS, N_STOPS):
        raise ValueError("forest-connection matrix must be 10x10")
    if not (np.isfinite(q).all() and np.isfinite(y).all() and
            np.isfinite(h).all() and np.isfinite(forest).all() and
            np.isfinite(c).all()):
        raise ValueError("nonfinite input")
    if not np.all((q > 0) & (q < 1)):
        raise ValueError("q must be strictly in (0,1), and must not be refitted")
    if not np.all((y == 0) | (y == 1)):
        raise ValueError("observed must be binary")
    if not np.all((h == 0) | (h == 1)):
        raise ValueError("history must be binary")
    if not np.all((forest >= 0) & (forest <= 1)):
        raise ValueError("forest fractions outside [0,1]")
    if not np.all((c >= 0) & (c <= 1)) or not np.allclose(c, c.T, atol=1e-12):
        raise ValueError("forest connection must be symmetric in [0,1]")
    if not np.allclose(np.diag(c), 0.0, atol=1e-12):
        raise ValueError("forest connection diagonal must be zero")
    soil = float(event["soil_change_z"])
    guild = float(event["guild"])
    if not math.isfinite(soil) or guild not in (0.0, 1.0):
        raise ValueError("soil must be finite and guild must be response-blind binary")
    return q, y, h, forest, c, soil, guild

def event_design(event):
    """All exact-k candidate configurations and their frozen-q offsets.

    Event-constant route-scale soil moisture does not enter the likelihood
    as a main effect: at exactly k selected sites its term cancels.
    """
    q, y, h, forest, c, soil, guild = verified(event)
    k = int(np.sum(y))
    if k in (0, N_STOPS):
        raise ValueError("k=0/10 contains no conditional placement information")
    choices = choices_for_k(k)
    log_odds = np.log(q) - np.log1p(-q)
    offset = log_odds[choices].sum(axis=1)
    history_sum = h[choices].sum(axis=1)
    forest_sum = forest[choices].sum(axis=1)
    linked_pairs = np.zeros(len(choices), float)
    for a in range(k):
        for b in range(a + 1, k):
            linked_pairs += c[choices[:, a], choices[:, b]]
    X = np.column_stack([history_sum, soil * history_sum, forest_sum,
                         guild * forest_sum, linked_pairs])
    selected = tuple(np.flatnonzero(y).tolist())
    matches = np.flatnonzero(np.all(choices == selected, axis=1))
    if len(matches) != 1:
        raise ValueError("observed site combination not among exact-k configurations")
    return offset, X, int(matches[0])

def event_pmf(event, beta):
    """Enumerate the exact-k subset distribution (at most C(10,5)=252)."""
    beta = np.asarray(beta, float)
    if beta.shape != (len(FEATURE_NAMES),) or not np.isfinite(beta).all():
        raise ValueError("beta must be five finite coefficients")
    offset, X, selected = event_design(event)
    score = offset + X @ beta
    probs = np.exp(score - logsumexp(score))
    return choices_for_k(int(np.sum(event["observed"]))), probs, selected

def event_logprob(event, beta):
    beta = np.asarray(beta, float)
    if beta.shape != (len(FEATURE_NAMES),) or not np.isfinite(beta).all():
        raise ValueError("invalid coefficient vector")
    offset, X, observed_index = event_design(event)
    score = offset + X @ beta
    return float(score[observed_index] - logsumexp(score))

def rank_of_features(events, active_features):
    indices = [FEATURE_NAMES.index(name) for name in active_features]
    # A feature constant across exact-k choices has zero within-event rank.
    X = []
    for event in events:
        _, x, _ = event_design(event)
        X.append(x[:, indices] - x[:, indices].mean(axis=0, keepdims=True))
    return int(np.linalg.matrix_rank(np.vstack(X))) if X else 0

def fit_train_only(events, active_features, ridge=RIDGE_PENALTY):
    """Fit conditional placement on training events only; do NOT feed heldout.

    The caller is responsible for route/time blocking and prior q training.
    For inference use route-block resampling or a preregistered block method.
    """
    active_features = tuple(active_features)
    if not active_features or len(set(active_features)) != len(active_features):
        raise ValueError("active_features must be unique and nonempty")
    indices = [FEATURE_NAMES.index(name) for name in active_features]
    if ridge < 0 or not math.isfinite(ridge):
        raise ValueError("invalid ridge penalty")
    designs = [event_design(event) for event in events]
    if not designs:
        raise ValueError("no informative training events")
    rank = rank_of_features(events, active_features)
    if rank < len(indices):
        raise ValueError(f"unidentifiable exact-k features: rank={rank}/{len(indices)}")
    # Normalized per training event to avoid scale with training-set size.
    def loss_grad(x):
        objective = 0.5 * ridge * float(np.sum(x * x))
        gradient = ridge * x
        for offset, Xall, yi in designs:
            xmat = Xall[:, indices]
            logw = offset + xmat @ x
            ps = np.exp(logw - logsumexp(logw))
            objective += float(logsumexp(logw) - logw[yi]) / len(designs)
            gradient += (ps @ xmat - xmat[yi]) / len(designs)
        return objective, gradient
    fit = minimize(loss_grad, np.zeros(len(indices)), jac=True,
                   method="L-BFGS-B", options={"maxiter": 300, "ftol": 1e-12})
    if not fit.success or not np.isfinite(fit.x).all():
        raise RuntimeError("exact-k conditional model did not converge")
    beta = np.zeros(len(FEATURE_NAMES), float)
    beta[indices] = fit.x
    return {"beta": beta, "rank": rank, "n_training_events": len(designs),
            "active_features": active_features,
            "train_neg_loglik_per_event": sum(
                -event_logprob(e, beta) for e in events) / len(events)}

def heldout_comparison(events, trained_beta):
    """Score untouched events against fixed-q (beta=0), without any refit."""
    n = len(events)
    if not n:
        raise ValueError("no heldout events")
    base = np.zeros(len(FEATURE_NAMES), float)
    improvements = [event_logprob(e, trained_beta) - event_logprob(e, base)
                    for e in events]
    return {"n_heldout_events": n,
            "mean_logscore_gain_per_event": float(np.mean(improvements)),
            "mean_baseline_neg_loglik": -float(np.mean(
                [event_logprob(e, base) for e in events])),
            "mean_model_neg_loglik": -float(np.mean(
                [event_logprob(e, trained_beta) for e in events])),
            "independent_confirmation": False}  # external provenance is caller's job
