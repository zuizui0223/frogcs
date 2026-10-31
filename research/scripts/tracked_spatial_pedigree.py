"""Durable parent/child pedigree and local-extirpation accounting for frogcs ABM.

The TRUE stochastic per-step kernel is unchanged: each time step calls
multigeneration_reversal.abm_step exactly once and uses NO additional RNG.
The parent-child source is its explicit immutable UID and direct-parent field.
This audit only observes agents alive after each tick: surviving dispersal
events are observed, but jumps of individuals dying in that same tick cannot
be reconstructed without changing the kernel and are NOT counted as dispersal.

This model is the original seven-stage SYNTHETIC ABM/PDE pilot, NOT the
different 120-day + 80-year deterministic stage-network ABC. Do not join
their parameter numbers or claim NAAMP acoustic field fit.
"""
from __future__ import annotations

from dataclasses import replace
from pathlib import Path
import argparse
import hashlib
import json

import numpy as np
import pandas as pd

from multigeneration_reversal import (
    FT,FA,SL,SA,DN,DE,DA,STAGES,PREDATION,Rates,
    initial_agents,initial_grid,ensure_inputs,abm_step,simulate_pde,
    _schedule
)

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/"research/results/stochastic_pedigree_metapop_20261031"
GUILDS=("F","S","D")
GUILD_OF_STAGE=np.asarray([0,0,1,1,2,2,2])
SEEDS=(101,102,103,104)
MOBILITY=("off","original")
REVERSE=(False,True)
YEARS=20
DT=.05


def patch_occupancy_transitions(previous,current):
    """Annual integer-guild occupancy transitions, never count initial census."""
    before=np.asarray(previous,int)
    after=np.asarray(current,int)
    if before.shape!=after.shape or before.ndim!=2 or before.shape[0]!=3:
        raise ValueError("Occupancy requires paired [3,n_patch] nonnegative integer tables")
    if np.any(before<0) or np.any(after<0):
        raise ValueError("Negative original guild abundance")
    extinct=(before>0)&(after==0)
    recolonized=(before==0)&(after>0)
    if np.any(extinct&recolonized):
        raise AssertionError("A patch cannot become extinct and recolonized at same annual census")
    return extinct,recolonized


def per_guild_patch_counts(pop,n_patches):
    guild=np.asarray(GUILD_OF_STAGE,dtype=int)[pop.stage]
    return np.bincount(guild*n_patches+pop.cell,
                       minlength=3*n_patches).reshape(3,n_patches)


