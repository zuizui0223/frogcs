#!/usr/bin/env python3
"""Macro ecological sensitivity: species-equal phenology and shifted-month null.

Use ONLY five original record-level iNaturalist GBIF stage tables, 2015–2025,
outside NAAMP. Biological endpoint is relative temporal stage availability,
NOT predator-prey contact, causality, true pond occurrence or predation rate.
This was designed after inspecting initial guild-level results and is
explicitly exploratory/post-result, not confirmatory.
"""
from __future__ import annotations
import argparse,csv,json
from collections import defaultdict
from pathlib import Path
import numpy as np

from ecology.macro_stage.scripts.analyze_gbif_observations import read_original
from ecology.macro_stage.scripts.harvest_gbif_observations import REGIONS_SELECTED

YEAR_MIN_RECORDS=15
MIN_MONTHS=2
SPECIES_MIN_RECORDS=10
SPECIES_MIN_PER_GROUP=3
SOURCE_N_RECORDS=21979
SEED=2840223
STAGES=("frog_larva","salamander_egg","salamander_larva")

def shared_stage_months(rows):
    by_year=defaultdict(lambda:np.zeros(12,int))
    by_species=defaultdict(lambda:np.zeros(12,int))
    for r in rows:
        reg,year,stage=r["region"],int(r["year"]),r["guild_stage"]
        if stage not in STAGES:continue
        m=int(r["month"])-1
        by_year[(reg,year,stage)][m]+=1
        if str(r.get("taxonRank","")).upper()=="SPECIES" and r.get("speciesKey"):
            by_species[(reg,stage,str(r["speciesKey"]))][m]+=1
    return by_year,by_species

def overlap_and_excess(a,b):
    aa=np.asarray(a,float);bb=np.asarray(b,float)
    if aa.shape!=(12,) or bb.shape!=(12,) or aa.sum()<=0 or bb.sum()<=0:
        raise ValueError("two positive monthly original stage distributions required")
    pa,pb=aa/aa.sum(),bb/bb.sum()
    overlaps=np.asarray([np.minimum(pa,np.roll(pb,shift)).sum() for shift in range(12)])
    return float(overlaps[0]),float(overlaps[0]-overlaps.mean())

def year_by_year(by_year):
    out=[]
    for region in REGIONS_SELECTED:
        for year in range(2015,2026):
            f=by_year[(region,year,"frog_larva")]
            e=by_year[(region,year,"salamander_egg")]
            l=by_year[(region,year,"salamander_larva")]
            if not all(v.sum()>=YEAR_MIN_RECORDS and (v>0).sum()>=MIN_MONTHS for v in (f,e,l)):
                continue
            oe,xe=overlap_and_excess(f,e)
            ol,xl=overlap_and_excess(f,l)
            out.append({"region":region,"year":year,
                "n_frog_larva":int(f.sum()),"n_salamander_egg":int(e.sum()),
                "n_salamander_larva":int(l.sum()),
                "month_overlap_frog_larva_sal_egg":round(oe,6),
                "month_overlap_frog_larva_sal_larva":round(ol,6),
                "unadjusted_larval_minus_egg":round(ol-oe,6),
                "phase_excess_frog_larva_sal_egg":round(xe,6),
                "phase_excess_frog_larva_sal_larva":round(xl,6),
                "phase_adjusted_larval_minus_egg":round(xl-xe,6)})
    return out

