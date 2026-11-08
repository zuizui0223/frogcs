"""G17 original G15 accepted/null field source: 2x2 SDM env/main × source rank swap.

201 frozen original G15 source templates (794 accepted + SIGN_ONLY + 199
conditional nulls), two environment main-effect designs × two source-rank
designs, exactly original NAAMP 4248 sites/56 geographical blocks/5 folds.
Post-hoc model-specification diagnostic; no field posterior or biological model.
"""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path

import numpy as np
import pandas as pd

from acoustic_mechanism_cv import BACKGROUNDS,RIDGE,log_score
from g1_shared_environment_spatial_block import design_matrices
from g4_field_model_alignment_8corner_audit_20261106 import original_rank01,predictor_basis
from g5_source_constrained_acoustic_holdout_20261106 import constrained_train_predict
from g14_abc_ensemble_geographic_acoustic_holdout import (
    read_field,predictor_templates,N_SITE,N_VISITS,N_STRONG,N_FOLD,N_BLOCK,
)
from g15_abc_selection_specificity_holdout import (
    G15 as SOURCE_DIR,REP as N_NULLS,SEED as ORIGINAL_NULL_SEED,
)

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/"research/results/g17_sdm_env_rank_crossswap_20261108"
N_TEMPLATES=N_NULLS+2
NSHARDS=4
BLOCK_BOOT=9999
BLOCK_SEED=20261108
ORIGINAL_G15_RUN=42379659618
ACCEPTED="ABC_794"
SIGN_ONLY="SIGN_ONLY"
FIELDS=("uniform","target_group")
PAIR_CELLS=tuple((env,rank) for env in FIELDS for rank in FIELDS)
SOURCE_TEMPLATE_COLUMNS=("coefficient_OS","coefficient_OV","coefficient_SV","coefficient_OSV")
N_EXPECTED=N_SITE*len(PAIR_CELLS)*N_TEMPLATES
NUMERIC_G15_NLL_TOL=1e-6
NUMERIC_G15_P_MAX_TOL=1e-4
NUMERIC_G15_BLOCK_LOSS_TOL=0.02

def require(ok,message):
    if not bool(ok):raise AssertionError(message)

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def frozen_templates():
    rec=json.loads((SOURCE_DIR/"G15_full_source_audit_receipt.json").read_text())
    require(rec["status"]=="G15_199_RATE_CONTEXT_NULL_ACOUSTIC_FIELD_SOURCE_COMPLETE"
           and rec["templates_total"]==N_TEMPLATES
           and rec["null_replicates"]==N_NULLS
           and rec["null_rate_context_strata"]==81
           and not rec["source_specificity_fixed_joint_gate_pass"],
           "G15 original 201-source metadata or negative gate changed")
    f=SOURCE_DIR/"G15_frozen_source_templates.csv"
    require(sha(f)==rec["file_sha256"][f.name],"G15 source coefficient SHA drift")
    t=pd.read_csv(f).sort_values("null_id",ascending=True).reset_index(drop=True)
    require(len(t)==N_TEMPLATES and t.candidate.is_unique
           and set(t.null_id)==set(range(N_NULLS))|{-1,-2}
           and t.query("null_id >= 0").model_draws.eq(794).all(),
           "Original 199 source-stratum nulls or accepted source classes changed")
    for m in (ACCEPTED,SIGN_ONLY):
        require((t.candidate==m).sum()==1,"ABC/sign-only G15 source missing")
    require(tuple(BACKGROUNDS)==FIELDS,"Original G14 SDM backgrounds changed")
    c=t[list(SOURCE_TEMPLATE_COLUMNS)].to_numpy(float)
    require(np.isfinite(c).all() and c.shape==(N_TEMPLATES,4),"Undefined model-source coefficient")
    return t,rec

