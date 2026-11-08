"""Source-backed B/C/D editorial figure composites. NO new ecological analysis.
Reads frozen INBO/USGS outputs, checks historical signed C coefficients,
and plots already-audited model numeric summaries. Never infer mechanism from calls.
"""
from pathlib import Path
import json
import shutil
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT/"editorial"/"figures"
INBO = ROOT/"research/results/part2_inbo_hyla_g1/observed_results.json"
USGS = ROOT/"research/results/g18_USGS_original_stage_observation_20261108/audited/G18_USGS_INDEPENDENT_STAGE_OBSERVATION_RESULT.json"
S_C = ROOT/"research/manuscript/TWO_PART_MANUSCRIPT_DRAFT_2026-10-26.md"
P1 = ROOT/"research/P1_VEGETATION_BENEFIT_RESULT_2026-11-06.md"
G11 = ROOT/"research/G11_DISJOINT_STRUCTURE_HOLDOUT_VERIFIED_RESULT_2026-11-07.md"
G8 = ROOT/"research/G8_27RATE_VERIFIED_RESULT_2026-11-07.md"

def req(ok,msg):
    if not ok:raise AssertionError(msg)

def style():
    plt.rcParams.update({"font.family":"DejaVu Sans","font.size":10,"axes.titlesize":11,
                         "axes.labelsize":9,"axes.spines.right":False,
                         "axes.spines.top":False,"figure.dpi":180})

