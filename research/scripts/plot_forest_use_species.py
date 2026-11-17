from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
root=Path(__file__).resolve().parents[1]/"results/forest_use_wetland_species_20261111"
d=pd.read_csv(root/"species.csv")
d=d[(d.scale=="rank") & (d.term=="woody_minus_herbaceous") & d.within_route.eq(0)]
names=["Pseudacris crucifer","Lithobates sylvaticus","Hyla versicolor","Lithobates clamitans","Lithobates catesbeianus","Lithobates palustris"]
fig,axes=plt.subplots(1,2,figsize=(8.4,3.6),sharey=True,sharex=True,layout="constrained")
for ax,domain,title in zip(axes,["all","shared_routes"],["Across 432 survey routes","Within the 45 shared routes¹"]):
    for j,s in enumerate(names):
        r=d[(d.species==s)&(d.domain==domain)].iloc[0]
        ax.errorbar(r.estimate,5-j,xerr=[[r.estimate-r.low],[r.high-r.estimate]],fmt="o",color="#216952" if j<3 else "#705842",capsize=3)
    ax.axvline(0,color="0.6",ls="--",lw=0.8)
    ax.axhline(2.5,color="0.8",lw=0.7)
    ax.set_yticks(range(6),names[::-1],fontstyle="italic")
    ax.set_title(title.replace("Within the 45 shared routes¹","Across 45 shared routes"),fontsize=11)
    ax.spines[["top","right"]].set_visible(False)
fig.supxlabel("Difference in odonate–calling slope change (woody minus herbaceous wetland)",fontsize=10)
fig.savefig(root/"species_contrasts.png",dpi=220)
