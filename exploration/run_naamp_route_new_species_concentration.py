#!/usr/bin/env python3
from __future__ import annotations
import importlib.util,json
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
NAAMP=ROOT/"scripts"/"naamp"
OUT=ROOT/"exploration"/"NAAMP_ROUTE_NEW_SPECIES_CONCENTRATION_RECEIPT_V0_1.json"

def loadmod(name,path):
    s=importlib.util.spec_from_file_location(name,path); m=importlib.util.module_from_spec(s)
    assert s.loader; s.loader.exec_module(m); return m

uniform=loadmod("uniform",NAAMP/"run_naamp_uniform_activation_null.py")

def main():
    pairs,pair_data,pools,dry_ids,sampled,ss,r,den,obs,bm,rb,db,os=uniform.prepare()
    species_all=sorted({sp for d in pair_data for sp in d["species"]})
    index={sp:i for i,sp in enumerate(species_all)}
    numer=np.zeros(len(species_all),float)

    for i,d in enumerate(pair_data):
        dry_route=d["dry"].any(axis=1)
        wet_counts=d["wet"].sum(axis=1)
        route_new=(~dry_route)&(wet_counts>0)
        extra=np.maximum(wet_counts-1,0)*route_new
        for j,sp in enumerate(d["species"]):
            if extra[j]:
                numer[index[sp]] += r[i]*float(extra[j])

    betas=numer/den
    total=float(np.sum(betas))
    positive=np.maximum(betas,0)
    pos_sum=float(np.sum(positive))
    shares=positive/pos_sum if pos_sum>0 else np.zeros_like(positive)
    order=np.argsort(-shares)
    ranked=[
      {"species":species_all[int(i)],"beta":float(betas[int(i)]),"positive_share":float(shares[int(i)])}
      for i in order if shares[int(i)]>0
    ]
    top1=float(shares[order[0]]) if len(order) and pos_sum>0 else 0.0
    top5=float(np.sum(shares[order[:5]])) if pos_sum>0 else 0.0
    hhi=float(np.sum(shares**2)) if pos_sum>0 else 0.0
    loo=total-betas
    min_i=int(np.argmin(loo))
    allpos=bool(np.all(loo>0))
    n_positive=int(np.sum(betas>0))
    n_ge1pct=int(np.sum(shares>=0.01))
    diffuse=bool(top1<=.25 and top5<=.60 and hhi<=.10 and allpos)

    out={
      "analysis":"naamp_route_new_species_concentration_v0_1",
      "contract":"exploration/NAAMP_ROUTE_NEW_SPECIES_CONCENTRATION_CONTRACT_V0_1.json",
      "n_pairs":int(len(pairs)),
      "n_species":int(len(species_all)),
      "decomposition":{"total_extra_stop_beta":total,"sum_species_betas":float(np.sum(betas)),"identity_error":float(total-np.sum(betas))},
      "concentration":{
        "positive_beta_mass":pos_sum,
        "negative_beta_mass":float(np.sum(np.minimum(betas,0))),
        "n_species_positive_beta":n_positive,
        "n_species_positive_share_ge_1pct":n_ge1pct,
        "top1_positive_share":top1,
        "top5_positive_share":top5,
        "hhi_positive_shares":hhi,
        "minimum_leave_one_species_out_beta":float(loo[min_i]),
        "species_causing_minimum_loo":species_all[min_i],
        "all_leave_one_species_out_betas_positive":allpos
      },
      "top_positive_species":ranked[:20],
      "classification":{"diffuse_across_taxa_under_prefixed_rule":diffuse},
      "interpretation_boundary":{
        "every_species_responds":False,
        "species_trait_mechanism_identified":False,
        "universal_claim":False
      }
    }
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,indent=2,sort_keys=True))
if __name__=="__main__": main()
