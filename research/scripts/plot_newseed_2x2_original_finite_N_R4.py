"""Publication R4 figures from independent true80 finite-N source audit only.

Source inputs must already have passed old PR161 same 256 canonical source IDs,
24,576 integer stochastic model-arm outcomes and 256-background bootstrap.
No field estimation or source biological re-simulation is performed here.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

N_SOURCE=256
Q=(3,12)
MOVEMENTS=(0,1)
ARMS=("00","10","01","11")
LABELS=("Neither","F-from-S shelter","D-to-F feeding support","Both functions")


def require(condition,message):
    if not bool(condition):
        raise AssertionError(message)


def read_effect(t,metric,kind,contrast,q,move,stage="pooled"):
    z=t[(t.metric==metric)&(t.kind==kind)&(t.contrast==contrast)&
        (t.q==q)&(t.move_on==move)&(t.stage==stage)]
    require(len(z)==1,f"Missing source real80 interval: {metric} {contrast} {q} {move} {stage}")
    a=z.iloc[0]
    value=(float(a["mean"]),float(a.mc95_low),float(a.mc95_high))
    require(np.isfinite(value).all() and value[1]<=value[0]<=value[2],
            "Invalid original source 256 model-cluster bootstrap interval")
    return value


def pooled_population_figure(t,dest):
    fig,axes=plt.subplots(1,2,figsize=(13.4,5.4),sharey=True)
    for ax,q in zip(axes,Q):
        for move,label,offset in ((0,"Movement OFF",-.08),(1,"Movement ON",.08)):
            y=np.array([read_effect(t,"occupied_year80","arm",arm,q,move)
                        for arm in ARMS],dtype=float)
            x=np.arange(4)+offset
            ax.errorbar(x,y[:,0],yerr=np.vstack([y[:,0]-y[:,1],y[:,2]-y[:,0]]),
                        marker="o",linestyle="-",capsize=3,label=label)
        ax.set_xticks(np.arange(4),LABELS,rotation=20,ha="right",fontsize=9)
        ax.set_ylim(0,8.35)
        ax.set_title(f"Original hypothetical finite-population scale q={q}")
        ax.grid(axis="y",alpha=.15)
    axes[0].legend(loc="lower left")
    axes[0].set_ylabel("Model year-80 F-occupied artificial ring patches (0–8)")
    fig.suptitle("R4 · Same 256 new-seed 2×2 model structures: full population outcomes")
    fig.text(.02,.01,
       "95% original 256-source background Monte Carlo ranges. Source has external immigration ON. "
       "Movement does not uniquely cause reoccupancy.",fontsize=8)
    fig.tight_layout(rect=(0,.05,1,.92))
    fig.savefig(dest/"Figure_R4_newseed256_year80_population_occupancy.png",dpi=190)
    plt.close(fig)


def source_factorial_figure(t,move,dest):
    fig,(ax,bx)=plt.subplots(1,2,figsize=(13.6,5.2))
    for graph,contrast,kind,title in (
       (ax,"both_vs_neither","pair","A · Both functions minus neither"),
       (bx,"2x2_factorial","synergy","B · Matched 2×2 vegetation factorial"),
    ):
        for q,off in ((3,-.09),(12,.09)):
            v=np.array([read_effect(t,"occupied_year80",kind,contrast,q,move,st)
                       for st in ("0","1","2","pooled")])
            graph.errorbar(np.arange(4)+off,v[:,0],
                           yerr=np.vstack([v[:,0]-v[:,1],v[:,2]-v[:,0]]),
                           marker="o",linestyle="none",capsize=3,
                           label=f"q={q}")
        graph.axhline(0,color="grey",lw=1)
        graph.set_xticks(range(4),["Stage 0","Stage 1","Stage 2","Pooled"])
        graph.set_ylabel("Difference in original F-occupied model patches")
        graph.grid(axis="y",alpha=.15)
        graph.set_title(title)
    ax.legend(loc="lower left")
    fig.suptitle(f"R4 · Matched vegetation mechanisms on year80 population: movement {'ON' if move else 'OFF'}")
    fig.text(.015,.012,
       "Original 256 source-background 95% Monte Carlo ranges, not wild population confidence intervals. "
       "All three developmental contexts repeated within each model background.",fontsize=8)
    fig.tight_layout(rect=(0,.055,1,.92))
    fig.savefig(dest/f"Figure_R4_newseed256_2x2_demography_move{move}.png",dpi=190)
    plt.close(fig)


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source-intervals",type=Path,required=True)
    p.add_argument("--source-receipt",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    t=pd.read_csv(a.source_intervals,dtype={"stage":str})
    r=json.loads(a.source_receipt.read_text())
    require(r["status"]=="PR161_SAME256_R4_GENUINE80_FINITE_N_INDEPENDENT_SOURCE_AUDIT_SUCCESS"
            and r["genuine_stochastic_80year_arms"]==24576
            and r["original_canonical_structures"]==N_SOURCE and len(t)==1280,
            "Original complete genuine model source result was not audited")
    a.output.mkdir(parents=True,exist_ok=True)
    pooled_population_figure(t,a.output)
    for move in MOVEMENTS:
        source_factorial_figure(t,move,a.output)
    pngs=sorted(a.output.glob("Figure_R4_*.png"))
    require(len(pngs)==3 and all(png.stat().st_size>20000 for png in pngs),
            "Source-backed 80-year R4 scientific figures missing")
    manifest=dict(
      status="PR161_NEWSEED_R4_3_SOURCE_BACKED_POPULATION_FIGURES_CREATED",
      source_year80_arms=24576,
      source_model_clusters=256,
      real_world_ponds=0,
      source_github_audit_status=r["status"],
      plot_files=[f.name for f in pngs],
    )
    (a.output/"R4_source_figure_manifest.json").write_text(
        json.dumps(manifest,indent=2,ensure_ascii=False)+"\n")
    print("PR161_NEWSEED_R4_THREE_POPULATION_FIGURES_SOURCE_VALIDATED",
          json.dumps(manifest),flush=True)


if __name__=="__main__":
    main()
