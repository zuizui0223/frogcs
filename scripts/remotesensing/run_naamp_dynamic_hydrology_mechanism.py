#!/usr/bin/env python3
from __future__ import annotations

import csv, hashlib, importlib.util, io, json, math, os, urllib.request
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm

ROOT=Path(__file__).resolve().parents[2]
EXP=ROOT/"exploration"
OUT=ROOT/"remotesensing"/"NAAMP_DYNAMIC_HYDROLOGY_MECHANISM_RECEIPT_V0_1.json"

VAR_CSV=Path(os.environ.get(
    "NAAMP_HYDRO_VARIABILITY_CSV",
    str(ROOT/"remotesensing"/"NAAMP_JRC_V1_HYDROLOGY_VARIABILITY_V0_1.csv")
))

COORD_URL="https://www.sciencebase.gov/catalog/file/get/583dc314e4b0d1899f9dea8d?f=__disk__77%2F22%2F7e%2F77227ec46ac1c01592cd7d158d442cd8343a7536"
COORD_SHA="f71a87df9fc94e0d6c5d4466b4745c3bbaff874cbe7c28796b3f9eb44c2e6e83"

B=1000
ANCHOR=0.75
MIN_POSITIVE_CELLS=20
MIN_POSITIVE_ROUTES=5
SEEDS={"M0":2840310,"M1":2840311,"M2":2840312,"M3":2840313}

def loadmod(name,path):
    s=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(s)
    assert s.loader
    s.loader.exec_module(m)
    return m

flex=loadmod("flex",EXP/"run_naamp_flexible_common_environment_null.py")
joint=flex.joint
mem=flex.mem
uniform=flex.uniform

def fetch(url):
    req=urllib.request.Request(url,headers={"User-Agent":"frogcs-dynamic-hydrology-mechanism/0.1"})
    with urllib.request.urlopen(req,timeout=180) as r:
        return r.read()

def hav(lat1,lon1,lat2,lon2):
    R=6371.0088
    a1,a2=math.radians(lat1),math.radians(lat2)
    dlat=math.radians(lat2-lat1); dlon=math.radians(lon2-lon1)
    h=math.sin(dlat/2)**2+math.cos(a1)*math.cos(a2)*math.sin(dlon/2)**2
    return 2*R*math.asin(min(1.0,math.sqrt(h)))

def strict_routes():
    b=fetch(COORD_URL)
    if hashlib.sha256(b).hexdigest()!=COORD_SHA:
        raise RuntimeError("coordinate SHA drift")
    byroute=defaultdict(list)
    for r in csv.DictReader(io.StringIO(b.decode("utf-8-sig"))):
        rid=(r.get("RouteNumber") or "").strip()
        sid=(r.get("SiteID") or "").strip()
        if not rid or not sid: continue
        byroute[rid].append((sid,float(r["lat"]),float(r["lon"])))
    good=set()
    for rid,pts in byroute.items():
        bysid=defaultdict(set)
        for sid,lat,lon in pts:
            bysid[sid].add((lat,lon))
        if any(len(v)>1 for v in bysid.values()): continue
        u=[]
        for sid,v in bysid.items():
            lat,lon=next(iter(v)); u.append((sid,lat,lon))
        if len(u)<8 or any(not(24<=x[1]<=50 and -125<=x[2]<=-66) for x in u): continue
        ds=[hav(u[i][1],u[i][2],u[j][1],u[j][2]) for i in range(len(u)) for j in range(i+1,len(u))]
        if ds and max(ds)>30: continue
        mlat=float(np.median([x[1] for x in u])); mlon=float(np.median([x[2] for x in u]))
        d=np.asarray([hav(x[1],x[2],mlat,mlon) for x in u],float)
        if len(d) and float(d.max())>15: continue
        med=float(np.median(d)) if len(d) else 0.0
        mad=float(np.median(np.abs(d-med))) if len(d) else 0.0
        if mad>0 and np.any(d>med+8*mad): continue
        good.add(rid)
    return good

