#!/usr/bin/env python3
from __future__ import annotations

import csv, hashlib, io, json, math, re, urllib.request
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
B=1024
Q=1.959963984540054

def get_json(url):
    req=urllib.request.Request(url,headers={"User-Agent":"frogcs-shuffle-null/0.1","Accept":"application/json"})
    with urllib.request.urlopen(req,timeout=60) as r:
        return json.loads(r.read().decode("utf-8"))

def get_bytes(url):
    req=urllib.request.Request(url,headers={"User-Agent":"frogcs-shuffle-null/0.1"})
    with urllib.request.urlopen(req,timeout=120) as r:
        return r.read()

def file_url(f):
    return f.get("downloadUri") or f.get("url") or f.get("uri")

def find_file(item,name):
    for f in item.get("files") or []:
        if (f.get("name") or "")==name:
            return file_url(f)
    raise RuntimeError(name)

def year(x):
    m=re.search(r"(?<!\d)((?:19|20)\d{2})(?!\d)",str(x or ""))
    return int(m.group(1)) if m else None

def doy(x):
    s=str(x or "").strip()
    for fmt in ("%m/%d/%Y","%m/%d/%y","%Y-%m-%d","%Y/%m/%d"):
        try:return datetime.strptime(s,fmt).timetuple().tm_yday
        except Exception:pass
    return None

def z(x):
    a=np.asarray(x,float)
    sd=float(np.nanstd(a,ddof=0))
    if not np.isfinite(sd) or sd==0:
        raise RuntimeError("invalid SD")
    return (a-float(np.nanmean(a)))/sd

def load():
    item=get_json(ITEM_URL); out={}
    for name,sha in PINS.items():
        b=get_bytes(find_file(item,name))
        if hashlib.sha256(b).hexdigest()!=sha:
            raise RuntimeError("hash drift "+name)
        out[name]=list(csv.DictReader(io.StringIO(b.decode("utf-8-sig"))))
    return out

def build(raw):
    runs={}
    for r in raw["Runs.csv"]:
        y=year(r.get("SurveyYear")) or year(r.get("SurveyDate"))
        d=doy(r.get("SurveyDate"))
        if y is None or d is None or not 2001<=y<=2015: continue
        if (r.get("UnifiedProtocol") or "").strip()!="1": continue
        rid=(r.get("RunID") or "").strip()
        rn=(r.get("RunNumber") or "").strip()
        if not rid or rn not in {"1","2","3","4"}: continue
        try: rain=float((r.get("DaysSinceRain") or "").strip())
        except Exception: continue
        if not math.isfinite(rain) or rain<0 or rain>180: continue
        runs[rid]={
            "RunID":rid,"State":(r.get("State") or "").strip(),
            "RouteNumber":(r.get("RouteNumber") or "").strip(),
            "RouteType":(r.get("RouteType") or "").strip(),
            "RunNumber":rn,"SurveyYear":y,"DaysSinceRain":rain,
            "TempScale":(r.get("TempScale") or "").strip(),"doy":d,
        }

    sampled=defaultdict(set); temps=defaultdict(list)
    for s in raw["Stops.csv"]:
        rid=(s.get("RunID") or "").strip()
        if rid not in runs or (s.get("SkippedStop") or "").strip()!="0": continue
        st=(s.get("StopNumber") or "").strip()
        if not st: continue
        sampled[rid].add(st)
        try:t=float((s.get("AirTemp") or "").strip())
        except Exception:continue
        sc=runs[rid]["TempScale"]
        if sc=="F":t=(t-32.0)*5.0/9.0
        elif sc!="C":continue
        if np.isfinite(t):temps[rid].append(t)

    stop_species=defaultdict(set)
    for c in raw["Counts.csv"]:
        rid=(c.get("RunID") or "").strip(); st=(c.get("StopNumber") or "").strip()
        if rid not in sampled or st not in sampled[rid]: continue
        if (c.get("CallingIndex") or "").strip() not in POS: continue
        sp=(c.get("Species") or "").strip()
        if sp:stop_species[(rid,st)].add(sp)

    rows=[]; matrices={}
    for rid,r in runs.items():
        stops=sorted(sampled.get(rid,set()))
        ts=temps.get(rid,[])
        if len(stops)!=10 or len(ts)<8 or not r["State"] or not r["RouteNumber"] or not r["RouteType"]: continue
        mt=float(np.mean(ts))
        if not TEMP_LO<=mt<=TEMP_HI: continue
        pool=sorted({sp for st in stops for sp in stop_species.get((rid,st),set())})
        if len(pool)<2: continue
        X=np.zeros((len(pool),10),dtype=np.uint8)
        for i,sp in enumerate(pool):
            for j,st in enumerate(stops):
                X[i,j]=int(sp in stop_species.get((rid,st),set()))
        observed=float(np.mean(X.sum(axis=0)>=2))
        rows.append({**r,"mean_temp_c":mt,"pool_richness":len(pool),"observed_multi":observed})
        matrices[rid]=X

    d=pd.DataFrame(rows)
    d["rain_z"]=z(np.log1p(d.DaysSinceRain.astype(float)))
    d["temp_z"]=z(d.mean_temp_c.astype(float))
    d["year_z"]=z(d.SurveyYear.astype(float))
    d["route_cluster"]=d.State.astype(str)+":"+d.RouteNumber.astype(str)
    return d,matrices

