#!/usr/bin/env python3
"""GloBI-directed GBIF stage co-reporting × real WorldClim monthly rain.

Post hoc 2010–2024 *within same 1° grid-year* co-report vs single-report
month precipitation contrast. Not effect of rain on actual predation or frogs.
No P-value, no substitution for NAAMP 72-hour rain or local wetland plants.
Protocol: research/GLOBAL_RAIN_STAGE_GRID_COPRESENCE_SPEC_V0_1.md
"""
import argparse
import collections
import csv
import json
import math
import statistics
from pathlib import Path

from fixed_globi_gbif_month_shift_null import read_edges

YEARS=range(2010,2025)
THRESHOLDS=(1,5)
MIN_YEAR_STRATA=5


def read_source_csv(path):
    rain=collections.defaultdict(dict)
    seen_species=collections.defaultdict(lambda:collections.defaultdict(dict))
    audit=collections.Counter()
    with Path(path).open(encoding="utf8",newline="") as f:
        rd=csv.DictReader(f)
        required={
            "species","stage","loncell","latcell","year","month","n_records",
            "precipitation_mm_month","climate_status"
        }
        if not required.issubset(rd.fieldnames or []):
            raise ValueError("Source GBIF×WorldClim CSV schema mismatch")
        for r in rd:
            audit["rows"]+=1
            lat=int(r["latcell"]);lon=int(r["loncell"])
            y=int(r["year"]);m=int(r["month"]);n=int(r["n_records"])
            if not 2010<=y<=2024 or not 1<=m<=12 or n<=0:
                raise ValueError("Invalid georeferenced dated GBIF source row")
            if not -90<=lat<90 or not -180<=lon<180:
                raise ValueError("Invalid 1degree GBIF location")
            k=(lat,lon,y);mk=(m)
            if r["climate_status"]!="ON_LAND_CRU_MONTHLY_RAIN":
                audit["missing_climate_rows"]+=1
                continue
            try:p=float(r["precipitation_mm_month"])
            except (ValueError,TypeError):
                raise ValueError("Non-numeric measured rain at on-land grid")
            if not math.isfinite(p) or p<0 or p>3000:
                raise ValueError("Invalid monthly precipitation, not a percentage")
            if mk in rain[k] and abs(rain[k][mk]-p)>0.0002:
                raise ValueError("Conflicting rainfall for repeated species in same grid-year-month")
            rain[k][mk]=p
            t=(r["species"].strip(),r["stage"].strip())
            prev=seen_species[t][k].get(m,0)
            seen_species[t][k][m]=prev+n
            audit["onland_rows"]+=1
    audit["unique_species_stage"]=len(seen_species)
    audit["unique_grid_years"]=len(rain)
    audit["unique_grid_year_months"]=sum(len(m) for m in rain.values())
    return seen_species,rain,dict(audit)


def contrast(pred,prey,rain,minobs):
    keys=set(pred)&set(prey)
    deltas=[]
    special=[]
    n_c=0;n_u=0;n_year=0
    p_wet=0;p_dry=0
    for key in keys:
        rainfall=rain.get(key,{})
        pm={m for m,n in pred[key].items() if n>=minobs and m in rainfall}
        qm={m for m,n in prey[key].items() if n>=minobs and m in rainfall}
        if not pm or not qm:
            continue
        both=pm&qm
        one=pm^qm
        n_year+=1
        n_c+=len(both)
        n_u+=len(one)
        if not both or not one:
            continue
        cmean=statistics.mean(rainfall[m] for m in both)
        umean=statistics.mean(rainfall[m] for m in one)
        deltas.append((key,cmean-umean))
        # Conditional wet vs dry month imbalance within exact grid-year.
        months=sorted(pm|qm)
        if len(months)>=3:
            median=statistics.median(rainfall[m] for m in months)
            sw=sum(m in both for m in months if rainfall[m]>median)
            sd=sum(m in both for m in months if rainfall[m]<=median)
            if sw+sd:
                special.append((key,sw,sd))
    return {
        "grid_year_with_both_stages_any_observed_month":n_year,
        "co_reported_stage_grid_year_months":n_c,
        "single_report_stage_grid_year_months":n_u,
        "informative_grid_years_with_both_month_categories":len(deltas),
        "distinct_grid_sites_in_informative_strata":len(set((k[0],k[1]) for k,_ in deltas)),
        "mean_within_grid_year_rain_difference_mm_month":
            statistics.mean(v for _,v in deltas) if deltas else None,
        "median_within_grid_year_rain_difference_mm_month":
            statistics.median(v for _,v in deltas) if deltas else None,
        "fraction_grid_years_with_copresence_month_wetter":
            sum(v>0 for _,v in deltas)/len(deltas) if deltas else None,
        "co_reported_above_gridyear_observed_month_rain_median":
            sum(x[1] for x in special),
        "co_reported_at_or_below_gridyear_observed_month_rain_median":
            sum(x[2] for x in special),
        "status":"DESCRIPTIVE_NONCAUSAL" if len(deltas)>=MIN_YEAR_STRATA
                 else "INSUFFICIENT_GRID_YEARS_FOR_DIRECTION",
        "example_grid_years":[dict(latcell=k[0],loncell=k[1],year=k[2],
                                   delta_mm_month=round(d,4))
                              for k,d in sorted(deltas)[:6]],
    }


