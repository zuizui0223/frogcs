#!/usr/bin/env python3
"""v6.6 source-free counterexample: acoustic lag proxies unmodeled slow water.

Original data: NONE. Synthetic planned mechanism:
V6_6_OMITTED_SLOW_HYDROLOGY_SPURIOUS_ACOUSTIC_MEMORY_CONTRACT.md.
"""
from __future__ import annotations

import json
from statistics import median
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss

N_WETLANDS = 180
N_EPISODES = 24
SEEDS = (20261011, 20261012, 20261013, 20261014, 20261015)

def assert_prior_feature(source_episode: int, target_episode: int, training_end: int) -> None:
    if not (source_episode < target_episode and
            (target_episode <= training_end or source_episode <= training_end)):
        raise ValueError("HELDOUT_OR_FUTURE_ACOUSTIC_LEAK")

def generate(seed: int, direct_acoustic: float):
    rng = np.random.default_rng(seed)
    site = rng.normal(0, 0.65, N_WETLANDS)
    depth = np.empty((N_EPISODES, N_WETLANDS))
    depth[0] = rng.normal(0, 1, N_WETLANDS)
    for t in range(1, N_EPISODES):
        depth[t] = 0.84 * depth[t-1] + rng.normal(0, 0.62, N_WETLANDS)
    phase = np.zeros_like(depth)
    phase[1:] = np.sign(depth[1:] - depth[:-1])
    slow = np.empty_like(depth)
    slow[0] = depth[0]
    for t in range(1, N_EPISODES):
        slow[t] = 0.84 * slow[t-1] + 0.16 * depth[t]
    diel = rng.normal(0, 1, (N_EPISODES, N_WETLANDS))
    calls = np.zeros_like(depth)
    for t in range(N_EPISODES):
        old = calls[t-1] if t else np.full(N_WETLANDS, 0.5)
        logit = (-0.5 + site + 0.35 * depth[t] +
                 2.5 * slow[t] + 0.25 * diel[t] +
                 direct_acoustic * (old - 0.5))
        prob = 1 / (1 + np.exp(-np.clip(logit, -35, 35)))
        calls[t] = (rng.random(N_WETLANDS) < prob).astype(float)
    return depth, phase, slow, diel, calls

def matrix(depth, phase, slow, diel, calls, times, add_slow, add_lag,
           seed=0, placebo=False):
    n = depth.shape[1]
    inputs = [
        depth[times].reshape(-1, 1),
        phase[times].reshape(-1, 1),
        diel[times].reshape(-1, 1),
    ]
    if add_slow:
        inputs.append(slow[times].reshape(-1, 1))
    if add_lag:
        past = []
        for t in times:
            assert_prior_feature(int(t)-1, int(t), N_EPISODES-2)
            if t == 0:
                raise ValueError("NO_FINISHED_PREVIOUS_EPISODE")
            vec = calls[t-1].copy()
            if placebo:
                rng=np.random.default_rng(seed*1000 + int(t))
                vec=vec[rng.permutation(n)]
            past.append(vec)
        inputs.append(np.stack(past).reshape(-1, 1))
    # Wetland-specific stable propensity estimated in train only.
    inputs.append(np.tile(np.eye(n), (len(times), 1)))
    return np.hstack(inputs)

def run_one(seed: int, direct_acoustic: float):
    depth,phase,slow,diel,calls=generate(seed,direct_acoustic)
    train = np.arange(1, N_EPISODES-1)
    test = np.array([N_EPISODES-1])
    assert_prior_feature(N_EPISODES-2,N_EPISODES-1,N_EPISODES-2)
    y_train = calls[train].ravel()
    y_test = calls[test].ravel()
    output = {}
    specs = {
        "SHORT_HYDRO": (False, False, False),
        "SHORT_PLUS_CALL_LAG": (False, True, False),
        "FULL_SLOW_WATER": (True, False, False),
        "FULL_PLUS_CALL_LAG": (True, True, False),
        "FULL_PLUS_WRONG_WETLAND_LAG": (True, True, True),
    }
    for name,(slow_flag,lag,placebo) in specs.items():
        X_train=matrix(depth,phase,slow,diel,calls,train,slow_flag,lag,seed,placebo)
        X_test=matrix(depth,phase,slow,diel,calls,test,slow_flag,lag,seed,placebo)
        clf=LogisticRegression(C=2, max_iter=350, solver="lbfgs")
        clf.fit(X_train,y_train)
        pred=clf.predict_proba(X_test)[:,1]
        output[name]=-float(log_loss(y_test,pred,labels=[0,1]))
    return {
        "naive_lag_gain":output["SHORT_PLUS_CALL_LAG"]-output["SHORT_HYDRO"],
        "adjusted_lag_gain":output["FULL_PLUS_CALL_LAG"]-output["FULL_SLOW_WATER"],
        "measured_slow_water_gain":output["FULL_SLOW_WATER"]-output["SHORT_HYDRO"],
        "wrong_wetland_placebo_gain":output["FULL_PLUS_WRONG_WETLAND_LAG"]-output["FULL_SLOW_WATER"],
    }

def tests():
    for bad in [(N_EPISODES-1,N_EPISODES-1,N_EPISODES-2),
                (N_EPISODES,N_EPISODES-1,N_EPISODES-2)]:
        try:assert_prior_feature(*bad)
        except ValueError:pass
        else:raise AssertionError("future/heldout call history accepted")
    cases={
        "H0_SLOW_WATER_ONLY_NO_DIRECT_ACOUSTIC_MEMORY":0.0,
        "H1_SLOW_WATER_PLUS_TRUE_DIRECT_CARRYOVER":2.0,
    }
    results={}
    for name,acoustic_coefficient in cases.items():
        runs=[run_one(seed,acoustic_coefficient) for seed in SEEDS]
        results[name]={k:round(float(median(v[k] for v in runs)),6)
                       for k in runs[0]}
        results[name]["per_seed_naive_lag_gains"]=[
            round(float(v["naive_lag_gain"]),6) for v in runs]
        results[name]["per_seed_adjusted_lag_gains"]=[
            round(float(v["adjusted_lag_gain"]),6) for v in runs]
    # Do not hardcode a preferred sign of a synthetic numerical contrast:
    # negative/noisy results are valid design diagnostic outcomes.
    assert all(np.isfinite(v) for x in results.values()
               for k,v in x.items() if not isinstance(v,list))
    payload={
        "status":"SYNTHETIC_OMITTED_HYDROLOGY_DIAGNOSTIC_EXECUTED",
        "synthetic_wetlands":N_WETLANDS,
        "synthetic_episodes":N_EPISODES,
        "five_fixed_seeds":list(SEEDS),
        "artificial_slow_water_causally_defined_by_past_current_depth_only":True,
        "H0_has_zero_direct_acoustic_lag_by_construction":True,
        "heldout_call_outcomes_as_predictors":False,
        "two_artificial_worlds_median_paired_heldout_neglogloss_gains":results,
        "new_real_frog_evidence":False,
        "jae_RC6_changed":False,
    }
    print(json.dumps(payload,sort_keys=True))
    print("PASS: synthetic counterexample execution; interpretation depends on logged directions")

if __name__=="__main__":
    tests()
