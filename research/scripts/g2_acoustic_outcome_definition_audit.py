"""G2: observational acoustic-state outcome decomposition for R1, original source only.

Reproduces original 4,248-site strong-call R1 point/route intervals exactly;
then compares any-call frequency and strong conditional on recorded any calls.
This is NOT calibration of simulated aquatic F_B to wild adult male calls,
not occupancy detection modelling, and not evidence of field predator density.
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

from naamp_site_use_associations import rank_association
from naamp_odonata_caudata_associations import tertiles

SEED=20261027
BOOT=1000
SITE_COUNT=4248
EXPECTED_VISITS=63180
GROUP="pond_breeding_Caudata"
BGS=("uniform","target_group")
SCOPE=(False,True)
OUTCOMES=("strong_all","any_all","strong_given_any")


def require(v,reason):
    if not bool(v):
        raise AssertionError(reason)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def rebuild(sites,visits):
    require(len(sites)==SITE_COUNT and sites.site.is_unique,
            "Not the original 4248 acoustic sites")
    site_set=set(sites.site)
    original=visits[(visits.timeout==0)&visits.site.isin(site_set)].copy()
    require(len(original)==EXPECTED_VISITS,
            "NAAMP completed original observation-visit count changed")
    require(not original.duplicated(["site","run"]).any(),
            "Original per-site acoustic visit duplicates exist")
    require(original["any"].isin([0,1]).all() and
            original.strong.isin([0,1]).all() and
            (original.strong<=original["any"]).all(),
            "Acoustic strong event cannot be present without an any event")
    grp=original.groupby("site").agg(
        n_rebuilt=("strong","size"),
        any_events=("any","sum"),
        strong_events=("strong","sum"),
    )
    d=sites.merge(grp,left_on="site",right_index=True,validate="one_to_one",
                  how="left",sort=False)
    require(d[["n_rebuilt","any_events","strong_events"]].notna().all().all(),
            "Source site missing observed visits")
    require(np.array_equal(d.n_visits.to_numpy(),d.n_rebuilt.to_numpy()),
            "Original acoustic visit denominators changed")
    d["strong_all"]=d.strong_events/d.n_rebuilt
    d["any_all"]=d.any_events/d.n_rebuilt
    d["strong_given_any"]=d.strong_events/d.any_events.replace(0,np.nan)
    require(np.allclose(d.strong_all,d.strong_rate,atol=1e-12,rtol=0)
            and np.allclose(d.any_all,d.any_rate,atol=1e-12,rtol=0),
            "Original source strong_rate/any_rate did not replay individual observations")
    require(int(d.n_rebuilt.sum())==EXPECTED_VISITS and
            (d.strong_events<=d.any_events).all(),
            "Invalid underlying acoustic source totals")
    return d


def reproduce(d,original):
    observed=original[original.group.eq(GROUP)].copy()
    require(len(observed)==4 and
            not observed.duplicated(["background","within_route"]).any(),
            "Original R1 pond-Caudata source high-minus-low contrasts missing")
    rng=np.random.default_rng(SEED)
    routes=d.route.to_numpy()
    blocks=[np.flatnonzero(routes==route) for route in sorted(d.route.unique())]
    require(len(blocks)>300 and all(len(b)>0 for b in blocks),
            "Original 4248 acoustic route cluster support changed")
    idxs=[np.concatenate([blocks[j] for j in
           rng.integers(0,len(blocks),len(blocks))]) for _ in range(BOOT)]
    rows=[]
    contrasts=[]
    contrast_diff=[]
    support=[]
    for bg in BGS:
        scol=f"mean_suitability_{GROUP}_{bg}"
        xcol=f"mean_suitability_Odonata_{bg}"
        sbin,cuts=tertiles(d[scol])
        for tertile in range(3):
            selected=d.iloc[np.flatnonzero(sbin==tertile)]
            support.append(dict(background=bg,caudata_tertile=tertile,
                n_source_sites=len(selected),n_routes=selected.route.nunique(),
                n_any_positive_sites=int(selected.any_events.gt(0).sum()),
                n_any_zero_sites=int(selected.any_events.eq(0).sum()),
                n_completed_visits=int(selected.n_rebuilt.sum()),
                n_any_call_events=int(selected.any_events.sum()),
                n_strong_call_events=int(selected.strong_events.sum()),
                source_tertile_low=float(cuts[0]),source_tertile_high=float(cuts[1])))
        for within in SCOPE:
            draws={outcome:np.full((BOOT,3),np.nan) for outcome in OUTCOMES}
            points={}
            for outcome in OUTCOMES:
                ps=[]
                for sb in range(3):
                    part=d.iloc[np.flatnonzero((sbin==sb) &
                            (d.any_events.gt(0).to_numpy() if
                             outcome=="strong_given_any" else True))]
                    rho=rank_association(part[xcol],part[outcome],part.route,within)
                    require(rho is not None,"Acoustic source tertile has no rank information")
                    ps.append(rho)
                points[outcome]=ps
            for i,idx in enumerate(idxs):
                mask=sbin[idx]
                sub=d.iloc[idx]
                for outcome in OUTCOMES:
                    good=(sub.any_events.gt(0).to_numpy()
                          if outcome=="strong_given_any"
                          else np.ones(len(idx),dtype=bool))
                    for sb in range(3):
                        part=sub.iloc[np.flatnonzero((mask==sb)&good)]
                        draws[outcome][i,sb]=rank_association(
                            part[xcol],part[outcome],part.route,within)
            for outcome in OUTCOMES:
                ci=np.nanquantile(draws[outcome],[.025,.975],axis=0)
                require(np.isfinite(ci).all(),"Incomplete route-cluster acoustic bootstrap")
                for sb in range(3):
                    elig=(sbin==sb)&(d.any_events.gt(0).to_numpy() if
                       outcome=="strong_given_any" else True)
                    rows.append(dict(background=bg,scope="within_route" if within else "whole",
                        outcome=outcome,caudata_tertile=sb,
                        rho=float(points[outcome][sb]),
                        mc95_low=float(ci[0,sb]),mc95_high=float(ci[1,sb]),
                        n_eligible_sites=int(elig.sum()),
                        n_eligible_routes=int(d.loc[elig,"route"].nunique()),
                        route_bootstrap_replicates=BOOT,
                        observational_outcome_only=True))
                difference=draws[outcome][:,2]-draws[outcome][:,0]
                lo,hi=np.nanquantile(difference,[.025,.975])
                val=points[outcome][2]-points[outcome][0]
                contrasts.append(dict(
                    background=bg,scope="within_route" if within else "whole",
                    outcome=outcome,high_minus_low_rho=float(val),
                    mc95_low=float(lo),mc95_high=float(hi),
                    n_eligible_sites=int((d.any_events.gt(0).sum())
                       if outcome=="strong_given_any" else len(d)),
                    n_routes=int(d.loc[d.any_events.gt(0),"route"].nunique()
                       if outcome=="strong_given_any" else d.route.nunique()),
                    conditional_any_changes_population=outcome=="strong_given_any"))
            # Original strong response should match historic full-cohort
            # ecological association AND original bootstrap intervals exactly.
            source=observed[(observed.background==bg)&
                            (observed.within_route==within)]
            require(len(source)==1,"Missing historical same-background R1 field row")
            x=source.iloc[0]
            strong=next(z for z in contrasts if z["background"]==bg and
                  z["scope"]==("within_route" if within else "whole") and
                  z["outcome"]=="strong_all")
            for left,right in (("high_minus_low_rho","high_minus_low_rho"),
                               ("mc95_low","low"),("mc95_high","high")):
                require(abs(strong[left]-float(x[right]))<=1e-11,
                        f"Frozen original R1 strong outcome did not exactly replay: "
                        f"{bg} {within} {left} {strong[left]} != {x[right]}")
            difference=(draws["strong_all"][:,2]-draws["strong_all"][:,0]-
                        draws["any_all"][:,2]+draws["any_all"][:,0])
            lo,hi=np.nanquantile(difference,[.025,.975])
            contrast_diff.append(dict(
                background=bg,scope="within_route" if within else "whole",
                outcome_comparison="strong minus any high-low association contrast",
                delta_rho=float((points["strong_all"][2]-points["strong_all"][0])-
                                (points["any_all"][2]-points["any_all"][0])),
                paired_route_bootstrap95_low=float(lo),
                paired_route_bootstrap95_high=float(hi),
                same_sites_both_outcomes=True,
                estimated_predator_mortality=False))
    a,b,c,sup=(pd.DataFrame(rows),pd.DataFrame(contrasts),
                pd.DataFrame(contrast_diff),pd.DataFrame(support))
    require(len(a)==36 and len(b)==12 and len(c)==4 and len(sup)==6,
            "The full 4,248-site three-acoustic-outcome 2-background test is incomplete")
    require(a.n_eligible_sites.min()>300,
            "No substantive source support for conditional strong-call comparison")
    require(sup.n_source_sites.sum()==2*SITE_COUNT and
            not a.duplicated(["background","scope","outcome","caudata_tertile"]).any(),
            "Wrong original sites/tertiles in observed R1 outcome decomposition")
    return a,b,c,sup


def plot(contrasts,out):
    fig,ax=plt.subplots(figsize=(11.1,6.0))
    order=["strong_all","any_all","strong_given_any"]
    labels=["Strong on all visits","Any call on all visits","Strong among detected calls"]
    offsets={("uniform","whole"):-.27,("target_group","whole"):-.09,
             ("uniform","within_route"):.09,("target_group","within_route"):.27}
    for oi,(outcome,label) in enumerate(zip(order,labels)):
        for bg in BGS:
            for scope in ("whole","within_route"):
                z=contrasts[(contrasts.outcome==outcome)&
                            (contrasts.background==bg)&
                            (contrasts.scope==scope)]
                require(len(z)==1,"Observed outcome figure cell missing")
                x=z.iloc[0]
                y=2-oi+offsets[(bg,scope)]
                ax.errorbar(x.high_minus_low_rho,y,
                            xerr=[[x.high_minus_low_rho-x.mc95_low],
                                  [x.mc95_high-x.high_minus_low_rho]],
                            marker="s" if scope=="within_route" else "o",
                            color="C0" if bg=="uniform" else "C1",
                            linestyle="none",capsize=3)
    ax.axvline(0,color="gray",lw=1)
    ax.set_yticks([2,1,0],labels)
    ax.set_xlabel("High − low pond-breeding Caudata suitability tertile Δ Spearman rho")
    ax.set_title("Observed acoustic definition sensitivity (4,248 original NAAMP sites)")
    ax.grid(axis="x",alpha=.18)
    from matplotlib.lines import Line2D
    handles=[
        Line2D([0],[0],color="C0",marker="o",linestyle="none",label="Uniform SDM · whole"),
        Line2D([0],[0],color="C1",marker="o",linestyle="none",label="Target-group SDM · whole"),
        Line2D([0],[0],color="C0",marker="s",linestyle="none",label="Uniform SDM · within-route"),
        Line2D([0],[0],color="C1",marker="s",linestyle="none",label="Target-group SDM · within-route"),
    ]
    ax.legend(handles=handles,loc="lower left",fontsize=8)
    fig.text(.02,.015,
       "95% original fixed-score route-cluster bootstrap intervals. Conditional strong excludes zero-any sites. "
       "Acoustic responses are neither pond occupancy nor observed larval predation.",fontsize=8)
    fig.tight_layout(rect=(0,.055,1,.98))
    fig.savefig(out/"G2_R1_three_acoustic_outcome_contrasts.png",dpi=190)
    plt.close(fig)


def run(sites_path,visits_path,source_high_low,out):
    sites=pd.read_csv(sites_path)
    visits=pd.read_csv(visits_path)
    source=pd.read_csv(source_high_low)
    d=rebuild(sites,visits)
    strata,contrast,paired,support=reproduce(d,source)
    out.mkdir(parents=True,exist_ok=True)
    for name,x in [
        ("observed_stratified_correlations_by_call_definition.csv",strata),
        ("observed_high_low_by_call_definition.csv",contrast),
        ("paired_original_source_strong_minus_any.csv",paired),
        ("original_tertile_call_event_support.csv",support),
    ]:
        x.to_csv(out/name,index=False)
    plot(contrast,out)
    receipt=dict(
        status="G2_ORIGINAL_4248_VISITS_REPLAY_AND_ACOUSTIC_OUTCOME_DECOMPOSITION_SUCCESS",
        original_main_sha="5e2f0a87c639df373fa2700b29403d2ab417a1cc",
        n_original_sites=SITE_COUNT,
        n_original_completed_acoustic_surveys=EXPECTED_VISITS,
        n_original_routes=int(d.route.nunique()),
        source_any_call_visits=int(d.any_events.sum()),
        source_strong_call_visits=int(d.strong_events.sum()),
        n_original_sites_with_no_any_call=int(d.any_events.eq(0).sum()),
        n_original_tertiles_per_background=3,
        repeated_observation_bootstraps=BOOT,
        frozen_bootstrap_seed=SEED,
        original_R1_strong_acoustic_contrast_and_route_interval_reproduced=True,
        source_files_sha256={Path(p).name:sha(p) for p in
            (sites_path,visits_path,source_high_low)},
        n_stratum_correlation_rows=len(strata),n_outcome_contrast_rows=len(contrast),
        n_paired_strong_any_comparisons=len(paired),
        original_observation_bridge_larval_to_adult_calibrated=False,
        true_frog_occupancy_inferred=False,
        predator_density_measured=False,
        any_call_is_not_true_occupancy=True,
        repeated_recording_detection_probability_not_separately_estimated=True,
        note="Two background SDMs share sites; all uncertainty conditional on saved SDM scores.",
    )
    (out/"G2_source_replay_receipt.json").write_text(
        json.dumps(receipt,ensure_ascii=False,indent=2)+"\n")
    print("G2_ORIGINAL_ACOUSTIC_OUTCOME_SOURCE_AUDIT_SUCCESS",
          json.dumps({k:v for k,v in receipt.items() if k!="source_files_sha256"}),
          flush=True)
    print("G2_ACOUSTIC_DEFINITION_CONTRASTS\n"+contrast.to_string(index=False),flush=True)
    print("G2_PAIRED_STRONG_ANY\n"+paired.to_string(index=False),flush=True)
    return strata,contrast,paired,support


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--site",type=Path,required=True)
    parser.add_argument("--visits",type=Path,required=True)
    parser.add_argument("--original-high-low",type=Path,required=True)
    parser.add_argument("--out",type=Path,required=True)
    a=parser.parse_args()
    run(a.site,a.visits,a.original_high_low,a.out)
