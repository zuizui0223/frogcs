#!/usr/bin/env python3
"""Exploratory, exact sampled-day overlap null for independent Mohonk vernal pools.

Pair wood-frog tadpoles with spotted-/Jefferson-salamander eggs, retaining
the true pond-year survey calendar, stage-specific assessed cells, and marginal
numbers of positive dates. Co-detection is NOT predation or survival.
"""
from __future__ import annotations
import argparse
import csv
import json
import math
import random
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

import numpy as np
from ecology.data.mohonk.analyze_egg_stage_priority import load_original

WOOD="Lithobates sylvaticus"
SPOT="Ambystoma maculatum"
JEFF="Ambystoma jeffersonianum"
SEED=2840223
EXPECTED_ORIGINAL_ROWS=13862
POND_YEARS=59

def stage_sequences(raw,partner):
    by_visit=defaultdict(dict)
    ponds=set();all_dates=set()
    for r in raw:
        day=date.fromisoformat(r["eventDate"])
        if not 2016<=day.year<=2021: continue
        pond=(r["decimalLatitude"],r["decimalLongitude"])
        ponds.add(pond)
        all_dates.add((pond,day))
        species=r["scientificName"]
        stage=r["lifeStage"]
        if (species,stage) not in ((WOOD,"tadpole"),(partner,"egg")):
            continue
        rowkey=(pond,day.year,day)
        key="frog" if species==WOOD else "partner"
        present=int(r["individualCount"])>0
        # Preserve any-positive if publisher has duplicate species-stage rows.
        by_visit[rowkey][key]=by_visit[rowkey].get(key,False) or present
    out=defaultdict(list)
    for (pond,year,day),r in by_visit.items():
        if "frog" in r and "partner" in r:
            out[(pond,year)].append((day,r["frog"],r["partner"]))
    return {k:sorted(v) for k,v in out.items()},len(ponds),len(all_dates)

def fixed_marginal_pmf(a,b):
    """Exact hypergeometric common-date overlap under exchangeable sampled dates."""
    aa=np.asarray(a,bool)
    bb=np.asarray(b,bool)
    if aa.ndim!=1 or bb.shape!=aa.shape or not len(aa):
        raise ValueError("need matched assessed event sequences")
    n=len(aa);na=int(aa.sum());nb=int(bb.sum())
    pmf=np.zeros(min(na,nb)+1,dtype=float)
    for x in range(max(0,na+nb-n),min(na,nb)+1):
        pmf[x]=math.comb(na,x)*math.comb(n-na,nb-x)/math.comb(n,nb)
    if abs(float(pmf.sum())-1)>1e-12: raise ValueError("null invalid")
    return pmf

def circular_pmf(a,b):
    aa=np.asarray(a,bool)
    bb=np.asarray(b,bool)
    if aa.shape!=bb.shape or not len(aa):
        raise ValueError("sequences not aligned")
    n=len(aa)
    hits=np.array([int((np.roll(aa,s)&bb).sum()) for s in range(n)],int)
    pmf=np.bincount(hits,minlength=min(int(aa.sum()),int(bb.sum()))+1).astype(float)/n
    return pmf

def summarize_groups(groups,model="fixed"):
    dist=np.array([1.],float)
    seen=0
    expected=0.
    observed=0
    for g in groups:
        a,b=g["frog"],g["partner"]
        null=fixed_marginal_pmf(a,b) if model=="fixed" else circular_pmf(a,b)
        dist=np.convolve(dist,null)
        if (not np.isfinite(dist).all()) or dist.sum()<=0:
            raise RuntimeError("invalid convolved sampled-day null")
        observed+=g["joint"]
        expected+=sum(i*float(p) for i,p in enumerate(null))
        seen+=1
    if not seen:raise ValueError("no eligible paired-stage surveys")
    dist=dist/dist.sum()
    if observed>=len(dist):raise ValueError("observed overlap outside null support")
    cdf=np.cumsum(dist)
    q=[int(np.searchsorted(cdf,p)) for p in (.025,.975)]
    return {"observed":observed,"expected":round(expected,7),
        "observed_to_expected":round(observed/expected,6) if expected>0 else None,
        "null_lower_2_5pct":q[0],"null_upper_97_5pct":q[1],
        "conditional_one_sided_upper_tail":round(float(dist[observed:].sum()),9),
        "model":model,"pond_year_groups":seen}

