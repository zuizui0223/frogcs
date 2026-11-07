"""G15: rate×context-conditioned source-acceptance null vs ABC and sign-only field predictor.

Pre-frozen before G15 outcomes; never treats adult calling as a calibrated
likelihood for wild predator mechanisms. Four source shards processed with
identical original G14 field folds, ridge and constrained observation link.
"""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
import numpy as np
import pandas as pd
from acoustic_mechanism_cv import BACKGROUNDS,RIDGE,train_predict,log_score
from g14_abc_ensemble_geographic_acoustic_holdout import (
    original_four_interaction_coefficients,read_field,predictor_templates,
    constrained_train_predict,read_original_20k,N_SITE,N_VISITS,N_BLOCK,
)
from g13_abc_pom_conditional_structure_null import read_source,build_strata
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/"research/results/g15_abc_acoustic_specificity_20261107"
ORIGINAL=ROOT/"research/results/g14_abc_pom_field_ensemble_20261107"
REP=199
SEED=20261108
SHARDS=4
MODELS=("ABC_794","SIGN_ONLY")

def require(ok,message):
    if not bool(ok):raise AssertionError(message)

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def freeze_source(out):
    d,accepted,_,receipt=read_source(ROOT/"research/results/g12_abc_pom_prior_20261107")
    require(accepted.sum()==794 and len(d)==20000,"G15 original source model draw drift")
    z=d[["log_OS","log_OV","log_SV","log_OSV"]].to_numpy(float)
    coef=original_four_interaction_coefficients(z)
    observed=coef[accepted].mean(axis=0)
    expected=pd.read_csv(ORIGINAL/"G14_original_ABC_source_templates.csv")
    original=expected[expected.template=="ABC_accepted"]
    require(len(original)==1 and original.source_n.iloc[0]==794,
            "G14 original ABC accepted source count drift")
    ground=original.iloc[0][["coefficient_OS","coefficient_OV","coefficient_SV","coefficient_OSV"]].to_numpy(float)
    require(np.max(np.abs(observed-ground))<1e-12,"G14 original 794 model template changed")
    _,indices,ks=build_strata(d,accepted)
    rng=np.random.default_rng(SEED)
    rows=[]
    for j in range(REP):
        sample=np.concatenate([
          rng.choice(ix,size=int(k),replace=False) for ix,k in zip(indices,ks) if k>0])
        require(len(sample)==794 and len(set(sample))==794,"Lost within-stratum 794 proposals")
        vec=coef[sample].mean(axis=0)
        rows.append((f"STRAT_NULL_{j:03d}",j,794,*vec))
    signed=original_four_interaction_coefficients(
        np.array([[-1.,-1.,1.,1.]]))[0]
    rows.extend([("ABC_794",-1,794,*observed),("SIGN_ONLY",-2,0,*signed)])
    names=("candidate","null_id","model_draws","coefficient_OS","coefficient_OV","coefficient_SV","coefficient_OSV")
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    f=out/"g15_frozen_model_source_templates.csv"
    pd.DataFrame(rows,columns=names).to_csv(f,index=False)
    info=dict(status="G15_SOURCE_TEMPLATES_FROZEN_BEFORE_NEW_FIELD_FITS",
      original_accepted=794,original_proposed=20000,original_rate_context_strata=81,
      original_ABC_source_shape_replay_max_abs=float(np.max(np.abs(observed-ground))),
      frozen_null_count=REP,seed=SEED,reference_SHA256=receipt["original_shard_sha256"],
      field_evidence_not_used_in_null_selection=True,
      original_ABCG14_source_shape_reproduced=True,
      template_file_sha256=sha(f))
    (out/"g15_source_template_receipt.json").write_text(json.dumps(info,indent=2)+"\n")
    print("G15_FROZEN_199_NULLS",json.dumps({k:info[k] for k in ("status","frozen_null_count","template_file_sha256")}))
    return info