def rank_basis(d,background):
    require(background in FIELDS,"Unknown source-rank SDM background")
    o=original_rank01(d["mean_suitability_Odonata_"+background])
    s=original_rank01(d["mean_suitability_pond_breeding_Caudata_"+background])
    v=d.V.to_numpy(float)
    basis=predictor_basis(o,s,v)[:,4:]
    require(basis.shape==(N_SITE,4) and np.linalg.matrix_rank(basis)==4,
            "Original rank-coded O/S/V source interactions drift")
    return basis

def split_templates(t,shard):
    require(0<=shard<NSHARDS,"Unknown original G17 source template shard")
    null_ids=tuple(range(shard,N_NULLS,NSHARDS))
    selection=t[t.null_id.isin(null_ids)].copy()
    if shard==0:
        selection=pd.concat([selection,t[t.candidate.isin((ACCEPTED,SIGN_ONLY))]],
                            ignore_index=True)
    require(len(selection)==len(null_ids)+(2 if shard==0 else 0),
            "Incomplete 199 original source assignments")
    return selection,null_ids

def run_shard(shard,out):
    templates,source_receipt=frozen_templates()
    chosen,null_ids=split_templates(templates,shard)
    d,folds=read_field() # original source-locked 4248 site / 63180 visit / 56 block
    require(len(d)==N_SITE and len(folds)==N_SITE
            and d.site.is_unique and d.n.sum()==N_VISITS
            and d.k.sum()==N_STRONG and d.spatial_block.nunique()==N_BLOCK
            and d.assign(fold=folds).groupby("spatial_block").fold.nunique().eq(1).all(),
            "G17 original geographic source or complete cohort drift")
    k=d.k.to_numpy(dtype=int)
    n=d.n.to_numpy(dtype=int)
    source_coeff=chosen[list(SOURCE_TEMPLATE_COLUMNS)].to_numpy(float)
    require(np.isfinite(source_coeff).all(),"Nonfinite original source coefficient")
    envs={e:design_matrices(d,e)["flex_add"] for e in FIELDS}
    ranks={r:rank_basis(d,r) for r in FIELDS}
    # Ensure original diagonal source response columns are exactly G14
    # before opening any cross-swapped field outcomes.
    if shard==0:
        abc=chosen[chosen.candidate==ACCEPTED]
        require(len(abc)==1,"ABC control not in G17 original shard0")
        coeff=abc[list(SOURCE_TEMPLATE_COLUMNS)].to_numpy(float).reshape(4)
        for b in FIELDS:
            _,replayed=predictor_templates(d,b,{ACCEPTED:coeff})
            diff=float(np.max(abs(replayed[ACCEPTED]-ranks[b]@coeff)))
            require(diff<1e-12,"Original G14/G15 source signal mismatch "+b)
    result=[];fitinfo=[]
    for e,r in PAIR_CELLS:
        env=envs[e]
        # Original fixed source-shape 4 coefficients × original rank interactions.
        allphi=ranks[r]@source_coeff.T
        require(allphi.shape==(N_SITE,len(chosen)) and np.isfinite(allphi).all(),
                "G17 source rank cross-swap feature null or incomplete")
        for fold in range(N_FOLD):
            mask=folds==fold;train=~mask
            require(train.sum()>2000 and mask.sum()>100,"G17 original heldout support lost")
            ix=np.flatnonzero(mask)
            for ci,row in enumerate(chosen.itertuples(index=False)):
                phi=allphi[:,ci]
                # A non-finite or degenerate template is a failed source gate.
                require(np.std(phi[train])>1e-8,
                        "G17 source rank interaction degenerate "+row.candidate)
                X=np.column_stack((env,phi))
                prediction,slope=constrained_train_predict(
                    X[train],k[train],n[train],X[mask],ridge=RIDGE)
                require(slope>=-1e-12 and np.isfinite(prediction).all()
                        and np.all((prediction>0)&(prediction<1)),
                        "G17 original constrained source fit failed "+row.candidate)
                l=log_score(k[ix],n[ix],prediction)
                require(np.isfinite(l).all(),"G17 field binomial loss nonfinite")
                result.append(pd.DataFrame({
                    "candidate":row.candidate,"env_bg":e,"rank_bg":r,
                    "site":d.site.iloc[ix].to_numpy(),
                    "spatial_block":d.spatial_block.iloc[ix].to_numpy(),
                    "fold":fold,"n_completed":n[ix],"k_strong":k[ix],
                    "predicted":prediction,"loss":l,
                }))
                fitinfo.append(dict(candidate=row.candidate,env_bg=e,rank_bg=r,fold=fold,
                                    source_slope=float(slope),n_train=int(train.sum()),
                                    n_test=int(mask.sum())))
    site=pd.concat(result,ignore_index=True)
    fit=pd.DataFrame(fitinfo)
    require(len(site)==len(chosen)*len(PAIR_CELLS)*N_SITE
            and len(fit)==len(chosen)*len(PAIR_CELLS)*N_FOLD
            and not site.duplicated(["candidate","env_bg","rank_bg","site"]).any(),
            "G17 incomplete site/template/cross-cell recording")
    block=(site.groupby(["candidate","env_bg","rank_bg","spatial_block"],sort=True)
           .agg(total_loss=("loss","sum"),visits=("n_completed","sum"),
                strong_events=("k_strong","sum"),sites=("site","size")).reset_index())
    require(len(block)==len(chosen)*len(PAIR_CELLS)*N_BLOCK,
            "G17 original 56 geographic blocks missing")
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    lab=f"G17_source_crossswap_{shard:02d}"
    gz={"method":"gzip","mtime":0}
    fn=out/(lab+"_sites.csv.gz")
    bf=out/(lab+"_blocks.csv")
    sf=out/(lab+"_slopes.csv")
    site.to_csv(fn,index=False,compression=gz)
    block.to_csv(bf,index=False)
    fit.to_csv(sf,index=False)
    receipt=dict(
        status="G17_ALL_SOURCE_2X2_ORIGINAL_NAAMP_SHARD_SUCCESS",
        shard=shard,total_shards=NSHARDS,
        original_199_null_ids=list(null_ids),
        source_controls_present=shard==0,
        G15_frozen_source_SHA=source_receipt["file_sha256"][
            "G15_frozen_source_templates.csv"],
        pair_cells=[list(x) for x in PAIR_CELLS],
        original_sites=N_SITE,original_visits=N_VISITS,geographic_blocks=N_BLOCK,
        source_templates=len(chosen),site_rows=len(site),
        folds=len(fit),block_records=len(block),
        no_new_biological_simulation=True,no_wild_field_mechanism_validation=True,
        files_sha256={p.name:sha(p) for p in (fn,bf,sf)},
    )
    (out/(lab+"_receipt.json")).write_text(json.dumps(receipt,indent=2)+"\n")
    print("G17_2X2_SOURCE_SHARD "+json.dumps({
        "status":receipt["status"],"shard":shard,
        "source_templates":len(chosen),"site_rows":len(site)}),flush=True)
    return receipt


