#!/usr/bin/env python3
"""v6.7 SYNTHETIC ONLY: logger noise and missing depth can fake chorus-memory gain.

Read frozen V6_7_SENSOR_MEASUREMENT_ERROR_FALSE_ACOUSTIC_MEMORY_CONTRACT.md.
No original frog, recorder, coordinate, depth or biological outcome data.
"""
from __future__ import annotations

import json
from statistics import median
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss

from test_omitted_slow_hydrology_acoustic_lag_v66 import (
    N_WETLANDS, N_EPISODES, SEEDS, generate, assert_prior_feature,
)

SIGMA = 1.10                 # invented error, NOT instrument calibration
GAP_PROBABILITY = 0.25       # artificial MCAR gap rate, NOT source missingness
REGIMES = ("ORACLE_UNOBSERVABLE", "ONE_NOISY_LOGGER",
           "FOUR_LOGGERS_MEAN", "ONE_NOISY_LOGGER_WITH_GAPS")

def measured_water(depth, seed, regime):
    """Observe synthetic truth through an artificial instrument; never forward-fill."""
    if regime not in REGIMES:
        raise ValueError("UNKNOWN_ARTIFICIAL_SENSOR_REGIME")
    ntime,nwet=depth.shape
    rng=np.random.default_rng(seed+70_000_000)
    # Shared sensor #1 ensures paired comparison with the four-sensor mean.
    errors=rng.normal(0,SIGMA,(4,ntime,nwet))
    gap = rng.random((ntime,nwet)) < GAP_PROBABILITY
    if regime == "ORACLE_UNOBSERVABLE":
        raw = depth.copy()
        missing = np.zeros_like(depth,dtype=bool)
    elif regime == "FOUR_LOGGERS_MEAN":
        raw = depth+errors.mean(axis=0)
        missing = np.zeros_like(depth,dtype=bool)
    elif regime == "ONE_NOISY_LOGGER":
        raw = depth+errors[0]
        missing = np.zeros_like(depth,dtype=bool)
    else:
        raw = depth+errors[0]
        missing = gap
    observed=np.empty_like(depth)
    age=np.zeros_like(depth)
    for w in range(nwet):
        last=0.0          # fixed calibration-zero placeholder, never future data
        since=0
        for t in range(ntime):
            if missing[t,w]:
                since+=1
            else:
                last=raw[t,w]
                since=0
            observed[t,w]=last
            age[t,w]=since
    phase=np.zeros_like(depth)
    # Deliberately illustrates naive phase from a forward-carried depth signal.
    phase[1:]=np.sign(observed[1:]-observed[:-1])
    slow=np.empty_like(depth)
    slow[0]=observed[0]
    for t in range(1,ntime):
        slow[t]=0.84*slow[t-1]+0.16*observed[t]
    return observed,phase,slow,missing.astype(float),age

def features(observed,phase,slow,diel,missing,age,calls,times,
             include_lag,seed,placebo=False):
    n=observed.shape[1]
    if n != N_WETLANDS:
        raise ValueError("UNEXPECTED_SYNTHETIC_WETLAND_COUNT")
    cols=[observed[times].reshape(-1,1),phase[times].reshape(-1,1),
          slow[times].reshape(-1,1),diel[times].reshape(-1,1),
          missing[times].reshape(-1,1),age[times].reshape(-1,1)]
    if include_lag:
        historical=[]
        for t in times:
            t=int(t)
            if t<=0:
                raise ValueError("NO_PRIOR_COMPLETED_EPISODE")
            assert_prior_feature(t-1,t,N_EPISODES-2)
            v=calls[t-1].copy()         # neither calls[t] nor future call labels
            if placebo:
                v=v[np.random.default_rng(seed*1000+t).permutation(n)]
            historical.append(v)
        cols.append(np.stack(historical).reshape(-1,1))
    # Fit physical-wetland propensity strictly on training labels.
    cols.append(np.tile(np.eye(n),(len(times),1)))
    return np.hstack(cols)