def read_templates(src):
    src=Path(src)
    info=json.loads((src/"g15_source_template_receipt.json").read_text())
    csv=src/"g15_frozen_model_source_templates.csv"
    require(sha(csv)==info["template_file_sha256"],"G15 frozen source template archive altered")
    t=pd.read_csv(csv)
    require(len(t)==REP+2 and t.candidate.is_unique and
            set(t.null_id)==set(range(REP))|{-1,-2},"Missing original null catalog")
    return t,info

def shard_run(source,out,shard):
    require(0<=shard<SHARDS,"Invalid G15 null shard ID")
    t,source_receipt=read_templates(source)
    ids=tuple(range(shard,REP,SHARDS))
    subset=t[t.null_id.isin(ids)].copy()
    if shard==0:
        subset=pd.concat([subset,t[t.candidate.isin(MODELS)]],ignore_index=True)
    require(len(subset)==len(ids)+(2 if shard==0 else 0),
            "Incomplete fixed null shard assignment")
    templates={row.candidate:np.array([row.coefficient_OS,row.coefficient_OV,row.coefficient_SV,row.coefficient_OSV])
               for row in subset.itertuples(index=False)}
    d,folds=read_field()
    k=d.k.to_numpy(int)
    n=d.n.to_numpy(int)
    output=[];fitted=[]
    for background in BACKGROUNDS:
        matrices,features=predictor_templates(d,background,templates)
        env=matrices["flex_add"]
        # The original source model may be near-degenerate for a stochastic null.
        # In that case use the independently refitted flex_add baseline, never
        # drop the null or replace it with another source template.
        for fold in range(5):
            train=folds!=fold;test=~train
            ix=np.flatnonzero(test)
            baseline_pred=train_predict(env[train],k[train],n[train],env[test],ridge=RIDGE)
            for name,phi in features.items():
                degenerate=bool(np.std(phi[train])<=1e-8)
                if degenerate:
                    prediction=baseline_pred.copy()
                    slope=0.
                else:
                    x=np.column_stack((env,phi))
                    prediction,slope=constrained_train_predict(x[train],k[train],n[train],x[test],ridge=RIDGE)
                losses=log_score(k[ix],n[ix],prediction)
                require(np.isfinite(losses).all() and slope>=-1e-12,"Undefined G15 null model prediction")
                output.append(pd.DataFrame(dict(candidate=name,
                    background=background,fold=fold,
                    site=d.site.iloc[ix].to_numpy(),
                    spatial_block=d.spatial_block.iloc[ix].to_numpy(),
                    n_completed=n[ix],k_strong=k[ix],
                    predicted=prediction,loss=losses)))
                fitted.append(dict(candidate=name,background=background,fold=fold,
                    slope=slope,degenerate_source_shape=degenerate,
                    trained_sites=int(train.sum()),tested_sites=int(test.sum())))
    df=pd.concat(output,ignore_index=True)
    require(len(df)==len(subset)*len(BACKGROUNDS)*N_SITE
            and not df.duplicated(["candidate","background","site"]).any(),
            "G15 null field source prediction rows incomplete")
    original=pd.read_csv(ORIGINAL/"G14_original_acoustic_NLL_scores.csv")
    if shard==0:
        for bg in BACKGROUNDS:
            a=df[(df.candidate=="ABC_794")&(df.background==bg)]
            b=original[(original.background==bg)&(original.candidate=="ABC_accepted")]
            actual=float(a.loss.sum()/N_VISITS)
            expected=float(b.nll_per_visit.iloc[0]) if len(b)==1 else float("nan")
            oldsite=pd.read_csv(
                ORIGINAL/"G14_all_4248_heldout_site_predictions.csv.gz")
            oldsite=oldsite[(oldsite.background==bg)&
                            (oldsite.candidate=="ABC_accepted")].set_index("site")
            aa=a.set_index("site")
            require(len(oldsite)==len(aa)==N_SITE and
                    oldsite.index.is_unique and aa.index.is_unique and
                    set(oldsite.index)==set(aa.index),
                    "G14 and G15 acoustic response source site IDs differ")
            oldsite=oldsite.reindex(aa.index)
            require(np.array_equal(oldsite.n_completed,aa.n_completed) and
                    np.array_equal(oldsite.k_strong,aa.k_strong) and
                    np.array_equal(oldsite.spatial_block,aa.spatial_block),
                    "G14 and G15 acoustic source visits, events or blocks differ")
            max_pred_abs=float(np.max(np.abs(
                oldsite.predicted.to_numpy(float)-aa.predicted.to_numpy(float))))
            print("G15_G14_ORIGINAL_ABC_NUMERICAL_REPLAY",bg,
                  {"actual_NLL":actual,"expected_NLL":expected,
                   "absolute_NLL_difference":abs(actual-expected),
                   "max_absolute_probability_difference":max_pred_abs,
                   "sites":len(aa)},flush=True)
            # The actual source and field records are byte-identical.
            # L-BFGS-B can take a slightly different convergence path with
            # otherwise equivalent input matrix assembly; this is a
            # numerical replay safeguard, not a new scientific effect gate.
            require(len(b)==1 and abs(actual-expected)<1e-6 and
                    max_pred_abs<1e-4,
                    "G14 ABC source acoustic predictions diverge beyond the "
                    "declared numerical replay tolerance: "+bg+
                    f" NLL_delta={actual-expected:.5g} p_max_delta={max_pred_abs:.5g}")
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    name=f"g15_predictive_null_shard_{shard:02d}"
    site=out/(name+"_full_site.csv.gz")
    df.to_csv(site,index=False,compression={"method":"gzip","mtime":0})
    slopes=out/(name+"_train_slopes.csv")
    pd.DataFrame(fitted).to_csv(slopes,index=False)
    agg=(df.groupby(["candidate","background","spatial_block"],sort=True)
          .agg(total_loss=("loss","sum"),original_visits=("n_completed","sum"),
               strong_calls=("k_strong","sum"),sites=("site","size")).reset_index())
    blocks=out/(name+"_56blocks.csv")
    agg.to_csv(blocks,index=False)
    receipt=dict(status="G15_ORIGINAL_FIELD_SOURCE_NULL_SHARD_SUCCESS",
       shard=shard,nshards=SHARDS,null_ids=list(ids),
       with_ABC_and_signonly_controls=shard==0,
       fixed_source_templates_SHA=source_receipt["template_file_sha256"],
       site_rows=len(df),fitted_models=len(subset),
       n_field_sites=N_SITE,n_field_visits=N_VISITS,
       full_original_site_outcome_scores=True,
       outcome_selected_nulls=False,
       files_sha256={p.name:sha(p) for p in (site,slopes,blocks)})
    (out/(name+"_receipt.json")).write_text(json.dumps(receipt,indent=2)+"\n")
    print("G15_FIELD_NULL_SHARD "+json.dumps({k:receipt[k] for k in ("status","shard","site_rows","fitted_models")}))
    return receipt

