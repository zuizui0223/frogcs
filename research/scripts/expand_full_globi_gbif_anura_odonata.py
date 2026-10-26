#!/usr/bin/env python3
"""Expanded FULL GloBI source-defined stage edge → FULL GBIF Anura/Odonata grids.

- GloBI stage evidence from full fixed September 2026 24M Parquet source,
  only nonself species-stage predator/prey associations (not attacks).
- GBIF full August 2026 anonymous open-data Parquet partition source,
  Anura and Odonata entire orders, 2010–2026 1° lat/lon × month/year.
- Detailed source-study, missing-stage, taxonomy and GBIF effort boundaries.
This is a post-hoc public-data comparison, not a confirmation/causal study.
"""
from __future__ import annotations
import argparse
import collections
import csv
import json
import math
import time
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow.fs as fs
import pyarrow.parquet as pq

from gbif_open_full_stage_grid import (
    BUCKET, PARTITIONS, COLS, s3_list, selected_row_groups,
    normalized_stage, write_csv
)
ALLOWED={"Anura","Odonata"}
STAGES={"adult","aquatic_immature","juvenile","egg"}
FIELDS=[
    "predator","prey","predator_guild","prey_guild",
    "predator_stage","prey_stage","source_doi","reference_citation",
    "source_tier"
]


def source_edges(input_dir):
    f=list(Path(input_dir).rglob("full_nonself_staged_GloBI_provenance.csv"))
    if len(f)!=1:
        raise RuntimeError("Expected exactly one all-source full GloBI staged provenance export")
    all_rows=0
    eligible=collections.defaultdict(lambda:{"rows":0,"citations":set(),
                                               "source_dois":set(),"tiers":set()})
    species=set()
    unavailable=collections.Counter()
    for rec in csv.DictReader(f[0].open(encoding="utf8",newline="")):
        all_rows+=1
        guild1=rec["predator_guild"]
        guild2=rec["prey_guild"]
        if guild1 not in ALLOWED or guild2 not in ALLOWED:
            unavailable[(guild1,guild2)]+=1
            continue
        a=rec["predator"].strip()
        b=rec["prey"].strip()
        ps=rec["predator_stage"].strip()
        qs=rec["prey_stage"].strip()
        if a==b:
            raise RuntimeError("Self species link leaked into full GloBI nonself input")
        if ps not in STAGES or qs not in STAGES:
            raise RuntimeError("GloBI source staged non-canonical row unexpectedly included")
        key=(a,ps,b,qs)
        ed=eligible[key]
        ed["rows"]+=1
        ed["tiers"].add(rec.get("source_tier") or "unspecified")
        if rec.get("source_doi"):
            ed["source_dois"].add(rec["source_doi"])
        if rec.get("reference_citation"):
            ed["citations"].add(rec["reference_citation"])
        species.add(a);species.add(b)
    if all_rows!=1240:
        raise RuntimeError(f"Full GloBI staged input changed: {all_rows} instead of 1240")
    if not eligible:
        raise RuntimeError("No eligible full source-defined Anura/Odonata pair stages")
    if len(species)>600:
        raise RuntimeError(f"Excessive study-selected stage taxa ({len(species)}); analyze or partition order groups rather than outcome-driven cap")
    return {
        "original_source_rows":all_rows,
        "eligible":eligible,
        "species":sorted(species),
        "excluded_guilds":unavailable,
        "source_file":str(f[0])
    }


