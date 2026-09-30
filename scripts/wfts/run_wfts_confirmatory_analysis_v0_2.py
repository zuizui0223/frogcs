#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf

ROOT=Path(__file__).resolve().parents[2]
SCHEMA_PATH=ROOT/"revision"/"WFTS_CANONICAL_SCHEMA_V0_1.json"

B=1000
SEED=2840223
ANCHOR=0.75
KAPPA=2.0
MIN_POSITIVE_CELLS=20
MIN_POSITIVE_ROUTES=5


def expit(x):
    x=np.asarray(x,float)
    out=np.empty_like(x)
    pos=x>=0
    out[pos]=1.0/(1.0+np.exp(-x[pos]))
    e=np.exp(x[~pos])
    out[~pos]=e/(1.0+e)
    return out


def logit(p):
    p=np.clip(np.asarray(p,float),1e-12,1-1e-12)
    return np.log(p)-np.log1p(-p)


def solve_shift(p,target):
    n=p.size
    if target<=0:
        return np.zeros_like(p)
    if target>=n:
        return np.ones_like(p)
    eta=logit(p)
    lo,hi=-40.0,40.0
    for _ in range(80):
        mid=(lo+hi)/2.0
        if float(expit(eta+mid).sum())<target:
            lo=mid
        else:
            hi=mid
    return expit(eta+(lo+hi)/2.0)


def fold_for_route(route_id):
    b=hashlib.sha256(str(route_id).encode("utf-8")).digest()[0]
    return "A" if b<128 else "B"


def load_inputs(runs_path,matrix_path):
    schema=json.loads(SCHEMA_PATH.read_text())
    runs=pd.read_csv(runs_path)
    matrix=pd.read_csv(matrix_path)

    for col in schema["runs_file"]["required_columns"]:
        if col not in runs:
            raise RuntimeError(f"runs missing required column: {col}")
    for col in schema["matrix_file"]["required_columns"]:
        if col not in matrix:
            raise RuntimeError(f"matrix missing required column: {col}")

    runs=runs.copy()
    matrix=matrix.copy()
    runs["route_id"]=runs["route_id"].astype(str)
    matrix["route_id"]=matrix["route_id"].astype(str)
    runs["survey_period"]=runs["survey_period"].astype(str)
    matrix["survey_period"]=matrix["survey_period"].astype(str)
    runs["survey_year"]=runs["survey_year"].astype(int)
    matrix["survey_year"]=matrix["survey_year"].astype(int)
    runs["survey_date"]=pd.to_datetime(runs["survey_date"],errors="raise")
    matrix["survey_date"]=pd.to_datetime(matrix["survey_date"],errors="raise")
    matrix["station_order"]=matrix["station_order"].astype(int)
    matrix["physical_site_id"]=matrix["physical_site_id"].astype(str)
    matrix["taxon_key"]=matrix["taxon_key"].astype(str)
    matrix["call_index"]=matrix["call_index"].astype(int)

    allowed_periods=set(schema["runs_file"]["survey_period_levels"])
    if not set(runs.survey_period.unique())<=allowed_periods:
        raise RuntimeError("unexpected survey_period level")
    if not set(matrix.survey_period.unique())<=allowed_periods:
        raise RuntimeError("unexpected matrix survey_period level")
    if not set(matrix.station_order.unique())<=set(range(1,11)):
        raise RuntimeError("station_order outside 1..10")
    if not set(matrix.call_index.unique())<=set([0,1,2,3]):
        raise RuntimeError("call_index outside 0..3")

    key=["route_id","survey_period","survey_year"]
    if runs.duplicated(key).any():
        raise RuntimeError("duplicate route-period-year in runs")

    taxa=list(schema["taxa"])
    unknown=sorted(set(matrix.taxon_key.unique())-set(taxa))
    if unknown:
        raise RuntimeError(f"unknown taxon_key values: {unknown}")

    matrix_key=["route_id","survey_period","survey_year","station_order","taxon_key"]
    if matrix.duplicated(matrix_key).any():
        raise RuntimeError("duplicate route-period-year-station-taxon rows in matrix")

    expected=len(runs)*10*len(taxa)
    if len(matrix)!=expected:
        raise RuntimeError(f"matrix is not complete: rows={len(matrix)} expected={expected}")

    run_keys=set(map(tuple,runs[["route_id","survey_period","survey_year"]].to_records(index=False)))
    matrix_keys=set(map(tuple,matrix[["route_id","survey_period","survey_year"]].drop_duplicates().to_records(index=False)))
    if run_keys!=matrix_keys:
        raise RuntimeError("runs/matrix route-period-year keys differ")

    date_check=(
        matrix.groupby(["route_id","survey_period","survey_year"])["survey_date"]
        .nunique()
    )
    if (date_check!=1).any():
        raise RuntimeError("matrix contains multiple dates within a route-period-year")

    return schema,runs,matrix,taxa


