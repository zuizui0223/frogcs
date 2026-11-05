"""Source-only figure for independently audited P1 arrival×duration original80 models.

Plots source-cluster 95% Monte Carlo ranges from complete original
256-background paired factorial; does not rerun or select any biology.
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

STAGES=("LS","LL","ES","EL")
STAGE_LABEL=("Late / short\nS day40 · 40d","Late / long\nS day40 · 60d",
             "Early / short\nS day0 · 40d","Early / long\nS day0 · 60d")
MODERATION=(
    "pure_arrival_moderation_of_plant_effect",
    "pure_duration_moderation_of_plant_effect",
    "arrival_x_duration_moderation_of_plant_effect",
)
MODERATION_LABEL=("Early versus late\n(averaged over duration)",
                  "Long versus short\n(averaged over arrival)",
                  "Timing × duration\nextra interaction")


def require(b,why):
    if not bool(b):
        raise AssertionError(why)


def recorded(rows,col,name):
    out=rows[(rows.metric==col)&(rows.contrast==name)].set_index("timing")
    require(set(out.index)==set(STAGES),"Four exact counterfactual contexts not matched")
    out=out.loc[list(STAGES)]
    require(out.n_original_source_backgrounds.eq(256).all() and
            np.isfinite(out[["mean","mc95_low","mc95_high"]]).all().all(),
            "Original 256 source sampling and 95% range insufficient")
    return out


def figure_original_sign_vs_frog(plant,out):
    fig,axes=plt.subplots(1,2,figsize=(13.8,5.7))
    for ax,metric,unit,scale in [
        (axes[0],"mean_log_F_B","Both functions − neither · mean log aquatic F",1),
        (axes[1],"accepted","Both functions − neither · four-sign compatibility (pp)",100),
    ]:
        t=recorded(plant,metric,"both_minus_neither")
        x=np.arange(4)
        mean=t["mean"].to_numpy()*scale
        lo=t.mc95_low.to_numpy()*scale
        hi=t.mc95_high.to_numpy()*scale
        ax.errorbar(x,mean,yerr=np.vstack((mean-lo,hi-mean)),
                    marker="o",markersize=7,linestyle="none",
                    capsize=4,linewidth=2,color="#20588a")
        ax.axhline(0,color="#888888",lw=1)
        ax.set_xticks(x,list(STAGE_LABEL),fontsize=9)
        ax.set_ylabel(unit,fontsize=10)
        ax.grid(axis="y",alpha=.18)
        ax.set_xlim(-.45,3.45)
        if metric=="mean_log_F_B":
            ax.set_title("A. Focal frog cohort benefit",fontsize=12)
        else:
            ax.set_title("B. Ability to generate four idealized signs",fontsize=12)
        for xi,yi in zip(x,mean):
            ax.annotate(f"{yi:+.3f}" if scale==1 else f"{yi:+.2f} pp",
                        (xi,yi),textcoords="offset points",xytext=(0,10),
                        ha="center",fontsize=8)
    fig.suptitle("P1: independently separate salamander arrival from aquatic duration",fontsize=15)
    fig.text(.016,.02,
        "Original unchanged PR161 256 food-web backgrounds × 4 stage combinations; source-cluster 95% MC ranges. "
        "Model-only timing, not observed wetland breeding onset.",fontsize=8)
    fig.tight_layout(rect=(0,.055,1,.92))
    fn=out/"Figure_P1_early_vs_duration_pattern_population_divergence.png"
    fig.savefig(fn,dpi=190)
    plt.close(fig)
    return fn


def figure_moderators(moderators,out):
    fig,axes=plt.subplots(1,2,figsize=(13.7,5.8))
    for ax,metric,title,scale in [
        (axes[0],"mean_log_F_B","A. Moderation of the vegetation effect on frog amount",1),
        (axes[1],"accepted","B. Moderation of vegetation effect on four-sign success",100),
    ]:
        x=moderators[moderators.metric==metric].set_index("contrast")
        require(set(x.index)==set(MODERATION),"Missing arrival or duration separate contrast")
        x=x.loc[list(MODERATION)]
        y=x["mean"].to_numpy(dtype=float)*scale
        lo=x.mc95_low.to_numpy(dtype=float)*scale
        hi=x.mc95_high.to_numpy(dtype=float)*scale
        require(np.isfinite(np.c_[y,lo,hi]).all() and
                x.n_original_source_backgrounds.eq(256).all(),
                "Unverified source-cluster timing×duration uncertainty")
        ypos=np.arange(3)
        ax.errorbar(y,ypos,xerr=np.vstack([y-lo,hi-y]),
                    marker="o",linestyle="none",capsize=4,
                    color="#20588a")
        ax.axvline(0,color="#888888",lw=1)
        ax.set_yticks(ypos,list(MODERATION_LABEL),fontsize=10)
        ax.invert_yaxis()
        ax.set_title(title,fontsize=12)
        ax.set_xlabel("Effect on 11−00 " + ("log F" if scale==1 else "compatibility (pp)"))
        ax.grid(axis="x",alpha=.18)
    fig.suptitle("P1: source-matched pure arrival, duration and interaction contrasts",fontsize=15)
    fig.text(.02,.02,"256 model backgrounds, repeated original biological rates. 10,000 bootstrap source resamples; "
             "95% Monte Carlo intervals, not field confidence intervals.",fontsize=8)
    fig.tight_layout(rect=(0,.06,1,.91))
    fn=out/"Figure_P1_pure_arrival_duration_moderators.png"
    fig.savefig(fn,dpi=190)
    plt.close(fig)
    return fn


def run(root,out):
    root=Path(root);out=Path(out)
    receipt=json.loads((root/"P1_isolated_stage_source_receipt.json").read_text())
    require(receipt["status"]==
            "P1_PURE_SALAMANDER_ARRIVAL_VS_DURATION_ORIGINAL80_SOURCE_AUDIT_SUCCESS"
            and receipt["source_80year_scenarios"]==4096
            and receipt["source_8corner_80year_outputs"]==32768
            and receipt["source_original_stage1_2_replay"]
                  ["legacy_original_16384_original_vertices_replayed"],
            "P1 source factor/old original models were not audited")
    pair=root/"P1_within_timing_paired_vegetation_effects.csv"
    mods=root/"P1_pure_arrival_duration_and_interaction.csv"
    a=pd.read_csv(pair,dtype={"timing":str})
    b=pd.read_csv(mods)
    out.mkdir(parents=True,exist_ok=True)
    figs=[figure_original_sign_vs_frog(a,out),
          figure_moderators(b,out)]
    require(all(f.stat().st_size>35_000 for f in figs),
            "P1 numerical scientific figures empty/failed")
    manifest=dict(
      status="P1_TWO_SOURCE_BACKED_256_BACKGROUND_STAGE_FIGURES_VERIFIED",
      source_audit_sha256=hashlib.sha256((root/"P1_isolated_stage_source_receipt.json").read_bytes()).hexdigest(),
      complete_original_pr161_replay=True,model_source_backgrounds=256,
      original_true80_scenarios=4096,
      source_data_shas={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (pair,mods)},
      figures=[dict(path=f.name,bytes=f.stat().st_size) for f in figs],
      real_natural_pond_breeding_priority_measured=False,
    )
    (out/"P1_figure_source_manifest.json").write_text(
        json.dumps(manifest,indent=2,ensure_ascii=False)+"\n")
    print("P1_ORIGINAL256_PURE_TIMING_FIGURES_SOURCE_VERIFIED",json.dumps(manifest),flush=True)


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--source",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    x=p.parse_args()
    run(x.source,x.output)
