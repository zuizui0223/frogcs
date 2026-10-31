"""Exploratory nonnegative cohort-to-call link for already selected scenarios.

No new model search.  Compare an imposed nonnegative log(F_B) coefficient to
the original unconstrained fit, additive and interacted environmental baselines.
All model coefficients are learned exclusively on outer training blocks.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

from select_macro_trophic_scenarios import (
    ROOT, OUT as PARENT, SITE, VISITS, SOURCES, NULLS, OUTER, SEED,
    load_cohort, scenario_surfaces, candidate_scores_at_sites, predictor_design,
    assign_folds, fit_predict, neglog
)
from diagnose_macro_scenario_information import replay_selected

OUT=PARENT/"monotone_link_sensitivity"
CHOICES=PARENT/"outer_chosen_scenarios.csv"
SCORES=PARENT/"outer_model_scores.csv"


def compute_fixed_choice_constrained(d,surfaces,choices,reps=999):
    folds=assign_folds(d,OUTER,seed=SEED)
    rows=[];labels=[]
    for background in ("uniform","target_group"):
        design=predictor_design(d,background,candidate_scores_at_sites(d,background,surfaces))
        for fold in range(OUTER):
            choice=choices[(choices.background==background)&(choices.outer_fold==fold)]
            if len(choice)!=1:raise ValueError("Missing or duplicate outer choice")
            choice=choice.iloc[0]
            train=folds!=fold;test=~train
            name=choice.selected_scenario
            x=design[name]
            k=d.k.to_numpy(float);n=d.n.to_numpy(float)
            pure,slope=fit_predict(x[train],k[train],n[train],x[test],
                                   return_mechanism_slope=True)
            bounded,beta=fit_predict(x[train],k[train],n[train],x[test],
                                     return_mechanism_slope=True,
                                     nonnegative_mechanism=True)
            if beta<-1e-9:raise AssertionError("Constrained model has negative slope")
            environment={}
            for null in NULLS:
                xx=design[null]
                environment[null]=fit_predict(xx[train],k[train],n[train],xx[test])
            if slope<0:
                if beta>2e-6:
                    raise AssertionError("Negative free slope was not zeroed at positive boundary")
                if np.max(np.abs(bounded-environment["env_additive"]))>3e-5:
                    raise AssertionError("Zero-slope link does not reproduce environment additive")
            labels.append(dict(background=background,outer_fold=fold,scenario=name,
                               selected_null=choice.selected_null,
                               unconstrained_standardized_slope=float(slope),
                               nonnegative_standardized_slope=float(beta),
                               coefficient_at_boundary=bool(beta<=2e-6),
                               train_sites=int(train.sum()),test_sites=int(test.sum())))
            for j,i in enumerate(np.flatnonzero(test)):
                rows.append(dict(background=background,outer_fold=fold,
                                 site=d.site.iloc[i],spatial_block=d.spatial_block.iloc[i],
                                 V=int(d.V.iloc[i]),n=int(d.n.iloc[i]),k=int(d.k.iloc[i]),
                                 scenario=name,selected_null=choice.selected_null,
                                 p_unconstrained=float(pure[j]),p_nonnegative=float(bounded[j]),
                                 p_selected_environment=float(environment[choice.selected_null][j]),
                                 p_env_additive=float(environment["env_additive"][j]),
                                 p_env_interactions=float(environment["env_interactions"][j])))
    data=pd.DataFrame(rows);slopes=pd.DataFrame(labels)
    if len(data)!=2*len(d) or data.duplicated(["background","site"]).any():
        raise AssertionError("Missing heldout site")
    scores=[]
    for bg in ("uniform","target_group"):
        base=data[data.background==bg]
        for subgroup,group in [("all",base),("V_positive",base[base.V==1]),("V_zero",base[base.V==0])]:
            if group.empty:raise AssertionError("Missing vegetation support")
            pred=group.p_nonnegative.to_numpy()
            k=group.k.to_numpy(float);n=group.n.to_numpy(float)
            model_loss=neglog(k,n,pred)
            scores.append(dict(background=bg,vegetation_support=subgroup,comparator="nonnegative_link",
                               n_sites=len(group),n_visits=int(n.sum()),
                               nll_per_visit=float(model_loss.sum()/n.sum()),
                               gain_null_minus_nonnegative=0.,gain_low_conditional=0.,gain_high_conditional=0.))
            for name in ("unconstrained","selected_environment","env_additive","env_interactions"):
                reference=group["p_"+name].to_numpy()
                null_loss=neglog(k,n,reference)
                pair=null_loss-model_loss
                blocks=group.assign(diff=pair).groupby("spatial_block")[["diff","n"]].sum().to_numpy(float)
                rng=np.random.default_rng(SEED)
                idx=rng.integers(0,len(blocks),size=(reps,len(blocks)))
                draws=blocks[idx].sum(axis=1)
                q=draws[:,0]/draws[:,1]
                scores.append(dict(background=bg,vegetation_support=subgroup,
                                   comparator=name,n_sites=len(group),n_visits=int(n.sum()),
                                   nll_per_visit=float(model_loss.sum()/n.sum()),
                                   gain_null_minus_nonnegative=float(pair.sum()/n.sum()),
                                   gain_low_conditional=float(np.quantile(q,.025)),
                                   gain_high_conditional=float(np.quantile(q,.975))))
    return data,slopes,pd.DataFrame(scores)


def run():
    OUT.mkdir(parents=True,exist_ok=True)
    d=load_cohort(pd.read_csv(SITE),pd.read_csv(VISITS),expected=4248)
    choices=pd.read_csv(CHOICES)
    frozen=pd.read_csv(SCORES)
    sources=[pd.read_csv(p) for p in SOURCES]
    surfaces,meta=scenario_surfaces(sources)
    data,slopes,summary=compute_fixed_choice_constrained(d,surfaces,choices)
    original=data.copy()
    for bg in ("uniform","target_group"):
        q=original[original.background==bg]
        nll=float(neglog(q.k,q.n,q.p_unconstrained).sum()/q.n.sum())
        prev=frozen[(frozen.background==bg)&(frozen.model=="selected_mechanism")].iloc[0]
        if not np.isclose(nll,prev.nll_per_visit,rtol=0,atol=1e-9):
            raise AssertionError("Unconstrained baseline has changed")
    slopes.to_csv(OUT/"selected_fold_link_sign_sensitivity.csv",index=False)
    summary.to_csv(OUT/"nonnegative_link_heldout_scores.csv",index=False)
    data.to_csv(OUT/"nonnegative_link_heldout_sites.csv.gz",index=False,
                compression={"method":"gzip","mtime":0})
    receipt=dict(status="POST_SELECTION_MONOTONICITY_ASSUMPTION_ONLY",
                 sites=len(d),surveys=int(d.n.sum()),cohort_model_source="F_B at season start",
                 fold_choices_unchanged=True,scenario_refit=False,environment_only_nulls_unchanged=True,
                 interpretation="Nonnegative log(F_B) logit slope is imposed, not measured. A boundary zero removes mechanistic signal.",
                 limits=["No independent adult calling calibration","F_B not stage-specific adult male counts",
                         "Post hoc check on previously studied NAAMP data","No new scenario winner search"],
                 source_hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
                                for p in [SITE,VISITS,CHOICES,SCORES]+SOURCES},
                 script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    (OUT/"receipt.json").write_text(json.dumps(receipt,indent=2)+"\n")
    print("FOLD LINK SIGN\n"+slopes.to_string(index=False))
    print("NONNEGATIVE LINK SCORES\n"+summary.to_string(index=False))
    return data,slopes,summary


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--run",action="store_true")
    opts=p.parse_args()
    if not opts.run:p.error("Explicit --run required")
    run()
