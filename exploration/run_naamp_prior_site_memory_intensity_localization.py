#!/usr/bin/env python3
from __future__ import annotations
import importlib.util,json
from collections import defaultdict
from pathlib import Path
import numpy as np,pandas as pd,statsmodels.api as sm

ROOT=Path(__file__).resolve().parents[1]; NAAMP=ROOT/"scripts"/"naamp"
OUT=ROOT/"exploration"/"NAAMP_PRIOR_SITE_MEMORY_INTENSITY_LOCALIZATION_RECEIPT_V0_1.json"; Q=1.959963984540054

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

def meta(runs,sampled,site,ci):
 md={};by=defaultdict(list);route=defaultdict(set);sitehist=defaultdict(set)
 for r in runs.itertuples(index=False):
  rid=str(r.RunID);key=(str(r.State),str(r.RouteNumber),str(r.RunNumber));yr=int(r.SurveyYear);md[rid]=(key,yr);by[key].append(rid)
  for st in sampled.get(rid,set()):
   sid=site.get((rid,st))
   if sid is None:continue
   for sp,val in ci.get((rid,st),{}).items():
    if val>0:route[rid].add(sp);sitehist[(rid,sid)].add(sp)
 for k in by:by[k]=sorted(by[k],key=lambda rid:(md[rid][1],rid))
 return md,by,route,sitehist

def rows_for_pair(pid,p,sampled,site,ci,md,by,route,sitehist):
 w=str(p.wet_RunID);d=str(p.dry_RunID);key,_=md[w];cut=int(p.year_earlier)
 prior=[rid for rid in by[key] if md[rid][1]<cut]
 if not prior:return []
 prior_route=set();prior_site=defaultdict(set)
 for rid in prior:
  prior_route.update(route.get(rid,set()))
  for st in sampled.get(rid,set()):
   sid=site.get((rid,st))
   if sid is not None:prior_site[sid].update(sitehist.get((rid,sid),set()))
 dry_route=set()
 for st in sampled[d]:dry_route.update(ci.get((d,st),{}).keys())
 candidates=[sp for sp in prior_route if sp not in dry_route]
 out=[]
 for sp in candidates:
  tmp=[]
  for st in sorted(sampled[w]):
   sid=site[(w,st)];mem=int(sp in prior_site.get(sid,set()));val=int(ci.get((w,st),{}).get(sp,0))
   tmp.append((sid,mem,int(val==1),int(val==2),int(val==3),int(val>=2)))
  mems=[x[1] for x in tmp]
  if min(mems)==max(mems):continue
  gid=f"{pid}|{sp}"
  for sid,mem,y1,y2only,y3,y2plus in tmp:
   out.append({"group_id":gid,"pair_id":pid,"species":sp,"SiteID":sid,"prior_same_site":float(mem),
               "wet_ci1_only":float(y1),"wet_ci2_only":float(y2only),
               "wet_ci3_only":float(y3),"wet_ci2plus":float(y2plus),
               "rain_contrast":float(p.rain_contrast),
               "route_cluster":str(p.route_cluster),"wet_RunID":w,"dry_RunID":d})
 return out

def fit(d,response):
 x=d.copy();grp=x.groupby("group_id")
 x["m_w"]=x.prior_same_site-grp.prior_same_site.transform("mean")
 x["y_w"]=x[response]-grp[response].transform("mean")
 x["rm"]=x.prior_same_site*x.rain_contrast
 x["rm_w"]=x.rm-grp.rm.transform("mean")
 X=x[["m_w","rm_w"]].astype(float);y=x.y_w.astype(float)
 f=sm.OLS(y,X).fit(cov_type="cluster",cov_kwds={"groups":x.route_cluster})
 b=float(f.params["rm_w"]);se=float(f.bse["rm_w"])
 return {"interaction_beta":b,"se":se,"ci95":[b-Q*se,b+Q*se],"p":float(f.pvalues["rm_w"]),
         "memory_main_beta":float(f.params["m_w"]),"n_cells":int(len(x)),"n_groups":int(x.group_id.nunique()),
         "n_pairs":int(x.pair_id.nunique()),"n_routes":int(x.route_cluster.nunique())}

def main():
 raw=base.load();runs,sets=base.build_runs(raw);eligible=set(runs.RunID.astype(str))
 sampled,_=spatial.stop_matrix(raw,eligible);site=site_map(raw,eligible);ci=ci_map(raw,eligible,sampled)
 pairs_all=base.pair_runs(runs,sets).copy().reset_index(drop=True)
 pairs=pairs_all.loc[np.asarray([stable(p,sampled,site) for p in pairs_all.itertuples(index=False)],bool)].copy().reset_index(drop=True)
 md,by,route,sitehist=meta(runs,sampled,site,ci)
 rows=[]
 for pid,p in enumerate(pairs.itertuples(index=False)):rows.extend(rows_for_pair(pid,p,sampled,site,ci,md,by,route,sitehist))
 d=pd.DataFrame(rows)
 gate=bool(len(d)>=5000 and d.group_id.nunique()>=500 and d.route_cluster.nunique()>=200)
 if not gate:
  out={"analysis":"naamp_prior_site_memory_within_species_v0_1","status":"not_run_due_to_gate",
       "coverage":{"cells":int(len(d)),"groups":int(d.group_id.nunique()) if len(d) else 0,"routes":int(d.route_cluster.nunique()) if len(d) else 0}}
  OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print(json.dumps(out,indent=2));return
 ci1=fit(d,"wet_ci1_only");ci2only=fit(d,"wet_ci2_only");ci3=fit(d,"wet_ci3_only");ci2plus=fit(d,"wet_ci2plus")
 _,same=sameobs.same_observer_pairs(raw,runs,sets);keys={(str(p.wet_RunID),str(p.dry_RunID)) for p in same.itertuples(index=False)}
 ds=d[d.apply(lambda r:(str(r.wet_RunID),str(r.dry_RunID)) in keys,axis=1)].copy()
 sg=bool(len(ds)>=3500 and ds.group_id.nunique()>=350 and ds.route_cluster.nunique()>=150)
 sres=fit(ds,"wet_ci2_only") if sg else None
 out={"analysis":"naamp_prior_site_memory_intensity_localization_v0_1",
      "contract":"exploration/NAAMP_PRIOR_SITE_MEMORY_INTENSITY_LOCALIZATION_CONTRACT_V0_1.json",
      "coverage":{"all_pairs":int(len(pairs_all)),"stable_pairs":int(len(pairs)),"cells":int(len(d)),"groups":int(d.group_id.nunique()),"pairs":int(d.pair_id.nunique()),"routes":int(d.route_cluster.nunique())},
      "wet_ci1_only":ci1,"wet_ci2_only":ci2only,"wet_ci3_only":ci3,"wet_ci2plus_reference":ci2plus,
      "same_observer_ci2_only":{"gate_pass":sg,"result":sres},
      "identity_check_interaction_beta":float(ci2plus["interaction_beta"]-ci2only["interaction_beta"]-ci3["interaction_beta"]),
      "interpretation_boundary":{"post_readback_localization":True,"pair_species_fixed_effect":True,"future_information_used":False,"causal_rainfall_claim":False}}
 OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print(json.dumps(out,indent=2,sort_keys=True))
if __name__=="__main__":main()
