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
from scipy.stats import spearmanr

ROOT=Path(__file__).resolve().parent
BASE_SCRIPT=ROOT/"run_naamp_ecological_pulse.py"
TRAIT_SCRIPT=ROOT/"run_naamp_rainfall_filter_traits.py"

spec=importlib.util.spec_from_file_location("pulse_base",BASE_SCRIPT)
base=importlib.util.module_from_spec(spec)
assert spec.loader
spec.loader.exec_module(base)

tspec=importlib.util.spec_from_file_location("trait_base",TRAIT_SCRIPT)
trait=importlib.util.module_from_spec(tspec)
assert tspec.loader
tspec.loader.exec_module(trait)

BASELINE_YEARS=set(range(2001,2008))
VALIDATION_YEARS=set(range(2008,2016))
Q=1.959963984540054
B=100000
SEED=20260926

def baseline_traits(d,sets):
    b=d[d["SurveyYear"].isin(BASELINE_YEARS)].copy()
    if b.empty:
        raise SystemExit("no baseline runs")

    # species -> route clusters where detected at least once in baseline
    route_sets=defaultdict(set)
    for r in b.itertuples(index=False):
        spp=sets.get(str(r.RunID),set())
        for sp in spp:
            route_sets[sp].add(str(r.route_cluster))

    rows=[]
    for sp,routes in sorted(route_sets.items()):
        if len(routes)<10:
            continue
        x=b[b["route_cluster"].isin(routes)].copy()
        if x.empty:
            continue
        active=np.array([sp in sets.get(str(rid),set()) for rid in x["RunID"]],dtype=bool)
        n=len(x); a=int(active.sum())
        prevalence=a/n
        recurrence_logit=float(np.log((a+0.5)/(n-a+0.5)))

        probs=[]
        windows_with_effort=0
        seasonal_counts={}
        for rn in ["1","2","3","4"]:
            xx=x[x["RunNumber"].astype(str)==rn]
            if len(xx)==0:
                seasonal_counts[rn]={"eligible_runs":0,"positive_runs":0,"activity_probability":None}
                continue
            windows_with_effort+=1
            aa=int(sum(sp in sets.get(str(rid),set()) for rid in xx["RunID"]))
            p=aa/len(xx)
            seasonal_counts[rn]={
                "eligible_runs":int(len(xx)),
                "positive_runs":aa,
                "activity_probability":float(p)
            }
            probs.append(p)

        if windows_with_effort>=3 and sum(probs)>0:
            q=np.asarray(probs,float)
            q=q/q.sum()
            h=float(-np.sum(q[q>0]*np.log(q[q>0])))
            eff=float(np.exp(h))
            concentration=float(1.0-eff/windows_with_effort)
        else:
            h=eff=concentration=np.nan

        rows.append({
            "species":sp,
            "baseline_routes":int(len(routes)),
            "baseline_eligible_runs":int(n),
            "baseline_active_runs":a,
            "baseline_recurrence":float(prevalence),
            "baseline_recurrence_logit":recurrence_logit,
            "baseline_windows_with_effort":int(windows_with_effort),
            "baseline_seasonal_entropy":h,
            "baseline_effective_windows":eff,
            "baseline_seasonal_concentration":concentration,
            "baseline_window_counts":seasonal_counts
        })
    return pd.DataFrame(rows)

def validation_pairs(d,sets):
    v=d[d["SurveyYear"].isin(VALIDATION_YEARS)].copy()
    p=base.pair_runs(v,sets)
    return v,p