def figure1(out):
    inbo=json.loads(INBO.read_text());usgs=json.loads(USGS.read_text())
    ctext=S_C.read_text()
    req(inbo["complete_case_site_years"]==245 and inbo["independent_site_ids"]==93,"INBO source data changed")
    req(usgs["same_event"]["source_sites"]==64 and usgs["same_event"]["matched_species"]==13,"USGS source data changed")
    req(usgs["same_event"]["in_call_and_larva"]==45 and usgs["same_event"]["in_larva_only"]==125,
        "Original USGS paired counts changed")
    for coeff in ["−0.166","−0.087","−0.086","−0.064"]:
        req(coeff in ctext,"Historical observational rank model coeff unsupported: "+coeff)
    m0=inbo["models"]["M0_time_hydrology_recording"]["held_out_site_group_brier"]
    m1=inbo["models"]["M1_add_prior_chorus"]["held_out_site_group_brier"]
    t0=inbo["temporal_2024_2025_validation"]["models"]["M0"]["brier"]
    t1=inbo["temporal_2024_2025_validation"]["models"]["M1"]["brier"]
    req(abs(m0-0.258227)<1e-5 and abs(m1-0.242712)<1e-5 and t1>t0,"INBO source gate")
    pa=usgs["same_event"]["larva_detection_given_in_call"]
    pn=usgs["same_event"]["larva_detection_given_in_nocall"]
    req(abs(pa-45/860)<1e-12 and abs(pn-125/12842)<1e-12,"USGS ratio reconstruction")

    style()
    fig, axes=plt.subplots(2,2,figsize=(12.2,8.7),constrained_layout=True)
    # A: two genuinely different predictive validation settings
    ax=axes[0,0]
    names=["93-site geographic holdout", "2024–25 future-year holdout"]
    baseline=np.array([m0,t0]);plus=np.array([m1,t1])
    y=np.array([1,0])
    for yi,b,c in zip(y,baseline,plus):
        ax.plot([b,c],[yi,yi],lw=1.8,color="0.65",zorder=1)
    ax.scatter(baseline,y,s=70,marker="s",label="Timing/effort only",zorder=2)
    ax.scatter(plus,y,s=85,marker="o",label="+ earlier calling",zorder=2)
    ax.set_yticks(y,names);ax.set_xlim(0.20,0.39)
    ax.set_xlabel("Brier loss (lower is better)")
    ax.set_title("A   INBO: adult calling → later larval detection",loc="left",weight="bold")
    ax.legend(frameon=False,loc="lower right",fontsize=8)
    ax.text(.205,-0.46,"245 site-years (main); future 35 rows. Temporal transfer fails.",fontsize=8,color="0.25")
    # B: source observation probabilities, no survival inference
    ax=axes[0,1]
    vals=[pn,pa];labs=["No call\n(n=12,842)","Adult call\n(n=860)"]
    ax.bar([0,1],np.array(vals)*100,width=.55,alpha=.76)
    for i,val in enumerate(vals):
        ax.text(i,val*100+.18,f"{val*100:.2f}%",ha="center",va="bottom",fontsize=10)
    ax.set_xticks([0,1],labs);ax.set_ylabel("Same-sample larval detection (%)")
    ax.set_ylim(0,7.4);ax.set_title("B   USGS: independent co-detection",loc="left",weight="bold")
    ax.text(-.42,7.0,"13 frog species; 64 physical sites; not survival.",fontsize=8,color="0.25")
    # C: published original pre-G1 historical rank-interaction table
    ax=axes[1,0]
    groups=["Odonata × Caudata","Odonata × landscape V"]
    data={"Uniform":([-0.166,-0.087],[-0.229,-0.124],[-0.108,-0.048]),
          "Target-group":([-0.086,-0.064],[-0.151,-0.115],[-0.023,-0.014])}
    for z,(name,(v,lo,hi)) in enumerate(data.items()):
        yi=np.array([1,0])+(0.09 if z==0 else -0.09)
        v=np.array(v);lo=np.array(lo);hi=np.array(hi)
        ax.errorbar(v,yi,xerr=np.vstack((v-lo,hi-v)),fmt="o",capsize=3,ms=5,label=name)
    ax.axvline(0,lw=1,color="0.4")
    ax.set_xlim(-.27,.03);ax.set_yticks([1,0],groups)
    ax.set_xlabel("Signed rank-regression coefficient (95% route-bootstrap interval)")
    ax.set_title("C   Continental acoustic associations",loc="left",weight="bold")
    ax.legend(frameon=False,fontsize=8,loc="lower left")
    # D: rank correlations by caudate tertile from original field source
    ax=axes[1,1]
    names=["Whole-region contrast","Within-route contrast"]
    vals={"Uniform":([-0.385,-0.122],[-0.509,-0.199],[-0.240,-0.034]),
          "Target-group":([-0.179,-0.072],[-0.328,-0.183],[-0.029,0.023])}
    for z,(name,(v,lo,hi)) in enumerate(vals.items()):
        yi=np.array([1,0])+(0.09 if z==0 else -0.09)
        v=np.array(v);lo=np.array(lo);hi=np.array(hi)
        ax.errorbar(v,yi,xerr=np.vstack((v-lo,hi-v)),fmt="o",capsize=3,ms=5,label=name)
    ax.axvline(0,lw=1,color="0.4")
    ax.set_xlim(-.6,.15);ax.set_yticks([1,0],names)
    ax.set_xlabel("High-minus-low Caudata Spearman contrast (95% interval)")
    ax.set_title("D   Odonata–calling correlation varies with Caudata",loc="left",weight="bold")
    ax.legend(frameon=False,fontsize=8,loc="lower left")
    fig.suptitle("Stage observations justify a mechanistic question; continental calling indicates context, not predation",
                 y=1.02,fontsize=12,weight="bold")
    fig.savefig(out/"Figure1_BC_StageAndContinentalContext_EDITORIAL.png",dpi=210,bbox_inches="tight")
    plt.close(fig)

