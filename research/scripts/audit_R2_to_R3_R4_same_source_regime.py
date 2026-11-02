"""R2 source-defined rate regimes → same-source R3 and R4 consequences.

Exploratory conditional source projection based on original 20,000 source
draws, independent of any wetland parameter measurements. Reuses the
96 previously selected accepted M×T×theta draws; 23 weak-attack/high-rho
examples and 14 also bearing both vegetation features, NOT an independent
20k-draw population followup, and not a posterior conditioned on field calls.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
import pandas as pd

SOURCE_SHA={
    "selected_draws.csv":"739ac81c0e781451537d5485a362bb1be27d9807fda03842c82ca2a0f0e82934",
    "posterior_paired_plant_stage.csv":"878bdcbb909598bc02459c1be178a9e91eddd7700e7dcc4a8c15325ba547f905",
    "joint_mechanism_stage_population.csv":"aeb4268faa574da6952f237fd4d34ebbb0571f17283f999ba85ce668d0690329",
}
ALL_REGIME_PRIOR={0:90,1:65,2:24}
DOUBLE_PLANT_REGIME_PRIOR={0:53,1:42,2:11}
CONDITIONS={
    "weak_attack_high_rho_23":(23,{0:5,1:11,2:7},ALL_REGIME_PRIOR),
    "weak_high_rho_with_double_plant_14":(14,{0:3,1:8,2:3},DOUBLE_PLANT_REGIME_PRIOR),
}
AXES=("cover_SF","cover_DS")
SEED=20261102
REPS=12000


def require(ok,why):
    if not bool(ok):
        raise AssertionError(why)


def read_authorized(path,expected_name=None):
    name=expected_name or Path(path).name
    require(name in SOURCE_SHA,"Unknown biological source file")
    sha=hashlib.sha256(Path(path).read_bytes()).hexdigest()
    require(sha==SOURCE_SHA[name],f"Changed original 80y source record: {name} {sha}")
    return pd.read_csv(path)


def source_inventory(selected,paired,joined,struct_stage):
    require(len(selected)==96 and selected.draw_id.nunique()==96,
            "Original 96 accepted M-stage-theta source IDs missing")
    require(set(selected.context_id)=={0,1,2} and
            selected.groupby("context_id").size().eq(32).all(),
            "Original 32 per original stage source selection changed")
    require(selected.accepted.all() and len(paired)==576 and len(joined)==192,
            "Changed biological accepted draw/plant intervention/demography source")
    require(not paired.duplicated(["source_draw_id","axis","counterfactual_context"]).any(),
            "Duplicate original 96 R3 intervention responses")
    require(not joined.duplicated(["draw_id","q"]).any(),
            "Duplicate same-source R4 occupancy results")
    require(paired.groupby("source_draw_id").size().eq(6).all(),
            "Selected M-theta source has fewer than six model-R3 contrasts")
    require(joined.groupby("draw_id").q.nunique().eq(2).all() and
            set(joined.q)=={3,12},"Selected source q3/q12 followup missing")
    require(set(paired.source_draw_id)==set(selected.draw_id)==set(joined.draw_id),
            "R2 selected, R3 and R4 biological source IDs do not match")
    need=["context_id","support_DF","cover_SF","n_accepted"]
    require(len(struct_stage)==12 and not struct_stage.duplicated(need[:-1]).any(),
            "R2 original 20k structural x context joint source corrupted")
    for label, count, feature in [
            ("all",ALL_REGIME_PRIOR,None),
            ("joint",DOUBLE_PLANT_REGIME_PRIOR,True)]:
        for c,n in count.items():
            if feature is None:
                q=struct_stage[struct_stage.context_id==c]
            else:
                q=struct_stage[(struct_stage.context_id==c)&
                        (struct_stage.support_DF==1)&(struct_stage.cover_SF==1)]
            require(int(q.n_accepted.sum())==n,
                    f"R2 source prior accepted mass shifted for {label} context {c}")
    return True


def selected_group(selected,key):
    if key=="weak_attack_high_rho_23":
        mask=selected.attack.eq(.5)&selected.rho.eq(.75)
    elif key=="weak_high_rho_with_double_plant_14":
        mask=selected.attack.eq(.5)&selected.rho.eq(.75)&(
             selected.support_DF.eq(1)&selected.cover_SF.eq(1))
    else:
        raise ValueError("Unregistered source regime")
    sub=selected.loc[mask].sort_values("draw_id").reset_index(drop=True)
    n,count,target=CONDITIONS[key]
    require(len(sub)==n and sub.context_id.value_counts().to_dict()==count,
            "Exact original R3/4 accepted draw subset changed")
    require(sub.draw_id.is_unique and sub.accepted.all(),
            "Duplicated or unaccepted R2 draw in R3/4 source subset")
    # The original 96 proposals were sampled 32/context irrespective of
    # this regime. Reweight their strata to the *complete 20k original*
    # regime accepted context frequencies (90/65/24 or 53/42/11).
    weights=sub.context_id.map({c:target[c]/sum(target.values())/count[c]
                                for c in range(3)}).to_numpy(float)
    require(np.isclose(weights.sum(),1.0,atol=1e-12),
            "Post-selection stage-stratum source weights not normalized")
    return sub,weights


def bootstrap_strata(sub,weights,n=REPS):
    rng=np.random.default_rng(SEED)
    ix=np.empty((n,len(sub)),dtype=np.int32)
    for c in (0,1,2):
        pos=np.flatnonzero(sub.context_id.to_numpy()==c)
        require(len(pos)>=3,"A conditional source stratum is too small")
        ix[:,pos]=pos[rng.integers(0,len(pos),size=(n,len(pos)))]
    w=weights[ix]
    require(np.allclose(w.sum(axis=1),1,atol=1e-12),
            "Source prior stratified bootstrap does not preserve weight mass")
    return ix,w


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--selected",type=Path,required=True)
    p.add_argument("--paired",type=Path,required=True)
    p.add_argument("--joined",type=Path,required=True)
    p.add_argument("--r2-stage-structure",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    selected=read_authorized(a.selected)
    paired=read_authorized(a.paired)
    joined=read_authorized(a.joined)
    stage=pd.read_csv(a.r2_stage_structure)
    source_inventory(selected,paired,joined,stage)
    rows=[];ids=[]
    for label in CONDITIONS:
        sub,w=selected_group(selected,label)
        ix,bw=bootstrap_strata(sub,w)
        for item in sub.itertuples(index=False):
            ids.append(dict(regime=label,draw_id=int(item.draw_id),
                            main_model_id=int(item.model_id),
                            original_context=int(item.context_id),
                            attack=float(item.attack),
                            rho=float(item.rho),
                            conversion=float(item.conversion),
                            support_DF=int(item.support_DF),
                            cover_SF=int(item.cover_SF),
                            floor_ok=bool(item.floor_ok),
                            source_weights=float(w[sub.index[sub.draw_id==item.draw_id][0]])))
        for axis in AXES:
            part=paired[(paired.axis==axis)&
                        paired.source_draw_id.isin(sub.draw_id)]
            for context in (0,1,2):
                q=part[part.counterfactual_context==context].set_index("source_draw_id").loc[sub.draw_id]
                require(len(q)==len(sub),"Missing original within-draw R3 counterfactual")
                for measure in ("delta_mean_log_F_B","delta_pass"):
                    v=q[measure].to_numpy(float)
                    boot=(v[ix]*bw).sum(axis=1)
                    lo,hi=np.quantile(boot,[.025,.975])
                    rows.append(dict(regime=label,component="R3_refuge",
                                     factor=axis,context=context,q=np.nan,
                                     measure=measure,weighted_mean=float(np.dot(w,v)),
                                     mc95_low=float(lo),mc95_high=float(hi),
                                     n_original_source_ids=len(sub),
                                     accepted_context_counts=";".join(str(CONDITIONS[label][2][k]) for k in range(3)),
                                     selected_source_context_counts=";".join(str(CONDITIONS[label][1][k]) for k in range(3))))
        for scale in (3,12):
            q=joined[(joined.q==scale)&joined.draw_id.isin(sub.draw_id)]
            q=q.set_index("draw_id").loc[sub.draw_id]
            for measure in (
                "move_effect_SF_on_occupied_year80",
                "move_effect_SF_off_occupied_year80",
                "edge_moderation_of_movement_occupied_year80",
                "edge_moderation_of_movement_occupied_mean_year61_80",
            ):
                v=q[measure].to_numpy(float)
                bs=(v[ix]*bw).sum(axis=1)
                lo,hi=np.quantile(bs,[.025,.975])
                rows.append(dict(regime=label,component="R4_longrun",
                                 factor="S_to_F_predation_and_movement",
                                 context=np.nan,q=scale,measure=measure,
                                 weighted_mean=float(np.dot(w,v)),
                                 mc95_low=float(lo),mc95_high=float(hi),
                                 n_original_source_ids=len(sub),
                                 accepted_context_counts=";".join(str(CONDITIONS[label][2][k]) for k in range(3)),
                                 selected_source_context_counts=";".join(str(CONDITIONS[label][1][k]) for k in range(3))))
    result=pd.DataFrame(rows)
    record=pd.DataFrame(ids)
    require(len(result)==2*(2*3*2+2*4) and len(record)==23+14,
            "R2-source conditional matched R3/R4 result inventory incomplete")
    require(not result.duplicated(["regime","component","factor","context","q","measure"]).any(),
            "Duplicate R2 to R3/R4 source interpretation")
    a.output.mkdir(parents=True,exist_ok=True)
    result.to_csv(a.output/"r2_regime_same_source_r3_r4_effects.csv",index=False)
    record.to_csv(a.output/"original_source_23_14_id_audit.csv",index=False)
    receipt=dict(
      status="R2_RATE_REGION_SAME_ORIGINAL_R3_R4_SOURCE_MATCHED_AUDIT_SUCCESS",
      original_source_run=41262102436,
      original_r2_source_run=41390511365,
      n_full_accepted_source_models=794,
      n_R3_R4_selected_models=96,
      weak_attack_high_rho_selected=23,
      weak_high_rho_double_plant_selected=14,
      original_full_priors_weak_high_by_context=[90,65,24],
      original_full_priors_double_plant_by_context=[53,42,11],
      resampling_unit="selected original source draw ID, fixed strata",
      resampling_reps=REPS,seed=SEED,
      source_biological_reruns=0,independent_real_field_data=False,
      original_field_posterior=False,
      conditions_chosen_after_R2_prior_exploration=True,
      source_shas=SOURCE_SHA,
    )
    (a.output/"source_locked_conditional_receipt.json").write_text(
      json.dumps(receipt,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("FROGCS_R2_R3_R4_FULL_SOURCE_ID_CHAIN_AUDIT_SUCCESS",json.dumps({
        k:v for k,v in receipt.items() if k!="source_shas"}),flush=True)
    print(result[["regime","component","context","q","factor","measure","weighted_mean",
                  "mc95_low","mc95_high"]].to_string(index=False),flush=True)


if __name__=="__main__":
    main()
