#!/usr/bin/env python3
"""Global stage-selective EarthEnv habitat context from GBIF Anura/Odonata.

One GBIF observation of aquatic larva/nymph at 1° landcover background is NOT
measured larval abundance, demographic outcome, aquatic prey or attack.
Source: GloBI 2026-09 fixed-version supported guilds; 2026-08 GBIF complete
partition stage grids; Tuanmu & Jetz 2014 EarthEnv class 6/8/12.
"""
import argparse
import collections
import csv
import json
import math
import random
import statistics
from pathlib import Path

from earthenv_wetland_matched_stage_links import read_earthenv
from globi_gbif_prey_specificity_controls import prepare_taxa

STAGES=("adult","aquatic_immature")
MEASURES=("flooded","openwater","herbaceous")
MIN_REPORT_CELLS=30
MIN_GEO_CELLS=5
STRATUM_MIN_GEO_CELLS=3
SEED=20261025


def get_source(path,guilds):
    eligible_stage=collections.defaultdict(set)
    qualifying_species=collections.defaultdict(dict)
    records=[]
    cnt=collections.Counter()
    with Path(path).open(encoding="utf8",newline="") as f:
        read=csv.DictReader(f)
        cols={"species","stage","latcell","loncell","year","month","n_records"}
        if not cols.issubset(read.fieldnames or []):
            raise ValueError("GBIF full source stage 1degree grid schema mismatch")
        for r in read:
            cnt["all_stage_grid_rows"]+=1
            name=r["species"]
            stage=r["stage"]
            if stage not in STAGES:
                cnt["non_adult_aquatic_stage_rows_excluded"]+=1
                continue
            if name not in guilds or guilds[name] not in ("Anura","Odonata"):
                cnt["no_source_vetted_taxon_order"]+=1
                continue
            try:
                lat=int(r["latcell"])
                lon=int(r["loncell"])
                year=int(r["year"])
                month=int(r["month"])
                records_n=int(r["n_records"])
            except ValueError:
                raise ValueError("GBIF source dated stage fields invalid")
            if not (-90<=lat<90 and -180<=lon<180 and
                    2010<=year<=2025 and 1<=month<=12 and records_n>0):
                cnt["invalid_or_partial_2026_rows_excluded"]+=1
                continue
            eligible_stage[(name,stage)].add((lat,lon,year,month))
            qualifying_species[(name,stage)].setdefault(
                "geogrid",set()).add((lat,lon))
            records.append((name,stage,lat,lon,year,month,records_n))
    return records,eligible_stage,qualifying_species,dict(cnt)


def gather_groups(records,eligible_stage,geo,habitat):
    qualifying={}
    stage_volumes=collections.defaultdict(dict)
    names={name for name,stage in eligible_stage}
    for sp in sorted(names):
        counts={}
        for stage in STAGES:
            obs=len(eligible_stage.get((sp,stage),set()))
            points=len(geo.get((sp,stage),{}).get("geogrid",set()))
            counts[stage]=dict(grid_month_year_records=obs,unique_1deg_cells=points)
        qualified=(all(counts[s]["grid_month_year_records"]>=MIN_REPORT_CELLS and
                       counts[s]["unique_1deg_cells"]>=MIN_GEO_CELLS for s in STAGES))
        qualifying[sp]=dict(qualified=qualified,**{
            s:counts[s] for s in STAGES})
    monthly=collections.defaultdict(
        lambda:{"adult":set(),"aquatic_immature":set()})
    strict=collections.defaultdict(
        lambda:{"adult":set(),"aquatic_immature":set()})
    qa=collections.Counter()
    for name,stage,lat,lon,year,month,n in records:
        if not qualifying[name]["qualified"]:
            qa["excluded_species_insufficient_report_volume"]+=1
            continue
        bg=habitat.get((lat,lon))
        if not bg:
            qa["no_earthenv_1deg_cell"]+=1
            continue
        if bg[0]=="ocean_dominated":
            qa["open_water_majority_1deg_excluded"]+=1
            continue
        if bg[0] not in ("near_zero","low_intermediate","relatively_high"):
            qa["missing_env_data"]+=1
            continue
        band=(math.floor((lat+.5)/10)*10)
        monthly[(name,band,month)][stage].add((lat,lon))
        strict[(name,band,year,month)][stage].add((lat,lon))
        qa["retained_observed_gbif_stage_gridmonth_rows"]+=1
    return qualifying,monthly,strict,dict(qa)


def average(values,measure):
    index={"flooded":1,"openwater":2,"herbaceous":3}[measure]
    return statistics.mean(values[x][index] for x in values)


