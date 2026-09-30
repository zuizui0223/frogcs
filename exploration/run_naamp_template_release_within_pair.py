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
OUT=ROOT/"exploration"/"NAAMP_TEMPLATE_RELEASE_WITHIN_PAIR_RECEIPT_V0_1.json"
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
            x=int(float((r.get("CallingIndex") or "").strip()))
        except Exception:
            continue
        if x in (1,2,3):
            vals[(rid,st,sp)].append(x)
    by=defaultdict(dict)
    for (rid,st,sp),v in vals.items():
        by[(rid,st)][sp]=max(v)
    return by

def stable_pair(p,sampled,site):
    w=str(p.wet_RunID); d=str(p.dry_RunID)
    ws=set(sampled[w]); ds=set(sampled[d])
    return len(ws)==10 and ws==ds and all(
        site.get((w,st)) is not None and site.get((w,st))==site.get((d,st))
        for st in ws
    )

def history_index(runs):
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

def pair_rows(pair_id,p,sampled,site,ci,meta,by_stratum,same_observer):
    w=str(p.wet_RunID); d=str(p.dry_RunID)
    key=meta[w]["key"]; cutoff=int(p.year_earlier)
    prior=[rid for rid in by_stratum[key] if meta[rid]["year"]<cutoff]
    if not prior:
        return []

    current_stops=sorted(sampled[w],key=lambda x:float(x))
    current_sids=[site[(w,st)] for st in current_stops]

    site_opp=defaultdict(int)
    site_any=defaultdict(set)
    site_strong=defaultdict(set)
    route_runs_with_species=defaultdict(int)
    route_prior_species=set()

    for rid in prior:
        seen_route=set()
        seen_sid=set()
        for st in sampled.get(rid,set()):
            sid=site.get((rid,st))
            if sid is None:
                continue
            if sid in current_sids and sid not in seen_sid:
                site_opp[sid]+=1
                seen_sid.add(sid)
            for sp,x in ci.get((rid,st),{}).items():
                if int(x)>0:
                    route_prior_species.add(sp)
                    seen_route.add(sp)
                    if sid in current_sids:
                        site_any[sid].add(sp)
                if int(x)>=2 and sid in current_sids:
                    site_strong[sid].add(sp)
        for sp in seen_route:
            route_runs_with_species[sp]+=1

    opportunity=[sid for sid in current_sids if site_opp.get(sid,0)>0]
    if len(opportunity)<8:
        return []

    wet_species=set()
    dry_species=set()
    wet_by=defaultdict(dict)
    dry_by=defaultdict(dict)
    for st in current_stops:
        for sp,x in ci.get((w,st),{}).items():
            if int(x)>0:
                wet_species.add(sp); wet_by[sp][st]=int(x)
        for sp,x in ci.get((d,st),{}).items():
            if int(x)>0:
                dry_species.add(sp); dry_by[sp][st]=int(x)

    discordant=sorted((wet_species ^ dry_species) & route_prior_species)
    rows=[]
    for sp in discordant:
        wet_active=int(sp in wet_species)
        occ=wet_by[sp] if wet_active else dry_by[sp]
        active_k=len(occ)
        if active_k<1:
            continue
        prior_any=sum(sp in site_any.get(sid,set()) for sid in opportunity)/len(opportunity)
        prior_strong=sum(sp in site_strong.get(sid,set()) for sid in opportunity)/len(opportunity)
        prior_freq=route_runs_with_species.get(sp,0)/len(prior)
        strong_k=sum(int(x)>=2 for x in occ.values())
        rows.append({
            "pair_id":int(pair_id),
            "species":sp,
            "route_cluster":str(p.route_cluster),
            "State":str(p.State),
            "RunNumber":str(p.RunNumber),
            "same_observer":bool(same_observer),
            "year_gap":float(p.year_gap),
            "rain_contrast":float(p.rain_contrast),
            "wet_active":float(wet_active),
            "prior_strong_breadth":float(prior_strong),
            "prior_any_breadth":float(prior_any),
            "prior_route_frequency":float(prior_freq),
            "active_k":float(active_k),
            "spatial_depth":float(active_k-1),
            "third_plus_depth":float(max(active_k-2,0)),
            "active_strong_k":float(strong_k),
        })
    return rows

