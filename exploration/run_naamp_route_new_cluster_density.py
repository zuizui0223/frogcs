#!/usr/bin/env python3
from __future__ import annotations

import csv, hashlib, importlib.util, io, itertools, json, math, time, urllib.error, urllib.request
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT=Path(__file__).resolve().parents[1]
NAAMP=ROOT/"scripts"/"naamp"
OUT=ROOT/"exploration"/"NAAMP_ROUTE_NEW_CLUSTER_DENSITY_RECEIPT_V0_1.json"
COORD_URL="https://www.sciencebase.gov/catalog/file/get/583dc314e4b0d1899f9dea8d?f=__disk__77%2F22%2F7e%2F77227ec46ac1c01592cd7d158d442cd8343a7536"
COORD_SHA="f71a87df9fc94e0d6c5d4466b4745c3bbaff874cbe7c28796b3f9eb44c2e6e83"
B=1000; KAPPA=2.0; ANCHOR=0.75

def loadmod(name,path):
    s=importlib.util.spec_from_file_location(name,path); m=importlib.util.module_from_spec(s)
    assert s.loader; s.loader.exec_module(m); return m

base=loadmod("base",NAAMP/"run_naamp_ecological_pulse.py")
spatial=loadmod("spatial",NAAMP/"run_naamp_spatial_taxonomic_activation_decomposition.py")
uniform=loadmod("uniform",NAAMP/"run_naamp_uniform_activation_null.py")
persistence=loadmod("persistence",NAAMP/"run_naamp_persistence_preserving_null.py")

def fetch(url,retries=6):
    last=None
    for i in range(retries):
        try:
            req=urllib.request.Request(url,headers={"User-Agent":"frogcs-route-new-cluster-density/0.1"})
            with urllib.request.urlopen(req,timeout=180) as r: return r.read()
        except urllib.error.HTTPError as e:
            last=e
            if e.code not in (403,429,500,502,503,504): raise
            time.sleep(2*(i+1))
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
        if sid in out and out[sid]!=(lat,lon): raise RuntimeError(f"coord conflict {sid}")
        out[sid]=(lat,lon)
    return out

def site_map(raw,eligible):
    vals=defaultdict(set)
    for s in raw["Stops.csv"]:
        rid=(s.get("RunID") or "").strip(); st=(s.get("StopNumber") or "").strip(); sid=(s.get("SiteID") or "").strip()
        if rid not in eligible or (s.get("SkippedStop") or "").strip()!="0" or not st: continue
        if sid: vals[(rid,st)].add(sid)
    bad={k:v for k,v in vals.items() if len(v)>1}
    if bad: raise RuntimeError(f"multiple SiteIDs {list(bad)[:10]}")
    return {k:next(iter(v)) for k,v in vals.items() if v}

def hav(a,b):
    lat1,lon1=a; lat2,lon2=b; rr=6371.0088
    p1=math.radians(lat1); p2=math.radians(lat2); dp=math.radians(lat2-lat1); dl=math.radians(lon2-lon1)
    h=math.sin(dp/2)**2+math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return 2*rr*math.asin(min(1,math.sqrt(h)))

def dm(coords):
    n=len(coords); x=np.zeros((n,n),float)
    for i in range(n):
        for j in range(i+1,n): x[i,j]=x[j,i]=hav(coords[i],coords[j])
    return x

def expected_span_by_k(dmat):
    out={}
    ids=range(dmat.shape[0])
    for k in range(2,dmat.shape[0]+1):
        spans=[]
        for comb in itertools.combinations(ids,k):
            a=np.asarray(comb,int)
            spans.append(float(np.max(dmat[np.ix_(a,a)])))
        out[k]=float(np.mean(spans))
    return out

def stable_ids(p,stops,site,coords):
    w=str(p.wet_RunID); d=str(p.dry_RunID); ids=[]
    for st in stops:
        ws=site.get((w,st)); ds=site.get((d,st))
        if ws is None or ds is None or ws!=ds or ws not in coords: return None
        ids.append(ws)
    return ids

def metrics(w,d,dmat,expected):
    dryroute=d.any(axis=1); route_new=(~dryroute)&w.any(axis=1)
    vals=[]
    for s in np.flatnonzero(route_new):
        occ=np.flatnonzero(w[s]); k=len(occ)
        if k<2: continue
        span=float(np.max(dmat[np.ix_(occ,occ)])); ref=float(expected[k])
        if ref<=0: continue
        vals.append(1.0-span/ref)
    if not vals: return np.asarray([0.0,0.0,0.0],float)
    a=np.asarray(vals,float)
    return np.asarray([float(a.sum()),float(a.mean()),float(len(a))],float)

