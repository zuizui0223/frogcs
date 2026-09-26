#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import io
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

def loadmod(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    mod=importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(mod)
    return mod

base=loadmod("pulse_base",ROOT/"run_naamp_ecological_pulse.py")
spatial=loadmod("spatial_base",ROOT/"run_naamp_spatial_taxonomic_activation_decomposition.py")
func=loadmod("functional_base",ROOT/"run_naamp_functional_community_expansion.py")

Q=1.959963984540054
EARLY=set(range(2001,2008))
LATE=set(range(2008,2016))
N_PERM=100000
SEED=2026092601

def early_breadth(runs,sets,sampled,stop_species):
    early=runs[runs["SurveyYear"].isin(EARLY)].copy()
    vals=defaultdict(list)
    vals_active=defaultdict(list)
    routes=defaultdict(set)

    for r in early.itertuples(index=False):
        rid=str(r.RunID)
        stops=sorted(sampled[rid])
        if len(stops)!=10:
            raise RuntimeError(f"early eligible run not 10-stop: {rid}")
        by={st:set(stop_species.get((rid,st),set())) for st in stops}
        active=[st for st in stops if by[st]]
        for sp in sets[rid]:
            n=sum(sp in by[st] for st in stops)
            if n<=0:
                raise RuntimeError(f"route-set species absent from stop matrix: {rid} {sp}")
            vals[sp].append(n/10.0)
            vals_active[sp].append(n/len(active) if active else np.nan)
            routes[sp].add(str(r.route_cluster))

    rows=[]
    for sp in sorted(vals):
        a=np.asarray(vals[sp],float)
        b=np.asarray(vals_active[sp],float)
        good=np.isfinite(b)
        if len(a)<20 or len(routes[sp])<10:
            continue
        rows.append({
            "species":sp,
            "early_presence_runs":int(len(a)),
            "early_routes":int(len(routes[sp])),
            "early_spatial_breadth":float(np.mean(a)),
            "early_spatial_breadth_sd":float(np.std(a,ddof=0)),
            "early_active_footprint_fraction":float(np.mean(b[good])) if good.any() else np.nan
        })
    return early,pd.DataFrame(rows)

def fit_species_response(sp,events):
    x=pd.DataFrame(events)
    nr=x["route_cluster"].nunique() if len(x) else 0
    if len(x)<25 or nr<8:
        return None
    for c in ["rain_contrast","temp_difference","doy_difference","year_gap"]:
        x["c_"+c]=x[c]-x[c].mean()
    formula="y ~ c_rain_contrast + c_temp_difference + c_doy_difference + c_year_gap"
    try:
        f=smf.glm(formula,data=x,family=sm.families.Binomial()).fit(
            cov_type="cluster",cov_kwds={"groups":x["route_cluster"]}
        )
        b=float(f.params["Intercept"]);se=float(f.bse["Intercept"])
        if not np.isfinite(b) or not np.isfinite(se) or se<=0:
            return None
        return {
            "species":sp,
            "late_adjusted_log_odds":b,
            "late_se":se,
            "late_weight":float(1/(se*se)),
            "late_events":int(len(x)),
            "late_routes":int(nr),
            "late_wet_probability":float(1/(1+np.exp(-b)))
        }
    except Exception:
        return None

def late_responses(runs,sets):
    late=runs[runs["SurveyYear"].isin(LATE)].copy()
    pairs=base.pair_runs(late,sets)
    events=defaultdict(list)
    for r in pairs.itertuples(index=False):
        W=sets[str(r.wet_RunID)];D=sets[str(r.dry_RunID)]
        for sp in W^D:
            events[sp].append({
                "y":int(sp in W),
                "route_cluster":str(r.route_cluster),
                "rain_contrast":float(r.rain_contrast),
                "temp_difference":float(r.temp_difference),
                "doy_difference":float(r.doy_difference),
                "year_gap":float(r.year_gap)
            })
    rows=[]
    for sp in sorted(events):
        z=fit_species_response(sp,events[sp])
        if z is not None:
            rows.append(z)
    return late,pairs,pd.DataFrame(rows)

def zscore(x):
    a=np.asarray(x,float)
    sd=float(np.std(a,ddof=0))
    if not sd>0:
        raise RuntimeError("zero predictor variance")
    return (a-float(np.mean(a)))/sd

def fit_wls(m,predictor):
    x=m.copy()
    zname="z_"+predictor
    x[zname]=zscore(x[predictor])
    f=smf.wls(
        f"late_adjusted_log_odds ~ {zname}",
        data=x,weights=x["late_weight"]
    ).fit(cov_type="HC3")
    b=float(f.params[zname]);se=float(f.bse[zname]);p=float(f.pvalues[zname])
    return {
        "predictor":predictor,
        "z_predictor":zname,
        "n_species":int(len(x)),
        "beta":b,
        "se_hc3":se,
        "ci95":[b-Q*se,b+Q*se],
        "p_value":p,
        "negative_ci_support":bool(b<0 and b+Q*se<0)
    }

def load_amphibio_meta(species):
    b=func.getb(func.URL)
    if func.blobsha(b)!=func.BLOB:
        raise RuntimeError("AmphiBIO drift")
    try:t=pd.read_csv(io.BytesIO(b),encoding="utf-8")
    except UnicodeDecodeError:t=pd.read_csv(io.BytesIO(b),encoding="cp1252")
    t["sp"]=t["Species"].map(func.norm);idx={s:i for i,s in enumerate(t["sp"])}
    out={}
    for sp0 in species:
        sp=func.norm(sp0);cands=[sp];tok=sp.split()
        if len(tok)==2 and tok[0] in func.ALIASES:
            cands.append(func.ALIASES[tok[0]]+" "+tok[1])
        hits=[c for c in cands if c in idx]
        chosen=sp if sp in hits else (hits[0] if len(hits)==1 else None)
        if chosen is None:
            out[sp0]={"family":"","body_size_mm":np.nan}
            continue
        rr=t.iloc[idx[chosen]]
        fam=str(rr.get("Family","") or "").strip()
        bs=pd.to_numeric(rr.get("Body_size_mm",np.nan),errors="coerce")
        out[sp0]={"family":fam,"body_size_mm":float(bs) if np.isfinite(bs) and bs>0 else np.nan}
    return out

def weighted_slope(x,y,w):
    x=np.asarray(x,float);y=np.asarray(y,float);w=np.asarray(w,float)
    mx=float(np.sum(w*x)/np.sum(w));my=float(np.sum(w*y)/np.sum(w))
    den=float(np.sum(w*(x-mx)**2))
    if den<=0:return np.nan
    return float(np.sum(w*(x-mx)*(y-my))/den)

def family_permutation(m):
    x=m.copy().reset_index(drop=True)
    meta=load_amphibio_meta(x["species"].tolist())
    x["family"]=[meta[s]["family"] for s in x["species"]]
    x=x[x["family"].astype(str)!=""].copy().reset_index(drop=True)
    if len(x)<15:
        return {"estimable":False,"n_species":int(len(x)),"reason":"family_coverage_below_minimum"}

    x["z_breadth"]=zscore(x["early_spatial_breadth"])
    observed=weighted_slope(
        x["z_breadth"],x["late_adjusted_log_odds"],x["late_weight"]
    )
    groups=[g.index.to_numpy() for _,g in x.groupby("family") if len(g)>=2]
    if not groups:
        return {"estimable":False,"n_species":int(len(x)),"reason":"no_multispecies_families"}

    rng=np.random.default_rng(SEED)
    y0=x["late_adjusted_log_odds"].to_numpy(float)
    w0=x["late_weight"].to_numpy(float)
    xv=x["z_breadth"].to_numpy(float)
    null=np.empty(N_PERM,float)
    for b in range(N_PERM):
        y=y0.copy();w=w0.copy()
        for idx in groups:
            perm=rng.permutation(idx)
            y[idx]=y0[perm]
            w[idx]=w0[perm]
        null[b]=weighted_slope(xv,y,w)
    null=null[np.isfinite(null)]
    p2=float((1+np.sum(np.abs(null)>=abs(observed)))/(1+len(null)))
    pneg=float((1+np.sum(null<=observed))/(1+len(null)))
    return {
        "estimable":True,
        "n_species":int(len(x)),
        "n_families":int(x["family"].nunique()),
        "family_counts":{str(k):int(v) for k,v in x["family"].value_counts().to_dict().items()},
        "observed_weighted_slope":float(observed),
        "permutations":int(len(null)),
        "seed":SEED,
        "two_sided_p":p2,
        "negative_tail_p":pneg,
        "negative_support":bool(pneg<0.05),
        "null_mean":float(np.mean(null)),
        "null_sd":float(np.std(null,ddof=0))
    }

def tertiles(m):
    x=m.copy()
    q1=float(x["early_spatial_breadth"].quantile(1/3))
    q2=float(x["early_spatial_breadth"].quantile(2/3))
    def grp(v):
        if v<=q1:return "narrow"
        if v>=q2:return "broad"
        return "middle"
    x["breadth_group"]=x["early_spatial_breadth"].map(grp)
    out={}
    for g,d in x.groupby("breadth_group"):
        w=d["late_weight"].to_numpy(float);y=d["late_adjusted_log_odds"].to_numpy(float)
        out[str(g)]={
            "n_species":int(len(d)),
            "weighted_mean_late_log_odds":float(np.sum(w*y)/np.sum(w)),
            "mean_late_wet_probability":float(d["late_wet_probability"].mean()),
            "species":sorted(d["species"].astype(str).tolist())
        }
    return {"q33":q1,"q67":q2,"groups":out}

def body_size_corr(m):
    meta=load_amphibio_meta(m["species"].tolist())
    rows=[]
    for r in m.itertuples(index=False):
        bs=meta[str(r.species)]["body_size_mm"]
        if np.isfinite(bs):
            rows.append((float(r.early_spatial_breadth),math.log(bs)))
    if len(rows)<10:
        return {"estimable":False,"n_species":len(rows)}
    a=np.asarray(rows,float)
    rho,p=spearmanr(a[:,0],a[:,1])
    return {"estimable":True,"n_species":int(len(a)),"spearman_rho":float(rho),"p_value":float(p)}

def main():
    raw=base.load()
    runs,sets=base.build_runs(raw)
    eligible=set(runs["RunID"].astype(str))
    sampled,stop_species=spatial.stop_matrix(raw,eligible)

    early,breadth=early_breadth(runs,sets,sampled,stop_species)
    late,late_pairs,response=late_responses(runs,sets)
    m=breadth.merge(response,on="species",how="inner",validate="one_to_one")
    if len(m)<15:
        raise SystemExit(f"intersection below minimum: {len(m)}")

    primary=fit_wls(m,"early_spatial_breadth")
    sens=fit_wls(m[np.isfinite(m["early_active_footprint_fraction"])].copy(),
                 "early_active_footprint_fraction")
    rho,p=spearmanr(m["early_spatial_breadth"],m["late_adjusted_log_odds"])

    result={
        "analysis":"naamp_spatial_niche_breadth_response_v0_1",
        "contract":"NAAMP_SPATIAL_NICHE_BREADTH_RESPONSE_CONTRACT_V0_1.json",
        "time_split":{"trait_period":[2001,2007],"validation_period":[2008,2015]},
        "early":{
            "eligible_runs":int(len(early)),
            "eligible_breadth_species":int(len(breadth))
        },
        "late":{
            "eligible_runs":int(len(late)),
            "matched_pairs":int(len(late_pairs)),
            "estimable_response_species":int(len(response))
        },
        "intersection_species":int(len(m)),
        "primary":primary,
        "active_footprint_fraction_sensitivity":sens,
        "family_permutation":family_permutation(m),
        "secondary":{
            "spearman_rho":float(rho),
            "spearman_p":float(p),
            "breadth_tertiles":tertiles(m),
            "body_size_correlation":body_size_corr(m)
        },
        "species_table":[
            {
              "species":str(r.species),
              "early_presence_runs":int(r.early_presence_runs),
              "early_routes":int(r.early_routes),
              "early_spatial_breadth":float(r.early_spatial_breadth),
              "early_active_footprint_fraction":float(r.early_active_footprint_fraction),
              "late_events":int(r.late_events),
              "late_routes":int(r.late_routes),
              "late_adjusted_log_odds":float(r.late_adjusted_log_odds),
              "late_se":float(r.late_se),
              "late_wet_probability":float(r.late_wet_probability)
            }
            for r in m.itertuples(index=False)
        ],
        "interpretation_boundary":{
            "spatial_breadth":"Early-period acoustic stop-use breadth, not occupancy niche breadth or dispersal ability.",
            "temporal_holdout":True,
            "causal_rainfall_claim_authorized":False,
            "physiological_mechanism_claim_authorized":False,
            "endpoint_retuning_after_readback_authorized":False
        }
    }
    Path("NAAMP_SPATIAL_NICHE_BREADTH_RESPONSE_RECEIPT_V0_1.json").write_text(
        json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