def compare_with_original_g15(diagonal,original):
    """Verify per-site original G15 diagonal outcomes and all original 56-block scores."""
    prior=pd.concat([pd.read_csv(x) for x in sorted(Path(original).glob(
        "g15_predictive_null_shard_*_full_site.csv.gz"))],ignore_index=True)
    require(len(prior)==N_TEMPLATES*2*N_SITE
            and not prior.duplicated(["candidate","background","site"]).any(),
            "Original G15 artifact full-site cohort missing")
    frames=[]
    for bg in FIELDS:
        a=diagonal[(diagonal.env_bg==bg)&(diagonal.rank_bg==bg)].copy()
        b=prior[prior.background==bg].copy()
        require(len(a)==len(b)==N_TEMPLATES*N_SITE,
                "G17 original G15 diagonal source sample drift")
        cols=["candidate","site"]
        a=a.set_index(cols).sort_index()
        b=b.set_index(cols).sort_index()
        require(a.index.is_unique and a.index.equals(b.index),
                "G17 diagonal missing original G15 source template/site")
        for col in ("spatial_block","fold","n_completed","k_strong"):
            require(np.array_equal(a[col].to_numpy(),b[col].to_numpy()),
                    "G17 original G15 field outcomes or geography changed "+col)
        maxp=float(np.max(abs(a.predicted.to_numpy(float)-
                               b.predicted.to_numpy(float))))
        block_a=a.reset_index().groupby(["candidate","spatial_block"]).loss.sum()
        block_b=b.reset_index().groupby(["candidate","spatial_block"]).loss.sum()
        require(block_a.index.equals(block_b.index),"G17 original 56block source identity drift")
        maxblock=float(np.max(abs(block_a.to_numpy(float)-block_b.to_numpy(float))))
        agg_a=a.reset_index().groupby("candidate").agg(loss=("loss","sum"),n=("n_completed","sum"))
        agg_b=b.reset_index().groupby("candidate").agg(loss=("loss","sum"),n=("n_completed","sum"))
        require(agg_a.n.eq(N_VISITS).all() and agg_b.n.eq(N_VISITS).all(),
                "G17 source diagonal visits absent")
        max_nll=float(np.max(abs(agg_a.loss.to_numpy(float)/N_VISITS-
                                  agg_b.loss.to_numpy(float)/N_VISITS)))
        frames.append(dict(background=bg,n_source_templates=N_TEMPLATES,
                           n_original_sites=N_SITE,max_abs_probability=maxp,
                           max_abs_block_nll=maxblock,
                           max_abs_mean_nll_per_visit=max_nll,
                           numerical_source_replay_pass=(
                            maxp<NUMERIC_G15_P_MAX_TOL and
                            maxblock<NUMERIC_G15_BLOCK_LOSS_TOL and
                            max_nll<NUMERIC_G15_NLL_TOL)))
    checks=pd.DataFrame(frames)
    require(checks.numerical_source_replay_pass.all(),
            "G17 diagonal numerical replay exceeded frozen tolerance: "+
            checks.to_json(orient="records"))
    return checks


