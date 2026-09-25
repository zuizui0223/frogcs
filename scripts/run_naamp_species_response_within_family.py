#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import numpy as np
from scipy.stats import chi2

ROOT=Path(__file__).resolve().parent
TRAIT_SCRIPT=ROOT/"run_naamp_rainfall_filter_traits.py"
spec=importlib.util.spec_from_file_location("trait_base",TRAIT_SCRIPT)
trait=importlib.util.module_from_spec(spec)
assert spec.loader
spec.loader.exec_module(trait)

def load_adjusted():
    p=Path("NAAMP_SPECIES_PULSE_ADJUSTED_ROBUSTNESS_RECEIPT_V0_1.json")
    if not p.is_file():
        raise SystemExit("adjusted species receipt missing")
    obj=json.loads(p.read_text(encoding="utf-8"))
    if int(obj.get("fixed_species_family",-1))!=29 or int(obj.get("estimable_species",-1))!=29:
        raise SystemExit("adjusted species family drift")
    rows=[]
    for x in obj["species_results"]:
        if not x.get("estimable"):
            continue
        se=float(x["intercept_se_cluster"])
        if not np.isfinite(se) or se<=0:
            continue
        rows.append({
            "species":trait.normalize_binomial(x["species"]),
            "theta":float(x["intercept_log_odds"]),
            "se":se,
            "weight":1.0/(se*se),
            "adjusted_wet_probability":float(x["adjusted_wet_probability"])
        })
    return rows,obj

def match_family(rows):
    t,blob=trait.load_traits()
    idx={s:i for i,s in enumerate(t["species_norm"].tolist())}
    out=[];audit=[]
    for r in rows:
        sp=r["species"]
        candidates=[sp]
        toks=sp.split()
        if len(toks)==2 and toks[0] in trait.ALIASES:
            candidates.append(trait.ALIASES[toks[0]]+" "+toks[1])
        hits=[c for c in candidates if c in idx]
        if sp in hits:
            chosen=sp
        elif len(hits)==1:
            chosen=hits[0]
        elif len(hits)>1:
            raise SystemExit(f"ambiguous family match {sp}: {hits}")
        else:
            chosen=None
        rr=dict(r)
        if chosen is None:
            rr.update({"matched":False,"amphibio_species":None,"Family":""})
            audit.append({"naamp_species":sp,"matched":False,"amphibio_species":None})
        else:
            tr=t.iloc[idx[chosen]]
            fam=str(tr.get("Family","") or "").strip()
            rr.update({"matched":bool(fam),"amphibio_species":chosen,"Family":fam})
            audit.append({
                "naamp_species":sp,"matched":bool(fam),"amphibio_species":chosen,
                "Family":fam,"match_type":"exact" if chosen==sp else "frozen_genus_alias"
            })
        out.append(rr)
    return out,audit,blob

def weighted_mean(rows):
    w=np.array([r["weight"] for r in rows],float)
    y=np.array([r["theta"] for r in rows],float)
    return float(np.sum(w*y)/np.sum(w))

def q_stat(rows,mu):
    return float(sum(r["weight"]*(r["theta"]-mu)**2 for r in rows))

def main():
    rows,adj=load_adjusted()
    rows,audit,blob=match_family(rows)
    rows=[r for r in rows if r.get("matched") and r.get("Family")]
    if len(rows)<15:
        raise SystemExit(f"too few family-matched species: {len(rows)}")

    families={}
    for r in rows:
        families.setdefault(r["Family"],[]).append(r)

    grand=weighted_mean(rows)
    q_total=q_stat(rows,grand)

    family_means={}
    q_within=0.0
    for fam,rr in families.items():
        mu=weighted_mean(rr)
        family_means[fam]=mu
        q_within+=q_stat(rr,mu)

    q_between=max(0.0,q_total-q_within)
    n=len(rows); k=len(families)
    df_total=n-1
    df_within=n-k
    df_between=k-1

    family_specific=[]
    for fam,rr in sorted(families.items()):
        mu=family_means[fam]
        if len(rr)>=3:
            q=q_stat(rr,mu)
            df=len(rr)-1
            p=float(chi2.sf(q,df))
            family_specific.append({
                "family":fam,"n_species":len(rr),"weighted_mean_log_odds":mu,
                "Q":q,"df":df,"p_value":p,
                "species":[
                    {"species":r["species"],"theta":r["theta"],"se":r["se"],
                     "adjusted_wet_probability":r["adjusted_wet_probability"]}
                    for r in rr
                ]
            })
        else:
            family_specific.append({
                "family":fam,"n_species":len(rr),"weighted_mean_log_odds":mu,
                "estimable_Q":False,"reason":"family_has_fewer_than_3_species"
            })

    result={
        "analysis":"naamp_species_response_within_family_heterogeneity_v0_1",
        "contract":"NAAMP_SPECIES_RESPONSE_WITHIN_FAMILY_CONTRACT_V0_1.json",
        "adjusted_response_source":{
            "contract":adj.get("contract"),
            "estimable_species":adj.get("estimable_species"),
            "heterogeneity_test":adj.get("heterogeneity_test")
        },
        "family_source":{
            "dataset":"AmphiBIO v1",
            "mirror_commit":"c437acbc65b51b66e3dc4abd821ebe1cb06b200c",
            "git_blob_sha1":blob
        },
        "matched_species":n,
        "n_families":k,
        "family_counts":{fam:len(rr) for fam,rr in sorted(families.items())},
        "taxonomy_audit":audit,
        "decomposition":{
            "grand_weighted_mean_log_odds":grand,
            "Q_total":q_total,"df_total":df_total,"p_total":float(chi2.sf(q_total,df_total)),
            "Q_within":q_within,"df_within":df_within,"p_within":float(chi2.sf(q_within,df_within)),
            "Q_between":q_between,"df_between":df_between,"p_between":float(chi2.sf(q_between,df_between)),
            "within_fraction_of_Q":float(q_within/q_total) if q_total>0 else None
        },
        "family_specific":family_specific,
        "interpretation":{
            "within_family_heterogeneity_supported":bool(chi2.sf(q_within,df_within)<0.05),
            "between_family_heterogeneity_supported":bool(chi2.sf(q_between,df_between)<0.05),
            "boundary":"Family is a coarse taxonomic proxy; this is not a phylogenetic comparative analysis."
        }
    }
    Path("NAAMP_SPECIES_RESPONSE_WITHIN_FAMILY_RECEIPT_V0_1.json").write_text(
        json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8"
    )
    print(json.dumps(result,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