def prepare_sample(df):
    d=df.copy()
    if d.empty:
        return d
    informative=d.groupby("pair_id").wet_active.nunique()
    good=informative[informative>=2].index
    return d[d.pair_id.isin(good)].copy().reset_index(drop=True)

def gate_report(d,kind="primary"):
    if d.empty:
        return {"pass":False,"n_pair_species":0,"n_pairs":0,"n_routes":0,"n_species":0,"breadth_sd":0.0}
    sd=float(d.prior_strong_breadth.std(ddof=0))
    if kind=="primary":
        ok=(
            len(d)>=1500 and d.pair_id.nunique()>=500 and d.route_cluster.nunique()>=300
            and d.species.nunique()>=20 and sd>=0.10
        )
    else:
        ok=(
            len(d)>=1000 and d.pair_id.nunique()>=350 and d.route_cluster.nunique()>=225
            and d.species.nunique()>=20 and sd>=0.10
        )
    return {
        "pass":bool(ok),
        "n_pair_species":int(len(d)),
        "n_pairs":int(d.pair_id.nunique()),
        "n_routes":int(d.route_cluster.nunique()),
        "n_species":int(d.species.nunique()),
        "breadth_sd":sd,
    }

def fit_primary(df,response,predictor):
    d=prepare_sample(df)
    if d.empty:
        return None
    x=d[predictor].to_numpy(float)
    sd=float(np.std(x,ddof=0))
    if not sd>0:
        return None
    d["z_breadth"]=(x-float(np.mean(x)))/sd
    d["wet_breadth"]=d.wet_active*d.z_breadth
    form=(
        f"{response} ~ wet_active + z_breadth + wet_breadth + prior_route_frequency + "
        "C(pair_id) + C(species)"
    )
    m=smf.ols(form,data=d).fit(
        cov_type="cluster",cov_kwds={"groups":d.route_cluster}
    )
    b=float(m.params["wet_breadth"]); se=float(m.bse["wet_breadth"])
    return {
        "response":response,
        "predictor":predictor,
        "n_pair_species":int(len(d)),
        "n_pairs":int(d.pair_id.nunique()),
        "n_routes":int(d.route_cluster.nunique()),
        "n_species":int(d.species.nunique()),
        "breadth_mean":float(np.mean(x)),
        "breadth_sd":sd,
        "wet_x_breadth_beta":b,
        "wet_x_breadth_se":se,
        "wet_x_breadth_ci95":[b-Q*se,b+Q*se],
        "wet_x_breadth_p":float(m.pvalues["wet_breadth"]),
        "positive_ci":bool(b>0 and b-Q*se>0),
        "wet_active_beta":float(m.params["wet_active"]),
    }

def fit_magnitude(df):
    d=prepare_sample(df)
    if d.empty:
        return None
    x=d.prior_strong_breadth.to_numpy(float)
    sd=float(np.std(x,ddof=0))
    if not sd>0:
        return None
    d["z_breadth"]=(x-float(np.mean(x)))/sd
    d["c_rain"]=d.rain_contrast-float(d.rain_contrast.mean())
    d["wet_breadth"]=d.wet_active*d.z_breadth
    d["wet_rain"]=d.wet_active*d.c_rain
    d["breadth_rain"]=d.z_breadth*d.c_rain
    d["wet_breadth_rain"]=d.wet_active*d.z_breadth*d.c_rain
    form=(
        "third_plus_depth ~ wet_active + z_breadth + wet_breadth + "
        "wet_rain + breadth_rain + wet_breadth_rain + prior_route_frequency + "
        "C(pair_id) + C(species)"
    )
    m=smf.ols(form,data=d).fit(
        cov_type="cluster",cov_kwds={"groups":d.route_cluster}
    )
    b=float(m.params["wet_breadth_rain"]); se=float(m.bse["wet_breadth_rain"])
    return {
        "n_pair_species":int(len(d)),
        "three_way_beta":b,
        "three_way_se":se,
        "three_way_ci95":[b-Q*se,b+Q*se],
        "three_way_p":float(m.pvalues["wet_breadth_rain"]),
        "wet_x_breadth_beta":float(m.params["wet_breadth"]),
        "wet_x_rain_beta":float(m.params["wet_rain"]),
    }

