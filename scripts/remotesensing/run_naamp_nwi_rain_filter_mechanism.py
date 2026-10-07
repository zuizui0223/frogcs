#!/usr/bin/env python3
from __future__ import annotations

import hashlib, importlib.util, json, math, os
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf

ROOT=Path(__file__).resolve().parents[2]
EXP=ROOT/"exploration"
RS=ROOT/"scripts"/"remotesensing"
ASSIGN=Path(os.environ.get("NAAMP_NWI_ASSIGNMENTS",str(ROOT/"remotesensing"/"NAAMP_NWI_SITE_ASSIGNMENTS_V0_1.csv")))
COVERAGE=Path(os.environ.get("NAAMP_NWI_COVERAGE",str(ROOT/"remotesensing"/"NAAMP_NWI_COVERAGE_V0_1.json")))
OUT=ROOT/"remotesensing"/"NAAMP_NWI_RAIN_FILTER_MECHANISM_RECEIPT_V0_1.json"

B=1000
SEED0=2840320
SEED1=2840321
ANCHOR=.75
MIN_POS=20
MIN_ROUTES=5

def loadmod(name,path):
    s=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(s); assert s.loader; s.loader.exec_module(m); return m

flex=loadmod("flex",EXP/"run_naamp_flexible_common_environment_null.py")
hyd=loadmod("hyd",RS/"run_naamp_dynamic_hydrology_mechanism.py")
joint=flex.joint
mem=flex.mem
uniform=flex.uniform

def fit_dry_slope(d):
    if len(d)==0 or d["y"].sum()<MIN_POS or d.loc[d.y>0,"route_cluster"].astype(str).nunique()<MIN_ROUTES or d["y"].nunique()<2:
        return None,"zero_gate"
    formula="y ~ dry_x + mean_temp_c + sin_doy + cos_doy + C(State) + C(RunNumber)"
    mod=smf.glm(formula,data=d,family=sm.families.Binomial())
    try:
        fit=mod.fit(maxiter=200,disp=0)
        beta=float(fit.params["dry_x"])
        if not np.isfinite(beta) or abs(beta)>20: raise RuntimeError("unstable")
        return beta,"glm"
    except Exception:
        try:
            fit=mod.fit_regularized(alpha=.01,L1_wt=0.0,maxiter=1000)
            beta=float(fit.params["dry_x"])
            if not np.isfinite(beta) or abs(beta)>20:return None,"zero_unstable"
            return beta,"ridge"
        except Exception:
            return None,"zero_failed"

def build_complete_sample(raw,runs,psub,dsub,hsub,assign):
    eligible=set(runs.RunID.astype(str))
    site=mem.site_map(raw,eligible)
    safe=hyd.strict_routes()
    kp=[];kd=[];kh=[];hab=[];fail=defaultdict(int)
    for p,dct,ph in zip(psub.itertuples(index=False),dsub,hsub):
        if str(p.RouteNumber) not in safe:
            fail["strict_geometry"]+=1;continue
        ids=mem.focal_siteids(p,dct,site)
        if ids is None or len(ids)!=10:
            fail["siteid_identity"]+=1;continue
        hh=[]
        ok=True
        for sid in ids:
            h=assign.get(str(sid))
            if h is None:
                fail["nwi_missing"]+=1;ok=False;break
            hh.append(h)
        if not ok:continue
        kp.append(p);kd.append(dct);kh.append(ph);hab.append({"siteids":list(ids),"habitat":list(hh)})
    return pd.DataFrame([x._asdict() for x in kp]),kd,kh,hab,site,dict(fail)

def build_training_cells(raw,runs,sampled,ss,site,assign):
    rows=[];callers=[]
    for r in runs.itertuples(index=False):
        rid=str(r.RunID)
        fold=joint.fold_for_route(str(r.route_cluster))
        theta=2*np.pi*float(r.doy)/365.25
        for st in sorted(sampled.get(rid,set())):
            sid=site.get((rid,str(st)))
            if sid is None:continue
            h=assign.get(str(sid))
            if h is None:continue
            rows.append({
              "RunID":rid,"route_cluster":str(r.route_cluster),"route_fold":fold,
              "State":str(r.State),"RunNumber":str(r.RunNumber),
              "dry_x":math.log1p(float(r.DaysSinceRain)),"mean_temp_c":float(r.mean_temp_c),
              "sin_doy":math.sin(theta),"cos_doy":math.cos(theta),
              "SiteID":str(sid),"habitat":str(h)
            })
            callers.append(ss.get((rid,str(st)),set()))
    return pd.DataFrame(rows),callers