def compute_four_cell(block):
    """One ABC and 199 null NLL score per each of four fixed crossed cells."""
    require(len(block)==N_TEMPLATES*len(PAIR_CELLS)*N_BLOCK,
            "G17 block source grid incomplete")
    scores=(block.groupby(["candidate","env_bg","rank_bg"],sort=True)
            .agg(loss=("total_loss","sum"),visits=("visits","sum"),
                 strong=("strong_events","sum"),
                 blocks=("spatial_block","nunique")).reset_index())
    require(scores.visits.eq(N_VISITS).all() and scores.strong.eq(N_STRONG).all()
            and scores.blocks.eq(N_BLOCK).all(),"G17 original site totals changed")
    scores["NLL_per_visit"]=scores.loss/scores.visits
    rows=[]
    for env,rank in PAIR_CELLS:
        q=scores[(scores.env_bg==env)&(scores.rank_bg==rank)].set_index("candidate")
        require(len(q)==N_TEMPLATES,"G17 missing template in crossed cell")
        abc=float(q.loc[ACCEPTED,"NLL_per_visit"])
        sign=float(q.loc[SIGN_ONLY,"NLL_per_visit"])
        null=np.array([float(q.loc[f"STRAT_NULL_{j:03d}","NLL_per_visit"])
                       for j in range(N_NULLS)])
        wins=int((null<=abc).sum())
        rows.append(dict(env_bg=env,rank_bg=rank,
                         ABC_794_nll=abc,SIGN_ONLY_nll=sign,
                         mean199null_nll=float(null.mean()),
                         median199null_nll=float(np.median(null)),
                         null95_low_nll=float(np.quantile(null,.025)),
                         null95_high_nll=float(np.quantile(null,.975)),
                         source_nulls_better_or_equal_ABC=wins,
                         conditional_source_p=(1+wins)/(N_NULLS+1),
                         ABC_minus_null_gain=float(null.mean()-abc),
                         ABC_minus_SIGN_ONLY_gain=float(sign-abc),
                         original_site_visits=N_VISITS,
                         original_geographic_blocks=N_BLOCK))
    return scores,pd.DataFrame(rows)


