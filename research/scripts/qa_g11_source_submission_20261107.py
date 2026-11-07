"""Fail-closed G11 original-source, 27-rate and 2026-11-07 Letter manuscript QA.

Never treats an incomplete source audit or uncalibrated model as field validation.
"""
from __future__ import annotations
import hashlib
import json
import re
from pathlib import Path

import numpy as np
import pandas as pd

from audit_submission_claims_20261105 import (
    TARGETS, audited_metrics, verify_submission_docs,
)

ROOT=Path(__file__).resolve().parents[2]


def req(x,message):
    if not bool(x):
        raise AssertionError(message)


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    base=ROOT/"research/results/submission_frozen_sources_20261106"
    counts=audited_metrics(*[base/k for k in ("R2","R3","R4","G2","G2B","P1")])
    req(len(counts)==44 and set(counts)==set(TARGETS),
        "Legacy R1-R4/P1 44 source claims changed")
    for name,(target,tol) in TARGETS.items():
        req(np.isfinite(counts[name]) and abs(counts[name]-target)<=tol,
            "Legacy original source claim drift: "+name)
    main_path=ROOT/"editorial/MAIN_TEXT_R1_R4_SUBMISSION_CANDIDATE_2026-11-05.md"
    si_path=ROOT/"editorial/SUPPLEMENTARY_METHODS_AND_EVIDENCE_R1_R4_2026-11-05.md"
    cover_path=ROOT/"editorial/ECOLOGY_LETTERS_COVER_LETTER_DRAFT_2026-11-06.md"
    report_path=ROOT/"research/G11_DISJOINT_STRUCTURE_HOLDOUT_VERIFIED_RESULT_2026-11-07.md"
    protocol_path=ROOT/"research/G11_DISJOINT_STRUCTURE_HOLDOUT_PROTOCOL_2026-11-07.md"
    structural,abstract_words,main_words,si_words=verify_submission_docs(main_path,si_path)
    req(len(structural)==13 and all(structural.values()),
        "Existing 13 manuscript structural safeguards invalidated")
    req(abstract_words==138 and main_words==4988,
        "Post-G11 manuscript no longer matches independently verified word counts")
    g11=ROOT/"research/results/g11_disjoint_holdout_20261107/audited"
    g8=ROOT/"research/results/g8_27rate_paired_20261107/audited"
    g9=ROOT/"research/results/g9_pattern_demography_20261107"
    g10=ROOT/"research/results/g10_standardized_sign_benefit_20261107"
    d=json.loads((g11/"g11_final_independent_validation_receipt.json").read_text())
    req(d["status"]=="G11_DISJOINT_256_STRUCTURE_27_RATE_TRUE80_AUDIT_SUCCESS",
        "G11 must be original-80-year full-audit SUCCESS")
    req(d["full_shards"]==64 and d["source_scenarios"]==82944 and
        d["source_vertices"]==663552 and
        d["matched_source_rate_context"]==20736 and
        len(d["shard_independent_receipts"])==64 and
        d["all_64_independent_source_sign_gates_passed"],
        "Incomplete G11 64-shard structural holdout")
    req(d["disjoint_G11_source_structures"]==256 and
        d["original_G8_base_structures"]==256 and
        d["old_new_model_structure_overlap"]==0 and
        d["eligible_legal_base_structures"]==720 and
        d["previously_unused_baselines"]==464,
        "G11 structural source eligibility or disjointness drift")
    req(d["original_main_sha"]=="5e2f0a87c639df373fa2700b29403d2ab417a1cc",
        "Original biological kernel source changed")
    for f,digest in d["archived_files_sha256"].items():
        req(sha(g11/f)==digest,"Committed original scientific result SHA mismatch "+f)
    select=json.loads((g11/"g11_frozen_structure_selection.json").read_text())
    req(select["sha256"]==d["selection_sha256"] and
        len(select["selection"]["new_base_ids_by_source"])==256 and
        len(set(select["selection"]["new_base_ids_by_source"]))==256 and
        not (set(select["selection"]["new_base_ids_by_source"]) &
             set(select["selection"]["old_base_ids_sorted"])),
        "G11 source selection not response-blind or not disjoint")
    gates=d["fixed_replication_gates"]
    req(gates=={
        "higher_compatibility_in_unseen_structures":True,
        "lower_mean_frog_cohort_in_unseen_structures":True,
        "joint_compatibility_population_mismatch":True},
        "One or more prespecified G11 structural replication directions failed")
    now=d["holdout_pooled_effects"]
    old=d["old_G8_pooled_means"]
    req(abs(now["compatibility"]["mean"]-0.027536651234567902)<1e-12
        and abs(now["frog_log_cohort"]["mean"]+0.04124961905793842)<1e-12,
        "G11 27-rate pooled effects changed")
    req(now["compatibility"]["pointwise_mc95_low"]>0 and
        now["frog_log_cohort"]["pointwise_mc95_high"]<0 and
        abs(old["compatibility"]-0.0270543981481481)<1e-12 and
        abs(old["frog_log_cohort"]+0.040299976951775)<1e-12,
        "Original G8 or G11 structural gate drift")
    # Independent numbers from the complete original paired file, not receipts alone.
    matched=pd.read_csv(g11/"g11_disjoint_20736_matched_source_rate_context.csv.gz")
    req(len(matched)==256*27*3 and
        not matched.duplicated(["source_id","rate_id","context_id"]).any(),
        "Original heldout paired source rows incomplete")
    new=matched.compatibility.eq(1)
    loss=matched.frog_log_cohort.lt(0)
    req((int(new.sum()),int((new&loss).sum()))==(835,612),
        "Independent new-four-sign/tadpole joint count changed")
    req(abs(float((new&loss).sum()/new.sum())-d["G11_new_sign_case_loss_fraction"])<1e-12,
        "New-sign model frog loss ratio is inconsistent")
    pairs_g8=pd.read_csv(g8/"g8_all_source_rate_context_paired.csv.gz")
    new_old=pairs_g8.compatibility.eq(1)
    loss_old=pairs_g8.frog_log_cohort.lt(0)
    req((len(pairs_g8),int(new_old.sum()),int((new_old&loss_old).sum()))
        ==(20736,782,571),"Original G8/G9 new-sign cohort data changed")
    cells=pd.read_csv(g11/"g11_all_27_rate_paired_effects.csv")
    req(len(cells)==27 and cells[["attack","rho","conversion"]].drop_duplicates().shape[0]==27,
        "G11 all 27 fixed synthetic rate cells incomplete")
    req((int((cells.compatibility>0).sum()),
         int((cells.compatibility<0).sum()),
         int((cells.compatibility==0).sum()))==(11,11,5),
        "G11 rate positive/negative/zero count changed")
    req((int((cells.frog_log_cohort<0).sum()),
         int((cells.frog_log_cohort_ci95_high<0).sum()))==(27,26),
        "G11 27-cell frog-cohort response sign counts changed")
    req(abs(cells.compatibility.mean()-now["compatibility"]["mean"])<1e-12
        and abs(cells.frog_log_cohort.mean()-now["frog_log_cohort"]["mean"])<1e-12,
        "Pooled rates do not reconcile with all 27 cells")
    contexts=pd.read_csv(g11/"g11_developmental_context_vs_g8.csv")
    req(len(contexts)==12 and set(contexts.context)=={0,1,2} and
        set(contexts.metric)=={"compatibility","frog_log_cohort",
                              "viable_compatibility","factorial_compatibility"},
        "G11 12 context-comparison rows incomplete")
    for context in (0,1,2):
        q=matched[matched.context_id==context]
        p=contexts[(contexts.context==context)&(contexts.metric=="frog_log_cohort")]
        req(len(p)==1 and len(q)==256*27 and
            abs(float(q.frog_log_cohort.mean())-float(p.g11_mean.iloc[0]))<1e-12,
            "G11 context "+str(context)+" not derived from original paired model outcomes")
    req(contexts.query("metric=='frog_log_cohort'").sort_values("context").g11_mean.gt(0).tolist()==[False,False,True],
        "Model developmental-context frog response reversal changed")
    g10receipt=json.loads((g10/"g10_source_receipt.json").read_text())
    req(g10receipt["primary_adjusted_loss_ci95_pp"][0]<0<
        g10receipt["primary_adjusted_loss_ci95_pp"][1],
        "G10 original negative adjusted excess-loss result overwritten")
    # Provenance and source integrity: only local relative links need to be checked.
    for p in (main_path,si_path,cover_path,report_path):
        content=p.read_text()
        for target in re.findall(r"\]\(([^)]+)\)",content):
            if target.startswith(("http://","https://","mailto:","#")):
                continue
            target=target.split("#",1)[0]
            if target and "?" not in target:
                req((p.parent/target).is_file(),
                    "Broken G11 manuscript/report local link: "+str(p)+" -> "+target)
    main_text=main_path.read_text()
    si_text=si_path.read_text()
    report=report_path.read_text()
    cover=cover_path.read_text()
    req("2.71/+2.75" in main_text and
        "+2.754 points" in main_text and
        "−0.04125" in main_text and
        "G11" in main_text and
        "## Supplementary Methods S13." in si_text and
        "no clear rate×context-adjusted excess loss" in main_text and
        "612" in si_text and "571" in si_text and
        "G5/G7" in si_text and
        "64-shard" in report and
        "4,988 words" in cover and "138 words" in cover and
        "G11" in cover and
        "before any new G11 80-year model outcomes" in si_text,
        "G11 manuscript, source provenance or negative controls missing")
    out=ROOT/"research/results/g11_submission_QA_20261107"
    out.mkdir(parents=True,exist_ok=True)
    result=dict(
       status="G11_64_SHARD_DISJOINT_MODEL_AND_COMPLETE_MANUSCRIPT_QA_SUCCESS",
       existing_independently_rechecked_source_claims=44,
       existing_document_structure_checks=13,
       original_model_pool=3600,eligible_original_counterfactual_baselines=720,
       old_source_models=256,disjoint_holdout_models=256,overlap=0,
       original_true80_shards=64,original_true80_scenarios=82944,
       original_source_vertices=663552,source_paired_comparisons=20736,
       model_rate_cells=27,model_contexts=3,holdout_gates=gates,
       G8_new_sign_and_losses=[782,571],G11_new_sign_and_losses=[835,612],
       source_bootstrap_draws=10000,abstract_words=abstract_words,
       main_body_words=main_words,supplement_words=si_words,
       completed_source_audit_link="https://github.com/zuizui0223/frogcs/actions/runs/42368396463",
       failed_original_aggregate_audit_explained=True,
       manuscript_submitted=False,wild_predator_mechanism_identified=False,
       source_files_sha256={p.name:sha(p) for p in
           (main_path,si_path,cover_path,report_path,protocol_path,
            g11/"g11_final_independent_validation_receipt.json")},
    )
    (out/"G11_submission_source_and_editorial_QA_receipt.json").write_text(
         json.dumps(result,indent=2,ensure_ascii=False)+"\n")
    print("G11_SUBMISSION_MODEL_SOURCE_QA_SUCCESS",json.dumps(
        {k:v for k,v in result.items() if k!="source_files_sha256"},ensure_ascii=False))
    return result


if __name__=="__main__":
    main()
