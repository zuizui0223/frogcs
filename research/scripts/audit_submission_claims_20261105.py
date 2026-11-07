"""Fail-closed source audit for the concise R1–R4 manuscript and SI.

Consumes frozen original Github Actions artifacts as CSV (already source-audited
by their original biology/observation workflows). Checks high-consequence
reported numbers from different source result tables, denominator meanings,
source-level predator-hazard share (NOT a ratio of averaged hazards), presence
of negative G1/G2B limitations, and the one-paper figure inventory. This audit
does not estimate actual pond predator causation or refit the source models.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

TARGETS = {
    "r2_proposals": (20000, 0),
    "r2_accepted": (794, 0),
    "r2_weak_high_n": (2245, 0),
    "r2_weak_high_accepted": (179, 0),
    "r2_weak_high_doubleplant_n": (675, 0),
    "r2_weak_high_doubleplant_success": (106, 0),
    "r3_n_original_backgrounds": (256, 0),
    "r3_n_biology_variants": (3072, 0),
    "r3_accept_00": (27, 0),
    "r3_accept_10": (44, 0),
    "r3_accept_01": (60, 0),
    "r3_accept_11": (108, 0),
    "r3_pair_both_neither_pp": (10.546875, 0.025),
    "r3_factorial_pp": (4.03645833333333, 0.025),
    "r3_hazard_share_00_pct": (59.6867, 0.05),
    "r3_hazard_share_11_pct": (73.9072, 0.05),
    "r3_hazard_share_gain_pp": (14.2205, 0.05),
    "r3_frog_log_change": (-0.0841, 0.001),
    "r4_true80_arms": (24576, 0),
    "r4_q3_mov1_net_occupancy": (0.029297, 1e-5),
    "r4_q3_mov1_factorial_occupancy": (0.100260, 1e-5),
    "r4_q3_mov1_stage2_net_occupancy": (0.1953125, 0.003),
    "r4_q3_mov1_frog_count": (-5.324707, 1e-4),
    "r4_q12_mov1_frog_count": (-23.653939, 1e-4),
    "g2_uniform_within_strong_minus_any": (-0.064358, 1e-5),
    "g2b_conditional_strong_flex_OS_uniform": (-0.000226, 1e-5),
    "g2b_conditional_strong_flex_OS_target": (-0.000515, 1e-5),
    "g2b_factored_additive_gain_uniform": (0.000415, 1e-5),
    "g2b_factored_additive_gain_target": (0.000860, 1e-5),
    "p1_4096_true80_source_models": (4096, 0),
    "p1_log_LS": (-0.1864, 0.0002),
    "p1_log_LL": (-0.1860, 0.0002),
    "p1_log_ES": (0.0021, 0.0002),
    "p1_log_EL": (0.1163, 0.0002),
    "p1_compat_LS_pp": (13.28125, 0.02),
    "p1_compat_LL_pp": (10.9375, 0.02),
    "p1_compat_ES_pp": (9.375, 0.02),
    "p1_compat_EL_pp": (2.34375, 0.02),
    "p1_early_arrival_log_moderator": (0.245389, 0.0001),
    "p1_long_aquatic_log_moderator": (0.057381, 0.0001),
    "p1_arrival_x_duration_log": (0.113819, 0.0001),
    "p1_early_arrival_signature_moderator_pp": (-6.25, 0.02),
    "p1_long_aquatic_signature_moderator_pp": (-4.6875, 0.02),
    "p1_arrival_x_duration_signature_moderator_pp": (-4.6875, 0.02),
}
G2B_STAGES={"any_all","strong_given_any","strong_all_direct","strong_all_factored"}
ARMS=("00","10","01","11")


def require(ok, reason):
    if not bool(ok):
        raise AssertionError(reason)


def load(root, filename, **kw):
    p = Path(root) / filename
    require(p.is_file(), "Missing archived source result: "+str(p))
    return pd.read_csv(p, **kw)


def audited_metrics(r2, pr161, r4, g2, g2b, p1):
    full = load(r2,"twentyseven_rate_cells.csv")
    regimes=load(r2,"exploratory_regimes_with_denominators.csv")
    plants=load(r2,"weak_high_rho_plant_mechanism_joint.csv")
    require(len(full)==27 and full.n_proposals.sum()==20000,
            "Not all 27 source original rate cells present")
    require(int(full.n_accepted.sum())==794,
            "Original full 20k accepted count changed")
    r=regimes.set_index("regime")
    require("weak_attack_high_local_rho" in r.index,
            "Frozen selected exploratory regime absent")
    row=r.loc["weak_attack_high_local_rho"]
    q=plants[(plants.support_DF==1)&(plants.cover_SF==1)]
    require(len(q)==1,"Double plant R2 structural source denominator missing")

    source=load(pr161,"true80_canonical_paired_2x2_proposals.csv.gz",
                compression="gzip",dtype={"arm":str})
    require(len(source)==3072 and source.source_id.nunique()==256,
            "Original independent new-seed canonical model inventory changed")
    require(source.groupby(["source_id","context_id"]).arm.nunique().eq(4).all(),
            "Newseed same-background four vegetation arms incomplete")
    by_arm=source.groupby("arm").accepted.agg(["sum","size"])
    require(set(by_arm.index)==set(ARMS) and by_arm["size"].eq(768).all(),
            "Each legal vegetation intervention must appear 768 times")
    w=(source.pivot(index=["source_id","context_id"],columns="arm",
                    values="accepted").astype(float))
    w=w.loc[:,list(ARMS)]
    delta=(w["11"]-w["00"]).groupby("source_id").mean()
    synergy=(w["11"]-w["10"]-w["01"]+w["00"]).groupby("source_id").mean()
    hazard=source.groupby("arm")["D_F_hazard_share_V1_S2_D2"].mean()
    require(set(hazard.index)==set(ARMS),
            "Source predator hazard share not by legal arm")
    ratio_check=(source.groupby("arm").H_DF_V1_S2_D2.mean()/
                 (source.groupby("arm").H_SF_V1_S2_D2.mean()+
                  source.groupby("arm").H_DF_V1_S2_D2.mean()))
    # This is an important nonlinearity, not a numerical error:
    # the source's average of unit-level hazard shares differs materially
    # from a ratio of averaged per-frog hazards.
    require(abs(hazard["00"]-ratio_check["00"])>.10,
            "Audit failed to distinguish source-level mean share vs ratio of means")
    v=source.pivot(index=["source_id","context_id"],columns="arm",
                   values="mean_log_F_B").astype(float)
    logdelta=(v["11"]-v["00"]).groupby("source_id").mean().mean()

    p4=load(r4,"R4_genuine_all_24576_model_80y_arms.csv.gz",
            compression="gzip",dtype={"arm":str})
    require(len(p4)==24576 and p4.source_id.nunique()==256 and
            p4.draw_id.nunique()==3072,"Not original same-source stochastic R4")
    t4=load(r4,"R4_full_256_model_2x2_occupancy_and_events.csv",
            dtype={"stage":str})
    require(len(t4)==1280,"Incomplete full R4 model effect source table")

    def rv(metric, contrast, q, move, stage="pooled"):
        rows=t4[(t4.metric==metric)&(t4.contrast==contrast)&
                (t4.q==q)&(t4.move_on==move)&(t4.stage==stage)]
        require(len(rows)==1,"Missing R4 source metric "+str((metric,contrast,q,move,stage)))
        return float(rows.iloc[0]["mean"])

    d2=load(g2,"paired_original_source_strong_minus_any.csv")
    gu=d2[(d2.background=="uniform")&(d2.scope=="within_route")]
    require(len(d2)==4 and len(gu)==1,"Original G2 paired route effect missing")

    g=load(g2b,"G2B_56block_paired_increments.csv")
    score=load(g2b,"G2B_stage_model_scores.csv")
    require(len(g)==24 and len(score)==32 and set(score.observation_stage)==G2B_STAGES,
            "Original 24 comparison G2B acoustic result incomplete")
    require(score[score.observation_stage=="strong_given_any"].trials.eq(47912).all(),
            "Conditional call intensity source denominator wrong")
    require(score[score.observation_stage=="strong_all_direct"].trials.eq(63180).all(),
            "Direct strong acoustic source denominator wrong")

    def gv(bg,stage,compare,base):
        rows=g[(g.background==bg)&(g.stage==stage)&
               (g.comparison==compare)&(g.baseline==base)]
        require(len(rows)==1,"Missing G2B original background/stage/contrast "+str((bg,stage,compare,base)))
        return float(rows.iloc[0].gain_nll_per_trial)

    p1_models=load(p1,"P1_original4096_isolated_timing_duration_80year.csv.gz",
                   compression="gzip",dtype={"timing":str,"arm":str})
    p1_effects=load(p1,"P1_within_timing_paired_vegetation_effects.csv",
                    dtype={"timing":str})
    p1_mod=load(p1,"P1_pure_arrival_duration_and_interaction.csv")
    p1_receipt=json.loads((Path(p1)/"P1_isolated_stage_source_receipt.json").read_text())
    require(p1_receipt["status"]==
            "P1_PURE_SALAMANDER_ARRIVAL_VS_DURATION_ORIGINAL80_SOURCE_AUDIT_SUCCESS"
            and len(p1_models)==4096
            and p1_models.source_id.nunique()==256
            and len(p1_effects)==192
            and len(p1_mod)==36
            and p1_receipt["source_original_stage1_2_replay"]
                     ["legacy_original_2048_true80_source_rows_replayed"],
            "P1 did not independently replay the original true80 stage biology")
    def pv(metric,timing):
        q=p1_effects[(p1_effects.metric==metric)&
                     (p1_effects.timing==timing)&
                     (p1_effects.contrast=="both_minus_neither")]
        require(len(q)==1 and int(q.iloc[0].n_original_source_backgrounds)==256,
                "P1 four original stage effects not exactly source paired")
        return float(q.iloc[0]["mean"])
    def pm(metric,term):
        q=p1_mod[(p1_mod.metric==metric)&(p1_mod.contrast==term)]
        require(len(q)==1 and int(q.iloc[0].n_original_source_backgrounds)==256,
                "P1 pure arrival/duration estimate not exact original source")
        return float(q.iloc[0]["mean"])

    return {
        "r2_proposals":int(full.n_proposals.sum()),
        "r2_accepted":int(full.n_accepted.sum()),
        "r2_weak_high_n":int(row.n_proposals),
        "r2_weak_high_accepted":int(row.n_accepted),
        "r2_weak_high_doubleplant_n":int(q.iloc[0].n_proposals),
        "r2_weak_high_doubleplant_success":int(q.iloc[0].n_accepted),
        "r3_n_original_backgrounds":int(source.source_id.nunique()),
        "r3_n_biology_variants":len(source),
        **{f"r3_accept_{arm}":int(by_arm.loc[arm,"sum"]) for arm in ARMS},
        "r3_pair_both_neither_pp":float(delta.mean()*100),
        "r3_factorial_pp":float(synergy.mean()*100),
        "r3_hazard_share_00_pct":float(hazard["00"]*100),
        "r3_hazard_share_11_pct":float(hazard["11"]*100),
        "r3_hazard_share_gain_pp":float((hazard["11"]-hazard["00"])*100),
        "r3_frog_log_change":float(logdelta),
        "r4_true80_arms":len(p4),
        "r4_q3_mov1_net_occupancy":rv("occupied_year80","both_vs_neither",3,1),
        "r4_q3_mov1_factorial_occupancy":rv("occupied_year80","2x2_factorial",3,1),
        "r4_q3_mov1_stage2_net_occupancy":rv("occupied_year80","both_vs_neither",3,1,"2"),
        "r4_q3_mov1_frog_count":rv("mean_F_count_year61_80","both_vs_neither",3,1),
        "r4_q12_mov1_frog_count":rv("mean_F_count_year61_80","both_vs_neither",12,1),
        "g2_uniform_within_strong_minus_any":float(gu.iloc[0].delta_rho),
        "g2b_conditional_strong_flex_OS_uniform":gv("uniform","strong_given_any","incremental_OS","flex_add"),
        "g2b_conditional_strong_flex_OS_target":gv("target_group","strong_given_any","incremental_OS","flex_add"),
        "g2b_factored_additive_gain_uniform":gv("uniform","strong_all_factored","factored_vs_direct_strong","env_add"),
        "g2b_factored_additive_gain_target":gv("target_group","strong_all_factored","factored_vs_direct_strong","env_add"),
        "p1_4096_true80_source_models":len(p1_models),
        **{"p1_log_"+stage:pv("mean_log_F_B",stage) for stage in ("LS","LL","ES","EL")},
        **{"p1_compat_"+stage+"_pp":pv("accepted",stage)*100 for stage in ("LS","LL","ES","EL")},
        "p1_early_arrival_log_moderator":pm("mean_log_F_B","pure_arrival_moderation_of_plant_effect"),
        "p1_long_aquatic_log_moderator":pm("mean_log_F_B","pure_duration_moderation_of_plant_effect"),
        "p1_arrival_x_duration_log":pm("mean_log_F_B","arrival_x_duration_moderation_of_plant_effect"),
        "p1_early_arrival_signature_moderator_pp":100*pm("accepted","pure_arrival_moderation_of_plant_effect"),
        "p1_long_aquatic_signature_moderator_pp":100*pm("accepted","pure_duration_moderation_of_plant_effect"),
        "p1_arrival_x_duration_signature_moderator_pp":100*pm("accepted","arrival_x_duration_moderation_of_plant_effect"),
    }


def verify_submission_docs(main_path,si_path):
    main=Path(main_path).read_text(encoding="utf-8")
    si=Path(si_path).read_text(encoding="utf-8")
    words=main.split("## Abstract\n")[1].split("**Keywords:**")[0].strip().split()
    # Ecology Letters counts ONLY the main body: title, abstract, figure legends,
    # reference/admin provenance, and Supplementary Information are excluded.
    # Retain headings in the count as an extra-conservative safeguard.
    start=main.index("## Introduction\n")
    stop=main.index("## Figure captions and submission layout")
    main_body=main[start:stop]
    main_body_words=len(main_body.split())
    checks={
      "abstract_max150_for_Ecology_Letters":len(words)<=150,
      "main_text_3000_to_5000_words":3000<=main_body_words<=5000,
      "one_each_main_figure":all(main.count("**Figure "+str(i)+" |")==1 for i in (1,2,3,4)),
      "three_model_response_sections":all(("### R"+str(i)+".") in main for i in (1,2,3,4)),
      "no_wild_causal_identification":("do not establish" in main or
                                      "not establish" in main),
      "exploratory_regime_labeled":("exploratory" in main and
                                  "synthetic" in main),
      "mean_of_hazard_shares_distinction":("mean of source-specific hazard shares" in main and
                                           "not the ratio" in main),
      "external_immigration_on_in_main":("external immigration ON" in main),
      "supplement_all_nine_methods":all("Supplementary Methods S"+str(i) in si for i in range(1,10)),
      "g8_complete_27rate_source_results_declared":(
          "### G8. Rate sweeps" in main and "Supplementary Methods S10" in si
          and "82,944" in main and "663,552" in si
          and "not quantitative fits" in main),
      "conditional_acoustic_denominator_declared":("47,912" in si and "63,180" in si),
      "source_model_priors_not_field_posteriors":("not a field-conditioned ABC posterior" in main and
                                                  "not a posterior" in si),
      "source_main_and_SI_crosslinked":("SUPPLEMENTARY_METHODS_AND_EVIDENCE_R1_R4_2026-11-05.md" in main),
    }
    require(all(checks.values()),
            "Main/SI publication-source safeguards failed: "+
            str([k for k,v in checks.items() if not v]))
    return checks,len(words),main_body_words,len(si.split())


def main():
    p=argparse.ArgumentParser()
    for flag in ("r2","pr161","r4","g2","g2b","p1","main","si","out"):
        p.add_argument("--"+flag,type=Path,required=True)
    a=p.parse_args()
    data=audited_metrics(a.r2,a.pr161,a.r4,a.g2,a.g2b,a.p1)
    require(set(data)==set(TARGETS),
            "Missing independent high-consequence source checks")
    rows=[]
    for key,(target,tolerance) in TARGETS.items():
        value=data[key]
        valid=bool(np.isfinite(value) and abs(value-target)<=tolerance)
        rows.append(dict(metric=key,source_value=value,
                         source_expected=target,absolute_tolerance=tolerance,
                         passed=valid))
    require(all(r["passed"] for r in rows),
            "At least one manuscript source estimate not reproduced: "+
            str([r for r in rows if not r["passed"]]))
    structural,abstract_words,main_words,si_words=verify_submission_docs(a.main,a.si)
    a.out.mkdir(parents=True,exist_ok=True)
    pd.DataFrame(rows).to_csv(a.out/"source_claim_checks.csv",index=False)
    receipt={
        "status":"R1_R4_SUBMISSION_SOURCE_CLAIMS_AND_MANUSCRIPT_STRUCTURAL_QA_PASS",
        "independently_recomputed_numerical_claims":len(rows),
        "document_structural_checks":structural,
        "abstract_words":abstract_words,
        "main_words":main_words,"supplementary_words":si_words,
        "journal_count_policy":"Introduction through Conclusion; headings retained; abstract and figure captions excluded",
        "source_file_sha256":{
           str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest()
           for root in (a.r2,a.pr161,a.r4,a.g2,a.g2b,a.p1)
           for p in root.glob("*.csv*")
        },
        "wild_predator_mechanism_identified":False,
        "manuscript_submitted":False,
    }
    (a.out/"submission_source_QA_receipt.json").write_text(
        json.dumps(receipt,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print("R1_R4_SUBMISSION_SOURCE_CLAIMS_QA_SUCCESS",json.dumps({
        k:v for k,v in receipt.items() if k!="source_file_sha256"}),flush=True)


if __name__=="__main__":
    main()
