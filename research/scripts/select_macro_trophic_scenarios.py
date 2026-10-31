"""Observed-pattern-first comparison of frozen multigeneration trophic scenarios.

Uses the existing deterministic seasonal cohort + delayed-recruitment outputs,
not ABM/PDE.  Stage suitability ranks, pond vegetation and adult calling are
different observables; the fitted statistical link is NOT biological calibration.

Primary result: *nested* spatially blocked selection among 24 fixed scenarios
and a separately inner-selected competitive additive/interaction environment
null, both scored on completely outer-held-out calling visits.
"""
from __future__ import annotations
import argparse
import hashlib
import itertools
import json
import platform
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import minimize
from scipy.special import expit
from scipy.stats import rankdata

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "research/results/macro_scenario_selection_20261031"
SITE = ROOT / "research/results/naamp_remote_vegetation_20261026/primary_site_landscape_context.csv.gz"
VISITS = ROOT / "research/results/naamp_three_guild_occurrence/full_naamp_history/naamp_completed_site_surveys.csv.gz"
SOURCES = [ROOT / f"research/results/literature_extension_20261029/primary_{risk}_dynamic_cells.csv.gz"
           for risk in (0, 1)]
SEED = 20261031
RIDGE = 10.0
LEVELS = 9
OUTER = 5
INNER = 3
CONTEXTS = ("original", "D_first_S_overtakes", "S_first_D_overtakes")
FAMILIES = ("baseline", "shared_both")
EDGES = ("dynamic", "frog_reverse")
NULLS = ("env_additive", "env_interactions")
SURVEY = ("n_visits", "n_years", "mean_air", "mean_noise",
          "season_2", "season_3", "season_4", "mean_doy")
ENV = ("bio1", "bio4", "bio12", "bio15", "water_3000m_mean", "herbaceous_3000m_mean")
COEFS = ("O", "S", "V", "OS", "OV", "SV", "OSV")


def rank_standardize(x):
    a=np.asarray(x,float)
    r=rankdata(a,axis=0)
    mean=r.mean(axis=0);sd=r.std(axis=0)
    return (r-mean)/np.maximum(sd,1e-12)


def rank_bin(x, levels=LEVELS):
    a=np.asarray(x,float)
    r=rankdata(a)
    return np.rint(((r-.5)/len(r))*(levels-1)).astype(int)


def load_cohort(sites: pd.DataFrame, visits: pd.DataFrame, expected=None):
    if sites.site.duplicated().any():
        raise ValueError("Duplicate site")
    v=visits[(visits.timeout==0)&(visits.site.isin(sites.site))].copy()
    if v.duplicated(["site","run"]).any() or not v.strong.isin([0,1]).all() or (v.strong>v["any"]).any():
        raise ValueError("Invalid nested strong/any visit or duplicate")
    counts=v.groupby("site").strong.agg(["sum","count"]).rename(columns={"sum":"k","count":"n"})
    d=sites.merge(counts,left_on="site",right_index=True,validate="one_to_one")
    if expected is not None and len(d)!=expected:
        raise ValueError("Incorrect site sample")
    if d[["k","n"]].isna().any().any() or (d.n<1).any():
        raise ValueError("Missing completed site survey")
    if not np.array_equal(d.n,d.n_visits):
        raise ValueError("Visit totals not reconciled")
    if not np.allclose(d.k/d.n,d.strong_rate,atol=1e-12):
        raise ValueError("Strong rate disagrees with archived aggregate")
    for season in (2,3,4):
        d[f"season_{season}"]=d.site.map(v.assign(flag=v.season==season).groupby("site").flag.mean())
    d["mean_doy"]=d.site.map(v.groupby("site").doy.mean())
    centers=d.groupby("route")[["lat","lon"]].mean()
    blocks=(np.floor(centers.lat/2).astype(int).astype(str)+"_"+
            np.floor(centers.lon/2).astype(int).astype(str))
    d["spatial_block"]=d.route.map(blocks)
    d["V"]=(d.flooded_3000m_mean>0).astype(int)
    required=list(SURVEY+ENV)+["V","lat","lon"]
    for background in ("uniform","target_group"):
        required.extend([f"mean_suitability_Odonata_{background}",
                         f"mean_suitability_pond_breeding_Caudata_{background}"])
    if not np.isfinite(d[required].to_numpy(float)).all():
        raise ValueError("Nonfinite predictor")
    return d.reset_index(drop=True)