def reduce_rowgroups(parquet,groups,names,counts,stats,per_species):
    names_set=set(names)
    for group in groups:
        tbl=parquet.read_row_group(group,columns=COLS)
        frame=tbl.to_pandas()
        frame=frame.loc[frame.species.isin(names_set)].copy()
        stats["rows_with_target_taxon_name"]+=len(frame)
        if frame.empty:
            continue
        yr=pd.to_numeric(frame.year,errors="coerce")
        mo=pd.to_numeric(frame.month,errors="coerce")
        lat=pd.to_numeric(frame.decimalLatitude,errors="coerce")
        lon=pd.to_numeric(frame.decimalLongitude,errors="coerce")
        unc=pd.to_numeric(frame.coordinateUncertaintyInMeters,errors="coerce")
        passed=(frame.occurrenceStatus=="PRESENT") & (frame.hasGeospatialIssues==False)
        passed&=yr.between(2010,2026)&mo.between(1,12)
        passed&=lat.between(-90,90)&lon.between(-180,180)
        passed&=unc.isna()|unc.le(10000)
        frame=frame.loc[passed].copy()
        if frame.empty:continue
        stats["valid_coords_year_month"]+=len(frame)
        lifestage=frame.lifeStage.map(normalized_stage)
        good=lifestage.isin(STAGES)
        stats["n_stage_labeled_rows"]+=int(good.sum())
        if not good.any():continue
        frame=frame.loc[good].copy()
        y=yr.loc[passed].loc[good].astype("int16")
        m=mo.loc[passed].loc[good].astype("int8")
        x=lat.loc[passed].loc[good].map(math.floor).astype("int16")
        z=lon.loc[passed].loc[good].map(math.floor).astype("int16")
        frame["life_stage"]=lifestage.loc[good]
        frame["year"]=y
        frame["month"]=m
        frame["latcell"]=x
        frame["loncell"]=z
        for sp,n in frame.species.value_counts().items():
            per_species[sp]+=int(n)
        grouped=frame.groupby(
            ["species","life_stage","latcell","loncell","year","month"],
            dropna=False).size()
        for (species,stage,ilat,ilon,year,month),n in grouped.items():
            counts[(species,stage,int(ilat),int(ilon),int(year),int(month))]+=int(n)


def join_full_gbif_counts(counts,edges,available_species):
    # GBIF counts per species×stage in date-consistent gridded detection unit
    keys=collections.defaultdict(dict)
    for (sp,stage,lat,lon,year,month),n in counts.items():
        keys[(sp,stage)][(lat,lon,year,month)]=n
    rows=[]
    positive_month=0
    complete_stage=0
    missing_species=missing_stage=0
    for j,((pred,ps,prey,qs),info) in enumerate(sorted(edges.items()),1):
        src=keys.get((pred,ps),{})
        dst=keys.get((prey,qs),{})
        have_sp=pred in available_species and prey in available_species
        have_stages=bool(src and dst)
        if not have_sp:missing_species+=1
        elif not have_stages:missing_stage+=1
        else:complete_stage+=1
        if have_stages:
            exact=set(src)&set(dst)
            annual={(x,y,z) for x,y,z,m in src} & {
                (x,y,z) for x,y,z,m in dst}
            spatial={(x,y) for x,y,z,m in src} & {
                (x,y) for x,y,z,m in dst}
            robust={cell for cell in exact if src[cell]>=5 and dst[cell]>=5}
            n_e,n_a,n_s,n_rob=len(exact),len(annual),len(spatial),len(robust)
            positive_month+=int(n_e>0)
        else:
            n_e=n_a=n_s=n_rob=None
        rows.append(dict(
            edge_id=j,predator=pred,predator_stage=ps,
            prey=prey,prey_stage=qs,
            predator_gbif_stage_report_cells=len(src),
            prey_gbif_stage_report_cells=len(dst),
            gbif_predator_prey_species_covered=have_sp,
            gbif_both_stages_reporting_available=have_stages,
            same_1deg_grid= n_s,
            same_1deg_grid_year=n_a,
            same_1deg_grid_year_month=n_e,
            same_1deg_grid_year_month_both_min5=n_rob,
            source_interaction_rows=info["rows"],
            distinct_citation_strings=len(info["citations"]),
            distinct_original_source_dois=len(info["source_dois"]),
            source_tier=";".join(sorted(info["tiers"])),
            example_reference=";".join(sorted(info["citations"])[:2])[:450],
            qualifier=("OBSERVATION_REPORTING_COMPATIBILITY_ONLY" if have_stages
                       else "SOURCE_COVERAGE_MISSING_NOT_SPECIES_ABSENCE")))
    return rows,dict(
        total_source_staged_nonself_patterns=len(rows),
        gbif_both_source_species_covered=len(rows)-missing_species,
        gbif_both_stages_reporting_available=complete_stage,
        source_patterns_uncovered_species=missing_species,
        source_patterns_stages_not_reported=missing_stage,
        stage_patterns_with_same_1deg_month_year_reporting=positive_month,
        stage_patterns_with_both_min5_records_same_month_year=sum(
            (r["same_1deg_grid_year_month_both_min5"] or 0)>0 for r in rows)
    )