def sim_metrics(w,d,dmat,expected):
    # w B x species x stop
    dryroute=d.any(axis=1)
    route_new=(~dryroute[None,:])&w.any(axis=2)
    occn=w.sum(axis=2)
    maxspan=np.zeros((w.shape[0],w.shape[1]),float)
    for i in range(dmat.shape[0]):
        for j in range(i+1,dmat.shape[1]):
            if dmat[i,j]<=0: continue
            both=w[:,:,i]&w[:,:,j]
            maxspan=np.maximum(maxspan,both*dmat[i,j])
    total=np.zeros(w.shape[0],float); count=np.zeros(w.shape[0],float)
    for k in range(2,11):
        mask=route_new&(occn==k)
        ref=float(expected[k])
        score=(1.0-maxspan/ref)*mask
        total+=score.sum(axis=1); count+=mask.sum(axis=1)
    mean=np.divide(total,count,out=np.zeros_like(total),where=count>0)
    return np.column_stack([total,mean,count])

def stat(v,obs):
    lo,hi=np.quantile(v,[.025,.975])
    return {"null_mean":float(np.mean(v)),"null_ci95":[float(lo),float(hi)],"observed":float(obs),
            "upper_tail_p":float((1+np.sum(v>=obs))/(len(v)+1))}

def main():
    raw=base.load(); runs,sets=base.build_runs(raw); eligible=set(runs["RunID"].astype(str))
    sampled,_=spatial.stop_matrix(raw,eligible); site=site_map(raw,eligible); coords=load_coords()
    pairs,pair_data,pools,dry_ids,sampled0,ss,r0,den0,obs0,bm,rb,db,os=uniform.prepare()
    pairs=pairs.copy().reset_index(drop=True)

    keep=[]; dm_all=[]; ex_all=[]
    for p,d in zip(pairs.itertuples(index=False),pair_data):
        ids=stable_ids(p,d["stops"],site,coords)
        keep.append(ids is not None)
        if ids is None:
            dm_all.append(None); ex_all.append(None)
        else:
            dd=dm([coords[s] for s in ids]); dm_all.append(dd); ex_all.append(expected_span_by_k(dd))
    idx=np.flatnonzero(np.asarray(keep,bool))
    psub=pairs.iloc[idx].copy().reset_index(drop=True); dsub=[pair_data[int(i)] for i in idx]
    dms=[dm_all[int(i)] for i in idx]; exps=[ex_all[int(i)] for i in idx]
    if len(psub)<3500 or psub.route_cluster.nunique()<450: raise RuntimeError("coverage gate failed")

    r,den=uniform.design_residual(psub)
    obsrows=np.asarray([metrics(d["wet"],d["dry"],dd,ex) for d,dd,ex in zip(dsub,dms,exps)],float)
    obs=(r[:,None]*obsrows).sum(axis=0)/den

    keys={d["key"] for d in dsub}; pools_sub={k:pools[k] for k in keys}; dry_sub=defaultdict(set)
    for p in psub.itertuples(index=False):
        dry_sub[(str(p.State),str(p.RouteNumber),str(p.RunNumber))].add(str(p.dry_RunID))
    stops={d["key"]:d["stops"] for d in dsub}
    probs=uniform.baseline_probs(KAPPA,pools_sub,dry_sub,stops,ss)
    hist=persistence.historical_cell_probs(pools_sub,dry_sub,stops,ss)

    def simulate(kind,seed):
        rng=np.random.default_rng(seed); num=np.zeros((B,3),float)
        for i,(d,dd,ex) in enumerate(zip(dsub,dms,exps)):
            if kind=="uniform": p=probs[d["key"]]
            else:
                p=(1-ANCHOR)*hist[d["key"]]+ANCHOR*d["dry"].astype(float); p=np.clip(p,1e-8,1-1e-8)
            q=uniform.solve_shift(p,d["wet_k"]); w=rng.random((B,)+q.shape)<q[None,:,:]
            num+=r[i]*sim_metrics(w,d["dry"],dd,ex)
        return num/den

    ub=simulate("uniform",uniform.SEED+61000); pb=simulate("persistence",uniform.SEED+62000)
    names=["total_compactness","mean_compactness","multi_stop_route_new_species"]
    us={names[j]:stat(ub[:,j],obs[j]) for j in range(3)}; ps={names[j]:stat(pb[:,j],obs[j]) for j in range(3)}
    supported=bool(obs[0]>us[names[0]]["null_ci95"][1] and obs[0]>ps[names[0]]["null_ci95"][1]
                   and obs[1]>us[names[1]]["null_ci95"][1] and obs[1]>ps[names[1]]["null_ci95"][1])
    out={"analysis":"naamp_route_new_cluster_density_v0_1",
         "contract":"exploration/NAAMP_ROUTE_NEW_CLUSTER_DENSITY_CONTRACT_V0_1.json",
         "coverage":{"pairs":int(len(psub)),"routes":int(psub.route_cluster.nunique())},
         "observed_betas":{names[j]:float(obs[j]) for j in range(3)},
         "uniform_kappa2":us,"persistence_anchor_0_75":ps,
         "classification":{"cluster_density_excess_supported":supported},
         "interpretation_boundary":{"post_readback":True,"causal_rainfall_claim":False,"specific_mediator_identified":False}}
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n"); print(json.dumps(out,indent=2,sort_keys=True))
if __name__=="__main__": main()
