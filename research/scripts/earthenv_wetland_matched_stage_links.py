#!/usr/bin/env python3
"""Full GloBI×GBIF named-stage linked versus matched prey under EarthEnv habitat.

Inputs: independent audited 1° EarthEnv historical consensus land cover;
       expanded real GBIF Anura/Odonata species×stage×grid×year×month;
       already-selected GloBI source documented vs same-guild/stage prey controls;
       optional historic CRU-WorldClim rain source (limited GBIF-mask coverage).

Reported outcomes are SEASONAL GBIF REPORTING compatibilities, NOT actual
predation, wetland encounters, fish/refuge causes, bird/bat warnings or chorus.
Protocol research/EARTHENV_WETLAND_MACRO_ALIGNMENT_SPEC_V0_1.md.
"""
from __future__ import annotations
import argparse
import collections
import csv
import json
import math
import statistics
from pathlib import Path

from fixed_globi_gbif_month_shift_null import read_cell_cubes, compare_one, THRESHOLDS

BINS=("near_zero","low_intermediate","relatively_high")
DATE="2026-10-25"
REPORTING_THRESHOLDS=(1,5)

def bin_environment(flooded):
    if flooded is None or not math.isfinite(flooded):
        return "missing"
    if flooded < .01:
        return "near_zero"
    if flooded < 1.:
        return "low_intermediate"
    return "relatively_high"


def read_earthenv(path):
    out={}
    stats=collections.Counter()
    with Path(path).open(newline="",encoding="utf8") as f:
        reader=csv.DictReader(f)
        required={"latcell","loncell",
                  "regularly_flooded_vegetation_pct","open_water_pct",
                  "generic_herbaceous_pct"}
        if not required.issubset(reader.fieldnames or []):
            raise ValueError("Not the source-checked EarthEnv global 1deg CSV")
        for row in reader:
            cell=(int(row["latcell"]),int(row["loncell"]))
            def dec(x):
                return float(x) if x not in ("",None) else None
            flood=dec(row["regularly_flooded_vegetation_pct"])
            water=dec(row["open_water_pct"])
            herbs=dec(row["generic_herbaceous_pct"])
            for x in (flood,water,herbs):
                if x is not None and (not 0<=x<=100):
                    raise ValueError("EarthEnv input percentage invalid")
            if cell in out:
                raise ValueError("Duplicate EarthEnv global 1deg cell")
            out[cell]=(bin_environment(flood),flood,water,herbs)
            stats[out[cell][0]]+=1
    if len(out)<50000:
        raise ValueError("Incomplete global raster EarthEnv input, len "+str(len(out)))
    return out,dict(stats)


def split_by_habitat(masks,habitat):
    """No-stage imputation: assign original taxon×stage×grid×year masks."""
    grouped={}
    sourcecounts={}
    for threshold in THRESHOLDS:
        grouped[threshold]={tier:collections.defaultdict(dict) for tier in BINS}
        footprint=collections.Counter()
        missing=0
        for key,locations in masks[threshold].items():
            for cell_year,bitmask in locations.items():
                (lat,lon,year)=cell_year
                src=habitat.get((lat,lon))
                if src is None or src[0] not in BINS:
                    missing+=1
                    continue
                tier=src[0]
                grouped[threshold][tier][key][cell_year]=bitmask
                footprint[tier]+=1
        sourcecounts[threshold]={"by_tier":dict(footprint),
                                 "unmapped_site_stage_grid_years":missing}
    return grouped,sourcecounts


def matched_controls(sourcefile):
    rows=[]
    with Path(sourcefile).open(newline="",encoding="utf8") as f:
        r=csv.DictReader(f)
        required={"predator","prey","predator_stage","prey_stage",
                  "threshold","control_preys","source_tiers"}
        if not required.issubset(r.fieldnames or []):
            raise ValueError("Expected preselected stage/guild prey comparison artifact")
        for x in r:
            if int(x["threshold"])!=1:
                continue
            controls=tuple(p.strip() for p in x["control_preys"].split(";")
                           if p.strip())
            if len(controls)<2:
                continue
            rows.append(dict(predator=x["predator"],
                             prey=x["prey"],
                             predator_stage=x["predator_stage"],
                             prey_stage=x["prey_stage"],
                             predator_guild=x.get("predator_guild",""),
                             prey_guild=x.get("prey_guild",""),
                             controls=controls,
                             source_tiers=x["source_tiers"]))
    if len(rows)<8:
        raise ValueError("Too few originally selected GloBI predator/prey controls")
    if len(set((x["predator"],x["predator_stage"],x["prey"],
                x["prey_stage"]) for x in rows))!=len(rows):
        raise ValueError("Duplicated matched GloBI source pair")
    return rows


