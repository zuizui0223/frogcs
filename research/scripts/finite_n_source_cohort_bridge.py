"""Finite-N spatial annual cohort extension using original frogcs seasonal trophic kernel.

Uses *unchanged* stage_network_extension_20261029.simulate and source PR146
annual conditional mean recurrence. Binomial season completion and adult
survival, Poisson local delayed recruitment and external immigration, and
integer-conserving annual neighbouring patch movement are newly introduced
stochastic assumptions. It is not the distinct PR147 seven-stage ABM.
No field-calibrated population sizes, true parent UID, or acoustic model.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

from stage_network_extension_20261029 import simulate as seasonal_kernel
from multiyear_stage_network import DEMOGRAPHY
from spatial_cohort_80y_bridge import (
    ROOT, PATCHES, PILOT_ROLES, synthetic_vegetation, replay_gate, pilot_cube,
)

OUT = ROOT / "research/results/finite_n_stage_bridge_20261031"
GUILDS = ("F", "S", "D")
MOVEMENT_MODES = ("off", "recruits", "carryover", "both")
CONTEXTS = ("original", "D_first_S_overtakes")
PLANTS = ("SF1_DF0_DS0_L1", "SF0_DF0_DS1_L0")
SCALES = (3, 12)
SEEDS = (101, 102, 103, 104)
YEARS = 80
WINDOW = 20
DT = .25
MOVE_FRAC = .15


def sample_ring_transfer(counts, rate, rng):
    """Integer-preserving 8-patch ring flow. Left/right each rate/2.

    Returns post-move counts, incoming and outgoing counts; all arrays
    [source_scenario, patch, F/S/D]. Each original agent moved at most once.
    """
    x = np.asarray(counts)
    if x.ndim != 3 or x.shape[1] < 3 or x.shape[2] != 3:
        raise ValueError("Need [scenario, >=3 patches, 3 guilds]")
    if not np.issubdtype(x.dtype, np.integer) or (x < 0).any():
        raise ValueError("Nonnegative integer cohorts required")
    if not np.isfinite(rate) or not (0 <= rate <= 1):
        raise ValueError("Move fraction must be in [0,1]")
    if rate == 0:
        return x.copy(), np.zeros_like(x), np.zeros_like(x)
    left = rng.binomial(x, rate / 2)
    right = rng.binomial(x-left, rate/(2-rate))
    stay = x-left-right
    # Departure left from patch i is arrival at patch i-1.
    incoming = np.roll(left, -1, axis=1) + np.roll(right, 1, axis=1)
    outgoing = left + right
    y = stay + incoming
    if not np.array_equal(y.sum(axis=1), x.sum(axis=1)):
        raise AssertionError("Stochastic ring movement violates conservation")
    if not np.array_equal(y, x - outgoing + incoming):
        raise AssertionError("Stochastic patch flow ledger mismatch")
    return y, incoming, outgoing


def annual_conditional_means(B, completed_due, survival, rho, conversion,
                             juvenile, delay, source, *, immigrants=True):
    """PR146 annual mean EXACT given B and previous matured C densities."""
    B = np.asarray(B, dtype=float)
    due = np.asarray(completed_due, dtype=float)
    if B.shape != due.shape or B.shape[-1] != 3:
        raise ValueError("Three-guild cohort/due density shape mismatch")
    K = float(DEMOGRAPHY["capacity"])
    local = rho * conversion * juvenile ** (delay-1) * due / (1+due/K)
    carry = survival * B
    external = ((1-rho)*(1-survival)*source if immigrants
                else np.zeros_like(B))
    return carry, local, external


def finite_annual_update(N, completed_due, survival, rho, conversion,
                         juvenile, delay, source, rng, *, scale, movement,
                         transfer=MOVE_FRAC, immigration=True):
    """Sample each SOURCE recurrence contribution, then shift 0/1/2 streams.

    source density is at each patch. Cohort N is integer count; due is an
    integer delayed *season-completion cohort*, not adult newborn pedigree.
    """
    n = np.asarray(N)
    d = np.asarray(completed_due)
    if (not np.issubdtype(n.dtype, np.integer) or not np.issubdtype(d.dtype, np.integer)
            or n.shape != d.shape or n.ndim != 3 or n.shape[2] != 3
            or (n < 0).any() or (d < 0).any()):
        raise ValueError("Expected nonnegative integer source/due patch cohorts")
    if not isinstance(scale, int) or scale < 1 or movement not in MOVEMENT_MODES:
        raise ValueError("Unknown scale or annual movement mode")
    carry_mean, local_mean, ext_mean = annual_conditional_means(
        n/scale, d/scale, survival, rho, conversion,
        juvenile, delay, source, immigrants=immigration
    )
    if not (np.isfinite(local_mean).all() and (local_mean >= 0).all()
            and (carry_mean >= 0).all() and (ext_mean >= 0).all()):
        raise AssertionError("Invalid stochastic source mean")
    # All dimensions broadcast [source_scenario, patch, guild].
    survivor = rng.binomial(n, np.broadcast_to(survival, n.shape))
    local = rng.poisson(scale*local_mean)
    ext = rng.poisson(scale*ext_mean)
    zero = np.zeros_like(n)
    if movement in ("carryover", "both"):
        carried, ci, co = sample_ring_transfer(survivor, transfer, rng)
    else:
        carried, ci, co = survivor, zero, zero
    if movement in ("recruits", "both"):
        recruited, li, lo = sample_ring_transfer(local, transfer, rng)
    else:
        recruited, li, lo = local, zero, zero
    incoming, outgoing = ci+li, co+lo
    next_n = carried + recruited + ext
    if not np.array_equal(next_n, survivor + local + ext + incoming - outgoing):
        raise AssertionError("Exact source/transfer population identity violated")
    if not np.array_equal(incoming.sum(axis=1), outgoing.sum(axis=1)):
        raise AssertionError("Closed landscape lost migrants")
    return next_n, dict(survivors=survivor, local_recruits=local,
                        external=ext, arrivals=incoming, departures=outgoing)


def source_cube(draws=1):
    """Small outcome-blind source subset of original four rate IDs."""
    if draws not in (1, 2):
        raise ValueError("First finite-N gate uses one or two predeclared source draw IDs")
    cube = pilot_cube(draws)
    cube = cube[cube.context.isin(CONTEXTS) &
                cube.plant_model.isin(PLANTS) &
                cube.risk.eq(False)].copy().reset_index(drop=True)
    expected = len(CONTEXTS)*len(PLANTS)*draws*2*8
    if len(cube) != expected or cube.duplicated(
            ["structure_id", "draw", "reverse_on", "vertex"]).any():
        raise AssertionError("Incomplete source-locked two-plant, two-order, edge factorial")
    return cube


def make_source_group(group, patches=PATCHES):
    """All hypothetical controls EXACTLY match PR146 annual plant simulation."""
    n = len(group)
    q = group.loc[group.index.repeat(patches)].reset_index(drop=True)
    pid = np.tile(np.arange(patches), n)
    vegetation = synthetic_vegetation(
        q.vegetation.to_numpy(float), pid, "mosaic"
    )
    n_rows = len(q)
    params = [
        dict(community="FSD", roles=15, refuge_order="D",
             vegetation=float(vegetation[i]), f_arrival=20.,
             s_arrival=float(row.sa), d_arrival=float(row.da),
             attack_scale=float(row.attack_scale), cue=0.,
             reverse=bool(row.reverse_on))
        for i, row in enumerate(q.itertuples(index=False))
    ]
    seasonal = dict(
        stage_durations=np.column_stack([
            np.full(n_rows,45.), np.full(n_rows,80.),
            q.dduration.to_numpy(float),
        ]),
        functional_response=("litter" if bool(q.litter.iloc[0]) else None),
        behavioral_refuge=bool(q.risk.iloc[0]),
        handling_s=q.hs.to_numpy(float), handling_d=q.hd.to_numpy(float),
        s_growth=q.sg.to_numpy(float), d_growth=q.dg.to_numpy(float),
        sd_size_mode="dynamic",
        pathway_controls=dict(
            cover_SF=q.cover_SF.to_numpy(float),
            cover_DF=q.cover_DF.to_numpy(float),
            cover_DS=q.cover_DS.to_numpy(float),
            cover_SD=np.zeros(n_rows), support_DF=np.zeros(n_rows),
            support_DS=np.zeros(n_rows), emerge_survival=np.zeros(n_rows),
            emerge_exposure=np.zeros(n_rows), cue_SD=np.zeros(n_rows),
            edge_SD=np.ones(n_rows), edge_DS=np.ones(n_rows),
        ),
    )
    source = np.column_stack([
        np.ones(n_rows), q.S_source.to_numpy(float),
        q.D_source.to_numpy(float),
    ]).reshape(n, patches, 3)
    rho = q.rho.to_numpy(float).reshape(n, patches, 1)
    survival = np.column_stack([
        q.f_adult_survival.to_numpy(float),
        np.full(n_rows,.5), np.zeros(n_rows)
    ]).reshape(n,patches,3)
    conversion = np.broadcast_to(
        q.conversion.to_numpy(float)[:,None], (n_rows,3)
    ).reshape(n,patches,3)
    juvenile = np.column_stack([
        q.f_juvenile_survival.to_numpy(float),
        np.full(n_rows,.8), np.full(n_rows,.8)
    ]).reshape(n,patches,3)
    delay = np.column_stack([
        q.f_delay.to_numpy(int), np.full(n_rows,2,int),
        np.ones(n_rows,int)
    ]).reshape(n,patches,3)
    if not np.isin(delay[:,:,0], (2,3)).all():
        raise AssertionError("Unexpected original annual maturation delay")
    return params, seasonal, source, rho, survival, conversion, juvenile, delay


def simulate_finite_group(group, *, scale, seed, mode, immigration=True,
                          years=YEARS, dt=DT, transfer=MOVE_FRAC):
    """True integer 0-based extirpation events for every guild and patch."""
    if years < 4 or dt <= 0 or not 1 <= int(scale) <= 500:
        raise ValueError("Finite biological simulation design required")
    n = len(group)
    params, season_opts, source, rho, survival, conv, juvenile, delay = (
        make_source_group(group)
    )
    patches=PATCHES
    # Reproducibility must be independent of dictionary hash randomization.
    # Each experiment arm has its own RNG, matched seed LABELS are not
    # pathwise common random numbers across different movement treatments.
    seed_key=(f"{seed}|{mode}|{immigration}|{scale}|"
              f"{group.context.iloc[0]}|{group.plant_model.iloc[0]}")
    random_seed=int.from_bytes(
        hashlib.blake2b(seed_key.encode(), digest_size=8).digest(), "big"
    )
    rng=np.random.default_rng(random_seed)
    initial=round(float(DEMOGRAPHY["initial_scale"])*scale)
    N=np.full((n, patches, 3), initial, dtype=np.int64)
    hist=np.zeros((years+1,n,patches,3),dtype=np.int32)
    recruit_hist=np.zeros((years,n,patches,3),dtype=np.int32)
    immigrant_hist=np.zeros_like(recruit_hist)
    arrival_hist=np.zeros_like(recruit_hist)
    departure_hist=np.zeros_like(recruit_hist)
    death_hist=np.zeros_like(recruit_hist)
    hist[0]=N
    prev1=np.zeros_like(N)
    prev2=np.zeros_like(N)
    for year in range(years):
        seasonal=seasonal_kernel(
            params,dt=dt,initial_cohorts=(N/scale).reshape(n*patches,3),
            **season_opts
        )
        C=seasonal[["F_completed","S_completed","D_completed"]].to_numpy(
            dtype=float
        ).reshape(n,patches,3)
        density=N/scale
        if not np.isfinite(C).all() or (C < -1e-12).any() or (
            C > density + 1e-10
        ).any():
            raise AssertionError("Source seasonal kernel completion is outside cohort bounds")
        p=np.divide(C,density,out=np.zeros_like(C),where=N>0)
        if (p < -1e-10).any() or (p > 1+1e-10).any():
            raise AssertionError("Cannot sample source season completion as binomial")
        complete=rng.binomial(N,np.clip(p,0,1))
        due=np.empty_like(N)
        due[:,:,0]=np.where(delay[:,:,0]==2,prev1[:,:,0],prev2[:,:,0])
        due[:,:,1]=prev1[:,:,1]
        due[:,:,2]=complete[:,:,2]
        next_n,ledger=finite_annual_update(
            N,due,survival,rho,conv,juvenile,delay,source,rng,
            scale=int(scale),movement=mode,transfer=transfer,
            immigration=immigration
        )
        hist[year+1]=next_n
        recruit_hist[year]=ledger["local_recruits"]
        immigrant_hist[year]=ledger["external"]
        arrival_hist[year]=ledger["arrivals"]
        departure_hist[year]=ledger["departures"]
        death_hist[year]=N-ledger["survivors"]
        prev2,prev1=prev1,complete
        N=next_n
    return {
        "hist":hist,"local_recruits":recruit_hist,
        "external":immigrant_hist,"arrivals":arrival_hist,
        "departures":departure_hist,
        "deaths":death_hist,
    }


def summarize_finite_group(group, outputs, *, scale, seed, mode, immigration,
                           years):
    """Census-based exact zeros, two-year censor, own delayed recruitment."""
    H=outputs["hist"]
    local=outputs["local_recruits"]
    ext=outputs["external"]
    arrivals=outputs["arrivals"]
    departures=outputs["departures"]
    deaths=outputs["deaths"]
    if H.shape[0] != years+1 or H.shape[-1] != 3:
        raise AssertionError("Missing complete annual source patch censuses")
    if not np.array_equal(arrivals.sum(axis=2),departures.sum(axis=2)):
        raise AssertionError("Non-conservative source movement in saved output")
    expected_final=(H[0].sum(axis=1)+local.sum(axis=(0,2))+
                    ext.sum(axis=(0,2))-deaths.sum(axis=(0,2)))
    if not np.array_equal(H[-1].sum(axis=1), expected_final):
        raise AssertionError("Source annual births/deaths/immigration conservation failed")
    if not immigration and ext.any():
        raise AssertionError("Source immigration OFF produced outside individuals")
    if mode=="off" and (arrivals.any() or departures.any()):
        raise AssertionError("Movement OFF produced migrants")

    summaries, events = [], []
    was=H[:-1]
    now=H[1:]
    for i,row in enumerate(group.itertuples(index=False)):
        identity=dict(structure_id=str(row.structure_id),context=str(row.context),
                      plant_model=str(row.plant_model),
                      draw=int(row.draw),reverse_on=int(row.reverse_on),
                      vertex=int(row.vertex),scale=int(scale),seed=int(seed),
                      movement=mode,immigration=int(immigration),
                      years=int(years))
        for g,name in enumerate(GUILDS):
            a=was[:,i,:,g]
            b=now[:,i,:,g]
            extinct=(a>0)&(b==0)
            returned=(a==0)&(b>0)
            local_g=local[:,i,:,g]
            ext_g=ext[:,i,:,g]
            arr_g=arrivals[:,i,:,g]
            dep_g=departures[:,i,:,g]
            checks=int((b < 0).sum())
            if checks:
                raise AssertionError("Negative integer censuses")
            two_op=0
            two_birth=0
            three_op=0
            three_birth=0
            return_total=int(returned.sum())
            for y,p in zip(*np.where(returned)):
                census_year=int(y+1)
                observable=census_year+2<=years
                two=bool(observable and
                         H[census_year+1,i,p,g]>0 and
                         H[census_year+2,i,p,g]>0)
                # Interval following the return census: year t to t+1.
                follow_local=int(local[census_year,i,p,g]) if census_year<years else 0
                two_op+=int(two)
                two_birth+=int(two and follow_local>0)
                # The source F maturation delay can be three years;
                # immediate next-year local recruitment should NOT be
                # interpreted as an unbiased test of colonist reproduction.
                observable3=census_year+3<=years
                three=bool(observable3 and all(
                    H[census_year+k,i,p,g]>0 for k in (1,2,3)
                ))
                follow_local3=int(local[census_year:census_year+3,i,p,g].sum()) if observable3 else 0
                three_op+=int(three)
                three_birth+=int(three and follow_local3>0)
                # At a prior zero patch, the carryover term is zero.
                # Only recruits remaining *after* departing the patch
                # can be considered the local source of reoccupancy.
                local_stayed=max(0,int(local_g[y,p])-int(dep_g[y,p]))
                contributors=int(ext_g[y,p]>0)+int(arr_g[y,p]>0)+int(local_stayed>0)
                events.append(dict(**identity,guild=name,patch=int(p),
                      census_year=census_year,
                      count_at_return=int(b[y,p]),
                      immigrant_at_return=int(ext_g[y,p]),
                      moved_in_at_return=int(arr_g[y,p]),
                      local_due_recruits_at_return=int(local_g[y,p]),
                      local_due_recruits_remaining=int(local_stayed),
                      return_sources=contributors,
                      cause_label=("mixed" if contributors>1 else
                        "external" if ext_g[y,p]>0 else
                        "moved_between_patches" if arr_g[y,p]>0 else
                        "delayed_local_recruitment" if local_stayed>0 else
                        "unclassified"),
                      followup_2y_observable=int(observable),
                      occupied_both_followups=int(two),
                      post_return_local_recruits=int(follow_local),
                      operational_2y_reproduction=int(two and follow_local>0),
                      followup_3y_observable=int(observable3),
                      occupied_three_followups=int(three),
                      post_return_local_recruits_first3=int(follow_local3),
                      operational_3y_recruitment=int(three and follow_local3>0)))
            if three_birth>three_op or three_op>return_total or two_birth>two_op or two_op>return_total:
                raise AssertionError("Invalid post-return persistence")
            summaries.append(dict(**identity,guild=name,
                first_year_occupied_patches=int((H[0,i,:,g]>0).sum()),
                final_occupied_patches=int((H[-1,i,:,g]>0).sum()),
                final_individual_count=int(H[-1,i,:,g].sum()),
                mean_cohort_B_last_window=float(
                    H[max(0,years-WINDOW):years,i,:,g].mean()/scale),
                n_local_extinctions=int(extinct.sum()),
                n_local_returns=return_total,
                n_2y_observable_returns=int(
                    sum((y+1+2<=years) for y,p in zip(*np.where(returned)))),
                n_2y_persistent_returns=two_op,
                n_2y_persistent_with_recruitment=two_birth,
                n_3y_observable_returns=int(
                    sum((y+1+3<=years) for y,p in zip(*np.where(returned)))),
                n_3y_persistent_returns=three_op,
                n_3y_persistent_with_recruitment=three_birth,
                n_local_recruits=int(local_g.sum()),
                n_total_deaths=int(deaths[:,i,:,g].sum()),
                n_external_immigrants=int(ext_g.sum()),
                n_recorded_migration_arrivals=int(arr_g.sum()),
                n_recorded_migration_departures=int(dep_g.sum()),
                total_initial_plus_births_immigrants=int(
                    H[0,i,:,g].sum()+local_g.sum()+ext_g.sum()),
            ))
    summaries=pd.DataFrame(summaries)
    events=pd.DataFrame(events)
    return summaries,events


def run(*, years=YEARS, draws=1, seeds=SEEDS,
        scales=SCALES, immigration_states=(False,True),
        movement_modes=MOVEMENT_MODES, dt=DT):
    if not isinstance(years,int) or years < 4:
        raise ValueError("Years must include two annual follow-ups")
    if len(set(seeds))!=len(seeds) or len(seeds)<1:
        raise ValueError("Distinct random seed labels required")
    cube=source_cube(draws)
    # Assert original deterministic source match at full horizon first.
    replay=replay_gate(cube,years=years,window=min(WINDOW,years),dt=dt)
    rows,returns=[],[]
    for seed in seeds:
        for scale in scales:
            for im in immigration_states:
                for movement in movement_modes:
                    for (_,litter),g in cube.groupby(["risk","litter"],sort=True):
                        g=g.reset_index(drop=True)
                        source=simulate_finite_group(
                            g,scale=int(scale),seed=int(seed),
                            mode=movement,immigration=bool(im),
                            years=years,dt=dt
                        )
                        summary,events=summarize_finite_group(
                            g,source,scale=int(scale),seed=int(seed),
                            mode=movement,immigration=bool(im),years=years
                        )
                        rows.append(summary)
                        if len(events):returns.append(events)
                    print("FINITE_ARM_OK",seed,scale,int(im),movement,
                          "years",years,flush=True)
    summary=pd.concat(rows,ignore_index=True)
    events=(pd.concat(returns,ignore_index=True) if returns else
            pd.DataFrame(columns=["structure_id","draw","seed","guild"]))
    keys=["structure_id","draw","reverse_on","vertex","scale","seed",
          "movement","immigration","guild"]
    if summary.duplicated(keys).any():
        raise AssertionError("Finite run duplicated biological scenario identities")
    expected=len(cube)*len(seeds)*len(scales)*len(immigration_states)*len(movement_modes)*3
    if len(summary)!=expected:
        raise AssertionError(f"Lost finite guild/scenario combinations: {len(summary)} of {expected}")
    if int(summary.n_local_returns.sum())!=len(events):
        raise AssertionError("Return-event denominator and raw ledger disagree")
    OUT.mkdir(parents=True,exist_ok=True)
    summary.to_csv(OUT/"finite_seed_scenario_guild_summary.csv.gz",index=False,
         compression={"method":"gzip","mtime":0})
    events.to_csv(OUT/"finite_recolonization_followups.csv.gz",index=False,
         compression={"method":"gzip","mtime":0})
    grouped=(summary.groupby(["scale","immigration","movement","context","plant_model","guild"],
                              sort=True)
       .agg(n_seed_scenarios=("seed","size"),
            mean_final_occupied=("final_occupied_patches","mean"),
            mean_final_abundance=("final_individual_count","mean"),
            mean_local_extinctions=("n_local_extinctions","mean"),
            mean_local_returns=("n_local_returns","mean"),
            total_2y_observable_returns=("n_2y_observable_returns","sum"),
            total_2y_persistent=("n_2y_persistent_returns","sum"),
            total_2y_with_recruitment=("n_2y_persistent_with_recruitment","sum"),
            total_3y_observable_returns=("n_3y_observable_returns","sum"),
            total_3y_persistent=("n_3y_persistent_returns","sum"),
            total_3y_with_recruitment=("n_3y_persistent_with_recruitment","sum"),
            mean_external_immigrants=("n_external_immigrants","mean"))
       .reset_index())
    grouped.to_csv(OUT/"finite_aggregated_condition_summary.csv",index=False)
    receipt=dict(
       status="GENUINE_FINITE_N_SYNTHETIC_ANNUAL_COHORT_PILOT",
       source_replay_differences=replay,
       source_years=years,source_dt=dt,patches=PATCHES,
       finite_individual_count_scales=list(map(int,scales)),
       seeds=list(map(int,seeds)),
       immigration_states=list(map(bool,immigration_states)),
       movement_modes=list(movement_modes),
       cohort_source_cases=len(cube),
       finite_guild_scenario_records=len(summary),
       observed_actual_0_to_positive_events=len(events),
       total_yearly_returns=int(summary.n_local_returns.sum()),
       total_followup_2y_observable=int(summary.n_2y_observable_returns.sum()),
       total_followup_3y_observable=int(summary.n_3y_observable_returns.sum()),
       total_3y_persistent_with_recruitment=int(summary.n_3y_persistent_with_recruitment.sum()),
       annual_count_summaries_not_acoustic_or_parent_uid=True,
       source_trophic_kernel_directly_called=True,
       new_binomial_poisson_demographic_sampling=True,
       movement_diffusion_not_calibrated_to_PR147=True,
       true_field_recolonization_or_posterior=False,
       code_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    )
    (OUT/"receipt.json").write_text(json.dumps(receipt,indent=2)+"\n")
    print(json.dumps(receipt,indent=2),flush=True)
    print("FINITE_AGGREGATED_GUILD_F\n"+grouped[grouped.guild.eq("F")].to_string(index=False),flush=True)
    return summary,events,grouped,receipt


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--run",action="store_true")
    p.add_argument("--draws",type=int,default=1)
    p.add_argument("--years",type=int,default=YEARS)
    p.add_argument("--seeds",type=int,default=len(SEEDS))
    p.add_argument("--scales",type=int,nargs="+",default=SCALES)
    p.add_argument("--dt",type=float,default=DT)
    p.add_argument("--immigration",choices=("both","off","on"),default="both")
    a=p.parse_args()
    if not a.run:p.error("Explicit --run required")
    if a.seeds<1 or a.seeds>len(SEEDS):
        p.error("Choose 1..4 predeclared seed labels")
    immigration_states=((False,True) if a.immigration=="both" else
                        (False,) if a.immigration=="off" else (True,))
    run(years=a.years,draws=a.draws,seeds=SEEDS[:a.seeds],
        scales=tuple(a.scales),immigration_states=immigration_states,
        dt=a.dt)