def run_months(runs):
    return {
      str(r.RunID):(int(r.SurveyYear),(date(int(r.SurveyYear),1,1)+timedelta(days=int(r.doy)-1)).month)
      for r in runs.itertuples(index=False)
    }

def build_complete_sample(raw,runs,psub,dsub,hsub,var,level):
    if level not in ("M1","M3"):
        raise ValueError(level)
    eligible=set(runs.RunID.astype(str))
    site=mem.site_map(raw,eligible)
    safe=strict_routes()

    vv={}
    for r in var.itertuples(index=False):
        cur=getattr(r,"current_water_fraction_r250")
        recent=getattr(r,"recent_wetness_3m_r250")
        sd=getattr(r,"hydro_sd_12m_r250")
        vv[(str(r.RunID),str(r.SiteID))]={
          "current_water":float(cur) if pd.notna(cur) else None,
          "recent3":float(recent) if pd.notna(recent) else None,
          "sd12":float(sd) if pd.notna(sd) else None
        }

    kp=[]; kd=[]; kh=[]; hydro=[]
    fail=defaultdict(int)
    for p,dct,ph in zip(psub.itertuples(index=False),dsub,hsub):
        if str(p.RouteNumber) not in safe:
            fail["strict_geometry"]+=1; continue
        ids=mem.focal_siteids(p,dct,site)
        if ids is None or len(ids)!=10:
            fail["siteid_identity"]+=1; continue
        wetid=str(p.wet_RunID); dryid=str(p.dry_RunID)
        Hw=[]; Hd=[]; Rw=[]; Rd=[]; Sw=[]; Sd=[]
        ok=True
        for sid in ids:
            vw=vv.get((wetid,sid)); vd=vv.get((dryid,sid))
            if vw is None or vd is None:
                fail["hydrology_row_missing"]+=1; ok=False; break
            if vw["current_water"] is None or vd["current_water"] is None:
                fail["current_missing"]+=1; ok=False; break
            if level=="M3" and (
                vw["recent3"] is None or vd["recent3"] is None or
                vw["sd12"] is None or vd["sd12"] is None
            ):
                fail["m3_missing"]+=1; ok=False; break
            Hw.append(vw["current_water"]); Hd.append(vd["current_water"])
            Rw.append(vw["recent3"] if vw["recent3"] is not None else np.nan)
            Rd.append(vd["recent3"] if vd["recent3"] is not None else np.nan)
            Sw.append(vw["sd12"] if vw["sd12"] is not None else np.nan)
            Sd.append(vd["sd12"] if vd["sd12"] is not None else np.nan)
        if not ok:
            continue
        kp.append(p); kd.append(dct); kh.append(ph)
        hydro.append({
          "siteids":ids,
          "wet_H":np.asarray(Hw,float),"dry_H":np.asarray(Hd,float),
          "wet_recent":np.asarray(Rw,float),"dry_recent":np.asarray(Rd,float),
          "wet_sd":np.asarray(Sw,float),"dry_sd":np.asarray(Sd,float)
        })

    pfinal=pd.DataFrame([x._asdict() for x in kp])
    return pfinal,kd,kh,hydro,site,safe,dict(fail)

def build_run_specs(pfinal,dsub,hydro,runs):
    runrow={str(r.RunID):r for r in runs.itertuples(index=False)}
    specs={}
    for p,dct,h in zip(pfinal.itertuples(index=False),dsub,hydro):
        for role in ("wet","dry"):
            rid=str(getattr(p,f"{role}_RunID"))
            row=runrow[rid]
            vals={
              "H":h[f"{role}_H"],
              "recent":h[f"{role}_recent"],
              "sd":h[f"{role}_sd"]
            }
            spec={
              "RunID":rid,"route_cluster":str(row.route_cluster),"State":str(row.State),
              "RunNumber":str(row.RunNumber),"DaysSinceRain":float(row.DaysSinceRain),
              "mean_temp_c":float(row.mean_temp_c),"doy":float(row.doy),
              "stops":list(dct["stops"]),"siteids":list(h["siteids"]),**vals
            }
            if rid in specs:
                if specs[rid]["siteids"]!=spec["siteids"]:
                    raise RuntimeError(f"RunID site identity drift {rid}")
            else:
                specs[rid]=spec
    return specs

