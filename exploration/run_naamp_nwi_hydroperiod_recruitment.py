#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm

ROOT=Path(__file__).resolve().parents[1]
NAAMP=ROOT/"scripts"/"naamp"
EXP=ROOT/"exploration"
ELIG=EXP/"NAAMP_NWI_CONTEXT_ELIGIBILITY_RECEIPT_V0_1.json"
OUT=EXP/"NAAMP_NWI_HYDROPERIOD_RECRUITMENT_RECEIPT_V0_1.json"
Q=1.959963984540054

PULSE={"A","C","J"}
PERSIST={"F","G","H"}


def loadmod(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    mod=importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(mod)
    return mod


base=loadmod("pulse_base",NAAMP/"run_naamp_ecological_pulse.py")
spatial=loadmod("spatial_base",NAAMP/"run_naamp_spatial_taxonomic_activation_decomposition.py")


def site_map(raw,eligible):
    vals=defaultdict(set)
    for s in raw["Stops.csv"]:
        rid=(s.get("RunID") or "").strip()
        st=(s.get("StopNumber") or "").strip()
        sid=(s.get("SiteID") or "").strip()
        if rid not in eligible or (s.get("SkippedStop") or "").strip()!="0" or not st:
            continue
        if sid:
            vals[(rid,st)].add(sid)
    conflict={k:v for k,v in vals.items() if len(v)>1}
    if conflict:
        raise RuntimeError(f"multiple SiteIDs per run-stop: {list(conflict)[:10]}")
    return {k:next(iter(v)) for k,v in vals.items() if v}


def group_for(site_match,radius):
    if site_match is None:
        return None
    if bool(site_match.get("ambiguous_tie",False)):
        return None
    d=site_match.get("distance_m")
    if d is None or float(d)>float(radius):
        return None
    code=str(site_match.get("WATER_REGIME") or "").strip().upper()
    if code in PULSE:
        return 1
    if code in PERSIST:
        return 0
    return None


def site_route_lookup(raw,runs,eligible):
    run_route={
        str(r.RunID):str(r.route_cluster)
        for r in runs.itertuples(index=False)
    }
    out={}
    for s in raw["Stops.csv"]:
        rid=(s.get("RunID") or "").strip()
        sid=(s.get("SiteID") or "").strip()
        if rid in eligible and sid and rid in run_route:
            out[sid]=run_route[rid]
    return out


def gate_report(matches,site_routes,eligibility):
    groups={0:[],1:[]}
    for sid,m in matches.items():
        g=group_for(m,200)
        if g is not None:
            groups[g].append(sid)
    route_counts={
        g:len({site_routes.get(s) for s in ss if site_routes.get(s)})
        for g,ss in groups.items()
    }
    site_counts={g:len(ss) for g,ss in groups.items()}
    gate=bool(
        eligibility["feasibility_gate"]["overall_pass"]
        and site_counts[0]>=200 and site_counts[1]>=200
        and route_counts[0]>=75 and route_counts[1]>=75
    )
    return {
        "eligibility_overall_pass":bool(eligibility["feasibility_gate"]["overall_pass"]),
        "pulse_sites":site_counts[1],
        "persistent_sites":site_counts[0],
        "pulse_routes":route_counts[1],
        "persistent_routes":route_counts[0],
        "mechanism_run_gate":gate,
    }


def build_stop_rows(raw,runs,route_sets,matches,radius):
    eligible=set(runs["RunID"].astype(str))
    sampled,stop_species=spatial.stop_matrix(raw,eligible)
    site=site_map(raw,eligible)
    pairs=base.pair_runs(runs,route_sets).copy().reset_index(drop=True)

    rows=[]
    stable_rows=0
    classified_rows=0
    for pid,p in enumerate(pairs.itertuples(index=False)):
        wet=str(p.wet_RunID); dry=str(p.dry_RunID)
        wst=set(sampled[wet]); dst=set(sampled[dry])
        if len(wst)!=10 or wst!=dst:
            raise RuntimeError(f"stop alignment failed pair {pid}")
        stops=sorted(wst)
        W=set()
        D=set()
        for st in stops:
            W.update(stop_species.get((wet,st),set()))
            D.update(stop_species.get((dry,st),set()))

        for st in stops:
            ws=site.get((wet,st)); ds=site.get((dry,st))
            if ws is None or ds is None or ws!=ds:
                continue
            stable_rows+=1
            g=group_for(matches.get(ws),radius)
            if g is None:
                continue
            classified_rows+=1
            wset=set(stop_species.get((wet,st),set()))
            dset=set(stop_species.get((dry,st),set()))
            gain=sum(1 for sp in (wset-dset) if sp not in D)
            loss=sum(1 for sp in (dset-wset) if sp not in W)
            rows.append({
                "pair_id":pid,
                "route_cluster":str(p.route_cluster),
                "State":str(p.State),
                "RouteNumber":str(p.RouteNumber),
                "RunNumber":str(p.RunNumber),
                "year_gap":int(p.year_gap),
                "rain_contrast":float(p.rain_contrast),
                "StopNumber":str(st),
                "SiteID":str(ws),
                "pulse":int(g),
                "gain_route_new":float(gain),
                "loss_route_new":float(loss),
                "net_route_new":float(gain-loss),
            })
    return pairs,pd.DataFrame(rows),{
        "stable_pair_stop_rows":int(stable_rows),
        "classified_pair_stop_rows":int(classified_rows),
    }


def fit_within_pair(df,response):
    d=df.copy()
    if d.empty:
        return None
    d["inter"]=d["pulse"].astype(float)*d["rain_contrast"].astype(float)
    informative=d.groupby("pair_id")["pulse"].nunique()
    good=informative[informative>=2].index
    d=d[d["pair_id"].isin(good)].copy()
    if len(d)<100:
        return None

    for col in (response,"pulse","inter"):
        d[col+"_w"]=d[col].astype(float)-d.groupby("pair_id")[col].transform("mean").astype(float)

    X=d[["pulse_w","inter_w"]].astype(float)
    y=d[response+"_w"].astype(float)
    fit=sm.OLS(y,X).fit(cov_type="cluster",cov_kwds={"groups":d["route_cluster"].astype(str)})
    b=float(fit.params["inter_w"])
    se=float(fit.bse["inter_w"])
    p=float(fit.pvalues["inter_w"])
    return {
        "response":response,
        "n_pair_stop_rows":int(len(d)),
        "n_informative_pairs":int(d["pair_id"].nunique()),
        "n_routes":int(d["route_cluster"].nunique()),
        "pulse_sites":int(d.loc[d["pulse"]==1,"SiteID"].nunique()),
        "persistent_sites":int(d.loc[d["pulse"]==0,"SiteID"].nunique()),
        "context_main_beta":float(fit.params["pulse_w"]),
        "interaction_beta":b,
        "interaction_se_cluster":se,
        "interaction_ci95":[b-Q*se,b+Q*se],
        "interaction_p":p,
        "prediction_pass":bool(b>0 and b-Q*se>0),
    }


def main():
    eligibility=json.loads(ELIG.read_text())
    matches=eligibility.get("site_matches") or {}

    raw=base.load()
    runs,route_sets=base.build_runs(raw)
    eligible=set(runs["RunID"].astype(str))
    routes=site_route_lookup(raw,runs,eligible)
    gate=gate_report(matches,routes,eligibility)

    if not gate["mechanism_run_gate"]:
        output={
            "analysis":"naamp_nwi_hydroperiod_recruitment_test_v0_1",
            "contract":"exploration/NAAMP_NWI_HYDROPERIOD_RECRUITMENT_CONTRACT_V0_1.json",
            "status":"not_run_due_to_prefixed_feasibility_gate",
            "gate":gate,
            "response_endpoints_read":False,
        }
        OUT.write_text(json.dumps(output,indent=2,sort_keys=True)+"\n")
        print(json.dumps(output,indent=2,sort_keys=True))
        return

    pairs,d200,audit200=build_stop_rows(raw,runs,route_sets,matches,200)
    primary=fit_within_pair(d200,"net_route_new")
    gain_only=fit_within_pair(d200,"gain_route_new")
    exact=fit_within_pair(d200[d200["year_gap"]==1].copy(),"net_route_new")

    _,d500,audit500=build_stop_rows(raw,runs,route_sets,matches,500)
    radius500=fit_within_pair(d500,"net_route_new")

    output={
        "analysis":"naamp_nwi_hydroperiod_recruitment_test_v0_1",
        "contract":"exploration/NAAMP_NWI_HYDROPERIOD_RECRUITMENT_CONTRACT_V0_1.json",
        "status":"completed_after_prefixed_feasibility_gate",
        "gate":gate,
        "primary_200m":{
            "row_audit":audit200,
            "model":primary,
        },
        "sensitivity_gain_only_200m":gain_only,
        "sensitivity_exact_consecutive_year_200m":exact,
        "sensitivity_radius_500m":{
            "row_audit":audit500,
            "model":radius500,
        },
        "classification":{
            "hydroperiod_recruitment_interaction_supported":bool(primary and primary["prediction_pass"]),
            "meaning":"Positive support means route-new recruitment is more strongly associated with rainfall contrast at pulse-limited than persistent-surface-water NWI contexts within the same matched pair."
        },
        "interpretation_boundary":{
            "survey_night_inundation_observed":False,
            "frog_call_origin_polygon_observed":False,
            "causal_mediator_identified":False,
            "causal_rainfall_claim":False,
            "submission_story_change_authorized":False,
        }
    }
    OUT.write_text(json.dumps(output,indent=2,sort_keys=True)+"\n")
    print(json.dumps(output,indent=2,sort_keys=True))


if __name__=="__main__":
    main()
