"""Explicit plant-pathway ablations using ORIGINAL frogcs 80-year stage dynamics.

Comparison 12 legal vegetation roles from main's 3,600 model space, conditional
on the previous ABC's strongest original timing and baseline handling.

No original seasonal kernel or main code changes: annual bookkeeping is
source-copied from model_native_2x2x2_prior. A genuine fixed-plant 80-year
replay must pass before any signal ABC can be reported.
"""
from __future__ import annotations
import argparse
import hashlib
import itertools
import json
from pathlib import Path

import numpy as np
import pandas as pd
from stage_network_extension_20261029 import simulate as seasonal_kernel
from multiyear_stage_network import DEMOGRAPHY
from model_native_2x2x2_prior import (
    ROOT,OUT,DESIGN,SOURCES,N_DRAWS,YEARS,WINDOW,DT,EPS,TARGET,METRICS,
    model_names,cube_design,matching_prior_draws,annual_recurrence_batch,
    summarize_cube_output
)
from run_macro_process_prior_predictive import anchor_values

OUT=ROOT/"research/results/macro_intrinsic_factorial_abc_20261031"
PILOT_DRAWS=64
PLANT_FLAGS=("cover_SF","cover_DF","cover_DS","litter")
CONTEXT="original"
FAMILY="baseline"


def legal_plant_inventory():
    """Only main-catalog-realizable initial plant roles; no untested joint SF+DF+litter."""
    plants=[]
    for sf,df,ds,litter in itertools.product((0,1),repeat=4):
        if df and litter:
            continue  # documented main catalog: litter forces cover_DF=0
        name=f"SF{sf}_DF{df}_DS{ds}_L{litter}"
        plants.append(dict(plant_model=name,cover_SF=sf,
                           cover_DF=df,cover_DS=ds,litter=litter))
    out=pd.DataFrame(plants).sort_values(list(PLANT_FLAGS)).reset_index(drop=True)
    if len(out)!=12 or out.duplicated(list(PLANT_FLAGS)).any():
        raise AssertionError("Main's 12 legal plant subroles not complete")
    # Original existing true 80-year ABC fixed model is fully represented.
    if len(out[(out.cover_SF==1)&(out.cover_DF==0)&
               (out.cover_DS==0)&(out.litter==1)])!=1:
        raise AssertionError("Original ABC's plant function baseline missing")
    return out


def cross_plant_design(base,plants):
    """Duplicate exact original source cube under each plant-role treatment."""
    if base.empty or plants.empty:
        raise ValueError("No models or plant treatments")
    parts=[]
    for plant in plants.to_dict("records"):
        g=base.copy()
        for f in PLANT_FLAGS:g[f]=int(plant[f])
        g["plant_model"]=plant["plant_model"]
        g["structure_id"]=g["structure_id"].astype(str)+"__"+plant["plant_model"]
        parts.append(g)
    out=pd.concat(parts,ignore_index=True)
    key=["structure_id","draw","reverse_on","vertex"]
    if out.duplicated(key).any() or out.groupby(key[:-1]).vertex.nunique().ne(8).any():
        raise AssertionError("Incomplete original model-native 8-vertex factorial")
    return out