def figure3(out):
    style()
    for f,val in [(P1,"124"),(G8,"2.705"),(G11,"2.754")]:
        req(val in f.read_text(),f"Unverified original model summary: {val}")
    fig,axes=plt.subplots(2,2,figsize=(12.2,8.4),constrained_layout=True)
    ax=axes[0,0]
    x=np.arange(2)
    y=np.array([2.705,2.754])
    low=np.array([2.021,2.083]);high=np.array([3.410,3.434])
    ax.errorbar(x,y,yerr=np.vstack([y-low,high-y]),fmt="o",capsize=4,ms=8)
    ax.set_xticks(x,["G8: first 256", "G11: disjoint 256"])
    ax.set_ylabel("Change in four-sign compatibility (percentage points)")
    ax.axhline(0,color="0.45",linewidth=1)
    ax.set_ylim(-1,5);ax.set_title("A   Vegetation increases pattern compatibility",loc="left",weight="bold")
    ax=axes[0,1]
    y=np.array([-.04030,-.04125]);low=np.array([-.04918,-.05018]);hi=np.array([-.03109,-.03202])
    ax.errorbar(x,y,yerr=np.vstack([y-low,hi-y]),fmt="o",capsize=4,ms=8)
    ax.set_xticks(x,["G8: first 256", "G11: disjoint 256"])
    ax.axhline(0,color="0.45",linewidth=1)
    ax.set_ylabel("Mean model log frog-cohort change")
    ax.set_ylim(-.065,.015)
    ax.set_title("B   The same intervention decreases abundance",loc="left",weight="bold")
    ax=axes[1,0]
    groups=["Late/short","Late/long","Early/short","Early/long"]
    y=np.array([-.1864,-.1860,.0021,.1163])
    low=np.array([-.2266,-.2271,-.0264,.0787])
    hi=np.array([-.1464,-.1463,.0317,.1560])
    ax.errorbar(range(4),y,yerr=np.vstack((y-low,hi-y)),fmt="o",capsize=3,ms=7)
    ax.axhline(0,color="0.45",lw=1);ax.set_xticks(range(4),groups,rotation=18)
    ax.set_ylabel("Both vegetation functions ON−OFF (model log cohorts)")
    ax.set_title("C   Salamander arrival × aquatic duration reverses benefit",loc="left",weight="bold")
    ax=axes[1,1]
    y=np.array([13.28,10.94,9.38,2.34])
    ax.bar(range(4),y,alpha=.75)
    ax.set_xticks(range(4),groups,rotation=18)
    ax.set_ylabel("ON−OFF four-sign compatibility (percentage points)")
    ax.set_ylim(0,16)
    ax.set_title("D   Largest benefit yields smallest signature gain",loc="left",weight="bold")
    ax.text(.02,.94,"P1: 124/256 source backgrounds flipped loss→benefit;\nno reverse flips (post-hoc decomposition).",
            transform=ax.transAxes,va="top",fontsize=8,bbox={"facecolor":"white","alpha":.8,"edgecolor":"none"})
    fig.suptitle("Across-rate replication and developmental contingency within original food-web simulations",
                 y=1.02,fontsize=12,weight="bold")
    fig.savefig(out/"Figure3_D_RateAndDevelopment_EDITORIAL.png",dpi=210,bbox_inches="tight")
    plt.close(fig)

def main(out):
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    figure1(out);figure3(out)
    # Original figures preserved byte-identically for source comparison.
    shutil.copyfile(BASE/"Figure2_InteractionSignature_VsFrogAbundance.png",
                    out/"Figure2_D_OriginalVegetationMechanism_AUDITED.png")
    shutil.copyfile(BASE/"Figure4_GenuineFinitePopulation_R4.png",
                    out/"Supplementary_Figure_S5_OriginalR4_AUDITED.png")
    import hashlib
    receipt={
        "status":"BCD_EDITORIAL_FIGURES_SOURCE_BACKED_NO_NEW_ANALYSIS",
        "source_stage_B":"original INBO 93-site/245-year and USGS 64-site/13-species source data",
        "C_signed_coefficients":"research/manuscript/TWO_PART_MANUSCRIPT_DRAFT_2026-10-26.md",
        "G8_G11_P1":"original independently audited model outputs, figures are summaries not refits",
        "Mohonk_specific_numerators_plotted":False,
        "main_figures":3,
        "R4_main_figure_relocated_to_S5":True,
        "figure_sha256":{f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(out.glob("*.png"))},
    }
    (out/"BCD_FIGURE_SOURCE_AND_BYTES_RECEIPT.json").write_text(json.dumps(receipt,indent=2)+"\n")
    print("BCD_SOURCE_BACKED_FIGURES_COMPLETE",len(receipt["figure_sha256"]))

if __name__=="__main__":
    import argparse
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,required=True)
    main(p.parse_args().out)
