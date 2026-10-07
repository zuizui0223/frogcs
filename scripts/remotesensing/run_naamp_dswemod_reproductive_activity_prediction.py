#!/usr/bin/env python3
from __future__ import annotations

import hashlib, importlib.util, json, math, os
from collections import defaultdict
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
OUT=ROOT/"remotesensing"/"NAAMP_DSWEMOD_REPRODUCTIVE_ACTIVITY_PREDICTION_RECEIPT_V0_1.json"

SEED=2840330
BOOT=10000
MIN_POS=20
MIN_ROUTES=5

def loadmod(name,path):
    s=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(s)
    assert s.loader
    s.loader.exec_module(m)
    return m

flex=loadmod("flex",EXP/"run_naamp_flexible_common_environment_null.py")
hyd=loadmod("hyd",RS/"run_naamp_dynamic_hydrology_mechanism.py")
joint=flex.joint
mem=flex.mem

def expit(x):
    x=np.clip(np.asarray(x,float),-20,20)
    return 1.0/(1.0+np.exp(-x))

def ci_map(raw,eligible,sampled):
    vals=defaultdict(list)
    for r in raw["Counts.csv"]:
        rid=(r.get("RunID") or "").strip()
        st=(r.get("StopNumber") or "").strip()
        sp=(r.get("Species") or "").strip()
        if rid not in eligible or st not in sampled.get(rid,set()) or not sp:
            continue
        try:
            x=int(float((r.get("CallingIndex") or "").strip()))
        except Exception:
            continue
        if x in (1,2,3):
            vals[(rid,st,sp)].append(x)
    return {k:max(v) for k,v in vals.items()}

def m3_population(metrics,raw,runs,psub,dsub,hsub):
    var=metrics[["RunID","SiteID"]].copy()
    var["current_water_fraction_r250"]=pd.to_numeric(metrics["current_D_r500"],errors="coerce")
    var["recent_wetness_3m_r250"]=pd.to_numeric(metrics["recent_D_3m_r500"],errors="coerce")
    var["hydro_sd_12m_r250"]=pd.to_numeric(metrics["DSWE_sd_12m_r500"],errors="coerce")
    return hyd.build_complete_sample(raw,runs,psub,dsub,hsub,var,"M3")

def build_cells(raw,runs,p3,d3,hyd3,pools,sampled,ss,metrics):
    runrow={str(r.RunID):r for r in runs.itertuples(index=False)}
    run_sites={}
    for p,h in zip(p3.itertuples(index=False),hyd3):
        for role in ("wet","dry"):
            rid=str(getattr(p,f"{role}_RunID"))
            ids=list(h["siteids"])
            if rid in run_sites and run_sites[rid]!=ids:
                raise RuntimeError(f"RunID site identity drift {rid}")
            run_sites[rid]=ids

    eligible=set(runs.RunID.astype(str))
    site=mem.site_map(raw,eligible)
    stop_for={}
    for rid,ids in run_sites.items():
        inv={}
        for st in sampled.get(rid,set()):
            sid=site.get((rid,str(st)))
            if sid is not None:
                inv[str(sid)]=str(st)
        for sid in ids:
            if str(sid) not in inv:
                raise RuntimeError(f"missing stop label for {rid} {sid}")
            stop_for[(rid,str(sid))]=inv[str(sid)]

    mm=metrics.copy()
    mm["RunID"]=mm["RunID"].astype(str)
    mm["SiteID"]=mm["SiteID"].astype(str)
    mlookup={(r.RunID,r.SiteID):r for r in mm.itertuples(index=False)}
    ci=ci_map(raw,eligible,sampled)

    rows=[]
    for rid in sorted(run_sites):
        rr=runrow[rid]
        key=(str(rr.State),str(rr.RouteNumber),str(rr.RunNumber))
        species=pools.get(key)
        if species is None:
            raise RuntimeError(f"missing species pool {key}")
        ids=run_sites[rid]
        hydrows=[mlookup.get((rid,str(sid))) for sid in ids]
        if any(z is None for z in hydrows):
            raise RuntimeError(f"missing M3 hydrology row {rid}")
        cur=np.asarray([float(z.current_D_r500) for z in hydrows],float)
        rec=np.asarray([float(z.recent_D_3m_r500) for z in hydrows],float)
        var=np.asarray([float(z.DSWE_sd_12m_r500) for z in hydrows],float)
        if not (np.isfinite(cur).all() and np.isfinite(rec).all() and np.isfinite(var).all()):
            raise RuntimeError(f"nonfinite M3 hydrology on complete run {rid}")
        rc=float(cur.mean()); rr3=float(rec.mean()); rv=float(var.mean())
        theta=2*np.pi*float(rr.doy)/365.25
        fold=joint.fold_for_route(str(rr.route_cluster))
        for sid,cval in zip(ids,cur):
            st=stop_for[(rid,str(sid))]
            for sp in species:
                civ=int(ci.get((rid,st,str(sp)),0))
                rows.append({
                  "RunID":rid,"SiteID":str(sid),"species":str(sp),
                  "route_cluster":str(rr.route_cluster),"route_fold":fold,
                  "State":str(rr.State),"RunNumber":str(rr.RunNumber),
                  "strong":int(civ>=2),"calling":int(civ>=1),
                  "dry_x":math.log1p(float(rr.DaysSinceRain)),
                  "mean_temp_c":float(rr.mean_temp_c),
                  "sin_doy":math.sin(theta),"cos_doy":math.cos(theta),
                  "route_current":rc,
                  "local_current":float(cval-rc),
                  "route_recent3":rr3,
                  "route_variability12":rv
                })
    out=pd.DataFrame(rows)
    if out.empty:
        raise RuntimeError("empty prediction cells")
    return out,run_sites

