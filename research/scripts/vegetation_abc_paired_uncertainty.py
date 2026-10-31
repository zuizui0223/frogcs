"""Paired 256-rate-ID uncertainty and plant-path interactions in actual 80y POM.

The same Latin-hypercube draw is used in every 12-plant mechanism, risk refuge
ON/OFF and postmetamorph reversal ON/OFF. Resample whole rate-draw IDs, NOT
4096/6144 pseudo-independent matches. This remains synthetic-prior-conditional
mechanism generation, not field vegetation causal identification.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from model_native_vegetation_abc import OUT
from summarize_model_native_vegetation_abc import (
    load_evidence,paired_role_effects
)

N_DRAWS=256
N_BOOT=1999
SEED=20261104
SCALES=("log","raw")
ROLES=("cover_SF","cover_DF","cover_DS","litter")
ENDPOINTS=("gain_acceptance","delta_beta_OS","delta_beta_OV",
           "delta_beta_SV","delta_beta_OSV")


def paired_draw_interval(group,draws=N_DRAWS,bs=N_BOOT,seed=SEED):
    """Mean pairwise ON−OFF per independent prior vector with 1999 shared resamples."""
    if group.draw.nunique()!=draws or group[["draw","reverse_on"]].isna().any().any():
        raise ValueError("Missing matched 256 original prior draw IDs")
    matrix=group.groupby("draw")[list(ENDPOINTS)].mean().sort_index()
    if len(matrix)!=draws or not np.isfinite(matrix.to_numpy(float)).all():
        raise ValueError("Nonfinite paired source contrast")
    random=np.random.default_rng(seed).integers(0,draws,size=(bs,draws))
    boot=matrix.to_numpy(float)[random].mean(axis=1)
    empirical=matrix.to_numpy(float).mean(axis=0)
    if not boot.shape==(bs,len(ENDPOINTS)):
        raise AssertionError("Incorrect source-identity bootstrap")
    return pd.DataFrame([dict(endpoint=k,mean=float(empirical[j]),
                              lower=float(np.quantile(boot[:,j],.025)),
                              upper=float(np.quantile(boot[:,j],.975)),
                              n_independent_rate_draws=draws,
                              n_original_pairwise_configs=len(group))
                         for j,k in enumerate(ENDPOINTS)])


def factorial_subgroup_stats(paired):
    """Document when each plant role actually improves generating all four signs."""
    out=[]
    for (scale,role),g in paired.groupby(["scale","axis"],sort=True):
        sub=paired_draw_interval(g,seed=SEED+(0 if scale=="log" else 100))
        for item in sub.to_dict("records"):
            out.append(dict(scale=scale,plant_axis=role,grouping="all_legal_pairs",
                            setting="all",**item))
        # Every other plant flag is a pre-existing model hypothesis. Stratify,
        # never flip multiple biology pathways in an ON−OFF pair.
        for second in ROLES:
            if second==role or second not in g:
                continue
            for flag,part in g.groupby(second):
                if part.draw.nunique()!=N_DRAWS:
                    raise AssertionError("Conditional mechanism subgroup lost rate draw")
                field=paired_draw_interval(
                    part,seed=SEED+500+(1 if scale=="raw" else 0)+
                    ROLES.index(role)*100+ROLES.index(second)*2+int(flag))
                for item in field.to_dict("records"):
                    out.append(dict(scale=scale,plant_axis=role,
                                    grouping="conditional_on_"+second,
                                    setting=str(int(flag)),**item))
    return pd.DataFrame(out)


def structural_ablation_interaction(paired,scale,role,condition):
    """Difference of paired gains when an independent plant axis is ON vs OFF."""
    selected=paired[(paired.scale==scale)&(paired.axis==role)]
    if role==condition or condition not in selected:
        raise ValueError("Independent plant treatment required")
    keys=[k for k in ("risk","draw","reverse_on","cover_SF","cover_DF",
                      "cover_DS","litter") if k in selected and
          k not in (role,condition)]
    if condition=="litter":
        selected=selected[selected.cover_DF==0]
    if role=="litter" and condition=="cover_DF":
        raise ValueError("Main catalog forbids litter×F-from-D physical double-path")
    source=selected.pivot(index=keys,columns=condition,
                          values="gain_acceptance")
    # Some combinations in the full main catalog are not independently
    # manipulable, so only matched legal strata remain.
    source=source.dropna()
    if source.empty:
        return None
    interactions=source[1]-source[0]
    base=interactions.reset_index()
    return pd.DataFrame(dict(draw=base.draw,
                             delta_of_on_off_gain=interactions.to_numpy(float)))


def run(source=OUT,out=OUT):
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    sim=load_evidence(Path(source),n=N_DRAWS)
    pairs=[]
    for scale in SCALES:
        p,_=paired_role_effects(sim,scale)
        pairs.append(p)
    full=pd.concat(pairs,ignore_index=True)
    report=factorial_subgroup_stats(full)
    main=report[(report.grouping=="all_legal_pairs")&
                (report.endpoint=="gain_acceptance")]
    if len(main)!=8 or main.n_independent_rate_draws.ne(N_DRAWS).any():
        raise AssertionError("Incomplete primary plant role acceptance effects")
    interactions=[]
    for mode in SCALES:
        for independent,context in (("cover_SF","litter"),
                                    ("cover_DS","litter"),
                                    ("litter","cover_SF"),
                                    ("litter","cover_DS")):
            q=structural_ablation_interaction(full,mode,independent,context)
            if q is None:continue
            if q.draw.nunique()!=N_DRAWS:
                raise AssertionError("Unmatched conditional model interaction rate IDs")
            z=paired_draw_interval(
                q.rename(columns={"delta_of_on_off_gain":"gain_acceptance"}).
                    assign(delta_beta_OS=0.,delta_beta_OV=0.,
                           delta_beta_SV=0.,delta_beta_OSV=0.),
                seed=SEED+ROLES.index(independent)*11+
                ROLES.index(context)*7+(1 if mode=="raw" else 0))
            item=z[z.endpoint=="gain_acceptance"].iloc[0]
            interactions.append(dict(scale=mode,primary_axis=independent,
                                     context_axis=context,
                                     n_independent_draws=N_DRAWS,
                                     mean_interaction=float(item["mean"]),
                                     bootstrap_ci_low=float(item.lower),
                                     bootstrap_ci_high=float(item.upper),
                                     n_paired_source_contexts=len(q)))
    interaction=pd.DataFrame(interactions)
    report.to_csv(out/"full256_vegetation_paired_bootstrap_by_axis.csv",index=False)
    main.to_csv(out/"full256_vegetation_paired_main_effects.csv",index=False)
    interaction.to_csv(out/"full256_vegetation_function_interactions.csv",index=False)
    print("FULL256_PAIRED_VEGETATION_MAIN_EFFECTS\n"+
          main.to_string(index=False),flush=True)
    print("FULL256_PAIRED_VEGETATION_SYNERGIES\n"+
          interaction.to_string(index=False),flush=True)
    return report,main,interaction


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--run",action="store_true")
    p.add_argument("--directory",type=Path,default=OUT)
    a=p.parse_args()
    if not a.run:p.error("Explicit --run required")
    run(a.directory,a.directory)
