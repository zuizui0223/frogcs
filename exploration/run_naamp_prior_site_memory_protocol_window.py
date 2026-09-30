#!/usr/bin/env python3
from __future__ import annotations
import importlib.util,json
from collections import defaultdict
from pathlib import Path
import numpy as np,pandas as pd,statsmodels.formula.api as smf

ROOT=Path(__file__).resolve().parents[1]; NAAMP=ROOT/"scripts"/"naamp"
OUT=ROOT/"exploration"/"NAAMP_PRIOR_SITE_MEMORY_PROTOCOL_WINDOW_RECEIPT_V0_1.json"; Q=1.959963984540054

def loadmod(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);assert s.loader;s.loader.exec_module(m);return m
base=loadmod("base",NAAMP/"run_naamp_ecological_pulse.py")
spatial=loadmod("spatial",NAAMP/"run_naamp_spatial_taxonomic_activation_decomposition.py")
sameobs=loadmod("sameobs",NAAMP/"run_naamp_same_observer_robustness.py")

def site_map(raw,eligible):
 v=defaultdict(set)
 for s in raw["Stops.csv"]:
  rid=(s.get("RunID") or "").strip();st=(s.get("StopNumber") or "").strip();sid=(s.get("SiteID") or "").strip()
  if rid in eligible and st and sid and (s.get("SkippedStop") or "").strip()=="0":v[(rid,st)].add(sid)
 bad={k:x for k,x in v.items() if len(x)>1}
 if bad:raise RuntimeError(f"site conflict {list(bad)[:5]}")
 return {k:next(iter(x)) for k,x in v.items()}

def ci_map(raw,eligible,sampled):
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

def stable(p,sampled,site):
 w=str(p.wet_RunID);d=str(p.dry_RunID);ws=set(sampled[w]);ds=set(sampled[d])
 return len(ws)==10 and ws==ds and all(site.get((w,st)) is not None and site.get((w,st))==site.get((d,st)) for st in ws)

def build_meta(runs,sampled,site,ci):
 meta={};by=defaultdict(list);site_species=defaultdict(set);route_species=defaultdict(set)
 for r in runs.itertuples(index=False):
  rid=str(r.RunID);key=(str(r.State),str(r.RouteNumber),str(r.RunNumber));meta[rid]=(key,int(r.SurveyYear));by[key].append(rid)
  for st in sampled.get(rid,set()):
   sid=site.get((rid,st))
   if sid is None:continue
   for sp,val in ci.get((rid,st),{}).items():
    if val>0:site_species[(rid,sid)].add(sp);route_species[rid].add(sp)
 for k in by:by[k]=sorted(by[k],key=lambda rid:(meta[rid][1],rid))
 return meta,by,site_species,route_species

def summarize_pair(p,sampled,site,ci,meta,by,site_species,route_species):
 w=str(p.wet_RunID);d=str(p.dry_RunID);key,_=meta[w];cut=int(p.year_earlier)
 prior=[rid for rid in by[key] if meta[rid][1]<cut]
 if not prior:return None
 prior_route=set();prior_site=defaultdict(set)
 for rid in prior:
  prior_route.update(route_species.get(rid,set()))
  for st in sampled.get(rid,set()):
   sid=site.get((rid,st))
   if sid is not None:prior_site[sid].update(site_species.get((rid,sid),set()))
 dry_route=set()
 for st in sampled[d]:dry_route.update(ci.get((d,st),{}).keys())
 candidates=[sp for sp in prior_route if sp not in dry_route]
 if not candidates:return None
 n_same=n_other=y_same=y_other=0
 for st in sorted(sampled[w]):
  sid=site[(w,st)];wm=ci.get((w,st),{})
  mem=prior_site.get(sid,set())
  for sp in candidates:
   if sp in mem:
    n_same+=1;y_same+=int(int(wm.get(sp,0))==3)
   else:
    n_other+=1;y_other+=int(int(wm.get(sp,0))==3)
 if n_same<5 or n_other<5:return None
 rs=y_same/n_same;ro=y_other/n_other
 return {"same_rate":rs,"route_only_rate":ro,"rate_difference":rs-ro,
         "n_same":float(n_same),"n_route_only":float(n_other),
         "opportunity_weight":float(n_same*n_other/(n_same+n_other)),
         "prior_runs":float(len(prior))}

