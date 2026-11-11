#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import itertools
import json
import math
import urllib.request
from pathlib import Path

import numpy as np
import pandas as pd

ITEM_ID="600789c4d34e162231fb1cdb"
ITEM_URL=f"https://www.sciencebase.gov/catalog/item/{ITEM_ID}?format=json"
TARGET_NAME="LAMPDataForPLOS.csv"
OUT=Path("external/LAMP_HELDOUT_DEEP_TEMPLATE_RECEIPT_V0_1.json")
TRAIN_END=2008
VALID_START=2009
VALID_END=2017
MIN_TRAIN_OPPS=3
MIN_ACTIVE_TRAIN_YEARS=5
DEEP_K=4
BOOT=10000
SEED=2840242

META=["RouteRegion","RouteNumb","RouteName","Run","Stop","Year","Month","Day"]

def get_json(url):
    req=urllib.request.Request(url,headers={"User-Agent":"frogcs-lamp-holdout/0.1","Accept":"application/json"})
    with urllib.request.urlopen(req,timeout=60) as r:
        return json.loads(r.read().decode("utf-8"))

def download_file(url,path):
    req=urllib.request.Request(url,headers={"User-Agent":"frogcs-lamp-holdout/0.1"})
    with urllib.request.urlopen(req,timeout=120) as r:
        b=r.read()
    path.write_bytes(b)
    return hashlib.sha256(b).hexdigest(),len(b)

def route_key(df):
    return df["RouteRegion"].astype(str)+"|"+df["RouteNumb"].astype(str)+"|"+df["RouteName"].astype(str)

def coerce_call_values(df,species):
    bad={}
    out=df.copy()
    for sp in species:
        s=out[sp]
        nonblank=s.notna() & (s.astype(str).str.strip()!="")
        vals=pd.to_numeric(s.where(nonblank),errors="coerce")
        bad_mask=nonblank & vals.isna()
        if bad_mask.any():
            bad[sp]=sorted(set(s[bad_mask].astype(str)))[:20]
        vals=vals.fillna(0.0)
        bad_num=~vals.isin([0.0,1.0,2.0,3.0])
        if bad_num.any():
            bad.setdefault(sp,[])
            bad[sp]+=sorted(set(vals[bad_num].astype(str)))[:20]
        out[sp]=vals.astype(int)
    if bad:
        raise ValueError("Undocumented call-index codes: "+json.dumps(bad,ensure_ascii=False))
    return out

def complete_run_years(df):
    # One row per stop, exactly stops 1..10, within Route x Run x Year.
    key=["route_id","Run","Year"]
    keep=[]
    for gk,g in df.groupby(key,sort=False):
        stops=list(g["Stop"].astype(int))
        if len(g)==10 and len(set(stops))==10 and set(stops)==set(range(1,11)):
            keep.append(g)
    if not keep:
        return df.iloc[0:0].copy()
    return pd.concat(keep,ignore_index=True)

def template_for_group(g,sp):
    # g contains complete training route-run-years, so every included year has all 10 stops.
    years=sorted(g["Year"].unique())
    if len(years)<MIN_TRAIN_OPPS:
        return None
    active_years=sum(bool((yy[sp]>0).any()) for _,yy in g.groupby("Year"))
    if active_years<MIN_ACTIVE_TRAIN_YEARS:
        return None
    rows=[]
    for st in range(1,11):
        s=g.loc[g["Stop"]==st,sp]
        n_obs=int(len(s))
        n_active=int((s>0).sum())
        q=(n_active+0.5)/(n_obs+1.0)
        prior_strong=bool((s>=2).any())
        rows.append((st,q,prior_strong,n_obs,n_active))
    if not any(x[2] for x in rows) or all(x[2] for x in rows):
        return None
    return rows

def exact_k_expected_overlap(q,strong,k):
    idx=range(10)
    vals=[]
    logw=[]
    odds=np.asarray(q,dtype=float)/(1-np.asarray(q,dtype=float))
    for comb in itertools.combinations(idx,k):
        comb=set(comb)
        vals.append(sum(1 for i in comb if strong[i]))
        logw.append(sum(math.log(odds[i]) for i in comb))
    m=max(logw)
    w=np.exp(np.asarray(logw)-m)
    w=w/w.sum()
    return float(np.dot(w,np.asarray(vals,dtype=float)))

def block_bootstrap(clusters):
    rng=np.random.default_rng(SEED)
    routes=clusters["route_id"].drop_duplicates().to_numpy()
    by_route={r:clusters.loc[clusters["route_id"]==r] for r in routes}
    delta=np.empty(BOOT)
    deepmean=np.empty(BOOT)
    for b in range(BOOT):
        picks=rng.choice(routes,size=len(routes),replace=True)
        parts=[by_route[r] for r in picks]
        z=pd.concat(parts,ignore_index=True)
        d=z.loc[z["depth_class"]=="deep","R"]
        s=z.loc[z["depth_class"]=="shallow","R"]
        delta[b]=d.mean()-s.mean() if len(d) and len(s) else np.nan
        deepmean[b]=d.mean() if len(d) else np.nan
    delta=delta[np.isfinite(delta)]
    deepmean=deepmean[np.isfinite(deepmean)]
    return {
        "delta_ci95":[float(np.quantile(delta,0.025)),float(np.quantile(delta,0.975))],
        "deep_mean_ci95":[float(np.quantile(deepmean,0.025)),float(np.quantile(deepmean,0.975))],
        "valid_delta_boot":int(len(delta)),
        "valid_deep_boot":int(len(deepmean)),
    }

