#!/usr/bin/env python3
from __future__ import annotations

import csv, hashlib, io, json, math, urllib.request
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
import patsy
import statsmodels.api as sm

CALLING_ITEM="5b3e4054e4b060350a0ef7e3"
WATER_ITEM="5b3e4093e4b060350a0ef7f6"
CALLING_FILE="Daily Calling activity Pcrucifer SC4DAI2 2008to2012.csv"
WATER_FILE="Median daily water depths.csv"
CALLING_SHA="1a308c30fa7bcf42e576998625b312f25c700dd1abd6f23ee554e535fc2b81f5"
WATER_SHA="a3dca71608ea75be5a1f06c9ddd3fc05a6114ecdb37ff45dc249e532d68e66f3"
SITE="SC4DAI2"
OUT=Path("exploration/STCROIX_DIRECT_HYDROLOGY_ANALYSIS_RECEIPT_V0_1.json")
Q=1.959963984540054


def get_json(item):
    req=urllib.request.Request(
        f"https://www.sciencebase.gov/catalog/item/{item}?format=json",
        headers={"User-Agent":"frogcs-stcroix-analysis/0.1","Accept":"application/json"}
    )
    with urllib.request.urlopen(req,timeout=90) as r:
        return json.loads(r.read().decode("utf-8"))


def get_bytes(url):
    req=urllib.request.Request(url,headers={"User-Agent":"frogcs-stcroix-analysis/0.1"})
    with urllib.request.urlopen(req,timeout=180) as r:
        return r.read()


def file_url(f):
    return f.get("downloadUri") or f.get("url") or f.get("uri")


def exact_csv(item_id,name,sha):
    obj=get_json(item_id)
    hits=[f for f in obj.get("files") or [] if (f.get("name") or "")==name]
    if len(hits)!=1:
        raise RuntimeError(f"expected one file {name}, found {len(hits)}")
    b=get_bytes(file_url(hits[0]))
    got=hashlib.sha256(b).hexdigest()
    if got!=sha:
        raise RuntimeError(f"hash drift {name}: {got}")
    return list(csv.DictReader(io.StringIO(b.decode("utf-8-sig"))))


def parse_date(x):
    s=str(x or "").strip()
    for fmt in ("%m/%d/%Y","%m/%d/%y","%Y-%m-%d"):
        try:
            return datetime.strptime(s,fmt).date()
        except ValueError:
            pass
    raise RuntimeError(f"bad date {s!r}")


def num(x):
    try:
        v=float(str(x or "").strip())
        return v if np.isfinite(v) else np.nan
    except Exception:
        return np.nan


def build_join():
    calling=exact_csv(CALLING_ITEM,CALLING_FILE,CALLING_SHA)
    water=exact_csv(WATER_ITEM,WATER_FILE,WATER_SHA)
    call_cols=[c for c in calling[0] if "integrand" in c.lower()]
    if len(call_cols)!=1:
        raise RuntimeError(f"calling column ambiguity {call_cols}")
    cc=call_cols[0]

    cr=[]
    for r in calling:
        v=num(r.get(cc))
        if not np.isfinite(v):
            continue
        cr.append({"date":parse_date(r["Date"]),"calling":float(v)})
    wr=[]
    for r in water:
        if str(r.get("Site") or "").strip()!=SITE:
            continue
        v=num(r.get("Median water depth (m)"))
        if not np.isfinite(v):
            continue
        wr.append({"date":parse_date(r["Date"]),"water_depth_m":float(v)})

    c=pd.DataFrame(cr)
    w=pd.DataFrame(wr)
    if c.date.duplicated().any() or w.date.duplicated().any():
        raise RuntimeError("duplicate dates")
    d=c.merge(w,on="date",how="inner").sort_values("date").reset_index(drop=True)
    if len(d)!=282:
        raise RuntimeError(f"join drift {len(d)} != 282")
    d["year"]=pd.to_datetime(d.date).dt.year.astype(int)
    d["doy"]=pd.to_datetime(d.date).dt.dayofyear.astype(float)
    d["log_call"]=np.log1p(d.calling.astype(float))
    d["water_depth_z"]=(d.water_depth_m-d.water_depth_m.mean())/d.water_depth_m.std(ddof=0)

    progress=np.zeros(len(d),float)
    for y,g in d.groupby("year"):
        idx=g.index.to_numpy()
        dates=pd.to_datetime(g.date)
        lo=dates.min()
        hi=dates.max()
        denom=max((hi-lo).days,1)
        progress[idx]=((dates-lo).dt.days/denom).to_numpy(float)
    d["season_progress"]=progress
    d["water_depth_year_z"]=d.groupby("year").water_depth_m.transform(
        lambda x:(x-x.mean())/(x.std(ddof=0) if x.std(ddof=0)>0 else np.nan)
    )
    if not np.isfinite(d.water_depth_year_z).all():
        raise RuntimeError("within-year depth variance failure")
    return d


