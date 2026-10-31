"""Exploratory spatial ABM + 1-D reaction-diffusion model of ontogenetic predation.

NOT calibrated to NAAMP, field density, or meth-eDNA.  A separate alternative
to the existing deterministic annual cohort model, not its exact replacement.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from pathlib import Path
import argparse
import hashlib
import json
import platform
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "research/results/multigeneration_reversal_20261031"
STAGES = ("F_tadpole", "F_adult", "S_larva", "S_adult", "D_nymph", "D_emerging", "D_adult")
FT, FA, SL, SA, DN, DE, DA = range(7)
PREDATION = ("S_larva_to_F_tadpole", "D_nymph_to_F_tadpole",
             "D_nymph_to_S_larva", "S_larva_to_D_nymph", "F_adult_to_D_emerging")
PREY = (FT, FT, SL, DN, DE)
MATURATION = ((FT, FA), (SL, SA), (DN, DE), (DE, DA))
BIRTH = ((FA, FT, 0), (SA, SL, 1), (DA, DN, 2))
WINDOWS = ((.05, .40), (.10, .50), (.15, .70))


@dataclass(frozen=True)
class Rates:
    # Arbitrary model-year rates; no claim of cross-species numerical calibration.
    natural: tuple = (.50, .70, .50, .55, .50, .85, .95)
    maturation: tuple = (3.0, 0., 2.0, 0., 2.0, 16.0, 0.)
    fecundity: tuple = (0., 3.5, 0., 2.2, 0., 0., 4.5)
    diffusion: tuple = (.05, .50, .05, .22, .04, .02, .65)
    capacity: float = 65.
    handling_density: float = 20.
    a_sf: float = .019
    a_df: float = .026
    a_ds: float = .018
    a_sd: float = .005
    a_fe: float = .12
    refuge_sf: float = .50
    refuge_df: float = .20
    refuge_ds: float = .20
    refuge_fe: float = .20
    density_response: bool = True
    seasonal_births: bool = True

    def validate(self, dt):
        vectors = (self.natural, self.maturation, self.fecundity, self.diffusion)
        if any(len(x) != len(STAGES) for x in vectors):
            raise ValueError("Seven stage rates required")
        values = np.asarray([v for group in vectors for v in group] +
                            [self.capacity, self.handling_density, self.a_sf, self.a_df,
                             self.a_ds, self.a_sd, self.a_fe, self.refuge_sf,
                             self.refuge_df, self.refuge_ds, self.refuge_fe, dt], float)
        if not np.isfinite(values).all() or (values < 0).any() or dt <= 0:
            raise ValueError("Finite, nonnegative rates and positive time step required")
        if self.capacity <= 0 or self.handling_density <= 0:
            raise ValueError("Positive density scales required")
        if 2 * max(self.diffusion) * dt > 1:
            raise ValueError("Explicit 1-D diffusion / ABM jump CFL exceeded")


def counts_from_agents(stage, cell, cells):
    return np.bincount(stage * cells + cell, minlength=7 * cells).reshape(7, cells)


def ensure_inputs(initial, vegetation, dt, params):
    x = np.asarray(initial)
    v = np.asarray(vegetation, float)
    if x.ndim != 2 or x.shape[0] != 7 or x.shape[1] < 1:
        raise ValueError("Expected [7, n_cells] stage population")
    if v.shape != (x.shape[1],) or not np.isfinite(v).all() or (v < 0).any() or (v > 1).any():
        raise ValueError("Vegetation must have one bounded value per cell")
    if not np.isfinite(x).all() or (x < 0).any():
        raise ValueError("Nonnegative finite initial state required")
    params.validate(dt)
    return x, v


def birth_multiplier(t, guild, params):
    if not params.seasonal_births:
        return 1.
    lo, hi = WINDOWS[guild]
    phase = t % 1.
    return (1. / (hi - lo)) if lo <= phase < hi else 0.


def predation_hazards(x, v, params, reverse=True, s_to_d=False):
    """Same per-prey hazard rates in stochastic ABM and density PDE."""
    ft, fa, sl, _sa, dn, de, _da = x
    h = np.zeros((5, x.shape[1]), float)
    h[0] = params.a_sf * sl * np.exp(-params.refuge_sf * v)
    h[1] = params.a_df * dn * np.exp(-params.refuge_df * v)
    if params.density_response:
        q = ft / params.handling_density
        h[1] *= (1-v)*2/(1+q) + v*2*q/(1+q*q)
    h[2] = params.a_ds * dn * np.exp(-params.refuge_ds * v)
    h[3] = params.a_sd * sl if s_to_d else 0.
    h[4] = params.a_fe * fa * np.exp(-params.refuge_fe * v) if reverse else 0.
    return h


def pde_step(initial, vegetation, params, dt, time, reverse=True, s_to_d=False):
    """Finite-difference reaction–diffusion, periodic boundary and positivity."""
    state, v = ensure_inputs(initial, vegetation, dt, params)
    x = state.astype(float, copy=True)
    d = np.asarray(params.diffusion)[:, None]
    x += dt * d * (np.roll(x, 1, axis=1) + np.roll(x, -1, axis=1) - 2*x)
    if x.min() < -1e-10:
        raise AssertionError("Negative density from diffusion")
    x = np.maximum(x, 0.)
    h = predation_hazards(x, v, params, reverse, s_to_d)
    total = np.broadcast_to(np.asarray(params.natural)[:, None], x.shape).copy()
    for edge, prey in enumerate(PREY):
        total[prey] += h[edge]
    dead = x * (-np.expm1(-total*dt))
    by_edge = np.zeros_like(h)
    for edge, prey in enumerate(PREY):
        by_edge[edge] = np.divide(dead[prey]*h[edge], total[prey],
                                 out=np.zeros_like(h[edge]), where=total[prey] > 0)
    remaining = x - dead
    move = np.zeros_like(remaining)
    for source, target in MATURATION:
        matured = remaining[source] * (-np.expm1(-params.maturation[source]*dt))
        move[source] -= matured
        move[target] += matured
    remaining += move
    water = remaining[FT] + remaining[SL] + remaining[DN]
    for adult, juvenile, guild in BIRTH:
        remaining[juvenile] += (remaining[adult] * params.fecundity[adult] *
                               birth_multiplier(time, guild, params) * dt /
                               (1 + water / params.capacity))
    if not np.isfinite(remaining).all() or (remaining < -1e-10).any():
        raise AssertionError("Invalid PDE density")
    return np.maximum(remaining, 0.), by_edge


@dataclass
class Agents:
    stage: np.ndarray
    cell: np.ndarray
    age: np.ndarray
    uid: np.ndarray
    parent: np.ndarray
    generation: np.ndarray
    next_uid: int

    def counts(self, cells):
        return counts_from_agents(self.stage, self.cell, cells)

    def validate(self, cells):
        n = len(self.stage)
        if any(len(a) != n for a in (self.cell, self.age, self.uid, self.parent, self.generation)):
            raise AssertionError("Agent table length mismatch")
        if len(np.unique(self.uid)) != n or np.any(self.cell >= cells) or np.any(self.cell < 0):
            raise AssertionError("Duplicated individuals or invalid cell")
        if np.any(self.age < 0) or np.any(self.generation < 0):
            raise AssertionError("Invalid age/generation")


def initial_agents(initial):
    x = np.asarray(initial)
    if not np.array_equal(x, x.astype(int)):
        raise ValueError("ABM requires integer individual counts")
    stage, cell = np.indices(x.shape)
    s = np.repeat(stage.ravel(), x.astype(int).ravel())
    c = np.repeat(cell.ravel(), x.astype(int).ravel())
    n = len(s)
    return Agents(s, c, np.zeros(n), np.arange(n, dtype=np.int64),
                  np.full(n, -1, dtype=np.int64), np.zeros(n, dtype=np.int64), n)


def abm_step(pop, vegetation, params, dt, time, rng, reverse=True, s_to_d=False,
             max_individuals=200000):
    """Explicit individuals: diffusion jumps, competing deaths, stage changes, offspring."""
    n_cells = len(vegetation)
    params.validate(dt)
    n_start = len(pop.stage)
    # Each individual moves independently to one of the two ring neighbors.
    chance = 2*np.asarray(params.diffusion)[pop.stage]*dt
    movers = rng.random(n_start) < chance
    directions = np.where(rng.random(n_start) < .5, -1, 1)
    pop.cell[movers] = (pop.cell[movers] + directions[movers]) % n_cells
    x = pop.counts(n_cells)
    h = predation_hazards(x, np.asarray(vegetation), params, reverse, s_to_d)
    rates = np.zeros((6, n_start))
    rates[0] = np.asarray(params.natural)[pop.stage]
    for edge, prey in enumerate(PREY):
        mask = pop.stage == prey
        rates[edge+1, mask] = h[edge, pop.cell[mask]]
    total = rates.sum(axis=0)
    dead = rng.random(n_start) < -np.expm1(-total*dt)
    cause = np.sum(rng.random(n_start)[None,:]*total[None,:] >
                   np.cumsum(rates, axis=0), axis=0)
    by_edge = np.zeros((5,n_cells), dtype=int)
    for edge in range(5):
        mask = dead & (cause == edge+1)
        np.add.at(by_edge[edge], pop.cell[mask], 1)
    survivors = ~dead
    stages = pop.stage[survivors].copy()
    before = stages.copy()  # no two maturations in one time step
    cells = pop.cell[survivors].copy()
    ages = pop.age[survivors]+dt
    uids = pop.uid[survivors].copy()
    parents = pop.parent[survivors].copy()
    generations = pop.generation[survivors].copy()
    for source, target in MATURATION:
        eligible = np.flatnonzero(before == source)
        transition_p = -np.expm1(-params.maturation[source]*dt)
        stages[eligible[rng.random(len(eligible)) < transition_p]] = target
    aquatic = counts_from_agents(stages, cells, n_cells)
    water = aquatic[FT] + aquatic[SL] + aquatic[DN]
    children = []
    for adult, juvenile, guild in BIRTH:
        candidates = np.flatnonzero(stages == adult)
        if not len(candidates):
            continue
        intensity = (params.fecundity[adult] * birth_multiplier(time, guild, params) *
                     dt / (1 + water[cells[candidates]] / params.capacity))
        n_babies = rng.poisson(intensity)
        child_from = np.repeat(candidates, n_babies)
        if len(child_from):
            children.append((juvenile, child_from))
    if children:
        newborn_stages = np.concatenate([np.full(len(idx), juvenile, dtype=int) for juvenile,idx in children])
        sources = np.concatenate([idx for juvenile,idx in children])
        baby_count = len(sources)
        if len(stages) + baby_count > max_individuals:
            raise ValueError("Exceeded explicit agent population safety limit")
        baby_uid = np.arange(pop.next_uid, pop.next_uid + baby_count, dtype=np.int64)
        pop.next_uid += baby_count
        stages = np.concatenate([stages,newborn_stages])
        cells = np.concatenate([cells,cells[sources]])
        ages = np.concatenate([ages,np.zeros(baby_count)])
        uids = np.concatenate([uids,baby_uid])
        parents = np.concatenate([parents,uids[sources]])
        generations = np.concatenate([generations,generations[sources]+1])
    pop.stage, pop.cell, pop.age = stages, cells, ages
    pop.uid, pop.parent, pop.generation = uids, parents, generations
    pop.validate(n_cells)
    if n_start + len(stages) - int(survivors.sum()) - int(dead.sum()) != len(stages):
        raise AssertionError("Agent birth/death accounting failed")
    return by_edge


def initial_grid(cells=8):
    """Synthetic uneven patches, no empirical site coordinates or densities."""
    if cells < 2:
        raise ValueError("Two or more habitat cells required for default experiment")
    v = np.where(np.arange(cells)%2 == 0, .10, .80)
    x = np.zeros((7,cells),int)
    for stage, base in enumerate((14, 13, 8, 6, 15, 2, 8)):
        x[stage] = np.maximum(1, base + np.rint(2*np.cos(2*np.pi*np.arange(cells)/cells + stage)).astype(int))
    return x,v


def _schedule(years, dt):
    if not isinstance(years,int) or years<1 or abs(1/dt-round(1/dt))>1e-8:
        raise ValueError("Require positive integer years and dt exactly dividing a year")
    return int(round(1/dt))


def _record(year, x, by_edge, model, reverse, seed=None, agents=None):
    row = dict(model=model,reverse=bool(reverse),seed=seed if seed is not None else -1,year=year)
    for j,label in enumerate(STAGES):
        row[label] = float(x[j].sum())
    row['n_total'] = float(x.sum())
    row['D_occupied_cells'] = int((x[DN]+x[DE]+x[DA] > 0).sum())
    for j,name in enumerate(PREDATION):
        row['deaths_'+name] = float(by_edge[j].sum())
    for guild,label in (([FT,FA],'F'),([SL,SA],'S'),([DN,DE,DA],'D')):
        mask = np.isin(agents.stage,guild) if agents is not None else None
        row['max_alive_generation_'+label] = int(agents.generation[mask].max()) if mask is not None and mask.any() else -1
    return row


def simulate_pde(initial, vegetation, params=Rates(), years=20, dt=.025,
                 reverse=True, s_to_d=False):
    x,v = ensure_inputs(initial,vegetation,dt,params)
    x = x.astype(float,copy=True)
    steps = _schedule(years,dt)
    rows = [_record(0,x,np.zeros((5,len(v))),"pde",reverse)]
    for year in range(years):
        ledger = np.zeros((5,len(v)))
        for tick in range(steps):
            x, deaths = pde_step(x,v,params,dt,year+tick*dt,reverse,s_to_d)
            ledger += deaths
        rows.append(_record(year+1,x,ledger,"pde",reverse))
    return pd.DataFrame(rows), x


def simulate_abm(initial, vegetation, params=Rates(), years=20, dt=.025,
                 reverse=True, s_to_d=False, seed=20261031):
    ensure_inputs(initial,vegetation,dt,params)
    agents = initial_agents(initial)
    agents.validate(len(vegetation))
    steps = _schedule(years,dt)
    rng = np.random.default_rng(seed)
    rows = [_record(0,agents.counts(len(vegetation)),np.zeros((5,len(vegetation))),
                    "abm",reverse,seed,agents)]
    for year in range(years):
        ledger = np.zeros((5,len(vegetation)))
        for tick in range(steps):
            deaths=abm_step(agents,vegetation,params,dt,year+tick*dt,rng,reverse,s_to_d)
            ledger += deaths
        rows.append(_record(year+1,agents.counts(len(vegetation)),ledger,
                            "abm",reverse,seed,agents))
    return pd.DataFrame(rows), agents


def run_experiment(years=20, seeds=(101,102,103,104), dt=.025, out=OUT):
    """Fixed finite counterfactual, no optimizing parameters to observations."""
    init,v=initial_grid()
    p=Rates()
    frames=[]
    for reverse in (False, True):
        full,_=simulate_pde(init,v,p,years,dt,reverse)
        frames.append(full)
        for seed in seeds:
            run,_=simulate_abm(init,v,p,years,dt,reverse,seed=seed)
            frames.append(run)
    all_years=pd.concat(frames,ignore_index=True)
    all_years.to_csv(out/'annual_stage_trajectories.csv',index=False)
    lookup = all_years.set_index(['model','seed','year','reverse'])
    totals = []
    for (model,seed,year), group in all_years.groupby(['model','seed','year']):
        if set(group.reverse)!={False,True}:raise AssertionError("Unpaired ablation")
        off=group.loc[~group.reverse].iloc[0]
        on=group.loc[group.reverse].iloc[0]
        totals.append(dict(model=model,seed=seed,year=year,
                           delta_D_nymph=on.D_nymph-off.D_nymph,
                           delta_D_adult=on.D_adult-off.D_adult,
                           delta_F_tadpole=on.F_tadpole-off.F_tadpole,
                           delta_F_adult=on.F_adult-off.F_adult,
                           delta_D_occupied_cells=on.D_occupied_cells-off.D_occupied_cells,
                           reversal_deaths=on['deaths_F_adult_to_D_emerging']))
    contrasts=pd.DataFrame(totals)
    contrasts.to_csv(out/'reverse_on_minus_off.csv',index=False)
    report=dict(status="SYNTHETIC_EXPLORATORY_NOT_FIELD_FIT",year_horizon=years,
                dt=dt,abiotic_space="synthetic_1D_periodic_eight_patches",
                methods=["explicit stochastic individual ABM","seven-stage finite-difference reaction–diffusion"],
                seeding=list(seeds),experiment="on/off adult frog to emerging dragonfly",
                source_note="stochastic seed pairing not pathwise identical random-number coupling",
                stage_count=7,spatial_patches=len(v),trajectory_rows=len(all_years),
                limits=["Not measured species-specific predation rates","PDE mean-field cannot capture stochastic extinction",
                        "Maturation is exponential, not fixed-age stage","Emergence window is coarse, not single-night resolution",
                        "No claim that adult salamander predation reverses","No direct NAAMP acoustic comparison"],
                python=platform.python_version(),numpy=np.__version__,pandas=pd.__version__,
                code_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    (out/'receipt.json').write_text(json.dumps(report,indent=2)+"\n")
    return all_years,contrasts,report


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--run',action='store_true')
    parser.add_argument('--years',type=int,default=20)
    parser.add_argument('--out',type=Path,default=OUT)
    args=parser.parse_args()
    if not args.run:parser.error("Explicit --run required")
    args.out.mkdir(parents=True,exist_ok=True)
    _,diff,report=run_experiment(years=args.years,out=args.out)
    print(json.dumps(report,indent=2))
    print(diff[diff.year.isin((1,2,5,10,args.years))].to_string(index=False))


if __name__=="__main__":
    main()
