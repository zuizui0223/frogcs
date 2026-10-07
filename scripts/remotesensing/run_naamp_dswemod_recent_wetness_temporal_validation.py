#!/usr/bin/env python3
from __future__ import annotations
import hashlib, importlib.util, json, math, os
from pathlib import Path
import numpy as np
import pandas as pd
import statsmodels.api as sm

ROOT=Path(__file__).resolve().parents[2]
EXP=ROOT/"exploration"
RS=ROOT/"scripts"/"remotesensing"
INCSV=Path(os.environ.get(
    "NAAMP_DSWEMOD_CSV",
    str(ROOT/"remotesensing"/"NAAMP_DSWEMOD_RUN_SITE_METRICS_V0_1.csv")
))
OUT=ROOT/"remotesensing"/"NAAMP_DSWEMOD_RECENT_WETNESS_TEMPORAL_VALIDATION_RECEIPT_V0_1.json"

TRAIN_YEARS={2003,2005,2006,2007,2008,2009}
TEST_YEARS={2010,2011,2012,2013,2014,2015}
MIN_POS=20
MIN_ROUTES=5
BOOT=10000
SEED=2840360

def loadmod(name,path):
    s=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(s); assert s.loader; s.loader.exec_module(m); return m

pred=loadmod("pred",RS/"run_naamp_dswemod_reproductive_activity_prediction.py")
flex=pred.flex

def expit(x):
    x=np.clip(np.asarray(x,float),-20,20)
    return 1/(1+np.exp(-x))

def matrix(df,with_recent,state_levels,run_levels):
    pieces=[
      np.ones((len(df),1),float),
      df[["dry_x","mean_temp_c","sin_doy","cos_doy"]].to_numpy(float)
    ]
    st=np.zeros((len(df),max(0,len(state_levels)-1)),float)
    smap={v:i for i,v in enumerate(state_levels[1:])}
    for i,v in enumerate(df["State"].astype(str)):
        j=smap.get(v)
        if j is not None: st[i,j]=1
    rn=np.zeros((len(df),max(0,len(run_levels)-1)),float)
    rmap={v:i for i,v in enumerate(run_levels[1:])}
    for i,v in enumerate(df["RunNumber"].astype(str)):
        j=rmap.get(v)
        if j is not None: rn[i,j]=1
    pieces.extend([st,rn])
    if with_recent:
        pieces.append(df[["route_recent3"]].to_numpy(float))
    return np.column_stack(pieces)

def fit_params(y,X):
    try:
        fit=sm.GLM(y,X,family=sm.families.Binomial()).fit(maxiter=200,disp=0)
        p=np.asarray(fit.params,float)
        if not np.all(np.isfinite(p)) or np.max(np.abs(p))>50:
            raise RuntimeError("unstable")
        return p,"glm"
    except Exception:
        try:
            fit=sm.GLM(y,X,family=sm.families.Binomial()).fit_regularized(
                alpha=.01,L1_wt=0.0,maxiter=1000
            )
            p=np.asarray(fit.params,float)
            if not np.all(np.isfinite(p)) or np.max(np.abs(p))>50:
                raise RuntimeError("unstable ridge")
            return p,"ridge"
        except Exception:
            return None,"failed"

def score_table(preds):
    rows=[]
    for sp,g in preds.groupby("species"):
        y=g.y.to_numpy(float)
        p0=np.clip(g.p_T0.to_numpy(float),1e-8,1-1e-8)
        p1=np.clip(g.p_T1.to_numpy(float),1e-8,1-1e-8)
        ll0=float(np.mean(-(y*np.log(p0)+(1-y)*np.log1p(-p0))))
        ll1=float(np.mean(-(y*np.log(p1)+(1-y)*np.log1p(-p1))))
        br0=float(np.mean((y-p0)**2))
        br1=float(np.mean((y-p1)**2))
        rows.append({"species":sp,"n":len(g),"logloss_T0":ll0,"logloss_T1":ll1,
                     "gain":ll0-ll1,"brier_T0":br0,"brier_T1":br1,"brier_gain":br0-br1})
    return pd.DataFrame(rows)

def bootstrap_routes(preds):
    routes=np.array(sorted(preds.route_cluster.astype(str).unique()))
    rng=np.random.default_rng(SEED)
    byroute={r:preds[preds.route_cluster.astype(str)==r].copy() for r in routes}
    gains=np.empty(BOOT,float)
    for b in range(BOOT):
        picks=rng.choice(routes,size=len(routes),replace=True)
        parts=[]
        for k,r in enumerate(picks):
            z=byroute[r].copy()
            # preserve duplicated bootstrap clusters as distinct pseudo-routes
            z["boot_route"]=f"{k}:{r}"
            parts.append(z)
        z=pd.concat(parts,ignore_index=True)
        st=score_table(z)
        gains[b]=float(st.gain.mean())
    return {
      "replicates":BOOT,"seed":SEED,
      "ci95":[float(np.quantile(gains,.025)),float(np.quantile(gains,.975))],
      "support_fraction_positive":float(np.mean(gains>0))
    }