def aggregate(src,shards,out):
    t,source_info=read_templates(src)
    shards=Path(shards);out=Path(out)
    full=[];all_slopes=[];all_blocks=[]
    for shard in range(SHARDS):
        name=f"g15_predictive_null_shard_{shard:02d}"
        p=shards/(name+"_receipt.json")
        require(p.is_file(),"Missing G15 null shard receipt "+name)
        info=json.loads(p.read_text())
        ids=list(range(shard,REP,SHARDS))
        require(info["status"]=="G15_ORIGINAL_FIELD_SOURCE_NULL_SHARD_SUCCESS"
                and info["fixed_source_templates_SHA"]==source_info["template_file_sha256"]
                and info["null_ids"]==ids and info["shard"]==shard,
                "G15 null shard source pairing/selection drift")
        for n,digest in info["files_sha256"].items():
            require(sha(shards/n)==digest,"G15 original per-site score SHA changed "+n)
        site=pd.read_csv(shards/(name+"_full_site.csv.gz"))
        require(len(site)==info["site_rows"],"Missing original G15 site-level scoring")
        p=site.predicted.to_numpy(float)
        k=site.k_strong.to_numpy(float);n=site.n_completed.to_numpy(float)
        actual=-(k*np.log(p)+(n-k)*np.log1p(-p))
        require(np.max(abs(actual-site.loss.to_numpy(float)))<1e-11,
                "G15 independent binomial site-level NLL check failed")
        full.append(site)
        all_slopes.append(pd.read_csv(shards/(name+"_train_slopes.csv")))
        all_blocks.append(pd.read_csv(shards/(name+"_56blocks.csv")))
    predictions=pd.concat(full,ignore_index=True)
    require(predictions.candidate.nunique()==REP+2
            and len(predictions)==(REP+2)*2*N_SITE
            and not predictions.duplicated(["candidate","background","site"]).any(),
            "G15 original 201 templates × all 4248 acoustic sites incomplete")
    source_slopes=pd.concat(all_slopes,ignore_index=True)
    blocks=pd.concat(all_blocks,ignore_index=True)
    require(len(source_slopes)==(REP+2)*2*5 and
            len(blocks)==(REP+2)*2*56,
            "G15 original fixed 5-fold/56-block support lost")
    means=(blocks.groupby(["candidate","background"],sort=True)
          .agg(loss=("total_loss","sum"),visits=("original_visits","sum"),
               strong=("strong_calls","sum"),blocks=("spatial_block","nunique")).reset_index())
    require(len(means)==(REP+2)*2 and means.visits.eq(N_VISITS).all()
            and means.strong.eq(36554).all()
            and means.blocks.eq(56).all(),
            "G15 complete source geographic denominators changed")
    means["NLL_per_visit"]=means.loss/means.visits
    results=[];nulls=[]
    oldscores=pd.read_csv(ORIGINAL/"G14_original_acoustic_NLL_scores.csv")
    for bg in BACKGROUNDS:
        m=means[means.background==bg].set_index("candidate")
        abc=float(m.loc["ABC_794","NLL_per_visit"])
        sign=float(m.loc["SIGN_ONLY","NLL_per_visit"])
        old=oldscores[(oldscores.background==bg)&(oldscores.candidate=="ABC_accepted")].iloc[0]
        require(abs(abc-old.nll_per_visit)<1e-6,
                "ABC G14 heldout NLL drift exceeds numerical tolerance "+bg)
        originals=pd.read_csv(ORIGINAL/"G14_original_acoustic_NLL_scores.csv")
        env=float(originals[(originals.background==bg)&(originals.candidate=="flex_add")].nll_per_visit.iloc[0])
        unrestricted=float(originals[(originals.background==bg)&(originals.candidate=="flex_all")].nll_per_visit.iloc[0])
        nullvalues=np.array([float(m.loc[f"STRAT_NULL_{j:03d}","NLL_per_visit"]) for j in range(REP)])
        p=float((1+np.sum(nullvalues<=abc))/(REP+1))
        lower,upper=np.quantile(nullvalues,[.025,.975])
        rows=dict(background=bg,accepted_ABC_NLL=abc,
                  signonly_NLL=sign,flex_add_NLL=env,flex_all_NLL=unrestricted,
                  ABC_minus_signonly_NLL=abc-sign,
                  signonly_minus_ABC_NLL=sign-abc,
                  null_mean_NLL=float(nullvalues.mean()),
                  null_median_NLL=float(np.median(nullvalues)),
                  null_95_low_NLL=float(lower),null_95_high_NLL=float(upper),
                  null_NLL_less_or_equal_ABC=int(np.sum(nullvalues<=abc)),
                  empirical_upper_tail_p=p,permutations=REP,
                  source_selection_specific_ABC_better_signonly=bool(abc<sign),
                  conditional_null_p_le_005=bool(p<=.05),
                  original_G14_primary_gain=env-abc,
                  original_G14_unrestricted_gain=unrestricted-abc)
        results.append(rows)
        nulls.extend(dict(background=bg,null_id=j,
                          NLL_per_visit=nullvalues[j],ABC_NLL_per_visit=abc,
                          null_minus_ABC_gain=nullvalues[j]-abc) for j in range(REP))
    result=pd.DataFrame(results)
    result["source_specificity_both_backgrounds"]=(result.source_selection_specific_ABC_better_signonly &
                                                    result.conditional_null_p_le_005)
    joint=bool(result.source_specificity_both_backgrounds.all())
    out.mkdir(parents=True,exist_ok=True)
    tables={
       "G15_199_rate_context_null_template_field_scores.csv":pd.DataFrame(nulls),
       "G15_G14_signonly_vs_ABC_null_comparison.csv":result,
       "G15_all_null_fold_source_slopes.csv":source_slopes,
       "G15_all_null_56block_losses.csv":blocks,
       "G15_frozen_source_templates.csv":t,
    }
    for name,frame in tables.items():frame.to_csv(out/name,index=False)
    receipt=dict(status="G15_199_RATE_CONTEXT_NULL_ACOUSTIC_FIELD_SOURCE_COMPLETE",
       source_template_sha256=source_info["template_file_sha256"],
       G14_accepted_794_reproduced=True,
       original_G14_NLL_replay_error_by_background={
           row["background"]:abs(float(row["accepted_ABC_NLL"])-
               float(oldscores[(oldscores.background==row["background"])&
                    (oldscores.candidate=="ABC_accepted")].nll_per_visit.iloc[0]))
           for row in results},
       declared_NLL_numerical_tolerance=1e-6,
       declared_probability_numerical_tolerance=1e-4,
       original_G14_dual_background_field_gate_pass=False,
       original_G14_unrestricted_interaction_gate_pass=False,
       source_specificity_fixed_joint_gate_pass=joint,
       original_G14_artifact_source_outcomes_not_refitted=True,
       null_rate_context_strata=81,null_replicates=REP,original_source_accepted=794,
       templates_total=REP+2,field_SDM_backgrounds=2,field_sites=N_SITE,
       source_shards=SHARDS,original_original_site_scores=len(predictions),
       original_field_sites=N_SITE,original_surveys=N_VISITS,geographic_blocks=N_BLOCK,
       no_biological_reruns=True,not_independent_field_observations=True,
       no_wild_trophic_mechanism_identified=True,no_empirical_ABC_posterior=True,
       file_sha256={name:sha(out/name) for name in tables},
       source_G14_sha256=sha(ORIGINAL/"G14_source_holds_and_claim_limits.json"))
    (out/"G15_full_source_audit_receipt.json").write_text(json.dumps(receipt,indent=2)+"\n")
    print("G15_ALL_199_CONDITIONED_FIELD_NULLS "+json.dumps({
        "joint_gate":joint,"by_background":results,
        "site_original_count":len(predictions)}),flush=True)
    return receipt

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--stage",required=True,choices=["prepare","shard","aggregate"])
    ap.add_argument("--source",type=Path,default=OUT/"preflight")
    ap.add_argument("--shards",type=Path,default=OUT/"shards")
    ap.add_argument("--out",type=Path,default=OUT/"audited")
    ap.add_argument("--shard",type=int)
    a=ap.parse_args()
    if a.stage=="prepare":freeze_source(a.out)
    elif a.stage=="shard":
        require(a.shard is not None,"Shard index missing")
        shard_run(a.source,a.out,a.shard)
    else:aggregate(a.source,a.shards,a.out)
