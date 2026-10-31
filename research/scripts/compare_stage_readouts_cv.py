"""Post-result nested spatial CV of genuine seasonal completion vs pre-season B.

Original F_B prediction must exactly replay PR #146's earlier numeric results.
Post-hoc F_C and F_fraction comparisons are exploratory, not a replacement
for the fixed no-winner conclusion or independent adult acoustic calibration.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
import pandas as pd

from select_macro_trophic_scenarios import (
    ROOT, OUT as PARENT, SITE, VISITS, SOURCES, OUTER, LEVELS, NULLS, SEED,
    assign_folds, load_cohort, scenario_surfaces,
    fixed_nested_comparison, score_selected, observed_pattern_diagnostic,
    predictor_design, candidate_scores_at_sites, fit_predict
)
from recompute_macro_stage_readouts import OUT as STAGES, run as run_stages

OUT = PARENT / "stage_readouts"
ORIGINAL_SCORE = PARENT / "outer_model_scores.csv"


def grids(readouts, column, link):
    keys=("case","vegetation","S_source","D_source")
    reference=np.asarray([(v,s,o) for v in (0.,1.) for s in np.linspace(.25,2.,LEVELS)
                          for o in np.linspace(.25,2.,LEVELS)])
    surfaces={}
    for number,g in readouts.groupby("case"):
        g=g.sort_values(list(keys)).reset_index(drop=True)
        if len(g)!=len(reference) or g.duplicated(list(keys)).any():
            raise ValueError("Incomplete case readout grid")
        if not np.allclose(g[["vegetation","S_source","D_source"]].to_numpy(float),
                           reference,rtol=0,atol=1e-8):
            raise ValueError("Unexpected density axes")
        y=g[column].to_numpy(float)
        if not np.isfinite(y).all() or (y<0).any():
            raise ValueError("Invalid life-stage endpoint")
        if link=="log":
            # The shared candidate mapping takes log(grid); clipping is
            # only used if F_C is zero, and must be reported in the receipt.
            values=np.maximum(y,1e-10)
        elif link=="logit":
            if np.any(y>1+1e-10):
                raise ValueError("Survival fraction exceeds 1")
            z=np.clip(y,1e-6,1-1e-6)
            values=z/(1-z)  # shared log(candidate) then gives logit(y)
        else:raise ValueError("Unknown signal link")
        surfaces[f"case_{int(number):03d}"]=values.reshape(2,LEVELS,LEVELS)
    if len(surfaces)!=24:
        raise ValueError("Incomplete 24-case surfaces")
    return surfaces


def selected_link_slopes(d,surfaces,choice):
    rows=[]
    folds=assign_folds(d,OUTER,seed=SEED)
    for bg in ("uniform","target_group"):
        x=predictor_design(d,bg,candidate_scores_at_sites(d,bg,surfaces))
        for outer in range(OUTER):
            selection=choice[(choice.background==bg)&(choice.outer_fold==outer)]
            if len(selection)!=1:
                raise AssertionError("Missing fold model")
            record=selection.iloc[0]
            train=folds!=outer;test=~train
            observed=d.k.to_numpy(float);denom=d.n.to_numpy(float)
            p,coef=fit_predict(x[record.selected_scenario][train],observed[train],denom[train],
                                x[record.selected_scenario][test],
                                return_mechanism_slope=True)
            if len(p)!=int(test.sum()) or not np.isfinite(coef):
                raise ValueError("Unidentifiable fitted stage readout slope")
            rows.append(dict(background=bg,outer_fold=outer,scenario=record.selected_scenario,
                             selected_null=record.selected_null,link_coefficient=float(coef),
                             link_negative=bool(coef<0),test_sites=int(test.sum())))
    return pd.DataFrame(rows)


def comparison(readouts,d,original_summary):
    folders=[];all_scores=[];all_gains=[];all_choices=[];all_patterns=[];all_slopes=[];summary=[]
    for name,col,link in (("preseason_B","F_B","log"),
                          ("season_completed_C","F_C","log"),
                          ("aquatic_survival_fraction","F_fraction","logit")):
        s=grids(readouts,col,link)
        folds=assign_folds(d,OUTER,seed=SEED)
        pred,inner,choice=fixed_nested_comparison(d,s,outer_folds=folds)
        scores,gains=score_selected(pred,choice)
        effects=observed_pattern_diagnostic(d,pred,choice)
        slopes=selected_link_slopes(d,s,choice)
        if name=="preseason_B":
            # Replay the authoritative original NLL across all 4 columns.
            for row in scores.itertuples(index=False):
                old=original_summary[(original_summary.background==row.background)&
                                     (original_summary.model==row.model)]
                if len(old)!=1:
                    raise AssertionError("Missing original NLL comparator")
                if not np.isclose(row.nll_per_visit,float(old.nll_per_visit.iloc[0]),
                                  atol=1e-9,rtol=0):
                    raise AssertionError(f"F_B original CV replay mismatch: {row.background}, {row.model}")
        for frame in (pred,inner,choice,scores,gains,effects,slopes):
            frame.insert(0,"readout",name)
        folder=dict(readout=name,observations=pred,inner_scores=inner,choices=choice,
                    scores=scores,gains=gains,effects=effects,slopes=slopes)
        folders.append(folder)
        all_scores.append(scores);all_gains.append(gains);all_choices.append(choice)
        all_patterns.append(effects);all_slopes.append(slopes)
        for bg in ("uniform","target_group"):
            q=scores[scores.background==bg].set_index("model")
            m=float(q.loc["selected_mechanism","nll_per_visit"])
            n_min=min(float(q.loc[x,"nll_per_visit"]) for x in NULLS)
            relevant=gains[(gains.background==bg)&(gains.reference=="env_additive")]
            other=gains[(gains.background==bg)&(gains.reference=="env_interactions")]
            strongest_gain=n_min-m
            # Paired interval must have positive lower bound against BOTH nulls.
            all_positive=bool(relevant.gain_low_conditional.iloc[0]>0 and
                              other.gain_low_conditional.iloc[0]>0)
            e=effects[(effects.background==bg)].set_index("series")
            observed=e.loc["observed"];predicted=e.loc["selected_mechanism"]
            summary.append(dict(readout=name,background=bg,
                                nll_selected=m,nll_better_env=n_min,
                                gain_vs_better_env=strongest_gain,
                                lower_bound_above_zero_both_nulls=all_positive,
                                OV_observed=float(observed.OV),
                                OV_predicted=float(predicted.OV),
                                OS_observed=float(observed.OS),
                                OS_predicted=float(predicted.OS),
                                negative_slopes=int(slopes[(slopes.background==bg)].link_negative.sum()),
                                case84_folds=int(((choice.background==bg)&
                                                  (choice.selected_scenario=="case_084")).sum())))
        print("READOUT CV",name,"DONE",flush=True)
    return folders,dict(scores=pd.concat(all_scores,ignore_index=True),
                        gains=pd.concat(all_gains,ignore_index=True),
                        choices=pd.concat(all_choices,ignore_index=True),
                        pattern=pd.concat(all_patterns,ignore_index=True),
                        slopes=pd.concat(all_slopes,ignore_index=True),
                        overview=pd.DataFrame(summary))


def run():
    OUT.mkdir(parents=True,exist_ok=True)
    # Recompute the model's actual seasonal completion, with a source replay gate.
    cells,bycase,source_receipt=run_stages()
    d=load_cohort(pd.read_csv(SITE),pd.read_csv(VISITS),expected=4248)
    original=pd.read_csv(ORIGINAL_SCORE)
    folders,data=comparison(cells,d,original)
    for name,frame in data.items():
        frame.to_csv(OUT/(name+".csv"),index=False)
    for part in folders:
        label=part["readout"]
        part["observations"].to_csv(OUT/(label+"_outer_predictions.csv.gz"),index=False,
                                     compression={"method":"gzip","mtime":0})
        part["inner_scores"].to_csv(OUT/(label+"_inner_scores.csv"),index=False)
    receipt=dict(status="POST_HOC_STAGE_READOUT_NOT_CAUSAL_CALIBRATION",
                 n_sites=len(d),n_visits=int(d.n.sum()),n_scenarios=24,
                 readouts=["preseason_B","season_completed_C","aquatic_survival_fraction"],
                 expected_original_NLL_replayed=True,
                 original_annual_source_replayed=source_receipt["original_80year_surfaces_replayed_exactly"],
                 original_annual_max_errors=source_receipt["source_error_max"],
                 nested_CV="Same 5 outer 3 inner spatial blocked folds, heldout strong call per-visit binomial NLL",
                 model_claims=["F_C is model seasonal completion, not measured calling adult males",
                               "F_fraction is synthetic aquatic survival, not mature census",
                               "No temporal lag determined by stationary last-20-year averages",
                               "No external stage-call conversion; mapping suitability is not density",
                               "New outcomes post hoc; only preregistered no-winner results are authoritative"],
                 input_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
                               for p in [SITE,VISITS,ORIGINAL_SCORE]+SOURCES},
                 code_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    (OUT/"stage_readout_cv_receipt.json").write_text(json.dumps(receipt,indent=2)+"\n")
    print("STAGE READOUT SELECTED COMPARISON\n"+data["overview"].to_string(index=False),flush=True)
    print("STAGE READOUT GAINS\n"+data["gains"].to_string(index=False),flush=True)
    print("STAGE READOUT CHOICES\n"+data["choices"].to_string(index=False),flush=True)
    return data,receipt


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--run",action="store_true")
    args=p.parse_args()
    if not args.run:p.error("Explicit --run needed")
    run()