def confirm_baseline_against_original(models,years=YEARS,window=WINDOW,dt=DT):
    """Compare unchanged annual source with independently copied plant-mode recurrence."""
    prior=pd.DataFrame([anchor_values()])
    model=models[(models.context==CONTEXT)&(models.family==FAMILY)]
    grid=cube_design(model,prior,anchor_both_edges=True)
    plants=legal_plant_inventory()
    p=plants[(plants.cover_SF==1)&(plants.cover_DF==0)&
             (plants.cover_DS==0)&(plants.litter==1)]
    altered=cross_plant_design(grid,p)
    actual=annual_recurrence_plant(altered,years=years,window=window,dt=dt)
    original=annual_recurrence_batch(grid,years=years,window=window,dt=dt)
    key=["original_case","vegetation","S_source","D_source"]
    x=actual.sort_values(key).reset_index(drop=True)
    y=original.sort_values(key).reset_index(drop=True)
    if len(x)!=len(y) or not np.array_equal(x[key].to_numpy(float),y[key].to_numpy(float)):
        raise AssertionError("Source replay index mismatch")
    checks={}
    for k,limit in (("F_B",1e-8),("F_fraction",1e-8),("F_B_sd",1e-7)):
        e=float(np.max(abs(x[k].to_numpy(float)-y[k].to_numpy(float))))
        checks[k]=e
        if e>limit:raise AssertionError("Source annual baseline mismatch "+k+" err "+str(e))
    if years==YEARS and window==WINDOW and dt==DT:
        saved=pd.concat([pd.read_csv(p) for p in SOURCES],ignore_index=True)
        saved=saved[saved.case.isin(actual.original_case.unique())]
        saved=saved[(saved.S_source.isin((.25,2.)))&
                    (saved.D_source.isin((.25,2.)))]
        s=saved.rename(columns={"case":"original_case"}).sort_values(key).reset_index(drop=True)
        if len(s)!=len(x) or not np.allclose(s[key].to_numpy(float),
                                            x[key].to_numpy(float),atol=1e-9,rtol=0):
            raise AssertionError("Frozen 2026-10-29 baseline coords mismatch")
        for k,lim in (("F_B",1e-8),("F_fraction",1e-8),("F_B_sd",1e-7)):
            err=float(np.abs(s[k]-x[k]).max())
            checks["archive_"+k]=err
            if err>lim:raise AssertionError("Frozen 80-year source plant control not replayed")
    return checks


def main_catalog_audit(plants):
    full=pd.read_csv(ROOT/"research/results/final_mechanism_20261027/catalog.csv")
    if len(full)!=3600 or full.model_id.nunique()!=3600:
        raise AssertionError("main 3,600 model source catalog changed")
    axes=["cover_SF","cover_DF","cover_DS","cover_SD","litter",
          "support_DF","support_DS","survival","timing","edge_SD","edge_DS",
          "reverse","behavior"]
    rows=[]
    for col in axes:
        for value,count in sorted(full[col].value_counts().items(),key=lambda x:str(x[0])):
            rows.append(dict(axis=col,value=str(value),n_main_models=int(count)))
    role=[]
    for p in plants.itertuples(index=False):
        sub=full[(full.cover_SF==p.cover_SF)&
                 (full.cover_DF==p.cover_DF)&
                 (full.cover_DS==p.cover_DS)&
                 (full.litter==p.litter)]
        role.append(dict(plant_model=p.plant_model,
                         cover_SF=p.cover_SF,cover_DF=p.cover_DF,
                         cover_DS=p.cover_DS,litter=p.litter,
                         matching_main_3600_models=len(sub)))
    return pd.DataFrame(rows),pd.DataFrame(role)


