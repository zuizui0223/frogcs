#!/usr/bin/env python3
"""v6.5 SYNTHETIC mechanism-falsification QA; NO real frog/wetland records.

Mechanism and pass criteria frozen in
V6_5_SYNTHETIC_HYDROLOGY_ACOUSTIC_MEMORY_FALSE_POSITIVE_CONTRACT.md.
Includes a placebo shuffled *past* calling outcome; tests false positive behavior.
"""
from __future__ import annotations
import json
import statistics

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss

N_WETLANDS = 180            # wholly invented labels
N_EPISODES = 19             # invented chronological wetting episodes
SEEDS = (20261011, 20261012, 20261013, 20261014, 20261015)
REGIMES = {
    "S0_NO_PATH_NO_CARRYOVER": (0.0, 0.0),
    "S1_HYDROLOGY_ONLY": (1.1, 0.0),
    "S2_ACOUSTIC_CARRYOVER_ONLY": (0.0, 2.5),
    "S3_BOTH": (1.1, 2.5),
}

def assert_time_boundary(history_episode, latest_training_episode, prediction_episode):
    """A feature must not read the prediction event or any evaluation-year labels."""
    if not (history_episode <= latest_training_episode < prediction_episode):
        raise ValueError("EVALUATION_OR_FUTURE_EPISODE_LEAKAGE")

def artificial_series(seed, hydro_coefficient, carry_coefficient):
    r = np.random.default_rng(seed)
    site_propensity = r.normal(0.0, 0.65, N_WETLANDS)
    depth = np.empty((N_EPISODES, N_WETLANDS))
    depth[0] = r.normal(0.0, 1.0, N_WETLANDS)
    for t in range(1, N_EPISODES):
        depth[t] = 0.6 * depth[t-1] + r.normal(0.0, 0.8, N_WETLANDS)
    # Hydrological phase follows *actual artificial depth increments*.
    phase = np.zeros_like(depth)
    phase[1:] = np.sign(depth[1:] - depth[:-1])
    diel = r.normal(0.0, 1.0, (N_EPISODES, N_WETLANDS))
    calling = np.zeros_like(depth)
    for t in range(N_EPISODES):
        previous = calling[t-1] if t else np.full(N_WETLANDS, 0.5)
        eta = (-0.35 + site_propensity + 0.8 * depth[t] + 0.35 * diel[t]
               + hydro_coefficient * phase[t]
               + carry_coefficient * (previous - 0.5))
        p = 1.0 / (1.0 + np.exp(-eta))
        calling[t] = (r.random(N_WETLANDS) < p).astype(float)
    return depth, phase, diel, calling

def model_features(depth, phase, diel, calling, time_indices, kind, seed, placebo=False):
    n = depth.shape[1]
    assert n == N_WETLANDS
    block = [
        depth[time_indices].reshape(-1, 1),
        diel[time_indices].reshape(-1, 1),
    ]
    if kind >= 1:
        block.append(phase[time_indices].reshape(-1, 1))
    if kind >= 2:
        previous = np.empty((len(time_indices), n))
        for row, t in enumerate(time_indices):
            assert_time_boundary(t-1, N_EPISODES-2, N_EPISODES-1) if t == N_EPISODES-1 else None
            if t <= 0:
                raise ValueError("NO_COMPLETED_PRIOR_ACOUSTIC_EPISODE")
            # No calling[t] in feature vector. Only previous completed episode.
            prev = calling[t-1].copy()
            if placebo:
                # Shuffle observed PREVIOUS-episode labels among artificial wetlands,
                # preserving a real-like prevalence but removing identity-specific lag.
                perm = np.random.default_rng(seed * 1000 + int(t)).permutation(n)
                prev = prev[perm]
            previous[row] = prev
        block.append(previous.reshape(-1, 1))
    # Explicit fixed wetland propensity. Fit the coefficients on training only.
    block.append(np.tile(np.eye(n), (len(time_indices), 1)))
    return np.hstack(block)

