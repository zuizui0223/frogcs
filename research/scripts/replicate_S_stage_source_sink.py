"""Replicate the original salamander stage×diffusion×trophic stochastic ABM.

Eight NEW seeds (105-112) for each of four stage/rate hypotheses ×2 reversal
arms; original four (101-104) are reused from successful source artifacts.
The biological kernel, rates and original pedigree observer are unmodified.

Every source guild×patch×annual census interval MUST satisfy:
    N[t] - N[t-1] == births - deaths + observed_survivor_in - observed_survivor_out
where within-step deaths are assigned to their last observed pre-step patch.
An incompatibility means a ledger-timing bug, NOT biological loss evidence.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
import pandas as pd

from multigeneration_reversal import initial_grid, Rates
from tracked_spatial_pedigree import simulate_traced_abm, ROOT
from run_equal_rate_S_stage_dispersal import (
    NEW_MODES,DIFFUSION_VALUES,equal_rate_modes
)
from assess_recolonization_establishment import (
    attach_validated_births,event_table,source_annual_stage_audit
)

OUT=ROOT/"research/results/replicated_S_stage_source_sink_20261031"
NEW_SEEDS=tuple(range(105,113))
PARENT_SEEDS=(101,102,103,104)
YEARS=20
DT=.05
GUILDS=("F","S","D")
PATCHES=8


def annual_group_counts(patch,registry,movements):
    """Verify one original ABM arm's exact local source–sink accounting."""
    p=patch.sort_values(["guild","patch","year"]).reset_index(drop=True)
    if len(p)!=(YEARS+1)*PATCHES*3 or p.duplicated(["guild","patch","year"]).any():
        raise AssertionError("Missing 21 annual guild×patch original model censuses")
    if not np.array_equal(np.sort(p.year.unique()),np.arange(YEARS+1)):
        raise AssertionError("Annual source census has missing years")
    n_by_cell=p.groupby(["guild","patch"]).size()
    if not n_by_cell.eq(YEARS+1).all():
        raise AssertionError("Incomplete original patch timeline")
    reg=registry
    if reg.uid.duplicated().any() or reg.parent_uid.ge(reg.uid).any():
        raise AssertionError("Original individual parent identifiers corrupted")
    if not set(reg.guild)==set(GUILDS):
        raise AssertionError("Some source species guild missing")
    births=reg[reg.parent_uid.ge(0)].copy()
    births["year"]=np.ceil(births.birth_time.to_numpy(float)-1e-9).astype(int)
    if births.year.lt(1).any() or births.year.gt(YEARS).any():
        raise AssertionError("Birth outside actual source ABM year horizon")
    born=(births.groupby(["year","guild","natal_patch"]).size()
          .rename("births").reset_index().rename(columns={"natal_patch":"patch"}))
    dead=reg[reg.alive.eq(False)].copy()
    if dead.death_time.isna().any():
        raise AssertionError("Missing historical death time in durable UID registry")
    dead["year"]=np.ceil(dead.death_time.to_numpy(float)-1e-9).astype(int)
    if dead.year.lt(1).any() or dead.year.gt(YEARS).any():
        raise AssertionError("Death outside observed ABM horizon")
    deaths=(dead.groupby(["year","guild","last_known_patch"]).size()
            .rename("deaths").reset_index().rename(columns={"last_known_patch":"patch"}))
    if not movements.empty:
        move=movements.copy()
        if "time_year" not in move or "source_patch" not in move:
            raise AssertionError("Original survivor-only movement ledger missing")
        move["year"]=np.ceil(move.time_year.to_numpy(float)-1e-9).astype(int)
        if move.year.lt(1).any() or move.year.gt(YEARS).any():
            raise AssertionError("Move outside observed year")
        incoming=(move.groupby(["year","guild","destination_patch"]).size()
                  .rename("inbound").reset_index().rename(columns={"destination_patch":"patch"}))
        outgoing=(move.groupby(["year","guild","source_patch"]).size()
                  .rename("outbound").reset_index().rename(columns={"source_patch":"patch"}))
    else:
        incoming=pd.DataFrame(columns=["year","guild","patch","inbound"])
        outgoing=pd.DataFrame(columns=["year","guild","patch","outbound"])
    current=p[p.year>0].copy()
    current["previous_alive"]=(p.groupby(["guild","patch"]).alive.shift(1)
                               .loc[current.index].to_numpy())
    if current.previous_alive.isna().any():
        raise AssertionError("Missing previous annual original source census")
    for sub in (born,deaths,incoming,outgoing):
        current=current.merge(sub,on=["year","guild","patch"],
                              how="left",validate="one_to_one")
    for label in ("births","deaths","inbound","outbound"):
        current[label]=current[label].fillna(0).astype(int)
    if not (current.n_newborn.to_numpy(int)==current.births.to_numpy(int)).all():
        raise AssertionError("Original model annual newborn counts vs full dead+alive UID birth records differ")
    current["delta_alive"]=current.alive-current.previous_alive
    current["net_surviving_migration"]=current.inbound-current.outbound
    current["source_sink_balance"]=(
        current.births-current.deaths+current.net_surviving_migration)
    current["identity_residual"]=current.delta_alive-current.source_sink_balance
    if current.identity_residual.ne(0).any():
        raise AssertionError("Cannot infer source–sink flux: within-year UID conservation FAILS "+
                             str(current[current.identity_residual.ne(0)][
                                 ["year","guild","patch","delta_alive","births","deaths",
                                  "inbound","outbound","identity_residual"]].head(5).to_dict("records")))
    for (year,guild),q in current.groupby(["year","guild"]):
        if q.inbound.sum()!=q.outbound.sum():
            raise AssertionError("Movement on a closed periodic ring did not conserve guild counts")
    if current.source_sink_balance.isna().any().any():
        raise AssertionError("Missing source-sink decomposition")
    return current


