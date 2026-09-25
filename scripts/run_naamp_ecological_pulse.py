#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import io
import json
import math
import re
import urllib.request
from collections import defaultdict
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

ITEM_ID="583dc314e4b0d1899f9dea8d"
ITEM_URL=f"https://www.sciencebase.gov/catalog/item/{ITEM_ID}?format=json"
PINS={
    "Runs.csv":"ec6b314fe4cd8ec8c048a973e576c8810ea12b21c739c1140e3a12123c611730",
    "Stops.csv":"28138cdaab43a56ecad8df3b523060c812edfad018c20c67b14581c569a84b0f",
    "Counts.csv":"60a3f6bc29402cd81fb01155923baaa07bccd172bce8b94fe1051d3ae25e7086",
}
POS={"1","2","3"}
TEMP_LO,TEMP_HI=-10.0,45.0
RAIN_LO,RAIN_HI=0.0,180.0
Q=1.959963984540054

def get_json(url):
    req=urllib.request.Request(url,headers={"User-Agent":"frogcs-ecological-pulse/0.1","Accept":"application/json"})
    with urllib.request.urlopen(req,timeout=60) as r:
        return json.loads(r.read().decode("utf-8"))

def get_bytes(url):
    req=urllib.request.Request(url,headers={"User-Agent":"frogcs-ecological-pulse/0.1"})
    with urllib.request.urlopen(req,timeout=120) as r:
        return r.read()

def file_url(f):
    return f.get("downloadUri") or f.get("url") or f.get("uri")

def find_file(item,name):
    for f in item.get("files") or []:
        if (f.get("name") or "")==name:
            return file_url(f)
    raise RuntimeError(f"missing {name}")

def parse_year(x):
    m=re.search(r"(?<!\d)((?:19|20)\d{2})(?!\d)",str(x or ""))
    return int(m.group(1)) if m else None

def parse_doy(x):
    s=str(x or "").strip()
    for fmt in ("%m/%d/%Y","%m/%d/%y","%Y-%m-%d","%Y/%m/%d"):
        try:
            return datetime.strptime(s,fmt).timetuple().tm_yday
        except Exception:
            pass
    return None

def load():
    item=get_json(ITEM_URL)
    out={}
    for name,sha in PINS.items():
        b=get_bytes(find_file(item,name))
        got=hashlib.sha256(b).hexdigest()
        if got!=sha:
            raise RuntimeError(f"hash drift {name}: {got}")
        out[name]=list(csv.DictReader(io.StringIO(b.decode("utf-8-sig"))))
    return out

def build_runs(raw):
    runs={}
    for r in raw["Runs.csv"]:
        y=parse_year(r.get("SurveyYear")) or parse_year(r.get("SurveyDate"))
        d=parse_doy(r.get("SurveyDate"))
        if y is None or d is None or not 2001<=y<=2015:
            continue
        if (r.get("UnifiedProtocol") or "").strip()!="1":
            continue
        rid=(r.get("RunID") or "").strip()
        rn=(r.get("RunNumber") or "").strip()
        state=(r.get("State") or "").strip()
        route=(r.get("RouteNumber") or "").strip()
        rtype=(r.get("RouteType") or "").strip()
        if not rid or rn not in {"1","2","3","4"} or not state or not route or not rtype:
            continue
        try:
            rain=float((r.get("DaysSinceRain") or "").strip())
        except Exception:
            continue
        if not math.isfinite(rain) or not RAIN_LO<=rain<=RAIN_HI:
            continue
        runs[rid]={
            "RunID":rid,"State":state,"RouteNumber":route,"RouteType":rtype,
            "RunNumber":rn,"SurveyYear":y,"doy":d,"DaysSinceRain":rain,
            "TempScale":(r.get("TempScale") or "").strip()
        }

    sampled=defaultdict(set)
    temps=defaultdict(list)
    for s in raw["Stops.csv"]:
        rid=(s.get("RunID") or "").strip()
        if rid not in runs or (s.get("SkippedStop") or "").strip()!="0":
            continue
        st=(s.get("StopNumber") or "").strip()
        if not st:
            continue
        sampled[rid].add(st)
        try:
            t=float((s.get("AirTemp") or "").strip())
        except Exception:
            continue
        scale=runs[rid]["TempScale"]
        if scale=="F":
            t=(t-32.0)*5.0/9.0
        elif scale!="C":
            continue
        if np.isfinite(t):
            temps[rid].append(t)

    stop_species=defaultdict(set)
    for c in raw["Counts.csv"]:
        rid=(c.get("RunID") or "").strip()
        st=(c.get("StopNumber") or "").strip()
        if rid not in sampled or st not in sampled[rid]:
            continue
        if (c.get("CallingIndex") or "").strip() not in POS:
            continue
        sp=(c.get("Species") or "").strip()
        if sp:
            stop_species[(rid,st)].add(sp)

    rows=[]
    species_sets={}
    for rid,r in runs.items():
        stops=sorted(sampled.get(rid,set()))
        ts=temps.get(rid,[])
        if len(stops)!=10 or len(ts)<8:
            continue
        mt=float(np.mean(ts))
        if not TEMP_LO<=mt<=TEMP_HI:
            continue
        spp=set()
        for st in stops:
            spp.update(stop_species.get((rid,st),set()))
        species_sets[rid]=spp
        rows.append({**r,"mean_temp_c":mt,"richness":len(spp),"route_cluster":r["State"]+":"+r["RouteNumber"]})

    return pd.DataFrame(rows),species_sets

