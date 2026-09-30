#!/usr/bin/env python3
from __future__ import annotations
import importlib.util, json
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
EXP=ROOT/"exploration"
OUT=EXP/"NAAMP_HIGHER_ORDER_FINAL_RAIN_HISTORY_GATE_RECEIPT_V0_1.json"
B=1000
SEED=2944223

def loadmod(name,path):
    s=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(s)
    assert s.loader
    s.loader.exec_module(m)
    return m

final=loadmod("final_gate",EXP/"run_naamp_crossfit_rain_local_memory_gating_null.py")
joint=final.joint
uniform=final.uniform

def metrics(w,d):
    d_route=d.any(axis=1)
    route_new=(~d_route)&w.any(axis=1)
    if not np.any(route_new):
        return np.asarray([0.,0.,0.,0.])
    k=w[route_new].sum(axis=1).astype(float)
    extra=np.maximum(k-1.,0.)
    higher=extra*np.maximum(extra-1.,0.)/2.
    return np.asarray([
        float(len(k)),
        float(extra.sum()),
        float(higher.sum()),
        float(np.sum(k>=3.))
    ])

def sim_metrics(w,d):
    d_route=d.any(axis=1)
    route_new=(~d_route[None,:])&w.any(axis=2)
    k=w.sum(axis=2).astype(float)
    extra=np.maximum(k-1.,0.)*route_new
    higher=extra*np.maximum(extra-1.,0.)/2.
    return np.column_stack([
        route_new.sum(axis=1).astype(float),
        extra.sum(axis=1).astype(float),
        higher.sum(axis=1).astype(float),
        ((k>=3.)&route_new).sum(axis=1).astype(float)
    ])

def conditional(sim,obs):
    X=np.column_stack([np.ones(len(sim)),sim[:,0],sim[:,1]])
    y=sim[:,2]
    coef=np.linalg.lstsq(X,y,rcond=None)[0]
    pred=X@coef
    resid=y-pred
    obs_pred=float(coef[0]+coef[1]*obs[0]+coef[2]*obs[1])
    obs_resid=float(obs[2]-obs_pred)
    lo,hi=np.quantile(resid,[.025,.975])
    p=float((1+np.sum(resid>=obs_resid))/(len(resid)+1))
    return {
      "null_regression_intercept":float(coef[0]),
      "null_regression_new_species_slope":float(coef[1]),
      "null_regression_extra_stop_slope":float(coef[2]),
      "predicted_higher_order_beta":obs_pred,
      "observed_conditional_residual":obs_resid,
      "null_residual_ci95":[float(lo),float(hi)],
      "conditional_upper_tail_p":p,
      "above_upper_95":bool(obs_resid>hi)
    }

def simulate_final(psub,dsub,hsub,slopes_by_train,lambdas,r,den):
    rng=np.random.default_rng(SEED)
    numer=np.zeros((B,4),float)
    for i,(p,dct,p_hist) in enumerate(zip(psub.itertuples(index=False),dsub,hsub)):
        test_fold=joint.fold_for_route(str(p.route_cluster))
        train_fold="B" if test_fold=="A" else "A"
        slopes=slopes_by_train[train_fold]
        lmbda=float(lambdas[train_fold])

        base_eta,x=final.cell_terms(p,dct,p_hist,slopes)
        pre=uniform.expit(base_eta+lmbda*x)
        q=uniform.solve_shift(pre,dct["wet_k"])
        wsim=rng.random((B,)+q.shape)<q[None,:,:]
        numer += r[i]*sim_metrics(wsim,dct["dry"])
    return numer/den

def main():
    raw,runs,psub,dsub,hsub,asub,pools,sampled,ss=final.prepare_subset()
    if len(psub)!=2916 or psub.route_cluster.nunique()!=439:
        raise RuntimeError(f"subset drift: {len(psub)} pairs, {psub.route_cluster.nunique()} routes")

    all_species=sorted({sp for spp in pools.values() for sp in spp})
    slopes_A,audit_A,fold_A=joint.fit_species_slopes(runs,sampled,ss,all_species,"A")
    slopes_B,audit_B,fold_B=joint.fit_species_slopes(runs,sampled,ss,all_species,"B")
    slopes_by_train={"A":slopes_A,"B":slopes_B}

    lambda_A,audit_lA=final.fit_lambda("A",psub,dsub,hsub,slopes_A)
    lambda_B,audit_lB=final.fit_lambda("B",psub,dsub,hsub,slopes_B)
    if not (audit_lA["lambda_within_stability_bound"] and audit_lB["lambda_within_stability_bound"]):
        raise RuntimeError("lambda stability gate failed")
    lambdas={"A":lambda_A,"B":lambda_B}

    obs_rows=np.asarray([metrics(d["wet"],d["dry"]) for d in dsub],float)
    r,den=uniform.design_residual(psub)
    obs=(r[:,None]*obs_rows).sum(axis=0)/den

    sim=simulate_final(psub,dsub,hsub,slopes_by_train,lambdas,r,den)
    test=conditional(sim,obs)

    out={
      "analysis":"naamp_higher_order_final_rain_history_gate_v0_1",
      "contract":"exploration/NAAMP_HIGHER_ORDER_FINAL_RAIN_HISTORY_GATE_CONTRACT_V0_1.json",
      "coverage":{"pairs":int(len(psub)),"routes":int(psub.route_cluster.nunique()),"states":int(psub.State.nunique())},
      "observed":{
        "route_new_species_beta":float(obs[0]),
        "extra_stop_beta":float(obs[1]),
        "higher_order_beta":float(obs[2]),
        "threeplus_species_beta":float(obs[3])
      },
      "species_shift_training":{"fold_A":fold_A,"fold_B":fold_B},
      "lambda_training":{"fold_A":audit_lA,"fold_B":audit_lB},
      "final_crossfit_rain_by_history_gate":test,
      "classification":{"higher_order_dependence_survives_final_gate":bool(test["above_upper_95"])},
      "interpretation_boundary":{
        "existing_null_only":True,
        "literal_synchrony_inferred":False,
        "individual_movement_inferred":False,
        "causal_rainfall_claim":False,
        "unique_lower_level_mechanism_identified":False
      }
    }
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
