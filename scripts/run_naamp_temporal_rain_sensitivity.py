#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import math
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
import patsy
import statsmodels.api as sm
import statsmodels.formula.api as smf
from scipy.stats import spearmanr

ROOT=Path(__file__).resolve().parent

# Reuse the frozen ecological data construction.
BASE_SCRIPT=ROOT/"run_naamp_ecological_pulse.py"
spec=importlib.util.spec_from_file_location("pulse_base",BASE_SCRIPT)
base=importlib.util.module_from_spec(spec)
assert spec.loader
spec.loader.exec_module(base)

# Reuse only taxonomy/family source helpers from the existing AmphiBIO script.
TRAIT_SCRIPT=ROOT/"run_naamp_rainfall_filter_traits.py"
spec2=importlib.util.spec_from_file_location("trait_base",TRAIT_SCRIPT)
trait=importlib.util.module_from_spec(spec2)
assert spec2.loader
spec2.loader.exec_module(trait)

Q=1.959963984540054
TRAIN_YEARS=range(2001,2008)
VALID_YEARS=range(2008,2016)
MIN_TRAIN_ROUTES=8
MIN_TRAIN_RUNS=40
MIN_TRAIN_POS=10
MIN_TRAIN_NEG=10
MIN_VALID_EVENTS=20
MIN_VALID_ROUTES=5
B=100000
SEED=20260926

def zscale(s: pd.Series) -> pd.Series:
    a=pd.to_numeric(s,errors="coerce").astype(float)
    sd=float(a.std(ddof=0))
    if not np.isfinite(sd) or sd<=0:
        raise RuntimeError("non-positive scaling SD")
    return (a-float(a.mean()))/sd

def load_fixed_species():
    p=Path("NAAMP_SPECIES_PULSE_HETEROGENEITY_RECEIPT_V0_1.json")
    if not p.is_file():
        raise SystemExit("fixed species-family receipt missing")
    obj=json.loads(p.read_text(encoding="utf-8"))
    if int(obj["global"]["eligible_species"])!=29:
        raise SystemExit(f"species family drift: {obj['global']['eligible_species']}")
    spp=sorted(str(x["species_code"]) for x in obj["species_results"])
    if len(spp)!=29:
        raise SystemExit("expected 29 fixed species")
    return spp,obj

def training_table(runs: pd.DataFrame) -> pd.DataFrame:
    x=runs[runs.SurveyYear.isin(TRAIN_YEARS)].copy()
    x["log1p_days"]=np.log1p(x.DaysSinceRain.astype(float))
    x["dryness_z"]=zscale(x["log1p_days"])
    x["temp_z"]=zscale(x["mean_temp_c"])
    x["year_z"]=zscale(x["SurveyYear"])
    return x

def within_route_ols_species(sp: str,train: pd.DataFrame,sets: dict):
    # Opportunity routes are defined without using any validation-period data.
    pos_ids={rid for rid,spp in sets.items() if sp in spp}
    pos_train=train[train.RunID.astype(str).isin(pos_ids)]
    routes=set(pos_train.route_cluster.astype(str))
    x=train[train.route_cluster.astype(str).isin(routes)].copy()

    x["present"]=x.RunID.astype(str).map(lambda rid:int(sp in sets[rid]))
    n=int(len(x));nr=int(x.route_cluster.nunique())
    npos=int(x["present"].sum());nneg=int(n-npos)
    if nr<MIN_TRAIN_ROUTES or n<MIN_TRAIN_RUNS or npos<MIN_TRAIN_POS or nneg<MIN_TRAIN_NEG:
        return {
            "species":sp,"estimable":False,
            "n_runs":n,"n_routes":nr,"positive_runs":npos,"negative_runs":nneg,
            "reason":"training_coverage"
        }

    # Frisch–Waugh within-route transformation is algebraically equivalent to
    # including a full route fixed effect, but avoids thousands of dummy columns.
    X=patsy.dmatrix(
        "dryness_z + temp_z + bs(doy, df=5, degree=3) + C(RunNumber) + year_z",
        data=x,return_type="dataframe"
    )
    if "Intercept" in X.columns:
        X=X.drop(columns=["Intercept"])
    groups=x.route_cluster.astype(str)
    Xdm=X-X.groupby(groups).transform("mean")
    y=x["present"].astype(float)
    ydm=y-y.groupby(groups).transform("mean")

    # Remove zero-variance columns after within transformation.
    keep=[c for c in Xdm.columns if float(np.nanstd(Xdm[c]))>1e-12]
    Xdm=Xdm[keep]
    if "dryness_z" not in Xdm.columns:
        return {
            "species":sp,"estimable":False,
            "n_runs":n,"n_routes":nr,"positive_runs":npos,"negative_runs":nneg,
            "reason":"dryness_not_estimable_after_route_demean"
        }
    try:
        fit=sm.OLS(ydm.to_numpy(),Xdm.to_numpy()).fit(
            cov_type="cluster",cov_kwds={"groups":groups.to_numpy()}
        )
        j=list(Xdm.columns).index("dryness_z")
        b=float(fit.params[j]);se=float(fit.bse[j]);p=float(fit.pvalues[j])
        if not all(np.isfinite([b,se,p])) or se<=0:
            raise ValueError("nonfinite coefficient")
        lo=b-Q*se;hi=b+Q*se
        return {
            "species":sp,"estimable":True,
            "n_runs":n,"n_routes":nr,"positive_runs":npos,"negative_runs":nneg,
            "beta_dryness_z":b,"se_cluster":se,"ci95_beta":[lo,hi],"p_value":p,
            "rain_pulse_sensitivity":-b,
            "rain_pulse_sensitivity_se":se
        }
    except Exception as e:
        return {
            "species":sp,"estimable":False,
            "n_runs":n,"n_routes":nr,"positive_runs":npos,"negative_runs":nneg,
            "reason":repr(e)
        }