def run_key(route,period,year):
    return (str(route),str(period),int(year))


def build_run_matrices(runs,matrix,taxa):
    tax_idx={sp:i for i,sp in enumerate(taxa)}
    out={}
    sites={}
    dates={}

    for r in runs.itertuples(index=False):
        key=run_key(r.route_id,r.survey_period,r.survey_year)
        sub=matrix[
            (matrix.route_id==str(r.route_id))&
            (matrix.survey_period==str(r.survey_period))&
            (matrix.survey_year==int(r.survey_year))
        ].copy()
        if len(sub)!=10*len(taxa):
            raise RuntimeError(f"incomplete run matrix {key}")

        station_rows=(
            sub[["station_order","physical_site_id"]]
            .drop_duplicates()
            .sort_values("station_order")
        )
        if len(station_rows)!=10 or station_rows.station_order.tolist()!=list(range(1,11)):
            raise RuntimeError(f"run lacks exact 10 station orders {key}")

        site_ids=station_rows.physical_site_id.astype(str).tolist()
        m=np.zeros((len(taxa),10),dtype=np.int8)
        for row in sub.itertuples(index=False):
            m[tax_idx[row.taxon_key],int(row.station_order)-1]=int(row.call_index)

        out[key]=m
        sites[key]=site_ids
        dates[key]=pd.Timestamp(r.survey_date)

    return out,sites,dates


def build_support_pools(runs,run_mats,taxa):
    """Route × survey-period taxon support, mirroring NAAMP stratum pools.

    The full eligible time series defines only whether a taxon belongs to the
    candidate support. Probability weights remain strictly prior in the
    principal comparator.
    """
    pools={}
    for (route,period),g in runs.groupby(["route_id","survey_period"],sort=True):
        present=np.zeros(len(taxa),dtype=bool)
        for r in g.itertuples(index=False):
            key=run_key(r.route_id,r.survey_period,r.survey_year)
            present |= (run_mats[key]>0).any(axis=1)
        pools[(str(route),str(period))]=np.flatnonzero(present).astype(int)
    return pools


def build_pairs(runs,sites):
    rows=[]
    for (route,period),g in runs.groupby(["route_id","survey_period"],sort=True):
        g=g.sort_values(["survey_year","survey_date"]).reset_index(drop=True)
        for i in range(len(g)-1):
            a=g.iloc[i]
            b=g.iloc[i+1]
            if float(a.rain_recency)==float(b.rain_recency):
                continue

            ka=run_key(route,period,int(a.survey_year))
            kb=run_key(route,period,int(b.survey_year))
            if sites[ka]!=sites[kb]:
                continue

            if float(a.rain_recency)<float(b.rain_recency):
                wet,dry=a,b
            else:
                wet,dry=b,a

            rows.append({
                "route_id":str(route),
                "survey_period":str(period),
                "wet_year":int(wet.survey_year),
                "dry_year":int(dry.survey_year),
                "year_earlier":int(min(a.survey_year,b.survey_year)),
                "rain_contrast":float(dry.rain_recency-wet.rain_recency),
                "temp_difference":float(wet.tmean_run-dry.tmean_run),
                "doy_difference":float(pd.Timestamp(wet.survey_date).dayofyear-pd.Timestamp(dry.survey_date).dayofyear),
                "year_gap":float(abs(int(b.survey_year)-int(a.survey_year))),
                "wet_key":run_key(route,period,int(wet.survey_year)),
                "dry_key":run_key(route,period,int(dry.survey_year)),
            })
    return pd.DataFrame(rows)


