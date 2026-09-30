#!/usr/bin/env python3
from __future__ import annotations

import importlib.util, json, time, urllib.error
from collections import defaultdict
from pathlib import Path
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

ROOT=Path(__file__).resolve().parents[1]
NAAMP=ROOT/"scripts"/"naamp"
OUT=ROOT/"exploration"/"NAAMP_TEMPLATE_DEPTH_TEMPORAL_HOLDOUT_RECEIPT_V0_1.json"
Q=1.959963984540054
EARLY=set(range(2001,2008))
LATE=set(range(2008,2016))

def loadmod(name,path):
    s=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(s)
    assert s.loader; s.loader.exec_module(m); return m

base=loadmod("base",NAAMP/"run_naamp_ecological_pulse.py")
spatial=loadmod("spatial",NAAMP/"run_naamp_spatial_taxonomic_activation_decomposition.py")

def load_retry():
    last=None
    for i in range(6):
        try:return base.load()
        except urllib.error.HTTPError as e:
            last=e
            if e.code not in (403,429,500,502,503,504):raise
            time.sleep(2*(i+1))
    raise RuntimeError(f"NAAMP source failed after retries: {last}")

def site_map(raw,eligible):
    vals=defaultdict(set)
    for s in raw["Stops.csv"]:
        rid=(s.get("RunID") or "").strip(); st=(s.get("StopNumber") or "").strip(); sid=(s.get("SiteID") or "").strip()
        if rid in eligible and st and sid and (s.get("SkippedStop") or "").strip()=="0":vals[(rid,st)].add(sid)
    bad={k:v for k,v in vals.items() if len(v)>1}
    if bad:raise RuntimeError(f"multiple SiteIDs {list(bad)[:10]}")
    return {k:next(iter(v)) for k,v in vals.items()}

def ci_map(raw,eligible,sampled):
    vals=defaultdict(list)
    for r in raw["Counts.csv"]:
        rid=(r.get("RunID") or "").strip(); st=(r.get("StopNumber") or "").strip(); sp=(r.get("Species") or "").strip()
        if rid not in eligible or st not in sampled.get(rid,set()) or not sp:continue
        try:x=int(float((r.get("CallingIndex") or "").strip()))
        except Exception:continue
        if x in (1,2,3):vals[(rid,st,sp)].append(x)
    by=defaultdict(dict)
    for (rid,st,sp),v in vals.items():by[(rid,st)][sp]=max(v)
    return by

def observer_map(raw):
    return {
        str(r.get("RunID") or "").strip():str(r.get("ObserverTrackingID") or "").strip()
        for r in raw["Runs.csv"] if str(r.get("RunID") or "").strip()
    }

def stable_pair(p,sampled,site):
    w=str(p.wet_RunID);d=str(p.dry_RunID);ws=set(sampled[w]);ds=set(sampled[d])
    return len(ws)==10 and ws==ds and all(site.get((w,st)) and site.get((w,st))==site.get((d,st)) for st in ws)

def main_rows(raw,runs,sets,sampled,site,ci):
    val_runs=runs[runs.SurveyYear.isin(LATE)].copy()
    pairs=base.pair_runs(val_runs,sets).copy().reset_index(drop=True)
    stable=pairs.loc[np.asarray([stable_pair(p,sampled,site) for p in pairs.itertuples(index=False)],bool)].copy().reset_index(drop=True)

    early=runs[runs.SurveyYear.isin(EARLY)].copy()
    early_by=defaultdict(list)
    for r in early.itertuples(index=False):
        early_by[(str(r.State),str(r.RouteNumber),str(r.RunNumber))].append(str(r.RunID))

    obs=observer_map(raw)
    rows=[]
    for p in stable.itertuples(index=False):
        key=(str(p.State),str(p.RouteNumber),str(p.RunNumber))
        erids=sorted(early_by.get(key,[]))
        if len(erids)<2:continue

        w=str(p.wet_RunID);d=str(p.dry_RunID)
        stops=sorted(sampled[w],key=lambda x:float(x))
        current_sids=[site[(w,st)] for st in stops]

        site_opp=defaultdict(int); site_any=defaultdict(set); site_strong=defaultdict(set)
        route_runs_with_species=defaultdict(int); route_species=set()
        for rid in erids:
            seen_route=set(); seen_sid=set()
            for st in sampled.get(rid,set()):
                sid=site.get((rid,st))
                if sid is None:continue
                if sid in current_sids and sid not in seen_sid:
                    site_opp[sid]+=1;seen_sid.add(sid)
                for sp,x in ci.get((rid,st),{}).items():
                    if int(x)>0:
                        route_species.add(sp);seen_route.add(sp)
                        if sid in current_sids:site_any[sid].add(sp)
                    if int(x)>=2 and sid in current_sids:site_strong[sid].add(sp)
            for sp in seen_route:route_runs_with_species[sp]+=1

        opportunity=[sid for sid in current_sids if site_opp.get(sid,0)>0]
        if len(opportunity)<8:continue

        wet_species=set();dry_species=set();wet_by=defaultdict(dict)
        for st in stops:
            for sp,x in ci.get((w,st),{}).items():
                if int(x)>0:wet_species.add(sp);wet_by[sp][st]=int(x)
            for sp,x in ci.get((d,st),{}).items():
                if int(x)>0:dry_species.add(sp)
        focal=sorted((wet_species-dry_species)&route_species)
        same_observer=bool(obs.get(w) and obs.get(w)==obs.get(d))
        for sp in focal:
            occ=wet_by[sp];k=len(occ)
            any_b=sum(sp in site_any.get(sid,set()) for sid in opportunity)/len(opportunity)
            strong_b=sum(sp in site_strong.get(sid,set()) for sid in opportunity)/len(opportunity)
            freq=route_runs_with_species.get(sp,0)/len(erids)
            rows.append({
                "species":sp,"route_cluster":str(p.route_cluster),"State":str(p.State),"RunNumber":str(p.RunNumber),
                "same_observer":same_observer,"year_gap":float(p.year_gap),"rain_contrast":float(p.rain_contrast),
                "temp_difference":float(p.temp_difference),"doy_difference":float(p.doy_difference),
                "early_runs":float(len(erids)),"opportunity_sites":float(len(opportunity)),
                "early_strong_breadth":float(strong_b),"early_any_breadth":float(any_b),"early_route_frequency":float(freq),
                "wet_k":float(k),"spatial_depth":float(k-1),"third_plus_depth":float(max(k-2,0)),
                "wet_strong_k":float(sum(int(x)>=2 for x in occ.values()))
            })
    return pairs,stable,pd.DataFrame(rows)

