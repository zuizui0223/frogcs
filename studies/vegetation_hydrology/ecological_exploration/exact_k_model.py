#!/usr/bin/env python3
"""Pre-readback exact-k ten-site conditional acoustic location model.

For each taxon x pair, condition on the realised k of 10 strong-chorus sites.
Analytic score and fixed ridge penalty, geography-folded by complete route.
No source download or frog-outcome file access in this library.
"""
from __future__ import annotations
import hashlib
from functools import lru_cache
from itertools import combinations
import numpy as np
from scipy.optimize import minimize
from scipy.special import logsumexp

LAMBDA=1.0
N_STOPS=10
N_FOLDS=5
SEED=2840223

@lru_cache(None)
def masks_for_k(k):
    if not 2<=k<=9:
        raise ValueError("k must permit nontrivial multi-site placement")
    choices=list(combinations(range(N_STOPS),k))
    m=np.zeros((len(choices),N_STOPS),float)
    for j,indices in enumerate(choices):
        m[j,list(indices)]=1.
    return m

def route_fold(state,route):
    key=(str(state)+":"+str(route)).encode("utf-8")
    return int(hashlib.sha256(key).hexdigest()[:8],16)%N_FOLDS

def group_features(raw10,active10):
    x=np.asarray(raw10,float)
    y=np.asarray(active10,int)
    if x.ndim!=2 or x.shape[0]!=10 or not np.isfinite(x).all():
        raise ValueError("complete ten-site finite feature matrix required")
    if y.shape!=(10,) or not np.isin(y,[0,1]).all():
        raise ValueError("ten binary CallingIndex CI2/3 cells required")
    k=int(y.sum());ms=masks_for_k(k)
    x=x-x.mean(axis=0,keepdims=True)
    return k,ms@x,y@x

def _loss_gradient(beta,groups,penalty):
    cost=.5*penalty*float(beta@beta)
    grad=penalty*beta.copy()
    for permutations,selected in groups:
        logits=permutations@beta
        lse=logsumexp(logits)
        p=np.exp(logits-lse)
        cost+=float(lse-selected@beta)
        grad+=p@permutations-selected
    return cost,grad

def fit(groups,n_features,penalty=LAMBDA):
    if not groups:raise ValueError("empty train fold")
    sol=minimize(_loss_gradient,np.zeros(n_features),
        args=(groups,penalty),method="L-BFGS-B",jac=True,
        options={"maxiter":350,"ftol":1e-12,"gtol":1e-8})
    if not sol.success and np.linalg.norm(sol.jac)>1e-5:
        raise RuntimeError("exact-k optimization did not converge: "+str(sol.message))
    if not np.isfinite(sol.x).all():
        raise RuntimeError("invalid coefficients")
    return sol.x

def event_matrices(record,feature_ids):
    x=np.asarray(record["x"],float)[:,feature_ids]
    _,possible,selected=group_features(x,record["y"])
    return possible,selected

def log_probability(beta,possible,selected):
    return float(selected@beta-logsumexp(possible@beta))

def heldout_scores(records,feature_ids):
    if not records:raise ValueError("no eligible events")
    fold=np.array([route_fold(r["State"],r["RouteNumber"]) for r in records])
    result=np.full(len(records),np.nan)
    fitted={}
    for held in range(N_FOLDS):
        tr=np.flatnonzero(fold!=held);te=np.flatnonzero(fold==held)
        if not len(tr) or not len(te):
            raise RuntimeError("route-fold data insufficient")
        train=[event_matrices(records[i],feature_ids) for i in tr]
        beta=fit(train,len(feature_ids))
        fitted[str(held)]=beta.tolist()
        for i in te:
            possible,selected=event_matrices(records[i],feature_ids)
            result[i]=log_probability(beta,possible,selected)
    if not np.isfinite(result).all():
        raise RuntimeError("incomplete route-disjoint heldout scores")
    return result,fitted

def route_cluster_interval(records,difference,nboot=1200):
    by_route={}
    for event,d in zip(records,difference):
        key=(event["State"],event["RouteNumber"])
        by_route.setdefault(key,[]).append(float(d))
    if len(by_route)<2:raise RuntimeError("insufficient independent routes")
    arr=np.array([(len(v),sum(v)) for v in by_route.values()],float)
    rng=np.random.default_rng(SEED)
    index=rng.integers(0,len(arr),size=(nboot,len(arr)))
    grouped=arr[index].sum(axis=1)
    ratio=grouped[:,1]/grouped[:,0]
    return list(map(float,np.quantile(ratio,[.025,.975])))
