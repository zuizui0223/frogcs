"""Source-backed schematic of original R2 regime and same-draw R4 consequences.

Points are mean paired S->F moderation of the annual movement effect at
year80 with SOURCE-DRAW Monte Carlo resampling, NOT wild estimates. The
weak/high-rho regime and its two-plant subset were chosen retrospectively
from R2 model-prior sources and are not independent confirmations.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

LABELS=[
  ("all_96","All model-compatible sources (n=96)"),
  ("weak_attack_high_rho_23","Weak attack / high recruitment (n=23)"),
  ("weak_high_rho_with_double_plant_14","Same regime + two plant roles (n=14)"),
]


def parse():
    p=argparse.ArgumentParser()
    p.add_argument("--full-source-interval",type=Path,required=True)
    p.add_argument("--conditional-source-effects",type=Path,required=True)
    p.add_argument("--conditional-receipt",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    return p.parse_args()


def main():
    a=parse()
    orig=pd.read_csv(a.full_source_interval)
    cond=pd.read_csv(a.conditional_source_effects)
    receipt=json.loads(a.conditional_receipt.read_text())
    if (receipt["status"]!="R2_RATE_REGION_SAME_ORIGINAL_R3_R4_SOURCE_MATCHED_AUDIT_SUCCESS"
        or len(orig)!=2 or set(orig.q)!={3,12}
        or set(cond.regime)!=set(x[0] for x in LABELS[1:])):
        raise AssertionError("Incompatible R2/R3/R4 conditional source records")
    series=[]
    for name,label in LABELS:
        for q in (3,12):
            if name=="all_96":
                z=orig[orig.q==q].iloc[0]
                mean,lo,hi=float(z.mean_weighted_moderation),float(z.bootstrap_mc_low),float(z.bootstrap_mc_high)
            else:
                z=cond[(cond.regime==name)&(cond.component=="R4_longrun")&
                       (cond.q==q)&(cond.measure=="edge_moderation_of_movement_occupied_year80")]
                if len(z)!=1:raise AssertionError("R4 conditional source endpoint unavailable")
                z=z.iloc[0]
                mean,lo,hi=float(z.weighted_mean),float(z.mc95_low),float(z.mc95_high)
            if not np.isfinite([mean,lo,hi]).all() or not lo<=mean<=hi:
                raise AssertionError("Invalid source-draw MC interval")
            series.append(dict(regime=name,caption=label,q=q,mean=mean,low=lo,high=hi))
    d=pd.DataFrame(series)
    a.out.mkdir(parents=True,exist_ok=True)
    fig,ax=plt.subplots(figsize=(10.6,5.2))
    for i,q in enumerate((3,12)):
        z=d[d.q==q].set_index("regime")
        x=np.arange(3)+(-.11 if q==3 else .11)
        v=z.loc[[x[0] for x in LABELS],"mean"].to_numpy()
        l=z.loc[[x[0] for x in LABELS],"low"].to_numpy()
        u=z.loc[[x[0] for x in LABELS],"high"].to_numpy()
        ax.errorbar(v,x,xerr=np.vstack([v-l,u-v]),marker="o",linestyle="none",
                    capsize=4,label=f"q = {q}")
    ax.axvline(0,color="gray",linewidth=1)
    ax.set_yticks(np.arange(3),[x[1] for x in LABELS])
    ax.invert_yaxis()
    ax.set_xlabel("S→F predation-specific moderation of movement effect\n"
                  "(difference-in-differences in synthetic year-80 F occupied patches)")
    ax.set_title("Same-source R2 regime → R4 long-run consequence")
    ax.legend(loc="lower right",fontsize=9)
    ax.grid(axis="x",alpha=.2)
    fig.text(.02,.013,"Error bars: source-draw Monte Carlo ranges; exploratory conditioned model rates, NOT field CIs.",fontsize=8)
    fig.tight_layout(rect=(0,.045,1,.97))
    fig.savefig(a.out/"Figure_R4_rate_regime_conditioned_movement.png",dpi=190)
    plt.close(fig)
    d.to_csv(a.out/"Figure_R4_rate_regime_moderation_source_table.csv",index=False)
    print("FROGCS_R2_R4_SOURCE_CONDITIONAL_FIGURE_VERIFIED",len(d),"source units")
    return d


if __name__=="__main__":
    main()
