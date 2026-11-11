"""Plot daily contrasts in the original joint-sign, density-response subset."""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

OUT = Path(__file__).resolve().parents[1] / "results/matched_seasonal_hazard_20261111"
series = pd.read_csv(OUT / "daily.csv.gz").query("original_joint and litter == 1 and initial_frog == 1")
fig, axes = plt.subplots(4, 2, sharex=True, sharey="row", figsize=(9, 8.3))
metrics = [("frog_density", "Frogs remaining"),
           ("cumulative_caudate_kills", "Eaten by caudates\n(cumulative density)"),
           ("odonate_hazard_per_day", "Odonate hazard per\nsurviving frog / day"),
           ("cumulative_odonate_kills", "Eaten by odonates\n(cumulative density)")]
for v, column in enumerate(axes.T):
    for ax,(metric,label) in zip(column,metrics):
        for (arrival,duration),group in series[series.vegetation.eq(v)].groupby(["arrival","duration"]):
            table = group.pivot(index="day",columns="caudate_arm",values=metric)
            ax.plot(table.index,table.feeding_on-table.feeding_off,
                    color="#296b75" if arrival==0 else "#ae531c", ls="-" if duration==60 else "--",
                    label=f"Day {arrival}, {duration} days")
        ax.axhline(0,color=".5",lw=.6,zorder=0)
        if v==0: ax.set_ylabel(label)
        ax.spines[["right","top"]].set_visible(False)
    column[0].set_title(["Vegetation absent","Vegetation present"][v])
    column[-1].set_xlabel("Day of season")
handles,labels=axes[0,0].get_legend_handles_labels()
fig.legend(handles, labels, loc="upper center", ncol=4, frameon=False, bbox_to_anchor=(.5,.955))
fig.suptitle("Effect of allowing caudates to eat frogs", weight="bold")
fig.subplots_adjust(top=.84,bottom=.08,left=.16,right=.98,hspace=.23,wspace=.13)
fig.savefig(OUT/"feeding_timeseries.png",dpi=180)
