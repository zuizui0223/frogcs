#!/usr/bin/env python3
"""Full frozen GloBI 24.45M → verified non-self stage links → GBIF 1° grid.

GloBI version 0.11: 2026-09-10, DOI 10.5281/zenodo.22691479.
Independent open GBIF August 2026 1° Anura/Odonata Parquet artifact from
previous successful data workflow (run_id 40190152042).
Biological inference boundary: observed species-stage reporting compatibility,
NOT verified feeding, individual site fidelity or stage dominance reversal.
"""
import argparse
import collections
import csv
import json
import math
import re
import tempfile
import time
from pathlib import Path

import duckdb

from run_globi_fixed_full_foodweb import (
    GLOBI_BYTES, GLOBI_MD5, GLOBI_ROWS, download, quote_source, select_context
)

CANON={"adult","aquatic_immature","egg","juvenile"}
AMBIGUOUS=re.compile(
    r"juv\./adults|juvenile/adult|juveniles and adults|"
    r"larvae/adults|larv\./adults|adult and juvenile|"
    r"adults/juveniles|juvenile & adult|larva and adult", re.I)


def life_stage(value):
    s=str(value or "").strip().lower()
    if (s in ("", "-999", "unknown", "not recorded", "none",
              "missing", "(missing)", "unspecified")
            or AMBIGUOUS.search(s)):
        return ""
    if "post-juvenile adult" in s:
        return "adult"
    if any(t in s for t in ("larv", "tadpol", "nymph", "instar")):
        return "aquatic_immature"
    if "pupa" in s or "pupal" in s:
        return "pupa"
    if "egg" in s or "embryo" in s:
        return "egg"
    if any(t in s for t in ("juvenil", "subadult", "young", "immature")):
        return "juvenile"
    if "adult" in s or "imago" in s:
        return "adult"
    return ""


def citation_tier(reference, source_doi):
    s=(str(reference or "")+" "+str(source_doi or "")).lower()
    if "preston" in s and ("food web" in s or "california" in s):
        return "INTERPRETED_QUICK_POND_META_WEB"
    if "iNaturalist.org/observations/".lower() in s:
        return "INAT_LINK_OR_ORIGINAL_OBSERVATION"
    if "trophic meta-web" in s or "tetra-eu" in s:
        return "INTERPRETED_LITERATURE_META_WEB"
    if not s.strip():
        return "NO_PROVENANCE"
    return "OTHER_INDEXED_ASSOCIATION"


def verify_source(source, focus):
    result={"source_download":source, "full_source_parquet_rows":GLOBI_ROWS,
            "focal_rows":focus}
    if source["md5"] != GLOBI_MD5 or source["bytes"] != GLOBI_BYTES:
        raise ValueError("GloBI full-source integrity check failed")
    return result


def gbif_reported_cube(path):
    files=list(Path(path).rglob("focal_stage_1deg_month_year.csv"))
    if len(files)!=1:
        raise RuntimeError("Expected exactly one GloBI-aligned GBIF grid artifact CSV; found "+str(files))
    coverage=collections.Counter()
    packed=collections.defaultdict(dict)
    total_rows=0
    with files[0].open(newline="",encoding="utf8") as f:
        for row in csv.DictReader(f):
            total_rows+=1
            sp=row["species"].strip()
            stage=row["stage"].strip()
            if stage not in CANON:
                continue
            try:
                n=int(row["n_records"])
                key=(int(row["latcell"]),int(row["loncell"]),
                     int(row["year"]),int(row["month"]))
            except (ValueError,KeyError):
                continue
            if n<1:continue
            coverage[sp]+=n
            old=packed[(sp,stage)].get(key,0)
            packed[(sp,stage)][key]=old+n
    if total_rows<50000 or len(coverage)<35:
        raise RuntimeError("Expected prior full 1° GBIF experiment; source incomplete")
    return {
        "source_csv":str(files[0]),
        "grid_records":total_rows,
        "available_species":len(coverage),
        "counts":packed,
        "species":coverage
    }


def features(records, key):
    return records.get(key,{})


