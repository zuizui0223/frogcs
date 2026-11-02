"""Figure 3: source-locked finite-N long-run outcomes AND separate site adequacy.

The two results have non-identical observational targets:
 (a) PR160 true finite-N 80-year simulated F patch occupancy, 96 source draws;
 (b) S->F-specific movement effect under model interventions;
 (c) PR158 UNFITTED 4,248 field-site proxy POM: each source model's
     six descriptive observed-statistic marginal 95% intervals.

No model-native sign acceptance is relabeled field posterior probability.
No new biological simulation or parameter fitting is performed.
"""
from __future__ import annotations
import argparse
import gzip
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

SOURCE_CONTEXT_COUNTS=(317,265,212)
FIELDS=("draw_id","q","seed","edge_SF_on","move_on")
COUNT_SCALES=(3,12)
BGS=("uniform","target_group")
BOOTSTRAP_SEED=20261101
BOOTSTRAP_REPS=6000


def need(condition,message):
    if not bool(condition):
        raise AssertionError(message)


def load_finite(folder):
    files=sorted(folder.rglob("finite_predictions_shard_*.csv.gz"))
    need(len(files)==4,"Exactly four verified PR160 original source finite-N shards required")
    x=pd.concat([pd.read_csv(file,compression="gzip") for file in files],
                ignore_index=True)
    need(len(x)==1536 and x.draw_id.nunique()==96,
         "Original 96 draw x 2 q x 2 edge x 2 move x 2 seeds factorial incomplete")
    need(not x.duplicated(list(FIELDS)).any(),"Duplicate original 80y stochastic arm")
    need(set(x.q)==set(COUNT_SCALES) and set(x.edge_SF_on)=={0,1}
         and set(x.move_on)=={0,1} and set(x.seed)=={101,102},
         "Source scale, trophic ablation or movement design drifted")
    need(x.groupby("draw_id").size().eq(16).all(),
         "Selected 80y source M,T,theta is not paired across all 16 arms")
    source=x[["draw_id","context_id","sample_weight"]].drop_duplicates()
    need(len(source)==96 and source.groupby("context_id").size().eq(32).all(),
         "Original context-stratified source IDs invalid")
    expected=source.context_id.map({
        c:SOURCE_CONTEXT_COUNTS[c]/sum(SOURCE_CONTEXT_COUNTS)/32
        for c in (0,1,2)
    })
    need(np.allclose(source.sample_weight,expected,rtol=0,atol=1e-10),
         "Original accepted-context source weights changed")
    need(x.occupied_year80.between(0,8).all(),"Finite-N occupied patches outside 0-8")
    need(x.context_id.nunique()==3 and x.draw_id.is_unique is False,
         "Original selected cohort unexpectedly changed")
    return x,files,source.sort_values("draw_id").reset_index(drop=True)


def load_site(site,site_summary):
    y=pd.read_csv(site,compression="gzip")
    report=pd.read_csv(site_summary)
    k=["network","scale","movement","structure_id","draw"]
    need(len(y)==1536 and len(report)==2,"Wrong original PR158 site model population")
    need(set(y.background)==set(BGS) and set(report.background)==set(BGS),
         "Original two SDM backgrounds absent")
    need(y.groupby("background").size().eq(768).all(),
         "Each model site-background must contain 768 candidates")
    need(not y.duplicated(["background"]+k).any(),
         "Original source network x theta site model is not uniquely identified")
    counts=y.groupby("background").all_six_inside_marginal_95.sum()
    need(counts.to_dict()=={"uniform":0,"target_group":7},
         "Six-statistic original source adequacy counts differ")
    n_report=report.set_index("background").n_six_marginal_interval_compatible
    need(all(int(counts.loc[b])==int(n_report.loc[b]) for b in BGS),
         "Audited summary disagrees with original individual site model values")
    need(set(report.n_full_same_theta_candidate_models)=={768}
         and set(report.n_finite_four_seed_source_site_models)=={523},
         "Original PR158 field emission model denominator changed")
    pivot=y.pivot(index=k,columns="background",values="all_six_inside_marginal_95")
    need(not (pivot.uniform & pivot.target_group).any(),
         "A site model satisfied both backgrounds, contrary to verified source")
    return y,report


