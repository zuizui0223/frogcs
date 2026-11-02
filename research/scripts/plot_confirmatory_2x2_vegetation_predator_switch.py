"""Two source-locked publication candidate figures of the genuine 80-year 2x2.

Only reads independently source-audited 480-row paired group and 256-background
MC intervals; no new simulation, ecological data fit, or model refit.
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

LABELS=("0","1","2","pooled")
ARM_ORDER=("00","10","01","11")
ARM_LABEL={
    "00":"Neither function",
    "10":"F sheltered from S",
    "01":"D→F feeding support",
    "11":"Both functions"
}


def value(t,metric,contrast,context):
    x=t[(t.metric==metric)&(t.contrast==contrast)&
        (t.context==context)]
    if len(x)!=1:
        raise AssertionError(f"Incomplete original source plot cell {metric} {contrast} {context}")
    r=x.iloc[0]
    vals=np.array([float(r["mean"]),float(r.ci95_low),float(r.ci95_high)])
    if not np.all(np.isfinite(vals)) or vals[1]>vals[0] or vals[0]>vals[2]:
        raise AssertionError("Invalid source MC 95% interval")
    return vals


def figure_pattern(t,out):
    fig,(a,b)=plt.subplots(1,2,figsize=(14.4,5.3),
                           gridspec_kw={"width_ratios":[1.45,1]})
    for i,arm in enumerate(ARM_ORDER):
        v=np.array([value(t,"accepted","arm_rate_"+arm,c)
                    for c in LABELS])*100
        x=np.arange(4)+(.16*(i-1.5))
        a.errorbar(x,v[:,0],yerr=np.vstack([v[:,0]-v[:,1],v[:,2]-v[:,0]]),
                   marker="o",linestyle="-",capsize=3,label=ARM_LABEL[arm])
    a.set_xticks(np.arange(4),["Stage 0","Stage 1","Stage 2","Pooled"])
    a.set_ylabel("Four-sign compatibility (%)")
    a.set_title("A · Four original legal plant-function arms")
    a.grid(axis="y",alpha=.2)
    a.legend(loc="upper right",fontsize=8)
    v=np.array([value(t,"accepted","factorial_synergy",c)
                for c in LABELS])*100
    b.errorbar(np.arange(4),v[:,0],
               yerr=np.vstack([v[:,0]-v[:,1],v[:,2]-v[:,0]]),
               marker="o",linestyle="none",capsize=4)
    b.axhline(0,color="gray",lw=1)
    b.set_xticks(np.arange(4),["0","1","2","Pooled"])
    b.set_ylabel("Two-factor synergy in compatibility (percentage points)")
    b.set_title("B · Nonadditive 2×2 effect")
    b.grid(axis="y",alpha=.2)
    fig.suptitle("New independent seed: original 80-year canonical vegetation 2×2")
    fig.text(.02,.014,
       "95% source-background bootstrap ranges; 256 original model structures, 3 repeated stages. "
       "NOT a field posterior or measured trophic interaction.",fontsize=8)
    fig.tight_layout(rect=(0,.05,1,.93))
    fig.savefig(out/"Figure_R2_plant2x2_newseed_pattern_and_synergy.png",dpi=200)
    plt.close(fig)


def figure_hazard(t,out):
    fig,(a,b)=plt.subplots(1,2,figsize=(13.5,5.2))
    for arm,label,offset in [("00","Neither function",-.12),
                              ("11","Both functions",.12)]:
        h=np.array([value(t,"D_F_hazard_share_V1_S2_D2",
                          "arm_rate_"+arm,ctx) for ctx in LABELS[:3]])*100
        x=np.arange(3)+offset
        a.errorbar(x,h[:,0],yerr=np.vstack([h[:,0]-h[:,1],h[:,2]-h[:,0]]),
                   marker="o",linestyle="-",capsize=3,label=label)
    a.set_xticks(np.arange(3),["Stage 0","Stage 1","Stage 2"])
    a.set_ylim(0,100)
    a.set_ylabel("D→F fraction of S→F + D→F integrated hazard (%)")
    a.set_title("A · Predator-specific per-frog hazard share at V1/S2/D2")
    a.grid(axis="y",alpha=.2)
    a.legend(loc="lower left",fontsize=9)
    rows=np.array([value(t,"mean_log_F_B","both_minus_neither",ctx)
                   for ctx in LABELS])
    x=np.arange(4)
    b.errorbar(x,rows[:,0],yerr=np.vstack([rows[:,0]-rows[:,1],
                                           rows[:,2]-rows[:,0]]),
               marker="o",capsize=4,linestyle="none")
    b.axhline(0,color="gray",linewidth=1)
    b.set_xticks(x,["0","1","2","Pooled"])
    b.set_ylabel("Modelled mean log aquatic F cohort: both − neither")
    b.set_title("B · Four-sign generation ≠ F abundance benefit")
    b.grid(axis="y",alpha=.2)
    fig.suptitle("Plant functions shift model hazard allocation, but not uniformly frog abundance")
    fig.text(.015,.012,
       "Per-frog predator H is a season-integrated MODEL hazard, not observed tadpole deaths. "
       "95% source-background Monte Carlo intervals.",fontsize=8)
    fig.tight_layout(rect=(0,.055,1,.93))
    fig.savefig(out/"Figure_R3_hazard_share_vs_frog_cohort_newseed.png",dpi=200)
    plt.close(fig)


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source-table",type=Path,required=True)
    p.add_argument("--original-receipt",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    t=pd.read_csv(a.source_table,dtype={"context":str})
    receipt=json.loads(a.original_receipt.read_text())
    if (receipt.get("status")!="CONFIRMATORY_NEW_SEED_PAIRED_2x2_ORIGINAL_80Y_SOURCE_AUDIT_SUCCESS"
        or receipt.get("new_80year_model_proposals")!=3072
        or receipt.get("original_80year_vertices")!=24576
        or len(t)!=480):
        raise AssertionError("Original complete true80y audited source 2×2 result absent")
    a.out.mkdir(parents=True,exist_ok=True)
    figure_pattern(t,a.out)
    figure_hazard(t,a.out)
    source=pd.DataFrame([
        dict(component="four-sign generation and paired synergy",
             file="Figure_R2_plant2x2_newseed_pattern_and_synergy.png"),
        dict(component="relative predator hazard and frog abundance",
             file="Figure_R3_hazard_share_vs_frog_cohort_newseed.png")
    ])
    source.to_csv(a.out/"figure_source_manifest.csv",index=False)
    if any(x.stat().st_size<20000 for x in a.out.glob("Figure_*.png")):
        raise AssertionError("Publication model-native figure appears empty")
    print("CONFIRMATORY_2x2_FIGURES_2_PANELS_SOURCE_VERIFIED",str(a.out))


if __name__=="__main__":
    main()
