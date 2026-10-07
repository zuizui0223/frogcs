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
SEED2=2840322
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
    for train_fold in ("A","B"):
        idx=np.flatnonzero(cells.route_fold.to_numpy()==train_fold)
        d0=cells.iloc[idx].copy().reset_index(drop=True)
        c0=[callers[i] for i in idx]
        habitats=sorted(d0.habitat.astype(str).unique())
        states=sorted(d0.State.astype(str).unique())
        runs=sorted(d0.RunNumber.astype(str).unique())

        # Fold-level nuisance design shared across species:
        # intercept, temperature, season, state, run, habitat main effects.
        base=[
          np.ones(len(d0),float),
          d0["mean_temp_c"].to_numpy(float),
          d0["sin_doy"].to_numpy(float),
          d0["cos_doy"].to_numpy(float)
        ]
        for v in states[1:]:
            base.append((d0.State.astype(str).to_numpy()==v).astype(float))
        for v in runs[1:]:
            base.append((d0.RunNumber.astype(str).to_numpy()==v).astype(float))
        for h in habitats[1:]:
            base.append((d0.habitat.astype(str).to_numpy()==h).astype(float))

        # Direct within-SiteID dryness slopes for each habitat. Site-centering
        # removes persistent location quality before estimating rain response.
        d0["dry_x_c"]=d0["dry_x"]-d0.groupby("SiteID")["dry_x"].transform("mean")
        dry=d0["dry_x_c"].to_numpy(float)
        hvec=d0.habitat.astype(str).to_numpy()
        slope_cols=[dry*(hvec==h).astype(float) for h in habitats]
        X=np.column_stack(base+slope_cols)
        slope_start=X.shape[1]-len(habitats)
        rank=int(np.linalg.matrix_rank(X))

        foldmap={};foldaudit={}
        routes=d0.route_cluster.astype(str).to_numpy()
        for sp in all_species:
            y=np.asarray([1.0 if sp in z else 0.0 for z in c0],float)
            hinfo={}
            eligible=[]
            for h in habitats:
                m=(hvec==h)
                pos=int(y[m].sum())
                posroutes=int(len(set(routes[m & (y>0)])))
                cells_h=int(m.sum())
                ok=bool(pos>=MIN_POS and posroutes>=MIN_ROUTES)
                hinfo[h]={"positive_cells":pos,"positive_routes":posroutes,
                          "training_cells":cells_h,"estimable_gate":ok}
                if ok:
                    eligible.append(h)

            deltas={h:0.0 for h in habitats}
            method="zero_gate"
            slopes={h:None for h in habitats}

            if len(eligible)>=2 and y.sum()>=MIN_POS and np.any(y==0):
                mod=sm.GLM(y,X,family=sm.families.Binomial())
                params=None
                method="glm"
                try:
                    if rank!=X.shape[1]:
                        raise RuntimeError(f"rank deficient {rank}/{X.shape[1]}")
                    fit=mod.fit(maxiter=200,disp=0)
                    params=np.asarray(fit.params,float)
                    if not np.all(np.isfinite(params)):
                        raise RuntimeError("nonfinite")
                except Exception:
                    method="ridge_fallback"
                    try:
                        fit=mod.fit_regularized(alpha=.01,L1_wt=0.0,maxiter=1000)
                        params=np.asarray(fit.params,float)
                        if not np.all(np.isfinite(params)):
                            params=None
                    except Exception:
                        params=None

                if params is not None:
                    raw_slopes=np.asarray(params[slope_start:],float)
                    if np.all(np.isfinite(raw_slopes)) and np.all(np.abs(raw_slopes)<=20):
                        slopes={h:float(b) for h,b in zip(habitats,raw_slopes)}
                        w=np.asarray([hinfo[h]["training_cells"] for h in eligible],float)
                        b=np.asarray([slopes[h] for h in eligible],float)
                        mean_beta=float(np.average(b,weights=w))
                        for h in eligible:
                            # wet response gamma = -dryness beta;
                            # only habitat-relative redistribution is added to M0.
                            deltas[h]=float(-(slopes[h]-mean_beta))
                        method=method
                    else:
                        method="zero_unstable"
                else:
                    method="zero_failed"

            for h in habitats:
                hinfo[h]["beta_dry_joint"]=slopes[h]
                hinfo[h]["delta_gamma"]=float(deltas[h])
                hinfo[h]["used_interaction"]=bool(h in eligible and len(eligible)>=2 and method in ("glm","ridge_fallback"))

            foldmap[sp]=deltas
            foldaudit[sp]={
              "method":method,
              "eligible_habitats":eligible,
              "habitats":hinfo
            }

        out[train_fold]=foldmap
        audit[train_fold]={
          "training_cells":int(len(d0)),
          "training_routes":int(d0.route_cluster.nunique()),
          "design_columns":int(X.shape[1]),
          "design_rank":rank,
          "habitat_counts":{str(k):int(v) for k,v in d0.habitat.value_counts().to_dict().items()},
          "species":foldaudit
        }
    return out,audit