def cell_frame(run_specs,ss):
    rows=[]; callers=[]
    for rid,s in sorted(run_specs.items()):
        theta=2*np.pi*s["doy"]/365.25
        fold=joint.fold_for_route(s["route_cluster"])
        for j,(st,sid) in enumerate(zip(s["stops"],s["siteids"])):
            rows.append({
              "RunID":rid,"route_cluster":s["route_cluster"],"route_fold":fold,
              "State":s["State"],"RunNumber":s["RunNumber"],
              "dry_x":math.log1p(s["DaysSinceRain"]),"mean_temp_c":s["mean_temp_c"],
              "sin_doy":math.sin(theta),"cos_doy":math.cos(theta),
              "H":float(s["H"][j]),"recent":float(s["recent"][j]),"sd":float(s["sd"][j]),
              "StopNumber":str(st),"SiteID":sid
            })
            callers.append(ss.get((rid,str(st)),set()))
    cells=pd.DataFrame(rows)
    for rawc,newc in [("H","H_c"),("recent","recent_c"),("sd","sd_c")]:
        cells[newc]=cells[rawc]-cells.groupby("SiteID")[rawc].transform("mean")
        cells[newc]=cells[newc]-cells.groupby("RunID")[newc].transform("mean")
    return cells,callers

def design_matrix(cells,mask,model,state_levels,run_levels):
    x=cells.loc[mask].copy()
    base=np.column_stack([
      np.ones(len(x),float),
      x["dry_x"].to_numpy(float),
      x["mean_temp_c"].to_numpy(float),
      x["sin_doy"].to_numpy(float),
      x["cos_doy"].to_numpy(float)
    ])
    state=np.zeros((len(x),max(0,len(state_levels)-1)),float)
    smap={v:i for i,v in enumerate(state_levels[1:])}
    for i,v in enumerate(x["State"].astype(str)):
        j=smap.get(v)
        if j is not None: state[i,j]=1
    rn=np.zeros((len(x),max(0,len(run_levels)-1)),float)
    rmap={v:i for i,v in enumerate(run_levels[1:])}
    for i,v in enumerate(x["RunNumber"].astype(str)):
        j=rmap.get(v)
        if j is not None: rn[i,j]=1
    hyd_cols=["H_c"]
    if model in ("M2","M3"): hyd_cols.append("recent_c")
    if model=="M3": hyd_cols.append("sd_c")
    hyd=x[hyd_cols].to_numpy(float)
    X=np.column_stack([base,state,rn,hyd])
    return X,hyd_cols

