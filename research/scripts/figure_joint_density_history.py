from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

out=Path(__file__).resolve().parents[1]/"results/joint_density_history_20261111"
data=pd.read_csv(out/"high_minus_low_odonate.csv").query("arm=='natural'").groupby("S_source").mean(numeric_only=True)
fig,axes=plt.subplots(1,2,figsize=(9,3.4),layout="constrained")
for ax,metrics,labels,title in [
    (axes[0],["log_F_start","log_retention","log_F_end"],["At entry","Season survival","At completion"],"Frog cohort (log scale)"),
    (axes[1],["H_D","H_S"],["From odonates","From caudates"],"Cumulative hazard per frog")]:
    pos=np.arange(len(metrics))
    for s,offset,color,label in [(0.25,-.18,"#398e88","Low caudate supply"),(2.,.18,"#67447f","High caudate supply")]:
        ax.bar(pos+offset,data.loc[s,metrics],width=.33,color=color,label=label)
    ax.axhline(0,color=".45",lw=.8)
    ax.set_xticks(pos,labels)
    ax.set_title(title)
    ax.spines[["top","right"]].set_visible(False)
axes[0].set_ylabel("High minus low odonate supply")
axes[1].legend(frameon=False,fontsize=8)
fig.savefig(out/"high_low_odonate.png",dpi=190)
