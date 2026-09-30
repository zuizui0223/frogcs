#!/usr/bin/env python3
from __future__ import annotations
import csv, hashlib, importlib.util, io, json, math, time, urllib.error, urllib.request
from collections import defaultdict
from pathlib import Path
import numpy as np
import pandas as pd
import statsmodels.api as sm

ROOT=Path(__file__).resolve().parents[1]
NAAMP=ROOT/"scripts"/"naamp"
OUT=ROOT/"exploration"/"NAAMP_SITE_TEMPLATE_SPATIAL_SCALE_RECEIPT_V0_1.json"
COORD_URL="https://www.sciencebase.gov/catalog/file/get/583dc314e4b0d1899f9dea8d?f=__disk__77%2F22%2F7e%2F77227ec46ac1c01592cd7d158d442cd8343a7536"
COORD_SHA="f71a87df9fc94e0d6c5d4466b4745c3bbaff874cbe7c28796b3f9eb44c2e6e83"
Q=1.959963984540054

def loadmod(name,path):
    s=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(s)
    assert s.loader
    s.loader.exec_module(m)
    return m

base=loadmod("base",NAAMP/"run_naamp_ecological_pulse.py")
spatial=loadmod("spatial",NAAMP/"run_naamp_spatial_taxonomic_activation_decomposition.py")
sameobs=loadmod("sameobs",NAAMP/"run_naamp_same_observer_robustness.py")

def load_retry():
    last=None
    for i in range(6):
        try:
            return base.load()
        except urllib.error.HTTPError as e:
            last=e
            if e.code not in (403,429,500,502,503,504):
                raise
            time.sleep(2*(i+1))
    raise RuntimeError(f"NAAMP source failed after retries: {last}")

def fetch_coords():
    last=None
    for i in range(6):
        try:
            req=urllib.request.Request(COORD_URL,headers={"User-Agent":"frogcs-site-template-scale/0.1"})
            with urllib.request.urlopen(req,timeout=180) as r:
                raw=r.read()
            break
        except Exception as e:
            last=e; time.sleep(2*(i+1))
    else:
        raise RuntimeError(f"coordinate fetch failed: {last}")
    got=hashlib.sha256(raw).hexdigest()
    if got!=COORD_SHA:
        raise RuntimeError(f"Coordinates hash drift {got}")
    out={}
    for r in csv.DictReader(io.StringIO(raw.decode("utf-8-sig"))):
        sid=(r.get("SiteID") or "").strip()
        if sid:
            out[sid]=(float(r["lat"]),float(r["lon"]))
    return out

def hav_km(a,b):
    lat1,lon1=a; lat2,lon2=b; R=6371.0088
    p1=math.radians(lat1); p2=math.radians(lat2)
    dp=math.radians(lat2-lat1); dl=math.radians(lon2-lon1)
    h=math.sin(dp/2)**2+math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return 2*R*math.asin(min(1.0,math.sqrt(h)))

def site_map(raw,eligible):
    vals=defaultdict(set)
    for s in raw["Stops.csv"]:
        rid=(s.get("RunID") or "").strip()
        st=(s.get("StopNumber") or "").strip()
        sid=(s.get("SiteID") or "").strip()
        if rid in eligible and st and sid and (s.get("SkippedStop") or "").strip()=="0":
            vals[(rid,st)].add(sid)
    bad={k:v for k,v in vals.items() if len(v)>1}
    if bad:
        raise RuntimeError(f"multiple SiteIDs {list(bad)[:10]}")
    return {k:next(iter(v)) for k,v in vals.items()}

def ci_map(raw,eligible,sampled):
    vals=defaultdict(list)
    for r in raw["Counts.csv"]:
        rid=(r.get("RunID") or "").strip()
        st=(r.get("StopNumber") or "").strip()
        sp=(r.get("Species") or "").strip()
        if rid not in eligible or st not in sampled.get(rid,set()) or not sp:
            continue
        try:
            x=int(float((r.get("CallingIndex") or "").strip()))
        except Exception:
            continue
        if x in (1,2,3):
            vals[(rid,st,sp)].append(x)
    by=defaultdict(dict)
    for (rid,st,sp),v in vals.items():
        by[(rid,st)][sp]=max(v)
    return by

