"""G14: synthetic ABC-selected original food-web interaction templates vs adult calls.

All source templates frozen from the original 20,000 80-year model proposals,
without field outcome selection. Compare against G5's source-locked geographic
folds and environmental baselines. This is NOT wild biological calibration.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

from acoustic_mechanism_cv import (
    BACKGROUNDS, RIDGE, assign_spatial_folds, log_score, prepare_sites, train_predict,
)
from g1_shared_environment_spatial_block import design_matrices
from g4_field_model_alignment_8corner_audit_20261106 import (
    original_rank01, predictor_basis,
)
from g5_source_constrained_acoustic_holdout_20261106 import constrained_train_predict

ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/"research/results/g12_abc_pom_prior_20261107"
SITE=ROOT/"research/results/naamp_remote_vegetation_20261026/primary_site_landscape_context.csv.gz"
VISITS=ROOT/"research/results/naamp_three_guild_occurrence/full_naamp_history/naamp_completed_site_surveys.csv.gz"
OUT=ROOT/"research/results/g14_abc_pom_field_ensemble_20261107"
FIELD_SOURCE_SHA={
    "site":"cbb389264f8bf167f53b5dfd38c5e1a17aec6243cc6ce30cbb7ae3b5417f75ff",
    "visits":"74d28435ce6e1a842e003eaa6754c6db373e026728cfbf457784814c47cd997c",
}
TEMPLATES=("ABC_accepted","ABC_accepted_viable","all_20000_prior","R2_rejected")
BASELINES=("flex_add","flex_all")
N_SITE=4248
N_VISITS=63180
N_STRONG=36554
N_BLOCK=56
N_ROUTE=432
N_VEG=506
N_FOLD=5
N_BOOT=999
SEED=20261106
EPS=1e-6

def require(ok,message):
    if not bool(ok):
        raise AssertionError(message)

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def original_four_interaction_coefficients(z):
    """Map four balanced factorial contrasts to the four O/S/V polynomial terms."""
    a=np.asarray(z,float)
    require(a.ndim==2 and a.shape[1]==4 and np.isfinite(a).all(),
            "Require finite [OS,OV,SV,OSV] source log-factorial contrasts")
    return np.column_stack((a[:,0]-a[:,3]/2,
                            a[:,1]-a[:,3]/2,
                            a[:,2]-a[:,3]/2,
                            a[:,3]))

def read_original_20k():
    receipt=json.loads((SOURCE/"source_receipt/r2_original_source_receipt.json").read_text())
    require(receipt["status"]=="FROGCS_MAIN3600_R2_ALL_20000_SOURCE_RATES_STRUCTURES_VERIFIED"
            and receipt["original_main_sha"]=="5e2f0a87c639df373fa2700b29403d2ab417a1cc"
            and receipt["accepted_four_sign"]==794
            and receipt["accepted_after_original_survival_floor"]==426,
            "G14 original R2 80-year source receipt missing")
    paths=sorted((SOURCE/"original_20k").glob("shard_*.csv.gz"))
    require({p.name for p in paths}=={f"shard_{i:02d}.csv.gz" for i in range(8)},
            "G14 original eight source shards missing")
    data=[]
    for p in paths:
        require(sha(p)==receipt["original_shard_sha256"][p.name],
                "G14 original biological model source changed: "+p.name)
        q=pd.read_csv(p)
        require(len(q)==2500,"Each original ABC source shard must be 2,500")
        data.append(q)
    d=pd.concat(data,ignore_index=True).sort_values("draw_id").reset_index(drop=True)
    require(len(d)==20000 and d.draw_id.eq(np.arange(20000)).all(),
            "Original 20,000 source draws missing")
    q=d[["log_OS","log_OV","log_SV","log_OSV"]].to_numpy(float)
    accept=(q[:,0]<-EPS)&(q[:,1]<-EPS)&(q[:,2]>EPS)&(q[:,3]>EPS)
    viable=accept & d.floor_ok.to_numpy(bool)
    require(np.array_equal(accept,d.accepted.to_numpy(bool))
            and int(accept.sum())==794 and int(viable.sum())==426
            and int(d.loc[accept,"model_id"].nunique())==647,
            "G14 ABC screen acceptance changed after the fact")
    transformed=original_four_interaction_coefficients(q)
    select={
        "ABC_accepted":accept,
        "ABC_accepted_viable":viable,
        "all_20000_prior":np.ones(20000,bool),
        "R2_rejected":~accept,
    }
    rows=[]
    templates={}
    for name,mask in select.items():
        require(mask.sum()>0,"Empty fixed G14 template "+name)
        coeff=np.mean(transformed[mask],axis=0)
        templates[name]=coeff
        rows.append(dict(template=name,source_n=int(mask.sum()),
            source_20k_sha256_model="G12-eight-original-SHA",
            original_model_source_scale="mean log aquatic frog cohort",
            coefficient_OS=float(coeff[0]),coefficient_OV=float(coeff[1]),
            coefficient_SV=float(coeff[2]),coefficient_OSV=float(coeff[3])))
    require(tuple(templates)==TEMPLATES,"G14 source template order changed")
    return templates,pd.DataFrame(rows),receipt

def read_field():
    require(sha(SITE)==FIELD_SOURCE_SHA["site"]
            and sha(VISITS)==FIELD_SOURCE_SHA["visits"],
            "G14 field site or original visit file SHA changed")
    sites=pd.read_csv(SITE)
    visits=pd.read_csv(VISITS)
    d=prepare_sites(sites,visits,expected_sites=N_SITE)
    require(d.site.is_unique and len(d)==N_SITE
            and d.n.sum()==N_VISITS and d.k.sum()==N_STRONG
            and d.V.sum()==N_VEG
            and d.route.nunique()==N_ROUTE
            and d.spatial_block.nunique()==N_BLOCK,
            "G14 R1 original field cohort or call outcome changed")
    folds=assign_spatial_folds(d)
    require(set(folds)==set(range(N_FOLD)) and
            d.assign(fold=folds).groupby("spatial_block").fold.nunique().eq(1).all(),
            "Leaked original geographic block across folds")
    return d,folds

def predictor_templates(d,background,source):
    designs=design_matrices(d,background)
    o=original_rank01(d["mean_suitability_Odonata_"+background])
    s=original_rank01(d["mean_suitability_pond_breeding_Caudata_"+background])
    v=d.V.to_numpy(float)
    target=predictor_basis(o,s,v)[:,4:]
    require(np.linalg.matrix_rank(target)==4,
            "G14 O/S/V interactions lack original rank")
    features={}
    maximal_span=np.column_stack((np.ones(len(d)),designs["env_all"]))
    for name,coefs in source.items():
        phi=target@coefs
        require(np.isfinite(phi).all() and np.std(phi)>1e-8,
                "Degenerate fixed G14 synthetic interaction template: "+name)
        # G4 source-span invariant: no extra identifiable field variable.
        projection=np.linalg.lstsq(maximal_span,phi,rcond=None)[0]
        error=float(np.max(np.abs(maximal_span@projection-phi)))
        require(error<1e-8,
                "Original synthetic source signal outside saturated empirical 4 interaction terms")
        features[name]=phi
    return designs,features

def heldout(d,folds,templates):
    allrows=[];slopes=[]
    k=d.k.to_numpy(dtype=int)
    n=d.n.to_numpy(dtype=int)
    for background in BACKGROUNDS:
        matrices,features=predictor_templates(d,background,templates)
        for fold in range(N_FOLD):
            test=folds==fold
            train=~test
            require(train.sum()>2000 and test.sum()>100,
                    "G14 originally fixed heldout support missing")
            ix=np.flatnonzero(test)
            for name in BASELINES+TEMPLATES:
                if name in BASELINES:
                    X=matrices[name]
                    fit=train_predict(X[train],k[train],n[train],X[test],ridge=RIDGE)
                    slope=np.nan
                else:
                    X=np.column_stack((matrices["flex_add"],features[name]))
                    fit,slope=constrained_train_predict(X[train],k[train],n[train],
                                                      X[test],ridge=RIDGE)
                    require(slope>=-1e-12,
                            "G14 fixed nonnegative source slope violated")
                rows=pd.DataFrame(dict(
                    site=d.site.iloc[ix].to_numpy(),
                    route=d.route.iloc[ix].to_numpy(),
                    spatial_block=d.spatial_block.iloc[ix].to_numpy(),
                    fold=fold,background=background,candidate=name,
                    k_strong=k[ix],n_completed=n[ix],predicted=fit))
                allrows.append(rows)
                slopes.append(dict(background=background,fold=fold,candidate=name,
                    train_original_sites=int(train.sum()),test_original_sites=int(test.sum()),
                    source_beta=slope,
                    source_sign_constrained=name in TEMPLATES))
    predictions=pd.concat(allrows,ignore_index=True)
    fitinfo=pd.DataFrame(slopes)
    require(len(predictions)==N_SITE*len(BACKGROUNDS)*(len(BASELINES)+len(TEMPLATES))
            and len(fitinfo)==N_FOLD*len(BACKGROUNDS)*(len(BASELINES)+len(TEMPLATES))
            and not predictions.duplicated(["site","background","candidate"]).any(),
            "G14 5fold adult acoustic predictions lost original sites")
    require(predictions.groupby(["background","candidate"]).site.nunique().eq(N_SITE).all()
            and predictions.groupby(["background","candidate"]).n_completed.sum().eq(N_VISITS).all(),
            "G14 field totals changed in original block heldouts")
    return predictions,fitinfo

def score(predictions):
    p=predictions.copy()
    p["loss"]=log_score(p.k_strong,p.n_completed,p.predicted)
    score=p.groupby(["background","candidate"],sort=True).agg(
        sites=("site","nunique"),blocks=("spatial_block","nunique"),
        completed_visits=("n_completed","sum"),strong_events=("k_strong","sum"),
        total_nll=("loss","sum")).reset_index()
    score["nll_per_visit"]=score.total_nll/score.completed_visits
    require(score.completed_visits.eq(N_VISITS).all()
            and score.strong_events.eq(N_STRONG).all()
            and score.blocks.eq(N_BLOCK).all(),
            "G14 original NAAMP heldout scoring denominators incorrect")
    return p,score

def contrasts(predictions):
    groups=predictions.groupby(["background","candidate","spatial_block"],sort=True).agg(
        loss=("loss","sum"),visits=("n_completed","sum")).reset_index()
    source=[]
    rng=np.random.default_rng(SEED)
    ix=rng.integers(0,N_BLOCK,size=(N_BOOT,N_BLOCK))
    for background in BACKGROUNDS:
        q=groups[groups.background==background]
        blocks=sorted(q.spatial_block.unique())
        require(len(blocks)==N_BLOCK,"G14 fewer than 56 blocks")
        for base in BASELINES:
            original=q[q.candidate==base].set_index("spatial_block").loc[blocks]
            for name in TEMPLATES:
                compare=q[q.candidate==name].set_index("spatial_block").loc[blocks]
                require(np.array_equal(original.visits,compare.visits),
                        "G14 paired spatial holdout visits changed")
                numerator=(original.loss-compare.loss).to_numpy(float)
                visits=original.visits.to_numpy(float)
                bs=numerator[ix].sum(axis=1)/visits[ix].sum(axis=1)
                lo,hi=np.quantile(bs,[.025,.975])
                source.append(dict(background=background,
                    comparison=f"{base}_minus_{name}",
                    baseline=base,mechanism=name,
                    gain_nll_per_visit=float(numerator.sum()/visits.sum()),
                    block_bootstrap95_low=float(lo),block_bootstrap95_high=float(hi),
                    source_blocks=N_BLOCK,original_visits=N_VISITS,
                    bootstrap=N_BOOT,bootstrap_seed=SEED))
    return pd.DataFrame(source)

def run(out=OUT):
    out=Path(out)
    source,source_coefs,old=read_original_20k()
    d,folds=read_field()
    predictions,slopes=heldout(d,folds,source)
    withloss,scores=score(predictions)
    compared=contrasts(withloss)
    primary=compared[(compared.baseline=="flex_add")&
                     (compared.mechanism=="ABC_accepted")]
    unrestricted=compared[(compared.baseline=="flex_all")&
                          (compared.mechanism=="ABC_accepted")]
    require(len(primary)==len(unrestricted)==2 and
            set(primary.background)==set(BACKGROUNDS),
            "G14 pre-fixed dual-background comparison lost")
    gate={
        "improves_flexible_environment_additive_in_both_backgrounds":
          bool(primary.block_bootstrap95_low.gt(0).all()),
        "beats_unrestricted_four_interactions_in_both_backgrounds":
          bool(unrestricted.block_bootstrap95_low.gt(0).all()),
    }
    gate["joint_strong_predictive_compatibility"]=all(gate.values())
    out.mkdir(parents=True,exist_ok=True)
    files={
        "G14_original_ABC_source_templates.csv":source_coefs,
        "G14_5fold_source_slope_fits.csv":slopes,
        "G14_original_acoustic_NLL_scores.csv":scores,
        "G14_block_paired_all_source_template_competitions.csv":compared,
    }
    for name,frame in files.items():
        frame.to_csv(out/name,index=False)
    outfile=out/"G14_all_4248_heldout_site_predictions.csv.gz"
    withloss.to_csv(outfile,index=False,compression={"method":"gzip","mtime":0})
    receipt=dict(
        status="G14_ORIGINAL_ABC_ENSEMBLE_GEOGRAPHIC_ACOUSTIC_HOLDOUT_SOURCE_AUDIT_PASS",
        original_source_R2_run=41262102436,
        original_R2_source_shard_sha256=old["original_shard_sha256"],
        original_model_kernel_sha="5e2f0a87c639df373fa2700b29403d2ab417a1cc",
        field_sites=N_SITE,field_visits=N_VISITS,field_strong_events=N_STRONG,
        field_routes=N_ROUTE,geographic_blocks=N_BLOCK,original_folds=N_FOLD,
        field_original_data_sha256=FIELD_SOURCE_SHA,
        original_ABC_proposals=20000,
        original_ABC_accepted=794,
        original_ABC_accepted_viable=426,
        original_ABC_rejected=19206,
        source_templates=list(TEMPLATES),
        original_SDM_backgrounds=list(BACKGROUNDS),
        source_predictor_in_saturated_interaction_span=True,
        model_source_slope_nonnegative_training_only=True,
        original_field_target_not_independently_discovered=True,
        comparison_gates=gate,
        source_bootstrap_block_draws=N_BOOT,
        source_file_sha256={path.name:sha(path) for path in sorted(out.iterdir()) if path.is_file()},
        no_new_field_observations=True,
        no_natural_predator_mechanism_identification=True,
        no_empirical_ABC_posterior=True,
    )
    (out/"G14_source_holds_and_claim_limits.json").write_text(
        json.dumps(receipt,indent=2)+"\n")
    print("G14_ABC_POM_FIELD_BRIDGE "+json.dumps({
        "status":receipt["status"],
        "comparison_gates":gate,
        "primary":primary.to_dict("records"),
        "unrestricted":unrestricted.to_dict("records"),
    }),flush=True)
    return receipt

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",type=Path,default=OUT)
    args=ap.parse_args()
    run(args.out)