def read_rain(path):
    if not path:
        return {},{"status":"not_attached"}
    rain={}
    n=0
    with Path(path).open(newline="",encoding="utf8") as f:
        reader=csv.DictReader(f)
        keys={"latcell","loncell","year","month","precipitation_mm_month"}
        if not keys.issubset(reader.fieldnames or []):
            raise ValueError("WorldClim GBIF monthly coverage artifact schema changed")
        for r in reader:
            n+=1
            if r.get("status") not in (None,"","ON_LAND","ON_LAND_CRU_MONTHLY_RAIN"):
                continue
            if r["precipitation_mm_month"] in ("",None):
                continue
            yy=int(r["year"]); mm=int(r["month"])
            if not (2010<=yy<=2024 and 1<=mm<=12):
                continue
            key=(int(r["latcell"]),int(r["loncell"]),yy,mm)
            val=float(r["precipitation_mm_month"])
            if val<0 or val>4000:
                raise ValueError("Unexpected WorldClim source precipitation")
            if key in rain and abs(rain[key]-val)>.005:
                raise ValueError("Inconsistent climate repeats in same grid-month")
            rain[key]=val
    return rain,dict(source_rows=n,unique_climate_grid_months=len(rain),
                     status="PARTIAL_MONTHS_ONLY_SOURCE_CONDITIONED_ON_INITIAL_GBIF_REPORTS")


def joint_rain(predator,prey,rain):
    if not rain:
        return None,0,0
    vals=[]
    expected=0
    for (lat,lon,year) in set(predator)&set(prey):
        if year>2024:
            continue
        both=predator[(lat,lon,year)]&prey[(lat,lon,year)]
        for month in range(1,13):
            if both & (1<<(month-1)):
                expected+=1
                val=rain.get((lat,lon,year,month))
                if val is not None:
                    vals.append(val)
    return ((statistics.mean(vals) if vals else None),len(vals),expected)


def read_source_arrays(gbif,wetland,matched,rain=None):
    habitat,coverage=read_earthenv(wetland)
    masks,gbif_receipt=read_cell_cubes(gbif)
    grouped,tier_coverage=split_by_habitat(masks,habitat)
    comparisons=matched_controls(matched)
    rainmap,rain_receipt=read_rain(rain)
    return habitat,coverage,masks,gbif_receipt,grouped,tier_coverage,comparisons,rainmap,rain_receipt