def structural_principal_pairs(pairs,runs,sites):
    keep=[]
    by_group={
        (str(route),str(period)):g.sort_values("survey_year")
        for (route,period),g in runs.groupby(["route_id","survey_period"],sort=False)
    }
    for p in pairs.itertuples(index=False):
        g=by_group[(str(p.route_id),str(p.survey_period))]
        focal_sites=set(sites[p.wet_key])
        prior=[]
        for r in g.itertuples(index=False):
            if int(r.survey_year)>=int(p.year_earlier):
                continue
            key=run_key(r.route_id,r.survey_period,r.survey_year)
            if len(focal_sites & set(sites[key]))>=8:
                prior.append(key)
        keep.append(len(prior)>0)
    return pairs.loc[np.asarray(keep,bool)].copy().reset_index(drop=True)


def design_residual(df):
    x=df["rain_contrast"].to_numpy(float)
    theta=[]
    pieces=[
        np.ones((len(df),1),float),
        df[["temp_difference","doy_difference","year_gap"]].to_numpy(float),
        pd.get_dummies(df["survey_period"].astype(str),drop_first=True,dtype=float).to_numpy(),
    ]
    z=np.column_stack(pieces)
    coef=np.linalg.lstsq(z,x,rcond=None)[0]
    r=x-z@coef
    den=float(r@r)
    if not np.isfinite(den) or den<=0:
        raise RuntimeError("invalid residualized rain denominator")
    return r,den


def fit_species_slopes(runs,run_mats,taxa,training_fold):
    x=runs.copy()
    x["route_fold"]=x["route_id"].astype(str).map(fold_for_route)
    x=x[x.route_fold==training_fold].copy().reset_index(drop=True)
    theta=2*np.pi*x["survey_date"].dt.dayofyear.astype(float)/365.25
    x["sin_doy"]=np.sin(theta)
    x["cos_doy"]=np.cos(theta)

    slopes={}
    audit={}
    for j,sp in enumerate(taxa):
        y=np.asarray([
            np.sum(run_mats[run_key(r.route_id,r.survey_period,r.survey_year)][j,:]>0)
            for r in x.itertuples(index=False)
        ],float)
        pos_cells=int(y.sum())
        pos_routes=int(x.loc[y>0,"route_id"].astype(str).nunique())
        info={
            "positive_stop_cells":pos_cells,
            "positive_routes":pos_routes,
            "estimable":False,
            "method":"zero_differential_shift",
            "dryness_beta":0.0,
            "wet_shift_gamma":0.0,
        }
        if pos_cells<MIN_POSITIVE_CELLS or pos_routes<MIN_POSITIVE_ROUTES:
            slopes[sp]=0.0
            audit[sp]=info
            continue

        d=x[["survey_period","tmean_run","rain_recency","sin_doy","cos_doy"]].copy()
        d["prop"]=y/10.0
        glm=smf.glm(
            "prop ~ rain_recency + tmean_run + sin_doy + cos_doy + C(survey_period)",
            data=d,
            family=sm.families.Binomial(),
            freq_weights=np.repeat(10.0,len(d)),
        )
        method="glm"
        try:
            fit=glm.fit(maxiter=200,disp=0)
            beta=float(fit.params["rain_recency"])
            if not np.isfinite(beta) or abs(beta)>20:
                raise RuntimeError("unstable species slope")
        except Exception:
            method="ridge_fallback"
            fit=glm.fit_regularized(alpha=0.01,L1_wt=0.0,maxiter=1000)
            beta=float(fit.params["rain_recency"])
            if not np.isfinite(beta):
                beta=0.0
                method="zero_after_failed_regularization"

        gamma=float(-beta)
        slopes[sp]=gamma
        info.update({
            "estimable":bool(method!="zero_after_failed_regularization"),
            "method":method,
            "dryness_beta":beta,
            "wet_shift_gamma":gamma,
        })
        audit[sp]=info

    return slopes,audit,{
        "training_fold":training_fold,
        "n_runs":int(len(x)),
        "n_routes":int(x.route_id.nunique()),
        "n_taxa":int(len(taxa)),
        "n_taxa_estimable":int(sum(v["estimable"] for v in audit.values())),
    }


