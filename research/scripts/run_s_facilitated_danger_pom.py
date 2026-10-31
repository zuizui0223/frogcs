"""Post-result hypothesis test: S facilitates dragonfly-on-frog predation.

No original kernel is changed. Neutral source replay must succeed; sensitivity
values are invented structural contrasts, NOT empirical attack-rate estimates.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
import pandas as pd

from annual_s_facilitated_danger_20261031 import summarize_years
from run_macro_process_prior_predictive import scenario_set, anchor_values, as_surface
from select_macro_trophic_scenarios import ROOT, SITE, VISITS, SOURCES, load_cohort
from pattern_oriented_abc_pilot import (
    SEED, N_BOOT, BACKGROUNDS, PATTERNS, get_design, stats_from_y,
    compare_frozen_macro, bootstrap_observed, bootstrap_heldout,
    site_response, pattern_assessment
)
from directional_pom_132 import (
    observational_categories, selected_directional_constraints,
    nuisance_draws, simulate_response_states, agreement
)

OUT=ROOT/"research/results/macro_s_facilitated_danger_20261031"
DESIGN=ROOT/"research/results/literature_extension_20261029/design.csv"
CONDITIONS=(("neutral",0.,1.),("moderate",1.,.5),("strong",2.5,.15))


def simulate_conditional(grid,strength=0.,basal=1.):
    params=anchor_values()
    frames=[]
    for risk,g in grid.groupby("risk",sort=True):
        g=g.reset_index(drop=True);n=len(g)
        cases=[dict(community="FSD",roles=15,refuge_order="D",
                    vegetation=float(row.vegetation),f_arrival=20.,
                    s_arrival=float(row.sa),d_arrival=float(row.da),
                    attack_scale=.5,cue=0.,reverse=row.edge=="frog_reverse",
                    rho=.75) for row in g.itertuples(index=False)]
        controls=dict(cover_SF=1.,cover_DF=0.,cover_DS=0.,cover_SD=0.,
                      support_DF=0.,support_DS=0.,emerge_survival=0.,
                      emerge_exposure=0.,cue_SD=0.,edge_SD=np.ones(n),
                      edge_DS=np.ones(n))
        options=dict(stage_durations=np.column_stack([
                         np.full(n,45.),np.full(n,80.),g.dduration.to_numpy(float)]),
                     functional_response="litter",behavioral_refuge=bool(risk),
                     handling_s=g.hs.to_numpy(float),handling_d=g.hd.to_numpy(float),
                     s_growth=g.sg.to_numpy(float),d_growth=g.dg.to_numpy(float),
                     sd_size_mode="dynamic",pathway_controls=controls,
                     s_facilitated_danger_strength=strength,
                     background_danger_fraction=basal)
        source=np.column_stack([np.ones(n),g.S_source.to_numpy(float),
                                g.D_source.to_numpy(float)])
        cohort=summarize_years(cases,years=80,window=20,dt=.25,
                               source_cohorts=source,seasonal_options=options,
                               conversion=4.)
        frames.append(pd.concat([g,cohort],axis=1))
    result=pd.concat(frames,ignore_index=True)
    if len(result)!=len(grid):raise AssertionError("Missing source cells")
    return result


def check_baseline(real,original):
    base=pd.concat(original,ignore_index=True)
    key=["case","vegetation","S_source","D_source"]
    x=real.sort_values(key).reset_index(drop=True)
    y=base[base.case.isin(x.case.unique())].sort_values(key).reset_index(drop=True)
    if len(x)!=len(y) or not np.allclose(x[key].to_numpy(float),
                                         y[key].to_numpy(float),rtol=0,atol=1e-9):
        raise AssertionError("Source model grid mismatch")
    errors={}
    for name,tol in (("F_B",1e-8),("F_fraction",1e-8),("F_B_sd",1e-7)):
        d=float(np.abs(x[name].to_numpy(float)-y[name].to_numpy(float)).max())
        errors[name]=d
        if d>tol:raise AssertionError("Fork zero-strength replay mismatch "+name)
    return errors


def evaluate(d,scenarios):
    rows=[];observed=[]
    for bg in BACKGROUNDS:
        design=get_design(d,bg)
        obs,hold=stats_from_y(d.strong_rate,design,holdout=True)
        compare_frozen_macro(obs,bg)
        boot,_,inv,_=bootstrap_observed(d.strong_rate,design,d.spatial_block,n_boot=N_BOOT)
        heldboot=bootstrap_heldout(d.strong_rate,design,d.spatial_block,n_boot=N_BOOT)
        states,delta=observational_categories(boot)
        use=selected_directional_constraints(states)
        point,_=observational_categories(obs[None,:],threshold=delta)
        noise=nuisance_draws(d,32,SEED+(0 if bg=="uniform" else 10000))
        for name,strength,basal in CONDITIONS:
            grid=as_surface(scenarios[name])
            shape=pattern_assessment(d,bg,design,grid,obs,hold,inv,boot,
                                     holdout_draw=heldboot).set_index("case")
            for case,surface in sorted(grid.items()):
                actual=site_response(d,bg,surface)
                primary=stats_from_y(actual,design)
                symbol,_=observational_categories(primary[None,:],threshold=delta)
                stochastic=simulate_response_states(d,bg,design,surface,delta,noise)
                soft,exact,composite=agreement(states,stochastic,use)
                q=shape.loc[case]
                rows.append(dict(background=bg,hypothesis=name,case=case,
                                 strength=strength,basal=basal,
                                 direction_soft=soft,strict_joint_match=exact,
                                 composite_agreement=composite,
                                 n_selected_constraints=len(use),
                                 deterministic_selected_matches=int(np.sum(
                                     symbol[0,list(use)]==point[0,list(use)])),
                                 lowS_state=int(symbol[0,4]),
                                 modeled_lowS=float(primary[4]),
                                 observed_lowS=float(obs[4]),
                                 continuous_distance=float(q.distance_mahalanobis),
                                 continuous_patterns_within95=int(q.fitted_patterns_within_marginal_95),
                                 unselected_patterns_within95=int(q.heldout_patterns_within_95)))
        for i,p in enumerate(PATTERNS):
            prob=np.mean(states[:,i]==-1)
            observed.append(dict(background=bg,pattern=p,
                                 bootstrap_negative=float(prob),
                                 selected=bool(i in use),near_zero_band=delta if i==4 else np.nan))
    result=pd.DataFrame(rows)
    if len(result)!=len(CONDITIONS)*24*len(BACKGROUNDS):
        raise AssertionError("Incomplete hypothesis comparison")
    summaries=[]
    for bg in BACKGROUNDS:
        for name,_,_ in CONDITIONS:
            g=result[(result.background==bg)&(result.hypothesis==name)]
            top=g.sort_values(["direction_soft","case"],ascending=[False,True]).iloc[0]
            summaries.append(dict(background=bg,hypothesis=name,
                                  n_cases=len(g),top_case=top.case,
                                  top_joint_soft=float(top.direction_soft),
                                  top_strict=float(top.strict_joint_match),
                                  top_selected_directions=int(top.deterministic_selected_matches),
                                  n_selected_constraints=int(top.n_selected_constraints),
                                  lowS_state=int(top.lowS_state),
                                  n_full_selected_direction_cases=int(
                                      (g.deterministic_selected_matches==g.n_selected_constraints).sum()),
                                  best_quantitative_distance=float(g.continuous_distance.min()),
                                  best_quantitative_pattern_matches=int(
                                      g.continuous_patterns_within95.max()),
                                  best_unselected_matches=int(g.unselected_patterns_within95.max()),
                                  status="POST_HOC_HYPOTHETICAL_NOT_FIELD_CAUSAL"))
    return result,pd.DataFrame(summaries),pd.DataFrame(observed)


def run():
    OUT.mkdir(parents=True,exist_ok=True)
    allcases,_=scenario_set(pd.read_csv(DESIGN))
    orig=[pd.read_csv(path) for path in SOURCES]
    d=load_cohort(pd.read_csv(SITE),pd.read_csv(VISITS),expected=4248)
    results={}
    for name,strength,basal in CONDITIONS:
        print("RUN_HYPOTHETICAL_DANGER",name,strength,basal,flush=True)
        x=simulate_conditional(allcases,strength,basal)
        x["hypothesis"]=name
        results[name]=x
    replay=check_baseline(results["neutral"],orig)
    print("FROZEN_BASELINE_REPLAY",json.dumps(replay),flush=True)
    scores,summary,observation=evaluate(d,results)
    scores.to_csv(OUT/"hypothetical_directional_scores.csv",index=False)
    summary.to_csv(OUT/"hypothetical_directional_summary.csv",index=False)
    observation.to_csv(OUT/"observed_constraints.csv",index=False)
    pd.concat(results.values()).to_csv(OUT/"hypothetical_80year_F_B_cells.csv.gz",
                                       index=False,compression={"method":"gzip","mtime":0})
    receipt=dict(status="EXPLORATORY_S_FACILITATED_DANGER_NOT_RATE_CALIBRATED",
                 original_baseline_verified=True,baseline_replay_errors=replay,
                 candidate_settings=[list(z) for z in CONDITIONS],n_cases=24,sites=len(d),
                 original_kernel_unchanged=True,
                 method="Post-result hypothetical facilitation of D nymph attack on F tadpoles by S aquatic presence",
                 prior_calibrated=False,true_model_posterior=False,
                 sources={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
                          for p in [SITE,VISITS,DESIGN,*SOURCES]},
                 code_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    (OUT/"receipt.json").write_text(json.dumps(receipt,indent=2,ensure_ascii=False)+"\n")
    print("HYPOTHESIS_DIRECTION_SUMMARY\n"+summary.to_string(index=False),flush=True)
    return summary


if __name__=="__main__":
    a=argparse.ArgumentParser();a.add_argument("--run",action="store_true")
    args=a.parse_args()
    if not args.run:a.error("Explicit --run needed")
    run()