def audited_one(mode,reverse,seed,years=YEARS,dt=DT):
    if years!=YEARS or dt!=DT or mode not in NEW_MODES or seed not in NEW_SEEDS:
        raise ValueError("Experimental horizon, rate and prespecified new seed labels immutable")
    x,v=initial_grid(PATCHES)
    params=equal_rate_modes(mode)
    result=simulate_traced_abm(x,v,params,years=years,dt=dt,
                               reverse=reverse,seed=seed)
    full=annual_group_counts(result["patch"],result["registry"],result["movements"])
    # Independently recover the source record's counts from dead+alive UID.
    origin=result["registry"]
    if int(origin.parent_uid.ge(0).sum())!=int(full.births.sum()):
        raise AssertionError("Source annual births and global parent UID registry disagree")
    if int((~origin.alive).sum())!=int(full.deaths.sum()):
        raise AssertionError("Source annual mortality and global dead UID registry disagree")
    if len(result["movements"])!=int(full.inbound.sum()):
        raise AssertionError("Source movement events counted twice or omitted")
    # The source tracer returns one arm's raw UID/patch tables; the shared
    # source-census auditor expects the same explicit arm keys as its archived
    # four-seed data. These are labels only, not alterations of the simulator.
    labeled={}
    for name in ("patch","registry","annual","movements"):
        fragment=result[name].copy()
        fragment["mobility"]=mode
        fragment["reverse"]=bool(reverse)
        fragment["seed"]=int(seed)
        labeled[name]=fragment
    linked=attach_validated_births(labeled["patch"],labeled["registry"])
    source_annual_stage_audit(linked,labeled["annual"])
    events=event_table(linked)
    label=f"{mode}"
    full["mobility"]=label
    full["reverse"]=bool(reverse)
    full["seed"]=int(seed)
    full["rate"]=DIFFUSION_VALUES[mode.rsplit("_",1)[1]]
    full["stage_mobility"]=mode.rsplit("_",1)[0]
    if len(events):
        events["mobility"]=label
        events["reverse"]=bool(reverse)
        events["seed"]=int(seed)
    summary=[]
    for guild in GUILDS:
        q=full[full.guild==guild]
        sub=linked[linked.guild==guild]
        events_g=events[events.guild==guild] if len(events) else pd.DataFrame()
        end=sub[sub.year==years]
        n_follow=(events_g.two_census_followups_observed.sum()
                  if len(events_g) else 0)
        summary.append(dict(mobility=label,reverse=bool(reverse),seed=int(seed),
                            guild=guild,stage_mobility=mode.rsplit("_",1)[0],
                            per_capita_diffusion=DIFFUSION_VALUES[mode.rsplit("_",1)[1]],
                            occupied_year20=int(end.occupied.sum()),
                            alive_year20=int(end.alive.sum()),
                            total_births=int(q.births.sum()),
                            total_deaths=int(q.deaths.sum()),
                            cumulative_net_recruitment=int((q.births-q.deaths).sum()),
                            n_surviving_moves=int(q.inbound.sum()),
                            n_local_extinctions=int(q.locally_extinct.sum()),
                            n_recolonizations=int(q.recolonized.sum()),
                            n_return_followups_eligible=int(n_follow),
                            n_return_persistent_two_censuses=int(
                                events_g.retained_at_two_followups.fillna(False).astype(int).sum())
                                if len(events_g) else 0,
                            n_return_persistent_and_born_locally=int(
                                events_g.two_census_persistence_and_postreturn_births.fillna(False)
                                .astype(int).sum()) if len(events_g) else 0,
                            n_return_censored=int((~events_g.two_census_followups_observed).sum())
                                if len(events_g) else 0,
                            max_abs_local_source_sink_residual=int(abs(q.identity_residual).max())))
    annual=result["annual"].copy()
    annual["mobility"]=label;annual["stage_mobility"]=mode.rsplit("_",1)[0]
    annual["diffusion"]=DIFFUSION_VALUES[mode.rsplit("_",1)[1]]
    annual["reverse"]=bool(reverse);annual["seed"]=seed
    labeled_result=dict(result)
    labeled_result.update(labeled)
    return full,pd.DataFrame(summary),annual,events,labeled_result