def calculate(gbif,wetland,matched,optional_rain=None):
    (habitat,envcover,rawmasks,gbif_receipt,by_tier,tier_coverage,comparisons,
     rainmap,rain_receipt)=read_source_arrays(gbif,wetland,matched,optional_rain)
    rows=[]
    missingpair=collections.Counter()
    for r in comparisons:
        pred_key=(r["predator"],r["predator_stage"])
        prey_key=(r["prey"],r["prey_stage"])
        for threshold in REPORTING_THRESHOLDS:
            for tier in BINS:
                index=by_tier[threshold][tier]
                pred=index.get(pred_key,{})
                prey=index.get(prey_key,{})
                shared_year=len(set(pred)&set(prey))
                if shared_year<5:
                    missingpair[(threshold,tier,"insufficient_true_partner_gridyears")]+=1
                    continue
                valid_controls=[]
                for alt in r["controls"]:
                    control=index.get((alt,r["prey_stage"]),{})
                    alt_year=len(set(pred)&set(control))
                    if alt_year<5:
                        continue
                    q=compare_one(pred,control)
                    av,nn,dd=joint_rain(pred,control,rainmap)
                    valid_controls.append(dict(
                        species=alt,
                        shared_years=alt_year,
                        phase_ratio=q["observed_over_shift_mean_plus1"],
                        exact_co_reporting=q["observed_exact_grid_year_month"],
                        climate_mean_co_report_mm=av,
                        climate_matched_n=nn,
                        climate_observed_co_report_cells=dd))
                if len(valid_controls)<2:
                    missingpair[(threshold,tier,"fewer_than_two_matched_alternatives")]+=1
                    continue
                value=compare_one(pred,prey)
                avg,nn,dd=joint_rain(pred,prey,rainmap)
                cq=statistics.median(z["phase_ratio"] for z in valid_controls)
                q=value["observed_over_shift_mean_plus1"]
                alt_rain=[z["climate_mean_co_report_mm"]
                          for z in valid_controls
                          if z["climate_mean_co_report_mm"] is not None and
                             z["climate_matched_n"]>=5]
                delta_rain=(avg-statistics.median(alt_rain)
                            if avg is not None and nn>=5 and len(alt_rain)>=2
                            else None)
                rows.append(dict(
                    predator=r["predator"],prey=r["prey"],
                    predator_stage=r["predator_stage"],
                    prey_stage=r["prey_stage"],
                    predator_guild=r["predator_guild"],
                    prey_guild=r["prey_guild"],
                    source_tiers=r["source_tiers"],
                    minimum_reports_per_taxon_stage_grid_month=threshold,
                    wetland_static_background_tier=tier,
                    predator_prey_shared_grid_years=shared_year,
                    n_valid_alternative_prey=len(valid_controls),
                    alternative_prey_species=";".join(x["species"] for x in valid_controls),
                    observed_shared_1deg_cell_year_month=value["observed_exact_grid_year_month"],
                    shifted_month_null_mean=value["month_shift_null_mean"],
                    documented_edge_phase_ratio=q,
                    matched_undocumented_prey_median_phase_ratio=cq,
                    phase_ratio_focal_minus_control=q-cq,
                    focal_above_matched_median=int(q>cq),
                    focal_mean_rain_mm=avg,
                    focal_rain_source_months=nn,
                    focal_eligible_rain_source_months=dd,
                    focal_minus_alternative_rain_mm=delta_rain,
                    scientific_boundary="STATIC_WETLAND_CONTEXT_NOT_CAUSAL_PREDATION",
                ))
    site_details={}
    for cell,(tier,flood,water,herbs) in habitat.items():
        if tier not in BINS:
            continue
        site_details.setdefault(tier,{"count":0,"flood":[],"water":[],"herbs":[]})
        group=site_details[tier]
        group["count"]+=1
        group["flood"].append(flood)
        group["water"].append(water)
        group["herbs"].append(herbs)
    env_tiers={}
    for tier in BINS:
        group=site_details.get(tier)
        env_tiers[tier]=dict(
            global_1deg_cells=group["count"] if group else 0,
            median_flooded_vegetation_pct=(statistics.median(group["flood"]) if group else None),
            median_open_water_pct=(statistics.median(group["water"]) if group else None),
            median_generic_herbaceous_pct=(statistics.median(group["herbs"]) if group else None))
    summary=[]
    for threshold in REPORTING_THRESHOLDS:
        for tier in BINS:
            part=[r for r in rows if
                  r["minimum_reports_per_taxon_stage_grid_month"]==threshold and
                  r["wetland_static_background_tier"]==tier]
            comparable={k:r for k,r in enumerate(part)}
            vals=[x["phase_ratio_focal_minus_control"] for x in part]
            rain_comparable=[x["focal_minus_alternative_rain_mm"]
                             for x in part
                             if x["focal_minus_alternative_rain_mm"] is not None]
            summary.append(dict(
                threshold=threshold,environment_tier=tier,
                source_documented_staged_edges=len(part),
                distinct_predator_taxa=len(set(x["predator"] for x in part)),
                source_iNat_links=sum("INAT" in x["source_tiers"] for x in part),
                source_curated_links=sum("QUICK_POND" in x["source_tiers"] for x in part),
                documented_above_matched_alternative=sum(
                    x["focal_above_matched_median"] for x in part),
                documented_below_equal_matched_alternative=len(part)-sum(
                    x["focal_above_matched_median"] for x in part),
                median_focal_minus_alternative_phase_ratio=(
                    statistics.median(vals) if vals else None),
                mean_focal_minus_alternative_phase_ratio=(
                    statistics.mean(vals) if vals else None),
                within_pair_rain_comparisons=len(rain_comparable),
                median_focal_minus_matched_prey_month_rain_mm=(
                    statistics.median(rain_comparable)
                    if rain_comparable else None),
                interpretation="POSTHOC_OBSERVATION_REPORTING_ECOLOGICAL_BACKGROUND_ONLY"
            ))
    paired=[]
    for threshold in REPORTING_THRESHOLDS:
        grouped=collections.defaultdict(dict)
        for r in rows:
            if r["minimum_reports_per_taxon_stage_grid_month"]!=threshold:
                continue
            key=(r["predator"],r["predator_stage"],
                 r["prey"],r["prey_stage"])
            grouped[key][r["wetland_static_background_tier"]]=r
        for key, tiers in grouped.items():
            if "near_zero" not in tiers or "relatively_high" not in tiers:
                continue
            low=tiers["near_zero"]
            high=tiers["relatively_high"]
            paired.append(dict(
                threshold=threshold,predator=key[0],prey=key[2],
                predator_stage=key[1],prey_stage=key[3],
                high_minus_nearzero_specificity_ratio=(
                    high["phase_ratio_focal_minus_control"] -
                    low["phase_ratio_focal_minus_control"]),
                high_background_pair_gridyears=high["predator_prey_shared_grid_years"],
                nearzero_background_pair_gridyears=low["predator_prey_shared_grid_years"]
            ))
    return rows,dict(
        date=DATE,
        status="REAL_STATIC_EARTHENV_GLOBI_GBIF_MATCHED_STAGE_PREY_DIAGNOSTIC",
        earthenv_1deg_source="https://www.earthenv.org/landcover, Tuanmu & Jetz 2014, CC BY-NC 4.0",
        primary_source_GloBI="https://doi.org/10.5281/zenodo.22691479",
        primary_source_GBIF="https://github.com/zuizui0223/frogcs/actions/runs/40194946916",
        climate_source="WorldClim 2.1 CRU-TS4.09 historical monthly precipitation 2010–2024 partial GBIF-only cached grid months" if optional_rain else "not joined",
        gbif_source_QC=gbif_receipt,
        static_habitat_raster_QC=dict(
            EarthEnv_grid_coverage=envcover,
            EarthEnv_by_flooded_fraction_bin=env_tiers),
        stage_grid_background_coverage=tier_coverage,
        source_matched_prey_documented_edges=len(comparisons),
        discarded_source_edges_by_bin_reason={
            "|".join(map(str,k)):v for k,v in missingpair.items()},
        comparison_by_threshold_and_background=summary,
        source_pairs_with_both_nearzero_and_high_flooded_bins=[
            dict(threshold=thr,
                 n_matched_source_pairs=sum(x["threshold"]==thr for x in paired),
                 unique_predator_species=len(set(x["predator"] for x in paired
                                                 if x["threshold"]==thr)),
                 median_high_minus_nearzero_focal_specificity=(
                    statistics.median(x["high_minus_nearzero_specificity_ratio"]
                                      for x in paired if x["threshold"]==thr)
                    if any(x["threshold"]==thr for x in paired) else None))
            for thr in REPORTING_THRESHOLDS],
        top_focal_paired_gradient=sorted(paired,key=lambda x:(
            -abs(x["high_minus_nearzero_specificity_ratio"]),x["predator"]))[:20],
        limitations=[
            "EarthEnv periodically flooded vegetation from mixed 1990s–2000s data is not live emergent stems, Typha or aquatic plant density.",
            "GBIF 1° cell and month/year reports by separate taxa are NOT pond co-occurrence, observed attacks, mortality, or a causal food-web interaction.",
            "Controls are undocumented in complete-staged GloBI subset, NOT independently verified as absent prey or noninteractors.",
            "Some source pair controls have insufficient GBIF overlap in given wetland bins, so there is nonrandom within-tier sample selection and no global regression or P-values.",
            "Stage reporting, citizen-science density, taxonomy and introduced status bias geographic and seasonal coincidence.",
            "WorldClim cached months are conditioned on another GBIF focal sample; rain comparisons are low-confidence source coverage diagnostics, not 72-hour NAAMP rain response.",
            "Multiple pair observations share predator, prey, GBIF records and source citation; source-level independent replication not achieved.",
            "No direct world wetland inventory/geometry, wetland hydroperiod, future egg recruitment or frog chorus record was matched."
        ],
    )


