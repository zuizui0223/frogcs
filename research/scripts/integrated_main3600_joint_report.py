"""One joined source-ID report: 80y ABC → plant×stage response → finite q×movement×SF.

All environmental, structural, biological-rate IDs and selection weights are
carried through. No finite-N outcome can change ABC acceptance.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd
from integrated_80y_prepare import HERE
from integrated_finite_main3600 import ARMS


def summaries(prepared: pd.DataFrame, paired: pd.DataFrame,
              finite: pd.DataFrame, out: Path):
    source_ids = set(prepared.draw_id.astype(int))
    if len(prepared) != 96 or not prepared.draw_id.is_unique:
        raise AssertionError("Expected source-locked selected 96 draw IDs")
    if set(finite.draw_id.astype(int)) != source_ids:
        raise AssertionError("Predictive arms not from EXACT accepted 80y IDs")
    if len(finite) != len(prepared)*len(ARMS) or finite.duplicated(
        ["draw_id","q","edge_SF_on","move_on","seed"]
    ).any():
        raise AssertionError("Missing/duplicated finite-N posterior predictions")
    if set(paired.source_draw_id.astype(int)) != source_ids or len(paired) != 96*2*3:
        raise AssertionError("Missing/duplicated paired plant context contrasts")
    # 2x2 (movement x SF-edge) within exact source draw, q and stochastic seed.
    table = finite.pivot(
        index=["draw_id","q","seed"],
        columns=["edge_SF_on","move_on"],
        values=["occupied_year80","occupied_mean_year61_80",
                "recolonization_events_80y","movement_assisted_returns_80y"]
    )
    if table.isna().any().any():
        raise AssertionError("Incomplete within-source finite counterfactual tensor")
    paired_effects = pd.DataFrame(index=table.index)
    for metric in ("occupied_year80", "occupied_mean_year61_80",
                   "recolonization_events_80y"):
        delta1 = table[(metric,1,1)] - table[(metric,1,0)]
        delta0 = table[(metric,0,1)] - table[(metric,0,0)]
        paired_effects[f"move_effect_SF_on_{metric}"] = delta1
        paired_effects[f"move_effect_SF_off_{metric}"] = delta0
        paired_effects[f"edge_moderation_of_movement_{metric}"] = delta1-delta0
    paired_effects["returns_assisted_SF_on"] = table[
        ("movement_assisted_returns_80y",1,1)
    ]
    paired_effects["returns_assisted_SF_off"] = table[
        ("movement_assisted_returns_80y",0,1)
    ]
    per_draw_q = paired_effects.reset_index().groupby(
        ["draw_id","q"],as_index=False
    ).mean(numeric_only=True)
    source = prepared.drop_duplicates("draw_id").set_index("draw_id")
    joined = per_draw_q.join(source, on="draw_id",validate="many_to_one")
    if len(joined) != len(prepared)*2:
        raise AssertionError("Lost source-to-prediction links")
    # The SAME selected draw, at its SELECTED stage, has paired S→F and D→S
    # plant pathway ON/OFF responses, measured at full 80y resolution.
    local = paired.merge(
        prepared[["draw_id","context_id"]],
        left_on="source_draw_id", right_on="draw_id",
        validate="many_to_one"
    )
    local = local[local.counterfactual_context==local.context_id]
    stage = local.pivot(
        index="source_draw_id", columns="axis",
        values=["delta_mean_log_F_B", "delta_log_OSV", "delta_pass"]
    )
    if stage.isna().any().any() or len(stage) != len(prepared):
        raise AssertionError("Stage/plant result lost source ID")
    stage.columns = [f"{effect}_{axis}" for effect,axis in stage.columns]
    joined = joined.join(stage, on="draw_id", validate="many_to_one")
    out.mkdir(parents=True,exist_ok=True)
    joined.to_csv(out/"joint_mechanism_stage_population.csv",index=False)
    paired_effects.reset_index().to_csv(
        out/"paired_finite_movement_sfpredation.csv",index=False
    )
    target = "edge_moderation_of_movement_occupied_year80"
    descriptive = []
    # Only source draw is the uncertainty unit: collapse process seeds first.
    for q in (3,12):
        g = joined[joined.q==q]
        for axis in ("context_id","cover_SF","cover_DS","edge_SD",
                     "edge_DS","litter","behavior"):
            for level,b in g.groupby(axis):
                if len(b)<3:
                    continue
                descriptive.append({
                    "q":q, "axis":axis, "level":str(level),
                    "n_source_draws":len(b),
                    "mean_move_with_SF":float(
                        b.move_effect_SF_on_occupied_year80.mean()),
                    "mean_move_without_SF":float(
                        b.move_effect_SF_off_occupied_year80.mean()),
                    "mean_predation_moderation":float(b[target].mean()),
                    "fraction_predation_moderation_pos":float((b[target]>0).mean()),
                    "fraction_predation_moderation_neg":float((b[target]<0).mean()),
                    "posterior_draw_weight_sum":float(b.sample_weight.sum()),
                })
    pd.DataFrame(descriptive).to_csv(
        out/"context_structure_q_posterior_predictive.csv",index=False
    )
    # Monte Carlo uncertainty over source draws (not measured field ponds).
    rng = np.random.default_rng(20261103)
    bootstrap = []
    for q,g in joined.groupby("q"):
        n=len(g)
        v=g[target].to_numpy()
        w=g.sample_weight.to_numpy()
        w=w/w.sum()
        point=float(np.sum(v*w))
        # Re-sample within original selection contexts to retain
        # the prospective fixed 32/context design.
        simulated=[]
        groups=[x for _,x in g.groupby("context_id")]
        for _ in range(499):
            samples=[x.iloc[rng.integers(0,len(x),size=len(x))] for x in groups]
            boot=pd.concat(samples,ignore_index=True)
            bweight=boot.sample_weight.to_numpy()
            simulated.append(float(np.average(boot[target].to_numpy(),weights=bweight)))
        lo,hi=np.quantile(simulated,[.025,.975])
        bootstrap.append(dict(
            q=int(q), n_draws=n, mean_weighted_moderation=point,
            bootstrap_mc_low=float(lo),bootstrap_mc_high=float(hi),
            unit="synthetic accepted source draw; not independent real sites",
        ))
    pd.DataFrame(bootstrap).to_csv(out/"draw_bootstrap_predictive_interval.csv",index=False)
    manifest = {
        "status":"integrated_model_native_posterior_predictive_not_field_causal",
        "n_80y_accepted_draws_selected":len(prepared),
        "same_theta_q_rows":len(joined),
        "stochastic_source_arms":len(finite),
        "paired_stochastic_counterfactual_units":len(paired_effects),
        "year80_bounds":[0,8],
        "main_seasonal_kernel":"stage_vegetation_network.simulate",
        "main_annual_kernel":"final_network_summary.summarize_years",
        "predictive_edge_intervention":"edge_SF=0 versus original edge_SF=1",
        "movement":"synthetic annual conservative ring transfer 15% of carryover and local recruits",
        "posterior_weights":"account for equal-32-per-context selection",
        "observation_mapping":"NONE: no 4248-site POM or field empirical posterior fitted",
        "sensitivity_flags":[
            "finite-N stochastic completion does not enter rejection ABC",
            "synthetic 8 patch ring geometry affects dispersal outcome",
            "q=3/12 is assumed integer-per-density scaling, not field population size",
            "external immigration from original main recurrence remains ON",
            "movement-assisted zero-to-positive transitions are not exclusive causal returns",
            "structural catalog and 80y target are not a calibrated ecological likelihood",
        ],
        "bootstrap_q":bootstrap,
    }
    (out/"integrated_result_manifest.json").write_text(
        json.dumps(manifest,indent=2,ensure_ascii=False)+"\n",encoding="utf-8"
    )
    print("INTEGRATED_234_COMPLETE "+json.dumps(manifest),flush=True)
    print("INTEGRATED_Q_SUMMARY\n"+pd.DataFrame(bootstrap).to_string(index=False),flush=True)
    return joined


if __name__ == "__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--input",type=Path,default=HERE)
    ap.add_argument("--shards",type=int,default=4)
    ap.add_argument("--out",type=Path,default=HERE)
    args=ap.parse_args()
    prepared=pd.read_csv(args.input/"selected_draws.csv")
    paired=pd.read_csv(args.input/"posterior_paired_plant_stage.csv")
    files=sorted(args.input.glob("finite_predictions_shard_*.csv.gz"))
    if len(files)!=args.shards:
        raise AssertionError("Missing prospective finite shards")
    finite=pd.concat((pd.read_csv(x) for x in files),ignore_index=True)
    summaries(prepared,paired,finite,args.out)