def factorial(rows):
    q=rows.set_index(["env_bg","rank_bg"])
    def d(e,r):return float(q.loc[(e,r),"ABC_minus_null_gain"])
    uu,ut,tu,tt=(d("uniform","uniform"),d("uniform","target_group"),
                 d("target_group","uniform"),d("target_group","target_group"))
    e=.5*((uu-tu)+(ut-tt))
    r=.5*((uu-ut)+(tu-tt))
    d0=uu-tt
    i=uu-ut-tu+tt
    require(abs(e+r-d0)<1e-14,"G17 full 2x2 crossed source factor identity broken")
    return dict(original_diagonal_difference=d0,
                environment_main_effect=e,source_rank_main_effect=r,
                crossed_nonlinear_interaction=i,
                environment_fraction_of_signed_diagonal=e/d0 if d0 else np.nan,
                rank_fraction_of_signed_diagonal=r/d0 if d0 else np.nan,
                D_UU=uu,D_UT=ut,D_TU=tu,D_TT=tt)


def original_spatial_bootstrap(block):
    """Exactly paired 56-block resampling of all four background cross-swaps."""
    blockids=sorted(block.spatial_block.unique())
    require(len(blockids)==N_BLOCK,"Need all original 56 geographic blocks")
    x={}
    originalvisits=None
    for e,r in PAIR_CELLS:
        q=block[(block.env_bg==e)&(block.rank_bg==r)]
        w=q.pivot(index="spatial_block",columns="candidate",values="total_loss").loc[blockids]
        v=q.pivot(index="spatial_block",columns="candidate",values="visits").loc[blockids]
        require(len(w)==N_BLOCK and w.shape[1]==N_TEMPLATES,
                "G17 original 201 source 56-block lattice incomplete")
        r0=v[ACCEPTED].to_numpy(float)
        if originalvisits is None:originalvisits=r0
        require(np.array_equal(r0,originalvisits),"G17 mismatch source block weighting")
        abc=w[ACCEPTED].to_numpy(float)
        null=w[[f"STRAT_NULL_{j:03d}" for j in range(N_NULLS)]].to_numpy(float).mean(axis=1)
        x[(e,r)]=null-abc
    rng=np.random.default_rng(BLOCK_SEED)
    ids=rng.integers(0,N_BLOCK,size=(BLOCK_BOOT,N_BLOCK))
    visits=originalvisits[ids].sum(axis=1)
    u=x[("uniform","uniform")][ids].sum(axis=1)/visits
    v=x[("uniform","target_group")][ids].sum(axis=1)/visits
    w=x[("target_group","uniform")][ids].sum(axis=1)/visits
    z=x[("target_group","target_group")][ids].sum(axis=1)/visits
    estimates={
       "D_UU":u,"D_UT":v,"D_TU":w,"D_TT":z,
       "original_diagonal_difference":u-z,
       "environment_main_effect":.5*((u-w)+(v-z)),
       "source_rank_main_effect":.5*((u-v)+(w-z)),
       "crossed_nonlinear_interaction":u-v-w+z,
    }
    return estimates


