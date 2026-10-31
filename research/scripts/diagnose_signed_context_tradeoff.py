"""Post-result minimal incompatible directional constraints for frogcs POM.

Consumes previously successful GitHub Actions artifacts and never re-fits
models, re-selects signs, retunes parameters, or treats scenario labels as
independent ecological experiments.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from pathlib import Path

import numpy as np
import pandas as pd

from select_macro_trophic_scenarios import ROOT
from directional_context_modulation_pom import METRICS

OUT=ROOT/"research/results/macro_signed_context_tradeoff_20261031"
SIGNED=ROOT/"research/results/macro_signed_context_modulation_20261031"
PROCESS=ROOT/"research/results/macro_pom_process_prior_20261031"
LEVELS=(.90,.95)
BACKGROUNDS=("uniform","target_group")


def normalize_sources(fixed,rate,source):
    if len(fixed)!=264 or fixed.groupby("background").case.nunique().ne(132).any():
        raise ValueError("Missing fixed 132-case directional ledger")
    if len(rate)!=384 or rate.groupby("background").size().ne(192).any():
        raise ValueError("Missing actual 8×24 simulated-rate ledger")
    if len(source)!=384 or source.groupby("background").size().ne(192).any():
        raise ValueError("Missing original process-rate statistical patterns")
    if fixed.groupby("background").source_group.nunique().ne(104).any():
        raise ValueError("Unexpected fixed-model distinct source group count")
    source=source.rename(columns={"draw":"rate_draw"})
    joined=rate.merge(source,on=["background","rate_draw","case"],
                      how="inner",validate="one_to_one",suffixes=("","_source"))
    if len(joined)!=len(rate):
        raise AssertionError("Process rate signs and source statistical patterns not paired")
    original_s=joined.O_with_S_high.to_numpy(float)-joined.O_with_S_low.to_numpy(float)
    original_v=(joined.heldout_O_with_V_positive.to_numpy(float)-
                joined.heldout_O_with_V_zero.to_numpy(float))
    if not np.allclose(original_s,joined.model_delta_S.to_numpy(float),rtol=0,atol=1e-9):
        raise AssertionError("Disagreement in preexisting true 80-year ΔS responses")
    if not np.allclose(original_v,joined.model_delta_V.to_numpy(float),rtol=0,atol=1e-9):
        raise AssertionError("Disagreement in preexisting true 80-year ΔV responses")
    candidates=fixed[["background","case","source_group"]].copy()
    for metric in METRICS:
        key="model_sign_"+metric
        if key not in fixed:raise ValueError("Missing frozen model sign "+key)
        signs=fixed[key].to_numpy(float)
        if not np.isin(signs,[-1,0,1]).all():
            raise ValueError("Corrupt source sign field")
        candidates[metric]=signs.astype(int)
    actual=joined[["background","rate_draw","case","structural_group"]].copy()
    numbers=dict(OS=joined.OS,OV=joined.OV,
                 delta_S_high_minus_low=joined.model_delta_S,
                 delta_V_positive_minus_zero=joined.model_delta_V)
    for key,vals in numbers.items():
        x=np.sign(vals.to_numpy(float))
        if not np.isfinite(x).all():
            raise ValueError("Nonfinite rate-source statistic")
        actual[key]=x.astype(int)
    return candidates,actual,dict(n_frozen=len(candidates),n_real_rate=len(actual),
                                  max_recomputed_delta_S_discrepancy=float(np.abs(
                                      original_s-joined.model_delta_S).max()),
                                  max_recomputed_delta_V_discrepancy=float(np.abs(
                                      original_v-joined.model_delta_V).max()))


def observed_sign_targets(obs,cutoff):
    result={}
    for bg in BACKGROUNDS:
        frame=obs[obs.background==bg]
        if len(frame)!=4 or frame.metric.nunique()!=4:
            raise ValueError("Incomplete 4-component observed signed context")
        selected={}
        for r in frame.itertuples(index=False):
            val=max(r.frequency_negative,r.frequency_positive)
            if val>=cutoff:
                sign=-1 if r.frequency_negative>r.frequency_positive else 1
                if sign!=int(r.observed_direction):
                    raise AssertionError("Observed sign vs bootstrap direction disagreement")
                selected[str(r.metric)]=sign
        if not selected:raise ValueError("No robust signs at fixed confidence cutoff")
        result[bg]=selected
    return result


def satisfies(frame,conditions):
    if not conditions:raise ValueError("Empty sign constraint subset")
    masks=[frame[name].to_numpy(dtype=int)==sign
           for name,sign in conditions.items()]
    return np.logical_and.reduce(masks)


def enumerate_all_subsets(fixed,actual,targets):
    records=[]
    for bg in BACKGROUNDS:
        f=fixed[fixed.background==bg]
        a=actual[actual.background==bg]
        eligible=list(targets[bg])
        for n in range(1,len(eligible)+1):
            for names in itertools.combinations(eligible,n):
                conditions={k:targets[bg][k] for k in names}
                vf=f.loc[satisfies(f,conditions)]
                va=a.loc[satisfies(a,conditions)]
                records.append(dict(background=bg,n_constraints=len(names),
                                    subset=";".join(names),
                                    direction_signature=";".join(
                                        k+("−" if v<0 else "+") for k,v in conditions.items()),
                                    n_frozen_cases=len(vf),
                                    n_frozen_source_groups=vf.source_group.nunique(),
                                    n_real_rate_configs=len(va),
                                    n_real_rate_structure_groups=va.structural_group.nunique()))
    out=pd.DataFrame(records)
    if len(out)!=2*(2**len(METRICS)-1):
        raise AssertionError("Incomplete sign subset lattice")
    return out


def minimal_conflicts(table,column):
    """A minimal unsatisfied set has no proper unsatisfied nonempty subset."""
    result=[]
    for r in table.itertuples(index=False):
        if getattr(r,column)!=0:continue
        terms=set(r.subset.split(";"))
        bg=table[table.background==r.background]
        has_smaller_failure=False
        for small in bg.itertuples(index=False):
            proper=set(small.subset.split(";"))
            if proper < terms and getattr(small,column)==0:
                has_smaller_failure=True
                break
        if not has_smaller_failure:
            result.append(dict(background=r.background,subset=r.subset,
                               n_constraints=r.n_constraints,
                               dataset=column))
    return pd.DataFrame(result)


def threshold_sensitivity(fixed,actual,obs):
    rows=[]
    for threshold in LEVELS:
        targets=observed_sign_targets(obs,threshold)
        passing={}
        for bg in BACKGROUNDS:
            f=fixed[fixed.background==bg]
            a=actual[actual.background==bg]
            fi=f.loc[satisfies(f,targets[bg])]
            ra=a.loc[satisfies(a,targets[bg])]
            passing[bg]=set(fi.case)
            rows.append(dict(threshold=threshold,background=bg,
                             eligible=";".join(targets[bg]),
                             n_robust_directions=len(targets[bg]),
                             n_fixed_case_labels=len(fi),
                             n_exact_source_groups=fi.source_group.nunique(),
                             n_rate_configs=len(ra),
                             n_rate_structure_groups=ra.structural_group.nunique(),
                             n_cross_background_case_labels=np.nan))
        combined=len(passing[BACKGROUNDS[0]]&passing[BACKGROUNDS[1]])
        for row in rows[-2:]:row["n_cross_background_case_labels"]=combined
    return pd.DataFrame(rows)


def run(signed=SIGNED,process=PROCESS,out=OUT):
    out.mkdir(parents=True,exist_ok=True)
    paths=[signed/"observed_signed_context.csv",
           signed/"fixed_case_scores.csv",
           signed/"real_rate_case_scores.csv",
           process/"process_prior_predictive_patterns.csv"]
    for p in paths:
        if not p.is_file() or p.stat().st_size<100:
            raise FileNotFoundError("Missing pinned real-data evidence "+str(p))
    observation,fixed,rate,source=[pd.read_csv(path) for path in paths]
    original,demographic,replay=normalize_sources(fixed,rate,source)
    targets=observed_sign_targets(observation,.90)
    subsets=enumerate_all_subsets(original,demographic,targets)
    minimum=pd.concat([
        minimal_conflicts(subsets,"n_frozen_source_groups"),
        minimal_conflicts(subsets,"n_real_rate_configs")],ignore_index=True)
    thresholds=threshold_sensitivity(original,demographic,observation)
    for name,frame in [("all_nonempty_direction_subsets",subsets),
                       ("minimal_incompatible_direction_sets",minimum),
                       ("observed_sign_threshold_sensitivity",thresholds)]:
        frame.to_csv(out/(name+".csv"),index=False)
    receipt=dict(status="POST_RESULT_MINIMAL_DIRECTION_INCOMPATIBILITY_DIAGNOSTIC",
                 same_observed_signed_context=True,
                 model_data_not_refitted=True,
                 biological_parameter_priors_not_calibrated=True,
                 source_replay=replay,
                 n_subsets=len(subsets),
                 near_zero_threshold_not_used=True,
                 supported_direction_thresholds=list(LEVELS),
                 source_hashes={str(path.relative_to(ROOT)):hashlib.sha256(path.read_bytes()).hexdigest()
                                for path in paths},
                 code_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    (out/"receipt.json").write_text(json.dumps(receipt,indent=2)+"\n")
    print("SUBSET_DIRECTION_TRADEOFFS\n"+subsets.to_string(index=False),flush=True)
    print("MINIMAL_INCOMPATIBILITIES\n"+minimum.to_string(index=False),flush=True)
    print("THRESHOLD_SENSITIVITY\n"+thresholds.to_string(index=False),flush=True)
    return subsets,minimum,thresholds


if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--run",action="store_true")
    p.add_argument("--signed-artifact",type=Path,default=SIGNED)
    p.add_argument("--process-artifact",type=Path,default=PROCESS)
    args=p.parse_args()
    if not args.run:p.error("Explicit --run required")
    run(signed=args.signed_artifact,process=args.process_artifact)
