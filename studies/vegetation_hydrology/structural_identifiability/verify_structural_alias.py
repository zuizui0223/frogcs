#!/usr/bin/env python3
"""Fixed-k ten-stop acoustic placement: structural identification theorem.

No NAAMP frog outcomes accessed. See prereadback protocol and empirical
rank audit results for the separate environment-only test.
"""
from __future__ import annotations

from itertools import combinations
from math import comb
import numpy as np

FIXED_SITE_COUNT = 10
SIMULATION_SEED = 2840223

def probabilities(eta, k):
    """All exactly-k configurations over ten sites, with stable normalization."""
    e=np.asarray(eta,float)
    if e.shape!=(FIXED_SITE_COUNT,) or not np.isfinite(e).all():
        raise ValueError("ten finite fixed-site weights required")
    if not 1<=k<=FIXED_SITE_COUNT:
        raise ValueError("invalid k")
    subsets=np.asarray(list(combinations(range(FIXED_SITE_COUNT),k)),int)
    logits=e[subsets].sum(axis=1)
    shifted=logits-logits.max()
    unscaled=np.exp(shifted)
    p=unscaled/unscaled.sum()
    if len(p)!=comb(FIXED_SITE_COUNT,k) or not np.isclose(p.sum(),1):
        raise RuntimeError("bad exact-k denominator")
    return p

def aliased_parameterizations(wetland,openwater,site_effect,habitat_beta=(2.0,.8)):
    w=np.asarray(wetland,float)
    o=np.asarray(openwater,float)
    u=np.asarray(site_effect,float)
    if w.shape!=(10,) or o.shape!=(10,) or u.shape!=(10,):
        raise ValueError("need ten locations")
    habitat=habitat_beta[0]*w+habitat_beta[1]*o
    # Model A: true habitat coefficient + original persistent site process
    model_A=habitat+u
    # Model B: ZERO habitat coefficient, identical fixed-site preferences
    model_B=u+habitat
    return model_A,model_B

def site_specific_change_rank(water_initial,water_next):
    a=np.asarray(water_initial,float);b=np.asarray(water_next,float)
    if a.shape!=b.shape or a.ndim!=1 or len(a)<6 or not np.isfinite(a).all() or not np.isfinite(b).all():
        raise ValueError("at least six matched, observed water measures required")
    d=b-a
    centred=d-d.mean()
    return {"mean_route_common_change":float(d.mean()),
            "site_specific_change_range":float(d.max()-d.min()),
            "site_specific_rms":float(np.sqrt(np.mean(centred**2))),
            "rank_support_ge5pp":bool(d.max()-d.min()>=.05)}

def self_test():
    rng=np.random.default_rng(SIMULATION_SEED)
    maximum_alias=0.
    maximum_weather=0.
    for _ in range(333):
        w=rng.uniform(0,1,10)
        o=rng.uniform(0,.5,10)
        u=rng.normal(0,.35,10)
        a,b=aliased_parameterizations(w,o,u)
        for k in (2,3,5):
            p=probabilities(a,k)
            maximum_alias=max(maximum_alias,float(np.max(np.abs(p-probabilities(b,k)))))
            maximum_weather=max(maximum_weather,float(np.max(np.abs(p-probabilities(a+3.7,k)))))
    if maximum_alias>1e-12 or maximum_weather>1e-12:
        raise RuntimeError("nonidentifiability numerical verification failed")
    return {"source":"known-truth synthetic, not frog observations",
            "n_routes":333,"k":[2,3,5],
            "max_site_effect_parameter_alias_difference":maximum_alias,
            "max_routewide_weather_offset_difference":maximum_weather}

if __name__=="__main__":
    import json
    print(json.dumps(self_test(),indent=2))
