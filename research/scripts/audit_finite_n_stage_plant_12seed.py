"""Independent seed-block ontogeny × plant effect audit, no model rerunning.

Input is the exact synthetic 12-seed annual-cohort source artifact from
Actions #41193107034; its 64 model vertices are *not* independent seed
replicates. All stage, plant, scale, and immigration cells are retained.
"""
from __future__ import annotations
import argparse
from pathlib import Path

import numpy as np
import pandas as pd

N_SEEDS=12
N_MC=9999
LABELS=list(range(101,113))
OUTCOME="final_occupied_patches"
GROUP=["scale","immigration","context","plant_model","guild"]


def audit(path:Path,out:Path):
    df=pd.read_csv(path)
    required=set(GROUP+["seed",OUTCOME,"n_local_returns"])
    if not required.issubset(df.columns):
        raise AssertionError("Missing unretuned stage×plant source columns")
    if len(df)!=2*2*2*2*3*N_SEEDS or df.duplicated(GROUP+["seed"]).any():
        raise AssertionError("Incomplete or duplicate 12seed treatment factorial")
    if sorted(df.seed.unique().tolist())!=LABELS or not np.isfinite(
        df[[OUTCOME,"n_local_returns"]].to_numpy(float)
    ).all():
        raise AssertionError("All genuine 12 seed means required")
    contexts={"original","D_first_S_overtakes"}
    plants={"SF1_DF0_DS0_L1","SF0_DF0_DS1_L0"}
    if set(df.context)!=contexts or set(df.plant_model)!=plants:
        raise AssertionError("Source ontogeny or plant roles unexpectedly changed")
    rng=np.random.default_rng(20261031)
    rows=[]
    for key,g in df.groupby(GROUP,sort=True):
        g=g.sort_values("seed")
        if g.seed.tolist()!=LABELS:
            raise AssertionError("Stage×plant source is not 12 full unique RNG blocks")
        a=g[OUTCOME].to_numpy(float)
        bootstrap=a[rng.integers(0,N_SEEDS,size=(N_MC,N_SEEDS))].mean(axis=1)
        row=dict(zip(GROUP,key))
        row.update(n_independent_seeds=N_SEEDS,delta_occupied_mean=float(a.mean()),
                   delta_occupied_seed_min=float(a.min()),
                   delta_occupied_seed_max=float(a.max()),
                   delta_occupied_MC_lower=float(np.quantile(bootstrap,.025)),
                   delta_occupied_MC_upper=float(np.quantile(bootstrap,.975)),
                   n_seed_positive=int((a>0).sum()),
                   n_seed_negative=int((a<0).sum()),
                   n_seed_zero=int((a==0).sum()),
                   delta_local_returns_mean=float(g.n_local_returns.mean()))
        rows.append(row)
    role=pd.DataFrame(rows)

    # Within the same seed/block, compare stage ordering's modulation of the
    # (movement both - movement off) effect. Do not treat the many source
    # 2x2x2 factorial vertices as independent replicates.
    mods=[]
    idx=["scale","immigration","plant_model","guild","seed"]
    orig=df[df.context.eq("original")].set_index(idx).sort_index()
    alternate=df[df.context.eq("D_first_S_overtakes")].set_index(idx).sort_index()
    if not orig.index.equals(alternate.index):
        raise AssertionError("Mismatched source conditional stage comparisons")
    contrast=(orig[[OUTCOME,"n_local_returns"]]-
              alternate[[OUTCOME,"n_local_returns"]]).reset_index()
    for key,g in contrast.groupby(idx[:-1],sort=True):
        g=g.sort_values("seed")
        if g.seed.tolist()!=LABELS:
            raise AssertionError("Source-order interaction must have 12 RNG blocks")
        a=g[OUTCOME].to_numpy(float)
        boot=a[rng.integers(0,N_SEEDS,size=(N_MC,N_SEEDS))].mean(axis=1)
        r=dict(zip(idx[:-1],key))
        r.update(n_independent_seeds=N_SEEDS,
                 order_modification_mean=float(a.mean()),
                 order_modification_MC_lower=float(np.quantile(boot,.025)),
                 order_modification_MC_upper=float(np.quantile(boot,.975)),
                 n_seed_positive=int((a>0).sum()),
                 n_seed_negative=int((a<0).sum()),
                 n_seed_zero=int((a==0).sum()),
                 order_modification_returns_mean=float(g.n_local_returns.mean()))
        mods.append(r)
    mod=pd.DataFrame(mods)
    if len(role)!=48 or len(mod)!=24:
        raise AssertionError("Incomplete stage×vegetation scientific contrast audit")

    out.mkdir(parents=True,exist_ok=True)
    role.to_csv(out/"12seed_stage_plant_occupancy_mc_intervals.csv",index=False)
    mod.to_csv(out/"12seed_ontogeny_modification_mc_intervals.csv",index=False)
    focal=role[(role.scale==3)&(role.immigration==0)&
               role.guild.eq("F")].copy()
    focal2=mod[(mod.scale==3)&(mod.immigration==0)&
               mod.guild.eq("F")].copy()
    highD=role[(role.scale==12)&(role.immigration==0)&
               role.guild.eq("D")].copy()
    report=[
        "# Frogcs source 80y: stage-specific movement rescue and turnover",
        "",
        "**Verified synthetic 12seed conditional MC intervals.** Each row uses"
        " exactly 12 independent simulation seed labels, with 64 fixed"
        " source 2x2x2 model vertices per seed. No field causal inference.",
        "",
        "## Primary q3, external immigration OFF, frog F",
        "",
        focal.to_markdown(index=False,floatfmt=".4f"),
        "",
        "## Differences in the movement effect caused by ontogenetic ordering",
        "",
        "Positive = (original stage movement-minus-OFF effect) minus"
        " (D-first stage movement-minus-OFF effect).",
        "",
        focal2.to_markdown(index=False,floatfmt=".4f"),
        "",
        "## q12, external immigration OFF, dragonfly D",
        "",
        highD.to_markdown(index=False,floatfmt=".4f"),
        "",
        "The stage-order contrast is a **within-synthetic-model sensitivity**"
        " to developmental ordering, conditioned on the supplied plant role,"
        " arbitrary migration fraction .15, source rate draw ID0, q scale,"
        " source availability and other fixed mechanisms. It does not show"
        " that the true wetland processes have these rates or causally explain"
        " the empirical NAAMP SDM/calling coefficients.",
        "",
        "Intervals are nonparametric resampling of the 12 independent RNG"
        " label-level mean responses (9999 draws), not field confidence"
        " intervals or a posterior over ecological mechanism classes.",
    ]
    (out/"AUDITED_12SEED_STAGE_PLANT_SOURCE_ORDER.md").write_text(
        "\n".join(report)+"\n",encoding="utf-8"
    )
    print("STAGE_PLANT_12SEED_AUDIT_SUCCESS",len(role),len(mod),flush=True)
    print("FOCAL_F_Q3_EXTERNAL_OFF\n"+focal.to_string(index=False),flush=True)
    print("ONT_ORDER_CONTRAST\n"+focal2.to_string(index=False),flush=True)
    print("FOCAL_D_Q12_EXTERNAL_OFF\n"+highD.to_string(index=False),flush=True)
    return role,mod

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--source",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    audit(a.source,a.out)