def fit_habitat_deltas(cells,callers,all_species):
    out={};audit={}
    habitats=sorted(cells.habitat.astype(str).unique())
    for train_fold in ("A","B"):
        mask=np.flatnonzero(cells.route_fold.to_numpy()==train_fold)
        d0=cells.iloc[mask].reset_index(drop=True)
        c0=[callers[i] for i in mask]
        foldmap={};foldaudit={}
        for sp in all_species:
            y=np.asarray([1 if sp in z else 0 for z in c0],int)
            base=d0.copy();base["y"]=y
            beta_all,method_all=fit_dry_slope(base)
            rec={"global_beta":beta_all,"global_method":method_all,"habitats":{}}
            deltas={}
            if beta_all is None:
                for h in habitats:
                    deltas[h]=0.0;rec["habitats"][h]={"delta_gamma":0.0,"method":"zero_global"}
            else:
                for h in habitats:
                    dh=base[base.habitat.astype(str)==h].copy()
                    beta_h,method=fit_dry_slope(dh)
                    pos=int(dh.y.sum()) if len(dh) else 0
                    pr=int(dh.loc[dh.y>0,"route_cluster"].astype(str).nunique()) if len(dh) else 0
                    if beta_h is None:
                        delta=0.0
                    else:
                        # gamma=-beta, so habitat-specific deviation in wet response:
                        delta=float(-(beta_h-beta_all))
                    deltas[h]=delta
                    rec["habitats"][h]={"beta_h":beta_h,"delta_gamma":delta,"method":method,
                                          "positive_cells":pos,"positive_routes":pr,"cells":int(len(dh))}
            foldmap[sp]=deltas;foldaudit[sp]=rec
        out[train_fold]=foldmap
        audit[train_fold]={
          "training_cells":int(len(d0)),"training_routes":int(d0.route_cluster.nunique()),
          "habitat_counts":{str(k):int(v) for k,v in d0.habitat.value_counts().to_dict().items()},
          "species":foldaudit
        }
    return out,audit

def simulate(model,pfinal,dsub,hsub,hab,rain_slopes,hab_delta,r,den):
    rng=np.random.default_rng(SEED0 if model=="M0" else SEED1)
    num=np.zeros((B,3),float)
    shifts=[]
    for i,(p,dct,ph,hb) in enumerate(zip(pfinal.itertuples(index=False),dsub,hsub,hab)):
        if len(dct["species"])==0:continue
        dry=dct["dry"].astype(float)
        p_anchor=(1-ANCHOR)*ph+ANCHOR*dry
        p_anchor=np.clip(p_anchor,1e-8,1-1e-8)
        test_fold=joint.fold_for_route(str(p.route_cluster))
        train_fold="B" if test_fold=="A" else "A"
        gamma=np.asarray([float(rain_slopes[train_fold].get(sp,0.0)) for sp in dct["species"]],float)
        eta=uniform.logit(p_anchor)+gamma[:,None]*float(p.rain_contrast)
        if model=="MNWI":
            dg=np.zeros((len(dct["species"]),10),float)
            for j,sp in enumerate(dct["species"]):
                smap=hab_delta[train_fold].get(sp,{})
                dg[j,:]=[float(smap.get(str(h),0.0)) for h in hb["habitat"]]
            hs=dg*float(p.rain_contrast)
            eta=eta+hs
            shifts.append(np.abs(hs).ravel())
        q=uniform.solve_shift(uniform.expit(eta),dct["wet_k"])
        w=rng.random((B,)+q.shape)<q[None,:,:]
        num+=r[i]*flex.sim_metrics(w,dct["dry"])
    shift=np.concatenate(shifts) if shifts else np.asarray([],float)
    return num/den,{
      "mean_abs_habitat_logit_shift":float(shift.mean()) if len(shift) else 0.0,
      "q95_abs_habitat_logit_shift":float(np.quantile(shift,.95)) if len(shift) else 0.0
    }