def analyse(raw,partner):
    by_pond,number_ponds,number_days=stage_sequences(raw,partner)
    groups=[]
    for (pond,year),rows in sorted(by_pond.items()):
        a=np.array([r[1] for r in rows],bool)
        b=np.array([r[2] for r in rows],bool)
        groups.append({"pond":pond,"year":year,"n":len(rows),
            "frog":a,"partner":b,
            "n_frog_days":int(a.sum()),"n_partner_days":int(b.sum()),
            "joint":int((a&b).sum())})
    overall=summarize_groups(groups)
    cir=summarize_groups(groups,model="circular")
    year_results=[]
    for y in range(2016,2022):
        subset=[g for g in groups if g["year"]==y]
        z=summarize_groups(subset)
        z["year"]=y
        year_results.append(z)
    loo_pond=[]
    for pond in sorted({g["pond"] for g in groups}):
        sub=[g for g in groups if g["pond"]!=pond]
        r=summarize_groups(sub)
        r["pond_anonymous"]=str(sorted({g["pond"] for g in groups}).index(pond)+1)
        loo_pond.append(r)
    loo_year=[]
    for y in range(2016,2022):
        r=summarize_groups([g for g in groups if g["year"]!=y])
        r["left_out_year"]=y
        loo_year.append(r)
    return {
      "analysis":"independent_mohonk_stage_pair_sampled_day_null_v0_1",
      "original_rows":len(raw),
      "original_ponds":number_ponds,
      "original_pond_dates_2016_2021":number_days,
      "stage_pair":{"frog":WOOD+" / tadpole","partner":partner+" / egg"},
      "n_pondyears_with_both_stage_cells_assessed":len(groups),
      "n_assessed_pond_dates":sum(g["n"] for g in groups),
      "n_pondyears_with_both_stages_positive":sum(g["n_frog_days"]>0 and g["n_partner_days"]>0 for g in groups),
      "n_exchangeable_groups_n_ge2":sum(g["n"]>=2 for g in groups),
      "primary_fixed_margin":overall,
      "circular_shift_temporal_clustering_sensitivity":cir,
      "by_year":year_results,
      "leave_one_pond_out":loo_pond,
      "leave_one_year_out":loo_year,
      "ecological_outcome":"stage co-detection within a pond on a sampled date; not predation",
      "caveats":["exploratory analysis after field outcome counts and marginals inspected",
          "not an ecological independence-calibrated P-value across repeated pond-years",
          "within-pond-year date permutation breaks seasonality; circular shift wraps spring endpoints",
          "positive detection of egg/tadpole does not establish direct trophic contact",
          "absence of positive detection is not absence from pond"],
      "independent_of_naamp":True}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source",required=True,type=Path)
    p.add_argument("--outdir",required=True,type=Path)
    args=p.parse_args()
    raw=load_original(args.source)
    if len(raw)!=EXPECTED_ORIGINAL_ROWS:raise RuntimeError("original publisher record count drift")
    outputs={}
    for partner,tag in ((SPOT,"spotted"),(JEFF,"jefferson")):
        result=analyse(raw,partner)
        if result["original_ponds"]!=11 or result["n_pondyears_with_both_stage_cells_assessed"]!=POND_YEARS:
            raise RuntimeError("environmental source pond-year census drift")
        outputs[tag]=result
    if outputs["spotted"]["primary_fixed_margin"]["observed"]!=31:
        raise RuntimeError("original previously checked co-detection count drift")
    if outputs["jefferson"]["primary_fixed_margin"]["observed"]!=9:
        raise RuntimeError("original secondary co-detection count drift")
    args.outdir.mkdir(parents=True,exist_ok=True)
    (args.outdir/"mohonk_stage_overlap_exact_null_result.json").write_text(
        json.dumps(outputs,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    with (args.outdir/"mohonk_stage_overlap_yearly.csv").open("w",newline="",encoding="utf-8") as f:
        columns=["partner","year","observed","expected","observed_to_expected","conditional_one_sided_upper_tail"]
        writer=csv.DictWriter(f,fieldnames=columns);writer.writeheader()
        for tag,out in outputs.items():
            for row in out["by_year"]:
                writer.writerow({col:tag if col=="partner" else row.get(col,"") for col in columns})
    compact={k:{"fixed":v["primary_fixed_margin"],"circular":v["circular_shift_temporal_clustering_sensitivity"],
                "pond_dates":v["n_assessed_pond_dates"],"pond_years":v["n_pondyears_with_both_stage_cells_assessed"]}
             for k,v in outputs.items()}
    print(json.dumps(compact,indent=2))
if __name__=="__main__":
    main()
