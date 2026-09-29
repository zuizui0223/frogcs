#!/usr/bin/env python3
from __future__ import annotations

import csv, hashlib, importlib.util, io, itertools, json, math, time, urllib.error, urllib.request
from collections import defaultdict
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
NAAMP=ROOT/"scripts"/"naamp"
OUT=ROOT/"exploration"/"NAAMP_ROUTE_NEW_SPATIAL_STRUCTURE_RECEIPT_V0_1.json"
COORD_URL="https://www.sciencebase.gov/catalog/file/get/583dc314e4b0d1899f9dea8d?f=__disk__77%2F22%2F7e%2F77227ec46ac1c01592cd7d158d442cd8343a7536"
COORD_SHA="f71a87df9fc94e0d6c5d4466b4745c3bbaff874cbe7c28796b3f9eb44c2e6e83"
B=1000; KAPPA=2.0; ANCHOR=0.75
POW2=(1<<np.arange(10,dtype=np.int64))

def loadmod(name,path):
    s=importlib.util.spec_from_file_location(name,path); m=importlib.util.module_from_spec(s)
    assert s.loader; s.loader.exec_module(m); return m

base=loadmod("base",NAAMP/"run_naamp_ecological_pulse.py")
spatial=loadmod("spatial",NAAMP/"run_naamp_spatial_taxonomic_activation_decomposition.py")
uniform=loadmod("uniform",NAAMP/"run_naamp_uniform_activation_null.py")
persistence=loadmod("persistence",NAAMP/"run_naamp_persistence_preserving_null.py")

def fetch(url):
    last=None
    for i in range(6):
        try:
            req=urllib.request.Request(url,headers={"User-Agent":"frogcs-route-new-spatial-structure/0.1"})
            with urllib.request.urlopen(req,timeout=180) as r:return r.read()
        except urllib.error.HTTPError as e:
            last=e
            if e.code not in (403,429,500,502,503,504): raise
            time.sleep(2*(i+1))
        except Exception as e:
            last=e; time.sleep(2*(i+1))
    raise RuntimeError(last)

def coords():
    raw=fetch(COORD_URL); got=hashlib.sha256(raw).hexdigest()
    if got!=COORD_SHA: raise RuntimeError(f"coord hash drift {got}")
    out={}
    for r in csv.DictReader(io.StringIO(raw.decode("utf-8-sig"))):
        sid=(r.get("SiteID") or "").strip()
        if sid: out[sid]=(float(r["lat"]),float(r["lon"]))
    return out

def sites(raw,eligible):
    v=defaultdict(set)
    for s in raw["Stops.csv"]:
        rid=(s.get("RunID") or "").strip(); st=(s.get("StopNumber") or "").strip(); sid=(s.get("SiteID") or "").strip()
        if rid in eligible and st and sid and (s.get("SkippedStop") or "").strip()=="0": v[(rid,st)].add(sid)
    bad={k:x for k,x in v.items() if len(x)>1}
    if bad: raise RuntimeError(f"site conflict {list(bad)[:5]}")
    return {k:next(iter(x)) for k,x in v.items()}

def hav(a,b):
    lat1,lon1=a; lat2,lon2=b; rr=6371.0088
    p1=math.radians(lat1);p2=math.radians(lat2);dp=math.radians(lat2-lat1);dl=math.radians(lon2-lon1)
    h=math.sin(dp/2)**2+math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return 2*rr*math.asin(min(1,math.sqrt(h)))

def dm_for(cs):
    d=np.zeros((10,10))
    for i in range(10):
        for j in range(i+1,10):d[i,j]=d[j,i]=hav(cs[i],cs[j])
    return d

def mst_len(dm,idx):
    idx=list(idx)
    if len(idx)<2:return 0.0
    used={idx[0]}; total=0.0
    while len(used)<len(idx):
        best=None
        for i in used:
            for j in idx:
                if j in used:continue
                val=dm[i,j]
                if best is None or val<best[0]:best=(val,j)
        total+=best[0];used.add(best[1])
    return total

def subset_metrics(dm,nums,idx):
    idx=list(idx); k=len(idx)
    vals=[dm[i,j] for a,i in enumerate(idx) for j in idx[a+1:]]
    mpd=float(np.mean(vals))
    mst=float(mst_len(dm,idx))
    s=sorted(nums[i] for i in idx)
    adj=sum((b-a)==1 for a,b in zip(s[:-1],s[1:]))/(k-1)
    return mpd,mst,float(adj)

def lookup(dm,nums):
    refs={}
    for k in range(2,11):
        vals=[subset_metrics(dm,nums,c) for c in itertools.combinations(range(10),k)]
        refs[k]=np.mean(np.asarray(vals,float),axis=0)
    out=np.zeros((1024,3),float)
    for mask in range(1024):
        idx=[i for i in range(10) if mask&(1<<i)]
        k=len(idx)
        if k<2:continue
        obs=np.asarray(subset_metrics(dm,nums,idx),float); ref=refs[k]
        out[mask,0]=1-obs[0]/ref[0] if ref[0]>0 else 0
        out[mask,1]=1-obs[1]/ref[1] if ref[1]>0 else 0
        out[mask,2]=obs[2]-ref[2]
    return out