def assign_folds(frame, fold_count, seed=SEED):
    """Route-level 2-degree blocks, outcome-blind balancing of site/V support."""
    blocks=frame.groupby("spatial_block").agg(sites=("site","size"),v_positive=("V","sum")).reset_index()
    if len(blocks)<fold_count or int(frame.V.sum())<fold_count:
        raise ValueError("Insufficient blocks or vegetation support")
    rng=np.random.default_rng(seed)
    blocks["tie"]=rng.random(len(blocks))
    blocks=blocks.sort_values(["sites","v_positive","tie"],ascending=[False,False,True])
    total=np.zeros(fold_count,float);positive=np.zeros(fold_count,float);mapping={}
    nt=max(len(frame)/fold_count,1.)
    vt=max(float(frame.V.sum())/fold_count,1.)
    for row in blocks.itertuples(index=False):
        score=((total+row.sites)/nt)**2-(total/nt)**2
        score+=((positive+row.v_positive)/vt)**2-(positive/vt)**2
        slot=int(np.argmin(score))
        mapping[row.spatial_block]=slot
        total[slot]+=row.sites
        positive[slot]+=row.v_positive
    assigned=frame.spatial_block.map(mapping).to_numpy(int)
    if (len(np.unique(assigned))!=fold_count or
        any(not (frame.V.to_numpy()[assigned==f]>0).any() for f in range(fold_count))):
        raise ValueError("Holdout fold has zero vegetated sites")
    if frame.assign(fold=assigned).groupby("route").fold.nunique().max()!=1:
        raise ValueError("Spatial fold leaks a route")
    return assigned


def scenario_surfaces(frames, levels=LEVELS):
    """Reject missing or changed source factorial cells; no score-led selection."""
    merged=pd.concat(frames,ignore_index=True)
    expected={(a,b,c,d) for a,b,c,d in itertools.product(CONTEXTS,FAMILIES,(False,True),EDGES)}
    found={tuple(x) for x in merged[["context","family","risk","edge"]].drop_duplicates().itertuples(index=False,name=None)
           if x[0] in CONTEXTS and x[1] in FAMILIES and x[3] in EDGES}
    if found!=expected:
        raise ValueError(f"Incomplete 24-scenario factorial: {len(found)} / 24")
    surfaces={};metadata={}
    axes=np.linspace(.25,2.,levels)
    expected_grid=np.asarray([(v,s,o) for v in (0.,1.) for s in axes for o in axes])
    for context,family,risk,edge in sorted(expected):
        rows=merged[(merged.context==context)&(merged.family==family)&
                    (merged.risk==risk)&(merged.edge==edge)].copy()
        if len(rows)!=len(expected_grid) or rows.duplicated(["vegetation","S_source","D_source"]).any():
            raise ValueError("Missing or duplicated scenario grid cells")
        if rows.case.nunique()!=1:
            raise ValueError("Scenario aliases mixed case identity")
        rows=rows.sort_values(["vegetation","S_source","D_source"])
        if not np.allclose(rows[["vegetation","S_source","D_source"]].to_numpy(float),expected_grid,
                           rtol=0,atol=1e-8):
            raise ValueError("Unexpected grid values/order")
        y=rows.F_B.to_numpy(float)
        if not np.isfinite(y).all() or (y<=0).any():
            raise ValueError("Invalid multigeneration frog population")
        label=f"case_{int(rows.case.iloc[0]):03d}"
        if label in surfaces:
            raise ValueError("Duplicate case ID")
        surfaces[label]=y.reshape(2,levels,levels)
        metadata[label]=dict(case=int(rows.case.iloc[0]),context=context,family=family,
                             risk=bool(risk),edge=edge,years=80,window=20,levels=levels)
    if len(surfaces)!=24:
        raise ValueError("Wrong scenario count")
    return surfaces, metadata


def candidate_scores_at_sites(d,background,surfaces):
    o=d[f"mean_suitability_Odonata_{background}"].to_numpy(float)
    s=d[f"mean_suitability_pond_breeding_Caudata_{background}"].to_numpy(float)
    v=d.V.to_numpy(int)
    return {name:np.log(grid[v,rank_bin(s,grid.shape[1]),rank_bin(o,grid.shape[2])])
            for name,grid in surfaces.items()}


def predictor_design(d,background,scenario_values):
    o=rank_standardize(d[f"mean_suitability_Odonata_{background}"])
    s=rank_standardize(d[f"mean_suitability_pond_breeding_Caudata_{background}"])
    v=d.V.to_numpy(float)
    cov=rank_standardize(d[list(SURVEY+ENV)].to_numpy())
    lat,lon=rank_standardize(d[["lat","lon"]].to_numpy()).T
    space=np.column_stack([lat,lon,lat*lat,lat*lon,lon*lon])
    additive=np.column_stack([o,s,v,cov,space])
    full=np.column_stack([additive,o*s,o*v,s*v,o*s*v])
    all_design={"env_additive":additive,"env_interactions":full}
    for key,values in scenario_values.items():
        all_design[key]=np.column_stack([additive,values])
    return all_design


