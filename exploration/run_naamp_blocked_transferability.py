#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf

ROOT=Path(__file__).resolve().parents[1]
EXP=ROOT/"exploration"
OUT=EXP/"NAAMP_BLOCKED_TRANSFERABILITY_RECEIPT_V0_1.json"

B=1000
SEED=2840261
ANCHOR=0.75
MIN_POSITIVE_CELLS=20
MIN_POSITIVE_ROUTES=5
TEMPORAL_CUTOFF=2008

def loadmod(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    mod=importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(mod)
    return mod

cross=loadmod("crossfit_current",EXP/"run_naamp_higher_order_crossfit_species_history.py")
joint=cross.joint
mem=joint.mem
uniform=joint.uniform

def fit_species_slopes_mask(runs,sampled,ss,all_species,mask,label):
    x=runs.loc[np.asarray(mask,bool)].copy().reset_index(drop=True)
    x["dry_x"]=np.log1p(x["DaysSinceRain"].astype(float))
    theta=2*np.pi*x["doy"].astype(float)/365.25
    x["sin_doy"]=np.sin(theta)
    x["cos_doy"]=np.cos(theta)
    counts=joint.run_species_counts(x,sampled,ss)

    slopes={}
    audit={}
    for sp in sorted(all_species):
        y=np.asarray([counts[str(rid)].get(sp,0) for rid in x["RunID"].astype(str)],float)
        pos_cells=int(y.sum())
        pos_routes=int(x.loc[y>0,"route_cluster"].astype(str).nunique())
        info={
            "positive_stop_cells":pos_cells,
            "positive_routes":pos_routes,
            "estimable":False,
            "method":"zero_differential_shift",
            "wet_shift_gamma":0.0,
        }
        if pos_cells<MIN_POSITIVE_CELLS or pos_routes<MIN_POSITIVE_ROUTES:
            slopes[sp]=0.0
            audit[sp]=info
            continue

        d=x[["State","RunNumber","mean_temp_c","dry_x","sin_doy","cos_doy"]].copy()
        d["prop"]=y/10.0
        formula="prop ~ dry_x + mean_temp_c + sin_doy + cos_doy + C(State) + C(RunNumber)"
        glm=smf.glm(
            formula,data=d,family=sm.families.Binomial(),
            freq_weights=np.repeat(10.0,len(d))
        )
        method="glm"
        try:
            fit=glm.fit(maxiter=200,disp=0)
            beta=float(fit.params["dry_x"])
            if not np.isfinite(beta) or abs(beta)>20:
                raise RuntimeError("unstable slope")
        except Exception:
            method="ridge_fallback"
            fit=glm.fit_regularized(alpha=0.01,L1_wt=0.0,maxiter=1000)
            beta=float(fit.params["dry_x"])
            if not np.isfinite(beta):
                beta=0.0
                method="zero_after_failed_regularization"

        gamma=float(-beta)
        slopes[sp]=gamma
        info.update({
            "estimable":bool(method!="zero_after_failed_regularization"),
            "method":method,
            "wet_shift_gamma":gamma,
        })
        audit[sp]=info

    return slopes,{
        "label":label,
        "n_runs":int(len(x)),
        "n_routes":int(x.route_cluster.nunique()),
        "n_states":int(x.State.nunique()),
        "year_min":int(x.SurveyYear.min()) if len(x) else None,
        "year_max":int(x.SurveyYear.max()) if len(x) else None,
        "n_species_total":int(len(all_species)),
        "n_species_estimable":int(sum(v["estimable"] for v in audit.values())),
    },audit

def prepare_principal():
    raw=mem.load_retry()
    runs,_=mem.base.build_runs(raw)
    eligible=set(runs.RunID.astype(str))
    uniform.base.load=lambda:raw
    (
        pairs,pair_data,pools,dry_ids,sampled,ss,r0,den0,obs0,
        beta_mask,r_beta,den_beta,obs_sor
    )=uniform.prepare()
    pairs=pairs.copy().reset_index(drop=True)

    site=mem.site_map(raw,eligible)
    meta,by_stratum,run_sites,run_site_species=mem.build_history_index(
        runs,sampled,ss,site
    )

    keep=[]
    histories=[]
    siteids=[]
    prior_ids=[]
    for p,dct in zip(pairs.itertuples(index=False),pair_data):
        ids=mem.focal_siteids(p,dct,site)
        if ids is None:
            keep.append(False); histories.append(None); siteids.append(None); prior_ids.append(None)
            continue
        prior=mem.eligible_prior_runs(p,dct,ids,meta,by_stratum,run_sites)
        if not prior:
            keep.append(False); histories.append(None); siteids.append(None); prior_ids.append(None)
            continue
        ph,_=mem.prior_probs(dct,ids,prior,run_sites,run_site_species)
        keep.append(True); histories.append(ph); siteids.append(ids); prior_ids.append(prior)

    keep=np.asarray(keep,bool)
    idx=np.flatnonzero(keep)
    psub=pairs.iloc[idx].copy().reset_index(drop=True)
    dsub=[pair_data[int(i)] for i in idx]
    hsub=[histories[int(i)] for i in idx]
    isub=[siteids[int(i)] for i in idx]
    prsub=[prior_ids[int(i)] for i in idx]

    if len(psub)!=2916 or psub.route_cluster.nunique()!=439:
        raise RuntimeError(f"principal subset drift: {len(psub)} pairs, {psub.route_cluster.nunique()} routes")

    return raw,runs,psub,dsub,hsub,isub,prsub,pools,sampled,ss,meta,run_sites,run_site_species

def simulate(psub,dsub,hsub,slopes_for_pair,r,den,seed):
    rng=np.random.default_rng(seed)
    numer=np.zeros((B,4),float)
    for i,(p,dct,ph) in enumerate(zip(psub.itertuples(index=False),dsub,hsub)):
        dry=dct["dry"].astype(float)
        p_anchor=(1-ANCHOR)*ph+ANCHOR*dry
        p_anchor=np.clip(p_anchor,1e-8,1-1e-8)
        slopes=slopes_for_pair(p)
        gamma=np.asarray([float(slopes.get(sp,0.0)) for sp in dct["species"]],float)
        eta=uniform.logit(p_anchor)+gamma[:,None]*float(p.rain_contrast)
        pre=uniform.expit(eta)
        q=uniform.solve_shift(pre,dct["wet_k"])
        w=rng.random((B,)+q.shape)<q[None,:,:]
        numer += r[i]*cross.sim_metrics(w,dct["dry"])
    return numer/den

def observed_test(psub,dsub,sim):
    obs_rows=np.asarray([cross.metrics(d["wet"],d["dry"]) for d in dsub],float)
    r,den=uniform.design_residual(psub)
    obs=(r[:,None]*obs_rows).sum(axis=0)/den
    out=cross.conditional(sim,obs)
    out["observed_route_new_species_beta"]=float(obs[0])
    out["observed_extra_stop_beta"]=float(obs[1])
    out["observed_concentration_beta"]=float(obs[2])
    return out

def classify(x):
    resid=float(x["observed_conditional_residual"])
    if bool(x["above_upper_95"]):
        return "excess_transfers"
    if resid>0:
        return "directional_only"
    return "no_positive_transfer"

def main():
    (
        raw,runs,psub,dsub,hsub,isub,prsub,pools,sampled,ss,
        meta,run_sites,run_site_species
    )=prepare_principal()
    all_species=sorted({sp for spp in pools.values() for sp in spp})

    states=sorted(psub.State.astype(str).unique())
    spatial_gate={
        "pairs":int(len(psub)),
        "routes":int(psub.route_cluster.nunique()),
        "states":int(len(states)),
    }
    spatial_gate_pass=(
        spatial_gate["pairs"]==2916 and
        spatial_gate["routes"]==439 and
        spatial_gate["states"]>=18
    )

    # Temporal eligibility is determined without reading the focal endpoint.
    tidx=[]
    thist=[]
    for i,(p,dct,ids,prior) in enumerate(zip(psub.itertuples(index=False),dsub,isub,prsub)):
        if int(p.year_earlier)<TEMPORAL_CUTOFF+1:
            continue
        frozen=[rid for rid in prior if int(meta[rid]["year"])<=TEMPORAL_CUTOFF]
        if not frozen:
            continue
        ph,_=mem.prior_probs(dct,ids,frozen,run_sites,run_site_species)
        tidx.append(i)
        thist.append(ph)

    ptemp=psub.iloc[tidx].copy().reset_index(drop=True)
    dtemp=[dsub[i] for i in tidx]
    temporal_gate={
        "pairs":int(len(ptemp)),
        "routes":int(ptemp.route_cluster.nunique()) if len(ptemp) else 0,
        "states":int(ptemp.State.nunique()) if len(ptemp) else 0,
    }
    temporal_gate_pass=(
        temporal_gate["pairs"]>=500 and
        temporal_gate["routes"]>=100 and
        temporal_gate["states"]>=12
    )

    out={
        "analysis":"naamp_blocked_transferability_v0_1",
        "contract":"exploration/NAAMP_BLOCKED_TRANSFERABILITY_CONTRACT_V0_1.json",
        "status":"coverage_checked_before_blocked_endpoint_read",
        "simulation_replicates":B,
        "seed":SEED,
        "spatial_gate":{**spatial_gate,"pass":spatial_gate_pass},
        "temporal_gate":{**temporal_gate,"cutoff_year":TEMPORAL_CUTOFF,"pass":temporal_gate_pass},
        "response_endpoint_read":False,
    }
    if not spatial_gate_pass or not temporal_gate_pass:
        OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
        print(json.dumps(out,indent=2,sort_keys=True))
        return

    # Spatial block: every focal State receives gamma estimates trained without that State.
    slopes_by_state={}
    state_training={}
    state_audit={}
    for state in states:
        mask=runs.State.astype(str).to_numpy()!=state
        slopes,info,audit=fit_species_slopes_mask(
            runs,sampled,ss,all_species,mask,f"exclude_state_{state}"
        )
        slopes_by_state[state]=slopes
        state_training[state]=info
        state_audit[state]={
            "n_estimable":int(sum(v["estimable"] for v in audit.values()))
        }

    r_sp,den_sp=uniform.design_residual(psub)
    sim_sp=simulate(
        psub,dsub,hsub,
        lambda p:slopes_by_state[str(p.State)],
        r_sp,den_sp,SEED+1000
    )
    spatial_result=observed_test(psub,dsub,sim_sp)

    # Temporal block: species response and site-history template frozen at 2008.
    train_mask=runs.SurveyYear.astype(int).to_numpy()<=TEMPORAL_CUTOFF
    temporal_slopes,temporal_training,temporal_audit=fit_species_slopes_mask(
        runs,sampled,ss,all_species,train_mask,"years_2001_2008"
    )
    r_t,den_t=uniform.design_residual(ptemp)
    sim_t=simulate(
        ptemp,dtemp,thist,
        lambda p:temporal_slopes,
        r_t,den_t,SEED+2000
    )
    temporal_result=observed_test(ptemp,dtemp,sim_t)

    out.update({
        "status":"complete",
        "response_endpoint_read":True,
        "spatial_leave_one_state_out_mosaic":{
            "training":state_training,
            "estimability":state_audit,
            "result":spatial_result,
            "classification":classify(spatial_result),
        },
        "temporal_2001_2008_to_2009_2015":{
            "training":temporal_training,
            "n_species_estimable":int(sum(v["estimable"] for v in temporal_audit.values())),
            "history_frozen_through":TEMPORAL_CUTOFF,
            "result":temporal_result,
            "classification":classify(temporal_result),
        },
        "interpretation_boundary":{
            "posthoc_transferability_assessment":True,
            "independent_confirmation":False,
            "observed_total_activation_conditioned_on":True,
            "spatial_species_response_uses_focal_state":False,
            "temporal_species_response_uses_post_2008_data":False,
            "temporal_history_uses_post_2008_data":False,
            "causal_rainfall_claim":False,
        }
    })
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(out,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