class PedigreeAudit:
    def __init__(self,agents,n_patches):
        agents.validate(n_patches)
        self.n_patches=n_patches
        self.registry={}
        self.movements=[]
        self.recorded_births=0
        self.recorded_deaths=0
        self.recorded_movements=0
        self.annual_births=np.zeros((3,n_patches),dtype=np.int64)
        self.annual_moves_in=np.zeros((3,n_patches),dtype=np.int64)
        for uid,stage,patch in zip(agents.uid,agents.stage,agents.cell):
            key=int(uid);patch=int(patch)
            self.registry[key]=dict(
                uid=key,parent_uid=-1,founder_uid=key,
                guild=GUILDS[int(GUILD_OF_STAGE[int(stage)])],
                generation=0,birth_time=0.,natal_patch=patch,
                founder_patch=patch,last_known_patch=patch,
                alive=True,death_time=np.nan,
                lifetime_surviving_moves=0,n_direct_children=0)
        if len(self.registry)!=agents.next_uid:
            raise AssertionError("Founders registry not the original ABM UID baseline")

    def _register_tick(self,before_uid,before_cell,before_stage,before_next,after,
                       time_year):
        after.validate(self.n_patches)
        if len(np.unique(before_uid))!=len(before_uid):
            raise AssertionError("Invalid duplicate before-step UID")
        # The original ABM appends newborn UIDs sequentially; old survivors
        # keep their pre-birth sort order. This must be true to map paths.
        if (len(before_uid)>1 and np.any(np.diff(before_uid)<=0)) or (
            len(after.uid)>1 and np.any(np.diff(after.uid)<=0)):
            raise AssertionError("Original ABM UID ordering changed")
        original_alive=after.uid < before_next
        surviving=after.uid[original_alive]
        at=np.searchsorted(before_uid,surviving)
        if np.any(at>=len(before_uid)) or not np.array_equal(before_uid[at],surviving):
            raise AssertionError("Previously nonexistent UID in original stochastic ABM")
        new_ids=after.uid[~original_alive]
        if not np.array_equal(new_ids,np.arange(before_next,after.next_uid)):
            raise AssertionError("Gap, collision or reuse of newborn ID")
        # Every original UID must be either surviving or dead.
        survivors_mask=np.zeros(len(before_uid),bool);survivors_mask[at]=True
        died_uid=before_uid[~survivors_mask]
        dead_pos=before_cell[~survivors_mask]
        for uid,patch in zip(died_uid,dead_pos):
            person=self.registry[int(uid)]
            if not person["alive"]:raise AssertionError("A dead person died twice")
            person["alive"]=False
            person["death_time"]=float(time_year)
            # This was their last observed patch at beginning of tick;
            # unobserved moves of dead agents are NOT falsely allocated.
            person["last_known_patch"]=int(patch)
        self.recorded_deaths+=len(died_uid)
        old_patch=before_cell[at]
        new_patch=after.cell[original_alive]
        shifted=old_patch!=new_patch
        for uid,src,dst,stage in zip(surviving[shifted],
                                     old_patch[shifted],
                                     new_patch[shifted],
                                     before_stage[at][shifted]):
            if int(dst) not in ((int(src)-1)%self.n_patches,
                                (int(src)+1)%self.n_patches):
                raise AssertionError("Dispersal must be a nearest-neighbour periodic-ring jump")
            person=self.registry[int(uid)]
            person["lifetime_surviving_moves"]+=1
            guild=int(GUILD_OF_STAGE[int(stage)])
            self.annual_moves_in[guild,int(dst)]+=1
            self.movements.append(dict(uid=int(uid),guild=GUILDS[guild],
                                       time_year=float(time_year),
                                       source_patch=int(src),destination_patch=int(dst),
                                       stage=STAGES[int(stage)],
                                       generation=person["generation"],
                                       founder_uid=person["founder_uid"],
                                       founder_patch=person["founder_patch"]))
        self.recorded_movements+=int(shifted.sum())
        for uid,cell in zip(surviving,new_patch):
            self.registry[int(uid)]["last_known_patch"]=int(cell)
        after_birth_index=np.flatnonzero(~original_alive)
        for ix in after_birth_index:
            uid=int(after.uid[ix]);parent=int(after.parent[ix])
            if uid in self.registry or parent not in self.registry:
                raise AssertionError("Unknown parent or recycled child UID")
            ancestor=self.registry[parent]
            if not ancestor["alive"]:
                raise AssertionError("A child was assigned a dead parent")
            own_guild=GUILDS[int(GUILD_OF_STAGE[int(after.stage[ix])])]
            if ancestor["guild"]!=own_guild:
                raise AssertionError("Predator/prey or stage transition gave cross-species parentage")
            if int(after.generation[ix])!=ancestor["generation"]+1:
                raise AssertionError("Generation count disconnected from the parent's genealogy")
            cell=int(after.cell[ix])
            if cell!=ancestor["last_known_patch"]:
                raise AssertionError("Birth patch differs from parent's current patch")
            self.registry[uid]=dict(
                uid=uid,parent_uid=parent,founder_uid=ancestor["founder_uid"],
                guild=own_guild,generation=ancestor["generation"]+1,
                birth_time=float(time_year),natal_patch=cell,
                founder_patch=ancestor["founder_patch"],last_known_patch=cell,
                alive=True,death_time=np.nan,lifetime_surviving_moves=0,
                n_direct_children=0)
            ancestor["n_direct_children"]+=1
            guild_idx=int(GUILD_OF_STAGE[int(after.stage[ix])])
            self.annual_births[guild_idx,cell]+=1
        self.recorded_births+=len(after_birth_index)
        if len(before_uid)+len(after_birth_index)-len(died_uid)!=len(after.uid):
            raise AssertionError("Original ABM births and deaths do not conserve individual identities")
        if len(self.registry)!=after.next_uid or sum(q["alive"] for q in self.registry.values())!=len(after.uid):
            raise AssertionError("No exact living/dead registry census")
        return len(after_birth_index),len(died_uid),int(shifted.sum())

    def step(self,pop,vegetation,params,dt,year_time,rng,
             reverse=True,s_to_d=False):
        before_uid=pop.uid.copy()
        before_cell=pop.cell.copy()
        before_stage=pop.stage.copy()
        before_next=int(pop.next_uid)
        cause_by_patch=abm_step(pop,vegetation,params,dt,year_time,rng,
                                reverse=reverse,s_to_d=s_to_d)
        born,died,shifted=self._register_tick(
            before_uid,before_cell,before_stage,before_next,pop,year_time+dt)
        if cause_by_patch.shape!=(5,self.n_patches) or cause_by_patch.sum()>died:
            raise AssertionError("Invalid source-ABM attributed predation deaths")
        return cause_by_patch,dict(births=born,deaths=died,movements=shifted)

    def audit(self,agents):
        agents.validate(self.n_patches)
        uid=agents.uid
        if any(self.registry[int(u)]["alive"] is False for u in uid):
            raise AssertionError("Living individual marked extinct in historical pedigree")
        if sum(x["alive"] for x in self.registry.values())!=len(uid):
            raise AssertionError("Dead or living individual omitted from historical pedigree")
        for child in self.registry.values():
            parent=child["parent_uid"]
            if parent==-1:
                if (child["generation"]!=0 or
                    child["founder_uid"]!=child["uid"]):
                    raise AssertionError("Founder incorrectly assigned a parent")
            else:
                if parent>=child["uid"] or parent not in self.registry:
                    raise AssertionError("Historical parent record absent")
                parent_record=self.registry[parent]
                if (child["generation"]!=parent_record["generation"]+1 or
                    child["founder_uid"]!=parent_record["founder_uid"] or
                    child["guild"]!=parent_record["guild"]):
                    raise AssertionError("Multigenerational offspring not genealogically traceable")
        if len(self.registry)!=agents.next_uid:
            raise AssertionError("Total lifetime births and founders not preserved")

    def census(self,pop,year,previous=None):
        self.audit(pop)
        counts=per_guild_patch_counts(pop,self.n_patches)
        if previous is None:
            extinct=np.zeros_like(counts,bool)
            arrivals=np.zeros_like(counts,bool)
        else:
            extinct,arrivals=patch_occupancy_transitions(previous,counts)
        annual=[]
        for g,guild in enumerate(GUILDS):
            for patch in range(self.n_patches):
                mask=(GUILD_OF_STAGE[pop.stage]==g)&(pop.cell==patch)
                here=pop.uid[mask]
                alive_record=[self.registry[int(k)] for k in here]
                donor=sum(q["founder_patch"]!=patch for q in alive_record)
                generations=[q["generation"] for q in alive_record]
                annual.append(dict(year=int(year),guild=guild,patch=patch,
                    alive=int(counts[g,patch]),occupied=bool(counts[g,patch]>0),
                    locally_extinct=bool(extinct[g,patch]),
                    recolonized=bool(arrivals[g,patch]),
                    known_surviving_immigrant_arrivals=int(self.annual_moves_in[g,patch]),
                    recolonized_with_seen_immigrant=bool(
                        arrivals[g,patch] and self.annual_moves_in[g,patch]>0),
                    n_newborn=int(self.annual_births[g,patch]),
                    n_living_descendants_of_other_patch=int(donor),
                    max_generation=max(generations,default=-1),
                    n_living_grandchild_or_later=int(sum(z>=2 for z in generations)),
                    n_distinct_founder_lineages=len({q["founder_uid"] for q in alive_record})))
        self.annual_births.fill(0)
        self.annual_moves_in.fill(0)
        return pd.DataFrame(annual),counts

    def lineage_summary(self):
        x=pd.DataFrame(self.registry.values())
        rows=[]
        for guild in GUILDS:
            allgroup=x[x.guild==guild]
            alive=allgroup[allgroup.alive]
            descendants=alive[alive.generation>0]
            lineages=(descendants.groupby("founder_uid").
                      last_known_patch.nunique())
            rows.append(dict(guild=guild,
                n_all_ever_recorded=len(allgroup),
                n_founders=int((allgroup.generation==0).sum()),
                n_nonfounder_births=int((allgroup.generation>0).sum()),
                n_living=int(alive.shape[0]),
                n_living_grandchild_or_later=int((alive.generation>=2).sum()),
                n_living_elsewhere_than_founder_patch=int((
                    alive.last_known_patch!=alive.founder_patch).sum()),
                n_lineages_with_living_descendants_in_multiple_patches=int(
                    (lineages>=2).sum()),
                max_generation_ever=int(allgroup.generation.max()) if len(allgroup) else -1,
                max_generation_alive=int(alive.generation.max()) if len(alive) else -1))
        return pd.DataFrame(rows)


