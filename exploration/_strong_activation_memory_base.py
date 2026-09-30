#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import time
import urllib.error
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

ROOT=Path(__file__).resolve().parents[1]
NAAMP=ROOT/"scripts"/"naamp"
OUT=ROOT/"exploration"/"NAAMP_STRONG_ACTIVATION_MEMORY_RECEIPT_V0_1.json"
Q=1.959963984540054

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
    vals=defaultdict(set)
    for s in raw["Stops.csv"]:
        rid=(s.get("RunID") or "").strip()
        st=(s.get("StopNumber") or "").strip()
        sid=(s.get("SiteID") or "").strip()
        if rid in eligible and st and sid and (s.get("SkippedStop") or "").strip()=="0":
            vals[(rid,st)].add(sid)
    bad={k:v for k,v in vals.items() if len(v)>1}
    if bad:
        raise RuntimeError(f"multiple SiteIDs: {list(bad)[:10]}")
    return {k:next(iter(v)) for k,v in vals.items()}

def ci_map(raw,eligible,sampled):
    vals=defaultdict(list)
    for r in raw["Counts.csv"]:
        rid=(r.get("RunID") or "").strip()
        st=(r.get("StopNumber") or "").strip()
        sp=(r.get("Species") or "").strip()
        if rid not in eligible or st not in sampled.get(rid,set()) or not sp:
            continue
        try:
            ci=int(float((r.get("CallingIndex") or "").strip()))
        except Exception:
            continue
        if ci in (1,2,3):
            vals[(rid,st,sp)].append(ci)
    by=defaultdict(dict)
    for (rid,st,sp),v in vals.items():
        by[(rid,st)][sp]=max(v)
    return by

def stable(p,sampled,site):
    w=str(p.wet_RunID); d=str(p.dry_RunID)
    ws=set(sampled[w]); ds=set(sampled[d])
    return len(ws)==10 and ws==ds and all(
        site.get((w,st)) is not None and site.get((w,st))==site.get((d,st))
        for st in ws
    )

def build_history(runs,sampled,site,ci):
    meta={}
    by_stratum=defaultdict(list)
    for r in runs.itertuples(index=False):
        rid=str(r.RunID)
        key=(str(r.State),str(r.RouteNumber),str(r.RunNumber))
        meta[rid]={"key":key,"year":int(r.SurveyYear)}
        by_stratum[key].append(rid)
    for key in by_stratum:
        by_stratum[key]=sorted(by_stratum[key],key=lambda rid:(meta[rid]["year"],rid))
    return meta,by_stratum