def matrix(df,model,state_levels,run_levels):
    pieces=[
      np.ones((len(df),1),float),
      df[["dry_x","mean_temp_c","sin_doy","cos_doy"]].to_numpy(float)
    ]
    st=np.zeros((len(df),max(0,len(state_levels)-1)),float)
    smap={v:i for i,v in enumerate(state_levels[1:])}
    for i,v in enumerate(df["State"].astype(str)):
        j=smap.get(v)
        if j is not None: st[i,j]=1.0
    rn=np.zeros((len(df),max(0,len(run_levels)-1)),float)
    rmap={v:i for i,v in enumerate(run_levels[1:])}
    for i,v in enumerate(df["RunNumber"].astype(str)):
        j=rmap.get(v)
        if j is not None: rn[i,j]=1.0
    pieces.extend([st,rn])
    hydcols=[]
    if model in ("B1","B2","B3"):
        hydcols += ["route_current","local_current"]
    if model in ("B2","B3"):
        hydcols += ["route_recent3"]
    if model=="B3":
        hydcols += ["route_variability12"]
    if hydcols:
        pieces.append(df[hydcols].to_numpy(float))
    X=np.column_stack(pieces)
    return X,hydcols

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

def crossfit_predictions(cells,response):
    states=sorted(cells.State.astype(str).unique())
    runlevels=sorted(cells.RunNumber.astype(str).unique())
    species=sorted(cells.species.astype(str).unique())
    pred_rows=[]
    audits=[]
    coef_by_species=defaultdict(lambda:defaultdict(list))

    for train_fold in ("A","B"):
        test_fold="B" if train_fold=="A" else "A"
        for sp in species:
            tr=cells[(cells.route_fold==train_fold)&(cells.species==sp)].copy()
            te=cells[(cells.route_fold==test_fold)&(cells.species==sp)].copy()
            if len(te)==0:
                continue
            y=tr[response].to_numpy(float)
            pos=int(y.sum())
            posroutes=int(tr.loc[y>0,"route_cluster"].nunique()) if len(tr) else 0
            prevalence=float((pos+.5)/(len(tr)+1.0))
            eligible=bool(len(tr)>0 and pos>=MIN_POS and posroutes>=MIN_ROUTES and np.any(y==0))
            methods={}
            params={}
            fail_closed=False

            if eligible:
                for model in ("B0","B1","B2","B3"):
                    Xtr,hydcols=matrix(tr,model,states,runlevels)
                    p,meth=fit_params(y,Xtr)
                    methods[model]=meth
                    params[model]=(p,hydcols)
                    if p is None:
                        fail_closed=True
                        break
            else:
                fail_closed=True
                methods={m:"prevalence_gate" for m in ("B0","B1","B2","B3")}

            if fail_closed:
                probs={m:np.full(len(te),prevalence,float) for m in ("B0","B1","B2","B3")}
                if eligible:
                    methods={m:"prevalence_fail_closed" for m in ("B0","B1","B2","B3")}
            else:
                probs={}
                for model in ("B0","B1","B2","B3"):
                    Xte,hydcols=matrix(te,model,states,runlevels)
                    pp=expit(Xte@params[model][0])
                    probs[model]=np.clip(pp,1e-8,1-1e-8)
                    if model!="B0":
                        hv=params[model][0][-len(hydcols):]
                        for name,beta in zip(hydcols,hv):
                            coef_by_species[sp][name].append(float(beta))

            yte=te[response].to_numpy(int)
            for i,row in enumerate(te.itertuples(index=False)):
                rec={
                  "species":sp,"route_cluster":str(row.route_cluster),
                  "RunID":str(row.RunID),"SiteID":str(row.SiteID),
                  "y":int(yte[i]),"test_fold":test_fold
                }
                for model in ("B0","B1","B2","B3"):
                    rec[f"p_{model}"]=float(probs[model][i])
                pred_rows.append(rec)

            audits.append({
              "species":sp,"training_fold":train_fold,"test_fold":test_fold,
              "training_cells":int(len(tr)),"test_cells":int(len(te)),
              "positive_cells":pos,"positive_routes":posroutes,
              "estimable_gate":eligible,"fail_closed":fail_closed,
              "methods":methods,"prevalence_fallback":prevalence
            })

    pred=pd.DataFrame(pred_rows)
    return pred,audits,coef_by_species

