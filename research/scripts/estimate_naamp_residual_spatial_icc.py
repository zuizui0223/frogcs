"""NAAMP spatial-block covariance of residuals from the fixed eight-term rank OLS.

This is NOT a measurement-error ICC or acoustic-detection parameter: genuine
unmeasured environmental spatial structure and sampling-route dependence also
contribute.  Bootstrap refits neither OLS nor model signs, and treats each
resampled spatial block as a distinct pseudo-cluster.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

from select_macro_trophic_scenarios import ROOT, SITE, VISITS, load_cohort
from pattern_oriented_abc_pilot import BACKGROUNDS, get_design, rankz
from r2_calibrated_directional_pom import orthogonal_regression, rankrows, site_rank_r2

OUT = ROOT/"research/results/macro_observed_residual_icc_20261031"
BOOT = 999
SEED = 20261031
PREVIOUS_BLOCK_ALPHA = .25
NEAR_ONE_CUTOFF = 1-1e-10


def grouped_sufficient(residual,groups):
    v=np.asarray(residual,float)
    group=np.asarray(groups)
    if v.ndim!=1 or len(v)!=len(group) or len(v)<8 or not np.isfinite(v).all():
        raise ValueError("Residual/group shape or finite check failed")
    ids,categories=pd.factorize(group,sort=True)
    counts=np.bincount(ids).astype(float)
    if len(counts)<3 or np.sum(counts)>0 and np.sum(counts)==len(counts):
        raise ValueError("Need >=3 groups and within-group replicate support")
    total=np.bincount(ids,weights=v)
    ss=np.bincount(ids,weights=v*v)
    means=total/counts
    within=np.maximum(0.,ss-counts*means*means)
    return pd.DataFrame(dict(group=np.asarray(categories).astype(str),
                             n=counts.astype(int),mean=means,withinSS=within))


def unequal_icc(stats):
    s=stats
    n=np.asarray(s["n"],float)
    m=np.asarray(s["mean"],float)
    within=np.asarray(s["withinSS"],float)
    if len(n)<3 or any(n<1) or any(within<0) or not np.isfinite(m).all():
        raise ValueError("Bad group sufficient statistics")
    N=n.sum()
    B=len(n)
    effective=(N-(n*n).sum()/N)/(B-1)
    if effective<=1e-12 or N<=B:
        raise ValueError("No estimable unequal-size cluster variance")
    grand=np.dot(n,m)/N
    ssb=float(np.dot(n,(m-grand)**2))
    ssw=float(within.sum())
    msb=ssb/(B-1)
    msw=ssw/(N-B)
    tau_raw=(msb-msw)/effective
    tau=max(0.,tau_raw)
    denominator=tau+msw
    if denominator<=0:
        raise ValueError("No variance, ICC undefined")
    icc=tau/denominator
    if not 0<=icc<NEAR_ONE_CUTOFF:
        raise ValueError("Rank-residual block ICC too close to one")
    alpha=np.sqrt(icc/(1-icc)) if icc>0 else 0.
    return dict(n_sites=int(N),n_groups=B,grand_mean=float(grand),
                effective_group_size=float(effective),ms_between=float(msb),
                ms_within=float(msw),tau2_raw=float(tau_raw),
                tau2_truncated=float(tau),within_variance=float(msw),
                icc=float(icc),alpha_block_to_site=float(alpha))


def icc_conditional_bootstrap(stats,n_boot=BOOT,seed=SEED):
    if n_boot<1:raise ValueError("Require at least one resampling")
    rng=np.random.default_rng(seed)
    s=stats.reset_index(drop=True)
    draws=[]
    for _ in range(n_boot):
        ids=rng.integers(0,len(s),size=len(s))
        # Duplicate sampled groups are DISTINCT pseudo-clusters, not merged.
        sub=s.iloc[ids]
        d=unequal_icc(sub)
        draws.append((d["icc"],d["alpha_block_to_site"],d["tau2_raw"]))
    x=pd.DataFrame(draws,columns=["icc","alpha_block_to_site","tau2_raw"])
    if not np.isfinite(x.to_numpy(float)).all():
        raise AssertionError("Invalid clustered ICC bootstrap")
    return x


def observed_residual_cohort(d,background,n_boot=BOOT):
    design=get_design(d,background)
    q,pinv=orthogonal_regression(design)
    y=rankrows(d.strong_rate.to_numpy(float)[None,:])[0]
    r2=float(site_rank_r2(y[None,:],q)[0])
    coefficients=pinv@y
    residual=y-design["x"]@coefficients
    if not np.allclose(design["x"].T@residual,np.zeros(8),rtol=0,atol=1e-8):
        raise AssertionError("Original rank-OLS residual not orthogonal")
    expected={"uniform":.0469943882980746,
              "target_group":.051772116477594}
    if not np.isclose(r2,expected[background],rtol=0,atol=1e-9):
        raise AssertionError("Archived original observed eight-term R² not reproduced")
    spatial=grouped_sufficient(residual,d.spatial_block)
    route=grouped_sufficient(residual,d.route)
    spatial_est=unequal_icc(spatial)
    route_est=unequal_icc(route)
    draws=icc_conditional_bootstrap(spatial,n_boot=n_boot,seed=SEED)
    lo,hi=np.quantile(draws.icc,[.025,.975])
    alo,ahi=np.quantile(draws.alpha_block_to_site,[.025,.975])
    metadata=dict(background=background,
                  sites=len(d),completed_surveys=int(d.n.sum()),
                  n_routes=len(route),n_spatial_blocks=len(spatial),
                  min_sites_per_block=int(spatial.n.min()),
                  median_sites_per_block=float(spatial.n.median()),
                  max_sites_per_block=int(spatial.n.max()),
                  observed_8term_rank_r2=r2,
                  residual_rank_variance=float(np.mean(residual*residual)),
                  **{k:v for k,v in spatial_est.items()
                     if k not in ("n_sites","n_groups")},
                  spatial_icc_ci_low=float(lo),spatial_icc_ci_high=float(hi),
                  spatial_alpha_ci_low=float(alo),spatial_alpha_ci_high=float(ahi),
                  n_bootstrap=int(len(draws)),
                  bootstrap_negative_tau_fraction=float((draws.tau2_raw<=0).mean()),
                  route_icc=float(route_est["icc"]),
                  route_alpha=float(route_est["alpha_block_to_site"]),
                  old_hypothetical_alpha=PREVIOUS_BLOCK_ALPHA,
                  old_hypothetical_icc=PREVIOUS_BLOCK_ALPHA**2/
                  (1+PREVIOUS_BLOCK_ALPHA**2))
    return metadata,spatial,draws


def empirical_block_noise(d,n,seed,icc):
    """Add common Gaussian block process using the same unit noise convention."""
    if not 0<=icc<NEAR_ONE_CUTOFF:
        raise ValueError("Invalid empirical rank-residual ICC")
    if n<1:raise ValueError("Zero noise draws")
    blocks,_=pd.factorize(d.spatial_block,sort=True)
    rng=np.random.default_rng(seed)
    site=rng.normal(size=(n,len(d)))
    if icc>0:
        a=np.sqrt(icc/(1-icc))
        block=rng.normal(size=(n,int(blocks.max()+1)))
        site+=a*block[:,blocks]
    site-=site.mean(axis=1,keepdims=True)
    sd=site.std(axis=1,keepdims=True)
    if np.any(sd<=0):raise ValueError("Bad Gaussian noise")
    return site/sd


def run():
    OUT.mkdir(parents=True,exist_ok=True)
    d=load_cohort(pd.read_csv(SITE),pd.read_csv(VISITS),expected=4248)
    if int(d.n.sum())!=63180 or int(d.V.sum())!=506:
        raise AssertionError("Field source ledger size changed")
    rows=[];draws=[]
    for bg in BACKGROUNDS:
        result,spatial,boot=observed_residual_cohort(d,bg)
        rows.append(result)
        boot["background"]=bg
        draws.append(boot)
        print("NAAMP_RESIDUAL_SPATIAL_ICC",bg,json.dumps(result),flush=True)
    summary=pd.DataFrame(rows)
    summary.to_csv(OUT/"observed_residual_spatial_icc.csv",index=False)
    pd.concat(draws,ignore_index=True).to_csv(
        OUT/"conditional_block_bootstrap_icc.csv",index=False)
    record=dict(status="CONDITIONAL_RESIDUAL_SPATIAL_ICC_NOT_DETECTION_NOISE_CALIBRATION",
                sample_sites=4248,survey_visits=63180,
                spatial_definition="Route-centroid floored to 2-degree grid; same as original frogcs nested CV",
                estimator="Unequal-group-size one-way random-intercept ANOVA method of moments",
                bootstrap="999 whole 2-degree spatial block sufficient-statistic resamples, no regression refit",
                caveats=["Remaining residual ICC includes real unmodeled environmental spatial structure",
                         "Not an acoustic instrument error measurement",
                         "Not a model of aquatic F_B to calling adult male or NAAMP detection",
                         "R2 and ICC estimated from same previously explored NAAMP outcome",
                         "Block Gaussian assumption is hypothetical even if ICC is data-derived"],
                source_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
                               for p in [SITE,VISITS]},
                script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    (OUT/"receipt.json").write_text(json.dumps(record,indent=2,ensure_ascii=False)+"\n")
    return summary


if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--run",action="store_true")
    args=p.parse_args()
    if not args.run:p.error("Explicit --run required")
    run()