def aggregate_edge_rows(rows):
    raw_nonself=[]
    raw_self=0
    stage_unknown=0
    stage_mixed=0
    ambiguous_examples=collections.Counter()
    edges=collections.defaultdict(lambda:{
        "rows":0,"source_dois":set(),"refs":set(),"original_labels":set(),
        "citation_examples":set(),"source_tiers":set()})
    for r in rows:
        (pred,prey,pg,qg,pstage,qstage,ref,refdoi,sourcedoi,
         namespace,lat,lon,eventdate)=r
        if pred==prey:
            raw_self+=1
            continue
        ps=life_stage(pstage)
        qs=life_stage(qstage)
        if AMBIGUOUS.search(str(pstage or "")) or AMBIGUOUS.search(str(qstage or "")):
            stage_mixed+=1
        if ps not in CANON or qs not in CANON:
            stage_unknown+=1
            ambiguous_examples[(str(pstage),str(qstage))]+=1
            continue
        src_kind=citation_tier(ref,sourcedoi)
        raw_nonself.append({
            "predator":pred,"prey":prey,"predator_guild":pg,
            "prey_guild":qg,"predator_stage":ps,"prey_stage":qs,
            "original_predator_stage":str(pstage or ""),
            "original_prey_stage":str(qstage or ""),
            "source_doi":str(sourcedoi or ""),
            "reference_doi":str(refdoi or ""),
            "source_namespace":str(namespace or ""),
            "reference_citation":str(ref or "")[:600],
            "source_tier":src_kind,
            "latitude":lat if lat is not None else "",
            "longitude":lon if lon is not None else "",
            "event_date":str(eventdate or ""),
            "source_claim":"indexed_trophic_association_not_verified_attack"
        })
        key=(pred,prey,ps,qs)
        e=edges[key]
        e["rows"]+=1
        if sourcedoi:e["source_dois"].add(str(sourcedoi))
        if ref:e["refs"].add(str(ref))
        e["original_labels"].add((str(pstage),str(qstage)))
        if ref and len(e["citation_examples"])<5:
            e["citation_examples"].add(str(ref)[:250])
        e["source_tiers"].add(src_kind)
    return {
        "valid_rows":raw_nonself,
        "patterns":edges,
        "raw_self":raw_self,
        "raw_missing_or_noncanonical":stage_unknown,
        "raw_ambiguous_composite":stage_mixed,
        "stage_exclusion_examples":ambiguous_examples.most_common(15),
    }


def overlap_patterns(patterns, cube):
    cells=cube["counts"]
    eligible=set(cube["species"])
    out=[]
    for idx,((pred,prey,ps,qs),val) in enumerate(sorted(patterns.items()),1):
        pred_cube=cells.get((pred,ps),{})
        prey_cube=cells.get((prey,qs),{})
        pred_included=pred in eligible
        prey_included=prey in eligible
        pair_covered=bool(pred_cube and prey_cube)
        if pair_covered:
            pred_grid=set((a,b) for a,b,y,m in pred_cube)
            prey_grid=set((a,b) for a,b,y,m in prey_cube)
            pred_year=set((a,b,y) for a,b,y,m in pred_cube)
            prey_year=set((a,b,y) for a,b,y,m in prey_cube)
            both=set(pred_cube)&set(prey_cube)
            both5={cell for cell in both if pred_cube[cell]>=5 and prey_cube[cell]>=5}
            spatial=len(pred_grid&prey_grid)
            year=len(pred_year&prey_year)
            exact=len(both)
        else:
            spatial=year=exact=None
            both5=set()
        if not pred_included or not prey_included:
            condition="GBIF_SPECIES_NOT_INCLUDED_IN_PREVIOUS_FOCAL_61"
        elif not pair_covered:
            condition="GBIF_SAME_STAGE_RECORDS_UNAVAILABLE_OR_NOT_DETECTED"
        else:
            condition="GBIF_1DEG_REPORT_COMPATIBILITY_NOT_VERIFIED_ENCOUNTER"
        tiers=sorted(val["source_tiers"])
        out.append(dict(
            pattern_id=idx,predator=pred,prey=prey,
            predator_stage=ps,prey_stage=qs,
            focal_gbif_predator_species_included=pred_included,
            focal_gbif_prey_species_included=prey_included,
            gbif_predator_stage_cells=len(pred_cube),
            gbif_prey_stage_cells=len(prey_cube),
            gbif_both_stage_reporting_available=pair_covered,
            shared_1deg_spatial_cells=spatial,
            shared_1deg_cell_year=year,
            shared_1deg_cell_year_month=exact,
            shared_1deg_cell_year_month_both_atleast5=(
                len(both5) if pair_covered else None),
            source_rows=val["rows"],
            distinct_reference_citations=len(val["refs"]),
            original_source_doi_count=len(val["source_dois"]),
            source_dois="; ".join(sorted(val["source_dois"]))[:500],
            citation_examples=" | ".join(sorted(val["citation_examples"]))[:800],
            original_stages="; ".join(sorted(
                f"{a}->{b}" for a,b in val["original_labels"]))[:300],
            source_tiers="; ".join(tiers),
            eligibility=condition))
    return out


