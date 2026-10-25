#!/usr/bin/env python3
"""Macro ecology: original iNaturalist stage observations resolved by year/grid.

Exploratory community phenology (not predator-prey attacks). Output biological
stage availability at (i) 5 latitude-region × 2015–2025 years, and (ii)
0.5 degree grid × year × month co-recorded life-history stages. Missing partner
records are unassessed, NOT true absence. Source is entirely outside NAAMP.
"""
from __future__ import annotations
import argparse,csv,hashlib,json
from collections import Counter,defaultdict
from pathlib import Path
import numpy as np

from ecology.macro_stage.scripts.harvest_gbif_observations import REGIONS_SELECTED,COLUMNS,COMMON_INAT_GBIF_DATASET
from ecology.macro_stage.scripts.analyze_gbif_macro import overlap
MIN_STAGE_YEAR=15
MIN_MONTHS=2
YEAR_RANGE=range(2015,2026)
STAGE_KEYS=("frog_larva","frog_egg","salamander_egg","salamander_larva","odonate_nymph")
REGION_EDGES=(("frog_larva","salamander_egg"),("frog_larva","salamander_larva"),("frog_larva","odonate_nymph"))

def read_original(directory):
    all_rows=[];source_receipts={}
    seen=set()
    for region in REGIONS_SELECTED:
        path=Path(directory)/f"macro_gbif_records_{region}.csv"
        receipt=Path(directory)/f"macro_gbif_original_page_receipt_{region}.json"
        if not path.is_file() or not receipt.is_file():raise RuntimeError("missing original GBIF regional source: "+region)
        j=json.loads(receipt.read_text())
        raw=path.read_bytes()
        if (j["region"]!=region or j["source_datasetKey"]!=COMMON_INAT_GBIF_DATASET
            or hashlib.sha256(raw).hexdigest()!=j["csv_sha256"]):
            raise RuntimeError("source table/GBIF page provenance failed")
        with path.open(newline="",encoding="utf-8") as f:
            reader=csv.DictReader(f)
            if set(reader.fieldnames or [])!=set(COLUMNS):
                raise ValueError("original stage record column schema unexpected")
            rows=list(reader)
        if len(rows)!=j["original_records_with_month_and_coarse_coordinate"]:
            raise RuntimeError("original stage source receipt total inconsistent")
        for r in rows:
            if r["region"]!=region or r["guild_stage"] not in STAGE_KEYS:
                raise ValueError("source stage/region invalid")
            if r["datasetKey"]!=COMMON_INAT_GBIF_DATASET:
                raise ValueError("multiple GBIF publishers inserted")
            if r["gbifID"] in seen:raise ValueError("GBIF same original occurrence repeated")
            seen.add(r["gbifID"])
            r["year"]=int(r["year"]);r["month"]=int(r["month"])
            if r["year"] not in YEAR_RANGE or not 1<=r["month"]<=12:raise ValueError("bad original date")
            all_rows.append(r)
        source_receipts[region]={"original_records":len(rows),"csv_sha256":j["csv_sha256"],
            "source_api_pages":len(j["source_http_page_sha256"])}
    return all_rows,source_receipts

