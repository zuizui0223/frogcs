#!/usr/bin/env python3
from __future__ import annotations

import csv, hashlib, importlib.util, io, json, math, time, urllib.request
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
import planetary_computer
import rasterio
from rasterio.windows import from_bounds
from pystac_client import Client
import statsmodels.api as sm

ROOT=Path(__file__).resolve().parents[1]
NAAMP=ROOT/"scripts"/"naamp"
OUT=ROOT/"exploration"/"NAAMP_JRC_SURFACE_WATER_CONTEXT_RECEIPT_V0_1.json"
COORD_URL="https://www.sciencebase.gov/catalog/file/get/583dc314e4b0d1899f9dea8d?f=__disk__77%2F22%2F7e%2F77227ec46ac1c01592cd7d158d442cd8343a7536"
COORD_SHA="f71a87df9fc94e0d6c5d4466b4745c3bbaff874cbe7c28796b3f9eb44c2e6e83"
Q=1.959963984540054

def loadmod(name,path):
    s=importlib.util.spec_from_file_location(name,path); m=importlib.util.module_from_spec(s)
    assert s.loader; s.loader.exec_module(m); return m

base=loadmod("base",NAAMP/"run_naamp_ecological_pulse.py")
spatial=loadmod("spatial",NAAMP/"run_naamp_spatial_taxonomic_activation_decomposition.py")

def fetch(url,retries=6):
    last=None
    for i in range(retries):
        try:
            req=urllib.request.Request(url,headers={"User-Agent":"frogcs-jrc-water-context/0.1"})
            with urllib.request.urlopen(req,timeout=180) as r: return r.read()
        except Exception as e:
            last=e; time.sleep(2*(i+1))
    raise RuntimeError(f"fetch failed: {last}")

def load_coords():
    raw=fetch(COORD_URL)
    got=hashlib.sha256(raw).hexdigest()
    if got!=COORD_SHA: raise RuntimeError(f"Coordinates hash drift {got}")
    rows=list(csv.DictReader(io.StringIO(raw.decode("utf-8-sig"))))
    out={}
    for r in rows:
        sid=(r.get("SiteID") or "").strip()
        if not sid: continue
        lat=float(r["lat"]); lon=float(r["lon"])
        if sid in out and out[sid]!=(lat,lon): raise RuntimeError(f"coordinate conflict {sid}")
        out[sid]=(lat,lon)
    return out

def site_map(raw,eligible):
    vals=defaultdict(set)
    for s in raw["Stops.csv"]:
        rid=(s.get("RunID") or "").strip(); st=(s.get("StopNumber") or "").strip(); sid=(s.get("SiteID") or "").strip()
        if rid not in eligible or (s.get("SkippedStop") or "").strip()!="0" or not st: continue
        if sid: vals[(rid,st)].add(sid)
    bad={k:v for k,v in vals.items() if len(v)>1}
    if bad: raise RuntimeError(f"multiple SiteID values {list(bad)[:10]}")
    return {k:next(iter(v)) for k,v in vals.items() if v}

def pair_used_siteids(raw,runs,sets):
    pairs=base.pair_runs(runs,sets).copy().reset_index(drop=True)
    eligible=set(runs["RunID"].astype(str)); site=site_map(raw,eligible)
    ids=set()
    for p in pairs.itertuples(index=False):
        for rid in (str(p.wet_RunID),str(p.dry_RunID)):
            for st in range(1,11):
                sid=site.get((rid,str(st)))
                if sid: ids.add(sid)
    return pairs,site,ids

def stac_items(bbox):
    cat=Client.open("https://planetarycomputer.microsoft.com/api/stac/v1")
    search=cat.search(collections=["jrc-gsw"],bbox=bbox)
    items=list(search.items())
    if not items: raise RuntimeError("no jrc-gsw items")
    return items

def intersects(bbox,bb):
    return not (bbox[2]<bb[0] or bbox[0]>bb[2] or bbox[3]<bb[1] or bbox[1]>bb[3])

