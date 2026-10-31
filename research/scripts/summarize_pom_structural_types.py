"""Aggregate prior directional POM into balanced ecological STRUCTURAL TYPES.

Read previously SUCCESSFUL frozen-132, true-80y-rate-192 and separately
hypothetical-danger-72 source artifacts. Never rerun biological models, change
observation-noise parameters, or use predicted sign matches to select cases.
All 12 backgrounds x scale x noise are sensitivity choices on ONE NAAMP cohort,
NOT twelve independent datasets or observations.

Main balanced target: ontogenetic context x handling baseline/shared_both x
behavioural refuge = 3 x 2 x 2 = 12 types. Reversal edge ON/OFF is tested as
a matched subfactor, with *identical response surfaces de-duplicated* before
type-mean scoring. Parameters/danger exposures are not pooled carelessly.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

from select_macro_trophic_scenarios import ROOT
from r2_calibrated_directional_pom import FAMILIES, BACKGROUNDS, MODES

PREVIOUS=ROOT/"research/results/macro_empirical_block_pom_20261031"
DESIGN=ROOT/"research/results/literature_extension_20261029/design.csv"
OUT=ROOT/"research/results/macro_pom_structural_type_20261031"
CONTEXTS=("original","D_first_S_overtakes","S_first_D_overtakes")
HANDLING=("baseline","shared_both")
NOISE=("iid","spatial_block_025","naamp_residual_icc_2degree")
EDGES=("dynamic","frog_reverse")
MATCHED=("MATCHED_R2","MATCHED_WITHOUT_NOISE")
N_SENS=12
N_TYPES=12


def read_sources(root=PREVIOUS,design_path=DESIGN):
    root=Path(root);design_path=Path(design_path)
    scores=pd.read_csv(root/"all_group_three_noise_scores.csv")
    design=pd.read_csv(design_path)
    if len(design)!=132 or design.case.duplicated().any():
        raise ValueError("Archived 132-case biological design changed")
    cols=["family","noise_type","background","mode","source_group"]
    if scores.duplicated(cols).any():
        raise AssertionError("Duplicate source in observed-nuisance context")
    if not set(scores.family)==set(FAMILIES) or set(scores.noise_type)!=set(NOISE):
        raise AssertionError("Missing three observation-noise conditions")
    counts={"frozen132":104,"realrate192":128,"facilitation72":48}
    for family,n in counts.items():
        f=scores[scores.family==family]
        if len(f)!=n*N_SENS or f.groupby("source_group").size().ne(N_SENS).any():
            raise AssertionError("One or more 12-context source scores missing: "+family)
        if not f.calibration_status.isin(MATCHED).all():
            raise ValueError("Unmatched R2 calibration cannot enter structure average")
    source=[]
    for family,expected in (("frozen132",132),("realrate192",192),("facilitation72",72)):
        path=root/(family+"_candidate_scores.csv")
        candidates=pd.read_csv(path)
        if len(candidates)!=4*expected:
            raise AssertionError("Missing candidate alias metadata "+family)
        if candidates.duplicated(["background","mode","model_label"]).any():
            raise ValueError("Duplicated candidate/background/scale")
        by_label=candidates.groupby("model_label").agg(
            n=("source_group","size"),source_group_count=("source_group","nunique"),
            case_count=("case","nunique"),draw_count=("rate_draw","nunique"),
            hypothesis_count=("hypothesis","nunique"))
        if len(by_label)!=expected or not by_label.n.eq(4).all() or not by_label[
            ["source_group_count","case_count","draw_count","hypothesis_count"]].eq(1).all().all():
            raise AssertionError("Source alias is not invariant over the four conditions "+family)
        subset=candidates[(candidates.background=="uniform")&
                          (candidates["mode"]=="rank_signal")].copy()
        if len(subset)!=expected:
            raise AssertionError("Failed source identity extraction")
        source.append(subset[["family","model_label","case","rate_draw",
                              "hypothesis","source_group"]])
    aliases=pd.concat(source,ignore_index=True)
    aliases["case_numeric"]=aliases.case.str.extract(r"^case_(\d{3})$",expand=False)
    if aliases.case_numeric.isna().any():
        raise ValueError("Case labels must carry archived biological case ID")
    aliases["case_numeric"]=aliases.case_numeric.astype(int)
    aliases=aliases.merge(design[["case","context","family","risk","edge",
                                  "hs","hd"]].rename(columns={
        "case":"case_numeric","family":"handling"}),
        on="case_numeric",how="left",validate="many_to_one")
    if aliases[["context","handling","risk","edge"]].isna().any().any():
        raise AssertionError("Unmatched biological case identities")
    if not aliases.groupby("family").size().to_dict()=={
        "frozen132":132,"realrate192":192,"facilitation72":72}:
        raise AssertionError("Inconsistent input alias quantities")
    if not set(aliases[aliases.family=="realrate192"].rate_draw)==set(range(8)):
        raise AssertionError("True 80-year rate draws missing")
    if set(aliases[aliases.family=="facilitation72"].hypothesis)!={
        "neutral","moderate","strong"}:
        raise AssertionError("Missing separately validated facilitation conditions")
    return scores,aliases,design


def join_all(scores,aliases):
    join=scores.merge(aliases,on=["family","source_group"],how="left",
                      validate="many_to_many")
    if len(join)!=12*len(aliases):
        raise AssertionError("Source alias matching lost background/signal/noise rows")
    if join[["model_label","context","handling","risk","edge"]].isna().any().any():
        raise ValueError("Unassigned ecological structure")
    for family,size in {"frozen132":132,"realrate192":192,"facilitation72":72}.items():
        x=join[join.family==family]
        if len(x)!=size*N_SENS:
            raise AssertionError("Biological case family has missing nuisance settings")
    join["risk"]=join["risk"].astype(bool)
    join["original_type"]=join["context"]+"|"+join["handling"]+"|risk="+join.risk.astype(str)
    join["rate_draw"]=join.rate_draw.astype(int)
    return join


def common_structure(join):
    """Fair main 24-configuration factorial; no selection based on model fit."""
    selected=join[
        join.context.isin(CONTEXTS)&
        join.handling.isin(HANDLING)&
        join.edge.isin(EDGES)
    ].copy()
    selected=selected[(selected.family!="facilitation72")|
                      (selected.hypothesis=="neutral")]
    size={"frozen132":24,"realrate192":192,"facilitation72":24}
    for fam,expected in size.items():
        y=selected[selected.family==fam]
        if y.model_label.nunique()!=expected or len(y)!=expected*N_SENS:
            raise AssertionError("Incomplete balanced structural factorial: "+fam)
        if y.groupby(["noise_type","background","mode"]).original_type.nunique().ne(N_TYPES).any():
            raise AssertionError("Not all twelve biological types represented")
    return selected


def type_conditional_scores(common):
    """Avoid duplicate reversal edges, then average equally over true rate draws."""
    columns=["family","noise_type","background","mode",
             "context","handling","risk","original_type","rate_draw"]
    # Distinct edges with exactly same source_group give ONE data point per
    # parameter draw, so apparent reversal redundancy cannot inflate support.
    independent=common.drop_duplicates(columns+["source_group"]).copy()
    at_draw=independent.groupby(columns,as_index=False).agg(
        mean_soft=("soft_joint_agreement","mean"),
        mean_complete=("modal_complete_frequency","mean"),
        n_unique_source_groups=("source_group","size"),
        max_soft=("soft_joint_agreement","max"),
        min_soft=("soft_joint_agreement","min"))
    type_keys=[x for x in columns if x!="rate_draw"]
    per=at_draw.groupby(type_keys,as_index=False).agg(
        soft=("mean_soft","mean"),
        complete=("mean_complete","mean"),
        source_groups_per_draw=("n_unique_source_groups","mean"),
        n_rate_draws=("rate_draw","nunique"),
        within_draw_soft_min=("min_soft","min"),
        within_draw_soft_max=("max_soft","max"))
    if len(per)!=len(FAMILIES)*N_SENS*N_TYPES:
        raise AssertionError("Missing type/background/noise/scale panel")
    if per.groupby(["family","noise_type","background","mode"]).size().ne(N_TYPES).any():
        raise AssertionError("Missing matched original types within a nuisance context")
    for family,n in [("frozen132",1),("realrate192",8),("facilitation72",1)]:
        if not per[per.family==family].n_rate_draws.eq(n).all():
            raise AssertionError("Model type weights not balanced over param draws")
    per["rank_within_context"]=per.groupby(["family","noise_type","background","mode"])[
        "soft"].rank(ascending=False,method="average")
    per["relative_rank_percentile"]=(N_TYPES-per.rank_within_context)/(N_TYPES-1)
    per["in_top3"]=per.rank_within_context<=3
    per["in_top1"]=per.rank_within_context<=1
    return per,at_draw,independent


def type_overall(per):
    out=per.groupby(["family","context","handling","risk","original_type"],as_index=False).agg(
        n_conditions=("soft","size"),
        mean_joint_soft=("soft","mean"),
        median_joint_soft=("soft","median"),
        worst_joint_soft=("soft","min"),
        best_joint_soft=("soft","max"),
        across_noise_soft_sd=("soft","std"),
        mean_complete_frequency=("complete","mean"),
        worst_complete_frequency=("complete","min"),
        n_any_complete=("complete",lambda x:int((x>0).sum())),
        n_complete_ge_10pct=("complete",lambda x:int((x>=.1).sum())),
        mean_rank_percentile=("relative_rank_percentile","mean"),
        n_top3=("in_top3","sum"),
        n_top1=("in_top1","sum"),
        min_source_groups_per_draw=("source_groups_per_draw","min"))
    if len(out)!=len(FAMILIES)*N_TYPES or out.n_conditions.ne(N_SENS).any():
        raise AssertionError("Unbalanced type consensus over 12 nuisance conditions")
    out["rank_by_equal_weight_mean"]=out.groupby("family").mean_joint_soft.rank(
        ascending=False,method="min").astype(int)
    out["rank_by_worst_context"]=out.groupby("family").worst_joint_soft.rank(
        ascending=False,method="min").astype(int)
    return out.sort_values(["family","rank_by_equal_weight_mean","context","handling","risk"])


def handling_comparison(per):
    """Matched handling contrast in every one of 72 season/risk/nuisance cells."""
    keys=["family","noise_type","background","mode","context","risk"]
    p=per.pivot(index=keys,columns="handling",values=["soft","complete",
                                                        "rank_within_context"])
    if p.isna().any().any() or len(p)!=len(FAMILIES)*3*2*N_SENS:
        raise AssertionError("Unbalanced baseline vs shared_both type comparison")
    x=p.copy()
    comparison=pd.DataFrame({
        "delta_soft":x[("soft","shared_both")]-x[("soft","baseline")],
        "delta_complete":x[("complete","shared_both")]-x[("complete","baseline")],
        "rank_delta_shared_minus_baseline":x[("rank_within_context","shared_both")]-
                                           x[("rank_within_context","baseline")]
    }).reset_index()
    if len(comparison)!=len(FAMILIES)*72:
        raise AssertionError("Expected 72 exact handling contrasts per family")
    totals=comparison.groupby(["family"],as_index=False).agg(
        n_paired_contexts=("delta_soft","size"),
        mean_shared_minus_baseline_soft=("delta_soft","mean"),
        median_shared_minus_baseline_soft=("delta_soft","median"),
        n_shared_better=("delta_soft",lambda s:int((s>1e-12).sum())),
        n_baseline_better=("delta_soft",lambda s:int((s< -1e-12).sum())),
        n_equal=("delta_soft",lambda s:int((abs(s)<=1e-12).sum())),
        mean_complete_gain=("delta_complete","mean"))
    strat=comparison.groupby(["family","noise_type","background","mode"],as_index=False).agg(
        n_timing_risk_pairs=("delta_soft","size"),
        mean_shared_minus_baseline_soft=("delta_soft","mean"),
        n_shared_better=("delta_soft",lambda s:int((s>1e-12).sum())))
    if not totals.n_paired_contexts.eq(72).all() or not strat.n_timing_risk_pairs.eq(6).all():
        raise AssertionError("A handling context was lost")
    return comparison,totals,strat


def reversal_contrasts(join):
    """Pair ON/OFF in same rate draw/treatment and original stage structure."""
    x=join[join.handling.isin(HANDLING)&join.context.isin(CONTEXTS)&
           join.edge.isin(EDGES)].copy()
    dimensions=["family","noise_type","background","mode","context","handling",
                "risk","rate_draw","hypothesis"]
    off=x[x.edge=="dynamic"].set_index(dimensions)
    on=x[x.edge=="frog_reverse"].set_index(dimensions)
    if not off.index.is_unique or not on.index.is_unique or not off.index.equals(on.index):
        off=off.sort_index();on=on.sort_index()
    if not off.index.is_unique or not on.index.is_unique or not off.index.equals(on.index):
        raise AssertionError("Can't match exact reversed-predation structure/draw")
    diff=pd.DataFrame({
        "source_identical":off.source_group==on.source_group,
        "delta_reversal_soft":on.soft_joint_agreement-off.soft_joint_agreement,
        "delta_reversal_complete":on.modal_complete_frequency-off.modal_complete_frequency
    }).reset_index()
    n_expected={"frozen132":12*N_SENS,
                "realrate192":12*8*N_SENS,
                "facilitation72":12*3*N_SENS}
    for fam,n in n_expected.items():
        z=diff[diff.family==fam]
        if len(z)!=n:raise AssertionError("Unbalanced ON/OFF source cases "+fam)
        if (z.source_identical & (abs(z.delta_reversal_soft)>1e-12)).any():
            raise AssertionError("Identical model surface received different observation noise/scores")
    totals=diff.groupby("family",as_index=False).agg(
        n_reversal_pairs=("source_identical","size"),
        fraction_identical_sources=("source_identical","mean"),
        mean_reversal_soft_gain=("delta_reversal_soft","mean"),
        n_reversal_better=("delta_reversal_soft",lambda s:int((s>1e-12).sum())),
        n_reversal_worse=("delta_reversal_soft",lambda s:int((s< -1e-12).sum())),
        n_same=("delta_reversal_soft",lambda s:int((abs(s)<=1e-12).sum()))
    return diff,totals


def expanded_frozen_type_comparison(join):
    """Complete extra source variants, but don't mix them with balanced core."""
    f=join[join.family=="frozen132"].copy()
    f["handling_strength"]=f.hs.astype(float).round(6).astype(str)
    cols=["family","noise_type","background","mode","context","handling",
          "handling_strength","risk","edge"]
    extra=f.drop_duplicates(cols+["source_group"]).groupby(cols,as_index=False).agg(
        soft=("soft_joint_agreement","mean"),
        complete=("modal_complete_frequency","mean"),
        n_source_groups=("source_group","size"))
    grouping=["context","handling","handling_strength","risk","edge"]
    totals=extra.groupby(grouping,as_index=False).agg(
        n_contexts=("soft","size"),mean_soft=("soft","mean"),
        worst_soft=("soft","min"),mean_complete=("complete","mean"))
    if extra.groupby(grouping).size().ne(N_SENS).any():
        raise AssertionError("Unequal extra stage-structure condition coverage")
    return extra,totals