def simulate_traced_abm(initial,vegetation,params=Rates(),years=YEARS,
                        dt=DT,reverse=True,s_to_d=False,seed=101):
    x,v=ensure_inputs(initial,vegetation,dt,params)
    agents=initial_agents(x)
    tracer=PedigreeAudit(agents,len(v))
    rng=np.random.default_rng(seed)
    steps=_schedule(years,dt)
    patch,previous=tracer.census(agents,0)
    patches=[patch]
    annual=[]
    for year in range(years):
        count=np.zeros(3,int)
        all_causes=np.zeros((5,len(v)),int)
        for tick in range(steps):
            by_edge,events=tracer.step(agents,v,params,dt,
                                       year+tick*dt,rng,reverse,s_to_d)
            all_causes+=by_edge
            for key in ("births","deaths","movements"):
                count[("births","deaths","movements").index(key)]+=events[key]
        following,previous=tracer.census(agents,year+1,previous)
        patches.append(following)
        stage=agents.counts(len(v))
        annual.append(dict(year=year+1,seed=seed,reverse=bool(reverse),
                           n_alive=len(agents.uid),
                           F_adult=int(stage[FA].sum()),
                           F_tadpole=int(stage[FT].sum()),
                           S_larva=int(stage[SL].sum()),
                           D_nymph=int(stage[DN].sum()),
                           D_emerging=int(stage[DE].sum()),
                           D_adult=int(stage[DA].sum()),
                           n_births=int(count[0]),n_deaths=int(count[1]),
                           n_observed_survivor_movements=int(count[2]),
                           **{"deaths_"+name:int(all_causes[i].sum())
                              for i,name in enumerate(PREDATION)}))
    tracers=pd.DataFrame(tracer.registry.values())
    tr_move=pd.DataFrame(tracer.movements)
    return dict(annual=pd.DataFrame(annual),
                patch=pd.concat(patches,ignore_index=True),
                registry=tracers,movements=tr_move,
                lineages=tracer.lineage_summary(),final_agents=agents)