def annual_recurrence_plant(cube,years=YEARS,window=WINDOW,dt=DT):
    """Batched but EXACT old seasonal network and demographic difference equations.

    Variable survival/juvenile/maturation priors are per draw, not a single
    scalar globally. F immature delays 2/3, S2, D1 are explicitly lagged.
    Old demographic recursion is source-checked at baseline for every case.
    """
    if len(cube)<8 or not 1<=window<=years or dt<=0:
        raise ValueError("Invalid cohort model horizon or grid")
    outputs=[]
    for (risk,litter),g in cube.groupby(["risk","litter"],sort=True):
        g=g.reset_index(drop=True)
        n=len(g)
        params=[dict(community="FSD",roles=15,refuge_order="D",
                     vegetation=float(r.vegetation),f_arrival=20.,
                     s_arrival=float(r.sa),d_arrival=float(r.da),
                     attack_scale=float(r.attack_scale),cue=0.,
                     reverse=bool(r.reverse_on))
                for r in g.itertuples(index=False)]
        opts=dict(
            stage_durations=np.column_stack([np.full(n,45.),np.full(n,80.),
                                              g.dduration.to_numpy(float)]),
            functional_response=("litter" if bool(litter) else None),behavioral_refuge=bool(risk),
            handling_s=g.hs.to_numpy(float),handling_d=g.hd.to_numpy(float),
            s_growth=g.sg.to_numpy(float),d_growth=g.dg.to_numpy(float),
            sd_size_mode="dynamic",
            pathway_controls=dict(
                cover_SF=g.cover_SF.to_numpy(float),
                cover_DF=g.cover_DF.to_numpy(float),
                cover_DS=g.cover_DS.to_numpy(float),
                cover_SD=np.zeros(n),
                support_DF=np.zeros(n),support_DS=np.zeros(n),
                emerge_survival=np.zeros(n),emerge_exposure=np.zeros(n),
                cue_SD=np.zeros(n),edge_SD=np.ones(n),edge_DS=np.ones(n)))
        source=np.column_stack([np.ones(n),g.S_source.to_numpy(float),
                                g.D_source.to_numpy(float)])
        rho=g.rho.to_numpy(float)[:,None]
        survival=np.column_stack([g.f_adult_survival.to_numpy(float),
                                  np.full(n,.5),np.zeros(n)])
        conversion=np.broadcast_to(g.conversion.to_numpy(float)[:,None],
                                   (n,3)).copy()
        juvenile=np.column_stack([g.f_juvenile_survival.to_numpy(float),
                                  np.full(n,.8),np.full(n,.8)])
        delays=np.column_stack([g.f_delay.to_numpy(int),
                                np.full(n,2,int),np.ones(n,int)])
        if (survival>=1).any() or (survival<0).any() or (juvenile>1).any() or (juvenile<0).any():
            raise ValueError("Invalid synthetic survival priors")
        if not np.isin(delays[:,0],[2,3]).all():
            raise ValueError("F delay must be exactly 2 or 3 years")
        K=float(DEMOGRAPHY["capacity"])
        immigrant=(1-rho)*(1-survival)*source
        B=np.ones_like(source)*float(DEMOGRAPHY["initial_scale"])
        upper=np.maximum(B,(rho*conversion*K+immigrant)/(1-survival))
        previous1=np.zeros_like(B)
        previous2=np.zeros_like(B)
        sum_B=np.zeros(n);sum_frac=np.zeros(n);sum_B2=np.zeros(n)
        for year in range(years):
            out=seasonal_kernel(params,dt=dt,initial_cohorts=B,**opts)
            C=out[["F_completed","S_completed","D_completed"]].to_numpy(float)
            if not np.isfinite(C).all() or (C<0).any():
                raise AssertionError("Invalid seasonal metamorph completion")
            due=np.empty_like(C)
            due[:,0]=np.where(delays[:,0]==2,previous1[:,0],previous2[:,0])
            due[:,1]=previous1[:,1]
            due[:,2]=C[:,2]
            local=rho*conversion*juvenile**(delays-1)*due/(1+due/K)
            nxt=survival*B+local+immigrant
            if not np.isfinite(nxt).all() or (nxt<0).any() or (nxt>upper+1e-10).any():
                raise AssertionError("Original annual maturation/recruitment mass bounds violated")
            if year>=years-window:
                sum_B+=B[:,0]
                sum_B2+=B[:,0]**2
                sum_frac+=np.divide(C[:,0],B[:,0],
                                    out=np.ones(n,float),where=B[:,0]>0)
            previous2,previous1=previous1,C
            B=nxt
            if (year+1)%20==0:
                print("ANNUAL_COMPLETED",str(g.risk.iloc[0]),year+1,
                      "of",years,"n_vertices",n,flush=True)
        result=g[["structure_id","context","family","risk","original_case",
                  "reverse_on","draw","vertex","vegetation","S_source","D_source",
                  "plant_model","cover_SF","cover_DF","cover_DS","litter"]].copy()
        result["F_B"]=sum_B/window
        result["F_fraction"]=sum_frac/window
        result["F_B_sd"]=np.sqrt(np.maximum(0,sum_B2/window-result.F_B.to_numpy(float)**2))
        if not np.isfinite(result[["F_B","F_fraction","F_B_sd"]].to_numpy(float)).all():
            raise AssertionError("Nonfinite model readouts")
        if (result.F_B<=0).any() or not result.F_fraction.between(0,1).all():
            raise AssertionError("Nonnatural synthetic F cohort outcome")
        outputs.append(result)
    data=pd.concat(outputs,ignore_index=True)
    if len(data)!=len(cube):
        raise AssertionError("Lost treatment rows in annual demographic integration")
    return data



