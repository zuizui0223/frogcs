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
OUT=EXP/"NAAMP_NWI_WETLAND_SYSTEM_STRONG_CHORUS_RECEIPT_V0_1.json"
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
sameobs=loadmod("sameobs_base",NAAMP/"run_naamp_same_observer_robustness.py")


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
    bad={k:v for k,v in vals.items() if len(v)>1}
    if bad:
        raise RuntimeError(f"multiple SiteIDs per run-stop: {list(bad)[:10]}")
    return {k:next(iter(v)) for k,v in vals.items() if v}


def calling_index_map(raw,eligible,sampled):
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
    duplicate_cells=0
    conflict_cells=0
    for (rid,st,sp),x in vals.items():
        if len(x)>1:
            duplicate_cells+=1
            conflict_cells+=int(len(set(x))>1)
        by[(rid,st)][sp]=max(x)
    return by,{
        "positive_cells":int(len(vals)),
        "duplicate_cells":int(duplicate_cells),
        "conflicting_duplicate_cells":int(conflict_cells),
        "duplicate_resolution":"maximum CallingIndex"
    }


def group_for(match,radius):
    if not match or bool(match.get("ambiguous_tie",False)):
        return None
    d=match.get("distance_m")
    if d is None or float(d)>float(radius):
        return None
    attr=str(match.get("ATTRIBUTE") or "").strip().upper()
    if attr.startswith("P"):
        return 1
    if attr.startswith("R") or attr.startswith("L"):
        return 0
    return None


def site_route_lookup(raw,runs,eligible):
    rr={str(r.RunID):str(r.route_cluster) for r in runs.itertuples(index=False)}
    out={}
    for s in raw["Stops.csv"]:
        rid=(s.get("RunID") or "").strip()
        sid=(s.get("SiteID") or "").strip()
        if rid in eligible and sid and rid in rr:
            out[sid]=rr[rid]
    return out


def gate_report(matches,site_routes,eligibility):
    groups={0:[],1:[]}
    for sid,m in matches.items():
        g=group_for(m,200)
        if g is not None:
            groups[g].append(sid)
    routes={
        g:len({site_routes.get(s) for s in ids if site_routes.get(s)})
        for g,ids in groups.items()
    }
    sites={g:len(ids) for g,ids in groups.items()}
    gate=bool(
        eligibility["feasibility_gate"]["overall_pass"]
        and sites[0]>=500 and sites[1]>=500
        and routes[0]>=150 and routes[1]>=150
    )
    return {
        "eligibility_overall_pass":bool(eligibility["feasibility_gate"]["overall_pass"]),
        "palustrine_sites":sites[1],"riverine_lacustrine_sites":sites[0],
        "palustrine_routes":routes[1],"riverine_lacustrine_routes":routes[0],
        "mechanism_run_gate":gate,
    }


def build_rows(raw,runs,route_sets,matches,radius,same_observer_keys):
    eligible=set(runs["RunID"].astype(str))
    sampled,_=spatial.stop_matrix(raw,eligible)
    site=site_map(raw,eligible)
    ci,ci_audit=calling_index_map(raw,eligible,sampled)
    pairs=base.pair_runs(runs,route_sets).copy().reset_index(drop=True)

    rows=[]
    stable_rows=0
    classified_rows=0
    for pid,p in enumerate(pairs.itertuples(index=False)):
        wet=str(p.wet_RunID); dry=str(p.dry_RunID)
        wst=set(sampled[wet]); dst=set(sampled[dry])
        if len(wst)!=10 or wst!=dst:
            raise RuntimeError(f"stop alignment failed pair {pid}")
        pair_sameobs=(wet,dry) in same_observer_keys

        for st in sorted(wst):
            ws=site.get((wet,st)); ds=site.get((dry,st))
            if ws is None or ds is None or ws!=ds:
                continue
            stable_rows+=1
            g=group_for(matches.get(ws),radius)
            if g is None:
                continue
            classified_rows+=1

            wm=ci.get((wet,st),{})
            dm=ci.get((dry,st),{})
            strong_score=0.0
            strong_count=0.0
            weak_score=0.0
            for sp in set(wm)|set(dm):
                w=int(wm.get(sp,0)); d=int(dm.get(sp,0))
                if d==0 and w>0:
                    if w>=2:
                        strong_score+=float(w)
                        strong_count+=1.0
                    else:
                        weak_score+=1.0
            rows.append({
                "pair_id":int(pid),
                "route_cluster":str(p.route_cluster),
                "year_gap":int(p.year_gap),
                "rain_contrast":float(p.rain_contrast),
                "StopNumber":str(st),
                "SiteID":str(ws),
                "palustrine":int(g),
                "strong_new_score":strong_score,
                "strong_new_count":strong_count,
                "weak_new_score":weak_score,
                "same_observer":bool(pair_sameobs),
            })
    return pd.DataFrame(rows),{
        "stable_pair_stop_rows":int(stable_rows),
        "classified_pair_stop_rows":int(classified_rows),
        "calling_index_audit":ci_audit,
    }


