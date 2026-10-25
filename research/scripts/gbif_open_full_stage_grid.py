#!/usr/bin/env python3
"""Direct global GBIF anonymous taxon-partition parquet: species × stage × 1° grid × month/year.

Source: public experimental GBIF August 2026 DWCA Parquet partitions.
Aligned GloBI v0.11 stage-linked focal species from full-source summary.
This is reported spatial detection overlap, NOT realized predation or cohort abundance.
"""
import argparse
import collections
import csv
import json
import math
import re
import time
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen, Request
import xml.etree.ElementTree as ET

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import pyarrow.fs as fs

BUCKET="gbif-public-data"
BASE="development/2026-08-01-DWCA/p_taxon/"
PARTITIONS={
    "Anura":"Animalia_Chordata_Amphibia_Anura",
    "Odonata":"Animalia_Arthropoda_Insecta_Odonata",
}
COLS=["gbifID","species","speciesKey","year","month",
      "lifeStage","occurrenceStatus","hasGeospatialIssues",
      "decimalLatitude","decimalLongitude","coordinateUncertaintyInMeters"]
STAGE_TAGS={
    "adult":"adult","imago":"adult",
    "larva":"aquatic_immature","nymph":"aquatic_immature",
    "tadpole":"aquatic_immature",
    "egg":"egg",
    "juvenile":"juvenile","subadult":"juvenile",
    "immature":"juvenile","young":"juvenile"
}
HAND_FALLBACK=[
    "Anax junius","Anaxyrus boreas","Pseudacris regilla",
    "Libellula luctuosa","Rana temporaria","Pelophylax lessonae",
    "Rhinella marina","Osteopilus septentrionalis",
    "Bufo bufo","Coenagrion puella","Sympetrum vulgatum",
    "Taricha torosa","Anaxyrus americanus",
]
MAX_TAXA=120
SPECIES_RE=re.compile(r"^[A-Z][a-z]+ [a-z][a-z-]+$")


def globi_stage(raw):
    r=str(raw or "").strip().lower()
    if r in ["", "-999", "unknown", "(missing)"]:return ""
    if "post-juvenile adult" in r or "adult" in r or "imago" in r:
        return "adult"
    if any(q in r for q in ("larv","tadpol","nymph","instar")):
        return "aquatic_immature"
    if "egg" in r or "embryo" in r:return "egg"
    if "young" in r or "juvenil" in r or "subadult" in r:
        return "juvenile"
    return ""


def input_from_globi(p):
    data=json.loads(Path(p).read_text(encoding="utf-8"))
    pairs=data.get("top_stage_pattern_examples",[])
    reverse=data.get("reciprocal_candidate_examples",[])
    selected={}
    for x in pairs:
        for name in (x.get("predator"),x.get("prey")):
            if name and SPECIES_RE.fullmatch(name):
                selected[name]=selected.get(name,0)+int(x.get("source_rows",1))
    for x in reverse[:75]:
        for name in (x.get("species_a"),x.get("species_b")):
            if name and SPECIES_RE.fullmatch(name):
                selected[name]=selected.get(name,0)+int(x.get("a_eats_b_rows",1))
    # Global initial focus adds fixed bridge exemplars, not selected from
    # geographic GBIF overlap. Source selection was made before seeing GBIF grid.
    for name in HAND_FALLBACK:
        selected[name]=max(selected.get(name,0),1)
    names=sorted(selected,key=lambda name:(-selected[name],name))[:MAX_TAXA]
    edges=[]
    for row in pairs:
        a,b=row.get("predator"),row.get("prey")
        u,v=globi_stage(row.get("predator_stage")),globi_stage(row.get("prey_stage"))
        if a in names and b in names and u and v:
            edges.append((a,u,b,v))
    return names,sorted(set(edges))


def s3_list(part):
    prefix=BASE+f"taxonpartition={part}/"
    url=f"https://{BUCKET}.s3.amazonaws.com/?"+urlencode({
        "list-type":2,"prefix":prefix,"max-keys":100})
    with urlopen(Request(url,headers={"User-Agent":"frogcs-stage-grid-open-data/1.0"}),timeout=50) as req:
        root=ET.fromstring(req.read())
    def text(x,label):
        t=x.find("{*}"+label)
        return t.text if t is not None else ""
    rows=sorted((text(r,"Key"),int(text(r,"Size")))
                for r in root.findall("{*}Contents"))
    rows=[(p,size) for p,size in rows if p.endswith(".parquet")]
    if not rows or len(rows)>20:
        raise RuntimeError(f"Unexpected count of parquet files for {part}: {len(rows)}")
    return rows


def selected_row_groups(meta,key,names):
    idx=meta.schema.names.index("species")
    hits=[]
    no_stats=0
    for rg in range(meta.num_row_groups):
        stats=meta.row_group(rg).column(idx).statistics
        if not stats or not stats.has_min_max:
            hits.append(rg)
            no_stats+=1
            continue
        mi,ma=stats.min,stats.max
        if isinstance(mi,bytes): mi=mi.decode("utf8","replace")
        if isinstance(ma,bytes): ma=ma.decode("utf8","replace")
        if any(str(mi)<=name<=str(ma) for name in names):
            hits.append(rg)
    return hits,no_stats