def site_metric(lat,lon,items,radius_m):
    dlat=radius_m/111320.0
    dlon=radius_m/(111320.0*max(0.1,math.cos(math.radians(lat))))
    query=[lon-dlon,lat-dlat,lon+dlon,lat+dlat]
    vals=[]
    for item in items:
        if not intersects(query,item.bbox): continue
        signed=planetary_computer.sign(item)
        href=signed.assets["occurrence"].href
        with rasterio.open(href) as ds:
            win=from_bounds(*query,transform=ds.transform)
            win=win.round_offsets().round_lengths()
            try:
                arr=ds.read(1,window=win,boundless=True,fill_value=0)
            except TypeError:
                arr=ds.read(1,window=win,boundless=True)
            tr=ds.window_transform(win)
            rr,cc=np.indices(arr.shape)
            xs=tr.c + (cc+0.5)*tr.a + (rr+0.5)*tr.b
            ys=tr.f + (cc+0.5)*tr.d + (rr+0.5)*tr.e
            dx=(xs-lon)*111320.0*math.cos(math.radians(lat))
            dy=(ys-lat)*111320.0
            mask=(dx*dx+dy*dy)<=radius_m*radius_m
            good=mask & (arr>=1) & (arr<=100)
            if np.any(good): vals.extend(arr[good].astype(float).tolist())
    if not vals: return None
    a=np.asarray(vals,float)
    return {"n_water_pixels":int(len(a)),"mean_occurrence":float(np.mean(a)),"p90_occurrence":float(np.quantile(a,.90))}

def context_all(site_ids,coords,radius):
    pts=[coords[s] for s in site_ids if s in coords]
    minlat=min(x[0] for x in pts)-0.02; maxlat=max(x[0] for x in pts)+0.02
    minlon=min(x[1] for x in pts)-0.02; maxlon=max(x[1] for x in pts)+0.02
    items=stac_items([minlon,minlat,maxlon,maxlat])
    out={}
    for i,sid in enumerate(sorted(site_ids)):
        if sid not in coords: continue
        lat,lon=coords[sid]
        out[sid]=site_metric(lat,lon,items,radius)
        if (i+1)%500==0: print(json.dumps({"radius":radius,"sites_done":i+1,"total":len(site_ids)}),flush=True)
    return out

def response_rows(raw,runs,sets,site,context,metric):
    eligible=set(runs["RunID"].astype(str)); sampled,ss=spatial.stop_matrix(raw,eligible)
    pairs=base.pair_runs(runs,sets).copy().reset_index(drop=True)
    rows=[]
    for pid,p in enumerate(pairs.itertuples(index=False)):
        w=str(p.wet_RunID); d=str(p.dry_RunID); stops=sorted(sampled[w])
        if set(stops)!=set(sampled[d]) or len(stops)!=10: raise RuntimeError("stop alignment")
        W=set(); D=set()
        for st in stops:
            W.update(ss.get((w,st),set())); D.update(ss.get((d,st),set()))
        for st in stops:
            ws=site.get((w,st)); ds=site.get((d,st))
            if ws is None or ds is None or ws!=ds: continue
            ctx=context.get(ws)
            if not ctx: continue
            occ=float(ctx[metric]); pulse=100.0-occ
            wset=set(ss.get((w,st),set())); dset=set(ss.get((d,st),set()))
            gain=sum(1 for sp in (wset-dset) if sp not in D)
            loss=sum(1 for sp in (dset-wset) if sp not in W)
            rows.append({
              "pair_id":pid,"route_cluster":str(p.route_cluster),"year_gap":int(p.year_gap),
              "rain_contrast":float(p.rain_contrast),"SiteID":ws,"pulse_raw":pulse,
              "net_route_new":float(gain-loss),"gain_route_new":float(gain)
            })
    return pd.DataFrame(rows)

