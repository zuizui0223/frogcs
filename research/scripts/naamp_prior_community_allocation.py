"""Exploratory exact-k location allocation; NOT RC6 depth explained or competition identified."""
from __future__ import annotations
import argparse
import csv
import hashlib
import importlib.util
import io
import itertools
import json
from pathlib import Path
import numpy as np
from scipy.optimize import minimize_scalar
from scipy.special import logsumexp

ROOT=Path(__file__).resolve().parents[2]

def subsets(n,k):
    return np.array(list(itertools.combinations(range(n),k)),dtype=int)

def conditional_loglik(offset,x,y,beta):
    y=np.asarray(y,bool); eta=np.asarray(offset,float)+beta*np.asarray(x,float)
    comb=subsets(len(y),int(y.sum()))
    return float(eta[y].sum()-logsumexp(eta[comb].sum(axis=1)))

def other_history(counts,exposure,target):
    exposure=np.asarray(exposure,float)
    if np.any(exposure<=0): raise ValueError('Missing prior site survey exposure')
    counts=np.asarray(counts,float)
    return (counts.sum(axis=0)-counts[target])/exposure

def loadmod(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    return mod

def prepare(cache):
    flex=loadmod('allocation_flex',ROOT/'exploration/run_naamp_flexible_common_environment_null.py')
    mem=flex.mem
    cache.mkdir(parents=True,exist_ok=True)
    raw={}; item=None
    for name,sha in mem.base.PINS.items():
        f=cache/name
        if not f.exists():
            if item is None: item=mem.base.get_json(mem.base.ITEM_URL)
            b=mem.base.get_bytes(mem.base.find_file(item,name))
            if hashlib.sha256(b).hexdigest()!=sha: raise ValueError('Source drift: '+name)
            f.write_bytes(b)
        b=f.read_bytes()
        if hashlib.sha256(b).hexdigest()!=sha: raise ValueError('Cached source drift: '+name)
        raw[name]=list(csv.DictReader(io.StringIO(b.decode('utf-8-sig'))))
        print('Validated source',name,len(raw[name]),flush=True)
    mem.load_retry=lambda:raw
    raw,runs,pairs,data,histories,pools,sampled,ss=flex.prepare_subset()
    print('Frozen history cohort',len(pairs),flush=True)
    site=mem.site_map(raw,set(runs.RunID.astype(str)))
    meta,strata,run_sites,run_species=mem.build_history_index(runs,sampled,ss,site)
    rows=[]; excluded_missing=0
    for p,dct,ph in zip(pairs.itertuples(index=False),data,histories):
        ids=mem.focal_siteids(p,dct,site)
        prior=mem.eligible_prior_runs(p,dct,ids,meta,strata,run_sites)
        species=dct['species']; lookup={sp:i for i,sp in enumerate(species)}
        counts=np.zeros((len(species),10)); exposure=np.zeros(10)
        for rid in prior:
            assert meta[rid]['year']<int(p.year_earlier)
            for j,sid in enumerate(ids):
                if sid not in run_sites[rid]: continue
                exposure[j]+=1
                for sp in run_species.get((rid,sid),set()):
                    if sp in lookup: counts[lookup[sp],j]+=1
        if np.any(exposure<=0):
            excluded_missing+=1; continue
        for i,sp in enumerate(species):
            if dct['dry'][i].any(): continue
            y=dct['wet'][i].astype(bool); k=int(y.sum())
            if k<1 or k>9: continue
            x=other_history(counts,exposure,i); x=x-x.mean()
            q=np.clip(.25*ph[i],1e-7,1-1e-7)
            offset=np.log(q)-np.log1p(-q)
            comb=subsets(10,k)
            b=offset[comb].sum(axis=1)
            b-=logsumexp(b)
            rows.append({'route':str(p.route_cluster),'fold':flex.joint.fold_for_route(str(p.route_cluster)),
                         'b':b,'x':x[comb].sum(axis=1),
                         'base_ll':conditional_loglik(offset,x,y,0),'observed_x':float(x[y].sum()),
                         'k':k,'species':sp,'constant_x':bool(np.ptp(x)<1e-12)})
    return rows,{'frozen_pairs':len(pairs),'frozen_routes':int(pairs.route_cluster.nunique()),
                 'pairs_excluded_for_any_unobserved_prior_stop':excluded_missing,'source_sha256':mem.base.PINS}

class Likelihood:
    def __init__(self,rows):
        self.b=np.concatenate([r['b'] for r in rows]); self.x=np.concatenate([r['x'] for r in rows])
        self.lengths=np.array([len(r['b']) for r in rows]); self.starts=np.r_[0,np.cumsum(self.lengths)[:-1]]
        self.obs=np.array([r['observed_x'] for r in rows]); self.base=np.array([r['base_ll'] for r in rows])
    def gain(self,beta):
        z=self.b+beta*self.x
        mx=np.maximum.reduceat(z,self.starts)
        norm=mx+np.log(np.add.reduceat(np.exp(z-np.repeat(mx,self.lengths)),self.starts))
        return beta*self.obs-norm

def fit_and_score(rows):
    fits={}; gains=np.zeros(len(rows))
    for fold in ('A','B'):
        train=[r for r in rows if r['fold']==fold]
        testidx=[i for i,r in enumerate(rows) if r['fold']!=fold]
        routes=len({r['route'] for r in train})
        if routes<30 or len(train)<100: raise ValueError('Fold coverage insufficient')
        model=Likelihood(train)
        fit=minimize_scalar(lambda b:-model.gain(b).sum(),bounds=(-5,5),method='bounded',options={'xatol':1e-7})
        if not fit.success: raise ValueError('Fit failed')
        test=Likelihood([rows[i] for i in testidx])
        gains[testidx]=test.gain(float(fit.x))
        fits[fold]={'training_routes':routes,'training_clusters':len(train),'beta':float(fit.x),
                    'boundary_optimum':bool(abs(fit.x)>4.99),'test_clusters':len(testidx),
                    'test_mean_logscore_gain':float(gains[testidx].mean())}
    routes=sorted({r['route'] for r in rows})
    sums=np.array([sum(g for r,g in zip(rows,gains) if r['route']==route) for route in routes])
    ns=np.array([sum(r['route']==route for r in rows) for route in routes])
    rng=np.random.default_rng(20261026); ix=rng.integers(0,len(routes),size=(2000,len(routes)))
    boots=sums[ix].sum(axis=1)/ns[ix].sum(axis=1)
    lo,hi=np.quantile(boots,[.025,.975])
    betas=[f['beta'] for f in fits.values()]
    decision=('NEGATIVE_HISTORY_ASSOCIATION_WITH_HELDOUT_GAIN' if lo>0 and max(betas)<0 else
              'POSITIVE_HISTORY_ASSOCIATION_WITH_HELDOUT_GAIN' if lo>0 and min(betas)>0 else
              'NO_STABLE_DIRECTIONAL_HELDOUT_GAIN')
    return {'folds':fits,'clusters':len(rows),'routes':len(routes),'taxa':len({r['species'] for r in rows}),
            'constant_exposure_clusters':sum(r['constant_x'] for r in rows),
            'heldout_mean_logscore_gain_nats_per_cluster':float(gains.mean()),
            'route_bootstrap_95ci_fixed_fitted_models':[float(lo),float(hi)],'decision':decision,
            'bootstrap_refits_models':False,'original_RC6_concentration_residual_explained':False,
            'competition_identified':False,'stop_level_habitat_fully_controlled':False}

def main():
    parser=argparse.ArgumentParser(); parser.add_argument('--cache',type=Path,required=True); parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args(); rows,provenance=prepare(args.cache)
    print('Eligible allocation clusters',len(rows),flush=True)
    result=fit_and_score(rows)
    result.update({'analysis':'NAAMP_prior_other_taxon_history_exact_k_allocation_v1',
                   'contract':'research/NAAMP_PRIOR_COMMUNITY_ALLOCATION_CONTRACT_2026-10-26.md',
                   'provenance':provenance,'code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                   'status':'POSTHOC_EXPLORATORY_LOCATION_ALLOCATION_NOT_CAUSAL',
                   'limitation':'Route-night-common weather cancels conditional on k; unmeasured local habitat/detection remain. CI>=1, not strong-call endpoint.'})
    args.out.parent.mkdir(parents=True,exist_ok=True); args.out.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2),flush=True)

if __name__=='__main__': main()
