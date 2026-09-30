#!/usr/bin/env python3
from __future__ import annotations

import importlib.util, json, time, urllib.error
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

ROOT=Path(__file__).resolve().parents[1]
NAAMP=ROOT/"scripts"/"naamp"
OUT=ROOT/"exploration"/"NAAMP_RAIN_SELECTIVE_MEMORY_BOOTSTRAP_RECEIPT_V0_1.json"
Q=1.959963984540054
B=1000
SEED=2840223

def loadmod(name,path):
    s=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(s)
    assert s.loader
    s.loader.exec_module(m)
    return m

base=loadmod("base",NAAMP/"run_naamp_ecological_pulse.py")
spatial=loadmod("spatial",NAAMP/"run_naamp_spatial_taxonomic_activation_decomposition.py")
sameobs=loadmod("sameobs",NAAMP/"run_naamp_same_observer_robustness.py")

def load_retry():
    last=None
    for i in range(6):
        try:
            return base.load()
        except urllib.error.HTTPError as e:
            last=e
            if e.code not in (403,429,500,502,503,504):
                raise
            time.sleep(2*(i+1))
    raise RuntimeError(f"NAAMP source failed after retries: {last}")

def site_map(raw,eligible):
    v=defaultdict(set)
    for s in raw["Stops.csv"]:
        rid=(s.get("RunID") or "").strip()
        st=(s.get("StopNumber") or "").strip()
        sid=(s.get("SiteID") or "").strip()
        if rid in eligible and st and sid and (s.get("SkippedStop") or "").strip()=="0":
            v[(rid,st)].add(sid)
    bad={k:x for k,x in v.items() if len(x)>1}
    if bad:
        raise RuntimeError(f"site conflict {list(bad)[:5]}")
    return {k:next(iter(x)) for k,x in v.items()}

def ci_map(raw,eligible,sampled):
    v=defaultdict(list)
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
            v[(rid,st,sp)].append(x)
    by=defaultdict(dict)
    for (rid,st,sp),x in v.items():
        by[(rid,st)][sp]=max(x)
    return by

def stable(p,sampled,site):
    w=str(p.wet_RunID);d=str(p.dry_RunID)
    ws=set(sampled[w]);ds=set(sampled[d])
    return len(ws)==10 and ws==ds and all(
        site.get((w,st)) is not None and site.get((w,st))==site.get((d,st))
        for st in ws
    )

def build_meta(runs,sampled,site,ci):
    meta={};by=defaultdict(list);site_species=defaultdict(set);route_species=defaultdict(set)
    for r in runs.itertuples(index=False):
        rid=str(r.RunID)
        key=(str(r.State),str(r.RouteNumber),str(r.RunNumber))
        meta[rid]=(key,int(r.SurveyYear))
        by[key].append(rid)
        for st in sampled.get(rid,set()):
            sid=site.get((rid,st))
            if sid is None:
                continue
            for sp,val in ci.get((rid,st),{}).items():
                if val>0:
                    site_species[(rid,sid)].add(sp)
                    route_species[rid].add(sp)
    for k in by:
        by[k]=sorted(by[k],key=lambda rid:(meta[rid][1],rid))
    return meta,by,site_species,route_species

def direction_summary(p,target,reference,sampled,site,ci,meta,by,site_species,route_species):
    key,_=meta[target]
    cut=int(p.year_earlier)
    prior=[rid for rid in by[key] if meta[rid][1]<cut]
    if not prior:
        return None

    prior_route=set()
    prior_site=defaultdict(set)
    for rid in prior:
        prior_route.update(route_species.get(rid,set()))
        for st in sampled.get(rid,set()):
            sid=site.get((rid,st))
            if sid is not None:
                prior_site[sid].update(site_species.get((rid,sid),set()))

    reference_route=set()
    for st in sampled[reference]:
        reference_route.update(ci.get((reference,st),{}).keys())
    candidates=[sp for sp in prior_route if sp not in reference_route]
    if not candidates:
        return None

    n_same=n_other=0
    y3_same=y3_other=0
    y2_same=y2_other=0
    for st in sorted(sampled[target]):
        sid=site[(target,st)]
        tm=ci.get((target,st),{})
        mem=prior_site.get(sid,set())
        for sp in candidates:
            val=int(tm.get(sp,0))
            if sp in mem:
                n_same+=1
                y3_same+=int(val==3)
                y2_same+=int(val>=2)
            else:
                n_other+=1
                y3_other+=int(val==3)
                y2_other+=int(val>=2)

    if n_same<5 or n_other<5:
        return None

    w=n_same*n_other/(n_same+n_other)
    return {
        "ci3_rate_difference":float(y3_same/n_same-y3_other/n_other),
        "ci2plus_rate_difference":float(y2_same/n_same-y2_other/n_other),
        "opportunity_weight":float(w),
        "n_same":float(n_same),
        "n_route_only":float(n_other),
        "prior_runs":float(len(prior)),
    }

