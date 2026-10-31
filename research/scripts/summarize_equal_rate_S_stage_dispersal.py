"""Paired S larva/adult stage effects at IDENTICAL per-capita diffusion rates.

Real original stochastic seven-stage ABM, same seed labels and same 20-y
duration. No acoustic POM target and no field demographic posterior. Four
seeds are the independent noise units, not patch/year/individual counts.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
import pandas as pd

from tracked_spatial_pedigree import ROOT,SEEDS,GUILDS
from run_equal_rate_S_stage_dispersal import OUT,NEW_MODES,DIFFUSION_VALUES

ENDPOINTS=("n_occupied_year_end","n_local_extinction_events",
           "n_recolonizations","n_two_year_followup_eligible",
           "n_two_year_retained","n_two_census_persistence_plus_local_births",
           "n_seen_survivor_movements",
           "n_with_external_natal_parent_births",
           "n_multisite_founder_lineages",
           "n_living_elsewhere_than_founder_patch")
S_STAGE=("S_larva","S_adult")
RATES=("005","022")


def input_modes(source=OUT):
    frames=[];receipts={}
    for mode in NEW_MODES:
        sfile=source/(mode+"_seed_summary.csv")
        lineage=source/(mode+"_lineage.csv")
        rcfile=source/(mode+"_receipt.json")
        for f in (sfile,lineage,rcfile):
            if not f.is_file() or f.stat().st_size<50:
                raise FileNotFoundError("Missing genuine equal-rate stochastic parent source "+str(f))
        s=pd.read_csv(sfile)
        li=pd.read_csv(lineage)
        receipt=json.loads(rcfile.read_text())
        if (len(s)!=24 or len(li)!=24 or
            s.groupby(["reverse","guild"]).seed.nunique().ne(4).any()
            or receipt.get("n_new_actual_stochastic_runs")!=8 or
            receipt.get("original_ABM_kernel_unchanged") is not True):
            raise AssertionError("Incomplete original model source per equal-rate stage arm")
        if (s.duplicated(["mobility","reverse","seed","guild"]).any()
            or li.duplicated(["mobility","reverse","seed","guild"]).any()):
            raise AssertionError("Duplicated source seed or taxa")
        if s.mobility.nunique()!=1 or s.mobility.iloc[0]!=mode:
            raise AssertionError("Wrong mobility stage source")
        if not np.isclose(receipt["chosen_diffusion"],DIFFUSION_VALUES[mode[-3:]]):
            raise AssertionError("Original source diffusion coefficient not matched")
        data=s.merge(li[["mobility","reverse","seed","guild",
                         "n_lineages_with_living_descendants_in_multiple_patches",
                         "n_living_elsewhere_than_founder_patch"]],
                     on=["mobility","reverse","seed","guild"],
                     validate="one_to_one")
        data=data.rename(columns={
            "n_lineages_with_living_descendants_in_multiple_patches":
                "n_multisite_founder_lineages"})
        if len(data)!=24:raise AssertionError("Lost complete original source lineage")
        data["S_move_stage"]=mode.rsplit("_",1)[0]
        data["rate_code"]=mode[-3:]
        data["per_capita_diffusion"]=DIFFUSION_VALUES[mode[-3:]]
        frames.append(data)
        receipts[mode]={f.name:hashlib.sha256(f.read_bytes()).hexdigest()
                        for f in (sfile,lineage,rcfile)}
    allrows=pd.concat(frames,ignore_index=True)
    if (len(allrows)!=96 or len(allrows[allrows.guild=="S"])!=32 or
        allrows.duplicated(["mobility","reverse","seed","guild"]).any()):
        raise AssertionError("Four source stage × rate modes not equally sampled")
    for key in ENDPOINTS:
        if not np.isfinite(allrows[key].to_numpy(float)).all():
            raise ValueError("Source nonfinite rate-stage result "+key)
    if (allrows.n_occupied_year_end.gt(8).any()
        or allrows.n_two_year_retained.gt(allrows.n_two_year_followup_eligible).any()
        or allrows.n_two_census_persistence_plus_local_births.gt(
            allrows.n_two_year_retained).any()
        or allrows.n_two_year_followup_eligible+allrows.n_return_events_right_censored_at_2years
           != allrows.n_recolonizations).any():
        raise AssertionError("Stage/census source local rescue and censoring inconsistent")
    return allrows,receipts


def paired_effects(data):
    s=data[data.guild=="S"].copy()
    if len(s)!=32 or set(s.S_move_stage)!=set(S_STAGE) or set(s.rate_code)!=set(RATES):
        raise AssertionError("Stage×rate paired biological movement source missing")
    idx=["reverse","seed","rate_code"]
    adult=s[s.S_move_stage=="S_adult"].set_index(idx)
    larva=s[s.S_move_stage=="S_larva"].set_index(idx)
    if not adult.index.equals(larva.index):
        raise AssertionError("S larva/adult do not have same RNG labels per coefficient")
    stage=[]
    for i,key in enumerate(adult.index):
        r=dict(reverse=bool(key[0]),seed=int(key[1]),
               rate_code=str(key[2]),comparison="adult_minus_larva_at_same_per_capita_rate")
        for outcome in ENDPOINTS:
            r["delta_"+outcome]=float(adult.iloc[i][outcome]-larva.iloc[i][outcome])
        stage.append(r)
    st=pd.DataFrame(stage)
    idx=["reverse","seed","S_move_stage"]
    high=s[s.rate_code=="022"].set_index(idx)
    low=s[s.rate_code=="005"].set_index(idx)
    if not high.index.equals(low.index):
        raise AssertionError("High/low coefficients lack identical seeded S stage trials")
    intensity=[]
    for i,key in enumerate(high.index):
        r=dict(reverse=bool(key[0]),seed=int(key[1]),S_move_stage=str(key[2]),
               comparison="diffusion022_minus005_at_same_S_stage")
        for outcome in ENDPOINTS:
            r["delta_"+outcome]=float(high.iloc[i][outcome]-low.iloc[i][outcome])
        intensity.append(r)
    speed=pd.DataFrame(intensity)
    interaction=[]
    for (reverse,seed),g in st.groupby(["reverse","seed"]):
        h=g.set_index("rate_code")
        if set(h.index)!=set(RATES):
            raise AssertionError("Rate×stage interaction cannot be computed")
        r=dict(reverse=bool(reverse),seed=int(seed),
               comparison="adult_minus_larva_difference_022_minus_005")
        for outcome in ENDPOINTS:
            field="delta_"+outcome
            r["interaction_"+outcome]=float(h.loc["022",field]-h.loc["005",field])
        interaction.append(r)
    if len(st)!=16 or len(speed)!=16 or len(interaction)!=8:
        raise AssertionError("Incomplete paired S stage/rate contrasts")
    return st,speed,pd.DataFrame(interaction)


def summarize_four_seed(stage,intensity,interaction):
    records=[]
    for groupname,g,keys,axis in [
        ("stage",stage,["reverse","rate_code"],"delta_"),
        ("rate",intensity,["reverse","S_move_stage"],"delta_"),
        ("interaction",interaction,["reverse"],"interaction_")]:
        for group,part in g.groupby(keys,sort=True):
            if len(part)!=4 or set(part.seed)!=set(SEEDS):
                raise AssertionError("Four independent prior RNG replicates must remain paired")
            group=(group,) if not isinstance(group,tuple) else group
            row=dict(comparison=groupname,n_stochastic_seed_pairs=4)
            for k,v in zip(keys,group):row[k]=v
            for metric in ENDPOINTS:
                col=axis+metric
                v=part[col].to_numpy(float)
                row["mean_"+metric]=float(v.mean())
                row["min_seed_"+metric]=float(v.min())
                row["max_seed_"+metric]=float(v.max())
                row["n_positive_seed_"+metric]=int((v>0).sum())
                row["n_negative_seed_"+metric]=int((v<0).sum())
            records.append(row)
    return pd.DataFrame(records)


def run(source=OUT):
    source=Path(source)
    table,receipt=input_modes(source)
    adult,rate,interaction=paired_effects(table)
    summary=summarize_four_seed(adult,rate,interaction)
    for name,data in [
        ("equal_rate_S_stage_all_seed_guild",table),
        ("equal_rate_S_stage_paired_stage_effects",adult),
        ("equal_rate_S_stage_paired_rate_effects",rate),
        ("equal_rate_S_stage_rate_interaction",interaction),
        ("equal_rate_S_stage_effect_summary",summary)]:
        data.to_csv(source/(name+".csv"),index=False)
    prov=dict(status="EQUAL_PER_CAPITA_DIFFUSION_STAGE_COMPARISON_NOT_FIELD_POSTERIOR",
        n_new_actual_20y_model_arms=32,
        four_per_capita_movement_hypotheses=list(NEW_MODES),
        per_capita_coefficients=DIFFUSION_VALUES,
        n_independent_seeds_per_model=4,
        n_original_kernel_versions=1,
        no_real_field_stage_dispersal_calibration=True,
        original_80year_ABC_different_model=True,
        equal_diffusion_does_not_imply_equal_realized_migrant_flux=True,
        source_files_SHA256=receipt,
        script_SHA256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    (source/"equal_rate_S_stage_comparison_receipt.json").write_text(
        json.dumps(prov,indent=2)+"\n")
    print("EQUAL_S_STAGE_RATE_20YEAR_SUMMARY\n"+
          table[table.guild=="S"].to_string(index=False),flush=True)
    print("EQUAL_S_RATE_CROSS_STAGE_PAIRWISE\n"+summary.to_string(index=False),flush=True)
    return table,adult,rate,summary,prov


if __name__=="__main__":
    a=argparse.ArgumentParser()
    a.add_argument("--run",action="store_true")
    a.add_argument("--source",type=Path,default=OUT)
    v=a.parse_args()
    if not v.run:a.error("Explicit --run required")
    run(v.source)