def run(src,globi,provenance,out):
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    species,rain,source=read_source_csv(src)
    edges,discard=read_edges(globi,provenance)
    if not edges:
        raise RuntimeError("No eligible fixed stage pairs")
    rows=[]
    for e in edges:
        pred=species.get((e["predator"],e["predator_stage"]),{})
        prey=species.get((e["prey"],e["prey_stage"]),{})
        for t in THRESHOLDS:
            v=contrast(pred,prey,rain,t)
            x={key:e.get(key,"") for key in (
                "predator","prey","predator_stage","prey_stage",
                "predator_guild","prey_guild","source_tiers",
                "source_rows","source_dois","citation_examples")}
            x.update(dict(min_records_per_stage_grid_month=t))
            x.update(v)
            x.pop("example_grid_years",None)
            rows.append(x)
    with (out/"rain_samegrid_stage_pair_contrasts.csv").open(
            "w",encoding="utf8",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]),extrasaction="ignore")
        writer.writeheader();writer.writerows(rows)
    summary=[]
    for t in THRESHOLDS:
        rr=[r for r in rows if r["min_records_per_stage_grid_month"]==t]
        ok=[r for r in rr if r["status"]=="DESCRIPTIVE_NONCAUSAL"]
        vals=[r["mean_within_grid_year_rain_difference_mm_month"] for r in ok]
        summary.append({
            "min_records_per_taxon_stage_grid_month":t,
            "all_candidate_species_stage_pairs":len(rr),
            "pairs_with_enough_informative_grid_years":len(ok),
            "pairs_insufficient":len(rr)-len(ok),
            "pairs_where_monthly_rain_co_report_is_greater_than_single_report":
                sum(x>0 for x in vals),
            "pairs_where_monthly_rain_co_report_is_lower":sum(x<0 for x in vals),
            "median_pair_mean_rain_difference_mm_month":
                statistics.median(vals) if vals else None,
            "weighted_mean_grid_year_delta_not_reported_as_global_effect":True,
            "most_informative_pairs":sorted([
                {k:x.get(k) for k in (
                    "predator","prey","predator_stage","prey_stage",
                    "informative_grid_years_with_both_month_categories",
                    "mean_within_grid_year_rain_difference_mm_month",
                    "status","source_tiers")}
                for x in ok
            ],key=lambda x:-x["informative_grid_years_with_both_month_categories"])[:12]
        })
    result={
        "date":"2026-10-25",
        "status":"REAL_GLOBI_GBIF_WORLDCLIM_2010_2024_MONTHLY_RAIN_DESCRIPTIVE",
        "source_fixed_globi":"https://doi.org/10.5281/zenodo.22691479",
        "source_GBIF_stage":"https://github.com/zuizui0223/frogcs/actions/runs/40190152042",
        "source_precip":"WorldClim 2.1 CRU-TS4.09 historical 2010-2024 https://www.worldclim.org/data/monthlywth.html",
        "input_join":"research/results/gbif_worldclim_monthly_rain/observed_results.json",
        "main_description":"Within a single 1° grid-year with both species stages recorded, monthly precipitation when both are observed minus when exactly one is observed",
        "source_row_quality":source,
        "GloBI_stage_pairs_total":len(edges),
        "GloBI_source_exclusions":discard,
        "per_threshold":summary,
        "warnings":[
            "This is not true animal co-occurrence within a pond or realized predation.",
            "Actual CRU-WorldClim monthly rain is NOT same as NAAMP antecedent 72-hour rain or local water depth/hydroperiod.",
            "GBIF stage reporting, effort, accessibility and taxonomic coverage vary seasonally; a wet-month correlation could arise without biotic interaction.",
            "Rain was sampled at the centre of 1degree cells, not frog chorus GPS or original GloBI interaction event sites.",
            "Only world land cells with source precipitation and GBIF reported stage records were used; absence is missing, not true absence.",
            "Repeated grid-year observations and duplicated GloBI source metawebs preclude independent P-values.",
            "No emergent/submerged plant stem structure, native range or species-specific demography is represented.",
            "All stage links come from a nonrepresentative subset of taxa with GBIF observed stages.",
            "The reported pair mean effects are descriptive exploratory within-space-year contrasts, not predation or chorusing causal effects."
        ]}
    (out/"observed_results.json").write_text(
        json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    print("BEGIN_GLOBI_GBIF_GRID_YEAR_RAIN_RESULTS")
    print(json.dumps(result,ensure_ascii=False,indent=2))
    print("END_GLOBI_GBIF_GRID_YEAR_RAIN_RESULTS")


def selftest():
    src={(30,-90,2021):{4:1,5:1,7:1}}
    prey={(30,-90,2021):{4:1,7:1}}
    precip={(30,-90,2021):{4:100.,5:20.,7:10.}}
    # Both observed in months 4 and 7; only one in month 5.
    a=contrast(src,prey,precip,1)
    assert a["informative_grid_years_with_both_month_categories"]==1
    assert a["co_reported_stage_grid_year_months"]==2
    assert a["single_report_stage_grid_year_months"]==1
    assert abs(a["mean_within_grid_year_rain_difference_mm_month"]-35)<1e-9
    print("GLOBAL_MONTHLY_RAIN_WITHIN_GRIDYEAR_SYNTHETIC_QA_PASS")


if __name__=="__main__":
    a=argparse.ArgumentParser()
    a.add_argument("--gbif-rain",default="research/data/climate/gbif_stage_1degree_year_month_precipitation.csv")
    a.add_argument("--globi",default="research/data/globi/nonself_stage_pair_grid_results.csv")
    a.add_argument("--provenance",default="research/data/globi/full_nonself_staged_GloBI_provenance.csv")
    a.add_argument("--out",default="research/results/globi_gbif_rain_contrast")
    a.add_argument("--self-test",action="store_true")
    x=a.parse_args()
    if x.self_test:selftest()
    else:run(x.gbif_rain,x.globi,x.provenance,x.out)