def stable_pair(p,sampled,site,coords):
    w=str(p.wet_RunID); d=str(p.dry_RunID)
    ws=set(sampled[w]); ds=set(sampled[d])
    if len(ws)!=10 or ws!=ds:
        return False
    return all(
        site.get((w,st)) is not None
        and site.get((w,st))==site.get((d,st))
        and site.get((w,st)) in coords
        for st in ws
    )

def history_index(runs):
    meta={}
    by_stratum=defaultdict(list)
    for r in runs.itertuples(index=False):
        rid=str(r.RunID)
        key=(str(r.State),str(r.RouteNumber),str(r.RunNumber))
        meta[rid]={"key":key,"year":int(r.SurveyYear)}
        by_stratum[key].append(rid)
    for k in by_stratum:
        by_stratum[k]=sorted(by_stratum[k],key=lambda rid:(meta[rid]["year"],rid))
    return meta,by_stratum

def pair_rows(pid,p,sampled,site,ci,coords,meta,by_stratum,same_observer):
    w=str(p.wet_RunID); d=str(p.dry_RunID)
    key=meta[w]["key"]; cutoff=int(p.year_earlier)
    prior=[rid for rid in by_stratum[key] if meta[rid]["year"]<cutoff]
    if not prior: return []

    dry_route=set(); wet_route=set()
    for st in sampled[d]: dry_route.update(ci.get((d,st),{}))
    for st in sampled[w]: wet_route.update(ci.get((w,st),{}))

    prior_strong_sites=defaultdict(set)  # species -> set SiteID
    for rid in prior:
        for st in sampled.get(rid,set()):
            sid=site.get((rid,st))
            if sid is None or sid not in coords: continue
            for sp,x in ci.get((rid,st),{}).items():
                if x>=2:
                    prior_strong_sites[sp].add(sid)

    focal=sorted(sp for sp in (wet_route-dry_route) if prior_strong_sites.get(sp))
    if not focal: return []

    stops=sorted(sampled[w],key=lambda x:float(x))
    current_sids=[site[(w,st)] for st in stops]
    adjacent=[]
    for a,b in zip(current_sids[:-1],current_sids[1:]):
        adjacent.append(hav_km(coords[a],coords[b]))
    spacing=float(np.median(adjacent))
    if not np.isfinite(spacing) or spacing<=0:
        return []

    rows=[]
    for sp in focal:
        prior_sites=prior_strong_sites[sp]
        group=f"{pid}|{sp}"
        for st,sid in zip(stops,current_sids):
            dmin=min(hav_km(coords[sid],coords[ps]) for ps in prior_sites)
            exact=float(sid in prior_sites)
            wet=int(ci.get((w,st),{}).get(sp,0))
            rows.append({
                "pair_id":int(pid),
                "pair_species":group,
                "species":sp,
                "route_cluster":str(p.route_cluster),
                "same_observer":bool(same_observer),
                "SiteID":sid,
                "route_spacing_km":spacing,
                "exact_prior_strong":exact,
                "nearest_prior_strong_km":float(dmin),
                "log_distance_units":float(np.log1p(dmin/spacing)),
                "wet_strong":float(wet>=2),
                "wet_full":float(wet==3),
            })
    return rows