def run_shuffle(rid,X):
    seed=int.from_bytes(hashlib.sha256(("frogcs-shuffle-v0.1|"+rid).encode()).digest()[:8],"big")
    rng=np.random.default_rng(seed)
    occ=np.zeros((B,10),dtype=np.uint16)
    for row in X:
        k=int(row.sum())
        if k<=0: continue
        if k>=10:
            occ+=1
            continue
        keys=rng.random((B,10))
        idx=np.argpartition(keys,k-1,axis=1)[:,:k]
        rr=np.arange(B)[:,None]
        chosen=np.zeros((B,10),dtype=np.uint8)
        chosen[rr,idx]=1
        occ+=chosen
    stat=np.mean(occ>=2,axis=1)
    mean=float(stat.mean())
    sd=float(stat.std(ddof=1))
    return mean,sd

def fit(d):
    formula="shuffle_residual ~ rain_z + temp_z + bs(doy, df=5, degree=3) + C(State) + C(RunNumber) + C(RouteType) + year_z"
    f=smf.ols(formula,data=d).fit(cov_type="cluster",cov_kwds={"groups":d.route_cluster})
    b=float(f.params["rain_z"]);se=float(f.bse["rain_z"]);p=float(f.pvalues["rain_z"])
    lo=b-Q*se;hi=b+Q*se
    return {"formula":formula,"n_runs":int(len(d)),"n_routes":int(d.route_cluster.nunique()),
            "beta_rain_z":b,"se_cluster":se,"ci95_beta":[lo,hi],"p_value":p}

def main():
    d,matrices=build(load())
    means=[];sds=[]
    for r in d.itertuples(index=False):
        m,s=run_shuffle(str(r.RunID),matrices[str(r.RunID)])
        means.append(m);sds.append(s)
    d["shuffle_mean"]=means; d["shuffle_sd"]=sds
    d["shuffle_residual"]=d.observed_multi-d.shuffle_mean
    d["shuffle_z"]=np.where(d.shuffle_sd>0,d.shuffle_residual/d.shuffle_sd,np.nan)

    result={
      "analysis":"naamp_fixed_marginal_shuffle_null_v0_1",
      "contract":"NAAMP_SHUFFLE_NULL_CONTRACT_V0_1.json",
      "permutations_per_run":B,
      "subset":{"n_runs":int(len(d)),"n_routes":int(d.route_cluster.nunique()),
                "pool_richness_mean":float(d.pool_richness.mean()),
                "observed_multi_mean":float(d.observed_multi.mean()),
                "shuffle_mean_mean":float(d.shuffle_mean.mean()),
                "shuffle_residual_mean":float(d.shuffle_residual.mean()),
                "shuffle_sd_median":float(d.shuffle_sd.median())},
      "rain_effect_on_shuffle_residual":fit(d),
      "standardized_excess_summary":{
          "mean":float(np.nanmean(d.shuffle_z)),
          "median":float(np.nanmedian(d.shuffle_z)),
          "fraction_positive":float(np.nanmean(d.shuffle_z>0))
      },
      "interpretation_boundary":"reviewer-motivated post-opening diagnostic; fixed species frequencies within each run; no causal claim",
      "existing_independence_residual_replaced":False,
      "original_primary_replaced":False
    }
    Path("NAAMP_SHUFFLE_NULL_RECEIPT_V0_1.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
