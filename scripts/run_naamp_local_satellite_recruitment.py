#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import math
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf

ROOT=Path(__file__).resolve().parent
BASE_SCRIPT=ROOT/"run_naamp_ecological_pulse.py"
spec=importlib.util.spec_from_file_location("pulse_base",BASE_SCRIPT)
base=importlib.util.module_from_spec(spec)
assert spec.loader
spec.loader.exec_module(base)

Q=1.959963984540054
MIN_BG=3

def logit(p: float) -> float:
    return float(math.log(p/(1.0-p)))

def jeffreys(k: int,n: int) -> float:
    return float((k+0.5)/(n+1.0))

def make_pair_id(r) -> str:
    return f"{r.State}|{r.RouteNumber}|{r.RunNumber}|{r.wet_RunID}|{r.dry_RunID}"

def build_event_tables(runs,sets,pairs):
    strata=defaultdict(list)
    run_meta={}
    for r in runs.itertuples(index=False):
        key=(str(r.State),str(r.RouteNumber),str(r.RunNumber))
        strata[key].append(str(r.RunID))
        run_meta[str(r.RunID)]={
            "SurveyYear":int(r.SurveyYear),
            "species":sets[str(r.RunID)],
        }

    events=[]
    prior_events=[]

    for pr in pairs.itertuples(index=False):
        key=(str(pr.State),str(pr.RouteNumber),str(pr.RunNumber))
        all_ids=strata[key]
        excluded={str(pr.wet_RunID),str(pr.dry_RunID)}
        bg_ids=[rid for rid in all_ids if rid not in excluded]
        prior_ids=[
            rid for rid in bg_ids
            if run_meta[rid]["SurveyYear"] < int(pr.year_earlier)
        ]

        W=sets[str(pr.wet_RunID)]
        D=sets[str(pr.dry_RunID)]
        discord=(W-D)|(D-W)
        pid=make_pair_id(pr)

        common={
            "pair_id":pid,
            "State":str(pr.State),
            "RouteNumber":str(pr.RouteNumber),
            "RunNumber":str(pr.RunNumber),
            "route_cluster":str(pr.route_cluster),
            "year_earlier":int(pr.year_earlier),
            "year_later":int(pr.year_later),
            "year_gap":int(pr.year_gap),
            "rain_contrast":float(pr.rain_contrast),
            "temp_difference":float(pr.temp_difference),
            "doy_difference":float(pr.doy_difference),
        }

        for sp in sorted(discord):
            y=int(sp in W)
            if len(bg_ids)>=MIN_BG:
                k=sum(sp in run_meta[rid]["species"] for rid in bg_ids)
                p=jeffreys(k,len(bg_ids))
                events.append({
                    **common,
                    "species":sp,
                    "wet_only":y,
                    "n_background":int(len(bg_ids)),
                    "positive_background":int(k),
                    "local_prevalence":p,
                    "local_logit_prevalence":logit(p),
                    "local_class":"satellite" if p<=.25 else ("core" if p>=.75 else "intermediate"),
                })

            if len(prior_ids)>=MIN_BG:
                k=sum(sp in run_meta[rid]["species"] for rid in prior_ids)
                p=jeffreys(k,len(prior_ids))
                prior_events.append({
                    **common,
                    "species":sp,
                    "wet_only":y,
                    "n_background":int(len(prior_ids)),
                    "positive_background":int(k),
                    "local_prevalence":p,
                    "local_logit_prevalence":logit(p),
                    "local_class":"satellite" if p<=.25 else ("core" if p>=.75 else "intermediate"),
                })

    return pd.DataFrame(events),pd.DataFrame(prior_events)