def fit_cluster(d,response,robust=True):
    form=f"{response} ~ rain_contrast + temp_difference + doy_difference + year_gap + C(State) + C(RunNumber)"
    if robust:
        m=smf.wls(form,data=d,weights=d.opportunity_weight).fit(
            cov_type="cluster",cov_kwds={"groups":d.route_cluster}
        )
    else:
        m=smf.wls(form,data=d,weights=d.opportunity_weight).fit()
    b=float(m.params["rain_contrast"])
    se=float(m.bse["rain_contrast"]) if robust else None
    out={"beta":b,"n_pairs":int(len(d)),"n_routes":int(d.route_cluster.nunique())}
    if robust:
        out.update({
            "se":se,
            "ci95":[b-Q*se,b+Q*se],
            "p":float(m.pvalues["rain_contrast"]),
            "positive_ci":bool(b>0 and b-Q*se>0)
        })
    return out

def design_matrix(d):
    x=d.copy()
    state=sorted(x.State.astype(str).unique())
    run=sorted(x.RunNumber.astype(str).unique())
    cols=[
        np.ones(len(x),float),
        x.rain_contrast.to_numpy(float),
        x.temp_difference.to_numpy(float),
        x.doy_difference.to_numpy(float),
        x.year_gap.to_numpy(float),
    ]
    names=["Intercept","rain_contrast","temp_difference","doy_difference","year_gap"]
    for level in state[1:]:
        cols.append((x.State.astype(str)==level).to_numpy(float))
        names.append("State:"+level)
    for level in run[1:]:
        cols.append((x.RunNumber.astype(str)==level).to_numpy(float))
        names.append("RunNumber:"+level)
    return np.column_stack(cols),names

def matrix_wls_beta(d,response,route_levels,multiplicity=None):
    X,names=design_matrix(d)
    y=d[response].to_numpy(float)
    w=d.opportunity_weight.to_numpy(float).copy()
    if multiplicity is not None:
        rindex={r:i for i,r in enumerate(route_levels)}
        mult=np.asarray([multiplicity[rindex[str(r)]] for r in d.route_cluster.astype(str)],float)
        w*=mult
    ok=np.isfinite(y)&np.all(np.isfinite(X),axis=1)&np.isfinite(w)&(w>0)
    if int(ok.sum())<X.shape[1]+2:
        raise RuntimeError("insufficient weighted rows")
    sw=np.sqrt(w[ok])
    beta=np.linalg.lstsq(X[ok]*sw[:,None],y[ok]*sw,rcond=None)[0]
    return float(beta[names.index("rain_contrast")])

def bootstrap_diff(wet,dry,response):
    rng=np.random.default_rng(SEED + (0 if response=="ci3_rate_difference" else 10000))
    routes=sorted(set(wet.route_cluster.astype(str))|set(dry.route_cluster.astype(str)))
    # Exact implementation audit: matrix WLS must reproduce the formula WLS rain slope.
    wet_formula=fit_cluster(wet,response,robust=False)["beta"]
    dry_formula=fit_cluster(dry,response,robust=False)["beta"]
    ones=np.ones(len(routes),dtype=int)
    wet_matrix=matrix_wls_beta(wet,response,routes,ones)
    dry_matrix=matrix_wls_beta(dry,response,routes,ones)
    if abs(wet_formula-wet_matrix)>1e-9 or abs(dry_formula-dry_matrix)>1e-9:
        raise RuntimeError(
            f"matrix WLS reproduction failed {response}: "
            f"wet {wet_formula} vs {wet_matrix}; dry {dry_formula} vs {dry_matrix}"
        )

    vals=[]
    failed=0
    for _ in range(B):
        draw=rng.integers(0,len(routes),size=len(routes))
        mult=np.bincount(draw,minlength=len(routes))
        try:
            bw=matrix_wls_beta(wet,response,routes,mult)
            bd=matrix_wls_beta(dry,response,routes,mult)
            if np.isfinite(bw) and np.isfinite(bd):
                vals.append(float(bw-bd))
            else:
                failed+=1
        except Exception:
            failed+=1
    a=np.asarray(vals,float)
    if len(a)<900:
        raise RuntimeError(f"bootstrap too many failures: valid={len(a)} failed={failed}")
    lo,hi=np.quantile(a,[.025,.975])
    return {
        "implementation":"cluster multiplicity matrix-WLS; algebraically equivalent to duplicated-cluster WLS",
        "matrix_formula_reproduction":{
            "wet_abs_error":float(abs(wet_formula-wet_matrix)),
            "dry_abs_error":float(abs(dry_formula-dry_matrix)),
        },
        "replicates_requested":B,
        "replicates_valid":int(len(a)),
        "replicates_failed":int(failed),
        "mean_difference":float(a.mean()),
        "median_difference":float(np.median(a)),
        "percentile_ci95":[float(lo),float(hi)],
        "fraction_le_zero":float((1+np.sum(a<=0))/(len(a)+1)),
        "support":bool(lo>0),
    }