def fit_model(df,outcome):
    d=df.copy()
    informative=d.groupby("pair_species")["exact_prior_strong"].nunique()
    good=informative[informative>=2].index
    d=d[d.pair_species.isin(good)].copy()
    if d.empty: return None
    for col in (outcome,"exact_prior_strong","log_distance_units"):
        d[col+"_w"]=d[col]-d.groupby("pair_species")[col].transform("mean")
    X=d[["exact_prior_strong_w","log_distance_units_w"]].astype(float)
    fit=sm.OLS(d[outcome+"_w"].astype(float),X).fit(
        cov_type="cluster",cov_kwds={"groups":d.route_cluster}
    )
    be=float(fit.params["exact_prior_strong_w"]); see=float(fit.bse["exact_prior_strong_w"])
    bd=float(fit.params["log_distance_units_w"]); sed=float(fit.bse["log_distance_units_w"])
    return {
        "outcome":outcome,
        "n_rows":int(len(d)),
        "n_pair_species_groups":int(d.pair_species.nunique()),
        "n_routes":int(d.route_cluster.nunique()),
        "n_species":int(d.species.nunique()),
        "median_route_spacing_km":float(d.route_spacing_km.median()),
        "exact_site_beta":be,
        "exact_site_se":see,
        "exact_site_ci95":[be-Q*see,be+Q*see],
        "exact_site_p":float(fit.pvalues["exact_prior_strong_w"]),
        "exact_site_positive_ci":bool(be>0 and be-Q*see>0),
        "distance_beta":bd,
        "distance_se":sed,
        "distance_ci95":[bd-Q*sed,bd+Q*sed],
        "distance_p":float(fit.pvalues["log_distance_units_w"]),
    }

def main():
    raw=load_retry()
    runs,sets=base.build_runs(raw)
    eligible=set(runs.RunID.astype(str))
    sampled,_=spatial.stop_matrix(raw,eligible)
    site=site_map(raw,eligible)
    ci=ci_map(raw,eligible,sampled)
    coords=fetch_coords()
    meta,by_stratum=history_index(runs)

    allpairs=base.pair_runs(runs,sets).copy().reset_index(drop=True)
    stable=allpairs.loc[
        np.asarray([stable_pair(p,sampled,site,coords) for p in allpairs.itertuples(index=False)],bool)
    ].copy().reset_index(drop=True)
    _,same=sameobs.same_observer_pairs(raw,runs,sets)
    same_keys={(str(p.wet_RunID),str(p.dry_RunID)) for p in same.itertuples(index=False)}

    rows=[]
    for pid,p in enumerate(stable.itertuples(index=False)):
        rows.extend(pair_rows(
            pid,p,sampled,site,ci,coords,meta,by_stratum,
            (str(p.wet_RunID),str(p.dry_RunID)) in same_keys
        ))
    d=pd.DataFrame(rows)

    primary=fit_model(d,"wet_strong")
    gate=bool(
        primary is not None
        and primary["n_pair_species_groups"]>=500
        and primary["n_routes"]>=250
        and primary["n_species"]>=20
    )
    out={
        "analysis":"naamp_site_template_spatial_scale_v0_1",
        "contract":"exploration/NAAMP_SITE_TEMPLATE_SPATIAL_SCALE_CONTRACT_V0_1.json",
        "coverage":{
            "physically_stable_pairs":int(len(stable)),
            "candidate_rows":int(len(d)),
            "candidate_groups":int(d.pair_species.nunique()) if len(d) else 0,
            "candidate_species":int(d.species.nunique()) if len(d) else 0,
            "gate_pass":gate,
        },
        "response_endpoints_read":False,
    }
    if not gate:
        out["primary_precheck"]=primary
        OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
        print(json.dumps(out,indent=2,sort_keys=True))
        return

    full=primary
    full_chorus=fit_model(d,"wet_full")
    ds=d[d.same_observer].copy()
    same_fit=fit_model(ds,"wet_strong")
    out.update({
        "response_endpoints_read":True,
        "primary_wet_strong":full,
        "secondary_wet_full":full_chorus,
        "same_observer_sensitivity":same_fit,
        "classification":{
            "exact_site_component_supported":bool(full["exact_site_positive_ci"]),
            "same_observer_support":bool(same_fit and same_fit["exact_site_positive_ci"]),
            "full_chorus_support":bool(full_chorus and full_chorus["exact_site_positive_ci"]),
        },
        "interpretation_boundary":{
            "neighborhood_proximity_controlled":True,
            "persistent_population_vs_microhabitat_unresolved":True,
            "individual_site_fidelity_inferred":False,
            "causal_rainfall_claim":False,
        }
    })
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
