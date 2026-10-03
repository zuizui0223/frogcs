#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT=Path(__file__).resolve().parents[1]
EXP=ROOT/"exploration"
OUT=EXP/"NAAMP_SPECIES_ROUTE_NIGHT_RESIDUAL_BREADTH_RECEIPT_V0_1.json"

ANCHOR=0.75
EPS=1e-7
MIN_CLUSTERS=30
MIN_POSITIVE_CLUSTERS=10
MIN_CELLS=300

def loadmod(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    mod=importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(mod)
    return mod

depmod=loadmod("dep",EXP/"run_naamp_species_route_night_residual_dependence.py")
rain=depmod.rain
flex=depmod.flex
joint=depmod.joint
uniform=depmod.uniform

def species_num_den(y,q):
    e=np.asarray(y,float)-np.asarray(q,float)
    s=e.sum()
    ss=(e*e).sum()
    num=float((s*s-ss)/2.0)
    v=np.clip(np.asarray(q,float)*(1.0-np.asarray(q,float)),EPS,None)
    z=np.sqrt(v)
    zs=z.sum()
    zss=(z*z).sum()
    den=float((zs*zs-zss)/2.0)
    return num,den

def main():
    trigger=json.loads((EXP/"NAAMP_SPECIES_ROUTE_NIGHT_RESIDUAL_DEPENDENCE_RECEIPT_V0_1.json").read_text())
    if not trigger["residual_dependence"]["positive_dependence_supported"]:
        out={"analysis":"naamp_species_route_night_residual_breadth_v0_1","status":"not_run_trigger_not_met"}
        OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
        print(json.dumps(out,indent=2,sort_keys=True))
        return

    raw,runs,psub,dsub,hsub,pools,sampled,ss=flex.prepare_subset()
    mid=rain.build_midpoints(raw,runs)
    weather,weather_sha=rain.antecedent_amounts(mid)

    mask=np.asarray([
        str(p.wet_RunID) in weather and str(p.dry_RunID) in weather
        for p in psub.itertuples(index=False)
    ],bool)
    idx=np.flatnonzero(mask)
    pw=psub.iloc[idx].copy().reset_index(drop=True)
    dw=[dsub[int(i)] for i in idx]
    hw=[hsub[int(i)] for i in idx]
    if len(pw)!=2835:
        raise RuntimeError(f"weather subset drift {len(pw)} != 2835")

    runs_weather=runs[runs["RunID"].astype(str).isin(weather)].copy().reset_index(drop=True)
    runs_weather["rain72_mm"]=[weather[str(r)]["rain72_mm"] for r in runs_weather["RunID"].astype(str)]
    runs_weather["rain72_log"]=np.log1p(runs_weather["rain72_mm"].astype(float))

    all_species=sorted({sp for spp in pools.values() for sp in spp})
    pred_A,audit_A,fold_A=rain.fit_predict_amount_environment(runs_weather,sampled,ss,all_species,"A")
    pred_B,audit_B,fold_B=rain.fit_predict_amount_environment(runs_weather,sampled,ss,all_species,"B")
    pred_by_train={"A":pred_A,"B":pred_B}

    num=defaultdict(float)
    den=defaultdict(float)
    clusters=defaultdict(int)
    pos_clusters=defaultdict(int)
    cells=defaultdict(int)

    for p,dct,p_hist in zip(pw.itertuples(index=False),dw,hw):
        test_fold=joint.fold_for_route(str(p.route_cluster))
        train_fold="B" if test_fold=="A" else "A"
        pred=pred_by_train[train_fold]
        wet_id=str(p.wet_RunID)
        dry_id=str(p.dry_RunID)
        delta=np.asarray([
            pred[wet_id].get(sp,0.0)-pred[dry_id].get(sp,0.0)
            for sp in dct["species"]
        ],float)

        dry=dct["dry"].astype(float)
        p_anchor=(1.0-ANCHOR)*p_hist+ANCHOR*dry
        p_anchor=np.clip(p_anchor,EPS,1-EPS)
        pre=uniform.expit(uniform.logit(p_anchor)+delta[:,None])
        q=uniform.solve_shift(pre,dct["wet_k"])
        q=np.clip(q,EPS,1-EPS)
        y=dct["wet"].astype(float)

        for i,sp in enumerate(dct["species"]):
            n,d=species_num_den(y[i],q[i])
            num[sp]+=n
            den[sp]+=d
            clusters[sp]+=1
            pos_clusters[sp]+=int(y[i].sum()>0)
            cells[sp]+=int(y.shape[1])

    global_num=float(sum(num.values()))
    global_den=float(sum(den.values()))
    global_rho=global_num/global_den
    expected=float(trigger["residual_dependence"]["rho_resid"])
    if abs(global_rho-expected)>1e-10:
        raise RuntimeError(f"global rho reproduction drift {global_rho} vs {expected}")

    records={}
    eligible=[]
    for sp in sorted(num):
        d=float(den[sp])
        rho=float(num[sp]/d) if d>0 else None
        ok=bool(
            clusters[sp]>=MIN_CLUSTERS and
            pos_clusters[sp]>=MIN_POSITIVE_CLUSTERS and
            cells[sp]>=MIN_CELLS and
            rho is not None
        )
        loo_den=global_den-d
        loo_rho=float((global_num-num[sp])/loo_den) if loo_den>0 else None
        rec={
            "clusters":int(clusters[sp]),
            "observed_positive_clusters":int(pos_clusters[sp]),
            "stop_cells":int(cells[sp]),
            "numerator":float(num[sp]),
            "denominator":d,
            "rho_resid":rho,
            "eligible":ok,
            "leave_one_species_out_global_rho":loo_rho
        }
        records[sp]=rec
        if ok:
            eligible.append(rec)

    rho_vals=np.asarray([r["rho_resid"] for r in eligible],float)
    positive_num={sp:float(v) for sp,v in num.items() if v>0}
    total_pos=float(sum(positive_num.values()))
    shares=np.asarray([v/total_pos for v in positive_num.values()],float) if total_pos>0 else np.asarray([],float)
    sorted_shares=np.sort(shares)[::-1] if len(shares) else shares
    loo_vals=np.asarray([
        r["leave_one_species_out_global_rho"]
        for r in records.values()
        if r["leave_one_species_out_global_rho"] is not None
    ],float)

    frac_pos=float(np.mean(rho_vals>0)) if len(rho_vals) else None
    top1=float(sorted_shares[0]) if len(sorted_shares) else None
    top5=float(sorted_shares[:5].sum()) if len(sorted_shares) else None
    hhi=float(np.sum(shares*shares)) if len(shares) else None
    broad=bool(
        len(rho_vals)>0 and frac_pos>0.5 and
        top1 is not None and top1<0.25 and
        len(loo_vals)>0 and float(np.min(loo_vals))>0
    )

    out={
        "analysis":"naamp_species_route_night_residual_breadth_v0_1",
        "contract":"exploration/NAAMP_SPECIES_ROUTE_NIGHT_RESIDUAL_BREADTH_CONTRACT_V0_1.json",
        "status":"posthoc_breadth_audit_triggered",
        "coverage":{
            "pairs":int(len(pw)),
            "routes":int(pw.route_cluster.nunique()),
            "species_total":int(len(records)),
            "species_eligible":int(len(eligible))
        },
        "reproduction":{
            "global_rho_resid":global_rho,
            "trigger_global_rho_resid":expected
        },
        "breadth":{
            "eligible_positive_rho_count":int(np.sum(rho_vals>0)) if len(rho_vals) else 0,
            "eligible_positive_rho_fraction":frac_pos,
            "eligible_rho_median":float(np.median(rho_vals)) if len(rho_vals) else None,
            "eligible_rho_iqr":[float(np.quantile(rho_vals,.25)),float(np.quantile(rho_vals,.75))] if len(rho_vals) else None,
            "top1_positive_numerator_share":top1,
            "top5_positive_numerator_share":top5,
            "positive_numerator_hhi":hhi,
            "leave_one_species_out_global_rho_min":float(np.min(loo_vals)) if len(loo_vals) else None,
            "leave_one_species_out_global_rho_max":float(np.max(loo_vals)) if len(loo_vals) else None,
            "broad_by_frozen_rule":broad
        },
        "eligibility_thresholds":{
            "minimum_species_route_night_clusters":MIN_CLUSTERS,
            "minimum_observed_positive_clusters":MIN_POSITIVE_CLUSTERS,
            "minimum_stop_cells":MIN_CELLS
        },
        "species_records":records,
        "weather_provenance":{
            "era5_antecedent_amount_sha256":weather_sha
        },
        "interpretation_boundary":{
            "shared_mechanism_across_all_species":False,
            "independent_confirmation":False
        }
    }
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
