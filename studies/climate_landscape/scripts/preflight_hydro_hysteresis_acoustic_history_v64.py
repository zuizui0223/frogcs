#!/usr/bin/env python3
"""v6.4 synthetic-only ecological phase/history preflight (NO real animal data).

A prospective analysis guard, not a fitted model or biological result.
See V6_4_HYDROLOGICAL_HYSTERESIS_VS_ACOUSTIC_HISTORY_PROSPECTIVE_DESIGN.md
"""
from __future__ import annotations
from collections import defaultdict
from datetime import datetime
import json


def time(s):
    d=datetime.fromisoformat(s.replace("Z","+00:00"))
    if d.tzinfo is None or d.utcoffset() is None:
        raise ValueError("TIMEZONE_REQUIRED")
    return d

def past_only_water_phase(rows, noise_threshold, max_interval_seconds, depth_bin):
    """Classify local rising/falling using only current and PREVIOUS values.

    Input measurements are synthetic numeric depths with date-effective
    logger-to-wetland mapping ALREADY separately source-authenticated.
    Returns internal event records for downstream metadata QC; NEVER export
    those keys from original sensitive sources.
    """
    if noise_threshold is None or noise_threshold < 0 or depth_bin is None or depth_bin <= 0:
        raise ValueError("SOURCE_SENSOR_THRESHOLDS_REQUIRED")
    if not isinstance(max_interval_seconds,(int,float)) or max_interval_seconds <= 0:
        raise ValueError("SOURCE_GAP_LIMIT_REQUIRED")
    groups=defaultdict(list)
    for r in rows:
        if not isinstance(r.get("wetland"),str) or not isinstance(r.get("logger"),str):
            raise ValueError("MISSING_SOURCE_WETLAND_LOGGER")
        if not isinstance(r.get("depth"), (int,float)):
            raise ValueError("MISSING_NUMERIC_DEPTH")
        groups[(r["wetland"],r["logger"])].append((time(r["timestamp"]),r["depth"]))
    out=[]
    for (wet,logger),observations in groups.items():
        ordered=sorted(observations)
        for index,(t,d) in enumerate(ordered):
            phase="UNKNOWN"
            if index>0:
                previous_t,previous_d=ordered[index-1]
                span=(t-previous_t).total_seconds()
                if span==0:raise ValueError("DUPLICATE_LOGGER_TIMESTAMP")
                if span<=max_interval_seconds:
                    difference=d-previous_d
                    phase=("RISING" if difference>noise_threshold else
                           "FALLING" if difference < -noise_threshold else "STABLE")
            # Bin is a SENSOR-based depth interval; never learned from frog calls.
            bin_id=round(d/depth_bin)
            out.append({"wetland":wet,"logger":logger,
                        "timestamp":t.isoformat(),"depth_bin":bin_id,"phase":phase})
    return out


def phase_support(phase_records):
    """Count distinct wetland × depth-bin strata with both limbs.

    This is necessary, NOT sufficient: season/solar phase, climate, noise and
    independent episode support still must be checked before a real analysis.
    """
    pairs=defaultdict(set)
    for r in phase_records:
        if r["phase"] in {"RISING","FALLING"}:
            pairs[(r["wetland"],r["depth_bin"])].add(r["phase"])
    valid={key for key,phases in pairs.items() if phases=={"RISING","FALLING"}}
    return {
       "n_wetlands_with_both_limbs_same_sensor_depth_bin":len({k[0] for k in valid}),
       "n_wetland_depth_bins_with_both_limbs":len(valid),
       "solar_season_climate_matching_verified":False,
       "independent_wetting_episodes_verified":False,
    }


