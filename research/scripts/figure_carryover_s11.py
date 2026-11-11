"""Figure S11 from the paired seasonal replays of the selected 1,925 draws."""
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

out = Path(__file__).resolve().parents[1] / "results/joint_density_history_20261111"
data = pd.read_csv(out / "interaction_by_vegetation.csv").set_index(["arm","vegetation"])
fig, axes = plt.subplots(1, 2, figsize=(9, 3.8))
for pos, (v, color, label) in enumerate([(0,"#986634","Vegetation absent"), (1,"#237467","Vegetation present")]):
    offset = (pos-.5)*.34
    natural = data.loc[("natural",v)]
    axes[0].bar(np.arange(2)+offset, natural[["H_D","H_S"]], width=.33,color=color,label=label)
    axes[1].bar(np.arange(2)+offset,[natural.log_F_end,data.loc[("common_frog",v),"log_F_end"]],width=.33,color=color)
mean = pd.read_csv(out/"interaction_summary.csv").set_index("arm")
axes[1].plot([0,1],mean.loc[["natural","common_frog"],"log_F_end"], "kD",ms=5,label="Vegetation average")
for ax, title, ylabel, labels in [
    (axes[0],"A   Seasonal predation","Interaction in per-frog cumulative hazard",["Odonate hazard","Caudate hazard"]),
    (axes[1],"B   Frogs completing the aquatic stage","Interaction in log cohort size",["Inherited entry density","Equal frog entry density"])]:
    ax.set_title(title,loc="left",fontsize=11)
    ax.set_ylabel(ylabel,fontsize=9)
    ax.axhline(0,color="0.4",lw=.8)
    ax.set_xticks([0,1],labels,fontsize=9)
    ax.spines[["top","right"]].set_visible(False)
h,l=axes[0].get_legend_handles_labels()
h2,l2=axes[1].get_legend_handles_labels()
fig.legend(h+h2,l+l2,loc="lower center",ncol=3,frameon=False)
fig.subplots_adjust(bottom=.23,left=.1,right=.98,wspace=.37,top=.88)
fig.savefig(out/"figure_s11.png",dpi=210)