def fit_predict(x_train,k_train,n_train,x_test,return_mechanism_slope=False):
    """Regularized site-binomial observation link; train means and SD from train."""
    mu=x_train.mean(axis=0);sd=x_train.std(axis=0)
    keep=sd>1e-11
    z=np.column_stack([np.ones(len(x_train)),(x_train[:,keep]-mu[keep])/sd[keep]])
    xt=np.column_stack([np.ones(len(x_test)),(x_test[:,keep]-mu[keep])/sd[keep]])
    baseline=np.clip(np.sum(k_train)/np.sum(n_train),1e-7,1-1e-7)
    init=np.zeros(z.shape[1],float);init[0]=np.log(baseline/(1-baseline))
    def objective(beta):
        eta=z@beta
        nll=np.dot(n_train,np.logaddexp(0,eta))-np.dot(k_train,eta)
        nll+=RIDGE*np.dot(beta[1:],beta[1:])/2
        grad=z.T@(n_train*expit(eta)-k_train)
        grad[1:]+=RIDGE*beta[1:]
        return float(nll),grad
    opt=minimize(objective,init,method="L-BFGS-B",jac=True,options={"maxiter":400,"ftol":1e-11})
    if not opt.success and np.linalg.norm(opt.jac,ord=np.inf)>.1:
        raise RuntimeError("Binomial fit failed: "+str(opt.message))
    p=np.clip(expit(xt@opt.x),1e-10,1-1e-10)
    if return_mechanism_slope:
        # The last input column is log(F_B) in the mechanism-only designs.
        # A removed zero-variance predictor has no identifiable slope.
        if not keep[-1]:
            return p,float("nan")
        return p,float(opt.x[-1])
    return p


def neglog(k,n,p):
    return -(k*np.log(p)+(n-k)*np.log1p(-p))


def select_one_outer(d,design,folds,outer,restrict_candidates=None):
    """Inner selection only sees the outer TRAIN rows; no outcome leakage."""
    train=folds!=outer
    test=~train
    if not train.any() or not test.any():
        raise ValueError("Empty outer fold")
    tr=d.loc[train].reset_index(drop=True)
    inner_folds=assign_folds(tr,INNER,seed=SEED+1000+outer)
    ks=tr.k.to_numpy(float);ns=tr.n.to_numpy(float)
    names=list(design) if restrict_candidates is None else list(NULLS)+list(restrict_candidates)
    if set(NULLS)-set(names):
        raise ValueError("Both null benchmarks required")
    all_scores=[]
    inner_columns={key:x[train] for key,x in design.items()}
    for name in names:
        x=inner_columns[name];loss=0.;total_n=0.
        for inner in range(INNER):
            val=inner_folds==inner;dev=~val
            p=fit_predict(x[dev],ks[dev],ns[dev],x[val])
            loss+=float(neglog(ks[val],ns[val],p).sum())
            total_n+=float(ns[val].sum())
        all_scores.append(dict(outer_fold=outer,candidate=name,inner_nll=loss/total_n,
                               inner_visits=int(total_n)))
    inner=pd.DataFrame(all_scores)
    scoring=lambda names:sorted(((float(inner.loc[inner.candidate==name,"inner_nll"].iloc[0]),name)
                                for name in names))[0][1]
    candidate_list=[name for name in names if name not in NULLS]
    if not candidate_list:
        raise ValueError("No mechanistic candidates")
    win=scoring(candidate_list);null=scoring(NULLS)
    outer_rows=[]
    for candidate in [win,"env_additive","env_interactions"]:
        x=design[candidate]
        p=fit_predict(x[train],d.k.to_numpy(float)[train],d.n.to_numpy(float)[train],x[test])
        for pos, pred in zip(np.flatnonzero(test),p):
            outer_rows.append(dict(site=d.site.iloc[pos],spatial_block=d.spatial_block.iloc[pos],
                                   route=d.route.iloc[pos],background=None,outer_fold=outer,
                                   candidate=candidate,k=int(d.k.iloc[pos]),n=int(d.n.iloc[pos]),
                                   V=int(d.V.iloc[pos]),predicted=float(pred)))
    pred=pd.DataFrame(outer_rows)
    support=dict(outer_fold=outer,n_test_sites=int(test.sum()),n_test_visits=int(d.n.to_numpy()[test].sum()),
                 test_vegetated=int(d.V.to_numpy()[test].sum()),
                 train_vegetated=int(d.V.to_numpy()[train].sum()),
                 selected_scenario=win,selected_null=null)
    return pred, inner, support


