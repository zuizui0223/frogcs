"""Recovery power of NAAMP acoustic spatial POM patterns under STABLE
near-neighbour mixing and an additional temporally persistent LOCAL
ENVIRONMENTAL null (NO migration).

The first pilot's strong 0.65 lagged-state coupling had total memory
0.5+0.65=1.15 and could amplify state autocorrelation; this source run
replaces that for inferential model-recovery assessment by
  z_t = .55 * [(1-m) z_(t-1,i) + m z_(t-1,nearest)] + forcing,
with m in a predeclared stable range 0.0, .12, .25, .40, .65.
This is an acoustic latent mixing counterfactual, not an original source
F/S/D population-conserving 80-year migration simulator.
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
   annual_panel, fixed_effect_association, auc_score, SEED
)

MIXING=(0.,.12,.25,.40,.65)
N_REPS=48
SOURCE_NEAR_FAR=.003714030411959474


def stable_synthetic_panel(annual,geometry,*,seed,kind,mixing):
    if kind not in ("SHARED_ROUTE_ENV","LOCAL_ENV_PERSISTENCE","STABLE_NEIGHBOUR_MIXING"):
        raise ValueError("Unknown numerical null or spatial-mixing alternative")
    if mixing not in MIXING:
        raise ValueError("Model source mixing fraction not prespecified")
    if kind!="STABLE_NEIGHBOUR_MIXING" and mixing!=0.:
        raise ValueError("Environment-only null cannot be assigned organism mixing")
    g=geometry.drop_duplicates("site").reset_index(drop=True)
    n=len(g)
    ids={s:i for i,s in enumerate(g.site)}
    near=np.array([ids[s] for s in g.nearest_site],int)
    far=np.array([ids[s] for s in g.farthest_site],int)
    route=pd.factorize(g.route,sort=True)[0]
    nr=int(route.max()+1)
    pos=np.array([ids.get(s,-1) for s in annual.site],int)
    years=annual.year.to_numpy(int)
    num=annual["count"].to_numpy(int)
    result=np.zeros(len(annual),float)
    rng=np.random.default_rng(seed)
    base=rng.normal(size=n)
    site_bias=.6*base+.4*(base[near]+base[far])/2
    frogs_prev=rng.normal(size=n)
    local_env_prev=rng.normal(size=n)
    route_shock=np.zeros(nr)
    for year in range(int(years.min()),int(years.max())+1):
        route_shock=.67*route_shock+rng.normal(scale=.66,size=nr)
        if kind=="LOCAL_ENV_PERSISTENCE":
            # Dynamic spatially correlated weather/hydroperiod proxy: NO
            # organism moves; the local environment spreads/autocorrelates.
            env_now=(.45*local_env_prev+.38*local_env_prev[near]
                     +.22*site_bias+.42*route_shock[route]
                     +rng.normal(scale=.60,size=n))
            frog_now=(.55*frogs_prev+.65*env_now+.28*site_bias
                      +rng.normal(scale=.55,size=n))
            local_env_prev=env_now
        else:
            mixed=(1-mixing)*frogs_prev+mixing*frogs_prev[near]
            frog_now=(.55*mixed+.45*site_bias+
                      .55*route_shock[route]+rng.normal(scale=.65,size=n))
        idx=np.flatnonzero((years==year)&(pos>=0))
        if len(idx):
            logits=np.clip(-.6+.65*frog_now[pos[idx]],-30,30)
            p=1/(1+np.exp(-logits))
            result[idx]=rng.binomial(num[idx],p)/num[idx]
        frogs_prev=frog_now
    return result


def source_table_and_simulation(source_root,out,reps=N_REPS):
    sys.path.insert(0,str(source_root/"research/scripts"))
    from select_macro_trophic_scenarios import load_cohort,SITE,VISITS
    s=pd.read_csv(SITE);v=pd.read_csv(VISITS)
    d=load_cohort(s,v,expected=4248)
    if int(d.n.sum())!=63180:raise AssertionError("Original source NAAMP visits changed")
    annual,panel,geometry=annual_panel(d,v,expect_sites=4248,expect_visits=63180)
    obs=fixed_effect_association(panel,n_boot=0)
    if (len(panel)!=17183 or int(panel.route.nunique())!=369 or
        abs(obs["nearest_minus_farthest"]-SOURCE_NEAR_FAR)>1e-9):
        raise AssertionError("Actual acoustic yearly source must reproduce original observed pilot")

    scenarios=[("SHARED_ROUTE_ENV",0.),("LOCAL_ENV_PERSISTENCE",0.)]
    scenarios.extend(("STABLE_NEIGHBOUR_MIXING",m) for m in MIXING[1:])
    records=[]
    for it in range(reps):
        for name,m in scenarios:
            samples=stable_synthetic_panel(
                annual,geometry,seed=SEED+it,kind=name,mixing=m)
            res=fixed_effect_association(panel,values=samples,n_boot=0)
            records.append(dict(scenario=name,mixing_fraction=m,
                seed=SEED+it,replicate=it,
                nearest_minus_farthest=res["nearest_minus_farthest"],
                nearest_prior=res["beta_nearest_prior"],
                farthest_prior=res["beta_farthest_prior"],
                own_prior=res["beta_own_prior"]))
        if it%12==0:print("SPATIAL_ENV_NULL_RECOVERY_REPLICATE",it,flush=True)
    trials=pd.DataFrame(records)
    if (len(trials)!=len(scenarios)*reps or
        trials.duplicated(["scenario","mixing_fraction","seed"]).any()):
        raise AssertionError("Missing or duplicate source synthetic null/mixing comparisons")
    null=trials[trials.scenario.eq("SHARED_ROUTE_ENV")]
    env=trials[trials.scenario.eq("LOCAL_ENV_PERSISTENCE")]
    test=[]
    for m in MIXING[1:]:
        movement=trials[(trials.scenario=="STABLE_NEIGHBOUR_MIXING")&
                        (trials.mixing_fraction==m)]
        test.append(dict(source_mixing_fraction=m,
            model="STABLE_NEIGHBOUR_MIXING",
            AUC_vs_shared_route_environment=auc_score(
               null.nearest_minus_farthest,movement.nearest_minus_farthest),
            AUC_vs_dynamic_local_environment=auc_score(
               env.nearest_minus_farthest,movement.nearest_minus_farthest),
            null_mean=float(null.nearest_minus_farthest.mean()),
            dynamic_env_null_mean=float(env.nearest_minus_farthest.mean()),
            movement_mean=float(movement.nearest_minus_farthest.mean()),
            movement_95sim_low=float(movement.nearest_minus_farthest.quantile(.025)),
            movement_95sim_high=float(movement.nearest_minus_farthest.quantile(.975)),
            observed_near_minus_far=float(obs["nearest_minus_farthest"]),
            observed_below_fraction_of_movement_draws=float(
                (movement.nearest_minus_farthest>=
                 obs["nearest_minus_farthest"]).mean())))
    summary=pd.DataFrame(test)
    out.mkdir(parents=True,exist_ok=True)
    trials.to_csv(out/"spatial_environment_null_vs_stable_mixing_recovery.csv",index=False)
    summary.to_csv(out/"source_geometry_mixing_identifiability_auc.csv",index=False)
    receipt=dict(
        status="REAL_NAAMP_SPATIAL_HISTORY_OBSERVED_AND_STABLE_COUNTERFACTUAL_RECOVERY_SUCCESS",
        empirical_source_sites=4248,empirical_source_completed_surveys=63180,
        empirical_valid_site_years=len(panel),
        empirical_routes=int(panel.route.nunique()),
        observed_nearest_minus_farthest=float(obs["nearest_minus_farthest"]),
        tested_mixing=list(MIXING),
        independently_seeded_source_replicates_per_abstract_model=reps,
        n_all_simulated_panels=len(trials),
        dynamic_environment_null_includes_no_animal_movement=True,
        stable_neighbour_update_total_memory=.55,
        stable_mixing_is_not_original_finiteN_population_conservative_dispersal=True,
        acoustic_detection_and_true_larval_displacement_not_calibrated=True,
        ecological_mechanism_posterior_estimated=False,
        data_SHA256={"site":hashlib.sha256(SITE.read_bytes()).hexdigest(),
                     "visits":hashlib.sha256(VISITS.read_bytes()).hexdigest()},
        code_SHA256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    )
    (out/"receipt.json").write_text(json.dumps(receipt,indent=2,ensure_ascii=False)+"\n")
    print("SPATIAL_ENV_NULL_RECOVERY_VERIFIED",json.dumps({
        "n_site_years":len(panel),"observed":obs["nearest_minus_farthest"],
        "per_coupling":summary.to_dict("records")
    }),flush=True)
    return receipt

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--source-root",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    p.add_argument("--reps",type=int,default=N_REPS)
    a=p.parse_args()
    if a.reps<12:p.error("Too few independently randomized synthetic source replicates")
    source_table_and_simulation(a.source_root.resolve(),a.out,reps=a.reps)