def fit_hydrology_coefficients(cells,callers,all_species,models=("M1","M2","M3")):
    out={m:{} for m in models}
    audit={m:{} for m in models}

    for train_fold in ("A","B"):
        mask=(cells["route_fold"].to_numpy()==train_fold)
        train_cells=cells.loc[mask]
        state_levels=sorted(train_cells["State"].astype(str).unique())
        run_levels=sorted(train_cells["RunNumber"].astype(str).unique())
        routes=train_cells["route_cluster"].astype(str).to_numpy()
        caller_sub=[callers[i] for i in np.flatnonzero(mask)]
        for model in models:
            X,hyd_cols=design_matrix(cells,mask,model,state_levels,run_levels)
            rank=int(np.linalg.matrix_rank(X))
            if rank!=X.shape[1]:
                raise RuntimeError(f"rank-deficient hydrology design after fold-specific levels: {train_fold} {model} rank={rank} p={X.shape[1]}")
            hstart=X.shape[1]-len(hyd_cols)
            coefmap={}
            aud={}
            for sp in all_species:
                y=np.asarray([1.0 if sp in s else 0.0 for s in caller_sub],float)
                pos=int(y.sum())
                posroutes=int(len(set(routes[y>0])))
                info={"positive_cells":pos,"positive_routes":posroutes,"estimable":False,"method":"zero"}
                vals=np.zeros(3,float)
                if pos>=MIN_POSITIVE_CELLS and posroutes>=MIN_POSITIVE_ROUTES and np.any(y==0):
                    mod=sm.GLM(y,X,family=sm.families.Binomial())
                    method="glm"
                    try:
                        fit=mod.fit(maxiter=200,disp=0)
                        params=np.asarray(fit.params,float)
                        if not np.all(np.isfinite(params)):
                            raise RuntimeError("nonfinite")
                    except Exception:
                        method="ridge_fallback"
                        fit=mod.fit_regularized(alpha=0.01,L1_wt=0.0,maxiter=1000)
                        params=np.asarray(fit.params,float)
                    hv=np.asarray(params[hstart:],float)
                    if np.all(np.isfinite(hv)) and np.all(np.abs(hv)<=20):
                        vals[0]=hv[0]
                        if model in ("M2","M3"): vals[1]=hv[1]
                        if model=="M3": vals[2]=hv[2]
                        info.update({"estimable":True,"method":method})
                    else:
                        info["method"]="zero_after_unstable_fit"
                coefmap[sp]=vals
                info["beta_H"]=float(vals[0]); info["beta_recent"]=float(vals[1]); info["beta_sd"]=float(vals[2])
                aud[sp]=info
            out[model][train_fold]=coefmap
            audit[model][train_fold]={
              "training_cells":int(mask.sum()),"training_routes":int(cells.loc[mask,"route_cluster"].nunique()),
              "design_rank":int(rank),"design_columns":int(X.shape[1]),
              "species_estimable":int(sum(v["estimable"] for v in aud.values())),
              "species":aud
            }
    return out,audit

def simulate_model(model,pfinal,dsub,hsub,hydro,rain_slopes,hydro_coef,r,den):
    rng=np.random.default_rng(SEEDS[model])
    num=np.zeros((B,3),float)
    shifts=[]
    for i,(p,dct,ph,h) in enumerate(zip(pfinal.itertuples(index=False),dsub,hsub,hydro)):
        test_fold=joint.fold_for_route(str(p.route_cluster))
        train_fold="B" if test_fold=="A" else "A"
        rs=rain_slopes[train_fold]
        gamma=np.asarray([float(rs.get(sp,0.0)) for sp in dct["species"]],float)

        dry=dct["dry"].astype(float)
        p_anchor=(1-ANCHOR)*ph+ANCHOR*dry
        p_anchor=np.clip(p_anchor,1e-8,1-1e-8)
        eta=uniform.logit(p_anchor)+gamma[:,None]*float(p.rain_contrast)

        if model!="M0":
            cm=hydro_coef[model][train_fold]
            bet=np.asarray([cm.get(sp,np.zeros(3,float)) for sp in dct["species"]],float)
            dH=h["wet_H"]-h["dry_H"]
            dR=h["wet_recent"]-h["dry_recent"]
            dS=h["wet_sd"]-h["dry_sd"]
            hs=bet[:,0,None]*dH[None,:]
            if model in ("M2","M3"):
                hs=hs+bet[:,1,None]*dR[None,:]
            if model=="M3":
                hs=hs+bet[:,2,None]*dS[None,:]
            eta=eta+hs
            shifts.append(np.abs(hs).ravel())

        pre=uniform.expit(eta)
        q=uniform.solve_shift(pre,dct["wet_k"])
        w=rng.random((B,)+q.shape)<q[None,:,:]
        num+=r[i]*flex.sim_metrics(w,dct["dry"])

    sim=num/den
    shift=np.concatenate(shifts) if shifts else np.asarray([],float)
    return sim,{
      "mean_abs_hydrology_logit_shift":float(np.mean(shift)) if len(shift) else 0.0,
      "q95_abs_hydrology_logit_shift":float(np.quantile(shift,.95)) if len(shift) else 0.0
    }