def fixed_nested_comparison(d,surfaces,outer_folds=None,restrict_candidates=None):
    if outer_folds is None:
        outer_folds=assign_folds(d,OUTER,seed=SEED)
    result=[];tables=[];choices=[]
    backgrounds=("uniform","target_group")
    for bg in backgrounds:
        design=predictor_design(d,bg,candidate_scores_at_sites(d,bg,surfaces))
        for fold in sorted(np.unique(outer_folds)):
            pred,inner,support=select_one_outer(d,design,outer_folds,int(fold),restrict_candidates)
            pred["background"]=bg;inner["background"]=bg
            support["background"]=bg
            result.append(pred);tables.append(inner);choices.append(support)
            print("NESTED",bg,"fold",fold,"winner",support["selected_scenario"],
                  "null",support["selected_null"],"support",support["test_vegetated"],flush=True)
    return pd.concat(result,ignore_index=True),pd.concat(tables,ignore_index=True),pd.DataFrame(choices)


def score_selected(pred,choices,reps=999):
    """Evaluate locked inner-selected candidates and baselines on outer predictions."""
    score_rows=[];block_rows=[]
    for bg in ("uniform","target_group"):
        frame=pred[pred.background==bg]
        choose=choices[choices.background==bg]
        target=pd.concat([frame[(frame.outer_fold==r.outer_fold)&(frame.candidate==r.selected_scenario)]
                         for r in choose.itertuples(index=False)],ignore_index=True)
        null=pd.concat([frame[(frame.outer_fold==r.outer_fold)&(frame.candidate==r.selected_null)]
                       for r in choose.itertuples(index=False)],ignore_index=True)
        if len(target)==0 or target.site.duplicated().any() or null.site.duplicated().any():
            raise AssertionError("Invalid selected out-of-fold prediction set")
        for tag,part in [("selected_mechanism",target),("selected_environment",null)]+[
            (name,frame[frame.candidate==name]) for name in NULLS
        ]:
            p=part.predicted.to_numpy();k=part.k.to_numpy();n=part.n.to_numpy()
            score_rows.append(dict(background=bg,model=tag,n_sites=len(part),n_visits=int(n.sum()),
                                   nll_per_visit=float(neglog(k,n,p).sum()/n.sum()),
                                   brier_per_visit=float(np.sum(k*(1-p)**2+(n-k)*p**2)/n.sum())))
        for ref_name,ref in [("selected_environment",null),
                             ("env_additive",frame[frame.candidate=="env_additive"]),
                             ("env_interactions",frame[frame.candidate=="env_interactions"])]:
            a=target[["site","spatial_block","k","n","predicted"]]
            b=ref[["site","spatial_block","k","n","predicted"]].rename(columns={"predicted":"null_pred"})
            pair=a.merge(b,on=["site","spatial_block","k","n"],validate="one_to_one")
            if len(pair)!=len(a) or len(pair)!=len(b):
                raise AssertionError("Improper paired site score")
            diff=neglog(pair.k,pair.n,pair.null_pred)-neglog(pair.k,pair.n,pair.predicted)
            blocks=pair.assign(improvement=diff).groupby("spatial_block")[["improvement","n"]].sum()
            mat=blocks.to_numpy(float)
            rng=np.random.default_rng(SEED)
            picks=rng.integers(0,len(mat),size=(reps,len(mat)))
            draws=mat[picks].sum(axis=1)
            vals=draws[:,0]/draws[:,1]
            block_rows.append(dict(background=bg,reference=ref_name,
                                   mechanism_minus_null_gain=float(diff.sum()/pair.n.sum()),
                                   gain_low_conditional=float(np.quantile(vals,.025)),
                                   gain_high_conditional=float(np.quantile(vals,.975)),
                                   n_blocks=len(mat),n_sites=len(pair),n_visits=int(pair.n.sum())))
    return pd.DataFrame(score_rows),pd.DataFrame(block_rows)


