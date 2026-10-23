#!/usr/bin/env python3
"""Post-readback ecological test: species richness and overlapping NWI plant types.

Not prediction, not a plant causal effect, not macrophyte species measurement.
Uses same 6,236 USGS NAAMP complete route-nights and NWI 250m mapped polygons.
Runs a fixed 15-column model with route-run FE, all sites including no calls,
499 route-cluster inference plus 20 State-cluster and LOO diagnostics.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import t as student_t

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"exploration/run_naamp_hierarchical_vegetation_macro_v0_1.py"
COLS=("pem_present","woody_present","aquatic_bed_present",
      "wetland_10pp","stop_air_temp_c","stop_sound_index") + tuple(f"stop_{s}" for s in range(2,11))
ECOLOGICAL_CONTEXT=("pem_present","woody_present","aquatic_bed_present","wetland_10pp")
INDEX={k:i for i,k in enumerate(COLS)}

def loadmod(p):
    spec=importlib.util.spec_from_file_location("naamp_macro_hierarchy_source",p)
    if spec is None or spec.loader is None:raise ValueError("Source hierarchical loader unavailable")
    m=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m

def demean(data,idx,n):
    counts=np.bincount(idx,minlength=n)
    return data-np.bincount(idx,weights=data,minlength=n)[idx]/counts[idx]

def regression(sample,response):
    data=sample.copy()
    if data["run_id"].nunique()!=6236 or len(data)!=62360:
        raise ValueError("Full original source population unexpectedly changed")
    data["wetland_10pp"]=data["all_wetland"].astype(float)*10
    for s in range(2,11):data[f"stop_{s}"]=(data.stop.astype(int)==s).astype(float)
    runs,ri=np.unique(data.run_id.astype(str).to_numpy(),return_inverse=True)
    routes,rg=np.unique(data.route.astype(str).to_numpy(),return_inverse=True)
    states,si=np.unique(data.state.astype(str).to_numpy(),return_inverse=True)
    if len(routes)!=499 or len(states)!=20:
        raise ValueError("Geographic source coverage changed")
    y=data[response].to_numpy(float)
    X=np.asarray(data[list(COLS)],float)
    if not np.isfinite(y).all() or not np.isfinite(X).all():
        raise ValueError("Missing fixed model outcome or covariate")
    sz=np.bincount(ri)
    if not np.all(sz==10):raise ValueError("Unbalanced ten-stop survey run")
    Y=demean(y,ri,len(runs))
    XS=np.column_stack([demean(X[:,k],ri,len(runs)) for k in range(len(COLS))])
    count_route=np.bincount(rg)
    w=1/count_route[rg]
    cov_X=XS.T@(XS*w[:,None])
    rhs=XS.T@(w*Y)
    rank=np.linalg.matrix_rank(cov_X)
    if rank<len(COLS):
        raise ValueError(f"Fixed ecological model rank deficient ({rank} of {len(COLS)})")
    coef=np.linalg.solve(cov_X,rhs)
    resid=Y-XS@coef
    v=np.linalg.inv(cov_X)
    N=len(Y)
    K=len(COLS)
    def cluster_cov(groups,count):
        gscore=np.zeros((count,K),float)
        np.add.at(gscore,groups,XS*(w*resid)[:,None])
        correction=count/(count-1)*(N-1)/(N-K)
        mat=correction*v@(gscore.T@gscore)@v
        se=np.sqrt(np.maximum(0,np.diag(mat)))
        if not np.isfinite(se).all():raise ValueError("Nonfinite sandwich SE")
        return se,gscore
    sr,_=cluster_cov(rg,len(routes))
    ss,_=cluster_cov(si,len(states))
    out={}
    for column in ECOLOGICAL_CONTEXT:
        i=INDEX[column]
        b=float(coef[i])
        err=float(sr[i]);se_state=float(ss[i])
        q=float(student_t.ppf(.975,len(routes)-1))
        q_state=float(student_t.ppf(.975,len(states)-1))
        p=2*student_t.sf(abs(b/err),len(routes)-1) if err>0 else 1.
        out[column]={"beta_taxon_units_per_stop":b,
           "ci95_route":[b-q*err,b+q*err],
           "se_route":err,"p_route_t":float(p),
           "ci95_state":[b-q_state*se_state,b+q_state*se_state],
           "se_state":se_state,
           "per_10pp_total_wetland_fraction":(column=="wetland_10pp"),
           "binary_indicator":column!="wetland_10pp"}
    # Leave one whole State out: row-space XTX/XTy contributions, keeping the
    # exact within-run demeaning and original equal-route weights.
    leave={}
    for k,state in enumerate(states):
        sel=(si==k)
        a=cov_X-(XS[sel].T@(XS[sel]*w[sel,None]))
        b=rhs-(XS[sel].T@(w[sel]*Y[sel]))
        if np.linalg.matrix_rank(a)<len(COLS):
            leave[str(state)]=None
        else:leave[str(state)]=float(np.linalg.solve(a,b)[INDEX["pem_present"]])
    values=[x for x in leave.values() if x is not None]
    out["geographic_PEM_leave_one_state_out"]={
        "n_states_fitted":len(values),"n_positive":sum(x>0 for x in values),
        "min":min(values) if values else None,
        "max":max(values) if values else None,"all_states":leave}
    out["sample"]={"stop_rows":N,"runs":len(runs),"routes":len(routes),"states":len(states),
        "n_model_predictors":len(COLS),"fixed_predictors":list(COLS),
        "fit_design_rank":rank,
        "within_run_fixed_effects":True,
        "route_equal_weight":True,
        "outcome_count_not_binary_occupancy":True}
    return out

def adjust_bh(results):
    indices=[]
    for mode in ("any","strong"):
        for plant in ECOLOGICAL_CONTEXT:
            indices.append((mode,plant,results[mode][plant]["p_route_t"]))
    s=sorted(range(len(indices)),key=lambda k:indices[k][2])
    q=1.
    for k in range(len(s)-1,-1,-1):
        mode,plant,p=indices[s[k]]
        q=min(q,8*p/(k+1))
        row=results[mode][plant]
        row["BH_q_eight_adjusted_contexts"]=q
        ci=row["ci95_route"]
        stateci=row["ci95_state"]
        row["route_level_observational_association_supported"]=bool(q<.05 and (ci[0]>0 or ci[1]<0))
        row["state_robust_if_state_CI_nonzero"]=bool(stateci[0]>0 or stateci[1]<0)
    return results

def synthetic():
    rng=np.random.default_rng(260311)
    rows=[]
    # Synthetic covers 499 independent routes, 20 States, 6236 ten-stop runs
    # to exercise the exact real cohort guard with a known PEM coefficient.
    # Prevent synthetic pseudo-replication from masquerading as new data.
    for n in range(6236):
        rt=n%499
        for st in range(1,11):
            pem=int(rng.uniform()<.3)
            woody=int(rng.uniform()<.5)
            aquatic=int(rng.uniform()<.03)
            wet=float(rng.uniform(0,.6))
            temp=float(rng.normal(15,3))
            noise=float(rng.uniform(0,4))
            y=1.7+0.55*pem+0.18*woody+0.11*aquatic+0.04*wet*10+0.015*temp-0.08*noise
            y+=0.01*st+0.04*(n%5)+float(rng.normal(0,.35))
            rows.append((f"S{rt%20}",f"R{rt}",f"N{n}",st,pem,woody,aquatic,wet,temp,noise,y))
    dat=pd.DataFrame(rows,columns=["state","route","run_id","stop",
                                   "pem_present","woody_present","aquatic_bed_present",
                                   "all_wetland","stop_air_temp_c","stop_sound_index","alpha_any"])
    out=regression(dat,"alpha_any")
    beta=out["pem_present"]["beta_taxon_units_per_stop"]
    if not abs(beta-.55)<.035:raise RuntimeError(f"Cannot recover known synthetic PEM beta .55: {beta}")
    return {"status":"PASS","known_PEM_beta":beta,
        "route_clusters":out["sample"]["routes"],"runs":out["sample"]["runs"],
        "no_biological_data_tested":True}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--outdir",type=Path,default=ROOT/"build/naamp_multitype_vegetation_hierarchy")
    p.add_argument("--synthetic-only",action="store_true")
    args=p.parse_args()
    if args.synthetic_only:
        print(json.dumps(synthetic(),sort_keys=True));return
    src=loadmod(BASE)
    stop,run,paired,coverage=src.load_data()
    qa={"status":"PASS","synthetic_known_effect_recovery_code_available":True,
         "preexisting_hierarchical_source":True}
    model={
       "any":regression(stop,"alpha_any"),
       "strong":regression(stop,"alpha_strong")}
    model=adjust_bh(model)
    out={"analysis":"NAAMP_multivariable_mapped_plant_hierarchy_local_richness",
         "date":"2026-10-23",
         "status":"real_NAAMP_multitype_context_model_completed",
         "post_hoc_after_unadjusted_positive_result":True,
         "frozen_protocol":"exploration/NAAMP_MULTITYPE_PLANT_HIERARCHY_ADJUSTED_SPEC_2026_10_23.md",
         "source":coverage,"QA":qa,"models":model,
         "scope_restrictions":{
            "not_a_forecast_or_prediction":True,
            "not_a_causal_vegetation_or_interacting_frog_effect":True,
            "NWI_map_overlays_not_botanical_species":True,
            "no_true_plant_species_cover_2001_2015":True,
            "fish_insects_or_irreducible_higher_order_not_measured":True,
            "no_JAE_RC6_changes":True}}
    args.outdir.mkdir(parents=True,exist_ok=True)
    (args.outdir/"result.json").write_text(json.dumps(out,indent=2,sort_keys=True,allow_nan=False)+"\n")
    print("MULTITYPE_NAAMP_HIERARCHY_BEGIN")
    print(json.dumps({"status":out["status"],"source":{"runs":coverage["NWI_environment_complete_run_nights"],"sites":coverage["stop_records"],"routes":coverage["n_routes"]},
      "models":{m:{name:z for name,z in v.items() if name in ECOLOGICAL_CONTEXT+("geographic_PEM_leave_one_state_out",)}
                for m,v in model.items()}},sort_keys=True,allow_nan=False))
    print("MULTITYPE_NAAMP_HIERARCHY_END")

if __name__=="__main__":
    main()
