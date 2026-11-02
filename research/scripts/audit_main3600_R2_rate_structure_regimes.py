"""PR160 full 20,000 original source-draw conditional rate-and-structure audit.

Exhaustive source reads from immutable Actions 41262102436 eight original 80y
ABC shards. No new simulations or field model fit. This is MODEL-NATIVE
conditional generation, NOT ecological posterior inference from NAAMP.
Regime boundaries were chosen after seeing the marginal screening results and
are hence exploratory: report the full 27-cell rate grid without deletion.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
from pathlib import Path
import zipfile

import numpy as np
import pandas as pd

EXPECTED_SOURCE_RUN=41262102436
EXPECTED_MAIN_SHA="5e2f0a87c639df373fa2700b29403d2ab417a1cc"
RATE_LEVELS={"attack":(0.5,1.5,3.0),
             "rho":(0.25,0.50,0.75),
             "conversion":(2.0,4.0,8.0)}
CONDITIONAL_AXES=("edge_SD","edge_DS","cover_SF","cover_DS",
                  "support_DF","support_DS","litter")
MAIN_SIGNS=("log_OS","log_OV","log_SV","log_OSV")
EXPECTED=20_000
N_ACCEPTED=794
SEED=20261101
REGIME_LABELS=(
    "all_source_prior",
    "attack_weak",
    "attack_strong",
    "rho_low",
    "rho_high",
    "weak_attack_high_local_rho",
    "strong_attack_low_local_rho",
    "weak_high_rho_high_conversion",
    "strong_low_rho_low_conversion",
    "original_survival_floor",
    "weak_high_rho_original_survival_floor",
)


def require(cond,msg):
    if not bool(cond):
        raise AssertionError(msg)


def wilson(k,n,z=1.959963984540054):
    if n==0:
        return float("nan"),float("nan")
    p=k/n
    c=(p+z*z/(2*n))/(1+z*z/n)
    h=z*np.sqrt(p*(1-p)/n+z*z/(4*n*n))/(1+z*z/n)
    return float(max(0,c-h)),float(min(1,c+h))


def grouped(data,keys, *,outcome="accepted"):
    out=[]
    for group,g in data.groupby(keys,sort=True,dropna=False):
        group=(group,) if len(keys)==1 else tuple(group)
        k=int(g[outcome].sum())
        n=len(g)
        lo,hi=wilson(k,n)
        out.append(dict(zip(keys,group),n_proposals=n,n_accepted=k,
                        acceptance_rate=float(k/n),
                        monte_carlo_wilson95_low=lo,
                        monte_carlo_wilson95_high=hi))
    return pd.DataFrame(out)


def get_regimes(d):
    return {
        "all_source_prior": d,
        "attack_weak": d[d.attack.eq(.5)],
        "attack_strong": d[d.attack.eq(3.)],
        "rho_low": d[d.rho.eq(.25)],
        "rho_high": d[d.rho.eq(.75)],
        "weak_attack_high_local_rho": d[d.attack.eq(.5)&d.rho.eq(.75)],
        "strong_attack_low_local_rho": d[d.attack.eq(3.)&d.rho.eq(.25)],
        "weak_high_rho_high_conversion": d[d.attack.eq(.5)&d.rho.eq(.75)&d.conversion.eq(8.)],
        "strong_low_rho_low_conversion": d[d.attack.eq(3.)&d.rho.eq(.25)&d.conversion.eq(2.)],
        "original_survival_floor": d[d.floor_ok],
        "weak_high_rho_original_survival_floor": d[d.attack.eq(.5)&d.rho.eq(.75)&d.floor_ok],
    }


def load_sources(shard_root,final_receipt):
    # The exact 8 binary artifacts are the original full 20000 simulation record.
    shard_root=Path(shard_root)
    paths=sorted(shard_root.rglob("shard_*.csv.gz"))
    require(len(paths)==8,"Expected precisely eight original PR160 source shards")
    expected_files={f"shard_{i:02}.csv.gz" for i in range(8)}
    require({p.name for p in paths}==expected_files,
            "Original fixed eight 80y LHS source shard names changed")
    raw=[]
    source_shas={}
    for p in paths:
        source_shas[p.name]=hashlib.sha256(p.read_bytes()).hexdigest()
        d=pd.read_csv(p)
        require(len(d)==2500,f"{p}: 2500 source M-stage-theta draws expected")
        raw.append(d)
    d=pd.concat(raw,ignore_index=True).sort_values("draw_id").reset_index(drop=True)
    require(len(d)==EXPECTED and d.draw_id.nunique()==EXPECTED,
            "Missing or repeated original complete 20,000 proposal IDs")
    require(d.draw_id.eq(np.arange(EXPECTED)).all(),
            "Original 20k source IDs must be 0..19999 exactly")
    require(int(d.accepted.sum())==N_ACCEPTED,
            "Original 80y accepted 794 source draws not reproduced")
    require(int((d.accepted&d.floor_ok).sum())==426,
            "Original accepted source floor sensitivity not reproduced")
    require(d.model_id.between(0,3599).all() and
            d.model_id.nunique()==3582 and
            d.context_id.isin([0,1,2]).all(),
            "Changed original main 3,600 structure catalogue or stage design")
    for name,levels in RATE_LEVELS.items():
        require(set(d[name])==set(levels),f"Original {name} rate prior changed")
    for name in CONDITIONAL_AXES:
        require(set(d[name])=={0,1},f"Model structure feature {name} changed")
    # The original source 80y algorithm's sign convention, which includes
    # strict negative OS,OV and positive SV,OSV, must be recounted.
    sign=(d.log_OS<0)&(d.log_OV<0)&(d.log_SV>0)&(d.log_OSV>0)
    require(np.array_equal(sign.to_numpy(bool),d.accepted.to_numpy(bool)),
            "Saved original four-sign compatibility changed")
    require(np.isfinite(d[list(MAIN_SIGNS)].to_numpy(float)).all(),
            "Source directional contrasts nonfinite")
    summary=json.loads(Path(final_receipt).read_text())
    require(summary["base_main_sha"]==EXPECTED_MAIN_SHA and
            summary["n_proposed"]==EXPECTED and
            summary["n_accepted_log"]==N_ACCEPTED and
            summary["n_accepted_log_and_floor5pct"]==426 and
            summary["model_space"]==3600,
            "Source original main/80y model acceptance receipt drifted")
    return d,source_shas


def compute(d):
    grid=grouped(d,["attack","rho","conversion"])
    require(len(grid)==27 and grid.n_proposals.min()>600 and
            int(grid.n_accepted.sum())==N_ACCEPTED,
            "Full 3x3x3 source-prior rate grid incomplete")
    rawgrid=grouped(d.assign(viable_and_accepted=d.accepted&d.floor_ok),
                    ["attack","rho","conversion"],outcome="viable_and_accepted")
    grid=grid.merge(rawgrid[["attack","rho","conversion","n_accepted",
                             "acceptance_rate"]],
                    on=["attack","rho","conversion"],
                    validate="one_to_one",suffixes=("","_and_survival_floor"))
    marg=pd.concat([
        grouped(d,[axis]).rename(columns={axis:"rate_level"}).assign(rate_axis=axis)
        for axis in RATE_LEVELS],ignore_index=True)
    reg=get_regimes(d)
    require(set(reg)==set(REGIME_LABELS),"Unreported source rate regime")
    regions=[]
    structure=[]
    for name,subset in reg.items():
        k=int(subset.accepted.sum())
        n=len(subset)
        lo,hi=wilson(k,n)
        regions.append(dict(regime=name,n_proposals=n,n_accepted=k,
            acceptance_rate=k/n,mc_wilson95_low=lo,mc_wilson95_high=hi,
            n_source_original_floor_ok=int(subset.floor_ok.sum()),
            accepted_and_floor=int((subset.accepted&subset.floor_ok).sum()),
            floor_qualified_fraction=float(subset.floor_ok.mean()),
            posthoc_regime=True))
        for ax in CONDITIONAL_AXES:
            t=grouped(subset,[ax])
            t=t.rename(columns={ax:"feature_level"})
            t["structural_axis"]=ax
            t["rate_regime"]=name
            t["accepted_share_within_regime"]=t.n_accepted/k if k else 0.
            t["proposal_share_within_regime"]=t.n_proposals/n
            t["relative_accepted_to_proposal_share"]=np.where(
                t.proposal_share_within_regime>0,
                t.accepted_share_within_regime/t.proposal_share_within_regime,np.nan)
            structure.append(t)
    regimes=pd.DataFrame(regions)
    struct=pd.concat(structure,ignore_index=True)
    focus=d[d.attack.eq(.5)&d.rho.eq(.75)]
    struct2=grouped(focus,["context_id","support_DF","cover_SF"])
    require(len(struct2)==12 and int(struct2.n_accepted.sum())==179,
            "Source 3stage x 2 D-feeding support x 2 frog refuge grid missing")
    both=grouped(focus,["support_DF","cover_SF"])
    require(len(both)==4 and int(both.n_accepted.sum())==179,
            "Source selected regime's plant function joint acceptance invalid")
    floors=d.groupby("attack",sort=True).agg(
        n_proposals=("draw_id","size"),
        n_floor_ok=("floor_ok","sum"),
        n_accepted=("accepted","sum")).reset_index()
    floors["accepted_and_floor"]=floors.apply(
        lambda row:int(((d.attack==row.attack)&d.accepted&d.floor_ok).sum()),axis=1)
    floors["floor_frac"]=floors.n_floor_ok/floors.n_proposals
    floors["accepted_and_floor_all_proposal_rate"]=floors.accepted_and_floor/floors.n_proposals
    floors["among_floor_ok_acceptance"]=floors.accepted_and_floor/floors.n_floor_ok
    require(floors.accepted_and_floor.sum()==426,
            "Original source 5-percent survival floor count invalid")
    # Build the retrospective cross-sample contrast without converting
    # structurally correlated observational acceptance to a causal effect.
    rates=dict(zip(regimes.regime,regimes.acceptance_rate))
    require(round(rates["weak_attack_high_local_rho"],6)==round(179/2245,6),
            "Original weak-attack high-local-rho source count changed")
    require(int(regimes.loc[regimes.regime=="strong_attack_low_local_rho",
                            "n_accepted"].iloc[0])==11,"Original strong-low cell changed")
    return grid,marg,regimes,struct,struct2,both,floors


def figure_heatmap(grid,output):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig,axs=plt.subplots(1,3,figsize=(14.2,4.5),sharex=True,sharey=True)
    levels=RATE_LEVELS
    m0=None
    for ax,attack in zip(axs,levels["attack"]):
        t=(grid[grid.attack==attack].pivot(index="rho",columns="conversion",
                values="acceptance_rate").loc[list(levels["rho"]),list(levels["conversion"])])
        val=100*t.to_numpy(float)
        m0=ax.imshow(val,origin="lower",aspect="auto",cmap="viridis",vmin=0,vmax=12)
        for i,rho in enumerate(levels["rho"]):
            for j,conv in enumerate(levels["conversion"]):
                v=grid[(grid.attack==attack)&(grid.rho==rho)&(grid.conversion==conv)].iloc[0]
                ax.text(j,i,f"{100*v.acceptance_rate:.1f}%\n{int(v.n_accepted)}/{int(v.n_proposals)}",
                    ha="center",va="center",color="white" if val[i,j]<5 else "black",fontsize=8)
        ax.set_xticks(range(3),[str(v) for v in levels["conversion"]])
        ax.set_yticks(range(3),[str(v) for v in levels["rho"]])
        ax.set_title(f"Attack coefficient = {attack:g}")
        ax.set_xlabel("Hypothetical conversion")
    axs[0].set_ylabel("Hypothetical local recruitment fraction ρ")
    fig.colorbar(m0,ax=axs.ravel().tolist(),shrink=.78,label="Four-sign compatibility (%)")
    fig.suptitle("Original main3600: all 20,000 80-year source draws (no post hoc rate filtering)")
    fig.text(.02,.012,
        "Simulation sign acceptance; 27 source-prior rate cells. No field-calibrated predation, "
        "recruitment or empirical mechanism posterior.",fontsize=9)
    fig.subplots_adjust(left=.08,right=.90,top=.82,bottom=.16,wspace=.12)
    fig.savefig(output,dpi=190)
    plt.close(fig)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--shards",type=Path,required=True)
    parser.add_argument("--original-summary",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args()
    d,shas=load_sources(args.shards,args.original_summary)
    grid,marg,regimes,structure,stage_grid,plant_joint,floors=compute(d)
    args.output.mkdir(parents=True,exist_ok=True)
    outputs={
        "twentyseven_rate_cells.csv":grid,
        "original_prior_marginal_acceptance.csv":marg,
        "exploratory_regimes_with_denominators.csv":regimes,
        "conditional_structure_by_regime.csv":structure,
        "weak_high_rho_stage_x_plant_mechanism.csv":stage_grid,
        "weak_high_rho_plant_mechanism_joint.csv":plant_joint,
        "rate_survival_floor_sensitivity.csv":floors,
    }
    for name,table in outputs.items():
        table.to_csv(args.output/name,index=False)
    figure_heatmap(grid,args.output/"Figure_R2_full_27_rate_cell_compatibility.png")
    receipt=dict(
        status="FROGCS_MAIN3600_R2_ALL_20000_SOURCE_RATES_STRUCTURES_VERIFIED",
        original_workflow=EXPECTED_SOURCE_RUN,
        original_main_sha=EXPECTED_MAIN_SHA,
        original_shard_sha256=shas,
        source_draws=20000,
        accepted_four_sign=794,
        accepted_after_original_survival_floor=426,
        count_original_main_model_ids=3582,
        n_rate_cells=27,
        regime_weak_attack_high_rho=[2245,179],
        regime_strong_attack_low_rho=[2228,11],
        regimen_joint_plant_weak_high_rho=[675,106],
        n_regimes=len(regimes),
        numerical_prior_not_field_calibrated=True,
        conditional_structural_correlations_not_paired_intervention=True,
        regime_subgroups_retrospectively_inspected=True,
        raw_abundance_magnitude_field_fit=False,
        stage_moderation_mechanism_not_observed=True,
        outputs=list(outputs)+["Figure_R2_full_27_rate_cell_compatibility.png"],
    )
    (args.output/"r2_original_source_receipt.json").write_text(
        json.dumps(receipt,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("FROGCS_MAIN3600_R2_SOURCE_20000_INDEPENDENT_CONDITIONAL_AUDIT_SUCCESS",
          json.dumps({k:v for k,v in receipt.items() if k!="original_shard_sha256"}),flush=True)
    print("R2_REGION_SUMMARY\n"+regimes.to_string(index=False),flush=True)
    print("R2_WEAK_HIGH_RHO_PLANT_JOINT\n"+plant_joint.to_string(index=False),flush=True)


if __name__=="__main__":
    main()