def matched_danger_comparison(join):
    """A separately labeled hypothesis: same case, three added danger levels."""
    source=join[join.family=="facilitation72"].copy()
    keys=["noise_type","background","mode","case","context","handling","risk","edge"]
    tab=source.pivot(index=keys,columns="hypothesis",values=["soft_joint_agreement",
                                                             "modal_complete_frequency"])
    if len(tab)!=24*N_SENS or tab.isna().any().any():
        raise AssertionError("Unbalanced danger amplification within biological case")
    rows=[]
    for hypo in ("moderate","strong"):
        rows.append(pd.DataFrame({
            "hypothesis":hypo,
            "gain_soft":tab[("soft_joint_agreement",hypo)]-
                        tab[("soft_joint_agreement","neutral")],
            "gain_complete":tab[("modal_complete_frequency",hypo)]-
                            tab[("modal_complete_frequency","neutral")]
        }).reset_index())
    contrast=pd.concat(rows,ignore_index=True)
    if len(contrast)!=24*N_SENS*2:
        raise AssertionError("Missing matched amplification comparisons")
    summary=contrast.groupby(["hypothesis","handling"],as_index=False).agg(
        n_paired_contexts=("gain_soft","size"),
        mean_gain_soft=("gain_soft","mean"),
        n_positive=("gain_soft",lambda s:int((s>1e-12).sum())),
        n_negative=("gain_soft",lambda s:int((s< -1e-12).sum())),
        mean_gain_complete=("gain_complete","mean"))
    if not summary.n_paired_contexts.eq(12*N_SENS).all():
        raise AssertionError("Amplification and handling not fully paired")
    return contrast,summary


