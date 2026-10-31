"""Post-result rate-prior stress test using REAL original frogcs 80-y source ABC.

Same 12 ontogenetic model classes, actual 256 independent demographic rate
draws and paired ON/OFF reversal responses. Importance weights represent
explicit hypothetical new prior DENSITIES on IDENTICAL supports, not new
simulations, new field samples or calibrated biological priors.

Resample the SAME 256 draw IDs across all 12 classes, both reverse states,
both ecological response scales and each new prior sensitivity hypothesis.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

from model_native_2x2x2_prior import OUT, METRICS, TARGET, N_DRAWS
from model_native_abc_rf import load_actual_refs
from abc_model_parameter_regions import independent_prior_weights

N_BOOT=999
SEED=20261102
SCALES=("log","raw")
SCENARIOS=(
    "original",
    "attack_uniform",
    "attack_favors_weak",
    "attack_favors_strong",
    "frog_juvenile_favors_high",
    "frog_juvenile_favors_low",
    "maturity_favors_2y",
    "maturity_favors_3y",
    "joint_weak_attack_high_juvenile",
)
PRIOR_PARAMETERS=("attack_scale","s_growth_multiplier","d_growth_multiplier",
                  "rho","conversion","f_juvenile_survival",
                  "f_adult_survival","f_delay")
BASELINE=OUT/"abc_rejection_model_acceptance.csv"


def importance_weights(prior):
    """Normalized per-rate importance weights, *never* case-specific fitting."""
    q=prior.sort_values("draw").reset_index(drop=True)
    if len(q)!=N_DRAWS or q.draw.nunique()!=N_DRAWS:
        raise ValueError("Need all 256 uniquely paired original rate draws")
    if any(k not in q for k in PRIOR_PARAMETERS):
        raise ValueError("A biological process parameter is missing")
    a=q.attack_scale.to_numpy(float)
    j=q.f_juvenile_survival.to_numpy(float)
    delay=q.f_delay.to_numpy(int)
    if (np.any(~np.isfinite(a)) or np.any(~np.isfinite(j)) or
        np.any((a<=.25)|(a>=1.0)) or
        np.any((j<=.60)|(j>=.90)) or set(delay)!={2,3} or
        (q.f_delay.value_counts().to_dict()!={2:N_DRAWS//2,3:N_DRAWS//2})):
        raise ValueError("Outside frozen prior support or unequal delays")
    attack_uniform=a*np.log(4.)/.75
    low_attack=2*(1-a)*a*np.log(4.)/(.75**2)
    high_attack=2*(a-.25)*a*np.log(4.)/(.75**2)
    high_survival=2*(j-.60)/.30
    low_survival=2*(.90-j)/.30
    prior_weight={
        "original":np.ones(len(q),float),
        "attack_uniform":attack_uniform,
        "attack_favors_weak":low_attack,
        "attack_favors_strong":high_attack,
        "frog_juvenile_favors_high":high_survival,
        "frog_juvenile_favors_low":low_survival,
        "maturity_favors_2y":np.where(delay==2,1.5,.5),
        "maturity_favors_3y":np.where(delay==3,1.5,.5),
        "joint_weak_attack_high_juvenile":low_attack*high_survival,
    }
    if set(prior_weight)!=set(SCENARIOS):
        raise AssertionError("Not all prespecified prior density changes applied")
    rows=[]
    for name,weights in prior_weight.items():
        if not np.isfinite(weights).all() or (weights<0).any() or weights.sum()<=0:
            raise ValueError("Invalid importance density ratio")
        # Self-normalized importance sampling is conditional on the same
        # already simulated, finite Latin-hypercube rate source.
        weights=weights*len(weights)/weights.sum()
        prior_weight[name]=weights
        for draw,w in zip(q.draw,weights):
            rows.append(dict(draw=int(draw),scenario=name,weight=float(w)))
    return pd.DataFrame(rows),prior_weight


def matrix_of_independent_rate_draws(reference,scale):
    """One row per original 256 rate vectors and one column per true class."""
    if scale not in SCALES:
        raise ValueError("Unexpected response-scale hypothesis")
    grouped=independent_prior_weights(reference,scale)
    if len(grouped)!=12*N_DRAWS or grouped.duplicated(
            ["draw","structure_id"]).any():
        raise AssertionError("Genuine reverse-paired source completeness failed")
    if not grouped.accepted_weight.between(0,1).all():
        raise AssertionError("Fraction of two reversed edges must lie in [0,1]")
    draw_ids=sorted(grouped.draw.unique())
    classes=sorted(grouped.structure_id.unique())
    if len(draw_ids)!=N_DRAWS or len(classes)!=12:
        raise AssertionError("Wrong number of real demographic simulations")
    result=grouped.pivot(index="draw",columns="structure_id",
                         values="accepted_weight").loc[draw_ids,classes]
    if result.isna().any().any():raise AssertionError("Missing matched rate record")
    # Note: for all existing cases this is either 0 or 1. Keep .5 valid,
    # because reversal paths can eventually change the target if priors change.
    arr=result.to_numpy(float)
    return np.asarray(draw_ids,int),classes,arr,grouped


def weighted_summary(A,w,replicate_indices=None):
    """Rates and equal-class-prior model shares without duplicating ON/OFF."""
    data=np.asarray(A,float);weights=np.asarray(w,float)
    if data.ndim!=2 or len(weights)!=len(data) or not np.isfinite(data).all():
        raise ValueError("Bad importance/reference dimensions")
    if not (np.isfinite(weights).all() and (weights>=0).all() and weights.sum()>0):
        raise ValueError("Nonpositive/invalid importance weights")
    hits=weights[:,None]*data
    rates=hits.sum(axis=0)/weights.sum()
    mass=rates.sum()
    if mass<=0:
        raise ValueError("No four-sign matches under this hypothetical prior: undefined model shares")
    shares=rates/mass
    n_eff_prior=float(weights.sum()**2/np.sum(weights**2))
    accepted_eff=np.divide(hits.sum(axis=0)**2,np.sum(hits**2,axis=0),
                           out=np.zeros(data.shape[1],float),
                           where=np.sum(hits**2,axis=0)>0)
    if replicate_indices is None:
        return rates,shares,accepted_eff,n_eff_prior,None,None
    indices=np.asarray(replicate_indices,int)
    if indices.ndim!=2 or indices.shape[1]!=len(weights):
        raise ValueError("Bootstrap must resample full matched rate-ID blocks")
    weighted_samples=weights[indices]
    response_samples=data[indices,:]
    sums=np.einsum("bd,bdc->bc",weighted_samples,response_samples)
    normalizer=weighted_samples.sum(axis=1)
    if np.any(normalizer<=0) or np.any(sums.sum(axis=1)<=0):
        raise ValueError("Zero accepted mass in one paired importance bootstrap")
    rates_boot=sums/normalizer[:,None]
    shares_boot=sums/sums.sum(axis=1,keepdims=True)
    return rates,shares,accepted_eff,n_eff_prior,rates_boot,shares_boot


def run(folder=OUT,n_boot=N_BOOT):
    folder=Path(folder)
    reference,priors,source_receipts=load_actual_refs(folder)
    weights_ledger,all_w=importance_weights(priors)
    archived=pd.read_csv(BASELINE if folder==OUT else folder/"abc_rejection_model_acceptance.csv")
    all_results=[];all_marginals=[];all_chosen=[];all_matrix=[]
    rng=np.random.default_rng(SEED)
    bootstrap=rng.integers(0,N_DRAWS,size=(n_boot,N_DRAWS))
    for scale in SCALES:
        ids,classes,A,grouped=matrix_of_independent_rate_draws(reference,scale)
        if not np.array_equal(ids,priors.sort_values("draw").draw.to_numpy(int)):
            raise AssertionError("Reference draw IDs differ from original parameter priors")
        details=grouped.drop_duplicates("structure_id").set_index("structure_id")
        for prior_name in SCENARIOS:
            w=all_w[prior_name]
            rates,shares,accepted_eff,ess,bs_rates,bs_shares=weighted_summary(
                A,w,bootstrap)
            if prior_name=="original":
                baseline=archived[archived.scale==scale].set_index("structure_id")
                if len(baseline)!=12:
                    raise AssertionError("Wrong frozen published ABC source")
                for j,name in enumerate(classes):
                    if name not in baseline.index or (
                        abs(rates[j]-float(baseline.loc[name,"acceptance_rate"]))>1e-12 or
                        abs(shares[j]-float(baseline.loc[name,"conditional_abc_model_share"]))>1e-12):
                        raise AssertionError("Published 80y ABC model result cannot be replayed")
            marginal_groups={x:[] for x in ("context","family","risk")}
            for j,cls in enumerate(classes):
                meta=details.loc[cls]
                values=dict(scale=scale,prior_sensitivity=prior_name,
                            structure_id=cls,context=str(meta.context),
                            family=str(meta.family),risk=bool(meta.risk),
                            n_original_rate_draws=N_DRAWS,
                            original_reverse_edge_variants=2,
                            weighted_acceptance_rate=float(rates[j]),
                            acceptance_rate_ci_low=float(np.quantile(bs_rates[:,j],.025)),
                            acceptance_rate_ci_high=float(np.quantile(bs_rates[:,j],.975)),
                            conditional_abc_share=float(shares[j]),
                            conditional_share_ci_low=float(np.quantile(bs_shares[:,j],.025)),
                            conditional_share_ci_high=float(np.quantile(bs_shares[:,j],.975)),
                            effective_prior_draws=float(ess),
                            effective_accepted_draws=float(accepted_eff[j]),
                            accepted_parameter_regime_interpretable=bool(accepted_eff[j]>=20),
                            status="IMPORTANCE_REWEIGHTED_REAL_80Y_HYPOTHETICAL_PRIOR")
                all_results.append(values)
                for dimension in marginal_groups:
                    marginal_groups[dimension].append(meta[dimension])
            for dimension,members in marginal_groups.items():
                levels=sorted(set(members),key=str)
                for label in levels:
                    ix=np.flatnonzero(np.asarray(members)==label)
                    q=bs_shares[:,ix].sum(axis=1)
                    all_marginals.append(dict(
                        scale=scale,prior_sensitivity=prior_name,
                        dimension=dimension,label=str(label),
                        conditional_abc_share=float(shares[ix].sum()),
                        share_ci_low=float(np.quantile(q,.025)),
                        share_ci_high=float(np.quantile(q,.975)),
                        effective_prior_draws=ess))
            top=int(np.argmax(shares))
            original_share=sum(shares[j] for j,c in enumerate(classes)
                               if details.loc[c,"context"]=="original")
            baseline_share=sum(shares[j] for j,c in enumerate(classes)
                               if details.loc[c,"family"]=="baseline")
            all_chosen.append(dict(scale=scale,prior_sensitivity=prior_name,
                                   winner=classes[top],
                                   winner_share=float(shares[top]),
                                   winner_acceptance=float(rates[top]),
                                   n_classes_positive=int((rates>0).sum()),
                                   original_context_share=float(original_share),
                                   baseline_handling_share=float(baseline_share),
                                   effective_prior_draws=ess,
                                   min_class_effective_accepted=float(accepted_eff.min()),
                                   n_classes_effective_accepted_ge20=int((accepted_eff>=20).sum())))
        for j,cls in enumerate(classes):
            for i,draw in enumerate(ids):
                all_matrix.append(dict(scale=scale,draw=int(draw),
                                       structure_id=cls,
                                       paired_edge_accepted_fraction=float(A[i,j])))
    result=pd.DataFrame(all_results)
    marginal=pd.DataFrame(all_marginals)
    chosen=pd.DataFrame(all_chosen)
    accepted=pd.DataFrame(all_matrix)
    if len(result)!=len(SCALES)*len(SCENARIOS)*12 or len(chosen)!=18:
        raise AssertionError("Missing some conditional model-prior comparisons")
    folder.mkdir(parents=True,exist_ok=True)
    prefix="prior_density_stress_"
    for name,frame in [("source_weights",weights_ledger),("class_shares",result),
                       ("structural_axis_marginals",marginal),
                       ("winner_sensitivity",chosen),
                       ("source_paired_draw_acceptance",accepted)]:
        frame.to_csv(folder/(prefix+name+".csv"),index=False)
    provenance=[folder/(name+"_prior_predictive_reference.csv.gz") for name in
                ("original","D_first_S_overtakes","S_first_D_overtakes")]
    provenance+=[folder/(name+"_parameter_draws.csv") for name in
                 ("original","D_first_S_overtakes","S_first_D_overtakes")]
    receipt=dict(status="GENUINE_80_YEAR_ABCPOM_PRIOR_DENSITY_STRESS_NOT_FIELD_MODEL_PROBABILITY",
                 n_source_structures=12,source_runs_80year=6144,
                 n_matched_prior_draws=N_DRAWS,n_bootstrap=n_boot,
                 scenarios=list(SCENARIOS),scales=list(SCALES),
                 original_model_replay_success=True,
                 original_case_source_receipts=source_receipts,
                 method="self-normalized analytic density-ratio reweighting under identical support",
                 caveats=["Original and alternate rate priors are hypothetical not field-calibrated",
                          "No extra demographic model runs were executed; original 6144 reused",
                          "Same 256 rate vectors shared by all classes and both edge choices",
                          "Four model-native interaction signs are not a field likelihood",
                          "Model-class shares are conditional on candidate models and importance prior",
                          "No real-world posterior mechanism probabilities"],
                 source_sha256={str(p.relative_to(Path(folder).parents[2])):
                                hashlib.sha256(p.read_bytes()).hexdigest()
                                for p in provenance},
                 script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    (folder/(prefix+"receipt.json")).write_text(
        json.dumps(receipt,indent=2,ensure_ascii=False)+"\n")
    print("PRIOR_SENSITIVITY_WINNERS\n"+chosen.to_string(index=False),flush=True)
    print("MODEL_CLASS_PRIOR_STRESS\n"+result.to_string(index=False),flush=True)
    print("PRIOR_SENSITIVITY_MARGINALS\n"+marginal.to_string(index=False),flush=True)
    return dict(class_shares=result,marginal=marginal,winners=chosen,weights=weights_ledger)


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--run",action="store_true")
    parser.add_argument("--directory",type=Path,default=OUT)
    parser.add_argument("--bootstrap",type=int,default=N_BOOT)
    opts=parser.parse_args()
    if not opts.run:parser.error("Explicit --run required")
    run(opts.directory,opts.bootstrap)
