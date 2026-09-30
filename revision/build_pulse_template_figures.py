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
    fig.savefig(OUT/f"{name}.png",dpi=300,bbox_inches="tight")
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

# Figure 3: within-taxon multi-site concentration
x=DATA["figure3"]
labels=[
    "Principal: species + prior site history",
    "+ held-out rain × history gate",
    "Cross-fit species response",
    "Uniform activation",
    "Dry-state persistence",
]
obs=[
    x["prior_subset_observed"],
    x["prior_subset_observed"],
    x["full_observed"],
    x["full_observed"],
    x["full_observed"],
]
pred=[
    x["joint_predicted"],
    x["final_gate_predicted"],
    x["species_predicted"],
    x["uniform_predicted"],
    x["persistence_predicted"],
]
fig,ax=plt.subplots(figsize=(9.4,5.7))
y=np.arange(len(labels))
for yi,(o,p) in enumerate(zip(obs,pred)):
    lw=3 if yi<2 else 1.8
    ax.plot([p,o],[yi,yi],linewidth=lw)
    ax.plot(p,yi,marker="o",linestyle="None")
    ax.plot(o,yi,marker="s",linestyle="None")
ax.set_yticks(y,labels)
ax.invert_yaxis()
ax.set_xlabel("Within-taxon concentration rainfall coefficient")
ax.set_title("Fig. 3  Species and site propensities underpredict multi-site concentration")
ax.text(.99,.04,
        "circle = comparator prediction at observed recruitment + spread\n"
        "square = observed; all conditional P = 0.000999\n"
        f"secondary exchangeable N,K diagnostic: raw β={x['exact_raw_beta']:.3f} "
        f"({x['exact_raw_ci95'][0]:.3f}–{x['exact_raw_ci95'][1]:.3f})",
        transform=ax.transAxes,ha="right",va="bottom")
save(fig,"fig3_within_taxon_concentration")

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
fig,axs=plt.subplots(1,2,figsize=(11.2,5.4))

# A. Taxonomic breadth / concentration
ax=axs[0]
cats=["Positive taxa","≥1% positive mass","Top-5 positive mass","Top-1 positive mass"]
vals=[
    x["taxa_positive"]/x["taxa_total"],
    x["taxa_ge_1pct"]/x["taxa_total"],
    x["top5_positive_share"],
    x["top1_positive_share"],
]
y=np.arange(len(cats))
ax.barh(y,vals,alpha=.78)
ax.set_yticks(y,cats)
ax.invert_yaxis()
ax.set_xlim(0,1)
ax.set_xlabel("Proportion")
ax.set_title("A  Taxonomic breadth")
for yi,v in enumerate(vals):
    ax.text(min(v+.025,.92),yi,f"{100*v:.1f}%",va="center")
ax.text(.02,.03,
        f"{x['taxa_positive']}/{x['taxa_total']} taxa positive; "
        f"HHI={x['hhi']:.3f}\n"
        f"All leave-one-taxon totals >0; min β={x['min_leave_one_taxon_beta']:.3f}",
        transform=ax.transAxes,va="bottom")

# B. Geographic robustness versus heterogeneity
ax=axs[1]
lo,hi=x["loo_state_beta_range"]
ax.hlines(2,lo,hi,linewidth=5)
ax.plot([lo,hi],[2,2],marker="|",linestyle="None",markersize=14)
ax.axvline(0,linewidth=.8)
ax.scatter([x["loo_state_min_ci_lower"]],[1],s=55)
ax.barh([0.35,0.0],
        [x["state_positive"]/x["state_estimable"],
         x["state_positive_ci"]/x["state_estimable"]],
        height=.22,alpha=.78)
ax.text(.02,.35,
        f"{x['state_positive']}/{x['state_estimable']} positive state slopes",
        va="center")
ax.text(.02,0.0,
        f"{x['state_positive_ci']}/{x['state_estimable']} state CIs >0",
        va="center")
ax.set_yticks([2,1],["Leave-one-state β range","Smallest LOO CI lower"])
ax.set_ylim(-.45,2.45)
ax.set_xlim(min(0,lo)-.1,max(hi,1)+.15)
ax.set_xlabel("Coefficient / proportion")
ax.set_title("B  Robust pooled signal, heterogeneous states")
ax.text(.02,.73,
        "21/21 state omissions retain positive coefficients and CIs\n"
        "State-specific slopes are much less uniform",
        transform=ax.transAxes,va="top")

fig.suptitle("Fig. 5  Within-taxon multi-site concentration is broad but geographically heterogeneous",y=1.02)
save(fig,"fig5_breadth_and_heterogeneity")