def do_analysis(records):
    stage_month=defaultdict(lambda:np.zeros(12,dtype=int))
    species=defaultdict(set)
    bins=defaultdict(set)
    group_grid_month=defaultdict(set)
    for r in records:
        region,year,stage,month=r["region"],int(r["year"]),r["guild_stage"],int(r["month"])
        stage_month[(region,year,stage)][month-1]+=1
        if r["speciesKey"]:
            species[(region,year,stage)].add(str(r["speciesKey"]))
        grid=(r["grid_lat_05"],r["grid_lon_05"],year,month)
        bins[(region,year,stage)].add((r["grid_lat_05"],r["grid_lon_05"]))
        group_grid_month[(region,stage)].add(grid)
    stages=[];yearly=[];region_eligible=Counter()
    for region in REGIONS_SELECTED:
        for year in YEAR_RANGE:
            for stage in STAGE_KEYS:
                vec=stage_month[(region,year,stage)]
                stages.append({"region":region,"year":year,"life_stage":stage,
                    "original_observations":int(vec.sum()),"nonzero_months":int((vec>0).sum()),
                    "unique_species_keys":len(species[(region,year,stage)]),
                    "occupied_half_degree_grids":len(bins[(region,year,stage)]),
                    "eligible_15_records_2months":bool(vec.sum()>=MIN_STAGE_YEAR and (vec>0).sum()>=MIN_MONTHS)})
            for a,b in REGION_EDGES:
                x,y=stage_month[(region,year,a)],stage_month[(region,year,b)]
                eligible=x.sum()>=MIN_STAGE_YEAR and y.sum()>=MIN_STAGE_YEAR and (x>0).sum()>=MIN_MONTHS and (y>0).sum()>=MIN_MONTHS
                row={"region":region,"year":year,"stage_A":a,"stage_B":b,
                    "n_stage_A":int(x.sum()),"n_stage_B":int(y.sum()),
                    "meets_15records_per_stage_2months":bool(eligible),
                    "not_measured_breeding_pond_or_predation":True}
                if eligible:
                    row.update(year_resolved_month_overlap=round(overlap(x/x.sum(),y/y.sum()),6),
                        peak_month_A=int(x.argmax()+1),peak_month_B=int(y.argmax()+1))
                    region_eligible[(a,b)]+=1
                yearly.append(row)
    grids=[];summary=[]
    for region in REGIONS_SELECTED:
        a=group_grid_month[(region,"frog_larva")]
        for partner in ("salamander_egg","salamander_larva","odonate_nymph"):
            b=group_grid_month[(region,partner)]
            intersection=a&b
            summary.append({"region":region,"frog_larva_grid_year_month_positive":len(a),
                "partner_life_stage":partner,
                "partner_grid_year_month_positive":len(b),
                "both_positive_grid_year_month":len(intersection),
                "fraction_of_frog_positive_grids_with_partner_recorded":round(len(intersection)/len(a),6) if a else None,
                "spatial_resolution":"0.5° bin, not same pond",
                "absence_of_partner_does_not_mean_biological_absence":True})
            for cell in sorted(intersection):
                grids.append({"region":region,"partner_stage":partner,
                    "grid_lat_05":cell[0],"grid_lon_05":cell[1],
                    "year":cell[2],"month":cell[3]})
    # Fair phenological pairwise comparison uses same region-years with all three stages observable.
    by={(r["region"],r["year"],r["stage_B"]):r for r in yearly if r["meets_15records_per_stage_2months"]}
    fair=[]
    for region in REGIONS_SELECTED:
        for year in YEAR_RANGE:
            e=by.get((region,year,"salamander_egg"))
            l=by.get((region,year,"salamander_larva"))
            if e is None or l is None:continue
            fair.append({"region":region,"year":year,
                "frog_larva_salamander_egg_overlap":e["year_resolved_month_overlap"],
                "frog_larva_salamander_larva_overlap":l["year_resolved_month_overlap"],
                "larval_minus_egg_overlap":round(l["year_resolved_month_overlap"]-e["year_resolved_month_overlap"],6)})
    positives=sum(x["larval_minus_egg_overlap"]>0 for x in fair)
    summary_json={"analysis":"original_gbif_iNaturalist_species_stage_5regions_11years_0p5degree_2026_v0_1",
        "n_stage_annotated_original_observations":len(records),
        "n_source_regions":len(REGIONS_SELECTED),"n_years":len(YEAR_RANGE),
        "n_eligible_region_years_all_three_amphibian_stages":len(fair),
        "fraction_with_larval_window_greater_than_egg_window":round(positives/len(fair),6) if fair else None,
        "mean_larval_minus_egg_month_overlap":round(float(np.mean([x["larval_minus_egg_overlap"] for x in fair])),6) if fair else None,
        "n_region_years_with_larval_window_larger":positives,
        "n_half_degree_grid_year_month_frog_and_partner_observation":summary,
        "minimum_stage_record_gate":MIN_STAGE_YEAR,
        "no_surveys_without_observations_assumed":True,
        "no_predation_or_competition_observed":True,
        "shared_source":"GBIF iNaturalist "+COMMON_INAT_GBIF_DATASET,
        "cannot_claim_pond_level_encounters":True,
        "no_naamp_data_read":True}
    return stages,yearly,fair,grids,summary_json

def write_csv(path,items):
    with path.open("w",newline="",encoding="utf-8") as f:
        if not items:return
        w=csv.DictWriter(f,fieldnames=list(items[0]));w.writeheader();w.writerows(items)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--inputs",type=Path,required=True)
    p.add_argument("--outdir",type=Path,required=True)
    args=p.parse_args()
    rows,source=read_original(args.inputs)
    stages,yearly,fair,grids,report=do_analysis(rows)
    report["original_source_receipts"]=source
    args.outdir.mkdir(parents=True,exist_ok=True)
    for filename,items in [
        ("macro_stage_species_year_coverage.csv",stages),
        ("macro_stage_year_resolved_interaction_windows.csv",yearly),
        ("macro_stage_same_region_year_larva_egg_contrast.csv",fair),
        ("macro_stage_same_grid_year_month_opportunities.csv",grids)]:
        write_csv(args.outdir/filename,items)
    (args.outdir/"macro_original_record_species_stage_report.json").write_text(json.dumps(report,sort_keys=True,indent=2)+"\n")
    print(json.dumps(report,indent=2,sort_keys=True))
if __name__=="__main__":
    main()