def evaluate(seed,truth,regime):
    depth,diel,calls=truth
    observed,phase,slow,missing,age=measured_water(depth,seed,regime)
    train=np.arange(1,N_EPISODES-1)
    test=np.array([N_EPISODES-1])
    y_train=calls[train].ravel()
    y_test=calls[test].ravel()
    scores={}
    for model_name,lag,placebo in (
        ("BASELINE_HYDRO",False,False),
        ("HYDRO_PLUS_CORRECT_LAG",True,False),
        ("HYDRO_PLUS_WRONG_WETLAND_LAG",True,True),
    ):
        Xtrain=features(observed,phase,slow,diel,missing,age,calls,
                        train,lag,seed,placebo)
        Xtest=features(observed,phase,slow,diel,missing,age,calls,
                       test,lag,seed,placebo)
        estimator=LogisticRegression(C=2.0,max_iter=350,solver="lbfgs")
        estimator.fit(Xtrain,y_train)
        prediction=estimator.predict_proba(Xtest)[:,1]
        scores[model_name]=-float(log_loss(y_test,prediction,labels=[0,1]))
    return {
        "true_lag_gain_when_direct_effect_zero":
            scores["HYDRO_PLUS_CORRECT_LAG"]-scores["BASELINE_HYDRO"],
        "wrong_wetland_lag_placebo_gain":
            scores["HYDRO_PLUS_WRONG_WETLAND_LAG"]-scores["BASELINE_HYDRO"],
        "synthetic_missing_depth_fraction":float(np.mean(missing)),
        "heldout_synthetic_depth_missing_fraction":float(np.mean(missing[test])),
    }

def tests():
    try:
        assert_prior_feature(N_EPISODES-1,N_EPISODES-1,N_EPISODES-2)
    except ValueError as ex:
        assert str(ex)=="HELDOUT_OR_FUTURE_ACOUSTIC_LEAK"
    else:
        raise AssertionError("HELDOUT_LABEL_ALLOWED_AS_HISTORICAL_PREDICTOR")
    toy=np.array([[0.,2.],[1.,3.],[2.,4.]],dtype=float)
    # The oracle observation must exactly recover depth+phase+known EMA.
    o,p,s,mask,age=measured_water(toy,SEEDS[0],"ORACLE_UNOBSERVABLE")
    assert np.array_equal(o,toy) and np.all(mask==0) and np.all(age==0)
    assert np.array_equal(p[1:],np.ones((2,2)))
    try:measured_water(toy,SEEDS[0],"UNDEFINED")
    except ValueError as ex:assert str(ex)=="UNKNOWN_ARTIFICIAL_SENSOR_REGIME"
    else:raise AssertionError("UNDECLARED_SOURCE_SENSOR_SCENARIO_ACCEPTED")

    rows={r:[] for r in REGIMES}
    for seed in SEEDS:
        # Use the actual locked v6.6 synthetic generative truth unchanged.
        depth,_,_,diel,calls=generate(seed,0.0)
        shared_truth=(depth,diel,calls)
        for regime in REGIMES:
            rows[regime].append(evaluate(seed,shared_truth,regime))
    result={}
    for regime,draws in rows.items():
        result[regime]={
            "median_heldout_negative_logloss_lag_gain_QA_ONLY":
                round(float(median(x["true_lag_gain_when_direct_effect_zero"]
                                   for x in draws)),6),
            "five_seed_lag_gains_QA_ONLY":[
                round(x["true_lag_gain_when_direct_effect_zero"],6) for x in draws],
            "median_wrong_wetland_lag_placebo_gain_QA_ONLY":
                round(float(median(x["wrong_wetland_lag_placebo_gain"]
                                   for x in draws)),6),
            "mean_generated_depth_missing_fraction":
                round(float(np.mean([x["synthetic_missing_depth_fraction"]
                                     for x in draws])),6)
        }
    payload={
        "status":"SYNTHETIC_SENSOR_ERROR_COUNTEREXAMPLE_EXECUTED",
        "known_true_direct_acoustic_lag":0.0,
        "synthetic_episode_count":N_EPISODES,
        "synthetic_independently_labelled_wetland_count":N_WETLANDS,
        "five_fixed_seeds":list(SEEDS),
        "noise_sd_invented_depth_units":SIGMA,
        "gap_rate_simulation_parameter":GAP_PROBABILITY,
        "scenarios":result,
        "only_synthetic_data":True,
        "no_original_logger_or_audio_observations_read":True,
        "jae_RC6_main_changed":False
    }
    # No sensitive IDs even in artificial public summary output.
    print(json.dumps(payload,sort_keys=True))
    print("PASS: source-free sensor observation regimes, back-only gaps, strictly-prior lag, paired held-out comparisons")

if __name__=="__main__":
    tests()
