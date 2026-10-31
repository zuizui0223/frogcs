"""12-seed replicated S larva/adult × rate × trophic source-sink POM.

Reuse the FIRST four real seed trajectories from original completed 32 ABMs,
and 8 truly new seed trajectories from separate 4-mode source CI. NO
synthetic pseudodata and NO acoustic/observational ABC posterior.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
import pandas as pd

from tracked_spatial_pedigree import ROOT
from run_equal_rate_S_stage_dispersal import (
    OUT as OLD,NEW_MODES,DIFFUSION_VALUES
)
from replicate_S_stage_source_sink import (
    OUT,NEW_SEEDS,PARENT_SEEDS,YEARS,GUILDS,annual_group_counts
)

ALL_SEEDS=tuple(PARENT_SEEDS)+tuple(NEW_SEEDS)
METRICS=("occupied_year20","alive_year20","total_births","total_deaths",
         "cumulative_net_recruitment","n_surviving_moves",
         "n_local_extinctions","n_recolonizations",
         "n_return_followups_eligible","n_return_persistent_two_censuses",
         "n_return_persistent_and_born_locally","n_return_censored")
BOOT=9999
SEED=20261031


def load_old_real_ABM_source(folder=OLD):
    rows=[];sources={}
    for mode in NEW_MODES:
        p=Path(folder)
        paths=[p/(mode+"_"+name) for name in (
            "seed_summary.csv","patch.csv.gz",
            "registry.csv.gz","observed_movements.csv.gz","receipt.json")]
        if any(not x.is_file() for x in paths):
            raise FileNotFoundError("Missing genuine original 4-seed source "+mode)
        summ,patch,reg,moves=(pd.read_csv(x) for x in paths[:4])
        receipt=json.loads(paths[4].read_text())
        if (len(summ)!=24 or set(summ.seed)!=set(PARENT_SEEDS) or
            receipt.get("n_new_actual_stochastic_runs")!=8 or
            receipt.get("original_ABM_kernel_unchanged") is not True):
            raise AssertionError("First 32 stochastic source arms not audit-safe")
        for rev in (False,True):
            for seed in PARENT_SEEDS:
                part=lambda df: df[df.reverse.eq(rev)&df.seed.eq(seed)].copy()
                p0=part(patch);r0=part(reg);m0=part(moves)
                if len(p0)!=(YEARS+1)*8*3:
                    raise AssertionError("Missing original patch annual census")
                flow=annual_group_counts(p0,r0,m0)
                for guild in GUILDS:
                    q=flow[flow.guild==guild]
                    anchor=summ[(summ.reverse==rev)&(summ.seed==seed)&
                                (summ.guild==guild)]
                    if len(anchor)!=1:
                        raise AssertionError("Missing original 4-seed source summary row")
                    orig=anchor.iloc[0]
                    if (int(q[q.year==YEARS].alive.gt(0).sum())!=
                            int(orig.n_occupied_year_end) or
                        int(q.recolonized.sum())!=int(orig.n_recolonizations) or
                        int(q.locally_extinct.sum())!=int(orig.n_local_extinction_events) or
                        int(q.inbound.sum())!=int(orig.n_seen_survivor_movements)):
                        raise AssertionError("Original seed re-read disagrees with newly audited UID source")
                    yearend=q[q.year==YEARS]
                    births=int(q.births.sum());deaths=int(q.deaths.sum())
                    rows.append(dict(
                        mobility=mode,reverse=bool(rev),seed=int(seed),
                        guild=guild,stage_mobility=mode.rsplit("_",1)[0],
                        per_capita_diffusion=DIFFUSION_VALUES[mode.rsplit("_",1)[1]],
                        occupied_year20=int(yearend.alive.gt(0).sum()),
                        alive_year20=int(yearend.alive.sum()),
                        total_births=births,total_deaths=deaths,
                        cumulative_net_recruitment=births-deaths,
                        n_surviving_moves=int(q.inbound.sum()),
                        n_local_extinctions=int(q.locally_extinct.sum()),
                        n_recolonizations=int(q.recolonized.sum()),
                        n_return_followups_eligible=int(orig.n_two_year_followup_eligible),
                        n_return_persistent_two_censuses=int(orig.n_two_year_retained),
                        n_return_persistent_and_born_locally=int(
                            orig.n_two_census_persistence_plus_local_births),
                        n_return_censored=int(orig.n_return_events_right_censored_at_2years),
                        max_abs_local_source_sink_residual=int(abs(q.identity_residual).max())))
        sources[mode]={x.name:hashlib.sha256(x.read_bytes()).hexdigest()
                       for x in paths}
    a=pd.DataFrame(rows)
    if len(a)!=4*2*4*3 or a.max_abs_local_source_sink_residual.ne(0).any():
        raise AssertionError("Original 32 ABMs were not all preserved and audited")
    return a,sources


def load_new_real_ABM_source(folder=OUT):
    rows=[];sources={}
    for mode in NEW_MODES:
        name=mode+"_new_seed_guild_source_sink_summary.csv"
        receipt=mode+"_new_seed_receipt.json"
        p=Path(folder)
        paths=[p/name,p/receipt,
               p/(mode+"_new_seed_local_flux.csv.gz"),
               p/(mode+"_new_seed_all_parent_UIDs.csv.gz"),
               p/(mode+"_new_seed_surviving_movement_UIDs.csv.gz")]
        if any(not x.is_file() for x in paths):
            raise FileNotFoundError("Missing 8 genuinely new tracked original source seeds "+mode)
        q=pd.read_csv(paths[0])
        rc=json.loads(paths[1].read_text())
        if (len(q)!=2*8*3 or set(q.seed)!=set(NEW_SEEDS)
            or rc.get("new_20year_arms")!=16
            or rc.get("every_patch_year_source_sink_identity_exact") is not True
            or q.max_abs_local_source_sink_residual.ne(0).any()):
            raise AssertionError("New 64 original model trajectories have incomplete ledger")
        if q.groupby(["reverse","guild"]).seed.nunique().ne(8).any():
            raise AssertionError("Original stochastic seed×stage/trophic conditions incomplete")
        rows.append(q)
        sources[mode]={x.name:hashlib.sha256(x.read_bytes()).hexdigest()
                       for x in paths}
    a=pd.concat(rows,ignore_index=True)
    if len(a)!=4*2*8*3 or a.duplicated(["mobility","reverse","seed","guild"]).any():
        raise AssertionError("One new sample path was lost or duplicated")
    return a,sources


def matched_stage_rate_trophic_pom(complete,n_boot=BOOT):
    if (len(complete)!=4*2*12*3 or
        complete.duplicated(["mobility","reverse","seed","guild"]).any() or
        complete.max_abs_local_source_sink_residual.ne(0).any()):
        raise ValueError("Both real ABM source cohorts are not complete")
    if set(complete.seed)!=set(ALL_SEEDS):
        raise ValueError("Original four plus eight additional independent seed labels missing")
    s=complete[complete.guild.eq("S")].copy()
    s["S_stage"]=s.mobility.str.rsplit("_",n=1).str[0]
    s["rate_code"]=s.mobility.str.rsplit("_",n=1).str[-1]
    keys=["seed","reverse"]
    rows=[]
    for (seed,rev),g in s.groupby(keys):
        if len(g)!=4 or g.duplicated(["S_stage","rate_code"]).any():
            raise AssertionError("Each original RNG label must cover 2×2 S stages/rates")
        lookup=g.set_index(["S_stage","rate_code"])
        for metric in METRICS:
            a005=lookup.loc[("S_adult","005"),metric]
            l005=lookup.loc[("S_larva","005"),metric]
            a022=lookup.loc[("S_adult","022"),metric]
            l022=lookup.loc[("S_larva","022"),metric]
            rows.append(dict(seed=int(seed),reverse=bool(rev),metric=metric,
                             adult_minus_larva_005=float(a005-l005),
                             adult_minus_larva_022=float(a022-l022),
                             interaction_rate_by_stage=float((a022-l022)-(a005-l005)),
                             adult_022_minus_005=float(a022-a005),
                             larva_022_minus_005=float(l022-l005)))
    contrasts=pd.DataFrame(rows)
    if len(contrasts)!=len(ALL_SEEDS)*2*len(METRICS):
        raise AssertionError("Incomplete true 12-seed stage×rate effects")
    # All original rate and reverse settings must be crossed with the exact same
    # 12 source RNG labels; these are simulator runs, not literal paired UID paths.
    draws=np.random.default_rng(SEED).integers(0,len(ALL_SEEDS),
                                               size=(n_boot,len(ALL_SEEDS)))
    report=[]
    comparisons=("adult_minus_larva_005","adult_minus_larva_022",
                 "interaction_rate_by_stage","adult_022_minus_005",
                 "larva_022_minus_005")
    for (rev,metric),g in contrasts.groupby(["reverse","metric"],sort=True):
        g=g.set_index("seed").loc[list(ALL_SEEDS)]
        for name in comparisons:
            data=g[name].to_numpy(float)
            boot=data[draws].mean(axis=1)
            report.append(dict(reverse=bool(rev),metric=metric,
                comparison=name,n_seed_replicates=len(data),
                mean_difference=float(data.mean()),
                bootstrap_ci_low=float(np.quantile(boot,.025)),
                bootstrap_ci_high=float(np.quantile(boot,.975)),
                n_positive=int((data>0).sum()),
                n_negative=int((data<0).sum()),
                n_zero=int((data==0).sum()),
                stochastic_seed_scope="SIMULATOR_REPLICATION_NOT_FIELD_PRECISION"))
    summary=pd.DataFrame(report)
    if len(summary)!=2*len(METRICS)*len(comparisons):
        raise AssertionError("Missing sign/source-sink factorial contrasts")
    condition=(s.groupby(["reverse","S_stage","rate_code"])
               .agg(n_seeds=("seed","nunique"),
                    mean_occupied_year20=("occupied_year20","mean"),
                    mean_births=("total_births","mean"),
                    mean_deaths=("total_deaths","mean"),
                    mean_surviving_moves=("n_surviving_moves","mean"),
                    mean_extinctions=("n_local_extinctions","mean"),
                    mean_recolonizations=("n_recolonizations","mean"),
                    mean_eligible_two_year_returns=("n_return_followups_eligible","mean"),
                    mean_persistent_birth_returns=("n_return_persistent_and_born_locally","mean"))
               .reset_index())
    if not condition.n_seeds.eq(len(ALL_SEEDS)).all() or len(condition)!=8:
        raise AssertionError("Unequal original and newly simulated survival trajectories")
    return s,contrasts,summary,condition


def run(old=OLD,new=OUT):
    old=Path(old)
    new=Path(new);new.mkdir(parents=True,exist_ok=True)
    a,oldsha=load_old_real_ABM_source(old)
    b,newsha=load_new_real_ABM_source(new)
    combined=pd.concat([a,b],ignore_index=True)
    s,contrasts,summary,condition=matched_stage_rate_trophic_pom(combined)
    output=dict(
        replicated_12seed_all_guild_source_sink=combined,
        replicated_12seed_S_conditions=condition,
        replicated_12seed_paired_effects=contrasts,
        replicated_12seed_paired_bootstrap_summary=summary)
    for name,x in output.items():x.to_csv(new/(name+".csv"),index=False)
    receipt=dict(status="GENUINE_96_ABM_12_SEED_STAGE_RATE_TROPHIC_SOURCE_SINK_REPLICATION",
        actual_20year_model_runs=96,new_original_kernel_runs=64,previous_runs_reused=32,
        independent_seed_labels=list(ALL_SEEDS),
        all_annual_local_source_sink_balances_exact=True,
        test_constraints_predeclared=True,
        n_bootstrap_seed_samples=BOOT,
        same_numeric_seed_labels_do_not_make_individual_pathwise_counterfactual=True,
        local_extinction_not_permanent_loss=True,
        source_32_models_SHA256=oldsha,source_64_models_SHA256=newsha,
        code_SHA256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    (new/"replicated_12seed_receipt.json").write_text(json.dumps(receipt,indent=2)+"\n")
    print("REPLICATED_12SEED_STAGE_RATE_CONDITIONS\n"+condition.to_string(index=False),flush=True)
    print("REPLICATED_12SEED_STAGE_RATE_EFFECTS\n"+
          summary[summary.metric.isin(["occupied_year20",
                    "n_recolonizations","n_local_extinctions","total_births",
                    "total_deaths","n_surviving_moves"])].to_string(index=False),flush=True)
    return output,receipt


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--run",action="store_true")
    p.add_argument("--old",type=Path,default=OLD)
    p.add_argument("--new",type=Path,default=OUT)
    args=p.parse_args()
    if not args.run:p.error("Explicit --run required")
    run(args.old,args.new)