def stable_geometry(p,dct,site,co):
    w=str(p.wet_RunID);d=str(p.dry_RunID);ids=[]
    for st in dct["stops"]:
        a=site.get((w,st));b=site.get((d,st))
        if a is None or b is None or a!=b or a not in co:return None
        ids.append(a)
    nums=[int(float(x)) for x in dct["stops"]]
    return ids,nums

def metrics_matrix(w,d,lut):
    dry_route=d.any(axis=1); route_new=(~dry_route)&w.any(axis=1)
    masks=(w.astype(np.int64)*POW2[None,:]).sum(axis=1)
    vals=lut[masks]
    vals=vals*route_new[:,None]
    return vals.sum(axis=0)

def sim_metrics(w,d,lut):
    dry_route=d.any(axis=1)
    rn=(~dry_route[None,:])&w.any(axis=2)
    masks=(w.astype(np.int64)*POW2[None,None,:]).sum(axis=2)
    vals=lut[masks]*rn[:,:,None]
    return vals.sum(axis=1)

def stat(v,o):
    lo,hi=np.quantile(v,[.025,.975])
    return {"null_mean":float(v.mean()),"null_ci95":[float(lo),float(hi)],"observed":float(o),
            "upper_tail_p":float((1+np.sum(v>=o))/(len(v)+1))}

def main():
    raw=base.load();runs,sets=base.build_runs(raw);eligible=set(runs.RunID.astype(str))
    site=sites(raw,eligible);co=coords()
    pairs,pair_data,pools,dry_ids,sampled,ss,r0,den0,obs0,bm,rb,db,os=uniform.prepare()
    pairs=pairs.copy().reset_index(drop=True)
    keep=[];luts=[]
    for p,d in zip(pairs.itertuples(index=False),pair_data):
        g=stable_geometry(p,d,site,co);keep.append(g is not None)
        if g is None:luts.append(None)
        else:
            ids,nums=g;luts.append(lookup(dm_for([co[x] for x in ids]),nums))
    keep=np.asarray(keep,bool);idx=np.flatnonzero(keep)
    psub=pairs.iloc[idx].copy().reset_index(drop=True);dsub=[pair_data[i] for i in idx];lsub=[luts[i] for i in idx]
    r,den=uniform.design_residual(psub)
    obs_rows=np.asarray([metrics_matrix(d["wet"],d["dry"],lut) for d,lut in zip(dsub,lsub)])
    obs=(r[:,None]*obs_rows).sum(axis=0)/den

    keys={d["key"] for d in dsub};pools2={k:pools[k] for k in keys};dry2=defaultdict(set)
    for p in psub.itertuples(index=False):dry2[(str(p.State),str(p.RouteNumber),str(p.RunNumber))].add(str(p.dry_RunID))
    stops={d["key"]:d["stops"] for d in dsub}
    probs=uniform.baseline_probs(KAPPA,pools2,dry2,stops,ss)
    hist=persistence.historical_cell_probs(pools2,dry2,stops,ss)

    def simulate(kind,seed):
        rng=np.random.default_rng(seed);num=np.zeros((B,3))
        for i,(d,lut) in enumerate(zip(dsub,lsub)):
            if kind=="u":p=probs[d["key"]]
            else:
                p=(1-ANCHOR)*hist[d["key"]]+ANCHOR*d["dry"].astype(float);p=np.clip(p,1e-8,1-1e-8)
            q=uniform.solve_shift(p,d["wet_k"])
            w=rng.random((B,)+q.shape)<q[None,:,:]
            num+=r[i]*sim_metrics(w,d["dry"],lut)
        return num/den
    ub=simulate("u",uniform.SEED+61000);pb=simulate("p",uniform.SEED+62000)
    names=["total_mpd_compactness","total_mst_compactness","total_adjacency_excess"]
    U={names[j]:stat(ub[:,j],obs[j]) for j in range(3)};P={names[j]:stat(pb[:,j],obs[j]) for j in range(3)}
    support=all(obs[j]>U[names[j]]["null_ci95"][1] and obs[j]>P[names[j]]["null_ci95"][1] for j in (0,1))
    out={"analysis":"naamp_route_new_spatial_structure_v0_1",
         "contract":"exploration/NAAMP_ROUTE_NEW_SPATIAL_STRUCTURE_CONTRACT_V0_1.json",
         "coverage":{"pairs":int(len(psub)),"routes":int(psub.route_cluster.nunique())},
         "observed_betas":{names[j]:float(obs[j]) for j in range(3)},
         "uniform_kappa2":U,"persistence_anchor_0_75":P,
         "classification":{"convergent_local_cluster_support":bool(support)},
         "interpretation_boundary":{"post_readback":True,"specific_mediator_identified":False,"causal_rainfall_claim":False}}
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print(json.dumps(out,indent=2,sort_keys=True))
if __name__=="__main__":main()
