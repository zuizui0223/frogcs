"""G5: pre-fixed mechanism-constrained observation prediction vs environmental nulls.

Source coefficients from G4 independently original-256 PR161 mean log aquatic F_B
eight-corner arms 11 and 00, NOT selected using observed acoustic outcomes.
Only the acoustic observation slope is train-fitted (constrained >=0). Predict
original strong adult calling on the same 56 geographic block holdouts.

A good heldout score is predictive COMPATIBILITY, not an identified natural
predator mechanism, because the eight-corner surface is exactly spanned by
unrestricted O/S/V interactions and O/S are habitat suitability not density.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.optimize import minimize
from scipy.special import expit

from acoustic_mechanism_cv import (
    prepare_sites, assign_spatial_folds, BACKGROUNDS, RIDGE,
    train_predict, log_score,
)
from g1_shared_environment_spatial_block import design_matrices
from g4_field_model_alignment_8corner_audit_20261106 import (
    original_rank01,predictor_basis,CORNERS,
)

SOURCE_MAIN="5e2f0a87c639df373fa2700b29403d2ab417a1cc"
SOURCE_G4_RUN=42172357235
N_SITES=4248
N_VISITS=63180
N_BLOCKS=56
N_ROUTES=432
N_FOLDS=5
N_BOOT=999
BOOT_SEED=20261106
SOURCE_ARMS=("00","11")
MODELS=("env_add","env_all","flex_add","flex_all","flex_prior_00","flex_prior_11")
PRECOMMITTED_COMPARISONS=(
    ("flex_add","flex_prior_11","primary_11_vs_flex_environment"),
    ("flex_add","flex_prior_00","alternative_00_vs_flex_environment"),
    ("flex_prior_00","flex_prior_11","11_vs_00_source_structure"),
    ("flex_all","flex_prior_11","11_vs_flexible_four_interactions"),
    ("env_add","env_all","original_free_interactions_vs_additive"),
    ("flex_add","flex_all","flexible_four_interactions_vs_flex_environment"),
)
REPLAY={
    "uniform":{"env_add":.670490,"env_all":.668009},
    "target_group":{"env_add":.672097,"env_all":.674809},
}


def require(v,msg):
    if not bool(v):
        raise AssertionError(msg)


def read_corner_source(path):
    z=pd.read_csv(path,dtype={"arm":str})
    require(len(z)==16 and {"arm","vegetation","caudata","odonata","mean_log_F_B"}.issubset(z.columns),
            "Only frozen original G4 source-prior 2×8 corners accepted")
    require(set(z.arm)==set(SOURCE_ARMS),"Model source prior arm identity drifted")
    source={}
    for arm in SOURCE_ARMS:
        a=z[z.arm==arm]
        require(len(a)==8 and not a.duplicated(["vegetation","caudata","odonata"]).any(),
                "Incomplete original G4 source full 2x2x2 factorial")
        values={(int(r.vegetation),int(r.caudata),int(r.odonata)):float(r.mean_log_F_B)
                for r in a.itertuples(index=False)}
        require(set(values)==set(CORNERS),"Source prior original 8-corner identity missing")
        # Exact 8 factorial vertex response on a 1,O,S,V,OS,OV,SV,OSV basis.
        mat=np.array([predictor_basis([d],[s],[v])[0] for v,s,d in CORNERS])
        coef=np.linalg.solve(mat,np.array([values[c] for c in CORNERS],dtype=float))
        require(np.allclose(mat@coef,[values[c] for c in CORNERS],atol=1e-10,rtol=0),
                "Original model source corner sign geometry changed")
        source[arm]=coef
    return source


def constrained_train_predict(xtrain,k,n,xtest,ridge=RIDGE):
    """As in original PR145, but LAST standardized model-source slope >= 0."""
    xtrain=np.asarray(xtrain,float)
    xtest=np.asarray(xtest,float)
    n=np.asarray(n,float)
    k=np.asarray(k,float)
    require(xtrain.shape[1]==xtest.shape[1] and np.isfinite(xtrain).all()
            and np.isfinite(xtest).all(),"Source model observation design nonfinite")
    require((n>0).all() and (k>=0).all() and (k<=n).all(),
            "Original adult-call binomial source invalid")
    mean=xtrain.mean(axis=0)
    sd=xtrain.std(axis=0)
    # Keep source proxy LAST and reject a degenerate source shape.
    require(sd[-1]>1e-8,"Original mechanism geometry has no testable cross-site variation")
    good=sd>1e-12
    z=(xtrain[:,good]-mean[good])/sd[good]
    t=(xtest[:,good]-mean[good])/sd[good]
    z=np.column_stack((np.ones(len(z)),z))
    t=np.column_stack((np.ones(len(t)),t))
    p0=np.clip(k.sum()/n.sum(),1e-6,1-1e-6)
    init=np.zeros(z.shape[1]);init[0]=np.log(p0/(1-p0))
    def objective(beta):
        lin=z@beta
        val=np.logaddexp(0,lin)@n-lin@k+ridge*(beta[1:]@beta[1:])/2
        grad=z.T@(n*expit(lin)-k)
        grad[1:]+=ridge*beta[1:]
        return float(val),grad
    bounds=[(None,None)]*(len(init)-1)+[(0,None)]
    fit=minimize(objective,init,jac=True,method="L-BFGS-B",bounds=bounds,
                 options={"maxiter":650,"ftol":1e-11})
    require(fit.success or np.linalg.norm(fit.jac,ord=np.inf)<0.15,
            "Source constrained acoustic model failed convergence "+str(fit.message))
    require(fit.x[-1]>=-1e-12,"Mechanistic acoustic response fit inverted source hazard prior")
    pred=np.clip(expit(t@fit.x),1e-10,1-1e-10)
    return pred,float(fit.x[-1])


def features_by_background(d,background,source):
    design=design_matrices(d,background)
    O=original_rank01(d["mean_suitability_Odonata_"+background])
    S=original_rank01(d["mean_suitability_pond_breeding_Caudata_"+background])
    V=d.V.to_numpy(dtype=float)
    whole=predictor_basis(O,S,V)
    result={}
    # Only predeclared model interaction shape is added to the flexible
    # environment additive model; model intercept/additive O/S/V components
    # must not shift main-effect penalty or be described as new mechanism.
    for arm in SOURCE_ARMS:
        coef=source[arm]
        interaction=(whole[:,4:]@coef[4:])
        require(np.isfinite(interaction).all() and interaction.std()>1e-8,
                "Original source-prior model interaction has no independent field variation")
        # G4 mathematical rank audit already showed the full source signal
        # lies within the empirical saturated 8-dimensional interaction span.
        additive_full=np.column_stack((np.ones(len(d)),design["env_all"]))
        projection=np.linalg.lstsq(additive_full,interaction,rcond=None)[0]
        residual=np.max(np.abs(additive_full@projection-interaction))
        require(residual<=1e-8,
                "Original mechanism source predictor unexpectedly outside saturated O/S/V empirical basis")
        result[arm]=interaction
    return design,result


def heldout_site_predictions(d,folds,source):
    all_predictions=[]
    regression=[]
    for background in BACKGROUNDS:
        design,features=features_by_background(d,background,source)
        for fold in range(N_FOLDS):
            train=folds!=fold
            test=folds==fold
            require(train.sum()>2000 and test.sum()>100,
                    "Original 5-fold acoustic-geographical support inadequate")
            ix=np.flatnonzero(test)
            for model in MODELS:
                if model in ("flex_prior_00","flex_prior_11"):
                    arm=model.rsplit("_",1)[-1]
                    x=np.column_stack((design["flex_add"],features[arm]))
                    pred,coefficient=constrained_train_predict(
                        x[train],d.k.to_numpy()[train],d.n.to_numpy()[train],x[test])
                else:
                    x=design[model]
                    pred=train_predict(x[train],d.k.to_numpy()[train],
                                       d.n.to_numpy()[train],x[test],ridge=RIDGE)
                    coefficient=np.nan
                all_predictions.append(pd.DataFrame({
                    "site":d.site.iloc[ix].to_numpy(),
                    "route":d.route.iloc[ix].to_numpy(),
                    "spatial_block":d.spatial_block.iloc[ix].to_numpy(),
                    "background":background,"fold":fold,"candidate":model,
                    "k_strong":d.k.iloc[ix].to_numpy(dtype=int),
                    "n_completed":d.n.iloc[ix].to_numpy(dtype=int),
                    "predicted":pred
                }))
                regression.append(dict(background=background,fold=fold,
                    candidate=model,original_train_sites=int(train.sum()),
                    heldout_sites=int(test.sum()),
                    constrained_source_beta=coefficient,
                    source_slope_constrained_positive=model.startswith("flex_prior_")))
    out=pd.concat(all_predictions,ignore_index=True)
    diagnostic=pd.DataFrame(regression)
    require(len(out)==N_SITES*len(BACKGROUNDS)*len(MODELS) and
            len(diagnostic)==N_FOLDS*len(BACKGROUNDS)*len(MODELS) and
            not out.duplicated(["site","background","candidate"]).any(),
            "G5 source-prior heldout acoustic prediction inventory incomplete")
    require(out.groupby(["background","candidate"]).site.nunique().eq(N_SITES).all()
            and out.groupby(["background","candidate"]).n_completed.sum().eq(N_VISITS).all()
            and out.groupby(["background","candidate"]).spatial_block.nunique().eq(N_BLOCKS).all(),
            "Original source heldout site/visit/spatial block denominators changed")
    return out,diagnostic


def model_scores(heldout):
    h=heldout.copy()
    h["loss"]=log_score(h.k_strong,h.n_completed,h.predicted)
    h["brier"]=h.k_strong*(1-h.predicted)**2+(h.n_completed-h.k_strong)*h.predicted**2
    agg=h.groupby(["background","candidate"],sort=True).agg(
        sites=("site","nunique"),blocks=("spatial_block","nunique"),
        surveys=("n_completed","sum"),strong=("k_strong","sum"),
        total_nll=("loss","sum"),total_brier=("brier","sum")
    ).reset_index()
    agg["nll_per_visit"]=agg.total_nll/agg.surveys
    agg["brier_per_visit"]=agg.total_brier/agg.surveys
    require(len(agg)==len(BACKGROUNDS)*len(MODELS) and
            agg.surveys.eq(N_VISITS).all() and agg.strong.eq(36554).all(),
            "Original 4,248-site R1 strong call denominators/source changed")
    for bg in BACKGROUNDS:
        for arm,value in REPLAY[bg].items():
            z=agg[(agg.background==bg)&(agg.candidate==arm)]
            require(len(z)==1 and abs(float(z.iloc[0].nll_per_visit)-value)<3e-5,
                    "Original PR145 train/holdout acoustic predictor replay failed "+bg+" "+arm)
    return h,agg


def block_paired_contrasts(h,boot=N_BOOT):
    rows=[]
    for bg in BACKGROUNDS:
        x=h[h.background.eq(bg)]
        a=x.groupby(["candidate","spatial_block"],sort=True).agg(
            loss=("loss","sum"),trials=("n_completed","sum")
        ).reset_index()
        blocks=sorted(a.spatial_block.unique())
        require(len(blocks)==N_BLOCKS,"Original 56 geographic blocks missing")
        for base,compare,label in PRECOMMITTED_COMPARISONS:
            b=a[a.candidate.eq(base)].set_index("spatial_block").loc[blocks]
            z=a[a.candidate.eq(compare)].set_index("spatial_block").loc[blocks]
            require(np.array_equal(b.trials,z.trials),"Paired heldout blocks have unequal source trials")
            d=b.loss.to_numpy()-z.loss.to_numpy()
            n=b.trials.to_numpy(dtype=float)
            ix=np.random.default_rng(BOOT_SEED).integers(
                0,len(blocks),size=(boot,len(blocks)))
            estimates=d[ix].sum(axis=1)/n[ix].sum(axis=1)
            lo,hi=np.quantile(estimates,[.025,.975])
            rows.append(dict(background=bg,contrast=label,
                 baseline=base,augmented=compare,
                 gain_nll_per_completed_visit=float(d.sum()/n.sum()),
                 source_block_mc95_low=float(lo),source_block_mc95_high=float(hi),
                 n_original_source_blocks=N_BLOCKS,n_original_acoustic_visits=N_VISITS,
                 source_bootstrap_repetitions=boot,
                 model_interaction_prior_unselected_on_field=True))
    out=pd.DataFrame(rows)
    require(len(out)==len(BACKGROUNDS)*len(PRECOMMITTED_COMPARISONS),
            "Precommitted source-only G5 contrasts incomplete")
    return out


def plot(contrasts,out):
    p=contrasts[contrasts.contrast.isin((
        "primary_11_vs_flex_environment","alternative_00_vs_flex_environment",
        "11_vs_00_source_structure","11_vs_flexible_four_interactions"
    ))].copy()
    labels={
       "primary_11_vs_flex_environment":"11 mechanism versus nonlinear environment",
       "alternative_00_vs_flex_environment":"00 alternative versus nonlinear environment",
       "11_vs_00_source_structure":"11 mechanism versus 00 alternative",
       "11_vs_flexible_four_interactions":"11 mechanism versus four free interactions"
    }
    fig,ax=plt.subplots(figsize=(11.7,5.6))
    for i,name in enumerate(labels):
        for bg,shift,color,marker in (
            ("uniform",-.12,"C0","o"),
            ("target_group",.12,"C1","s"),
        ):
            r=p[(p.background==bg)&(p.contrast==name)]
            require(len(r)==1,"G5 source prediction plot missing comparator")
            x=r.iloc[0]; y=3-i+shift
            ax.errorbar(x.gain_nll_per_completed_visit,y,
                 xerr=[[x.gain_nll_per_completed_visit-x.source_block_mc95_low],
                       [x.source_block_mc95_high-x.gain_nll_per_completed_visit]],
                 color=color,marker=marker,linestyle="none",capsize=4)
    ax.axvline(0,color="grey",lw=1)
    ax.set_yticks(range(4),list(reversed(labels.values())))
    ax.set_xlabel("Reduction in out-of-geographic-block strong-call NLL / completed visit (positive = gain)")
    ax.grid(axis="x",alpha=.18)
    fig.suptitle("G5 · A source-constrained trophic surface is a testable acoustic predictor",y=.97)
    from matplotlib.lines import Line2D
    fig.legend(handles=[Line2D([0],[0],color="C0",marker="o",linestyle="none",label="Uniform SDM"),
                        Line2D([0],[0],color="C1",marker="s",linestyle="none",label="Target-group SDM")],
               ncol=2,frameon=False,loc="upper center",bbox_to_anchor=(.5,.90))
    fig.text(.015,.018,
       "95% 56-spatial-block resampling of unchanged 4,248 sites/63,180 calls. "
       "Only train-block observation slopes fitted; predator mechanism NOT identified.",fontsize=8)
    fig.tight_layout(rect=(0,.06,1,.80))
    fig.savefig(out/"G5_fixed_source_mechanism_vs_free_environment_holdout.png",dpi=180)
    plt.close(fig)


def run(sites,visits,source_file,g4_receipt,out):
    g4=json.loads(Path(g4_receipt).read_text())
    require(g4["status"]=="G4_ORIGINAL_FIELD_EIGHT_CORNER_AND_MODEL_SPAN_AUDIT_SUCCESS"
            and g4["observed_cells_supported"]==15 and
            g4["both_SDM_backgrounds_all_eight_corners_supported"] is False,
            "Original G4 field 15/16 support gate missing or changed")
    raw=pd.read_csv(sites)
    survey=pd.read_csv(visits)
    d=prepare_sites(raw,survey,expected_sites=N_SITES)
    require(d.site.is_unique and int(d.n.sum())==N_VISITS and
            int(d.V.sum())==506 and d.spatial_block.nunique()==N_BLOCKS
            and d.route.nunique()==N_ROUTES,
            "Original acoustic site/vegetation/source denominator drift")
    folds=assign_spatial_folds(d)
    require(set(folds)==set(range(5)) and
            d.assign(fold=folds).groupby("spatial_block").fold.nunique().max()==1,
            "Original source fold leakage")
    source=read_corner_source(source_file)
    heldout,slopes=heldout_site_predictions(d,folds,source)
    scored,agg=model_scores(heldout)
    contrasts=block_paired_contrasts(scored)
    primary=contrasts[contrasts.contrast=="primary_11_vs_flex_environment"]
    fit=slopes[slopes.candidate=="flex_prior_11"]
    robust=bool(len(primary)==2 and
                primary.source_block_mc95_low.gt(0).all() and
                fit.groupby("background").constrained_source_beta.apply(
                    lambda x: (x>1e-6).sum()>=4).all())
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    heldout.to_csv(out/"G5_4248_original_site_source_holdout_predictions.csv.gz",
                   index=False,compression={"method":"gzip","mtime":0})
    slopes.to_csv(out/"G5_5fold_constrained_acoustic_source_slopes.csv",index=False)
    agg.to_csv(out/"G5_original_site_binomial_acoustic_scores.csv",index=False)
    contrasts.to_csv(out/"G5_56block_source_repeated_model_comparisons.csv",index=False)
    plot(contrasts,out)
    receipt=dict(
       status="G5_ORIGINAL_SOURCE_CONSTRAINED_ACOUSTIC_HOLDOUT_AUDIT_SUCCESS",
       original_main_sha=SOURCE_MAIN,source_G4_run=SOURCE_G4_RUN,
       original_field_sites=N_SITES,original_completed_visits=N_VISITS,
       original_geographic_blocks=N_BLOCKS,original_routes=N_ROUTES,
       original_256_model_source_all_models_pooled=True,
       source_acoustic_environment_G1_replay_passed=True,
       source_predictor_span_inside_original_four_interactions=True,
       source_model_mechanism_as_positively_constrained_train_slope=True,
       independent_geographic_predictive_gain_both_backgrounds=robust,
       source_prediction_rows=len(heldout),source_score_rows=len(agg),
       source_paired_contrast_rows=len(contrasts),
       model_penalty=RIDGE,source_model_bootstrap=N_BOOT,
       source_bootstrap_seed=BOOT_SEED,
       identified_actual_pond_predation=False,
       calibrated_larval_to_adult_observation_link=False,
       original_field_corner_support_passed_both_backgrounds=False,
       original_input_sha256={Path(p).name:hashlib.sha256(Path(p).read_bytes()).hexdigest()
                             for p in (sites,visits,source_file,g4_receipt)}
    )
    (out/"G5_source_constrained_observation_receipt.json").write_text(
        json.dumps(receipt,indent=2,ensure_ascii=False)+"\n")
    print("G5_SOURCE_MECHANISTIC_FIELD_PREDICTION_AUDIT_SUCCESS",json.dumps({
       k:v for k,v in receipt.items() if k!="original_input_sha256"
    }),flush=True)
    print("G5_ORIGINAL_56BLOCK_SOURCE_INCREMENTAL_EFFECTS\n"+
          contrasts.to_string(index=False),flush=True)
    print("G5_ORIGINAL_SITE_SOURCE_BINOMIAL_SCORE\n"+
          agg.to_string(index=False),flush=True)


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    for key in ("sites","visits","source_file","g4_receipt","out"):
        parser.add_argument("--"+key.replace("_","-"),type=Path,required=True)
    a=parser.parse_args()
    run(a.sites,a.visits,a.source_file,a.g4_receipt,a.out)