def build_validation_pairs(runs: pd.DataFrame,sets: dict):
    late=runs[runs.SurveyYear.isin(VALID_YEARS)].copy()
    return base.pair_runs(late,sets),late

def species_validation_events(pairs: pd.DataFrame,sets: dict,fixed_species: list[str]):
    fixed=set(fixed_species)
    ev=defaultdict(list)
    for r in pairs.itertuples(index=False):
        W=sets[str(r.wet_RunID)]
        D=sets[str(r.dry_RunID)]
        for sp in (W^D):
            if sp not in fixed:
                continue
            ev[sp].append({
                "y":int(sp in W),
                "route_cluster":str(r.route_cluster),
                "rain_contrast":float(r.rain_contrast),
                "temp_difference":float(r.temp_difference),
                "doy_difference":float(r.doy_difference),
                "year_gap":float(r.year_gap),
            })
    return ev

def fit_validation_species(sp: str,events):
    x=pd.DataFrame(events)
    if len(x)<MIN_VALID_EVENTS or (len(x) and x.route_cluster.nunique()<MIN_VALID_ROUTES):
        return {
            "species":sp,"estimable":False,
            "n_events":int(len(x)),
            "n_routes":int(x.route_cluster.nunique()) if len(x) else 0,
            "reason":"validation_coverage"
        }
    if x.y.nunique()<2:
        return {
            "species":sp,"estimable":False,
            "n_events":int(len(x)),"n_routes":int(x.route_cluster.nunique()),
            "reason":"no_outcome_variation"
        }
    for c in ["rain_contrast","temp_difference","doy_difference","year_gap"]:
        x["c_"+c]=x[c]-x[c].mean()
    formula="y ~ c_rain_contrast + c_temp_difference + c_doy_difference + c_year_gap"
    try:
        fit=smf.glm(formula,data=x,family=sm.families.Binomial()).fit(
            cov_type="cluster",cov_kwds={"groups":x.route_cluster},maxiter=200
        )
        b=float(fit.params["Intercept"]);se=float(fit.bse["Intercept"]);p=float(fit.pvalues["Intercept"])
        if not all(np.isfinite([b,se,p])) or se<=0:
            raise ValueError("nonfinite validation intercept")
        lo=b-Q*se;hi=b+Q*se
        return {
            "species":sp,"estimable":True,
            "n_events":int(len(x)),"n_routes":int(x.route_cluster.nunique()),
            "intercept_log_odds":b,"intercept_se_cluster":se,
            "ci95_log_odds":[lo,hi],"p_value":p,
            "adjusted_wet_probability":float(1/(1+math.exp(-b)))
        }
    except Exception as e:
        return {
            "species":sp,"estimable":False,
            "n_events":int(len(x)),"n_routes":int(x.route_cluster.nunique()),
            "reason":repr(e)
        }