def fit_species_response(sp,events):
    x=pd.DataFrame(events)
    if len(x)<30 or x.route_cluster.nunique()<10:
        return {
            "species":sp,"estimable":False,"n_events":int(len(x)),
            "n_routes":int(x.route_cluster.nunique()) if len(x) else 0,
            "reason":"validation_eligibility"
        }
    for col in ["rain_contrast","temp_difference","doy_difference","year_gap"]:
        x["c_"+col]=x[col]-x[col].mean()
    formula="y ~ c_rain_contrast + c_temp_difference + c_doy_difference + c_year_gap"
    try:
        fit=smf.glm(formula,data=x,family=sm.families.Binomial()).fit(
            cov_type="cluster",cov_kwds={"groups":x.route_cluster}
        )
        b=float(fit.params["Intercept"])
        se=float(fit.bse["Intercept"])
        p=float(fit.pvalues["Intercept"])
        if not all(np.isfinite([b,se,p])) or se<=0:
            raise ValueError("nonfinite intercept")
        lo=b-Q*se;hi=b+Q*se
        return {
            "species":sp,"estimable":True,"n_events":int(len(x)),
            "n_routes":int(x.route_cluster.nunique()),
            "adjusted_log_odds":b,"adjusted_se":se,
            "ci95_log_odds":[lo,hi],"p_value":p,
            "adjusted_wet_probability":float(1/(1+np.exp(-b))),
            "weight":float(1/(se*se))
        }
    except Exception as e:
        return {"species":sp,"estimable":False,"n_events":int(len(x)),"reason":str(e)}

def validation_species_responses(pairs,sets):
    events=defaultdict(list)
    all_species=set()
    for r in pairs.itertuples(index=False):
        W=sets[str(r.wet_RunID)]
        D=sets[str(r.dry_RunID)]
        all_species.update(W^D)
        for sp in W^D:
            events[sp].append({
                "y":int(sp in W),
                "route_cluster":str(r.route_cluster),
                "rain_contrast":float(r.rain_contrast),
                "temp_difference":float(r.temp_difference),
                "doy_difference":float(r.doy_difference),
                "year_gap":float(r.year_gap)
            })
    return pd.DataFrame([fit_species_response(sp,events.get(sp,[])) for sp in sorted(all_species)])

def wls_test(d,predictor,expected_sign):
    x=d[np.isfinite(pd.to_numeric(d[predictor],errors="coerce")) &
        np.isfinite(pd.to_numeric(d["adjusted_log_odds"],errors="coerce")) &
        np.isfinite(pd.to_numeric(d["weight"],errors="coerce"))].copy()
    if len(x)<15 or x[predictor].nunique()<2:
        return {"estimable":False,"predictor":predictor,"n_species":int(len(x)),"reason":"insufficient_species_or_variation"},x
    f=smf.wls(f"adjusted_log_odds ~ {predictor}",data=x,weights=x.weight).fit(cov_type="HC3")
    b=float(f.params[predictor]);se=float(f.bse[predictor]);p=float(f.pvalues[predictor])
    lo=b-Q*se;hi=b+Q*se
    rho,prho=spearmanr(x[predictor].astype(float),x["adjusted_log_odds"].astype(float))
    support=(hi<0) if expected_sign=="negative" else (lo>0)
    return {
        "estimable":True,"predictor":predictor,"n_species":int(len(x)),
        "beta":b,"se_hc3":se,"ci95_beta":[lo,hi],"p_value":p,
        "expected_sign":expected_sign,"directional_ci_support":bool(support),
        "spearman_rho":float(rho),"spearman_p":float(prho)
    },x

def family_map(species):
    t,blob=trait.load_traits()
    idx={s:i for i,s in enumerate(t["species_norm"].tolist())}
    out={};audit=[]
    for sp in species:
        candidates=[sp]
        toks=sp.split()
        if len(toks)==2 and toks[0] in trait.ALIASES:
            candidates.append(trait.ALIASES[toks[0]]+" "+toks[1])
        hits=[c for c in candidates if c in idx]
        if sp in hits:
            chosen=sp
        elif len(hits)==1:
            chosen=hits[0]
        else:
            chosen=None
        fam=""
        if chosen is not None:
            fam=str(t.iloc[idx[chosen]].get("Family","") or "").strip()
        out[sp]=fam
        audit.append({"species":sp,"matched":bool(fam),"amphibio_species":chosen,"family":fam})
    return out,audit,blob

