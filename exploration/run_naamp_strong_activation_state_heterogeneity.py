#!/usr/bin/env python3
from __future__ import annotations
import importlib.util,json,warnings
from collections import defaultdict
from pathlib import Path
import numpy as np,pandas as pd,statsmodels.formula.api as smf

ROOT=Path(__file__).resolve().parents[1];NAAMP=ROOT/"scripts"/"naamp"
OUT=ROOT/"exploration"/"NAAMP_STRONG_ACTIVATION_STATE_HETEROGENEITY_RECEIPT_V0_1.json";Q=1.959963984540054

def loadmod(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);assert s.loader;s.loader.exec_module(m);return m
base=loadmod("base",NAAMP/"run_naamp_ecological_pulse.py")
spatial=loadmod("spatial",NAAMP/"run_naamp_spatial_taxonomic_activation_decomposition.py")

def ci(raw,eligible,sampled):
 v=defaultdict(list)
 for r in raw["Counts.csv"]:
  rid=(r.get("RunID") or "").strip();st=(r.get("StopNumber") or "").strip();sp=(r.get("Species") or "").strip()
  if rid not in eligible or st not in sampled.get(rid,set()) or not sp:continue
  try:x=int(float((r.get("CallingIndex") or "").strip()))
  except:continue
  if x in (1,2,3):v[(rid,st,sp)].append(x)
 by=defaultdict(dict)
 for (rid,st,sp),x in v.items():by[(rid,st)][sp]=max(x)
 return by

def score(p,sampled,by):
 w=str(p.wet_RunID);d=str(p.dry_RunID);s=0.0
 for st in sorted(sampled[w]):
  wm=by.get((w,st),{});dm=by.get((d,st),{})
  for sp in set(wm)|set(dm):
   wi=int(wm.get(sp,0));di=int(dm.get(sp,0))
   if di==0 and wi>=2:s+=wi
 return s

def state_fit(g):
 if len(g)<30 or g.route_cluster.nunique()<5:return {"estimable":False,"n_pairs":int(len(g)),"n_routes":int(g.route_cluster.nunique())}
 f="strong_new_score ~ rain_contrast + temp_difference + doy_difference + year_gap + C(RunNumber)"
 try:
  m=smf.ols(f,data=g).fit(cov_type="cluster",cov_kwds={"groups":g.route_cluster})
  b=float(m.params["rain_contrast"]);se=float(m.bse["rain_contrast"])
  return {"estimable":True,"n_pairs":int(len(g)),"n_routes":int(g.route_cluster.nunique()),"beta":b,"se":se,"ci95":[b-Q*se,b+Q*se],"p":float(m.pvalues["rain_contrast"])}
 except Exception as e:return {"estimable":False,"n_pairs":int(len(g)),"n_routes":int(g.route_cluster.nunique()),"reason":str(e)}

def main():
 raw=base.load();runs,sets=base.build_runs(raw);eligible=set(runs.RunID.astype(str))
 sampled,_=spatial.stop_matrix(raw,eligible);by=ci(raw,eligible,sampled)
 d=base.pair_runs(runs,sets).copy().reset_index(drop=True);d["strong_new_score"]=[score(p,sampled,by) for p in d.itertuples(index=False)]
 states={}
 for st,g in d.groupby("State",sort=True):states[str(st)]=state_fit(g.copy())
 est=[x for x in states.values() if x.get("estimable")]
 mixed={}
 f="strong_new_score ~ rain_contrast + temp_difference + doy_difference + year_gap + C(RunNumber)"
 with warnings.catch_warnings(record=True) as ws:
  warnings.simplefilter("always")
  try:
   m=smf.mixedlm(f,d,groups=d["State"],re_formula="~rain_contrast").fit(reml=True,method="lbfgs",maxiter=1000,disp=False)
   cov=m.cov_re;sd=float(np.sqrt(max(float(cov.loc["rain_contrast","rain_contrast"]),0)))
   pop=float(m.params["rain_contrast"])
   mixed={"converged":bool(m.converged),"population_beta":pop,"state_slope_sd":sd,"warnings":[str(w.message) for w in ws]}
  except Exception as e:mixed={"converged":False,"error":repr(e),"warnings":[str(w.message) for w in ws]}
 bet=np.asarray([x["beta"] for x in est],float) if est else np.asarray([])
 out={"analysis":"naamp_strong_activation_state_heterogeneity_v0_1","contract":"exploration/NAAMP_STRONG_ACTIVATION_STATE_HETEROGENEITY_CONTRACT_V0_1.json",
      "n_pairs":int(len(d)),"n_routes":int(d.route_cluster.nunique()),"n_states":int(d.State.nunique()),
      "state_specific":states,
      "summary":{"n_estimable_states":int(len(est)),"positive_fraction":float(np.mean(bet>0)) if len(bet) else None,
                 "ci_positive_fraction":float(np.mean([x["ci95"][0]>0 for x in est])) if est else None,
                 "median_beta":float(np.median(bet)) if len(bet) else None,
                 "beta_range":[float(bet.min()),float(bet.max())] if len(bet) else None},
      "random_slope":mixed,
      "interpretation_boundary":{"sampled_NAAMP_states_only":True,"universal_claim":False}}
 OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print(json.dumps(out,indent=2,sort_keys=True))
if __name__=="__main__":main()
