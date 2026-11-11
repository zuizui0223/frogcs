"""Plot the paired wetland contrasts for the manuscript from the saved estimates."""
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
d=Path(__file__).resolve().parents[1]/"results/annual_nlcd_wetlands_20261111"
data=pd.read_csv(d/"coefficients.csv")
data=data[(data.background=="uniform") & ~data.within_route]
fig,axes=plt.subplots(1,2,figsize=(8,2.9),layout="constrained",sharey=True)
for ax,scale,title in zip(axes,["10_percentage_points","standardized_rank"],["A   Equal area (+10 percentage points)","B   Equal change in cover rank (+1 SD)"]):
    for row,(term,color) in enumerate(zip(["odonate_x_herb","odonate_x_woody","herb_minus_woody"],["#1d7762","#785338","#293c50"])):
        r=data[(data.scale==scale)&(data.term==term)].iloc[0]
        ax.errorbar(r.estimate,2-row,xerr=[[r.estimate-r.low],[r.high-r.estimate]],fmt="D" if row==2 else "o",color=color,capsize=3)
    ax.axvline(0,color="0.5",ls="--",lw=.8)
    ax.set_title(title,fontsize=10,loc="left")
    ax.set_xlabel("Change in odonate–calling slope",fontsize=9)
    ax.set_ylim(-.55,2.55)
    ax.set_yticks([2,1,0],["Herbaceous","Woody","Herbaceous − woody"])
    ax.spines[["right","top"]].set_visible(False)
fig.savefig(d/"figure_s9.png",dpi=240,bbox_inches="tight")