def main():
    if not INCSV.exists(): raise RuntimeError(f"missing DSWEmod metrics {INCSV}")
    metrics=pd.read_csv(INCSV,dtype={"RunID":str,"SiteID":str})
    raw,runs,psub,dsub,hsub,pools,sampled,ss=flex.prepare_subset()
    p3,d3,h3,hyd3,site,safe,fail=pred.m3_population(metrics,raw,runs,psub,dsub,hsub)
    cells,run_sites=pred.build_cells(raw,runs,p3,d3,hyd3,pools,sampled,ss,metrics)

    year_map={str(r.RunID):int(r.SurveyYear) for r in runs.itertuples(index=False)}
    cells["SurveyYear"]=cells.RunID.astype(str).map(year_map)
    tr=cells[cells.SurveyYear.isin(TRAIN_YEARS)].copy()
    te=cells[cells.SurveyYear.isin(TEST_YEARS)].copy()
    if tr.empty or te.empty: raise RuntimeError("empty temporal split")

    species=sorted(te.species.astype(str).unique())
    states=sorted(tr.State.astype(str).unique())
    runlevels=sorted(tr.RunNumber.astype(str).unique())

    pred_rows=[]
    audit=[]
    recent_betas=[]
    for sp in species:
        a=tr[tr.species.astype(str)==sp].copy()
        b=te[te.species.astype(str)==sp].copy()
        if b.empty: continue
        y=a.strong.to_numpy(float)
        pos=int(y.sum())
        posroutes=int(a.loc[y>0,"route_cluster"].astype(str).nunique()) if len(a) else 0
        prev=float((pos+.5)/(len(a)+1)) if len(a) else .5
        eligible=bool(len(a)>0 and pos>=MIN_POS and posroutes>=MIN_ROUTES and np.any(y==0))
        method0=method1="prevalence_gate"
        p0=p1=None
        beta_recent=None
        fail_closed=True

        if eligible:
            X0=matrix(a,False,states,runlevels)
            X1=matrix(a,True,states,runlevels)
            q0,method0=fit_params(y,X0)
            q1,method1=fit_params(y,X1)
            if q0 is not None and q1 is not None:
                Xt0=matrix(b,False,states,runlevels)
                Xt1=matrix(b,True,states,runlevels)
                p0=np.clip(expit(Xt0@q0),1e-8,1-1e-8)
                p1=np.clip(expit(Xt1@q1),1e-8,1-1e-8)
                beta_recent=float(q1[-1])
                recent_betas.append(beta_recent)
                fail_closed=False

        if fail_closed:
            p0=np.full(len(b),prev,float)
            p1=np.full(len(b),prev,float)
            if eligible:
                method0=method1="prevalence_fail_closed"

        for i,row in enumerate(b.itertuples(index=False)):
            pred_rows.append({
              "species":sp,"route_cluster":str(row.route_cluster),
              "RunID":str(row.RunID),"SiteID":str(row.SiteID),"SurveyYear":int(row.SurveyYear),
              "y":int(row.strong),"p_T0":float(p0[i]),"p_T1":float(p1[i])
            })
        audit.append({"species":sp,"training_cells":int(len(a)),"validation_cells":int(len(b)),
                      "positive_training_cells":pos,"positive_training_routes":posroutes,
                      "estimable_gate":eligible,"fail_closed":fail_closed,
                      "method_T0":method0,"method_T1":method1,"beta_recent3":beta_recent})

    preds=pd.DataFrame(pred_rows)
    scores=score_table(preds)
    observed=float(scores.gain.mean())
    brier_gain=float(scores.brier_gain.mean())
    boot=bootstrap_routes(preds)
    ci=boot["ci95"]
    support=bool(observed>0 and ci[0]>0)

    # Fixed robustness diagnostics.
    loo={}
    total=float(scores.gain.sum())
    n=len(scores)
    for r in scores.itertuples(index=False):
        loo[str(r.species)]=float((total-float(r.gain))/(n-1)) if n>1 else None

    out={
      "analysis":"naamp_dswemod_recent_wetness_temporal_validation_v0_1",
      "contract":"revision/NAAMP_DSWEMOD_RECENT_WETNESS_TEMPORAL_VALIDATION_V0_1.md",
      "source_csv_sha256":hashlib.sha256(INCSV.read_bytes()).hexdigest(),
      "split":{"training_years":sorted(TRAIN_YEARS),"validation_years":sorted(TEST_YEARS)},
      "coverage":{"training_cells":int(len(tr)),"validation_cells":int(len(te)),
                  "validation_routes":int(te.route_cluster.nunique()),"validation_species":int(te.species.nunique()),
                  "m3_population_pairs":int(len(p3)),"m3_population_routes":int(p3.route_cluster.nunique())},
      "observed_equal_species_mean_logloss_gain":observed,
      "observed_equal_species_mean_brier_gain":brier_gain,
      "bootstrap":boot,
      "species_diagnostics":{"positive_gain":int((scores.gain>0).sum()),
                             "negative_gain":int((scores.gain<0).sum()),
                             "zero_gain":int((scores.gain==0).sum()),
                             "min_leave_one_species_out_gain":float(min(v for v in loo.values() if v is not None)),
                             "max_leave_one_species_out_gain":float(max(v for v in loo.values() if v is not None)),
                             "species_gain":{str(r.species):float(r.gain) for r in scores.itertuples(index=False)}},
      "coefficient_summary":{"estimable_species":int(sum(x["beta_recent3"] is not None for x in audit)),
                             "median_beta_recent3":float(np.median(recent_betas)) if recent_betas else None,
                             "positive_beta":int(sum(x>0 for x in recent_betas)),
                             "negative_beta":int(sum(x<0 for x in recent_betas))},
      "fit_audit":audit,
      "classification":"recent_wetness_temporal_transfer_supported" if support else "recent_wetness_temporal_transfer_not_supported",
      "interpretation_boundary":{"hydrological_memory_hypothesis":support,
                                 "reproductive_acoustic_activity":True,
                                 "reproductive_success_inferred":False,
                                 "concentration_mechanism_explained":False,
                                 "post_discovery_prospective_validation":True}
    }
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps({k:out[k] for k in ["analysis","split","coverage","observed_equal_species_mean_logloss_gain","observed_equal_species_mean_brier_gain","bootstrap","species_diagnostics","coefficient_summary","classification"]},indent=2,sort_keys=True))

if __name__=="__main__": main()