def run(src,output_dir):
    started=time.monotonic()
    source=source_edges(src)
    output=Path(output_dir);output.mkdir(parents=True,exist_ok=True)
    s3=fs.S3FileSystem(anonymous=True,region="us-east-1")
    counts=collections.Counter()
    study_species=source["species"]
    stats=collections.Counter()
    coverage=collections.Counter()
    receipts=[]
    for guild in ["Anura","Odonata"]:
        files=s3_list(PARTITIONS[guild])
        for file,size in files:
            with s3.open_input_file(f"{BUCKET}/{file}") as f:
                reader=pq.ParquetFile(f)
                groups,without_stats=selected_row_groups(
                    reader.metadata,file,study_species)
                reduce_rowgroups(reader,groups,study_species,
                                 counts,stats,coverage)
                receipts.append(dict(
                    guild=guild,parquet_file=f"s3://{BUCKET}/{file}",
                    parquet_bytes=size,
                    reported_rows=reader.metadata.num_rows,
                    total_rowgroups=reader.metadata.num_row_groups,
                    rowgroups_read=len(groups),
                    rowgroups_without_species_range=without_stats))
    if stats["valid_coords_year_month"]<1000:
        raise RuntimeError("Unexpectedly few GBIF data rows after audited scan")
    rows,join_summary=join_full_gbif_counts(
        counts,source["eligible"],set(coverage))
    if not rows:
        raise RuntimeError("No real full-source staged pair rows")
    source_counts=collections.Counter(
        (r["predator_stage"],r["prey_stage"]) for r in rows)
    write_csv(output/"source_fixed_nonself_stage_pair_grids.csv",rows,[
        "edge_id","predator","predator_stage","prey","prey_stage",
        "predator_gbif_stage_report_cells","prey_gbif_stage_report_cells",
        "gbif_predator_prey_species_covered",
        "gbif_both_stages_reporting_available","same_1deg_grid",
        "same_1deg_grid_year","same_1deg_grid_year_month",
        "same_1deg_grid_year_month_both_min5",
        "source_interaction_rows","distinct_citation_strings",
        "distinct_original_source_dois","source_tier",
        "example_reference","qualifier"])
    compact=[dict(species=sp,stage=stage,latcell=lat,loncell=lon,
                  year=year,month=month,n_records=n)
             for (sp,stage,lat,lon,year,month),n in sorted(counts.items())]
    write_csv(output/"focal_full_Anura_Odonata_stage_grids.csv",compact,[
        "species","stage","latcell","loncell","year","month","n_records"])
    summary={
        "date":"2026-10-25",
        "source_globi":"fixed v0.11 DOI 10.5281/zenodo.22691479; full predator-prey staged nonself records selected independently of GBIF maps",
        "source_gbif":"GBIF public experimental August 2026 entire taxon partitions Anura and Odonata only",
        "input_full_globi_valid_nonself_stage_rows":source["original_source_rows"],
        "input_anura_odonata_both_sides_source_row_patterns":sum(x["rows"]
            for x in source["eligible"].values()),
        "input_eligible_distinct_stage_pair_patterns":len(source["eligible"]),
        "input_eligible_species":len(study_species),
        "excluded_other_guild_source_rows":sum(source["excluded_guilds"].values()),
        "excluded_source_guild_pairs":[
            dict(predator_guild=a,prey_guild=b,rows=n)
            for (a,b),n in source["excluded_guilds"].most_common(20)],
        "gbif_order_files":receipts,
        "gbif_rows_with_selected_species_before_QC":stats["rows_with_target_taxon_name"],
        "gbif_rows_valid_geo_time":stats["valid_coords_year_month"],
        "gbif_rows_known_lifestage":stats["n_stage_labeled_rows"],
        "gbif_species_with_valid_records":len(coverage),
        "gbif_stage_species_cell_year_month_rows":len(counts),
        "source_stage_pattern_types":[dict(predator_stage=a,prey_stage=b,patterns=n)
                for (a,b),n in source_counts.most_common()],
        "matched_source_stage_grid":join_summary,
        "source_edge_examples":[r for r in sorted(rows,
            key=lambda x:-(x["same_1deg_grid_year_month"] or 0))[:16]],
        "elapsed_seconds":round(time.monotonic()-started,2),
        "scientific_boundaries":[
            "Taxonomy equality here is literal interpreted GloBI/GBIF species name, not synonym-aware global canonical identity.",
            "The source eligibility is Anura or Odonata BOTH sides, because only those two anonymized full public order partitions are audited and accessible; Caudata/Dytiscidae not tested or treated as biologically absent.",
            "Interpreted GloBI feeding metaweb links are not independently witnessed predation events.",
            "A GBIF 1° grid×month×year shared detection is not pond-level predator/prey interaction, local hydroperiod or consumed prey.",
            "Many GBIF lifeStage records are absent and many valid cells are not surveyed; reports reflect sampling bias.",
            "GBIF experimental August 2026 taxonomy can differ from GloBI September 2026 and official GBIF current accepted names.",
            "Shared cell detection can include introduced/out-of-native-range populations.",
            "No causal link to frog reproductive chorus, rainfall, emergent plant architecture or predation mortality is fitted."
        ]
    }
    (output/"observed_results.json").write_text(
        json.dumps(summary,indent=2,ensure_ascii=False)+"\n",encoding="utf8")
    print("BEGIN_EXPANDED_FULL_GLOBI_GBIF_STAGE_GRID")
    print(json.dumps({
        "source_stage_patterns":len(source["eligible"]),
        "source_selected_species":len(study_species),
        "gbif_valid_records":stats["valid_coords_year_month"],
        "gbif_staged_records":stats["n_stage_labeled_rows"],
        "gbif_stage_grid_rows":len(counts),
        "matched_source_stage_grid":join_summary,
        "first_pairs":summary["source_edge_examples"][:9],
        "elapsed_seconds":summary["elapsed_seconds"],
    },indent=2,ensure_ascii=False))
    print("END_EXPANDED_FULL_GLOBI_GBIF_STAGE_GRID")
    return summary