def pair_level(events: pd.DataFrame) -> pd.DataFrame:
    rows=[]
    if len(events)==0:
        return pd.DataFrame()
    for pid,g in events.groupby("pair_id",sort=False):
        wet=g[g.wet_only==1]
        dry=g[g.wet_only==0]
        if len(wet)==0 or len(dry)==0:
            continue
        r=g.iloc[0]
        rows.append({
            "pair_id":pid,
            "State":r.State,
            "RouteNumber":r.RouteNumber,
            "RunNumber":r.RunNumber,
            "route_cluster":r.route_cluster,
            "year_gap":int(r.year_gap),
            "rain_contrast":float(r.rain_contrast),
            "temp_difference":float(r.temp_difference),
            "doy_difference":float(r.doy_difference),
            "wet_species_n":int(len(wet)),
            "dry_species_n":int(len(dry)),
            "mean_wet_local_logit_prevalence":float(wet.local_logit_prevalence.mean()),
            "mean_dry_local_logit_prevalence":float(dry.local_logit_prevalence.mean()),
            "delta_local_logit_prevalence":float(wet.local_logit_prevalence.mean()-dry.local_logit_prevalence.mean()),
            "mean_wet_local_prevalence":float(wet.local_prevalence.mean()),
            "mean_dry_local_prevalence":float(dry.local_prevalence.mean()),
        })
    return pd.DataFrame(rows)

def intercept_test(pairs: pd.DataFrame):
    if len(pairs)<20 or pairs.route_cluster.nunique()<10:
        return {"estimable":False,"n_pairs":int(len(pairs)),"reason":"insufficient_pairs_or_routes"}
    f=smf.ols("delta_local_logit_prevalence ~ 1",data=pairs).fit(
        cov_type="cluster",cov_kwds={"groups":pairs.route_cluster}
    )
    b=float(f.params["Intercept"]);se=float(f.bse["Intercept"]);p=float(f.pvalues["Intercept"])
    lo=b-Q*se;hi=b+Q*se
    return {
        "estimable":True,
        "n_pairs":int(len(pairs)),
        "n_routes":int(pairs.route_cluster.nunique()),
        "mean_delta_logit_prevalence":b,
        "se_cluster":se,
        "ci95":[lo,hi],
        "p_value_two_sided":p,
        "negative_ci_support":bool(hi<0),
        "mean_wet_prevalence":float(pairs.mean_wet_local_prevalence.mean()),
        "mean_dry_prevalence":float(pairs.mean_dry_local_prevalence.mean()),
    }

def pulse_strength_test(pairs: pd.DataFrame):
    if len(pairs)<50 or pairs.route_cluster.nunique()<20:
        return {"estimable":False,"n_pairs":int(len(pairs)),"reason":"insufficient_pairs_or_routes"}
    formula="delta_local_logit_prevalence ~ rain_contrast + temp_difference + doy_difference + year_gap + C(State) + C(RunNumber)"
    f=smf.ols(formula,data=pairs).fit(
        cov_type="cluster",cov_kwds={"groups":pairs.route_cluster}
    )
    b=float(f.params["rain_contrast"]);se=float(f.bse["rain_contrast"]);p=float(f.pvalues["rain_contrast"])
    lo=b-Q*se;hi=b+Q*se
    return {
        "estimable":True,
        "n_pairs":int(len(pairs)),
        "n_routes":int(pairs.route_cluster.nunique()),
        "formula":formula,
        "beta_rain_contrast":b,
        "se_cluster":se,
        "ci95":[lo,hi],
        "p_value_two_sided":p,
        "negative_ci_support":bool(hi<0),
    }