def main():
    raw=load_retry()
    runs,sets=base.build_runs(raw)
    eligible=set(runs.RunID.astype(str))
    sampled,_=spatial.stop_matrix(raw,eligible)
    site=site_map(raw,eligible)
    ci=ci_map(raw,eligible,sampled)

    pairs_all=base.pair_runs(runs,sets).copy().reset_index(drop=True)
    pairs=pairs_all.loc[np.asarray([stable(p,sampled,site) for p in pairs_all.itertuples(index=False)],bool)].copy().reset_index(drop=True)
    meta,by,site_species,route_species=build_meta(runs,sampled,site,ci)

    _,same=sameobs.same_observer_pairs(raw,runs,sets)
    same_keys={(str(p.wet_RunID),str(p.dry_RunID)) for p in same.itertuples(index=False)}

    wet_rows=[];dry_rows=[]
    for p in pairs.itertuples(index=False):
        w=str(p.wet_RunID);d=str(p.dry_RunID)
        fw=direction_summary(p,w,d,sampled,site,ci,meta,by,site_species,route_species)
        rv=direction_summary(p,d,w,sampled,site,ci,meta,by,site_species,route_species)
        base_row=p._asdict()
        base_row["same_observer"]=(w,d) in same_keys
        if fw is not None:
            row=dict(base_row);row.update(fw);wet_rows.append(row)
        if rv is not None:
            row=dict(base_row);row.update(rv);dry_rows.append(row)

    wet=pd.DataFrame(wet_rows);dry=pd.DataFrame(dry_rows)
    gate=bool(
        len(wet)>=750 and wet.route_cluster.nunique()>=200
        and len(dry)>=750 and dry.route_cluster.nunique()>=200
    )
    out={
        "analysis":"naamp_rain_selective_memory_bootstrap_v0_1",
        "contract":"exploration/NAAMP_RAIN_SELECTIVE_MEMORY_BOOTSTRAP_CONTRACT_V0_1.json",
        "coverage":{
            "all_pairs":int(len(pairs_all)),
            "physically_stable_pairs":int(len(pairs)),
            "wet_target_pairs":int(len(wet)),
            "wet_target_routes":int(wet.route_cluster.nunique()) if len(wet) else 0,
            "dry_target_pairs":int(len(dry)),
            "dry_target_routes":int(dry.route_cluster.nunique()) if len(dry) else 0,
            "gate_pass":gate
        },
        "response_endpoints_read":False
    }
    if not gate:
        OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
        print(json.dumps(out,indent=2,sort_keys=True))
        return

    fw3=fit_cluster(wet,"ci3_rate_difference",True)
    rv3=fit_cluster(dry,"ci3_rate_difference",True)
    fw2=fit_cluster(wet,"ci2plus_rate_difference",True)
    rv2=fit_cluster(dry,"ci2plus_rate_difference",True)
    obs3=float(fw3["beta"]-rv3["beta"])
    obs2=float(fw2["beta"]-rv2["beta"])
    boot3=bootstrap_diff(wet,dry,"ci3_rate_difference")
    boot2=bootstrap_diff(wet,dry,"ci2plus_rate_difference")

    sw=wet[wet.same_observer].copy();sd=dry[dry.same_observer].copy()
    same_gate=bool(
        len(sw)>=500 and sw.route_cluster.nunique()>=150
        and len(sd)>=500 and sd.route_cluster.nunique()>=150
    )
    same_desc=None
    if same_gate:
        same_desc={
            "wet_ci3":fit_cluster(sw,"ci3_rate_difference",True),
            "dry_ci3":fit_cluster(sd,"ci3_rate_difference",True),
        }
        same_desc["observed_beta_difference"]=float(
            same_desc["wet_ci3"]["beta"]-same_desc["dry_ci3"]["beta"]
        )

    out.update({
        "response_endpoints_read":True,
        "ci3":{
            "wet_target":fw3,
            "dry_target":rv3,
            "observed_beta_difference_wet_minus_dry":obs3,
            "cluster_bootstrap_difference":boot3
        },
        "ci2plus":{
            "wet_target":fw2,
            "dry_target":rv2,
            "observed_beta_difference_wet_minus_dry":obs2,
            "cluster_bootstrap_difference":boot2
        },
        "same_observer_descriptive":{"gate_pass":same_gate,"result":same_desc},
        "classification":{
            "rain_selective_memory_ci3_supported":bool(obs3>0 and boot3["support"]),
            "rain_selective_memory_ci2plus_supported":bool(obs2>0 and boot2["support"])
        },
        "interpretation_boundary":{
            "future_information_used":False,
            "generic_recurrence_compared_symmetrically":True,
            "continuous_occupancy_proven":False,
            "causal_rainfall_claim":False
        }
    })
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
