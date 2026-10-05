#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
DATA=json.loads((ROOT/"revision"/"PULSE_TEMPLATE_FIGURE_DATA_V0_1.json").read_text())
OUT=ROOT/"figures_pulse_template"
OUT.mkdir(exist_ok=True)

mpl.rcParams["svg.hashsalt"]="frogcs-pulse-template-rc3"

for legacy in (
    "fig3_higher_order_null_ladder.svg",
    "fig3_higher_order_null_ladder.png",
):
    (OUT/legacy).unlink(missing_ok=True)

def save(fig,name):
    fig.tight_layout()
    fig.savefig(
        OUT/f"{name}.svg",
        bbox_inches="tight",
        metadata={"Date": None},
    )
    fig.savefig(
        OUT/f"{name}.png",
        dpi=300,
        bbox_inches="tight",
        metadata={"Software": "Matplotlib"},
    )
    plt.close(fig)

# Figure 1: calling-state switch
x=DATA["figure1"]
fig,ax=plt.subplots(figsize=(8.4,5.2))
labels=["Total CallingIndex","0→positive","0→CI2/3","0→CI3","0→CI3\nsame observer + site"]
vals=[
    x["total_calling_index_beta"],
    x["zero_to_positive_beta"],
    x["zero_to_strong_beta"],
    x["zero_to_ci3_beta"],
    x["robust_zero_to_ci3_beta"],
]
y=np.arange(len(labels))

# The first three quantities are exact decomposition point estimates in the
# frozen figure data; only the direct CI3 endpoints have stored 95% CIs.
ax.plot(vals[:3],y[:3],marker="o",linestyle="None",markersize=7)
for yi,key in [(3,"zero_to_ci3"),(4,"robust_zero_to_ci3")]:
    b=x[f"{key}_beta"]; lo,hi=x[f"{key}_ci95"]
    ax.errorbar(b,yi,xerr=[[b-lo],[hi-b]],fmt="o",capsize=4,markersize=7)

ax.axhline(2.5,linewidth=.7)
ax.axvline(0,linewidth=.8)
ax.set_yticks(y,labels)
ax.invert_yaxis()
ax.set_xlabel("Rainfall-contrast coefficient")
ax.text(.98,.96,
        "Decomposition point estimates (top)\n"
        "Direct CI3 estimates with 95% CI (bottom)",
        transform=ax.transAxes,ha="right",va="top",fontsize=9)
ax.text(.98,.05,
        "65.3% of CallingIndex slope = 0→positive\n"
        "87.1% of activation = 0→CI2/3",
        transform=ax.transAxes,ha="right",va="bottom")
save(fig,"fig1_chorus_state_switch")

# Figure 2: spatial-depth shape
x=DATA["figure2"]
fig,ax=plt.subplots(figsize=(8.8,5.4))
depth=np.asarray(x["marginal_depths"],float)
obs=np.asarray(x["marginal_site_beta"],float)
u_mean=np.asarray(x["uniform_marginal_mean"],float)
u_ci=np.asarray(x["uniform_marginal_ci95"],float)
p_mean=np.asarray(x["persistence_marginal_mean"],float)
p_ci=np.asarray(x["persistence_marginal_ci95"],float)

ax.fill_between(depth,u_ci[:,0],u_ci[:,1],alpha=.16,label="Uniform activation 95%")
ax.fill_between(depth,p_ci[:,0],p_ci[:,1],alpha=.16,label="Persistence-preserving 95%")
ax.plot(depth,u_mean,marker="o",linewidth=1.5,label="Uniform activation mean")
ax.plot(depth,p_mean,marker="o",linewidth=1.5,label="Persistence-preserving mean")
ax.plot(depth,obs,marker="s",linewidth=2.6,label="Observed")
ax.set_xticks(depth)
ax.set_xlabel("Occupied-stop depth within a route-new taxon")
ax.set_ylabel("Marginal rainfall-contrast coefficient")
ax.legend(frameon=False,fontsize=8)
ax.text(.98,.97,
        "Depths 1–3 within uniform envelope\n"
        "Persistence null: depths 1–2 below, depth 3 within\n"
        "Depths 4–10 above both upper 95% envelopes\n"
        "Cumulative third+ β=0.473; 97.3% carried by CI2/3",
        transform=ax.transAxes,ha="right",va="top",fontsize=9)
save(fig,"fig2_spatial_depth_strong_chorus")

# Figure 3: principal conditional residual tests
x=DATA["figure3"]
labels=[
    "Principal species + prior-site + persistence comparator\npred. 1.353; observed 1.650",
    "Held-out rain × history gate\npred. 1.332; observed 1.650",
]
residuals=np.asarray([x["joint_residual"],x["final_gate_residual"]],float)
cis=np.asarray([x["joint_residual_ci95"],x["final_gate_residual_ci95"]],float)
y=np.arange(len(labels))

fig,ax=plt.subplots(figsize=(9.2,4.2))
for yi,(r,ci) in enumerate(zip(residuals,cis)):
    ax.hlines(yi,ci[0],ci[1],linewidth=7,alpha=.28)
    ax.plot([ci[0],ci[1]],[yi,yi],marker="|",linestyle="None",markersize=15)
    ax.plot(r,yi,marker="s",linestyle="None",markersize=8)
    ax.text(r+.012,yi,f"{r:.3f}",va="center",ha="left",fontsize=9)

ax.axvline(0,linewidth=.9)
ax.set_yticks(y,labels)
ax.invert_yaxis()
ax.set_xlabel("Conditional residual in within-taxon concentration coefficient")
ax.set_xlim(min(cis[:,0].min()-.04,-.18),max(residuals.max()+.10,.42))
ax.text(.02,.05,
        "horizontal bar = simulated 95% null-residual interval\n"
        "square = observed residual; both upper-tail P ≈ 0.001\n"
        "(minimum attainable with 1,000 simulations)",
        transform=ax.transAxes,ha="left",va="bottom",fontsize=9)
save(fig,"fig3_within_taxon_concentration")

# Figure 4: historical site targeting
x=DATA["figure4"]
labels=[
    "Prior strong site → wet CI2/3",
    "Prior strong site → wet CI3",
    "Same observer: prior strong → CI2/3",
    "Rain-selective CI3 targeting",
    "Rain-selective CI3 targeting, same observer",
]
vals=[
    x["prior_strong_wet_strong_beta"],
    x["prior_strong_wet_ci3_beta"],
    x["same_observer_prior_strong_beta"],
    x["rain_selective_ci3_beta"],
    x["rain_selective_same_observer_beta"],
]
cis=[
    x["prior_strong_wet_strong_ci95"],
    x["prior_strong_wet_ci3_ci95"],
    x["same_observer_prior_strong_ci95"],
    x["rain_selective_ci3_ci95"],
    x["rain_selective_same_observer_ci95"],
]
fig,ax=plt.subplots(figsize=(9.2,5.4))
y=np.arange(len(labels))
for yi,(b,ci) in enumerate(zip(vals,cis)):
    ax.errorbar(b,yi,xerr=[[b-ci[0]],[ci[1]-b]],fmt="o",capsize=4)
ax.set_yticks(y,labels)
ax.invert_yaxis()
ax.axvline(0,linewidth=.8)
ax.set_xlabel("Coefficient (95% CI)")
save(fig,"fig4_historical_site_targeting")

# Figure 5: breadth and heterogeneity
x=DATA["figure5"]
fig,axs=plt.subplots(1,2,figsize=(11.2,5.2))

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

save(fig,"fig5_breadth_and_heterogeneity")