def draw_boot(source,values):
    """Matched 96 source IDs are the unit; repeat within original 3 strata."""
    ids=source.draw_id.to_numpy()
    contexts=source.context_id.to_numpy()
    weights=source.sample_weight.to_numpy(float)
    rng=np.random.default_rng(BOOTSTRAP_SEED)
    idx=np.empty((BOOTSTRAP_REPS,96),dtype=np.int16)
    for c in (0,1,2):
        pos=np.where(contexts==c)[0]
        need(len(pos)==32,"Original selection stratum lost")
        idx[:,pos]=pos[rng.integers(0,32,size=(BOOTSTRAP_REPS,32))]
    w=weights[idx]
    w/=w.sum(axis=1,keepdims=True)
    arr=np.asarray(values,dtype=float)
    need(arr.shape==(96,len(arr[0])) and np.isfinite(arr).all(),
         "Missing per-source sixteenth-arm aggregate")
    boot=np.einsum('bi,bij->bj',w,arr[idx])
    base=np.einsum('i,ij->j',weights,arr)
    low=np.quantile(boot,.025,axis=0)
    high=np.quantile(boot,.975,axis=0)
    return base,low,high


def figure_3a(finite,source,output):
    seed_averaged=(finite.groupby(["draw_id","q","edge_SF_on","move_on"],
                                  as_index=False).occupied_year80.mean())
    need(len(seed_averaged)==96*8,"A selected source lacks a two-seed prediction")
    rows=[]
    for q in COUNT_SCALES:
        arms=[]
        for pred in (0,1):
            for move in (0,1):
                col=(seed_averaged[(seed_averaged.q==q)
                                   &(seed_averaged.edge_SF_on==pred)
                                   &(seed_averaged.move_on==move)]
                     .set_index("draw_id").reindex(source.draw_id))
                need(col.occupied_year80.notna().all(),
                     "Source ID missing finite count endpoint")
                arms.append(col.occupied_year80.to_numpy(dtype=float))
        base,lo,hi=draw_boot(source,np.column_stack(arms))
        for i,(pred,move) in enumerate(((0,0),(0,1),(1,0),(1,1))):
            rows.append(dict(q=q,edge_SF_on=pred,move_on=move,
                             occupied_patch_mean=float(base[i]),
                             source_mc95_lo=float(lo[i]),source_mc95_hi=float(hi[i])))
    summary=pd.DataFrame(rows)
    fig,axs=plt.subplots(1,2,figsize=(12.8,5.7),sharey=True)
    for ax,q in zip(axs,COUNT_SCALES):
        part=summary[summary.q==q]
        for pred,label in ((0,"S→F predation OFF"),(1,"S→F predation ON")):
            ss=part[part.edge_SF_on==pred].sort_values("move_on")
            x=ss.move_on.to_numpy(dtype=float)
            y=ss.occupied_patch_mean.to_numpy(dtype=float)
            lo=y-ss.source_mc95_lo.to_numpy(dtype=float)
            hi=ss.source_mc95_hi.to_numpy(dtype=float)-y
            ax.errorbar(x,y,yerr=np.vstack((lo,hi)),marker="o",
                        capsize=4,linestyle="-",label=label)
        ax.set_xticks([0,1],["Movement OFF","Movement ON"])
        ax.set_ylim(0,8.35)
        ax.set_title(f"q = {q} (hypothetical scale)")
        ax.grid(axis="y",alpha=.25)
    axs[0].set_ylabel("Year-80 occupied F patches (out of eight synthetic patches)")
    axs[0].legend(fontsize=9,loc="lower left")
    fig.suptitle("Figure 3A · Same-source finite-population frog occupancy")
    fig.text(.02,.013,
        "Source-ID-stratified Monte Carlo intervals (96 M×T×θ draws; two stochastic seeds), "
        "not confidence intervals for wild frog populations.",fontsize=8)
    fig.tight_layout(rect=(0,.045,1,.94))
    fig.savefig(output/"Figure3A_finiteN_80year_occupancy.png",dpi=190)
    plt.close(fig)
    return summary