def fit(d):
 form="rate_difference ~ rain_contrast + temp_difference + doy_difference + year_gap + C(State) + C(RunNumber)"
 m=smf.wls(form,data=d,weights=d.opportunity_weight).fit(cov_type="cluster",cov_kwds={"groups":d.route_cluster})
 b=float(m.params["rain_contrast"]);se=float(m.bse["rain_contrast"])
 return {"beta_rain":b,"se":se,"ci95":[b-Q*se,b+Q*se],"p":float(m.pvalues["rain_contrast"]),
         "n_pairs":int(len(d)),"n_routes":int(d.route_cluster.nunique()),
         "weighted_mean_rate_difference":float(np.average(d.rate_difference,weights=d.opportunity_weight)),
         "median_prior_runs":float(d.prior_runs.median())}

def main():
 raw=base.load();runs,sets=base.build_runs(raw);eligible=set(runs.RunID.astype(str))
 sampled,_=spatial.stop_matrix(raw,eligible);site=site_map(raw,eligible);ci=ci_map(raw,eligible,sampled)
 pairs_all=base.pair_runs(runs,sets).copy().reset_index(drop=True)
 pairs=pairs_all.loc[np.asarray([stable(p,sampled,site) for p in pairs_all.itertuples(index=False)],bool)].copy().reset_index(drop=True)
 meta,by,site_species,route_species=build_meta(runs,sampled,site,ci)
 rows=[]
 for p in pairs.itertuples(index=False):
  x=summarize_pair(p,sampled,site,ci,meta,by,site_species,route_species)
  if x is None:continue
  r=p._asdict();r.update(x);rows.append(r)
 d=pd.DataFrame(rows)
 primary=d[d["dry_days_since_rain"]>=4].copy()
 gate=bool(len(primary)>=500 and primary.route_cluster.nunique()>=150)
 if not gate:
  out={"analysis":"naamp_prior_site_memory_protocol_window_v0_1",
       "contract":"exploration/NAAMP_PRIOR_SITE_MEMORY_PROTOCOL_WINDOW_CONTRACT_V0_1.json",
       "status":"not_run_due_to_primary_gate",
       "coverage":{"prior_opportunity_pairs":int(len(d)),
                   "primary_cross_window_pairs":int(len(primary)),
                   "primary_cross_window_routes":int(primary.route_cluster.nunique()) if len(primary) else 0},
       "response_endpoints_read":False}
  OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print(json.dumps(out,indent=2));return
 primary_fit=fit(primary)
 strict=primary[primary["wet_days_since_rain"]>=4].copy()
 strict_gate=bool(len(strict)>=100 and strict.route_cluster.nunique()>=75)
 strict_fit=fit(strict) if strict_gate else None
 _,same=sameobs.same_observer_pairs(raw,runs,sets)
 keys={(str(p.wet_RunID),str(p.dry_RunID)) for p in same.itertuples(index=False)}
 same_primary=primary[primary.apply(lambda r:(str(r.wet_RunID),str(r.dry_RunID)) in keys,axis=1)].copy()
 same_gate=bool(len(same_primary)>=350 and same_primary.route_cluster.nunique()>=125)
 same_fit=fit(same_primary) if same_gate else None
 out={"analysis":"naamp_prior_site_memory_protocol_window_v0_1",
      "contract":"exploration/NAAMP_PRIOR_SITE_MEMORY_PROTOCOL_WINDOW_CONTRACT_V0_1.json",
      "status":"completed_after_prefixed_gate",
      "coverage":{"all_pairs":int(len(pairs_all)),"physically_stable_pairs":int(len(pairs)),
                  "prior_opportunity_pairs":int(len(d)),
                  "primary_cross_window_pairs":int(len(primary)),"primary_cross_window_routes":int(primary.route_cluster.nunique()),
                  "strict_both_outside_pairs":int(len(strict)),"strict_both_outside_routes":int(strict.route_cluster.nunique()) if len(strict) else 0,
                  "same_observer_primary_pairs":int(len(same_primary)),"same_observer_primary_routes":int(same_primary.route_cluster.nunique()) if len(same_primary) else 0},
      "primary_cross_window":{**primary_fit,"support":bool(primary_fit["beta_rain"]>0 and primary_fit["ci95"][0]>0)},
      "strict_both_outside":{"gate_pass":strict_gate,"result":strict_fit},
      "same_observer_primary":{"gate_pass":same_gate,"result":same_fit},
      "interpretation_boundary":{"future_information_used":False,
          "comparisons_wholly_inside_0_3_day_window_required":False,
          "all_scheduling_confounding_removed":False,
          "continuous_occupancy_proven":False,
          "causal_rainfall_claim":False}}
 OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print(json.dumps(out,indent=2,sort_keys=True))
if __name__=="__main__":main()