def write_csv(path,rows,head):
    with Path(path).open("w",newline="",encoding="utf8") as f:
        writer=csv.DictWriter(f,fieldnames=head,extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def run(outdir,gbifdir):
    out=Path(outdir);out.mkdir(parents=True,exist_ok=True)
    started=time.monotonic()
    gbif=gbif_reported_cube(gbifdir)
    with tempfile.TemporaryDirectory(prefix="frogcs_full_stage_") as temp:
        file=Path(temp)/"interactions.parquet"
        receipt=download(file)
        con=duckdb.connect(str(Path(temp)/"scratch.duckdb"))
        con.execute("SET threads=2")
        con.execute("SET memory_limit='3GB'")
        con.execute("SET preserve_insertion_order=false")
        con.execute("SET enable_progress_bar=false")
        con.execute(f"CREATE TEMP TABLE focus AS {select_context('read_parquet('+quote_source(str(file))+')')}")
        source_rows=int(con.execute("SELECT COUNT(*) FROM focus").fetchone()[0])
        if source_rows!=77720:
            raise RuntimeError("Full pinned source focal filter changed; must reconcile")
        original_staged=con.execute("""
          SELECT predator,prey,predator_guild,prey_guild,ps,qs,
                 reference,reference_doi,source_doi,source_namespace,
                 lat,lon,eventdate
          FROM focus
          WHERE ps IS NOT NULL AND qs IS NOT NULL
        """).fetchall()
        con.close()
    result=aggregate_edge_rows(original_staged)
    all_edges=result["patterns"]
    rr=overlap_patterns(all_edges,gbif)
    pairs={ (x["predator"],x["prey"]) for x in rr }
    reverse=sorted(set(tuple(sorted((a,b))) for (a,b) in pairs
                       if a!=b and (b,a) in pairs))
    covered=[x for x in rr if x["gbif_both_stage_reporting_available"]]
    nonzero=[x for x in covered if (x["shared_1deg_cell_year_month"] or 0)>0]
    # Count source DOI, evidence-class and all stage types on an independent
    # pattern (not study) basis; avoid treating GloBI rows as attacks.
    bysource=collections.Counter()
    for rec in result["valid_rows"]:
        bysource[rec["source_tier"]]+=1
    globi_stage_summary={
        "fixed_full_globi_source":"https://doi.org/10.5281/zenodo.22691479",
        "globi_source_md5":receipt["md5"],
        "total_full_source_rows":GLOBI_ROWS,
        "full_focal_feeding_rows":source_rows,
        "raw_both_stages_populated_rows":len(original_staged),
        "self_species_raw_stage_rows_excluded":result["raw_self"],
        "nonself_stage_unknown_or_not_canonical_excluded":
            result["raw_missing_or_noncanonical"],
        "nonself_stage_ambiguous_composite_excluded":
            result["raw_ambiguous_composite"],
        "valid_certain_nonself_raw_stage_rows":len(result["valid_rows"]),
        "unique_valid_nonself_directed_stage_pairs":len(all_edges),
        "unique_valid_nonself_directed_species_pairs":len(pairs),
        "distinct_both_direction_different_species_candidates":
            len(reverse),
        "reversal_candidate_examples":reverse[:20],
        "n_distinct_original_source_dois":len(set(
            r["source_doi"] for r in result["valid_rows"] if r["source_doi"])),
        "n_distinct_reference_citations":len(set(
            r["reference_citation"] for r in result["valid_rows"]
            if r["reference_citation"])),
        "source_tier_record_counts":dict(bysource),
        "stage_exclusion_examples":result["stage_exclusion_examples"],
    }
    gbif_summary={
        "stage_grid_source":"GBIF experimental August 2026 anonymous parquet Anura+Odonata",
        "gbif_source_run":"https://github.com/zuizui0223/frogcs/actions/runs/40190152042",
        "gbif_stage_grid_csv_rows":gbif["grid_records"],
        "gbif_species_included":gbif["available_species"],
        "gbif_reported_records_for_selected_species":sum(gbif["species"].values()),
        "both_stage_grid_covered_patterns":len(covered),
        "both_stage_covered_pairs_with_same_1deg_cell_year_month":len(nonzero),
        "both_stage_covered_pairs_with_same_grid_year_month_atleast5_each":sum(
            (x["shared_1deg_cell_year_month_both_atleast5"] or 0)>0
            for x in covered),
        "source_patterns_without_both_species_in_previous_GBIF_scan":sum(
            x["eligibility"]=="GBIF_SPECIES_NOT_INCLUDED_IN_PREVIOUS_FOCAL_61"
            for x in rr),
        "source_patterns_species_present_but_stage_unreported":sum(
            x["eligibility"]=="GBIF_SAME_STAGE_RECORDS_UNAVAILABLE_OR_NOT_DETECTED"
            for x in rr),
        "candidate_pairs_with_positive_grid_examples":sorted(nonzero,
            key=lambda x:(
                -(x["shared_1deg_cell_year_month"] or 0),
                -x["distinct_reference_citations"],
                x["predator"],x["prey"]))[:15]
    }
    raw_head=[
        "predator","prey","predator_guild","prey_guild",
        "predator_stage","prey_stage","original_predator_stage",
        "original_prey_stage","source_doi","reference_doi",
        "source_namespace","reference_citation","source_tier",
        "latitude","longitude","event_date","source_claim"]
    write_csv(out/"full_nonself_staged_GloBI_provenance.csv",
              result["valid_rows"],raw_head)
    head=list(rr[0]) if rr else []
    write_csv(out/"nonself_stage_pair_grid_results.csv",rr,head)
    summary={
        "date":"2026-10-25",
        "status":"POSTHOC_GLOBAL_FIXED_GLOBI_GBIF_STAGE_GRID_REPAIR",
        "source_integrity":{
            **verify_source(receipt,source_rows),
            "elapsed_seconds_total":round(time.monotonic()-started,2)
        },
        "full_globi_stages":globi_stage_summary,
        "gbif_grid":gbif_summary,
        "bounds":[
            "Stage-directed GloBI association is NOT independently verified predation; raw sources may be inferred metawebs.",
            "Only 61 source-selected GBIF Anura/Odonata taxa covered, not the entire global taxonomic pool.",
            "Species stage absence in GBIF grid is an unmeasured/undetected reporting cell, not ecological absence.",
            "One-degree cell×year×month observational concordance is NOT live local predator-prey contact or attack.",
            "GBIF anonymous Parquet is experimental, with taxonomy and data-release mismatch relative to GloBI 2026-09.",
            "Reference citation strings and GloBI source DOI are provenance fields, not independent attack event counts.",
            "No claim of global trophic reversal prevalence or causal macrophyte/rainfall effects."
        ]}
    (out/"observed_results.json").write_text(json.dumps(summary,indent=2,
                                      ensure_ascii=False)+"\n",encoding="utf8")
    print("BEGIN_FULL_STAGE_FIXED_SOURCE_GRID_RESULTS")
    print(json.dumps(summary,indent=2,ensure_ascii=False))
    print("END_FULL_STAGE_FIXED_SOURCE_GRID_RESULTS")
    return summary


def test():
    assert life_stage("post-juvenile adult stage")=="adult"
    assert life_stage("larval")=="aquatic_immature"
    assert life_stage("juv./adults")==""
    assert life_stage("-999")==""
    rows=[
        ("Anax junius","Anaxyrus boreas","Odonata","Anura",
         "larval","larval","Preston California food web 2012",
         "", "source1","dataset",30,-99,""),
        ("Anaxyrus boreas","Anax junius","Anura","Odonata",
         "adult","larval","reference", "","source2","dataset",30,-99,""),
        ("Anax junius","Anax junius","Odonata","Odonata",
         "adult","adult","reference","","source3","dataset",31,-100,""),
    ]
    data=aggregate_edge_rows(rows)
    assert data["raw_self"]==1 and len(data["patterns"])==2
    assert len(data["valid_rows"])==2
    counts={
        ("Anax junius","aquatic_immature"):{(30,-99,2024,6):2},
        ("Anaxyrus boreas","aquatic_immature"):{(30,-99,2024,6):1},
        ("Anaxyrus boreas","adult"):{(30,-99,2024,6):6},
    }
    cube={"counts":counts,"species":{"Anax junius":2,"Anaxyrus boreas":7}}
    result=overlap_patterns(data["patterns"],cube)
    assert len(result)==2 and all(x["shared_1deg_cell_year_month"]==1 for x in result)
    assert all(x["predator"]!=x["prey"] for x in result)
    print("FULL_GLOBI_GBIF_1DEG_SOURCE_STAGE_GRID_QA_PASS")


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--out",default="research/results/full_globi_2026_stage_gbif_grid")
    parser.add_argument("--gbif-artifact",default="research/data/gbif_open_artifact")
    parser.add_argument("--self-test",action="store_true")
    a=parser.parse_args()
    if a.self_test:test()
    else:run(a.out,a.gbif_artifact)
