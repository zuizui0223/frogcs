#!/usr/bin/env python3
"""v6.8 synthetic shared-depth-logger error — never real frog observations.

Pre-frozen source-free contract:
V6_8_COMMON_MODE_DEPTH_LOGGER_ERROR_COUNTEREXAMPLE_CONTRACT.md
"""
from __future__ import annotations

import json
from statistics import median
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss

from test_omitted_slow_hydrology_acoustic_lag_v66 import (
    N_WETLANDS, N_EPISODES, SEEDS, generate,
)
from test_noisy_hydro_logger_spurious_acoustic_history_v67 import (
    SIGMA, features,
)

REGIMES = (
    "ORACLE",
    "ONE_INDEPENDENT_NOISY",
    "FOUR_INDEPENDENT",
    "FOUR_CORRELATED_RHO_0_75",
    "FOUR_FULLY_SHARED_RHO_1",
)

def artificial_sensor_array(depth, seed, rho):
    """Four simultaneous errors, same marginal SD; no source logger readings."""
    if rho not in (0.0, 0.75, 1.0):
        raise ValueError("UNDECLARED_SENSOR_CORRELATION")
    rng = np.random.default_rng(seed + 80_000_000)
    ntime, nwet = depth.shape
    common = rng.normal(0, 1, (ntime, nwet))
    independent = rng.normal(0, 1, (4, ntime, nwet))
    errors = SIGMA * (
        np.sqrt(rho) * common[None, :, :] +
        np.sqrt(1.0-rho) * independent
    )
    return depth[None, :, :] + errors

def source_free_measured_history(depth, seed, regime):
    if regime not in REGIMES:
        raise ValueError("UNDECLARED_SENSOR_REGIME")
    if regime == "ORACLE":
        observed = depth.copy()
    elif regime == "ONE_INDEPENDENT_NOISY":
        observed = artificial_sensor_array(depth,seed,0.0)[0]
    else:
        rho = {"FOUR_INDEPENDENT":0.0,
               "FOUR_CORRELATED_RHO_0_75":0.75,
               "FOUR_FULLY_SHARED_RHO_1":1.0}[regime]
        observed = artificial_sensor_array(depth,seed,rho).mean(axis=0)
    phase = np.zeros_like(depth)
    phase[1:] = np.sign(observed[1:]-observed[:-1])
    slow = np.empty_like(depth)
    slow[0] = observed[0]
    for t in range(1,N_EPISODES):
        slow[t] = 0.84*slow[t-1]+0.16*observed[t]
    missing = np.zeros_like(depth)
    age = np.zeros_like(depth)
    return observed,phase,slow,missing,age

def evaluate(seed, depth, diel, calls, regime):
    observed,phase,slow,missing,age = source_free_measured_history(
        depth,seed,regime
    )
    train = np.arange(1,N_EPISODES-1)
    test = np.array([N_EPISODES-1])
    y_train = calls[train].reshape(-1)
    y_test = calls[test].reshape(-1)
    scores = {}
    for label,lag,placebo in (
        ("B",False,False),
        ("B_PLUS_PAST",True,False),
        ("B_PLUS_SHUFFLED_PAST",True,True),
    ):
        x_train=features(observed,phase,slow,diel,missing,age,calls,
                         train,lag,seed,placebo)
        x_test=features(observed,phase,slow,diel,missing,age,calls,
                        test,lag,seed,placebo)
        clf=LogisticRegression(C=2.0,max_iter=350,solver="lbfgs")
        clf.fit(x_train,y_train)
        scores[label]=-float(log_loss(y_test,
            clf.predict_proba(x_test)[:,1],labels=[0,1]))
    return {
        "lag_gain":scores["B_PLUS_PAST"]-scores["B"],
        "placebo_gain":scores["B_PLUS_SHUFFLED_PAST"]-scores["B"],
    }

def test():
    toy = np.zeros((N_EPISODES,N_WETLANDS),dtype=float)
    oracle=source_free_measured_history(toy,SEEDS[0],"ORACLE")[0]
    assert np.array_equal(oracle,toy)
    fully_shared=artificial_sensor_array(toy,SEEDS[0],1.0)
    assert all(np.array_equal(fully_shared[0],fully_shared[i])
               for i in range(1,4))
    independent=artificial_sensor_array(toy,SEEDS[0],0.0)
    assert not np.array_equal(independent[0],independent[1])
    assert np.array_equal(
        source_free_measured_history(toy,SEEDS[0],"FOUR_INDEPENDENT")[0],
        independent.mean(axis=0))
    try:
        artificial_sensor_array(toy,SEEDS[0],0.74)
    except ValueError as e:
        assert str(e)=="UNDECLARED_SENSOR_CORRELATION"
    else:
        raise AssertionError("UNFROZEN_CORRELATION_ACCEPTED")
    outcomes={regime:[] for regime in REGIMES}
    for seed in SEEDS:
        # The exact v6.6 zero-direct-lag generator: do not refit or alter truth.
        depth,_,_,diel,calls=generate(seed,0.0)
        for regime in REGIMES:
            outcomes[regime].append(evaluate(seed,depth,diel,calls,regime))
    summary={}
    for key,entries in outcomes.items():
        lags=[float(x["lag_gain"]) for x in entries]
        controls=[float(x["placebo_gain"]) for x in entries]
        summary[key]={
            "lag_gain_median":round(median(lags),6),
            "lag_gains_each_seed":[round(z,6) for z in lags],
            "positive_seeds":sum(x>0 for x in lags),
            "wrong_wetland_placebo_gain_median":round(median(controls),6),
        }
    report={
        "status":"SYNTHETIC_COMMON_MODE_LOGGER_DIAGNOSTIC_EXECUTED",
        "generator_direct_acoustic_lag":0.0,
        "invented_wetlands":N_WETLANDS,
        "invented_episodes":N_EPISODES,
        "seeds":list(SEEDS),
        "simulated_logger_error_sd_in_invented_depth_units":SIGMA,
        "rho_scenarios":[0.0,0.75,1.0],
        "all_water_and_acoustic_rows_are_generated":True,
        "all_model_evaluations_use_same_heldout_final_episode":True,
        "measured_outcome_original_frogs":False,
        "real_logger_error_or_deployment_estimated":False,
        "submitted_jae_rc6_modified":False,
        "regime_results":summary,
    }
    print(json.dumps(report,sort_keys=True))
    print("PASS: frozen common error and independence scenarios executed on fully synthetic calls")

if __name__=="__main__":
    test()
