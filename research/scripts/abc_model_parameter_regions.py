"""Accepted biological rate regimes from ACTUAL original 80y trophic ABC library.

Analytic conditioning on four model-native signs. No posterior over real frog
mechanisms: priors and stage-to-acoustic bridge are uncalibrated. All 12
structural hypotheses / all 256 shared Latin-hypercube draws retained.

The two latent reverse predation states are averaged WITHIN a rate draw,
not treated as 512 independent draws for each structure.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

from model_native_abc_rf import load_actual_refs,PRIOR_PARAMS,SEED
from model_native_2x2x2_prior import OUT,CONTEXTS,METRICS,TARGET


SCALES=("log","raw")
N_PRIOR_DRAWS=256
N_BOOT=999
N_STRUCTURES=12
ORIGINAL_BASELINE=("original__baseline__risk0","original__baseline__risk1")
CONTINUOUS=tuple(x for x in PRIOR_PARAMS if x!="f_delay")


def independent_prior_weights(reference,scale):
    """Return one row per structural class and truly independent prior vector."""
    col=f"matches_{scale}"
    if col not in reference:
        raise ValueError("Missing model-native sign acceptance "+col)
    group_cols=["structure_id","context","family","risk","draw"]
    p=reference.groupby(group_cols,sort=True)
    checks=p.agg(n_reverse=("reverse_on","nunique"),
                 n_rows=("reverse_on","size"),
                 accepted_weight=(col,"mean"),
                 reverse_acceptance_difference=(col,lambda q:
                                                int(q.max())-int(q.min()))).reset_index()
    if len(checks)!=N_STRUCTURES*N_PRIOR_DRAWS:
        raise AssertionError("Incomplete unique structure x rate-draw ledger")
    if not checks.n_reverse.eq(2).all() or not checks.n_rows.eq(2).all():
        raise AssertionError("Reverse-on/off source not exactly paired")
    if checks.duplicated(["structure_id","draw"]).any():
        raise AssertionError("Rate draw duplicated")
    if not checks.accepted_weight.between(0,1).all():
        raise AssertionError("Invalid latent-edge marginal weight")
    return checks


def quartile_prior_codes(prior,param):
    original=prior.sort_values("draw").reset_index(drop=True)
    if original.draw.nunique()!=N_PRIOR_DRAWS:
        raise ValueError("Missing 256 independent prior vectors")
    if param=="f_delay":
        if set(original.f_delay)!={2,3} or original.f_delay.value_counts().to_dict()!={2:128,3:128}:
            raise ValueError("Maturation prior not balanced 2/3 years")
        return dict(zip(original.draw.to_numpy(int),
                        original.f_delay.to_numpy(int)))
    if param not in CONTINUOUS:
        raise ValueError("Unexpected biological parameter")
    s=original[param]
    if s.nunique()!=N_PRIOR_DRAWS:
        raise ValueError("Continuous LHS parameter not distinct")
    # Prior-draw ranks, exactly 64 values in each quartile. These bins
    # never depend on the observed four-sign acceptance.
    ranks=s.rank(method="first").to_numpy(dtype=int)-1
    bins=ranks//64
    if dict(pd.Series(bins).value_counts().sort_index())!={0:64,1:64,2:64,3:64}:
        raise AssertionError("Unequal prior quartile exposures")
    return dict(zip(original.draw.to_numpy(int),bins))


def all_parameter_regions(reference,prior):
    if len(prior)!=N_PRIOR_DRAWS:
        raise ValueError("Prior sample size changed")
    records=[];summary=[];weights=[]
    prior=prior.sort_values("draw")
    for scale in SCALES:
        marginal=independent_prior_weights(reference,scale)
        weights.append(marginal.assign(scale=scale))
        x=marginal.merge(prior,on="draw",how="inner",validate="many_to_one")
        if len(x)!=N_PRIOR_DRAWS*N_STRUCTURES:
            raise AssertionError("Actual parameters lost in prior join")
        for cls,g in x.groupby("structure_id"):
            full=float(g.accepted_weight.sum())
            p=full/len(g)
            for param in PRIOR_PARAMS:
                actual=g[param].to_numpy(float)
                med=float(np.median(actual))
                bins=quartile_prior_codes(prior,param)
                group=g.assign(prior_bin=g.draw.map(bins))
                accepted=group[group.accepted_weight>0]
                acc=accepted[param].to_numpy(float)
                w=accepted.accepted_weight.to_numpy(float)
                # Reverse-edge nuisance is integrated. If any straddles the
                # exact match edge threshold, weighted quantile replicates
                # are not generated; posterior medians remain descriptive.
                def weighted_quantile(level):
                    if len(acc)==0:return np.nan
                    ix=np.argsort(acc)
                    z=acc[ix];v=w[ix]
                    return float(np.interp(level*v.sum(),np.cumsum(v)-v*.5,z,
                                           left=z[0],right=z[-1]))
                summ=dict(scale=scale,structure_id=cls,parameter=param,
                          n_prior_draws=len(g),effective_accepted_draws=full,
                          weighted_acceptance_rate=p,
                          prior_median=med,
                          accepted_q10=weighted_quantile(.10),
                          accepted_median=weighted_quantile(.50),
                          accepted_q90=weighted_quantile(.90),
                          accepted_median_minus_prior=weighted_quantile(.50)-med
                             if len(acc) else np.nan,
                          enough_accepted_for_interpretation=bool(full>=20))
                summary.append(summ)
                for level,sub in group.groupby("prior_bin",sort=True):
                    n=len(sub)
                    k=float(sub.accepted_weight.sum())
                    records.append(dict(scale=scale,structure_id=cls,parameter=param,
                        prior_bin=int(level),n_prior_draws=n,
                        n_accepted_effective=k,acceptance_rate=k/n,
                        class_overall_acceptance_rate=p,
                        enrichment_vs_class_overall=k/n/p if p>0 else np.nan,
                        prior_bin_min=float(sub[param].min()),
                        prior_bin_median=float(sub[param].median()),
                        prior_bin_max=float(sub[param].max()),
                        prior_quantity="maturation_years" if param=="f_delay"
                                       else "prior_LHS_equal_count_quartile"))
    return pd.DataFrame(records),pd.DataFrame(summary),pd.concat(weights,ignore_index=True)


def pair_refuge_original(weights,n_boot=N_BOOT,seed=SEED+194):
    """Matched actual 256 rate draws, same class except refuge on/off."""
    rows=[];summaries=[]
    rng=np.random.default_rng(seed)
    for scale in SCALES:
        x=weights[(weights.scale==scale)&
                  (weights.structure_id.isin(ORIGINAL_BASELINE))]
        wide=x.pivot(index="draw",columns="structure_id",values="accepted_weight")
        if len(wide)!=N_PRIOR_DRAWS or wide.isna().any().any():
            raise AssertionError("Missing original risk on/off exact pair")
        off=wide[ORIGINAL_BASELINE[0]].to_numpy(float)
        on=wide[ORIGINAL_BASELINE[1]].to_numpy(float)
        gap=off-on
        accepted_off=float(off.sum())
        accepted_on=float(on.sum())
        # Joint paired multinomial bootstrap, not treating edges or class
        # members as 2× independent rate vectors.
        ix=rng.integers(0,len(wide),size=(n_boot,len(wide)))
        replicate=gap[ix].mean(axis=1)
        low,high=np.quantile(replicate,[.025,.975])
        categories=[]
        for draw,Off,On in zip(wide.index,off,on):
            if Off==1 and On==1:status="both"
            elif Off==1 and On==0:status="off_only"
            elif Off==0 and On==1:status="on_only"
            elif Off==0 and On==0:status="neither"
            else:status="edge_discordant_partial"
            rows.append(dict(scale=scale,draw=int(draw),
                             risk_off_acceptance=Off,
                             risk_on_acceptance=On,
                             off_minus_on=Off-On,
                             paired_category=status))
            categories.append(status)
        summaries.append(dict(scale=scale,n_shared_independent_draws=len(wide),
            risk_off_accepted_effective=accepted_off,
            risk_on_accepted_effective=accepted_on,
            risk_off_rate=accepted_off/len(wide),
            risk_on_rate=accepted_on/len(wide),
            mean_off_minus_on=float(gap.mean()),
            paired_bootstrap_95_low=float(low),
            paired_bootstrap_95_high=float(high),
            n_both=int(categories.count("both")),
            n_off_only=int(categories.count("off_only")),
            n_on_only=int(categories.count("on_only")),
            n_neither=int(categories.count("neither")),
            n_partial=int(categories.count("edge_discordant_partial")),
            error_source="999 paired resamplings of original 256 LHS draw IDs; not independent biological field errors"))
    return pd.DataFrame(rows),pd.DataFrame(summaries)


def run(folder=OUT):
    folder=Path(folder);folder.mkdir(exist_ok=True,parents=True)
    source,prior,receipts=load_actual_refs(folder)
    quartiles,marginal,independent=all_parameter_regions(source,prior)
    paired,summary=pair_refuge_original(independent)
    data=dict(prior_quartile_acceptance=quartiles,
              prior_enrichment_summary=marginal,
              independently_weighted_rate_draws=independent,
              matched_refuge_draw_outcomes=paired,
              paired_risk_acceptance=summary)
    for label,frame in data.items():
        frame.to_csv(folder/(label+".csv"),index=False)
    receipt=dict(status="TRUE_80_YEAR_POM_ABC_POSTERIOR_PARAMETER_REGIMES_CONDITIONAL_HYPOTHETICAL_PRIORS",
        n_model_classes=N_STRUCTURES,n_independent_parameter_draws=N_PRIOR_DRAWS,
        n_reverse_edges_per_parameter=2,
        primary_target=dict(zip(METRICS,TARGET)),
        primary_scale="log",
        secondary_scale="raw",n_paired_bootstrap=N_BOOT,
        prior_distributions_not_field_calibrated=True,
        source_refs={str(context):receipts[context]["source_sha256_for_reference"]
                     for context in CONTEXTS},
        code_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        caveats=["Parameter quartile bins fixed from complete LHS prior ranks, not selected sample",
                 "No additional true simulation or posterior prior retuning",
                 "All 12 structures kept; exact reverse ON/OFF averaged as matched rate-draw nuisance",
                 "Accepted parameter marginal is conditional on model class and hypothetical ecological ranges",
                 "Not a measured predation-rate or aquatic-to-adult calling conversion",
                 "Independently held out NAAMP field confirmation unavailable"])
    (folder/"abc_parameter_regions_receipt.json").write_text(
        json.dumps(receipt,indent=2,ensure_ascii=False)+"\n")
    print("ABC_PAIRED_RISK_COMPARISON\n"+summary.to_string(index=False),flush=True)
    main=marginal[(marginal.scale=="log") &
                  marginal.structure_id.isin(ORIGINAL_BASELINE)]
    print("ABC_ACCEPTED_PARAMETER_REGIMES_LOG\n"+main.to_string(index=False),flush=True)
    best=quartiles[(quartiles.scale=="log") &
                   quartiles.structure_id.isin(ORIGINAL_BASELINE)]
    print("ABC_PRIOR_QUARTILES_LOG\n"+
          best[["structure_id","parameter","prior_bin","n_accepted_effective",
                "acceptance_rate","enrichment_vs_class_overall"]].to_string(index=False),flush=True)
    return data


if __name__=="__main__":
    cli=argparse.ArgumentParser()
    cli.add_argument("--run",action="store_true")
    cli.add_argument("--folder",type=Path,default=OUT)
    a=cli.parse_args()
    if not a.run:cli.error("Explicit --run required")
    run(a.folder)
