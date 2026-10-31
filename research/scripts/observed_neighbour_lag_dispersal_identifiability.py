"""Source-verified NAAMP time-lag near-neighbour spatial pattern and recoverability pilot.

Uses ORIGINAL 4248 site / 63180 eligible acoustic observations (full NAAMP
site-year panel). No new field observations and NO inferred frog immigration.
Compares annual near/far history associations after absorbing site and
route×year effects; simulates habitat-spatial-correlated no-dispersal vs
lagged-neighbour coupling using precisely the empirical observation mask.

A discriminating acoustic time-lag alone is not a larval dispersal estimate.
This pilot is not an 80y common-source ABC posterior.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
import numpy as np
import pandas as pd

SEED=20261031
REPS=32
BOOT=399
MIN_PAIRS=300
FAR_MIN_SITES=3

def haversine_km(lat,lon):
    lat=np.radians(np.asarray(lat,float))
    lon=np.radians(np.asarray(lon,float))
    lat1=lat[:,None]; lat2=lat[None,:]
    dlat=lat2-lat1
    dlon=lon[None,:]-lon[:,None]
    a=np.sin(dlat/2)**2+np.cos(lat1)*np.cos(lat2)*np.sin(dlon/2)**2
    return 6371.0088*2*np.arctan2(np.sqrt(np.maximum(a,0)),
                                   np.sqrt(np.maximum(1-a,0)))

def neighbour_geometry(sites):
    """Nearest and farthest OTHER documented route stops, not synthetic pond edges."""
    required={"site","route","lat","lon"}
    if not required.issubset(sites):raise ValueError("Site identity/geometry absent")
    if sites.site.duplicated().any():raise ValueError("Duplicate observed physical site")
    vals=[]
    for route,g in sites.groupby("route",sort=True):
        if len(g)<FAR_MIN_SITES:continue
        x=g.reset_index(drop=True)
        D=haversine_km(x.lat.to_numpy(),x.lon.to_numpy())
        np.fill_diagonal(D,np.inf)
        nearest=np.argmin(D,axis=1)
        D2=D.copy();np.fill_diagonal(D2,-np.inf)
        farthest=np.argmax(D2,axis=1)
        for i in range(len(x)):
            vals.append((x.site.iat[i],route,x.site.iat[nearest[i]],
                         x.site.iat[farthest[i]],D[i,nearest[i]],
                         D2[i,farthest[i]],len(x)))
    out=pd.DataFrame(vals,columns=["site","route","nearest_site",
                  "farthest_site","nearest_km","farthest_km","sites_in_route"])
    if out.empty or out.site.duplicated().any():
        raise AssertionError("Route geometry yielded missing/duplicated site edges")
    if out.nearest_site.eq(out.site).any() or out.farthest_site.eq(out.site).any():
        raise AssertionError("A station was made its own neighbour")
    return out

def annual_panel(sites,visits,expect_sites=None,expect_visits=None):
    """Use source completed surveys only, exact prior CALENDAR year, no future leakage."""
    d=sites.copy()
    if expect_sites is not None and len(d)!=expect_sites:
        raise AssertionError("Source NAAMP site denominator changed")
    v=visits.loc[visits.site.isin(d.site)&visits.timeout.eq(0)].copy()
    if expect_visits is not None and len(v)!=expect_visits:
        raise AssertionError("Original NAAMP completed survey denominator changed")
    if v.duplicated(["site","run"]).any() or not v.strong.isin([0,1]).all():
        raise AssertionError("Source site/run duplicate or wrong calling event definition")
    for field in ("air","noise","doy"):
        if field not in v:raise ValueError("Original NAAMP effort/season field absent "+field)
    annual=(v.groupby(["site","year"],sort=True)
            .agg(rate=("strong","mean"),count=("strong","size"),
                 air=("air","mean"),noise=("noise","mean"),doy=("doy","mean"))
            .reset_index())
    annual["row_idx"]=np.arange(len(annual))
    geom=neighbour_geometry(d[["site","route","lat","lon"]])
    base=annual.merge(geom,on="site",how="inner",validate="many_to_one")
    # Full own previous calendar year plus two spatially distinct stations'
    # previously observed calling, strictly prior to current-site outcome.
    refs=[("site","own_prev","own_row_idx"),
          ("nearest_site","near_prev","near_row_idx"),
          ("farthest_site","far_prev","far_row_idx")]
    for key,ycol,idxcol in refs:
        prior=annual[["site","year","rate","row_idx"]].copy()
        prior["year"]+=1
        prior=prior.rename(columns={"site":key,"rate":ycol,"row_idx":idxcol})
        base=base.merge(prior,on=[key,"year"],how="left",validate="many_to_one")
    base=base.dropna(subset=["own_prev","near_prev","far_prev",
                             "air","noise","doy"]).copy()
    if base.empty:raise AssertionError("No previous-calendar-year neighbour observations")
    base["route_year"]=base.route.astype(str)+"|"+base.year.astype(str)
    # Iteratively remove site singletons and route×year groups without
    # within-group contrasts; these provide no fixed-effect information.
    for _ in range(6):
        old=len(base)
        group=base.groupby("route_year").site.transform("size")
        base=base[group>=3]
        group=base.groupby("site").year.transform("size")
        base=base[group>=2]
        if len(base)==old:break
    if len(base)<MIN_PAIRS or base.route.nunique()<20:
        raise AssertionError(f"Insufficient actual independent temporal-route support: {len(base)}")
    if (base.year<=0).any() or base.own_row_idx.isna().any():
        raise AssertionError("Incomplete source panel chronology")
    prior_ids=annual[["site","year"]].copy().set_index(["site","year"])
    for sitefield in ("site","nearest_site","farthest_site"):
        if not all((x,int(y)-1) in prior_ids.index
                   for x,y in zip(base[sitefield],base.year)):
            raise AssertionError("A future year or non-existent site was used as prior")
    # Avoid artificially repeating annual samples as independent site-years.
    if base.duplicated(["site","year"]).any():
        raise AssertionError("Duplicate eligible annual acoustic response")
    return annual,base.reset_index(drop=True),geom

def demean_matrix(z,groups,weights,iterations=120,tol=1e-10):
    """Weighted alternating projection onto site and route-year fixed effects."""
    x=np.asarray(z,dtype=float).copy()
    if x.ndim==1:x=x[:,None]
    w=np.asarray(weights,float)
    if len(x)!=len(w) or not (w>0).all():
        raise ValueError("Invalid fixed-effect weighted observations")
    for it in range(iterations):
        prior=x.copy() if it>0 else None
        for g in groups:
            codes=np.asarray(g,int)
            den=np.bincount(codes,weights=w)
            for col in range(x.shape[1]):
                num=np.bincount(codes,weights=x[:,col]*w,minlength=len(den))
                x[:,col]-=np.divide(num,den,out=np.zeros_like(num),
                                   where=den>0)[codes]
        if prior is not None and np.max(np.abs(x-prior))<tol:
            break
    return x

def fixed_effect_association(panel,values=None,n_boot=0,seed=SEED):
    """Route-year and physical-site adjusted partial near/far lag effects."""
    if values is None:
        yy=panel.rate.to_numpy(float)
        own=panel.own_prev.to_numpy(float)
        near=panel.near_prev.to_numpy(float)
        far=panel.far_prev.to_numpy(float)
    else:
        a=np.asarray(values,float)
        yy=a[panel.row_idx.to_numpy(int)]
        own=a[panel.own_row_idx.to_numpy(int)]
        near=a[panel.near_row_idx.to_numpy(int)]
        far=a[panel.far_row_idx.to_numpy(int)]
    # Mean air, noise, day of year measured in same site/year can
    # adjust observation conditions, but not a biological detection process.
    z=np.column_stack([yy,own,near,far,
                       panel.air.to_numpy(float),panel.noise.to_numpy(float),
                       panel.doy.to_numpy(float)])
    if not np.isfinite(z).all():raise AssertionError("Missing completed annual source values")
    groups=[pd.factorize(panel.site,sort=True)[0],
            pd.factorize(panel.route_year,sort=True)[0]]
    w=np.asarray(panel["count"],float)
    z=demean_matrix(z,groups,w)
    X=z[:,1:]
    y=z[:,0]
    if np.linalg.matrix_rank(X)<X.shape[1]:
        raise AssertionError("Local lag design is not identifiable after fixed effects")
    Xw=X*np.sqrt(w[:,None])
    yw=y*np.sqrt(w)
    beta=np.linalg.lstsq(Xw,yw,rcond=1e-10)[0]
    outputs=dict(beta_own_prior=float(beta[0]),
          beta_nearest_prior=float(beta[1]),
          beta_farthest_prior=float(beta[2]),
          nearest_minus_farthest=float(beta[1]-beta[2]),
          beta_air=float(beta[3]),beta_noise=float(beta[4]),beta_doy=float(beta[5]),
          n_site_years=len(panel),n_sites=int(panel.site.nunique()),
          n_routes=int(panel.route.nunique()),
          n_route_years=int(panel.route_year.nunique()),
          year_first=int(panel.year.min()),year_last=int(panel.year.max()),
          fixed_effect_convergence="site_and_route_year_weighted_projection",
          weighted_residual_sd=float(np.sqrt(np.average((y-X@beta)**2,weights=w))))
    if n_boot:
        # Conditional on original FE residuals; SEs are route-cluster
        # resampling of score moments, NOT a full FE-refit bootstrap.
        r=pd.factorize(panel.route,sort=True)[0]
        groups_count=int(r.max()+1)
        xx=np.zeros((groups_count,X.shape[1],X.shape[1]))
        xy=np.zeros((groups_count,X.shape[1]))
        np.add.at(xx,r,w[:,None,None]*X[:,:,None]*X[:,None,:])
        np.add.at(xy,r,w[:,None]*X*y[:,None])
        rng=np.random.default_rng(seed)
        draws=[]
        for _ in range(n_boot):
            counts=rng.multinomial(groups_count,np.full(groups_count,1/groups_count))
            mat=np.einsum("g,gij->ij",counts,xx)
            if np.linalg.matrix_rank(mat)<X.shape[1]:continue
            coeff=np.linalg.solve(mat,counts@xy)
            draws.append(coeff)
        a=np.asarray(draws)
        if len(a)<.95*n_boot:
            raise AssertionError("Insufficient route cluster bootstrap support")
        for index,label in ((1,"nearest_prior"),(2,"farthest_prior")):
            outputs[label+"_mc_low"]=float(np.quantile(a[:,index],.025))
            outputs[label+"_mc_high"]=float(np.quantile(a[:,index],.975))
        diff=a[:,1]-a[:,2]
        outputs["nearest_minus_farthest_mc_low"]=float(np.quantile(diff,.025))
        outputs["nearest_minus_farthest_mc_high"]=float(np.quantile(diff,.975))
        outputs["n_conditional_route_bootstraps"]=len(a)
    return outputs

def simulate_source_panel(annual,geometry,seed,neighbour_coupling):
    """Explicit synthetic shared route-year climate *or* same + neighbour lag."""
    if neighbour_coupling not in (0.,.65):
        raise ValueError("Only prior-fixed environmental-null or dispersal-like coupling")
    s=geometry.drop_duplicates("site").reset_index(drop=True)
    n=len(s)
    ids={item:j for j,item in enumerate(s.site)}
    near=np.array([ids[q] for q in s.nearest_site],int)
    far=np.array([ids[q] for q in s.farthest_site],int)
    route=pd.factorize(s.route,sort=True)[0]
    n_routes=route.max()+1
    rng=np.random.default_rng(seed)
    base=rng.normal(size=n)
    # Static spatially smooth unobserved site habitat exists in BOTH arms.
    static=.6*base+.4*(base[near]+base[far])/2
    zprev=rng.normal(size=n)
    routeprev=np.zeros(n_routes)
    unique_year=np.sort(annual.year.unique())
    if not set(annual.site).issubset(ids):
        # Geometry excludes tiny routes (<3); those source site-years get
        # an independent valid synthetic response but never enter POM.
        missing=np.array([item not in ids for item in annual.site])
    else:missing=np.zeros(len(annual),dtype=bool)
    values=np.zeros(len(annual),float)
    annual_pos=np.array([ids.get(item,-1) for item in annual.site],int)
    ny=annual.year.to_numpy(int)
    for year in range(int(unique_year.min()),int(unique_year.max())+1):
        routeprev=.67*routeprev+rng.normal(scale=.66,size=n_routes)
        shock=rng.normal(scale=.60,size=n)
        # Model 0: all spatial structure from shared route climate and
        # stable local habitat; model 1 additionally has true neighbour lag.
        z=(.50*zprev + neighbour_coupling*zprev[near]
           +.50*static+.60*routeprev[route]+shock)
        idx=np.flatnonzero((ny==year)&~missing)
        if len(idx):
            p=1/(1+np.exp(-np.clip(-.6+.6*z[annual_pos[idx]],-30,30)))
            visits=annual["count"].to_numpy(int)[idx]
            values[idx]=rng.binomial(visits,p)/visits
        zprev=z
    return values

def auc_score(negative,positive):
    a=np.asarray(negative,float);b=np.asarray(positive,float)
    return float(np.mean(b[:,None]>a[None,:])+
                 .5*np.mean(b[:,None]==a[None,:]))

def run(source_root,out,reps=REPS,bootstrap=BOOT):
    sys.path.insert(0,str(source_root/"research/scripts"))
    from select_macro_trophic_scenarios import load_cohort, SITE, VISITS
    # The imported 2026-10-31 PR146 source owns its exact ROOT and inputs.
    if not SITE.is_file() or not VISITS.is_file():
        raise AssertionError("Original 4248-site and 63180-visit NAAMP source absent")
    sites=pd.read_csv(SITE)
    visits=pd.read_csv(VISITS)
    d=load_cohort(sites,visits,expected=4248)
    if int(d.n.sum())!=63180:raise AssertionError("Original source empirical denominator changed")
    annual,panel,geometry=annual_panel(d,visits,expect_sites=4248,expect_visits=63180)
    obs=fixed_effect_association(panel,n_boot=bootstrap,seed=SEED)
    source_geom=dict(near_median_km=float(geometry.nearest_km.median()),
       near_p95_km=float(geometry.nearest_km.quantile(.95)),
       near_zero_km_pairs=int((geometry.nearest_km==0).sum()),
       far_median_km=float(geometry.farthest_km.median()),
       n_geometry_sites=len(geometry),n_annual_source_rows=len(annual))
    draws=[]
    for i in range(reps):
        for label,coupling in (("SHARED_ENVIRONMENT_NO_MIGRATION",0.),
                              ("SPATIAL_NEIGHBOUR_LAG",.65)):
            vals=simulate_source_panel(
                annual,geometry,seed=SEED+i,neighbour_coupling=coupling)
            a=fixed_effect_association(panel,values=vals,n_boot=0)
            draws.append(dict(model=label,replicate=i,synthetic_coupling=coupling,
                beta_nearest_prior=a["beta_nearest_prior"],
                beta_farthest_prior=a["beta_farthest_prior"],
                nearest_minus_farthest=a["nearest_minus_farthest"]))
        if i%8==0:print("RECOVERY_MODEL_RUN",i,flush=True)
    sim=pd.DataFrame(draws)
    env=sim[sim.model.eq("SHARED_ENVIRONMENT_NO_MIGRATION")].sort_values("replicate")
    spread=sim[sim.model.eq("SPATIAL_NEIGHBOUR_LAG")].sort_values("replicate")
    score="nearest_minus_farthest"
    A=auc_score(env[score],spread[score])
    # Two separate replicate groups; no observations used to tune threshold.
    n_train=max(4,int(reps*.75))
    threshold=float(.5*(env[score].iloc[:n_train].mean()+
                          spread[score].iloc[:n_train].mean()))
    sign=1 if spread[score].iloc[:n_train].mean()>=env[score].iloc[:n_train].mean() else -1
    test_env=env[score].iloc[n_train:]
    test_disp=spread[score].iloc[n_train:]
    balanced=.5*(float(np.mean(sign*test_env<sign*threshold))+
                 float(np.mean(sign*test_disp>sign*threshold)))
    observed_score=obs[score]
    out.mkdir(parents=True,exist_ok=True)
    pd.DataFrame([obs]).to_csv(out/"observed_annual_neighbour_lag.csv",index=False)
    sim.to_csv(out/"synthetic_environment_vs_neighbour_coupling_recovery.csv",index=False)
    receipt=dict(
       status="REAL_NAAMP_ANNUAL_NEIGHBOUR_LAG_AND_SYNTHETIC_RECOVERY_COMPLETED",
       actual_source_sites=4248,actual_source_visits=63180,
       source_annual_rows=len(annual),eligible_site_year_rows=len(panel),
       eligible_sites=obs["n_sites"],eligible_routes=obs["n_routes"],
       n_route_years=obs["n_route_years"],years=[obs["year_first"],obs["year_last"]],
       route_cluster_conditional_bootstrap=bootstrap,
       source_geometry=source_geom,
       observed_temporal_coefficient=obs,
       synthetic_comparison=dict(n_per_model=reps,
            environmental_null_shared_route_year_shocks=True,
            environmental_null_spatial_site_bias=True,
            neighbour_coupling_beta_0=.0,neighbour_coupling_beta_1=.65,
            auc_nearest_minus_far=A,
            heldout_balanced_accuracy=balanced,
            threshold_fitted_only_on_synthetic_train=threshold,
            not_calibrated_to_natural_larval_dispersal=True),
       interpretation="Historical near-neighbour acoustic association; not measured animal movement",
       statistical_caveats=[
         "Site and route×year fixed effects absorb stable site and common route-season heterogeneity, not all changing site environments",
         "Prior year acoustic status is not a frog juvenile cohort or migrant record",
         "Source listening stops can sample overlapping wetlands",
         "Route-cluster intervals condition on original nuisance and FE projections",
         "Synthetic environment/null and neighbour-lag alternatives are illustrative assumptions; classification is NOT ecological mechanism posterior"
       ],
       data_source_SHA256={
           "original_sites":hashlib.sha256(SITE.read_bytes()).hexdigest(),
           "original_visits":hashlib.sha256(VISITS.read_bytes()).hexdigest()
       },
       script_SHA256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    )
    (out/"receipt.json").write_text(json.dumps(receipt,indent=2,ensure_ascii=False)+"\n")
    print("NAAMP_TIME_LAG_SPATIAL_PATTERN",json.dumps({
       "n_site_year_rows":len(panel),"n_routes":obs["n_routes"],
       "near_beta":obs["beta_nearest_prior"],
       "far_beta":obs["beta_farthest_prior"],
       "near_minus_far":obs["nearest_minus_farthest"],
       "near_far_95mc":[obs["nearest_minus_farthest_mc_low"],
                         obs["nearest_minus_farthest_mc_high"]],
       "recovery_auc":A,"heldout_balanced_accuracy":balanced
    }),flush=True)
    return receipt

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--source-root",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    p.add_argument("--reps",type=int,default=REPS)
    p.add_argument("--boot",type=int,default=BOOT)
    a=p.parse_args()
    if a.reps<8 or a.boot<99: p.error("Need sufficient independent simulated replications and source route draws")
    run(a.source_root.resolve(),a.out,reps=a.reps,bootstrap=a.boot)
