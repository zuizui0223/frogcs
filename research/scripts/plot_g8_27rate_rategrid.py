"""Plot all G8 rate conditions from the completed original-source 27-cell audit.

Shows every rate cell, no favorable-only selection. Source-conditional, pointwise
background-bootstrap intervals are not field confidence intervals.
"""
from __future__ import annotations
import argparse
from pathlib import Path
import numpy as np
import pandas as pd

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def main(directory: Path):
    directory=Path(directory)
    rates=pd.read_csv(directory/"g8_27rate_descriptive_counts.csv")
    summary=pd.read_csv(directory/"g8_full_27rate_compatibility_abundance_summary.csv",
                        dtype={"rate_id":str, "context":str})
    keys=["compatibility","frog_log_cohort"]
    lookup=summary[(summary.context=="pooled_3") &
                   (summary.metric.isin(keys))].set_index(["rate_id","metric"])
    assert len(rates)==27 and len(lookup)==(27+1)*len(keys)
    assert rates.rate_id.is_unique
    for rate in rates.itertuples(index=False):
        for metric in keys:
            assert (str(rate.rate_id),metric) in lookup.index
    fig,axes=plt.subplots(3,2,figsize=(13,10),sharex="col")
    x=np.arange(9)
    for i,attack in enumerate((.5,1.5,3.)):
        q=rates.loc[rates.attack==attack].sort_values(["rho","conversion"]).reset_index(drop=True)
        assert len(q)==9
        for k,metric in enumerate(keys):
            scale=100 if metric=="compatibility" else 1
            means=np.array([lookup.loc[(str(int(z.rate_id)),metric),"mean"] for z in q.itertuples(index=False)])*scale
            lower=np.array([lookup.loc[(str(int(z.rate_id)),metric),"pointwise_mc95_low"] for z in q.itertuples(index=False)])*scale
            upper=np.array([lookup.loc[(str(int(z.rate_id)),metric),"pointwise_mc95_high"] for z in q.itertuples(index=False)])*scale
            assert np.isfinite(means).all() and np.all(lower<=means) and np.all(means<=upper)
            ax=axes[i,k]
            ax.axhline(0,color="#757575",lw=.9,linestyle="--",zorder=0)
            ax.errorbar(x,means,yerr=np.vstack((means-lower,upper-means)),
                        fmt="o",markersize=4,capsize=2.5,elinewidth=1.1,
                        color="#286a91" if k==0 else "#a85a43")
            ax.set_title(f"Attack coefficient = {attack:g}",loc="left",fontsize=11,fontweight="bold")
            ax.grid(axis="y",alpha=.2)
            ax.spines["top"].set_visible(False);ax.spines["right"].set_visible(False)
            ax.set_xticks(x)
            ax.set_xticklabels([f"{rho:g} / {conv:g}" for rho,conv in zip(q.rho,q.conversion)],rotation=45,ha="right")
            if i==2:ax.set_xlabel("Local recruitment fraction / conversion",fontsize=10)
            if k==0:ax.set_ylabel("Sign compatibility 11−00 (points)",fontsize=10)
            else:ax.set_ylabel("Mean log frog cohort 11−00",fontsize=10)
    fig.suptitle("The same food webs generate interaction signs without consistent demographic benefits",
                 fontsize=14,fontweight="bold",y=.985)
    fig.text(.5,.015,"All 256 original backgrounds and three developmental contexts; 27 hypothetical rate cells. "
                    "Bars: pointwise 95% source-bootstrap ranges (10,000 paired draws). No field calibration.",
             ha="center",fontsize=8)
    fig.tight_layout(rect=(0,.04,1,.95),h_pad=1.4,w_pad=1.5)
    output=directory/"G8_27rate_pattern_vs_population.png"
    fig.savefig(output,dpi=200)
    plt.close(fig)
    print("G8_ALL_27_RATE_CELLS_FIGURE",output)
    return output

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--results",type=Path,required=True)
    args=p.parse_args()
    main(args.results)
