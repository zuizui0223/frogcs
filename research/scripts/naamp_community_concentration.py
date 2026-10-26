"""Prior community extension of NAAMP's total-calibrated concentration diagnostic."""
from __future__ import annotations
import argparse
import csv
import hashlib
import io
import json
from pathlib import Path
import numpy as np
from scipy.optimize import minimize_scalar
from scipy.special import expit
from naamp_prior_community_allocation import ROOT,loadmod,other_history

def require_disjoint_routes(train,test):
    if set(train)&set(test):raise ValueError('Route leakage')

def endpoint(w,d):
    new=(~np.asarray(d,bool).any(axis=1))&np.asarray(w,bool).any(axis=1)
    k=np.asarray(w)[new].sum(axis=1)
    extra=np.maximum(k-1,0)
    return np.array([new.sum(),extra.sum(),(extra*(extra-1)/2).sum()],float)

class ProfiledPairs:
    def __init__(self,offsets,xs,ys):
        self.n=np.array([np.size(y) for y in ys],int)
        self.start=np.r_[0,np.cumsum(self.n)[:-1]]
        self.eta=np.concatenate([np.ravel(o) for o in offsets])
        self.x=np.concatenate([np.ravel(x) for x in xs])
        self.y=np.concatenate([np.ravel(y) for y in ys]).astype(float)
        self.target=np.add.reduceat(self.y,self.start)
        if not (np.isfinite(self.eta).all() and np.isfinite(self.x).all()):raise ValueError('Nonfinite model inputs')
    def probabilities(self,beta):
        eta=self.eta+beta*self.x
        bound=np.maximum.reduceat(np.abs(eta),self.start)+40
        lo=-bound; hi=bound
        for _ in range(55):
            mid=(lo+hi)/2
            total=np.add.reduceat(expit(eta+np.repeat(mid,self.n)),self.start)
            below=total<self.target
            lo=np.where(below,mid,lo); hi=np.where(below,hi,mid)
        q=expit(eta+np.repeat((lo+hi)/2,self.n))
        q[np.repeat(self.target==0,self.n)]=0
        q[np.repeat(self.target==self.n,self.n)]=1
        if not np.allclose(np.add.reduceat(q,self.start),self.target,atol=1e-8,rtol=0):raise ValueError('Pair-total calibration failed')
        return q
    def logscores(self,beta):
        q=np.clip(self.probabilities(beta),1e-12,1-1e-12)
        return np.add.reduceat(self.y*np.log(q)+(1-self.y)*np.log1p(-q),self.start)

def load_cohort(cache):
    flex=loadmod('concentration_flex',ROOT/'exploration/run_naamp_flexible_common_environment_null.py')
    mem=flex.mem; cache.mkdir(parents=True,exist_ok=True); raw={}; item=None
    for name,sha in mem.base.PINS.items():
        path=cache/name
        if not path.exists():
            if item is None:item=mem.base.get_json(mem.base.ITEM_URL)
            b=mem.base.get_bytes(mem.base.find_file(item,name))
            if hashlib.sha256(b).hexdigest()!=sha:raise ValueError('Source drift: '+name)
            path.write_bytes(b)
        b=path.read_bytes()
        if hashlib.sha256(b).hexdigest()!=sha:raise ValueError('Cache drift: '+name)
        raw[name]=list(csv.DictReader(io.StringIO(b.decode('utf-8-sig'))))
        print('Validated',name,len(raw[name]),flush=True)
    mem.load_retry=lambda:raw
    raw,runs,pairs,data,hist,pools,sampled,ss=flex.prepare_subset()
    r,den=flex.uniform.design_residual(pairs)
    obs=(r[:,None]*np.array([endpoint(d['wet'],d['dry']) for d in data])).sum(axis=0)/den
    if abs(obs[2]-1.6503201354367818)>1e-9:raise ValueError('Original concentration beta drift')
    site=mem.site_map(raw,set(runs.RunID.astype(str)))
    meta,strata,run_sites,run_species=mem.build_history_index(runs,sampled,ss,site)
    keep=[]; xs=[]
    for idx,(p,dct) in enumerate(zip(pairs.itertuples(index=False),data)):
        ids=mem.focal_siteids(p,dct,site)
        prior=mem.eligible_prior_runs(p,dct,ids,meta,strata,run_sites)
        lookup={sp:i for i,sp in enumerate(dct['species'])}
        count=np.zeros((len(lookup),10)); exposure=np.zeros(10)
        for rid in prior:
            if meta[rid]['year']>=int(p.year_earlier):raise ValueError('Future history')
            for j,sid in enumerate(ids):
                if sid not in run_sites[rid]:continue
                exposure[j]+=1
                for sp in run_species.get((rid,sid),set()):
                    if sp in lookup:count[lookup[sp],j]+=1
        if np.any(exposure<=0):continue
        x=np.array([other_history(count,exposure,i) for i in range(len(lookup))])
        xs.append(x-x.mean()); keep.append(idx)
    audit={'full_history_pairs':len(pairs),'full_history_routes':int(pairs.route_cluster.nunique()),
           'full_history_observed_N_L_C':obs.tolist(),'excluded_missing_history_pairs':len(pairs)-len(keep),
           'source_sha256':mem.base.PINS}
    return flex,runs,pairs.iloc[keep].reset_index(drop=True),[data[i] for i in keep],[hist[i] for i in keep],xs,pools,sampled,ss,audit