def family_adjusted_test(x,predictor):
    y=x[x["family"].astype(str)!=""].copy()
    if len(y)<18 or y["family"].nunique()<2:
        return {"estimable":False,"n_species":int(len(y)),"reason":"insufficient_family_coverage"}
    formula=f"adjusted_log_odds ~ {predictor} + C(family)"
    f=smf.wls(formula,data=y,weights=y.weight).fit(cov_type="HC3")
    if f.df_resid<10:
        return {
            "estimable":False,"n_species":int(len(y)),"n_families":int(y.family.nunique()),
            "df_resid":float(f.df_resid),"reason":"residual_df_below_10"
        }
    b=float(f.params[predictor]);se=float(f.bse[predictor]);p=float(f.pvalues[predictor])
    lo=b-Q*se;hi=b+Q*se
    return {
        "estimable":True,"n_species":int(len(y)),"n_families":int(y.family.nunique()),
        "df_resid":float(f.df_resid),"beta":b,"se_hc3":se,
        "ci95_beta":[lo,hi],"p_value":p
    }

def within_family_permutation(x,predictor):
    y=x[(x["family"].astype(str)!="") & np.isfinite(pd.to_numeric(x[predictor],errors="coerce"))].copy()
    if len(y)<15:
        return {"estimable":False,"n_species":int(len(y)),"reason":"below_minimum"}
    families={str(fam):g.index.to_numpy() for fam,g in y.groupby("family")}
    if len(families)<2:
        return {"estimable":False,"n_species":int(len(y)),"reason":"too_few_families"}
    yy=np.asarray(y["adjusted_log_odds"],float)
    ww=np.asarray(y["weight"],float)
    base_x=np.asarray(y[predictor],float)
    pos={idx:i for i,idx in enumerate(y.index)}

    def stat(xx):
        xc=np.zeros(len(y));yc=np.zeros(len(y))
        for fam,idxs in families.items():
            loc=np.array([pos[i] for i in idxs],int)
            wf=ww[loc]
            mx=np.sum(wf*xx[loc])/np.sum(wf)
            my=np.sum(wf*yy[loc])/np.sum(wf)
            xc[loc]=xx[loc]-mx
            yc[loc]=yy[loc]-my
        denom=np.sum(ww*xc*xc)
        return np.nan if denom<=0 else float(np.sum(ww*xc*yc)/denom)

    obs=stat(base_x)
    if not np.isfinite(obs):
        return {"estimable":False,"n_species":int(len(y)),"reason":"no_within_family_predictor_variation"}

    rng=np.random.default_rng(SEED)
    vals=np.empty(B,float)
    for b in range(B):
        xx=base_x.copy()
        for fam,idxs in families.items():
            loc=np.array([pos[i] for i in idxs],int)
            if len(loc)>1:
                xx[loc]=rng.permutation(xx[loc])
        vals[b]=stat(xx)
    vals=vals[np.isfinite(vals)]
    p2=(1+np.sum(np.abs(vals)>=abs(obs)))/(1+len(vals))
    neg=(1+np.sum(vals<=obs))/(1+len(vals))
    posp=(1+np.sum(vals>=obs))/(1+len(vals))
    return {
        "estimable":True,"n_species":int(len(y)),"n_families":int(len(families)),
        "observed_weighted_within_family_slope":obs,
        "permutations":int(len(vals)),"seed":SEED,
        "two_sided_p":float(p2),"negative_tail_p":float(neg),"positive_tail_p":float(posp),
        "permutation_mean":float(np.mean(vals)),"permutation_sd":float(np.std(vals,ddof=1)),
        "q025":float(np.quantile(vals,.025)),"q975":float(np.quantile(vals,.975))
    }

