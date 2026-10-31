"""Recompute correct annual stage outputs for fixed 24 literature-extension cases.

This reuses the UNCHANGED stage_network_extension_20261029 seasonal kernel and
annual demographic recurrence. It must reproduce saved mean F_B, F_fraction,
F_B_sd BEFORE its new mean F_C endpoint is accepted. No new model parameters.
"""
from __future__ import annotations
import argparse
import hashlib
import itertools
import json
from pathlib import Path

import numpy as np
import pandas as pd

from multiyear_stage_network import DEMOGRAPHY
from stage_network_extension_20261029 import DEFAULT, simulate
from select_macro_trophic_scenarios import ROOT, SOURCES, LEVELS, CONTEXTS, FAMILIES, EDGES

DESIGN=ROOT/"research/results/literature_extension_20261029/design.csv"
OUT=ROOT/"research/results/macro_scenario_selection_20261031/stage_readouts"
REQUIRED=("context","family","risk","edge","case")


def selected_design(spec):
    needed=spec[spec.context.isin(CONTEXTS)&spec.family.isin(FAMILIES)&
                spec.edge.isin(EDGES)].sort_values("case").reset_index(drop=True)
    if len(needed)!=24 or needed.case.duplicated().any():
        raise ValueError("Expected exactly 24 existing cases")
    if not set(needed.context)==set(CONTEXTS) or not set(needed.family)==set(FAMILIES):
        raise ValueError("Missing preregistered stage conditions")
    combos=needed.groupby(["context","family","risk","edge"]).size()
    if len(combos)!=24 or not combos.eq(1).all():
        raise ValueError("Duplicate or incomplete stage scenario combinations")
    return needed


def source_grid(spec, levels=LEVELS):
    if levels<2:raise ValueError("Source grid needs >=2 density levels")
    axes=np.linspace(.25,2.,levels)
    records=[]
    for row in spec.to_dict("records"):
        for v,s,d in itertools.product((0.,1.),axes,axes):
            records.append(dict(**row,vegetation=v,S_source=s,D_source=d))
    out=pd.DataFrame(records)
    if out.duplicated(["case","vegetation","S_source","D_source"]).any():
        raise AssertionError("Source design duplicate")
    return out


def replay_group(g, years=80, window=20, dt=.25):
    """Group must have identical behavior; cohort replay accounting is per cell."""
    if len(g)==0 or g.risk.nunique()!=1:
        raise ValueError("Group requires a single risk response")
    if not 1<=window<=years:
        raise ValueError("Invalid averaging window")
    g=g.reset_index(drop=True)
    n=len(g)
    params=[dict(community="FSD",roles=15,refuge_order="D",
                 vegetation=float(row.vegetation),f_arrival=20.,
                 s_arrival=float(row.sa),d_arrival=float(row.da),
                 attack_scale=.5,cue=0.,reverse=bool(row.edge=="frog_reverse"),
                 rho=.75) for row in g.itertuples()]
    params_kernel=[{k:v for k,v in row.items() if k!="rho"} for row in params]
    controls=dict(cover_SF=1.,cover_DF=0.,cover_DS=0.,cover_SD=0.,
                  support_DF=0.,support_DS=0.,emerge_survival=0.,
                  emerge_exposure=0.,cue_SD=0.,edge_SD=np.ones(n),
                  edge_DS=np.ones(n))
    options=dict(stage_durations=np.column_stack([np.full(n,45.),
                                                  np.full(n,80.),g.dduration.to_numpy(float)]),
                 functional_response="litter",behavioral_refuge=bool(g.risk.iloc[0]),
                 handling_s=g.hs.to_numpy(float),handling_d=g.hd.to_numpy(float),
                 s_growth=g.sg.to_numpy(float),d_growth=g.dg.to_numpy(float),
                 sd_size_mode="dynamic")
    m=np.asarray(DEMOGRAPHY["delays"],int)
    surv=np.asarray(DEMOGRAPHY["survival"],float)
    convert=np.asarray(DEMOGRAPHY["conversion"],float)
    juvenile=np.asarray(DEMOGRAPHY["juvenile"],float)
    capacity=float(DEMOGRAPHY["capacity"])
    rho=np.full((n,1),.75)
    source=np.column_stack([np.ones(n),g.S_source.to_numpy(float),g.D_source.to_numpy(float)])
    B=np.ones_like(source)
    immigrant=(1-rho)*(1-surv)*source
    upper=np.maximum(B,(rho*convert*capacity+immigrant)/(1-surv))
    ring={}
    sum_B=np.zeros(n);sum_C=np.zeros(n);sum_fraction=np.zeros(n)
    sum_B2=np.zeros(n);sum_C2=np.zeros(n);sum_frac2=np.zeros(n)
    sum_local=np.zeros(n)
    min_survival=np.ones(n)
    for year in range(years):
        season=simulate(params_kernel,dt=dt,initial_cohorts=B,diagnostics=False,
                        pathway_controls=controls,**options)
        C=season[["F_completed","S_completed","D_completed"]].to_numpy(float)
        if not np.isfinite(C).all() or (C<0).any() or (C>B+1e-10).any():
            raise AssertionError("Invalid season completed cohort or survival bound")
        fraction=C[:,0]/B[:,0]
        ring[year]=C
        due=np.zeros_like(B)
        for guild in range(3):
            origin=year+1-m[guild]
            if origin>=0:due[:,guild]=ring[origin][:,guild]
        local=rho*convert*(juvenile**(m-1))*due/(1+due/capacity)
        next_B=surv*B+local+immigrant
        if not np.isfinite(next_B).all() or (next_B<0).any() or (next_B>upper+1e-10).any():
            raise AssertionError("Annual recruitment bounds violated")
        for key in list(ring):
            if key<year+1-int(max(m)):del ring[key]
        if year>=years-window:
            fB=B[:,0]
            fC=C[:,0]
            sum_B+=fB;sum_C+=fC;sum_fraction+=fraction
            sum_B2+=fB*fB;sum_C2+=fC*fC;sum_frac2+=fraction*fraction
            sum_local+=local[:,0]
            min_survival=np.minimum(min_survival,fraction)
        B=next_B
    mean_B=sum_B/window;mean_C=sum_C/window;mean_fraction=sum_fraction/window
    covariance=mean_C-mean_B*mean_fraction
    return pd.DataFrame(dict(case=g.case.to_numpy(int),
                vegetation=g.vegetation.to_numpy(float),
                S_source=g.S_source.to_numpy(float),D_source=g.D_source.to_numpy(float),
                F_B=mean_B,F_fraction=mean_fraction,F_C=mean_C,
                F_local_recruits_mean=sum_local/window,
                F_B_sd=np.sqrt(np.maximum(0.,sum_B2/window-mean_B**2)),
                F_C_sd=np.sqrt(np.maximum(0.,sum_C2/window-mean_C**2)),
                F_fraction_sd=np.sqrt(np.maximum(0.,sum_frac2/window-mean_fraction**2)),
                F_B_fraction_cov=covariance,
                F_C_minus_product_of_means=covariance,
                min_F_fraction=min_survival))