def prior_episode_history(targets, labelled_training_episodes, training_cutoff):
    """Causal-clock history feature, ONLY episodes ended before cutoff AND target.

    No same-episode, target evaluation year or future acoustic data may enter.
    This alone is not sufficient for fold-independent model estimation:
    classifier calibration/model fitting also needs leakage-free folds.
    """
    cutoff=time(training_cutoff)
    training=[]
    for x in labelled_training_episodes:
        a,b=time(x["start"]),time(x["end"])
        if not a < b: raise ValueError("INVALID_ACOUSTIC_HISTORY_EPISODE")
        if b>cutoff: raise ValueError("HISTORY_OUTSIDE_FROZEN_TRAINING_CUTOFF")
        training.append((x["wetland"],x["species"],a,b,x["acoustic_score"]))
    result=[]
    for y in targets:
        start=time(y["start"])
        if start<=cutoff:
            raise ValueError("TARGET_NOT_AFTER_TRAINING_CUTOFF")
        valid=[(end,score) for w,s,a,end,score in training
               if w==y["wetland"] and s==y["species"] and end<start]
        latest=max(valid,key=lambda x:x[0])[1] if valid else None
        result.append({"history_available":latest is not None,
                       "previous_completed_episode_score":latest})
    return result


def tests():
    data=[
      {"wetland":"W-A","logger":"L-A","timestamp":"2024-01-01T00:00:00+00:00","depth":0.0},
      {"wetland":"W-A","logger":"L-A","timestamp":"2024-01-01T01:00:00+00:00","depth":1.0},
      {"wetland":"W-A","logger":"L-A","timestamp":"2024-01-01T02:00:00+00:00","depth":2.0},
      {"wetland":"W-A","logger":"L-A","timestamp":"2024-01-01T03:00:00+00:00","depth":1.0},
      {"wetland":"W-A","logger":"L-A","timestamp":"2024-01-01T04:00:00+00:00","depth":0.0},
      {"wetland":"W-B","logger":"L-B","timestamp":"2024-01-01T00:00:00+00:00","depth":0.0},
      {"wetland":"W-B","logger":"L-B","timestamp":"2024-01-01T01:00:00+00:00","depth":1.0},
    ]
    phases=past_only_water_phase(data,0.1,3600,1.0)
    s=phase_support(phases)
    assert s["n_wetlands_with_both_limbs_same_sensor_depth_bin"]==1
    assert s["n_wetland_depth_bins_with_both_limbs"]==1
    assert phases[0]["phase"]=="UNKNOWN"
    assert phases[1]["phase"]=="RISING"
    assert phases[3]["phase"]=="FALLING"
    # Unknown phase when gauge measurement interval exceeds source QC gap.
    long_gap=past_only_water_phase(data,0.1,1,1.0)
    assert all(x["phase"]=="UNKNOWN" for x in long_gap)
    # Prior acoustic event is completed and strictly before BOTH target and cutoff.
    history=[{"wetland":"W-A","species":"S-A","start":"2023-01-01T00:00:00Z",
              "end":"2023-01-02T00:00:00Z","acoustic_score":0.6}]
    targets=[{"wetland":"W-A","species":"S-A","start":"2025-01-01T00:00:00Z"},
             {"wetland":"W-B","species":"S-A","start":"2025-01-01T00:00:00Z"}]
    h=prior_episode_history(targets,history,"2024-12-31T23:59:59Z")
    assert h[0]["previous_completed_episode_score"]==0.6
    assert not h[1]["history_available"]
    future=[*history,{"wetland":"W-A","species":"S-A","start":"2025-01-03T00:00:00Z",
                     "end":"2025-01-04T00:00:00Z","acoustic_score":0.99}]
    try:
        prior_episode_history(targets,future,"2024-12-31T23:59:59Z")
    except ValueError as ex:assert str(ex)=="HISTORY_OUTSIDE_FROZEN_TRAINING_CUTOFF"
    else:raise AssertionError("evaluation-year / future event leaked into history")
    try:
        past_only_water_phase(data, None, 3600, 1)
    except ValueError as ex:assert str(ex)=="SOURCE_SENSOR_THRESHOLDS_REQUIRED"
    else:raise AssertionError("non-source-calibrated depth phase was accepted")
    # Source labels never enter the public QC output.
    printed=json.dumps({"status":"SYNTHETIC_QA_ONLY","phase_support":s,
                        "future_labels_blocked":True,"source_data_accessed":False,
                        "jae_rc6_changed":False},sort_keys=True)
    assert "W-A" not in printed and "L-A" not in printed and "S-A" not in printed
    print(printed)
    print("PASS: synthetic rising/receding overlap, missing history, future leakage, timestamp gaps and source-threshold gate")

if __name__=="__main__":
    tests()