def save(rows,summary,out):
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    with (out/"habitat_matched_predator_prey_stage_comparisons.csv").open(
        "w",encoding="utf8",newline="") as f:
        if rows:
            w=csv.DictWriter(f,fieldnames=list(rows[0]))
            w.writeheader();w.writerows(rows)
    (out/"observed_results.json").write_text(
        json.dumps(summary,ensure_ascii=False,indent=2)+"\n",
        encoding="utf8")
    print("BEGIN_GLOBI_EARTHENV_WETLAND_STAGE_RESULTS")
    print(json.dumps(summary,ensure_ascii=False,indent=2))
    print("END_GLOBI_EARTHENV_WETLAND_STAGE_RESULTS")


def selftest():
    assert bin_environment(None)=="missing"
    assert bin_environment(0)=="near_zero"
    assert bin_environment(.0099)=="near_zero"
    assert bin_environment(.2)=="low_intermediate"
    assert bin_environment(1.)=="relatively_high"
    # Grid and year must be matched before reporting month and rain.
    pred={(52,5,2020):1<<2}
    prey={(52,5,2020):1<<2}
    climate={(52,5,2020,3):80}
    assert joint_rain(pred,prey,climate)==(80,1,1)
    assert joint_rain(pred,{(52,5,2020):1<<4},climate)==(None,0,0)
    print("EARTHENV_WETLAND_STAGE_MATCHED_NEGATIVE_CONTROL_SYNTHETIC_QA_PASS")


if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--gbif",required=False)
    ap.add_argument("--earthenv",required=False)
    ap.add_argument("--matched",required=False)
    ap.add_argument("--rain",required=False)
    ap.add_argument("--out",default="research/results/earthenv_gbif_matched_stage")
    ap.add_argument("--self-test",action="store_true")
    args=ap.parse_args()
    if args.self_test:selftest()
    else:
        if not all([args.gbif,args.earthenv,args.matched]):
            ap.error("--gbif --earthenv --matched required")
        result,summary=calculate(args.gbif,args.earthenv,
                                 args.matched,args.rain)
        save(result,summary,args.out)