def block_hac_fit(formula,d,maxlags):
    y,X=patsy.dmatrices(formula,d,return_type="dataframe")
    yv=np.asarray(y).reshape(-1)
    Xv=np.asarray(X,float)
    fit=sm.OLS(yv,Xv).fit()
    resid=np.asarray(fit.resid,float)
    names=list(X.columns)
    XtX_inv=np.linalg.pinv(Xv.T@Xv)
    meat=np.zeros((Xv.shape[1],Xv.shape[1]),float)

    years=np.asarray(d["year"],int)
    for yr in sorted(set(years)):
        idx=np.flatnonzero(years==yr)
        Xi=Xv[idx]
        ei=resid[idx]
        score=Xi*ei[:,None]
        meat+=score.T@score
        n=len(idx)
        for lag in range(1,min(maxlags,n-1)+1):
            weight=1.0-lag/(maxlags+1.0)
            G=score[lag:].T@score[:-lag]
            meat+=weight*(G+G.T)

    cov=XtX_inv@meat@XtX_inv
    se=np.sqrt(np.clip(np.diag(cov),0,None))
    params=np.asarray(fit.params,float)
    return {
        "formula":formula,
        "n":int(len(d)),
        "df_model":int(fit.df_model),
        "names":names,
        "params":params,
        "se":se,
        "cov":cov,
        "r2":float(fit.rsquared),
    }


def term(res,name):
    j=res["names"].index(name)
    b=float(res["params"][j])
    se=float(res["se"][j])
    z=b/se if se>0 else np.nan
    # Normal approximation, matching the exploratory NAAMP convention.
    p=float(math.erfc(abs(z)/math.sqrt(2))) if np.isfinite(z) else None
    return {
        "beta":b,
        "se_block_hac":se,
        "ci95":[b-Q*se,b+Q*se],
        "p_normal":p,
        "positive_ci":bool(b-Q*se>0),
    }


def primary_fit(d,predictor="water_depth_z"):
    formula=(
      f"log_call ~ {predictor} + C(year) + "
      "bs(season_progress, df=4, degree=3, include_intercept=False)"
    )
    res=block_hac_fit(formula,d.sort_values(["year","date"]).reset_index(drop=True),7)
    return {
        "n_days":int(len(d)),
        "years":sorted(int(x) for x in d.year.unique()),
        "model_r2":res["r2"],
        "water_depth":term(res,predictor),
        "formula":formula,
        "covariance":"block Newey-West HAC(7) within year"
    }


def year_specific_curve(d):
    formula=(
      "log_call ~ water_depth_z + C(year) + "
      "C(year):season_progress + C(year):I(season_progress ** 2)"
    )
    res=block_hac_fit(formula,d.sort_values(["year","date"]).reset_index(drop=True),7)
    return {
        "n_days":int(len(d)),
        "model_r2":res["r2"],
        "water_depth":term(res,"water_depth_z"),
        "formula":formula,
        "covariance":"block Newey-West HAC(7) within year"
    }


