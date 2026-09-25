#!/usr/bin/env python3
from __future__ import annotations

import csv, hashlib, io, json, math, re, urllib.request
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
RAIN_LO,RAIN_HI=0.0,180.0
TEMP_LO,TEMP_HI=-10.0,45.0
Q=1.959963984540054

def get_json(url):
    req=urllib.request.Request(url,headers={"User-Agent":"frogcs-review-repair/0.1","Accept":"application/json"})
    with urllib.request.urlopen(req,timeout=60) as r:
        return json.loads(r.read().decode("utf-8"))

def get_bytes(url):
    req=urllib.request.Request(url,headers={"User-Agent":"frogcs-review-repair/0.1"})
    with urllib.request.urlopen(req,timeout=120) as r:
        return r.read()

def file_url(f):
    return f.get("downloadUri") or f.get("url") or f.get("uri")

def find_file(item,name):
    for f in item.get("files") or []:
        if (f.get("name") or "")==name:
            return file_url(f)
    raise RuntimeError(f"missing {name}")

def year(x):
    m=re.search(r"(?<!\d)((?:19|20)\d{2})(?!\d)",str(x or ""))
    return int(m.group(1)) if m else None

def doy(x):
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

def audit_days_since_rain(raw):
    vals=[]
    nonnumeric=Counter()
    blank=0
    eligible=0
    for r in raw["Runs.csv"]:
        y=year(r.get("SurveyYear")) or year(r.get("SurveyDate"))
        if y is None or not 2001<=y<=2015:
            continue
        if (r.get("UnifiedProtocol") or "").strip()!="1":
            continue
        eligible+=1
        s=(r.get("DaysSinceRain") or "").strip()
        if not s:
            blank+=1
            continue
        try:
            v=float(s)
        except Exception:
            nonnumeric[s]+=1
            continue
        if math.isfinite(v):
            vals.append(v)
        else:
            nonnumeric[s]+=1

    a=np.asarray(vals,float)
    out_of_range=int(((a<RAIN_LO)|(a>RAIN_HI)).sum()) if len(a) else 0
    qs={str(q):float(np.quantile(a,q)) for q in [0,0.001,0.01,0.05,0.25,0.5,0.75,0.95,0.99,0.999,1]} if len(a) else {}
    exact={str(t):int(np.isclose(a,t).sum()) for t in [0,30,60,90,120,180]}
    gt={str(t):int((a>t).sum()) for t in [30,60,90,120,180]}
    return {
        "eligible_unified_runs":eligible,
        "numeric_values":int(len(a)),
        "blank_values":blank,
        "nonnumeric_values":dict(sorted(nonnumeric.items())),
        "publisher_documented_range_days":[RAIN_LO,RAIN_HI],
        "numeric_out_of_range":out_of_range,
        "min":float(a.min()) if len(a) else None,
        "max":float(a.max()) if len(a) else None,
        "quantiles":qs,
        "counts_at":exact,
        "counts_gt":gt,
        "pass":bool(out_of_range==0),
    }

