"""TRUE 80-year frogcs D+E SAME ENGINE: trophic POM and demographic outcomes.

Original scientific source is imported at immutable PR155 ancestry SHA.
The original seasonal 120day, annual delayed maturation and stochastic
finite-N cohort source are unmodified. This runs source model predictions
under six directional trophic networks, with q and annual movement as
explicit nuisance factors, NEVER a field ABC posterior.

Main comparison is model-native factorial patterns, not 4248 NAAMP sites.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

from spatial_cohort_80y_bridge import (
    pilot_cube,replay_gate
)
from model_native_2x2x2_prior import four_contrasts,TARGET
from finite_n_source_cohort_bridge import (
    simulate_finite_group,summarize_finite_group,GUILDS
)

RATE_IDS=(0,4,8,12)
CONTEXTS=("original","D_first_S_overtakes")
PLANTS=("SF1_DF0_DS0_L1","SF0_DF0_DS1_L0")
NETWORKS=("all_active","SF_only","no_SF","no_DF","no_DS","all_off")
MODES=("off","recruits","carryover","both")
QS=(3,12)
SEED_STARTS=(101,103)
REPS_PER_SHARD=2
YEAR_END=80
MOVE_FRAC=.15
NETWORK_OPTIONS={
  "all_active":{},
  "SF_only":{"active_edges":("SF",)},
  "no_SF":{"edge_off":"SF"},
  "no_DF":{"edge_off":"DF"},
  "no_DS":{"edge_off":"DS"},
  "all_off":{"active_edges":()},
}


def biological_cube(draw_ids=RATE_IDS):
    """Full original true 2×2×2 food-web source; selection independent of outcomes."""
    if tuple(draw_ids)!=RATE_IDS:
        raise ValueError("This source pilot fixes four unselected original parent rate IDs")
    full=pilot_cube(4)
    a=full[
        full.context.isin(CONTEXTS) &
        full.plant_model.isin(PLANTS) &
        full.reverse_on.eq(0) &
        full.risk.eq(False)
    ].sort_values(["context","plant_model","draw","vertex"]).reset_index(drop=True)
    if (len(a)!=2*2*4*8 or set(a.draw)!=set(RATE_IDS) or
        a.duplicated(["structure_id","draw","vertex"]).any() or
        set(a.reverse_on)!={0}):
        raise AssertionError("Original biology source cube incomplete")
    for (structure,draw),g in a.groupby(["structure_id","draw"]):
        if len(g)!=8 or set(g.vertex)!=set(range(8)):
            raise AssertionError("A model/biological prior draw lost a factorial corner")
    if not a.da.eq(0).all() or not a.sa.eq(20).all():
        raise AssertionError("Pilot contexts were mislabeled as new chronological onsets")
    # The 2 source contexts are coupled growth/duration changes, NOT
    # an isolated species arrival-order manipulation.
    return a


def score_model_native_four_signs(source):
    """One finite-N source scenario+seed+transport: four orthogonal effects.

    Source fields are actual mean F aquatic cohort density over years61–80.
    Explicit log1p is defined at N=0 but is NOT old PR146 log(F_B).
    """
    fields=["network","scale","movement","seed","structure_id","draw"]
    out=[]
    for key,g in source.groupby(fields,sort=True):
        g=g.sort_values("vertex")
        if (len(g)!=8 or set(g.vertex)!=set(range(8)) or
            g.plant_model.nunique()!=1 or g.context.nunique()!=1):
            raise AssertionError("Incomplete original 2×2×2 output for sign calculation")
        y=g.mean_cohort_B_last_window.to_numpy(float).reshape(2,2,2)
        if not np.isfinite(y).all() or (y<0).any():
            raise AssertionError("True F_B finite-N score invalid")
        row=dict(zip(fields,key))
        row.update(context=g.context.iloc[0],plant_model=g.plant_model.iloc[0],
                   f_year80_occupied_mean=float(g.final_occupied_patches.mean()),
                   n_local_returns_mean=float(g.n_local_returns.mean()),
                   n_local_extinctions_mean=float(g.n_local_extinctions.mean()),
                   n_f_vertices_zero=int((y==0).sum()))
        for scale,z in (("raw",y),("log1p",np.log1p(y))):
            d=four_contrasts(z)
            signs=np.sign(np.where(np.abs(d)>1e-9,d,0)).astype(int)
            for name,beta,sign in zip(("OS","OV","SV","OSV"),d,signs):
                row["beta_"+scale+"_"+name]=float(beta)
                row["sign_"+scale+"_"+name]=int(sign)
            row["matches_"+scale]=bool(np.array_equal(signs,TARGET))
        out.append(row)
    result=pd.DataFrame(out)
    if len(result)!=len(source)//8 or result.duplicated(fields).any():
        raise AssertionError("Source four-sign model-native scores incomplete")
    return result


def simulate_shard(*,scale,mode,seed_start,years=YEAR_END,out,source_replay=True):
    if (scale not in QS or mode not in MODES or seed_start not in SEED_STARTS or
        years not in (4,YEAR_END)):
        raise ValueError("Unapproved biological model, year horizon or nuisance level")
    cube=biological_cube()
    replay=(replay_gate(cube,years=min(4,years),
                        window=2,dt=.25)
            if source_replay else {})
    for name,limit in (("F_B",1e-8),("F_fraction",1e-8),("F_B_sd",1e-7)):
        if replay and replay[name]>limit:
            raise AssertionError("Original biological source season/annual replay changed")
    groups=[(key,g.reset_index(drop=True))
            for key,g in cube.groupby(
                ["context","plant_model","risk","litter"],sort=True)]
    if len(groups)!=4 or any(len(g)!=len(RATE_IDS)*8 for _,g in groups):
        raise AssertionError("Original plant×stage grouping cannot pair source rate draws")
    summaries=[];events=[];ledger=[]
    for seed in range(seed_start,seed_start+REPS_PER_SHARD):
        for net in NETWORKS:
            for (_context,_plant,_risk,_litter),g in groups:
                result=simulate_finite_group(
                    g,scale=int(scale),seed=int(seed),mode=mode,
                    immigration=False,years=years,dt=.25,
                    transfer=MOVE_FRAC,**NETWORK_OPTIONS[net]
                )
                summary,reoccupation=summarize_finite_group(
                    g,result,scale=int(scale),seed=int(seed),mode=mode,
                    immigration=False,years=years
                )
                summary["network"]=net
                if (len(summary)!=len(g)*len(GUILDS) or
                    set(summary.guild)!=set(GUILDS) or
                    not summary.scale.eq(scale).all() or
                    summary.n_external_immigrants.ne(0).any()):
                    raise AssertionError("True stochastic original process lost source guilds")
                if (int(summary.n_recorded_migration_arrivals.sum())!=
                    int(summary.n_recorded_migration_departures.sum())):
                    raise AssertionError("Stochastic ring cohort migration not conservative")
                if len(reoccupation):
                    if reoccupation.cause_label.eq("unclassified").any():
                        raise AssertionError("Original stochastic source has unexplained reoccupation")
                    reoccupation["network"]=net
                    events.append(reoccupation)
                ledger.append(dict(network=net,context=_context,plant_model=_plant,
                     scale=scale,mode=mode,seed=seed,
                     n_return_events=int(len(reoccupation)),
                     n_reported_returns=int(summary.n_local_returns.sum()),
                     n_source_guild_rows=int(len(summary)),
                     n_3y_source_followups=int(summary.n_3y_observable_returns.sum())))
                summaries.append(summary)
        print("D_E_SOURCE_80Y_NUISANCE_SEED_COMPLETED",
              scale,mode,seed,flush=True)
    frame=pd.concat(summaries,ignore_index=True)
    ef=(pd.concat(events,ignore_index=True) if events else
        pd.DataFrame(columns=["structure_id","draw","seed","guild","network"]))
    receipts=pd.DataFrame(ledger)
    expected=len(cube)*REPS_PER_SHARD*len(NETWORKS)*3
    keys=["structure_id","draw","reverse_on","vertex","scale","seed",
          "movement","guild","network"]
    if (len(frame)!=expected or
        frame.duplicated(keys).any() or
        set(frame.draw)!=set(RATE_IDS) or
        set(frame.context)!=set(CONTEXTS) or
        set(frame.plant_model)!=set(PLANTS) or
        set(frame.seed)!=set(range(seed_start,seed_start+REPS_PER_SHARD)) or
        set(frame.network)!=set(NETWORKS) or
        len(ef)!=int(frame.n_local_returns.sum()) or
        len(ef)!=int(receipts.n_return_events.sum())):
        raise AssertionError("True source factorial/seed/return event missing")
    f=frame[frame.guild.eq("F")].copy()
    scores=(score_model_native_four_signs(f) if years==YEAR_END else
            pd.DataFrame(columns=["network","scale","movement","seed","structure_id","draw"]))
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    compression={"method":"gzip","mtime":0}
    frame.to_csv(out/"original_80y_guild_scenario_summary.csv.gz",
                 index=False,compression=compression)
    ef.to_csv(out/"original_80y_zero_to_positive_events.csv.gz",
              index=False,compression=compression)
    receipts.to_csv(out/"actual_return_event_group_counts.csv",index=False)
    scores.to_csv(out/"same_run_native_four_signs_and_demography.csv",index=False)
    response=dict(status="D_E_ORIGINAL_TRUE80Y_COHORT_SIGN_AND_DEMOGRAPHY_SHARD_SUCCESS",
       original_source_immutable_commit="19d45ffb833e2970aff8d88de101736aee289d26",
       years=years,scale=scale,movement_mode=mode,
       synthetic_annual_transfer_fraction=MOVE_FRAC,
       independent_rng_seed_labels=list(range(seed_start,seed_start+REPS_PER_SHARD)),
       original_biological_lhs_rate_ids=list(RATE_IDS),
       n_source_factorial_vertices=len(cube),
       n_biological_networks=len(NETWORKS),
       n_real_guild_scenario_records=len(frame),
       n_same_run_four_sign_scores=len(scores),
       n_true_0_to_positive_events=len(ef),
       source_deterministic_replay_fouryear_errors=replay,
       external_immigration=False,modelled_feeding_stage_size_original=True,
       three_ontogenies_fully_tested=False,
       site_4248_field_pattern_abc_estimated=False,
       source_code_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    (out/"receipt.json").write_text(json.dumps(response,indent=2)+"\n")
    print("D_E_SOURCE_TRUE80Y_SHARD_RECEIPT",
          json.dumps(response),flush=True)
    if years==YEAR_END:
        print("D_E_SOURCE_NATIVE_MATCH_COUNT",
              scores.groupby(["network","scale","movement"])[
              "matches_log1p"].agg(["sum","count"]).to_string(),flush=True)
    return frame,scores,response


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--run",action="store_true")
    p.add_argument("--scale",type=int,choices=QS,required=True)
    p.add_argument("--mode",choices=MODES,required=True)
    p.add_argument("--seed-start",type=int,choices=SEED_STARTS,required=True)
    p.add_argument("--years",type=int,choices=(4,YEAR_END),default=YEAR_END)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    if not a.run:p.error("Explicit --run flag required")
    simulate_shard(scale=a.scale,mode=a.mode,seed_start=a.seed_start,
                   years=a.years,out=a.out)