def prior_memory_for_pair(p,sampled,site,ci,meta,by_stratum):
    w=str(p.wet_RunID); d=str(p.dry_RunID)
    key=meta[w]["key"]
    cutoff=int(p.year_earlier)
    prior=[rid for rid in by_stratum[key] if meta[rid]["year"]<cutoff]
    if not prior:
        return None

    site_any=defaultdict(set)
    site_strong=defaultdict(set)
    route_any=set()

    for rid in prior:
        for st in sampled.get(rid,set()):
            sid=site.get((rid,st))
            if sid is None:
                continue
            for sp,x in ci.get((rid,st),{}).items():
                if x>0:
                    site_any[sid].add(sp)
                    route_any.add(sp)
                if x>=2:
                    site_strong[sid].add(sp)

    cats=["same_site_prior_strong","same_site_prior_weak_only","route_only_prior","no_prior_stratum_record"]
    score={k:0.0 for k in cats}
    count={k:0.0 for k in cats}
    ci3={k:0.0 for k in cats}
    total_score=total_count=total_ci3=0.0

    for st in sorted(sampled[w]):
        sid=site.get((w,st))
        if sid is None:
            raise RuntimeError("missing stable SiteID")
        wm=ci.get((w,st),{})
        dm=ci.get((d,st),{})
        for sp in set(wm)|set(dm):
            wet=int(wm.get(sp,0))
            dry=int(dm.get(sp,0))
            if dry!=0 or wet<2:
                continue
            total_score+=wet
            total_count+=1
            if wet==3:
                total_ci3+=1

            if sp in site_strong.get(sid,set()):
                cat="same_site_prior_strong"
            elif sp in site_any.get(sid,set()):
                cat="same_site_prior_weak_only"
            elif sp in route_any:
                cat="route_only_prior"
            else:
                cat="no_prior_stratum_record"

            score[cat]+=wet
            count[cat]+=1
            if wet==3:
                ci3[cat]+=1

    if abs(total_score-sum(score.values()))>1e-12:
        raise RuntimeError("strong score memory identity failed")
    if abs(total_count-sum(count.values()))>1e-12:
        raise RuntimeError("strong count memory identity failed")
    if abs(total_ci3-sum(ci3.values()))>1e-12:
        raise RuntimeError("CI3 memory identity failed")

    out={
        "strong_new_score":total_score,
        "strong_new_count":total_count,
        "new_ci3_count":total_ci3,
        "memory_runs":float(len(prior)),
    }
    for cat in cats:
        out["score_"+cat]=score[cat]
        out["count_"+cat]=count[cat]
        out["ci3_"+cat]=ci3[cat]

    out["score_recurrent_sum"]=total_score-score["no_prior_stratum_record"]
    out["count_recurrent_sum"]=total_count-count["no_prior_stratum_record"]
    out["ci3_recurrent_sum"]=total_ci3-ci3["no_prior_stratum_record"]
    out["score_same_site_any"]=score["same_site_prior_strong"]+score["same_site_prior_weak_only"]
    out["ci3_same_site_any"]=ci3["same_site_prior_strong"]+ci3["same_site_prior_weak_only"]
    return out

def fit(d,response):
    form=f"{response} ~ rain_contrast + temp_difference + doy_difference + year_gap + C(State) + C(RunNumber)"
    m=smf.ols(form,data=d).fit(cov_type="cluster",cov_kwds={"groups":d.route_cluster})
    b=float(m.params["rain_contrast"])
    se=float(m.bse["rain_contrast"])
    return {
        "beta":b,"se":se,
        "ci95":[b-Q*se,b+Q*se],
        "p":float(m.pvalues["rain_contrast"]),
        "n_pairs":int(len(d)),
        "n_routes":int(d.route_cluster.nunique())
    }

def package(d):
    score_names=[
        "strong_new_score",
        "score_same_site_prior_strong",
        "score_same_site_prior_weak_only",
        "score_route_only_prior",
        "score_no_prior_stratum_record",
        "score_recurrent_sum",
        "score_same_site_any",
    ]
    count_names=[
        "strong_new_count",
        "count_same_site_prior_strong",
        "count_same_site_prior_weak_only",
        "count_route_only_prior",
        "count_no_prior_stratum_record",
        "count_recurrent_sum",
    ]
    ci3_names=[
        "new_ci3_count",
        "ci3_same_site_prior_strong",
        "ci3_same_site_prior_weak_only",
        "ci3_route_only_prior",
        "ci3_no_prior_stratum_record",
        "ci3_recurrent_sum",
        "ci3_same_site_any",
    ]
    models={x:fit(d,x) for x in score_names+count_names+ci3_names}
    total=models["strong_new_score"]["beta"]
    recurrent=models["score_recurrent_sum"]["beta"]
    share=float(recurrent/total) if abs(total)>1e-12 else None
    same_site_any=float(models["score_same_site_any"]["beta"]/total) if abs(total)>1e-12 else None
    same_site_strong=float(models["score_same_site_prior_strong"]["beta"]/total) if abs(total)>1e-12 else None

    ci3_total=models["new_ci3_count"]["beta"]
    ci3_recur=models["ci3_recurrent_sum"]["beta"]
    ci3_share=float(ci3_recur/ci3_total) if abs(ci3_total)>1e-12 else None

    score_err=float(
        total
        -models["score_same_site_prior_strong"]["beta"]
        -models["score_same_site_prior_weak_only"]["beta"]
        -models["score_route_only_prior"]["beta"]
        -models["score_no_prior_stratum_record"]["beta"]
    )
    support=bool(
        recurrent>0
        and models["score_recurrent_sum"]["ci95"][0]>0
        and share is not None
        and share>0.5
    )
    return {
        "models":models,
        "recurrent_share_of_strong_new_score_beta":share,
        "same_site_any_share_of_strong_new_score_beta":same_site_any,
        "same_site_prior_strong_share_of_strong_new_score_beta":same_site_strong,
        "recurrent_share_of_new_ci3_count_beta":ci3_share,
        "beta_identity_error_score":score_err,
        "classification":{"prior_memory_strong_activation_supported":support},
        "descriptive":{
            "mean_memory_runs":float(d.memory_runs.mean()),
            "median_memory_runs":float(d.memory_runs.median()),
        }
    }