def prior_probs_for_pair(p,runs,run_mats,sites,pool_idx):
    focal_sites=sites[p.wet_key]
    site_index={sid:i for i,sid in enumerate(focal_sites)}
    prior=[]
    g=runs[
        (runs.route_id.astype(str)==str(p.route_id))&
        (runs.survey_period.astype(str)==str(p.survey_period))&
        (runs.survey_year.astype(int)<int(p.year_earlier))
    ].sort_values("survey_year")

    for r in g.itertuples(index=False):
        key=run_key(r.route_id,r.survey_period,r.survey_year)
        if len(set(focal_sites)&set(sites[key]))>=8:
            prior.append(key)

    if not prior:
        raise RuntimeError("principal pair unexpectedly lacks prior history")

    y=np.zeros((len(pool_idx),10),float)
    exposure=np.zeros(10,float)
    for key in prior:
        m=run_mats[key]
        current_sites=sites[key]
        pos={sid:i for i,sid in enumerate(current_sites)}
        for t,sid in enumerate(focal_sites):
            if sid not in pos:
                continue
            exposure[t]+=1.0
            y[:,t]+=(m[pool_idx,pos[sid]]>0).astype(float)

    total_site_exposure=float(exposure.sum())
    mu0=(float(y.sum())+0.5)/(max(1.0,total_site_exposure*len(pool_idx))+1.0)
    ys=y.sum(axis=1)
    mus=(ys+KAPPA*mu0)/(total_site_exposure+KAPPA)
    p_hist=(y+KAPPA*mus[:,None])/(exposure[None,:]+KAPPA)
    return np.clip(p_hist,1e-8,1-1e-8),{
        "prior_runs":int(len(prior)),
        "site_exposure_min":float(exposure.min()),
        "site_exposure_median":float(np.median(exposure)),
        "site_exposure_max":float(exposure.max()),
    }


def pair_metrics(w,d):
    d_route=d.any(axis=1)
    route_new=(~d_route)&w.any(axis=1)
    if not np.any(route_new):
        return np.asarray([0.0,0.0,0.0])
    k=w[route_new].sum(axis=1).astype(float)
    extra=np.maximum(k-1.0,0.0)
    concentration=extra*np.maximum(extra-1.0,0.0)/2.0
    return np.asarray([float(len(k)),float(extra.sum()),float(concentration.sum())])


def sim_metrics(w,d):
    d_route=d.any(axis=1)
    route_new=(~d_route[None,:])&w.any(axis=2)
    k=w.sum(axis=2).astype(float)
    extra=np.maximum(k-1.0,0.0)*route_new
    concentration=extra*np.maximum(extra-1.0,0.0)/2.0
    return np.column_stack([
        route_new.sum(axis=1).astype(float),
        extra.sum(axis=1).astype(float),
        concentration.sum(axis=1).astype(float),
    ])


