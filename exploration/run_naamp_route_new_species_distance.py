#!/usr/bin/env python3
from __future__ import annotations

import csv, hashlib, importlib.util, io, json, math, time, urllib.error, urllib.request
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT=Path(__file__).resolve().parents[1]
NAAMP=ROOT/"scripts"/"naamp"
OUT=ROOT/"exploration"/"NAAMP_ROUTE_NEW_SPECIES_DISTANCE_RECEIPT_V0_1.json"
COORD_URL="https://www.sciencebase.gov/catalog/file/get/583dc314e4b0d1899f9dea8d?f=__disk__77%2F22%2F7e%2F77227ec46ac1c01592cd7d158d442cd8343a7536"
COORD_SHA="f71a87df9fc94e0d6c5d4466b4745c3bbaff874cbe7c28796b3f9eb44c2e6e83"
B=1000
KAPPA=2.0
ANCHOR=0.75


def loadmod(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    mod=importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(mod)
    return mod


base=loadmod("base",NAAMP/"run_naamp_ecological_pulse.py")
spatial=loadmod("spatial",NAAMP/"run_naamp_spatial_taxonomic_activation_decomposition.py")
uniform=loadmod("uniform",NAAMP/"run_naamp_uniform_activation_null.py")
persistence=loadmod("persistence",NAAMP/"run_naamp_persistence_preserving_null.py")


def fetch(url,retries=6):
    last=None
    for i in range(retries):
        try:
            req=urllib.request.Request(url,headers={"User-Agent":"frogcs-route-new-distance/0.1"})
            with urllib.request.urlopen(req,timeout=180) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            last=e
            if e.code not in (403,429,500,502,503,504):
                raise
            time.sleep(2*(i+1))
        except Exception as e:
            last=e
            time.sleep(2*(i+1))
    raise RuntimeError(f"fetch failed: {last}")


def load_coords():
    raw=fetch(COORD_URL)
    got=hashlib.sha256(raw).hexdigest()
    if got!=COORD_SHA:
        raise RuntimeError(f"Coordinates hash drift: {got}")
    rows=list(csv.DictReader(io.StringIO(raw.decode("utf-8-sig"))))
    out={}
    for r in rows:
        sid=(r.get("SiteID") or "").strip()
        if not sid:
            continue
        lat=float(r["lat"]); lon=float(r["lon"])
        if sid in out and out[sid]!=(lat,lon):
            raise RuntimeError(f"coordinate conflict {sid}")
        out[sid]=(lat,lon)
    return out


def site_map(raw,eligible):
    vals=defaultdict(set)
    for s in raw["Stops.csv"]:
        rid=(s.get("RunID") or "").strip()
        st=(s.get("StopNumber") or "").strip()
        sid=(s.get("SiteID") or "").strip()
        if rid not in eligible or (s.get("SkippedStop") or "").strip()!="0" or not st:
            continue
        if sid:
            vals[(rid,st)].add(sid)
    bad={k:v for k,v in vals.items() if len(v)>1}
    if bad:
        raise RuntimeError(f"multiple SiteID values per run-stop: {list(bad)[:10]}")
    return {k:next(iter(v)) for k,v in vals.items() if v}


def haversine_km(a,b):
    lat1,lon1=a; lat2,lon2=b
    rr=6371.0088
    p1=math.radians(lat1); p2=math.radians(lat2)
    dp=math.radians(lat2-lat1); dl=math.radians(lon2-lon1)
    h=math.sin(dp/2)**2+math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return 2*rr*math.asin(min(1.0,math.sqrt(h)))


def distance_matrix(stop_coords):
    n=len(stop_coords)
    d=np.zeros((n,n),float)
    for i in range(n):
        for j in range(i+1,n):
            x=haversine_km(stop_coords[i],stop_coords[j])
            d[i,j]=d[j,i]=x
    return d


def pair_stable_complete(p,stops,site,coords):
    w=str(p.wet_RunID); d=str(p.dry_RunID)
    ids=[]
    for st in stops:
        ws=site.get((w,st)); ds=site.get((d,st))
        if ws is None or ds is None or ws!=ds or ws not in coords:
            return None
        ids.append(ws)
    return ids


def species_spans_from_matrix(w,d,dm):
    d_route=d.any(axis=1)
    route_new=(~d_route)&w.any(axis=1)
    idx=np.flatnonzero(route_new)
    if len(idx)==0:
        return 0.0,0.0,0.0
    spans=[]
    multi=0
    for s in idx:
        occ=np.flatnonzero(w[s])
        if len(occ)>=2:
            multi+=1
            spans.append(float(np.max(dm[np.ix_(occ,occ)])))
        else:
            spans.append(0.0)
    a=np.asarray(spans,float)
    return float(a.sum()),float(a.mean()),float(multi)


def simulated_spans(w,d,dm):
    # w: B x species x stop
    d_route=d.any(axis=1)
    route_new=(~d_route[None,:])&w.any(axis=2)
    occ_n=w.sum(axis=2)
    spans=np.zeros((w.shape[0],w.shape[1]),float)
    for i in range(dm.shape[0]):
        for j in range(i+1,dm.shape[1]):
            if dm[i,j]<=0:
                continue
            both=w[:,:,i]&w[:,:,j]
            spans=np.maximum(spans,both.astype(float)*dm[i,j])
    spans*=route_new
    total=spans.sum(axis=1)
    n=route_new.sum(axis=1)
    mean=np.divide(total,n,out=np.zeros_like(total),where=n>0)
    multi=((occ_n>=2)&route_new).sum(axis=1).astype(float)
    return np.column_stack([total,mean,multi])


def stat(v,obs):
    lo,hi=np.quantile(v,[.025,.975])
    return {
        "null_mean":float(np.mean(v)),
        "null_ci95":[float(lo),float(hi)],
        "observed":float(obs),
        "upper_tail_p":float((1+np.sum(v>=obs))/(len(v)+1)),
        "lower_tail_p":float((1+np.sum(v<=obs))/(len(v)+1))
    }


def main():
    raw=base.load()
    runs,sets=base.build_runs(raw)
    eligible=set(runs["RunID"].astype(str))
    sampled,_=spatial.stop_matrix(raw,eligible)
    site=site_map(raw,eligible)
    coords=load_coords()

    pairs,pair_data,pools,dry_ids,sampled0,ss,r0,den0,obs0,bm,rb,db,os=uniform.prepare()
    pairs=pairs.copy().reset_index(drop=True)

    keep=[]
    dms=[]
    for p,dct in zip(pairs.itertuples(index=False),pair_data):
        stops=dct["stops"]
        ids=pair_stable_complete(p,stops,site,coords)
        keep.append(ids is not None)
        dms.append(distance_matrix([coords[s] for s in ids]) if ids is not None else None)

    keep=np.asarray(keep,bool)
    idx=np.flatnonzero(keep)
    psub=pairs.iloc[idx].copy().reset_index(drop=True)
    dsub=[pair_data[int(i)] for i in idx]
    dmsub=[dms[int(i)] for i in idx]
    gate=bool(len(psub)>=3500 and psub.route_cluster.nunique()>=450)

    out={
      "analysis":"naamp_route_new_species_distance_v0_1",
      "contract":"exploration/NAAMP_ROUTE_NEW_SPECIES_DISTANCE_CONTRACT_V0_1.json",
      "coverage":{"pairs":int(len(psub)),"routes":int(psub.route_cluster.nunique()),"gate":gate},
      "response_endpoints_read":False
    }
    if not gate:
        OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
        print(json.dumps(out,indent=2,sort_keys=True))
        return

    r,den=uniform.design_residual(psub)
    obs_rows=np.asarray([
        species_spans_from_matrix(d["wet"],d["dry"],dm)
        for d,dm in zip(dsub,dmsub)
    ],float)
    obs=(r[:,None]*obs_rows).sum(axis=0)/den

    keys={d["key"] for d in dsub}
    pools_sub={k:pools[k] for k in keys}
    dry_ids_sub=defaultdict(set)
    for p in psub.itertuples(index=False):
        key=(str(p.State),str(p.RouteNumber),str(p.RunNumber))
        dry_ids_sub[key].add(str(p.dry_RunID))
    stops_by_key={d["key"]:d["stops"] for d in dsub}
    probs=uniform.baseline_probs(KAPPA,pools_sub,dry_ids_sub,stops_by_key,ss)
    hist=persistence.historical_cell_probs(pools_sub,dry_ids_sub,stops_by_key,ss)

    def simulate(kind,seed):
        rng=np.random.default_rng(seed)
        num=np.zeros((B,3),float)
        for i,(d,dm) in enumerate(zip(dsub,dmsub)):
            if kind=="uniform":
                p=probs[d["key"]]
            else:
                p=(1-ANCHOR)*hist[d["key"]]+ANCHOR*d["dry"].astype(float)
                p=np.clip(p,1e-8,1-1e-8)
            q=uniform.solve_shift(p,d["wet_k"])
            w=rng.random((B,)+q.shape)<q[None,:,:]
            met=simulated_spans(w,d["dry"],dm)
            num += r[i]*met
        return num/den

    ub=simulate("uniform",uniform.SEED+51000)
    pb=simulate("persistence",uniform.SEED+52000)
    names=["total_route_new_span_km","mean_route_new_span_km","multi_stop_route_new_species"]
    us={names[j]:stat(ub[:,j],obs[j]) for j in range(3)}
    ps={names[j]:stat(pb[:,j],obs[j]) for j in range(3)}
    broad=bool(
        obs[0]>us[names[0]]["null_ci95"][1]
        and obs[0]>ps[names[0]]["null_ci95"][1]
        and obs[1]>us[names[1]]["null_ci95"][1]
        and obs[1]>ps[names[1]]["null_ci95"][1]
    )
    compact=bool(
        obs[0]<us[names[0]]["null_ci95"][0]
        and obs[0]<ps[names[0]]["null_ci95"][0]
        and obs[1]<us[names[1]]["null_ci95"][0]
        and obs[1]<ps[names[1]]["null_ci95"][0]
    )
    out.update({
      "response_endpoints_read":True,
      "observed_betas":{names[j]:float(obs[j]) for j in range(3)},
      "uniform_kappa2":us,
      "persistence_anchor_0_75":ps,
      "classification":{
        "broad_route_scale_activation_supported":broad,
        "compact_route_new_activation_supported_post_readback":compact,
        "compactness_contract":"exploration/NAAMP_ROUTE_NEW_SPECIES_COMPACTNESS_DIAGNOSTIC_V0_1.json"
      },
      "descriptive":{
        "median_route_max_stop_distance_km":float(np.median([np.max(dm) for dm in dmsub])),
        "q90_route_max_stop_distance_km":float(np.quantile([np.max(dm) for dm in dmsub],.90))
      },
      "interpretation_boundary":{
        "individual_movement_inferred":False,
        "atmospheric_cue_identified":False,
        "hydrological_cue_identified":False,
        "causal_rainfall_claim":False
      }
    })
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,indent=2,sort_keys=True))


if __name__=="__main__":
    main()
