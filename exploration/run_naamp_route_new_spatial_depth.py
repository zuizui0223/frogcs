#!/usr/bin/env python3
from __future__ import annotations
import importlib.util,json
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
NAAMP=ROOT/"scripts"/"naamp"
OUT=ROOT/"exploration"/"NAAMP_ROUTE_NEW_SPATIAL_DEPTH_RECEIPT_V0_1.json"
B=1000;KAPPA=2.0;ANCHOR=0.75

def loadmod(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);assert s.loader;s.loader.exec_module(m);return m
uniform=loadmod("uniform",NAAMP/"run_naamp_uniform_activation_null.py")
persistence=loadmod("persistence",NAAMP/"run_naamp_persistence_preserving_null.py")

def metrics(w,d):
 dryroute=d.any(axis=1);rn=(~dryroute)&w.any(axis=1);k=w.sum(axis=1)
 n=rn.sum()
 second=((k>=2)&rn).sum()
 third=(np.maximum(k-2,0)*rn).sum()
 extra=(np.maximum(k-1,0)*rn).sum()
 three=((k>=3)&rn).sum()
 fourth=(np.maximum(k-3,0)*rn).sum()
 if extra!=second+third:raise RuntimeError("depth identity failed")
 return np.asarray([n,second,third,extra,three,fourth],float)

def simmetrics(w,d):
 dryroute=d.any(axis=1);rn=(~dryroute[None,:])&w.any(axis=2);k=w.sum(axis=2)
 n=rn.sum(axis=1)
 second=((k>=2)&rn).sum(axis=1)
 third=(np.maximum(k-2,0)*rn).sum(axis=1)
 extra=(np.maximum(k-1,0)*rn).sum(axis=1)
 three=((k>=3)&rn).sum(axis=1)
 fourth=(np.maximum(k-3,0)*rn).sum(axis=1)
 if not np.all(extra==second+third):raise RuntimeError("sim depth identity failed")
 return np.column_stack([n,second,third,extra,three,fourth]).astype(float)

def stat(v,o):
 lo,hi=np.quantile(v,[.025,.975])
 return {"null_mean":float(v.mean()),"null_ci95":[float(lo),float(hi)],"observed":float(o),
         "upper_tail_p":float((1+np.sum(v>=o))/(len(v)+1))}

def main():
 pairs,pd,pools,dryids,sampled,ss,r,den,obs0,bm,rb,db,os=uniform.prepare()
 obsrows=np.asarray([metrics(d["wet"],d["dry"]) for d in pd])
 obs=(r[:,None]*obsrows).sum(axis=0)/den
 stops={d["key"]:d["stops"] for d in pd}
 probs=uniform.baseline_probs(KAPPA,pools,dryids,stops,ss)
 hist=persistence.historical_cell_probs(pools,dryids,stops,ss)
 def simulate(kind,seed):
  rng=np.random.default_rng(seed);num=np.zeros((B,6))
  for i,d in enumerate(pd):
   if kind=="u":p=probs[d["key"]]
   else:
    p=(1-ANCHOR)*hist[d["key"]]+ANCHOR*d["dry"].astype(float);p=np.clip(p,1e-8,1-1e-8)
   q=uniform.solve_shift(p,d["wet_k"])
   w=rng.random((B,)+q.shape)<q[None,:,:]
   num+=r[i]*simmetrics(w,d["dry"])
  return num/den
 ub=simulate("u",uniform.SEED+71000);pb=simulate("p",uniform.SEED+72000)
 names=["route_new_species_gain","second_stop_incidence_gain","third_plus_stop_incidence_gain","extra_stop_incidence_gain","threeplus_route_new_species","fourth_plus_stop_incidence_gain"]
 U={names[j]:stat(ub[:,j],obs[j]) for j in range(6)};P={names[j]:stat(pb[:,j],obs[j]) for j in range(6)}
 support=bool(obs[2]>U[names[2]]["null_ci95"][1] and obs[2]>P[names[2]]["null_ci95"][1])
 out={"analysis":"naamp_route_new_spatial_depth_v0_1","contract":"exploration/NAAMP_ROUTE_NEW_SPATIAL_DEPTH_CONTRACT_V0_1.json",
      "n_pairs":int(len(pairs)),"observed_betas":{names[j]:float(obs[j]) for j in range(6)},
      "identity_check":{"extra_minus_second_minus_third":float(obs[3]-obs[1]-obs[2])},
      "uniform_kappa2":U,"persistence_anchor_0_75":P,
      "classification":{"third_plus_spatial_depth_excess_supported":support},
      "interpretation_boundary":{"post_readback":True,"individual_movement_inferred":False,"specific_mediator_identified":False}}
 OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print(json.dumps(out,indent=2,sort_keys=True))
if __name__=="__main__":main()
