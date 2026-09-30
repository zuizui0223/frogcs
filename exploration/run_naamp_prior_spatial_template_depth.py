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
OUT=ROOT/"exploration"/"NAAMP_PRIOR_SPATIAL_TEMPLATE_DEPTH_RECEIPT_V0_1.json"
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

def pair_species_rows(p,sampled,site,ci,meta,by_stratum,same_observer):
    w=str(p.wet_RunID); d=str(p.dry_RunID)
    key=meta[w]["key"]; cutoff=int(p.year_earlier)
    prior=[rid for rid in by_stratum[key] if meta[rid]["year"]<cutoff]
    if not prior:
        return []

    current_stops=sorted(sampled[w],key=lambda x:float(x))
    current_sids=[site[(w,st)] for st in current_stops]

    # Prior sampling opportunities at each current physical SiteID and route occurrence.
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
                if x>0:
                    route_prior_species.add(sp)
                    seen_route.add(sp)
                    if sid in current_sids:
                        site_any[sid].add(sp)
                if x>=2 and sid in current_sids:
                    site_strong[sid].add(sp)
        for sp in seen_route:
            route_runs_with_species[sp]+=1

    opportunity=[sid for sid in current_sids if site_opp.get(sid,0)>0]
    if len(opportunity)<8:
        return []

    dry_route=set()
    wet_route=set()
    wet_by_species=defaultdict(dict)
    for st in current_stops:
        dry_route.update(ci.get((d,st),{}))
        wm=ci.get((w,st),{})
        wet_route.update(wm)
        for sp,x in wm.items():
            if int(x)>0:
                wet_by_species[sp][st]=int(x)

    focal=sorted((wet_route-dry_route)&route_prior_species)
    rows=[]
    for sp in focal:
        occ=wet_by_species.get(sp,{})
        wet_k=len(occ)
        if wet_k<1:
            continue
        any_sites=sum(sp in site_any.get(sid,set()) for sid in opportunity)
        strong_sites=sum(sp in site_strong.get(sid,set()) for sid in opportunity)
        prior_any_breadth=any_sites/len(opportunity)
        prior_strong_breadth=strong_sites/len(opportunity)
        prior_route_frequency=route_runs_with_species.get(sp,0)/len(prior)
        wet_strong_k=sum(int(x)>=2 for x in occ.values())
        rows.append({
            "species":sp,
            "route_cluster":str(p.route_cluster),
            "State":str(p.State),
            "RunNumber":str(p.RunNumber),
            "same_observer":bool(same_observer),
            "year_gap":float(p.year_gap),
            "rain_contrast":float(p.rain_contrast),
            "temp_difference":float(p.temp_difference),
            "doy_difference":float(p.doy_difference),
            "n_prior_runs":float(len(prior)),
            "n_opportunity_sites":float(len(opportunity)),
            "prior_any_breadth":float(prior_any_breadth),
            "prior_strong_breadth":float(prior_strong_breadth),
            "prior_route_frequency":float(prior_route_frequency),
            "wet_k":float(wet_k),
            "spatial_depth":float(wet_k-1),
            "third_plus_depth":float(max(wet_k-2,0)),
            "wet_strong_k":float(wet_strong_k),
        })
    return rows

def fit_model(df,response,predictor):
    d=df.copy()
    if d.empty:
        return None
    x=pd.to_numeric(d[predictor],errors="coerce").to_numpy(float)
    sd=float(np.std(x,ddof=0))
    if not sd>0:
        return None
    d["z_breadth"]=(x-float(np.mean(x)))/sd
    d["c_rain_contrast"]=d.rain_contrast-float(d.rain_contrast.mean())
    form=(
        f"{response} ~ z_breadth + c_rain_contrast + z_breadth:c_rain_contrast + "
        "prior_route_frequency + temp_difference + doy_difference + year_gap + "
        "C(species) + C(State) + C(RunNumber)"
    )
    m=smf.ols(form,data=d).fit(
        cov_type="cluster",cov_kwds={"groups":d.route_cluster}
    )
    b=float(m.params["z_breadth"]); se=float(m.bse["z_breadth"])
    bi=float(m.params["z_breadth:c_rain_contrast"])
    sei=float(m.bse["z_breadth:c_rain_contrast"])
    return {
        "response":response,
        "predictor":predictor,
        "n_pair_species":int(len(d)),
        "n_routes":int(d.route_cluster.nunique()),
        "n_species":int(d.species.nunique()),
        "predictor_mean":float(np.mean(x)),
        "predictor_sd":sd,
        "breadth_beta":b,
        "breadth_se":se,
        "breadth_ci95":[b-Q*se,b+Q*se],
        "breadth_p":float(m.pvalues["z_breadth"]),
        "breadth_positive_ci":bool(b>0 and b-Q*se>0),
        "breadth_x_rain_beta":bi,
        "breadth_x_rain_se":sei,
        "breadth_x_rain_ci95":[bi-Q*sei,bi+Q*sei],
        "breadth_x_rain_p":float(m.pvalues["z_breadth:c_rain_contrast"]),
    }

