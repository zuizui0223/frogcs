#!/usr/bin/env python3
"""Source-pinned expanded 78-pattern full GloBI × GBIF 1° prey specificity check.

Apply unchanged protocol from prior 18-edge control to expanded *both-side*
Anura/Odonata stage edges. 2026-10-25 exploratory post-readback sensitivity.
Source is full fixed GloBI v0.11 and GBIF public experimental full partitions.
No true negative feeding edges or causal temporal predator attraction inferred.
"""
import argparse
import csv
import json
from pathlib import Path

from fixed_globi_gbif_month_shift_null import read_cell_cubes
from globi_gbif_prey_specificity_controls import (
    prepare_taxa,compare,summary,write_csv
)

def load_expanded(path,groups):
    rows=[]
    seen=set()
    with Path(path).open(encoding="utf8",newline="") as f:
        reader=csv.DictReader(f)
        expected={"predator","prey","predator_stage","prey_stage",
                  "source_tier","source_interaction_rows",
                  "gbif_both_stages_reporting_available"}
        if not expected.issubset(reader.fieldnames or []):
            raise ValueError("Expanded full GloBI×GBIF stage-source column schema changed")
        for r in reader:
            a,b=r["predator"],r["prey"]
            ps,qs=r["predator_stage"],r["prey_stage"]
            if a==b:
                continue
            if str(r["gbif_both_stages_reporting_available"]).lower()!="true":
                continue
            ga,gb=groups.get(a),groups.get(b)
            if ga not in {"Anura","Odonata"} or gb not in {"Anura","Odonata"}:
                raise ValueError("Original full-source guild metadata cannot validate "+a+" "+b)
            key=(a,ps,b,qs)
            if key in seen:
                raise ValueError("Expanded full GloBI duplicate directed stage pattern")
            seen.add(key)
            rows.append(dict(
                predator=a,prey=b,predator_stage=ps,prey_stage=qs,
                predator_guild=ga,prey_guild=gb,
                source_tiers=r["source_tier"],
                source_rows=r["source_interaction_rows"],
                example_reference=r.get("example_reference",""),
                source_dois=""))
    return rows

def run(gbif,edges,provenance,out):
    target=Path(out);target.mkdir(parents=True,exist_ok=True)
    masks,qc=read_cell_cubes(gbif)
    groups,known=prepare_taxa(provenance)
    linked=load_expanded(edges,groups)
    row,excluded,selected=compare(masks,linked,groups,known)
    summ=summary(row,excluded,linked,qc,groups)
    summ.update({
        "study":"Post-readback application of same guild-stage prey control to expanded 2026-09 GloBI×2026-08 GBIF Anura/Odonata global stage links",
        "GloBI_source":"https://doi.org/10.5281/zenodo.22691479",
        "GBIF_source_run":"https://github.com/zuizui0223/frogcs/actions/runs/40194946916",
        "full_source_eligible_anura_odonata_stage_links_before_QC":78,
        "full_source_eligible_both_stage_recorded_in_expanded_GBIF":len(linked),
        "GBIF_full_expanded_grid_input_rows":qc["rows"],
        "matched_preys_are_not_known_true_negative_interactions":True,
        "specificity_hypothesis_status":"POST_READBACK_EXPLORATORY_NOT_PREREGISTERED",
        "scientific_bounds":[
            "No actual predator-prey attack, abundance, wetland vegetation, rainfall or frog chorus was measured.",
            "Same-guild/stage matched alternatives are undocumented in full-stage GloBI subset, not non-interactors.",
            "The expanded sample is dominantly adult Anura/Odonata and thus does not validate worldwide larval role reversal.",
            "GBIF source is anonymous 2026-08 experimental partitions, not official DOI-traceable October bulk download.",
            "GBIF stage reporting within 1° month-year is highly seasonally and spatially biased.",
            "If controls are too rare or 8 distinct predator taxa are unavailable, inferential uncertainty is not estimated."
        ]
    })
    if row:
        write_csv(target/"matched_prey_control_comparisons.csv",row)
    (target/"observed_results.json").write_text(
        json.dumps(summ,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    print("BEGIN_EXPANDED_GLOBI_PREY_SPECIFICITY")
    print(json.dumps(summ,ensure_ascii=False,indent=2))
    print("END_EXPANDED_GLOBI_PREY_SPECIFICITY")

def selftest():
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        p=Path(d)/"edges.csv"
        p.write_text(
            "predator,prey,predator_stage,prey_stage,source_tier,"
            "source_interaction_rows,gbif_both_stages_reporting_available\n"
            "A a,B b,adult,adult,INAT_LINK_OR_ORIGINAL_OBSERVATION,3,True\n"
            "A a,C c,adult,adult,OTHER_INDEXED_ASSOCIATION,1,False\n",encoding="utf8")
        z=load_expanded(p,{"A a":"Anura","B b":"Odonata","C c":"Odonata"})
        assert len(z)==1 and z[0]["prey"]=="B b"
    print("EXPANDED_STAGE_PREY_SPECIFICITY_QA_PASS")

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--gbif",default="research/data/expanded/focal_full_Anura_Odonata_stage_grids.csv")
    p.add_argument("--edges",default="research/data/expanded/source_fixed_nonself_stage_pair_grids.csv")
    p.add_argument("--provenance",default="research/data/globi/full_nonself_staged_GloBI_provenance.csv")
    p.add_argument("--out",default="research/results/expanded_stage_specificity")
    p.add_argument("--self-test",action="store_true")
    a=p.parse_args()
    if a.self_test:selftest()
    else:run(a.gbif,a.edges,a.provenance,a.out)
