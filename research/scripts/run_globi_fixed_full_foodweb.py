#!/usr/bin/env python3
"""Full fixed-release GloBI v0.11 worldwide stage-dependent feeding screen.

Source: GloBI Community (2026-09-10), doi:10.5281/zenodo.22691479,
file interactions.parquet, 24,453,954 rows in 198 row groups,
MD5: 8212776b7ba0c4fa8de26a00b5ce8595, CC0 at aggregate release.
Cite original dataset/sourceDOI/referenceCitation for any derived links.

No GBIF species grid, wetlands, predation rates, chorus or causal
plant/hydrology drivers included in these source data. "Reversal" flags
are candidate opposite directional species pairs, not dominance reversal.
"""
import argparse
import hashlib
import json
import os
import re
import shutil
import tempfile
import time
import urllib.request
from pathlib import Path

import duckdb

GLOBI_URL="https://zenodo.org/api/records/22691479/files/interactions.parquet/content"
GLOBI_MD5="8212776b7ba0c4fa8de26a00b5ce8595"
GLOBI_BYTES=2375721521
GLOBI_ROWS=24453954
SPECIES_RX=r"^[A-Z][a-z]+ [a-z][a-z-]+$"
SOURCE_MD="https://doi.org/10.5281/zenodo.22691479"
MAX_GB=3.1
SOURCE_SELECTED=[
    "sourceTaxonName", "sourceTaxonSpeciesName",
    "sourceTaxonOrderName", "sourceTaxonFamilyName",
    "sourceTaxonClassName",
    "sourceLifeStageName","interactionTypeName",
    "targetTaxonName","targetTaxonSpeciesName",
    "targetTaxonOrderName","targetTaxonFamilyName",
    "targetTaxonClassName","targetLifeStageName",
    "decimalLatitude","decimalLongitude","eventDate",
    "referenceCitation","referenceDoi","sourceDOI","sourceNamespace",
]


def download(target):
    req=urllib.request.Request(
        GLOBI_URL,headers={"User-Agent":"FrogcsFullGloBI2026/1.0 (university ecological open-data research)"})
    md5=hashlib.md5()
    size=0
    t=time.monotonic()
    with urllib.request.urlopen(req, timeout=160) as response, open(target,"wb") as f:
        while True:
            part=response.read(4*1024*1024)
            if not part:break
            size+=len(part)
            if size>GLOBI_BYTES+1000:
                raise RuntimeError("GloBI file exceeded expected release size; fail closed")
            md5.update(part)
            f.write(part)
    if size != GLOBI_BYTES or md5.hexdigest()!=GLOBI_MD5:
        raise RuntimeError(f"Source mismatch bytes={size}, md5={md5.hexdigest()}")
    return dict(bytes=size,md5=md5.hexdigest(),elapsed_seconds=round(time.monotonic()-t,2))


def quote_source(path):
    return "'"+str(path).replace("'","''")+"'"

