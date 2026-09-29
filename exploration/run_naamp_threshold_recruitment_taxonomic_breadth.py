#!/usr/bin/env python3
from __future__ import annotations
import importlib.util, json
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr
import statsmodels.formula.api as smf

ROOT=Path(__file__).resolve().parents[1]
NAAMP=ROOT/"scripts"/"naamp"
OUT=ROOT/"exploration"/"NAAMP_THRESHOLD_RECRUITMENT_TAXONOMIC_BREADTH_RECEIPT_V0_1.json"
Q=1.959963984540054

def loadmod(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    mod=importlib.util.module_from_spec(spec); assert spec.loader; spec.loader.exec_module(mod); return mod

base=loadmod("base",NAAMP/"run_naamp_ecological_pulse.py")
spatial=loadmod("spatial",NAAMP/"run_naamp_spatial_taxonomic_activation_decomposition.py")
uniform=loadmod("uniform",NAAMP/"run_naamp_uniform_activation_null.py")

def build_ci(raw,eligible,sampled):
    vals=defaultdict(list)
    for r in raw["Counts.csv"]:
        rid=(r.get("RunID") or "").strip(); st=(r.get("StopNumber") or "").strip(); sp=(r.get("Species") or "").strip()
        if rid not in eligible or st not in sampled.get(rid,set()) or not sp: continue
        try: ci=int(float((r.get("CallingIndex") or "").strip()))
        except Exception: continue
        if ci in (1,2,3): vals[(rid,st,sp)].append(ci)
    by=defaultdict(dict); freq=Counter()
    for (rid,st,sp),v in vals.items():
        x=max(v); by[(rid,st)][sp]=x; freq[sp]+=1
    return by,freq

def strong_by_species(pair,sampled,by):
    wet=str(pair.wet_RunID); dry=str(pair.dry_RunID)
    stops=sorted(sampled[wet])
    if len(stops)!=10 or set(stops)!=set(sampled[dry]): raise RuntimeError("stop alignment")
    out=defaultdict(float)
    for st in stops:
        wm=by.get((wet,st),{}); dm=by.get((dry,st),{})
        for sp,w in wm.items():
            d=int(dm.get(sp,0)); w=int(w)
            if d==0 and w in (2,3): out[sp]+=w
    return out

def fit(df,response):
    formula=f"{response} ~ rain_contrast + temp_difference + doy_difference + year_gap + C(State) + C(RunNumber)"
    m=smf.ols(formula,data=df).fit(cov_type="cluster",cov_kwds={"groups":df["route_cluster"]})
    b=float(m.params["rain_contrast"]); se=float(m.bse["rain_contrast"])
    return {"beta":b,"se":se,"ci95":[b-Q*se,b+Q*se],"p":float(m.pvalues["rain_contrast"])}

def main():
    raw=base.load(); runs,sets=base.build_runs(raw); eligible=set(runs["RunID"].astype(str))
    sampled,_=spatial.stop_matrix(raw,eligible); by,freq=build_ci(raw,eligible,sampled)
    pairs=base.pair_runs(runs,sets).copy().reset_index(drop=True)

    pair_maps=[strong_by_species(p,sampled,by) for p in pairs.itertuples(index=False)]
    species=sorted({sp for m in pair_maps for sp in m})
    Y=np.zeros((len(pairs),len(species)),float)
    index={sp:j for j,sp in enumerate(species)}
    for i,m in enumerate(pair_maps):
        for sp,v in m.items(): Y[i,index[sp]]=v
    total=Y.sum(axis=1)
    pairs=pairs.copy(); pairs["_strong_total"]=total

    r,den=uniform.design_residual(pairs)
    betas=(r[:,None]*Y).sum(axis=0)/den
    global_beta=float((r*total).sum()/den)
    identity_error=float(global_beta-betas.sum())
    if abs(identity_error)>1e-10: raise RuntimeError(f"beta identity failed {identity_error}")

    positive=np.maximum(betas,0)
    pos_sum=float(positive.sum())
    weights=positive/pos_sum if pos_sum>0 else np.zeros_like(positive)
    eff=float(1/np.sum(weights**2)) if np.sum(weights**2)>0 else None
    order=np.argsort(-positive)
    def top_share(n):
        return float(positive[order[:n]].sum()/pos_sum) if pos_sum>0 else None

    total_model=fit(pairs,"_strong_total")
    loo=[]
    for j,sp in enumerate(species):
        d=pairs.copy(); d["_loo"]=total-Y[:,j]
        m=fit(d,"_loo")
        loo.append({"species":sp,"removed_species_beta_contribution":float(betas[j]),**m})
    no_single=all(x["beta"]>0 and x["ci95"][0]>0 for x in loo)

    denom=max(1,len(runs)*10)
    prevalence=np.asarray([freq.get(sp,0)/denom for sp in species],float)
    rho,pval=spearmanr(prevalence,betas)
    rows=sorted([
        {
          "species":sp,
          "beta_contribution":float(betas[j]),
          "positive_weight":float(weights[j]),
          "baseline_positive_cell_fraction_all_eligible_runs":float(prevalence[j]),
        } for j,sp in enumerate(species)
    ],key=lambda x:x["beta_contribution"],reverse=True)

    out={
      "analysis":"naamp_threshold_recruitment_taxonomic_breadth_v0_1",
      "contract":"exploration/NAAMP_THRESHOLD_RECRUITMENT_TAXONOMIC_BREADTH_CONTRACT_V0_1.json",
      "coverage":{"pairs":int(len(pairs)),"routes":int(pairs.route_cluster.nunique()),"species_with_any_strong_new_cell":int(len(species))},
      "identity":{"global_beta_residualized":global_beta,"sum_species_betas":float(betas.sum()),"error":identity_error,"global_cluster_model":total_model},
      "concentration":{
        "positive_beta_species":int(np.sum(betas>0)),
        "negative_beta_species":int(np.sum(betas<0)),
        "zero_beta_species":int(np.sum(np.isclose(betas,0))),
        "top1_positive_share":top_share(1),
        "top5_positive_share":top_share(5),
        "top10_positive_share":top_share(10),
        "effective_number_positive_contributors":eff,
      },
      "baseline_prevalence_correlation":{"spearman_rho":float(rho),"p":float(pval),"interpretation":"descriptive only; global prevalence is not an opportunity-corrected species trait"},
      "leave_one_species_out":{
        "no_single_species_robustness_pass":bool(no_single),
        "minimum_beta":float(min(x["beta"] for x in loo)),
        "minimum_ci_lower":float(min(x["ci95"][0] for x in loo)),
        "results":loo
      },
      "species_contributions":rows,
      "interpretation_boundary":{
        "rainfall_specific_species_trait_authorized":False,
        "activation_geometry_placebo_failure_still_binding":True,
        "causal_rainfall_claim":False,
        "submission_story_change_authorized":False
      }
    }
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps({k:v for k,v in out.items() if k not in ("species_contributions","leave_one_species_out")},indent=2,sort_keys=True))
    print(json.dumps({"no_single_species_robustness_pass":no_single,"top10":rows[:10]},indent=2))

if __name__=="__main__": main()