def evaluate(flex,runs,pairs,data,hist,xs,pools,sampled,ss):
    joint=flex.joint; routes=pairs.route_cluster.astype(str).to_numpy()
    fold=np.array([joint.fold_for_route(r) for r in routes])
    all_species=sorted({s for v in pools.values() for s in v})
    qs=[{},{}]; gains=np.zeros(len(data)); audits={}
    for training in ['A','B']:
        train=np.flatnonzero(fold==training); test=np.flatnonzero(fold!=training)
        require_disjoint_routes(routes[train],routes[test])
        if len(set(routes[train]))<30 or len(train)<100:raise ValueError('Insufficient fold')
        slopes,sp_audit,fit_audit=joint.fit_species_slopes(runs,sampled,ss,all_species,training)
        print('Fitted environmental slopes',training,fit_audit,flush=True)
        offsets=[]
        for p,dct,ph in zip(pairs.itertuples(index=False),data,hist):
            anchor=np.clip(.25*ph+.75*dct['dry'].astype(float),1e-8,1-1e-8)
            gamma=np.array([slopes.get(sp,0.) for sp in dct['species']])
            offsets.append(np.log(anchor)-np.log1p(-anchor)+gamma[:,None]*float(p.rain_contrast))
        def model(ix):return ProfiledPairs([offsets[i] for i in ix],[xs[i] for i in ix],[data[i]['wet'] for i in ix])
        m=model(train)
        fit=minimize_scalar(lambda beta:-m.logscores(beta).sum(),bounds=(-5,5),method='bounded',options={'xatol':1e-6})
        if not fit.success:raise ValueError('Biotic fit failed')
        held=model(test); beta=float(fit.x)
        gains[test]=held.logscores(beta)-held.logscores(0)
        for which,b in enumerate([0.,beta]):
            flat=held.probabilities(b)
            for j,i in enumerate(test):
                qs[which][i]=flat[held.start[j]:held.start[j]+held.n[j]].reshape(data[i]['wet'].shape)
        audits[training]={'environment_training':fit_audit,'beta':beta,'boundary_optimum':abs(beta)>4.99,
                          'training_pairs':len(train),'test_pairs':len(test),
                          'environment_species_estimable':sum(x['estimable'] for x in sp_audit.values()),
                          'heldout_gain_per_cell':float(gains[test].sum()/held.n.sum())}
        print('Biotic coefficient',training,beta,flush=True)
    unique=sorted(set(routes)); ncell=np.array([d['wet'].size for d in data])
    by_route=np.array([[gains[routes==r].sum(),ncell[routes==r].sum()] for r in unique])
    rng=np.random.default_rng(20261027); ix=rng.integers(0,len(unique),size=(2000,len(unique)))
    ci=np.quantile(by_route[ix,0].sum(axis=1)/by_route[ix,1].sum(axis=1),[.025,.975])
    r,den=flex.uniform.design_residual(pairs)
    obs=(r[:,None]*np.array([endpoint(d['wet'],d['dry']) for d in data])).sum(axis=0)/den
    sims=[np.zeros((2000,3)),np.zeros((2000,3))]
    rng=np.random.default_rng(20261027)
    for i,d in enumerate(data):
        u=rng.random((2000,)+d['wet'].shape)
        for which in range(2):
            sims[which]+=r[i]*flex.sim_metrics(u<qs[which][i][None,:,:],d['dry'])
    sims=[x/den for x in sims]
    models={}
    for name,sim in zip(['M0_environment_own_history_dry_anchor','M1_add_prior_other_taxa'],sims):
        models[name]={'raw_predicted_N_L_C_mean':sim.mean(axis=0).tolist(),
                      'conditional_C':flex.conditional(sim,obs)}
    delta=models['M0_environment_own_history_dry_anchor']['conditional_C']['observed_conditional_residual']-models['M1_add_prior_other_taxa']['conditional_C']['observed_conditional_residual']
    return {'coverage':{'pairs':len(data),'routes':len(unique),'species_stop_cells':int(ncell.sum())},
            'folds':audits,'observed_N_L_C':obs.tolist(),'models':models,
            'M0_minus_M1_conditional_C_residual':float(delta),
            'oracle_total_calibrated_logscore_gain_per_cell':float(gains.sum()/ncell.sum()),
            'fixed_model_route_bootstrap_95ci_gain_per_cell':ci.tolist(),
            'simulation_draws':2000,'simulation_seed':20261027,'independent_simulation_per_species_stop':True,
            'heldout_response_total_used_for_calibration':True,'unconditional_prediction':False,
            'same_subset_comparison':True,'causal_competition_fraction_identified':False,
            'direct_local_water_vegetation_adjustment':False,'model_refitting_in_bootstrap':False}

def main():
    p=argparse.ArgumentParser();p.add_argument('--cache',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    a=p.parse_args(); flex,runs,pairs,data,hist,xs,pools,sampled,ss,audit=load_cohort(a.cache)
    print('Eligible pairs',len(pairs),flush=True)
    result=evaluate(flex,runs,pairs,data,hist,xs,pools,sampled,ss)
    result.update({'analysis':'NAAMP_prior_community_original_concentration_diagnostic_v1','status':'POSTHOC_EXPLORATORY_ORACLE_TOTAL_CONFIGURATION',
                   'contract':'research/NAAMP_COMMUNITY_CONCENTRATION_CONTRACT_2026-10-26.md',
                   'provenance':audit,'code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()})
    a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
    print(json.dumps(result,indent=2),flush=True)

if __name__=='__main__':main()
