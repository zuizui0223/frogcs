#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import io
import json
import math
import re
import urllib.request
from collections import Counter, defaultdict
from datetime import datetime
from itertools import combinations
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
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

def get_json(url):
    q=urllib.request.Request(url,headers={"User-Agent":"frogcs-review-repair/0.1","Accept":"application/json"})
    with urllib.request.urlopen(q,timeout=60) as r:
        return json.loads(r.read().decode("utf-8"))

def get_bytes(url):
    q=urllib.request.Request(url,headers={"User-Agent":"frogcs-review-repair/0.1"})
    with urllib.request.urlopen(q,timeout=120) as r:
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

def z(x):
    a=np.asarray(x,dtype=float)
    sd=float(np.nanstd(a,ddof=0))
    if not np.isfinite(sd) or sd==0:
        raise ValueError("invalid SD")
    return (a-float(np.nanmean(a)))/sd

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

def build(raw):
    audit_values=[]
    nonnumeric=Counter()
    runs={}
    for r in raw["Runs.csv"]:
        y=parse_year(r.get("SurveyYear")) or parse_year(r.get("SurveyDate"))
        if y is None or not 2001<=y<=2015:
            continue
        if (r.get("UnifiedProtocol") or "").strip()!="1":
            continue
        rid=(r.get("RunID") or "").strip()
        if not rid:
            continue
        raw_rain=(r.get("DaysSinceRain") or "").strip()
        try:
            rain=float(raw_rain)
            if np.isfinite(rain):
                audit_values.append(rain)
            else:
                nonnumeric["nonfinite"]+=1
                continue
        except Exception:
            nonnumeric[raw_rain or "<blank>"]+=1
            continue

        rn=(r.get("RunNumber") or "").strip()
        runs[rid]={
            "RunID":rid,
            "State":(r.get("State") or "").strip(),
            "RouteNumber":(r.get("RouteNumber") or "").strip(),
            "RouteType":(r.get("RouteType") or "").strip(),
            "RunNumber":rn,
            "SurveyYear":y,
            "SurveyDate":(r.get("SurveyDate") or "").strip(),
            "doy":parse_doy(r.get("SurveyDate")),
            "DaysSinceRain":rain,
            "TempScale":(r.get("TempScale") or "").strip(),
        }

    vals=np.asarray(audit_values,dtype=float)
    if len(vals)==0:
        raise RuntimeError("no numeric DaysSinceRain values")
    quantiles={str(q):float(np.quantile(vals,q)) for q in [0,0.001,0.01,0.05,0.25,0.5,0.75,0.95,0.99,0.999,1]}
    audit={
        "n_numeric":int(len(vals)),
        "min":float(vals.min()),
        "max":float(vals.max()),
        "quantiles":quantiles,
        "counts_at":{str(x):int(np.sum(vals==x)) for x in [0,30,60,90,120,180]},
        "counts_gt":{str(x):int(np.sum(vals>x)) for x in [30,60,90,120,180]},
        "numeric_out_of_documented_range":int(np.sum((vals<RAIN_LO)|(vals>RAIN_HI))),
        "nonnumeric_values":dict(sorted(nonnumeric.items())),
        "publisher_range":[RAIN_LO,RAIN_HI],
        "publisher_null_code":"Null",
    }

    if audit["numeric_out_of_documented_range"]>0:
        raise RuntimeError("DaysSinceRain numeric values outside documented [0,180] range")

    sampled=defaultdict(set)
    temps=defaultdict(list)
    for s in raw["Stops.csv"]:
        rid=(s.get("RunID") or "").strip()
        if rid not in runs:
            continue
        if (s.get("SkippedStop") or "").strip()!="0":
            continue
        stop=(s.get("StopNumber") or "").strip()
        if not stop:
            continue
        sampled[rid].add(stop)
        rawt=(s.get("AirTemp") or "").strip()
        if rawt:
            try:
                t=float(rawt)
                sc=runs[rid]["TempScale"]
                if sc=="F":
                    t=(t-32.0)*5.0/9.0
                elif sc!="C":
                    continue
                if np.isfinite(t):
                    temps[rid].append(t)
            except Exception:
                pass

    stop_species=defaultdict(set)
    for c in raw["Counts.csv"]:
        rid=(c.get("RunID") or "").strip()
        stop=(c.get("StopNumber") or "").strip()
        if rid not in sampled or stop not in sampled[rid]:
            continue
        if (c.get("CallingIndex") or "").strip() not in POS:
            continue
        sp=(c.get("Species") or "").strip()
        if sp:
            stop_species[(rid,stop)].add(sp)

    rows=[]
    for rid,r in runs.items():
        stops=sorted(sampled.get(rid,set()))
        if not stops:
            continue
        if not r["State"] or not r["RouteNumber"] or r["RunNumber"] not in {"1","2","3","4"}:
            continue
        multi=sum(len(stop_species.get((rid,s),set()))>=2 for s in stops)
        pool=set()
        for s in stops:
            pool.update(stop_species.get((rid,s),set()))
        ts=temps.get(rid,[])
        rows.append({
            **r,
            "trials":len(stops),
            "successes":multi,
            "pool_richness":len(pool),
            "n_temp_stops":len(ts),
            "mean_temp_c":float(np.mean(ts)) if ts else np.nan,
        })
    d=pd.DataFrame(rows)
    d["prop"]=d.successes/d.trials
    d["rain_z"]=z(np.log1p(d.DaysSinceRain.astype(float)))
    d["year_z"]=z(d.SurveyYear.astype(float))
    d["route_cluster"]=d.State.astype(str)+":"+d.RouteNumber.astype(str)

    state_last=(d.groupby("State")["RunNumber"].apply(lambda s:max(int(x) for x in s)).to_dict())
    d["state_last_window"]=d.State.map(state_last)
    d["shoulder"]=((d.RunNumber.astype(int)==1)|(d.RunNumber.astype(int)==d.state_last_window)).astype(int)

    # Add complete-run independence diagnostics.
    diag=[]
    for row in d.itertuples(index=False):
        if row.trials!=10:
            continue
        stops=sorted(sampled[row.RunID])
        pool=sorted({sp for s in stops for sp in stop_species.get((row.RunID,s),set())})
        if len(pool)<2:
            expected=np.nan
            pair_cov=np.nan
        else:
            counts={sp:sum(sp in stop_species.get((row.RunID,s),set()) for s in stops) for sp in pool}
            ps={sp:counts[sp]/10.0 for sp in pool}
            q0=1.0
            for sp in pool:
                q0*=1.0-ps[sp]
            q1=0.0
            for sp in pool:
                term=ps[sp]
                for other in pool:
                    if other!=sp:
                        term*=1.0-ps[other]
                q1+=term
            expected=max(0.0,min(1.0,1.0-q0-q1))

            covs=[]
            for a,b in combinations(pool,2):
                obs=sum((a in stop_species.get((row.RunID,s),set())) and (b in stop_species.get((row.RunID,s),set())) for s in stops)/10.0
                covs.append(obs-ps[a]*ps[b])
            pair_cov=float(np.mean(covs)) if covs else np.nan

        diag.append({
            "RunID":row.RunID,
            "expected_ge2_independence":expected,
            "observed_ge2":row.successes/10.0,
            "independence_residual":row.successes/10.0-expected if np.isfinite(expected) else np.nan,
            "pair_covariance_mean":pair_cov,
        })
    diag=pd.DataFrame(diag)
    d=d.merge(diag,on="RunID",how="left")
    return d,audit

