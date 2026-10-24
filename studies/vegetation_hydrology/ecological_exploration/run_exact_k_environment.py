#!/usr/bin/env python3
"""Frozen-before-outcomes exploratory NAAMP frog chorus strong-site placement.

Use original USGS source tables, hash-pinned NLCD Collection 1.2 and JRC
preceding-calendar-month water. New research branch, not RC6 confirmation.
"""
from __future__ import annotations
import argparse
import bisect
import csv
import datetime as dt
import hashlib
import importlib.util
import json
import math
from collections import defaultdict
from pathlib import Path
import numpy as np
import pandas as pd
from exact_k_model import heldout_scores, route_cluster_interval

JRC_SHA="bd291a4f42a9768a4dfc2d92c68050344bde4e5b2bbb0a923a1218399e96f81b"
MIN_PRIMARY_EVENTS=200
MIN_PRIMARY_ROUTES=50
MIN_SECONDARY_EVENTS=100
MIN_SECONDARY_ROUTES=30
MIN_SECONDARY_SPREAD_FRACTION=.10
PRIOR_ALPHA=PRIOR_BETA=.5

def sha256(path):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for b in iter(lambda:f.read(1<<20),b""):
            h.update(b)
    return h.hexdigest()

def base_source(repo_root):
    path=Path(repo_root)/"scripts/naamp/run_naamp_ecological_pulse.py"
    if not path.is_file():raise FileNotFoundError(path)
    spec=importlib.util.spec_from_file_location("frozen_parent_naamp",path)
    m=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m

def environment(args):
    panel=pd.read_csv(args.nlcd,dtype={"RouteNumber":str,"SiteID":str})
    panel=panel.loc[panel.radius_m.eq(500)&panel.qc_status.eq("ok")].rename(columns={"year":"SurveyYear"})
    panel["SurveyYear"]=panel.SurveyYear.astype(int)
    if len(panel)!=64779 or panel[["RouteNumber","SiteID","SurveyYear"]].duplicated().any():
        raise RuntimeError("full NLCD environmental source failed QC")
    nlcd={}
    for r in panel.itertuples(index=False):
        nlcd[(r.RouteNumber,r.SiteID,int(r.SurveyYear))]=(
            float(r.frac_woody_wetland+r.frac_emergent_wetland),float(r.frac_open_water))
    if sha256(args.water)!=JRC_SHA:
        raise RuntimeError("strictly previous-calendar-month source SHA256 changed")
    w=pd.read_csv(args.water,dtype={"RouteNumber":str,"SiteID":str,"PreviousMonth":str})
    if len(w)!=172153 or w[["RouteNumber","SiteID","SurveyYear","PreviousMonth"]].duplicated().any():
        raise RuntimeError("full JRC source site-month coverage failed")
    water={}
    for r in w.itertuples(index=False):
        if float(r.valid_fraction)>=.5 and math.isfinite(float(r.water_fraction_among_observed)):
            water[(r.RouteNumber,r.SiteID,int(r.SurveyYear),r.PreviousMonth)]=(
                float(r.water_fraction_among_observed),float(r.valid_fraction))
    return nlcd,water

def positive_int(v):
    try:return int(v)
    except (TypeError,ValueError):return 0

