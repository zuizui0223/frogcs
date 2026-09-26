#!/usr/bin/env python3
from pathlib import Path
import json
import matplotlib.pyplot as plt
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"figures_ecology_v0_8"
OUT.mkdir(exist_ok=True)

def load(name):
    return json.loads((ROOT/name).read_text(encoding="utf-8"))

meta=load("NAAMP_METACOMMUNITY_ALPHA_BETA_GAMMA_SUMMARY_V0_1.json")
quad=load("NAAMP_SPECIES_STOP_QUADRANTS_SUMMARY_V0_1.json")
depth=load("NAAMP_WITHIN_ACTIVE_DEPTH_SUMMARY_V0_1.json")
func=load("NAAMP_FUNCTIONAL_COMMUNITY_EXPANSION_SUMMARY_V0_1.json")
resp=load("NAAMP_FUNCTIONAL_RESPONSE_DECOUPLING_SUMMARY_V0_1.json")
buff=load("NAAMP_RESPONSE_DIVERSITY_BUFFERING_SUMMARY_V0_1.json")
geometry=load("NAAMP_SPECIES_ACTIVATION_GEOMETRY_REPEATABILITY_SUMMARY_V0_1.json")
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
ax.set_title("A  Spatial footprint, alpha and gamma")

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
ax.set_title("B  Among-active-site beta diversity")

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
    f"n = {meta['exact_consecutive_year']['n_pairs']:,}"
)
ax.text(.04,.94,txt,va="top",ha="left",fontsize=11)
ax.set_title("D  Design and robustness")
fig.suptitle("Recent rainfall expands the acoustically active community across scales",fontsize=14)
fig.tight_layout(rect=[0,0,1,.96])
save(fig,"FIGURE_1_METACOMMUNITY_EXPANSION_V0_1.svg")

# Figure 2: incidence quadrants + local depth
fig,axs=plt.subplots(1,2,figsize=(11,5.2))
ax=axs[0]
keys=["corner_expansion","spatial_spread","taxonomic_deepening","within_core_rearrangement"]
labs=["New species ×\nnew sites","Existing species ×\nnew sites","New species ×\nactive sites","Existing species ×\nactive sites"]
shares=[100*quad["components"][k]["fraction_total_beta"] for k in keys]
bars=ax.barh(np.arange(4),shares)
ax.set_yticks(np.arange(4),labs)
ax.invert_yaxis()
ax.set_xlabel("Share of total rain-associated incidence slope (%)")
ax.set_xlim(0,max(shares)*1.25)
for b,v in zip(bars,shares):
    ax.text(v+0.8,b.get_y()+b.get_height()/2,f"{v:.1f}%",va="center")
ax.set_title("A  Exact species × site decomposition")

ax=axs[1]
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
ax.set_title("B  Local taxonomic depth")
fig.suptitle("Rainfall-associated expansion occurs mainly at matrix boundaries",fontsize=14)
fig.tight_layout(rect=[0,0,1,.94])
save(fig,"FIGURE_2_MATRIX_EXPANSION_V0_1.svg")

# Figure 3: taxonomic, functional, response dimensions
fig,axs=plt.subplots(1,3,figsize=(12,4.8))
ax=axs[0]
items=[
    ("Trait-covered\nrichness",func["primary"]["trait_covered_richness"]),
    ("Functional MPD",func["primary"]["functional_mpd"]),
    ("Novelty balance",func["primary"]["functional_novelty_balance"]),
]
for y,(lab,o) in enumerate(items):
    b=o["beta"];ci=o["ci95"]
    ax.errorbar(b,y,xerr=err(b,ci),fmt="o",capsize=3)
ax.axvline(0,linewidth=1)
ax.set_yticks(range(3),[x[0] for x in items])
ax.invert_yaxis()
ax.set_xlabel("Rain-contrast coefficient")
ax.set_title("A  Functional community")

ax=axs[1]
ax.axvline(0,linewidth=1)
r=resp["primary"]["correlation"]
ax.scatter([r],[0])
ax.set_xlim(-.5,.5)
ax.set_ylim(-1,1)
ax.set_yticks([])
ax.set_xlabel("Correlation: functional distance\nvs rainfall-response difference")
ax.text(.05,.80,
        f"r = {r:.3f}\nPermutation P = {resp['primary']['two_sided_p']:.3f}\n"
        f"Within-family P = {resp['family_stratified']['two_sided_p']:.3f}",
        transform=ax.transAxes)
ax.set_title("B  Functional vs response diversity")

ax=axs[2]
xs=np.array([r["early"] for r in geometry["species_table"]],float)
ys=np.array([r["late"] for r in geometry["species_table"]],float)
lims=[min(xs.min(),ys.min())-.15,max(xs.max(),ys.max())+.15]
ax.scatter(xs,ys)
ax.plot(lims,lims,linewidth=1)
ax.axhline(0,linewidth=.8)
ax.axvline(0,linewidth=.8)
ax.set_xlim(lims);ax.set_ylim(lims)
ax.set_xlabel("Early activation geometry")
ax.set_ylabel("Late activation geometry")
ax.text(.04,.96,
        f"ρ = {geometry['primary']['spearman_rho']:.3f}\n"
        f"P = {geometry['primary']['p_value']:.4f}\n"
        f"same sign = {geometry['sign_concordance']['same_sign']}/{geometry['sign_concordance']['n_species']}",
        transform=ax.transAxes,va="top")
ax.set_title("C  Repeatable activation geometry")
fig.suptitle("Conventional functional traits and response geometry describe different dimensions",fontsize=14)
fig.tight_layout(rect=[0,0,1,.94])
save(fig,"FIGURE_3_FUNCTIONAL_RESPONSE_DIVERSITY_V0_1.svg")

print("built",len(list(OUT.glob("*.svg"))),"figures")