def loss_arrays(pred):
    species=sorted(pred.species.unique())
    routes=sorted(pred.route_cluster.unique())
    si={s:i for i,s in enumerate(species)}
    ri={r:i for i,r in enumerate(routes)}
    nr,ns=len(routes),len(species)
    n=np.zeros((nr,ns),float)
    ll={m:np.zeros((nr,ns),float) for m in ("B0","B1","B2","B3")}
    br={m:np.zeros((nr,ns),float) for m in ("B0","B1","B2","B3")}
    for row in pred.itertuples(index=False):
        a=ri[str(row.route_cluster)]; b=si[str(row.species)]
        y=float(row.y); n[a,b]+=1
        for m in ("B0","B1","B2","B3"):
            p=float(getattr(row,f"p_{m}"))
            ll[m][a,b]+=-(y*math.log(p)+(1-y)*math.log1p(-p))
            br[m][a,b]+=(y-p)**2
    return routes,species,n,ll,br

def observed_scores(n,ll,br,species):
    N=n.sum(axis=0)
    keep=N>0
    logloss={m:ll[m].sum(axis=0)[keep]/N[keep] for m in ll}
    brier={m:br[m].sum(axis=0)[keep]/N[keep] for m in br}
    gains={
      "current_gain":logloss["B0"]-logloss["B1"],
      "recent_gain":logloss["B1"]-logloss["B2"],
      "variability_gain":logloss["B2"]-logloss["B3"],
      "total_gain":logloss["B0"]-logloss["B3"]
    }
    sp=np.asarray(species)[keep]
    return {
      "species_n":int(keep.sum()),
      "logloss_equal_species_mean":{m:float(v.mean()) for m,v in logloss.items()},
      "brier_equal_species_mean":{m:float(v.mean()) for m,v in brier.items()},
      "gain_equal_species_mean":{k:float(v.mean()) for k,v in gains.items()},
      "species_gain":{str(sp[i]):{k:float(v[i]) for k,v in gains.items()} for i in range(len(sp))}
    }

def bootstrap(n,ll):
    rng=np.random.default_rng(SEED)
    nr=n.shape[0]
    vals_total=np.empty(BOOT,float)
    vals_var=np.empty(BOOT,float)
    vals_cur=np.empty(BOOT,float)
    vals_rec=np.empty(BOOT,float)
    for b in range(BOOT):
        idx=rng.integers(0,nr,size=nr)
        N=n[idx].sum(axis=0)
        keep=N>0
        scores={}
        for m in ("B0","B1","B2","B3"):
            scores[m]=ll[m][idx].sum(axis=0)[keep]/N[keep]
        vals_cur[b]=float(np.mean(scores["B0"]-scores["B1"]))
        vals_rec[b]=float(np.mean(scores["B1"]-scores["B2"]))
        vals_var[b]=float(np.mean(scores["B2"]-scores["B3"]))
        vals_total[b]=float(np.mean(scores["B0"]-scores["B3"]))
    def q(x): return [float(np.quantile(x,.025)),float(np.quantile(x,.975))]
    return {
      "replicates":BOOT,"seed":SEED,
      "current_gain_ci95":q(vals_cur),
      "recent_gain_ci95":q(vals_rec),
      "variability_gain_ci95":q(vals_var),
      "total_gain_ci95":q(vals_total),
      "total_support":bool(q(vals_total)[0]>0),
      "variability_support":bool(q(vals_var)[0]>0)
    }

