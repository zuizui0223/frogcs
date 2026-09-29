#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

ROOT=Path(__file__).resolve().parents[1]
NAAMP=ROOT/"scripts"/"naamp"
OUT=ROOT/"exploration"/"NAAMP_LATENT_SITE_REACTIVATION_RECEIPT_V0_1.json"
Q=1.959963984540054


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
    bad={k:v for k,v in vals.items() if len(v)>1}
    if bad:
        raise RuntimeError(f"multiple SiteIDs per run-stop: {list(bad)[:10]}")
    return {k:next(iter(v)) for k,v in vals.items() if v}


def fit(df,response):
    x=df[np.isfinite(pd.to_numeric(df[response],errors="coerce"))].copy()
    formula=(
        f"{response} ~ rain_contrast + temp_difference + doy_difference + "
        "year_gap + C(State) + C(RunNumber)"
    )
    m=smf.ols(formula,data=x).fit(
        cov_type="cluster",cov_kwds={"groups":x["route_cluster"]}
    )
    b=float(m.params["rain_contrast"]); se=float(m.bse["rain_contrast"])
    return {
        "response":response,
        "n_pairs":int(len(x)),
        "n_routes":int(x["route_cluster"].nunique()),
        "beta_rain_contrast":b,
        "se_cluster":se,
        "ci95":[b-Q*se,b+Q*se],
        "p_value":float(m.pvalues["rain_contrast"]),
    }