def fit(df,response):
    d=df.copy()
    pair_sd=d.groupby("pair_id")["pulse_raw"].std()
    good=pair_sd[pair_sd>1e-12].index
    d=d[d.pair_id.isin(good)].copy()
    if len(d)<100: return None
    mu=float(d.pulse_raw.mean()); sd=float(d.pulse_raw.std(ddof=0))
    if sd<=0: return None
    d["pulse_z"]=(d.pulse_raw-mu)/sd
    d["inter"]=d.pulse_z*d.rain_contrast
    for col in (response,"pulse_z","inter"):
        d[col+"_w"]=d[col]-d.groupby("pair_id")[col].transform("mean")
    X=d[["pulse_z_w","inter_w"]].astype(float); y=d[response+"_w"].astype(float)
    m=sm.OLS(y,X).fit(cov_type="cluster",cov_kwds={"groups":d.route_cluster.astype(str)})
    b=float(m.params["inter_w"]); se=float(m.bse["inter_w"])
    return {
      "n_rows":int(len(d)),"n_pairs":int(d.pair_id.nunique()),"n_routes":int(d.route_cluster.nunique()),
      "n_sites":int(d.SiteID.nunique()),"pulse_mean":mu,"pulse_sd":sd,
      "interaction_beta":b,"se":se,"ci95":[b-Q*se,b+Q*se],"p":float(m.pvalues["inter_w"]),
      "support":bool(b>0 and b-Q*se>0)
    }

def main():
    raw=base.load(); runs,sets=base.build_runs(raw); pairs,site,used=pair_used_siteids(raw,runs,sets); coords=load_coords()
    used_coord={s for s in used if s in coords}
    c200=context_all(used_coord,coords,200)
    classified={s:m for s,m in c200.items() if m}
    pulse=np.asarray([100-m["mean_occurrence"] for m in classified.values()],float)
    prelim_rows=response_rows(raw,runs,sets,site,c200,"mean_occurrence")
    pair_var=prelim_rows.groupby("pair_id")["pulse_raw"].std()
    informative_ids=pair_var[pair_var>1e-12].index
    informative=prelim_rows[prelim_rows.pair_id.isin(informative_ids)]
    coverage=len(classified)/len(used_coord) if used_coord else 0.0
    variation=float(np.std(pulse,ddof=0)) if len(pulse) else 0.0
    gate=bool(coverage>=.50 and variation>=10 and informative.pair_id.nunique()>=1000 and informative.route_cluster.nunique()>=300)
    output={
      "analysis":"naamp_jrc_surface_water_context_v0_1",
      "contract":"exploration/NAAMP_JRC_SURFACE_WATER_CONTEXT_CONTRACT_V0_1.json",
      "eligibility":{
        "pair_used_siteids":int(len(used)),"with_coordinates":int(len(used_coord)),
        "classified_200m":int(len(classified)),"coverage_200m":float(coverage),
        "pulse_index_sd":variation,
        "informative_pairs":int(informative.pair_id.nunique()),
        "informative_routes":int(informative.route_cluster.nunique()),
        "overall_pass":gate
      },
      "response_endpoints_read":False
    }
    if gate:
        primary=fit(prelim_rows,"net_route_new")
        gain=fit(prelim_rows,"gain_route_new")
        exact=fit(prelim_rows[prelim_rows.year_gap==1].copy(),"net_route_new")
        p90rows=response_rows(raw,runs,sets,site,c200,"p90_occurrence")
        p90=fit(p90rows,"net_route_new")
        c500=context_all(used_coord,coords,500)
        r500=response_rows(raw,runs,sets,site,c500,"mean_occurrence")
        m500=fit(r500,"net_route_new")
        output.update({
          "response_endpoints_read":True,
          "primary_200m_mean_occurrence":primary,
          "sensitivity_gain_only":gain,
          "sensitivity_exact_year":exact,
          "sensitivity_200m_p90_occurrence":p90,
          "sensitivity_500m_mean_occurrence":m500,
          "classification":{"pulse_limited_recruitment_supported":bool(primary and primary["support"])}
        })
    OUT.write_text(json.dumps(output,indent=2,sort_keys=True)+"\n")
    print(json.dumps(output,indent=2,sort_keys=True))

if __name__=="__main__": main()