def coef_summary(coefs):
    names=["route_current","local_current","route_recent3","route_variability12"]
    out={}
    for name in names:
        vals=[]
        for sp,d in coefs.items():
            x=d.get(name,[])
            if x:
                vals.append(float(np.mean(x)))
        a=np.asarray(vals,float)
        out[name]={
          "species_n":int(len(a)),
          "median":float(np.median(a)) if len(a) else None,
          "iqr":[float(np.quantile(a,.25)),float(np.quantile(a,.75))] if len(a) else None,
          "positive":int((a>0).sum()) if len(a) else 0,
          "negative":int((a<0).sum()) if len(a) else 0,
          "zero":int((a==0).sum()) if len(a) else 0
        }
    return out

def main():
    if not INCSV.exists():
        raise RuntimeError(f"missing DSWEmod metrics: {INCSV}")
    metrics=pd.read_csv(INCSV,dtype={"RunID":str,"SiteID":str})

    raw,runs,psub,dsub,hsub,pools,sampled,ss=flex.prepare_subset()
    p3,d3,h3,hyd3,site,safe,fail=m3_population(metrics,raw,runs,psub,dsub,hsub)
    coverage={
      "pairs":int(len(p3)),
      "routes":int(p3.route_cluster.nunique()) if len(p3) else 0,
      "states":int(p3.State.nunique()) if len(p3) else 0,
      "failures":fail
    }
    if coverage["pairs"]!=1649 or coverage["routes"]!=324 or coverage["states"]!=19:
        raise RuntimeError(f"frozen M3 population drift: {coverage}")

    cells,run_sites=build_cells(raw,runs,p3,d3,hyd3,pools,sampled,ss,metrics)

    result={
      "analysis":"naamp_dswemod_reproductive_activity_prediction_v0_1",
      "contract":"revision/NAAMP_DSWEMOD_REPRODUCTIVE_ACTIVITY_PREDICTION_CONTRACT_V0_1.md",
      "source_csv_sha256":hashlib.sha256(INCSV.read_bytes()).hexdigest(),
      "coverage":{**coverage,"unique_runids":int(len(run_sites)),"prediction_cells":int(len(cells))},
      "primary_response":"CallingIndex>=2",
      "frog_endpoint_read":True
    }

    pred,audit,coefs=crossfit_predictions(cells,"strong")
    routes,species,n,ll,br=loss_arrays(pred)
    obs=observed_scores(n,ll,br,species)
    boot=bootstrap(n,ll)
    result["primary_strong"]={
      "heldout_rows":int(len(pred)),
      "routes":int(len(routes)),
      "species":int(len(species)),
      "scores":obs,
      "bootstrap":boot,
      "coefficient_summary":coef_summary(coefs),
      "fit_audit":audit,
      "classification":"hydrology_activity_prediction_supported" if boot["total_support"] else "hydrology_activity_prediction_not_supported",
      "variability_classification":"hydrology_variability_prediction_supported" if boot["variability_support"] else "hydrology_variability_prediction_not_supported"
    }

    # Frozen secondary any-calling endpoint.
    pred2,audit2,coefs2=crossfit_predictions(cells,"calling")
    routes2,species2,n2,ll2,br2=loss_arrays(pred2)
    obs2=observed_scores(n2,ll2,br2,species2)
    boot2=bootstrap(n2,ll2)
    result["secondary_any_calling"]={
      "heldout_rows":int(len(pred2)),
      "routes":int(len(routes2)),
      "species":int(len(species2)),
      "scores":obs2,
      "bootstrap":boot2,
      "coefficient_summary":coef_summary(coefs2),
      "fit_audit":audit2,
      "cannot_reverse_primary":True
    }

    result["interpretation_boundary"]={
      "reproductive_acoustic_activity":True,
      "reproductive_success_inferred":False,
      "concentration_mechanism_rescued":False,
      "out_of_route_prediction":True
    }
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps({
      "analysis":result["analysis"],
      "coverage":result["coverage"],
      "primary_strong":{
        "scores":obs,
        "bootstrap":boot,
        "classification":result["primary_strong"]["classification"],
        "variability_classification":result["primary_strong"]["variability_classification"],
        "coefficient_summary":result["primary_strong"]["coefficient_summary"]
      },
      "secondary_any_calling":{
        "scores":obs2,
        "bootstrap":boot2
      }
    },indent=2,sort_keys=True))

if __name__=="__main__":
    main()