def gate_report(d):
    sd=float(d.prior_strong_breadth.std(ddof=0)) if len(d) else 0.0
    return {
        "n_pair_species":int(len(d)),
        "n_routes":int(d.route_cluster.nunique()) if len(d) else 0,
        "n_species":int(d.species.nunique()) if len(d) else 0,
        "prior_strong_breadth_sd":sd,
        "pass":bool(
            len(d)>=1000
            and d.route_cluster.nunique()>=300
            and d.species.nunique()>=20
            and sd>=0.10
        )
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
    for p in stable.itertuples(index=False):
        rows.extend(pair_species_rows(
            p,sampled,site,ci,meta,by_stratum,
            (str(p.wet_RunID),str(p.dry_RunID)) in same_keys
        ))
    d=pd.DataFrame(rows)
    gate=gate_report(d)

    out={
        "analysis":"naamp_prior_spatial_template_depth_v0_1",
        "contract":"exploration/NAAMP_PRIOR_SPATIAL_TEMPLATE_DEPTH_CONTRACT_V0_1.json",
        "coverage":{
            "all_pairs":int(len(allpairs)),
            "physically_stable_pairs":int(len(stable)),
            **gate,
        },
        "response_endpoints_read":False,
    }
    if not gate["pass"]:
        OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
        print(json.dumps(out,indent=2,sort_keys=True))
        return

    primary=fit_model(d,"third_plus_depth","prior_strong_breadth")
    secondary_depth=fit_model(d,"spatial_depth","prior_strong_breadth")
    secondary_k=fit_model(d,"wet_k","prior_strong_breadth")
    strong_k=fit_model(d,"wet_strong_k","prior_strong_breadth")
    any_breadth=fit_model(d,"third_plus_depth","prior_any_breadth")

    ds=d[d.same_observer].copy()
    same_gate=gate_report(ds)
    same_fit=fit_model(ds,"third_plus_depth","prior_strong_breadth") if same_gate["pass"] else None

    exact=d[d.year_gap==1].copy()
    exact_gate=gate_report(exact)
    exact_fit=fit_model(exact,"third_plus_depth","prior_strong_breadth") if exact_gate["pass"] else None

    out.update({
        "response_endpoints_read":True,
        "primary_third_plus_depth":primary,
        "secondary_spatial_depth":secondary_depth,
        "secondary_wet_k":secondary_k,
        "secondary_wet_strong_k":strong_k,
        "sensitivity_prior_any_breadth":any_breadth,
        "same_observer_sensitivity":{"gate":same_gate,"model":same_fit},
        "exact_consecutive_year_sensitivity":{"gate":exact_gate,"model":exact_fit},
        "classification":{
            "prior_strong_template_breadth_predicts_depth":bool(primary and primary["breadth_positive_ci"]),
            "same_observer_support":bool(same_fit and same_fit["breadth_positive_ci"]),
            "exact_year_support":bool(exact_fit and exact_fit["breadth_positive_ci"]),
        },
        "interpretation_boundary":{
            "post_activation_model":True,
            "activation_probability_modeled":False,
            "persistent_population_vs_habitat_template_unresolved":True,
            "movement_inferred":False,
            "causal_rainfall_claim":False,
        }
    })
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