def build_frames(raw):
    runs={}
    for r in raw["Runs.csv"]:
        y=year(r.get("SurveyYear")) or year(r.get("SurveyDate"))
        d=doy(r.get("SurveyDate"))
        if y is None or d is None or not 2001<=y<=2015:
            continue
        if (r.get("UnifiedProtocol") or "").strip()!="1":
            continue
        rid=(r.get("RunID") or "").strip()
        rn=(r.get("RunNumber") or "").strip()
        if not rid or rn not in {"1","2","3","4"}:
            continue
        s=(r.get("DaysSinceRain") or "").strip()
        try:
            rain=float(s)
        except Exception:
            continue
        if not math.isfinite(rain) or not RAIN_LO<=rain<=RAIN_HI:
            continue
        runs[rid]={
            "RunID":rid,
            "State":(r.get("State") or "").strip(),
            "RouteNumber":(r.get("RouteNumber") or "").strip(),
            "RouteType":(r.get("RouteType") or "").strip(),
            "RunNumber":rn,
            "SurveyYear":y,
            "DaysSinceRain":rain,
            "TempScale":(r.get("TempScale") or "").strip(),
            "doy":d,
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
        rawt=(s.get("AirTemp") or "").strip()
        try:
            t=float(rawt)
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
    for rid,r in runs.items():
        stops=sampled.get(rid,set())
        if not stops or not r["State"] or not r["RouteNumber"] or not r["RouteType"]:
            continue
        active=0
        multi=0
        pool=set()
        species_stop_counts=Counter()
        pair_stop_counts=Counter()
        for st in stops:
            ss=stop_species.get((rid,st),set())
            if len(ss)>=1:
                active+=1
            if len(ss)>=2:
                multi+=1
            pool.update(ss)
            for sp in ss:
                species_stop_counts[sp]+=1
            for pair in combinations(sorted(ss),2):
                pair_stop_counts[pair]+=1
        ts=temps.get(rid,[])
        rows.append({
            **r,
            "trials":len(stops),
            "active":active,
            "multi":multi,
            "pool_richness":len(pool),
            "mean_temp_c":float(np.mean(ts)) if len(ts) else np.nan,
            "n_temp_stops":len(ts),
            "_species_stop_counts":dict(species_stop_counts),
            "_pair_stop_counts":{"||".join(k):v for k,v in pair_stop_counts.items()},
        })

    d=pd.DataFrame(rows)
    d["prop"]=d["multi"]/d["trials"]
    d["rain_z"]=z(np.log1p(d["DaysSinceRain"].astype(float)))
    d["year_z"]=z(d["SurveyYear"].astype(float))
    d["route_cluster"]=d["State"].astype(str)+":"+d["RouteNumber"].astype(str)

    state_last=(d.groupby("State")["RunNumber"]
                  .apply(lambda s:max(int(x) for x in s if str(x) in {"1","2","3","4"}))
                  .to_dict())
    d["state_last_window"]=d["State"].map(state_last)
    d["shoulder"]=((d["RunNumber"].astype(int)==1) |
                    (d["RunNumber"].astype(int)==d["state_last_window"])).astype(int)

    complete=d[
        (d["trials"]==10) &
        (d["n_temp_stops"]>=8) &
        np.isfinite(d["mean_temp_c"]) &
        (d["mean_temp_c"]>=TEMP_LO) &
        (d["mean_temp_c"]<=TEMP_HI)
    ].copy()
    complete["temp_z"]=z(complete["mean_temp_c"].astype(float))
    complete["log1p_pool"]=np.log1p(complete["pool_richness"].astype(float))

    obs=[]
    exp=[]
    pair_cov=[]
    for r in complete.itertuples(index=False):
        counts=getattr(r,"_species_stop_counts")
        ps=[float(v)/10.0 for v in counts.values()]
        observed=float(r.multi)/10.0
        if len(ps)>=2:
            p0=float(np.prod([1.0-p for p in ps]))
            p1=0.0
            for i,p in enumerate(ps):
                p1+=p*float(np.prod([1.0-q for j,q in enumerate(ps) if j!=i]))
            expected=1.0-p0-p1
        else:
            expected=0.0
        obs.append(observed); exp.append(expected)

        if len(ps)>=2:
            vals=[]
            keys=sorted(counts)
            pair_counts=getattr(r,"_pair_stop_counts")
            for a,b in combinations(keys,2):
                observed_pair=float(pair_counts.get(a+"||"+b,0))/10.0
                pa=float(counts[a])/10.0; pb=float(counts[b])/10.0
                vals.append(observed_pair-pa*pb)
            pair_cov.append(float(np.mean(vals)) if vals else np.nan)
        else:
            pair_cov.append(np.nan)

    complete["observed_multi_prob"]=obs
    complete["independence_expected_multi_prob"]=exp
    complete["independence_residual"]=complete["observed_multi_prob"]-complete["independence_expected_multi_prob"]
    complete["pair_covariance_mean"]=pair_cov
    return d,complete

def glm_term(d,formula,term,weight_col):
    m=smf.glm(formula,data=d,family=sm.families.Binomial(),freq_weights=d[weight_col].astype(float))
    f=m.fit(cov_type="cluster",cov_kwds={"groups":d["route_cluster"]})
    b=float(f.params[term]); se=float(f.bse[term]); p=float(f.pvalues[term])
    lo=b-Q*se; hi=b+Q*se
    return {
        "n_runs":int(len(d)),"n_routes":int(d.route_cluster.nunique()),
        "term":term,"beta":b,"se_cluster":se,"ci95_beta":[lo,hi],
        "odds_ratio":math.exp(b),"ci95_or":[math.exp(lo),math.exp(hi)],"p_value":p
    }

def ols_term(d,formula,term):
    f=smf.ols(formula,data=d).fit(cov_type="cluster",cov_kwds={"groups":d["route_cluster"]})
    b=float(f.params[term]); se=float(f.bse[term]); p=float(f.pvalues[term])
    lo=b-Q*se; hi=b+Q*se
    return {
        "n_runs":int(len(d)),"n_routes":int(d.route_cluster.nunique()),
        "term":term,"beta":b,"se_cluster":se,"ci95_beta":[lo,hi],"p_value":p
    }

def main():
    raw=load()
    audit=audit_days_since_rain(raw)
    if not audit["pass"]:
        raise RuntimeError("DaysSinceRain contains numeric values outside publisher-documented [0,180] range")

    all_runs,complete=build_frames(raw)

    h=all_runs[all_runs["state_last_window"].isin([3,4])].copy()
    h3_primary=glm_term(
        h,
        "prop ~ rain_z * shoulder + C(State) + C(RunNumber) + C(RouteType) + year_z",
        "rain_z:shoulder",
        "trials",
    )
    h3_sensitivity=glm_term(
        h,
        "prop ~ rain_z + rain_z:shoulder + C(State) * C(RunNumber) + C(RouteType) + year_z",
        "rain_z:shoulder",
        "trials",
    )

    pool=ols_term(
        complete,
        "log1p_pool ~ rain_z + temp_z + bs(doy, df=5, degree=3) + C(State) + C(RunNumber) + C(RouteType) + year_z",
        "rain_z",
    )

    indep=complete[complete["pool_richness"]>=2].copy()
    independence=ols_term(
        indep,
        "independence_residual ~ rain_z + temp_z + bs(doy, df=5, degree=3) + C(State) + C(RunNumber) + C(RouteType) + year_z",
        "rain_z",
    )
    pair=indep[np.isfinite(indep["pair_covariance_mean"])].copy()
    pair_sensitivity=ols_term(
        pair,
        "pair_covariance_mean ~ rain_z + temp_z + bs(doy, df=5, degree=3) + C(State) + C(RunNumber) + C(RouteType) + year_z",
        "rain_z",
    )

    result={
        "analysis":"naamp_review_repairs_v0_1",
        "contract":"NAAMP_REVIEW_REPAIR_CONTRACT_V0_1.json",
        "days_since_rain_audit":audit,
        "h3_hierarchy_repair":{
            "primary_with_shoulder_main_effect":h3_primary,
            "state_by_runwindow_sensitivity":h3_sensitivity,
            "retrospective_status":"repair_only_original_H3_decision_not_upgraded"
        },
        "active_pool_richness":{
            "response":"log1p distinct positively calling species across a complete 10-stop run",
            "complete_runs":int(len(complete)),
            "pool_richness_summary":{
                "mean":float(complete["pool_richness"].mean()),
                "median":float(complete["pool_richness"].median()),
                "min":int(complete["pool_richness"].min()),
                "max":int(complete["pool_richness"].max()),
            },
            "rain_effect":pool,
        },
        "independence_residual":{
            "definition":"observed P(>=2 calling species) minus plug-in independence expectation from species-specific marginal stop frequencies within the same run",
            "rain_effect":independence,
            "pair_covariance_sensitivity":pair_sensitivity,
            "observed_mean":float(indep["observed_multi_prob"].mean()),
            "expected_mean":float(indep["independence_expected_multi_prob"].mean()),
            "residual_mean":float(indep["independence_residual"].mean()),
        },
        "original_primary_replaced":False,
        "original_network_result_replaced":False,
        "causal_claim_authorized":False,
        "diagnostic_status":"reviewer_motivated_post_primary"
    }

    Path("NAAMP_REVIEW_REPAIRS_RECEIPT_V0_1.json").write_text(
        json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8"
    )
    print(json.dumps(result,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