def run(root=PREVIOUS,out=OUT,design_path=DESIGN):
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    score,aliases,design=read_sources(root,design_path)
    joined=join_all(score,aliases)
    common=common_structure(joined)
    per,at_draw,distinct=type_conditional_scores(common)
    types=type_overall(per)
    handling,handling_summary,handling_strata=handling_comparison(per)
    reversal,reversal_summary=reversal_contrasts(joined)
    extra,extra_summary=expanded_frozen_type_comparison(joined)
    danger,danger_summary=matched_danger_comparison(joined)
    data={
        "balanced_type_per_condition":per,
        "balanced_type_across_12_conditions":types,
        "matched_shared_both_vs_baseline":handling,
        "shared_both_vs_baseline_summary":handling_summary,
        "shared_both_vs_baseline_by_condition":handling_strata,
        "matched_reversal_on_vs_off":reversal,
        "reversal_identifiability_summary":reversal_summary,
        "expanded_full132_type_per_condition":extra,
        "expanded_full132_type_summary":extra_summary,
        "matched_danger_type_effects":danger,
        "matched_danger_by_handling":danger_summary,
        "source_alias_to_biological_design":aliases
    }
    for name,frame in data.items():
        frame.to_csv(out/(name+".csv"),index=False)
    necessary=[Path(root)/"all_group_three_noise_scores.csv",
        Path(design_path),*[Path(root)/(f+"_candidate_scores.csv") for f in FAMILIES]]
    receipt=dict(status="POST_RESULT_STRUCTURAL_TYPE_POM_EQUAL_WEIGHT_12_SENSITIVITY_SETTINGS",
        n_original_case_labels=int(len(aliases)),n_model_families=len(FAMILIES),
        n_independent_noise_background_scale_settings=N_SENS,
        independence_caveat="All 12 are correlated sensitivities of same 4248 NAAMP site response",
        common_types_per_family=N_TYPES,
        common_reversal_modes=list(EDGES),
        n_biological_rate_draws=8,
        model_rate_priors_empirically_calibrated=False,
        summary_type_weight="Equal nuisance-setting; within each rate draw collapse exact F_B source groups; then equal rate draws",
        reverse_note="Exactly identical output curves not counted as two independent supportive structures",
        hypothetical_danger_note="Neutral baseline-only primary type comparison; moderate/strong are separately paired",
        no_posterior_model_probability=True,
        source_hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
                       for p in necessary},
        script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    (out/"receipt.json").write_text(json.dumps(receipt,indent=2,ensure_ascii=False)+"\n")
    print("EQUAL_12_CONDITION_STRUCTURAL_TYPES\n"+
          types.to_string(index=False),flush=True)
    print("PAIRED_SHARED_HANDLING\n"+
          handling_summary.to_string(index=False),flush=True)
    print("REVERSAL_IDENTIFIABILITY\n"+
          reversal_summary.to_string(index=False),flush=True)
    print("HYPOTHETICAL_DANGER_BY_HANDLING\n"+
          danger_summary.to_string(index=False),flush=True)
    print("COMPLETE_FULL132_EXTENDED_SOURCE_TYPES\n"+
          extra_summary.to_string(index=False),flush=True)
    return data


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--run",action="store_true")
    p.add_argument("--source-dir",type=Path,default=PREVIOUS)
    p.add_argument("--output-dir",type=Path,default=OUT)
    args=p.parse_args()
    if not args.run:p.error("Explicit --run required")
    run(args.source_dir,args.output_dir)
