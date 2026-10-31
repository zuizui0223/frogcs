"""Full 80-year frogcs stage-network prior predictive on model-native 2x2x2 cubes.

Each of 12 structural classes gets SAME 256 predeclared hypothetical rate
draws, with BOTH frog-postmetamorph→emerging-D reversal ON/OFF outcomes
evaluated at every draw, then integrated with exactly equal prior weight.
Vectorized annual dynamics are numerically checked against the ORIGINAL
unmodified extension_annual_summary_20261029 model at 24 scenario x 8 corners.

No field-site transport, O/S SDM suitability, acoustic noise, arbitrary posterior.
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
from run_macro_process_prior_predictive import (
    DESIGN, SOURCES, prior_draws, anchor_values,
    CONTEXTS, FAMILIES, EDGES,
)
from select_macro_trophic_scenarios import ROOT

OUT=ROOT/"research/results/model_native_abc_rf_20261031"
N_DRAWS=256
YEARS=80
WINDOW=20
DT=.25
EPS=1e-9
TARGET=(-1,-1,1,1)
METRICS=("OS","OV","SV","OSV")
VERTICES=np.asarray([(v,s,d) for v in (0,1) for s in (0,1) for d in (0,1)],dtype=int)
CONTEXT_LABELS={"original":"original",
                "D_first_S_overtakes":"D_first_S_overtakes",
                "S_first_D_overtakes":"S_first_D_overtakes"}


def model_names(design):
    p=design[design.context.isin(CONTEXTS)&design.family.isin(FAMILIES)&
             design.edge.isin(EDGES)].copy()
    if len(p)!=24 or p.duplicated(["context","family","risk","edge"]).any():
        raise ValueError("Frozen 24-case ontogeny model catalog incomplete")
    classes=[]
    for (context,family,risk),part in p.groupby(["context","family","risk"],sort=True):
        if set(part.edge)!=set(EDGES) or len(part)!=2:
            raise AssertionError("Model cannot balance original/FO reversal")
        row=part[part.edge=="dynamic"].iloc[0]
        edge_on=part[part.edge=="frog_reverse"].iloc[0]
        for col in ("sa","da","sg","dg","dduration","hs","hd"):
            if not np.isclose(row[col],edge_on[col]):
                raise AssertionError("Reverse predator change also changed another structural parameter")
        classes.append(dict(structure_id=f"{context}__{family}__risk{int(risk)}",
                            context=context,family=family,risk=bool(risk),
                            case_off=int(row.case),case_on=int(edge_on.case),
                            sa=float(row.sa),da=float(row.da),
                            sg=float(row.sg),dg=float(row.dg),
                            hs=float(row.hs),hd=float(row.hd),
                            dduration=float(row.dduration)))
    if len(classes)!=12 or len({x["structure_id"] for x in classes})!=12:
        raise AssertionError("Wrong structural class count")
    return pd.DataFrame(classes)


def matching_prior_draws(n=N_DRAWS,seed=20261031):
    x=prior_draws(n,seed=seed)
    if len(x)!=n:raise AssertionError("Incomplete real process prior")
    # Reverse predation is integrated by *paired* full simulation at each
    # rate draw (0.5 each), avoiding finite-nuisance sampling noise.
    return x


def cube_design(structures,draws,anchor_both_edges=False):
    records=[]
    for struct in structures.to_dict("records"):
        for theta in draws.to_dict("records"):
            edges=(False,True)  # exact 0.5/0.5 latent-edge prior at every draw
            for reverse in edges:
                for vertex,(v,s,d) in enumerate(VERTICES):
                    records.append(dict(
                        structure_id=struct["structure_id"],context=struct["context"],
                        family=struct["family"],risk=bool(struct["risk"]),
                        original_case=struct["case_on"] if reverse else struct["case_off"],
                        reverse_on=int(reverse),draw=int(theta["draw"]),vertex=vertex,
                        vegetation=float(v),S_source=.25 if s==0 else 2.,
                        D_source=.25 if d==0 else 2.,
                        sa=struct["sa"],da=struct["da"],
                        sg=struct["sg"]*theta["s_growth_multiplier"],
                        dg=struct["dg"]*theta["d_growth_multiplier"],
                        hs=struct["hs"],hd=struct["hd"],dduration=struct["dduration"],
                        attack_scale=theta["attack_scale"],rho=theta["rho"],
                        conversion=theta["conversion"],
                        f_juvenile_survival=theta["f_juvenile_survival"],
                        f_adult_survival=theta["f_adult_survival"],
                        f_delay=int(theta["f_delay"])))
    frame=pd.DataFrame(records)
    unit=["structure_id","draw","reverse_on"]
    counts=frame.groupby(unit).vertex.agg(["nunique","size"])
    if not counts["nunique"].eq(8).all() or not counts["size"].eq(8).all():
        raise AssertionError("Missing or duplicate factorial treatment vertex")
    return frame


def annual_recurrence_batch(cube,years=YEARS,window=WINDOW,dt=DT):
    """Batched but EXACT old seasonal network and demographic difference equations.

    Variable survival/juvenile/maturation priors are per draw, not a single
    scalar globally. F immature delays 2/3, S2, D1 are explicitly lagged.
    Old demographic recursion is source-checked at baseline for every case.
    """
    if len(cube)<8 or not 1<=window<=years or dt<=0:
        raise ValueError("Invalid cohort model horizon or grid")
    outputs=[]
    for risk,g in cube.groupby("risk",sort=True):
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
            functional_response="litter",behavioral_refuge=bool(risk),
            handling_s=g.hs.to_numpy(float),handling_d=g.hd.to_numpy(float),
            s_growth=g.sg.to_numpy(float),d_growth=g.dg.to_numpy(float),
            sd_size_mode="dynamic",
            pathway_controls=dict(cover_SF=1.,cover_DF=0.,cover_DS=0.,cover_SD=0.,
                support_DF=0.,support_DS=0.,emerge_survival=0.,emerge_exposure=0.,
                cue_SD=0.,edge_SD=np.ones(n),edge_DS=np.ones(n)))
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
                  "reverse_on","draw","vertex","vegetation","S_source","D_source"]].copy()
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


def four_contrasts(corners):
    """Balanced orthogonal factorial 2^3 contrasts, deterministic and scaled.

    index order is V, S, D; average over the irrelevant third axis for all
    two-way effects. OSV is the unaveraged three-way difference.
    """
    y=np.asarray(corners,float)
    if y.shape!=(2,2,2) or not np.isfinite(y).all():
        raise ValueError("2x2x2 finite source field required")
    dd=y[:,:,1]-y[:,:,0]       # (V,S)
    ss=y[:,1,:]-y[:,0,:]       # (V,D)
    os=float(np.mean(dd[:,1]-dd[:,0]))
    ov=float(np.mean(dd[1,:]-dd[0,:]))
    sv=float(np.mean(ss[1,:]-ss[0,:]))
    osv=float((dd[1,1]-dd[1,0])-(dd[0,1]-dd[0,0]))
    return np.asarray([os,ov,sv,osv],float)


def categorized_sign(values,epsilon=EPS):
    x=np.asarray(values,float)
    if not np.isfinite(x).all() or epsilon<0:
        raise ValueError("Nonfinite or incorrect contrast threshold")
    return np.where(x>epsilon,1,np.where(x < -epsilon,-1,0)).astype(int)


def summarize_cube_output(results,epsilon=EPS):
    records=[]
    for (structure,draw,reverse),g in results.groupby(
            ["structure_id","draw","reverse_on"],sort=True):
        if len(g)!=8 or g.vertex.nunique()!=8 or set(g.vertex)!=set(range(8)):
            raise AssertionError("Lost model-native factorial grid cell")
        g=g.sort_values("vertex")
        cube=g.F_B.to_numpy(float).reshape(2,2,2)
        if np.any(cube<=0):
            raise AssertionError("log(F_B) undefined")
        row=g.iloc[0]
        rec=dict(structure_id=structure,context=row.context,
                 family=row.family,risk=bool(row.risk),
                 reverse_on=int(row.reverse_on),
                 original_case=int(row.original_case),draw=int(draw),
                 min_F_B=float(cube.min()),max_F_B=float(cube.max()))
        for mode,data in (("log",np.log(cube)),("raw",cube)):
            delta=four_contrasts(data)
            signs=categorized_sign(delta,epsilon=epsilon)
            for k,name in enumerate(METRICS):
                rec["beta_"+mode+"_"+name]=float(delta[k])
                rec["sign_"+mode+"_"+name]=int(signs[k])
            rec["matches_"+mode]=bool(np.array_equal(signs,np.asarray(TARGET)))
            rec["pattern_"+mode]="".join(str(int(s)) for s in signs)
            for alternative in (1e-11,1e-7):
                suffix=("strict11" if alternative==1e-11 else "loose7")
                rec["matches_"+mode+"_"+suffix]=bool(np.array_equal(
                    categorized_sign(delta,epsilon=alternative),TARGET))
        records.append(rec)
    a=pd.DataFrame(records)
    if a.duplicated(["structure_id","draw","reverse_on"]).any():
        raise AssertionError("Duplicate model/parameter draw summary")
    return a


def verify_fixed_original_24_corner_cases(design,archive,dt=DT):
    structures=model_names(design)
    prior=pd.DataFrame([dict(**anchor_values(),reverse_on=0)])
    cube=cube_design(structures,prior,anchor_both_edges=True)
    sim=annual_recurrence_batch(cube,years=YEARS,window=WINDOW,dt=dt)
    saved=pd.concat(archive,ignore_index=True)
    key=["original_case","vegetation","S_source","D_source"]
    old=saved.rename(columns={"case":"original_case"})
    old=old[(old.S_source.isin((.25,2.)))&(old.D_source.isin((.25,2.)))&
            old.original_case.isin(sim.original_case.unique())]
    x=sim.sort_values(key).reset_index(drop=True)
    y=old.sort_values(key).reset_index(drop=True)
    if len(x)!=24*8 or len(y)!=24*8:
        raise AssertionError("Original 24×8 treatment vertices not available")
    if not np.allclose(x[key].to_numpy(float),y[key].to_numpy(float),
                       atol=1e-10,rtol=0):
        raise AssertionError("Original 24 original case × 8 vertex coordinates mismatch")
    checks={}
    for var,tol in (("F_B",1e-8),("F_fraction",1e-8),("F_B_sd",1e-7)):
        error=float(np.max(np.abs(x[var].to_numpy(float)-y[var].to_numpy(float))))
        checks[var]=error
        if error>tol:
            raise AssertionError("Original 80-year stage/annual model replay failed "+var+
                                 " max error "+str(error))
    return sim,checks


def run(context,n=N_DRAWS,out=OUT):
    if context not in CONTEXTS or n<4 or n%2:
        raise ValueError("Need specified ontogeny context and even N>=4")
    if not (YEARS==80 and WINDOW==20 and DT==.25):
        raise AssertionError("Default source year/kernel changed")
    out.mkdir(parents=True,exist_ok=True)
    design=pd.read_csv(DESIGN)
    models=model_names(design)
    saved=[pd.read_csv(p) for p in SOURCES]
    original,checks=verify_fixed_original_24_corner_cases(design,saved)
    print("VERIFIED_SOURCE_REPLAY",checks,flush=True)
    selected=models[models.context==context].copy()
    if len(selected)!=4:
        raise AssertionError("Each context must have 2 handling ×2 refuge")
    priors=matching_prior_draws(n)
    cube=cube_design(selected,priors)
    print("FULL_80_YEAR_ABC_START",context,"rows",len(cube),
          "structure_classes",len(selected),"prior_draws",len(priors),flush=True)
    realized=annual_recurrence_batch(cube)
    ref=summarize_cube_output(realized)
    if len(ref)!=4*n*2 or ref.structure_id.nunique()!=4:
        raise AssertionError("Incomplete ABC reference draws")
    if (ref.groupby("structure_id").draw.nunique().ne(n).any() or
        ref.groupby(["structure_id","draw"]).reverse_on.nunique().ne(2).any()):
        raise AssertionError("Not equal structural model prior")
    prefix=context
    ref.to_csv(out/(prefix+"_prior_predictive_reference.csv.gz"),index=False,
               compression={"method":"gzip","mtime":0})
    priors.to_csv(out/(prefix+"_parameter_draws.csv"),index=False)
    models.to_csv(out/(prefix+"_structure_inventory.csv"),index=False)
    original.to_csv(out/(prefix+"_anchor_24_corner_replay.csv"),index=False)
    # Matched rate-draw reversal ablation: do not silently call on/off
    # equivalent merely because many frozen source grids were identical.
    key=["structure_id","draw"]
    off=ref[ref.reverse_on==0].set_index(key)
    on=ref[ref.reverse_on==1].set_index(key)
    if len(off)!=len(on) or not off.index.equals(on.index):
        raise AssertionError("Exact reversal-pair rate-draw matching failed")
    flags={}
    for mode in ("log","raw"):
        signs=[f"sign_{mode}_{k}" for k in METRICS]
        flags[mode]=np.all(off[signs].to_numpy()==on[signs].to_numpy(),axis=1)
    paired=pd.DataFrame(dict(structure_id=[q[0] for q in on.index],
                             draw=[int(q[1]) for q in on.index],
                             log_sign_vector_identical=flags["log"],
                             raw_sign_vector_identical=flags["raw"]))
    paired.to_csv(out/(prefix+"_reverse_edge_signature_pairs.csv"),index=False)
    score=[]
    for structure,g in ref.groupby("structure_id"):
        score.append(dict(context=context,structure_id=structure,n_simulator_runs=len(g),
                          n_rate_draws=int(g.draw.nunique()),
                          acceptance_log=int(g.matches_log.sum()),
                          acceptance_raw=int(g.matches_raw.sum()),
                          n_reversed_on=int(g.reverse_on.sum()),
                 n_reversed_off=int((1-g.reverse_on).sum()),
                          n_log_symmetric_zero_patterns=int(
                            g[[f"sign_log_{k}" for k in METRICS]].eq(0).any(axis=1).sum())))
    pd.DataFrame(score).to_csv(out/(prefix+"_source_run_diagnostics.csv"),index=False)
    receipt=dict(status="ACTUAL_80YEAR_MODEL_NATIVE_FACTORIAL_PRIOR_PREDICTIVE",
                 target_signs=dict(zip(METRICS,TARGET)),
                 rate_ranges_are_hypothetical_not_literature_estimates=True,
                 genuine_biological_ABC_posterior_not_estimated=True,
                 n_draws_per_structure=n,context=context,n_structural_classes=4,
                 n_source_vertices=len(realized),n_original_replay_vertices=24*8,
                 original_source_replay_max_error=checks,dt=DT,years=YEARS,window=WINDOW,
                 log_f_b_primary=True,raw_f_b_sensitivity=True,
                 reversal_prior="Bernoulli(0.5), exactly evaluated both ON/OFF at every parameter draw",
                 source_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
                                for p in [DESIGN,*SOURCES]},
                 script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    (out/(prefix+"_receipt.json")).write_text(json.dumps(receipt,indent=2)+"\n")
    print("MODELS_NATIVE_PRIOR_DIAGNOSTICS\n"+
          pd.DataFrame(score).to_string(index=False),flush=True)
    return ref


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--context",required=True,choices=CONTEXTS)
    p.add_argument("--draws",type=int,default=N_DRAWS)
    p.add_argument("--run",action="store_true")
    args=p.parse_args()
    if not args.run:p.error("Explicit --run required")
    run(args.context,args.draws)