def pair_runs(d,species_sets):
    rows=[]
    for _,g in d.groupby(["State","RouteNumber","RunNumber"],sort=False):
        g=g.sort_values(["SurveyYear","RunID"]).reset_index(drop=True)
        for i in range(len(g)-1):
            a=g.iloc[i]
            b=g.iloc[i+1]
            if a.DaysSinceRain==b.DaysSinceRain:
                continue
            if a.DaysSinceRain < b.DaysSinceRain:
                wet,dry=a,b
            else:
                wet,dry=b,a

            W=species_sets[str(wet.RunID)]
            D=species_sets[str(dry.RunID)]
            shared=len(W & D)
            wet_only=len(W-D)
            dry_only=len(D-W)
            denom_s=2*shared+wet_only+dry_only
            sorensen=((wet_only+dry_only)/denom_s) if denom_s>0 else np.nan

            mn=min(wet_only,dry_only)
            denom_t=shared+mn
            if denom_t>0:
                turnover=mn/denom_t
            elif (wet_only+dry_only)>0:
                turnover=0.0
            else:
                turnover=np.nan
            nestedness=(sorensen-turnover) if np.isfinite(sorensen) and np.isfinite(turnover) else np.nan

            discordant=wet_only+dry_only
            gain_share=wet_only/discordant if discordant>0 else np.nan
            dry_rich=shared+dry_only
            dry_retention=shared/dry_rich if dry_rich>0 else np.nan

            rows.append({
                "State":wet.State,
                "RouteNumber":wet.RouteNumber,
                "RunNumber":wet.RunNumber,
                "route_cluster":wet.route_cluster,
                "year_earlier":int(min(a.SurveyYear,b.SurveyYear)),
                "year_later":int(max(a.SurveyYear,b.SurveyYear)),
                "year_gap":int(abs(a.SurveyYear-b.SurveyYear)),
                "wet_RunID":wet.RunID,
                "dry_RunID":dry.RunID,
                "wet_days_since_rain":float(wet.DaysSinceRain),
                "dry_days_since_rain":float(dry.DaysSinceRain),
                "rain_contrast":float(np.log1p(dry.DaysSinceRain)-np.log1p(wet.DaysSinceRain)),
                "temp_difference":float(wet.mean_temp_c-dry.mean_temp_c),
                "doy_difference":float(wet.doy-dry.doy),
                "wet_richness":int(len(W)),
                "dry_richness":int(len(D)),
                "richness_gain":int(len(W)-len(D)),
                "shared":shared,
                "wet_only":wet_only,
                "dry_only":dry_only,
                "discordant":discordant,
                "sorensen_dissimilarity":sorensen,
                "simpson_turnover":turnover,
                "nestedness_component":nestedness,
                "gain_share":gain_share,
                "dry_core_retention":dry_retention
            })
    return pd.DataFrame(rows)

