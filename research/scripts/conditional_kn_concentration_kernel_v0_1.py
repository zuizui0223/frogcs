#!/usr/bin/env python3
"""Exact total-K + route-new-N conditioned species×stop allocation model.

Unlike conditioning on each species' k, this distribution CAN change the
within-taxon concentration statistic sum choose(max(k_s-1,0),2). It retains:
 - the observed total positive species×stop cells K;
 - the number N of wet-positive taxa that were dry-route silent;
 - a fixed cross-fitted q[s,stop] first-order baseline for the SAME CI threshold.

Optional predetermined interaction energies:
 - generic same-taxon active-stop pairs, a baseline for non-independent calling;
 - pairwise same-taxon active stops linked by a verified forest patch,
   evaluated as ADDITIONAL to generic coactivation;
 - its interaction with an INDEPENDENT guild classification;
 - event-scale soil change × strictly-prior strong-site history;
 - site forest fraction and guild × site forest fraction.

Identifiability note: if every stop pair is forest-connected, the generic
same-taxon-pair statistic and forest-link-pair statistic coincide and cannot
be separately estimated. A route-level positive link score alone is insufficient
for mechanistic attribution; the null must include generic pair dependence.

This is new, POST-HOC, exploratory methodological infrastructure.
It does not reconstruct the original JAE null-regression-conditioned beta;
it defines a separate exact-(K,N) conditional allocation estimand.
No frog data, GeoTIFFs, paid API or external resources are loaded.
"""
from __future__ import annotations
from dataclasses import dataclass
from itertools import combinations
from functools import lru_cache
import math

import numpy as np
from scipy.special import logsumexp

FEATURES=("generic_same_taxon_pairs","forest_link","terrestrial_guild_by_link",
          "soil_by_prior_strong","site_forest","guild_by_site_forest")

@lru_cache(maxsize=20)
def fixed_subsets(n):
    if n<1 or n>10:
        raise ValueError("site count outside 1..10")
    return {k:(np.empty((1,0),dtype=int) if k==0 else
               np.asarray(list(combinations(range(n),k)),dtype=int).reshape(-1,k))
            for k in range(n+1)}

