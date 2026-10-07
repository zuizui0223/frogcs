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
METRICS=Path(os.environ.get("NAAMP_NWI_AMOUNT",str(ROOT/"remotesensing"/"NAAMP_NWI_WETLAND_AMOUNT_V0_1.csv")))
COVERAGE=Path(os.environ.get("NAAMP_NWI_AMOUNT_COVERAGE",str(ROOT/"remotesensing"/"NAAMP_NWI_WETLAND_AMOUNT_COVERAGE_V0_1.json")))
OUT=ROOT/"remotesensing"/"NAAMP_NWI_WETLAND_AMOUNT_MECHANISM_RECEIPT_V0_1.json"

B=1000
SEED0=2840340
SEED1=2840341
ANCHOR=.75
MIN_POS=20
MIN_ROUTES=5

def loadmod(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);assert s.loader;s.loader.exec_module(m);return m

flex=loadmod("flex",EXP/"run_naamp_flexible_common_environment_null.py")
joint=flex.joint
mem=flex.mem
uniform=flex.uniform

def build_sample(raw,runs,psub,dsub,hsub,metric):
    eligible=set(runs.RunID.astype(str));site=mem.site_map(raw,eligible)
    kp=[];kd=[];kh=[];areas=[];fail=defaultdict(int)
    for p,dct,ph in zip(psub.itertuples(index=False),dsub,hsub):
        ids=mem.focal_siteids(p,dct,site)
        if ids is None or len(ids)!=10:
            fail["siteid_identity"]+=1;continue
        vals=[]
        ok=True
        for sid in ids:
            v=metric.get(str(sid))
            if v is None or not np.isfinite(v):
                fail["wetland_amount_missing"]+=1;ok=False;break
            vals.append(float(v))
        if not ok:continue
        kp.append(p);kd.append(dct);kh.append(ph)
        areas.append(np.asarray(vals,float))
    return pd.DataFrame([x._asdict() for x in kp]),kd,kh,areas,site,dict(fail)

def training_cells(runs,sampled,ss,site,metric):
    rows=[];callers=[]
    for r in runs.itertuples(index=False):
        rid=str(r.RunID);fold=joint.fold_for_route(str(r.route_cluster))
        theta=2*np.pi*float(r.doy)/365.25
        for st in sorted(sampled.get(rid,set())):
            sid=site.get((rid,str(st)))
            if sid is None:continue
            A=metric.get(str(sid))
            if A is None or not np.isfinite(A):continue
            rows.append({
              "RunID":rid,"route_cluster":str(r.route_cluster),"route_fold":fold,
              "State":str(r.State),"RunNumber":str(r.RunNumber),"SiteID":str(sid),
              "dry_x":math.log1p(float(r.DaysSinceRain)),
              "mean_temp_c":float(r.mean_temp_c),
              "sin_doy":math.sin(theta),"cos_doy":math.cos(theta),
              "A":float(A)
            })
            callers.append(ss.get((rid,str(st)),set()))
    return pd.DataFrame(rows),callers

def design_fold(d):
    x=d.copy().reset_index(drop=True)
    x["dry_x_c"]=x["dry_x"]-x.groupby("SiteID")["dry_x"].transform("mean")
    am=float(x["A"].mean());asd=float(x["A"].std(ddof=0))
    if not np.isfinite(asd) or asd<=0:
        asd=0.0;x["A_z"]=0.0
    else:
        x["A_z"]=(x["A"]-am)/asd
    x["rain_area"]=x["dry_x_c"]*x["A_z"]
    states=sorted(x.State.astype(str).unique())
    runs=sorted(x.RunNumber.astype(str).unique())
    cols=[
      np.ones(len(x),float),
      x["dry_x_c"].to_numpy(float),
      x["A_z"].to_numpy(float),
      x["rain_area"].to_numpy(float),
      x["mean_temp_c"].to_numpy(float),
      x["sin_doy"].to_numpy(float),
      x["cos_doy"].to_numpy(float)
    ]
    for v in states[1:]:
        cols.append((x.State.astype(str).to_numpy()==v).astype(float))
    for v in runs[1:]:
        cols.append((x.RunNumber.astype(str).to_numpy()==v).astype(float))
    return x,np.column_stack(cols),{"A_mean":am,"A_sd":asd,"states":states,"runs":runs}