def conditional_test(sim,obs):
    X=np.column_stack([np.ones(len(sim)),sim[:,0],sim[:,1]])
    y=sim[:,2]
    coef=np.linalg.lstsq(X,y,rcond=None)[0]
    pred=X@coef
    resid=y-pred
    obs_pred=float(coef[0]+coef[1]*obs[0]+coef[2]*obs[1])
    obs_resid=float(obs[2]-obs_pred)
    lo,hi=np.quantile(resid,[0.025,0.975])
    p=float((1+np.sum(resid>=obs_resid))/(len(resid)+1))
    return {
        "predicted_concentration_beta":obs_pred,
        "observed_conditional_residual":obs_resid,
        "null_residual_ci95":[float(lo),float(hi)],
        "upper_tail_p":p,
        "pass":bool(obs_resid>hi),
        "null_regression":[float(x) for x in coef],
    }


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--runs",required=True)
    ap.add_argument("--matrix",required=True)
    ap.add_argument("--output",required=True)
    args=ap.parse_args()

    schema,runs,matrix,taxa=load_inputs(args.runs,args.matrix)
    run_mats_ci,sites,dates=build_run_matrices(runs,matrix,taxa)
    run_mats={k:(v>0) for k,v in run_mats_ci.items()}
    support_pools=build_support_pools(runs,run_mats_ci,taxa)

    pairs=build_pairs(runs,sites)
    psub=structural_principal_pairs(pairs,runs,sites)

    routes=int(psub.route_id.nunique())
    fold_counts={
        fold:int(psub.loc[psub.route_id.astype(str).map(fold_for_route)==fold,"route_id"].nunique())
        for fold in ("A","B")
    }
    gate=bool(
        routes>=schema["coverage_gate"]["minimum_routes"] and
        len(psub)>=schema["coverage_gate"]["minimum_principal_pairs"] and
        min(fold_counts.values())>=schema["coverage_gate"]["minimum_routes_per_fold"]
    )

    out={
        "analysis":"wfts_prospective_within_taxon_concentration_v0_2",
        "schema":"revision/WFTS_CANONICAL_SCHEMA_V0_1.json",
        "candidate_support_rule":"RouteID x SurveyPeriod union of taxa positive in any eligible run; used as support only",
        "coverage":{
            "eligible_runs":int(len(runs)),
            "all_matched_pairs":int(len(pairs)),
            "principal_history_pairs":int(len(psub)),
            "principal_routes":routes,
            "routes_by_fold":fold_counts,
            "gate_pass":gate,
        },
        "response_endpoints_read":False,
    }

    if not gate:
        Path(args.output).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
        print(json.dumps(out,indent=2,sort_keys=True))
        return

    slopes_A,audit_A,fold_A=fit_species_slopes(runs,run_mats,taxa,"A")
    slopes_B,audit_B,fold_B=fit_species_slopes(runs,run_mats,taxa,"B")
    slopes_by_train={"A":slopes_A,"B":slopes_B}

    obs_rows=[]
    p_hist=[]
    wet_mats=[]
    dry_mats=[]
    wet_k=[]
    histories=[]
    pair_species=[]
    for p in psub.itertuples(index=False):
        pool_idx=support_pools[(str(p.route_id),str(p.survey_period))]
        wet=run_mats[p.wet_key][pool_idx,:]
        dry=run_mats[p.dry_key][pool_idx,:]
        ph,ha=prior_probs_for_pair(p,runs,run_mats,sites,pool_idx)
        obs_rows.append(pair_metrics(wet,dry))
        p_hist.append(ph)
        wet_mats.append(wet)
        dry_mats.append(dry)
        wet_k.append(int(wet.sum()))
        pair_species.append([taxa[int(j)] for j in pool_idx])
        histories.append(ha)

    r,den=design_residual(psub)
    obs=(r[:,None]*np.asarray(obs_rows,float)).sum(axis=0)/den

    rng=np.random.default_rng(SEED)
    numer=np.zeros((B,3),float)
    for i,(p,ph,dry,target,species) in enumerate(zip(psub.itertuples(index=False),p_hist,dry_mats,wet_k,pair_species)):
        test_fold=fold_for_route(str(p.route_id))
        train_fold="B" if test_fold=="A" else "A"
        slopes=slopes_by_train[train_fold]

        p_anchor=(1.0-ANCHOR)*ph+ANCHOR*dry.astype(float)
        p_anchor=np.clip(p_anchor,1e-8,1-1e-8)
        gamma=np.asarray([float(slopes.get(sp,0.0)) for sp in species],float)
        eta=logit(p_anchor)+gamma[:,None]*float(p.rain_contrast)
        pre=expit(eta)
        q=solve_shift(pre,target)
        wsim=rng.random((B,)+q.shape)<q[None,:,:]
        numer += r[i]*sim_metrics(wsim,dry)

    sim=numer/den
    test=conditional_test(sim,obs)

    out.update({
        "response_endpoints_read":True,
        "observed":{
            "route_new_taxon_beta":float(obs[0]),
            "extra_stop_beta":float(obs[1]),
            "within_taxon_concentration_beta":float(obs[2]),
        },
        "species_shift_training":{
            "fold_A":fold_A,
            "fold_B":fold_B,
            "minimum_positive_stop_cells":MIN_POSITIVE_CELLS,
            "minimum_positive_routes":MIN_POSITIVE_ROUTES,
        },
        "history_audit":{
            "median_prior_runs":float(np.median([x["prior_runs"] for x in histories])),
            "median_min_site_exposure":float(np.median([x["site_exposure_min"] for x in histories])),
        },
        "principal_comparator":test,
        "decision":"replication_support" if test["pass"] else "replication_not_supported",
        "interpretation_boundary":{
            "external_to_discovery_dataset":True,
            "methodologically_unrelated_network_claim":False,
            "causal_rainfall_claim":False,
            "unique_lower_level_mechanism_identified":False,
            "retuning_after_readback_authorized":False,
        },
    })

    Path(args.output).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,indent=2,sort_keys=True))


if __name__=="__main__":
    main()
