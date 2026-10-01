#!/usr/bin/env python3
from __future__ import annotations
import importlib.util,json
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
NAAMP=ROOT/"scripts"/"naamp"
OUT=ROOT/"exploration"/"NAAMP_HIGHER_ORDER_TAXONOMIC_GENERALITY_RECEIPT_V0_1.json"

def loadmod(name,path):
    s=importlib.util.spec_from_file_location(name,path); m=importlib.util.module_from_spec(s)
    assert s.loader; s.loader.exec_module(m); return m
uniform=loadmod("uniform",NAAMP/"run_naamp_uniform_activation_null.py")

def main():
    pairs,pair_data,pools,dry_ids,sampled,ss,r,den,obs0,beta_mask,r_beta,den_beta,obs_sor=uniform.prepare()
    species=sorted({sp for d in pair_data for sp in d["species"]})
    idx={sp:j for j,sp in enumerate(species)}
    mat=np.zeros((len(pair_data),len(species)),float)
    for i,d in enumerate(pair_data):
        dry_route=d["dry"].any(axis=1)
        wet_route=d["wet"].any(axis=1)
        route_new=(~dry_route)&wet_route
        k=d["wet"].sum(axis=1).astype(float)
        extra=np.maximum(k-1.,0.)
        higher=extra*np.maximum(extra-1.,0.)/2.
        for j,sp in enumerate(d["species"]):
            if route_new[j] and higher[j]>0:
                mat[i,idx[sp]]=higher[j]
    betas=(r[:,None]*mat).sum(axis=0)/den
    total=float(betas.sum())
    pos=np.maximum(betas,0)
    pos_total=float(pos.sum())
    shares=pos/pos_total if pos_total>0 else np.zeros_like(pos)
    order=np.argsort(-shares)
    top1=float(shares[order[0]]) if len(order) else 0.0
    top5=float(shares[order[:5]].sum()) if len(order) else 0.0
    hhi=float(np.sum(shares**2))
    loo=total-betas
    min_loo=float(np.min(loo))
    npos=int(np.sum(betas>0))
    n1=int(np.sum(shares>=.01))
    diffuse=bool(top1<=.25 and top5<=.60 and hhi<=.10 and np.all(loo>0))
    rows=[{"species":species[j],"beta":float(betas[j]),"positive_share":float(shares[j]),"leave_one_out_total_beta":float(loo[j])} for j in order]
    out={
      "analysis":"naamp_higher_order_taxonomic_generality_v0_1",
      "n_pairs":int(len(pairs)),
      "n_routes":int(pairs.route_cluster.nunique()),
      "n_species":int(len(species)),
      "total_higher_order_beta":total,
      "positive_species":npos,
      "species_at_least_1pct_positive_mass":n1,
      "top1_positive_share":top1,
      "top5_positive_share":top5,
      "hhi_positive_shares":hhi,
      "minimum_leave_one_species_out_total_beta":min_loo,
      "all_leave_one_species_out_positive":bool(np.all(loo>0)),
      "classification":{"diffuse_taxonomic_contribution":diffuse},
      "species_contributions":rows
    }
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n"); print(json.dumps(out,indent=2,sort_keys=True))
if __name__=="__main__": main()