def fit_area(cells,callers,all_species):
    out={};audit={};scales={}
    for train_fold in ("A","B"):
        idx=np.flatnonzero(cells.route_fold.to_numpy()==train_fold)
        d=cells.iloc[idx].copy()
        c=[callers[i] for i in idx]
        x,X,scale=design_fold(d)
        scales[train_fold]={"A_mean":scale["A_mean"],"A_sd":scale["A_sd"]}
        routes=x.route_cluster.astype(str).to_numpy()
        rank=int(np.linalg.matrix_rank(X))
        foldmap={};foldaudit={}
        for sp in all_species:
            y=np.asarray([1.0 if sp in z else 0.0 for z in c],float)
            pos=int(y.sum());pr=int(len(set(routes[y>0])))
            delta=0.0;method="zero_gate";beta=None
            if pos>=MIN_POS and pr>=MIN_ROUTES and np.any(y==0) and scale["A_sd"]>0:
                mod=sm.GLM(y,X,family=sm.families.Binomial())
                params=None
                if rank==X.shape[1]:
                    try:
                        fit=mod.fit(maxiter=200,disp=0)
                        params=np.asarray(fit.params,float);method="glm"
                        if not np.all(np.isfinite(params)):params=None
                    except Exception:
                        params=None
                if params is None:
                    try:
                        fit=mod.fit_regularized(alpha=.01,L1_wt=0.0,maxiter=1000)
                        params=np.asarray(fit.params,float);method="ridge_fallback"
                        if not np.all(np.isfinite(params)):params=None
                    except Exception:
                        params=None
                if params is not None:
                    beta=float(params[3])
                    if np.isfinite(beta) and abs(beta)<=20:
                        delta=float(-beta)
                    else:
                        beta=None;delta=0.0;method="zero_unstable"
                else:
                    method="zero_failed"
            foldmap[sp]=delta
            foldaudit[sp]={"positive_cells":pos,"positive_routes":pr,
                           "beta_dryness_x_area":beta,"delta_wet_response_per_Az":delta,
                           "method":method}
        out[train_fold]=foldmap
        audit[train_fold]={
          "training_cells":int(len(x)),"training_routes":int(x.route_cluster.nunique()),
          "design_rank":rank,"design_columns":int(X.shape[1]),
          "A_mean":float(scale["A_mean"]),"A_sd":float(scale["A_sd"]),
          "species_estimable":int(sum(v["method"] in ("glm","ridge_fallback") for v in foldaudit.values())),
          "species":foldaudit
        }
    return out,audit,scales

def simulate(model,p,d,h,areas,rain,adelta,scales,r,den):
    rng=np.random.default_rng(SEED0 if model=="M0" else SEED1)
    num=np.zeros((B,3),float);sh=[]
    for i,(pp,dct,ph,A) in enumerate(zip(p.itertuples(index=False),d,h,areas)):
        if len(dct["species"])==0:continue
        test=joint.fold_for_route(str(pp.route_cluster));train="B" if test=="A" else "A"
        gamma=np.asarray([float(rain[train].get(sp,0.0)) for sp in dct["species"]],float)
        dry=dct["dry"].astype(float)
        pa=(1-ANCHOR)*ph+ANCHOR*dry
        pa=np.clip(pa,1e-8,1-1e-8)
        eta=uniform.logit(pa)+gamma[:,None]*float(pp.rain_contrast)
        if model=="MAREA":
            sc=scales[train];sd=float(sc["A_sd"])
            Az=np.zeros(10,float) if sd<=0 else (A-float(sc["A_mean"]))/sd
            dg=np.asarray([float(adelta[train].get(sp,0.0)) for sp in dct["species"]],float)
            hs=dg[:,None]*Az[None,:]*float(pp.rain_contrast)
            eta=eta+hs;sh.append(np.abs(hs).ravel())
        q=uniform.solve_shift(uniform.expit(eta),dct["wet_k"])
        w=rng.random((B,)+q.shape)<q[None,:,:]
        num+=r[i]*flex.sim_metrics(w,dct["dry"])
    z=np.concatenate(sh) if sh else np.asarray([],float)
    return num/den,{
      "mean_abs_area_logit_shift":float(z.mean()) if len(z) else 0.0,
      "q95_abs_area_logit_shift":float(np.quantile(z,.95)) if len(z) else 0.0
    }

