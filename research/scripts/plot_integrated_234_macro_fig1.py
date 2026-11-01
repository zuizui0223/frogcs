"""Publication Figure 1 from frozen main 4,248-site NAAMP summary CSVs.

The input is the EXACT original same-site correlations and rank-interaction
bootstrap summaries, NOT re-fitted from model-generated source cohorts.
Two SDM backgrounds are sensitivity specifications on shared occurrences,
not independent geographical replications.

Usage:
 python research/scripts/plot_integrated_234_macro_fig1.py \
  --strata path/stratified_correlations.csv \
  --contrasts path/high_low_contrasts.csv \
  --vegetation path/network_rank_coefficients.csv --output DIR
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

GUILD="pond_breeding_Caudata"
BACKGROUNDS=("uniform","target_group")
TERTILES=("Low","Middle","High")
TERMS=(
    ("Odonata:Caudata","O × S"),
    ("Odonata:vegetation","O × V"),
    ("Caudata:vegetation","S × V"),
    ("Odonata:Caudata:vegetation","O × S × V"),
)


def need(cond,why):
    if not bool(cond):
        raise AssertionError(why)


def verify_interval(data,label,point,low="low",high="high"):
    n=data[[point,low,high]].to_numpy(dtype=float)
    need(np.isfinite(n).all(),f"{label}: invalid uncertainty endpoints")
    need(((n[:,1]<=n[:,0])&(n[:,0]<=n[:,2])).all(),
         f"{label}: intervals do not contain point estimates")


def validate_field(strata,contrasts,vegetation):
    need(len(strata)==24,"Original 24 correlation strata absent")
    need(len(contrasts)==8,"Original 8 tertile contrasts absent")
    need(len(vegetation)==112,"Original 112 3-km vegetation coefficient rows absent")
    s=strata[(strata.group==GUILD)&(~strata.within_route)].copy()
    c=contrasts[(contrasts.group==GUILD)].copy()
    v=vegetation[(vegetation.group==GUILD)&
                 (vegetation.vegetation_metric=="mean")&
                 (vegetation.radius_m==3000)&
                 (vegetation.term.isin([t[0] for t in TERMS]))].copy()
    need(len(s)==6 and len(c)==4 and len(v)==16,
         "Missing pond-breeding caudate background/route estimates")
    need(not s.duplicated(["background","caudata_tertile"]).any(),
         "Repeated source survey stratum")
    need(not c.duplicated(["background","within_route"]).any(),
         "Repeated high-minus-low comparison")
    need(not v.duplicated(["background","within_route","term"]).any(),
         "Repeated vegetation interaction coefficient")
    for b in BACKGROUNDS:
        q=s[s.background==b]
        need(set(q.caudata_tertile)=={0,1,2},"Expected exactly three source tertiles")
        need(int(q.sites.sum())==4248,"Source survey denominator changed")
        need(set(c[c.background==b].within_route)=={True,False},
             "Whole-region/within-route contrast missing")
        need(v[v.background==b].shape[0]==8,"Vegetation 4x2 coefficients incomplete")
    need(set(v.valid_bootstraps)=={1000},
         "Reported vegetation route-resampling source changed")
    verify_interval(s,"stratified observed rho","rho")
    verify_interval(c,"high minus low observed rho","high_minus_low_rho")
    verify_interval(v,"observed vegetation coefficients","beta")
    for b in BACKGROUNDS:
        q=s[s.background==b].set_index("caudata_tertile").sort_index()
        p=c[(c.background==b)&(~c.within_route)].iloc[0]
        need(abs((q.loc[2,"rho"]-q.loc[0,"rho"])-p.high_minus_low_rho)<1e-10,
             "Original source high-low contrast changed")
    return s,c,v


def plot_corr(s,c,out):
    fig,(a,b)=plt.subplots(1,2,figsize=(13.6,5.4),
                           gridspec_kw={"width_ratios":[1.18,1]})
    for bg,label,offset in [("uniform","Uniform SDM",-.08),
                            ("target_group","Target-group SDM",.08)]:
        g=s[s.background==bg].sort_values("caudata_tertile")
        x=g.caudata_tertile.to_numpy(float)+offset
        y=g.rho.to_numpy(float)
        err=np.vstack([y-g.low.to_numpy(float),g.high.to_numpy(float)-y])
        a.errorbar(x,y,yerr=err,marker="o",linestyle="-",capsize=3,label=label)
        row=c[(c.background==bg)&(~c.within_route)].iloc[0]
        xx=row.high_minus_low_rho
        b.errorbar([xx],[1 if bg=="uniform" else 0],
                   xerr=[[xx-row.low],[row.high-xx]],marker="o",capsize=4,
                   linestyle="none",label=label)
    a.axhline(0,color="grey",linewidth=1)
    a.set_xticks([0,1,2],TERTILES)
    a.set_xlabel("Pond-breeding Caudata suitability tertile")
    a.set_ylabel("Odonata suitability × frog strong-calling Spearman ρ")
    a.set_title("A · Third-guild context")
    a.grid(axis="y",alpha=.2)
    a.legend(loc="lower left")
    b.axvline(0,color="grey",linewidth=1)
    b.set_yticks([1,0],["Uniform SDM","Target-group SDM"])
    b.set_xlim(-.6,.15)
    b.set_xlabel("High − low Caudata difference in ρ")
    b.set_title("B · Between-stratum contrast")
    b.grid(axis="x",alpha=.2)
    fig.suptitle("Figure 1A · Observed continental frog calling association (4,248 sites)")
    fig.text(.015,.015,
        "95% route-bootstrap intervals, fixed SDM scores; backgrounds reuse sites. "
        "Adult calling and environmental suitability do not measure larval predation.",
        fontsize=8)
    fig.tight_layout(rect=(0,.04,1,.92))
    fig.savefig(out/"Figure1A_third_guild_observed_association.png",dpi=190)
    plt.close(fig)


def plot_veg(v,out):
    fig,ax=plt.subplots(figsize=(12.5,5.8))
    colors=plt.rcParams['axes.prop_cycle'].by_key().get('color',['C0','C1','C2','C3'])
    markers={False:'o',True:'s'}
    offsets={("uniform",False):-.28,("target_group",False):-.09,
             ("uniform",True):.09,("target_group",True):.28}
    for i,(term,label) in enumerate(TERMS):
        for bg in BACKGROUNDS:
            for within in (False,True):
                row=v[(v.term==term)&(v.background==bg)&(v.within_route==within)].iloc[0]
                y=3-i+offsets[(bg,within)]
                low=row.beta-row.low; high=row.high-row.beta
                ax.errorbar([row.beta],[y],xerr=[[low],[high]],
                            marker=markers[within],linestyle='none',capsize=2,
                            color=colors[BACKGROUNDS.index(bg)+2*int(within)])
    ax.axvline(0,color="grey",linewidth=1)
    ax.set_yticks([3,2,1,0],[label for _,label in TERMS])
    ax.set_xlabel("Standardized rank-interaction coefficient")
    ax.set_title("Figure 1B · Vegetation context: whole region versus within-route")
    ax.grid(axis="x",alpha=.2)
    from matplotlib.lines import Line2D
    labels=[]
    for bg in BACKGROUNDS:
        for within in (False,True):
            labels.append(Line2D([0],[0],color=colors[BACKGROUNDS.index(bg)+2*int(within)],
                                 marker=markers[within],linestyle="none",
                                 label=bg.replace("_","-")+" | "+
                                       ("within-route" if within else "whole region")))
    ax.legend(handles=labels,loc="lower left",fontsize=8)
    fig.text(.02,.017,
        "Observed 3-km EarthEnv wetland-vegetation proxy; 95% route-bootstrap intervals. "
        "Plant refuge function is NOT observed.",fontsize=8)
    fig.tight_layout(rect=(0,.045,1,.95))
    fig.savefig(out/"Figure1B_vegetation_rank_interactions.png",dpi=190)
    plt.close(fig)


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--strata",type=Path,required=True)
    p.add_argument("--contrasts",type=Path,required=True)
    p.add_argument("--vegetation",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    data=[pd.read_csv(t) for t in (a.strata,a.contrasts,a.vegetation)]
    s,c,v=validate_field(*data)
    a.output.mkdir(parents=True,exist_ok=True)
    plot_corr(s,c,a.output)
    plot_veg(v,a.output)
    manifest={
      "status":"SOURCE_VERIFIED_FIGURE1_REAL_OBSERVED_SITE_SUMMARIES",
      "observed_listening_sites":4248,
      "focal_taxa_condition":"pond_breeding_Caudata",
      "n_SDM_backgrounds":2,"actual_caudate_larvae_not_observed":True,
      "not_a_predation_effect":True,
      "source_main_commit":"5e2f0a87c639df373fa2700b29403d2ab417a1cc",
      "sources":{path.name:hashlib.sha256(path.read_bytes()).hexdigest()
                 for path in (a.strata,a.contrasts,a.vegetation)},
      "figures":["Figure1A_third_guild_observed_association.png",
                 "Figure1B_vegetation_rank_interactions.png"],
    }
    (a.output/"Figure1_source_receipt.json").write_text(
        json.dumps(manifest,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print("FROGCS_FIELD_FIGURE1_VERIFIED",json.dumps(manifest,ensure_ascii=False),flush=True)


if __name__=="__main__":
    main()