def make_events(raw,runs,pairs,nlcd,water,accepted):
    """Fixed ten-site physical comparisons and strong-site prior-year history."""
    eligible={str(r.RunID):r for r in runs.itertuples(index=False)}
    if len(eligible)!=7848:
        raise RuntimeError("canonical runs changed")
    stops={rid:{} for rid in eligible}
    previous_visits=defaultdict(list)
    for r in raw["Stops.csv"]:
        rid=str(r.get("RunID","")).strip()
        stop=positive_int(r.get("StopNumber"))
        if rid not in eligible or not 1<=stop<=10 or str(r.get("SkippedStop","")).strip()!="0":
            continue
        route=str(eligible[rid].RouteNumber)
        site=str(r.get("SiteID","")).strip()
        if not site:continue
        if stop in stops[rid]:raise ValueError("duplicate StopNumber in run")
        stops[rid][stop]=site
        previous_visits[(route,site)].append(int(eligible[rid].SurveyYear))
    previous_visits={k:sorted(v) for k,v in previous_visits.items()}
    detected=defaultdict(dict)
    for r in raw["Counts.csv"]:
        rid=str(r.get("RunID","")).strip()
        if rid not in eligible:continue
        stop=positive_int(r.get("StopNumber"))
        if stop not in stops[rid]:continue
        taxon=str(r.get("Species","")).strip()
        ci=positive_int(r.get("CallingIndex"))
        if not taxon or ci not in (1,2,3):continue
        detected.setdefault(rid,{}).setdefault(taxon,{})[stop]=max(
            ci,detected.get(rid,{}).get(taxon,{}).get(stop,0))
    historical_strong=defaultdict(list)
    for rid,taxa in detected.items():
        year=int(eligible[rid].SurveyYear)
        route=str(eligible[rid].RouteNumber)
        for taxon,cells in taxa.items():
            for stop,ci in cells.items():
                if ci>=2:
                    historical_strong[(taxon,route,stops[rid][stop])].append(year)
    historical_strong={k:sorted(v) for k,v in historical_strong.items()}
    records=[];attr=defaultdict(int);taxon_tokens=set()
    for pair in pairs.itertuples(index=False):
        attr["canonical_pairs"]+=1
        wetid=str(pair.wet_RunID);dryid=str(pair.dry_RunID)
        if wetid not in eligible or dryid not in eligible:raise ValueError("missing matched RunID")
        route=str(pair.RouteNumber);state=str(pair.State)
        wet_stops=stops[wetid];dry_stops=stops[dryid]
        if len(wet_stops)!=10 or wet_stops!=dry_stops:
            attr["site_turnover_or_incomplete_pairs"]+=1
            continue
        sites=[wet_stops[i] for i in range(1,11)]
        if any((route,site) not in accepted for site in sites):
            attr["coordinate_rejected_pairs"]+=1
            continue
        wetter=eligible[wetid];drier=eligible[dryid]
        wet_year=int(wetter.SurveyYear)
        cutoff=min(wet_year,int(drier.SurveyYear))
        visit_day=dt.date(wet_year,1,1)+dt.timedelta(days=int(wetter.doy)-1)
        previous_month=visit_day.replace(day=1)-dt.timedelta(days=1)
        ym=f"{previous_month.year:04d}-{previous_month.month:02d}"
        mapped=[];observed_water=[];all_nlcd=True;all_water=True
        for site in sites:
            feature=nlcd.get((route,site,wet_year))
            if feature is None:
                all_nlcd=False
                break
            mapped.append(feature)
            source=water.get((route,site,wet_year,ym))
            if source is None:all_water=False
            observed_water.append(source[0] if source else float("nan"))
        if not all_nlcd:
            attr["missing_nlcd_pairs"]+=1
            continue
        if all_water:attr["pairs_with_all_jrc_usable"]+=1
        possible_new=set(detected.get(wetid,{}))-set(detected.get(dryid,{}))
        for taxon in sorted(possible_new):
            strong_cells=detected[wetid][taxon]
            y=[int(strong_cells.get(i,0)>=2) for i in range(1,11)]
            k=sum(y)
            if not 2<=k<=9:continue
            taxon_tokens.add(taxon)
            hist=[]
            for site in sites:
                n_prior=bisect.bisect_left(previous_visits.get((route,site),[]),cutoff)
                n_strong=bisect.bisect_left(historical_strong.get((taxon,route,site),[]),cutoff)
                p=(n_strong+PRIOR_ALPHA)/(n_prior+PRIOR_ALPHA+PRIOR_BETA)
                hist.append(math.log(p/(1.-p)))
            cov=np.column_stack([hist,np.asarray(mapped)[:,0],np.asarray(mapped)[:,1],observed_water])
            records.append({"State":state,"RouteNumber":route,"taxon":taxon,
                "pair_id":wetid+":"+dryid,"wet_year":wet_year,
                "strong_site_count":k,"x":cov.tolist(),"y":y,
                "complete_water":bool(all_water),
                "water_range":float(np.nanmax(observed_water)-np.nanmin(observed_water))
                   if np.isfinite(observed_water).any() else None})
            attr["eligible_placement_groups"]+=1
    attr["taxon_tokens"]=len(taxon_tokens)
    return records,dict(attr)