def fit_ols(d,response):
    x=d[np.isfinite(d[response])].copy()
    formula=f"{response} ~ rain_contrast + temp_difference + doy_difference + year_gap + C(State) + C(RunNumber)"
    f=smf.ols(formula,data=x).fit(cov_type="cluster",cov_kwds={"groups":x.route_cluster})
    b=float(f.params["rain_contrast"]);se=float(f.bse["rain_contrast"]);p=float(f.pvalues["rain_contrast"])
    lo=b-Q*se;hi=b+Q*se
    return {
        "response":response,"formula":formula,"n_pairs":int(len(x)),
        "n_routes":int(x.route_cluster.nunique()),
        "beta_rain_contrast":b,"se_cluster":se,"ci95_beta":[lo,hi],"p_value":p
    }

def summaries(pairs):
    return {
        "n_pairs":int(len(pairs)),
        "n_routes":int(pairs.route_cluster.nunique()),
        "n_states":int(pairs.State.nunique()),
        "year_gap":{
            "mean":float(pairs.year_gap.mean()),
            "median":float(pairs.year_gap.median()),
            "fraction_exactly_1":float(np.mean(pairs.year_gap==1))
        },
        "rain_contrast":{
            "mean":float(pairs.rain_contrast.mean()),
            "median":float(pairs.rain_contrast.median()),
            "q95":float(pairs.rain_contrast.quantile(.95))
        },
        "richness":{
            "wet_mean":float(pairs.wet_richness.mean()),
            "dry_mean":float(pairs.dry_richness.mean()),
            "mean_gain":float(pairs.richness_gain.mean()),
            "median_gain":float(pairs.richness_gain.median())
        },
        "composition":{
            "total_wet_only":int(pairs.wet_only.sum()),
            "total_dry_only":int(pairs.dry_only.sum()),
            "overall_gain_share":float(pairs.wet_only.sum()/(pairs.wet_only.sum()+pairs.dry_only.sum())) if (pairs.wet_only.sum()+pairs.dry_only.sum())>0 else None,
            "mean_pair_gain_share":float(pairs.gain_share.mean()),
            "median_pair_gain_share":float(pairs.gain_share.median()),
            "mean_dry_core_retention":float(pairs.dry_core_retention.mean()),
            "median_dry_core_retention":float(pairs.dry_core_retention.median()),
            "mean_sorensen":float(pairs.sorensen_dissimilarity.mean()),
            "mean_turnover":float(pairs.simpson_turnover.mean()),
            "mean_nestedness":float(pairs.nestedness_component.mean())
        }
    }

def main():
    d,sets=build_runs(load())
    pairs=pair_runs(d,sets)
    if len(pairs)==0:
        raise RuntimeError("no eligible pairs")

    primary={
        "richness_gain":fit_ols(pairs,"richness_gain"),
        "nestedness_component":fit_ols(pairs,"nestedness_component"),
        "simpson_turnover":fit_ols(pairs,"simpson_turnover")
    }

    exact=pairs[pairs.year_gap==1].copy()
    sensitivity={
        "n_pairs":int(len(exact)),
        "richness_gain":fit_ols(exact,"richness_gain") if len(exact)>0 else None,
        "nestedness_component":fit_ols(exact,"nestedness_component") if len(exact)>0 else None,
        "simpson_turnover":fit_ols(exact,"simpson_turnover") if len(exact)>0 else None
    }

    result={
        "analysis":"naamp_pulse_nested_recruitment_v0_1",
        "contract":"NAAMP_ECOLOGICAL_PULSE_CONTRACT_V0_1.json",
        "eligible_runs":int(len(d)),
        "primary_pair_summary":summaries(pairs),
        "primary_models":primary,
        "exact_consecutive_year_sensitivity":sensitivity,
        "interpretation_boundary":{
            "acoustic_activity":"Active species composition reflects calling activity, not abundance or breeding success.",
            "causality":"No causal rainfall claim.",
            "status":"Post-opening ecological extension frozen before its own effect readback."
        }
    }

    Path("NAAMP_ECOLOGICAL_PULSE_RECEIPT_V0_1.json").write_text(
        json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8"
    )
    print(json.dumps(result,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