def glm_interaction(d,formula):
    fit=smf.glm(formula,data=d,family=sm.families.Binomial(),freq_weights=d.trials.astype(float)).fit(
        cov_type="cluster",cov_kwds={"groups":d.route_cluster}
    )
    term="rain_z:shoulder"
    b=float(fit.params[term]); se=float(fit.bse[term]); p=float(fit.pvalues[term])
    q=1.959963984540054; lo=b-q*se; hi=b+q*se
    return {
        "n_runs":int(len(d)),"n_routes":int(d.route_cluster.nunique()),
        "formula":formula,"term":term,"beta":b,"se_cluster":se,
        "ci95_beta":[lo,hi],"odds_ratio":math.exp(b),"ci95_or":[math.exp(lo),math.exp(hi)],
        "p_value":p,"negative_ci_support":bool(hi<0)
    }

def ols_term(d,response,formula):
    fit=smf.ols(formula,data=d).fit(cov_type="cluster",cov_kwds={"groups":d.route_cluster})
    term="rain_z"
    b=float(fit.params[term]); se=float(fit.bse[term]); p=float(fit.pvalues[term])
    q=1.959963984540054; lo=b-q*se; hi=b+q*se
    return {
        "n_runs":int(len(d)),"n_routes":int(d.route_cluster.nunique()),
        "response":response,"formula":formula,"term":term,
        "beta":b,"se_cluster":se,"ci95_beta":[lo,hi],"p_value":p
    }