def analyze(records,attr):
    n_routes=len({(r["State"],r["RouteNumber"]) for r in records})
    if len(records)<MIN_PRIMARY_EVENTS or n_routes<MIN_PRIMARY_ROUTES:
        return {"status":"non_estimable_primary","n_events":len(records),"n_routes":n_routes,"attrition":attr}
    m0,c0=heldout_scores(records,[0])
    m1,c1=heldout_scores(records,[0,1,2])
    delta=m1-m0
    result={"status":"exploratory_only","primary_event_count":len(records),
        "primary_physical_routes":n_routes,
        "raw_operational_taxon_tokens":len(set(r["taxon"] for r in records)),
        "heldout_average_logscore_delta_M1minusM0":float(delta.mean()),
        "physical_route_bootstrap_95ci":route_cluster_interval(records,delta),
        "mean_heldout_logscore_M0":float(m0.mean()),
        "mean_heldout_logscore_M1":float(m1.mean()),
        "M0_coefficients_by_train_fold":c0,
        "M1_coefficients_by_train_fold":c1,
        "fixed_predictor_order":["strictly prior site CI2/3 logit","NLCD 500m woody+emergent wetland","NLCD 500m open water"],"source_attrition":attr}
    complete=[r for r in records if r["complete_water"]]
    n_jrc_routes=len({(r["State"],r["RouteNumber"]) for r in complete})
    n_jrc_spread=sum(r["water_range"] is not None and r["water_range"]>=.05 for r in complete)
    secondary={"n_events":len(complete),"n_routes":n_jrc_routes,
        "fraction_with_site_water_spread_ge5pp":n_jrc_spread/len(complete) if complete else None}
    if len(complete)<MIN_SECONDARY_EVENTS or n_jrc_routes<MIN_SECONDARY_ROUTES or n_jrc_spread/max(len(complete),1)<MIN_SECONDARY_SPREAD_FRACTION:
        secondary["status"]="non_estimable_JRC_pixel_and_variation_gates"
    else:
        v0,_=heldout_scores(complete,[0])
        v1,_=heldout_scores(complete,[0,1,2])
        v2,c2=heldout_scores(complete,[0,1,2,3])
        secondary.update(status="exploratory_only",
            same_sample_M2minusM1=float((v2-v1).mean()),
            same_sample_M1minusM0=float((v1-v0).mean()),
            physical_route_bootstrap_95ci=route_cluster_interval(complete,v2-v1),
            M2_coefficients_by_train_fold=c2)
    result["secondary_JRC_prior_month"]=secondary
    result["independent_replication"]=False
    result["no_colonisation_or_spawning_inference"]=True
    return result

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--repo-root",required=True)
    p.add_argument("--nlcd",required=True)
    p.add_argument("--water",required=True)
    p.add_argument("--coordinates",required=True)
    p.add_argument("--out",required=True)
    args=p.parse_args()
    base=base_source(args.repo_root)
    nlcd,water=environment(args)
    with open(args.coordinates,newline="",encoding="utf-8-sig") as f:
        accepted={(r["RouteNumber"],r["SiteID"])
                  for r in csv.DictReader(f) if r["status"]=="accepted"}
    original=base.load()
    runs,species_sets=base.build_runs(original)
    pairs=base.pair_runs(runs,species_sets)
    if len(runs)!=7848 or len(pairs)!=4236:
        raise RuntimeError(f"canonical original NAAMP case count changed: runs={len(runs)} pairs={len(pairs)}")
    records,attr=make_events(original,runs,pairs,nlcd,water,accepted)
    report=analyze(records,attr)
    report["analysis"]="new_independent_branch_posthoc_exploratory_exact_k_chorus_environment_v0_1"
    report["sources"]={"Runs_sha256":base.PINS["Runs.csv"],
        "Stops_sha256":base.PINS["Stops.csv"],
        "Counts_sha256":base.PINS["Counts.csv"],
        "JRC_full_csv_sha256":JRC_SHA,
        "annual_habitat":"USGS NLCD Collection 1.2"}
    report["reuses_previously_studied_NAAMP"]=True
    report["cannot_claim_independent_confirmation"]=True
    report["biological_boundary"]="acoustic CI2/3 stop placement, not synchrony, population occupancy, frog movement or breeding success"
    dest=Path(args.out);dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(report,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({k:v for k,v in report.items() if not str(k).endswith("coefficients_by_train_fold")},indent=2))

if __name__=="__main__":
    main()