def analyze_sample(label,pfinal,dfinal,hfinal,hydro,runs,sampled,ss,pools,models):
    all_species=sorted({sp for spp in pools.values() for sp in spp})

    rainA,auditA,foldA=joint.fit_species_slopes(runs,sampled,ss,all_species,"A")
    rainB,auditB,foldB=joint.fit_species_slopes(runs,sampled,ss,all_species,"B")
    rain_slopes={"A":rainA,"B":rainB}

    run_specs=build_run_specs(pfinal,dfinal,hydro,runs)
    cells,callers=cell_frame(run_specs,ss)
    hydro_models=tuple(m for m in models if m!="M0")
    hydro_coef,hydro_audit=fit_hydrology_coefficients(
        cells,callers,all_species,models=hydro_models
    ) if hydro_models else ({},{})

    obs_rows=np.asarray([flex.metrics(d["wet"],d["dry"]) for d in dfinal],float)
    r,den=uniform.design_residual(pfinal)
    obs=(r[:,None]*obs_rows).sum(axis=0)/den

    results={}
    shift_audit={}
    for model in models:
        sim,sa=simulate_model(model,pfinal,dfinal,hfinal,hydro,rain_slopes,hydro_coef,r,den)
        results[model]=flex.conditional(sim,obs)
        shift_audit[model]=sa

    res={m:float(results[m]["observed_conditional_residual"]) for m in results}
    out={
      "label":label,
      "coverage":{"pairs":int(len(pfinal)),"routes":int(pfinal.route_cluster.nunique()),"states":int(pfinal.State.nunique())},
      "observed":{"route_new_species_beta":float(obs[0]),"extra_stop_beta":float(obs[1]),"concentration_beta":float(obs[2])},
      "models":results,
      "rainfall_training":{"fold_A":foldA,"fold_B":foldB},
      "hydrology_training":hydro_audit,
      "hydrology_shift_audit":shift_audit
    }
    if "M0" in res and "M1" in res:
        base=res["M0"]
        out["fraction_removed_current"]=float((res["M0"]-res["M1"])/base) if base!=0 else None
        out["M1_sufficient"]=bool(not results["M1"]["above_upper_95"])
    if all(m in res for m in ("M0","M1","M2","M3")):
        base=res["M0"]
        out["residual_decomposition"]={
          "same_sample_M0_residual":base,
          "M1_residual":res["M1"],"M2_residual":res["M2"],"M3_residual":res["M3"],
          "fraction_removed_total":float((res["M0"]-res["M3"])/base) if base!=0 else None,
          "fraction_removed_current":float((res["M0"]-res["M1"])/base) if base!=0 else None,
          "increment_recent":float((res["M1"]-res["M2"])/base) if base!=0 else None,
          "increment_variability":float((res["M2"]-res["M3"])/base) if base!=0 else None
        }
        out["M3_sufficient"]=bool(not results["M3"]["above_upper_95"])
    return out