def figure_3bc(bootstrap,site_report,output):
    need(set(bootstrap.q)==set(COUNT_SCALES) and len(bootstrap)==2,
         "True original 96-source moderation intervals missing")
    fig,(ax,bx)=plt.subplots(1,2,figsize=(13.0,5.2))
    for i,q in enumerate(COUNT_SCALES):
        row=bootstrap[bootstrap.q==q].iloc[0]
        value=float(row.mean_weighted_moderation)
        errlo=value-float(row.bootstrap_mc_low)
        errhi=float(row.bootstrap_mc_high)-value
        need(errlo>=0 and errhi>=0,
             "Original source effect outside bootstrap Monte Carlo interval")
        ax.errorbar([value],[1-i],xerr=[[errlo],[errhi]],
                    marker="o",linestyle="none",capsize=4)
    ax.set_yticks([1,0],["q = 3","q = 12"])
    ax.axvline(0,color="grey",linewidth=1)
    ax.set_xlim(-.36,.36)
    ax.set_xlabel("S→F modulation of movement effect (F patches)")
    ax.set_title("B · No stable predation-specific movement benefit")
    ax.grid(axis="x",alpha=.2)
    summary=site_report.set_index("background")
    for i,bg in enumerate(BGS):
        row=summary.loc[bg]
        n=int(row.n_six_marginal_interval_compatible)
        bx.barh(1-i,n)
        bx.text(n+.14,1-i,f"{n} / 768",va="center",fontsize=10)
    bx.set_xlim(0,9)
    bx.set_yticks([1,0],["Uniform SDM","Target-group SDM"])
    bx.set_xlabel("Candidates inside six individual observed intervals")
    bx.set_title("C · Six-statistic field proxy adequacy")
    bx.grid(axis="x",alpha=.2)
    fig.suptitle("Figure 3B–C · Synthetic persistence versus observed-site fit")
    fig.text(.02,.012,
        "Panel B: matched synthetic source bootstrap (not wild CI). "
        "Panel C: unfitted site proxy; six marginal 95% intervals, NOT a joint test. "
        "No structure matched both SDM backgrounds.",fontsize=8)
    fig.tight_layout(rect=(0,.06,1,.92))
    fig.savefig(output/"Figure3BC_movement_and_field_adequacy.png",dpi=190)
    plt.close(fig)


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--finite-dir",type=Path,required=True)
    p.add_argument("--source-bootstrap",type=Path,required=True)
    p.add_argument("--site-models",type=Path,required=True)
    p.add_argument("--site-summary",type=Path,required=True)
    p.add_argument("--main-abc-summary",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    finite,files,source=load_finite(a.finite_dir)
    site,report=load_site(a.site_models,a.site_summary)
    monte=pd.read_csv(a.source_bootstrap)
    main=json.loads(a.main_abc_summary.read_text())
    need(main.get("n_proposed")==20000 and main.get("n_accepted_log")==794
         and main.get("model_space")==3600,
         "Original 80y model-native acceptance source changed")
    a.output.mkdir(parents=True,exist_ok=True)
    groups=figure_3a(finite,source,a.output)
    # Fixed original source report #160 is crosschecked to avoid silent
    # missing demographic rows or reinterpreting a different scale.
    expected={(3,0,0):7.519,(3,0,1):7.724,(3,1,0):6.461,(3,1,1):6.657,
              (12,0,0):7.990,(12,0,1):7.969,(12,1,0):7.906,(12,1,1):7.874}
    for row in groups.itertuples():
        key=(row.q,row.edge_SF_on,row.move_on)
        need(abs(row.occupied_patch_mean-expected[key])<.001,
             f"Original source published figure differs from selected draw calculation: {key}")
    figure_3bc(monte,report,a.output)
    groups.to_csv(a.output/"Figure3A_source_occupancy_summary.csv",index=False)
    receipt={
        "status":"FIGURE3_SOURCE_VERIFIED_GENUINE_80Y_AND_DISTINCT_REAL_SITE_ADEQUACY",
        "model_source_run":41262102436,"field_proxy_source_run":41215171866,
        "main_catalogue_size":3600,"accepted_model_native_sign_draws":794,
        "n_selected_M_stage_theta":96,"n_true_80year_finite_arms":1536,
        "n_real_site_comparison_per_sdm":768,
        "no_model_adequate_both_backgrounds":True,
        "original_process_observation_bridge_fitted":False,
        "source_mc_not_ecological_CI":True,
        "source_sha256":{f.name:hashlib.sha256(f.read_bytes()).hexdigest()
          for f in [*files,a.source_bootstrap,a.site_models,a.site_summary,a.main_abc_summary]},
        "figures":["Figure3A_finiteN_80year_occupancy.png",
                   "Figure3BC_movement_and_field_adequacy.png"]
    }
    (a.output/"Figure3_source_receipt.json").write_text(
        json.dumps(receipt,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print("FROGCS_FIGURE3_SOURCE_LINKED_VERIFIED",
          json.dumps({k:v for k,v in receipt.items() if k!="source_sha256"}),flush=True)


if __name__=="__main__":
    main()
