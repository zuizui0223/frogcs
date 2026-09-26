#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
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

EARLY=set(range(2001,2008))
LATE=set(range(2008,2016))
Q=1.959963984540054

def baseline_local_history(d,sets):
    b=d[d["SurveyYear"].isin(EARLY)].copy()
    histories={}
    route_summary={}
    for route,g in b.groupby("route_cluster"):
        if len(g)<4:
            continue
        route=str(route)
        route_summary[route]={"eligible_runs":int(len(g))}
        species=set()
        for rid in g["RunID"]:
            species.update(sets.get(str(rid),set()))
        for sp in species:
            active=sum(sp in sets.get(str(rid),set()) for rid in g["RunID"])
            if active<1:
                continue
            inactive=len(g)-active
            recurrence=active/len(g)
            logit=float(np.log((active+0.5)/(inactive+0.5)))
            histories[(sp,route)]={
                "baseline_runs":int(len(g)),
                "baseline_active_runs":int(active),
                "baseline_recurrence":float(recurrence),
                "baseline_local_recurrence_logit":logit
            }
    return histories,route_summary

def validation_events(d,sets,histories):
    v=d[d["SurveyYear"].isin(LATE)].copy()
    pairs=base.pair_runs(v,sets)
    rows=[]
    all_wet=all_dry=known_wet=known_dry=0
    for r in pairs.itertuples(index=False):
        W=sets[str(r.wet_RunID)]
        D=sets[str(r.dry_RunID)]
        route=str(r.route_cluster)
        for sp in W-D:
            all_wet+=1
            h=histories.get((sp,route))
            if h is not None:
                known_wet+=1
                rows.append({
                    "y":1,"species":sp,"route_cluster":route,
                    "species_route":sp+"||"+route,
                    "RunNumber":str(r.RunNumber),
                    "year_gap":float(r.year_gap),
                    "rain_contrast":float(r.rain_contrast),
                    "temp_difference":float(r.temp_difference),
                    "doy_difference":float(r.doy_difference),
                    **h
                })
        for sp in D-W:
            all_dry+=1
            h=histories.get((sp,route))
            if h is not None:
                known_dry+=1
                rows.append({
                    "y":0,"species":sp,"route_cluster":route,
                    "species_route":sp+"||"+route,
                    "RunNumber":str(r.RunNumber),
                    "year_gap":float(r.year_gap),
                    "rain_contrast":float(r.rain_contrast),
                    "temp_difference":float(r.temp_difference),
                    "doy_difference":float(r.doy_difference),
                    **h
                })
    return v,pairs,pd.DataFrame(rows),{
        "all_wet_only_events":int(all_wet),
        "all_dry_only_events":int(all_dry),
        "baseline_known_wet_only_events":int(known_wet),
        "baseline_known_dry_only_events":int(known_dry),
        "baseline_known_fraction_wet_only":float(known_wet/all_wet) if all_wet else None,
        "baseline_known_fraction_dry_only":float(known_dry/all_dry) if all_dry else None
    }

def fit_primary(x):
    formula="y ~ baseline_local_recurrence_logit + rain_contrast + temp_difference + doy_difference + year_gap + C(species) + C(route_cluster) + C(RunNumber)"
    fit=smf.glm(formula,data=x,family=sm.families.Binomial()).fit(
        cov_type="cluster",cov_kwds={"groups":x["species_route"]}
    )
    term="baseline_local_recurrence_logit"
    b=float(fit.params[term]);se=float(fit.bse[term]);p=float(fit.pvalues[term])
    lo=b-Q*se;hi=b+Q*se
    return {
        "formula":formula,"n_events":int(len(x)),
        "n_species":int(x.species.nunique()),"n_routes":int(x.route_cluster.nunique()),
        "n_species_routes":int(x.species_route.nunique()),
        "beta":b,"se_cluster":se,"ci95_beta":[lo,hi],"p_value":p,
        "negative_ci_support":bool(hi<0)
    }

def fit_interaction(x):
    formula="y ~ baseline_local_recurrence_logit * rain_contrast + temp_difference + doy_difference + year_gap + C(species) + C(route_cluster) + C(RunNumber)"
    fit=smf.glm(formula,data=x,family=sm.families.Binomial()).fit(
        cov_type="cluster",cov_kwds={"groups":x["species_route"]}
    )
    term="baseline_local_recurrence_logit:rain_contrast"
    b=float(fit.params[term]);se=float(fit.bse[term]);p=float(fit.pvalues[term])
    lo=b-Q*se;hi=b+Q*se
    return {
        "formula":formula,"n_events":int(len(x)),
        "beta_interaction":b,"se_cluster":se,"ci95_beta":[lo,hi],"p_value":p,
        "negative_ci_support":bool(hi<0)
    }

def descriptives(x,coverage):
    wet=x[x.y==1]
    dry=x[x.y==0]
    return {
        **coverage,
        "modeled_events":int(len(x)),
        "modeled_wet_only":int((x.y==1).sum()),
        "modeled_dry_only":int((x.y==0).sum()),
        "modeled_species":int(x.species.nunique()),
        "modeled_routes":int(x.route_cluster.nunique()),
        "modeled_species_routes":int(x.species_route.nunique()),
        "median_baseline_recurrence_wet_only":float(wet.baseline_recurrence.median()) if len(wet) else None,
        "median_baseline_recurrence_dry_only":float(dry.baseline_recurrence.median()) if len(dry) else None,
        "mean_baseline_recurrence_wet_only":float(wet.baseline_recurrence.mean()) if len(wet) else None,
        "mean_baseline_recurrence_dry_only":float(dry.baseline_recurrence.mean()) if len(dry) else None
    }

def main():
    raw=base.load()
    d,sets=base.build_runs(raw)
    histories,route_summary=baseline_local_history(d,sets)
    v,pairs,x,coverage=validation_events(d,sets,histories)
    if len(x)==0:
        raise SystemExit("no baseline-known validation discordant events")

    primary=fit_primary(x)
    secondary=fit_interaction(x)

    exact=x[x["year_gap"]==1].copy()
    exact_primary=fit_primary(exact) if len(exact)>0 else None

    result={
        "analysis":"naamp_local_latent_recruitment_v0_1",
        "contract":"NAAMP_LOCAL_LATENT_RECRUITMENT_CONTRACT_V0_1.json",
        "time_split":{"baseline":[2001,2007],"validation":[2008,2015]},
        "baseline":{
            "eligible_routes":int(len(route_summary)),
            "species_route_histories":int(len(histories))
        },
        "validation":{
            "eligible_runs":int(len(v)),
            "matched_pairs":int(len(pairs))
        },
        "descriptives":descriptives(x,coverage),
        "primary_local_recurrence":primary,
        "secondary_recurrence_x_rain_contrast":secondary,
        "exact_consecutive_year_sensitivity":{
            "n_events":int(len(exact)),
            "primary_local_recurrence":exact_primary
        },
        "interpretation_boundary":{
            "baseline_uses_validation_years":False,
            "validation_uses_baseline_years":False,
            "baseline_known_means_continuous_occupancy":False,
            "wet_only_means_colonization":False,
            "causal_claim_authorized":False
        }
    }

    Path("NAAMP_LOCAL_LATENT_RECRUITMENT_RECEIPT_V0_1.json").write_text(
        json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8"
    )
    print(json.dumps(result,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
