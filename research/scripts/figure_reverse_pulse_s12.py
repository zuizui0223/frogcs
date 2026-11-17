"""Draw paired next-season outcomes for every reverse-predation calendar."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "results/reverse_pulse_20261111"
data = pd.read_csv(OUT / "calendar_summary.csv")
order = [(f,0,0) for f in (0,20,40,60,71,78,84)] + [(78,78,0),(78,0,78),(78,78,78)]
fig, axes = plt.subplots(1,2,figsize=(9,5.7), sharey=True)
for ax,(metric,title) in zip(axes,[("next_yago","A   Next-season odonate larval density"),
                                    ("next_H_DF","B   Next-season hazard per tadpole")]):
    values = data.pivot(index=["frog_delay","s_delay","d_delay"],columns="vegetation",values=metric+"_difference").loc[order]
    ax.imshow(-values,aspect="auto",cmap="Blues",vmin=0,vmax=-values.min().min())
    for i,key in enumerate(order):
        for v in (0,1):
            row = data.set_index(["frog_delay","s_delay","d_delay","vegetation"]).loc[(*key,v)]
            ax.text(v,i,f"{row[metric+'_off']:.3f} → {row[metric+'_on']:.3f}",ha="center",va="center",
                    color="white" if -values.iloc[i,v]>-.53*values.min().min() else "black",fontsize=9)
    ax.set_xticks([0,1],["No vegetation","Vegetation"])
    ax.tick_params(length=0)
    ax.set_title(title,fontsize=11)
axes[0].set_yticks(range(len(order)),[" / ".join(map(str,k)) for k in order])
axes[0].set_ylabel("Delay in days (frog / salamander / odonate)")
fig.suptitle("Effect of frog predation during odonate emergence")
fig.text(.54,.02,"Cells show pathway off → on. Darker shading marks a larger decrease within each panel.",ha="center",fontsize=9)
fig.tight_layout(rect=(0,.04,1,.97))
fig.savefig(OUT/"figure_s12.png",dpi=240)