def main():
    if not VAR_CSV.exists():
        raise RuntimeError(f"missing hydrology input: {VAR_CSV}")

    var=pd.read_csv(VAR_CSV)
    raw,runs,psub,dsub,hsub,pools,sampled,ss=flex.prepare_subset()

    p1,d1,h1,hyd1,site,safe,fail1=build_complete_sample(
        raw,runs,psub,dsub,hsub,var,"M1"
    )
    p3,d3,h3,hyd3,site,safe,fail3=build_complete_sample(
        raw,runs,psub,dsub,hsub,var,"M3"
    )

    gate1=bool(
        len(p1)>=1500 and len(p1)>0 and
        p1.route_cluster.nunique()>=300 and p1.State.nunique()>=15
    )
    gate3=bool(
        len(p3)>=1500 and len(p3)>0 and
        p3.route_cluster.nunique()>=300 and p3.State.nunique()>=15
    )

    coverage={
      "strict_geometry_routes":int(len(safe)),
      "M1":{"pairs":int(len(p1)),"routes":int(p1.route_cluster.nunique()) if len(p1) else 0,
            "states":int(p1.State.nunique()) if len(p1) else 0,"failures":fail1,"gate_pass":gate1},
      "M3":{"pairs":int(len(p3)),"routes":int(p3.route_cluster.nunique()) if len(p3) else 0,
            "states":int(p3.State.nunique()) if len(p3) else 0,"failures":fail3,"gate_pass":gate3}
    }

    output={
      "analysis":"naamp_dynamic_hydrology_mechanism_v0_2",
      "contract":"revision/NAAMP_DYNAMIC_HYDROLOGY_MECHANISM_EXTENSION_V0_4.md",
      "model_spec":"revision/NAAMP_DYNAMIC_HYDROLOGY_MODEL_SPEC_V0_1.md",
      "coverage":coverage,
      "hydrology_sources":{
        "variability_csv_sha256":hashlib.sha256(VAR_CSV.read_bytes()).hexdigest(),
        "primary_M1_exposure":"within-SiteID wet-minus-dry current monthly water fraction"
      },
      "frog_endpoint_read":False
    }

    if not gate1:
        output["classification"]="current_hydrology_coverage_inconclusive"
        OUT.write_text(json.dumps(output,indent=2,sort_keys=True)+"\n")
        print(json.dumps(output,indent=2,sort_keys=True))
        return

    output["frog_endpoint_read"]=True

    if gate3:
        full=analyze_sample("M0-M3 common sample",p3,d3,h3,hyd3,runs,sampled,ss,pools,("M0","M1","M2","M3"))
        output["full_sequence"]=full
        if full["M3_sufficient"]:
            classification="dynamic_hydrology_sufficient"
        elif full["residual_decomposition"]["fraction_removed_total"] is not None and full["residual_decomposition"]["fraction_removed_total"]>0:
            classification="dynamic_hydrology_partial"
        else:
            classification="dynamic_hydrology_not_supported_as_principal_mechanism"
    else:
        current=analyze_sample("M0-M1 current-water sample",p1,d1,h1,hyd1,runs,sampled,ss,pools,("M0","M1"))
        output["current_only"]=current
        if current["M1_sufficient"]:
            classification="current_hydrology_sufficient_M3_inconclusive"
        elif current["fraction_removed_current"] is not None and current["fraction_removed_current"]>0:
            classification="current_hydrology_partial_M3_inconclusive"
        else:
            classification="current_hydrology_not_supported_M3_inconclusive"

    output["classification"]=classification
    output["interpretation_boundary"]={
      "reproductive_acoustic_activity":True,
      "reproductive_success_inferred":False,
      "unique_causal_mediation_proven":False,
      "outcome_is_observational":True
    }
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(output,indent=2,sort_keys=True)+"\n")
    summary={"analysis":output["analysis"],"coverage":coverage,"classification":classification}
    if "full_sequence" in output:
        summary["full_sequence"]={
          "observed":output["full_sequence"]["observed"],
          "models":output["full_sequence"]["models"],
          "residual_decomposition":output["full_sequence"]["residual_decomposition"]
        }
    if "current_only" in output:
        summary["current_only"]={
          "observed":output["current_only"]["observed"],
          "models":output["current_only"]["models"],
          "fraction_removed_current":output["current_only"]["fraction_removed_current"]
        }
    print(json.dumps(summary,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
