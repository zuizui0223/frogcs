#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import io
import json
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from scipy.special import logit
from scipy.stats import spearmanr, binomtest

ROOT=Path(__file__).resolve().parent
Q=1.959963984540054
EARLY=set(range(2001,2008))
LATE=set(range(2008,2016))

def loadmod(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    mod=importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(mod)
    return mod

base=loadmod("pulse_base",ROOT/"run_naamp_ecological_pulse.py")
spatial=loadmod("spatial_base",ROOT/"run_naamp_spatial_taxonomic_activation_decomposition.py")
func=loadmod("functional_base",ROOT/"run_naamp_functional_community_expansion.py")

def period_gain_rows(runs,route_sets,sampled,stop_species,years):
    pruns=runs[runs["SurveyYear"].isin(years)].copy()
    pairs=base.pair_runs(pruns,route_sets).copy()
    rows=[]
    structural_uninformative=0
    for p in pairs.itertuples(index=False):
        w,d=str(p.wet_RunID),str(p.dry_RunID)
        sw=set(sampled[w]);sd=set(sampled[d])
        if len(sw)!=10 or sw!=sd:
            raise RuntimeError(f"stop alignment failed wet={w} dry={d}")
        stops=sorted(sw)
        W={st:set(stop_species.get((w,st),set())) for st in stops}
        D={st:set(stop_species.get((d,st),set())) for st in stops}
        dry_inactive={st:(len(D[st])==0) for st in stops}
        q=sum(dry_inactive.values())/10.0
        if q<=0 or q>=1:
            structural_uninformative+=1
            continue
        gain_by=defaultdict(lambda:[0,0])
        for st in stops:
            for sp in W[st]-D[st]:
                gain_by[sp][1]+=1
                if dry_inactive[st]:
                    gain_by[sp][0]+=1
        for sp,(succ,total) in gain_by.items():
            if total<=0: continue
            rows.append({
                "species":sp,
                "route_cluster":str(p.route_cluster),
                "State":str(p.State),
                "RouteNumber":str(p.RouteNumber),
                "RunNumber":str(p.RunNumber),
                "wet_RunID":w,"dry_RunID":d,
                "successes":int(succ),
                "failures":int(total-succ),
                "total":int(total),
                "q_pair":float(q),
                "offset_logit_q":float(logit(q)),
                "raw_new_site_fraction":float(succ/total)
            })
    return pruns,pairs,pd.DataFrame(rows),structural_uninformative

def fit_species(sp,d):
    x=d[d["species"]==sp].copy()
    ninc=int(x["total"].sum()) if len(x) else 0
    nr=int(x["route_cluster"].nunique()) if len(x) else 0
    npairs=int(len(x))
    if ninc<30 or nr<10 or npairs<15:
        return {
            "species":sp,"estimable":False,
            "n_informative_wet_gain_incidences":ninc,
            "n_routes":nr,"n_pairs":npairs,
            "reason":"period_eligibility"
        }
    endog=np.column_stack([x["successes"].to_numpy(int),x["failures"].to_numpy(int)])
    exog=np.ones((len(x),1),float)
    offset=x["offset_logit_q"].to_numpy(float)
    try:
        m=sm.GLM(endog,exog,family=sm.families.Binomial(),offset=offset)
        f=m.fit(cov_type="cluster",cov_kwds={"groups":x["route_cluster"].to_numpy()})
        b=float(f.params[0]);se=float(f.bse[0]);p=float(f.pvalues[0])
        if not np.isfinite(b) or not np.isfinite(se) or se<=0:
            raise ValueError("nonfinite geometry estimate")
        return {
            "species":sp,"estimable":True,
            "n_informative_wet_gain_incidences":ninc,
            "n_routes":nr,"n_pairs":npairs,
            "activation_geometry_log_odds":b,
            "se_cluster":se,
            "ci95":[b-Q*se,b+Q*se],
            "p_value":p,
            "raw_new_site_fraction":float(x["successes"].sum()/x["total"].sum()),
            "mean_available_inactive_fraction":float(np.average(x["q_pair"],weights=x["total"]))
        }
    except Exception as e:
        return {
            "species":sp,"estimable":False,
            "n_informative_wet_gain_incidences":ninc,
            "n_routes":nr,"n_pairs":npairs,
            "reason":str(e)
        }

def fit_period(rows):
    species=sorted(rows["species"].unique()) if len(rows) else []
    out=[fit_species(sp,rows) for sp in species]
    return pd.DataFrame(out)

def family_and_traits(species):
    b=func.getb(func.URL)
    if func.blobsha(b)!=func.BLOB:
        raise RuntimeError("AmphiBIO drift")
    try:t=pd.read_csv(io.BytesIO(b),encoding="utf-8")
    except UnicodeDecodeError:t=pd.read_csv(io.BytesIO(b),encoding="cp1252")
    t["sp"]=t["Species"].map(func.norm)
    idx={s:i for i,s in enumerate(t["sp"])}
    aliases=func.ALIASES
    out={}
    for sp0 in species:
        sp=func.norm(sp0); cands=[sp]; tok=sp.split()
        if len(tok)==2 and tok[0] in aliases:
            cands.append(aliases[tok[0]]+" "+tok[1])
        hits=[c for c in cands if c in idx]
        chosen=sp if sp in hits else (hits[0] if len(hits)==1 else None)
        if chosen is None:
            out[sp0]={"family":""}
            continue
        r=t.iloc[idx[chosen]]
        out[sp0]={
            "family":str(r.get("Family","") or "").strip(),
            "Body_size_mm":pd.to_numeric(r.get("Body_size_mm",np.nan),errors="coerce"),
            "Litter_size_min_n":pd.to_numeric(r.get("Litter_size_min_n",np.nan),errors="coerce"),
            "Litter_size_max_n":pd.to_numeric(r.get("Litter_size_max_n",np.nan),errors="coerce"),
            "Offspring_size_min_mm":pd.to_numeric(r.get("Offspring_size_min_mm",np.nan),errors="coerce"),
            "Offspring_size_max_mm":pd.to_numeric(r.get("Offspring_size_max_mm",np.nan),errors="coerce"),
            "Reproductive_output_y":pd.to_numeric(r.get("Reproductive_output_y",np.nan),errors="coerce")
        }
    return out

def weighted_regression(m):
    f=smf.wls(
        "late_geometry ~ early_geometry",
        data=m,weights=1/(m["late_se"]**2)
    ).fit(cov_type="HC3")
    b=float(f.params["early_geometry"]);se=float(f.bse["early_geometry"]);p=float(f.pvalues["early_geometry"])
    return {"beta":b,"se_hc3":se,"ci95":[b-Q*se,b+Q*se],"p_value":p,"positive_ci_support":bool(b-Q*se>0)}

def sign_concordance(m):
    use=m[(m["early_geometry"]!=0)&(m["late_geometry"]!=0)].copy()
    same=(np.sign(use["early_geometry"])==np.sign(use["late_geometry"]))
    n=int(len(use)); k=int(same.sum())
    bt=binomtest(k,n,p=.5,alternative="greater") if n else None
    return {
        "n_species":n,"same_sign":k,
        "fraction_same_sign":float(k/n) if n else None,
        "one_sided_binomial_p":float(bt.pvalue) if bt else None
    }

def family_adjusted(m):
    y=m[m["family"].astype(str)!=""].copy()
    if len(y)<18 or y["family"].nunique()<2:
        return {"estimable":False,"n_species":int(len(y)),"reason":"insufficient_family_coverage"}
    f=smf.wls(
        "late_geometry ~ early_geometry + C(family)",
        data=y,weights=1/(y["late_se"]**2)
    ).fit(cov_type="HC3")
    if f.df_resid<10:
        return {"estimable":False,"n_species":int(len(y)),"df_resid":float(f.df_resid),"reason":"residual_df_below_10"}
    b=float(f.params["early_geometry"]);se=float(f.bse["early_geometry"]);p=float(f.pvalues["early_geometry"])
    return {
        "estimable":True,"n_species":int(len(y)),"n_families":int(y["family"].nunique()),
        "df_resid":float(f.df_resid),"beta":b,"se_hc3":se,
        "ci95":[b-Q*se,b+Q*se],"p_value":p,
        "positive_ci_support":bool(b-Q*se>0)
    }

def trait_descriptives(m,meta):
    rows=[]
    for r in m.itertuples(index=False):
        z=meta.get(str(r.species),{})
        vals={}
        bs=z.get("Body_size_mm",np.nan)
        vals["log_body_size"]=np.log(bs) if np.isfinite(bs) and bs>0 else np.nan
        a,b=z.get("Litter_size_min_n",np.nan),z.get("Litter_size_max_n",np.nan)
        vals["log_clutch_size"]=.5*(np.log(a)+np.log(b)) if np.isfinite(a) and a>0 and np.isfinite(b) and b>0 else np.nan
        a,b=z.get("Offspring_size_min_mm",np.nan),z.get("Offspring_size_max_mm",np.nan)
        vals["log_offspring_size"]=.5*(np.log(a)+np.log(b)) if np.isfinite(a) and a>0 and np.isfinite(b) and b>0 else np.nan
        ro=z.get("Reproductive_output_y",np.nan)
        vals["log_reproductive_output"]=np.log(ro) if np.isfinite(ro) and ro>0 else np.nan
        rows.append({"species":r.species,"early_geometry":r.early_geometry,**vals})
    d=pd.DataFrame(rows)
    out={}
    for c in ["log_body_size","log_clutch_size","log_offspring_size","log_reproductive_output"]:
        x=d[np.isfinite(d[c])].copy()
        if len(x)>=10:
            rho,p=spearmanr(x["early_geometry"],x[c])
            out[c]={"n_species":int(len(x)),"spearman_rho":float(rho),"p_value_descriptive":float(p)}
        else:
            out[c]={"n_species":int(len(x)),"estimable":False}
    return out

def main():
    raw=base.load()
    runs,route_sets=base.build_runs(raw)
    eligible=set(runs["RunID"].astype(str))
    sampled,stop_species=spatial.stop_matrix(raw,eligible)

    eruns,epairs,erows,euninf=period_gain_rows(runs,route_sets,sampled,stop_species,EARLY)
    lruns,lpairs,lrows,luninf=period_gain_rows(runs,route_sets,sampled,stop_species,LATE)
    e=fit_period(erows);l=fit_period(lrows)
    ee=e[e["estimable"]==True].copy()
    ll=l[l["estimable"]==True].copy()

    m=ee.merge(ll,on="species",suffixes=("_early","_late"))
    if len(m)<15:
        raise SystemExit(f"overlap species below frozen minimum: {len(m)}")
    m=m.rename(columns={
        "activation_geometry_log_odds_early":"early_geometry",
        "se_cluster_early":"early_se",
        "activation_geometry_log_odds_late":"late_geometry",
        "se_cluster_late":"late_se"
    })

    meta=family_and_traits(m["species"].tolist())
    m["family"]=[meta[s]["family"] for s in m["species"]]

    rho,p=spearmanr(m["early_geometry"],m["late_geometry"])
    primary={
        "n_species":int(len(m)),
        "spearman_rho":float(rho),
        "p_value":float(p),
        "positive_support":bool(rho>0 and p<0.05)
    }
    wls=weighted_regression(m)
    signs=sign_concordance(m)
    fam=family_adjusted(m)
    traits=trait_descriptives(m,meta)

    result={
        "analysis":"naamp_species_activation_geometry_repeatability_v0_1",
        "contract":"NAAMP_SPECIES_ACTIVATION_GEOMETRY_REPEATABILITY_CONTRACT_V0_1.json",
        "time_split":{"early":[2001,2007],"late":[2008,2015]},
        "early":{
            "eligible_runs":int(len(eruns)),"matched_pairs":int(len(epairs)),
            "structurally_uninformative_pairs":int(euninf),
            "species_with_any_informative_gain":int(erows["species"].nunique()) if len(erows) else 0,
            "estimable_species":int(len(ee))
        },
        "late":{
            "eligible_runs":int(len(lruns)),"matched_pairs":int(len(lpairs)),
            "structurally_uninformative_pairs":int(luninf),
            "species_with_any_informative_gain":int(lrows["species"].nunique()) if len(lrows) else 0,
            "estimable_species":int(len(ll))
        },
        "overlap_species":int(len(m)),
        "primary_repeatability":primary,
        "weighted_regression_sensitivity":wls,
        "sign_concordance":signs,
        "family_adjusted_sensitivity":fam,
        "functional_trait_descriptives":traits,
        "species_table":[
            {
                "species":str(r.species),"family":str(r.family),
                "early_geometry":float(r.early_geometry),"early_se":float(r.early_se),
                "early_raw_new_site_fraction":float(r.raw_new_site_fraction_early),
                "early_mean_available_inactive_fraction":float(r.mean_available_inactive_fraction_early),
                "late_geometry":float(r.late_geometry),"late_se":float(r.late_se),
                "late_raw_new_site_fraction":float(r.raw_new_site_fraction_late),
                "late_mean_available_inactive_fraction":float(r.mean_available_inactive_fraction_late),
                "same_sign":bool(np.sign(r.early_geometry)==np.sign(r.late_geometry))
            }
            for r in m.itertuples(index=False)
        ],
        "interpretation_boundary":{
            "response_trait":"Opportunity-corrected acoustic gain placement on newly active versus already-active stops.",
            "occupancy_or_dispersal_trait":False,
            "same_species_temporal_validation":True,
            "independent_species_replication":False,
            "causal_rainfall_claim_authorized":False,
            "endpoint_retuning_after_readback_authorized":False
        }
    }
    Path("NAAMP_SPECIES_ACTIVATION_GEOMETRY_REPEATABILITY_RECEIPT_V0_1.json").write_text(
        json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8"
    )
    print(json.dumps(result,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