def gate(d,primary=True):
    sd=float(d.early_strong_breadth.std(ddof=0)) if len(d) else 0
    if primary:ok=len(d)>=500 and d.route_cluster.nunique()>=150 and d.species.nunique()>=20 and sd>=.10
    else:ok=len(d)>=350 and d.route_cluster.nunique()>=120 and d.species.nunique()>=20 and sd>=.10
    return {"pass":bool(ok),"n_pair_species":int(len(d)),"n_routes":int(d.route_cluster.nunique()) if len(d) else 0,
            "n_species":int(d.species.nunique()) if len(d) else 0,"breadth_sd":sd}

def fit(d,response,predictor):
    x=d.copy();v=x[predictor].to_numpy(float);sd=float(np.std(v,ddof=0))
    x["z_breadth"]=(v-float(np.mean(v)))/sd;x["c_rain"]=x.rain_contrast-float(x.rain_contrast.mean())
    form=(f"{response} ~ z_breadth + c_rain + z_breadth:c_rain + early_route_frequency + "
          "temp_difference + doy_difference + year_gap + C(species) + C(State) + C(RunNumber)")
    m=smf.ols(form,data=x).fit(cov_type="cluster",cov_kwds={"groups":x.route_cluster})
    b=float(m.params["z_breadth"]);se=float(m.bse["z_breadth"]);bi=float(m.params["z_breadth:c_rain"]);sei=float(m.bse["z_breadth:c_rain"])
    return {"response":response,"predictor":predictor,"n_pair_species":int(len(x)),"n_routes":int(x.route_cluster.nunique()),"n_species":int(x.species.nunique()),
            "breadth_mean":float(np.mean(v)),"breadth_sd":sd,"breadth_beta":b,"breadth_ci95":[b-Q*se,b+Q*se],"breadth_p":float(m.pvalues["z_breadth"]),
            "breadth_positive_ci":bool(b>0 and b-Q*se>0),"breadth_x_rain_beta":bi,"breadth_x_rain_ci95":[bi-Q*sei,bi+Q*sei],
            "breadth_x_rain_p":float(m.pvalues["z_breadth:c_rain"])}

def main():
    raw=load_retry();runs,sets=base.build_runs(raw);eligible=set(runs.RunID.astype(str))
    sampled,_=spatial.stop_matrix(raw,eligible);site=site_map(raw,eligible);ci=ci_map(raw,eligible,sampled)
    pairs,stable,d=main_rows(raw,runs,sets,sampled,site,ci);g=gate(d,True)
    out={"analysis":"naamp_template_depth_temporal_holdout_v0_1","contract":"exploration/NAAMP_TEMPLATE_DEPTH_TEMPORAL_HOLDOUT_CONTRACT_V0_1.json",
         "coverage":{"validation_pairs":int(len(pairs)),"stable_validation_pairs":int(len(stable)),**g},"response_endpoints_read":False}
    if not g["pass"]:
        OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print(json.dumps(out,indent=2,sort_keys=True));return
    primary=fit(d,"third_plus_depth","early_strong_breadth")
    sec_k=fit(d,"wet_k","early_strong_breadth");sec_depth=fit(d,"spatial_depth","early_strong_breadth");strong_k=fit(d,"wet_strong_k","early_strong_breadth")
    anyb=fit(d,"third_plus_depth","early_any_breadth")
    ds=d[d.same_observer].copy();gs=gate(ds,False);samefit=fit(ds,"third_plus_depth","early_strong_breadth") if gs["pass"] else None
    de=d[d.year_gap==1].copy();ge=gate(de,False);exactfit=fit(de,"third_plus_depth","early_strong_breadth") if ge["pass"] else None
    out.update({"response_endpoints_read":True,"primary_third_plus_depth":primary,"secondary_wet_k":sec_k,"secondary_spatial_depth":sec_depth,
                "secondary_wet_strong_k":strong_k,"sensitivity_early_any_breadth":anyb,
                "same_observer_sensitivity":{"gate":gs,"model":samefit},"exact_consecutive_year_sensitivity":{"gate":ge,"model":exactfit},
                "classification":{"temporal_holdout_template_depth_supported":bool(primary["breadth_positive_ci"]),
                                  "same_observer_support":bool(samefit and samefit["breadth_positive_ci"]),
                                  "exact_year_support":bool(exactfit and exactfit["breadth_positive_ci"])},
                "interpretation_boundary":{"nonoverlapping_template_validation":True,"post_activation_model":True,"activation_probability_modeled":False,
                                           "movement_inferred":False,"causal_rainfall_claim":False}})
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print(json.dumps(out,indent=2,sort_keys=True))

if __name__=="__main__":main()
