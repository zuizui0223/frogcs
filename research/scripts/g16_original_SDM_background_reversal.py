"""G16: why G15 accepted ABC vs synthetic source null reverses across SDM backgrounds.

Reuses 1,707,696 original heldout site-source predictions from run #42379659618.
No new acoustic model fits, biology, filtering of source outcomes or field sampling.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

from g14_abc_ensemble_geographic_acoustic_holdout import read_field, original_rank01

ROOT = Path(__file__).resolve().parents[2]
G15 = ROOT/"research/results/g15_abc_acoustic_specificity_20261107/audited"
G14 = ROOT/"research/results/g14_abc_pom_field_ensemble_20261107"
OUT = ROOT/"research/results/g16_sdm_background_reversal_20261108"
SEED = 20261108
BOOT = 9999
NSHARDS = 4
N_SOURCE_TEMPLATES = 201
N_NULLS = 199
SITES = 4248
N_VISITS = 63180
BLOCKS = 56
BACKGROUND = ("uniform","target_group")
PCT = (.025,.975)
VI_SITES = 506
G15_SOURCE_RUN = 42379659618


def require(ok,msg):
    if not bool(ok):
        raise AssertionError(msg)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_original_site_predictions(shards):
    """Require all four original source artifacts; no partial success inference."""
    shards = Path(shards)
    meta = json.loads((G15/"G15_full_source_audit_receipt.json").read_text())
    require(meta["status"]=="G15_199_RATE_CONTEXT_NULL_ACOUSTIC_FIELD_SOURCE_COMPLETE"
            and meta["null_replicates"]==N_NULLS
            and meta["templates_total"]==N_SOURCE_TEMPLATES
            and meta["original_original_site_scores"]==N_SOURCE_TEMPLATES*2*SITES
            and meta["source_shards"]==NSHARDS
            and not meta["source_specificity_fixed_joint_gate_pass"],
            "Frozen G15 source and negative selection-specificity gate changed")
    allsite = []
    manifests = []
    for shard in range(NSHARDS):
        name=f"g15_predictive_null_shard_{shard:02d}"
        receipt_path=shards/(name+"_receipt.json")
        require(receipt_path.is_file(), "Original G15 source shard absent "+name)
        receipt=json.loads(receipt_path.read_text())
        ids=list(range(shard,N_NULLS,NSHARDS))
        require(receipt["status"]=="G15_ORIGINAL_FIELD_SOURCE_NULL_SHARD_SUCCESS"
                and receipt["shard"]==shard and receipt["nshards"]==NSHARDS
                and receipt["null_ids"]==ids
                and receipt["fixed_source_templates_SHA"]==meta["source_template_sha256"]
                and receipt["n_field_sites"]==SITES
                and receipt["n_field_visits"]==N_VISITS,
                "Original G15 source template identity/strata mismatch "+name)
        for file,original_sha in receipt["files_sha256"].items():
            require(sha(shards/file)==original_sha,
                    "G15 original source artifact byte SHA changed "+file)
        src=shards/(name+"_full_site.csv.gz")
        d=pd.read_csv(src)
        required={"candidate","background","fold","site","spatial_block",
                  "n_completed","k_strong","predicted","loss"}
        require(required.issubset(d.columns)
                and len(d)==receipt["site_rows"]
                and len(d)==(len(ids)+(2 if shard==0 else 0))*2*SITES,
                "Original source site rows missing "+name)
        require(not d.duplicated(["candidate","background","site"]).any(),
                "Source duplicate site/template prediction "+name)
        p=d.predicted.to_numpy(float)
        n=d.n_completed.to_numpy(float)
        k=d.k_strong.to_numpy(float)
        require(np.isfinite(p).all() and (p>0).all() and (p<1).all()
                and (n>0).all() and (k>=0).all() and (k<=n).all(),
                "Original G15 NAAMP binomial outcomes invalid")
        recalc=-(k*np.log(p)+(n-k)*np.log1p(-p))
        require(np.max(np.abs(recalc-d.loss.to_numpy(float)))<1e-11,
                "Original G15 per-site independently reconstructed NLL mismatch")
        allsite.append(d)
        manifests.append({
            "shard":shard,"original_source_receipt_sha256":sha(receipt_path),
            "source_site_rows":len(d),
            "source_sites_file_sha256":sha(src),
            "archived_original_file_sha256":receipt["files_sha256"],
        })
    full=pd.concat(allsite,ignore_index=True)
    require(len(full)==SITES*2*N_SOURCE_TEMPLATES
            and full.candidate.nunique()==N_SOURCE_TEMPLATES
            and set(full.background)==set(BACKGROUND)
            and full.site.nunique()==SITES
            and full.spatial_block.nunique()==BLOCKS
            and full.groupby(["candidate","background"]).site.nunique().eq(SITES).all()
            and not full.duplicated(["candidate","background","site"]).any(),
            "All 1,707,696 original G15 site×source×background outcomes required")
    return full,meta,manifests


def independent_block_archive_replay(full):
    r=G15/"G15_all_null_56block_losses.csv"
    meta=json.loads((G15/"G15_full_source_audit_receipt.json").read_text())
    require(sha(r)==meta["file_sha256"][r.name],
            "Original G15 199-null 56-block source archive SHA changed")
    old=pd.read_csv(r)
    actual=(full.groupby(["candidate","background","spatial_block"],sort=True)
            .agg(total_loss=("loss","sum"),
                 original_visits=("n_completed","sum"),
                 strong_calls=("k_strong","sum"),
                 sites=("site","size")).reset_index())
    require(len(actual)==N_SOURCE_TEMPLATES*2*BLOCKS
            and len(old)==len(actual), "Incomplete archived G15 geographic block scores")
    key=["candidate","background","spatial_block"]
    before=old.set_index(key).sort_index()
    after=actual.set_index(key).sort_index()
    require(before.index.is_unique and before.index.equals(after.index),
            "G15 56-block identities drifted")
    for col in ("original_visits","strong_calls","sites"):
        require(np.array_equal(before[col].to_numpy(),after[col].to_numpy()),
                "G15 original source block visit/strong/site counts changed "+col)
    err=float(np.max(np.abs(before.total_loss.to_numpy(float)-
                            after.total_loss.to_numpy(float))))
    require(err<1e-8, f"Independent original per-block NLL source replay: {err}")
    return err


def paired_bootstrap(block, draws=BOOT, seed=SEED):
    """Geographic-block resampling preserves identical IDs in both SDM backgrounds."""
    require(len(block)==BLOCKS and block.spatial_block.is_unique,"Need original 56 blocks")
    n=block.n_completed.to_numpy(float)
    u=block.uniform_gain_sum.to_numpy(float)
    t=block.target_group_gain_sum.to_numpy(float)
    require(np.all(n>0),"Zero-visit geographic block")
    sampler=np.random.default_rng(seed).integers(0,BLOCKS,size=(draws,BLOCKS))
    denom=n[sampler].sum(axis=1)
    bu=u[sampler].sum(axis=1)/denom
    bt=t[sampler].sum(axis=1)/denom
    def summary(name,values,observed):
        lo,hi=np.quantile(values,PCT)
        return dict(metric=name,estimate=float(observed),pointwise_MC95_low=float(lo),
                    pointwise_MC95_high=float(hi),bootstrap_draws=draws,
                    fixed_source_geographic_block_units=BLOCKS)
    full_n=n.sum()
    return pd.DataFrame([
      summary("uniform_ABC_minus_mean_null_gain",bu,u.sum()/full_n),
      summary("target_group_ABC_minus_mean_null_gain",bt,t.sum()/full_n),
      summary("uniform_minus_target_background_difference",bu-bt,(u.sum()-t.sum())/full_n),
    ])


def leave_one_out(block):
    require(len(block)==BLOCKS and block.spatial_block.is_unique,"56 original blocks required")
    num=block.n_completed.to_numpy(float)
    u=block.uniform_gain_sum.to_numpy(float)
    t=block.target_group_gain_sum.to_numpy(float)
    tot=num.sum()
    rest=tot-num
    require((rest>0).all(),"Cannot remove original source block")
    au=(u.sum()-u)/rest
    at=(t.sum()-t)/rest
    return pd.DataFrame(dict(
        removed_original_spatial_block=block.spatial_block.to_numpy(),
        removed_sites=block.n_sites.to_numpy(int),
        removed_visits=num.astype(int),
        retained_blocks=BLOCKS-1,
        retained_original_visits=rest.astype(int),
        uniform_gain_after_removal=au,
        target_group_gain_after_removal=at,
        paired_background_difference_after_removal=au-at,
    ))


def source_site_ledger(full):
    src,dofolds=read_field()   # checks original field-site and completed-visit source SHA256
    require(len(src)==SITES and src.site.is_unique
            and src.V.sum()==VI_SITES and src.n.sum()==N_VISITS
            and src.k.sum()==36554 and src.spatial_block.nunique()==BLOCKS,
            "G16 original 4248-site/506-V field cohort changed")
    originals=full[full.candidate=="ABC_794"][
        ["site","background","spatial_block","fold","k_strong",
         "n_completed","loss","predicted"]].copy()
    require(len(originals)==SITES*2,"Original 794-source both background site records missing")
    require(originals.groupby("background").site.nunique().eq(SITES).all(),
            "Original ABC model missing geographic sites")
    null=full[full.candidate.str.startswith("STRAT_NULL_")]
    require(null.candidate.nunique()==N_NULLS
            and null.groupby(["site","background"]).candidate.nunique().eq(N_NULLS).all(),
            "G15 all 199 null source predictions not covered at every original site")
    nullmean=(null.groupby(["site","background"],sort=True)
              .loss.mean().rename("mean_199_null_loss").reset_index())
    site=originals.merge(nullmean,on=["site","background"],how="left",validate="one_to_one")
    require(len(site)==SITES*2 and site.mean_199_null_loss.notna().all(),
            "Original mean-null site alignment incomplete")
    site["ABC_advantage_loss_sum"]=site.mean_199_null_loss-site.loss
    fields=["site","route","spatial_block","V","k","n",
            "mean_suitability_Odonata_uniform",
            "mean_suitability_Odonata_target_group",
            "mean_suitability_pond_breeding_Caudata_uniform",
            "mean_suitability_pond_breeding_Caudata_target_group"]
    orig=src[fields].copy()
    orig["O_rank_uniform"]=original_rank01(orig.mean_suitability_Odonata_uniform)
    orig["O_rank_target_group"]=original_rank01(orig.mean_suitability_Odonata_target_group)
    orig["S_rank_uniform"]=original_rank01(orig.mean_suitability_pond_breeding_Caudata_uniform)
    orig["S_rank_target_group"]=original_rank01(orig.mean_suitability_pond_breeding_Caudata_target_group)
    site=site.merge(orig,on="site",how="left",validate="many_to_one",suffixes=("_saved","_source"))
    require(len(site)==SITES*2
            and np.array_equal(site.k_strong.to_numpy(),site.k.to_numpy())
            and np.array_equal(site.n_completed.to_numpy(),site.n.to_numpy())
            and np.array_equal(site.spatial_block_saved.to_numpy(),
                               site.spatial_block_source.to_numpy()),
            "Original field source outcomes or geographic block changed")
    require((site.V.isin([0,1])).all() and site.V.sum()==2*VI_SITES,
            "Original landscape V classification drifted")
    check_folds=src.assign(fold=dofolds).set_index("site").fold
    require(np.array_equal(site.fold.to_numpy(int),site.site.map(check_folds).to_numpy(int)),
            "Original source spatial CV fold changed")
    site=site.rename(columns={"spatial_block_source":"spatial_block"})
    return site


def background_metrics(site):
    u=site[site.background=="uniform"].set_index("site").sort_index()
    t=site[site.background=="target_group"].set_index("site").sort_index()
    require(len(u)==len(t)==SITES and u.index.equals(t.index)
            and np.array_equal(u.n.to_numpy(int),t.n.to_numpy(int))
            and np.array_equal(u.V.to_numpy(int),t.V.to_numpy(int)),
            "SDM background versions do not share original acoustic sites")
    pair=u[["route","spatial_block","V","n","k",
            "O_rank_uniform","O_rank_target_group",
            "S_rank_uniform","S_rank_target_group"]].copy()
    pair["uniform_gain_sum"]=u.ABC_advantage_loss_sum
    pair["target_group_gain_sum"]=t.ABC_advantage_loss_sum
    pair["uniform_gain_per_visit"]=pair.uniform_gain_sum/pair.n
    pair["target_group_gain_per_visit"]=pair.target_group_gain_sum/pair.n
    pair["background_gain_diff_per_visit"]=(
        pair.uniform_gain_per_visit-pair.target_group_gain_per_visit)
    pair["O_abs_rank_discrepancy"]=abs(pair.O_rank_uniform-pair.O_rank_target_group)
    pair["S_abs_rank_discrepancy"]=abs(pair.S_rank_uniform-pair.S_rank_target_group)
    pair["mean_OS_abs_rank_discrepancy"]=(
        pair.O_abs_rank_discrepancy+pair.S_abs_rank_discrepancy)/2
    pair=pair.reset_index()
    require(len(pair)==SITES and pair.site.is_unique,
            "Cross-background matched-site source ledger incomplete")
    return pair


def group_metrics(pair,boot_summary):
    main=[]
    for v in (0,1):
        x=pair[pair.V==v]
        require(len(x)==(VI_SITES if v==1 else SITES-VI_SITES),
                "Predeclared V positive/negative field sites lost")
        for bg in BACKGROUND:
            y=x[bg+"_gain_sum"].to_numpy(float)
            main.append(dict(landscape_flooded_vegetation=v,background=bg,
              sites=int(len(x)),completed_visits=int(x.n.sum()),
              strong_call_events=int(x.k.sum()),
              abc_minus_mean_null_NLL_per_visit=float(y.sum()/x.n.sum()),
              abc_minus_mean_null_contribution_to_whole_NLL_per_visit=float(y.sum()/N_VISITS),
              original_world_sites_not_independent_across_background=True))
    landscapes=pd.DataFrame(main)
    require(landscapes.groupby("background").completed_visits.sum().eq(N_VISITS).all()
            and landscapes.groupby("background").sites.sum().eq(SITES).all(),
            "Landscape V source grouping incomplete")
    for bg in BACKGROUND:
        pooled=landscapes[landscapes.background==bg]
        val=pooled.abc_minus_mean_null_contribution_to_whole_NLL_per_visit.sum()
        z=boot_summary[boot_summary.metric==bg+"_ABC_minus_mean_null_gain"].estimate.iloc[0]
        require(abs(val-z)<1e-12,"V landscape decomposition does not sum to original pooled G15")
    corr=[]
    for group,sub in [("all",pair),("V0",pair[pair.V==0]),("V1",pair[pair.V==1])]:
        for guild in ("O","S"):
            a=sub[guild+"_rank_uniform"].to_numpy(float)
            b=sub[guild+"_rank_target_group"].to_numpy(float)
            rho=float(spearmanr(a,b).statistic)
            discord=abs(a-b)
            corr.append(dict(group=group,guild=guild,n_original_sites=len(sub),
              Spearman_cross_SDM_rank=rho,
              median_absolute_rank_difference=float(np.median(discord)),
              p90_absolute_rank_difference=float(np.quantile(discord,.9))))
    corrs=pd.DataFrame(corr)
    analytic=[]
    for group,sub in [("all",pair),("V0",pair[pair.V==0]),("V1",pair[pair.V==1])]:
        v=sub.mean_OS_abs_rank_discrepancy
        y=abs(sub.background_gain_diff_per_visit)
        analytic.append(dict(group=group,
           n_original_sites=len(sub),
           Spearman_source_rank_discrepancy_vs_absolute_prediction_gain_discrepancy=
             float(spearmanr(v,y).statistic),
           descriptive_only_no_causality=True))
    assoc=pd.DataFrame(analytic)
    return landscapes,corrs,assoc


def main(shards,out=OUT):
    out=Path(out)
    original,meta,shardreceipts=read_original_site_predictions(shards)
    replay=independent_block_archive_replay(original)
    site=source_site_ledger(original)
    pair=background_metrics(site)
    block=(pair.groupby("spatial_block",sort=True).agg(
       n_sites=("site","size"),
       n_completed=("n","sum"),n_strong=("k","sum"),
       n_V1=("V","sum"),
       uniform_gain_sum=("uniform_gain_sum","sum"),
       target_group_gain_sum=("target_group_gain_sum","sum")).reset_index())
    require(len(block)==BLOCKS and block.n_completed.sum()==N_VISITS
            and block.n_V1.sum()==VI_SITES and block.n_strong.sum()==36554,
            "All 56 original geographic blocks incomplete")
    block["uniform_gain_per_block_visit"]=block.uniform_gain_sum/block.n_completed
    block["target_group_gain_per_block_visit"]=block.target_group_gain_sum/block.n_completed
    block["signed_cross_background_gain_sum"] = (block.uniform_gain_sum-
                                                  block.target_group_gain_sum)
    block["absolute_cross_background_influence"]=abs(block.signed_cross_background_gain_sum)
    overall=paired_bootstrap(block)
    expected=pd.read_csv(G15/"G15_G14_signonly_vs_ABC_null_comparison.csv")
    for bg in BACKGROUND:
        archived=expected[expected.background==bg]
        require(len(archived)==1,"G15 archived background score missing "+bg)
        known=float(archived.null_mean_NLL.iloc[0]-archived.accepted_ABC_NLL.iloc[0])
        measured=float(overall[overall.metric==bg+"_ABC_minus_mean_null_gain"].estimate.iloc[0])
        require(abs(measured-known)<1e-10,"G15 original pooled source NLL ranking not replayed: "+bg)
    loo=leave_one_out(block)
    order=block.sort_values(["absolute_cross_background_influence","spatial_block"],
                            ascending=[False,True])
    stress=[]
    for n in (1,3,5):
        x=order.iloc[:n];z=block[~block.spatial_block.isin(x.spatial_block)]
        denom=float(z.n_completed.sum())
        gu=float(z.uniform_gain_sum.sum()/denom)
        gt=float(z.target_group_gain_sum.sum()/denom)
        stress.append(dict(blocks_removed=n,
          source_block_ids_removed=";".join(x.spatial_block.astype(str)),
          source_visits_removed=int(x.n_completed.sum()),
          retained_source_blocks=int(len(z)),retained_source_visits=int(denom),
          uniform_gain=gu,target_group_gain=gt,
          difference_uniform_minus_target=gu-gt,
          diagnostic_only_outcome_selected_stress=True))
    stress=pd.DataFrame(stress)
    V,corr,assoc=group_metrics(pair,overall)
    out.mkdir(parents=True,exist_ok=True)
    tables={
       "G16_56block_ABC_minus_mean_null_gains.csv":block,
       "G16_56_block_leave_one_out.csv":loo,
       "G16_top_1_3_5_block_influence.csv":stress,
       "G16_original_V0_V1_landscape_contributions.csv":V,
       "G16_SDM_predictor_rank_concordance.csv":corr,
       "G16_rank_discrepancy_vs_predictive_discrepancy.csv":assoc,
       "G16_geographic_bootstrap_9999_summary.csv":overall,
    }
    for name,frame in tables.items():
        frame.to_csv(out/name,index=False)
    q=out/"G16_4248_original_site_pair_diagnostic.csv.gz"
    pair.to_csv(q,index=False,compression={"method":"gzip","mtime":0})
    assert len(tables)==7
    receipt={
        "status":"G16_G15_SDM_BACKGROUND_REVERSAL_SOURCE_AUDIT_SUCCESS",
        "original_G15_run":G15_SOURCE_RUN,
        "original_heldout_source_site_rows":len(original),
        "original_ABC_source_templates":N_SOURCE_TEMPLATES,
        "original_199_null_templates":N_NULLS,
        "original_56_geographical_blocks":BLOCKS,
        "original_NAAMP_sites":SITES,
        "original_completed_visits":N_VISITS,
        "original_vegetated_landscape_sites":VI_SITES,
        "original_strong_events":36554,
        "source_G15_sha256":sha(G15/"G15_full_source_audit_receipt.json"),
        "source_G15_archive_replay_max_abs":replay,
        "original_4_shard_SHA_receipts":shardreceipts,
        "fixed_9999_bootstraps":BOOT,
        "bootstrap_seed":SEED,
        "source_pooled_gains":{
            line.metric:float(line.estimate) for line in overall.itertuples(index=False)
        },
        "original_G15_dual_background_specificity_gate_pass":False,
        "original_G14_dual_background_field_gate_pass":False,
        "no_new_model_fitting":True,"no_new_field_data":True,
        "no_ecological_causal_identification":True,
        "posthoc_followup":True,
        "G16_files_sha256":{f.name:sha(f) for f in sorted(out.iterdir())
                            if f.is_file()},
    }
    (out/"G16_complete_original_source_receipt.json").write_text(
        json.dumps(receipt,indent=2)+"\n")
    print("G16_SOURCE_BACKGROUND_REVERSAL_COMPLETE",json.dumps({
       "status":receipt["status"],
       "block_bootstrap":overall.to_dict("records"),
       "landscape_V":V.to_dict("records"),
       "rank_concordance":corr.to_dict("records"),
       "block_leave_one_out_uniform_positive":int((loo.uniform_gain_after_removal>0).sum()),
       "block_leave_one_out_target_negative":int((loo.target_group_gain_after_removal<0).sum()),
       "top5_trim":stress.iloc[-1].to_dict(),
    }),flush=True)
    return receipt


if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--shards",required=True,type=Path)
    ap.add_argument("--out",type=Path,default=OUT)
    args=ap.parse_args()
    main(args.shards,args.out)
