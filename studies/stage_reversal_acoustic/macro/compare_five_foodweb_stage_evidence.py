#!/usr/bin/env python3
"""ONTO-TIME five local foodweb typed-stage source-ontology sensitivity.

Data are original-source audited receipt aggregates from three *source
programmes*, five local community networks. Never treat their 806 graph
candidates as 806 independent observed predator reversals.
"""
import argparse
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
RESULTS=HERE/"results"
SOURCES={
 "preston":RESULTS/"PRESTON2012_ORIGINAL_STAGE_RECIPROCITY_EVIDENCE_TIER_V0_1.json",
 "otago":RESULTS/"OTAGO2011_ORIGINAL_STAGE_RECIPROCITY_PARASITE_CLASS_V0_1.json",
 "estuaries":RESULTS/"HECHINGER2011_THREE_ESTUARY_ORIGINAL_TYPED_STAGE_V0_1.json"}
REFERENCE=RESULTS/"ONTO_TIME_FIVE_ECOSYSTEM_EVIDENCE_TIER_COMPARISON_V0_1.json"

def pre_stages(pair):
    species_a,species_b=pair["species_pair"].split("::")
    forward=[x for x in pair["edges"] if x["predator"]==species_a]
    backward=[x for x in pair["edges"] if x["predator"]==species_b]
    if not forward or not backward:
        raise ValueError("source receipt reciprocal direction inconsistency")
    return any(a["predator_stage"]!=b["prey_stage"] or
               a["prey_stage"]!=b["predator_stage"]
               for a in forward for b in backward)

def source_rows(a,b,c):
    pond_count=sum(pre_stages(p) for p in a["reciprocity"])
    if pond_count!=a["totals"]["n_named_species_pairs_with_links_in_both_directions"]:
        raise ValueError("pond reciprocal stage switch classifier drift")
    if a["totals"]["n_reciprocal_pairs_with_both_source_class_observed_and_stage_change"]!=0:
        raise ValueError("source observed true stage switch unexpectedly positive")
    out=[
      {"id":"CA_QUICK_POND","source_programme":"Preston2012",
       "all_interaction_stage_shift":pond_count,
       "predation_only_stage_shift":pond_count,"n_bivalve_motifs":0,
       "observed_bidirectional_stage_switch_status":"SOURCE_TAGGED_OBSERVED_ZERO"},
      {"id":"NZ_OTAGO_HARBOUR","source_programme":"Mouritsen2011",
       "all_interaction_stage_shift":b["totals"]["n_reciprocal_stage_shift_candidates_mixed_types"],
       "predation_only_stage_shift":b["totals"]["n_reciprocal_stage_shift_candidates_predation_only"],
       "n_bivalve_motifs":0,
       "observed_bidirectional_stage_switch_status":"NOT_ESTIMABLE_ORIGINAL_LINK_EVIDENCE_BLANK"},
    ]
    for site in ("CSM","EPB","BSQ"):
        entry=c["sites"][site]
        out.append({
           "id":"HECHINGER_"+site,"source_programme":"Hechinger2011",
           "all_interaction_stage_shift":entry["stage_shift_all_classes_strict_species"],
           "predation_only_stage_shift":entry["predation_only"]["stage_shift_candidate_pairs"],
           "n_bivalve_motifs":entry["bivalve_motif"]["n_pairs"],
           "observed_bidirectional_stage_switch_status":"NOT_ESTIMABLE_COMPILED_PROJECTED_META_LINKS"})
    return out

def compute(sources):
    rows=source_rows(sources["preston"],sources["otago"],sources["estuaries"])
    m=sum(x["all_interaction_stage_shift"] for x in rows)
    d=sum(x["predation_only_stage_shift"] for x in rows)
    counts={
      "n_local_ecosystems":len(rows),
      "n_independent_compilation_programmes":len({x["source_programme"] for x in rows}),
      "total_stage_shift_candidates_mixed_links_or_source_predation_only":m,
      "total_candidate_stage_shift_predation_only":d,
      "typed_filter_retention_fraction":d/m,
      "typed_filter_removed_fraction":1-d/m,
      "estimated_bivalve_module_site_pairs":sum(x["n_bivalve_motifs"] for x in rows),
      "preston_predation_only_original_stage_switch_source_tagged_both_directions_observed":0,
      "n_site_networks_without_direct_attack_evidence_field":sum(
          "NOT_ESTIMABLE" in x["observed_bidirectional_stage_switch_status"] for x in rows)
    }
    return {"counts":counts,"site_values":rows,
            "claim_ceiling":"These are cross-programme source graph structure differences and missing original direct-attack evidence. No true cross-system stage-reversal prevalence, timing or frog acoustic warning."}

def validate(out,source_file=REFERENCE):
    ref=json.loads(Path(source_file).read_text(encoding="utf-8"))
    want=ref["counts"]
    for key,v in out["counts"].items():
        if abs(v-want[key])>1e-12:
            raise ValueError("independent five-source source graph count changed: "+key)
    lhs={r["id"]:r for r in ref["local_ecosystems"]}
    for row in out["site_values"]:
        expected=lhs[row["id"]]
        for k,v in row.items():
            if expected[k]!=v:
                raise ValueError("site-level source class changes: "+row["id"]+" "+k)
    return True

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",required=True)
    args=p.parse_args()
    sources={key:json.loads(path.read_text(encoding="utf-8")) for key,path in SOURCES.items()}
    report=compute(sources)
    report["source_exact_readback"]=validate(report)
    Path(args.out).write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"status":"FIVE_SOURCE_TYPED_STAGE_EVIDENCE_MACRO_REPLAY",
                      "counts":report["counts"],
                      "original_source_aggregate_exact":report["source_exact_readback"]},ensure_ascii=False))
if __name__=="__main__":
    main()
