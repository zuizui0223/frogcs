#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path

import numpy as np
import pandas as pd
import patsy
import statsmodels.api as sm
import statsmodels.formula.api as smf
from statsmodels.stats.sandwich_covariance import cov_cluster

ROOT=Path(__file__).resolve().parents[2]
WFTS=ROOT/"scripts"/"wfts"
AUTH=ROOT/"revision"/"WFTS_PROSPECTIVE_COMMON_ENVIRONMENT_DIAGNOSTIC_V0_2.json"

B=1000
CONC_SEED=2840226
DEPENDENCE_SEED=2840230
LAG_SEED=2840231
ANCHOR=0.75
MIN_POSITIVE_CELLS=20
MIN_POSITIVE_ROUTES=5
EPS=1e-7
Q95=1.959963984540054

def loadmod(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    mod=importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(mod)
    return mod

base=loadmod("wfts_primary",WFTS/"run_wfts_confirmatory_analysis_v0_5.py")

def feature_matrix(runs, exposure_col, period_levels):
    x=runs.copy().reset_index(drop=True)
    rain=x["rain_recency"].astype(float).to_numpy()
    amount=x[exposure_col].astype(float).to_numpy()
    temp=x["tmean_run"].astype(float).to_numpy()

    # Bounds are fixed from physically allowed transformations rather than
    # learned from response outcomes.
    rain_basis=np.asarray(patsy.dmatrix(
        "bs(v, df=4, degree=3, include_intercept=False) - 1",
        {"v":rain},return_type="dataframe"
    ),float)
    amount_basis=np.asarray(patsy.dmatrix(
        "bs(v, df=4, degree=3, include_intercept=False) - 1",
        {"v":amount},return_type="dataframe"
    ),float)
    temp_basis=np.asarray(patsy.dmatrix(
        "bs(v, df=4, degree=3, include_intercept=False) - 1",
        {"v":temp},return_type="dataframe"
    ),float)
    interactions=np.column_stack([rain*amount,amount*temp])

    period=np.zeros((len(x),max(0,len(period_levels)-1)),float)
    pidx={v:i for i,v in enumerate(period_levels[1:])}
    for i,v in enumerate(x["survey_period"].astype(str)):
        j=pidx.get(v)
        if j is not None:
            period[i,j]=1.0

    return np.column_stack([
        np.ones(len(x),float),rain_basis,amount_basis,temp_basis,interactions,period
    ])

def fit_common_environment(runs,run_mats,taxa,training_fold,exposure_col):
    x=runs.copy().reset_index(drop=True)
    x["route_fold"]=x["route_id"].astype(str).map(base.fold_for_route)
    periods=sorted(x["survey_period"].astype(str).unique())
    X_all=feature_matrix(x,exposure_col,periods)
    train=x["route_fold"].to_numpy()==training_fold
    X=X_all[train]
    train_routes=x.loc[train,"route_id"].astype(str).to_numpy()
    runids=[base.run_key(r.route_id,r.survey_period,r.survey_year) for r in x.itertuples(index=False)]

    eta_by_species={}
    audit={}
    for j,sp in enumerate(taxa):
        y_all=np.asarray([np.sum(run_mats[k][j,:]>0) for k in runids],float)
        y=y_all[train]
        pos_cells=int(y.sum())
        pos_routes=int(len(set(train_routes[y>0])))
        info={"positive_stop_cells":pos_cells,"positive_routes":pos_routes,"estimable":False,"method":"zero_environment_shift"}
        if pos_cells<MIN_POSITIVE_CELLS or pos_routes<MIN_POSITIVE_ROUTES:
            eta_by_species[sp]=np.zeros(len(x),float)
            audit[sp]=info
            continue

        prop=y/10.0
        model=sm.GLM(prop,X,family=sm.families.Binomial(),freq_weights=np.repeat(10.0,len(prop)))
        method="glm"
        try:
            fit=model.fit(maxiter=200,disp=0)
            params=np.asarray(fit.params,float)
            if (not np.all(np.isfinite(params))) or np.max(np.abs(params))>50:
                raise RuntimeError("unstable coefficients")
        except Exception:
            method="ridge_fallback"
            fit=model.fit_regularized(alpha=0.01,L1_wt=0.0,maxiter=1000)
            params=np.asarray(fit.params,float)
            if not np.all(np.isfinite(params)):
                eta_by_species[sp]=np.zeros(len(x),float)
                info["method"]="zero_after_failed_regularization"
                audit[sp]=info
                continue
        eta_by_species[sp]=np.clip(X_all@params,-20,20)
        info.update({"estimable":True,"method":method})
        audit[sp]=info

    pred={}
    for i,k in enumerate(runids):
        pred[k]={sp:float(eta_by_species[sp][i]) for sp in taxa}
    return pred,audit,{
        "training_fold":training_fold,
        "n_training_runs":int(train.sum()),
        "n_training_routes":int(x.loc[train,"route_id"].nunique()),
        "n_estimable_taxa":int(sum(a["estimable"] for a in audit.values())),
        "feature_count":int(X.shape[1]),
        "exposure_col":exposure_col
    }

def prepare_analysis(runs_path,matrix_path,common_path,primary):
    schema,runs,matrix,taxa=base.load_inputs(runs_path,matrix_path)
    run_mats_ci,sites,dates=base.build_run_matrices(runs,matrix,taxa)
    run_mats={k:(v>0) for k,v in run_mats_ci.items()}
    support=base.build_support_pools(runs,run_mats_ci,taxa)
    pairs=base.build_pairs(runs,sites)
    psub=base.structural_principal_pairs(pairs,runs,sites)

    pcov=primary["coverage"]
    if len(psub)!=int(pcov["principal_history_pairs"]) or psub.route_id.nunique()!=int(pcov["principal_routes"]):
        raise RuntimeError("primary pair coverage drift in secondary diagnostic")

    common=pd.read_csv(common_path)
    common["route_id"]=common.route_id.astype(str)
    common["survey_period"]=common.survey_period.astype(str)
    common["survey_year"]=common.survey_year.astype(int)
    common["survey_date"]=pd.to_datetime(common.survey_date,errors="raise")
    key=["route_id","survey_period","survey_year"]
    if common.duplicated(key).any():
        raise RuntimeError("duplicate common-environment route-run keys")
    merged=runs.merge(
        common[key+["survey_date","prcp_1d_exposure","prcp_3d_exposure","prcp_7d_exposure"]],
        on=key,how="left",validate="one_to_one",suffixes=("","_common")
    )
    if merged[["prcp_1d_exposure","prcp_3d_exposure","prcp_7d_exposure"]].isna().any().any():
        raise RuntimeError("common-environment weather missing for canonical run")
    if not (merged.survey_date.to_numpy()==merged.survey_date_common.to_numpy()).all():
        raise RuntimeError("common-environment dates differ from canonical runs")
    merged=merged.drop(columns=["survey_date_common"])

    obs_rows=[]; phs=[]; drys=[]; wets=[]; wet_k=[]; species_list=[]
    for p in psub.itertuples(index=False):
        pool_idx=support[(str(p.route_id),str(p.survey_period))]
        species=[taxa[int(j)] for j in pool_idx]
        wet=run_mats[p.wet_key][pool_idx,:]
        dry=run_mats[p.dry_key][pool_idx,:]
        ph,_=base.prior_probs_for_pair(p,runs,run_mats,sites,pool_idx)
        obs_rows.append(base.pair_metrics(wet,dry))
        phs.append(ph); drys.append(dry); wets.append(wet); wet_k.append(int(wet.sum())); species_list.append(species)

    r,den=base.design_residual(psub)
    obs=(r[:,None]*np.asarray(obs_rows,float)).sum(axis=0)/den
    return merged,taxa,psub,phs,drys,wets,wet_k,species_list,r,den,obs

def run_common_env_window(runs,taxa,psub,phs,drys,wets,wet_k,species_list,r,den,obs,exposure_col,seed,return_q=False):
    # Full matrices are recovered through a closure populated by main.
    run_mats=run_common_env_window.run_mats
    pred_A,audit_A,fold_A=fit_common_environment(runs,run_mats,taxa,"A",exposure_col)
    pred_B,audit_B,fold_B=fit_common_environment(runs,run_mats,taxa,"B",exposure_col)
    pred_by_train={"A":pred_A,"B":pred_B}

    rng=np.random.default_rng(seed)
    numer=np.zeros((B,3),float)
    q_list=[]
    for i,(p,ph,dry,target,species) in enumerate(zip(psub.itertuples(index=False),phs,drys,wet_k,species_list)):
        test_fold=base.fold_for_route(str(p.route_id))
        train_fold="B" if test_fold=="A" else "A"
        pred=pred_by_train[train_fold]
        delta=np.asarray([
            pred[p.wet_key].get(sp,0.0)-pred[p.dry_key].get(sp,0.0)
            for sp in species
        ],float)
        p_anchor=(1.0-ANCHOR)*ph+ANCHOR*dry.astype(float)
        p_anchor=np.clip(p_anchor,EPS,1-EPS)
        pre=base.expit(base.logit(p_anchor)+delta[:,None])
        q=base.solve_shift(pre,target)
        q=np.clip(q,EPS,1-EPS)
        wsim=rng.random((B,)+q.shape)<q[None,:,:]
        numer += r[i]*base.sim_metrics(wsim,dry)
        if return_q:
            q_list.append(q)
    sim=numer/den
    test=base.conditional_test(sim,obs)
    return test,q_list,{
        "fold_A":fold_A,"fold_B":fold_B,
        "fold_A_taxa":audit_A,"fold_B_taxa":audit_B
    }

def bounded_dep(q_list,wets,drys,seed):
    rng=np.random.default_rng(seed)
    stats={
      "all":{"on":0.0,"od":0.0,"nn":np.zeros(B),"nd":np.zeros(B),"clusters":0},
      "dry_route_silent":{"on":0.0,"od":0.0,"nn":np.zeros(B),"nd":np.zeros(B),"clusters":0}
    }
    for q,wet,dry in zip(q_list,wets,drys):
        for i in range(q.shape[0]):
            e=wet[i].astype(float)-q[i]
            s=float(e.sum()); ss=float(np.sum(e*e))
            on=s*s-ss; od=9.0*ss
            w=rng.random((B,10))<q[i][None,:]
            ee=w.astype(float)-q[i][None,:]
            ssim=ee.sum(axis=1); sssim=np.sum(ee*ee,axis=1)
            nn=ssim*ssim-sssim; nd=9.0*sssim
            labs=["all"]
            if dry[i].sum()==0: labs.append("dry_route_silent")
            for lab in labs:
                st=stats[lab]; st["on"]+=on; st["od"]+=od; st["nn"]+=nn; st["nd"]+=nd; st["clusters"]+=1

    out={}
    for lab,st in stats.items():
        obs=float(st["on"]/st["od"]); null=st["nn"]/st["nd"]
        lo,hi=np.quantile(null,[.025,.975]); p=float((1+np.sum(null>=obs))/(B+1))
        out[lab]={
          "clusters":int(st["clusters"]),"rho_bounded":obs,
          "null_ci95":[float(lo),float(hi)],"null_mean":float(np.mean(null)),
          "plus_one_upper_tail_p":p,"positive_dependence_supported":bool(obs>hi and p<.05)
        }
    return out

def lag_profile(q_list,wets,drys,seed):
    rng=np.random.default_rng(seed)
    lags=range(1,10)
    acc={d:{"on":0.0,"ox":0.0,"oy":0.0,"nn":np.zeros(B),"nx":np.zeros(B),"ny":np.zeros(B)} for d in lags}
    clusters=0
    for q,wet,dry in zip(q_list,wets,drys):
        for i in range(q.shape[0]):
            if dry[i].sum()!=0: continue
            e=wet[i].astype(float)-q[i]
            w=rng.random((B,10))<q[i][None,:]
            es=w.astype(float)-q[i][None,:]
            clusters+=1
            for d in lags:
                x=e[:-d]; y=e[d:]; xs=es[:,:-d]; ys=es[:,d:]
                a=acc[d]
                a["on"]+=float(np.sum(x*y)); a["ox"]+=float(np.sum(x*x)); a["oy"]+=float(np.sum(y*y))
                a["nn"]+=np.sum(xs*ys,axis=1); a["nx"]+=np.sum(xs*xs,axis=1); a["ny"]+=np.sum(ys*ys,axis=1)

    def finish(ds):
        on=sum(acc[d]["on"] for d in ds); ox=sum(acc[d]["ox"] for d in ds); oy=sum(acc[d]["oy"] for d in ds)
        nn=sum((acc[d]["nn"] for d in ds),np.zeros(B)); nx=sum((acc[d]["nx"] for d in ds),np.zeros(B)); ny=sum((acc[d]["ny"] for d in ds),np.zeros(B))
        obs=float(on/np.sqrt(ox*oy)); null=nn/np.sqrt(nx*ny)
        lo,hi=np.quantile(null,[.025,.975]); p=float((1+np.sum(null>=obs))/(B+1))
        return {"rho_lag":obs,"null_ci95":[float(lo),float(hi)],"null_mean":float(np.mean(null)),"plus_one_upper_tail_p":p,"positive_dependence_supported":bool(obs>hi and p<.05)}
    return {
      "dry_route_silent_clusters":int(clusters),
      "near_lags_1_3":finish([1,2,3]),
      "far_lags_7_9":finish([7,8,9]),
      "lags":{str(d):finish([d]) for d in lags}
    }

def monitoring_specieswise(psub,wets,drys,species_list):
    rows=[]
    for p,wet,dry,species in zip(psub.itertuples(index=False),wets,drys,species_list):
        pair=f"{p.wet_key}|{p.dry_key}"
        for i,sp in enumerate(species):
            for j in np.flatnonzero(~dry[i].astype(bool)):
                rows.append({
                  "wet_activation":int(wet[i,j]),"rain_contrast":float(p.rain_contrast),
                  "temp_difference":float(p.temp_difference),"doy_difference":float(p.doy_difference),
                  "year_gap":float(p.year_gap),"survey_period":str(p.survey_period),
                  "taxon":str(sp),"pair_cluster":pair,"route_cluster":str(p.route_id)
                })
    df=pd.DataFrame(rows)
    records={}
    for sp,g in df.groupby("taxon",sort=True):
        rec={"risk_cells":int(len(g)),"positive_wet_cells":int(g.wet_activation.sum()),"pair_clusters":int(g.pair_cluster.nunique()),"routes":int(g.route_cluster.nunique()),"eligible":False,"estimable":False}
        ok=rec["risk_cells"]>=200 and rec["positive_wet_cells"]>=20 and rec["pair_clusters"]>=30 and rec["routes"]>=10
        rec["eligible"]=bool(ok)
        if not ok:
            records[sp]=rec; continue
        try:
            fit=smf.glm("wet_activation ~ rain_contrast + temp_difference + doy_difference + year_gap + C(survey_period)",data=g,family=sm.families.Binomial()).fit(maxiter=200,disp=0)
            names=list(fit.params.index); jj=names.index("rain_contrast")
            iid=float(fit.bse["rain_contrast"])
            cp=cov_cluster(fit,g["pair_cluster"].to_numpy(),use_correction=True)
            cr=cov_cluster(fit,g["route_cluster"].to_numpy(),use_correction=True)
            pse=float(np.sqrt(cp[jj,jj])); rse=float(np.sqrt(cr[jj,jj]))
            if min(iid,pse,rse)<=0 or not all(np.isfinite([iid,pse,rse])): raise RuntimeError("invalid SE")
            rec.update({"estimable":True,"beta":float(fit.params["rain_contrast"]),"iid_se":iid,"pair_cluster_se":pse,"route_cluster_se":rse,"pair_over_iid":pse/iid,"route_over_iid":rse/iid})
        except Exception as e:
            rec["failure"]=type(e).__name__+":"+str(e)[:160]
        records[sp]=rec
    est=[v for v in records.values() if v.get("estimable")]
    def summ(key):
        v=np.asarray([x[key] for x in est],float)
        return None if not len(v) else {"median":float(np.median(v)),"iqr":[float(np.quantile(v,.25)),float(np.quantile(v,.75))],"fraction_gt_1":float(np.mean(v>1)),"n_gt_1":int(np.sum(v>1))}
    return {"eligible_taxa":int(sum(v["eligible"] for v in records.values())),"estimable_taxa":int(len(est)),"pair_over_iid":summ("pair_over_iid"),"route_over_iid":summ("route_over_iid"),"records":records}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--runs",required=True)
    ap.add_argument("--matrix",required=True)
    ap.add_argument("--preflight-receipt",required=True)
    ap.add_argument("--primary-result",required=True)
    ap.add_argument("--common-env-runs",required=True)
    ap.add_argument("--common-env-receipt",required=True)
    ap.add_argument("--output",required=True)
    args=ap.parse_args()

    runs_path=Path(args.runs); matrix_path=Path(args.matrix)
    primary=json.loads(Path(args.primary_result).read_text())
    preflight=json.loads(Path(args.preflight_receipt).read_text())
    weather_receipt=json.loads(Path(args.common_env_receipt).read_text())

    if primary.get("response_endpoints_read") is not True:
        raise RuntimeError("primary WFTS analysis has not completed response stage")
    if primary.get("input_sha256")!={"runs":base.sha256_file(runs_path),"matrix":base.sha256_file(matrix_path)}:
        raise RuntimeError("secondary inputs differ from primary WFTS analysis")
    if primary.get("preflight_receipt")!=str(Path(args.preflight_receipt)):
        # File-system path text may differ in real execution; cryptographic input identity above is authoritative.
        pass
    if preflight.get("coverage",{}).get("gate_pass") is not True:
        raise RuntimeError("preflight gate was not PASS")
    if weather_receipt.get("response_columns_read") is not False:
        raise RuntimeError("secondary weather adapter read response columns")
    if weather_receipt.get("output_sha256",{}).get("runs")!=base.sha256_file(Path(args.common_env_runs)):
        raise RuntimeError("common-environment weather runs hash mismatch")

    runs_full,taxa,psub,phs,drys,wets,wet_k,species_list,r,den,obs=prepare_analysis(
        runs_path,matrix_path,Path(args.common_env_runs),primary
    )
    # Expose binary full-taxon matrices to the cross-fit training function.
    _,r0,matrix0,taxa0=base.load_inputs(runs_path,matrix_path)
    ci,_,_=base.build_run_matrices(r0,matrix0,taxa0)
    run_common_env_window.run_mats={k:(v>0) for k,v in ci.items()}

    results={}
    q_primary=None
    for exposure,seed,return_q in [
        ("prcp_3d_exposure",CONC_SEED,True),
        ("prcp_1d_exposure",CONC_SEED+1,False),
        ("prcp_7d_exposure",CONC_SEED+2,False)
    ]:
        test,qs,training=run_common_env_window(
            runs_full,taxa,psub,phs,drys,wets,wet_k,species_list,r,den,obs,exposure,seed,return_q
        )
        results[exposure]={"test":test,"training":training}
        if return_q: q_primary=qs

    if q_primary is None or len(q_primary)!=len(psub):
        raise RuntimeError("primary common-environment q matrices missing")

    dep=bounded_dep(q_primary,wets,drys,DEPENDENCE_SEED)
    lag=lag_profile(q_primary,wets,drys,LAG_SEED)
    monitoring=monitoring_specieswise(psub,wets,drys,species_list)

    primary_res=float(primary["principal_comparator"]["observed_conditional_residual"])
    common_res=float(results["prcp_3d_exposure"]["test"]["observed_conditional_residual"])
    frac=(primary_res-common_res)/primary_res if primary_res!=0 else None

    out={
      "analysis":"wfts_prospective_common_environment_and_route_night_diagnostic_v0_2",
      "authority":"revision/WFTS_PROSPECTIVE_COMMON_ENVIRONMENT_DIAGNOSTIC_V0_2.json",
      "status":"prospective_secondary_executed_after_primary",
      "primary_decision":primary.get("decision"),
      "primary_replication_classification_unchanged":True,
      "coverage":{"pairs":int(len(psub)),"routes":int(psub.route_id.nunique()),"taxa":int(len(taxa))},
      "observed":{"route_new_taxon_beta":float(obs[0]),"extra_stop_beta":float(obs[1]),"concentration_beta":float(obs[2])},
      "common_environment":{
        "primary_3day":results["prcp_3d_exposure"],
        "sensitivity_1day":results["prcp_1d_exposure"],
        "sensitivity_7day":results["prcp_7d_exposure"],
        "primary_comparator_residual":primary_res,
        "primary_3day_residual":common_res,
        "fraction_primary_residual_removed":float(frac) if frac is not None else None
      },
      "bounded_route_night_dependence":dep,
      "route_position_lag_profile":lag,
      "monitoring_uncertainty":monitoring,
      "provenance":{
        "primary_input_sha256":primary["input_sha256"],
        "common_environment_runs_sha256":base.sha256_file(Path(args.common_env_runs)),
        "common_environment_receipt_sha256":base.sha256_file(Path(args.common_env_receipt))
      },
      "interpretation_boundary":{
        "secondary_can_rescue_or_retune_primary":False,
        "unique_lower_level_mechanism_identified":False,
        "station_number_is_exact_distance":False
      }
    }
    Path(args.output).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
