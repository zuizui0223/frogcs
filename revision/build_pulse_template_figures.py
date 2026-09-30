#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
DATA=json.loads((ROOT/"revision"/"PULSE_TEMPLATE_FIGURE_DATA_V0_1.json").read_text())
OUT=ROOT/"figures_pulse_template"
OUT.mkdir(exist_ok=True)

def save(fig,name):
    fig.tight_layout()
    fig.savefig(OUT/f"{name}.svg",bbox_inches="tight")
    fig.savefig(OUT/f"{name}.png",dpi=240,bbox_inches="tight")
    plt.close(fig)

# Figure 1: calling-state switch
x=DATA["figure1"]
fig,ax=plt.subplots(figsize=(8.4,5.4))
labels=["Total CallingIndex","0→positive","0→CI2/3","0→CI3","0→CI3\nsame observer + site"]
vals=[x["total_calling_index_beta"],x["zero_to_positive_beta"],x["zero_to_strong_beta"],x["zero_to_ci3_beta"],x["robust_zero_to_ci3_beta"]]
y=np.arange(len(labels))
ax.barh(y[:3],vals[:3],alpha=.75)
for yi,key in [(3,"zero_to_ci3"),(4,"robust_zero_to_ci3")]:
    b=x[f"{key}_beta"]; lo,hi=x[f"{key}_ci95"]
    ax.errorbar(b,yi,xerr=[[b-lo],[hi-b]],fmt="o",capsize=4)
ax.set_yticks(y,labels)
ax.invert_yaxis()
ax.axvline(0,linewidth=.8)
ax.set_xlabel("Rainfall-contrast coefficient")
ax.set_title("Fig. 1  Rain-associated change enters from silence and often as strong chorus")
ax.text(.98,.05,f"65.3% of CallingIndex slope = 0→positive\n87.1% of activation = 0→CI2/3",transform=ax.transAxes,ha="right",va="bottom")
save(fig,"fig1_chorus_state_switch")

# Figure 2: spatial depth
x=DATA["figure2"]
fig,ax=plt.subplots(figsize=(8.4,5.2))
labels=["Second occupied site","Third and later sites","Fourth and later sites"]
vals=[x["second_stop_beta"],x["third_plus_beta"],x["fourth_plus_beta"]]
y=np.arange(3)
ax.barh(y,vals,alpha=.75)
ax.set_yticks(y,labels)
ax.invert_yaxis()
ax.axvline(0,linewidth=.8)
ax.set_xlabel("Rainfall-contrast coefficient")
ax.set_title("Fig. 2  The unusual spatial response begins beyond the second site")
ax.text(.98,.08,"Third+ coefficient: 97.3% carried by CI2/3\nSame-observer + same-site: 95.4%",transform=ax.transAxes,ha="right",va="bottom")
save(fig,"fig2_spatial_depth_strong_chorus")

# Figure 3: higher-order conditional excess
x=DATA["figure3"]
labels=["Uniform activation","Dry-state persistence","Cross-fit species response","Species + prior site history"]
obs=[x["full_observed"],x["full_observed"],x["full_observed"],x["prior_subset_observed"]]
pred=[x["uniform_predicted"],x["persistence_predicted"],x["species_predicted"],x["joint_predicted"]]
fig,ax=plt.subplots(figsize=(9.2,5.4))
y=np.arange(len(labels))
for yi,(o,p) in enumerate(zip(obs,pred)):
    ax.plot([p,o],[yi,yi],linewidth=2)
    ax.plot(p,yi,marker="o",linestyle="None")
    ax.plot(o,yi,marker="s",linestyle="None")
ax.set_yticks(y,labels)
ax.invert_yaxis()
ax.set_xlabel("Higher-order within-taxon rainfall coefficient")
ax.set_title("Fig. 3  First-order species and site propensities underpredict higher-order concentration")
ax.text(.99,.04,"circle = null prediction at observed recruitment + spread\nsquare = observed; all conditional P = 0.000999",transform=ax.transAxes,ha="right",va="bottom")
save(fig,"fig3_higher_order_null_ladder")

# Figure 4: historical site targeting
x=DATA["figure4"]
labels=["Prior strong site → wet CI2/3","Prior strong site → wet CI3","Same observer: prior strong → CI2/3","Rain-selective CI3 targeting","Rain-selective CI3 targeting, same observer"]
vals=[x["prior_strong_wet_strong_beta"],x["prior_strong_wet_ci3_beta"],x["same_observer_prior_strong_beta"],x["rain_selective_ci3_beta"],x["rain_selective_same_observer_beta"]]
cis=[x["prior_strong_wet_strong_ci95"],x["prior_strong_wet_ci3_ci95"],x["same_observer_prior_strong_ci95"],x["rain_selective_ci3_ci95"],x["rain_selective_same_observer_ci95"]]
fig,ax=plt.subplots(figsize=(9.2,5.6))
y=np.arange(len(labels))
for yi,(b,ci) in enumerate(zip(vals,cis)):
    ax.errorbar(b,yi,xerr=[[b-ci[0]],[ci[1]-b]],fmt="o",capsize=4)
ax.set_yticks(y,labels)
ax.invert_yaxis()
ax.axvline(0,linewidth=.8)
ax.set_xlabel("Coefficient (95% CI)")
ax.set_title("Fig. 4  Strong chorus placement recurs at species-specific historical sites")
save(fig,"fig4_historical_site_targeting")

# Figure 5: breadth and heterogeneity
x=DATA["figure5"]
fig,ax=plt.subplots(figsize=(9.2,5.6))
ax.axis("off")
lines=[
    "Higher-order coherence is broad, but not homogeneous",
    "",
    f"Taxonomic breadth: {x['taxa_positive']}/{x['taxa_total']} taxa positive; {x['taxa_ge_1pct']} contribute ≥1% of positive mass",
    f"Concentration: top 1 = {100*x['top1_positive_share']:.1f}%; top 5 = {100*x['top5_positive_share']:.1f}%; HHI = {x['hhi']:.3f}",
    f"Every leave-one-taxon-out total remains positive; minimum β = {x['min_leave_one_taxon_beta']:.3f}",
    "",
    f"Geographic robustness: 21/21 leave-one-state-out coefficients and CIs positive",
    f"Leave-one-state-out β range = {x['loo_state_beta_range'][0]:.3f}–{x['loo_state_beta_range'][1]:.3f}",
    f"Smallest leave-one-state-out CI lower bound = {x['loo_state_min_ci_lower']:.3f}",
    "",
    f"State-specific heterogeneity: {x['state_positive']}/{x['state_estimable']} positive point estimates; {x['state_positive_ci']}/{x['state_estimable']} positive 95% CIs"
]
for i,line in enumerate(lines):
    ax.text(.04,.95-i*.078,line,transform=ax.transAxes,va="top",fontsize=12 if i else 15,weight="bold" if i==0 else "normal")
save(fig,"fig5_breadth_and_heterogeneity")