def first_difference(d):
    rows=[]
    for y,g in d.groupby("year",sort=True):
        g=g.sort_values("date").reset_index(drop=True)
        for i in range(1,len(g)):
            gap=(g.loc[i,"date"]-g.loc[i-1,"date"]).days
            if gap!=1:
                continue
            rows.append({
                "year":int(y),
                "date":g.loc[i,"date"],
                "delta_log_call":float(g.loc[i,"log_call"]-g.loc[i-1,"log_call"]),
                "delta_depth_m":float(g.loc[i,"water_depth_m"]-g.loc[i-1,"water_depth_m"])
            })
    x=pd.DataFrame(rows)
    formula="delta_log_call ~ delta_depth_m + C(year)"
    res=block_hac_fit(formula,x.sort_values(["year","date"]).reset_index(drop=True),3)
    return {
        "n_consecutive_day_differences":int(len(x)),
        "years":sorted(int(v) for v in x.year.unique()),
        "delta_water_depth":term(res,"delta_depth_m"),
        "formula":formula,
        "covariance":"block Newey-West HAC(3) within year"
    }


def leave_one_year_out(d):
    out={}
    for y in sorted(d.year.unique()):
        x=d[d.year!=y].copy()
        out[str(int(y))]=primary_fit(x)
    return out


def descriptive(d):
    return {
        "n_days":int(len(d)),
        "years":{str(int(y)):int(n) for y,n in d.year.value_counts().sort_index().items()},
        "calling_integrand":{
            "min":float(d.calling.min()),
            "median":float(d.calling.median()),
            "max":float(d.calling.max()),
            "zero_days":int((d.calling==0).sum())
        },
        "water_depth_m":{
            "min":float(d.water_depth_m.min()),
            "median":float(d.water_depth_m.median()),
            "max":float(d.water_depth_m.max()),
            "sd":float(d.water_depth_m.std(ddof=0)),
            "per_year_sd":{str(int(y)):float(g.water_depth_m.std(ddof=0)) for y,g in d.groupby("year")}
        }
    }


def main():
    d=build_join()
    p=primary_fit(d)
    ys=year_specific_curve(d)
    wy=primary_fit(d,predictor="water_depth_year_z")
    fd=first_difference(d)
    loo=leave_one_year_out(d)
    out={
      "analysis":"stcroix_direct_hydrology_calling_v0_1",
      "contract":"exploration/STCROIX_DIRECT_HYDROLOGY_ANALYSIS_CONTRACT_V0_1.json",
      "source_pins":{
        "calling_sha256":CALLING_SHA,
        "water_sha256":WATER_SHA,
        "site":SITE
      },
      "descriptive":descriptive(d),
      "primary":p,
      "sensitivity_year_specific_season_curve":ys,
      "sensitivity_within_year_depth_z":wy,
      "sensitivity_consecutive_day_first_difference":fd,
      "leave_one_year_out":loo,
      "classification":{
        "direct_water_depth_calling_support":bool(p["water_depth"]["positive_ci"]),
        "year_specific_curve_support":bool(ys["water_depth"]["positive_ci"]),
        "within_year_depth_support":bool(wy["water_depth"]["positive_ci"]),
        "leave_one_year_out_all_positive":bool(all(v["water_depth"]["beta"]>0 for v in loo.values())),
        "leave_one_year_out_all_ci_positive":bool(all(v["water_depth"]["positive_ci"] for v in loo.values()))
      },
      "interpretation_boundary":{
        "single_species_single_wetland":True,
        "community_matrix_replication":False,
        "temperature_precipitation_adjusted":False,
        "water_depth_is_body_hydration":False,
        "causal_mediation_established":False,
        "rc11_change_authorized":False
      }
    }
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,indent=2,sort_keys=True))


if __name__=="__main__":
    main()
