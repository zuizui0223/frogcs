"""Independent four-seed, source-conditional diagnostic (NO new simulation).

Resample four genuinely independent RNG seed labels as BLOCKS, keeping the
same 64 original 2x2x2 model-source corners fixed. A 4-seed interval is an
unstable synthetic Monte Carlo diagnostic, never a field CI or posterior.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd

KEY=["structure_id","draw","reverse_on","vertex","scale","seed","immigration","guild"]
FIELDS=("final_occupied_patches","n_local_returns","n_local_extinctions",
        "n_3y_persistent_with_recruitment")


def audit(source, out):
    df=pd.read_csv(source/"source_80year_finite_seed_scenarios.csv.gz")
    if len(df)!=12288 or sorted(df.seed.unique().tolist())!=[101,102,103,104]:
        raise AssertionError("Must audit EXACT original 4-seed 80-year source")
    if set(df.movement)!=set(("off","recruits","carryover","both")):
        raise AssertionError("All four source movement modes required")
    original=df[df.movement.eq("off")].set_index(KEY).sort_index()
    records=[]
    for move in ("recruits","carryover","both"):
        treated=df[df.movement.eq(move)].set_index(KEY).sort_index()
        if not treated.index.equals(original.index):
            raise AssertionError("Matched fixed source/seed/vegetation IDs missing")
        delta=(treated[list(FIELDS)]-original[list(FIELDS)]).reset_index()
        delta["movement"]=move
        records.append(delta)
    paired=pd.concat(records,ignore_index=True)
    vars=[f"delta_{x}" if f"delta_{x}" in paired.columns else x for x in FIELDS]
    # Treated-minus-control column labels are inherited from subtraction.
    # Keep contrasts by guild and one genuine RNG seed label (64 model
    # configurations per seed). Do not consider 64 scenarios independent.
    blocks=(paired.groupby(["scale","immigration","guild","movement","seed"],sort=True)[list(FIELDS)]
            .mean().reset_index())
    for f in FIELDS:
        blocks.rename(columns={f:"delta_"+f},inplace=True)

    rng=np.random.default_rng(20261031)
    stats=[]
    for key,g in blocks.groupby(["scale","immigration","guild","movement"],sort=True):
        if g.seed.nunique()!=4 or len(g)!=4:
            raise AssertionError("Need exactly four independent RNG blocks per fixed treatment")
        g=g.sort_values("seed")
        row=dict(zip(["scale","immigration","guild","movement"],key))
        row["n_independent_rng_seeds"]=4
        row["n_fixed_cube_scenarios_per_seed"]=64
        for var in FIELDS:
            v=g["delta_"+var].to_numpy(float)
            draws=rng.integers(0,len(v),size=(9999,len(v)))
            boot=v[draws].mean(axis=1)
            row["mean_delta_"+var]=float(v.mean())
            row["seed_min_delta_"+var]=float(v.min())
            row["seed_max_delta_"+var]=float(v.max())
            row["n_seed_blocks_positive_"+var]=int((v>0).sum())
            row["n_seed_blocks_negative_"+var]=int((v<0).sum())
            row["MC4seed_boot_lower_"+var]=float(np.quantile(boot,.025))
            row["MC4seed_boot_upper_"+var]=float(np.quantile(boot,.975))
        stats.append(row)
    summary=pd.DataFrame(stats)
    out.mkdir(parents=True,exist_ok=True)
    blocks.to_csv(out/"source_80y_per_seed_block_effects.csv",index=False)
    summary.to_csv(out/"source_80y_4seed_bootstrap_diagnostics.csv",index=False)
    short=summary[["scale","immigration","guild","movement",
                   "mean_delta_final_occupied_patches",
                   "seed_min_delta_final_occupied_patches",
                   "seed_max_delta_final_occupied_patches",
                   "n_seed_blocks_positive_final_occupied_patches",
                   "n_seed_blocks_negative_final_occupied_patches",
                   "mean_delta_n_local_returns"]]
    readme=[
        "# Frogcs finite-N 80y: seed-block stability of spatial rescue",
        "",
        "**Method only: four RNG seeds are the independent replication units.**",
        "Every seed contains the same 64 pre-fixed stage×plant×reverse×",
        "factorial source cases, which are not independently sampled field sites.",
        "A seed is compared against the corresponding label from the OFF arm,"
        " but different treatments have different random streams and are NOT"
        " pathwise individual-matched. The 9999 seed-block bootstraps"
        " quantify limited synthetic Monte Carlo uncertainty and cannot"
        " establish robust ecology.",
        "",
        short.to_markdown(index=False,floatfmt=".3f"),
        "",
        "Per-seed values and all 9999-bootstrap intervals for every outcome"
        " are in the companion CSV files.",
        "Interpret zero final occupancy despite positive reoccupancy as"
        " temporary turnover rather than demographic rescue.",
    ]
    (out/"AUDITED_80Y_SEED_BLOCK_STABILITY.md").write_text(
        "\n".join(readme)+"\n",encoding="utf-8"
    )
    print("AUDIT_SOURCE_80Y_SEED_BLOCKS_SUCCESS",len(blocks),len(summary),flush=True)
    print(short.to_string(index=False),flush=True)
    return summary


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--source",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    audit(args.source,args.out)