def run(cover_sf,litter,n=PILOT_DRAWS):
    if cover_sf not in (0,1) or litter not in (0,1) or n<4 or n%2:
        raise ValueError("Fixed vegetation scenario and even prior count required")
    OUT.mkdir(parents=True,exist_ok=True)
    designs=pd.read_csv(DESIGN)
    models=model_names(designs)
    # True long-horizon original baseline replay occurs in every independent
    # process shard BEFORE testing any additional plant role.
    anchor=confirm_baseline_against_original(models)
    prior=matching_prior_draws(n)
    selected=models[(models.context==CONTEXT)&(models.family==FAMILY)]
    if len(selected)!=2:
        raise AssertionError("Risk OFF/ON base structural pair missing")
    plants=legal_plant_inventory()
    plants=plants[(plants.cover_SF==cover_sf)&(plants.litter==litter)]
    cube=cross_plant_design(cube_design(selected,prior),plants)
    simulation=annual_recurrence_plant(cube)
    scores=summarize_cube_output(simulation)
    if len(scores)!=len(plants)*2*n*2:
        raise AssertionError("Missing all 80-year plant/parameter/edge outputs")
    flags=simulation[["structure_id","plant_model","cover_SF","cover_DF",
                      "cover_DS","litter"]].drop_duplicates("structure_id")
    scores=scores.merge(flags,on="structure_id",validate="many_to_one")
    if scores.duplicated(["structure_id","draw","reverse_on"]).any():
        raise AssertionError("Duplicate 80y source scenario/parameter")
    spec=f"SF{cover_sf}_L{litter}"
    scores.to_csv(OUT/(spec+"_prior_vegetation_signs.csv.gz"),index=False,
                  compression={"method":"gzip","mtime":0})
    prior.to_csv(OUT/(spec+"_rate_draws.csv"),index=False)
    n_full=int(scores.matches_log.sum())
    chart=(scores.groupby(["plant_model","risk"]).agg(
        n_simulated=("matches_log","size"),
        accepted_log=("matches_log","sum"),
        accepted_raw=("matches_raw","sum")).reset_index())
    chart["acceptance_log"]=chart.accepted_log/chart.n_simulated
    chart["acceptance_raw"]=chart.accepted_raw/chart.n_simulated
    chart.to_csv(OUT/(spec+"_plant_pom_summary.csv"),index=False)
    if cover_sf==0 and litter==0:
        axes,roles=main_catalog_audit(legal_plant_inventory())
        axes.to_csv(OUT/"main_3600_model_axis_inventory.csv",index=False)
        roles.to_csv(OUT/"plant_roles_in_main_3600.csv",index=False)
    receipt=dict(status="FULL_TRUE_80Y_VEGETATION_ROLE_PILOT_NOT_FULL_3600_ABC",
                 role_shard=spec,source_context=CONTEXT,source_handling=FAMILY,
                 n_prior_vectors=n,n_reversal_edge_states=2,n_plant_scenarios=len(plants),
                 n_risk_structures=2,
                 n_80year_process_runs=len(scores),n_8vertex_treatment_cells=len(simulation),
                 original_full_80year_archive_replay=anchor,
                 original_kernel_unchanged=True,
                 scenario_prior_calibrated_from_field=False,
                 main_3600_exhaustively_run=False,
                 source_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
                                for p in [DESIGN,*SOURCES,
                                          ROOT/"research/results/final_mechanism_20261027/catalog.csv"]},
                 script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    (OUT/(spec+"_receipt.json")).write_text(
        json.dumps(receipt,indent=2,ensure_ascii=False)+"\n")
    print("MAIN_VEGETATION_80Y_POM",spec,"full matches",n_full,"of",len(scores),flush=True)
    print(chart.to_string(index=False),flush=True)
    return scores,chart,receipt


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--run",action="store_true")
    parser.add_argument("--cover-sf",type=int,required=True)
    parser.add_argument("--litter",type=int,required=True)
    parser.add_argument("--draws",type=int,default=PILOT_DRAWS)
    args=parser.parse_args()
    if not args.run:parser.error("Explicit --run required")
    run(args.cover_sf,args.litter,args.draws)