item=get_json(ITEM_URL)
file_obj=None
for f in item.get("files") or []:
    if f.get("name")==TARGET_NAME:
        file_obj=f; break
if file_obj is None:
    raise RuntimeError("Target CSV not found in ScienceBase item")
url=file_obj.get("downloadUri") or file_obj.get("url") or file_obj.get("uri")
if not url:
    raise RuntimeError("Target CSV has no download URL")

data_path=Path("external_data")/TARGET_NAME
data_path.parent.mkdir(exist_ok=True)
sha,size=download_file(url,data_path)

raw=pd.read_csv(data_path,dtype=str,keep_default_na=False)
missing=[c for c in META if c not in raw.columns]
if missing:
    raise ValueError("Missing fixed metadata columns: "+repr(missing))
species=[c for c in raw.columns if c not in META]
if len(species)<5:
    raise ValueError("Too few species columns")

# structural fields
for c in ["Year","Stop"]:
    raw[c]=pd.to_numeric(raw[c],errors="raise").astype(int)
raw["route_id"]=route_key(raw)
raw=coerce_call_values(raw,species)

# Work only with complete ten-stop route-runs. This avoids treating unvisited stops as zeros.
complete=complete_run_years(raw)
train=complete.loc[complete["Year"]<=TRAIN_END].copy()
valid=complete.loc[(complete["Year"]>=VALID_START)&(complete["Year"]<=VALID_END)].copy()

templates={}
for (rid,run),g in train.groupby(["route_id","Run"],sort=False):
    for sp in species:
        t=template_for_group(g,sp)
        if t is not None:
            templates[(rid,str(run),sp)]={st:{"q":q,"prior_strong":ps,"n_obs":no,"n_active":na}
                                          for st,q,ps,no,na in t}

clusters=[]
for (rid,run,yr),g in valid.groupby(["route_id","Run","Year"],sort=False):
    if len(g)!=10:
        continue
    g=g.sort_values("Stop")
    for sp in species:
        key=(rid,str(run),sp)
        if key not in templates:
            continue
        vals=g[sp].to_numpy(dtype=int)
        active=vals>0
        k=int(active.sum())
        if k<1 or k>9:
            continue
        t=templates[key]
        q=np.array([t[i]["q"] for i in range(1,11)],dtype=float)
        strong=np.array([t[i]["prior_strong"] for i in range(1,11)],dtype=bool)
        obs=int(strong[active].sum())
        exp=exact_k_expected_overlap(q,strong,k)
        R=float(obs-exp)
        clusters.append({
            "route_id":rid,"Run":str(run),"Year":int(yr),"species":sp,
            "K":k,"depth_class":"deep" if k>=DEEP_K else "shallow",
            "observed_overlap":obs,"expected_overlap":exp,"R":R
        })

cl=pd.DataFrame(clusters)
if cl.empty:
    result={"analysis":"lamp_heldout_deep_template_v0_1","classification":"inconclusive_holdout_template_test",
            "reason":"no eligible validation clusters","outcome_values_read":True}
else:
    deep=cl[cl["depth_class"]=="deep"]
    shallow=cl[cl["depth_class"]=="shallow"]
    counts={
        "complete_train_route_run_years":int(train.groupby(["route_id","Run","Year"]).ngroups),
        "complete_validation_route_run_years":int(valid.groupby(["route_id","Run","Year"]).ngroups),
        "eligible_templates":int(len(templates)),
        "validation_clusters":int(len(cl)),
        "deep_clusters":int(len(deep)),
        "shallow_clusters":int(len(shallow)),
        "deep_taxa":int(deep["species"].nunique()),
        "deep_routes":int(deep["route_id"].nunique()),
    }
    gate=(counts["deep_clusters"]>=50 and counts["shallow_clusters"]>=100 and
          counts["deep_taxa"]>=5 and counts["deep_routes"]>=20)
    delta=float(deep["R"].mean()-shallow["R"].mean()) if len(deep) and len(shallow) else float("nan")
    D=float(deep["R"].mean()) if len(deep) else float("nan")
    S=float(shallow["R"].mean()) if len(shallow) else float("nan")
    boot=block_bootstrap(cl) if gate else None
    primary=bool(gate and delta>0 and boot["delta_ci95"][0]>0)
    secondary=bool(gate and D>0 and boot["deep_mean_ci95"][0]>0)
    if not gate:
        classification="inconclusive_holdout_template_test"
    elif primary and secondary:
        classification="heldout_template_support"
    else:
        classification="heldout_template_non_support"
    result={
        "analysis":"lamp_heldout_deep_template_v0_1",
        "contract":"revision/LAMP_HELDOUT_DEEP_TEMPLATE_TEST_V0_1.md",
        "source":{"item_id":ITEM_ID,"file":TARGET_NAME,"sha256":sha,"size_bytes":size},
        "split":{"training":"1997-2008","validation":"2009-2017"},
        "counts":counts,
        "informativeness_gate_pass":gate,
        "observed":{
            "mean_R_deep":D,
            "mean_R_shallow":S,
            "deep_minus_shallow":delta,
        },
        "bootstrap":boot,
        "primary_support":primary,
        "secondary_support":secondary,
        "classification":classification,
        "outcome_values_read":True,
        "retuning_after_readback":False,
    }

OUT.parent.mkdir(exist_ok=True)
OUT.write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding="utf-8")
print(json.dumps(result,indent=2,ensure_ascii=False))