def synthetic():
    data=collections.defaultdict(lambda:{"rows":0,"citations":set(),
                                         "source_dois":set(),"tiers":set()})
    a=("Anax junius","aquatic_immature","Anaxyrus boreas","aquatic_immature")
    data[a]["rows"]=1
    counts={
        ("Anax junius","aquatic_immature",33,-118,2024,6):3,
        ("Anaxyrus boreas","aquatic_immature",33,-118,2024,6):4,
    }
    fake_source=collections.Counter({"Anax junius":3,"Anaxyrus boreas":4})
    rows,summary=join_full_gbif_counts(counts,data,set(fake_source))
    assert summary["stage_patterns_with_same_1deg_month_year_reporting"]==1
    assert rows[0]["same_1deg_grid_year_month"]==1
    assert rows[0]["same_1deg_grid_year_month_both_min5"]==0
    assert rows[0]["predator"]!=rows[0]["prey"]
    print("EXPANDED_FULL_SOURCE_GBIF_STAGED_1DEG_GRID_QA_PASS")


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--globi-artifact",default="research/data/full_globi_stage_artifact")
    p.add_argument("--out",default="research/results/gbif_open_expanded_anura_odonata")
    p.add_argument("--self-test",action="store_true")
    args=p.parse_args()
    if args.self_test:synthetic()
    else:run(args.globi_artifact,args.out)
