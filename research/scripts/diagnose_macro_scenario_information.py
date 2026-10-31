"""Post-result audit of why fixed frog trophic mechanisms fail macro prediction.

Not an additional winner search. Replays the ten PREVIOUSLY selected outer-fold
candidates and evaluates structural information, link sign and V=0/1 support.
No demographic parameter is fitted or modified.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
import pandas as pd

from select_macro_trophic_scenarios import (
    ROOT, OUT as PARENT, SITE, VISITS, SOURCES, SEED, OUTER, NULLS,
    rank_standardize, load_cohort, scenario_surfaces, candidate_scores_at_sites,
    predictor_design, assign_folds, fit_predict, neglog,
)

OUT = PARENT / "information_diagnostic"
BACKGROUNDS = ("uniform", "target_group")
METADATA = PARENT / "scenario_metadata.json"
CHOICES = PARENT / "outer_chosen_scenarios.csv"
SCORES = PARENT / "outer_model_scores.csv"


def fraction_independent(signal, design):
    """Residual variation after ordinary least-squares projection (not score)."""
    z=np.asarray(signal,float)
    x=np.asarray(design,float)
    if len(z)!=len(x) or len(z)<2 or not np.isfinite(z).all() or not np.isfinite(x).all():
        raise ValueError("Invalid information audit inputs")
    sd=z.std()
    if sd<=1e-13:
        return 0.0
    xx=np.column_stack([np.ones(len(x)),x])
    coef=np.linalg.lstsq(xx,z,rcond=1e-10)[0]
    residual=z-xx@coef
    fraction=float((residual@residual)/((z-z.mean())@(z-z.mean())))
    if fraction<-1e-9 or fraction>1+1e-8:
        raise AssertionError("OLS signal residual outside variance bounds")
    return max(0.,min(1.,fraction))


def candidate_information(d,surfaces):
    rows=[]
    for bg in BACKGROUNDS:
        source=candidate_scores_at_sites(d,bg,surfaces)
        additive=predictor_design(d,bg,{})["env_additive"]
        interacted=predictor_design(d,bg,{})["env_interactions"]
        for name, feature in source.items():
            total=float(np.std(feature))
            frac_a=fraction_independent(feature,additive)
            frac_i=fraction_independent(feature,interacted)
            rows.append(dict(background=bg,scenario=name,n_sites=len(d),
                             log_f_sd=total,frac_not_explained_by_additive=frac_a,
                             frac_not_explained_by_interactions=frac_i,
                             incremental_sd_beyond_additive=total*np.sqrt(frac_a),
                             incremental_sd_beyond_interactions=total*np.sqrt(frac_i)))
    return pd.DataFrame(rows)


def reversals_independent(surfaces, metadata):
    groups={}
    for k,v in metadata.items():
        ctx=(v["context"],v["family"],bool(v["risk"]))
        groups.setdefault(ctx,{})[v["edge"]]=k
    rows=[]
    for (ctx,family,risk),edges in sorted(groups.items()):
        if set(edges)!={"dynamic","frog_reverse"}:
            raise ValueError("Incomplete counterfactual pair")
        before=surfaces[edges["dynamic"]]
        after=surfaces[edges["frog_reverse"]]
        if before.shape!=after.shape:
            raise ValueError("Unmatched source grid")
        delta=after-before
        rows.append(dict(context=ctx,family=family,risk=risk,off=edges["dynamic"],
                         on=edges["frog_reverse"],grid_cells=before.size,
                         exactly_equal_cells=int(np.sum(delta==0)),
                         n_changed_cells_gt_1e_10=int(np.sum(np.abs(delta)>1e-10)),
                         max_abs_delta_F_B=float(np.abs(delta).max()),
                         mean_abs_delta_F_B=float(np.abs(delta).mean()),
                         mean_rel_abs_delta_F_B=float(np.mean(np.abs(delta)/before))))
    if len(rows)!=12:
        raise ValueError("Wrong number of reverse pairs")
    return pd.DataFrame(rows)


def replay_selected(d,surfaces,choices,expected_scores=None):
    """Replay the frozen outer choices; NEVER select based on outer calls."""
    if choices.duplicated(["background","outer_fold"]).any() or len(choices)!=OUTER*2:
        raise ValueError("Expected one selected scenario per bg/fold")
    fold=assign_folds(d,OUTER,seed=SEED)
    predictions=[];slopes=[]
    for bg in BACKGROUNDS:
        design=predictor_design(d,bg,candidate_scores_at_sites(d,bg,surfaces))
        for outer in range(OUTER):
            choice=choices[(choices.background==bg)&(choices.outer_fold==outer)].iloc[0]
            mechanism=choice.selected_scenario
            if mechanism not in surfaces or choice.selected_null not in NULLS:
                raise ValueError("Unrecognized selected model")
            train=fold!=outer;test=fold==outer
            if (int(test.sum())!=choice.n_test_sites or
                int(d.n[test].sum())!=choice.n_test_visits or
                int(d.V[test].sum())!=choice.test_vegetated):
                raise ValueError("Outer spatial folds changed or support mismatch")
            x=design[mechanism]
            k=d.k.to_numpy(float);n=d.n.to_numpy(float)
            candidate,coef=fit_predict(x[train],k[train],n[train],x[test],
                                        return_mechanism_slope=True)
            slopes.append(dict(background=bg,outer_fold=outer,scenario=mechanism,
                               selected_null=choice.selected_null,training_sites=int(train.sum()),
                               training_vegetated=int(d.V[train].sum()),
                               normalized_log_F_B_coefficient=coef,
                               sign="positive" if coef>0 else "negative" if coef<0 else "zero"))
            reference={}
            for model in NULLS:
                x0=design[model]
                reference[model]=fit_predict(x0[train],k[train],n[train],x0[test])
            for j,index in enumerate(np.flatnonzero(test)):
                row=dict(background=bg,outer_fold=outer,site=d.site.iloc[index],
                         spatial_block=d.spatial_block.iloc[index],V=int(d.V.iloc[index]),
                         k=int(d.k.iloc[index]),n=int(d.n.iloc[index]),
                         scenario=mechanism,selected_null=choice.selected_null,
                         p_scenario=float(candidate[j]))
                row.update({"p_"+model:float(reference[model][j]) for model in NULLS})
                row["p_selected_environment"]=row["p_"+choice.selected_null]
                predictions.append(row)
    p=pd.DataFrame(predictions)
    if len(p)!=2*len(d) or p.duplicated(["background","site"]).any():
        raise AssertionError("Missing/duplicate outer test sites")
    if expected_scores is not None:
        for bg in BACKGROUNDS:
            z=p[p.background==bg]
            for label,column in [("selected_mechanism","p_scenario"),
                                 ("selected_environment","p_selected_environment"),
                                 ("env_additive","p_env_additive"),
                                 ("env_interactions","p_env_interactions")]:
                loss=float(neglog(z.k,z.n,z[column]).sum()/z.n.sum())
                reference=expected_scores[(expected_scores.background==bg)&
                                           (expected_scores.model==label)].iloc[0]
                if not np.isclose(loss,reference.nll_per_visit,rtol=0,atol=1e-9):
                    raise AssertionError("Archived outer CV failed exact numerical replay")
    return p,pd.DataFrame(slopes)


def stratum_score(pred,reps=999):
    """Paired block bootstrap of V=0/1; conditioning on trained predictions."""
    all_rows=[];group_rows=[]
    for bg in BACKGROUNDS:
        sub=pred[pred.background==bg]
        for vegetation, group in [("all",sub),("V_positive",sub[sub.V==1]),("V_zero",sub[sub.V==0])]:
            if group.empty:raise ValueError("Empty vegetation support")
            for reference in ("p_selected_environment","p_env_additive","p_env_interactions"):
                loss_mech=neglog(group.k.to_numpy(float),group.n.to_numpy(float),
                                 group.p_scenario.to_numpy(float))
                loss_null=neglog(group.k.to_numpy(float),group.n.to_numpy(float),
                                 group[reference].to_numpy(float))
                gains=loss_null-loss_mech
                blocks=group.assign(diff=gains).groupby("spatial_block")[["diff","n"]].sum()
                mat=blocks.to_numpy(float)
                rng=np.random.default_rng(SEED)
                indices=rng.integers(0,len(mat),size=(reps,len(mat)))
                draws=mat[indices].sum(axis=1)
                valid=draws[:,1]>0
                if valid.sum()<min(900,int(.9*reps)):
                    raise ValueError("Spatial bootstrap V support insufficient")
                boots=draws[valid,0]/draws[valid,1]
                score=float(gains.sum()/group.n.sum())
                all_rows.append(dict(background=bg,vegetation_support=vegetation,
                                     reference=reference.replace("p_",""),
                                     n_sites=len(group),n_visits=int(group.n.sum()),
                                     n_spatial_blocks=blocks.shape[0],
                                     gain_null_minus_mechanism=score,
                                     gain_low_conditional=float(np.quantile(boots,.025)),
                                     gain_high_conditional=float(np.quantile(boots,.975)),
                                     valid_block_draws=int(valid.sum())))
            group_rows.append(dict(background=bg,vegetation_support=vegetation,
                                   sites=len(group),n_visits=int(group.n.sum()),
                                   n_spatial_blocks=group.spatial_block.nunique()))
    return pd.DataFrame(all_rows),pd.DataFrame(group_rows)


def run():
    OUT.mkdir(parents=True,exist_ok=True)
    d=load_cohort(pd.read_csv(SITE),pd.read_csv(VISITS),expected=4248)
    if int(d.n.sum())!=63180 or int(d.V.sum())!=506:
        raise AssertionError("Frozen 4,248-site cohort changed")
    surfaces,meta=scenario_surfaces([pd.read_csv(path) for path in SOURCES])
    archived=json.loads(METADATA.read_text())
    if archived!=meta:
        raise AssertionError("Frozen metadata mismatches source")
    choices=pd.read_csv(CHOICES)
    previous=pd.read_csv(SCORES)
    info=candidate_information(d,surfaces)
    reversals=reversals_independent(surfaces,meta)
    pred,slopes=replay_selected(d,surfaces,choices,previous)
    scores,support=stratum_score(pred)
    for name,frame in [("scenario_information",info),("reversal_surface_identity",reversals),
                       ("selected_fold_mechanism_slopes",slopes),
                       ("vegetation_stratified_heldout_scores",scores),
                       ("vegetation_support",support)]:
        frame.to_csv(OUT/(name+".csv"),index=False)
    pred.to_csv(OUT/"replayed_outer_site_predictions.csv.gz",index=False,
                compression={"method":"gzip","mtime":0})
    provenance=[SITE,VISITS,CHOICES,SCORES,METADATA]+SOURCES
    receipt=dict(status="POST_RESULT_DIAGNOSTIC_NO_NEW_WINNER_SEARCH",
                 prior_results_replayed_exactly=True,sites=len(d),surveys=int(d.n.sum()),
                 vegetated_sites=int(d.V.sum()),scenarios=len(surfaces),
                 diagnostic_only=["source signal after additive/full covariates",
                                  "slope of train-fitted log F_B observation feature",
                                  "out-of-fold V-positive vs V-zero scored prediction",
                                  "paired source surface identity for reversed edge"],
                 assumptions=["V positive denotes remotely detected flooded vegetation, not pond plant cover",
                              "suitability ranks not local predator counts",
                              "coefficient sign not independently calibrated maturation/recruitment",
                              "nested CV performed on previously studied NAAMP cohort",
                              "conditional block intervals do not refit link or SDMs"],
                 sources={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in provenance},
                 script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    (OUT/"receipt.json").write_text(json.dumps(receipt,indent=2)+"\n")
    print("MECHANISTIC COVARIATE INFORMATION\n"+info.to_string(index=False))
    print("SELECTED OBSERVATION SLOPES\n"+slopes.to_string(index=False))
    print("VEGETATION STRATIFIED SCORES\n"+scores.to_string(index=False))
    print("REVERSAL GRID IDENTIFIABILITY\n"+reversals.to_string(index=False))
    return dict(info=info,slopes=slopes,scores=scores,reversals=reversals)


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--run",action="store_true")
    args=p.parse_args()
    if not args.run:p.error("Explicit --run needed")
    run()