def primary_cross_species(train_results,valid_results):
    tr={x["species"]:x for x in train_results if x.get("estimable")}
    va={x["species"]:x for x in valid_results if x.get("estimable")}
    spp=sorted(set(tr)&set(va))
    if len(spp)<15:
        return {"estimable":False,"n_species":len(spp),"reason":"overlap_below_15"},pd.DataFrame()

    rows=[]
    for sp in spp:
        rows.append({
            "species":sp,
            "early_sensitivity":float(tr[sp]["rain_pulse_sensitivity"]),
            "early_sensitivity_se":float(tr[sp]["rain_pulse_sensitivity_se"]),
            "late_log_odds":float(va[sp]["intercept_log_odds"]),
            "late_se":float(va[sp]["intercept_se_cluster"]),
            "late_wet_probability":float(va[sp]["adjusted_wet_probability"]),
            "weight":1.0/(float(va[sp]["intercept_se_cluster"])**2),
        })
    d=pd.DataFrame(rows)
    sd=float(d.early_sensitivity.std(ddof=0))
    if not np.isfinite(sd) or sd<=0:
        return {"estimable":False,"n_species":len(d),"reason":"no_early_sensitivity_variation"},d
    d["z_early_sensitivity"]=(d.early_sensitivity-d.early_sensitivity.mean())/sd

    fit=smf.wls("late_log_odds ~ z_early_sensitivity",data=d,weights=d.weight).fit(cov_type="HC3")
    b=float(fit.params["z_early_sensitivity"]);se=float(fit.bse["z_early_sensitivity"]);p=float(fit.pvalues["z_early_sensitivity"])
    lo=b-Q*se;hi=b+Q*se
    rho,prho=spearmanr(d.early_sensitivity,d.late_log_odds)
    return {
        "estimable":True,"n_species":int(len(d)),
        "beta_per_1sd_early_sensitivity":b,"se_hc3":se,
        "ci95_beta":[lo,hi],"p_value":p,
        "positive_ci_support":bool(lo>0),
        "spearman_rho":float(rho),"spearman_p":float(prho),
        "early_sensitivity_mean":float(d.early_sensitivity.mean()),
        "early_sensitivity_sd":sd
    },d

def attach_family(d: pd.DataFrame):
    if len(d)==0:
        return d,[],None
    t,blob=trait.load_traits()
    idx={s:i for i,s in enumerate(t["species_norm"].tolist())}
    rows=[];audit=[]
    for r in d.itertuples(index=False):
        sp=trait.normalize_binomial(r.species)
        candidates=[sp]
        toks=sp.split()
        if len(toks)==2 and toks[0] in trait.ALIASES:
            candidates.append(trait.ALIASES[toks[0]]+" "+toks[1])
        hits=[c for c in candidates if c in idx]
        if sp in hits: chosen=sp
        elif len(hits)==1: chosen=hits[0]
        elif len(hits)>1: raise SystemExit(f"ambiguous family match {sp}: {hits}")
        else: chosen=None
        rr=dict(r._asdict())
        if chosen is None:
            rr["Family"]=""
            audit.append({"species":sp,"matched":False})
        else:
            tr=t.iloc[idx[chosen]]
            fam=str(tr.get("Family","") or "").strip()
            rr["Family"]=fam
            audit.append({
                "species":sp,"matched":bool(fam),"trait_species":chosen,"Family":fam,
                "match_type":"exact" if chosen==sp else "frozen_genus_alias"
            })
        rows.append(rr)
    return pd.DataFrame(rows),audit,blob

