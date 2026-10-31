"""Direction-only audit of *actual rerun* 80-y process-rate scenarios.

Input comes from the separately SUCCESSFUL 8-draw, 24-structure GitHub Actions
artifact. The demographic process varied in the upstream run. This program
adds only explicitly hypothetical common site/rank observation noise; it does
not perform a new demographic draw or estimate a biological model posterior.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
import hashlib
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd

from select_macro_trophic_scenarios import ROOT, SITE, VISITS, LEVELS, load_cohort
from pattern_oriented_abc_pilot import (
    SEED, PATTERNS, BACKGROUNDS, N_BOOT,
    get_design, stats_from_y, compare_frozen_macro, bootstrap_observed,
    site_response,
)
from directional_pom_132 import (
    LOW_S, observational_categories,
)
from directional_pom_132 import (
    selected_directional_constraints, nuisance_draws, simulate_response_states,
    agreement, probability_rows
)

SOURCE=ROOT/"research/results/macro_pom_process_prior_20261031"
CELLS=SOURCE/"real_simulator_F_B_cells.csv.gz"
PATTERNS_CSV=SOURCE/"process_prior_predictive_patterns.csv"
DRAW=SOURCE/"hypothetical_process_rate_draws.csv"
OUT=ROOT/"research/results/macro_directional_process_rate_20261031"
REPS_PER_RATE=16
DRAW_COUNT=8
CASE_COUNT=24


def recover_grid(sub):
    axes=np.asarray([(v,s,o) for v in (0.,1.) for s in np.linspace(.25,2.,LEVELS)
                     for o in np.linspace(.25,2.,LEVELS)])
    g=sub.sort_values(["vegetation","S_source","D_source"])
    if len(g)!=len(axes) or not np.allclose(
            g[["vegetation","S_source","D_source"]].to_numpy(float),axes,
            rtol=0,atol=1e-9):
        raise ValueError("Stage-response source grid corrupt")
    f=g.F_B.to_numpy(float)
    if not np.isfinite(f).all() or (f<=0).any():
        raise ValueError("Invalid regenerated stage cohort")
    return f.reshape(2,LEVELS,LEVELS)


def evaluate_rate_direction(d,cells,model_meta,n_reps=REPS_PER_RATE):
    if len(cells)!=DRAW_COUNT*CASE_COUNT*2*LEVELS*LEVELS:
        raise ValueError("Incomplete real 8-draw demographic library")
    if len(model_meta)!=DRAW_COUNT*CASE_COUNT*len(BACKGROUNDS):
        raise ValueError("Incomplete source-backed model metadata")
    results=[];observed=[];overall=[];recovery=[]
    grid_map={(int(draw),int(case)):recover_grid(sub) for (draw,case),sub in
              cells.groupby(["draw","case"])}
    if len(grid_map)!=DRAW_COUNT*CASE_COUNT:
        raise AssertionError("Missing draw×case")
    for bg in BACKGROUNDS:
        design=get_design(d,bg)
        obsvec=stats_from_y(d.strong_rate,design)
        compare_frozen_macro(obsvec,bg)
        boot,cov,inv,diag=bootstrap_observed(d.strong_rate,design,d.spatial_block,
                                               n_boot=N_BOOT)
        ostates,delta=observational_categories(boot)
        selected=selected_directional_constraints(ostates)
        point_state,_=observational_categories(obsvec[None,:],threshold=delta)
        nuisance=nuisance_draws(d,n_reps,SEED+40000+
                                (0 if bg=="uniform" else 10000))
        by_group=defaultdict(list);by_draw=defaultdict(list)
        for draw in range(DRAW_COUNT):
            for case in sorted(cells.case.unique()):
                desc=model_meta[(model_meta.background==bg)&
                                (model_meta.draw==draw)&
                                (model_meta.case==f"case_{int(case):03d}")]
                if len(desc)!=1:raise ValueError("Missing case/draw identity")
                identity=desc.iloc[0]
                group=str(identity.structural_group)
                grid=grid_map[(draw,int(case))]
                states=simulate_response_states(d,bg,design,grid,delta,nuisance)
                by_group[group].append(states)
                by_draw[(draw,group)].append(states)
                deterministic=stats_from_y(
                    site_response(d,bg,grid),
                    design)
                cat,_=observational_categories(deterministic[None,:],threshold=delta)
                row=dict(background=bg,draw=draw,case=int(case),structural_group=group,
                         deterministic_selected_matches=int(
                             np.sum(cat[0,list(selected)] ==
                                    point_state[0,list(selected)])),
                         selected_constraint_count=len(selected))
                for i,p in enumerate(PATTERNS):
                    row["model_"+p]=float(deterministic[i])
                    row["state_"+p]=int(cat[0,i])
                results.append(row)
        for i,p in enumerate(PATTERNS):
            probs=probability_rows(ostates,[i])[0]
            observed.append(dict(background=bg,pattern=p,observed=float(obsvec[i]),
                                 bootstrap_negative=float(probs[0]),
                                 bootstrap_zero=float(probs[1]),
                                 bootstrap_positive=float(probs[2]),
                                 selected=bool(i in selected),
                                 ternary_delta=delta if i==LOW_S else np.nan))
        trained_probs={}
        for group,frags in sorted(by_group.items()):
            states=np.concatenate(frags,axis=0)
            soft,strict,comp=agreement(ostates,states,selected)
            trained_probs[group]=probability_rows(states,range(len(PATTERNS)))
            overall.append(dict(background=bg,structural_group=group,
                                n_actual_rate_draws=DRAW_COUNT,
                                n_structural_edge_variants=len(frags)//DRAW_COUNT,
                                n_synthetic_observation_reps=len(states),
                                n_strong_direction_constraints=len(selected)-1,
                                delta_near_zero=delta,
                                selected_patterns=";".join(PATTERNS[i] for i in selected),
                                joint_direction_score=soft,
                                strict_joint_match_frequency=strict,
                                marginal_composite_agreement=comp,
                                chance_independent_reference=1/(3*2**(len(selected)-1)),
                                status="EXPLORATORY_REAL_DEMOGRAPHIC_DRAWS_NO_FIELD_RATE_PRIOR"))
        groupnames=sorted(trained_probs)
        # Leave whole true PROCESS-RATE draws out of the candidate reference.
        # Use one noise realization from the held-out source for each class.
        for held in range(DRAW_COUNT):
            train_q={}
            for grp in groupnames:
                others=[np.concatenate(by_draw[(other,grp)],axis=0)
                        for other in range(DRAW_COUNT) if other!=held]
                train_q[grp]=probability_rows(np.concatenate(others,axis=0),
                                             range(len(PATTERNS)))
            for true in groupnames:
                test=by_draw[(held,true)][0][0]
                choices=[]
                for grp in groupnames:
                    probs=train_q[grp];ll=0.
                    for idx in selected:
                        ll+=math.log(max(float(probs[idx,int(test[idx])+1]),1e-9))
                    choices.append((ll,grp))
                pred=sorted(choices,key=lambda z:(-z[0],z[1]))[0][1]
                recovery.append(dict(background=bg,heldout_rate_draw=held,
                                     true_group=true,predicted_group=pred,
                                     recovered=bool(pred==true)))
        groupscores=[r for r in overall if r["background"]==bg]
        leader=max(groupscores,key=lambda z:z["joint_direction_score"])
        for note in groupscores:
            note["best_within_background"]=bool(note["structural_group"]==leader["structural_group"])
        print("REAL_RATE_DIRECTIONAL",bg,"n_groups",len(groupscores),
              "selected",",".join(PATTERNS[i] for i in selected),
              "top",leader["structural_group"],"score",leader["joint_direction_score"],
              "strict",leader["strict_joint_match_frequency"],
              flush=True)
    r=pd.DataFrame(results);o=pd.DataFrame(observed);m=pd.DataFrame(overall);rec=pd.DataFrame(recovery)
    return dict(process_case_signs=r,observed_signs=o,structural_group_agreement=m,
                rate_draw_recovery=rec)


def run():
    OUT.mkdir(parents=True,exist_ok=True)
    d=load_cohort(pd.read_csv(SITE),pd.read_csv(VISITS),expected=4248)
    cells=pd.read_csv(CELLS)
    metadata=pd.read_csv(PATTERNS_CSV)
    prior=pd.read_csv(DRAW)
    if (len(prior)!=DRAW_COUNT or cells.draw.nunique()!=DRAW_COUNT or
        len(metadata)!=DRAW_COUNT*CASE_COUNT*2):
        raise ValueError("Missing actual process ensemble")
    if not all(x in cells for x in ("F_B","draw","case","vegetation","S_source","D_source")):
        raise ValueError("Missing demographic source fields")
    tables=evaluate_rate_direction(d,cells,metadata)
    rec=tables["rate_draw_recovery"]
    confusion=(rec.groupby(["background","true_group","predicted_group"])
               .size().rename("n").reset_index())
    confusion["n_true_group"]=confusion.groupby(
        ["background","true_group"]).n.transform("sum")
    confusion["fraction_of_true_group"]=confusion.n/confusion.n_true_group
    if int(confusion.n.sum())!=len(rec):raise AssertionError("Dropped heldout rate draws")
    tables["structural_rate_draw_confusion"]=confusion
    for name,frame in tables.items():frame.to_csv(OUT/(name+".csv"),index=False)
    receipt=dict(status="DIRECTIONAL_REANALYSIS_OF_EIGHT_ACTUAL_UNCALIBRATED_PROCESS_DRAWS",
                 original_run="https://github.com/zuizui0223/frogcs/actions/runs/41163370575",
                 no_new_process_rate_calibration=True,
                 per_case_actual_80_year_simulator_output=True,
                 only_stochasticity="hypothetical common observation rank noise/warps",
                 source_hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
                                for p in (SITE,VISITS,CELLS,PATTERNS_CSV,DRAW)},
                 outcome="category sign agreement, low-S ternary and leave-rate-draw-out recovery",
                 limitation="Not a biological scenario posterior or independent field verification",
                 script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    (OUT/"receipt.json").write_text(json.dumps(receipt,indent=2)+"\n")
    print("REAL RATE GROUP COMPARISON\n"+tables["structural_group_agreement"].sort_values(
        ["background","joint_direction_score"],ascending=[True,False]).to_string(index=False),flush=True)
    print("RECOVERY\n"+tables["rate_draw_recovery"].groupby(
        "background").recovered.agg(["mean","size"]).to_string(),flush=True)
    return tables


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--run",action="store_true")
    a=p.parse_args()
    if not a.run:p.error("Explicit --run required")
    run()