def main():
    raw=base.load()
    runs,route_sets=base.build_runs(raw)
    eligible=set(runs["RunID"].astype(str))
    sampled,stop_species=spatial.stop_matrix(raw,eligible)
    site=site_map(raw,eligible)
    pairs=base.pair_runs(runs,route_sets).copy().reset_index(drop=True)

    run_meta={
        str(r.RunID):{
            "key":(str(r.State),str(r.RouteNumber),str(r.RunNumber)),
            "route_key":(str(r.State),str(r.RouteNumber)),
            "year":int(r.SurveyYear),
        }
        for r in runs.itertuples(index=False)
    }
    strata_runs=defaultdict(list)
    route_runs=defaultdict(list)
    for rid,meta in run_meta.items():
        strata_runs[meta["key"]].append(rid)
        route_runs[meta["route_key"]].append(rid)

    # Exact physical-site species detections per run.
    run_site_species=defaultdict(set)
    for (rid,st),spp in stop_species.items():
        sid=site.get((rid,st))
        if sid:
            run_site_species[(rid,sid)].update(spp)

    # Index all species x SiteID detections by stratum and route to make
    # leave-pair-out recurrence checks independent of the focal endpoints.
    stratum_history=defaultdict(lambda:defaultdict(set))
    route_history=defaultdict(lambda:defaultdict(set))
    for (rid,sid),spp in run_site_species.items():
        meta=run_meta[rid]
        for sp in spp:
            stratum_history[meta["key"]][(sid,sp)].add(rid)
            route_history[meta["route_key"]][(sid,sp)].add(rid)

    rows=[]
    excluded_unstable=0
    event_counts=CounterLike()

    for p in pairs.itertuples(index=False):
        wet=str(p.wet_RunID); dry=str(p.dry_RunID)
        stops=sorted(sampled[wet])
        if len(stops)!=10 or set(stops)!=set(sampled[dry]):
            raise RuntimeError("stop-number alignment drift")

        # Exact physical stability.
        stable=True
        sids={}
        for st in stops:
            ws=site.get((wet,st)); ds=site.get((dry,st))
            if not ws or not ds or ws!=ds:
                stable=False
                break
            sids[st]=ws
        if not stable:
            excluded_unstable+=1
            continue

        W=set()
        D=set()
        for st in stops:
            W.update(stop_species.get((wet,st),set()))
            D.update(stop_species.get((dry,st),set()))

        key=(str(p.State),str(p.RouteNumber),str(p.RunNumber))
        route_key=(str(p.State),str(p.RouteNumber))
        focal={wet,dry}
        first_year=min(int(p.year_earlier),int(p.year_later))

        recurrent_gain=recurrent_loss=novel_gain=novel_loss=0
        prior_gain=prior_loss=0
        routeany_gain=routeany_loss=0
        total_gain=total_loss=0

        for st in stops:
            sid=sids[st]
            wset=set(stop_species.get((wet,st),set()))
            dset=set(stop_species.get((dry,st),set()))
            gains={sp for sp in (wset-dset) if sp not in D}
            losses={sp for sp in (dset-wset) if sp not in W}

            for sp in gains:
                total_gain+=1
                others=stratum_history[key].get((sid,sp),set())-focal
                recurrent=bool(others)
                if recurrent: recurrent_gain+=1
                else: novel_gain+=1
                prior=any(run_meta[r]["year"]<first_year for r in others)
                prior_gain+=int(prior)
                route_others=route_history[route_key].get((sid,sp),set())-focal
                routeany_gain+=int(bool(route_others))

            for sp in losses:
                total_loss+=1
                others=stratum_history[key].get((sid,sp),set())-focal
                recurrent=bool(others)
                if recurrent: recurrent_loss+=1
                else: novel_loss+=1
                prior=any(run_meta[r]["year"]<first_year for r in others)
                prior_loss+=int(prior)
                route_others=route_history[route_key].get((sid,sp),set())-focal
                routeany_loss+=int(bool(route_others))

        if recurrent_gain+novel_gain!=total_gain or recurrent_loss+novel_loss!=total_loss:
            raise RuntimeError("recurrence partition identity failed")

        row=p._asdict()
        row.update({
            "route_new_total_net":float(total_gain-total_loss),
            "recurrent_net":float(recurrent_gain-recurrent_loss),
            "novel_net":float(novel_gain-novel_loss),
            "prior_recurrent_net":float(prior_gain-prior_loss),
            "same_route_any_window_recurrent_net":float(routeany_gain-routeany_loss),
            "route_new_gain":int(total_gain),
            "route_new_loss":int(total_loss),
            "recurrent_gain":int(recurrent_gain),
            "recurrent_loss":int(recurrent_loss),
            "novel_gain":int(novel_gain),
            "novel_loss":int(novel_loss),
        })
        rows.append(row)

    df=pd.DataFrame(rows)
    if len(df)==0:
        raise RuntimeError("no stable pairs")

    if not np.allclose(
        df["route_new_total_net"].to_numpy(float),
        (df["recurrent_net"]+df["novel_net"]).to_numpy(float),
        atol=0,rtol=0,
    ):
        raise RuntimeError("pair-level route-new identity failed")

    primary={
        x:fit(df,x)
        for x in ("route_new_total_net","recurrent_net","novel_net")
    }
    total_b=primary["route_new_total_net"]["beta_rain_contrast"]
    rec_b=primary["recurrent_net"]["beta_rain_contrast"]
    nov_b=primary["novel_net"]["beta_rain_contrast"]
    beta_identity=float(total_b-rec_b-nov_b)
    share=float(rec_b/total_b) if abs(total_b)>1e-12 else None
    ci=primary["recurrent_net"]["ci95"]
    support=bool(
        total_b>0 and rec_b>0 and ci[0]>0
        and share is not None and share>0.5
        and rec_b>nov_b
    )

    prior=fit(df,"prior_recurrent_net")
    routeany=fit(df,"same_route_any_window_recurrent_net")
    exact={
        x:fit(df[df["year_gap"]==1].copy(),x)
        for x in ("route_new_total_net","recurrent_net","novel_net")
    }

    total_gain=int(df["route_new_gain"].sum())
    recurrent_gain=int(df["recurrent_gain"].sum())
    output={
        "analysis":"naamp_latent_site_reactivation_v0_1",
        "contract":"exploration/NAAMP_LATENT_SITE_REACTIVATION_CONTRACT_V0_1.json",
        "population":{
            "original_pairs":int(len(pairs)),
            "physically_stable_pairs":int(len(df)),
            "excluded_unstable_pairs":int(excluded_unstable),
            "routes":int(df["route_cluster"].nunique()),
        },
        "primary_models":primary,
        "identity":{
            "beta_identity_error":beta_identity,
            "recurrent_beta_share_of_route_new_total":share,
        },
        "classification":{
            "latent_site_reactivation_supported":support,
            "rule":"recurrent beta >0 with CI>0; recurrent beta share >0.5; recurrent beta > novel beta"
        },
        "descriptive":{
            "route_new_gain_events":total_gain,
            "recurrent_route_new_gain_events":recurrent_gain,
            "recurrent_fraction_of_route_new_gains":float(recurrent_gain/total_gain) if total_gain else None,
            "novel_route_new_gain_events":int(df["novel_gain"].sum()),
            "route_new_loss_events":int(df["route_new_loss"].sum()),
        },
        "sensitivity_prior_only":prior,
        "sensitivity_same_route_any_window":routeany,
        "exact_consecutive_year":exact,
        "interpretation_boundary":{
            "recurrent_means_repeated_acoustic_use_not_continuous_occupancy":True,
            "novel_means_never_observed_not_proven_ecological_novelty":True,
            "physiological_mechanism_identified":False,
            "causal_rainfall_claim":False,
            "submission_story_change_authorized":False,
        }
    }
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(output,indent=2,sort_keys=True)+"\n")
    print(json.dumps(output,indent=2,sort_keys=True))


class CounterLike:
    # Placeholder retained to make the event-count namespace explicit without
    # importing a second aggregation dependency; no endpoint depends on it.
    pass


if __name__=="__main__":
    main()