def event_sensitivity(events: pd.DataFrame):
    if len(events)<100 or events.route_cluster.nunique()<20 or events.species.nunique()<5:
        return {"estimable":False,"n_events":int(len(events)),"reason":"insufficient_events_routes_or_species"}
    formula=(
        "wet_only ~ local_logit_prevalence + rain_contrast + "
        "local_logit_prevalence:rain_contrast + temp_difference + "
        "doy_difference + year_gap + C(species)"
    )
    try:
        f=smf.glm(formula,data=events,family=sm.families.Binomial()).fit(
            cov_type="cluster",cov_kwds={"groups":events.route_cluster},
            maxiter=200
        )
        out={
            "estimable":True,
            "n_events":int(len(events)),
            "n_pairs":int(events.pair_id.nunique()),
            "n_routes":int(events.route_cluster.nunique()),
            "n_species":int(events.species.nunique()),
            "formula":formula,
        }
        for term,label in [
            ("local_logit_prevalence","local_prevalence"),
            ("local_logit_prevalence:rain_contrast","prevalence_x_rain")
        ]:
            b=float(f.params[term]);se=float(f.bse[term]);p=float(f.pvalues[term])
            lo=b-Q*se;hi=b+Q*se
            out[label]={
                "beta":b,"se_cluster":se,"ci95":[lo,hi],
                "odds_ratio":math.exp(b),
                "ci95_or":[math.exp(lo),math.exp(hi)],
                "p_value_two_sided":p,
                "negative_ci_support":bool(hi<0)
            }
        return out
    except Exception as e:
        return {"estimable":False,"n_events":int(len(events)),"reason":repr(e)}

def descriptive_classes(events: pd.DataFrame):
    if len(events)==0:
        return {}
    tab=(events.groupby(["local_class","wet_only"]).size().unstack(fill_value=0))
    out={}
    for cls in ["satellite","intermediate","core"]:
        if cls not in tab.index:
            out[cls]={"wet_only":0,"dry_only":0,"wet_share":None}
            continue
        wet=int(tab.loc[cls].get(1,0));dry=int(tab.loc[cls].get(0,0))
        out[cls]={
            "wet_only":wet,"dry_only":dry,
            "wet_share":float(wet/(wet+dry)) if wet+dry>0 else None
        }
    return out

def background_summary(events: pd.DataFrame):
    if len(events)==0:
        return {}
    return {
        "events":int(len(events)),
        "pairs":int(events.pair_id.nunique()),
        "routes":int(events.route_cluster.nunique()),
        "species":int(events.species.nunique()),
        "background_runs_median":float(events.n_background.median()),
        "background_runs_min":int(events.n_background.min()),
        "background_runs_max":int(events.n_background.max()),
        "local_prevalence_median":float(events.local_prevalence.median()),
    }

def main():
    raw=base.load()
    runs,sets=base.build_runs(raw)
    pairs=base.pair_runs(runs,sets)

    events,prior_events=build_event_tables(runs,sets,pairs)
    paired=pair_level(events)
    prior_paired=pair_level(prior_events)

    result={
        "analysis":"naamp_local_satellite_recruitment_v0_1",
        "contract":"NAAMP_LOCAL_SATELLITE_RECRUITMENT_CONTRACT_V0_1.json",
        "eligible_runs":int(len(runs)),
        "matched_pairs_total":int(len(pairs)),
        "leave_pair_out_background":background_summary(events),
        "primary_pair_level":intercept_test(paired),
        "pulse_strength":pulse_strength_test(paired),
        "event_level_sensitivity":event_sensitivity(events),
        "prior_only_sensitivity":{
            "background":background_summary(prior_events),
            "primary_pair_level":intercept_test(prior_paired)
        },
        "descriptive_classes":descriptive_classes(events),
        "pair_level_descriptive":{
            "pairs_with_both_wet_and_dry_discordant_species":int(len(paired)),
            "delta_median":float(paired.delta_local_logit_prevalence.median()) if len(paired) else None,
            "fraction_delta_negative":float(np.mean(paired.delta_local_logit_prevalence<0)) if len(paired) else None,
        },
        "boundaries":{
            "local_prevalence":"Acoustic participation frequency in other runs at the same route and RunNumber; not occupancy probability.",
            "wet_only":"Does not imply colonization.",
            "dry_only":"Does not imply extinction.",
            "status":"Post-opening ecological mechanism follow-up frozen before local-prevalence readback.",
            "causal_claim_authorized":False
        }
    }
    Path("NAAMP_LOCAL_SATELLITE_RECRUITMENT_RECEIPT_V0_1.json").write_text(
        json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8"
    )
    print(json.dumps(result,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
