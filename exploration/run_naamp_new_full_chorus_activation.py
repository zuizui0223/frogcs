#!/usr/bin/env python3
from __future__ import annotations
import importlib.util,json
from collections import defaultdict
from pathlib import Path
import numpy as np,pandas as pd,statsmodels.formula.api as smf

ROOT=Path(__file__).resolve().parents[1];NAAMP=ROOT/"scripts"/"naamp"
OUT=ROOT/"exploration"/"NAAMP_NEW_FULL_CHORUS_ACTIVATION_RECEIPT_V0_1.json";Q=1.959963984540054

def loadmod(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);assert s.loader;s.loader.exec_module(m);return m
base=loadmod("base",NAAMP/"run_naamp_ecological_pulse.py")
spatial=loadmod("spatial",NAAMP/"run_naamp_spatial_taxonomic_activation_decomposition.py")
sameobs=loadmod("sameobs",NAAMP/"run_naamp_same_observer_robustness.py")

def ci_map(raw,eligible,sampled):
 vals=defaultdict(list)
 for r in raw["Counts.csv"]:
  rid=(r.get("RunID") or "").strip();st=(r.get("StopNumber") or "").strip();sp=(r.get("Species") or "").strip()
  if rid not in eligible or st not in sampled.get(rid,set()) or not sp:continue
  try:x=int(float((r.get("CallingIndex") or "").strip()))
  except:continue
  if x in (1,2,3):vals[(rid,st,sp)].append(x)
 by=defaultdict(dict)
 for (rid,st,sp),x in vals.items():by[(rid,st)][sp]=max(x)
 return by

def site_map(raw,eligible):
 v=defaultdict(set)
 for s in raw["Stops.csv"]:
  rid=(s.get("RunID") or "").strip();st=(s.get("StopNumber") or "").strip();sid=(s.get("SiteID") or "").strip()
  if rid in eligible and st and sid and (s.get("SkippedStop") or "").strip()=="0":v[(rid,st)].add(sid)
 bad={k:x for k,x in v.items() if len(x)>1}
 if bad:raise RuntimeError(f"site conflict {list(bad)[:5]}")
 return {k:next(iter(x)) for k,x in v.items()}

def stable(p,sampled,site):
 w=str(p.wet_RunID);d=str(p.dry_RunID);ws=set(sampled[w]);ds=set(sampled[d])
 return len(ws)==10 and ws==ds and all(site.get((w,st)) is not None and site.get((w,st))==site.get((d,st)) for st in ws)

def metrics(p,sampled,by):
 w=str(p.wet_RunID);d=str(p.dry_RunID);n1=n2=n3=0
 for st in sorted(sampled[w]):
  wm=by.get((w,st),{});dm=by.get((d,st),{})
  for sp in set(wm)|set(dm):
   wi=int(wm.get(sp,0));di=int(dm.get(sp,0))
   if di==0:
    n1+=int(wi==1);n2+=int(wi==2);n3+=int(wi==3)
 return {"new_ci1_count":float(n1),"new_ci2_count":float(n2),"new_ci3_count":float(n3),"full_chorus_score":float(3*n3)}

def fit(d,response):
 f=f"{response} ~ rain_contrast + temp_difference + doy_difference + year_gap + C(State) + C(RunNumber)"
 m=smf.ols(f,data=d).fit(cov_type="cluster",cov_kwds={"groups":d.route_cluster})
 b=float(m.params["rain_contrast"]);se=float(m.bse["rain_contrast"])
 return {"beta":b,"se":se,"ci95":[b-Q*se,b+Q*se],"p":float(m.pvalues["rain_contrast"]),"n_pairs":int(len(d)),"n_routes":int(d.route_cluster.nunique())}

def package(pairs,sampled,by):
 rows=[]
 for p in pairs.itertuples(index=False):
  r=p._asdict();r.update(metrics(p,sampled,by));rows.append(r)
 d=pd.DataFrame(rows)
 mods={x:fit(d,x) for x in ("new_ci1_count","new_ci2_count","new_ci3_count","full_chorus_score")}
 support=bool(mods["new_ci3_count"]["beta"]>0 and mods["new_ci3_count"]["ci95"][0]>0)
 return {"models":mods,"classification":{"new_full_chorus_activation_supported":support}}

def main():
 raw=base.load();runs,sets=base.build_runs(raw);eligible=set(runs.RunID.astype(str))
 sampled,_=spatial.stop_matrix(raw,eligible);by=ci_map(raw,eligible,sampled)
 allpairs=base.pair_runs(runs,sets).copy().reset_index(drop=True)
 _,same=sameobs.same_observer_pairs(raw,runs,sets);site=site_map(raw,eligible)
 robust=same.loc[np.asarray([stable(p,sampled,site) for p in same.itertuples(index=False)],bool)].copy().reset_index(drop=True)
 full=package(allpairs,sampled,by);rob=package(robust,sampled,by)
 out={"analysis":"naamp_new_full_chorus_activation_v0_1",
      "contract":"exploration/NAAMP_NEW_FULL_CHORUS_ACTIVATION_CONTRACT_V0_1.json",
      "coverage":{"full_pairs":int(len(allpairs)),"robust_pairs":int(len(robust)),"robust_routes":int(robust.route_cluster.nunique())},
      "full":full,"robust_same_observer_physical_stop":rob,
      "classification":{"full_support":bool(full["classification"]["new_full_chorus_activation_supported"]),
                        "joint_robust_support":bool(full["classification"]["new_full_chorus_activation_supported"] and rob["classification"]["new_full_chorus_activation_supported"])},
      "interpretation_boundary":{"full_chorus_is_ordinal_proxy":True,"reproductive_success_measured":False,"causal_rainfall_claim":False}}
 OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print(json.dumps(out,indent=2,sort_keys=True))
if __name__=="__main__":main()