def main():
    raw=load_retry()
    runs,sets=base.build_runs(raw)
    eligible=set(runs.RunID.astype(str))
    sampled,_=spatial.stop_matrix(raw,eligible)
    site=site_map(raw,eligible)
    ci=ci_map(raw,eligible,sampled)
    meta,by_stratum=build_history(runs,sampled,site,ci)

    allpairs=base.pair_runs(runs,sets).copy().reset_index(drop=True)
    stable_mask=np.asarray([stable(p,sampled,site) for p in allpairs.itertuples(index=False)],bool)
    stable_pairs=allpairs.loc[stable_mask].copy().reset_index(drop=True)

    _,same=sameobs.same_observer_pairs(raw,runs,sets)
    same_key={(str(p.wet_RunID),str(p.dry_RunID)) for p in same.itertuples(index=False)}

    rows=[]
    for p in stable_pairs.itertuples(index=False):
        m=prior_memory_for_pair(p,sampled,site,ci,meta,by_stratum)
        if m is None:
            continue
        r=p._asdict()
        r.update(m)
        r["same_observer"]=(str(p.wet_RunID),str(p.dry_RunID)) in same_key
        rows.append(r)
    d=pd.DataFrame(rows)

    gate=bool(len(d)>=1500 and d.route_cluster.nunique()>=300)
    if not gate:
        out={
            "analysis":"naamp_strong_activation_memory_v0_1",
            "contract":"exploration/NAAMP_STRONG_ACTIVATION_MEMORY_CONTRACT_V0_1.json",
            "status":"not_run_due_to_prefixed_gate",
            "coverage":{"pairs":int(len(d)),"routes":int(d.route_cluster.nunique()) if len(d) else 0}
        }
        OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
        print(json.dumps(out,indent=2,sort_keys=True))
        return

    primary=package(d)
    dsame=d[d.same_observer].copy()
    same_pkg=package(dsame) if len(dsame)>=1000 and dsame.route_cluster.nunique()>=250 else {
        "status":"not_run_due_to_sensitivity_gate",
        "n_pairs":int(len(dsame)),
        "n_routes":int(dsame.route_cluster.nunique())
    }

    out={
        "analysis":"naamp_strong_activation_memory_v0_1",
        "contract":"exploration/NAAMP_STRONG_ACTIVATION_MEMORY_CONTRACT_V0_1.json",
        "status":"completed",
        "coverage":{
            "all_pairs":int(len(allpairs)),
            "physically_stable_pairs":int(len(stable_pairs)),
            "prior_history_pairs":int(len(d)),
            "prior_history_routes":int(d.route_cluster.nunique()),
            "same_observer_prior_history_pairs":int(len(dsame)),
            "same_observer_prior_history_routes":int(dsame.route_cluster.nunique()),
        },
        "primary_prior_only":primary,
        "same_observer_sensitivity":same_pkg,
        "interpretation_boundary":{
            "continuous_occupancy_proven":False,
            "literal_colonization_excluded":False,
            "prior_local_acoustic_memory_supported":bool(primary["classification"]["prior_memory_strong_activation_supported"]),
            "causal_rainfall_claim":False
        }
    }
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