def observed_pattern_diagnostic(d,preds,choices):
    """Global interaction fingerprint, *secondary* (not used for scenario selection)."""
    rows=[]
    for bg in ("uniform","target_group"):
        o=rank_standardize(d[f"mean_suitability_Odonata_{bg}"])
        s=rank_standardize(d[f"mean_suitability_pond_breeding_Caudata_{bg}"])
        v=rank_standardize(d.V)
        focal=np.column_stack([o,s,v,o*s,o*v,s*v,o*s*v])
        lat,lon=rank_standardize(d[["lat","lon"]].to_numpy()).T
        cov=rank_standardize(d[list(SURVEY+ENV)].to_numpy())
        x=np.column_stack([focal,np.ones(len(d)),cov,lat,lon,lat**2,lat*lon,lon**2])
        bp=preds[preds.background==bg]
        ch=choices[choices.background==bg]
        for label in ("observed","selected_mechanism","selected_environment","env_additive","env_interactions"):
            if label=="observed":
                y=d.k.to_numpy()/d.n.to_numpy()
            else:
                if label in ("selected_mechanism","selected_environment"):
                    parts=[bp[(bp.outer_fold==row.outer_fold)&
                              (bp.candidate==(row.selected_scenario if label=="selected_mechanism"
                                             else row.selected_null))]
                           for row in ch.itertuples(index=False)]
                    q=pd.concat(parts).set_index("site")
                else:
                    q=bp[bp.candidate==label].set_index("site")
                if len(q)!=len(d) or q.index.duplicated().any():
                    raise ValueError("Missing/duplicate pattern predictions")
                y=d.site.map(q.predicted).to_numpy(float)
            beta=np.linalg.lstsq(x,rank_standardize(y),rcond=1e-10)[0][:7]
            rows.append(dict(background=bg,series=label,**dict(zip(COEFS,map(float,beta)))))
    return pd.DataFrame(rows)


def run_full():
    OUT.mkdir(parents=True,exist_ok=True)
    d=load_cohort(pd.read_csv(SITE),pd.read_csv(VISITS),expected=4248)
    if int(d.n.sum())!=63180 or int(d.V.sum())!=506:
        raise AssertionError("Unexpected NAAMP source size")
    sources=[pd.read_csv(p) for p in SOURCES]
    surfaces,metadata=scenario_surfaces(sources)
    outer=assign_folds(d,OUTER,seed=SEED)
    pred,inner,choices=fixed_nested_comparison(d,surfaces,outer)
    scores,comparison=score_selected(pred,choices)
    fingerprint=observed_pattern_diagnostic(d,pred,choices)
    wins=choices.groupby(["background","selected_scenario"]).size().rename("outer_folds_won").reset_index()
    outputs=dict(outer_heldout_probabilities=pred,inner_candidate_scores=inner,
                 outer_chosen_scenarios=choices,outer_model_scores=scores,
                 paired_null_comparisons=comparison,observed_predicted_interactions=fingerprint,
                 scenario_frequency=wins)
    for name,frame in outputs.items():
        frame.to_csv(OUT/(name+".csv"),index=False)
    (OUT/"scenario_metadata.json").write_text(json.dumps(metadata,indent=2)+"\n")
    recipe=dict(status="MACRO_FIRST_NESTED_CV_NOT_FIELD_CAUSAL_IDENTIFICATION",
                n_sites=len(d),n_surveys=int(d.n.sum()),n_vegetated=int(d.V.sum()),
                n_spatial_blocks=d.spatial_block.nunique(),n_scenarios=len(surfaces),
                source_horizon_years=80,source_last_window_years=20,
                outer_folds=OUTER,inner_folds=INNER,seed=SEED,ridge=RIDGE,
                backgrounds=["uniform","target_group"],
                selection="inner nested spatial CV per outer fold, best of 24 vs best of 2 environmental nulls",
                primary_score="heldout site-binomial negative log score per completed survey",
                assumptions=["O/S suitability rank transfer to model source bins is not density calibration",
                             "positive flooded-landscape proxy is not observed pond plant refuge",
                             "acoustic observation logit learned on training blocks, not independent stage calibration",
                             "past NAAMP exploratory analyses mean outer CV is not truly pristine external replication",
                             "site-level survey binomial ignores possible extra-binomial dependence",
                             "ABM/PDE synthetic pilot excluded from scenario selection"],
                source_hashes={str(path.relative_to(ROOT)):hashlib.sha256(path.read_bytes()).hexdigest()
                               for path in [SITE,VISITS]+SOURCES},
                code_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                runtime=dict(python=platform.python_version(),numpy=np.__version__,pandas=pd.__version__))
    (OUT/"receipt.json").write_text(json.dumps(recipe,indent=2)+"\n")
    print("SCORE TABLE\n"+scores.to_string(index=False))
    print("GAIN TABLE\n"+comparison.to_string(index=False))
    print("WINNERS\n"+wins.to_string(index=False))
    print("PATTERN FINGERPRINT\n"+fingerprint.to_string(index=False))
    return outputs


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--run",action="store_true")
    args=p.parse_args()
    if not args.run:
        p.error("Explicit --run required for fixed-site macro scenario selection")
    run_full()