def family_permutation(d: pd.DataFrame):
    x,audit,blob=attach_family(d)
    x=x[x.Family.astype(str)!=""].copy()
    if len(x)<15 or x.Family.nunique()<2:
        return {
            "estimable":False,"n_species":int(len(x)),
            "reason":"insufficient_family_coverage",
            "taxonomy_audit":audit,"trait_blob":blob
        }

    families={str(f):g.index.to_numpy() for f,g in x.groupby("Family")}
    pos={idx:i for i,idx in enumerate(x.index)}
    xx0=np.asarray(x.z_early_sensitivity,float)
    yy=np.asarray(x.late_log_odds,float)
    ww=np.asarray(x.weight,float)

    def stat(xx):
        xc=np.zeros(len(x));yc=np.zeros(len(x))
        for fam,idxs in families.items():
            loc=np.array([pos[i] for i in idxs],int)
            wf=ww[loc]
            mx=np.sum(wf*xx[loc])/np.sum(wf)
            my=np.sum(wf*yy[loc])/np.sum(wf)
            xc[loc]=xx[loc]-mx
            yc[loc]=yy[loc]-my
        den=np.sum(ww*xc*xc)
        if den<=0:return np.nan
        return float(np.sum(ww*xc*yc)/den)

    obs=stat(xx0)
    if not np.isfinite(obs):
        return {
            "estimable":False,"n_species":int(len(x)),
            "reason":"no_within_family_predictor_variation",
            "taxonomy_audit":audit,"trait_blob":blob
        }

    rng=np.random.default_rng(SEED)
    vals=np.empty(B,float)
    for i in range(B):
        xx=xx0.copy()
        for fam,idxs in families.items():
            loc=np.array([pos[j] for j in idxs],int)
            if len(loc)>1:
                xx[loc]=rng.permutation(xx[loc])
        vals[i]=stat(xx)
    vals=vals[np.isfinite(vals)]
    p2=(1+np.sum(np.abs(vals)>=abs(obs)))/(1+len(vals))
    ppos=(1+np.sum(vals>=obs))/(1+len(vals))
    return {
        "estimable":True,"n_species":int(len(x)),"n_families":int(x.Family.nunique()),
        "family_counts":{str(k):int(v) for k,v in x.Family.value_counts().to_dict().items()},
        "observed_weighted_within_family_slope":obs,
        "permutations":int(len(vals)),"seed":SEED,
        "two_sided_p":float(p2),"positive_tail_p":float(ppos),
        "positive_support":bool(ppos<0.05),
        "q025":float(np.quantile(vals,.025)),"q975":float(np.quantile(vals,.975)),
        "taxonomy_audit":audit,"trait_blob":blob
    }

def main():
    fixed,source_receipt=load_fixed_species()
    raw=base.load()
    runs,sets=base.build_runs(raw)

    train=training_table(runs)
    train_sets={str(rid):sets[str(rid)] for rid in train.RunID.astype(str)}
    train_results=[
        within_route_ols_species(sp,train,train_sets)
        for sp in fixed
    ]

    pairs,late_runs=build_validation_pairs(runs,sets)
    events=species_validation_events(pairs,sets,fixed)
    valid_results=[
        fit_validation_species(sp,events.get(sp,[]))
        for sp in fixed
    ]

    primary,cross=primary_cross_species(train_results,valid_results)
    fam=family_permutation(cross) if primary.get("estimable") else {"estimable":False,"reason":"primary_nonestimable"}

    result={
        "analysis":"naamp_temporally_disjoint_rain_sensitivity_v0_1",
        "contract":"NAAMP_TEMPORAL_RAIN_SENSITIVITY_CONTRACT_V0_1.json",
        "fixed_species_family":{
            "n_species":len(fixed),
            "source":"NAAMP_SPECIES_PULSE_HETEROGENEITY_RECEIPT_V0_1.json"
        },
        "time_split":{
            "training_years":[2001,2007],
            "validation_years":[2008,2015],
            "training_runs":int(len(train)),
            "validation_runs":int(len(late_runs)),
            "validation_pairs":int(len(pairs))
        },
        "training_species_results":train_results,
        "validation_species_results":valid_results,
        "coverage":{
            "training_estimable":int(sum(x.get("estimable",False) for x in train_results)),
            "validation_estimable":int(sum(x.get("estimable",False) for x in valid_results)),
            "overlap_estimable":int(primary.get("n_species",0))
        },
        "primary_cross_species":primary,
        "family_stratified_permutation":fam,
        "cross_species_table":[
            {
                "species":str(r.species),
                "early_rain_pulse_sensitivity":float(r.early_sensitivity),
                "early_sensitivity_se":float(r.early_sensitivity_se),
                "z_early_sensitivity":float(r.z_early_sensitivity),
                "late_adjusted_wet_log_odds":float(r.late_log_odds),
                "late_se":float(r.late_se),
                "late_adjusted_wet_probability":float(r.late_wet_probability)
            }
            for r in cross.itertuples(index=False)
        ] if len(cross) else [],
        "interpretation_boundary":{
            "status":"final mechanism slot; temporally disjoint training and validation years",
            "behavioral_trait":"Early rain sensitivity is estimated acoustic behavior, not physiology.",
            "causal_claim_authorized":False,
            "occupancy_claim_authorized":False
        }
    }
    Path("NAAMP_TEMPORAL_RAIN_SENSITIVITY_RECEIPT_V0_1.json").write_text(
        json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8"
    )
    print(json.dumps(result,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
