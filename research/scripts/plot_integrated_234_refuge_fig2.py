"""Reproducible manuscript Figure 2A/B from verified PR160 source audit CSVs.

Only plots *model-native* source-draw Monte Carlo effects. No model fitting,
field data transformations or synthetic regeneration occur in this script.
"""
from __future__ import annotations
import argparse
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

AXES = ("cover_SF", "cover_DS")
LABELS = [
    ("cover_SF", 0, "F sheltered from S · Context 0"),
    ("cover_SF", 1, "F sheltered from S · Context 1"),
    ("cover_SF", 2, "F sheltered from S · Context 2"),
    ("cover_DS", 0, "S sheltered from D · Context 0"),
    ("cover_DS", 1, "S sheltered from D · Context 1"),
    ("cover_DS", 2, "S sheltered from D · Context 2"),
]
ORIGINAL_FLOOR = "original_survival_floor_50"


def require_records(primary: pd.DataFrame, sensitivity: pd.DataFrame):
    if (primary.duplicated(["axis","stage_contrast","metric"]).any() or
        sensitivity.duplicated(["subset","axis","counterfactual_context","metric"]).any()):
        raise AssertionError("Source graph rows duplicated")
    if set(primary.axis) != set(AXES):
        raise AssertionError("Primary 96 accepted source axes missing")
    floor=sensitivity[sensitivity.subset == ORIGINAL_FLOOR].copy()
    if len(floor)!=36:
        raise AssertionError("Source floor must contain 2 axes x 3 contexts x 6 metrics")
    if not floor.n_source_draws.eq(50).all():
        raise AssertionError("Wrong floor-selection source count")
    for metric in ("delta_mean_log_F_B","delta_pass"):
        for axis,stage,_ in LABELS:
            aa=primary[(primary.axis==axis) & (primary.stage_contrast==str(stage)) & (primary.metric==metric)]
            bb=floor[(floor.axis==axis) & (floor.counterfactual_context==stage) & (floor.metric==metric)]
            if len(aa)!=1 or len(bb)!=1:
                raise AssertionError("Source plot would hide a missing arm")
    return floor


def triplet(primary, floor, metric, axis, stage, floor_flag, scale):
    if floor_flag:
        row=floor[(floor.axis==axis) & (floor.counterfactual_context==stage) &
                  (floor.metric==metric)].iloc[0]
        keys=("weighted_effect","bootstrap_95_low","bootstrap_95_high")
    else:
        row=primary[(primary.axis==axis) & (primary.stage_contrast==str(stage)) &
                    (primary.metric==metric)].iloc[0]
        keys=("weighted_mean","source_bootstrap_95_low","source_bootstrap_95_high")
    return tuple(scale*float(row[k]) for k in keys)


def render(primary, floor, metric, scale, xlabel, title, output):
    fig,ax=plt.subplots(figsize=(11.5,6.1))
    for offset,label,floor_flag in (
        (-.14,"All originally accepted sources (n=96)",False),
        (.14,"Original-context survival floor (n=50)",True),
    ):
        m=np.array([triplet(primary,floor,metric,axis,stage,floor_flag,scale)
                    for axis,stage,_ in LABELS])
        x=m[:,0]
        errors=np.vstack([x-m[:,1],m[:,2]-x])
        if (not np.isfinite(m).all() or (errors<0).any()):
            raise AssertionError("Invalid original source interval for Figure 2")
        ax.errorbar(x,np.arange(len(LABELS))+offset,xerr=errors,
                    marker="o",capsize=3,linestyle="none",label=label)
    ax.axvline(0,linewidth=1)
    ax.set_yticks(range(len(LABELS)),[x[2] for x in LABELS])
    ax.invert_yaxis()
    ax.set_xlabel(xlabel)
    ax.set_title(title)
    ax.grid(axis="x",alpha=.2)
    ax.legend(loc="lower right",fontsize=9)
    fig.text(.02,.013,
      "Error bars: 95% synthetic-source Monte Carlo intervals; not field CIs. Floor checked only in each draw's original context.",
      fontsize=8)
    fig.tight_layout(rect=(0,.05,1,1))
    fig.savefig(output,dpi=190)
    plt.close(fig)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--primary",required=True,type=Path)
    parser.add_argument("--sensitivity",required=True,type=Path)
    parser.add_argument("--output",required=True,type=Path)
    a=parser.parse_args()
    primary=pd.read_csv(a.primary)
    sensitivity=pd.read_csv(a.sensitivity)
    floor=require_records(primary,sensitivity)
    a.output.mkdir(parents=True,exist_ok=True)
    render(primary,floor,"delta_mean_log_F_B",1.0,
      "ON − OFF change in mean log aquatic frog cohort",
      "Figure 2A · Vegetation refuge and modelled frog abundance",
      a.output/"Figure2A_refuge_abundance.png")
    render(primary,floor,"delta_pass",100.0,
      "ON − OFF difference in four-sign compatibility (percentage points)",
      "Figure 2B · Vegetation refuge and four-sign interaction signature",
      a.output/"Figure2B_refuge_four_sign.png")
    print("FROGCS_FIGURE2_AB_ORIGINAL_SOURCE_AUDITED",str(a.output))


if __name__=="__main__":
    main()