def main():
    raw=load_retry()
    runs,sets=base.build_runs(raw)
    eligible=set(runs.RunID.astype(str))
    sampled,_=spatial.stop_matrix(raw,eligible)
    site=site_map(raw,eligible)
    ci=ci_map(raw,eligible,sampled)
    meta,by_stratum=history_index(runs)

    allpairs=base.pair_runs(runs,sets).copy().reset_index(drop=True)
    stable=allpairs.loc[
        np.asarray([stable_pair(p,sampled,site) for p in allpairs.itertuples(index=False)],bool)
    ].copy().reset_index(drop=True)
    _,same=sameobs.same_observer_pairs(raw,runs,sets)
    same_keys={(str(p.wet_RunID),str(p.dry_RunID)) for p in same.itertuples(index=False)}

    rows=[]
    for pid,p in enumerate(stable.itertuples(index=False)):
        rows.extend(pair_rows(
            pid,p,sampled,site,ci,meta,by_stratum,
            (str(p.wet_RunID),str(p.dry_RunID)) in same_keys
        ))
    rawdf=pd.DataFrame(rows)
    d=prepare_sample(rawdf)
    gate=gate_report(d,"primary")

    out={
        "analysis":"naamp_template_release_within_pair_v0_1",
        "contract":"exploration/NAAMP_TEMPLATE_RELEASE_WITHIN_PAIR_CONTRACT_V0_1.json",
        "coverage":{
            "all_pairs":int(len(allpairs)),
            "physically_stable_pairs":int(len(stable)),
            "candidate_pair_species":int(len(rawdf)),
            **gate,
        },
        "response_endpoints_read":False,
    }
    if not gate["pass"]:
        OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
        print(json.dumps(out,indent=2,sort_keys=True))
        return

    primary=fit_primary(d,"third_plus_depth","prior_strong_breadth")
    spatial_depth=fit_primary(d,"spatial_depth","prior_strong_breadth")
    active_k=fit_primary(d,"active_k","prior_strong_breadth")
    strong_k=fit_primary(d,"active_strong_k","prior_strong_breadth")
    any_breadth=fit_primary(d,"third_plus_depth","prior_any_breadth")
    magnitude=fit_magnitude(d)

    ds=prepare_sample(d[d.same_observer].copy())
    same_gate=gate_report(ds,"sensitivity")
    same_fit=fit_primary(ds,"third_plus_depth","prior_strong_breadth") if same_gate["pass"] else None

    de=prepare_sample(d[d.year_gap==1].copy())
    exact_gate=gate_report(de,"sensitivity")
    exact_fit=fit_primary(de,"third_plus_depth","prior_strong_breadth") if exact_gate["pass"] else None

    out.update({
        "response_endpoints_read":True,
        "primary_third_plus_depth":primary,
        "secondary_spatial_depth":spatial_depth,
        "secondary_active_k":active_k,
        "secondary_active_strong_k":strong_k,
        "sensitivity_prior_any_breadth":any_breadth,
        "magnitude_diagnostic":magnitude,
        "same_observer_sensitivity":{"gate":same_gate,"model":same_fit},
        "exact_consecutive_year_sensitivity":{"gate":exact_gate,"model":exact_fit},
        "classification":{
            "wet_side_releases_prior_template_depth":bool(primary and primary["positive_ci"]),
            "same_observer_support":bool(same_fit and same_fit["positive_ci"]),
            "exact_year_support":bool(exact_fit and exact_fit["positive_ci"]),
        },
        "interpretation_boundary":{
            "symmetric_wet_vs_dry_discordant_design":True,
            "pair_fixed_effects":True,
            "species_fixed_effects":True,
            "causal_rainfall_claim":False,
            "movement_inferred":False,
        }
    })
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