def run(mode,out=OUT):
    if mode not in NEW_MODES:
        raise ValueError("Mode not originally prespecified")
    out.mkdir(parents=True,exist_ok=True)
    flows=[];summaries=[];annual=[];events=[];registries=[];movements=[];lineages=[];total_registry=0
    for reverse in (False,True):
        for seed in NEW_SEEDS:
            flow,summary,year,episode,real=audited_one(mode,reverse,seed)
            flows.append(flow);summaries.append(summary);annual.append(year)
            if len(episode):events.append(episode)
            total_registry+=len(real["registry"])
            for field,destination in (("registry",registries),
                                      ("movements",movements),
                                      ("lineages",lineages)):
                fragment=real[field].copy()
                if fragment.empty:
                    continue
                fragment["mobility"]=mode
                fragment["reverse"]=bool(reverse)
                fragment["seed"]=int(seed)
                destination.append(fragment)
            print("S_STAGE_NEW_SEED_REAL_20Y",mode,reverse,seed,
                  "S year20 occupied",int(summary[summary.guild=="S"].occupied_year20.iloc[0]),
                  "S births",int(summary[summary.guild=="S"].total_births.iloc[0]),
                  "S deaths",int(summary[summary.guild=="S"].total_deaths.iloc[0]),
                  "S movements",int(summary[summary.guild=="S"].n_surviving_moves.iloc[0]),
                  flush=True)
    compact=pd.concat(summaries,ignore_index=True)
    allflow=pd.concat(flows,ignore_index=True)
    allannual=pd.concat(annual,ignore_index=True)
    e=pd.concat(events,ignore_index=True) if events else pd.DataFrame()
    if (len(compact)!=len(NEW_SEEDS)*2*3 or
        len(allflow)!=len(NEW_SEEDS)*2*3*PATCHES*YEARS or
        len(allannual)!=len(NEW_SEEDS)*2*YEARS):
        raise AssertionError("Unexpected genuine stochastic source grain")
    lineage=pd.concat(lineages,ignore_index=True)
    registry=pd.concat(registries,ignore_index=True)
    moves=pd.concat(movements,ignore_index=True) if movements else pd.DataFrame()
    if len(lineage)!=len(NEW_SEEDS)*2*3 or len(registry)!=total_registry:
        raise AssertionError("Full source ancestry history was not preserved")
    if len(moves)!=int(compact.n_surviving_moves.sum()):
        raise AssertionError("Individual movement sources are missing or double counted")
    if compact.max_abs_local_source_sink_residual.ne(0).any():
        raise AssertionError("Unresolved local births/deaths/observed survivor migration ledger")
    for field,table in [("new_seed_guild_source_sink_summary",compact),
                        ("new_seed_annual_stage_censuses",allannual)]:
        table.to_csv(out/(mode+"_"+field+".csv"),index=False)
    allflow.to_csv(out/(mode+"_new_seed_local_flux.csv.gz"),
                   index=False,compression={"method":"gzip","mtime":0})
    e.to_csv(out/(mode+"_new_seed_return_episodes.csv"),index=False)
    lineage.to_csv(out/(mode+"_new_seed_lineage_summary.csv"),index=False)
    registry.to_csv(out/(mode+"_new_seed_all_parent_UIDs.csv.gz"),index=False,
                    compression={"method":"gzip","mtime":0})
    moves.to_csv(out/(mode+"_new_seed_surviving_movement_UIDs.csv.gz"),index=False,
                 compression={"method":"gzip","mtime":0})
    receipt=dict(status="NEW_EIGHT_SEEDS_TRUE_20YEAR_S_STAGE_RATE_SOURCE_SINK",
                 source_genuine_ABM_unchanged=True,
                 mode=mode,original_4_seed_ids=list(PARENT_SEEDS),
                 new_independent_seed_ids=list(NEW_SEEDS),
                 reverse_conditions=[False,True],new_20year_arms=2*len(NEW_SEEDS),
                 n_patch_year_guild_rows=len(allflow),n_total_ever_lived_uids=total_registry,
                 every_patch_year_source_sink_identity_exact=True,
                 original_80year_four_direction_ABCPOM_is_distinct=True,
                 source_kernel_sha256=hashlib.sha256(
                     Path(__file__).with_name("multigeneration_reversal.py").read_bytes()).hexdigest(),
                 source_ancestry_tracer_sha256=hashlib.sha256(
                     Path(__file__).with_name("tracked_spatial_pedigree.py").read_bytes()).hexdigest(),
                 script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    (out/(mode+"_new_seed_receipt.json")).write_text(json.dumps(receipt,indent=2)+"\n")
    print("S_STAGE_NEW_SEED_SOURCE_SINK_SUMMARY\n"+compact[compact.guild=="S"].to_string(index=False),flush=True)
    return compact,allflow,e,receipt


if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--run",action="store_true")
    p.add_argument("--mode",required=True,choices=NEW_MODES)
    args=p.parse_args()
    if not args.run:p.error("Explicit --run required")
    run(args.mode)