def run_experiment(years=YEARS,dt=DT,seeds=SEEDS,out=OUT):
    out.mkdir(parents=True,exist_ok=True)
    initial,vegetation=initial_grid(8)
    rates=Rates()
    records=[];patches=[];lineages=[];movements=[];pedigrees=[];pde=[]
    for mobile in MOBILITY:
        p=(rates if mobile=="original" else
           replace(rates,diffusion=(0.,)*7))
        for reverse in REVERSE:
            from multigeneration_reversal import simulate_pde
            baseline,_=simulate_pde(initial,vegetation,p,years=years,dt=dt,
                                     reverse=reverse)
            baseline["mobility"]=mobile
            pde.append(baseline)
            for seed in seeds:
                one=simulate_traced_abm(initial,vegetation,p,years,dt,reverse,
                                        seed=seed)
                for field,target in (("annual",records),("patch",patches),
                                     ("registry",pedigrees),
                                     ("lineages",lineages),("movements",movements)):
                    df=one[field]
                    if field=="movements" and df.empty:continue
                    df=df.copy()
                    df["mobility"]=mobile
                    df["reverse"]=bool(reverse)
                    df["seed"]=int(seed)
                    target.append(df)
                print("LINEAGE_EXTINCTION_REAL_ABM",mobile,reverse,seed,
                      "year20_F_adult",one["annual"].F_adult.iloc[-1],
                      "year20_D_adult",one["annual"].D_adult.iloc[-1],
                      "total_birth_registry",len(one["registry"]),
                      flush=True)
    x=dict(annual=pd.concat(records,ignore_index=True),
           patch=pd.concat(patches,ignore_index=True),
           registry=pd.concat(pedigrees,ignore_index=True),
           lineage=pd.concat(lineages,ignore_index=True),
           movement=pd.concat(movements,ignore_index=True) if movements else pd.DataFrame(),
           pde=pd.concat(pde,ignore_index=True))
    n_arms=len(seeds)*len(REVERSE)*len(MOBILITY)
    if (len(x["annual"])!=years*n_arms or
        len(x["patch"])!=(years+1)*8*3*n_arms or
        len(x["lineage"])!=3*n_arms):
        raise AssertionError("Loss of baseline aligned annual/synthetic patch source")
    x["annual"].to_csv(out/"annual_stage_and_demographic_events.csv",index=False)
    x["patch"].to_csv(out/"patch_extirpation_recolonization.csv.gz",
                      index=False,compression={"method":"gzip","mtime":0})
    for key in ("registry","movement"):
        x[key].to_csv(out/(key+"_all_simulated_uids.csv.gz"),
                      index=False,compression={"method":"gzip","mtime":0})
    x["lineage"].to_csv(out/"lineage_generation_and_spatial_reach.csv",index=False)
    x["pde"].to_csv(out/"original_pde_density_comparison.csv",index=False)
    sum_rows=[]
    for (mobile,reverse,seed,guild),rows in x["patch"].groupby(
            ["mobility","reverse","seed","guild"]):
        end=rows[rows.year==years]
        events=rows[rows.year>0]
        lineage=x["lineage"][
            (x["lineage"].mobility==mobile)&
            (x["lineage"].reverse==reverse)&
            (x["lineage"].seed==seed)&
            (x["lineage"].guild==guild)].iloc[0]
        sum_rows.append(dict(mobility=mobile,reverse=bool(reverse),seed=int(seed),
                             guild=guild,year_end=years,
                             n_occupied_end=int(end.occupied.sum()),
                             n_local_extinction_events=int(events.locally_extinct.sum()),
                             n_recolonization_events=int(events.recolonized.sum()),
                             n_recolonizations_with_surviving_immigrant=int(
                                 events.recolonized_with_seen_immigrant.sum()),
                             n_survivor_movements=int(events.known_surviving_immigrant_arrivals.sum()),
                             n_living_elsewhere_than_ancestor_patch=int(
                                 lineage.n_living_elsewhere_than_founder_patch),
                             n_living_grandchild_or_later=int(
                                 lineage.n_living_grandchild_or_later),
                             n_multisite_founder_lineages=int(
                                 lineage.n_lineages_with_living_descendants_in_multiple_patches),
                             max_generation_alive=int(lineage.max_generation_alive)))
    summary=pd.DataFrame(sum_rows)
    summary.to_csv(out/"metapopulation_seed_level_summary.csv",index=False)
    receipt=dict(status="SYNTHETIC_SEVEN_STAGE_INDIVIDUAL_ABM_PARENT_CHILD_SPATIAL_TRACE",
                 model="unchanged multigeneration_reversal.abm_step",
                 not_same_kernel_as_original_80year_ABC=True,
                 spatial_patches=8,years=years,dt=dt,
                 seeds=list(seeds),mobility_settings=list(MOBILITY),
                 reverse_settings=[False,True],
                 n_independent_stochastic_seeds=len(seeds),
                 n_trajectory_arms=n_arms,
                 n_simulated_ever_lived_unique_ids=len(x["registry"]),
                 no_acoustic_or_trophic_field_calibration=True,
                 movement_count_excludes_within_tick_death_after_migration=True,
                 death_patch_last_observed_before_tick_not_exact_predation_location=True,
                 parenthood_is_single_model_breeder_not_genetically_resolved_paternity=True,
                 local_extinction_means_zero_living_guild_individuals_at_annual_census=True,
                 source_code_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    (out/"receipt.json").write_text(json.dumps(receipt,indent=2)+"\n")
    print("METAPOP_PEDIGREE_SUMMARY\n"+summary.to_string(index=False),flush=True)
    return x,summary,receipt


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--run",action="store_true")
    p.add_argument("--years",type=int,default=YEARS)
    p.add_argument("--dt",type=float,default=DT)
    p.add_argument("--seeds",type=int,nargs="+",default=SEEDS)
    args=p.parse_args()
    if not args.run:p.error("Explicit --run required")
    run_experiment(args.years,args.dt,tuple(args.seeds))
