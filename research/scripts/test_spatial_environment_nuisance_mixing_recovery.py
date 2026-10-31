"""No-organism-movement environmental nuisance grid versus stable acoustic spatial mixing.

AUC<0.5 from source oriented score DOES NOT imply nonidentifiability:
its reverse complement may recover the two FIXED generators. We therefore
report both oriented and orientation-invariant AUC and the full predeclared
dynamic-environment and mixing cross-product. Environments are *nuisance*
mechanisms, not a fitted ecological posterior. Existing NAAMP sites and
yearly observation mask are fixed by original source.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from observed_neighbour_lag_dispersal_identifiability import (
    annual_panel,fixed_effect_association,auc_score,SEED
)
from recover_dispersal_vs_spatiotemporal_environment import (
    stable_synthetic_panel,MIXING
)

ENV_LEVELS=(0.,.12,.25,.38,.5)
MOVING=(.12,.25,.40,.65)
REPS=40
OBSERVED=.003714030411959474


def run(source_root,out,reps=REPS):
    sys.path.insert(0,str(source_root/"research/scripts"))
    from select_macro_trophic_scenarios import SITE,VISITS,load_cohort
    sites=pd.read_csv(SITE);visits=pd.read_csv(VISITS)
    d=load_cohort(sites,visits,expected=4248)
    if int(d.n.sum())!=63180:
        raise AssertionError("Original empirical source survey denominator changed")
    annual,panel,geom=annual_panel(d,visits,expect_sites=4248,expect_visits=63180)
    source=fixed_effect_association(panel)
    if (len(panel)!=17183 or panel.route.nunique()!=369 or
        not np.isclose(source["nearest_minus_farthest"],OBSERVED,atol=1e-9,rtol=0)):
        raise AssertionError("Real spatial lag source no longer reproduces previous empirical pattern")
    data=[]
    scenarios=( [("LOCAL_ENV_PERSISTENCE",0.,v) for v in ENV_LEVELS]+
                [("STABLE_NEIGHBOUR_MIXING",v,.38) for v in MOVING])
    for i in range(reps):
        for kind,mixing,env_value in scenarios:
            y=stable_synthetic_panel(annual,geom,seed=SEED+i,kind=kind,
                    mixing=mixing,environment_near=env_value)
            result=fixed_effect_association(panel,values=y)
            data.append(dict(kind=kind,mixing=mixing,environment_near=env_value,
                replicate=i,seed=SEED+i,
                nearest_minus_farthest=result["nearest_minus_farthest"],
                beta_nearest=result["beta_nearest_prior"],
                beta_farthest=result["beta_farthest_prior"],
                own_prev=result["beta_own_prior"]))
        if i%10==0:print("ENVIRONMENT_MIXING_NUISANCE_GRID_REPLICATE",i,flush=True)
    table=pd.DataFrame(data)
    if len(table)!=9*reps or table.duplicated(
        ["kind","mixing","environment_near","seed"]).any():
        raise AssertionError("Model recovery nuisance grid incomplete")
    rows=[]
    for a in MOVING:
        move=table[(table.kind=="STABLE_NEIGHBOUR_MIXING")&
                   (table.mixing==a)].nearest_minus_farthest.to_numpy(float)
        for b in ENV_LEVELS:
            null=table[(table.kind=="LOCAL_ENV_PERSISTENCE")&
                       (table.environment_near==b)].nearest_minus_farthest.to_numpy(float)
            if len(move)!=reps or len(null)!=reps:
                raise AssertionError("Missing environment-to-mixing model recovery pairs")
            auc=auc_score(null,move)
            sed=np.sqrt((move.var(ddof=1)+null.var(ddof=1))/2)
            rows.append(dict(mixing=a,environment_propagation=b,
                environment_null_mean=float(null.mean()),
                mixing_mean=float(move.mean()),
                oriented_AUC=float(auc),
                direction_free_AUC=float(max(auc,1-auc)),
                standardized_difference=float((move.mean()-null.mean())/sed),
                n_independent_sim_seed_per_model=reps,
                observed_near_far=source["nearest_minus_farthest"],
                observed_in_environment_95sim=bool(np.quantile(null,.025)<=OBSERVED<=np.quantile(null,.975)),
                observed_in_mixing_95sim=bool(np.quantile(move,.025)<=OBSERVED<=np.quantile(move,.975)),
                ecological_field_posterior=False))
    matrix=pd.DataFrame(rows)
    closest=(matrix.loc[
        matrix.groupby("mixing").direction_free_AUC.apply(
            lambda s: (s-.5).abs().idxmin()
        ).to_numpy()
    ].sort_values("mixing")).copy()
    # "closest" is a *post-simulation diagnostic of nuisance overlap*,
    # NOT a selected ecological mechanism, prior or inferential model.
    receipt=dict(
       status="SOURCE_NAAMP_ENVIRONMENT_NUISANCE_GRID_RECOVERY_COMPLETED",
       NAAMP_sites=4248,NAAMP_visits=63180,annual_eligible_site_years=17183,
       routes=369,source_near_far_coefficient=OBSERVED,
       simulated_environment_nuisance=list(ENV_LEVELS),
       simulated_stable_neighbour_mixing=list(MOVING),
       independent_RNG_repetitions_per_fixed_model=reps,
       all_synthetic_source_panels=len(table),
       dynamic_environment_has_no_animal_transfer=True,
       original_120day_80y_demography_fit_to_field=False,
       field_movement_mechanism_identification=False,
       no_post_result_parameter_reweighting=True,
       source_SHA256=dict(site=hashlib.sha256(SITE.read_bytes()).hexdigest(),
                          visits=hashlib.sha256(VISITS.read_bytes()).hexdigest()))
    out.mkdir(parents=True,exist_ok=True)
    table.to_csv(out/"environment_nuisance_mixing_source_draws.csv",index=False)
    matrix.to_csv(out/"all_predeclared_nuisance_x_mixing_aucs.csv",index=False)
    closest.to_csv(out/"post_simulation_closest_null_diagnostics.csv",index=False)
    (out/"receipt.json").write_text(json.dumps(receipt,indent=2,ensure_ascii=False)+"\n")
    print("NAAMP_ENVIRONMENT_NUISANCE_GRID_RESULT",json.dumps({
       "source_observed_near_far":OBSERVED,
       "per_mixing_closest_environment":closest[[
          "mixing","environment_propagation","oriented_AUC",
          "direction_free_AUC","standardized_difference",
          "observed_in_environment_95sim","observed_in_mixing_95sim"
       ]].to_dict("records")
    }),flush=True)
    return matrix,receipt

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--source-root",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    p.add_argument("--reps",type=int,default=REPS)
    a=p.parse_args()
    if a.reps<16:p.error("Insufficient independent synthetic source replications")
    run(a.source_root.resolve(),a.out,a.reps)