def stratum_estimates(groups,habitat,min_per_stage):
    out=[]
    bad=collections.Counter()
    for key,g in sorted(groups.items()):
        a=g["adult"]
        i=g["aquatic_immature"]
        if len(a)<min_per_stage or len(i)<min_per_stage:
            bad["insufficient_stage_geo_grid_cells"]+=1
            continue
        if len(a|i)<2:
            bad["same_only_one_cell"]+=1
            continue
        rec=dict(
            species=key[0],
            lat_band_start=key[1],
            calendar_year=key[2] if len(key)==4 else None,
            month=key[3] if len(key)==4 else key[2],
            adult_distinct_1deg_cells=len(a),
            immature_distinct_1deg_cells=len(i),
            same_1deg_cell_count=len(a&i),
        )
        for metric in MEASURES:
            rec[f"adult_mean_{metric}_pct"]=average(habitat,a,metric)
            rec[f"immature_mean_{metric}_pct"]=average(habitat,i,metric)
            rec[f"immature_minus_adult_{metric}_pct"]=(
                rec[f"immature_mean_{metric}_pct"]-
                rec[f"adult_mean_{metric}_pct"])
        out.append(rec)
    return out,dict(bad)


def collapse_species(rows,guilds):
    grouped=collections.defaultdict(list)
    for r in rows:
        grouped[r["species"]].append(r)
    result=[]
    for sp,d in sorted(grouped.items()):
        z=dict(
            species=sp,guild=guilds[sp],n_latband_month_strata=len(d),
            n_total_distinct_grid_cells_immature=sum(x["immature_distinct_1deg_cells"] for x in d),
            n_total_distinct_grid_cells_adult=sum(x["adult_distinct_1deg_cells"] for x in d),
        )
        for m in MEASURES:
            deltas=[x[f"immature_minus_adult_{m}_pct"] for x in d]
            z[f"mean_immature_minus_adult_{m}_pct"]=statistics.mean(deltas)
            z[f"median_immature_minus_adult_{m}_pct"]=statistics.median(deltas)
        result.append(z)
    return result


def bootstrap_species(sub,field):
    rng=random.Random(SEED+len(sub))
    x=[z[field] for z in sub]
    if len(x)<8:return None
    res=sorted(statistics.mean([rng.choice(x) for _ in x])
               for _ in range(2000))
    return [res[49],res[1949]]


def summary_species(species,strata,strict,qual,qa,source_qa,earthenv_qa):
    source_species=sum(1 for z in qual.values() if z["qualified"])
    outputs=[]
    for guild in ("Anura","Odonata"):
        data=[r for r in species if r["guild"]==guild]
        stats=dict(
            guild=guild,
            eligible_species_reporting_both_stages=(
                len([s for s,v in qual.items() if v["qualified"] and
                     any(r["species"]==s for r in data)]) ),
            species_with_enough_1deg_latband_month_strata=len(data),
            n_latband_month_strata=sum(z["n_latband_month_strata"] for z in data),
        )
        for m in MEASURES:
            f=f"mean_immature_minus_adult_{m}_pct"
            values=[z[f] for z in data]
            stats[f"{m}_median_of_species_month_latband_mean_deltas_pct"]=(
                statistics.median(values) if values else None)
            stats[f"{m}_equal_species_mean_delta_pct"]=(
                statistics.mean(values) if values else None)
            stats[f"{m}_species_positive_delta"]=sum(v>0 for v in values)
            stats[f"{m}_species_negative_delta"]=sum(v<0 for v in values)
            stats[f"{m}_species_cluster_bootstrap_mean_interval_95"]=(
                bootstrap_species(data,f))
        outputs.append(stats)
    strict_species={r["species"] for r in strict}
    return dict(
        study="Real global within same-taxon latitude-10deg band seasonal month amphibian/dragonfly adult vs aquatic immature GBIF reported EarthEnv flooded habitat background",
        date="2026-10-25",
        analysis_status="EXPLORATORY_REPORTED_LIFESTAGE_ENV_ASSOCIATION_NOT_TRUE_NICHE_OR_ABUNDANCE",
        focal_full_GloBI_doi="https://doi.org/10.5281/zenodo.22691479",
        full_GBIF_stage_grid_source="https://github.com/zuizui0223/frogcs/actions/runs/40194946916",
        EarthEnv_raster_source="Tuanmu and Jetz (2014), 1-km consensus land cover EarthEnv class 8/12/6 CC BY-NC 4.0",
        source_gbif_QC=source_qa,
        stage_species_source_volume_eligible=source_species,
        species_with_qualifying_month_latband_comparisons=len(species),
        main_month_latband_comparison_strata=len(strata),
        strictly_same_year_month_latband_strata=len(strict),
        strict_strata_distinct_species=len(strict_species),
        habitat_source_and_exclusion_QC=qa,
        source_validated_earthenv_grid_class_coverage=earthenv_qa,
        species_stage_results=outputs,
        top_species_by_strata=sorted(species,key=lambda x:-x["n_latband_month_strata"])[:20],
        limitations=[
            "GBIF lifeStage labels are observational and detection-biased; more larvae being reported in one region does not show true biological abundance or larval residence.",
            "Stage observations can be different times/places/individuals across years; no individual development trajectories or actual feeding interactions were monitored.",
            "Old EarthEnv regularly flooded vegetation consensus maps historical 1990s–2000s landscape context, not current Typha or Phragmites stand stem density.",
            "Latitude band and calendar-month matching control coarse climate and timing but not observer sampling design, country/elevation or longitude/continental taxonomic reporting.",
            "Land-dominant 1degree restriction excludes ocean majority coastal wetlands and underreports coastal stage sampling.",
            "Different GBIF taxon-stage presence and synonyms in experimental August 2026 taxonomy are not fully canonicalized to GloBI species.",
            "No causal wetland structure, rainfall, predator prey attack frequency, demographic role reversal or frog chorusing effect is established.",
            "Multiple seasonal strata per species are correlated; any species-bootstrap intervals are exploratory and only shown for at least 8 source taxa.",
        ]
    )