def normalized_stage(v):
    return STAGE_TAGS.get(str(v or "").strip().lower(),"unlabelled")


def process_rowgroups(parquet,rg_list,names,counts,counters,coverage):
    target=set(names)
    for rg in rg_list:
        tbl=parquet.read_row_group(rg,columns=COLS)
        df=tbl.to_pandas()
        before=len(df)
        df=df.loc[df.species.isin(target)].copy()
        counters["all_rows_with_target_species"]+=len(df)
        if df.empty:continue
        year=pd.to_numeric(df.year,errors="coerce")
        month=pd.to_numeric(df.month,errors="coerce")
        lat=pd.to_numeric(df.decimalLatitude,errors="coerce")
        lon=pd.to_numeric(df.decimalLongitude,errors="coerce")
        uncertainty=pd.to_numeric(df.coordinateUncertaintyInMeters,errors="coerce")
        valid=(df.occurrenceStatus=="PRESENT") & (df.hasGeospatialIssues==False)
        valid&=year.between(2010,2026)&month.between(1,12)
        valid&=lat.between(-90,90)&lon.between(-180,180)
        valid&=uncertainty.isna() | uncertainty.le(10000)
        df=df.loc[valid].copy()
        if df.empty:continue
        lat=lat.loc[valid]
        lon=lon.loc[valid]
        year=year.loc[valid]
        month=month.loc[valid]
        df["latcell"]=lat.map(math.floor).astype("int16")
        df["loncell"]=lon.map(math.floor).astype("int16")
        df["year"]=year.astype("int16")
        df["month"]=month.astype("int8")
        df["stage"]=df.lifeStage.map(normalized_stage)
        counters["valid_target_records"]+=len(df)
        counters["valid_explicit_stage_records"]+=int((df.stage!="unlabelled").sum())
        for name,k in df.species.value_counts().items():
            coverage[name]+=int(k)
        grouped=df.groupby(
            ["species","stage","latcell","loncell","year","month"],
            dropna=False).size()
        for (name,stage,glat,glon,y,m),n in grouped.items():
            counts[(name,stage,int(glat),int(glon),int(y),int(m))]+=int(n)


def overlap_pairs(counts,edges,threshold=1):
    species_stage_sets=collections.defaultdict(set)
    for (sp,stage,lat,lon,year,month),count in counts.items():
        if count>=threshold:
            species_stage_sets[(sp,stage)].add((lat,lon,year,month))
    rows=[]
    for pred,ps,prey,qs in edges:
        src=species_stage_sets.get((pred,ps),set())
        tar=species_stage_sets.get((prey,qs),set())
        same=src & tar
        # same cell and year, dropping month for sensitivity only
        annual_a={(lat,lon,yr) for lat,lon,yr,_ in src}
        annual_b={(lat,lon,yr) for lat,lon,yr,_ in tar}
        rows.append({
            "predator":pred,"predator_stage":ps,
            "prey":prey,"prey_stage":qs,
            "reporting_cells_predator":len(src),
            "reporting_cells_prey":len(tar),
            "same_1deg_cell_month_year":len(same),
            "same_1deg_cell_year_any_month":len(annual_a & annual_b),
            "threshold_records_per_cell_stage":threshold,
            "biological_status":"CO_RECORDED_POTENTIAL_ONLY"
        })
    return rows