def concentration(wet,dry):
    """Posterior predictive score for route-new taxa only."""
    wet=np.asarray(wet,bool)
    dry=np.asarray(dry,bool)
    if wet.shape!=dry.shape or wet.ndim!=2:
        raise ValueError("dry/wet matrices must match")
    new=(~dry.any(axis=1)) & wet.any(axis=1)
    k=wet[new].sum(axis=1)
    return int(sum(max(int(v)-1,0)*max(int(v)-2,0)//2 for v in k))

def check(event):
    required={"q","wet","dry","prior_strong","forest","forest_link",
              "guild","soil_change_z","q_response_state","response_state"}
    missing=required-set(event)
    if missing:
        raise ValueError("missing "+repr(sorted(missing)))
    q=np.asarray(event["q"],float);wet=np.asarray(event["wet"],int)
    dry=np.asarray(event["dry"],int)
    if q.ndim!=2 or q.shape[1]!=10 or q.shape!=wet.shape or dry.shape!=wet.shape:
        raise ValueError("frozen q and acoustic wet/dry require matching species×10 shape")
    if event["q_response_state"]!=event["response_state"] or \
       event["response_state"] not in {"CI_ge_1","CI_ge_2","CI_eq_3"}:
        raise ValueError("mismatch: baseline q response is not observed CallingIndex threshold")
    prior=np.asarray(event["prior_strong"],float)
    forest=np.asarray(event["forest"],float)
    conn=np.asarray(event["forest_link"],float)
    guild=np.asarray(event["guild"],float)
    soil=float(event["soil_change_z"])
    if (prior.shape!=q.shape or forest.shape!=(10,) or conn.shape!=(10,10)
            or guild.shape!=(q.shape[0],)):
        raise ValueError("context arrays do not match frozen ten-stop support")
    if not all(np.isfinite(x).all() for x in (q,wet,dry,prior,forest,conn,guild)) \
       or not math.isfinite(soil):
        raise ValueError("nonfinite values")
    if not (np.all((q>0)&(q<1)) and
            np.all((wet==0)|(wet==1)) and np.all((dry==0)|(dry==1)) and
            np.all((prior==0)|(prior==1)) and np.all((guild==0)|(guild==1))):
        raise ValueError("invalid Bernoulli probabilities, acoustic binary states or guild")
    if not (np.all((forest>=0)&(forest<=1)) and
            np.all((conn>=0)&(conn<=1)) and np.allclose(conn,conn.T) and
            np.allclose(np.diag(conn),0)):
        raise ValueError("invalid forest fraction or symmetric patch graph")
    if event.get("forest_link_source") not in ("verified_original_raster","synthetic"):
        raise ValueError("forest links are not permitted from buffer overlap alone")
    return q,wet,dry,prior,forest,conn,guild,soil

def param_vector(params):
    if set(params)-set(FEATURES):
        raise ValueError("unknown model feature names")
    out=np.array([float(params.get(name,0)) for name in FEATURES])
    if not np.isfinite(out).all():
        raise ValueError("invalid coefficients")
    return out

@dataclass
class Conditional:
    q:np.ndarray
    wet:np.ndarray
    dry:np.ndarray
    options:list
    log_partitions:list
    DP:np.ndarray
    total_K:int
    route_new_N:int
    logZ:float
    params:np.ndarray

    def observed_logprob(self):
        v=0.
        for sp,row in enumerate(self.wet):
            k=int(row.sum())
            subset=tuple(np.flatnonzero(row))
            records=self.options[sp][k]
            lookup=records["lookup"]
            if subset not in lookup:
                raise ValueError("observed subset absent")
            v+=float(records["logw"][lookup[subset]])
        return v-self.logZ

    def draw(self,rng):
        K=self.total_K
        N=self.route_new_N
        y=np.zeros_like(self.wet,dtype=np.int8)
        for sp in range(len(self.options)-1,-1,-1):
            candidates=[]
            dry_silent=not self.dry[sp].any()
            for k in range(11):
                nn=1 if k>0 and dry_silent else 0
                if k>K or nn>N:
                    continue
                prev=self.DP[sp,K-k,N-nn]
                value=prev+self.log_partitions[sp][k]
                if np.isfinite(value):
                    candidates.append((k,nn,value))
            if not candidates:
                raise RuntimeError("backward conditional partition has no support")
            logweights=np.array([v for k,n,v in candidates])
            probs=np.exp(logweights-logsumexp(logweights))
            chosen=candidates[int(rng.choice(len(candidates),p=probs))]
            k,nn=chosen[:2]
            rec=self.options[sp][k]
            weights=np.exp(rec["logw"]-self.log_partitions[sp][k])
            sel=rec["subsets"][rng.choice(len(weights),p=weights)]
            y[sp,sel]=1
            K-=k;N-=nn
        if K!=0 or N!=0 or int(y.sum())!=self.total_K:
            raise RuntimeError("conditional sampler violates frozen total-K or new-N")
        return y

def build(event,params=None,max_cells=650):
    q,wet,dry,prior,forest,conn,guild,soil=check(event)
    p=param_vector(params or {})
    S,n=q.shape
    if q.size>max_cells:
        raise ValueError("frozen support larger than audited computational bound")
    K=int(wet.sum())
    nnew=int(np.sum(~dry.any(axis=1)&wet.any(axis=1)))
    if K<0 or K>S*10 or nnew>int((~dry.any(axis=1)).sum()):
        raise ValueError("infeasible observed configuration")
    opts=[];logs=[]
    subsets=fixed_subsets(10)
    logodds=np.log(q)-np.log1p(-q)
    for sp in range(S):
        group=[];row_lz=[]
        for k in range(11):
            comb=subsets[k]
            if k==0:
                feat=np.zeros((1,len(FEATURES)),float)
                logw=np.zeros(1,float)
            else:
                hist=prior[sp,comb].sum(axis=1)
                frst=forest[comb].sum(axis=1)
                linked=np.zeros(len(comb),float)
                for i in range(k):
                    for j in range(i+1,k):
                        linked+=conn[comb[:,i],comb[:,j]]
                feat=np.column_stack((np.full(len(comb),k*(k-1)/2.0),linked,
                                      linked*guild[sp],hist*soil,
                                      frst,frst*guild[sp]))
                logw=logodds[sp,comb].sum(axis=1)+feat@p
            row_lz.append(float(logsumexp(logw)))
            group.append({"subsets":comb,"logw":logw,
                          "lookup":{tuple(row):i for i,row in enumerate(comb)}})
        opts.append(group);logs.append(row_lz)
    dp=np.full((S+1,K+1,nnew+1),-np.inf,dtype=float)
    dp[0,0,0]=0.0
    # Vectorized dynamic programming over each taxon's possible depth (0..10).
    # Avoids a Python triple-loop over all K,N states for large NAAMP matrices.
    for sp in range(S):
        dry_silent=not dry[sp].any()
        for k in range(min(10,K)+1):
            step=int(k>0 and dry_silent)
            if step>nnew:
                continue
            source=dp[sp,:K-k+1,:nnew-step+1]+logs[sp][k]
            target=dp[sp+1,k:K+1,step:nnew+1]
            dp[sp+1,k:K+1,step:nnew+1]=np.logaddexp(target,source)
    z=dp[S,K,nnew]
    if not np.isfinite(z):
        raise ValueError("no feasible exact-K-and-route-new-N configurations")
    return Conditional(q,wet,dry,opts,logs,dp,K,nnew,float(z),p)

def heldout_gain(event,alternative_params):
    base=build(event,{})
    other=build(event,alternative_params)
    return {"baseline_logscore":base.observed_logprob(),
            "proposed_logscore":other.observed_logprob(),
            "heldout_gain":other.observed_logprob()-base.observed_logprob(),
            "total_positive_cells_fixed":base.total_K,
            "route_new_taxa_count_fixed":base.route_new_N,
            "each_species_k_fixed":False,
            "independent_replication_established":False,
            "not_identical_to_frozen_JAE_conditional_beta":True}

def posterior_predictive(event,params,draws,seed):
    fit=build(event,params)
    rng=np.random.default_rng(seed)
    scores=np.asarray([concentration(fit.draw(rng),fit.dry)
                       for _ in range(draws)],float)
    return {"observed_C":concentration(fit.wet,fit.dry),
            "simulated_C_mean":float(scores.mean()),
            "simulated_C_interval95":np.quantile(scores,[.025,.975]).tolist(),
            "C_simulation_has_variance":bool(scores.std()>0),
            "K":fit.total_K,"N":fit.route_new_N,
            "fixed_species_k":False,
            "no_new_frog_mechanism_established":True}