def main():
    raw=base.load()
    d,sets=base.build_runs(raw)

    btraits=baseline_traits(d,sets)
    v_runs,pairs=validation_pairs(d,sets)
    vresp=validation_species_responses(pairs,sets)
    vresp=vresp[vresp["estimable"]==True].copy()

    merged=vresp.merge(btraits,on="species",how="inner")
    fam,audit,blob=family_map(merged["species"].tolist())
    merged["family"]=merged["species"].map(fam).fillna("")

    primary,x1=wls_test(merged,"baseline_recurrence_logit","negative")
    secondary,x2=wls_test(merged,"baseline_seasonal_concentration","positive")

    p_fam=family_adjusted_test(x1.assign(family=x1["species"].map(fam).fillna("")),"baseline_recurrence_logit") if primary.get("estimable") else {"estimable":False,"reason":"primary_nonestimable"}
    s_fam=family_adjusted_test(x2.assign(family=x2["species"].map(fam).fillna("")),"baseline_seasonal_concentration") if secondary.get("estimable") else {"estimable":False,"reason":"secondary_nonestimable"}
    p_perm=within_family_permutation(x1.assign(family=x1["species"].map(fam).fillna("")),"baseline_recurrence_logit") if primary.get("estimable") else {"estimable":False,"reason":"primary_nonestimable"}
    s_perm=within_family_permutation(x2.assign(family=x2["species"].map(fam).fillna("")),"baseline_seasonal_concentration") if secondary.get("estimable") else {"estimable":False,"reason":"secondary_nonestimable"}

    if primary.get("estimable") and secondary.get("estimable"):
        zz=merged[
            np.isfinite(merged["baseline_recurrence_logit"]) &
            np.isfinite(merged["baseline_seasonal_concentration"])
        ].copy()
        if len(zz)>=3:
            a=-zz["baseline_recurrence_logit"].astype(float)
            b=zz["baseline_seasonal_concentration"].astype(float)
            za=(a-a.mean())/a.std(ddof=0)
            zb=(b-b.mean())/b.std(ddof=0)
            zz["episodicity_index"]=(za+zb)/2
            rho,pr=spearmanr(zz["episodicity_index"],zz["adjusted_log_odds"])
            combined={
                "n_species":int(len(zz)),
                "spearman_rho":float(rho),"p_value":float(pr),
                "authorized_as_inferential":bool(primary["directional_ci_support"] and secondary["directional_ci_support"])
            }
        else:
            combined={"n_species":int(len(zz)),"authorized_as_inferential":False}
    else:
        combined={"authorized_as_inferential":False}

    result={
        "analysis":"naamp_crossperiod_episodic_recruitment_v0_1",
        "contract":"NAAMP_CROSSPERIOD_EPISODIC_RECRUITMENT_CONTRACT_V0_1.json",
        "time_split":{"baseline":[2001,2007],"validation":[2008,2015]},
        "baseline":{
            "eligible_runs":int(len(d[d["SurveyYear"].isin(BASELINE_YEARS)])),
            "trait_species":int(len(btraits))
        },
        "validation":{
            "eligible_runs":int(len(v_runs)),
            "matched_pairs":int(len(pairs)),
            "estimable_species_responses":int(len(vresp))
        },
        "crossperiod_matched_species":int(len(merged)),
        "primary_baseline_recurrence":primary,
        "secondary_seasonal_concentration":secondary,
        "combined_episodicity_descriptive":combined,
        "family_sensitivities":{
            "family_source":{"dataset":"AmphiBIO v1","git_blob_sha1":blob},
            "taxonomy_audit":audit,
            "primary_family_adjusted":p_fam,
            "secondary_family_adjusted":s_fam,
            "primary_within_family_permutation":p_perm,
            "secondary_within_family_permutation":s_perm
        },
        "species_table":[
            {
                "species":str(r.species),
                "baseline_routes":int(r.baseline_routes),
                "baseline_eligible_runs":int(r.baseline_eligible_runs),
                "baseline_active_runs":int(r.baseline_active_runs),
                "baseline_recurrence":float(r.baseline_recurrence),
                "baseline_recurrence_logit":float(r.baseline_recurrence_logit),
                "baseline_windows_with_effort":int(r.baseline_windows_with_effort),
                "baseline_seasonal_concentration":None if not np.isfinite(r.baseline_seasonal_concentration) else float(r.baseline_seasonal_concentration),
                "validation_events":int(r.n_events),
                "validation_routes":int(r.n_routes),
                "validation_adjusted_log_odds":float(r.adjusted_log_odds),
                "validation_adjusted_wet_probability":float(r.adjusted_wet_probability),
                "validation_se":float(r.adjusted_se),
                "family":str(r.family)
            }
            for r in merged.itertuples(index=False)
        ],
        "interpretation_boundary":{
            "baseline_traits_use_validation_years":False,
            "validation_response_uses_baseline_years":False,
            "same_species_temporal_holdout":True,
            "occupancy_claim":False,
            "causal_claim_authorized":False
        }
    }

    Path("NAAMP_CROSSPERIOD_EPISODIC_RECRUITMENT_RECEIPT_V0_1.json").write_text(
        json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8"
    )
    print(json.dumps(result,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