def write_csv(path,rows,fields):
    with open(path,"w",encoding="utf8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=fields)
        w.writeheader();w.writerows(rows)


def run(a):
    names,edges=input_from_globi(a.globi_results)
    s3=fs.S3FileSystem(anonymous=True,region="us-east-1")
    out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
    counts=collections.Counter()
    coverage=collections.Counter()
    counters=collections.Counter()
    receipts=[]
    start=time.time()
    for order,part in PARTITIONS.items():
        files=s3_list(part)
        for file,size in files:
            with s3.open_input_file(f"{BUCKET}/{file}") as f:
                meta=pq.ParquetFile(f)
                hits,absent=selected_row_groups(meta.metadata,file,names)
                before=len(counts)
                process_rowgroups(meta,hits,names,counts,counters,coverage)
            receipts.append(dict(
                order=order,source=f"s3://{BUCKET}/{file}",
                parquet_bytes=size,
                parquet_rows=meta.metadata.num_rows,
                parquet_row_groups=meta.metadata.num_row_groups,
                row_groups_read=len(hits),
                groups_without_minmax=absent,
                gridded_records_after_file=sum(counts.values()),
                distinct_aggregated_cells=len(counts)))
    rows=[dict(species=s,stage=stage,latcell=lat,loncell=lon,
               year=year,month=month,n_records=n)
          for (s,stage,lat,lon,year,month),n in sorted(counts.items())]
    if not rows:raise RuntimeError("No observed focal species stage grid records")
    write_csv(out/"focal_stage_1deg_month_year.csv",rows,
              ["species","stage","latcell","loncell","year","month","n_records"])
    overlaps=overlap_pairs(counts,edges)
    write_csv(out/"gloBI_stage_pair_same_grid_report.csv",overlaps,[
        "predator","predator_stage","prey","prey_stage",
        "reporting_cells_predator","reporting_cells_prey",
        "same_1deg_cell_month_year","same_1deg_cell_year_any_month",
        "threshold_records_per_cell_stage","biological_status"])
    summary={
        "date":"2026-10-25",
        "source":"GBIF open anonymous experimental August 2026 DWCA taxon partitions",
        "experimental_status":"NOT_PRODUCTION_STABLE_LEGACY_TAXON_KEY",
        "classification":"Interpretation-first full partition scan with Parquet rowgroup species min/max range pruning",
        "source_snapshots":receipts,
        "focal_species_requested":len(names),
        "species_with_georeferenced_records":len(coverage),
        "global_taxa_requested":names,
        "actual_records_by_species":coverage.most_common(35),
        "source_rows_examined_with_species_filter":int(counters["all_rows_with_target_species"]),
        "valid_georeferenced_focal_records":int(counters["valid_target_records"]),
        "valid_lifestage_explicit_records":int(counters["valid_explicit_stage_records"]),
        "unique_species_stage_1deg_month_year_cells":len(counts),
        "named_predation_stage_pairs_tested":len(edges),
        "same_1deg_cell_month_year_edges":sum(r["same_1deg_cell_month_year"]>0 for r in overlaps),
        "same_1deg_cell_year_any_month_edges":sum(r["same_1deg_cell_year_any_month"]>0 for r in overlaps),
        "edge_co_reporting_examples":overlaps[:35],
        "target_species_key_note":"2026 GBIF experimental Parquet speciesKey is alphanumeric, so do not join it directly to the older numeric GBIF API speciesKey; normalized binomial species names were used.",
        "elapsed_seconds":round(time.time()-start,2),
        "warnings":[
            "Stage×cell reporting is NOT a kill event or contemporary pond-level contact.",
            "GBIF month-year dating does not imply records came from same day/habitat within 1° cell.",
            "Missing stage labels must not be counted as biological absence.",
            "Experimental August 2026 GBIF species taxonomy may differ from current GBIF API accepted taxa; synonym and identity match audit required.",
            "Parquet rowgroups were range-pruned using original species min/max; all matching groups were scanned, but snapshot is an experimental production not the official October release.",
            "Coordinate uncertainty >10 km excluded where recorded; missing coordinate uncertainty retained and must be quantified in a separate strict sensitivity.",
            "GloBI stage source observations can originate in literature-inferred food webs; external source evidence types not audited to true attacks.",
            "Not a population-level ontogenetic dominance reversal, frog chorus or vegetation effect.",
        ]
    }
    (out/"observed_results.json").write_text(
        json.dumps(summary,indent=2,ensure_ascii=False)+"\n",encoding="utf8")
    print("BEGIN_GBIF_ACTUAL_FINE_GRID")
    print(json.dumps({
        "source_counts":len(receipts),"requested":len(names),
        "matched":len(coverage),"records":counters,
        "grid_cells":len(counts),"pairs":len(edges),
        "pairs_with_overlap":summary["same_1deg_cell_month_year_edges"],
        "file_summary":[{key:x[key] for key in ("order","parquet_rows",
                     "parquet_row_groups","row_groups_read")}
                       for x in receipts],
        "top_species":coverage.most_common(20),
        "first_edges":overlaps[:15],
        "elapsed_seconds":summary["elapsed_seconds"]
    },indent=2,ensure_ascii=False))
    print("END_GBIF_ACTUAL_FINE_GRID")


def synthetic():
    assert normalized_stage("Nymph")=="aquatic_immature"
    assert normalized_stage("-999")=="unlabelled"
    assert globi_stage("post-juvenile adult stage")=="adult"
    c={("Anax junius","aquatic_immature",30,-90,2024,6):2,
       ("Anaxyrus boreas","aquatic_immature",30,-90,2024,6):1,
       ("Anaxyrus boreas","adult",31,-90,2023,7):5}
    edges=[("Anax junius","aquatic_immature",
             "Anaxyrus boreas","aquatic_immature")]
    res=overlap_pairs(c,edges)
    assert res[0]["same_1deg_cell_month_year"]==1
    print("GBIF_1DEG_STAGE_CELL_SYNTHETIC_QA_PASS")


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--globi-results",default="research/results/globi_fixed_full_foodweb/observed_results.json")
    p.add_argument("--out",default="research/results/gbif_open_stage_1deg")
    p.add_argument("--self-test",action="store_true")
    opts=p.parse_args()
    if opts.self_test:synthetic()
    else:run(opts)
