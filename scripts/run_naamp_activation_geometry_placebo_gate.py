#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from scipy.special import logit
from scipy.stats import spearmanr

ROOT=Path(__file__).resolve().parent
Q=1.959963984540054
RHO_STRONG=0.60

def loadmod(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    mod=importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(mod)
    return mod

geom=loadmod("activation_geometry",ROOT/"run_naamp_species_activation_geometry_repeatability.py")
base=geom.base
spatial=geom.spatial

def headline_species():
    obj=json.loads(Path("NAAMP_SPECIES_ACTIVATION_GEOMETRY_REPEATABILITY_SUMMARY_V0_1.json").read_text())
    spp=[str(x["species"]) for x in obj["species_table"]]
    if len(spp)!=16 or len(set(spp))!=16:
        raise RuntimeError(f"headline family drift: n={len(spp)} unique={len(set(spp))}")
    return spp

def gain_rows_from_pairs(pairs,sampled,stop_species,direction):
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

        if direction=="wet":
            ref=W
            other=D
            ref_run=w
            other_run=d
            other_inactive={st:(len(D[st])==0) for st in stops}
        elif direction=="dry":
            ref=D
            other=W
            ref_run=d
            other_run=w
            other_inactive={st:(len(W[st])==0) for st in stops}
        else:
            raise ValueError(direction)

        q=sum(other_inactive.values())/10.0
        if q<=0 or q>=1:
            structural_uninformative+=1
            continue

        by=defaultdict(lambda:[0,0])
        for st in stops:
            for sp in ref[st]-other[st]:
                by[sp][1]+=1
                if other_inactive[st]:
                    by[sp][0]+=1

        for sp,(succ,total) in by.items():
            if total<=0:
                continue
            rows.append({
                "species":sp,
                "route_cluster":str(p.route_cluster),
                "State":str(p.State),
                "RouteNumber":str(p.RouteNumber),
                "RunNumber":str(p.RunNumber),
                "wet_RunID":w,
                "dry_RunID":d,
                "reference_RunID":ref_run,
                "comparison_RunID":other_run,
                "successes":int(succ),
                "failures":int(total-succ),
                "total":int(total),
                "q_pair":float(q),
                "offset_logit_q":float(logit(q)),
                "raw_new_site_fraction":float(succ/total),
                "rain_contrast":float(p.rain_contrast)
            })
    return pd.DataFrame(rows),structural_uninformative

def baseline_solitude_rows(runs,sampled,stop_species):
    rows=[]
    raw=defaultdict(lambda:[0,0])
    structural_uninformative=0
    for r in runs.itertuples(index=False):
        rid=str(r.RunID)
        stops=sorted(sampled[rid])
        if len(stops)!=10:
            raise RuntimeError(f"eligible run lacks ten stops: {rid}")
        by={st:set(stop_species.get((rid,st),set())) for st in stops}
        active=[st for st in stops if by[st]]
        if not active:
            continue

        singleton={st:(len(by[st])==1) for st in active}
        q=sum(singleton.values())/len(active)

        per=defaultdict(lambda:[0,0])
        for st in active:
            for sp in by[st]:
                per[sp][1]+=1
                raw[sp][1]+=1
                if singleton[st]:
                    per[sp][0]+=1
                    raw[sp][0]+=1

        if q<=0 or q>=1:
            structural_uninformative+=1
            continue

        for sp,(succ,total) in per.items():
            rows.append({
                "species":sp,
                "route_cluster":str(r.route_cluster),
                "State":str(r.State),
                "RouteNumber":str(r.RouteNumber),
                "RunNumber":str(r.RunNumber),
                "RunID":rid,
                "successes":int(succ),
                "failures":int(total-succ),
                "total":int(total),
                "q_pair":float(q),
                "offset_logit_q":float(logit(q)),
                "raw_new_site_fraction":float(succ/total)
            })

    raw_fraction={
        sp:(succ/total if total>0 else np.nan)
        for sp,(succ,total) in raw.items()
    }
    return pd.DataFrame(rows),raw_fraction,structural_uninformative

def fit_fixed_family(rows,species):
    allfit=geom.fit_period(rows)
    if len(allfit)==0:
        return pd.DataFrame(columns=["species","estimable"])
    x=allfit[allfit["species"].isin(species)].copy()
    missing=[sp for sp in species if sp not in set(x["species"])]
    for sp in missing:
        x=pd.concat([x,pd.DataFrame([{"species":sp,"estimable":False,"reason":"no_rows"}])],ignore_index=True)
    return x.sort_values("species").reset_index(drop=True)

def estimable_table(fit,label):
    x=fit[fit["estimable"]==True].copy()
    return x[["species","activation_geometry_log_odds","se_cluster"]].rename(columns={
        "activation_geometry_log_odds":label,
        "se_cluster":label+"_se"
    })

def coupling(a,b,label):
    m=a.merge(b,on="species",how="inner",validate="one_to_one")
    if len(m)<12:
        return {
            "label":label,
            "n_species":int(len(m)),
            "estimable":False,
            "strong_same_rank_coupling":False,
            "reason":"below_frozen_minimum_12"
        },m
    rho,p=spearmanr(m.iloc[:,1],m.iloc[:,3])
    strong=bool(rho>=RHO_STRONG and p<0.05)

    wet_col=a.columns[1]
    other_col=b.columns[1]
    w=1/(m[wet_col+"_se"]**2)
    reg=smf.wls(f"{wet_col} ~ {other_col}",data=m,weights=w).fit(cov_type="HC3")
    beta=float(reg.params[other_col]);se=float(reg.bse[other_col])
    return {
        "label":label,
        "n_species":int(len(m)),
        "estimable":True,
        "spearman_rho":float(rho),
        "two_sided_p":float(p),
        "strong_same_rank_coupling":strong,
        "wls_beta_wet_on_placebo":beta,
        "wls_ci95":[beta-Q*se,beta+Q*se],
        "wls_p_value":float(reg.pvalues[other_col])
    },m

def raw_singleton_coupling(wet,raw_fraction):
    x=wet.copy()
    x["raw_singleton_fraction"]=x["species"].map(raw_fraction)
    x=x[np.isfinite(x["raw_singleton_fraction"])].copy()
    if len(x)<12:
        return {"n_species":int(len(x)),"estimable":False}
    rho,p=spearmanr(x["wet_geometry"],x["raw_singleton_fraction"])
    return {
        "n_species":int(len(x)),
        "estimable":True,
        "spearman_rho":float(rho),
        "two_sided_p":float(p),
        "strong_same_rank_coupling_descriptive":bool(rho>=RHO_STRONG and p<0.05)
    }

def main():
    family=headline_species()
    raw=base.load()
    runs,route_sets=base.build_runs(raw)
    eligible=set(runs["RunID"].astype(str))
    sampled,stop_species=spatial.stop_matrix(raw,eligible)
    pairs=base.pair_runs(runs,route_sets).copy()

    wet_rows,wet_uninf=gain_rows_from_pairs(pairs,sampled,stop_species,"wet")
    dry_rows,dry_uninf=gain_rows_from_pairs(pairs,sampled,stop_species,"dry")

    cutoff=float(pairs["rain_contrast"].quantile(.25))
    low_pairs=pairs[pairs["rain_contrast"]<=cutoff].copy()
    low_rows,low_uninf=gain_rows_from_pairs(low_pairs,sampled,stop_species,"wet")

    baseline_rows,raw_singleton,base_uninf=baseline_solitude_rows(runs,sampled,stop_species)

    wet_fit=fit_fixed_family(wet_rows,family)
    dry_fit=fit_fixed_family(dry_rows,family)
    low_fit=fit_fixed_family(low_rows,family)
    baseline_fit=fit_fixed_family(baseline_rows,family)

    wet=estimable_table(wet_fit,"wet_geometry")
    dry=estimable_table(dry_fit,"reverse_dry_geometry")
    low=estimable_table(low_fit,"low_contrast_geometry")
    baseline=estimable_table(baseline_fit,"baseline_solitude_geometry")

    rev,m_rev=coupling(wet,dry,"wet_vs_reverse_dry")
    lowc,m_low=coupling(wet,low,"wet_vs_low_contrast")
    basec,m_base=coupling(wet,baseline,"wet_vs_baseline_solitude")
    rawc=raw_singleton_coupling(wet,raw_singleton)

    primary=[rev,lowc,basec]
    gate_pass=bool(all(not x.get("strong_same_rank_coupling",False) for x in primary if x.get("estimable",False))
                   and all(x.get("estimable",False) for x in primary))

    joined=pd.DataFrame({"species":family})
    for tbl in [wet,dry,low,baseline]:
        joined=joined.merge(tbl,on="species",how="left")
    joined["raw_singleton_fraction"]=joined["species"].map(raw_singleton)

    result={
        "analysis":"naamp_activation_geometry_placebo_gate_v0_1",
        "contract":"NAAMP_ACTIVATION_GEOMETRY_PLACEBO_CONTRACT_V0_1.json",
        "headline_family_species":family,
        "sample":{
            "eligible_runs":int(len(runs)),
            "matched_pairs":int(len(pairs)),
            "low_contrast_cutpoint_q25":cutoff,
            "low_contrast_pairs":int(len(low_pairs)),
            "wet_structurally_uninformative_pairs":int(wet_uninf),
            "reverse_structurally_uninformative_pairs":int(dry_uninf),
            "low_contrast_structurally_uninformative_pairs":int(low_uninf),
            "baseline_structurally_uninformative_runs":int(base_uninf)
        },
        "estimable_counts":{
            "wet_geometry":int(len(wet)),
            "reverse_dry_geometry":int(len(dry)),
            "low_contrast_geometry":int(len(low)),
            "baseline_solitude_geometry":int(len(baseline))
        },
        "primary_placebo_couplings":{
            "reverse_direction":rev,
            "low_contrast":lowc,
            "baseline_solitude":basec
        },
        "raw_singleton_fraction_correlation":rawc,
        "headline_gate_pass":gate_pass,
        "headline_gate_decision":"retain_activation_geometry_in_title" if gate_pass else "demote_activation_geometry_from_title",
        "species_table":joined.replace({np.nan:None}).to_dict(orient="records"),
        "interpretation_boundary":{
            "strong_same_rank_threshold_rho":RHO_STRONG,
            "strong_same_rank_requires_p_below":0.05,
            "no_causal_claim":True,
            "no_redefinition_after_readback":True
        }
    }

    Path("NAAMP_ACTIVATION_GEOMETRY_PLACEBO_RECEIPT_V0_1.json").write_text(
        json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8"
    )
    print(json.dumps(result,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
