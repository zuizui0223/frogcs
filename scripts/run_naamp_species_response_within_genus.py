#!/usr/bin/env python3
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

import numpy as np
from scipy.stats import chi2

def operational_genus(label: str):
    s=str(label or "").strip()
    if "/" in s or "complex" in s.lower():
        return None
    toks=s.split()
    if len(toks)!=2:
        return None
    return toks[0]

def weighted_mean(rows):
    w=np.array([r["weight"] for r in rows],float)
    y=np.array([r["theta"] for r in rows],float)
    return float(np.sum(w*y)/np.sum(w))

def q_stat(rows,mu):
    return float(sum(r["weight"]*(r["theta"]-mu)**2 for r in rows))

def main():
    p=Path("NAAMP_SPECIES_PULSE_ADJUSTED_ROBUSTNESS_RECEIPT_V0_1.json")
    if not p.is_file():
        raise SystemExit("adjusted species-response receipt missing")
    obj=json.loads(p.read_text(encoding="utf-8"))
    if int(obj.get("fixed_species_family",-1))!=29 or int(obj.get("estimable_species",-1))!=29:
        raise SystemExit("adjusted species family drift")

    rows=[]
    excluded=[]
    for x in obj["species_results"]:
        if not x.get("estimable"):
            continue
        sp=str(x["species"])
        gen=operational_genus(sp)
        if gen is None:
            excluded.append(sp)
            continue
        se=float(x["intercept_se_cluster"])
        if not np.isfinite(se) or se<=0:
            continue
        rows.append({
            "species":sp,
            "genus":gen,
            "theta":float(x["intercept_log_odds"]),
            "se":se,
            "weight":1.0/(se*se),
            "adjusted_wet_probability":float(x["adjusted_wet_probability"])
        })

    genera=defaultdict(list)
    for r in rows:
        genera[r["genus"]].append(r)

    n=len(rows);k=len(genera)
    if n<15 or k<4:
        raise SystemExit(f"insufficient genus decomposition coverage: N={n}, K={k}")

    grand=weighted_mean(rows)
    q_total=q_stat(rows,grand)
    q_within=0.0
    genus_means={}
    for g,rr in genera.items():
        mu=weighted_mean(rr)
        genus_means[g]=mu
        q_within+=q_stat(rr,mu)

    q_between=max(0.0,q_total-q_within)
    df_total=n-1
    df_within=n-k
    df_between=k-1

    details=[]
    for g,rr in sorted(genera.items()):
        mu=genus_means[g]
        positives=sum(r["theta"]>0 for r in rr)
        negatives=sum(r["theta"]<0 for r in rr)
        d={
            "genus":g,
            "n_species":len(rr),
            "weighted_mean_log_odds":mu,
            "positive_species":int(positives),
            "negative_species":int(negatives),
            "species":[
                {
                    "species":r["species"],
                    "theta":r["theta"],
                    "se":r["se"],
                    "adjusted_wet_probability":r["adjusted_wet_probability"]
                } for r in rr
            ]
        }
        if len(rr)>=3:
            q=q_stat(rr,mu)
            df=len(rr)-1
            d.update({"Q":q,"df":df,"p_value":float(chi2.sf(q,df))})
        else:
            d.update({"estimable_Q":False,"reason":"fewer_than_3_species"})
        details.append(d)

    result={
        "analysis":"naamp_species_response_within_genus_heterogeneity_v0_1",
        "contract":"NAAMP_SPECIES_RESPONSE_WITHIN_GENUS_CONTRACT_V0_1.json",
        "response_source":{
            "contract":obj.get("contract"),
            "fixed_species_family":obj.get("fixed_species_family"),
            "estimable_species":obj.get("estimable_species"),
            "heterogeneity_test":obj.get("heterogeneity_test")
        },
        "included_species":n,
        "excluded_non_binomial_or_complex_labels":excluded,
        "n_genera":k,
        "genus_counts":{g:len(rr) for g,rr in sorted(genera.items())},
        "decomposition":{
            "grand_weighted_mean_log_odds":grand,
            "Q_total":q_total,"df_total":df_total,"p_total":float(chi2.sf(q_total,df_total)),
            "Q_within":q_within,"df_within":df_within,"p_within":float(chi2.sf(q_within,df_within)),
            "Q_between":q_between,"df_between":df_between,"p_between":float(chi2.sf(q_between,df_between)),
            "within_fraction_of_Q":float(q_within/q_total) if q_total>0 else None
        },
        "genus_specific":details,
        "interpretation":{
            "within_genus_heterogeneity_supported":bool(chi2.sf(q_within,df_within)<0.05),
            "between_genus_heterogeneity_supported":bool(chi2.sf(q_between,df_between)<0.05),
            "boundary":"Operational genus decomposition only; not a branch-length phylogenetic analysis."
        }
    }

    Path("NAAMP_SPECIES_RESPONSE_WITHIN_GENUS_RECEIPT_V0_1.json").write_text(
        json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8"
    )
    print(json.dumps(result,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