def replay_saved(readouts, saved_sources, atol=1e-9):
    frozen=pd.concat(saved_sources,ignore_index=True)
    key=["case","vegetation","S_source","D_source"]
    if readouts.duplicated(key).any() or frozen.duplicated(key).any():
        raise ValueError("Duplicate source/replay key")
    left=readouts.sort_values(key).reset_index(drop=True)
    right=frozen[frozen.case.isin(readouts.case.unique())].sort_values(key).reset_index(drop=True)
    if len(left)!=len(right) or not np.allclose(left[key].to_numpy(float),right[key].to_numpy(float),
                                                atol=1e-10,rtol=0):
        raise AssertionError("Source-to-replay design mismatch")
    maximum={}
    for col in ("F_B","F_fraction","F_B_sd"):
        delta=float(np.max(np.abs(left[col].to_numpy(float)-right[col].to_numpy(float))))
        maximum[col]=delta
        if delta>atol:
            raise AssertionError(f"Frozen annual summary replay failed: {col} maxerror={delta}")
    if np.any(readouts.F_C<0) or np.any(readouts.F_fraction<0) or np.any(readouts.F_fraction>1+1e-10):
        raise AssertionError("Bad completed cohort values")
    return maximum


def run(out=OUT, years=80, window=20, dt=.25):
    if years!=80 or window!=20 or dt!=.25:
        raise ValueError("Source-backed comparisons use exact frozen 80y/20y/dt.25")
    out.mkdir(parents=True,exist_ok=True)
    spec=selected_design(pd.read_csv(DESIGN))
    grid=source_grid(spec)
    frames=[]
    for risk,g in grid.groupby("risk",sort=True):
        print("ANNUAL REPLAY",risk,"cells",len(g),flush=True)
        result=replay_group(g,years=years,window=window,dt=dt)
        frames.append(result)
        print("COMPLETE",risk,flush=True)
    readouts=pd.concat(frames,ignore_index=True).sort_values(
        ["case","vegetation","S_source","D_source"]).reset_index(drop=True)
    if len(readouts)!=24*2*LEVELS**2:
        raise AssertionError("Wrong stage surface total")
    frozen=[pd.read_csv(path) for path in SOURCES]
    errors=replay_saved(readouts,frozen)
    readouts.to_csv(out/"stage_readout_cells.csv.gz",index=False,
                    compression={"method":"gzip","mtime":0})
    percase=readouts.groupby("case").agg(
        mean_F_B=("F_B","mean"),mean_F_C=("F_C","mean"),
        mean_fraction=("F_fraction","mean"),
        mean_abs_B_fraction_cov=("F_B_fraction_cov",lambda a:float(np.mean(np.abs(a)))),
        max_abs_B_fraction_cov=("F_B_fraction_cov",lambda a:float(np.max(np.abs(a)))),
        min_survival=("min_F_fraction","min"),max_survival=("F_fraction","max")).reset_index()
    percase.to_csv(out/"case_readout_summary.csv",index=False)
    receipt=dict(status="ANNUAL_STAGE_READOUT_REPLAY_NOT_FIELD_CALIBRATION",
                 original_80year_surfaces_replayed_exactly=True,source_error_max=errors,
                 cells=len(readouts),cases=24,levels=LEVELS,years=years,window=window,dt=dt,
                 readouts=["F_B","F_C","F_fraction"],
                 F_C_mean_definition="mean over last 20 years of actual model seasonal F_completed; NOT product of mean_B and mean_fraction",
                 maturity_note="F_C is aquatic metamorph completion, not observed mature singing adult males",
                 lag_note="No explicit temporal lag estimated from 20-year average surfaces",
                 source_sha256={str(path.relative_to(ROOT)):hashlib.sha256(path.read_bytes()).hexdigest()
                                for path in [DESIGN]+SOURCES},
                 script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    (out/"stage_readout_replay_receipt.json").write_text(json.dumps(receipt,indent=2)+"\n")
    print("REPLAY ERRORS",json.dumps(errors),flush=True)
    print("CASE STAGE OUTPUTS\n"+percase.to_string(index=False),flush=True)
    return readouts,percase,receipt


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--run",action="store_true")
    arg=p.parse_args()
    if not arg.run:p.error("Explicit --run required")
    run()
