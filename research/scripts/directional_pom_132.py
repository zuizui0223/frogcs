"""Uncertainty-aware direction-only POM on original frogcs NAAMP site distribution.

This is NOT biological ABC inference: model stochasticity is an illustrative
fixed rank-observation noise / SDM suitability transport model. All 132 frozen
trophic parameterizations enter. Identical F_B surfaces share identical draws.
Sign agreement is correlated across patterns and cannot be a field posterior.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd

from select_macro_trophic_scenarios import ROOT, SITE, VISITS, load_cohort
from pattern_oriented_abc_pilot import (
    SEED, PATTERNS, HOLDOUT, N_BOOT, BACKGROUNDS, NOISE_RANGE, WARP_RANGE,
    rankz, get_design, stats_from_y, bootstrap_observed, bootstrap_heldout,
    site_response, group_exact_surfaces,
)
from pattern_oriented_archive132 import FILES, DESIGN, archived_full_catalog

OUT=ROOT/"research/results/macro_directional_pom_20261031"
N_MODEL_REPS=64
N_RECOVERY_REPS=8
MIN_OBS_SIGN_CONF=.90
TERNARY_FLOOR=.05
PENALTY=.25  # Each additional mismatching category contributes factor .25.
STATES=(-1,0,1)
FIRST_FOUR=(0,1,2,3)
HIGH_S=5
LOW_S=4


def observational_categories(bootstrap,threshold=None):
    """Return joint categorical states (nb, 6), low-S is three-valued."""
    b=np.asarray(bootstrap,float)
    if b.ndim!=2 or b.shape[1]!=len(PATTERNS) or not np.isfinite(b).all():
        raise ValueError("Expected finite six-component bootstrap")
    if threshold is None:
        lower,upper=np.quantile(b[:,LOW_S],[.025,.975])
        threshold=max(TERNARY_FLOOR,float((upper-lower)/2))
    if not np.isfinite(threshold) or threshold<=0:
        raise ValueError("Nonpositive near-zero band")
    state=np.where(b<0,-1,1).astype(np.int8)
    low=b[:,LOW_S]
    state[:,LOW_S]=np.where(low < -threshold,-1,np.where(low>threshold,1,0))
    return state,float(threshold)


def selected_directional_constraints(observed_states):
    """Only confidently directed binary terms enter; low-S ternary always."""
    q=np.asarray(observed_states)
    if q.ndim!=2 or q.shape[1]!=len(PATTERNS):
        raise ValueError("Invalid observed joint-state samples")
    indices=[i for i in FIRST_FOUR+(HIGH_S,) if
             max(float(np.mean(q[:,i]==-1)),float(np.mean(q[:,i]==1)))>=MIN_OBS_SIGN_CONF]
    return tuple(indices+[LOW_S])


def probability_rows(states, indices):
    """For each pattern, full multinomial probability over -1/0/+1."""
    arr=np.asarray(states)
    out=np.asarray([[(arr[:,i]==j).mean() for j in STATES] for i in indices],float)
    return out


def deterministic_signature(y,design,delta):
    vec=stats_from_y(y,design)
    state,_=observational_categories(vec.reshape(1,-1),threshold=delta)
    return state[0],vec


def nuisance_draws(d,number,seed):
    rng=np.random.default_rng(seed)
    group,_=pd.factorize(d.spatial_block,sort=True)
    draws=[]
    for j in range(number):
        warp_o=float(rng.uniform(*WARP_RANGE))
        warp_s=float(rng.uniform(*WARP_RANGE))
        noise=float(rng.uniform(*NOISE_RANGE))
        site_error=rng.normal(size=len(d))
        block_error=rng.normal(size=int(group.max()+1))
        # Shared realization across every mechanism prevents random ranking of
        # source-identical surfaces.
        e=noise*(site_error+.25*block_error[group])
        draws.append((warp_o,warp_s,e))
    return draws


def simulate_response_states(d,bg,design,surface,delta,nuisance):
    outcomes=np.empty((len(nuisance),len(PATTERNS)),dtype=np.int8)
    for j,(warp_o,warp_s,e) in enumerate(nuisance):
        f=site_response(d,bg,surface,warps=(warp_o,warp_s))
        y=rankz(np.log(f))+e
        vec=stats_from_y(y,design)
        states,_=observational_categories(vec[None,:],threshold=delta)
        outcomes[j]=states[0]
    return outcomes


def agreement(obs_states,sim_states,selected):
    """Marginal P·Q plus joint no-independence assumption score."""
    obs=np.asarray(obs_states,dtype=np.int8)
    sim=np.asarray(sim_states,dtype=np.int8)
    sel=np.asarray(selected,dtype=int)
    if obs.shape[1]!=len(PATTERNS) or sim.shape[1]!=len(PATTERNS) or len(sel)==0:
        raise ValueError("Improper sign vector")
    # Paired under empirical JOINT observation and simulator pattern draws.
    mismatch=(obs[:,None,sel]!=sim[None,:,sel]).sum(axis=-1)
    if mismatch.ndim!=2 or mismatch.shape!=(len(obs),len(sim)):
        raise AssertionError("Mismatch tensor shape")
    joint_soft=float(np.mean(PENALTY**mismatch))
    joint_exact=float(np.mean(mismatch==0))
    op=probability_rows(obs,sel)
    sp=probability_rows(sim,sel)
    # A composite score only: NOT a marginal-likelihood factorization.
    dot=np.sum(op*sp,axis=1)
    composite=float(np.prod(dot))
    if not 0<=joint_exact<=1 or not 0<=joint_soft<=1 or not 0<=composite<=1:
        raise AssertionError("Invalid categorical agreement")
    return joint_soft,joint_exact,composite


def rank_direction_groups(d,bg,all_surfaces,eqgroups,observed,boot,nreps=N_MODEL_REPS,
                          nrecovery=N_RECOVERY_REPS):
    if nreps<5 or nrecovery<2:
        raise ValueError("Too few fixed noise diagnostics")
    design=get_design(d,bg)
    obs_states,delta=observational_categories(boot)
    selected=selected_directional_constraints(obs_states)
    if LOW_S not in selected:raise AssertionError("Lost near-zero focal condition")
    nuisance=nuisance_draws(d,nreps,seed=SEED+({"uniform":0,"target_group":10000}[bg]))
    independent=nuisance_draws(d,nrecovery*len(eqgroups),seed=SEED+20260+
                               ({"uniform":0,"target_group":10000}[bg]))
    keys=sorted(eqgroups)
    class_prob={}
    class_state={}
    case_to_group={}
    rows=[]
    all_case_labels=sorted(all_surfaces)
    for cls in keys:
        members=sorted(eqgroups[cls])
        if not members:raise ValueError("Empty class")
        name=members[0]
        grid=all_surfaces[name]
        deterministic,stats=deterministic_signature(site_response(d,bg,grid),
                                                    design,delta)
        sims=simulate_response_states(d,bg,design,grid,delta,nuisance)
        score,exact,comp=agreement(obs_states,sims,selected)
        class_prob[cls]=probability_rows(sims,range(len(PATTERNS)))
        class_state[cls]=deterministic
        for case in members:
            case_to_group[case]=cls
            row=dict(background=bg,case=case,exact_source_group=cls,
                     n_exact_cases=len(members),
                     joint_direction_soft_score=score,
                     strict_joint_matching_probability=exact,
                     marginal_composite_agreement=comp,
                     delta_near_zero=delta,n_selected_binary=len(selected)-1,
                     n_selected_total=len(selected),
                     deterministic_all_six_matches=int(
                         np.sum(deterministic==observational_categories(observed[None,:],
                                                                       threshold=delta)[0])))
            for i,p in enumerate(PATTERNS):
                obs_p=probability_rows(obs_states,[i])[0]
                sim_p=class_prob[cls][i]
                row["sim_"+p]=float(stats[i])
                row["det_state_"+p]=int(deterministic[i])
                for j,state_name in enumerate(("neg","zero","pos")):
                    row["obs_"+p+"_"+state_name]=float(obs_p[j])
                    row["sim_"+p+"_"+state_name]=float(sim_p[j])
            rows.append(row)
    if len(rows)!=len(all_case_labels):
        raise AssertionError("Missing case in directional ranking")
    # Coarse groups are the same categorical signature, not proof of
    # indistinguishable parameter dynamics.
    signature_to_groups=defaultdict(list)
    for cls,signature in class_state.items():
        sig=",".join(str(int(x)) for x in signature)
        signature_to_groups[sig].append(cls)
    key_by_sig={}
    for sign,classes in signature_to_groups.items():
        key_by_sig[sign]=min(classes)
    sig_rows=[]
    for sign,classes in signature_to_groups.items():
        result=[r for cls in classes for r in rows
                if r["case"]==min(eqgroups[cls])]
        sig_rows.append(dict(background=bg,directional_signature=sign,
                             direction_group=key_by_sig[sign],
                             n_exact_source_groups=len(classes),
                             n_case_labels=sum(len(eqgroups[x]) for x in classes),
                             representative_case=min(min(eqgroups[x]) for x in classes),
                             mean_joint_soft=float(np.mean([r["joint_direction_soft_score"] for r in result])),
                             maximum_joint_soft=float(max(r["joint_direction_soft_score"] for r in result)),
                             mean_exact_joint=float(np.mean([r["strict_joint_matching_probability"] for r in result])),
                             scenario_members=";".join(sorted(sum((eqgroups[x] for x in classes),[])))))
    table=pd.DataFrame(rows)
    sigtable=pd.DataFrame(sig_rows).sort_values(
        ["mean_joint_soft","direction_group"],ascending=[False,True]).reset_index(drop=True)
    # Independent pseudo targets validate whether a categorical model can
    # be returned to its *direction* group when its exact source is hidden.
    names=sorted(class_prob)
    signature_by_group={}
    for sign,classes in signature_to_groups.items():
        for cls in classes:signature_by_group[cls]=key_by_sig[sign]
    # Equal-weight priors over signatures rather than group multiplicities.
    classes_by_direction=defaultdict(list)
    for c in names:classes_by_direction[signature_by_group[c]].append(c)
    direction_prob={}
    for label,classes in classes_by_direction.items():
        direction_prob[label]=np.mean([class_prob[c] for c in classes],axis=0)
    rec=[]
    idx=0
    use=np.asarray(selected,dtype=int)
    for cls in names:
        for rep in range(nrecovery):
            q=simulate_response_states(d,bg,design,all_surfaces[min(eqgroups[cls])],
                                       delta,[independent[idx]])[0]
            idx+=1
            # Reference has no sample from this validation noise seed.
            ranked=[]
            for sig,probs in direction_prob.items():
                ll=0.
                for term in use:
                    j=int(q[term])+1
                    ll+=math.log(max(float(probs[term,j]),1e-8))
                ranked.append((ll,sig))
            pred=sorted(ranked,key=lambda r:(-r[0],r[1]))[0][1]
            rec.append(dict(background=bg,source_group=cls,
                            true_direction_group=signature_by_group[cls],
                            predicted_direction_group=pred,
                            directional_group_recovered=bool(pred==signature_by_group[cls]),
                            replicate=rep))
    obs_rows=[]
    obs_low,obs_high=np.quantile(boot,[.025,.975],axis=0)
    for i,p in enumerate(PATTERNS):
        pr=probability_rows(obs_states,[i])[0]
        obs_rows.append(dict(background=bg,pattern=p,observed_estimate=float(observed[i]),
                             bootstrap_low=float(obs_low[i]),bootstrap_high=float(obs_high[i]),
                             p_negative_bootstrap=float(pr[0]),p_near_zero_bootstrap=float(pr[1]),
                             p_positive_bootstrap=float(pr[2]),
                             robust_direction_selected=bool(i in selected and i!=LOW_S),
                             near_zero_threshold=delta if i==LOW_S else np.nan))
    group_overview=dict(background=bg,n_cases=len(rows),n_exact_source_groups=len(eqgroups),
                        n_direction_signatures=len(sigtable),
                        n_selected_binary=len(selected)-1,
                        near_zero_delta=delta,
                        selected_pattern_names=";".join(PATTERNS[i] for i in selected),
                        equally_likely_independent_chance_reference=1/(3*(2**(len(selected)-1))),
                        best_direction_group=sigtable.iloc[0].direction_group,
                        best_mean_soft_match=float(sigtable.iloc[0].mean_joint_soft),
                        best_raw_case=table.sort_values(
                            ["joint_direction_soft_score","case"],ascending=[False,True]).iloc[0].case,
                        model_group_recovery=float(pd.DataFrame(rec).directional_group_recovered.mean()),
                        status="DIRECTION_ONLY_CONDITIONAL_NOT_ECOLOGICAL_POSTERIOR")
    return (table,sigtable,pd.DataFrame(obs_rows),pd.DataFrame(rec),group_overview,
            class_prob,eqgroups)


def audit_heldout(d,bg,design,candidates,surfaces):
    obs=stats_from_y(d.strong_rate,design,holdout=True)[1]
    holdboot=bootstrap_heldout(d.strong_rate,design,d.spatial_block,n_boot=N_BOOT)
    lo,hi=np.quantile(holdboot,[.025,.975],axis=0)
    records=[]
    for name in candidates:
        vals=stats_from_y(site_response(d,bg,surfaces[name]),design,holdout=True)[1]
        for i,p in enumerate(HOLDOUT):
            records.append(dict(background=bg,case=name,pattern=p,
                                observed=float(obs[i]),model=float(vals[i]),
                                observed_low=float(lo[i]),observed_high=float(hi[i]),
                                within_observed95=bool(lo[i]<=vals[i]<=hi[i])))
    return pd.DataFrame(records)


def run(nreps=N_MODEL_REPS,nrecovery=N_RECOVERY_REPS,out=OUT):
    out.mkdir(parents=True,exist_ok=True)
    d=load_cohort(pd.read_csv(SITE),pd.read_csv(VISITS),expected=4248)
    if int(d.n.sum())!=63180 or int(d.V.sum())!=506:
        raise AssertionError("NAAMP sample changed")
    surfaces,metadata=archived_full_catalog(
        [pd.read_csv(p) for p in FILES],pd.read_csv(DESIGN))
    labels,group_hash=group_exact_surfaces(surfaces)
    eq={}
    for h,members in group_hash.items():
        eq[min(members)]=sorted(members)
    scores=[];directions=[];observations=[];recoveries=[];summary=[];holdouts=[]
    for bg in BACKGROUNDS:
        design=get_design(d,bg)
        vec=stats_from_y(d.strong_rate,design)
        # Check the original, fixed real-site POM unadjusted estimator.
        from pattern_oriented_abc_pilot import compare_frozen_macro
        compare_frozen_macro(vec,bg)
        boot,cov,inv,diagnostics=bootstrap_observed(
            d.strong_rate,design,d.spatial_block,n_boot=N_BOOT,seed=SEED)
        parts=rank_direction_groups(d,bg,surfaces,eq,vec,boot,nreps,nrecovery)
        ranked,sig,obs,rec,info,q,group=parts
        scores.append(ranked);directions.append(sig);observations.append(obs)
        recoveries.append(rec);summary.append(info)
        top_sign=sig.iloc[0]
        name=top_sign.representative_case
        holdouts.append(audit_heldout(d,bg,design,[name],surfaces))
        print("DIRECTIONAL",bg,"robust",info["selected_pattern_names"],
              "delta",info["near_zero_delta"],"groups",info["n_direction_signatures"],
              "top",info["best_direction_group"],
              "mean_score",info["best_mean_soft_match"],
              "recovery",info["model_group_recovery"],flush=True)
    tables=dict(case_scores=pd.concat(scores,ignore_index=True),
                directional_groups=pd.concat(directions,ignore_index=True),
                observed_sign_bootstrap=pd.concat(observations,ignore_index=True),
                recovery=pd.concat(recoveries,ignore_index=True),
                summary=pd.DataFrame(summary),
                unselected_pattern_diagnostics=pd.concat(holdouts,ignore_index=True))
    for label,frame in tables.items():frame.to_csv(out/(label+".csv"),index=False)
    receipt=dict(status="DIRECTION_ONLY_POM_NOT_TRUE_BIOLOGICAL_MODEL_POSTERIOR",
                 n_cases=len(surfaces),n_original_sites=len(d),
                 n_completed_visits=int(d.n.sum()),spatial_block_bootstrap=N_BOOT,
                 n_model_replicates=nreps,n_independent_pseudo_recovery_reps=nrecovery,
                 model_perturbation="paired common simulated noise/warps, not field-calibrated",
                 robust_binary_cutoff=MIN_OBS_SIGN_CONF,
                 ternary_lowS_delta_rule="max(0.05, observed 95% bootstrap halfwidth)",
                 score="joint categorical exponential mismatch with factor 0.25 per mismatch",
                 chance="equal-probability independent categorical combinatorial benchmark, NOT a p-value",
                 sources={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
                          for p in [SITE,VISITS,DESIGN,*FILES]},
                 code_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                 limits=["Bootstrap sign frequencies are not probabilities of a field mechanism",
                         "Site suitability not local predator counts",
                         "Same NAAMP cohort previously explored",
                         "Simulated stochasticity is chosen and not measured",
                         "Direction groups are coarser than exact biological mechanisms",
                         "No rate priors or independent adult-call calibration"])
    (out/"receipt.json").write_text(json.dumps(receipt,indent=2,ensure_ascii=False)+"\n")
    print("DIRECTION SUMMARY\n"+tables["summary"].to_string(index=False),flush=True)
    print("OBSERVED SIGN FREQUENCY\n"+tables["observed_sign_bootstrap"].to_string(index=False),flush=True)
    print("TOP DIRECTION SIGNATURES\n"+tables["directional_groups"].groupby(
        "background").head(8).to_string(index=False),flush=True)
    print("TOP INDIVIDUAL CASES\n"+tables["case_scores"].sort_values(
        ["background","joint_direction_soft_score"],ascending=[True,False]).groupby(
        "background").head(10)[["background","case","exact_source_group",
                                "joint_direction_soft_score",
                                "strict_joint_matching_probability",
                                "marginal_composite_agreement"]].to_string(index=False),flush=True)
    print("UNSELECTED PATTERNS\n"+tables["unselected_pattern_diagnostics"].to_string(index=False),flush=True)
    return tables


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--run",action="store_true")
    p.add_argument("--model-reps",type=int,default=N_MODEL_REPS)
    p.add_argument("--recovery-reps",type=int,default=N_RECOVERY_REPS)
    a=p.parse_args()
    if not a.run:p.error("Explicit --run required")
    run(nreps=a.model_reps,nrecovery=a.recovery_reps)