def main():
    if not METRICS.exists() or not COVERAGE.exists():raise RuntimeError("missing wetland amount inputs")
    cov=json.load(open(COVERAGE))
    out={
      "analysis":"naamp_nwi_wetland_amount_rain_mechanism_v0_1",
      "contract":"revision/NAAMP_NWI_WETLAND_AMOUNT_RAIN_MECHANISM_CONTRACT_V0_1.md",
      "coverage_receipt":cov,
      "metric_sha256":hashlib.sha256(METRICS.read_bytes()).hexdigest(),
      "frog_endpoint_read":False
    }
    if not cov.get("gate_pass",False):
        out["classification"]="wetland_amount_coverage_inconclusive"
        OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print(json.dumps(out,indent=2,sort_keys=True));return

    df=pd.read_csv(METRICS,dtype={"SiteID":str})
    good=df.query_success.map(lambda x:str(x).strip().lower() in ("true","1","yes"))
    metric={str(r.SiteID):float(r.wetland_area_fraction_500m) for r in df.loc[good].itertuples(index=False) if pd.notna(r.wetland_area_fraction_500m)}

    raw,runs,psub,dsub,hsub,pools,sampled,ss=flex.prepare_subset()
    p,d,h,A,site,fail=build_sample(raw,runs,psub,dsub,hsub,metric)
    gate=bool(len(p)>=1500 and p.route_cluster.nunique()>=300 and p.State.nunique()>=15)
    out["analysis_sample"]={"pairs":int(len(p)),"routes":int(p.route_cluster.nunique()) if len(p) else 0,
                            "states":int(p.State.nunique()) if len(p) else 0,"failures":fail,"gate_pass":gate}
    if not gate:
        out["classification"]="wetland_amount_analysis_sample_inconclusive"
        OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print(json.dumps(out,indent=2,sort_keys=True));return

    out["frog_endpoint_read"]=True
    all_species=sorted({sp for spp in pools.values() for sp in spp})
    rainA,audA,foldA=joint.fit_species_slopes(runs,sampled,ss,all_species,"A")
    rainB,audB,foldB=joint.fit_species_slopes(runs,sampled,ss,all_species,"B")
    rain={"A":rainA,"B":rainB}
    cells,callers=training_cells(runs,sampled,ss,site,metric)
    adelta,aaudit,scales=fit_area(cells,callers,all_species)

    obs_rows=np.asarray([flex.metrics(z["wet"],z["dry"]) for z in d],float)
    rr,den=uniform.design_residual(p)
    obs=(rr[:,None]*obs_rows).sum(axis=0)/den
    sim0,sa0=simulate("M0",p,d,h,A,rain,adelta,scales,rr,den)
    sim1,sa1=simulate("MAREA",p,d,h,A,rain,adelta,scales,rr,den)
    m0=flex.conditional(sim0,obs);m1=flex.conditional(sim1,obs)
    r0=float(m0["observed_conditional_residual"]);r1=float(m1["observed_conditional_residual"])
    frac=float((r0-r1)/r0) if r0!=0 else None
    sufficient=bool(not m1["above_upper_95"])
    out.update({
      "observed":{"route_new_species_beta":float(obs[0]),"extra_stop_beta":float(obs[1]),"concentration_beta":float(obs[2])},
      "models":{"M0":m0,"M_AREA":m1},
      "fraction_residual_removed":frac,
      "AREA_sufficient":sufficient,
      "area_training":aaudit,
      "area_scales":scales,
      "shift_audit":{"M0":sa0,"M_AREA":sa1},
      "classification":"wetland_amount_filter_sufficient" if sufficient else ("wetland_amount_filter_partial" if frac is not None and frac>0 else "wetland_amount_filter_not_supported")
    })
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps({
      "analysis":out["analysis"],"analysis_sample":out["analysis_sample"],
      "observed":out["observed"],"models":out["models"],
      "fraction_residual_removed":frac,"classification":out["classification"]
    },indent=2,sort_keys=True))

if __name__=="__main__":main()
