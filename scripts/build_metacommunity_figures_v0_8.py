#!/usr/bin/env python3
from pathlib import Path
import json
import matplotlib.pyplot as plt
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"figures_ecology_v0_8"
OUT.mkdir(exist_ok=True)
for old in OUT.glob("*.svg"):
    old.unlink()

def load(name):
    return json.loads((ROOT/name).read_text(encoding="utf-8"))

meta=load("NAAMP_METACOMMUNITY_ALPHA_BETA_GAMMA_SUMMARY_V0_1.json")
quad=load("NAAMP_SPECIES_STOP_QUADRANTS_SUMMARY_V0_1.json")
depth=load("NAAMP_WITHIN_ACTIVE_DEPTH_SUMMARY_V0_1.json")
det=load("NAAMP_DETECTION_QUALITY_ROBUSTNESS_SUMMARY_V0_1.json")
spatial=load("NAAMP_SPATIAL_TAXONOMIC_ACTIVATION_SUMMARY_V0_1.json")

def save(fig,name):
    fig.savefig(OUT/name,bbox_inches="tight")
    plt.close(fig)

def err(est,ci):
    return np.array([[est-ci[0]],[ci[1]-est]])

# Figure 1: multiscale expansion + beta + detection robustness
fig,axs=plt.subplots(2,2,figsize=(11,7.5))
ax=axs[0,0]
items=[
    ("Active stops",spatial["primary"]["delta_active_stops"]["beta"],spatial["primary"]["delta_active_stops"]["ci95"]),
    ("Local alpha",meta["primary"]["alpha_active"]["beta"],meta["primary"]["alpha_active"]["ci95"]),
    ("Route gamma",meta["primary"]["gamma"]["beta"],meta["primary"]["gamma"]["ci95"]),
]
for y,(lab,b,ci) in enumerate(items):
    ax.errorbar(b,y,xerr=err(b,ci),fmt="o",capsize=3)
ax.axvline(0,linewidth=1)
ax.set_yticks(range(len(items)),[x[0] for x in items])
ax.invert_yaxis()
ax.set_xlabel("Rain-contrast coefficient (native units)")
ax.set_title("A  Expansion across space and richness")
ax.text(.98,.04,"All three increase",transform=ax.transAxes,ha="right",va="bottom",fontsize=9)

ax=axs[0,1]
items=[
    ("Pairwise Sørensen",meta["primary"]["pairwise_sorensen_beta"]["beta"],meta["primary"]["pairwise_sorensen_beta"]["ci95"]),
    ("Normalized Whittaker",meta["primary"]["normalized_whittaker_beta"]["beta"],meta["primary"]["normalized_whittaker_beta"]["ci95"]),
]
for y,(lab,b,ci) in enumerate(items):
    ax.errorbar(b,y,xerr=err(b,ci),fmt="o",capsize=3)
ax.axvline(0,linewidth=1)
ax.set_yticks(range(len(items)),[x[0] for x in items])
ax.invert_yaxis()
ax.set_xlabel("Wet-minus-dry beta-diversity coefficient")
ax.set_title("B  Among-site differentiation")
ax.text(.98,.04,"No detectable shift",transform=ax.transAxes,ha="right",va="bottom",fontsize=9)

ax=axs[1,0]
labels=["Active stops","Local alpha","Route gamma"]
orig=[
    spatial["primary"]["delta_active_stops"]["beta"],
    meta["primary"]["alpha_active"]["beta"],
    meta["primary"]["gamma"]["beta"],
]
adj=[
    det["primary"]["active_stops"]["beta"],
    det["primary"]["alpha_active"]["beta"],
    det["primary"]["gamma_richness"]["beta"],
]
x=np.arange(3);w=.36
ax.bar(x-w/2,orig,width=w,label="Matched model")
ax.bar(x+w/2,adj,width=w,label="+ hearing/noise/wind")
ax.axhline(0,linewidth=1)
ax.set_xticks(x,labels,rotation=15,ha="right")
ax.set_ylabel("Rain-contrast coefficient")
ax.set_title("C  Recorded detection conditions")
ax.legend(frameon=False,fontsize=8)