def main():
    d,audit=build(load())

    h=d[d.state_last_window.isin([3,4])].copy()
    h3_primary=glm_interaction(
        h,
        "prop ~ rain_z * shoulder + C(State) + C(RunNumber) + C(RouteType) + year_z"
    )
    h4=h[h.state_last_window==4].copy()
    h3_four=glm_interaction(
        h4,
        "prop ~ rain_z + rain_z:shoulder + C(State) + C(RunNumber) + C(RouteType) + year_z"
    )

    x=d[
        (d.trials==10) &
        (d.n_temp_stops>=8) &
        np.isfinite(d.mean_temp_c) &
        (d.mean_temp_c>=TEMP_LO) &
        (d.mean_temp_c<=TEMP_HI) &
        d.doy.notna()
    ].copy()
    x["temp_z"]=z(x.mean_temp_c)
    x["log1p_pool"]=np.log1p(x.pool_richness.astype(float))

    common="rain_z + temp_z + bs(doy, df=5, degree=3) + C(State) + C(RunNumber) + C(RouteType) + year_z"
    richness=ols_term(x,"log1p_pool","log1p_pool ~ "+common)

    n=x[(x.pool_richness>=2)&np.isfinite(x.independence_residual)].copy()
    residual=ols_term(n,"independence_residual","independence_residual ~ "+common)
    paircov=ols_term(n,"pair_covariance_mean","pair_covariance_mean ~ "+common)

    result={
        "analysis":"naamp_reviewer_repair_v0_1",
        "contract":"NAAMP_REVIEW_REPAIR_CONTRACT_V0_1.json",
        "sensitivity_repair_contract":"NAAMP_REVIEW_REPAIR_CONTRACT_V0_1_1.json",
        "days_since_rain_audit":audit,
        "h3_hierarchy_repair":{
            "hierarchy_corrected":h3_primary,
            "four_window_states_sensitivity":h3_four,
            "original_h3_decision":"not_supported",
            "original_h3_upgraded":False,
        },
        "active_pool_richness":richness,
        "independence_residual":residual,
        "pair_covariance_sensitivity":paircov,
        "diagnostic_subset":{
            "complete_plausible_temp_runs":int(len(x)),
            "runs_with_pool_ge2":int(len(n)),
            "pool_richness_summary":{
                "mean":float(x.pool_richness.mean()),
                "median":float(x.pool_richness.median()),
                "min":int(x.pool_richness.min()),
                "max":int(x.pool_richness.max()),
            },
            "observed_ge2_mean":float(n.observed_ge2.mean()),
            "expected_ge2_independence_mean":float(n.expected_ge2_independence.mean()),
            "independence_residual_mean":float(n.independence_residual.mean()),
        },
        "labels":{
            "pool_and_independence_diagnostics":"reviewer-motivated post-opening diagnostics",
            "h3":"specification repair of previously opened secondary endpoint"
        },
        "original_primary_replaced":False,
        "original_network_result_replaced":False,
        "causal_claim_authorized":False,
    }
    Path("frog_naamp_reviewer_repair_v0_1.json").write_text(
        json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8"
    )
    print(json.dumps(result,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