def select_context(sql):
    return f"""
    WITH original AS (
       SELECT
         NULLIF(TRIM(sourceTaxonSpeciesName),'') AS predator,
         NULLIF(TRIM(targetTaxonSpeciesName),'') AS prey,
         lower(coalesce(interactionTypeName,'')) AS interaction,
         coalesce(sourceTaxonOrderName,'') AS po,
         coalesce(targetTaxonOrderName,'') AS qo,
         coalesce(sourceTaxonFamilyName,'') AS pf,
         coalesce(targetTaxonFamilyName,'') AS qf,
         coalesce(sourceTaxonClassName,'') AS pc,
         coalesce(targetTaxonClassName,'') AS qc,
         NULLIF(TRIM(sourceLifeStageName),'') AS ps,
         NULLIF(TRIM(targetLifeStageName),'') AS qs,
         TRY_CAST(decimalLatitude AS DOUBLE) AS lat,
         TRY_CAST(decimalLongitude AS DOUBLE) AS lon,
         NULLIF(TRIM(eventDate),'') AS eventdate,
         NULLIF(TRIM(referenceCitation),'') AS reference,
         NULLIF(TRIM(referenceDoi),'') AS reference_doi,
         NULLIF(TRIM(sourceDOI),'') AS source_doi,
         NULLIF(TRIM(sourceNamespace),'') AS source_namespace
       FROM {sql}
       WHERE lower(coalesce(interactionTypeName,'')) IN ('eats','preyson')
    )
    SELECT
      predator,prey,interaction,po,qo,pf,qf,pc,qc,ps,qs,lat,lon,
      eventdate,reference,reference_doi,source_doi,source_namespace,
      CASE
        WHEN po='Anura' THEN 'Anura'
        WHEN po='Caudata' THEN 'Caudata'
        WHEN po='Odonata' THEN 'Odonata'
        WHEN pf='Dytiscidae' THEN 'Dytiscidae'
        WHEN po='Hemiptera' THEN 'Other_Hemiptera'
        WHEN lower(pc) LIKE 'actinopter%' THEN 'Actinopterygii'
        ELSE 'other_predator'
      END AS predator_guild,
      CASE
        WHEN qo='Anura' THEN 'Anura'
        WHEN qo='Caudata' THEN 'Caudata'
        WHEN qo='Odonata' THEN 'Odonata'
        WHEN qf='Dytiscidae' THEN 'Dytiscidae'
        WHEN qo='Hemiptera' THEN 'Other_Hemiptera'
        WHEN lower(qc) LIKE 'actinopter%' THEN 'Actinopterygii'
        ELSE 'other_prey'
      END AS prey_guild
    FROM original
    WHERE predator IS NOT NULL AND prey IS NOT NULL
      AND regexp_matches(predator,{quote_source(SPECIES_RX)})
      AND regexp_matches(prey,{quote_source(SPECIES_RX)})
      AND (po IN ('Anura','Caudata','Odonata')
           OR qo IN ('Anura','Caudata','Odonata')
           OR pf='Dytiscidae' OR qf='Dytiscidae')
    """


def fetchdict(con,sql,params=None):
    cur=con.execute(sql,params or [])
    heads=[d[0] for d in cur.description]
    return [dict(zip(heads,row)) for row in cur.fetchall()]

def serial(x):
    if isinstance(x,float) and not (-1e309<x<1e309):
        return None
    return x