ax=axs[1,1]
ax.axis("off")
txt=(
    "Matched design\n"
    f"{meta['matched_pairs']:,} wet–dry pairs\n"
    "same route × seasonal window\n\n"
    "Detection robustness\n"
    f"{det['primary_sample']['pairs']:,} pairs / {det['primary_sample']['routes']} routes\n"
    "hearing impairment + timeout + wind\n"
    "all three 95% CIs remain > 0\n\n"
    "Exact consecutive-year sensitivity\n"
    f"n = {meta['exact_consecutive_year']['n_pairs']:,}\n\n"
    "Ecological contrast\n"
    "larger active community\n"
    "without detectable homogenization"
)
ax.text(.04,.94,txt,va="top",ha="left",fontsize=11)
ax.set_title("D  Design and interpretation")
fig.suptitle("Rainfall-associated expansion enlarges the active community without detectable homogenization",fontsize=14)
fig.tight_layout(rect=[0,0,1,.96])
save(fig,"FIGURE_1_METACOMMUNITY_EXPANSION_V0_1.svg")

# Figure 2: incidence quadrants + local depth
fig,axs=plt.subplots(1,3,figsize=(14,5.2))

# A: conceptual 2 x 2 incidence matrix for the exact community decomposition.
ax=axs[0]
keys=[
    ["corner_expansion","taxonomic_deepening"],
    ["spatial_spread","within_core_rearrangement"],
]
share_matrix=np.array([
    [100*quad["components"][keys[0][0]]["fraction_total_beta"],
     100*quad["components"][keys[0][1]]["fraction_total_beta"]],
    [100*quad["components"][keys[1][0]]["fraction_total_beta"],
     100*quad["components"][keys[1][1]]["fraction_total_beta"]],
])
im=ax.imshow(share_matrix)
ax.set_xticks([0,1],["Dry-inactive stop","Dry-active stop"],rotation=15,ha="right")
ax.set_yticks([0,1],["Route-new species","Route-existing species"])
for i in range(2):
    for j in range(2):
        ax.text(j,i,f"{share_matrix[i,j]:.1f}%",ha="center",va="center")
ax.set_title("A  Where wet-gain incidences enter")
fig.colorbar(im,ax=ax,fraction=.046,pad=.04,label="Share of total incidence slope (%)")

# B: coefficient shares of the exact four-way community decomposition.
ax=axs[1]
flat_keys=["corner_expansion","spatial_spread","taxonomic_deepening","within_core_rearrangement"]
labs=["New species ×\nnew sites","Existing species ×\nnew sites","New species ×\nactive sites","Existing species ×\nactive sites"]
shares=[100*quad["components"][k]["fraction_total_beta"] for k in flat_keys]
bars=ax.barh(np.arange(4),shares)
ax.set_yticks(np.arange(4),labs)
ax.invert_yaxis()
ax.set_xlabel("Share of total rain-associated incidence slope (%)")
ax.set_xlim(0,max(shares)*1.25)
for b,v in zip(bars,shares):
    ax.text(v+0.8,b.get_y()+b.get_height()/2,f"{v:.1f}%",va="center")
ax.set_title("B  Exact community decomposition")

# C: local taxonomic depth.
ax=axs[2]
vals=[
    100*depth["primary"]["threshold_2plus_component"]["fraction_of_mean_beta"],
    100*depth["primary"]["deep_excess_beyond_two_component"]["fraction_of_mean_beta"],
]
labs2=["1 → ≥2 species","Multiplicity beyond\nsecond species"]
bars=ax.barh(np.arange(2),vals)
ax.set_yticks(np.arange(2),labs2)
ax.invert_yaxis()
ax.set_xlabel("Share of active-stop alpha slope (%)")
ax.set_xlim(0,100)
for b,v in zip(bars,vals):
    ax.text(v+1,b.get_y()+b.get_height()/2,f"{v:.1f}%",va="center")
ax.text(.02,.04,
        f"Same-stop alpha: β = {depth['primary']['shared_active_stop_delta_species_mean']['beta']:.3f}\n"
        f"P = {depth['primary']['shared_active_stop_delta_species_mean']['p_value']:.3g}",
        transform=ax.transAxes,va="bottom")
ax.set_title("C  Local taxonomic depth")
fig.suptitle("Most rainfall-associated incidence growth crosses matrix boundaries",fontsize=14)
fig.tight_layout(rect=[0,0,1,.94])
save(fig,"FIGURE_2_MATRIX_EXPANSION_V0_1.svg")

print("built",len(list(OUT.glob("*.svg"))),"figures")