def main():
    if not ASSIGN.exists() or not COVERAGE.exists():raise RuntimeError("missing NWI coverage inputs")
    cov=json.load(open(COVERAGE))
    out={
      "analysis":"naamp_nwi_rain_filter_mechanism_v0_1",
      "contract":"revision/NAAMP_NWI_RAIN_FILTER_MECHANISM_CONTRACT_V0_1.md",
      "coverage_receipt":cov,
      "assignment_sha256":hashlib.sha256(ASSIGN.read_bytes()).hexdigest(),
      "frog_endpoint_read":False
    }
    if not cov.get("gate_pass",False):
        out["classification"]="nwi_coverage_inconclusive"
        OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
        print(json.dumps(out,indent=2,sort_keys=True));return

    adf=pd.read_csv(ASSIGN,dtype={"SiteID":str})
    assign={
      str(r.SiteID):str(r.WETLAND_TYPE)
      for r in adf.itertuples(index=False)
      if bool(r.query_success) and pd.notna(r.WETLAND_TYPE)
    }
    raw,runs,psub,dsub,hsub,pools,sampled,ss=flex.prepare_subset()
    p,d,h,hab,site,fail=build_complete_sample(raw,runs,psub,dsub,hsub,assign)
    gate=bool(len(p)>=1500 and p.route_cluster.nunique()>=300 and p.State.nunique()>=15)
    out["analysis_sample"]={"pairs":int(len(p)),"routes":int(p.route_cluster.nunique()) if len(p) else 0,
                            "states":int(p.State.nunique()) if len(p) else 0,"failures":fail,"gate_pass":gate}
    if not gate:
        out["classification"]="nwi_analysis_sample_inconclusive"
        OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
        print(json.dumps(out,indent=2,sort_keys=True));return

    out["frog_endpoint_read"]=True
    all_species=sorted({sp for spp in pools.values() for sp in spp})
    rainA,audA,foldA=joint.fit_species_slopes(runs,sampled,ss,all_species,"A")
    rainB,audB,foldB=joint.fit_species_slopes(runs,sampled,ss,all_species,"B")
    rain={"A":rainA,"B":rainB}
    cells,callers=build_training_cells(raw,runs,sampled,ss,site,assign)
    hd,ha=fit_habitat_deltas(cells,callers,all_species)

    obs_rows=np.asarray([flex.metrics(z["wet"],z["dry"]) for z in d],float)
    rr,den=uniform.design_residual(p)
    obs=(rr[:,None]*obs_rows).sum(axis=0)/den
    sim0,sa0=simulate("M0",p,d,h,hab,rain,hd,rr,den)
    sim1,sa1=simulate("MNWI",p,d,h,hab,rain,hd,rr,den)
    m0=flex.conditional(sim0,obs);m1=flex.conditional(sim1,obs)
    r0=float(m0["observed_conditional_residual"]);r1=float(m1["observed_conditional_residual"])
    frac=float((r0-r1)/r0) if r0!=0 else None
    sufficient=bool(not m1["above_upper_95"])
    out.update({
      "observed":{"route_new_species_beta":float(obs[0]),"extra_stop_beta":float(obs[1]),"concentration_beta":float(obs[2])},
      "models":{"M0":m0,"M_NWI":m1},
      "fraction_residual_removed":frac,
      "NWI_sufficient":sufficient,
      "habitat_training":ha,
      "shift_audit":{"M0":sa0,"M_NWI":sa1},
      "classification":"nwi_rain_filter_sufficient" if sufficient else ("nwi_rain_filter_partial" if frac is not None and frac>0 else "nwi_rain_filter_not_supported")
    })
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps({
      "analysis":out["analysis"],"analysis_sample":out["analysis_sample"],
      "observed":out["observed"],"models":out["models"],
      "fraction_residual_removed":frac,"classification":out["classification"]
    },indent=2,sort_keys=True))

if __name__=="__main__":main()
