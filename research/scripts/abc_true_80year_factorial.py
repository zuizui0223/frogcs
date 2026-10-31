"""True 80-year 2x2x2 stage-network reruns under matched biological rate draws.

This is *vectorized bookkeeping* of the same seasonal
stage_network_extension_20261029.simulate kernel and delayed-recruitment
equation used by extension_annual_summary_20261029. A factual replay gate
compares both code paths and the archived baseline before ABC results count.

Per-row demography is vectorized because every process draw may have a
different maturation lag, annual survival and conversion; no ABM/PDE.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

from select_macro_trophic_scenarios import ROOT
from run_macro_process_prior_predictive import prior_draws,anchor_values,batch_simulate
from abc_intrinsic_factorial import (
    OUT,LEVELS,eight_corners,catalogue_structure,subset_corners,
    summarize_factorial,METRICS
)
from multiyear_stage_network import DEMOGRAPHY
from stage_network_extension_20261029 import simulate as seasonal

N_PRIOR_DRAWS=128
YEARS=80
WINDOW=20
DT=.25
BATCHES=12


def ensemble_rows(cases,draws,context,family):
    """8 model corners for each 128 true prior vectors x 4 original model cases."""
    select=cases[(cases.context==context)&(cases.family==family)].copy()
    if len(select)!=4 or select.risk.nunique()!=2 or set(select.edge)!={"dynamic","frog_reverse"}:
        raise ValueError("Incomplete original 3x2x2x2 model family")
    if draws.draw.duplicated().any():
        raise ValueError("Prior draw ids must be unique")
    points=pd.DataFrame(eight_corners(),columns=["vegetation","S_source","D_source"])
    select=select.assign(_x=1).merge(points.assign(_x=1),on="_x").drop(columns="_x")
    result=select.assign(_x=1).merge(draws.assign(_x=1),on="_x").drop(columns="_x")
    # Consistent unique identity: same continuous/delay prior draw for every
    # structure, risk condition and both reverse edge states.
    if result.duplicated(["draw","case","vegetation","S_source","D_source"]).any():
        raise AssertionError("Missing one-to-one prior process source")
    result["structural_class"]=[
        "|".join([str(r.context),str(r.family),
                  "refuge_on" if bool(r.risk) else "refuge_off"])
        for r in result.itertuples(index=False)]
    return result


def vectorized_annual(rows,years=YEARS,window=WINDOW,dt=DT):
    """Heterogeneous-rate but mathematically identical annual update equation."""
    if not (1<=window<=years) or not len(rows):
        raise ValueError("Invalid annual vectorized inputs")
    records=[]
    for risk,g in rows.groupby("risk",sort=True):
        g=g.reset_index(drop=True)
        n=len(g)
        params=[dict(community="FSD",roles=15,refuge_order="D",
                     vegetation=float(p.vegetation),f_arrival=20.,
                     s_arrival=float(p.sa),d_arrival=float(p.da),
                     attack_scale=float(p.attack_scale),cue=0.,
                     reverse=(p.edge=="frog_reverse"))
                for p in g.itertuples(index=False)]
        rates=g[["rho","conversion","f_juvenile_survival",
                 "f_adult_survival","f_delay"]].to_numpy(float)
        rho=rates[:,0,None]
        conversion=np.repeat(rates[:,1,None],3,axis=1)
        juvenile=np.column_stack([rates[:,2],np.full(n,.8),np.full(n,.8)])
        survival=np.column_stack([rates[:,3],np.full(n,.5),np.zeros(n)])
        m=np.column_stack([rates[:,4].astype(int),np.full(n,2),np.ones(n,int)])
        if not (np.isfinite(rates).all() and np.all((rho>=0)&(rho<=1))
                and np.all((survival>=0)&(survival<1))
                and np.all((juvenile>=0)&(juvenile<=1))
                and np.all((m>=1)&(m<=3))):
            raise ValueError("Malformed heterogeneous demographic prior rates")
        B=np.ones((n,3),float) * float(DEMOGRAPHY["initial_scale"])
        source=np.column_stack([np.ones(n),
                                g.S_source.to_numpy(float),
                                g.D_source.to_numpy(float)])
        K=float(DEMOGRAPHY["capacity"])
        immigration=(1-rho)*(1-survival)*source
        upper=np.maximum(B,(rho*conversion*K+immigration)/(1-survival))
        control=dict(cover_SF=1.,cover_DF=0.,cover_DS=0.,cover_SD=0.,
                     support_DF=0.,support_DS=0.,emerge_survival=0.,
                     emerge_exposure=0.,cue_SD=0.,edge_SD=np.ones(n),
                     edge_DS=np.ones(n))
        options=dict(stage_durations=np.column_stack(
                        [np.full(n,45.),np.full(n,80.),
                         g.dduration.to_numpy(float)]),
                     functional_response="litter",
                     behavioral_refuge=bool(risk),
                     handling_s=g.hs.to_numpy(float),
                     handling_d=g.hd.to_numpy(float),
                     s_growth=g.sg.to_numpy(float)*
                        g.s_growth_multiplier.to_numpy(float),
                     d_growth=g.dg.to_numpy(float)*
                        g.d_growth_multiplier.to_numpy(float),
                     sd_size_mode="dynamic",pathway_controls=control,
                     diagnostics=False)
        ring={};running=np.zeros(n);running_sq=np.zeros(n);survival_sum=np.zeros(n)
        for year in range(years):
            result=seasonal(params,dt=dt,initial_cohorts=B,**options)
            C=result[["F_completed","S_completed","D_completed"]].to_numpy(float)
            if not np.isfinite(C).all() or (C<0).any() or (C>B+1e-10).any():
                raise AssertionError("Invalid aquatic stage completion")
            ring[year]=C
            due=np.zeros_like(B)
            # maturation delay is row-specific: S=2, D=1, F=2/3.
            for guild in range(3):
                for lag in np.unique(m[:,guild]):
                    origin=year+1-int(lag)
                    if origin>=0:
                        match=m[:,guild]==lag
                        due[match,guild]=ring[origin][match,guild]
            local=rho*conversion*(juvenile**(m-1))*due/(1+due/K)
            following=survival*B+local+immigration
            if (not np.isfinite(following).all() or
                (following<0).any() or (following>upper+1e-10).any()):
                raise AssertionError("Same original delayed annual feedback bounds violated")
            for past in list(ring):
                if past<year+1-int(m.max()):
                    del ring[past]
            if year>=years-window:
                running+=B[:,0]
                running_sq+=B[:,0]*B[:,0]
                survival_sum+=C[:,0]/B[:,0]
            B=following
        output=g.copy()
        output["F_B"]=running/window
        output["F_B_sd"]=np.sqrt(
            np.maximum(0.,running_sq/window-(running/window)**2))
        output["F_fraction"]=survival_sum/window
        if (not np.isfinite(output[["F_B","F_fraction","F_B_sd"]].to_numpy(float)).all()
            or (output.F_B<=0).any()
            or (output.F_fraction<0).any()
            or (output.F_fraction>1+1e-10).any()):
            raise AssertionError("Nonfinite source-parameter outputs")
        records.append(output)
        print("REAL_80YEAR_VECTOR_BATCH risk",risk,"n_rows",n,
              "years",years,"model window",window,flush=True)
    joined=pd.concat(records,ignore_index=True)
    if len(joined)!=len(rows):
        raise AssertionError("Unaccounted real demographic rows")
    return joined


def compare_source_path(cases,context,family,years=4,window=2,dt=.5):
    """Nontrivial proof that vectorization preserves old time-lag equation."""
    first=cases[(cases.context==context)&(cases.family==family)]
    prior=pd.DataFrame([dict(**anchor_values())])
    grid=ensemble_rows(first,prior,context,family)
    old=batch_simulate(grid,anchor_values(),years=years,window=window,dt=dt)
    new=vectorized_annual(grid,years=years,window=window,dt=dt)
    key=["case","vegetation","S_source","D_source"]
    a=old.sort_values(key).reset_index(drop=True)
    b=new.sort_values(key).reset_index(drop=True)
    if len(a)!=len(b):
        raise AssertionError("Different season/annual clone size")
    err={}
    for name,limit in [("F_B",1e-9),("F_fraction",1e-9),("F_B_sd",1e-7)]:
        err[name]=float(np.max(np.abs(a[name].to_numpy(float)-b[name].to_numpy(float))))
        if err[name]>limit:
            raise AssertionError("Not exact original model dynamics "+name+" max "+str(err[name]))
    return err


def compare_archived_baseline(cases,context,family,dt=DT):
    """Reproduce actual frozen 80y corner surfaces exactly before ABC."""
    prior=pd.DataFrame([anchor_values()])
    samples=ensemble_rows(cases,prior,context,family)
    actual=vectorized_annual(samples,years=YEARS,window=WINDOW,dt=dt)
    original=pd.concat([pd.read_csv(path) for path in (
        ROOT/"research/results/literature_extension_20261029/primary_0_dynamic_cells.csv.gz",
        ROOT/"research/results/literature_extension_20261029/primary_1_dynamic_cells.csv.gz")])
    original=original[original.case.isin(samples.case)]
    original=subset_corners(original)
    key=["case","vegetation","S_source","D_source"]
    a=actual.sort_values(key).reset_index(drop=True)
    b=original.sort_values(key).reset_index(drop=True)
    if len(a)!=len(b) or not np.allclose(a[key],b[key],atol=1e-9,rtol=0):
        raise AssertionError("Real baseline source eight-corner index changed")
    errors={}
    for name,tol in (("F_B",1e-8),("F_fraction",1e-8),("F_B_sd",1e-7)):
        errors[name]=float(np.abs(a[name].to_numpy(float)-b[name].to_numpy(float)).max())
        if errors[name]>tol:raise AssertionError("Frozen genuine 80-y replay "+name)
    return errors


def run(context,family,draw_count=N_PRIOR_DRAWS):
    if draw_count%2 or draw_count<2:
        raise ValueError("Balanced maturity prior draws need even >=2 count")
    if context not in ("original","D_first_S_overtakes","S_first_D_overtakes"):
        raise ValueError("Unknown original context")
    if family not in ("baseline","shared_both"):
        raise ValueError("Unknown original sharing model")
    OUT.mkdir(parents=True,exist_ok=True)
    cases,_=catalogue_structure()
    structure=cases[(cases.context==context)&(cases.family==family)]
    same=compare_source_path(cases,context,family)
    baseline=compare_archived_baseline(cases,context,family)
    priors=prior_draws(draw_count)
    grid=ensemble_rows(cases,priors,context,family)
    result=vectorized_annual(grid)
    compact=summarize_factorial_per_draw(result)
    folder=f"{context}_{family}"
    compact.to_csv(OUT/(folder+"_real80y_sign_draws.csv"),index=False)
    priors.to_csv(OUT/(folder+"_shared_prior_draws.csv"),index=False)
    summary=compact.groupby(["scale","structural_class"]).agg(
        exact_matches=("matching_target","sum"),
        available_configs=("matching_target","size"),
        mean_n_signs=("n_matching_signs","mean")).reset_index()
    summary.to_csv(OUT/(folder+"_model_prior_acceptance_summary.csv"),index=False)
    receipt=dict(status="TRUE_STAGE_KERNEL_80YEAR_2X2X2_PROCESS_RATE_PRIORS",
                 context=context,family=family,prior_draws_per_edge=draw_count,
                 edge_variants=2,structural_classes=2,
                 source_cells=len(grid),timesteps_days_per_year=int(120/DT),
                 years=YEARS,last_year_window=WINDOW,dt=DT,
                 comparison_to_original_short_years=same,
                 original_80year_archived_corner_replay=baseline,
                 parameter_priors_empirically_calibrated=False,
                 adult_calling_bridge_inferred=False,
                 target_four_signs=[int(x) for x in (-1,-1,1,1)],
                 output_scales=["log_F_B","raw_F_B"],
                 source_hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
                                for p in [DESIGN]},
                 script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    (OUT/(folder+"_receipt.json")).write_text(
        json.dumps(receipt,indent=2,ensure_ascii=False)+"\n")
    print("PROCESS_80YEAR_PRIOR_ACCEPTANCE",context,family,
          summary.to_string(index=False),flush=True)
    return compact,summary,receipt


def summarize_factorial_per_draw(source):
    frame=[]
    for draw,part in source.groupby("draw"):
        s=summarize_factorial(part)
        s.insert(0,"draw",int(draw))
        structure=part[["case","context","family","risk","edge","structural_class"]].drop_duplicates("case")
        if structure.case.duplicated().any():
            raise ValueError("Repeated case metadata")
        frame.append(s.merge(structure,on="case",validate="many_to_one"))
    if not len(frame):
        raise ValueError("Missing demographic draws")
    out=pd.concat(frame,ignore_index=True)
    if out.duplicated(["draw","case","scale"]).any():
        raise AssertionError("Same factorial draw repeated")
    return out


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--run",action="store_true")
    parser.add_argument("--context",required=True)
    parser.add_argument("--family",required=True)
    parser.add_argument("--draws",type=int,default=N_PRIOR_DRAWS)
    args=parser.parse_args()
    if not args.run:parser.error("Explicit --run required")
    run(args.context,args.family,args.draws)