def species_balanced(by_species):
    out=[]
    for region in REGIONS_SELECTED:
        pg={};sample_sizes={}
        for stage in STAGES:
            arr=[v/v.sum() for (r,taxon_stage,species),v in by_species.items()
                 if r==region and taxon_stage==stage and v.sum()>=SPECIES_MIN_RECORDS
                 and (v>0).sum()>=MIN_MONTHS]
            sample_sizes[stage]=len(arr)
            pg[stage]=np.mean(arr,axis=0) if arr else None
        if any(v<SPECIES_MIN_PER_GROUP for v in sample_sizes.values()):
            continue
        oe,xe=overlap_and_excess(pg["frog_larva"],pg["salamander_egg"])
        ol,xl=overlap_and_excess(pg["frog_larva"],pg["salamander_larva"])
        out.append({"region":region,
            "n_frog_larva_species":sample_sizes["frog_larva"],
            "n_salamander_egg_species":sample_sizes["salamander_egg"],
            "n_salamander_larva_species":sample_sizes["salamander_larva"],
            "species_equal_month_overlap_frog_larva_sal_egg":round(oe,6),
            "species_equal_month_overlap_frog_larva_sal_larva":round(ol,6),
            "species_equal_larval_minus_egg":round(ol-oe,6),
            "species_equal_phase_adjusted_larval_minus_egg":round(xl-xe,6)})
    return out

def output_report(year,balanced,source):
    # There is no independent repeat of region-year within region; descriptive only.
    positive=lambda v,k:sum(x[k]>0 for x in v)
    return {
        "analysis":"GBIF_shared_source_original_observations_macro_stage_phase_sensitivity_v0_1",
        "source":"GBIF iNaturalist original record-level stage observations 2015–2025, dataset 50c9509d-22c7-4a22-a47d-8c48425ef4a7",
        "n_original_gbif_stage_observations":SOURCE_N_RECORDS,
        "n_region_years_with_three_guild_stages":len(year),
        "year_cells_larval_window_greater_than_egg_window":positive(year,"unadjusted_larval_minus_egg"),
        "year_cells_after_12_month_circular_phase_baseline_positive":positive(year,"phase_adjusted_larval_minus_egg"),
        "mean_original_month_overlap_difference":round(float(np.mean([r["unadjusted_larval_minus_egg"] for r in year])),6) if year else None,
        "mean_phase_adjusted_difference":round(float(np.mean([r["phase_adjusted_larval_minus_egg"] for r in year])),6) if year else None,
        "n_regions_with_at_least_three_qualifying_species_per_stage":len(balanced),
        "species_equal_regions_with_larval_window_greater":positive(balanced,"species_equal_larval_minus_egg"),
        "species_equal_regions_with_positive_phase_excess_difference":positive(balanced,"species_equal_phase_adjusted_larval_minus_egg"),
        "region_means_phase_adjusted":[{"region":reg,
            "mean_phase_adjusted_difference":round(float(np.mean([v["phase_adjusted_larval_minus_egg"] for v in year if v["region"]==reg])),6)}
            for reg in REGIONS_SELECTED],
        "sources_sha256":source,
        "not_preregistered_prior_to_guild_results":True,
        "not_a_predation_or_salamander_fitness_study":True,
        "stage_observation_is_not_same_pond_or_individual":True,
        "year_region_repeats_not_37_independent_field_experiments":True,
        "frogcs_NAAMP_acoustic_tables_accessed":False}

def write_csv(path,items):
    if not items:raise RuntimeError("No observable rows for documented stage analysis")
    with Path(path).open("w",newline="",encoding="utf-8") as f:
        writer=csv.DictWriter(f,fieldnames=list(items[0]))
        writer.writeheader();writer.writerows(items)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--inputs",type=Path,required=True)
    p.add_argument("--outdir",type=Path,required=True)
    a=p.parse_args()
    raw,source=read_original(a.inputs)
    if len(raw)!=SOURCE_N_RECORDS:raise RuntimeError("original sampled source record count changed")
    stage_year,stage_species=shared_stage_months(raw)
    annual=year_by_year(stage_year)
    balanced=species_balanced(stage_species)
    result=output_report(annual,balanced,source)
    a.outdir.mkdir(parents=True,exist_ok=True)
    write_csv(a.outdir/"macro_yearly_stage_phase_null.csv",annual)
    write_csv(a.outdir/"macro_equal_species_stage_phase_sensitivity.csv",balanced)
    (a.outdir/"macro_year_species_phase_result.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps({k:v for k,v in result.items() if k!="sources_sha256"},indent=2))
if __name__=="__main__": main()