def simulated_heldout_scores(seed, hydro_coefficient, carry_coefficient):
    depth, phase, diel, call = artificial_series(seed, hydro_coefficient, carry_coefficient)
    train_times = np.arange(1, N_EPISODES-1)
    test_times = np.array([N_EPISODES-1])
    # Only final event is evaluated; immediately previous event is TRAINING.
    assert_time_boundary(N_EPISODES-2, N_EPISODES-2, N_EPISODES-1)
    train_outcome = call[train_times].reshape(-1)
    test_outcome = call[test_times].reshape(-1)
    scores = []
    for candidate in ("M0", "M1", "M2", "M2_PLACEBO"):
        kind = {"M0": 0, "M1": 1, "M2": 2, "M2_PLACEBO": 2}[candidate]
        placebo = candidate == "M2_PLACEBO"
        X_train = model_features(depth, phase, diel, call, train_times, kind, seed, placebo)
        X_test = model_features(depth, phase, diel, call, test_times, kind, seed, placebo)
        model = LogisticRegression(C=2.0, max_iter=250, tol=1e-4,
                                   solver="lbfgs")
        model.fit(X_train, train_outcome)
        prediction = model.predict_proba(X_test)[:, 1]
        # Signed NEGATIVE log-loss: larger = better, on identical wetland targets.
        scores.append(-float(log_loss(test_outcome, prediction, labels=[0, 1])))
    return {
        "hydrological_path_gain_M1_minus_M0": scores[1] - scores[0],
        "acoustic_carryover_gain_M2_minus_M1": scores[2] - scores[1],
        "cross_wetland_history_placebo_gain": scores[3] - scores[1],
        "true_minus_placebo_M2_gain": scores[2] - scores[3],
    }

def check_scenarios():
    report = {}
    for label, (water_effect, memory_effect) in REGIMES.items():
        draws = [simulated_heldout_scores(seed, water_effect, memory_effect)
                 for seed in SEEDS]
        medians = {
            name: round(statistics.median([x[name] for x in draws]), 6)
            for name in draws[0]
        }
        report[label] = medians

    null = report["S0_NO_PATH_NO_CARRYOVER"]
    hydro = report["S1_HYDROLOGY_ONLY"]
    memory = report["S2_ACOUSTIC_CARRYOVER_ONLY"]
    both = report["S3_BOTH"]
    p = "hydrological_path_gain_M1_minus_M0"
    h = "acoustic_carryover_gain_M2_minus_M1"
    placebo = "cross_wetland_history_placebo_gain"
    if not (abs(null[p]) < 0.02 and abs(null[h]) < 0.02
            and hydro[p] > 0.04 and abs(hydro[h]) < 0.02
            and memory[h] > 0.04 and abs(memory[placebo]) < 0.02
            and both[p] > 0.0 and both[h] > 0.03
            and abs(both[placebo]) < 0.02):
        raise AssertionError("SYNTHETIC_MECHANISM_DISCRIMINATION_FAILED")

    try:
        assert_time_boundary(N_EPISODES-1, N_EPISODES-2, N_EPISODES-1)
    except ValueError as exc:
        assert str(exc) == "EVALUATION_OR_FUTURE_EPISODE_LEAKAGE"
    else:
        raise AssertionError("EVALUATION_YEAR_LABEL_ACCEPTED_AS_HISTORY")

    receipt = {
        "status": "SYNTHETIC_MECHANISM_QA_PASSED",
        "only_artificial_source_generated_outcomes": True,
        "five_fixed_seeds": list(SEEDS),
        "invented_wetlands": N_WETLANDS,
        "invented_episodes": N_EPISODES,
        "number_of_heldout_episodes_per_wetland": 1,
        "site_propensity_estimated_from_training_only": True,
        "evaluation_year_labels_in_predictors": False,
        "scoring": "paired held-out negative-log-loss",
        "scenario_median_gains_QA_ONLY": report,
        "independent_external_frog_replication_obtained": False,
        "biological_hysteresis_or_memory_demonstrated": False,
        "jae_RC6_changed": False,
    }
    print(json.dumps(receipt, sort_keys=True))
    print("PASS: null stays null, water-only path recovered, true lag recovered, placebo history fails")

if __name__ == "__main__":
    check_scenarios()
