"""Pattern-oriented frogcs macro scenario comparison and conditional ABC pilot.

IMPORTANT:
 * 24 source surfaces have FIXED biological predation/growth/recruitment rates.
 * Pseudo-data priors are only arbitrary site-proxy transport and rank noise.
 * ABC "mass" is conditional on those ASSUMPTIONS, NOT a field posterior over
   biological causes. No scene is tuned to raw observed interaction signs.
 * All candidate responses are at the same *real* 4248 NAAMP sites.
 * Adult calling is compared with synthetic aquatic F_B only via ranks:
   a shared strictly monotonic transformation cannot alter rank patterns.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import rankdata
from scipy.linalg import eigh

from select_macro_trophic_scenarios import (
    ROOT, SITE, VISITS, SOURCES, SEED, LEVELS, load_cohort, scenario_surfaces,
)

OUT=ROOT/"research/results/macro_pom_abc_pilot_20261031"
MACRO=ROOT/"research/results/scale_comparison_20261029/macro_common_estimators.csv"
PATTERNS=("OS","OV","SV","OSV","O_with_S_low","O_with_S_high")
HOLDOUT=("O_with_V_zero","O_with_V_positive","within_route_OS","within_route_OV")
BACKGROUNDS=("uniform","target_group")
N_BOOT=999
N_REFERENCE_PER_CASE=64
N_PSEUDO_PER_CASE=12
ACCEPT_FRACTION=.02
NOISE_RANGE=(.2,.8)   # hypothetical rank observation noise; *not field calibrated*
WARP_RANGE=(.8,1.2)   # hypothetical suitability -> source-rank transport
COV_SHRINK=.25
EIGEN_FLOOR=1e-5


def rankz(x):
    r=rankdata(np.asarray(x,float),axis=0)
    std=r.std(axis=0)
    return (r-r.mean(axis=0))/np.maximum(std,1e-12)


def corr(a,b,weights=None):
    a=np.asarray(a,float);b=np.asarray(b,float)
    w=np.ones(len(a)) if weights is None else np.asarray(weights,float)
    tot=w.sum()
    if tot<3:return float("nan")
    aa=np.average(a,weights=w);bb=np.average(b,weights=w)
    va=np.dot(w,(a-aa)**2);vb=np.dot(w,(b-bb)**2)
    if va<=1e-16 or vb<=1e-16:return float("nan")
    return float(np.dot(w,(a-aa)*(b-bb))/np.sqrt(va*vb))


def get_design(d,background):
    o=rankz(d[f"mean_suitability_Odonata_{background}"])
    s=rankz(d[f"mean_suitability_pond_breeding_Caudata_{background}"])
    v=rankz(d.V.to_numpy(float))
    x=np.column_stack([np.ones(len(d)),o,s,v,o*s,o*v,s*v,o*s*v])
    if np.linalg.matrix_rank(x)<8:raise ValueError("Unidentified observational pattern design")
    smid=float(np.median(s))
    masks=dict(S_low=s<=smid,S_high=s>smid,
               V_zero=d.V.to_numpy()==0,V_positive=d.V.to_numpy()==1)
    if any(mask.sum()<10 for mask in masks.values()):
        raise ValueError("Missing predictor group support")
    p=np.linalg.pinv(x,rcond=1e-12)
    # Route-wise demeaning, *held out* from ranking metrics.
    g,_=pd.factorize(d.route,sort=True)
    cnt=np.bincount(g)
    xm=x[:,1:].copy()
    mean=np.zeros((len(cnt),7))
    np.add.at(mean,g,xm)
    xm-=mean[g]/cnt[g,None]
    within=np.linalg.pinv(xm,rcond=1e-12)
    if np.linalg.matrix_rank(xm)<7:
        raise ValueError("Within-route design is not identifiable")
    return dict(x=x,pinv=p,within_pinv=within,route_group=g,
                o=o,s=s,v=v,masks=masks,background=background)


def stats_from_y(y,design,holdout=False):
    y=rankz(y)
    beta=design["pinv"]@y
    output=np.asarray([beta[4],beta[5],beta[6],beta[7],
                       corr(design["o"][design["masks"]["S_low"]],
                            y[design["masks"]["S_low"]]),
                       corr(design["o"][design["masks"]["S_high"]],
                            y[design["masks"]["S_high"]])],float)
    if not np.isfinite(output).all():raise ValueError("Invalid primary pattern")
    if not holdout:return output
    g=design["route_group"]
    cnt=np.bincount(g)
    sums=np.bincount(g,weights=y)
    yr=y-sums[g]/cnt[g]
    within=design["within_pinv"]@yr
    h=np.asarray([corr(design["o"][design["masks"]["V_zero"]],
                       y[design["masks"]["V_zero"]]),
                  corr(design["o"][design["masks"]["V_positive"]],
                       y[design["masks"]["V_positive"]]),
                  within[3],within[4]],float)
    if not np.isfinite(h).all():raise ValueError("Invalid held-out patterns")
    return output,h


def compare_frozen_macro(observed,background,atol=1e-8):
    m=pd.read_csv(MACRO)
    a=m[(m.background==background)&(m.vegetation=="binary")&
        (m.x_transform=="rank")&(m.y_transform=="rank")&
        (m.adjustment=="none")&(m["mode"]=="pooled")].set_index("term")
    for i,name in enumerate(PATTERNS[:4]):
        if name not in a.index or abs(float(a.loc[name,"beta"])-observed[i])>atol:
            raise AssertionError(f"Original macro pattern was not replayed: {background}, {name}")
    return {name:float(a.loc[name,"beta"]) for name in PATTERNS[:4]}


def bootstrap_observed(y,design,groups,n_boot=N_BOOT,seed=SEED):
    """Fixed global ranks; spatial block bootstrap, covariance of six patterns."""
    y=rankz(y)
    x=design["x"];o=design["o"];masks=design["masks"]
    gid,_=pd.factorize(groups,sort=True)
    k=int(gid.max()+1)
    xx=np.zeros((k,8,8));xy=np.zeros((k,8))
    np.add.at(xx,gid,x[:,:,None]*x[:,None,:])
    np.add.at(xy,gid,x*y[:,None])
    moment={}
    for label in ("S_low","S_high"):
        mask=masks[label]
        # weighted Pearson ingredients per original spatial block
        z=np.column_stack([np.ones(mask.sum()),o[mask],y[mask],
                           o[mask]**2,y[mask]**2,o[mask]*y[mask]])
        val=np.zeros((k,6))
        np.add.at(val,gid[mask],z)
        moment[label]=val
    rng=np.random.default_rng(seed)
    weights=rng.multinomial(k,np.repeat(1/k,k),size=n_boot)
    out=[]
    for w in weights:
        A=np.einsum("b,bij->ij",w,xx)
        rhs=w@xy
        try:
            if np.linalg.matrix_rank(A)<8:continue
            beta=np.linalg.solve(A,rhs)
            tail=[]
            for name in ("S_low","S_high"):
                n,sx,sy,sxx,syy,sxy = w@moment[name]
                vx=sxx-sx*sx/n
                vy=syy-sy*sy/n
                if n<=4 or vx<=1e-12 or vy<=1e-12:raise ValueError("Empty bootstrap group")
                tail.append((sxy-sx*sy/n)/np.sqrt(vx*vy))
            out.append([beta[4],beta[5],beta[6],beta[7],*tail])
        except (ValueError,np.linalg.LinAlgError,ZeroDivisionError):
            continue
    draw=np.asarray(out)
    if len(draw)<.9*n_boot or draw.shape[1]!=len(PATTERNS):
        raise ValueError("Insufficient valid block bootstrap replicates")
    cov=np.cov(draw,rowvar=False,ddof=1)
    eigenvalues,eigenvectors=eigh(cov)
    lam=COV_SHRINK
    cov=(1-lam)*cov + lam*np.diag(np.diag(cov))
    ev,q=eigh(cov)
    min_eigen=max(float(ev.max())*EIGEN_FLOOR,1e-10)
    cov=q@np.diag(np.maximum(ev,min_eigen))@q.T
    inv=np.linalg.inv(cov)
    return draw,cov,inv,dict(n_spatial_blocks=k,valid_bootstraps=len(draw),
                             source_covariance_eigmin=float(eigenvalues.min()),
                             covariance_condition=float(np.linalg.cond(cov)))


def site_response(d,background,grid,warps=(1.,1.)):
    """Look up the saved F_B cell using only *predictor* rank mappings."""
    o=d[f"mean_suitability_Odonata_{background}"].to_numpy(float)
    s=d[f"mean_suitability_pond_breeding_Caudata_{background}"].to_numpy(float)
    if grid.shape!=(2,LEVELS,LEVELS):raise ValueError("Source grid wrong size")
    n=len(o)
    def idx(a,exponent):
        u=(rankdata(a)-.5)/len(a)
        return np.rint(u**exponent*(LEVELS-1)).astype(int)
    out=grid[d.V.to_numpy(int),idx(s,warps[1]),idx(o,warps[0])]
    if not np.isfinite(out).all() or (out<=0).any():
        raise ValueError("Invalid aquatic cohort")
    return out


def group_exact_surfaces(surfaces):
    hashes={name:hashlib.sha256(grid.astype("<f8").tobytes()).hexdigest()
            for name,grid in surfaces.items()}
    groups={}
    for case,h in hashes.items():
        groups.setdefault(h,[]).append(case)
    label={}
    for grp,cases in groups.items():
        name=sorted(cases)[0]
        for case in cases:label[case]=name
    if len(label)!=len(surfaces):raise AssertionError("Mechanistic cases missing")
    return label,groups


def multivariate_distance(a,target,inverse_cov):
    delta=np.asarray(a,float)-np.asarray(target,float)
    return np.einsum("...i,ij,...j->...",delta,inverse_cov,delta)


def conditional_abc(reference,observed,inverse_cov,accept_fraction=ACCEPT_FRACTION):
    """Toy rejection ABC under FIXED biological rates + explicit noise priors."""
    if not (0<accept_fraction<=1):raise ValueError("Invalid ABC tolerance")
    cols=list(PATTERNS)
    d2=multivariate_distance(reference[cols].to_numpy(float),observed,inverse_cov)
    n=max(1,int(np.ceil(len(d2)*accept_fraction)))
    ordered=np.argsort(d2,kind="stable")[:n]
    accepted=reference.iloc[ordered].copy()
    accepted["distance_squared"]=d2[ordered]
    # Equal prior for exact-source equivalence classes, *not case counts*.
    total=reference.groupby("equivalence_group").size()
    accepted_counts=accepted.groupby("equivalence_group").size().reindex(
        total.index,fill_value=0)
    mass=(accepted_counts/total).astype(float)
    if mass.sum()<=0:raise AssertionError("No accepted model")
    mass/=mass.sum()
    return mass,accepted,float(np.max(d2[ordered])),float(np.min(d2))


def pseudo_response(d,background,grid,design,rng,noise=None,warps=None):
    """Arbitrary positive rank observation + site/block error, not adult calling."""
    if noise is None:noise=float(rng.uniform(*NOISE_RANGE))
    if warps is None:warps=(float(rng.uniform(*WARP_RANGE)),
                           float(rng.uniform(*WARP_RANGE)))
    signal=rankz(np.log(site_response(d,background,grid,warps)))
    block,_=pd.factorize(d.spatial_block,sort=True)
    site_noise=rng.normal(size=len(d))
    block_noise=rng.normal(size=int(block.max()+1))
    y=signal+noise*(site_noise+.25*block_noise[block])
    return stats_from_y(y,design),dict(noise=float(noise),
                                       warp_o=float(warps[0]),warp_s=float(warps[1]))


def prior_reference(d,background,design,surfaces,equivalence,seed=SEED,
                    per_case=N_REFERENCE_PER_CASE):
    rng=np.random.default_rng(seed)
    rows=[]
    for case,grid in sorted(surfaces.items()):
        for draw in range(per_case):
            summary,params=pseudo_response(d,background,grid,design,rng)
            rows.append(dict(case=case,equivalence_group=equivalence[case],
                             replicate=draw,**params,**dict(zip(PATTERNS,summary))))
    x=pd.DataFrame(rows)
    if len(x)!=per_case*len(surfaces):raise AssertionError("ABC library count error")
    return x


def recovery_matrix(d,background,design,surfaces,equivalence,reference,inverse_cov,
                    seed=SEED,n=N_PSEUDO_PER_CASE):
    """Independent pseudo targets, report GROUP not unidentifiable case identity."""
    rng=np.random.default_rng(seed+1729)
    rows=[]
    for case,grid in sorted(surfaces.items()):
        for repeat in range(n):
            vec,params=pseudo_response(d,background,grid,design,rng)
            posterior,_,eps,min_dist=conditional_abc(reference,vec,inverse_cov)
            winner=str(posterior.sort_values(ascending=False,kind="stable").index[0])
            rows.append(dict(case=case,true_group=equivalence[case],
                             predicted_group=winner,replicate=repeat,
                             recovered=winner==equivalence[case],
                             max_group_mass=float(posterior.max()),
                             min_distance_sq=min_dist,**params))
    return pd.DataFrame(rows)


def pattern_assessment(d,background,design,surfaces,observed,holdobs,inv,observed_draw):
    rows=[]
    obs_ci=np.quantile(observed_draw,[.025,.975],axis=0)
    pattern_sds=observed_draw.std(axis=0,ddof=1)
    for case,grid in sorted(surfaces.items()):
        point,hold=stats_from_y(site_response(d,background,grid),design,holdout=True)
        distance=float(np.sqrt(multivariate_distance(point,observed,inv)))
        passed=(point>=obs_ci[0])&(point<=obs_ci[1])
        row=dict(background=background,case=case,distance_mahalanobis=distance,
                 fitted_patterns_within_marginal_95=int(passed.sum()),
                 fitted_pattern_count=len(PATTERNS))
        for i,name in enumerate(PATTERNS):
            row["model_"+name]=float(point[i]);row["obs_"+name]=float(observed[i])
            row["z_gap_"+name]=float((point[i]-observed[i])/pattern_sds[i])
            row["within_95_"+name]=bool(passed[i])
        for i,name in enumerate(HOLDOUT):
            row["model_holdout_"+name]=float(hold[i])
            row["obs_holdout_"+name]=float(holdobs[i])
        rows.append(row)
    return pd.DataFrame(rows)


def run(n_reference=N_REFERENCE_PER_CASE,n_pseudo=N_PSEUDO_PER_CASE):
    if n_reference<5 or n_pseudo<2:raise ValueError("Insufficient sampling")
    OUT.mkdir(parents=True,exist_ok=True)
    d=load_cohort(pd.read_csv(SITE),pd.read_csv(VISITS),expected=4248)
    if d.n.sum()!=63180 or int(d.V.sum())!=506:raise AssertionError("Source cohort changed")
    surfaces,metadata=scenario_surfaces([pd.read_csv(p) for p in SOURCES])
    eq,groups=group_exact_surfaces(surfaces)
    group_rows=[dict(group=sorted(cases)[0],n_cases=len(cases),
                     cases=";".join(sorted(cases)),surface_sha256=hashid)
                for hashid,cases in groups.items()]
    pd.DataFrame(group_rows).to_csv(OUT/"exact_surface_equivalence.csv",index=False)
    obs=d.strong_rate.to_numpy(float)
    result=[];posteriors=[];libraries=[];recoveries=[];bootall=[];holdouts=[]
    for bg in BACKGROUNDS:
        design=get_design(d,bg)
        o,h=stats_from_y(obs,design,holdout=True)
        compare_frozen_macro(o,bg)
        boot,cov,inv,diagnostics=bootstrap_observed(obs,design,d.spatial_block,
                                                     n_boot=N_BOOT,seed=SEED)
        measured=pattern_assessment(d,bg,design,surfaces,o,h,inv,boot)
        for row in measured.to_dict("records"):
            row["equivalence_group"]=eq[row["case"]]
            result.append(row)
        library=prior_reference(d,bg,design,surfaces,eq,seed=SEED+{'uniform':0,'target_group':10_000}[bg],
                                per_case=n_reference)
        mass,accepted,epsilon,min_d=conditional_abc(library,o,inv)
        for group,p in mass.items():
            posteriors.append(dict(background=bg,equivalence_group=group,
                                  toy_abc_mass=float(p),total_prior_cases=int(sum(eq[c]==group for c in eq)),
                                  n_accepted=int((accepted.equivalence_group==group).sum()),
                                  accepted_top_fraction=ACCEPT_FRACTION,
                                  accepted_max_d2=epsilon,minimum_d2=min_d,
                                  status="TOY_CONDITIONAL_NOT_BIOLOGICAL_POSTERIOR"))
        recovery=recovery_matrix(d,bg,design,surfaces,eq,library,inv,
                                 seed=SEED+{'uniform':0,'target_group':10_000}[bg],
                                 n=n_pseudo)
        recovery["background"]=bg
        recoveries.append(recovery)
        library["background"]=bg
        libraries.append(library)
        boot_df=pd.DataFrame(boot,columns=PATTERNS);boot_df["background"]=bg
        bootall.append(boot_df)
        for name,value in zip(HOLDOUT,h):
            holdouts.append(dict(background=bg,pattern=name,observed=value,
                                 status="NOT_USED_FOR_PATTERN_SELECTION"))
        print("PATTERN",bg,"cases",len(measured),"groups",len(groups),
              "best",measured.loc[measured.distance_mahalanobis.idxmin(),"case"],
              "best_mahal",float(measured.distance_mahalanobis.min()),
              "recovery",float(recovery.recovered.mean()),
              "abc_mass_top",str(mass.idxmax()),float(mass.max()),
              flush=True)
    results=dict(scenario_pattern_distance=pd.DataFrame(result),
                 toy_conditional_abc_mass=pd.DataFrame(posteriors),
                 pseudo_recovery_records=pd.concat(recoveries,ignore_index=True),
                 observed_pattern_bootstrap=pd.concat(bootall,ignore_index=True),
                 heldout_observed_patterns=pd.DataFrame(holdouts),
                 exact_surface_equivalence=pd.DataFrame(group_rows))
    for name,frame in results.items():
        frame.to_csv(OUT/(name+".csv"),index=False)
    # All ABC simulations are synthetic. Keep a small reference table and full
    # source hashes; avoid presenting it as biologically calibrated evidence.
    ref=pd.concat(libraries,ignore_index=True)
    ref.to_csv(OUT/"synthetic_abc_reference.csv.gz",index=False,
               compression={"method":"gzip","mtime":0})
    inputfiles=[SITE,VISITS,MACRO,*SOURCES]
    receipt=dict(status="POM_FIXED_PARAMETER_AND_CONDITIONAL_TOY_ABC_NOT_BIOLOGICAL_POSTERIOR",
                 n_sites=len(d),n_surveys=int(d.n.sum()),n_vegetated_sites=int(d.V.sum()),
                 candidate_cases=len(surfaces),source_equivalence_groups=len(groups),
                 pattern_dimensions=list(PATTERNS),heldout_dimensions=list(HOLDOUT),
                 reference_per_case=n_reference,pseudo_per_case=n_pseudo,
                 n_boot=N_BOOT,noise_prior=list(NOISE_RANGE),
                 proxy_warp_prior=list(WARP_RANGE),accept_fraction=ACCEPT_FRACTION,
                 spatial_block_bootstrap=True,rank_monotone_response="rank aquatic F_B vs rank observed strong-call fraction",
                 current_model_rates_held_fixed=True,
                 interpretation=["Synthetic likelihood and ABC mass apply only to arbitrary assumed rank noise/proxy warps",
                                 "NOT biological rate priors or a field scenario posterior",
                                 "No observed egg-to-adult stage or density-to-call conversion",
                                 "Same 4,248 sites were explored in previous PRs",
                                 "No environmental predictive baseline needed for descriptive POM",
                                 "Pattern fit does not imply field trophic causal identification"],
                 source_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputfiles},
                 code_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    (OUT/"receipt.json").write_text(json.dumps(receipt,indent=2)+"\n")
    print("DISTANCES\n"+results["scenario_pattern_distance"].sort_values(
        ["background","distance_mahalanobis"])[
        ["background","case","equivalence_group","distance_mahalanobis",
         "fitted_patterns_within_marginal_95"]].to_string(index=False),flush=True)
    print("CONDITIONAL TOY ABC\n"+results["toy_conditional_abc_mass"].sort_values(
        ["background","toy_abc_mass"],ascending=[True,False]).to_string(index=False),flush=True)
    print("PSEUDO RECOVERY\n"+results["pseudo_recovery_records"].groupby(
        ["background","true_group"]).recovered.agg(["mean","size"]).to_string(),flush=True)
    return results


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--run",action="store_true")
    p.add_argument("--reference-per-case",type=int,default=N_REFERENCE_PER_CASE)
    p.add_argument("--pseudo-per-case",type=int,default=N_PSEUDO_PER_CASE)
    args=p.parse_args()
    if not args.run:p.error("Explicit --run needed")
    run(n_reference=args.reference_per_case,n_pseudo=args.pseudo_per_case)