def simulate(model,pfinal,dsub,hsub,hab,rain_slopes,hab_delta,r,den,seed):
    rng=np.random.default_rng(seed)
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
    if not ASSIGN.exists() or not COVERAGE.exists():
        raise RuntimeError("missing NWI coverage inputs")
    cov=json.load(open(COVERAGE))
    out={
      "analysis":"naamp_nwi_water_regime_rain_filter_v0_2",
      "contract":"revision/NAAMP_NWI_WATER_REGIME_RAIN_FILTER_EXTENSION_V0_2.md",
      "coverage_receipt":cov,
      "assignment_sha256":hashlib.sha256(ASSIGN.read_bytes()).hexdigest(),
      "frog_endpoint_read":False
    }
    if not cov.get("gate_pass",False):
        out["classification"]="nwi_water_regime_coverage_inconclusive"
        OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
        print(json.dumps(out,indent=2,sort_keys=True))
        return

    adf=pd.read_csv(ASSIGN,dtype={"SiteID":str})
    complete=adf[
        adf["query_success"].fillna(False).astype(bool)
        & adf["code_join_success"].fillna(False).astype(bool)
        & adf["WATER_REGIME_NAME"].notna()
        & adf["WETLAND_TYPE"].notna()
    ].copy()
    regime_assign={str(r.SiteID):str(r.WATER_REGIME_NAME) for r in complete.itertuples(index=False)}
    type_assign={str(r.SiteID):str(r.WETLAND_TYPE) for r in complete.itertuples(index=False)}

    raw,runs,psub,dsub,hsub,pools,sampled,ss=flex.prepare_subset()
    p,d,h,regime_hab,site,fail=build_complete_sample(
        raw,runs,psub,dsub,hsub,regime_assign
    )
    p2,d2,h2,type_hab,site2,fail2=build_complete_sample(
        raw,runs,psub,dsub,hsub,type_assign
    )
    keycols=["wet_RunID","dry_RunID"]
    keys1=[tuple(map(str,x)) for x in p[keycols].to_numpy()] if len(p) else []
    keys2=[tuple(map(str,x)) for x in p2[keycols].to_numpy()] if len(p2) else []
    if keys1!=keys2:
        raise RuntimeError("primary and secondary NWI samples differ")

    gate=bool(len(p)>=1500 and p.route_cluster.nunique()>=300 and p.State.nunique()>=15)
    out["analysis_sample"]={
      "pairs":int(len(p)),
      "routes":int(p.route_cluster.nunique()) if len(p) else 0,
      "states":int(p.State.nunique()) if len(p) else 0,
      "primary_failures":fail,
      "secondary_failures":fail2,
      "gate_pass":gate
    }
    if not gate:
        out["classification"]="nwi_water_regime_analysis_sample_inconclusive"
        OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
        print(json.dumps(out,indent=2,sort_keys=True))
        return

    out["frog_endpoint_read"]=True
    all_species=sorted({sp for spp in pools.values() for sp in spp})
    rainA,audA,foldA=joint.fit_species_slopes(runs,sampled,ss,all_species,"A")
    rainB,audB,foldB=joint.fit_species_slopes(runs,sampled,ss,all_species,"B")
    rain={"A":rainA,"B":rainB}

    regime_cells,regime_callers=build_training_cells(
        raw,runs,sampled,ss,site,regime_assign
    )
    regime_delta,regime_audit=fit_habitat_deltas(
        regime_cells,regime_callers,all_species
    )

    type_cells,type_callers=build_training_cells(
        raw,runs,sampled,ss,site,type_assign
    )
    type_delta,type_audit=fit_habitat_deltas(
        type_cells,type_callers,all_species
    )

    obs_rows=np.asarray([flex.metrics(z["wet"],z["dry"]) for z in d],float)
    rr,den=uniform.design_residual(p)
    obs=(rr[:,None]*obs_rows).sum(axis=0)/den

    sim0,sa0=simulate("M0",p,d,h,regime_hab,rain,regime_delta,rr,den,SEED0)
    simr,sar=simulate("MNWI",p,d,h,regime_hab,rain,regime_delta,rr,den,SEED1)
    simt,sat=simulate("MNWI",p,d,h,type_hab,rain,type_delta,rr,den,SEED2)
    m0=flex.conditional(sim0,obs)
    mr=flex.conditional(simr,obs)
    mt=flex.conditional(simt,obs)

    r0=float(m0["observed_conditional_residual"])
    rr1=float(mr["observed_conditional_residual"])
    rt1=float(mt["observed_conditional_residual"])
    frac_regime=float((r0-rr1)/r0) if r0!=0 else None
    frac_type=float((r0-rt1)/r0) if r0!=0 else None
    sufficient=bool(not mr["above_upper_95"])

    out.update({
      "observed":{
        "route_new_species_beta":float(obs[0]),
        "extra_stop_beta":float(obs[1]),
        "concentration_beta":float(obs[2])
      },
      "models":{"M0":m0,"M_REGIME":mr,"M_TYPE":mt},
      "fraction_residual_removed_regime":frac_regime,
      "fraction_residual_removed_type_secondary":frac_type,
      "regime_sufficient":sufficient,
      "training":{
        "water_regime":regime_audit,
        "wetland_type_secondary":type_audit,
        "rainfall":{"fold_A":foldA,"fold_B":foldB}
      },
      "shift_audit":{"M0":sa0,"M_REGIME":sar,"M_TYPE":sat},
      "classification":"nwi_water_regime_filter_sufficient" if sufficient else (
        "nwi_water_regime_filter_partial" if frac_regime is not None and frac_regime>0
        else "nwi_water_regime_filter_not_supported"
      ),
      "secondary_boundary":{
        "WETLAND_TYPE_cannot_rescue_primary":True
      }
    })
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps({
      "analysis":out["analysis"],
      "analysis_sample":out["analysis_sample"],
      "observed":out["observed"],
      "models":out["models"],
      "fraction_residual_removed_regime":frac_regime,
      "fraction_residual_removed_type_secondary":frac_type,
      "classification":out["classification"]
    },indent=2,sort_keys=True))

if __name__=="__main__":main()