def fit_within_pair(df,response):
    d=df.copy()
    if d.empty:
        return None
    d["inter"]=d["palustrine"].astype(float)*d["rain_contrast"].astype(float)
    informative=d.groupby("pair_id")["palustrine"].nunique()
    good=informative[informative>=2].index
    d=d[d["pair_id"].isin(good)].copy()
    if len(d)<100:
        return None
    for col in (response,"palustrine","inter"):
        d[col+"_w"]=d[col].astype(float)-d.groupby("pair_id")[col].transform("mean").astype(float)
    X=d[["palustrine_w","inter_w"]].astype(float)
    y=d[response+"_w"].astype(float)
    fit=sm.OLS(y,X).fit(cov_type="cluster",cov_kwds={"groups":d["route_cluster"].astype(str)})
    b=float(fit.params["inter_w"])
    se=float(fit.bse["inter_w"])
    return {
        "response":response,
        "n_pair_stop_rows":int(len(d)),
        "n_informative_pairs":int(d["pair_id"].nunique()),
        "n_routes":int(d["route_cluster"].nunique()),
        "palustrine_sites":int(d.loc[d["palustrine"]==1,"SiteID"].nunique()),
        "riverine_lacustrine_sites":int(d.loc[d["palustrine"]==0,"SiteID"].nunique()),
        "context_main_beta":float(fit.params["palustrine_w"]),
        "interaction_beta":b,
        "interaction_se_cluster":se,
        "interaction_ci95":[b-Q*se,b+Q*se],
        "interaction_p":float(fit.pvalues["inter_w"]),
        "prediction_pass":bool(b>0 and b-Q*se>0),
    }


def main():
    eligibility=json.loads(ELIG.read_text())
    matches=eligibility.get("site_matches") or {}

    raw=base.load()
    runs,route_sets=base.build_runs(raw)
    eligible=set(runs["RunID"].astype(str))
    site_routes=site_route_lookup(raw,runs,eligible)
    gate=gate_report(matches,site_routes,eligibility)

    all_pairs,same= sameobs.same_observer_pairs(raw,runs,route_sets)
    same_keys={(str(p.wet_RunID),str(p.dry_RunID)) for p in same.itertuples(index=False)}

    if not gate["mechanism_run_gate"]:
        output={
            "analysis":"naamp_nwi_wetland_system_strong_chorus_v0_1",
            "contract":"exploration/NAAMP_NWI_WETLAND_SYSTEM_STRONG_CHORUS_CONTRACT_V0_1.json",
            "status":"not_run_due_to_prefixed_context_gate",
            "gate":gate,
            "response_endpoints_read":False,
        }
        OUT.write_text(json.dumps(output,indent=2,sort_keys=True)+"\n")
        print(json.dumps(output,indent=2,sort_keys=True))
        return

    d200,audit200=build_rows(raw,runs,route_sets,matches,200,same_keys)
    informative200=d200.groupby("pair_id")["palustrine"].nunique()
    n_informative200=int((informative200>=2).sum())
    if n_informative200 < 2000:
        output={
            "analysis":"naamp_nwi_wetland_system_strong_chorus_v0_1",
            "contract":"exploration/NAAMP_NWI_WETLAND_SYSTEM_STRONG_CHORUS_CONTRACT_V0_1.json",
            "status":"not_run_due_to_prefixed_within_pair_gate",
            "gate":{**gate,"informative_pairs_200m":n_informative200},
            "response_endpoints_read":False,
        }
        OUT.write_text(json.dumps(output,indent=2,sort_keys=True)+"\n")
        print(json.dumps(output,indent=2,sort_keys=True))
        return
    gate["informative_pairs_200m"]=n_informative200
    primary=fit_within_pair(d200,"strong_new_score")
    count=fit_within_pair(d200,"strong_new_count")
    weak=fit_within_pair(d200,"weak_new_score")
    sameobs_primary=fit_within_pair(d200[d200["same_observer"]].copy(),"strong_new_score")

    d500,audit500=build_rows(raw,runs,route_sets,matches,500,same_keys)
    radius500=fit_within_pair(d500,"strong_new_score")

    output={
        "analysis":"naamp_nwi_wetland_system_strong_chorus_v0_1",
        "contract":"exploration/NAAMP_NWI_WETLAND_SYSTEM_STRONG_CHORUS_CONTRACT_V0_1.json",
        "status":"completed_after_prefixed_context_gate",
        "gate":gate,
        "coverage":{
            "all_matched_pairs":int(len(all_pairs)),
            "same_observer_pairs":int(len(same)),
        },
        "primary_200m":{
            "row_audit":audit200,
            "model":primary,
        },
        "sensitivity_strong_count_200m":count,
        "diagnostic_weak_new_score_200m":weak,
        "sensitivity_same_observer_200m":sameobs_primary,
        "sensitivity_radius_500m":{
            "row_audit":audit500,
            "model":radius500,
        },
        "classification":{
            "palustrine_strong_chorus_activation_supported":bool(primary and primary["prediction_pass"]),
            "same_observer_support":bool(sameobs_primary and sameobs_primary["prediction_pass"]),
            "radius_500m_support":bool(radius500 and radius500["prediction_pass"]),
        },
        "interpretation_boundary":{
            "survey_night_inundation_observed":False,
            "frog_call_origin_polygon_observed":False,
            "calling_index_2_3":"overlapping/full chorus category, not breeding success",
            "physiological_mediator_identified":False,
            "causal_rainfall_claim":False,
            "submission_story_change_authorized":False,
        },
    }
    OUT.write_text(json.dumps(output,indent=2,sort_keys=True)+"\n")
    print(json.dumps(output,indent=2,sort_keys=True))


if __name__=="__main__":
    main()