def write_csv(file,rows):
    if not rows:return
    with Path(file).open("w",encoding="utf8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]))
        w.writeheader();w.writerows(rows)


def run(gbif,wetland,provenance,out):
    habitat,envcover=read_earthenv(wetland)
    guilds,_=prepare_taxa(provenance)
    rows,stage_source,locations,source_qa=get_source(gbif,guilds)
    qualified,months,strict,qa=gather_groups(rows,stage_source,locations,habitat)
    month_rows,month_removed=stratum_estimates(months,habitat,STRATUM_MIN_GEO_CELLS)
    strict_rows,strict_removed=stratum_estimates(strict,habitat,2)
    summary_rows=collapse_species(month_rows,guilds)
    summary=summary_species(
        summary_rows,month_rows,strict_rows,qualified,qa,source_qa,
        envcover)
    summary["exclusion_in_matching"]={
        "month_latband":month_removed,
        "stricter_same_year_month_latband":strict_removed
    }
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    write_csv(out/"same_species_month_latband_stage_habitat.csv",month_rows)
    write_csv(out/"species_stage_habitat_differences.csv",summary_rows)
    write_csv(out/"strict_year_month_latband_stages.csv",strict_rows)
    (out/"observed_results.json").write_text(
        json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    print("BEGIN_GBIF_STAGE_VS_EARTHENV_WETLAND_REPORTING")
    print(json.dumps(summary,ensure_ascii=False,indent=2))
    print("END_GBIF_STAGE_VS_EARTHENV_WETLAND_REPORTING")


def selftest():
    x={
        (20,30):("low",1,20,30),
        (20,31):("high",5,2,30),
        (20,32):("zero",0,0,10),
        (20,33):("low",3,15,40),
    }
    p={("Anax junius",20,5):{
        "adult":{(20,30),(20,31),(20,32)},
        "aquatic_immature":{(20,31),(20,32),(20,33)}}
    }
    rows,errs=stratum_estimates(p,x,3)
    assert len(rows)==1 and not errs
    assert rows[0]["immature_minus_adult_flooded_pct"]>0
    assert rows[0]["month"]==5
    q={("Anax junius",20,2020,5):p[("Anax junius",20,5)]}
    strict,errs=stratum_estimates(q,x,2)
    assert len(strict)==1 and strict[0]["calendar_year"]==2020
    print("GLOBAL_STAGE_HABITAT_WITHIN_SPECIES_LATMONTH_QA_PASS")


if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--gbif")
    ap.add_argument("--earthenv")
    ap.add_argument("--provenance")
    ap.add_argument("--out",default="research/results/global_ontogenetic_wetland")
    ap.add_argument("--self-test",action="store_true")
    a=ap.parse_args()
    if a.self_test:selftest()
    else:
        if not all([a.gbif,a.earthenv,a.provenance]):
            ap.error("--gbif --earthenv --provenance required")
        run(a.gbif,a.earthenv,a.provenance,a.out)