def aggregate(source_shards,original_g15_shards,out):
    t,orig=frozen_templates()
    source_shards=Path(source_shards);out=Path(out)
    allsites=[];allblocks=[];slopes=[];original_sha=[]
    for shard in range(NSHARDS):
        tag=f"G17_source_crossswap_{shard:02d}"
        rece=source_shards/(tag+"_receipt.json")
        require(rece.is_file(),"G17 source shard is missing "+tag)
        r=json.loads(rece.read_text())
        chosen,ids=split_templates(t,shard)
        require(r["status"]=="G17_ALL_SOURCE_2X2_ORIGINAL_NAAMP_SHARD_SUCCESS"
                and r["shard"]==shard and r["total_shards"]==NSHARDS
                and r["original_199_null_ids"]==list(ids)
                and r["G15_frozen_source_SHA"]==orig["file_sha256"][
                    "G15_frozen_source_templates.csv"]
                and r["source_templates"]==len(chosen)
                and r["pair_cells"]==[list(x) for x in PAIR_CELLS],
                "G17 original source-shard identity changed "+tag)
        for name,digest in r["files_sha256"].items():
            require(sha(source_shards/name)==digest,
                    "G17 original source blob SHA drift "+name)
        f=source_shards/(tag+"_sites.csv.gz")
        site=pd.read_csv(f)
        require(len(site)==r["site_rows"] and
                len(site)==len(chosen)*len(PAIR_CELLS)*N_SITE and
                not site.duplicated(["candidate","env_bg","rank_bg","site"]).any(),
                "G17 source shard site rows incomplete "+tag)
        pred=site.predicted.to_numpy(float)
        K=site.k_strong.to_numpy(float)
        N=site.n_completed.to_numpy(float)
        require(np.isfinite(pred).all() and np.all((pred>0)&(pred<1)),
                "G17 source predictions outside original binomial likelihood")
        independently=-(K*np.log(pred)+(N-K)*np.log1p(-pred))
        require(np.max(abs(independently-site.loss.to_numpy(float)))<1e-11,
                "G17 original field source-binomial likelihood mismatch")
        blocks=pd.read_csv(source_shards/(tag+"_blocks.csv"))
        check=(site.groupby(["candidate","env_bg","rank_bg","spatial_block"],sort=True)
              .agg(loss=("loss","sum"),visits=("n_completed","sum")).reset_index())
        joined=blocks.merge(check,
           on=["candidate","env_bg","rank_bg","spatial_block"],validate="one_to_one")
        require(len(joined)==len(blocks)==r["block_records"]
                and abs(joined.total_loss-joined.loss).max()<1e-8
                and np.array_equal(joined.visits_x,joined.visits_y),
                "G17 source 56 block ledger mismatch "+tag)
        allsites.append(site);allblocks.append(blocks)
        slopes.append(pd.read_csv(source_shards/(tag+"_slopes.csv")))
        original_sha.append(dict(shard=shard,original_receipt_sha256=sha(rece),
                                 files_sha256=r["files_sha256"]))
    site=pd.concat(allsites,ignore_index=True)
    block=pd.concat(allblocks,ignore_index=True)
    slope=pd.concat(slopes,ignore_index=True)
    require(len(site)==N_EXPECTED
            and len(block)==N_TEMPLATES*len(PAIR_CELLS)*N_BLOCK
            and len(slope)==N_TEMPLATES*len(PAIR_CELLS)*N_FOLD
            and site.candidate.nunique()==N_TEMPLATES
            and not site.duplicated(["candidate","env_bg","rank_bg","site"]).any(),
            "G17 original all source templates × all crossed SDMs incomplete")
    diagonal=site[site.env_bg==site.rank_bg]
    check=compare_with_original_g15(diagonal,original_g15_shards)
    scores,comparison=compute_four_cell(block)
    effects=factorial(comparison)
    bootstrap=original_spatial_bootstrap(block)
    records=[]
    for key,draws in bootstrap.items():
        lo,hi=np.quantile(draws,[.025,.975])
        records.append(dict(metric=key,estimate=float(effects[key]),
                            paired_56block_bootstrap95_low=float(lo),
                            paired_56block_bootstrap95_high=float(hi),
                            n_original_blocks=N_BLOCK,
                            n_bootstrap=BLOCK_BOOT,bootstrap_seed=BLOCK_SEED))
    bt=pd.DataFrame(records)
    # Preserve prior G15 science: two diagonal relative source ranking p.
    prior=pd.read_csv(SOURCE_DIR/"G15_G14_signonly_vs_ABC_null_comparison.csv")
    for bg in FIELDS:
        a=comparison[(comparison.env_bg==bg)&(comparison.rank_bg==bg)].iloc[0]
        b=prior[prior.background==bg].iloc[0]
        require(a.source_nulls_better_or_equal_ABC==b.null_NLL_less_or_equal_ABC
                and abs(a.ABC_minus_null_gain-(b.null_mean_NLL-b.accepted_ABC_NLL))
                     <NUMERIC_G15_NLL_TOL,
                "G17 original 199-source diagonal ranking not reproduced "+bg)
    out.mkdir(parents=True,exist_ok=True)
    archived={
      "G17_four_cells_ABC_vs_199source_null.csv":comparison,
      "G17_complete_804_source_template_NLL_scores.csv":scores,
      "G17_all_45024_source_geographic_block_losses.csv.gz":block,
      "G17_all_4020_source_slope_folds.csv":slope,
      "G17_2x2_paired56block_bootstrap_effects.csv":bt,
      "G17_g15_numerical_source_replay.csv":check,
    }
    for name,data in archived.items():
        if name.endswith(".gz"):
            data.to_csv(out/name,index=False,compression={"method":"gzip","mtime":0})
        else:
            data.to_csv(out/name,index=False)
    info=dict(
      status="G17_ORIGINAL_2X2_SDM_ENV_RANK_CROSSSWAP_ALL_SOURCE_SUCCESS",
      original_G15_source_run=ORIGINAL_G15_RUN,
      original_source_templates=N_TEMPLATES,original_null_templates=N_NULLS,
      original_source_shards=NSHARDS,original_source_rows=N_EXPECTED,
      original_NAAMP_sites=N_SITE,original_visits=N_VISITS,
      original_geo_blocks=N_BLOCK,original_strong_calls=N_STRONG,
      original_geographic_folds=N_FOLD,
      pair_cells=[list(x) for x in PAIR_CELLS],
      original_81_rate_context_conditioned_null_selection_not_changed=True,
      source_G15_template_sha256=orig["file_sha256"][
           "G15_frozen_source_templates.csv"],
      source_G15_archive_sha256=sha(SOURCE_DIR/"G15_full_source_audit_receipt.json"),
      source_shard_receipt_hashes=original_sha,
      original_G15_diagonal_numerical_replay=check.to_dict("records"),
      original_diagonal_cross_sdm_gains=effects,
      original_G14_G15_dual_SDM_field_predictive_gates_pass=False,
      model_env_and_source_rank_effects_not_causal=True,
      no_new_field_observations=True,no_biological_source_simulations=True,
      no_wild_field_trophic_identification=True,no_field_ABC_posterior=True,
      posthoc_diagnostic=True,
      output_sha256={name:sha(out/name) for name in archived})
    (out/"G17_complete_original_source_audit.json").write_text(
        json.dumps(info,indent=2,ensure_ascii=False)+"\n")
    print("G17_ORIGINAL_2X2_ENV_RANK_COMPLETE "+json.dumps({
        "status":info["status"],
        "G15_replay":check.to_dict("records"),
        "four_cell_ABC_null_results":comparison.to_dict("records"),
        "2x2_factorial":effects,
        "bootstrap_intervals":bt.to_dict("records")}),flush=True)
    return info

if __name__=="__main__":
    cli=argparse.ArgumentParser()
    cli.add_argument("--stage",required=True,choices=["shard","aggregate"])
    cli.add_argument("--shard",type=int)
    cli.add_argument("--source-shards",type=Path)
    cli.add_argument("--original-g15-shards",type=Path)
    cli.add_argument("--out",required=True,type=Path)
    z=cli.parse_args()
    if z.stage=="shard":
        require(z.shard is not None,"G17 source shard missing")
        run_shard(z.shard,z.out)
    else:
        require(z.source_shards is not None and z.original_g15_shards is not None,
                "G17 both source shard roots required")
        aggregate(z.source_shards,z.original_g15_shards,z.out)