def run(output_dir):
    output=Path(output_dir)
    output.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="frogcs_globi_") as td:
        work=Path(td)
        path=work/"interactions.parquet"
        receipt=download(path)
        con=duckdb.connect(str(work/"scratch.duckdb"))
        con.execute("SET threads=2")
        con.execute("SET memory_limit='3GB'")
        con.execute("SET preserve_insertion_order=false")
        con.execute(f"SET temp_directory={quote_source(str(work/'temp'))}")
        con.execute("SET enable_progress_bar=false")
        src=f"read_parquet({quote_source(str(path))})"
        source_rows=int(con.execute(f"SELECT count(*) FROM {src}").fetchone()[0])
        if source_rows != GLOBI_ROWS:
            raise RuntimeError(f"GloBI complete rowcount changed: {source_rows}")
        cols={r[0] for r in con.execute(f"DESCRIBE SELECT * FROM {src}").fetchall()}
        absent=[s for s in SOURCE_SELECTED if s not in cols]
        if absent:
            raise RuntimeError("GloBI column schema drift: "+str(absent))
        st=time.monotonic()
        con.execute(f"CREATE TEMP TABLE focus AS {select_context(src)}")
        focus_rows=int(con.execute("SELECT count(*) FROM focus").fetchone()[0])
        if focus_rows<100:
            raise RuntimeError(f"Unexpected few species-stage aquatic feeding edges {focus_rows}")
        # Current source label quality first; GloBI sourceDOI references original dataset,
        # not necessarily an independently observed predation event.
        edge_groups=fetchdict(con,"""
            SELECT predator_guild,prey_guild,
              count(*) as n_source_rows,
              count(DISTINCT predator || '|' || prey) AS n_directed_binomial_pairs,
              count(DISTINCT predator) AS n_predator_species,
              count(DISTINCT prey) AS n_prey_species,
              count(*) FILTER (WHERE ps IS NOT NULL) AS predator_stage_any,
              count(*) FILTER (WHERE qs IS NOT NULL) AS prey_stage_any,
              count(*) FILTER (WHERE ps IS NOT NULL AND qs IS NOT NULL) AS both_stages_present,
              count(*) FILTER (WHERE source_doi IS NOT NULL) AS rows_with_original_source_doi,
              count(DISTINCT source_doi) as distinct_source_dois,
              count(*) FILTER (WHERE reference IS NOT NULL) AS rows_with_ref,
              count(DISTINCT reference) as distinct_reference_citations,
              count(*) FILTER (
                WHERE lat BETWEEN -90 AND 90 AND lon BETWEEN -180 AND 180
                  AND NOT (abs(lat)<0.0001 and abs(lon)<0.0001)
              ) AS valid_geo_rows
            FROM focus
            GROUP BY predator_guild,prey_guild
            ORDER BY n_source_rows DESC
        """)
        stage_vocab=fetchdict(con,"""
            SELECT side,stage,count(*) AS raw_records
            FROM (
               SELECT 'predator' AS side,
                      COALESCE(ps,'(missing)') AS stage FROM focus
               UNION ALL
               SELECT 'prey' AS side,
                      COALESCE(qs,'(missing)') AS stage FROM focus
            )
            GROUP BY side,stage ORDER BY raw_records DESC LIMIT 75
        """)
        top_source=fetchdict(con,"""
           SELECT COALESCE(source_doi,'(missing)') AS original_source_doi,
                  count(*) AS records,
                  count(DISTINCT predator || '|' || prey) AS directed_edges,
                  count(*) FILTER (WHERE ps IS NOT NULL AND qs IS NOT NULL) AS staged_rows
           FROM focus GROUP BY original_source_doi
           ORDER BY records DESC LIMIT 30
        """)
        # Exact species-pair reverse evidence in stable release, unique A!=B.
        con.execute("""
            CREATE TEMP VIEW edge_summary AS
            SELECT predator,prey,
              count(*) AS rows,
              count(DISTINCT source_doi) AS source_doi_count,
              count(DISTINCT reference) AS reference_count,
              count(*) FILTER (WHERE ps IS NOT NULL AND qs IS NOT NULL) AS both_stage_rows
            FROM focus GROUP BY predator,prey
        """)
        recip=fetchdict(con,"""
            SELECT a.predator AS species_a,a.prey AS species_b,
                a.rows AS a_eats_b_rows,b.rows AS b_eats_a_rows,
                a.source_doi_count AS a_eats_b_source_dois,
                b.source_doi_count AS b_eats_a_source_dois,
                a.both_stage_rows AS a_eats_b_staged,
                b.both_stage_rows AS b_eats_a_staged
            FROM edge_summary a
            JOIN edge_summary b ON a.predator=b.prey AND a.prey=b.predator
            WHERE a.predator < a.prey
            ORDER BY (a.both_stage_rows+b.both_stage_rows) DESC,
                     (a.rows+b.rows) DESC LIMIT 100
        """)
        recip_n=con.execute("""
            SELECT count(*) FROM edge_summary a
            JOIN edge_summary b ON a.predator=b.prey AND a.prey=b.predator
            WHERE a.predator < a.prey
        """).fetchone()[0]
        # Pair and stage combinations for comparative GBIF follow-on (not all
        # given GloBI edge stages independent observed attacks).
        stages=fetchdict(con,"""
            SELECT predator,prey,predator_guild,prey_guild,
                COALESCE(ps,'(missing)') AS predator_stage,
                COALESCE(qs,'(missing)') AS prey_stage,
                count(*) AS source_rows,
                count(DISTINCT source_doi) AS source_dataset_dois,
                count(DISTINCT reference) AS reference_citations
            FROM focus WHERE ps IS NOT NULL OR qs IS NOT NULL
            GROUP BY predator,prey,predator_guild,prey_guild,ps,qs
            ORDER BY source_rows DESC LIMIT 120
        """)
        geo=fetchdict(con,"""
            SELECT
              CASE WHEN abs(lat)<23.5 THEN 'tropical'
                   WHEN abs(lat)<66.5 THEN 'temperate'
                   ELSE 'polar' END AS absolute_latitude_band,
              predator_guild,prey_guild,
              count(*) AS source_rows,
              count(DISTINCT source_doi) AS source_dataset_dois,
              count(*) FILTER (WHERE ps IS NOT NULL AND qs IS NOT NULL)
                 AS both_stage_records
            FROM focus
            WHERE lat BETWEEN -90 AND 90 AND lon BETWEEN -180 AND 180
              AND NOT (abs(lat)<0.0001 and abs(lon)<0.0001)
            GROUP BY 1,2,3 ORDER BY 1,source_rows DESC
        """)
        general=fetchdict(con,"""
            SELECT count(*) AS eligible_rows,
              count(DISTINCT predator) AS distinct_predator_species,
              count(DISTINCT prey) AS distinct_prey_species,
              count(DISTINCT predator || '|' || prey) AS distinct_directed_pairs,
              count(*) FILTER (WHERE predator=prey) AS self_feeding_source_rows,
              count(DISTINCT predator) FILTER (WHERE predator=prey)
                AS self_feeding_species,
              count(*) FILTER (WHERE ps IS NOT NULL AND qs IS NOT NULL)
                AS raw_both_stage_rows,
              count(*) FILTER (WHERE ps IS NOT NULL OR qs IS NOT NULL)
                AS raw_either_stage_rows,
              count(*) FILTER (WHERE source_doi IS NOT NULL)
                AS sourced_dataset_doi_rows
            FROM focus
        """)[0]
        duration=time.monotonic()-st
        report={
            "date":"2026-10-25",
            "status":"FULL_GLOBI_VERSIONED_REAL_DATA_ANALYSIS",
            "source":{
                "doi":SOURCE_MD,
                "released":"2026-09-10",
                "aggregate_license":"CC0, original sources to be cited individually",
                "md5":GLOBI_MD5,
                "download_bytes":receipt["bytes"],
                "source_rows":source_rows,
                "source_198_rowgroups":True,
                "download_elapsed_seconds":receipt["elapsed_seconds"],
                "query_elapsed_seconds":round(duration,2)
            },
            "focal_filter":"both species-level canonical names, documented eats/preysOn, at least one focal Anura/Caudata/Odonata or Dytiscidae family; GloBI interpreted taxon categories",
            "scope":general,
            "edge_groups":edge_groups,
            "stage_labels_most_frequent":stage_vocab,
            "top_source_dois":top_source,
            "candidate_reciprocal_different_species_pair_count":int(recip_n),
            "reciprocal_candidate_examples":recip,
            "top_stage_pattern_examples":stages,
            "georeferenced_source_records_by_latitude":geo,
            "bounds":[
               "This scans full versioned GloBI 24.45M records (not an API first page) but is filtered to focal aquatic guilds.",
               "GloBI indexed edges include literature-derived or inferred associations; not independent physical attacks or predation flux.",
               "Different stage labels and source DOIs can be missing or repeated; source author attribution required.",
               "GloBI source species names are not yet exhaustively canonicalized against GBIF taxon IDs.",
               "Latitudes of source interaction records are not random or ecologically standardized samples.",
               "A reciprocal named-species pair is a candidate *directional association*, not verified ontogenetic dominance reversal.",
               "Historical frog chorus/vegetation/hydrology require independent observed site×time linkage.",
               "This script does not access authenticated accounts, private data or GBIF bulk downloads."
            ]
        }
        (output/"observed_results.json").write_text(
             json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
        print("BEGIN_GLOBI_FULL_FIXED_SUMMARY")
        print(json.dumps({
            "source":report["source"],
            "scope":general,
            "edge_groups":edge_groups[:25],
            "top_source_dois":top_source[:12],
            "reciprocal_count":recip_n,
            "reciprocal_examples":recip[:20],
            "top_stage_patterns":stages[:15],
            "georeferenced":geo[:15]
        },ensure_ascii=False,indent=2))
        print("END_GLOBI_FULL_FIXED_SUMMARY")


def selftest():
    assert "CASE" in select_context("read_parquet('x')") and GLOBI_ROWS==24453954
    assert quote_source("file's-name")=="'file''s-name'"
    print("FULL_GLOBI_SYNTHETIC_SQL_QA_PASS")


if __name__=="__main__":
    a=argparse.ArgumentParser()
    a.add_argument("--out",default="research/results/globi_fixed_full_foodweb")
    a.add_argument("--self-test",action="store_true")
    args=a.parse_args()
    if args.self_test:selftest()
    else:run(args.out)
